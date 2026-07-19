"""Telegram gateway: the owner's messages become events; proposals come
back as messages with inline Approve/Reject buttons.
"""

import logging
from typing import Callable

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ..events import Event, EventBus
from ..permissions import DecisionInbox

HELP_TEXT = (
    "Komendy MysticAgent:\n"
    "/brief — podsumowanie: zadania, przypomnienia, kalendarz, poczta\n"
    "/status — co chodzi, ile oczekujących decyzji\n"
    "/pause — wstrzymaj samodzielne akcje  ·  /resume — wznów\n"
    "/skills — lista umiejętności\n"
    "/learn <opis> — naucz agenta nowego narzędzia\n"
    "/permissions — poziomy uprawnień\n"
    "/model — pokaż lub zmień model (np. /model opus)\n\n"
    "Poza tym po prostu pisz (lub nagraj / wyślij zdjęcie) — zajmę się resztą."
)

log = logging.getLogger(__name__)

# friendly shortcuts → full model ids (a full id can also be passed directly)
MODELS = {
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-5",
    "haiku": "claude-haiku-4-5-20251001",
}


class TelegramGateway:
    def __init__(
        self,
        token: str,
        owner_id: int,
        bus: EventBus,
        inbox: DecisionInbox,
        on_claim: Callable[[int], None] | None = None,
        registry=None,
        permissions=None,
        flags=None,
        status_fn=None,
    ) -> None:
        self._owner_id = owner_id
        self._bus = bus
        self._inbox = inbox
        self._on_claim = on_claim
        self._registry = registry
        self._permissions = permissions
        self._flags = flags
        self._status_fn = status_fn
        # wired up by the server after the agent loop exists
        self.on_set_model: Callable[[str], None] | None = None
        self.current_model: Callable[[], str] | None = None
        self._app = Application.builder().token(token).build()
        self._app.add_handler(CommandHandler("help", self._cmd_help))
        self._app.add_handler(CommandHandler("start", self._cmd_help))
        self._app.add_handler(CommandHandler("skills", self._cmd_skills))
        self._app.add_handler(CommandHandler("learn", self._cmd_learn))
        self._app.add_handler(CommandHandler("permissions", self._cmd_permissions))
        self._app.add_handler(CommandHandler("brief", self._cmd_brief))
        self._app.add_handler(CommandHandler("status", self._cmd_status))
        self._app.add_handler(CommandHandler("pause", self._cmd_pause))
        self._app.add_handler(CommandHandler("resume", self._cmd_resume))
        self._app.add_handler(CommandHandler("model", self._cmd_model))
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )
        self._app.add_handler(MessageHandler(filters.PHOTO, self._on_photo))
        self._app.add_handler(MessageHandler(filters.VOICE, self._on_voice))
        self._app.add_handler(CallbackQueryHandler(self._on_button))

    async def start(self) -> None:
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()
        log.info("telegram gateway polling")

    async def stop(self) -> None:
        await self._app.updater.stop()
        await self._app.stop()
        await self._app.shutdown()

    def _is_owner(self, chat_id: int) -> bool:
        # owner_id == 0 → first chat wins (onboarding); otherwise strict match
        if self._owner_id == 0:
            self._owner_id = chat_id
            if self._on_claim is not None:
                self._on_claim(chat_id)  # persist — survives restarts
            log.info("locked to owner chat id %s", chat_id)
            return True
        return chat_id == self._owner_id

    async def _on_message(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if update.message is None or update.message.text is None:
            return
        if not self._is_owner(update.message.chat_id):
            await update.message.reply_text("To prywatny agent — nie dla Ciebie.")
            return
        await self._bus.publish(
            Event(
                type="telegram.message",
                payload={"text": update.message.text},
                source="telegram",
            )
        )

    async def _cmd_help(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message and self._is_owner(update.message.chat_id):
            await update.message.reply_text(HELP_TEXT)

    async def _cmd_skills(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        if self._registry is None:
            await update.message.reply_text("brak rejestru narzędzi")
            return
        lines = [
            f"• {t.name} [{t.capability}] — {t.description}"
            for t in self._registry.all()
        ]
        await update.message.reply_text(
            "Umiejętności:\n" + "\n".join(lines) + "\n\nDodaj: /learn <opis>"
        )

    async def _cmd_permissions(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        if self._registry is None or self._permissions is None:
            return
        caps = sorted({t.capability for t in self._registry.all()})
        lines = [f"• {c}: {self._permissions.get(c).value}" for c in caps]
        await update.message.reply_text("Uprawnienia:\n" + "\n".join(lines))

    async def _cmd_brief(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        await self._bus.publish(
            Event(
                type="automation.run",
                payload={
                    "instruction": "Zrób zwięzły briefing: otwarte zadania,"
                    " dzisiejsze przypomnienia, najbliższe wydarzenia z kalendarza"
                    " i (jeśli masz dostęp) nieprzeczytane maile. Krótko, punktowo.",
                    "context": "",
                },
                source="telegram",
            )
        )

    async def _cmd_status(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        text = self._status_fn() if self._status_fn else "brak danych"
        await update.message.reply_text(text)

    async def _cmd_pause(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        if self._flags:
            self._flags.set_bool("paused", True)
        await update.message.reply_text(
            "⏸ Wstrzymane. Nie podejmę żadnych samodzielnych akcji. /resume by wznowić."
        )

    async def _cmd_resume(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        if self._flags:
            self._flags.set_bool("paused", False)
        await update.message.reply_text("▶️ Wznowione. Znów działam samodzielnie.")

    async def _cmd_model(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        arg = (update.message.text or "").partition(" ")[2].strip().lower()
        cur = self.current_model() if self.current_model else "?"
        if not arg:
            opts = "\n".join(f"  /model {k} → {v}" for k, v in MODELS.items())
            await update.message.reply_text(
                f"Aktualny model: {cur}\n\nZmień:\n{opts}\n\n"
                "Możesz też podać pełną nazwę, np. /model claude-opus-4-8"
            )
            return
        if self.on_set_model is None:
            await update.message.reply_text("Zmiana modelu jest teraz niedostępna.")
            return
        target = MODELS.get(arg, arg)
        try:
            self.on_set_model(target)
        except Exception as exc:  # np. brak klucza do danego dostawcy
            await update.message.reply_text(f"Nie udało się przełączyć: {exc}")
            return
        await update.message.reply_text(
            f"✓ Model ustawiony: {target}\nDziała od następnej wiadomości."
        )

    async def _cmd_learn(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        if not (update.message and self._is_owner(update.message.chat_id)):
            return
        desc = (update.message.text or "").partition(" ")[2].strip()
        if not desc:
            await update.message.reply_text(
                "Napisz co ma umieć, np:\n/learn policz ile dni do podanej daty"
            )
            return
        await self._bus.publish(
            Event(
                type="forge.request",
                payload={"description": desc},
                source="telegram",
            )
        )

    async def _on_photo(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        import tempfile

        if update.message is None or not update.message.photo:
            return
        if not self._is_owner(update.message.chat_id):
            return
        photo = update.message.photo[-1]  # largest size
        tg_file = await photo.get_file()
        path = tempfile.mktemp(prefix="mystic-photo-", suffix=".jpg")
        await tg_file.download_to_drive(path)
        await self._bus.publish(
            Event(
                type="telegram.photo",
                payload={"path": path, "caption": update.message.caption or ""},
                source="telegram",
            )
        )

    async def _on_voice(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        import tempfile

        if update.message is None or update.message.voice is None:
            return
        if not self._is_owner(update.message.chat_id):
            return
        tg_file = await update.message.voice.get_file()
        path = tempfile.mktemp(prefix="mystic-voice-", suffix=".ogg")
        await tg_file.download_to_drive(path)
        await self._bus.publish(
            Event(
                type="telegram.voice",
                payload={"path": path},
                source="telegram",
            )
        )

    async def _on_button(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        if query is None or query.data is None:
            return
        await query.answer()
        action, _, decision_id = query.data.partition(":")
        approved = action == "yes"
        decision = self._inbox.resolve(decision_id, approved)
        if decision is None:
            await query.edit_message_text("Ta propozycja została już rozstrzygnięta.")
            return
        await self._bus.publish(
            Event(
                type="decision.approved" if approved else "decision.rejected",
                payload=decision,
                source="telegram",
            )
        )
        verdict = "✅ zatwierdzone" if approved else "❌ odrzucone"
        await query.edit_message_text(f"{query.message.text}\n\n{verdict}")

    async def send(self, text: str, meta: dict | None = None) -> None:
        """Notifier hook for the agent loop."""
        if self._owner_id == 0:
            log.warning("no owner chat yet — dropping message: %s", text)
            return
        markup = None
        if meta and "decision_id" in meta:
            decision_id = meta["decision_id"]
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✅ Tak", callback_data=f"yes:{decision_id}"),
                        InlineKeyboardButton("❌ Nie", callback_data=f"no:{decision_id}"),
                    ]
                ]
            )
        await self._app.bot.send_message(
            chat_id=self._owner_id, text=text, reply_markup=markup
        )

    async def send_photo(self, path: str, caption: str = "") -> None:
        if self._owner_id == 0:
            log.warning("no owner chat yet — dropping photo")
            return
        with open(path, "rb") as photo:
            await self._app.bot.send_photo(
                chat_id=self._owner_id, photo=photo, caption=caption[:1000]
            )
