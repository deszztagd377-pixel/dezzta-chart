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
                CREATE TABLE IF NOT EXISTS ohlcv_overflow_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instrument_hint_json TEXT NOT NULL,
                    start_ns INTEGER NOT NULL,
                    end_ns INTEGER NOT NULL CHECK (end_ns > start_ns),
                    created_at_ns INTEGER NOT NULL,
                    UNIQUE (instrument_hint_json, start_ns, end_ns)
                );
                CREATE INDEX IF NOT EXISTS idx_ohlcv_overflow_journal_created
                ON ohlcv_overflow_journal(created_at_ns, id);
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

    def _mutate_scope(
        self, scope: Hashable, state: str, start_ns: int, end_ns: int,
    ) -> None:
        """Apply a scope mutation against the latest committed DB state.

        BEGIN IMMEDIATE serializes the read/modify/write sequence across
        independent tracker instances and processes sharing this database.
        """
        key = self._scope_key(scope)
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            rows = db.execute(
                """SELECT state,start_ns,end_ns
                FROM ohlcv_coverage_intervals WHERE scope_key=?
                ORDER BY state,start_ns,end_ns""",
                (key,),
            ).fetchall()
            covered = [
                (int(row["start_ns"]), int(row["end_ns"]))
                for row in rows if row["state"] == "covered"
            ]
            gaps = [
                (int(row["start_ns"]), int(row["end_ns"]))
                for row in rows if row["state"] == "gap"
            ]
            meta = db.execute(
                "SELECT int_value FROM ohlcv_coverage_meta WHERE meta_key='truncated'"
            ).fetchone()
            truncated = 0 if meta is None else int(meta["int_value"])

            current = CoverageTracker(max_intervals=self._max)
            current._covered[scope] = covered
            current.truncated = truncated
            if state == "covered":
                CoverageTracker.add_covered(current, scope, start_ns, end_ns)
                covered = current._covered.get(scope, [])
                gaps = self._subtract(gaps, start_ns, end_ns)
                truncated = current.truncated
            else:
                CoverageTracker.add_gap(current, scope, start_ns, end_ns)
                covered = current._covered.get(scope, [])
                gaps = self._merge(gaps, start_ns, end_ns)
                if len(gaps) > self._max:
                    truncated += len(gaps) - self._max
                    gaps = gaps[-self._max:]

            db.execute(
                "DELETE FROM ohlcv_coverage_intervals WHERE scope_key=?", (key,)
            )
            persisted = [
                (key, "covered", start, end) for start, end in covered
            ] + [
                (key, "gap", start, end) for start, end in gaps
            ]
            if persisted:
                db.executemany(
                    """INSERT INTO ohlcv_coverage_intervals
                    (scope_key,state,start_ns,end_ns) VALUES (?,?,?,?)""",
                    persisted,
                )
            db.execute(
                """INSERT INTO ohlcv_coverage_meta(meta_key,int_value)
                VALUES ('truncated', ?)
                ON CONFLICT(meta_key) DO UPDATE SET int_value=excluded.int_value""",
                (truncated,),
            )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

        # Publish the committed snapshot locally only after durable commit.
        self._covered[scope] = list(covered)
        self._gaps[scope] = list(gaps)
        self.truncated = truncated

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
        self._mutate_scope(scope, "covered", start_ns, end_ns)

    def add_gap(self, scope: Hashable, start_ns: int, end_ns: int) -> None:
        if end_ns <= start_ns:
            return
        self._mutate_scope(scope, "gap", start_ns, end_ns)

    def gaps(self, scope: Hashable) -> list[tuple[int, int]]:
        return list(self._gaps.get(scope, []))

    def gap_scopes(self) -> list[Hashable]:
        return [scope for scope, intervals in self._gaps.items() if intervals]

    def _refresh_scope(self, scope: Hashable) -> None:
        """Refresh one scope so long-lived instances observe other writers."""
        key = self._scope_key(scope)
        db = self._connect()
        try:
            rows = db.execute(
                """SELECT state,start_ns,end_ns
                FROM ohlcv_coverage_intervals WHERE scope_key=?
                ORDER BY state,start_ns,end_ns""",
                (key,),
            ).fetchall()
        finally:
            db.close()
        covered = [
            (int(row["start_ns"]), int(row["end_ns"]))
            for row in rows if row["state"] == "covered"
        ]
        gaps = [
            (int(row["start_ns"]), int(row["end_ns"]))
            for row in rows if row["state"] == "gap"
        ]
        if covered:
            self._covered[scope] = covered
        else:
            self._covered.pop(scope, None)
        if gaps:
            self._gaps[scope] = gaps
        else:
            self._gaps.pop(scope, None)

    def intervals(self, scope: Hashable) -> list[tuple[int, int]]:
        self._refresh_scope(scope)
        return super().intervals(scope)

    def status(self, scope: Hashable, start_ns: int, end_ns: int) -> str:
        self._refresh_scope(scope)
        return super().status(scope, start_ns, end_ns)

    def gaps(self, scope: Hashable) -> list[tuple[int, int]]:
        self._refresh_scope(scope)
        return list(self._gaps.get(scope, []))

    def gap_scopes(self) -> list[Hashable]:
        db = self._connect()
        try:
            rows = db.execute(
                """SELECT DISTINCT scope_key FROM ohlcv_coverage_intervals
                WHERE state='gap' ORDER BY scope_key"""
            ).fetchall()
        finally:
            db.close()
        scopes = [tuple(json.loads(row["scope_key"])) for row in rows]
        self._gaps = {}
        for scope in scopes:
            self._refresh_scope(scope)
        return scopes

    def journal_overflow(
        self, instrument_hint: tuple[int, int] | None,
        start_ns: int, end_ns: int, created_at_ns: int,
    ) -> int:
        """Durably record an overflow before attempting coverage mutation."""
        if end_ns <= start_ns:
            raise ValueError("overflow journal end must be greater than start")
        hint_json = json.dumps(
            None if instrument_hint is None else list(instrument_hint),
            separators=(",", ":"), ensure_ascii=True,
        )
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                """INSERT INTO ohlcv_overflow_journal
                (instrument_hint_json,start_ns,end_ns,created_at_ns)
                VALUES (?,?,?,?)
                ON CONFLICT(instrument_hint_json,start_ns,end_ns) DO NOTHING""",
                (hint_json, start_ns, end_ns, created_at_ns),
            )
            row = db.execute(
                """SELECT id FROM ohlcv_overflow_journal
                WHERE instrument_hint_json=? AND start_ns=? AND end_ns=?""",
                (hint_json, start_ns, end_ns),
            ).fetchone()
            db.execute("COMMIT")
            return int(row["id"])
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def pending_overflows(self) -> list[dict[str, object]]:
        """Return durable overflow records in deterministic replay order."""
        db = self._connect()
        try:
            rows = db.execute(
                """SELECT id,instrument_hint_json,start_ns,end_ns,created_at_ns
                FROM ohlcv_overflow_journal ORDER BY created_at_ns,id"""
            ).fetchall()
        finally:
            db.close()
        result = []
        for row in rows:
            hint = json.loads(row["instrument_hint_json"])
            result.append({
                "id": int(row["id"]),
                "instrument_hint": None if hint is None else tuple(int(v) for v in hint),
                "start_ns": int(row["start_ns"]),
                "end_ns": int(row["end_ns"]),
                "created_at_ns": int(row["created_at_ns"]),
            })
        return result

    def resolve_overflow(self, journal_id: int) -> None:
        """Remove a journal record only after its coverage gap is durable."""
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM ohlcv_overflow_journal WHERE id=?", (journal_id,))
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def stats(self) -> dict[str, int]:
        return {
            "scopes": len(set(self._covered) | set(self._gaps)),
            "covered_intervals": sum(len(v) for v in self._covered.values()),
            "gap_intervals": sum(len(v) for v in self._gaps.values()),
            "truncated": self.truncated,
        }
