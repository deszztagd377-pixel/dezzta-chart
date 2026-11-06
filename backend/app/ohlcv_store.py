"""Durable SQLite persistence for normalized OHLCV bars.

Bar identity is provider + dataset + publisher + instrument + series type +
timeframe + bucket start. Prices and volume are stored as exact decimal text;
all event/receive timestamps remain integer nanoseconds.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sqlite3
from typing import Mapping

from app.ohlcv import (
    DEFAULT_RETENTION,
    MIN_RETENTION,
    OhlcvBar,
    SUPPORTED_TIMEFRAMES,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS ohlcv_bars (
    provider TEXT NOT NULL,
    dataset TEXT NOT NULL,
    publisher_id INTEGER NOT NULL,
    instrument_id INTEGER NOT NULL,
    series_type TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    ts_start_ns INTEGER NOT NULL,
    raw_symbol TEXT NOT NULL,
    open TEXT NOT NULL,
    high TEXT NOT NULL,
    low TEXT NOT NULL,
    close TEXT NOT NULL,
    volume TEXT NOT NULL,
    ts_event_ns INTEGER NOT NULL,
    ts_received_ns INTEGER NOT NULL,
    sequence INTEGER NOT NULL,
    sequence_origin TEXT NOT NULL,
    origin TEXT NOT NULL,
    completeness TEXT NOT NULL,
    ts_provider_out_ns INTEGER,
    bucket_policy TEXT NOT NULL DEFAULT 'UTC_LEGACY',
    calendar_id TEXT NOT NULL DEFAULT '',
    calendar_version TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (
        provider, dataset, publisher_id, instrument_id,
        series_type, timeframe, ts_start_ns, bucket_policy,
        calendar_id, calendar_version
    )
);
CREATE INDEX IF NOT EXISTS idx_ohlcv_series_time
ON ohlcv_bars(provider, dataset, publisher_id, instrument_id,
              series_type, raw_symbol, timeframe, bucket_policy,
              calendar_id, calendar_version, ts_start_ns);
CREATE TABLE IF NOT EXISTS ohlcv_store_state (
    state_key TEXT PRIMARY KEY NOT NULL,
    int_value INTEGER NOT NULL
);
"""

_BUCKET_POLICY = "UTC_LEGACY"
_CALENDAR_ID = ""
_CALENDAR_VERSION = ""
_OHLCV_SCHEMA_VERSION = 2


