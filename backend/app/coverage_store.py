"""Durable SQLite coverage intervals and explicit ingestion gaps."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Hashable, Iterable

from app.coverage import CoverageTracker


class SQLiteCoverageTracker(CoverageTracker):
    """CoverageTracker backed by additive SQLite interval tables.

    Covered and gap intervals are half-open nanosecond ranges. A successful
    historical query fills its range and removes overlapping gap markers;
    queue overflow carves coverage out and records the affected gap even when
    no prior covered interval exists.
    """

    def __init__(
        self,
        database_path: str,
        max_intervals: int = 5_000,
        *,
        busy_timeout_ms: int = 10_000,
    ) -> None:
        if not isinstance(database_path, str) or not database_path.strip() or database_path == ":memory:":
            raise ValueError("A file-backed database_path is required.")
        if not isinstance(busy_timeout_ms, int) or isinstance(busy_timeout_ms, bool) or busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be positive.")
        super().__init__(max_intervals=max_intervals)
        self.database_path = str(Path(database_path).expanduser())
        self.busy_timeout_ms = busy_timeout_ms
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._gaps: dict[Hashable, list[tuple[int, int]]] = {}
        self._initialize()
        self._restore()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(
            self.database_path, timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        db.row_factory = sqlite3.Row
        db.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        return db

    def _initialize(self) -> None:
        db = self._connect()
        try:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS ohlcv_coverage_intervals (
                    scope_key TEXT NOT NULL,
                    state TEXT NOT NULL CHECK (state IN ('covered', 'gap')),
                    start_ns INTEGER NOT NULL,
                    end_ns INTEGER NOT NULL CHECK (end_ns > start_ns),
                    PRIMARY KEY (scope_key, state, start_ns, end_ns)
                );
                CREATE INDEX IF NOT EXISTS idx_ohlcv_coverage_scope
                ON ohlcv_coverage_intervals(scope_key, state, start_ns, end_ns);
                CREATE TABLE IF NOT EXISTS ohlcv_coverage_meta (
                    meta_key TEXT PRIMARY KEY NOT NULL,
                    int_value INTEGER NOT NULL
                );
                """
            )
        finally:
            db.close()

    @staticmethod
    def _scope_key(scope: Hashable) -> str:
        if not isinstance(scope, (tuple, list)) or not scope:
            raise ValueError("coverage scope must be a non-empty tuple or list.")
        try:
            return json.dumps(list(scope), separators=(",", ":"), ensure_ascii=True)
        except (TypeError, ValueError) as exc:
            raise ValueError("coverage scope must contain JSON scalar values.") from exc

    @staticmethod
    def _merge(intervals: Iterable[tuple[int, int]], start_ns: int, end_ns: int) -> list[tuple[int, int]]:
        merged: list[tuple[int, int]] = []
        a, b = start_ns, end_ns
        for start, end in intervals:
            if end < a or start > b:
                merged.append((start, end))
            else:
                a, b = min(a, start), max(b, end)
        merged.append((a, b))
        merged.sort()
        return merged

    @staticmethod
    def _subtract(intervals: Iterable[tuple[int, int]], start_ns: int, end_ns: int) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        for start, end in intervals:
            if end <= start_ns or start >= end_ns:
                result.append((start, end))
                continue
            if start < start_ns:
                result.append((start, start_ns))
            if end > end_ns:
                result.append((end_ns, end))
        return result

    def _persist_scope(self, scope: Hashable) -> None:
        key = self._scope_key(scope)
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM ohlcv_coverage_intervals WHERE scope_key=?", (key,))
            rows = [
                (key, "covered", start, end)
                for start, end in self._covered.get(scope, [])
            ] + [
                (key, "gap", start, end)
                for start, end in self._gaps.get(scope, [])
            ]
            if rows:
                db.executemany(
                    """INSERT INTO ohlcv_coverage_intervals
                    (scope_key,state,start_ns,end_ns) VALUES (?,?,?,?)""",
                    rows,
                )
            db.execute(
                """INSERT INTO ohlcv_coverage_meta(meta_key,int_value)
                VALUES ('truncated', ?)
                ON CONFLICT(meta_key) DO UPDATE SET int_value=excluded.int_value""",
                (self.truncated,),
            )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def _restore(self) -> None:
        db = self._connect()
        try:
            rows = db.execute(
                """SELECT scope_key,state,start_ns,end_ns
                FROM ohlcv_coverage_intervals
                ORDER BY scope_key,state,start_ns"""
            ).fetchall()
            meta = db.execute(
                "SELECT int_value FROM ohlcv_coverage_meta WHERE meta_key='truncated'"
            ).fetchone()
        finally:
            db.close()
        for row in rows:
            scope = tuple(json.loads(row["scope_key"]))
            interval = (int(row["start_ns"]), int(row["end_ns"]))
            if row["state"] == "covered":
                super().add_covered(scope, *interval)
            else:
                self._gaps[scope] = self._merge(
                    self._gaps.get(scope, []), *interval
                )
        if meta is not None:
            self.truncated = int(meta["int_value"])

    def add_covered(self, scope: Hashable, start_ns: int, end_ns: int) -> None:
        if end_ns <= start_ns:
            return
        old_covered = list(self._covered.get(scope, []))
        old_gaps = list(self._gaps.get(scope, []))
        old_truncated = self.truncated
        super().add_covered(scope, start_ns, end_ns)
        self._gaps[scope] = self._subtract(old_gaps, start_ns, end_ns)
        try:
            self._persist_scope(scope)
        except Exception:
            self._covered[scope] = old_covered
            self._gaps[scope] = old_gaps
            self.truncated = old_truncated
            raise

    def add_gap(self, scope: Hashable, start_ns: int, end_ns: int) -> None:
        if end_ns <= start_ns:
            return
        old_covered = list(self._covered.get(scope, []))
        old_gaps = list(self._gaps.get(scope, []))
        old_truncated = self.truncated
        super().add_gap(scope, start_ns, end_ns)
        merged_gaps = self._merge(old_gaps, start_ns, end_ns)
        if len(merged_gaps) > self._max:
            self.truncated += len(merged_gaps) - self._max
            merged_gaps = merged_gaps[-self._max:]
        self._gaps[scope] = merged_gaps
        try:
            self._persist_scope(scope)
        except Exception:
            self._covered[scope] = old_covered
            self._gaps[scope] = old_gaps
            self.truncated = old_truncated
            raise

    def gaps(self, scope: Hashable) -> list[tuple[int, int]]:
        return list(self._gaps.get(scope, []))

    def gap_scopes(self) -> list[Hashable]:
        return [scope for scope, intervals in self._gaps.items() if intervals]

    def stats(self) -> dict[str, int]:
        return {
            "scopes": len(set(self._covered) | set(self._gaps)),
            "covered_intervals": sum(len(v) for v in self._covered.values()),
            "gap_intervals": sum(len(v) for v in self._gaps.values()),
            "truncated": self.truncated,
        }
