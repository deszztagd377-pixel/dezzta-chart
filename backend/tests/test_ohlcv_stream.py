import asyncio
from decimal import Decimal

from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_stream import OhlcvStreamHub

_NS = 1_000_000_000
_T0 = 1_704_067_200 * _NS


def make_bar(offset: int, *, raw_symbol: str = "ESZ6", instrument_id: int = 101) -> OhlcvBar:
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
        provider="databento",
        series_type="contract",
        origin="provider",
        completeness="complete",
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
        )
        assert len(snapshot) == total == 1
        assert subscription.watermark == 0

        second = make_bar(1)
        assert pipeline.apply(second) == "inserted"
        hub.publish(second)

        update = subscription.queue.get_nowait()
        assert update["type"] == "market_data.ohlcv.update"
        assert update["streamId"] == subscription.stream_id
        assert update["sequence"] == 1
        assert update["bar"]["tsStartNs"] == str(_T0 + _NS)
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

        other = make_bar(1, raw_symbol="NQZ6", instrument_id=202)
        hub.publish(other)
        assert subscription.queue.empty()
        assert subscription.watermark == 0

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
