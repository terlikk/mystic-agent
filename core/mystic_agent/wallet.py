"""Spending guard. A hard ceiling on autonomous spending that sits ON TOP
of the permission system: even if the payment capability is set to act on
its own, nothing above the budget can go through.

Use a capped virtual card as the actual payment method — never a main card.
"""

from datetime import datetime, timezone
from pathlib import Path

from .db import db


class Wallet:
    def __init__(self, path: Path) -> None:
        self._path = path

    def policy(self) -> tuple[float, float, str]:
        with db(self._path) as conn:
            row = conn.execute("SELECT * FROM budget WHERE id = 1").fetchone()
        if row is None:
            return 0.0, 0.0, "PLN"
        return row["per_txn"], row["monthly"], row["currency"]

    def set_policy(self, per_txn: float, monthly: float, currency: str = "PLN") -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO budget (id, per_txn, monthly, currency)"
                " VALUES (1, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET"
                " per_txn = excluded.per_txn, monthly = excluded.monthly,"
                " currency = excluded.currency",
                (per_txn, monthly, currency),
            )

    def spent_this_month(self) -> float:
        prefix = datetime.now(timezone.utc).strftime("%Y-%m")
        with db(self._path) as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) AS s FROM spend_log"
                " WHERE ts LIKE ?",
                (f"{prefix}%",),
            ).fetchone()
        return float(row["s"])

    def check(self, amount: float) -> tuple[bool, str]:
        """Is this amount within the budget ceiling? (permission gate still
        decides whether it also needs a human yes/no)."""
        per_txn, monthly, cur = self.policy()
        if per_txn <= 0:
            return False, "budżet nie ustawiony — ustaw limit lub zatwierdź ręcznie"
        if amount > per_txn:
            return False, f"przekracza limit na transakcję ({per_txn:.2f} {cur})"
        if monthly > 0 and self.spent_this_month() + amount > monthly:
            return False, f"przekracza limit miesięczny ({monthly:.2f} {cur})"
        return True, "w ramach budżetu"

    def record(self, amount: float, merchant: str, url: str = "") -> None:
        with db(self._path) as conn:
            conn.execute(
                "INSERT INTO spend_log (ts, amount, merchant, url)"
                " VALUES (?, ?, ?, ?)",
                (
                    datetime.now(timezone.utc).isoformat(),
                    amount,
                    merchant,
                    url,
                ),
            )
