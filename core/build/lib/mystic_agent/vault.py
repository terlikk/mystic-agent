"""Encrypted local secret store.

Values are encrypted with Fernet (AES128-CBC + HMAC). The key lives next
to the database with 0600 permissions and never leaves the machine.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet

from .db import db


class Vault:
    def __init__(self, db_path: Path, key_path: Path) -> None:
        self._db_path = db_path
        self._fernet = Fernet(self._load_or_create_key(key_path))

    @staticmethod
    def _load_or_create_key(key_path: Path) -> bytes:
        if key_path.exists():
            return key_path.read_bytes()
        key = Fernet.generate_key()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.write_bytes(key)
        os.chmod(key_path, 0o600)
        return key

    def set(self, name: str, value: str) -> None:
        token = self._fernet.encrypt(value.encode())
        with db(self._db_path) as conn:
            conn.execute(
                "INSERT INTO vault (name, value, updated_at) VALUES (?, ?, ?)"
                " ON CONFLICT(name) DO UPDATE SET value = excluded.value,"
                " updated_at = excluded.updated_at",
                (name, token, datetime.now(timezone.utc).isoformat()),
            )

    def get(self, name: str) -> str | None:
        with db(self._db_path) as conn:
            row = conn.execute(
                "SELECT value FROM vault WHERE name = ?", (name,)
            ).fetchone()
        if row is None:
            return None
        return self._fernet.decrypt(row["value"]).decode()

    def names(self) -> list[str]:
        with db(self._db_path) as conn:
            rows = conn.execute("SELECT name FROM vault ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def delete(self, name: str) -> None:
        with db(self._db_path) as conn:
            conn.execute("DELETE FROM vault WHERE name = ?", (name,))
