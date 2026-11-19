import asyncio
from decimal import Decimal

from app.aggregation import Aggregator
from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_stream import OhlcvStreamHub

_NS = 1_000_000_000
_T0 = 1_704_067_200 * _NS


def make_bar(
    offset: int, *, raw_symbol: str = "ESZ6", instrument_id: int = 101,
    bucket_policy: str = "UTC_LEGACY", provider: str = "databento",
    series_type: str = "contract",
) -> OhlcvBar:
    start = _T0 + offset * _NS
    return OhlcvBar(
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=instrument_id,
        raw_symbol=raw_symbol,
        timeframe="1s",
        ts_start_ns=start,
        open=Decimal("100.00"),
        high=Decimal("101.00"),
        low=Decimal("99.00"),
        close=Decimal("100.50"),
        volume=Decimal("10"),
        ts_event_ns=start + 900_000_000,
        ts_received_ns=start + 950_000_000,
        sequence=offset + 1,
        provider=provider,
        series_type=series_type,
        origin="provider",
        completeness="complete",
        ts_provider_out_ns=start + 925_000_000,
        bucket_policy=bucket_policy,
    )


def test_snapshot_registration_is_atomic_boundary_for_following_updates() -> None:
    async def scenario() -> None:
        pipeline = OhlcvPipeline()
        first = make_bar(0)
        assert pipeline.apply(first) == "inserted"
        hub = OhlcvStreamHub(clock_ns=lambda: _T0 + 2 * _NS)

        subscription, snapshot, total = hub.subscribe_snapshot(
            pipeline,
            dataset="GLBX.MDP3",
            publisher_id=1,
            instrument_id=101,
            raw_symbol="ESZ6",
            timeframe="1s",
            limit=100,
            durable_cursor=41,
        )
        assert len(snapshot) == total == 1
        assert subscription.watermark == 0
        assert subscription.durable_cursor == 41

        second = make_bar(1)
        assert pipeline.apply(second) == "inserted"
        hub.publish(second, durable_cursor=42, durable_event_id="durable-event-42")

        update = subscription.queue.get_nowait()
        assert update["type"] == "market_data.ohlcv.update"
        assert update["streamId"] == subscription.stream_id
        assert update["sequence"] == 1
        assert update["cursor"] == "42"
        assert update["eventId"] == "durable-event-42"
        assert subscription.durable_cursor == 42
        assert update["bar"]["tsStartNs"] == str(_T0 + _NS)
        assert update["bar"]["tsProviderOutNs"] == str(_T0 + _NS + 925_000_000)
        assert update["isFinal"] is True
        assert subscription.watermark == 1
        hub.unsubscribe(subscription.stream_id)
        assert hub.subscriber_count == 0

    asyncio.run(scenario())


def test_stream_hub_filters_exact_series_identity() -> None:
    async def scenario() -> None:
        pipeline = OhlcvPipeline()
        pipeline.apply(make_bar(0))
        hub = OhlcvStreamHub()
        subscription, _, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100,
        )

        unrelated_series = [
            make_bar(1, raw_symbol="NQZ6", instrument_id=202),
            make_bar(1, provider="other-provider"),
            make_bar(1, series_type="continuous"),
        ]
        for bar in unrelated_series:
            hub.publish(bar)
        assert subscription.queue.empty()
        assert subscription.watermark == 0

    asyncio.run(scenario())


