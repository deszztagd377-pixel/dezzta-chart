from decimal import Decimal

import pytest

from app.ohlcv import (
    InvalidOhlcvBar,
    OhlcvBar,
    OhlcvPipeline,
    bucket_start_ns,
)

NS = 1_000_000_000


def bar(*, start=0, event=100, sequence=1, close="101", volume="12.5", **overrides):
    values = {
        "dataset": "GLBX.MDP3",
        "publisher_id": 1,
        "instrument_id": 123,
        "raw_symbol": "ESZ6",
        "timeframe": "1m",
        "ts_start_ns": start,
        "open": "100",
        "high": "103",
        "low": "99",
        "close": close,
        "volume": volume,
        "ts_event_ns": event,
        "ts_received_ns": event + 10,
        "sequence": sequence,
    }
    values.update(overrides)
    return OhlcvBar(**values)


def test_fixed_interval_bucket_alignment_uses_nanoseconds():
    assert bucket_start_ns(125 * NS, "1m") == 120 * NS
    assert bucket_start_ns(300 * NS, "5m") == 300 * NS


def test_weekly_bucket_starts_on_monday_utc():
    # 2024-01-04 Thursday 12:00 UTC belongs to Monday 2024-01-01.
    thursday = 1_704_365_600 * NS
    monday = 1_704_067_200 * NS
    assert bucket_start_ns(thursday, "1w") == monday


def test_month_and_quarter_buckets_use_calendar_boundaries():
    february_2024 = 1_706_745_600 * NS
    january_2024 = 1_704_067_200 * NS
    february_start = 1_706_745_600_000_000_000
    assert bucket_start_ns(february_2024, "1M") == february_start
    assert bucket_start_ns(february_2024, "3M") == january_2024


@pytest.mark.parametrize(
    "overrides",
    [
        {"volume": "-1"},
        {"high": "98"},
        {"low": "104"},
        {"open": "NaN"},
        {"close": "Infinity"},
        {"timeframe": "2m"},
        {"ts_start_ns": 1},
        {"ts_event_ns": -1},
    ],
)
def test_rejects_invalid_bar(overrides):
    with pytest.raises(InvalidOhlcvBar):
        bar(**overrides)


def test_duplicate_snapshot_replaces_instead_of_summing_volume():
    pipeline = OhlcvPipeline()
    duplicates = pipeline.replace_snapshot([
        bar(event=100, sequence=1, close="100.5", volume="10"),
        bar(event=101, sequence=2, close="101", volume="12"),
    ])

    result = pipeline.list_bars()
    assert duplicates == 1
    assert len(result) == 1
    assert result[0].close == Decimal("101")
    assert result[0].volume == Decimal("12")


def test_upsert_accepts_newer_revision_and_rejects_stale_revision():
    pipeline = OhlcvPipeline()
    assert pipeline.upsert(bar(event=100, sequence=2, close="100.5"))
    assert pipeline.upsert(bar(event=101, sequence=1, close="101"))
    assert not pipeline.upsert(bar(event=100, sequence=99, close="99"))

    result = pipeline.list_bars()
    assert len(result) == 1
    assert result[0].close == Decimal("101")


def test_upsert_uses_sequence_to_order_equal_event_timestamps():
    pipeline = OhlcvPipeline()
    assert pipeline.upsert(bar(event=100, sequence=1, close="100.5"))
    assert pipeline.upsert(bar(event=100, sequence=2, close="101"))
    assert not pipeline.upsert(bar(event=100, sequence=2, close="99"))
    assert pipeline.list_bars()[0].close == Decimal("101")


def test_snapshot_replacement_is_atomic_when_entry_type_is_invalid():
    pipeline = OhlcvPipeline()
    pipeline.upsert(bar())
    with pytest.raises(InvalidOhlcvBar):
        pipeline.replace_snapshot([bar(start=60 * NS), object()])
    assert len(pipeline.list_bars()) == 1
    assert pipeline.list_bars()[0].ts_start_ns == 0


def test_list_filters_and_returns_chronological_copy():
    pipeline = OhlcvPipeline()
    pipeline.upsert(bar(start=60 * NS, event=200))
    pipeline.upsert(bar(start=0, event=100))
    pipeline.upsert(bar(start=0, event=100, instrument_id=456))

    result = pipeline.list_bars(instrument_id=123, timeframe="1m")
    assert [item.ts_start_ns for item in result] == [0, 60 * NS]
    result.clear()
    assert len(pipeline.list_bars()) == 3


def test_clear_only_clears_pipeline_memory():
    pipeline = OhlcvPipeline()
    pipeline.upsert(bar())
    pipeline.clear()
    assert pipeline.list_bars() == []
