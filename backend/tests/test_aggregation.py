from decimal import Decimal

from app.aggregation import CHILDREN, PARENT, Aggregator
from app.coverage import CoverageTracker
from app.ohlcv import FIXED_INTERVAL_SECONDS, OhlcvBar, OhlcvPipeline, bucket_start_ns
from helpers import NS, T0, make_service, rec

ALL_TIMEFRAMES = [*FIXED_INTERVAL_SECONDS, "1w", "1M", "3M"]


def base_bar(offset, o, h, l, c, v, seq, tf="1s", base=T0, **kw):
    start = base + offset * NS
    return OhlcvBar(
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=101, raw_symbol="ESZ6",
        timeframe=tf, ts_start_ns=start, open=o, high=h, low=l, close=c, volume=v,
        ts_event_ns=start, ts_received_ns=start + 1, sequence=seq, **kw)


def feed(pipeline, aggregator, bar):
    assert pipeline.apply(bar) in ("inserted", "replaced")
    aggregator.on_bar_applied(bar)


def test_every_defined_timeframe_has_a_valid_parent_chain_to_1s():
    for tf in ALL_TIMEFRAMES:
        node, seen = tf, 0
        while PARENT[node] is not None:
            node = PARENT[node]
            seen += 1
            assert seen < 30
        assert node == "1s"
    assert sum(len(v) for v in CHILDREN.values()) == len(ALL_TIMEFRAMES) - 1


def test_all_timeframes_derive_from_sparse_1s_bars_with_correct_ohlcv():
    service, pipeline, *_ = make_service()
    bars = [
        base_bar(1, "100", "102", "99", "101", 5, 1),
        base_bar(2, "101", "105", "100", "104", 7, 2),
        base_bar(4, "104", "104.5", "98", "99", 3, 3),
    ]
    aggregator = Aggregator(pipeline)
    for b in bars:
        feed(pipeline, aggregator, b)
    for tf in ALL_TIMEFRAMES[1:]:
        derived = pipeline.list_bars(timeframe=tf)
        assert len(derived) == 1, tf  # exactly one bucket; none fabricated for empty ones
        d = derived[0]
        assert d.ts_start_ns == bucket_start_ns(T0, tf)
        assert (d.open, d.high, d.low, d.close) == (Decimal(100), Decimal(105), Decimal(98), Decimal(99)), tf
        assert d.volume == Decimal(15), tf
        assert d.origin == "derived"


def test_no_synthetic_candles_for_intervals_without_source_records():
    service, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    feed(pipeline, aggregator, base_bar(0, "100", "101", "99", "100", 1, 1))
    feed(pipeline, aggregator, base_bar(600, "110", "111", "109", "110", 2, 2))  # 10 min gap
    starts = [b.ts_start_ns for b in pipeline.list_bars(timeframe="1m")]
    assert starts == [T0, T0 + 600 * NS]  # nothing for the 9 empty minutes


def test_revision_and_duplicate_never_double_count_volume():
    service, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    feed(pipeline, aggregator, base_bar(0, "100", "101", "99", "100", 10, 1))
    feed(pipeline, aggregator, base_bar(1, "100", "102", "99", "101", 20, 2))
    assert pipeline.apply(base_bar(1, "100", "102", "99", "101", 20, 3)) == "duplicate"
    feed(pipeline, aggregator, base_bar(1, "100", "103", "99", "102", 25, 4))  # real revision
    d = pipeline.list_bars(timeframe="1m")[0]
    assert d.volume == Decimal(35) and d.high == Decimal(103) and d.close == Decimal(102)


def test_out_of_order_arrival_gives_the_same_result_as_ordered_arrival():
    def result(order):
        _, pipeline, *_ = make_service()
        aggregator = Aggregator(pipeline)
        # The local ingest sequence follows ARRIVAL order (monotonic), as in the service.
        for arrival, index in enumerate(order, start=1):
            i = index
            feed(pipeline, aggregator, base_bar(i, str(100 + i), str(102 + i), str(99 + i), str(101 + i), i + 1, arrival))
        d = pipeline.list_bars(timeframe="1m")[0]
        return (d.open, d.high, d.low, d.close, d.volume)
    assert result(range(6)) == result([5, 1, 3, 0, 4, 2])


