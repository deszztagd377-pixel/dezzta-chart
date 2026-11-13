from decimal import Decimal
from datetime import date, datetime, timezone

from app.aggregation import CHILDREN, PARENT, Aggregator
from app.coverage import CoverageTracker
from app.ohlcv import FIXED_INTERVAL_SECONDS, OhlcvBar, OhlcvPipeline, bucket_start_ns
from helpers import NS, T0, make_service, rec
from app.session_bar_validation import SessionBarValidation
from app.session_calendar import (
    CHICAGO, SessionCalendar, SessionCalendarRegistry, SessionRecord,
    datetime_to_epoch_ns,
)

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


def test_cme_session_bars_remain_unaggregated_until_calendar_bounds_are_resolved():
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1

    _, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    session_open = 1_730_668_800 * NS  # deliberately not a UTC-midnight boundary
    daily = base_bar(
        0, "100", "101", "99", "100", 5, 1,
        tf="1d", base=session_open,
        bucket_policy=BUCKET_POLICY_CME_SESSION_V1,
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2026.11.1",
    )
    feed(pipeline, aggregator, daily)

    assert pipeline.list_bars(timeframe="1d", bucket_policy=BUCKET_POLICY_CME_SESSION_V1) == [daily]
    assert pipeline.list_bars(timeframe="1w", bucket_policy=BUCKET_POLICY_CME_SESSION_V1) == []
    assert pipeline.list_bars(timeframe="1M", bucket_policy=BUCKET_POLICY_CME_SESSION_V1) == []
    assert aggregator.stats["skipped_cme_calendar_unresolved"] == 1


def test_derived_intraday_bars_inherit_fixed_utc_policy_and_stop_before_daily():
    _, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    child = base_bar(0, "100", "101", "99", "100", 2, 1,
                     bucket_policy="UTC_FIXED_V1")
    feed(pipeline, aggregator, child)
    five = pipeline.list_bars(timeframe="5s", bucket_policy="UTC_FIXED_V1")
    assert len(five) == 1
    assert five[0].bucket_policy == "UTC_FIXED_V1"
    assert pipeline.list_bars(timeframe="1d", bucket_policy="UTC_FIXED_V1") == []

def test_utc_fixed_one_second_input_keeps_every_intraday_timeframe_available():
    """The UTC-fixed intraday chain remains usable without a paid provider."""
    _, pipeline, *_ = make_service()
    aggregator = Aggregator(pipeline)
    first = base_bar(
        0, "100", "101", "99", "100", 1, 1,
        bucket_policy="UTC_FIXED_V1",
    )

    feed(pipeline, aggregator, first)

    intraday_timeframes = [
        tf for tf in FIXED_INTERVAL_SECONDS if tf not in {"1s", "1d"}
    ]
    for timeframe in intraday_timeframes:
        bars = pipeline.list_bars(
            timeframe=timeframe, bucket_policy="UTC_FIXED_V1"
        )
        assert len(bars) == 1, timeframe
        assert bars[0].ts_start_ns == bucket_start_ns(T0, timeframe)
        assert bars[0].origin == "derived"
    # Session-dependent higher periods must not be invented from UTC buckets.
    for timeframe in ("1d", "1w", "1M", "3M"):
        assert pipeline.list_bars(
            timeframe=timeframe, bucket_policy="UTC_FIXED_V1"
        ) == []


def test_cme_session_calendar_derives_week_month_and_quarter_buckets():
    from datetime import date, datetime, timedelta, timezone
    from app.session_calendar import CHICAGO, SessionCalendar, SessionCalendarRegistry, SessionRecord, datetime_to_epoch_ns
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1

    records = []
    day = date(2024, 1, 1)
    while day <= date(2024, 3, 31):
        if day.weekday() < 5:
            opened = datetime.combine(day - timedelta(days=1), datetime.min.time()).replace(hour=17, tzinfo=CHICAGO)
            closed = datetime.combine(day, datetime.min.time()).replace(hour=16, tzinfo=CHICAGO)
            records.append(SessionRecord(day, "regular", opened, closed))
        else:
            records.append(SessionRecord(day, "closed", None, None))
        day += timedelta(days=1)
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX", version="2024.Q1.test", product_family="ES",
        effective_start=date(2024, 1, 1), effective_end=date(2024, 3, 31),
        source_id="test-fixture", source_url="https://example.invalid/fixture",
        published_at_utc=datetime(2023, 12, 1, tzinfo=timezone.utc),
        checksum="sha256:" + "a" * 64, records={record.trading_date: record for record in records},
    )
    registry = SessionCalendarRegistry((calendar,))
    pipeline = OhlcvPipeline()
    aggregator = Aggregator(pipeline, session_calendars=registry)
    for trading_day, price in ((date(2024, 1, 2), "100"), (date(2024, 1, 3), "101"),
                               (date(2024, 2, 2), "102"), (date(2024, 3, 4), "103")):
        record = calendar.records[trading_day]
        start = datetime_to_epoch_ns(record.open_local)
        bar = OhlcvBar(
            dataset="GLBX.MDP3", publisher_id=1, instrument_id=101, raw_symbol="ESZ6",
            timeframe="1d", ts_start_ns=start, open=price, high=str(int(price)+1),
            low=str(int(price)-1), close=price, volume=10, ts_event_ns=start,
            ts_received_ns=start+1, sequence=len(pipeline.list_bars(timeframe="1d"))+1,
            bucket_policy=BUCKET_POLICY_CME_SESSION_V1,
            calendar_id="CME_EQUITY_INDEX", calendar_version="2024.Q1.test",
        )
        assert pipeline.apply(bar) == "inserted"
        aggregator.on_bar_applied(bar)
    weekly = pipeline.list_bars(timeframe="1w", bucket_policy=BUCKET_POLICY_CME_SESSION_V1)
    monthly = pipeline.list_bars(timeframe="1M", bucket_policy=BUCKET_POLICY_CME_SESSION_V1)
    quarterly = pipeline.list_bars(timeframe="3M", bucket_policy=BUCKET_POLICY_CME_SESSION_V1)
    assert len(weekly) == 3
    assert len(monthly) == 3
    assert len(quarterly) == 1
    assert quarterly[0].calendar_id == "CME_EQUITY_INDEX"
    assert quarterly[0].calendar_version == "2024.Q1.test"
    assert quarterly[0].volume == 40
    assert quarterly[0].completeness == "partial"
    assert aggregator.stats["skipped_cme_calendar_unresolved"] == 0