class SQLiteOhlcvStore:
    """Transaction-safe bounded bar store sharing the registry SQLite file."""

    def __init__(
        self,
        database_path: str,
        *,
        retention: Mapping[str, int] | None = None,
        busy_timeout_ms: int = 10_000,
    ) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable OHLCV.")
        if not isinstance(busy_timeout_ms, int) or isinstance(busy_timeout_ms, bool) or busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be a positive integer.")
        self.database_path = str(Path(database_path).expanduser())
        self.busy_timeout_ms = busy_timeout_ms
        self.retention = dict(DEFAULT_RETENTION)
        for timeframe, cap in (retention or {}).items():
            if timeframe not in SUPPORTED_TIMEFRAMES or not isinstance(cap, int) or isinstance(cap, bool) or cap < MIN_RETENTION[timeframe]:
                raise ValueError(f"Invalid retention for {timeframe!r}.")
            self.retention[timeframe] = cap
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(
            self.database_path, timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        db.row_factory = sqlite3.Row
        db.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def _initialize(self) -> None:
        """Create or transactionally migrate the OHLCV schema.

        This schema version is independent from PRAGMA user_version, which is
        owned by the shared instrument registry.
        """
        db = self._connect()
        try:
            db.execute("PRAGMA journal_mode = WAL")
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_schema_meta (
                    schema_key TEXT PRIMARY KEY NOT NULL,
                    schema_version INTEGER NOT NULL
                )"""
            )
            meta = db.execute(
                "SELECT schema_version FROM ohlcv_schema_meta WHERE schema_key='ohlcv'"
            ).fetchone()
            version = 0 if meta is None else int(meta["schema_version"])
            if version > _OHLCV_SCHEMA_VERSION:
                raise RuntimeError(
                    f"OHLCV schema version {version} is newer than supported "
                    f"{_OHLCV_SCHEMA_VERSION}."
                )

            table = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='ohlcv_bars'"
            ).fetchone()
            create_bars_sql = _SCHEMA.split("CREATE INDEX")[0].strip()
            if table is None:
                db.execute(create_bars_sql)
            else:
                columns = {
                    row["name"] for row in db.execute("PRAGMA table_info(ohlcv_bars)")
                }
                policy_columns = {"bucket_policy", "calendar_id", "calendar_version"}
                if not policy_columns.issubset(columns):
                    legacy_columns = {
                        "provider", "dataset", "publisher_id", "instrument_id",
                        "series_type", "timeframe", "ts_start_ns", "raw_symbol",
                        "open", "high", "low", "close", "volume", "ts_event_ns",
                        "ts_received_ns", "sequence", "sequence_origin", "origin",
                        "completeness", "ts_provider_out_ns",
                    }
                    missing = legacy_columns - columns
                    if missing:
                        raise RuntimeError(
                            "Cannot migrate OHLCV table; missing legacy columns: "
                            + ", ".join(sorted(missing))
                        )
                    db.execute("DROP INDEX IF EXISTS idx_ohlcv_series_time")
                    db.execute("ALTER TABLE ohlcv_bars RENAME TO ohlcv_bars_legacy_v1")
                    db.execute(create_bars_sql)
                    db.execute(
                        """INSERT INTO ohlcv_bars (
                            provider,dataset,publisher_id,instrument_id,series_type,
                            timeframe,ts_start_ns,raw_symbol,open,high,low,close,volume,
                            ts_event_ns,ts_received_ns,sequence,sequence_origin,origin,
                            completeness,ts_provider_out_ns,bucket_policy,calendar_id,
                            calendar_version
                        )
                        SELECT provider,dataset,publisher_id,instrument_id,series_type,
                            timeframe,ts_start_ns,raw_symbol,open,high,low,close,volume,
                            ts_event_ns,ts_received_ns,sequence,sequence_origin,origin,
                            completeness,ts_provider_out_ns,'UTC_LEGACY','',''
                        FROM ohlcv_bars_legacy_v1"""
                    )
                    db.execute("DROP TABLE ohlcv_bars_legacy_v1")

            db.execute(
                """CREATE INDEX IF NOT EXISTS idx_ohlcv_series_time
                ON ohlcv_bars(provider, dataset, publisher_id, instrument_id,
                    series_type, raw_symbol, timeframe, bucket_policy,
                    calendar_id, calendar_version, ts_start_ns)"""
            )
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_store_state (
                    state_key TEXT PRIMARY KEY NOT NULL,
                    int_value INTEGER NOT NULL
                )"""
            )
            db.execute(
                """INSERT INTO ohlcv_schema_meta(schema_key, schema_version)
                VALUES ('ohlcv', ?)
                ON CONFLICT(schema_key) DO UPDATE SET
                    schema_version=excluded.schema_version""",
                (_OHLCV_SCHEMA_VERSION,),
            )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> OhlcvBar:
        return OhlcvBar(
            provider=row["provider"], dataset=row["dataset"],
            publisher_id=row["publisher_id"], instrument_id=row["instrument_id"],
            series_type=row["series_type"], timeframe=row["timeframe"],
            ts_start_ns=row["ts_start_ns"], raw_symbol=row["raw_symbol"],
            open=Decimal(row["open"]), high=Decimal(row["high"]),
            low=Decimal(row["low"]), close=Decimal(row["close"]),
            volume=Decimal(row["volume"]), ts_event_ns=row["ts_event_ns"],
            ts_received_ns=row["ts_received_ns"], sequence=row["sequence"],
            sequence_origin=row["sequence_origin"], origin=row["origin"],
            completeness=row["completeness"],
            ts_provider_out_ns=row["ts_provider_out_ns"],
        )

    @staticmethod
    def _same_payload(a: OhlcvBar, b: OhlcvBar) -> bool:
        return (
            a.open == b.open and a.high == b.high and a.low == b.low
            and a.close == b.close and a.volume == b.volume
            and a.origin == b.origin and a.completeness == b.completeness
        )

    @staticmethod
    def _values(bar: OhlcvBar) -> tuple[object, ...]:
        return (
            bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
            bar.series_type, bar.timeframe, bar.ts_start_ns, bar.raw_symbol,
            format(bar.open, "f"), format(bar.high, "f"), format(bar.low, "f"),
            format(bar.close, "f"), format(bar.volume, "f"), bar.ts_event_ns,
            bar.ts_received_ns, bar.sequence, bar.sequence_origin, bar.origin,
            bar.completeness, bar.ts_provider_out_ns,
            _BUCKET_POLICY, _CALENDAR_ID, _CALENDAR_VERSION,
        )

    def apply(self, bar: OhlcvBar) -> str:
        """Persist one revision; result semantics match OhlcvPipeline.apply."""
        if not isinstance(bar, OhlcvBar):
            raise TypeError("Expected an OhlcvBar instance.")
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                """SELECT * FROM ohlcv_bars WHERE provider=? AND dataset=?
                AND publisher_id=? AND instrument_id=? AND series_type=?
                AND timeframe=? AND ts_start_ns=? AND bucket_policy=?
                AND calendar_id=? AND calendar_version=?""",
                (bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
                 bar.series_type, bar.timeframe, bar.ts_start_ns,
                 _BUCKET_POLICY, _CALENDAR_ID, _CALENDAR_VERSION),
            ).fetchone()
            if row is None:
                oldest = db.execute(
                    """SELECT MIN(ts_start_ns) AS oldest, COUNT(*) AS amount
                    FROM ohlcv_bars WHERE provider=? AND dataset=?
                    AND publisher_id=? AND instrument_id=? AND series_type=?
                    AND raw_symbol=? AND timeframe=? AND bucket_policy=?
                    AND calendar_id=? AND calendar_version=?""",
                    (bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
                     bar.series_type, bar.raw_symbol, bar.timeframe,
                     _BUCKET_POLICY, _CALENDAR_ID, _CALENDAR_VERSION),
                ).fetchone()
                if int(oldest["amount"]) >= self.retention[bar.timeframe] and (
                    oldest["oldest"] is not None and bar.ts_start_ns < int(oldest["oldest"])
                ):
                    db.execute("ROLLBACK")
                    return "expired"
            if row is not None:
                current = self._from_row(row)
                if current.raw_symbol != bar.raw_symbol:
                    db.execute("ROLLBACK")
                    return "conflict"
                provider_upgrade = current.origin != "provider" and bar.origin == "provider"
                if current.origin == "provider" and bar.origin != "provider":
                    db.execute("ROLLBACK")
                    return "provider_precedence"
                if not provider_upgrade:
                    if self._same_payload(current, bar):
                        db.execute("ROLLBACK")
                        return "duplicate"
                    incoming_order = (bar.ts_event_ns, bar.sequence)
                    current_order = (current.ts_event_ns, current.sequence)
                    if incoming_order < current_order or (
                        incoming_order == current_order and bar.origin != "derived"
                    ):
                        db.execute("ROLLBACK")
                        return "stale"
                result = "replaced"
            else:
                result = "inserted"

            if bar.sequence_origin == "local":
                db.execute(
                    """INSERT INTO ohlcv_store_state(state_key, int_value)
                    VALUES ('max_local_sequence', ?)
                    ON CONFLICT(state_key) DO UPDATE SET
                    int_value=MAX(int_value, excluded.int_value)""",
                    (bar.sequence,),
                )
            db.execute(
                """INSERT INTO ohlcv_bars (
                    provider,dataset,publisher_id,instrument_id,series_type,
                    timeframe,ts_start_ns,raw_symbol,open,high,low,close,volume,
                    ts_event_ns,ts_received_ns,sequence,sequence_origin,origin,
                    completeness,ts_provider_out_ns,bucket_policy,calendar_id,
                    calendar_version
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(provider,dataset,publisher_id,instrument_id,
                            series_type,timeframe,ts_start_ns,bucket_policy,
                            calendar_id,calendar_version)
                DO UPDATE SET
                    raw_symbol=excluded.raw_symbol, open=excluded.open,
                    high=excluded.high, low=excluded.low, close=excluded.close,
                    volume=excluded.volume, ts_event_ns=excluded.ts_event_ns,
                    ts_received_ns=excluded.ts_received_ns, sequence=excluded.sequence,
                    sequence_origin=excluded.sequence_origin, origin=excluded.origin,
                    completeness=excluded.completeness,
                    ts_provider_out_ns=excluded.ts_provider_out_ns""",
                self._values(bar),
            )
            cap = self.retention[bar.timeframe]
            db.execute(
                """DELETE FROM ohlcv_bars WHERE provider=? AND dataset=?
                AND publisher_id=? AND instrument_id=? AND series_type=?
                AND raw_symbol=? AND timeframe=? AND bucket_policy=?
                AND calendar_id=? AND calendar_version=? AND ts_start_ns NOT IN (
                    SELECT ts_start_ns FROM ohlcv_bars
                    WHERE provider=? AND dataset=? AND publisher_id=?
                    AND instrument_id=? AND series_type=? AND raw_symbol=?
                    AND timeframe=? AND bucket_policy=? AND calendar_id=?
                    AND calendar_version=? ORDER BY ts_start_ns DESC LIMIT ?
                )""",
                (bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
                 bar.series_type, bar.raw_symbol, bar.timeframe,
                 _BUCKET_POLICY, _CALENDAR_ID, _CALENDAR_VERSION,
                 bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
                 bar.series_type, bar.raw_symbol, bar.timeframe,
                 _BUCKET_POLICY, _CALENDAR_ID, _CALENDAR_VERSION, cap),
            )
            db.execute("COMMIT")
            return result
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def load_bars(self) -> list[OhlcvBar]:
        """Load the bounded retained snapshot in chronological order."""
        db = self._connect()
        try:
            rows = db.execute(
                """SELECT * FROM ohlcv_bars ORDER BY ts_start_ns, provider,
                dataset, publisher_id, instrument_id, series_type, timeframe,
                bucket_policy, calendar_id, calendar_version"""
            ).fetchall()
            return [self._from_row(row) for row in rows]
        finally:
            db.close()

    def query(
        self, *, dataset: str | None = None, publisher_id: int | None = None,
        instrument_id: int | None = None, timeframe: str | None = None,
        provider: str | None = None, raw_symbol: str | None = None,
        series_type: str | None = None, start_ns: int | None = None,
        end_ns: int | None = None, limit: int | None = None,
    ) -> tuple[list[OhlcvBar], int]:
        clauses: list[str] = []
        params: list[object] = []
        for column, value in (
            ("dataset", dataset), ("publisher_id", publisher_id),
            ("instrument_id", instrument_id), ("timeframe", timeframe),
            ("provider", provider), ("raw_symbol", raw_symbol),
            ("series_type", series_type),
        ):
            if value is not None:
                clauses.append(f"{column}=?")
                params.append(value)
        if start_ns is not None:
            clauses.append("ts_start_ns>=?")
            params.append(start_ns)
        if end_ns is not None:
            clauses.append("ts_start_ns<?")
            params.append(end_ns)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        db = self._connect()
        try:
            total = int(db.execute(
                "SELECT COUNT(*) FROM ohlcv_bars" + where, params
            ).fetchone()[0])
            sql = "SELECT * FROM ohlcv_bars" + where + " ORDER BY ts_start_ns DESC, provider DESC, dataset DESC, publisher_id DESC, instrument_id DESC, series_type DESC, raw_symbol DESC, timeframe DESC"
            query_params = list(params)
            if limit is not None:
                if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
                    raise ValueError("limit must be a positive integer.")
                sql += " LIMIT ?"
                query_params.append(limit)
            rows = db.execute(sql, query_params).fetchall()
            bars = [self._from_row(row) for row in reversed(rows)]
            return bars, total
        finally:
            db.close()

    def max_local_sequence(self) -> int:
        """High-water mark survives retention pruning and process restarts."""
        db = self._connect()
        try:
            row = db.execute(
                "SELECT int_value FROM ohlcv_store_state WHERE state_key='max_local_sequence'"
            ).fetchone()
            return 0 if row is None else int(row["int_value"])
        finally:
            db.close()

    def stats(self) -> dict[str, int]:
        db = self._connect()
        try:
            row = db.execute(
                "SELECT COUNT(*) AS bars, COUNT(DISTINCT provider || ':' || dataset || ':' || publisher_id || ':' || instrument_id || ':' || series_type || ':' || raw_symbol || ':' || timeframe || ':' || bucket_policy || ':' || calendar_id || ':' || calendar_version) AS series FROM ohlcv_bars"
            ).fetchone()
            return {"bars": int(row["bars"]), "series": int(row["series"])}
        finally:
            db.close()
