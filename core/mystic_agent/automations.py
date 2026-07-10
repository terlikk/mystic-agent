"""Standing instructions the agent runs on its own — the proactive core.

kind = "schedule": run the instruction on a daily time or every N minutes
kind = "email":    run the instruction for each NEW incoming email
kind = "url":      run the instruction when a watched page changes
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .db import db


class AutomationStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def add(self, kind: str, instruction: str, spec: dict, state: dict | None = None) -> int:
        with db(self._path) as conn:
            cur = conn.execute(
                "INSERT INTO automations (created_at, kind, instruction, spec_json,"
                " state_json) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    kind,
                    instruction,
                    json.dumps(spec, ensure_ascii=False),
                    json.dumps(state or {}, ensure_ascii=False),
                ),
            )
            return cur.lastrowid

    def enabled(self) -> list[dict]:
        with db(self._path) as conn:
            rows = conn.execute(
                "SELECT * FROM automations WHERE enabled = 1 ORDER BY id"
            ).fetchall()
        return [self._row(r) for r in rows]

    def all(self) -> list[dict]:
        with db(self._path) as conn:
            rows = conn.execute("SELECT * FROM automations ORDER BY id").fetchall()
        return [self._row(r) for r in rows]

    def set_state(self, automation_id: int, state: dict) -> None:
        with db(self._path) as conn:
            conn.execute(
                "UPDATE automations SET state_json = ? WHERE id = ?",
                (json.dumps(state, ensure_ascii=False), automation_id),
            )

    def disable(self, automation_id: int) -> bool:
        with db(self._path) as conn:
            cur = conn.execute(
                "UPDATE automations SET enabled = 0 WHERE id = ? AND enabled = 1",
                (automation_id,),
            )
            return cur.rowcount > 0

    @staticmethod
    def _row(r) -> dict:
        return {
            "id": r["id"],
            "kind": r["kind"],
            "instruction": r["instruction"],
            "spec": json.loads(r["spec_json"]),
            "state": json.loads(r["state_json"]),
        }