def test_stream_hub_keeps_bucket_policies_isolated_for_snapshots_and_updates() -> None:
    async def scenario() -> None:
        pipeline = OhlcvPipeline()
        legacy = make_bar(0, bucket_policy="UTC_LEGACY")
        fixed = make_bar(0, bucket_policy="UTC_FIXED_V1")
        assert pipeline.apply(legacy) == "inserted"
        assert pipeline.apply(fixed) == "inserted"
        hub = OhlcvStreamHub()
        legacy_sub, legacy_snapshot, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100, bucket_policy="UTC_LEGACY",
        )
        fixed_sub, fixed_snapshot, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100, bucket_policy="UTC_FIXED_V1",
        )
        assert [bar.bucket_policy for bar in legacy_snapshot] == ["UTC_LEGACY"]
        assert [bar.bucket_policy for bar in fixed_snapshot] == ["UTC_FIXED_V1"]
        legacy_revision = make_bar(1, bucket_policy="UTC_LEGACY")
        fixed_revision = make_bar(1, bucket_policy="UTC_FIXED_V1")
        assert pipeline.apply(legacy_revision) == "inserted"
        assert pipeline.apply(fixed_revision) == "inserted"
        hub.publish(legacy_revision)
        hub.publish(fixed_revision)
        legacy_update = legacy_sub.queue.get_nowait()
        fixed_update = fixed_sub.queue.get_nowait()
        assert legacy_update["series"]["bucketPolicy"] == "UTC_LEGACY"
        assert legacy_update["bar"]["bucketPolicy"] == "UTC_LEGACY"
        assert fixed_update["series"]["bucketPolicy"] == "UTC_FIXED_V1"
        assert fixed_update["bar"]["bucketPolicy"] == "UTC_FIXED_V1"
        assert legacy_sub.queue.empty() and fixed_sub.queue.empty()
    asyncio.run(scenario())


def test_slow_consumer_is_marked_for_resnapshot_without_silent_sequence_skip() -> None:
    async def scenario() -> None:
        pipeline = OhlcvPipeline()
        pipeline.apply(make_bar(0))
        hub = OhlcvStreamHub(queue_capacity=1)
        subscription, _, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100,
        )

        second = make_bar(1)
        third = make_bar(2)
        hub.publish(second)
        hub.publish(third)

        assert subscription.overflowed is True
        assert subscription.queue.qsize() == 1
        assert subscription.watermark == 1
        assert subscription.queue.get_nowait()["sequence"] == 1

    asyncio.run(scenario())


def test_hub_rejects_invalid_queue_capacity() -> None:
    for value in (0, -1, True, 1.5):
        try:
            OhlcvStreamHub(queue_capacity=value)
        except ValueError:
            continue
        raise AssertionError(f"queue capacity {value!r} should be rejected")

def test_derived_timeframe_revisions_are_streamed_to_the_matching_subscription() -> None:
    async def scenario() -> None:
        pipeline = OhlcvPipeline()
        hub = OhlcvStreamHub()
        aggregator = Aggregator(pipeline, on_derived_bar=hub.publish)

        for offset in range(4):
            child = make_bar(offset)
            assert pipeline.apply(child) == "inserted"
            aggregator.on_bar_applied(child)

        subscription, snapshot, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="5s", limit=100,
        )
        assert len(snapshot) == 1
        assert snapshot[0].origin == "derived"

        fifth = make_bar(4)
        assert pipeline.apply(fifth) == "inserted"
        aggregator.on_bar_applied(fifth)

        update = subscription.queue.get_nowait()
        assert update["series"]["timeframe"] == "5s"
        assert update["bar"]["origin"] == "derived"
        assert update["sequence"] == 1
        assert update["isFinal"] is False

    asyncio.run(scenario())



def test_stream_hub_rejects_invalid_durable_cursor() -> None:
    pipeline = OhlcvPipeline()
    for cursor in (-1, True, 1.5):
        try:
            OhlcvStreamHub().subscribe_snapshot(
                pipeline, dataset="GLBX.MDP3", publisher_id=1,
                instrument_id=101, raw_symbol="ESZ6", timeframe="1s",
                limit=10, durable_cursor=cursor,
            )
        except ValueError:
            continue
        raise AssertionError(f"durable cursor {cursor!r} should be rejected")


