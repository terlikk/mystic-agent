"""Tool registry. A tool = an executable capability with a JSON schema.

Skills forged by the agent (stage 4) will register here too.
"""

import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

from .db import db
from .llm import ToolSpec

ToolFunc = Callable[[dict[str, Any]], Awaitable[str]]


@dataclass
class Tool:
    name: str
    capability: str  # permission group, e.g. "notes", "reminders", "web"
    description: str
    parameters: dict[str, Any]  # JSON schema
    func: ToolFunc

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(self.name, self.description, self.parameters)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def specs(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]

    def all(self) -> list[Tool]:
        return list(self._tools.values())


_TAG_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S | re.I)


def builtin_tools(db_path: Path) -> list[Tool]:
    """The starter skill pack: time, persistent notes, reminders, web."""

    async def get_time(_: dict[str, Any]) -> str:
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    async def add_note(args: dict[str, Any]) -> str:
        text = str(args.get("text", "")).strip()
        if not text:
            return "pusta notatka — nic nie zapisano"
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO notes (ts, text) VALUES (?, ?)",
                (datetime.now(timezone.utc).isoformat(), text),
            )
        return f"zapisano notatkę: {text}"

    async def list_notes(_: dict[str, Any]) -> str:
        with db(db_path) as conn:
            rows = conn.execute(
                "SELECT id, text FROM notes ORDER BY id"
            ).fetchall()
        if not rows:
            return "brak notatek"
        return "\n".join(f"{r['id']}. {r['text']}" for r in rows)

    async def remind(args: dict[str, Any]) -> str:
        text = str(args.get("text", "")).strip()
        minutes = float(args.get("minutes", 0))
        if not text or minutes <= 0:
            return "podaj treść i dodatnią liczbę minut"
        due = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        with db(db_path) as conn:
            conn.execute(
                "INSERT INTO reminders (created_at, due_at, text) VALUES (?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    due.isoformat(),
                    text,
                ),
            )
        local = due.astimezone().strftime("%H:%M")
        return f"przypomnę o {local}: {text}"

    async def read_url(args: dict[str, Any]) -> str:
        import httpx

        url = str(args.get("url", ""))
        if not url.startswith(("http://", "https://")):
            return "podaj pełny adres http(s)"
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=20
        ) as client:
            resp = await client.get(url)
        text = _TAG_RE.sub(" ", resp.text)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        return text[:4000] or "(pusta strona)"

    return [
        Tool(
            name="get_time",
            capability="system",
            description="Zwraca aktualną datę i godzinę na maszynie użytkownika.",
            parameters={"type": "object", "properties": {}},
            func=get_time,
        ),
        Tool(
            name="add_note",
            capability="notes",
            description="Zapisuje trwałą notatkę użytkownika.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Treść notatki"}
                },
                "required": ["text"],
            },
            func=add_note,
        ),
        Tool(
            name="list_notes",
            capability="notes",
            description="Wyświetla zapisane notatki użytkownika.",
            parameters={"type": "object", "properties": {}},
            func=list_notes,
        ),
        Tool(
            name="remind",
            capability="reminders",
            description="Ustawia przypomnienie — agent odezwie się na telegramie"
            " po zadanym czasie.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "O czym przypomnieć"},
                    "minutes": {
                        "type": "number",
                        "description": "Za ile minut przypomnieć",
                    },
                },
                "required": ["text", "minutes"],
            },
            func=remind,
        ),
        Tool(
            name="read_url",
            capability="web",
            description="Pobiera stronę WWW i zwraca jej tekst (do researchu"
            " i sprawdzania cen/treści).",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Adres strony"}
                },
                "required": ["url"],
            },
            func=read_url,
        ),
    ]
