"""FastAPI service: health, audit, decision inbox. The dashboard (stage 3)
will be served from here too.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from pathlib import Path as _Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from . import __version__
from .agent import AgentLoop
from .audit import AuditLog
from .branding import NAME
from .config import settings
from .db import init_db
from .events import Event, EventBus
from .gateways.telegram import TelegramGateway
from .llm import make_provider
from .permissions import DecisionInbox, Level, PermissionStore
from .tools import ToolRegistry, builtin_tools
from .vault import Vault

log = logging.getLogger(__name__)


def build_app() -> FastAPI:
    settings.ensure_dirs()
    init_db(settings.db_path)

    bus = EventBus()
    audit = AuditLog(settings.db_path)
    vault = Vault(settings.db_path, settings.vault_key_path)
    permissions = PermissionStore(settings.db_path)
    inbox = DecisionInbox(settings.db_path)

    import secrets as _secrets

    from .automations import AutomationStore
    from .flags import Flags

    automations = AutomationStore(settings.db_path)
    flags = Flags(settings.db_path)

    # secret path token so only Twilio (which gets it in our TwiML) can reach
    # the public relay; generated once and kept in the vault
    relay_token = vault.get("relay_token")
    if not relay_token:
        relay_token = _secrets.token_urlsafe(24)
        vault.set("relay_token", relay_token)

    registry = ToolRegistry()
    for tool in builtin_tools(settings.db_path):
        registry.register(tool)
    from .tools import automation_tools, payment_tools, phone_tools
    from .wallet import Wallet

    for tool in automation_tools(automations):
        registry.register(tool)
    for tool in payment_tools(Wallet(settings.db_path)):
        registry.register(tool)
    for tool in phone_tools(vault, vault.get("user_name") or "użytkownika"):
        registry.register(tool)

    mailbox = None
    email_address = vault.get("email_address") or ""
    email_password = vault.get("email_password") or ""
    if email_address and email_password:
        from .email_tools import Mailbox, derive_hosts, email_tools

        imap_default, smtp_default = derive_hosts(email_address)
        mailbox = Mailbox(
            email_address,
            email_password,
            vault.get("email_imap_host") or imap_default,
            vault.get("email_smtp_host") or smtp_default,
        )
        for tool in email_tools(mailbox):
            registry.register(tool)

    def status_text() -> str:
        from .db import db as open_db

        with open_db(settings.db_path) as conn:
            tasks = conn.execute(
                "SELECT COUNT(*) c FROM tasks WHERE status='open'"
            ).fetchone()["c"]
            reminders = conn.execute(
                "SELECT COUNT(*) c FROM reminders WHERE status='pending'"
            ).fetchone()["c"]
        paused = flags.get_bool("paused")
        lines = [
            f"{'⏸ WSTRZYMANY' if paused else '▶️ aktywny'}",
            f"decyzje w kolejce: {len(inbox.pending())}",
            f"otwarte zadania: {tasks}",
            f"przypomnienia: {reminders}",
            f"automatyzacje: {len(automations.enabled())}",
            f"narzędzia: {len(registry.all())}",
        ]
        return "Status agenta:\n" + "\n".join(lines)

    telegram: TelegramGateway | None = None
    token = settings.telegram_bot_token or vault.get("telegram_bot_token") or ""
    owner_id = settings.telegram_owner_id or int(
        vault.get("telegram_owner_id") or 0
    )
    if token:
        telegram = TelegramGateway(
            token,
            owner_id,
            bus,
            inbox,
            on_claim=lambda chat_id: vault.set("telegram_owner_id", str(chat_id)),
            registry=registry,
            permissions=permissions,
            flags=flags,
            status_fn=status_text,
        )

    async def notify(text: str, meta: dict | None = None) -> None:
        if telegram is not None:
            await telegram.send(text, meta)
        else:
            log.info("notify (no telegram): %s", text)

    async def notify_photo(path: str, caption: str = "") -> None:
        if telegram is not None:
            await telegram.send_photo(path, caption)
        else:
            log.info("notify_photo (no telegram): %s", path)

    from .browser_tools import browser_available

    if browser_available():
        from .browser_tools import BrowserSession, browser_tools

        session = BrowserSession(settings.data_dir / "browser")
        for tool in browser_tools(session, notify_photo):
            registry.register(tool)

    model = vault.get("llm_model") or settings.llm_model
    provider = make_provider(
        model,
        settings.anthropic_api_key or vault.get("anthropic_api_key") or "",
        settings.openai_api_key or vault.get("openai_api_key") or "",
    )
    from .agent import build_system_prompt
    from .forge import Forge
    from .memory import Conversation, Memory
    from .skills_loader import skills_dir

    system_prompt = build_system_prompt(
        persona=vault.get("persona_prompt") or "",
        user_name=vault.get("user_name") or "",
    )
    loop = AgentLoop(
        bus, provider, registry, permissions, inbox, audit, notify,
        system_prompt=system_prompt,
        forge=Forge(provider),
        skills_dir=skills_dir(settings.data_dir),
        memory=Memory(settings.db_path),
        conversation=Conversation(settings.db_path),
        flags=flags,
    )
    # key used by voice transcription fallback
    loop._openai_key = settings.openai_api_key or vault.get("openai_api_key") or ""

    async def reminder_worker() -> None:
        """Fires due reminders — the agent speaks up on its own."""
        from datetime import datetime, timezone

        from .db import db as open_db

        while True:
            await asyncio.sleep(10)
            if flags.get_bool("paused"):
                continue
            now = datetime.now(timezone.utc).isoformat()
            with open_db(settings.db_path) as conn:
                due = conn.execute(
                    "SELECT id, text FROM reminders WHERE status = 'pending'"
                    " AND due_at <= ?",
                    (now,),
                ).fetchall()
                for row in due:
                    conn.execute(
                        "UPDATE reminders SET status = 'sent' WHERE id = ?",
                        (row["id"],),
                    )
            for row in due:
                await notify(f"⏰ Przypomnienie: {row['text']}", None)
                audit.record(
                    "agent", "reminder.fired", {"id": row["id"]},
                    row["text"], "zaplanowane przypomnienie",
                )

    async def scheduler_worker() -> None:
        """The proactive engine — turns standing automations into events."""
        from .proactive import Scheduler

        async def fetch_url(url: str) -> str:
            import httpx

            async with httpx.AsyncClient(
                follow_redirects=True, timeout=20
            ) as client:
                resp = await client.get(url)
            return resp.text

        scheduler = Scheduler(automations, bus, mailbox=mailbox, fetch_url=fetch_url)
        while True:
            await asyncio.sleep(30)
            try:
                await scheduler.tick()
            except Exception:
                log.exception("scheduler tick failed")

    @asynccontextmanager
    async def lifespan(fastapi_app: FastAPI):
        from .skills_loader import load_skills

        for tool in await load_skills(settings.data_dir):
            registry.register(tool)
        fastapi_app.state.tool_count = len(registry.all())

        tasks = [
            asyncio.create_task(loop.run_forever(), name="agent-loop"),
            asyncio.create_task(reminder_worker(), name="reminders"),
            asyncio.create_task(scheduler_worker(), name="scheduler"),
            asyncio.create_task(_run_relay_server(), name="relay-server"),
        ]
        if telegram is not None:
            await telegram.start()
        audit.record("system", "start", {}, "ok", f"{NAME} wstał")
        yield
        for task in tasks:
            task.cancel()
        if telegram is not None:
            await telegram.stop()

    app = FastAPI(title=NAME, version=__version__, lifespan=lifespan)
    app.state.telegram_on = telegram is not None
    app.state.model = model
    app.state.tool_count = len(registry.all())

    _dashboard = (_Path(__file__).parent / "dashboard" / "index.html").read_text(
        encoding="utf-8"
    )

    @app.get("/", response_class=HTMLResponse)
    async def dashboard() -> str:
        return _dashboard

    # The telephony relay lives on its OWN minimal app + port. Only this
    # port is ever exposed via a tunnel, and even then the WebSocket path
    # carries a secret token — the dashboard, vault and control endpoints
    # never leave localhost.
    relay_app = FastAPI()

    @relay_app.get("/health")
    async def relay_health() -> dict:
        return {"relay": "ok"}

    @relay_app.websocket("/relay/{token}")
    async def relay(ws: WebSocket, token: str) -> None:
        """Twilio ConversationRelay brain: transcribed speech in, spoken
        reply out. The agent runs the conversation toward a goal, then
        reports the outcome + transcript to the owner."""
        import json

        from .telephony import CALL_SYSTEM

        if token != relay_token:
            await ws.close(code=1008)
            return
        await ws.accept()
        state = {
            "goal": "", "owner": "użytkownika", "to": "",
            "messages": [], "transcript": [],
        }
        try:
            while True:
                msg = json.loads(await ws.receive_text())
                kind = msg.get("type")
                if kind == "setup":
                    params = msg.get("customParameters", {}) or {}
                    state["goal"] = params.get("goal", "")
                    state["owner"] = params.get("owner", "użytkownika")
                    state["to"] = msg.get("to", "")
                    audit.record(
                        "agent", "call.started", state["to"], state["goal"],
                        "rozmowa telefoniczna",
                    )
                elif kind == "prompt" and msg.get("last"):
                    said = msg.get("voicePrompt", "")
                    state["transcript"].append(f"rozmówca: {said}")
                    state["messages"].append({"role": "user", "content": said})
                    system = CALL_SYSTEM.format(owner=state["owner"], goal=state["goal"])
                    reply = await provider.chat(system, state["messages"], [])
                    text = (reply.text or "").strip() or "Przepraszam, czy może Pan powtórzyć?"
                    state["messages"].append({"role": "assistant", "content": text})
                    state["transcript"].append(f"asystent: {text}")
                    await ws.send_text(json.dumps({"type": "text", "token": text, "last": True}))
                elif kind == "error":
                    log.warning("relay error: %s", msg.get("description"))
        except WebSocketDisconnect:
            pass
        except Exception:
            log.exception("relay failed")
        finally:
            if state["transcript"]:
                await _finalize_call(state)

    async def _finalize_call(state: dict) -> None:
        transcript = "\n".join(state["transcript"])
        try:
            summary = await provider.chat(
                "Podsumuj wynik tej rozmowy telefonicznej w 1–2 zdaniach po polsku.",
                [{"role": "user", "content": transcript}],
                [],
            )
            outcome = (summary.text or "").strip()
        except Exception:
            outcome = "(nie udało się podsumować)"
        audit.record(
            "agent", "call.ended", state.get("to", ""), outcome,
            "wynik rozmowy telefonicznej",
        )
        await notify(
            f"📞 Rozmowa zakończona ({state.get('to','')})\n\n{outcome}\n\n"
            f"— transkrypcja —\n{transcript[:1500]}",
            None,
        )

    async def _run_relay_server() -> None:
        """Serve the relay app on its own localhost port (the only thing a
        tunnel ever exposes)."""
        import uvicorn as _uvicorn

        config = _uvicorn.Config(
            relay_app, host="127.0.0.1", port=settings.relay_port,
            log_level="warning",
        )
        await _uvicorn.Server(config).serve()

    @app.get("/connections")
    async def connections() -> dict:
        return {
            "llm": bool(
                settings.anthropic_api_key
                or settings.openai_api_key
                or vault.get("anthropic_api_key")
                or vault.get("openai_api_key")
            ),
            "telegram": bool(
                settings.telegram_bot_token or vault.get("telegram_bot_token")
            ),
            "email": bool(vault.get("email_address")),
            "phone": bool(
                vault.get("twilio_account_sid")
                and vault.get("twilio_number")
                and vault.get("public_url")
            ),
            "model": model,
        }

    @app.post("/connections")
    async def set_connections(request: Request) -> dict:
        body = await request.json()
        llm_key = str(body.get("llm_key", "")).strip()
        if llm_key.startswith("sk-ant"):
            vault.set("anthropic_api_key", llm_key)
        elif llm_key:
            vault.set("openai_api_key", llm_key)
        if body.get("telegram_token"):
            vault.set("telegram_bot_token", str(body["telegram_token"]).strip())
        if body.get("email_address") and body.get("email_password"):
            vault.set("email_address", str(body["email_address"]).strip())
            vault.set("email_password", str(body["email_password"]).strip())
        for k in ("twilio_number", "public_url", "elevenlabs_voice"):
            if body.get(k):
                vault.set(k, str(body[k]).strip())
        audit.record(
            "user", "connections.updated", list(body.keys()), "ok",
            "zmiana połączeń z panelu",
        )
        return {"ok": True, "note": "zrestartuj agenta, by zmiany weszły w życie"}

    @app.get("/health")
    async def health() -> dict:
        return {
            "name": NAME,
            "version": __version__,
            "events_pending": bus.pending,
            "telegram": telegram is not None,
            "paused": flags.get_bool("paused"),
            "tools": len(registry.all()),
            "automations": len(automations.enabled()),
            "pending": len(inbox.pending()),
        }

    @app.post("/pause")
    async def pause() -> dict:
        flags.set_bool("paused", True)
        audit.record("user", "pause", {}, "ok", "wstrzymano z panelu")
        return {"paused": True}

    @app.post("/resume")
    async def resume() -> dict:
        flags.set_bool("paused", False)
        audit.record("user", "resume", {}, "ok", "wznowiono z panelu")
        return {"paused": False}

    @app.get("/budget")
    async def budget() -> dict:
        from .wallet import Wallet

        w = Wallet(settings.db_path)
        per_txn, monthly, currency = w.policy()
        return {
            "per_txn": per_txn,
            "monthly": monthly,
            "currency": currency,
            "spent": w.spent_this_month(),
        }

    @app.get("/audit")
    async def audit_log(limit: int = 50) -> list[dict]:
        return audit.recent(limit)

    @app.get("/inbox")
    async def inbox_pending() -> list[dict]:
        return inbox.pending()

    @app.post("/inbox/{decision_id}/{verdict}")
    async def inbox_resolve(decision_id: str, verdict: str) -> dict:
        if verdict not in ("approve", "reject"):
            raise HTTPException(400, "verdict must be approve or reject")
        decision = inbox.resolve(decision_id, verdict == "approve")
        if decision is None:
            raise HTTPException(404, "no such pending decision")
        await bus.publish(
            Event(
                type="decision.approved"
                if verdict == "approve"
                else "decision.rejected",
                payload=decision,
                source="api",
            )
        )
        return decision

    @app.get("/automations")
    async def automations_list() -> list[dict]:
        return automations.all()

    @app.get("/skills")
    async def skills_list() -> list[dict]:
        return [
            {
                "name": t.name,
                "capability": t.capability,
                "description": t.description,
            }
            for t in registry.all()
        ]

    @app.get("/permissions")
    async def permissions_all() -> dict:
        caps = sorted({t.capability for t in registry.all()})
        return {cap: permissions.get(cap).value for cap in caps}

    @app.post("/permissions/{capability}/{level}")
    async def permissions_set(capability: str, level: str) -> dict:
        try:
            permissions.set(capability, Level(level))
        except ValueError:
            raise HTTPException(400, f"unknown level {level}")
        audit.record(
            "user", "permission.set", {capability: level}, "ok",
            "zmiana poziomu uprawnień",
        )
        return {capability: level}

    return app
