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
    "/help — ta pomoc\n"
    "/skills — lista umiejętności\n"
    "/learn <opis> — naucz agenta nowego narzędzia\n"
    "/permissions — poziomy uprawnień\n\n"
    "Poza tym po prostu pisz — zajmę się resztą."
)

log = logging.getLogger(__name__)


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
    ) -> None:
        self._owner_id = owner_id
        self._bus = bus
        self._inbox = inbox
        self._on_claim = on_claim
        self._registry = registry
        self._permissions = permissions
        self._app = Application.builder().token(token).build()
        self._app.add_handler(CommandHandler("help", self._cmd_help))
        self._app.add_handler(CommandHandler("start", self._cmd_help))
        self._app.add_handler(CommandHandler("skills", self._cmd_skills))
        self._app.add_handler(CommandHandler("learn", self._cmd_learn))
        self._app.add_handler(CommandHandler("permissions", self._cmd_permissions))
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )
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
