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


def test_replica_query_snapshot_returns_atomic_checkpoint_watermark(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    assert source.apply(make_bar(0)) == "inserted"
    assert source.apply(make_bar(1)) == "inserted"
    replica = install_replica(source, tmp_path)

    snapshot = replica.query_snapshot(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=123, timeframe="1m",
        raw_symbol="ESZ6", limit=1,
    )

    assert snapshot["cursor"] == 2
    assert snapshot["high_water"] == 2
    assert snapshot["retention_floor"] == 0
    assert snapshot["source_id"] == source.source_id()
    assert snapshot["total"] == 2
    assert len(snapshot["bars"]) == 1
    assert snapshot["bars"][0].close == Decimal("102")


def test_replica_query_snapshot_fails_closed_before_snapshot_install(tmp_path):
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "empty-replica.sqlite3"))
    with pytest.raises(RuntimeError, match="verified replica snapshot"):
        replica.query_snapshot()


def test_replica_snapshot_and_hub_registration_share_checkpoint_boundary(tmp_path):
    from app.ohlcv_replica_bridge import subscribe_replica_snapshot

    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    replica = install_replica(source, tmp_path)
    pipeline = OhlcvPipeline()
    hub = OhlcvStreamHub()

    first = make_bar(0)
    assert source.apply(first) == "inserted"
    first_event = source.read_outbox_batch(after_cursor=0, limit=1)["events"][0]
    # Simulate the consumer's durable SQLite commit before its event-loop
    # callback has run. The replica checkpoint is ahead of the in-memory pipe.
    assert replica.apply_replica_event(
        first_event, source_id=source.source_id(),
    )["status"] == "applied"

    subscription, snapshot, total, checkpoint = subscribe_replica_snapshot(
        replica, hub,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", bucket_policy="UTC_LEGACY",
        limit=10,
    )
    assert [bar.close for bar in snapshot] == [Decimal("101")]
    assert total == 1
    assert checkpoint == {
        "cursor": 1, "high_water": 1, "retention_floor": 0,
        "source_id": source.source_id(),
    }
    assert subscription.durable_cursor == 1

    # The delayed callback catches up the pipeline but is correctly fenced
    # from re-emitting an event already represented by the durable snapshot.
    assert forward_replica_event(first_event, pipeline, hub) == "inserted"
    assert subscription.queue.empty()

    second = make_bar(1)
    assert source.apply(second) == "inserted"
    second_event = source.read_outbox_batch(after_cursor=1, limit=1)["events"][0]
    assert replica.apply_replica_event(
        second_event, source_id=source.source_id(),
    )["status"] == "applied"
    assert forward_replica_event(second_event, pipeline, hub) == "inserted"

    live = subscription.queue.get_nowait()
    assert live["cursor"] == "2"
    assert live["eventId"] == second_event["eventId"]
    assert live["sequence"] == 1
    assert subscription.durable_cursor == 2


def test_replica_snapshot_hub_registration_rejects_mixed_series_bars():
    pipeline = OhlcvPipeline()
    hub = OhlcvStreamHub()
    with pytest.raises(ValueError, match="outside the requested exact series"):
        hub.subscribe_snapshot_bars(
            [make_bar(0), make_bar(1).__class__(
                provider="databento", dataset="GLBX.MDP3",
                publisher_id=1, instrument_id=999, series_type="contract",
                timeframe="1m", ts_start_ns=60 * NS, raw_symbol="NQZ6",
                open=Decimal("100"), high=Decimal("103"), low=Decimal("99"),
                close=Decimal("102"), volume=Decimal("12.5"),
                ts_event_ns=NS + 100, ts_received_ns=NS + 110,
                sequence=2, sequence_origin="local", origin="provider",
                completeness="unknown",
            )],
            total=2, dataset="GLBX.MDP3", publisher_id=1,
            instrument_id=123, raw_symbol="ESZ6", timeframe="1m",
            limit=10, bucket_policy="UTC_LEGACY",
        )


