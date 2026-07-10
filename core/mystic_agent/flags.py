"""Tiny key/value flags (e.g. the global pause switch)."""

from pathlib import Path

from .db import db


class Flags:
    def __init__(self, path: Path) -> None:
        self._path = path

    def get_bool(self, key: str) -> bool:
        with db(self._path) as conn:
            row = conn.execute(
                "SELECT value FROM flags WHERE key = ?", (key,)
            ).fetchone()
        return bool(row) and row["value"] == "1"

    def set_bool(self, key: str, value: bool) -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO flags (key, value) VALUES (?, ?)"
                " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, "1" if value else "0"),
            )
