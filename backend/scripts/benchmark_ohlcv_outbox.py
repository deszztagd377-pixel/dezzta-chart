"""Reproducible local-only OHLCV SQLite outbox microbenchmark.

The generated bars are synthetic and must never be described as provider data.
Run from the backend directory:
    python scripts/benchmark_ohlcv_outbox.py --bars 10000 --batch-size 500
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
import os
import platform
import statistics
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import sys
import tempfile
import time
from pathlib import Path

# Make direct execution from any working directory resolve backend/app.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ohlcv import OhlcvBar
from app.ohlcv_store import OUTBOX_MAX_EVENTS, SQLiteOhlcvStore

_PROVIDER = "benchmark-synthetic"
_DATASET = "SYNTHETIC-NOT-MARKET-DATA"
_PUBLISHER_ID = 1
_INSTRUMENT_ID = 1
_RAW_SYMBOL = "SYNTHETIC"
_TIMEFRAME = "1s"
_BUCKET_POLICY = "UTC_LEGACY"
_BASE_NS = 1_700_000_000_000_000_000


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _percentile(samples_ms: list[float], percentile: float) -> float:
    if not samples_ms:
        return 0.0
    ordered = sorted(samples_ms)
    # Nearest-rank percentile; deterministic for small sample sets.
    rank = max(1, int((percentile * len(ordered) + 0.9999999999)))
    return round(ordered[min(rank - 1, len(ordered) - 1)], 6)


def _summary(samples_ms: list[float]) -> dict[str, float | int]:
    return {
        "samples": len(samples_ms),
        "p50_ms": _percentile(samples_ms, 0.50),
        "p95_ms": _percentile(samples_ms, 0.95),
        "p99_ms": _percentile(samples_ms, 0.99),
        "mean_ms": round(statistics.fmean(samples_ms), 6) if samples_ms else 0.0,
    }


def _bar(index: int) -> OhlcvBar:
    start_ns = _BASE_NS + index * 1_000_000_000
    close = Decimal("100") + Decimal(index % 1000) / Decimal("100")
    return OhlcvBar(
        provider=_PROVIDER,
        dataset=_DATASET,
        publisher_id=_PUBLISHER_ID,
        instrument_id=_INSTRUMENT_ID,
        raw_symbol=_RAW_SYMBOL,
        series_type="contract",
        timeframe=_TIMEFRAME,
        ts_start_ns=start_ns,
        open=close - Decimal("0.25"),
        high=close + Decimal("0.50"),
        low=close - Decimal("0.50"),
        close=close,
        volume=Decimal("10.000"),
        ts_event_ns=start_ns + 900_000_000,
        ts_received_ns=start_ns + 950_000_000,
        sequence=index + 1,
        sequence_origin="local",
        origin="provider",
        completeness="complete",
        ts_provider_out_ns=start_ns + 925_000_000,
        bucket_policy=_BUCKET_POLICY,
    )


def _concurrent_replay_reader(
    store: SQLiteOhlcvStore,
    *,
    reader_id: int,
    batch_size: int,
    writer_done: Event,
) -> dict[str, object]:
    """Replay one exact synthetic series while the single writer is active."""
    cursor = 0
    last_event_cursor = 0
    replayed_events = 0
    replayed_event_ids: set[str] = set()
    page_samples_ms: list[float] = []

    while True:
        started = time.perf_counter_ns()
        page = store.replay_outbox(
            after_cursor=cursor,
            provider=_PROVIDER,
            dataset=_DATASET,
            publisher_id=_PUBLISHER_ID,
            instrument_id=_INSTRUMENT_ID,
            series_type="contract",
            raw_symbol=_RAW_SYMBOL,
            timeframe=_TIMEFRAME,
            bucket_policy=_BUCKET_POLICY,
            limit=batch_size,
        )
        page_samples_ms.append((time.perf_counter_ns() - started) / 1_000_000)
        if page.get("status") != "ok":
            raise RuntimeError(f"concurrent replay reader {reader_id} was refused: {page}")

        high_water = page.get("high_water")
        next_cursor = page.get("next_cursor")
        has_more = page.get("has_more")
        events = page.get("events")
        if (
            not isinstance(high_water, int)
            or isinstance(high_water, bool)
            or high_water < cursor
            or not isinstance(next_cursor, int)
            or isinstance(next_cursor, bool)
            or next_cursor < cursor
            or next_cursor > high_water
            or not isinstance(has_more, bool)
            or not isinstance(events, list)
        ):
            raise RuntimeError(f"concurrent replay reader {reader_id} received invalid page metadata")

        for event in events:
            event_cursor = event.get("cursor")
            event_id = event.get("eventId")
            if (
                not isinstance(event_cursor, int)
                or isinstance(event_cursor, bool)
                or event_cursor <= last_event_cursor
                or event_cursor > high_water
            ):
                raise RuntimeError(f"concurrent replay reader {reader_id} received an invalid event cursor")
            if not isinstance(event_id, str) or not event_id or event_id in replayed_event_ids:
                raise RuntimeError(f"concurrent replay reader {reader_id} received a missing or duplicate event ID")
            replayed_event_ids.add(event_id)
            last_event_cursor = event_cursor

        replayed_events += len(events)
        if has_more and (not events or next_cursor != last_event_cursor):
            raise RuntimeError(f"concurrent replay reader {reader_id} page boundary is inconsistent")
        if not has_more and next_cursor != high_water:
            raise RuntimeError(f"concurrent replay reader {reader_id} did not advance to high-water")

        cursor = next_cursor
        if writer_done.is_set():
            # The page's high-water belongs to its read snapshot. The writer
            # may have committed its final batch after that snapshot was read
            # but before writer_done became visible. Recheck the durable
            # high-water after completion before deciding the replay is done.
            if cursor == store.outbox_high_water():
                break
        if not events and not has_more:
            writer_done.wait(0.001)

    return {
        "reader_id": reader_id,
        "cursor": cursor,
        "replayed_events": replayed_events,
        "page_latency_ms": page_samples_ms,
    }


def run_benchmark(*, bars: int, batch_size: int, readers: int = 2, database_path: str | None = None) -> dict[str, object]:
    if not 1 <= bars <= OUTBOX_MAX_EVENTS:
        raise ValueError(f"bars must be between 1 and {OUTBOX_MAX_EVENTS}")
    if not 1 <= batch_size <= 1_000:
        raise ValueError("batch_size must be between 1 and 1000")
    if not 1 <= readers <= 4:
        raise ValueError("readers must be between 1 and 4")

    temporary_directory = None
    if database_path is None:
        temporary_directory = tempfile.TemporaryDirectory(prefix="dezzta-ohlcv-benchmark-")
        database_path = str(Path(temporary_directory.name) / "benchmark.sqlite3")
    else:
        # O_EXCL also rejects dangling symlinks and closes the exists/open race.
        try:
            descriptor = os.open(
                database_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except FileExistsError as exc:
            raise FileExistsError(
                "refusing to modify an existing database; choose a new benchmark path"
            ) from exc
        else:
            os.close(descriptor)

    try:
        store = SQLiteOhlcvStore(database_path)
        persist_samples: list[float] = []
        writer_done = Event()
        with ThreadPoolExecutor(max_workers=readers) as reader_pool:
            reader_futures = [
                reader_pool.submit(
                    _concurrent_replay_reader,
                    store,
                    reader_id=reader_id,
                    batch_size=batch_size,
                    writer_done=writer_done,
                )
                for reader_id in range(1, readers + 1)
            ]
            try:
                # Preserve the architecture's single-writer contract while
                # exercising concurrent durable replay readers.
                for index in range(bars):
                    started = time.perf_counter_ns()
                    outcome = store.apply(_bar(index))
                    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
                    if outcome != "inserted":
                        raise RuntimeError(f"synthetic bar {index} was not inserted: {outcome}")
                    persist_samples.append(elapsed_ms)
            finally:
                writer_done.set()
            concurrent_reader_results = [future.result() for future in reader_futures]

        for reader_result in concurrent_reader_results:
            if (
                reader_result["replayed_events"] != bars
                or reader_result["cursor"] != store.outbox_high_water()
            ):
                raise RuntimeError(
                    "concurrent replay reader did not consume the complete durable stream: "
                    f"{reader_result}"
                )
        concurrent_replay_samples = [
            sample
            for reader_result in concurrent_reader_results
            for sample in reader_result["page_latency_ms"]
        ]

        high_water = store.outbox_high_water()
        replay_samples: list[float] = []
        replayed_events = 0
        replayed_event_ids: set[str] = set()
        last_event_cursor = 0
        cursor = 0
        while cursor < high_water:
            started = time.perf_counter_ns()
            page = store.replay_outbox(
                after_cursor=cursor,
                provider=_PROVIDER,
                dataset=_DATASET,
                publisher_id=_PUBLISHER_ID,
                instrument_id=_INSTRUMENT_ID,
                series_type="contract",
                raw_symbol=_RAW_SYMBOL,
                timeframe=_TIMEFRAME,
                bucket_policy=_BUCKET_POLICY,
                limit=batch_size,
            )
            replay_samples.append((time.perf_counter_ns() - started) / 1_000_000)
            if page.get("status") != "ok":
                raise RuntimeError(f"replay refused benchmark cursor: {page}")
            events = page.get("events")
            if not isinstance(events, list):
                raise RuntimeError("replay returned an invalid events collection")
            for event in events:
                event_cursor = event.get("cursor")
                event_id = event.get("eventId")
                if (
                    not isinstance(event_cursor, int)
                    or isinstance(event_cursor, bool)
                    or event_cursor <= last_event_cursor
                    or event_cursor > high_water
                ):
                    raise RuntimeError("replay event cursor is invalid or out of order")
                if not isinstance(event_id, str) or not event_id or event_id in replayed_event_ids:
                    raise RuntimeError("replay event ID is missing or duplicated")
                replayed_event_ids.add(event_id)
                last_event_cursor = event_cursor
            replayed_events += len(events)
            next_cursor = page.get("next_cursor")
            if (
                not isinstance(next_cursor, int)
                or isinstance(next_cursor, bool)
                or next_cursor <= cursor
                or next_cursor > high_water
            ):
                raise RuntimeError("replay cursor failed to advance within the durable high-water")
            has_more = page.get("has_more")
            if not isinstance(has_more, bool):
                raise RuntimeError("replay returned an invalid has_more flag")
            if has_more and (not events or next_cursor != last_event_cursor):
                raise RuntimeError("replay page cursor does not match its final event")
            if not has_more and next_cursor != high_water:
                raise RuntimeError("final replay page did not reach the durable high-water")
            cursor = next_cursor
            if not has_more:
                break

        if replayed_events != bars or len(replayed_event_ids) != bars:
            raise RuntimeError(
                f"replay count mismatch: expected {bars}, received {replayed_events}"
            )
        if cursor != high_water:
            raise RuntimeError("replay terminated before the durable high-water")

        # Validate persisted rows independently of the replay API so a broken
        # query cannot make an incomplete benchmark look successful.
        with sqlite3.connect(database_path) as verification_db:
            integrity = verification_db.execute("PRAGMA integrity_check").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise RuntimeError(f"SQLite integrity_check failed: {integrity}")
            identity_params = (
                _PROVIDER, _DATASET, _PUBLISHER_ID, _INSTRUMENT_ID,
                "contract", _RAW_SYMBOL, _TIMEFRAME, _BUCKET_POLICY,
            )
            stored_bars = verification_db.execute(
                """SELECT COUNT(*) FROM ohlcv_bars
                WHERE provider=? AND dataset=? AND publisher_id=? AND instrument_id=?
                AND series_type=? AND raw_symbol=? AND timeframe=? AND bucket_policy=?""",
                identity_params,
            ).fetchone()[0]
            stored_events = verification_db.execute(
                """SELECT COUNT(*) FROM ohlcv_outbox
                WHERE provider=? AND dataset=? AND publisher_id=? AND instrument_id=?
                AND series_type=? AND raw_symbol=? AND timeframe=? AND bucket_policy=?""",
                identity_params,
            ).fetchone()[0]
        if stored_bars != bars or stored_events != bars:
            raise RuntimeError(
                "SQLite row-count mismatch: "
                f"expected {bars} bars/events, found {stored_bars}/{stored_events}"
            )

        return {
            "benchmark": "sqlite_ohlcv_outbox_local_microbenchmark",
            "data_source": "synthetic_only_not_market_data",
            "commit_sha": os.environ.get("GITHUB_SHA", "not_supplied"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "bars_inserted": bars,
            "outbox_high_water": high_water,
            "replay_batch_size": batch_size,
            "replayed_events": replayed_events,
            "concurrent_replay_readers": readers,
            "concurrent_replay_events_per_reader": [
                result["replayed_events"] for result in concurrent_reader_results
            ],
            "concurrent_replay_page_latency": _summary(concurrent_replay_samples),
            "persist_latency": _summary(persist_samples),
            "replay_page_latency": _summary(replay_samples),
            "notes": [
                "Single-process SQLite measurement with one writer and concurrent reader threads.",
                "Not a provider, WebSocket, reconnect-storm, or production-host benchmark.",
                "Not a multi-process benchmark; reader threads share one process.",
                "Do not infer provider latency, multi-worker capacity, or production SLOs.",
            ],
        }
    finally:
        if temporary_directory is not None:
            temporary_directory.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bars", type=_positive_int, default=1_000)
    parser.add_argument("--batch-size", type=_positive_int, default=500)
    parser.add_argument("--readers", type=_positive_int, default=2, help="concurrent replay readers (1-4); writer remains single-threaded")
    parser.add_argument("--database", default=None, help="optional explicit SQLite path")
    args = parser.parse_args()
    if args.bars > OUTBOX_MAX_EVENTS:
        parser.error(f"--bars cannot exceed {OUTBOX_MAX_EVENTS}")
    if args.batch_size > 1_000:
        parser.error("--batch-size cannot exceed 1000")
    if args.readers > 4:
        parser.error("--readers cannot exceed 4")
    report = run_benchmark(
        bars=args.bars,
        batch_size=args.batch_size,
        readers=args.readers,
        database_path=args.database,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