def test_forward_rejects_event_series_that_disagrees_with_bar_payload():
    from app.ohlcv_replica_bridge import _bar_from_event

    bar = make_bar(0)
    event = {
        "type": "market_data.ohlcv.update", "version": 1,
        "eventId": "series-mismatch", "operation": "upsert", "cursor": 1,
        "series": {
            "provider": bar.provider, "dataset": bar.dataset,
            "publisherId": bar.publisher_id, "instrumentId": 999,
            "seriesType": bar.series_type, "rawSymbol": bar.raw_symbol,
            "timeframe": bar.timeframe, "bucketPolicy": bar.bucket_policy,
            "calendarId": bar.calendar_id, "calendarVersion": bar.calendar_version,
        },
        "bar": {
            "dataset": bar.dataset, "provider": bar.provider,
            "publisherId": bar.publisher_id, "instrumentId": bar.instrument_id,
            "rawSymbol": bar.raw_symbol, "seriesType": bar.series_type,
            "timeframe": bar.timeframe, "bucketPolicy": bar.bucket_policy,
            "calendarId": bar.calendar_id, "calendarVersion": bar.calendar_version,
            "tsStartNs": str(bar.ts_start_ns), "open": str(bar.open),
            "high": str(bar.high), "low": str(bar.low), "close": str(bar.close),
            "volume": str(bar.volume), "tsEventNs": str(bar.ts_event_ns),
            "tsReceivedNs": str(bar.ts_received_ns),
            "tsProviderOutNs": None if bar.ts_provider_out_ns is None else str(bar.ts_provider_out_ns),
            "sequence": bar.sequence, "sequenceOrigin": bar.sequence_origin,
            "origin": bar.origin, "completeness": bar.completeness,
        },
    }
    with pytest.raises(ValueError, match="series identity does not match"):
        _bar_from_event(event)



@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("tsStartNs", 100),
        ("tsStartNs", True),
        ("tsEventNs", "-1"),
        ("tsReceivedNs", "1.0"),
        ("tsProviderOutNs", "١٢"),
    ],
)
def test_forward_rejects_noncanonical_nanosecond_fields(tmp_path, field, invalid_value):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    assert source.apply(make_bar(0)) == "inserted"
    event = source.read_outbox_batch(after_cursor=0, limit=1)["events"][0]
    event["bar"][field] = invalid_value

    with pytest.raises(ValueError, match=field):
        forward_replica_event(event, OhlcvPipeline(), OhlcvStreamHub())


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("open", 100),
        ("high", True),
        ("low", "1e3"),
        ("close", "NaN"),
        ("volume", "01"),
    ],
)
def test_forward_rejects_noncanonical_decimal_fields(tmp_path, field, invalid_value):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    assert source.apply(make_bar(0)) == "inserted"
    event = source.read_outbox_batch(after_cursor=0, limit=1)["events"][0]
    event["bar"][field] = invalid_value

    with pytest.raises(ValueError, match=field):
        forward_replica_event(event, OhlcvPipeline(), OhlcvStreamHub())


def test_forward_accepts_decimal_string_provider_output_timestamp(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    bar = make_bar(0)
    bar = OhlcvBar(
        provider=bar.provider, dataset=bar.dataset, publisher_id=bar.publisher_id,
        instrument_id=bar.instrument_id, series_type=bar.series_type,
        timeframe=bar.timeframe, ts_start_ns=bar.ts_start_ns,
        raw_symbol=bar.raw_symbol, open=bar.open, high=bar.high, low=bar.low,
        close=bar.close, volume=bar.volume, ts_event_ns=bar.ts_event_ns,
        ts_received_ns=bar.ts_received_ns, sequence=bar.sequence,
        sequence_origin=bar.sequence_origin, origin=bar.origin,
        completeness=bar.completeness, ts_provider_out_ns=120,
    )
    assert source.apply(bar) == "inserted"
    event = source.read_outbox_batch(after_cursor=0, limit=1)["events"][0]
    assert event["bar"]["tsProviderOutNs"] == "120"
    assert forward_replica_event(event, OhlcvPipeline(), OhlcvStreamHub()) == "inserted"


def test_hydration_reads_bars_and_checkpoint_from_one_atomic_snapshot(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    assert source.apply(make_bar(0)) == "inserted"
    assert source.apply(make_bar(1)) == "inserted"
    replica = install_replica(source, tmp_path)
    pipeline = OhlcvPipeline()

    # A consumer commit between separate reads could create cursor/bar skew.
    replica.checkpoint = lambda: pytest.fail("non-atomic checkpoint read used")
    replica.load_bars = lambda: pytest.fail("non-atomic bar read used")

    result = hydrate_replica_pipeline(replica, pipeline)

    assert result == {
        "bar_count": 2,
        "applied_cursor": 2,
        "retention_floor": 0,
    }
    bars, total = pipeline.query(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=123, timeframe="1m",
        raw_symbol="ESZ6", limit=10,
    )
    assert total == 2
    assert [bar.close for bar in bars] == [Decimal("101"), Decimal("102")]


def test_replica_load_snapshot_fails_closed_without_checkpoint(tmp_path):
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "empty-replica.sqlite3"))
    with pytest.raises(RuntimeError, match="verified replica snapshot"):
        replica.load_snapshot()
