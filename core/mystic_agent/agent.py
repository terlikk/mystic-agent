"""The agent loop: event → LLM decides → permission gate → tool → audit.

Proposals don't block the loop — they wait in the decision inbox and are
executed when a `decision.approved` event arrives.
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable

from .audit import AuditLog
from .branding import NAME
from .events import Event, EventBus
from .llm import LLMProvider, ToolCall
from .permissions import DecisionInbox, Level, PermissionStore
from .tools import ToolRegistry

log = logging.getLogger(__name__)

Notifier = Callable[[str, dict[str, Any] | None], Awaitable[None]]

BASE_PROMPT = f"""Jesteś {NAME} — osobistym, self-hosted asystentem AI \
użytkownika. Działasz na jego komputerze, komunikujesz się po polsku, \
krótko i konkretnie. Gdy zadanie pasuje do któregoś z narzędzi, użyj go. \
Gdy nie — odpowiedz tekstem. Nigdy nie zmyślaj wyników narzędzi."""


def build_system_prompt(persona: str = "", user_name: str = "") -> str:
    parts = [BASE_PROMPT]
    if persona:
        parts.append(persona)
    if user_name:
        parts.append(f"Do użytkownika zwracaj się: {user_name}.")
    return "\n\n".join(parts)

MAX_STEPS = 12  # hard cap per event: decide→act→observe iterations
               # (multi-step web tasks like a booking need several)


class AgentLoop:
    def __init__(
        self,
        bus: EventBus,
        provider: LLMProvider,
        tools: ToolRegistry,
        permissions: PermissionStore,
        inbox: DecisionInbox,
        audit: AuditLog,
        notify: Notifier,
        system_prompt: str | None = None,
        forge=None,
        skills_dir=None,
        memory=None,
        conversation=None,
        flags=None,
    ) -> None:
        self.bus = bus
        self.provider = provider
        self.tools = tools
        self.permissions = permissions
        self.inbox = inbox
        self.audit = audit
        self.notify = notify
        self.system_prompt = system_prompt or build_system_prompt()
        self.forge = forge
        self.skills_dir = skills_dir
        self.memory = memory
        self.conversation = conversation
        self.flags = flags
        self._proposed = False

    def is_paused(self) -> bool:
        return self.flags is not None and self.flags.get_bool("paused")

    async def run_forever(self) -> None:
        log.info("agent loop started")
        while True:
            event = await self.bus.get()
            try:
                await self.handle(event)
            except Exception:  # keep the loop alive no matter what
                log.exception("error handling event %s", event.type)
                self.audit.record(
                    "system", "event.error", event.payload, "exception",
                    f"unhandled error for {event.type}",
                )
            finally:
                self.bus.task_done()

    async def handle(self, event: Event) -> None:
        if event.type == "telegram.message":
            await self._converse(event.payload["text"])
        elif event.type == "telegram.photo":
            await self._handle_photo(
                event.payload["path"], event.payload.get("caption", "")
            )
        elif event.type == "telegram.voice":
            await self._handle_voice(event.payload["path"])
        elif event.type == "decision.approved":
            await self._execute_approved(event.payload)
        elif event.type == "decision.rejected":
            self.audit.record(
                "user", "decision.rejected", event.payload, "skipped",
                "użytkownik odrzucił propozycję", event.payload.get("id"),
            )
        elif event.type == "forge.request":
            await self._forge_skill(event.payload["description"])
        elif event.type == "automation.run":
            if self.is_paused():
                log.info("paused — skipping automation")
                return
            await self.run_instruction(
                event.payload["instruction"], event.payload.get("context", "")
            )
        elif event.type == "cron.tick":
            pass  # watchers will hook in here (stage 2+)
        else:
            log.debug("ignoring event type %s", event.type)

    async def _forge_skill(self, description: str) -> None:
        if self.forge is None:
            await self.notify("Kuźnia narzędzi jest niedostępna.", None)
            return
        await self.notify(f"🛠 Kuję narzędzie: {description} …", None)
        result = await self.forge.forge(description)
        if not result.ok:
            await self.notify(f"Nie udało się: {result.error}", None)
            self.audit.record(
                "agent", "forge.failed", description, result.error, "kuźnia"
            )
            return
        decision_id = self.inbox.propose(
            "forge", "__forge__",
            {"name": result.name, "code": result.code, "description": description},
            f"nowe narzędzie '{result.name}' — przeszło samotest w sandboxie",
        )
        self.audit.record(
            "agent", "forge.proposed", description, result.name,
            "narzędzie czeka na akceptację", decision_id,
        )
        preview = result.code[:900]
        await self.notify(
            f"🛠 Gotowe narzędzie: {result.name}\nSamotest w sandboxie: ✓\n\n"
            f"```\n{preview}\n```\nZarejestrować na stałe?",
            {"decision_id": decision_id},
        )

    async def _handle_photo(self, path: str, caption: str) -> None:
        import base64
        import os

        try:
            with open(path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode()
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        describe = getattr(self.provider, "describe_image", None)
        if describe is None:
            await self.notify("Ten model nie obsługuje zdjęć.", None)
            return
        prompt = (
            "Opisz dokładnie, co jest na obrazie. Jeśli to dokument, paragon,"
            " faktura lub tekst — przepisz kluczowe dane i kwoty."
        )
        try:
            seen = await describe(image_b64, prompt)
        except Exception:
            log.exception("vision failed")
            await self.notify("Nie udało mi się odczytać zdjęcia.", None)
            return
        self.audit.record("agent", "vision", caption or "(zdjęcie)", seen[:400], "odczyt obrazu")
        user_text = (
            f"[Użytkownik przysłał zdjęcie. Jego treść:]\n{seen}\n\n"
            f"{caption or 'Co z tym zrobić?'}"
        )
        await self._converse(user_text)

    async def _handle_voice(self, path: str) -> None:
        import os

        from .transcription import transcribe

        openai_key = getattr(self, "_openai_key", "")
        try:
            text = await transcribe(path, openai_key)
        except Exception:
            log.exception("transcription failed")
            text = None
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        if not text:
            await self.notify(
                "Nie mam obsługi głosu. Zainstaluj: pip install"
                ' "mystic-agent[voice]" (lub podaj klucz OpenAI).',
                None,
            )
            return
        self.audit.record("user", "voice", "(nagranie)", text, "transkrypcja")
        await self.notify(f"🎙 „{text}”", None)
        await self._converse(text)

    def _effective_system(self) -> str:
        prompt = self.system_prompt
        if self.memory is not None:
            block = self.memory.recall_block()
            if block:
                prompt = f"{prompt}\n\n{block}"
        return prompt

    async def _converse(self, user_text: str) -> None:
        history: list[dict[str, Any]] = (
            self.conversation.recent() if self.conversation is not None else []
        )
        messages: list[dict[str, Any]] = [
            *history,
            {"role": "user", "content": user_text},
        ]
        if self.conversation is not None:
            self.conversation.append("user", user_text)
        system = self._effective_system()
        self._proposed = False
        for _ in range(MAX_STEPS):
            reply = await self.provider.chat(
                system, messages, self.tools.specs()
            )
            if not reply.tool_calls:
                if reply.text:
                    await self.notify(reply.text, None)
                    if self.conversation is not None:
                        self.conversation.append("assistant", reply.text)
                    self.audit.record(
                        "agent", "reply", user_text, reply.text, "odpowiedź tekstowa"
                    )
                return

            # feed tool results back so the model can continue
            results: list[str] = []
            for call in reply.tool_calls:
                result = await self._dispatch(call, context=user_text)
                results.append(f"{call.name}: {result}")
            # if something is now waiting on the owner, stop — don't re-ask
            if self._proposed:
                return
            messages.append(
                {"role": "assistant", "content": reply.text or "(używam narzędzi)"}
            )
            messages.append(
                {"role": "user", "content": "Wyniki narzędzi:\n" + "\n".join(results)}
            )

    async def run_instruction(self, instruction: str, context: str = "") -> None:
        """Execute a standing instruction autonomously (from the scheduler).
        Actions still go through the permission gate, so a 'propose'-level
        send lands in the decision inbox instead of firing silently."""
        text = f"[ZADANIE AUTOMATYCZNE] {instruction}"
        if context:
            text += f"\n\nKontekst:\n{context}"
        messages: list[dict[str, Any]] = [{"role": "user", "content": text}]
        system = self._effective_system()
        self._proposed = False
        for _ in range(MAX_STEPS):
            reply = await self.provider.chat(system, messages, self.tools.specs())
            if not reply.tool_calls:
                if reply.text:
                    await self.notify(reply.text, None)
                    self.audit.record(
                        "agent", "autonomous", instruction, reply.text,
                        "zadanie automatyczne",
                    )
                return
            results: list[str] = []
            for call in reply.tool_calls:
                result = await self._dispatch(call, context=instruction)
                results.append(f"{call.name}: {result}")
            if self._proposed:
                return
            messages.append(
                {"role": "assistant", "content": reply.text or "(używam narzędzi)"}
            )
            messages.append(
                {"role": "user", "content": "Wyniki narzędzi:\n" + "\n".join(results)}
            )

    async def _dispatch(self, call: ToolCall, context: str) -> str:
        tool = self.tools.get(call.name)
        if tool is None:
            return f"nieznane narzędzie {call.name}"

        level = self.permissions.get(tool.capability)

        if level == Level.OFF:
            self.audit.record(
                "agent", f"tool.blocked:{tool.name}", call.args, "off",
                f"zdolność '{tool.capability}' jest wyłączona",
            )
            return f"zdolność '{tool.capability}' jest wyłączona przez użytkownika"

        if level == Level.PROPOSE:
            decision_id = self.inbox.propose(
                tool.capability, tool.name, call.args, context
            )
            self.audit.record(
                "agent", f"tool.proposed:{tool.name}", call.args, "pending",
                "akcja czeka w skrzynce decyzji", decision_id,
            )
            await self.notify(
                f"Proponuję: {tool.name} {call.args}\nPowód: {context}",
                {"decision_id": decision_id},
            )
            self._proposed = True
            return "propozycja wysłana do użytkownika — czekam na decyzję"

        result = await tool.func(call.args)
        self.audit.record(
            "agent", f"tool.executed:{tool.name}", call.args, result,
            f"poziom uprawnień: {level.value}",
        )
        if level == Level.ACT_REPORT:
            await self.notify(f"✓ {tool.name}: {result}", None)
        return result

    async def _execute_approved(self, decision: dict[str, Any]) -> None:
        if decision["tool"] == "__forge__":
            await self._register_forged(decision)
            return
        tool = self.tools.get(decision["tool"])
        if tool is None:
            return
        result = await tool.func(decision["args"])
        self.audit.record(
            "agent", f"tool.executed:{tool.name}", decision["args"], result,
            "wykonano po zgodzie użytkownika", decision["id"],
        )
        await self.notify(f"✓ zatwierdzone i wykonane — {tool.name}: {result}", None)

    async def _register_forged(self, decision: dict[str, Any]) -> None:
        from .skills_loader import load_one

        args = decision["args"]
        name = args["name"]
        path = self.skills_dir / f"{name}.py"
        path.write_text(args["code"], encoding="utf-8")
        tool = await load_one(path)
        if tool is None:
            await self.notify(f"Nie udało się załadować {name}.", None)
            return
        self.tools.register(tool)
        self.audit.record(
            "agent", "forge.registered", name, str(path),
            "narzędzie zarejestrowane po zgodzie użytkownika", decision["id"],
        )
        await self.notify(
            f"✓ Nauczyłem się: {name}. Możesz już go używać "
            f"(uprawnienie '{tool.capability}').",
            None,
        )
