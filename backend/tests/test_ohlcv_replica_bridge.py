from __future__ import annotations

from decimal import Decimal

import pytest

from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_replica_bridge import (
    ReplicaPipelineDivergence,
    forward_replica_event,
    hydrate_replica_pipeline,
)
from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore
from app.ohlcv_stream import OhlcvStreamHub

NS = 1_000_000_000


def make_bar(index=0):
    return OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=123, series_type="contract",
        timeframe="1m", ts_start_ns=index * 60 * NS, raw_symbol="ESZ6",
        open=Decimal("100"), high=Decimal("103"), low=Decimal("99"),
        close=Decimal(str(101 + index)), volume=Decimal("12.5"),
        ts_event_ns=100 + index, ts_received_ns=110 + index,
        sequence=index + 1, sequence_origin="local", origin="provider",
        completeness="unknown",
    )


def install_replica(source, tmp_path):
    snapshot = tmp_path / "snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica.sqlite3"))
    replica.install_global_snapshot(
        str(snapshot), expected_source_id=source.source_id(),
    )
    return replica


def test_hydration_restores_every_retained_bar_and_durable_cursor(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    assert source.apply(make_bar(0)) == "inserted"
    assert source.apply(make_bar(1)) == "inserted"
    replica = install_replica(source, tmp_path)
    pipeline = OhlcvPipeline()

    result = hydrate_replica_pipeline(replica, pipeline)

    bars, total = pipeline.query(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=123, timeframe="1m",
        raw_symbol="ESZ6", limit=10,
    )
    assert result == {
        "bar_count": 2,
        "applied_cursor": 2,
        "retention_floor": 0,
    }
    assert total == 2
    assert [bar.close for bar in bars] == [Decimal("101"), Decimal("102")]


def test_live_replica_event_fans_out_and_duplicate_cursor_is_suppressed(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    replica = install_replica(source, tmp_path)
    bar = make_bar(0)
    assert source.apply(bar) == "inserted"
    event_page = source.read_outbox_batch(after_cursor=0, limit=10)
    assert event_page["status"] == "ok"
    event = event_page["events"][0]
    assert replica.apply_replica_event(
        event, source_id=source.source_id(),
    )["status"] == "applied"

    pipeline = OhlcvPipeline()
    hub = OhlcvStreamHub(clock_ns=lambda: 123)
    subscription, snapshot, total = hub.subscribe_snapshot(
        pipeline,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", limit=10, durable_cursor=0,
    )
    assert snapshot == [] and total == 0

    assert forward_replica_event(event, pipeline, hub) == "inserted"
    assert forward_replica_event(event, pipeline, hub) == "duplicate"

    assert subscription.queue.qsize() == 1
    message = subscription.queue.get_nowait()
    assert message["cursor"] == "1"
    assert message["eventId"] == event["eventId"]
    assert message["sequence"] == 1
    assert subscription.durable_cursor == 1


def test_hydrated_snapshot_watermark_suppresses_replayed_old_event(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    first = make_bar(0)
    assert source.apply(first) == "inserted"
    first_event_page = source.read_outbox_batch(after_cursor=0, limit=1)
    assert first_event_page["status"] == "ok"
    first_event = first_event_page["events"][0]
    assert source.apply(make_bar(1)) == "inserted"
    replica = install_replica(source, tmp_path)
    pipeline = OhlcvPipeline()
    hydration = hydrate_replica_pipeline(replica, pipeline)

    hub = OhlcvStreamHub()
    subscription, bars, _ = hub.subscribe_snapshot(
        pipeline,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", limit=10,
        durable_cursor=hydration["applied_cursor"],
    )
    assert len(bars) == 2
    assert forward_replica_event(first_event, pipeline, hub) == "duplicate"
    assert subscription.queue.empty()
    assert subscription.durable_cursor == 2


def test_forward_rejects_pipeline_divergence_instead_of_silent_drop(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    bar = make_bar(0)
    assert source.apply(bar) == "inserted"
    event_page = source.read_outbox_batch(after_cursor=0, limit=1)
    assert event_page["status"] == "ok"
    event = event_page["events"][0]
    pipeline = OhlcvPipeline()
    # Seed a conflicting raw symbol at the same bar identity.
    conflicting = OhlcvBar(
        provider=bar.provider, dataset=bar.dataset,
        publisher_id=bar.publisher_id, instrument_id=bar.instrument_id,
        series_type=bar.series_type, timeframe=bar.timeframe,
        ts_start_ns=bar.ts_start_ns, raw_symbol="NQZ6",
        open=bar.open, high=bar.high, low=bar.low, close=bar.close,
        volume=bar.volume, ts_event_ns=bar.ts_event_ns,
        ts_received_ns=bar.ts_received_ns, sequence=bar.sequence,
        sequence_origin=bar.sequence_origin, origin=bar.origin,
        completeness=bar.completeness,
    )
    pipeline.apply(conflicting)
    with pytest.raises(ReplicaPipelineDivergence):
        forward_replica_event(event, pipeline, OhlcvStreamHub())
