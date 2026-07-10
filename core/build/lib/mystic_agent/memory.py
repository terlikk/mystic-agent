"""Long-term memory (facts about the user) and short-term conversation
history. Together these turn the agent from a goldfish into an assistant
that remembers who you are and what you were just talking about.
"""

from datetime import datetime, timezone
from pathlib import Path

from .db import db


class Memory:
    """Durable facts the user asked the agent to remember."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def add(self, fact: str) -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO memory (ts, fact) VALUES (?, ?)",
                (datetime.now(timezone.utc).isoformat(), fact.strip()),
            )

    def all(self) -> list[tuple[int, str]]:
        with db(self._path) as conn:
            rows = conn.execute(
                "SELECT id, fact FROM memory ORDER BY id"
            ).fetchall()
        return [(r["id"], r["fact"]) for r in rows]

    def forget(self, fact_id: int) -> None:
        with db(self._path) as conn:
            conn.execute("DELETE FROM memory WHERE id = ?", (fact_id,))

    def recall_block(self, limit: int = 40) -> str:
        facts = self.all()[:limit]
        if not facts:
            return ""
        lines = "\n".join(f"- {fact}" for _, fact in facts)
        return "Co wiesz o użytkowniku (pamięć długotrwała):\n" + lines


class Conversation:
    """Rolling short-term history so follow-ups make sense."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, role: str, content: str) -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO messages (ts, role, content) VALUES (?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), role, content),
            )

    def recent(self, limit: int = 12) -> list[dict[str, str]]:
        with db(self._path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