def test_stream_hub_routes_same_series_by_provider_without_cross_talk() -> None:
    async def scenario() -> None:
        pipeline = OhlcvPipeline()
        assert pipeline.apply(make_bar(0, provider="databento")) == "inserted"
        assert pipeline.apply(make_bar(0, provider="provider-b")) == "inserted"
        hub = OhlcvStreamHub()
        primary, primary_bars, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100,
        )
        secondary, secondary_bars, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100, provider="provider-b",
        )
        assert [bar.provider for bar in primary_bars] == ["databento"]
        assert [bar.provider for bar in secondary_bars] == ["provider-b"]
        update = make_bar(1, provider="provider-b")
        assert pipeline.apply(update) == "inserted"
        hub.publish(update)
        assert primary.queue.empty()
        assert secondary.queue.qsize() == 1
        assert secondary.queue.get_nowait()["bar"]["provider"] == "provider-b"
        hub.unsubscribe(primary.stream_id)
        hub.unsubscribe(secondary.stream_id)
    asyncio.run(scenario())


def test_replay_boundary_discards_covered_events_and_resequences_live_queue():
    async def scenario():
        pipeline = OhlcvPipeline()
        first = make_bar(0)
        assert pipeline.apply(first) == "inserted"
        hub = OhlcvStreamHub()
        subscription, _, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100, durable_cursor=41,
        )
        second = make_bar(1)
        third = make_bar(2)
        assert pipeline.apply(second) == "inserted"
        assert pipeline.apply(third) == "inserted"
        hub.publish(second, durable_cursor=42, durable_event_id="event-42")
        hub.publish(third, durable_cursor=43, durable_event_id="event-43")

        replay_series = {
            "provider": "databento", "dataset": "GLBX.MDP3",
            "publisherId": 1, "instrumentId": 101,
            "seriesType": "contract", "rawSymbol": "ESZ6",
            "timeframe": "1s", "bucketPolicy": "UTC_LEGACY",
            "calendarId": "", "calendarVersion": "",
        }
        merged = hub.merge_replay_boundary(
            subscription,
            [{"cursor": 42, "series": replay_series}],
            replay_end_cursor=42,
        )
        assert merged == 1
        assert subscription.queue.qsize() == 1
        live = subscription.queue.get_nowait()
        assert live["cursor"] == "43"
        assert live["eventId"] == "event-43"
        assert live["sequence"] == 2
        assert subscription.watermark == 2
        assert subscription.durable_cursor == 43

    asyncio.run(scenario())


def test_replay_boundary_fails_closed_on_overflow_or_wrong_series():
    async def scenario():
        pipeline = OhlcvPipeline()
        assert pipeline.apply(make_bar(0)) == "inserted"
        hub = OhlcvStreamHub(queue_capacity=1)
        subscription, _, _ = hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100, durable_cursor=41,
        )
        hub.publish(make_bar(1), durable_cursor=42)
        hub.publish(make_bar(2), durable_cursor=43)
        from app.ohlcv_stream import OhlcvStreamResnapshotRequired
        try:
            hub.merge_replay_boundary(subscription, [], 41)
        except OhlcvStreamResnapshotRequired:
            pass
        else:
            raise AssertionError("overflow must require a fresh snapshot")

        other_hub = OhlcvStreamHub()
        other_sub, _, _ = other_hub.subscribe_snapshot(
            pipeline, dataset="GLBX.MDP3", publisher_id=1, instrument_id=101,
            raw_symbol="ESZ6", timeframe="1s", limit=100, durable_cursor=41,
        )
        wrong_series = {
            "provider": "databento", "dataset": "GLBX.MDP3",
            "publisherId": 1, "instrumentId": 999,
            "seriesType": "contract", "rawSymbol": "NQZ6",
            "timeframe": "1s", "bucketPolicy": "UTC_LEGACY",
            "calendarId": "", "calendarVersion": "",
        }
        try:
            other_hub.merge_replay_boundary(
                other_sub, [{"cursor": 42, "series": wrong_series}], 42,
            )
        except ValueError as exc:
            assert "subscription series" in str(exc)
        else:
            raise AssertionError("wrong-series replay must be rejected")

    asyncio.run(scenario())