def test_provider_daily_bar_wins_and_feeds_week_month_quarter():
    _, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    feed(pipeline, aggregator, base_bar(0, "100", "101", "99", "100", 1, 1))  # derives a 1d bar
    daily = pipeline.list_bars(timeframe="1d")[0]
    assert daily.origin == "derived"
    provider_daily = base_bar(0, "100", "150", "90", "140", 9999, 2, tf="1d")
    feed(pipeline, aggregator, provider_daily)
    assert pipeline.list_bars(timeframe="1d")[0].origin == "provider"
    for tf in ("1w", "1M", "3M"):
        d = pipeline.list_bars(timeframe=tf)[0]
        assert (d.high, d.low, d.volume) == (Decimal(150), Decimal(90), Decimal(9999)), tf
    # a later derived recomputation must not overwrite the provider bar
    feed(pipeline, aggregator, base_bar(1, "100", "101", "99", "100", 1, 3))
    assert pipeline.list_bars(timeframe="1d")[0].volume == Decimal(9999)


def test_calendar_buckets_split_on_utc_boundaries():
    _, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    jan31 = T0 + 30 * 86400 * NS  # 2024-01-31 (Wednesday)
    feed(pipeline, aggregator, base_bar(0, "100", "101", "99", "100", 1, 1, base=jan31))
    feed(pipeline, aggregator, base_bar(86400, "101", "102", "100", "101", 2, 2, base=jan31))  # Feb 1
    assert len(pipeline.list_bars(timeframe="1d")) == 2
    assert len(pipeline.list_bars(timeframe="1w")) == 1  # Mon Jan 29 week
    assert len(pipeline.list_bars(timeframe="1M")) == 2
    assert len(pipeline.list_bars(timeframe="3M")) == 1  # Q1


def test_completeness_open_then_partial_or_complete_by_coverage():
    coverage = CoverageTracker()
    pipeline = OhlcvPipeline()
    aggregator = Aggregator(pipeline, coverage)
    scope = ("databento", "GLBX.MDP3", 1, 101, "contract", "ESZ6")
    coverage.add_covered(scope, T0, T0 + 3600 * NS)
    feed(pipeline, aggregator, base_bar(1, "100", "101", "99", "100", 1, 1))
    assert pipeline.list_bars(timeframe="5s")[0].completeness == "open"
    feed(pipeline, aggregator, base_bar(7, "100", "101", "99", "100", 1, 2))
    five = pipeline.list_bars(timeframe="5s")
    assert [b.completeness for b in five] == ["complete", "open"]  # first bucket finalized
    # an uncovered period can never be called complete
    other = Aggregator(OhlcvPipeline(), CoverageTracker())
    feed(other._pipeline, other, base_bar(1, "100", "101", "99", "100", 1, 1))
    feed(other._pipeline, other, base_bar(7, "100", "101", "99", "100", 1, 2))
    assert [b.completeness for b in other._pipeline.list_bars(timeframe="5s")] == ["partial", "open"]


def test_evicted_children_are_not_recomputed_into_a_shrunken_bar():
    pipeline = OhlcvPipeline({"1s": 5})
    aggregator = Aggregator(pipeline)
    for i in range(5):  # one full 5s bucket
        feed(pipeline, aggregator, base_bar(i, "100", "101", "99", "100", 10, i + 1))
    feed(pipeline, aggregator, base_bar(5, "100", "101", "99", "100", 10, 6))  # evicts 1s bar 0
    assert pipeline.stats()["evicted"] == 1
    assert pipeline.list_bars(timeframe="5s")[0].volume == Decimal(50)
    revised = base_bar(1, "100", "101", "99", "100", 99, 7)  # late revision, bucket partly evicted
    assert pipeline.apply(revised) == "replaced"
    aggregator.on_bar_applied(revised)
    assert pipeline.list_bars(timeframe="5s")[0].volume == Decimal(50)  # not shrunk
    assert aggregator.stats["skipped_evicted"] == 1  # and the skip is visible, not silent


def test_retention_below_the_tier_minimum_is_refused():
    import pytest
    with pytest.raises(ValueError):
        OhlcvPipeline({"1d": 5})

def test_derived_bar_durability_gate_runs_before_pipeline_mutation():
    pipeline = OhlcvPipeline()
    seen = []

    def persist_before_apply(derived):
        assert pipeline.list_bars(timeframe=derived.timeframe) == []
        seen.append(derived.timeframe)
        return False

    aggregator = Aggregator(
        pipeline, before_derived_apply=persist_before_apply
    )
    feed(pipeline, aggregator, base_bar(
        0, "100", "101", "99", "100", 1, 1
    ))
    assert seen  # attempted durable writes for derived intervals
    assert pipeline.list_bars(timeframe="1s")
    assert pipeline.list_bars(timeframe="5s") == []
    assert aggregator.stats["persistence_rejected"] == len(seen)
