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


# New/unknown capabilities ask by default; known low-risk ones don't, so
# the agent doesn't nag about harmless things like a web search.
DEFAULT_LEVEL = Level.PROPOSE

CAPABILITY_DEFAULTS: dict[str, "Level"] = {
    "system": Level.ACT_SILENT,     # clock — read only
    "web": Level.ACT_SILENT,        # search / read pages — read only
    "notes": Level.ACT_SILENT,
    "memory": Level.ACT_SILENT,
    "files": Level.ACT_SILENT,      # reading local files
    "contacts": Level.ACT_SILENT,
    "tasks": Level.ACT_SILENT,
    "files_write": Level.ACT_REPORT,  # writing to disk — tell the owner
    "reminders": Level.ACT_REPORT,
    "calendar": Level.ACT_REPORT,
    "automations": Level.ACT_REPORT,
    "email_read": Level.ACT_REPORT,
    "browser": Level.ACT_REPORT,    # shows screenshots as it works
    "email_send": Level.PROPOSE,    # consequential — always ask
    "shell": Level.PROPOSE,
    "payment": Level.PROPOSE,
}


class PermissionStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def get(self, capability: str) -> Level:
        with db(self._path) as conn:
            row = conn.execute(
                "SELECT level FROM permissions WHERE capability = ?",
                (capability,),
            ).fetchone()
        if row:
            return Level(row["level"])
        return CAPABILITY_DEFAULTS.get(capability, DEFAULT_LEVEL)

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
