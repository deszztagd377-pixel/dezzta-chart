"""Durable SQLite persistence for normalized OHLCV bars.

Bar identity is provider + dataset + publisher + instrument + series type +
timeframe + bucket start. Prices and volume are stored as exact decimal text;
all event/receive timestamps remain integer nanoseconds.
"""
from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import uuid
from typing import Mapping

from app.ohlcv import (
    DEFAULT_RETENTION,
    MIN_RETENTION,
    OhlcvBar,
    SUPPORTED_TIMEFRAMES,
    BUCKET_POLICY_UTC_LEGACY,
    BUCKET_POLICY_UTC_FIXED_V1,
    BUCKET_POLICY_CME_SESSION_V1,
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

OUTBOX_MAX_EVENTS = 100_000
OUTBOX_MAX_REPLAY_BATCH = 1_000
_OHLCV_SCHEMA_VERSION = 3


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
                """CREATE TABLE IF NOT EXISTS ohlcv_store_identity (
                    identity_key TEXT PRIMARY KEY NOT NULL,
                    identity_value TEXT NOT NULL
                )"""
            )
            db.execute(
                """INSERT INTO ohlcv_store_identity(identity_key,identity_value)
                VALUES ('source_id',?)
                ON CONFLICT(identity_key) DO NOTHING""",
                (uuid.uuid4().hex,),
            )
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_outbox (
                    cursor INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    provider TEXT NOT NULL,
                    dataset TEXT NOT NULL,
                    publisher_id INTEGER NOT NULL,
                    instrument_id INTEGER NOT NULL,
                    series_type TEXT NOT NULL,
                    raw_symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    bucket_policy TEXT NOT NULL,
                    calendar_id TEXT NOT NULL,
                    calendar_version TEXT NOT NULL,
                    created_at_ns INTEGER NOT NULL,
                    event_json TEXT NOT NULL
                )"""
            )
            db.execute(
                """CREATE INDEX IF NOT EXISTS idx_ohlcv_outbox_series_cursor
                ON ohlcv_outbox(provider,dataset,publisher_id,instrument_id,
                    series_type,raw_symbol,timeframe,bucket_policy,
                    calendar_id,calendar_version,cursor)"""
            )
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_outbox_state (
                    state_key TEXT PRIMARY KEY NOT NULL,
                    int_value INTEGER NOT NULL
                )"""
            )
            db.execute(
                """INSERT INTO ohlcv_outbox_state(state_key,int_value)
                VALUES ('retention_floor',0)
                ON CONFLICT(state_key) DO NOTHING"""
            )
            db.execute(
                """INSERT INTO ohlcv_outbox_state(state_key,int_value)
                VALUES ('high_water',0)
                ON CONFLICT(state_key) DO NOTHING"""
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
            bucket_policy=row["bucket_policy"],
            calendar_id=row["calendar_id"],
            calendar_version=row["calendar_version"],
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
            bar.bucket_policy, bar.calendar_id, bar.calendar_version,
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
                 bar.bucket_policy, bar.calendar_id, bar.calendar_version),
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
                     bar.bucket_policy, bar.calendar_id, bar.calendar_version),
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
            event_id = uuid.uuid4().hex
            event_payload = {
                "type": "market_data.ohlcv.update",
                "version": 1,
                "eventId": event_id,
                "operation": "upsert",
                "series": {
                    "provider": bar.provider,
                    "dataset": bar.dataset,
                    "publisherId": bar.publisher_id,
                    "instrumentId": bar.instrument_id,
                    "seriesType": bar.series_type,
                    "rawSymbol": bar.raw_symbol,
                    "timeframe": bar.timeframe,
                    "bucketPolicy": bar.bucket_policy,
                    "calendarId": bar.calendar_id,
                    "calendarVersion": bar.calendar_version,
                },
                "bar": {
                    "dataset": bar.dataset,
                    "provider": bar.provider,
                    "publisherId": bar.publisher_id,
                    "instrumentId": bar.instrument_id,
                    "rawSymbol": bar.raw_symbol,
                    "seriesType": bar.series_type,
                    "timeframe": bar.timeframe,
                    "bucketPolicy": bar.bucket_policy,
                    "calendarId": bar.calendar_id,
                    "calendarVersion": bar.calendar_version,
                    "tsStartNs": str(bar.ts_start_ns),
                    "open": format(bar.open, "f"),
                    "high": format(bar.high, "f"),
                    "low": format(bar.low, "f"),
                    "close": format(bar.close, "f"),
                    "volume": format(bar.volume, "f"),
                    "tsEventNs": str(bar.ts_event_ns),
                    "tsReceivedNs": str(bar.ts_received_ns),
                    "tsProviderOutNs": None if bar.ts_provider_out_ns is None else str(bar.ts_provider_out_ns),
                    "sequence": bar.sequence,
                    "sequenceOrigin": bar.sequence_origin,
                    "origin": bar.origin,
                    "completeness": bar.completeness,
                },
            }
            cursor = db.execute(
                """INSERT INTO ohlcv_outbox(
                    event_id,provider,dataset,publisher_id,instrument_id,
                    series_type,raw_symbol,timeframe,bucket_policy,calendar_id,
                    calendar_version,created_at_ns,event_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event_id, bar.provider, bar.dataset, bar.publisher_id,
                    bar.instrument_id, bar.series_type, bar.raw_symbol,
                    bar.timeframe, bar.bucket_policy, bar.calendar_id,
                    bar.calendar_version, bar.ts_received_ns,
                    json.dumps(event_payload, separators=(",", ":"), sort_keys=True),
                ),
            ).lastrowid
            db.execute(
                """UPDATE ohlcv_outbox_state SET int_value=?
                WHERE state_key='high_water'""",
                (int(cursor),),
            )
            # Keep a bounded global replay window. The floor records the largest
            # cursor deliberately removed, so old clients are forced to resnapshot.
            floor_row = db.execute(
                "SELECT int_value FROM ohlcv_outbox_state WHERE state_key='retention_floor'"
            ).fetchone()
            current_floor = 0 if floor_row is None else int(floor_row["int_value"])
            # Normal AUTOINCREMENT cursors are contiguous because inserts and
            # floor advancement share this transaction; avoid a full COUNT scan
            # on every market-data write once the retention window is full.
            if int(cursor) - current_floor > OUTBOX_MAX_EVENTS:
                new_floor = int(cursor) - OUTBOX_MAX_EVENTS
                db.execute("DELETE FROM ohlcv_outbox WHERE cursor<=?", (new_floor,))
                db.execute(
                    """UPDATE ohlcv_outbox_state SET int_value=MAX(int_value,?)
                    WHERE state_key='retention_floor'""",
                    (new_floor,),
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
                 bar.bucket_policy, bar.calendar_id, bar.calendar_version,
                 bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
                 bar.series_type, bar.raw_symbol, bar.timeframe,
                 bar.bucket_policy, bar.calendar_id, bar.calendar_version, cap),
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
                """SELECT * FROM ohlcv_bars
                WHERE (bucket_policy IN (?,?) AND calendar_id='' AND calendar_version='')
                   OR (bucket_policy=? AND timeframe IN ('1d','1w','1M','3M')
                       AND calendar_id<>'' AND calendar_version<>'')
                ORDER BY ts_start_ns,
                CASE bucket_policy WHEN 'UTC_LEGACY' THEN 0 ELSE 1 END,
                provider, dataset, publisher_id, instrument_id, series_type, timeframe""",
                (BUCKET_POLICY_UTC_LEGACY, BUCKET_POLICY_UTC_FIXED_V1, BUCKET_POLICY_CME_SESSION_V1)
            ).fetchall()
            return [self._from_row(row) for row in rows]
        finally:
            db.close()

    def query(
        self, *, dataset: str | None = None, publisher_id: int | None = None,
        instrument_id: int | None = None, timeframe: str | None = None,
        provider: str | None = None, raw_symbol: str | None = None,
        series_type: str | None = None, bucket_policy: str | None = None,
        calendar_id: str | None = None, calendar_version: str | None = None,
        start_ns: int | None = None, end_ns: int | None = None,
        limit: int | None = None,
    ) -> tuple[list[OhlcvBar], int]:
        clauses: list[str] = []
        params: list[object] = []
        if bucket_policy is None:
            clauses.append("bucket_policy IN (?,?)")
            params.extend([BUCKET_POLICY_UTC_LEGACY, BUCKET_POLICY_UTC_FIXED_V1])
        else:
            clauses.append("bucket_policy=?")
            params.append(bucket_policy)
        if calendar_id is not None:
            clauses.append("calendar_id=?")
            params.append(calendar_id)
        else:
            clauses.append("calendar_id=''")
        if calendar_version is not None:
            clauses.append("calendar_version=?")
            params.append(calendar_version)
        else:
            clauses.append("calendar_version=''")
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

    def query_snapshot(
        self, *, dataset: str | None = None, publisher_id: int | None = None,
        instrument_id: int | None = None, timeframe: str | None = None,
        provider: str | None = None, raw_symbol: str | None = None,
        series_type: str | None = None, bucket_policy: str | None = None,
        calendar_id: str | None = None, calendar_version: str | None = None,
        start_ns: int | None = None, end_ns: int | None = None,
        limit: int | None = None,
    ) -> dict[str, object]:
        """Return bars and their durable outbox watermark from one SQLite snapshot.

        The bar revision and its outbox cursor are committed in the same write
        transaction. Reading both under one SQLite read transaction gives a
        replica/gateway an unambiguous snapshot boundary for later replay.
        """
        if limit is not None and (
            not isinstance(limit, int) or isinstance(limit, bool) or limit < 1
        ):
            raise ValueError("limit must be a positive integer.")

        clauses: list[str] = []
        params: list[object] = []
        if bucket_policy is None:
            clauses.append("bucket_policy IN (?,?)")
            params.extend([BUCKET_POLICY_UTC_LEGACY, BUCKET_POLICY_UTC_FIXED_V1])
        else:
            clauses.append("bucket_policy=?")
            params.append(bucket_policy)
        if calendar_id is not None:
            clauses.append("calendar_id=?")
            params.append(calendar_id)
        else:
            clauses.append("calendar_id=''")
        if calendar_version is not None:
            clauses.append("calendar_version=?")
            params.append(calendar_version)
        else:
            clauses.append("calendar_version=''")
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
            db.execute("BEGIN")
            state = {
                row["state_key"]: int(row["int_value"])
                for row in db.execute(
                    "SELECT state_key,int_value FROM ohlcv_outbox_state"
                ).fetchall()
            }
            high_water = state.get("high_water", 0)
            retention_floor = state.get("retention_floor", 0)
            total = int(db.execute(
                "SELECT COUNT(*) FROM ohlcv_bars" + where, params
            ).fetchone()[0])
            sql = (
                "SELECT * FROM ohlcv_bars" + where
                + " ORDER BY ts_start_ns DESC, provider DESC, dataset DESC, "
                "publisher_id DESC, instrument_id DESC, series_type DESC, "
                "raw_symbol DESC, timeframe DESC"
            )
            query_params = list(params)
            if limit is not None:
                sql += " LIMIT ?"
                query_params.append(limit)
            rows = db.execute(sql, query_params).fetchall()
            return {
                "bars": [self._from_row(row) for row in reversed(rows)],
                "total": total,
                "cursor": high_water,
                "high_water": high_water,
                "retention_floor": retention_floor,
            }
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

    def outbox_high_water(self) -> int:
        """Return the durable global outbox cursor, including pruned history."""
        db = self._connect()
        try:
            row = db.execute(
                "SELECT int_value FROM ohlcv_outbox_state WHERE state_key='high_water'"
            ).fetchone()
            return 0 if row is None else int(row["int_value"])
        finally:
            db.close()

    def outbox_event_for_bar(self, bar: OhlcvBar) -> dict[str, object] | None:
        """Resolve the exact committed outbox event for one persisted bar revision.

        Several legitimate revisions can share timestamps and sequence values
        (for example, an open derived bar becoming complete). Compare the full
        canonical payload so a delayed callback cannot publish a different
        revision merely because its OHLCV values happen to match.
        """
        if not isinstance(bar, OhlcvBar):
            raise TypeError("Expected an OhlcvBar instance.")
        db = self._connect()
        try:
            patterns = (
                f'%"tsStartNs":"{bar.ts_start_ns}"%',
                f'%"tsEventNs":"{bar.ts_event_ns}"%',
                f'%"tsReceivedNs":"{bar.ts_received_ns}"%',
                f'%"sequence":{bar.sequence},"sequenceOrigin"%',
            )
            rows = db.execute(
                """SELECT cursor,event_id,event_json FROM ohlcv_outbox
                WHERE provider=? AND dataset=? AND publisher_id=? AND instrument_id=?
                AND series_type=? AND raw_symbol=? AND timeframe=? AND bucket_policy=?
                AND calendar_id=? AND calendar_version=?
                AND event_json LIKE ? AND event_json LIKE ?
                AND event_json LIKE ? AND event_json LIKE ?
                ORDER BY cursor DESC""",
                (
                    bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
                    bar.series_type, bar.raw_symbol, bar.timeframe, bar.bucket_policy,
                    bar.calendar_id, bar.calendar_version, *patterns,
                ),
            ).fetchall()
            expected = {
                "tsStartNs": str(bar.ts_start_ns),
                "open": format(bar.open, "f"),
                "high": format(bar.high, "f"),
                "low": format(bar.low, "f"),
                "close": format(bar.close, "f"),
                "volume": format(bar.volume, "f"),
                "tsEventNs": str(bar.ts_event_ns),
                "tsReceivedNs": str(bar.ts_received_ns),
                "tsProviderOutNs": (
                    None if bar.ts_provider_out_ns is None
                    else str(bar.ts_provider_out_ns)
                ),
                "sequence": bar.sequence,
                "sequenceOrigin": bar.sequence_origin,
                "origin": bar.origin,
                "completeness": bar.completeness,
            }
            for row in rows:
                payload = json.loads(row["event_json"])
                stored_bar = payload.get("bar")
                if isinstance(stored_bar, dict) and all(
                    stored_bar.get(key) == value for key, value in expected.items()
                ):
                    return {"cursor": int(row["cursor"]), "eventId": str(row["event_id"])}
            return None
        finally:
            db.close()

    def outbox_event_id(self, cursor: int) -> str | None:
        """Return the persisted stable event ID for a durable cursor."""
        if not isinstance(cursor, int) or isinstance(cursor, bool) or cursor < 1:
            raise ValueError("cursor must be a positive integer.")
        db = self._connect()
        try:
            row = db.execute(
                "SELECT event_id FROM ohlcv_outbox WHERE cursor=?",
                (cursor,),
            ).fetchone()
            return None if row is None else str(row["event_id"])
        finally:
            db.close()

    def read_outbox_batch(self, *, after_cursor: int, limit: int = 500) -> dict[str, object]:
        """Read a contiguous global outbox page or require a safe resnapshot.

        Unlike replay_outbox(), this method is not scoped to one series. It
        returns a consistent high-water/retention view and bounded event page.
        Cursor continuity is checked before a relay may advance its checkpoint;
        a missing retained cursor is an integrity failure, not an empty page.
        """
        if not isinstance(after_cursor, int) or isinstance(after_cursor, bool) or after_cursor < 0:
            raise ValueError("after_cursor must be a non-negative integer.")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= OUTBOX_MAX_REPLAY_BATCH:
            raise ValueError("limit must be between 1 and OUTBOX_MAX_REPLAY_BATCH.")
        db = self._connect()
        try:
            db.execute("BEGIN")
            state = {
                row["state_key"]: int(row["int_value"])
                for row in db.execute(
                    "SELECT state_key,int_value FROM ohlcv_outbox_state"
                ).fetchall()
            }
            floor = state.get("retention_floor", 0)
            high_water = state.get("high_water", 0)
            if after_cursor < floor or after_cursor > high_water:
                return {
                    "status": "resnapshot_required",
                    "reason": "cursor_expired" if after_cursor < floor else "cursor_ahead",
                    "events": [],
                    "next_cursor": high_water,
                    "high_water": high_water,
                    "retention_floor": floor,
                }
            rows = db.execute(
                """SELECT cursor,event_id,event_json FROM ohlcv_outbox
                WHERE cursor>? ORDER BY cursor ASC LIMIT ?""",
                (after_cursor, limit + 1),
            ).fetchall()

            # The outbox cursor is globally monotonic and contiguous between
            # retention_floor and high_water. Check the look-ahead row too, so
            # a gap at a page boundary is detected before a relay checkpoints.
            expected_cursor = after_cursor + 1
            for row in rows:
                actual_cursor = int(row["cursor"])
                if actual_cursor != expected_cursor:
                    return {
                        "status": "resnapshot_required",
                        "reason": "cursor_gap",
                        "events": [],
                        "next_cursor": high_water,
                        "high_water": high_water,
                        "retention_floor": floor,
                    }
                expected_cursor += 1

            has_more = len(rows) > limit
            selected = rows[:limit]
            if not has_more:
                last_cursor = int(selected[-1]["cursor"]) if selected else after_cursor
                if last_cursor != high_water:
                    return {
                        "status": "resnapshot_required",
                        "reason": "cursor_gap",
                        "events": [],
                        "next_cursor": high_water,
                        "high_water": high_water,
                        "retention_floor": floor,
                    }

            events: list[dict[str, object]] = []
            for row in selected:
                payload = json.loads(row["event_json"])
                payload["cursor"] = int(row["cursor"])
                payload["eventId"] = str(row["event_id"])
                events.append(payload)
            next_cursor = int(selected[-1]["cursor"]) if has_more else high_water
            return {
                "status": "ok",
                "events": events,
                "next_cursor": next_cursor,
                "high_water": high_water,
                "retention_floor": floor,
                "has_more": has_more,
            }
        finally:
            db.close()

    def replay_outbox(
        self, *, after_cursor: int, provider: str, dataset: str,
        publisher_id: int, instrument_id: int, series_type: str,
        raw_symbol: str, timeframe: str, bucket_policy: str,
        calendar_id: str = "", calendar_version: str = "",
        limit: int = 500,
    ) -> dict[str, object]:
        """Read a bounded, exact-series replay window or require a fresh snapshot.

        Cursors are global and monotonic. The returned cursor may advance across
        unrelated series only when no matching events remain before the high-water.
        """
        if not isinstance(after_cursor, int) or isinstance(after_cursor, bool) or after_cursor < 0:
            raise ValueError("after_cursor must be a non-negative integer.")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= OUTBOX_MAX_REPLAY_BATCH:
            raise ValueError("limit must be between 1 and OUTBOX_MAX_REPLAY_BATCH.")
        identity = (
            provider, dataset, publisher_id, instrument_id, series_type,
            raw_symbol, timeframe, bucket_policy, calendar_id, calendar_version,
        )
        if any(not isinstance(value, str) or not value for value in
               (provider, dataset, series_type, raw_symbol, timeframe, bucket_policy)):
            raise ValueError("A complete canonical series identity is required.")
        if not isinstance(calendar_id, str) or not isinstance(calendar_version, str):
            raise ValueError("calendar_id and calendar_version must be strings.")
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 1
               for value in (publisher_id, instrument_id)):
            raise ValueError("publisher_id and instrument_id must be positive integers.")
        db = self._connect()
        try:
            # Keep high-water, retention floor, and replay rows on one SQLite
            # read snapshot so a concurrent commit cannot split the cursor view.
            db.execute("BEGIN")
            state = {
                row["state_key"]: int(row["int_value"])
                for row in db.execute(
                    "SELECT state_key,int_value FROM ohlcv_outbox_state"
                ).fetchall()
            }
            floor = state.get("retention_floor", 0)
            high_water = state.get("high_water", 0)
            if after_cursor < floor or after_cursor > high_water:
                return {
                    "status": "resnapshot_required",
                    "reason": "cursor_expired" if after_cursor < floor else "cursor_ahead",
                    "events": [],
                    "next_cursor": high_water,
                    "high_water": high_water,
                    "retention_floor": floor,
                }
            rows = db.execute(
                """SELECT cursor,event_id,event_json FROM ohlcv_outbox
                WHERE cursor>? AND provider=? AND dataset=? AND publisher_id=?
                AND instrument_id=? AND series_type=? AND raw_symbol=?
                AND timeframe=? AND bucket_policy=? AND calendar_id=?
                AND calendar_version=? ORDER BY cursor ASC LIMIT ?""",
                (after_cursor, *identity, limit + 1),
            ).fetchall()
            has_more = len(rows) > limit
            selected = rows[:limit]
            events = []
            for row in selected:
                payload = json.loads(row["event_json"])
                payload["cursor"] = int(row["cursor"])
                payload["eventId"] = row["event_id"]
                events.append(payload)
            if has_more:
                next_cursor = int(selected[-1]["cursor"])
            else:
                next_cursor = high_water
            return {
                "status": "ok",
                "events": events,
                "next_cursor": next_cursor,
                "high_water": high_water,
                "retention_floor": floor,
                "has_more": has_more,
            }
        finally:
            db.close()

    def source_id(self) -> str:
        """Return the stable identity of this authoritative SQLite store."""
        db = self._connect()
        try:
            row = db.execute(
                "SELECT identity_value FROM ohlcv_store_identity WHERE identity_key='source_id'"
            ).fetchone()
            if row is None:
                raise RuntimeError("OHLCV source identity is missing.")
            return str(row["identity_value"])
        finally:
            db.close()

    def export_global_snapshot(
        self, destination_path: str, *, batch_size: int = 500,
    ) -> dict[str, object]:
        """Export every retained series from one read view to an atomic JSONL file.

        The source read transaction pins one SQLite snapshot while rows are
        streamed with fetchmany() into a temporary file on the destination
        filesystem. Writers may continue under WAL; WAL growth during a long
        export must be monitored operationally. The final file appears only
        after its footer manifest is flushed and the source read transaction
        completes successfully.
        """
        if not isinstance(destination_path, str) or not destination_path.strip():
            raise ValueError("destination_path is required.")
        if (
            not isinstance(batch_size, int) or isinstance(batch_size, bool)
            or not 1 <= batch_size <= 5_000
        ):
            raise ValueError("batch_size must be between 1 and 5000.")

        destination = Path(destination_path).expanduser()
        source_path = Path(self.database_path).resolve()
        if destination.resolve() == source_path:
            raise ValueError("Snapshot destination cannot overwrite the source database.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(
            f".{destination.name}.{uuid.uuid4().hex}.tmp"
        )
        generation_id = uuid.uuid4().hex
        source = self._connect()
        try:
            source.execute("BEGIN")
            state = {
                row["state_key"]: int(row["int_value"])
                for row in source.execute(
                    "SELECT state_key,int_value FROM ohlcv_outbox_state"
                ).fetchall()
            }
            identity = source.execute(
                "SELECT identity_value FROM ohlcv_store_identity "
                "WHERE identity_key='source_id'"
            ).fetchone()
            if identity is None:
                raise RuntimeError("OHLCV source identity is missing.")
            high_water = state.get("high_water", 0)
            retention_floor = state.get("retention_floor", 0)
            header = {
                "record": "header",
                "format": "dezzta.ohlcv.global-snapshot",
                "format_version": 2,
                "generation_id": generation_id,
                "source_id": str(identity["identity_value"]),
                "high_water": high_water,
                "retention_floor": retention_floor,
                "bar_retention": {
                    timeframe: self.retention[timeframe]
                    for timeframe in sorted(self.retention)
                },
            }
            digest = hashlib.sha256()
            row_count = 0
            query = source.execute(
                """SELECT * FROM ohlcv_bars
                ORDER BY provider,dataset,publisher_id,instrument_id,series_type,
                    timeframe,ts_start_ns,bucket_policy,calendar_id,calendar_version"""
            )
            with temporary.open("w", encoding="utf-8", newline="\n") as output:
                header_encoded = json.dumps(
                    header, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
                output.write(header_encoded.decode("utf-8") + "\n")
                digest.update(header_encoded + b"\n")
                while True:
                    rows = query.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        encoded = json.dumps(
                            {"record": "bar", "data": dict(row)},
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("utf-8")
                        output.write(encoded.decode("utf-8") + "\n")
                        digest.update(encoded + b"\n")
                        row_count += 1
                manifest = {
                    "record": "manifest",
                    "row_count": row_count,
                    "sha256": digest.hexdigest(),
                }
                output.write(json.dumps(
                    manifest, sort_keys=True, separators=(",", ":")
                ) + "\n")
                output.flush()
                os.fsync(output.fileno())

            source.execute("COMMIT")
            os.replace(temporary, destination)
            return {
                "path": str(destination),
                "generation_id": generation_id,
                "source_id": str(identity["identity_value"]),
                "cursor": high_water,
                "high_water": high_water,
                "retention_floor": retention_floor,
                "row_count": row_count,
                "sha256": digest.hexdigest(),
                "format_version": 2,
            }
        except Exception:
            if source.in_transaction:
                source.execute("ROLLBACK")
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise
        finally:
            source.close()

    @staticmethod
    def verify_global_snapshot(snapshot_path: str) -> dict[str, object]:
        """Stream-verify a global snapshot's envelope, row count and SHA-256."""
        if not isinstance(snapshot_path, str) or not snapshot_path.strip():
            raise ValueError("snapshot_path is required.")
        digest = hashlib.sha256()
        row_count = 0
        header: dict[str, object] | None = None
        manifest: dict[str, object] | None = None
        with Path(snapshot_path).expanduser().open("rb") as snapshot:
            first = snapshot.readline()
            if not first:
                raise ValueError("Snapshot is empty.")
            try:
                header = json.loads(first)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("Snapshot header is invalid.") from exc
            if (
                not isinstance(header, dict)
                or header.get("record") != "header"
                or header.get("format") != "dezzta.ohlcv.global-snapshot"
                or header.get("format_version") != 2
                or not isinstance(header.get("source_id"), str)
                or not header.get("source_id")
                or not isinstance(header.get("generation_id"), str)
                or not header.get("generation_id")
                or type(header.get("high_water")) is not int
                or header["high_water"] < 0
                or type(header.get("retention_floor")) is not int
                or not 0 <= header["retention_floor"] <= header["high_water"]
                or not isinstance(header.get("bar_retention"), dict)
                or set(header["bar_retention"]) != set(SUPPORTED_TIMEFRAMES)
                or any(
                    type(cap) is not int or cap < MIN_RETENTION[timeframe]
                    for timeframe, cap in header["bar_retention"].items()
                )
            ):
                raise ValueError("Snapshot header contract is invalid.")
            digest.update(first)

            for line in snapshot:
                try:
                    record = json.loads(line)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("Snapshot record is invalid.") from exc
                if not isinstance(record, dict):
                    raise ValueError("Snapshot record must be an object.")
                if record.get("record") == "bar" and manifest is None:
                    data = record.get("data")
                    if not isinstance(data, dict):
                        raise ValueError("Snapshot bar record is invalid.")
                    encoded = json.dumps(
                        record, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                    digest.update(encoded + b"\n")
                    row_count += 1
                elif record.get("record") == "manifest" and manifest is None:
                    manifest = record
                    if snapshot.readline():
                        raise ValueError("Snapshot contains data after its manifest.")
                    break
                else:
                    raise ValueError("Snapshot record order is invalid.")

        if (
            manifest is None
            or type(manifest.get("row_count")) is not int
            or manifest["row_count"] != row_count
            or not isinstance(manifest.get("sha256"), str)
            or manifest["sha256"] != digest.hexdigest()
        ):
            raise ValueError("Snapshot manifest does not match its contents.")
        return {
            "source_id": header["source_id"],
            "generation_id": header["generation_id"],
            "cursor": header["high_water"],
            "high_water": header["high_water"],
            "retention_floor": header["retention_floor"],
            "bar_retention": header["bar_retention"],
            "row_count": row_count,
            "sha256": digest.hexdigest(),
            "format_version": 2,
        }

    def stats(self) -> dict[str, int]:
        db = self._connect()
        try:
            row = db.execute(
                "SELECT COUNT(*) AS bars, COUNT(DISTINCT provider || ':' || dataset || ':' || publisher_id || ':' || instrument_id || ':' || series_type || ':' || raw_symbol || ':' || timeframe || ':' || bucket_policy || ':' || calendar_id || ':' || calendar_version) AS series FROM ohlcv_bars"
            ).fetchone()
            return {"bars": int(row["bars"]), "series": int(row["series"])}
        finally:
            db.close()

_REPLICA_PROTOCOL_VERSION = 1
_REPLICA_SCHEMA_VERSION = 1
_SNAPSHOT_BAR_FIELDS = frozenset((
    "provider", "dataset", "publisher_id", "instrument_id", "series_type",
    "timeframe", "ts_start_ns", "raw_symbol", "open", "high", "low", "close",
    "volume", "ts_event_ns", "ts_received_ns", "sequence", "sequence_origin",
    "origin", "completeness", "ts_provider_out_ns", "bucket_policy",
    "calendar_id", "calendar_version",
))
_REPLICA_INSERT_SQL = """INSERT INTO ohlcv_bars (
    provider,dataset,publisher_id,instrument_id,series_type,timeframe,
    ts_start_ns,raw_symbol,open,high,low,close,volume,ts_event_ns,
    ts_received_ns,sequence,sequence_origin,origin,completeness,
    ts_provider_out_ns,bucket_policy,calendar_id,calendar_version
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""


class SQLiteOhlcvReplicaStore(SQLiteOhlcvStore):
    """Independent local OHLCV read model with atomic snapshot installation.

    This store deliberately rejects source-writer apply() calls. Snapshot
    installation writes bars directly and records the source checkpoint in the
    same transaction, so it cannot echo imported bars into the source outbox.
    """

    def __init__(
        self,
        database_path: str,
        *,
        retention: Mapping[str, int] | None = None,
        busy_timeout_ms: int = 10_000,
    ) -> None:
        super().__init__(
            database_path, retention=retention, busy_timeout_ms=busy_timeout_ms,
        )
        self._initialize_replica_metadata()

    def _initialize_replica_metadata(self) -> None:
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_replica_identity (
                    identity_key TEXT PRIMARY KEY NOT NULL,
                    identity_value TEXT NOT NULL
                )"""
            )
            db.execute(
                """INSERT INTO ohlcv_replica_identity(identity_key,identity_value)
                VALUES ('replica_id',?)
                ON CONFLICT(identity_key) DO NOTHING""",
                (uuid.uuid4().hex,),
            )
            db.execute(
                """CREATE TABLE IF NOT EXISTS ohlcv_replica_checkpoint (
                    source_id TEXT PRIMARY KEY NOT NULL,
                    replica_id TEXT NOT NULL,
                    applied_cursor INTEGER NOT NULL CHECK(applied_cursor >= 0),
                    snapshot_generation TEXT NOT NULL,
                    retention_floor INTEGER NOT NULL CHECK(retention_floor >= 0),
                    bar_retention_json TEXT NOT NULL DEFAULT '{}',
                    schema_version INTEGER NOT NULL,
                    protocol_version INTEGER NOT NULL
                )"""
            )
            checkpoint_columns = {
                row["name"] for row in db.execute(
                    "PRAGMA table_info(ohlcv_replica_checkpoint)"
                )
            }
            if "bar_retention_json" not in checkpoint_columns:
                db.execute(
                    "ALTER TABLE ohlcv_replica_checkpoint "
                    "ADD COLUMN bar_retention_json TEXT NOT NULL DEFAULT '{}'"
                )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def source_id(self) -> str:
        raise RuntimeError(
            "A replica does not own an authoritative source identity; "
            "inspect its upstream checkpoint instead."
        )

    def replica_id(self) -> str:
        db = self._connect()
        try:
            row = db.execute(
                "SELECT identity_value FROM ohlcv_replica_identity "
                "WHERE identity_key='replica_id'"
            ).fetchone()
            if row is None:
                raise RuntimeError("OHLCV replica identity is missing.")
            return str(row["identity_value"])
        finally:
            db.close()

    def checkpoint(self) -> dict[str, object] | None:
        db = self._connect()
        try:
            row = db.execute(
                """SELECT source_id,replica_id,applied_cursor,snapshot_generation,
                    retention_floor,bar_retention_json,schema_version,protocol_version
                FROM ohlcv_replica_checkpoint LIMIT 1"""
            ).fetchone()
            if row is None:
                return None
            return {
                "source_id": str(row["source_id"]),
                "replica_id": str(row["replica_id"]),
                "applied_cursor": int(row["applied_cursor"]),
                "snapshot_generation": str(row["snapshot_generation"]),
                "retention_floor": int(row["retention_floor"]),
                "bar_retention": json.loads(row["bar_retention_json"]),
                "schema_version": int(row["schema_version"]),
                "protocol_version": int(row["protocol_version"]),
            }
        finally:
            db.close()

    def apply(self, bar: OhlcvBar) -> str:
        raise RuntimeError(
            "Replica stores cannot use source-writer apply(); "
            "use the replica event-apply protocol."
        )

    def install_global_snapshot(
        self,
        snapshot_path: str,
        *,
        expected_source_id: str | None = None,
        batch_size: int = 500,
    ) -> dict[str, object]:
        """Validate and atomically replace this replica's complete read model.

        Validation is performed once before taking the writer lock and again
        while rows are inserted. The second pass closes the verify/use race:
        checkpoint advancement, full bar replacement and final manifest
        validation all commit or roll back together.
        """
        if not isinstance(snapshot_path, str) or not snapshot_path.strip():
            raise ValueError("snapshot_path is required.")
        if (
            not isinstance(batch_size, int) or isinstance(batch_size, bool)
            or not 1 <= batch_size <= 5_000
        ):
            raise ValueError("batch_size must be between 1 and 5000.")
        if expected_source_id is not None and (
            not isinstance(expected_source_id, str) or not expected_source_id.strip()
        ):
            raise ValueError("expected_source_id must be a non-empty string.")

        metadata = SQLiteOhlcvStore.verify_global_snapshot(snapshot_path)
        source_id = str(metadata["source_id"])
        if expected_source_id is not None and source_id != expected_source_id:
            raise ValueError("Snapshot source identity does not match the configured source.")

        replica_id = self.replica_id()
        db = self._connect()
        inserted = 0
        digest = hashlib.sha256()
        batch: list[tuple[object, ...]] = []
        manifest: dict[str, object] | None = None

        try:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                """SELECT source_id,applied_cursor FROM ohlcv_replica_checkpoint
                LIMIT 1"""
            ).fetchone()
            if existing is not None:
                if str(existing["source_id"]) != source_id:
                    raise ValueError(
                        "Replica is already bound to a different authoritative source."
                    )
                if int(existing["applied_cursor"]) > int(metadata["high_water"]):
                    raise ValueError("Snapshot cursor is older than the replica checkpoint.")
            else:
                local_high_water = db.execute(
                    "SELECT int_value FROM ohlcv_outbox_state WHERE state_key='high_water'"
                ).fetchone()
                local_bar_count = int(
                    db.execute("SELECT COUNT(*) FROM ohlcv_bars").fetchone()[0]
                )
                local_outbox_count = int(
                    db.execute("SELECT COUNT(*) FROM ohlcv_outbox").fetchone()[0]
                )
                if (
                    (local_high_water is not None and int(local_high_water["int_value"]) > 0)
                    or local_bar_count > 0
                    or local_outbox_count > 0
                ):
                    raise RuntimeError(
                        "Replica installation requires a dedicated empty OHLCV read-model database."
                    )

            with Path(snapshot_path).expanduser().open("rb") as snapshot:
                first = snapshot.readline()
                try:
                    header = json.loads(first)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("Snapshot header is invalid.") from exc
                if (
                    not isinstance(header, dict)
                    or header.get("record") != "header"
                    or header.get("source_id") != source_id
                    or header.get("generation_id") != metadata["generation_id"]
                    or type(header.get("high_water")) is not int
                    or header["high_water"] != metadata["high_water"]
                    or type(header.get("retention_floor")) is not int
                    or header["retention_floor"] != metadata["retention_floor"]
                ):
                    raise ValueError("Snapshot header changed after preflight verification.")

                digest.update(first)
                db.execute("DELETE FROM ohlcv_bars")

                for line in snapshot:
                    try:
                        record = json.loads(line)
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise ValueError("Snapshot record is invalid.") from exc
                    if not isinstance(record, dict):
                        raise ValueError("Snapshot record must be an object.")

                    if record.get("record") == "bar" and manifest is None:
                        data = record.get("data")
                        if not isinstance(data, dict) or set(data) != _SNAPSHOT_BAR_FIELDS:
                            raise ValueError("Snapshot bar schema does not match the canonical contract.")
                        string_fields = (
                            "provider", "dataset", "series_type", "timeframe",
                            "raw_symbol", "sequence_origin", "origin",
                            "completeness", "bucket_policy", "calendar_id",
                            "calendar_version", "open", "high", "low", "close",
                            "volume",
                        )
                        integer_fields = (
                            "publisher_id", "instrument_id", "ts_start_ns",
                            "ts_event_ns", "ts_received_ns", "sequence",
                        )
                        if any(not isinstance(data[field], str) for field in string_fields):
                            raise ValueError("Snapshot string and exact-decimal fields must be strings.")
                        if any(type(data[field]) is not int for field in integer_fields):
                            raise ValueError("Snapshot integer and nanosecond fields must be integers.")
                        if data["ts_provider_out_ns"] is not None and type(data["ts_provider_out_ns"]) is not int:
                            raise ValueError("Snapshot provider timestamp must be an integer or null.")
                        try:
                            bar = OhlcvBar(**data)
                        except (TypeError, ValueError) as exc:
                            raise ValueError("Snapshot contains an invalid canonical OHLCV bar.") from exc

                        encoded = json.dumps(
                            record, sort_keys=True, separators=(",", ":")
                        ).encode("utf-8")
                        digest.update(encoded + b"\n")
                        batch.append(self._values(bar))
                        inserted += 1
                        if len(batch) >= batch_size:
                            db.executemany(_REPLICA_INSERT_SQL, batch)
                            batch.clear()
                    elif record.get("record") == "manifest" and manifest is None:
                        manifest = record
                        if snapshot.readline():
                            raise ValueError("Snapshot contains data after its manifest.")
                        break
                    else:
                        raise ValueError("Snapshot record order is invalid.")

            if batch:
                db.executemany(_REPLICA_INSERT_SQL, batch)
                batch.clear()

            if (
                manifest is None
                or type(manifest.get("row_count")) is not int
                or manifest["row_count"] != inserted
                or not isinstance(manifest.get("sha256"), str)
                or manifest["sha256"] != digest.hexdigest()
                or inserted != metadata["row_count"]
            ):
                raise ValueError("Snapshot manifest changed or does not match installed rows.")

            db.execute(
                """INSERT INTO ohlcv_replica_checkpoint(
                    source_id,replica_id,applied_cursor,snapshot_generation,
                    retention_floor,bar_retention_json,schema_version,protocol_version
                ) VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(source_id) DO UPDATE SET
                    replica_id=excluded.replica_id,
                    applied_cursor=excluded.applied_cursor,
                    snapshot_generation=excluded.snapshot_generation,
                    retention_floor=excluded.retention_floor,
                    bar_retention_json=excluded.bar_retention_json,
                    schema_version=excluded.schema_version,
                    protocol_version=excluded.protocol_version""",
                (
                    source_id, replica_id, int(metadata["high_water"]),
                    str(metadata["generation_id"]), int(metadata["retention_floor"]),
                    json.dumps(metadata["bar_retention"], sort_keys=True, separators=(",", ":")),
                    _REPLICA_SCHEMA_VERSION, _REPLICA_PROTOCOL_VERSION,
                ),
            )
            db.execute("COMMIT")
        except Exception:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

        return {
            **metadata,
            "replica_id": replica_id,
            "installed_rows": inserted,
            "status": "installed",
        }