def test_validated_cme_one_minute_bars_derive_session_daily_with_pinned_identity():
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1

    trading_date = date(2024, 3, 11)
    opened = datetime(2024, 3, 10, 17, 0, tzinfo=CHICAGO)
    closed = datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO)
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.1",
        product_family="ES",
        effective_start=trading_date,
        effective_end=trading_date,
        source_id="test-fixture-only",
        source_url="https://example.invalid/test-calendar",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:" + "b" * 64,
        records={
            trading_date: SessionRecord(
                trading_date, "regular", opened, closed
            )
        },
    )
    registry = SessionCalendarRegistry((calendar,))
    pipeline = OhlcvPipeline()
    aggregator = Aggregator(pipeline, session_calendars=registry)
    session_start = datetime_to_epoch_ns(opened)

    source_bars = [
        base_bar(
            0, "100", "102", "99", "101", 10, 1,
            tf="1m", base=session_start, bucket_policy="UTC_FIXED_V1",
        ),
        base_bar(
            60, "101", "103", "100", "102", 20, 2,
            tf="1m", base=session_start, bucket_policy="UTC_FIXED_V1",
        ),
    ]
    for source in source_bars:
        assert pipeline.apply(source) == "inserted"
        validation = SessionBarValidation(
            calendar_id="CME_EQUITY_INDEX",
            calendar_version="2024.03.1",
            trading_date=trading_date.isoformat(),
            session_state="open",
            interval_start_ns=source.ts_start_ns,
            interval_end_ns=source.ts_start_ns + 60 * NS,
        )
        aggregator.on_bar_applied(source, session_validation=validation)

    daily = pipeline.list_bars(
        timeframe="1d",
        bucket_policy=BUCKET_POLICY_CME_SESSION_V1,
    )
    assert len(daily) == 1
    assert daily[0].ts_start_ns == session_start
    assert (daily[0].open, daily[0].high, daily[0].low, daily[0].close) == (
        Decimal("100"), Decimal("103"), Decimal("99"), Decimal("102")
    )
    assert daily[0].volume == Decimal("30")
    assert daily[0].calendar_id == "CME_EQUITY_INDEX"
    assert daily[0].calendar_version == "2024.03.1"
    assert daily[0].completeness == "partial"
    assert pipeline.list_bars(
        timeframe="1d", bucket_policy="UTC_FIXED_V1"
    ) == []


def test_validated_cme_one_second_bars_derive_daily_through_the_minute_chain():
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1

    trading_date = date(2024, 3, 11)
    opened = datetime(2024, 3, 10, 17, 0, tzinfo=CHICAGO)
    closed = datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO)
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.1",
        product_family="ES",
        effective_start=trading_date,
        effective_end=trading_date,
        source_id="test-fixture-only",
        source_url="https://example.invalid/test-calendar",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:" + "d" * 64,
        records={trading_date: SessionRecord(trading_date, "regular", opened, closed)},
    )
    pipeline = OhlcvPipeline()
    aggregator = Aggregator(
        pipeline, session_calendars=SessionCalendarRegistry((calendar,))
    )
    session_start = datetime_to_epoch_ns(opened)
    source = base_bar(
        0, "100", "102", "99", "101", 10, 1,
        tf="1s", base=session_start, bucket_policy="UTC_FIXED_V1",
    )
    assert pipeline.apply(source) == "inserted"
    validation = SessionBarValidation(
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2024.03.1",
        trading_date=trading_date.isoformat(),
        session_state="open",
        interval_start_ns=source.ts_start_ns,
        interval_end_ns=source.ts_start_ns + NS,
    )

    aggregator.on_bar_applied(source, session_validation=validation)

    minute = pipeline.list_bars(timeframe="1m", bucket_policy="UTC_FIXED_V1")
    daily = pipeline.list_bars(
        timeframe="1d", bucket_policy=BUCKET_POLICY_CME_SESSION_V1
    )
    assert len(minute) == 1
    assert minute[0].origin == "derived"
    assert len(daily) == 1
    assert daily[0].ts_start_ns == session_start
    assert (daily[0].open, daily[0].high, daily[0].low, daily[0].close) == (
        Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101")
    )
    assert daily[0].volume == Decimal("10")
    assert daily[0].calendar_id == "CME_EQUITY_INDEX"
    assert daily[0].calendar_version == "2024.03.1"


