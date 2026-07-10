"""The scheduler: ticks periodically and turns standing automations into
`automation.run` events. The agent then executes each instruction on its
own, with every action still passing through the permission gate.
"""

import hashlib
import logging
from datetime import datetime, time, timedelta, timezone

from .automations import AutomationStore
from .events import Event, EventBus

log = logging.getLogger(__name__)


def _parse_hhmm(value: str) -> time | None:
    try:
        hh, mm = value.split(":")
        return time(int(hh), int(mm))
    except (ValueError, AttributeError):
        return None


def _next_daily(at: time, now: datetime) -> datetime:
    candidate = now.replace(
        hour=at.hour, minute=at.minute, second=0, microsecond=0
    )
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


class Scheduler:
    def __init__(
        self,
        store: AutomationStore,
        bus: EventBus,
        mailbox=None,
        fetch_url=None,
    ) -> None:
        self._store = store
        self._bus = bus
        self._mailbox = mailbox
        self._fetch_url = fetch_url  # async (url) -> str

    async def tick(self, now: datetime | None = None) -> int:
        """Run one pass. Returns the number of automation.run events fired."""
        now = now or datetime.now(timezone.utc)
        fired = 0
        for auto in self._store.enabled():
            try:
                fired += await self._handle(auto, now)
            except Exception:  # never let one automation kill the loop
                log.exception("automation %s failed", auto["id"])
        return fired

    async def _handle(self, auto: dict, now: datetime) -> int:
        kind = auto["kind"]
        if kind == "schedule":
            return await self._schedule(auto, now)
        if kind == "email":
            return await self._email(auto)
        if kind == "url":
            return await self._url(auto, now)
        return 0

    async def _schedule(self, auto: dict, now: datetime) -> int:
        spec, state = auto["spec"], auto["state"]
        next_due = state.get("next_due")
        if next_due is None:
            state["next_due"] = self._compute_next(spec, now).isoformat()
            self._store.set_state(auto["id"], state)
            return 0
        if datetime.fromisoformat(next_due) > now:
            return 0
        await self._fire(auto["instruction"], "")
        state["next_due"] = self._compute_next(spec, now).isoformat()
        self._store.set_state(auto["id"], state)
        return 1

    @staticmethod
    def _compute_next(spec: dict, now: datetime) -> datetime:
        at = _parse_hhmm(spec.get("at", ""))
        if at is not None:
            return _next_daily(at, now)
        minutes = int(spec.get("every_minutes", 60))
        return now + timedelta(minutes=max(1, minutes))

    async def _email(self, auto: dict) -> int:
        if self._mailbox is None:
            return 0
        state = auto["state"]
        last_uid = int(state.get("last_uid", -1))
        if last_uid < 0:
            # first run: baseline to current max so we don't reply to history
            state["last_uid"] = self._mailbox.max_uid()
            self._store.set_state(auto["id"], state)
            return 0
        sender = auto["spec"].get("sender", "")
        new, max_uid = self._mailbox.fetch_new(last_uid)
        fired = 0
        for mail in new:
            if sender and sender.lower() not in mail["from"].lower():
                continue
            context = (
                f"Nowy e-mail.\nOd: {mail['from']}\nTemat: {mail['subject']}\n\n"
                f"{mail['body'][:2500]}"
            )
            await self._fire(auto["instruction"], context)
            fired += 1
        if max_uid != last_uid:
            state["last_uid"] = max_uid
            self._store.set_state(auto["id"], state)
        return fired

    async def _url(self, auto: dict, now: datetime) -> int:
        if self._fetch_url is None:
            return 0
        spec, state = auto["spec"], auto["state"]
        next_due = state.get("next_due")
        if next_due and datetime.fromisoformat(next_due) > now:
            return 0
        minutes = int(spec.get("every_minutes", 60))
        state["next_due"] = (now + timedelta(minutes=max(1, minutes))).isoformat()
        content = await self._fetch_url(spec["url"])
        digest = hashlib.sha256(content.encode("utf-8", "replace")).hexdigest()
        fired = 0
        if state.get("last_hash") and state["last_hash"] != digest:
            await self._fire(
                auto["instruction"],
                f"Strona {spec['url']} się zmieniła.\n\n{content[:2500]}",
            )
            fired = 1
        state["last_hash"] = digest
        self._store.set_state(auto["id"], state)
        return fired

    async def _fire(self, instruction: str, context: str) -> None:
        await self._bus.publish(
            Event(
                type="automation.run",
                payload={"instruction": instruction, "context": context},
                source="scheduler",
            )
        )
