"""FastAPI service: health, audit, decision inbox. The dashboard (stage 3)
will be served from here too.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

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

    registry = ToolRegistry()
    for tool in builtin_tools(settings.db_path):
        registry.register(tool)

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
        )

    async def notify(text: str, meta: dict | None = None) -> None:
        if telegram is not None:
            await telegram.send(text, meta)
        else:
            log.info("notify (no telegram): %s", text)

    model = vault.get("llm_model") or settings.llm_model
    provider = make_provider(
        model,
        settings.anthropic_api_key or vault.get("anthropic_api_key") or "",
        settings.openai_api_key or vault.get("openai_api_key") or "",
    )
    from .agent import build_system_prompt

    system_prompt = build_system_prompt(
        persona=vault.get("persona_prompt") or "",
        user_name=vault.get("user_name") or "",
    )
    loop = AgentLoop(
        bus, provider, registry, permissions, inbox, audit, notify,
        system_prompt=system_prompt,
    )

    async def reminder_worker() -> None:
        """Fires due reminders — the agent speaks up on its own."""
        from datetime import datetime, timezone

        from .db import db as open_db

        while True:
            await asyncio.sleep(10)
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

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        tasks = [
            asyncio.create_task(loop.run_forever(), name="agent-loop"),
            asyncio.create_task(reminder_worker(), name="reminders"),
        ]
        if telegram is not None:
            await telegram.start()
        if settings.heartbeat_seconds > 0:

            async def heartbeat() -> None:
                while True:
                    await asyncio.sleep(settings.heartbeat_seconds)
                    await bus.publish(
                        Event(type="cron.tick", payload={}, source="cron")
                    )

            tasks.append(asyncio.create_task(heartbeat(), name="heartbeat"))
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

    @app.get("/health")
    async def health() -> dict:
        return {
            "name": NAME,
            "version": __version__,
            "events_pending": bus.pending,
            "telegram": telegram is not None,
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

    @app.get("/permissions")
    async def permissions_all() -> dict:
        levels = permissions.all()
        return {
            t.capability: levels.get(t.capability, "propose")
            for t in registry.all()
        }

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
