"""SQLite metrics collector: bounded, same-host, best-effort operational telemetry."""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

BUCKET_SECONDS = 900
RETENTION_SECONDS = 604800
STALE_SECONDS = 90
MAX_LIVE_WORKERS = 16
MAX_WORKER_GENERATIONS = 256
MAX_RETIRED_WORKERS = 4096
MAX_SERIES = 900
MAX_PAYLOAD_BYTES = 256 * 1024
MAX_ROWS = 650000
MAX_COUNTER = (1 << 53) - 1
WORKER_ID = re.compile(r"^[0-9a-f]{32}$")


def _lock_retry_delay(worker_id: str, attempt: int) -> float:
    """Return a stable per-worker jittered backoff without extending its bound."""
    seed = int.from_bytes(hashlib.blake2s(worker_id.encode("ascii"), digest_size=4).digest(), "big")
    factor = 0.5 + 0.5 * (seed / 0xFFFFFFFF)
    return min(0.01 * (2 ** attempt), 0.25) * factor


class MetricsCollectorError(RuntimeError):
    """Sanitized collector failure."""


class MetricsSnapshotRegression(MetricsCollectorError):
    """A process-local monotonic counter moved backwards."""


class SQLiteMetricsCollector:
    """Idempotent delta aggregation; no database I/O occurs on request hot paths."""

    def __init__(self, database_path: str) -> None:
        if not isinstance(database_path, str) or not database_path.strip() or database_path == ":memory:":
            raise ValueError("A persistent local metrics database path is required.")
        self.database_path = database_path
        self._schema_ready = False
        self._schema_lock = threading.Lock()

    def _connect(self) -> sqlite3.Connection:
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.database_path, timeout=0.25, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=250")
        try:
            if not self._schema_ready:
                with self._schema_lock:
                    if not self._schema_ready:
                        # Multiple ASGI processes may bootstrap the same local
                        # volume simultaneously. Retry only bounded SQLite lock
                        # failures; never hide corruption or other DB errors.
                        for attempt in range(7):
                            try:
                                db.execute("PRAGMA journal_mode=WAL")
                                db.execute("PRAGMA synchronous=NORMAL")
                                db.executescript("""
                                    CREATE TABLE IF NOT EXISTS metrics_workers (
                                        worker_id TEXT PRIMARY KEY,
                                        snapshot_json TEXT NOT NULL,
                                        last_seen REAL NOT NULL,
                                        active_connections INTEGER NOT NULL CHECK(active_connections >= 0)
                                    );
                                    CREATE TABLE IF NOT EXISTS metrics_buckets (
                                        bucket_start INTEGER NOT NULL,
                                        metric_key TEXT NOT NULL,
                                        value_json TEXT NOT NULL,
                                        PRIMARY KEY(bucket_start, metric_key)
                                    );
                                    CREATE INDEX IF NOT EXISTS idx_metrics_buckets_time
                                        ON metrics_buckets(bucket_start);
                                    CREATE INDEX IF NOT EXISTS idx_metrics_workers_seen
                                        ON metrics_workers(last_seen);
                                    CREATE TABLE IF NOT EXISTS metrics_retired_workers (
                                        worker_id TEXT PRIMARY KEY,
                                        expires_at REAL NOT NULL
                                    );
                                    CREATE INDEX IF NOT EXISTS idx_metrics_retired_expiry
                                        ON metrics_retired_workers(expires_at);
                                    CREATE TABLE IF NOT EXISTS metrics_meta (
                                        meta_key TEXT PRIMARY KEY,
                                        meta_value INTEGER NOT NULL CHECK(meta_value >= 0)
                                    );
                                    INSERT OR IGNORE INTO metrics_meta(meta_key,meta_value)
                                        VALUES('capacity_evicted_rows',0);
                                """)
                                self._schema_ready = True
                                break
                            except sqlite3.OperationalError as exc:
                                if "locked" not in str(exc).lower() or attempt == 6:
                                    raise
                                time.sleep(min(0.01 * (2 ** attempt), 0.25))
            else:
                db.execute("PRAGMA synchronous=NORMAL")
            return db
        except Exception:
            db.close()
            raise

    @staticmethod
    def _number(value: Any, *, integer: bool = False) -> int | float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise MetricsCollectorError("invalid_metric_value")
        if not math.isfinite(float(value)) or value < 0:
            raise MetricsCollectorError("invalid_metric_value")
        if integer and (not isinstance(value, int) or value > MAX_COUNTER):
            raise MetricsCollectorError("invalid_metric_counter")
        return value

    @classmethod
    def _flatten(cls, request: dict[str, Any], websocket: dict[str, Any]) -> tuple[dict[str, Any], int]:
        if request.get("schema_version") != 1 or websocket.get("schema_version") != 1:
            raise MetricsCollectorError("unsupported_snapshot_schema")
        values: dict[str, Any] = {}
        requests, latency = request.get("requests"), request.get("latency_ms")
        if not isinstance(requests, list) or not isinstance(latency, list):
            raise MetricsCollectorError("invalid_http_snapshot")
        if len(requests) > 762 or len(latency) > 127:
            raise MetricsCollectorError("series_limit_exceeded")
        methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "OTHER"}
        statuses = {"1xx", "2xx", "3xx", "4xx", "5xx", "other"}
        for item in requests:
            if not isinstance(item, dict):
                raise MetricsCollectorError("invalid_request_series")
            method, route, status = item.get("method"), item.get("route"), item.get("status_class")
            if method not in methods or not isinstance(route, str) or len(route) > 160 or status not in statuses:
                raise MetricsCollectorError("invalid_request_dimensions")
            key = f"http.requests|{method}|{route}|{status}"
            if key in values:
                raise MetricsCollectorError("duplicate_metric_series")
            values[key] = cls._number(item.get("count"), integer=True)
        for item in latency:
            if not isinstance(item, dict):
                raise MetricsCollectorError("invalid_latency_series")
            method, route = item.get("method"), item.get("route")
            if method not in methods or not isinstance(route, str) or len(route) > 160:
                raise MetricsCollectorError("invalid_latency_dimensions")
            buckets = item.get("buckets")
            if not isinstance(buckets, list) or len(buckets) != 11 or not all(isinstance(x, dict) for x in buckets):
                raise MetricsCollectorError("invalid_latency_buckets")
            counts = [cls._number(x.get("count"), integer=True) for x in buckets]
            if any(a > b for a, b in zip(counts, counts[1:])) or counts[-1] != cls._number(item.get("count"), integer=True):
                raise MetricsCollectorError("invalid_latency_buckets")
            key = f"http.latency|{method}|{route}"
            if key in values:
                raise MetricsCollectorError("duplicate_metric_series")
            values[key] = {
                "count": counts[-1],
                "sum_ms": cls._number(item.get("sum_ms")),
                "buckets": counts,
            }
        for field in ("connections_started", "connections_completed", "connections_accepted", "peer_disconnects"):
            values[f"websocket|{field}"] = cls._number(websocket.get(field), integer=True)
        values["websocket|duration_sum_ms"] = cls._number(websocket.get("duration_sum_ms"))
        close_codes = websocket.get("close_code_classes")
        if not isinstance(close_codes, dict) or set(close_codes) != {"1xxx", "2xxx", "4xxx", "5xxx", "other"}:
            raise MetricsCollectorError("invalid_websocket_close_classes")
        for code, count in close_codes.items():
            values[f"websocket|close|{code}"] = cls._number(count, integer=True)
        active = int(cls._number(websocket.get("connections_active"), integer=True))
        if len(values) > MAX_SERIES:
            raise MetricsCollectorError("series_limit_exceeded")
        return values, active

    @staticmethod
    def _subtract(current: Any, previous: Any) -> Any:
        if isinstance(current, dict):
            if not isinstance(previous, dict) or set(current) != set(previous):
                raise MetricsSnapshotRegression("snapshot_shape_changed")
            if current["count"] < previous["count"] or current["sum_ms"] < previous["sum_ms"]:
                raise MetricsSnapshotRegression("counter_regressed")
            if any(a < b for a, b in zip(current["buckets"], previous["buckets"])):
                raise MetricsSnapshotRegression("counter_regressed")
            return {
                "count": current["count"] - previous["count"],
                "sum_ms": current["sum_ms"] - previous["sum_ms"],
                "buckets": [a - b for a, b in zip(current["buckets"], previous["buckets"])],
            }
        if current < previous:
            raise MetricsSnapshotRegression("counter_regressed")
        return current - previous

    @staticmethod
    def _add(current: Any, delta: Any) -> Any:
        if isinstance(delta, dict):
            if not isinstance(current, dict):
                current = {"count": 0, "sum_ms": 0.0, "buckets": [0] * len(delta["buckets"])}
            return {
                "count": min(current["count"] + delta["count"], MAX_COUNTER),
                "sum_ms": min(current["sum_ms"] + delta["sum_ms"], 86400000.0 * MAX_COUNTER),
                "buckets": [min(a + b, MAX_COUNTER) for a, b in zip(current["buckets"], delta["buckets"])],
            }
        if isinstance(delta, int):
            return min(current + delta, MAX_COUNTER)
        return min(current + delta, 86400000.0 * MAX_COUNTER)

    def flush(self, worker_id: str, request_snapshot: dict[str, Any], websocket_snapshot: dict[str, Any], *, now: float | None = None) -> dict[str, int]:
        if not isinstance(worker_id, str) or not WORKER_ID.fullmatch(worker_id):
            raise MetricsCollectorError("invalid_worker_id")
        stamp = time.time() if now is None else float(now)
        if not math.isfinite(stamp) or stamp < 0:
            raise MetricsCollectorError("invalid_timestamp")
        values, active = self._flatten(request_snapshot, websocket_snapshot)
        encoded = json.dumps(values, separators=(",", ":"), sort_keys=True, allow_nan=False)
        if len(encoded.encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise MetricsCollectorError("snapshot_payload_too_large")
        bucket = int(stamp // BUCKET_SECONDS) * BUCKET_SECONDS
        cutoff = stamp - RETENTION_SECONDS
        db = self._connect()
        lock_retries = 0
        lock_wait_started_ns = time.perf_counter_ns()
        try:
            # SQLite has one writer at a time. With up to 16 ASGI workers,
            # retry lock acquisition before transaction work so bounded
            # contention does not discard a metrics interval.
            for attempt in range(8):
                try:
                    db.execute("BEGIN IMMEDIATE")
                    break
                except sqlite3.OperationalError as exc:
                    if "locked" not in str(exc).lower() or attempt == 7:
                        raise
                    lock_retries += 1
                    time.sleep(_lock_retry_delay(worker_id, attempt))
            lock_wait_ms = (time.perf_counter_ns() - lock_wait_started_ns) / 1_000_000
            transaction_started_ns = time.perf_counter_ns()
            db.execute("DELETE FROM metrics_retired_workers WHERE expires_at < ?", (stamp,))
            retired = db.execute(
                "SELECT 1 FROM metrics_retired_workers WHERE worker_id=?", (worker_id,)
            ).fetchone()
            if retired is not None:
                raise MetricsSnapshotRegression("worker_checkpoint_expired")
            workers = db.execute("SELECT worker_id,snapshot_json,last_seen FROM metrics_workers").fetchall()
            current = next((row for row in workers if row["worker_id"] == worker_id), None)
            live = sum(1 for row in workers if row["last_seen"] >= stamp - STALE_SECONDS and row["worker_id"] != worker_id)
            if live >= MAX_LIVE_WORKERS:
                raise MetricsCollectorError("live_worker_limit_exceeded")
            if current is not None and stamp < current["last_seen"]:
                raise MetricsSnapshotRegression("worker_timestamp_regressed")
            if current is None and len(workers) >= MAX_WORKER_GENERATIONS:
                needed = len(workers) - MAX_WORKER_GENERATIONS + 1
                stale_workers = db.execute(
                    "SELECT worker_id FROM metrics_workers WHERE last_seen < ? ORDER BY last_seen ASC LIMIT ?",
                    (stamp - STALE_SECONDS, needed),
                ).fetchall()
                if len(stale_workers) < needed:
                    raise MetricsCollectorError("worker_generation_limit_exceeded")
                retired_count = db.execute("SELECT COUNT(*) FROM metrics_retired_workers").fetchone()[0]
                if retired_count + len(stale_workers) > MAX_RETIRED_WORKERS:
                    raise MetricsCollectorError("retired_worker_limit_exceeded")
                for stale_worker in stale_workers:
                    db.execute(
                        "INSERT OR REPLACE INTO metrics_retired_workers(worker_id,expires_at) VALUES(?,?)",
                        (stale_worker["worker_id"], stamp + RETENTION_SECONDS),
                    )
                    db.execute("DELETE FROM metrics_workers WHERE worker_id=?", (stale_worker["worker_id"],))
            previous = json.loads(current["snapshot_json"]) if current else {}
            deltas = {key: self._subtract(value, previous[key]) if key in previous else value for key, value in values.items()}

            # Read this time bucket once instead of issuing one SELECT per
            # logical series. The transaction remains BEGIN IMMEDIATE, so the
            # snapshot of existing aggregates and subsequent UPSERTs are atomic.
            bucket_rows = db.execute(
                "SELECT metric_key,value_json FROM metrics_buckets WHERE bucket_start=?",
                (bucket,),
            ).fetchall()
            bucket_values = {row["metric_key"]: json.loads(row["value_json"]) for row in bucket_rows}
            upserts = []
            for key, delta in deltas.items():
                if isinstance(delta, dict):
                    if not (delta["count"] or delta["sum_ms"] or any(delta["buckets"])):
                        continue
                elif delta == 0:
                    continue
                total = self._add(bucket_values[key], delta) if key in bucket_values else delta
                upserts.append((
                    bucket,
                    key,
                    json.dumps(total, separators=(",", ":"), sort_keys=True, allow_nan=False),
                ))
            if upserts:
                db.executemany(
                    """INSERT INTO metrics_buckets(bucket_start,metric_key,value_json) VALUES(?,?,?)
                       ON CONFLICT(bucket_start,metric_key) DO UPDATE SET value_json=excluded.value_json""",
                    upserts,
                )
            db.execute(
                """INSERT INTO metrics_workers(worker_id,snapshot_json,last_seen,active_connections)
                   VALUES(?,?,?,?) ON CONFLICT(worker_id) DO UPDATE SET
                   snapshot_json=excluded.snapshot_json,last_seen=excluded.last_seen,
                   active_connections=excluded.active_connections""",
                (worker_id, encoded, stamp, active),
            )
            db.execute("DELETE FROM metrics_buckets WHERE bucket_start < ?", (int(cutoff // BUCKET_SECONDS) * BUCKET_SECONDS,))
            row_count = db.execute("SELECT COUNT(*) FROM metrics_buckets").fetchone()[0]
            if row_count > MAX_ROWS:
                evicted = db.execute(
                    """DELETE FROM metrics_buckets WHERE rowid IN
                       (SELECT rowid FROM metrics_buckets ORDER BY bucket_start ASC LIMIT ?)""",
                    (row_count - MAX_ROWS,),
                ).rowcount
                previous_evictions = db.execute(
                    "SELECT meta_value FROM metrics_meta WHERE meta_key='capacity_evicted_rows'"
                ).fetchone()[0]
                db.execute(
                    "UPDATE metrics_meta SET meta_value=? WHERE meta_key='capacity_evicted_rows'",
                    (min(previous_evictions + max(0, evicted), MAX_COUNTER),),
                )
                row_count = db.execute("SELECT COUNT(*) FROM metrics_buckets").fetchone()[0]
            db.commit()
            transaction_ms = (time.perf_counter_ns() - transaction_started_ns) / 1_000_000
            return {
                "series": len(values), "bucket": bucket, "rows": row_count,
                "lock_retries": lock_retries,
                "lock_wait_ms": round(lock_wait_ms, 6),
                "transaction_ms": round(transaction_ms, 6),
            }
        except Exception:
            if db.in_transaction:
                db.rollback()
            raise
        finally:
            db.close()

    def snapshot(self, *, now: float | None = None) -> dict[str, Any]:
        stamp = time.time() if now is None else float(now)
        if not math.isfinite(stamp) or stamp < 0:
            raise MetricsCollectorError("invalid_timestamp")
        cutoff_bucket = int((stamp - RETENTION_SECONDS) // BUCKET_SECONDS) * BUCKET_SECONDS
        db = self._connect()
        try:
            rows = db.execute(
                "SELECT metric_key,value_json FROM metrics_buckets WHERE bucket_start >= ? ORDER BY bucket_start",
                (cutoff_bucket,),
            ).fetchall()
            totals: dict[str, Any] = {}
            for row in rows:
                key, value = row["metric_key"], json.loads(row["value_json"])
                totals[key] = self._add(totals.get(key, 0), value)
            live = db.execute(
                "SELECT COUNT(*),COALESCE(SUM(active_connections),0) FROM metrics_workers WHERE last_seen >= ?",
                (stamp - STALE_SECONDS,),
            ).fetchone()
            oldest = db.execute(
                "SELECT MIN(bucket_start) FROM metrics_buckets WHERE bucket_start >= ?",
                (cutoff_bucket,),
            ).fetchone()[0]
            retained_rows = len(rows)
            capacity_evicted_rows = db.execute(
                "SELECT meta_value FROM metrics_meta WHERE meta_key='capacity_evicted_rows'"
            ).fetchone()[0]
            return {
                "schema_version": 1,
                "scope": "same_host_multi_worker",
                "worker_count": live[0],
                "active_websocket_connections": live[1],
                "series": totals,
                "oldest_bucket": oldest,
                "effective_retention_seconds": 0 if oldest is None else max(0, int(stamp - oldest)),
                "retention_seconds": RETENTION_SECONDS,
                "retained_aggregate_rows": retained_rows,
                "capacity_limit_rows": MAX_ROWS,
                "capacity_evicted_rows_total": capacity_evicted_rows,
                "capacity_eviction_seen": capacity_evicted_rows > 0,
                "degraded": False,
            }
        finally:
            db.close()
