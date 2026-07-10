"""The event bus: everything the agent reacts to is an Event.

Sources (telegram, cron, webhooks) publish; the agent loop consumes.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Event:
    type: str  # e.g. "telegram.message", "cron.tick", "decision.approved"
    payload: dict[str, Any]
    source: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    ts: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EventBus:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[Event] = asyncio.Queue()

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)

    async def get(self) -> Event:
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()

    @property
    def pending(self) -> int:
        return self._queue.qsize()
