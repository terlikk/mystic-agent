"""Permission levels and the decision inbox.

Every capability has a level:
  off         — the agent may not use it at all
  propose     — actions land in the decision inbox and wait for approval
  act_report  — the agent acts, then reports what it did
  act_silent  — the agent acts; details only in the audit log
"""

import json
import uuid
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from .db import db


class Level(StrEnum):
    OFF = "off"
    PROPOSE = "propose"
    ACT_REPORT = "act_report"
    ACT_SILENT = "act_silent"


DEFAULT_LEVEL = Level.PROPOSE


class PermissionStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def get(self, capability: str) -> Level:
        with db(self._path) as conn:
            row = conn.execute(
                "SELECT level FROM permissions WHERE capability = ?",
                (capability,),
            ).fetchone()
        return Level(row["level"]) if row else DEFAULT_LEVEL

    def set(self, capability: str, level: Level) -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO permissions (capability, level) VALUES (?, ?)"
                " ON CONFLICT(capability) DO UPDATE SET level = excluded.level",
                (capability, level.value),
            )

    def all(self) -> dict[str, str]:
        with db(self._path) as conn:
            rows = conn.execute("SELECT * FROM permissions").fetchall()
        return {r["capability"]: r["level"] for r in rows}


class DecisionInbox:
    """Proposed actions waiting for the owner's yes/no."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def propose(
        self, capability: str, tool: str, args: dict[str, Any], reason: str
    ) -> str:
        decision_id = uuid.uuid4().hex[:12]
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO decisions (id, created_at, status, capability,"
                " tool, args_json, reason) VALUES (?, ?, 'pending', ?, ?, ?, ?)",
                (
                    decision_id,
                    datetime.now(timezone.utc).isoformat(),
                    capability,
                    tool,
                    json.dumps(args, ensure_ascii=False),
                    reason,
                ),
            )
        return decision_id

    def resolve(self, decision_id: str, approved: bool) -> dict | None:
        """Mark a pending decision; returns the decision or None if not pending."""
        status = "approved" if approved else "rejected"
        with db(self._path) as conn:
            row = conn.execute(
                "SELECT * FROM decisions WHERE id = ? AND status = 'pending'",
                (decision_id,),
            ).fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE decisions SET status = ?, resolved_at = ? WHERE id = ?",
                (
                    status,
                    datetime.now(timezone.utc).isoformat(),
                    decision_id,
                ),
            )
        decision = dict(row)
        decision["status"] = status
        decision["args"] = json.loads(decision.pop("args_json"))
        return decision

    def pending(self) -> list[dict]:
        with db(self._path) as conn:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE status = 'pending'"
                " ORDER BY created_at"
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["args"] = json.loads(d.pop("args_json"))
            out.append(d)
        return out
