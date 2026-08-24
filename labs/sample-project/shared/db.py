"""Tiny in-memory stand-in for a real connection pool.

This module is orderflow's god node: every service imports it.
"""
from collections import defaultdict


class DatabasePool:
    """A fake pool storing rows per table in memory."""

    def __init__(self) -> None:
        self.tables: dict[str, list[dict]] = defaultdict(list)

    def execute(self, table: str, row: dict) -> None:
        if not isinstance(row, dict):
            raise TypeError(f"row must be a dict, got {type(row).__name__}")
        self.tables[table].append(row)

    def query(self, table: str, **filters) -> list[dict]:
        rows = self.tables.get(table, [])
        return [r for r in rows if all(r.get(k) == v for k, v in filters.items())]


POOL = DatabasePool()