def test_cme_daily_aggregation_rejects_derived_minute_crossing_segment_end():
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1
    from app.session_calendar import SessionSegment

    trading_date = date(2024, 3, 11)
    opened = datetime(2024, 3, 10, 17, 0, tzinfo=CHICAGO)
    segment_end = datetime(2024, 3, 10, 17, 0, 30, tzinfo=CHICAGO)
    next_segment = datetime(2024, 3, 10, 17, 1, tzinfo=CHICAGO)
    closed = datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO)
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.segment-test",
        product_family="ES",
        effective_start=trading_date,
        effective_end=trading_date,
        source_id="test-fixture-only",
        source_url="https://example.invalid/test-calendar",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:" + "e" * 64,
        records={
            trading_date: SessionRecord(
                trading_date, "regular", opened, closed,
                segments=(
                    SessionSegment(opened, segment_end),
                    SessionSegment(next_segment, closed),
                ),
            )
        },
    )
    pipeline = OhlcvPipeline()
    aggregator = Aggregator(
        pipeline, session_calendars=SessionCalendarRegistry((calendar,))
    )
    source = base_bar(
        0, "100", "102", "99", "101", 10, 1,
        tf="1s", base=datetime_to_epoch_ns(opened),
        bucket_policy="UTC_FIXED_V1",
    )
    assert pipeline.apply(source) == "inserted"
    validation = SessionBarValidation(
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2024.03.segment-test",
        trading_date=trading_date.isoformat(),
        session_state="open",
        interval_start_ns=source.ts_start_ns,
        interval_end_ns=source.ts_start_ns + NS,
    )

    aggregator.on_bar_applied(source, session_validation=validation)

    assert pipeline.list_bars(
        timeframe="1d", bucket_policy=BUCKET_POLICY_CME_SESSION_V1
    ) == []


def test_cme_daily_aggregation_rejects_children_crossing_session_segment():
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1
    from app.session_calendar import SessionSegment

    trading_date = date(2024, 3, 11)
    first_start = datetime(2024, 3, 10, 17, 0, tzinfo=CHICAGO)
    first_end = datetime(2024, 3, 10, 17, 0, 30, tzinfo=CHICAGO)
    second_start = datetime(2024, 3, 10, 17, 1, tzinfo=CHICAGO)
    close = datetime(2024, 3, 11, 16, 0, tzinfo=CHICAGO)
    calendar = SessionCalendar(
        calendar_id="CME_EQUITY_INDEX",
        version="2024.03.segment-test",
        product_family="ES",
        effective_start=trading_date,
        effective_end=trading_date,
        source_id="test-fixture-only",
        source_url="https://example.invalid/test-calendar",
        published_at_utc=datetime(2024, 2, 1, tzinfo=timezone.utc),
        checksum="sha256:" + "c" * 64,
        records={
            trading_date: SessionRecord(
                trading_date, "regular", first_start, close,
                segments=(
                    SessionSegment(first_start, first_end),
                    SessionSegment(second_start, close),
                ),
            )
        },
    )
    pipeline = OhlcvPipeline()
    aggregator = Aggregator(
        pipeline, session_calendars=SessionCalendarRegistry((calendar,))
    )
    session_start = datetime_to_epoch_ns(first_start)
    invalid_child = base_bar(
        0, "100", "102", "99", "101", 10, 1,
        tf="1m", base=session_start, bucket_policy="UTC_FIXED_V1",
    )
    valid_current = base_bar(
        60, "101", "103", "100", "102", 20, 2,
        tf="1m", base=session_start, bucket_policy="UTC_FIXED_V1",
    )
    assert pipeline.apply(invalid_child) == "inserted"
    assert pipeline.apply(valid_current) == "inserted"
    validation = SessionBarValidation(
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2024.03.segment-test",
        trading_date=trading_date.isoformat(),
        session_state="open",
        interval_start_ns=valid_current.ts_start_ns,
        interval_end_ns=valid_current.ts_start_ns + 60 * NS,
    )
    aggregator.on_bar_applied(valid_current, session_validation=validation)
    assert pipeline.list_bars(
        timeframe="1d", bucket_policy=BUCKET_POLICY_CME_SESSION_V1
    ) == []
    assert aggregator.stats["rejected_cme_daily_child"] == 1
