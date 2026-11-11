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
import tempfile
import time
from pathlib import Path

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


def run_benchmark(*, bars: int, batch_size: int, database_path: str | None = None) -> dict[str, object]:
    if not 1 <= bars <= OUTBOX_MAX_EVENTS:
        raise ValueError(f"bars must be between 1 and {OUTBOX_MAX_EVENTS}")
    if not 1 <= batch_size <= 1_000:
        raise ValueError("batch_size must be between 1 and 1000")

    temporary_directory = None
    if database_path is None:
        temporary_directory = tempfile.TemporaryDirectory(prefix="dezzta-ohlcv-benchmark-")
        database_path = str(Path(temporary_directory.name) / "benchmark.sqlite3")

    try:
        store = SQLiteOhlcvStore(database_path)
        persist_samples: list[float] = []
        for index in range(bars):
            started = time.perf_counter_ns()
            outcome = store.apply(_bar(index))
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
            if outcome != "inserted":
                raise RuntimeError(f"synthetic bar {index} was not inserted: {outcome}")
            persist_samples.append(elapsed_ms)

        high_water = store.outbox_high_water()
        replay_samples: list[float] = []
        replayed_events = 0
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
            replayed_events += len(events)
            next_cursor = page.get("next_cursor")
            if not isinstance(next_cursor, int) or next_cursor <= cursor:
                raise RuntimeError("replay cursor failed to advance")
            cursor = next_cursor
            if not page.get("has_more", False):
                break

        if replayed_events != bars:
            raise RuntimeError(
                f"replay count mismatch: expected {bars}, received {replayed_events}"
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
            "persist_latency": _summary(persist_samples),
            "replay_page_latency": _summary(replay_samples),
            "notes": [
                "Single-process local SQLite measurement only.",
                "Not a provider, WebSocket, reconnect-storm, or production-host benchmark.",
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
    parser.add_argument("--database", default=None, help="optional explicit SQLite path")
    args = parser.parse_args()
    if args.bars > OUTBOX_MAX_EVENTS:
        parser.error(f"--bars cannot exceed {OUTBOX_MAX_EVENTS}")
    if args.batch_size > 1_000:
        parser.error("--batch-size cannot exceed 1000")
    report = run_benchmark(
        bars=args.bars,
        batch_size=args.batch_size,
        database_path=args.database,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
