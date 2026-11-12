"""Durable SQLite persistence for normalized OHLCV bars.

Bar identity is provider + dataset + publisher + instrument + series type +
timeframe + bucket start. Prices and volume are stored as exact decimal text;
all event/receive timestamps remain integer nanoseconds.
"""
from __future__ import annotations

from decimal import Decimal
import json
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
                   OR bucket_policy=?
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

    def stats(self) -> dict[str, int]:
        db = self._connect()
        try:
            row = db.execute(
                "SELECT COUNT(*) AS bars, COUNT(DISTINCT provider || ':' || dataset || ':' || publisher_id || ':' || instrument_id || ':' || series_type || ':' || raw_symbol || ':' || timeframe || ':' || bucket_policy || ':' || calendar_id || ':' || calendar_version) AS series FROM ohlcv_bars"
            ).fetchone()
            return {"bars": int(row["bars"]), "series": int(row["series"])}
        finally:
            db.close()
