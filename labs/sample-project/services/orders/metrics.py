"""Canonical metric computations for orders-service.

weekly_active_users (WAU): unique customers with >= 1 completed order in a
rolling 7-day window, EXCLUDING internal test accounts. This is the attested
computation the OKF concept analytics/metrics/weekly_active_users documents —
if you change this logic, update the concept file (M08 teaches the hook that
enforces that).
"""
from datetime import datetime, timedelta, timezone

from shared.db import POOL

INTERNAL_TESTERS = {"cust_qa_1", "cust_qa_2", "cust_loadtest"}


def weekly_active_users(as_of: datetime | None = None) -> int:
    as_of = as_of or datetime.now(timezone.utc)
    window_start = as_of - timedelta(days=7)

    active: set[str] = set()
    for row in POOL.tables.get("orders_fact", []):
        try:
            completed = datetime.fromisoformat(row["completed_at"])
        except (KeyError, ValueError):
            continue  # malformed fact rows must not break the metric
        if window_start <= completed <= as_of and row["customer_id"] not in INTERNAL_TESTERS:
            active.add(row["customer_id"])
    return len(active)
