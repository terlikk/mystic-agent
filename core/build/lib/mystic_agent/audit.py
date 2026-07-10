import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .db import db


class AuditLog:
    """Every action the agent takes is written here — no exceptions."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def record(
        self,
        actor: str,
        action: str,
        input_: Any,
        output: Any,
        reason: str,
        decision_id: str | None = None,
    ) -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO audit (ts, actor, action, input, output, reason,"
                " decision_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    actor,
                    action,
                    json.dumps(input_, ensure_ascii=False, default=str),
                    json.dumps(output, ensure_ascii=False, default=str),
                    reason,
                    decision_id,
                ),
            )

    def recent(self, limit: int = 50) -> list[dict]:
        with db(self._path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
