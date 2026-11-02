from decimal import Decimal

import pytest

from app.ohlcv import InvalidOhlcvBar, OhlcvBar, OhlcvPipeline, bucket_end_ns, bucket_start_ns, decimal_to_string
from helpers import NS, T0


def bar(offset=0, tf="1s", seq=1, event=None, close="100.5", symbol="ESZ6", iid=101,
        provider="databento", dataset="GLBX.MDP3", origin="provider", volume="10",
        completeness="unknown", **kw):
    start = T0 + offset * NS
    return OhlcvBar(
        dataset=dataset, publisher_id=1, instrument_id=iid, raw_symbol=symbol,
        timeframe=tf, ts_start_ns=start, open="100", high="101", low="99", close=close,
        volume=volume, ts_event_ns=start if event is None else event, ts_received_ns=start + 5,
        sequence=seq, provider=provider, origin=origin, completeness=completeness, **kw)


def test_sequence_is_local_and_labelled_and_defaults_keep_old_constructors_valid():
    b = bar()
    assert b.sequence_origin == "local" and b.ingest_seq == b.sequence
    with pytest.raises(InvalidOhlcvBar):
        bar(sequence_origin="exchange")
    with pytest.raises(InvalidOhlcvBar):
        bar(completeness="done")


def test_identity_separates_provider_and_dataset():
    pipeline = OhlcvPipeline()
    assert pipeline.upsert(bar(provider="databento"))
    assert pipeline.upsert(bar(provider="other"))
    assert pipeline.upsert(bar(dataset="XNAS.ITCH"))
    assert len(pipeline.list_bars()) == 3
    assert len(pipeline.list_bars(provider="other")) == 1
    assert len(pipeline.list_bars(dataset="XNAS.ITCH")) == 1


def test_same_identity_with_different_symbol_is_a_conflict_not_an_overwrite():
    pipeline = OhlcvPipeline()
    pipeline.upsert(bar(symbol="ESZ6"))
    assert pipeline.apply(bar(symbol="ESH7", seq=9)) == "conflict"
    assert pipeline.list_bars()[0].raw_symbol == "ESZ6"
    assert pipeline.stats()["symbol_conflict"] == 1


def test_identical_redelivery_is_a_noop_duplicate():
    pipeline = OhlcvPipeline()
    assert pipeline.apply(bar(seq=1)) == "inserted"
    assert pipeline.apply(bar(seq=2)) == "duplicate"
    assert pipeline.list_bars()[0].sequence == 1
    assert pipeline.apply(bar(seq=3, close="100.7")) == "replaced"


def test_provider_bar_beats_derived_bar_but_not_the_reverse():
    pipeline = OhlcvPipeline()
    assert pipeline.apply(bar(tf="1m", origin="derived", seq=5, close="100.2")) == "inserted"
    assert pipeline.apply(bar(tf="1m", origin="provider", seq=1, close="100.9")) == "replaced"
    assert pipeline.apply(bar(tf="1m", origin="derived", seq=99, close="100.1")) == "provider_precedence"
    assert pipeline.list_bars()[0].close == Decimal("100.9")


def test_retention_is_bounded_counted_and_reports_floor():
    pipeline = OhlcvPipeline({"1s": 5})
    for i in range(7):
        assert pipeline.apply(bar(offset=i, seq=i + 1)) == "inserted"
    kept = [b.ts_start_ns for b in pipeline.list_bars()]
    assert kept == [T0 + k * NS for k in (2, 3, 4, 5, 6)]
    assert pipeline.stats()["evicted"] == 2
    series = pipeline.list_bars()[0].series_key
    assert pipeline.evicted_floor(series) == T0 + 1 * NS
    # A bar older than what retention already discarded is refused, and counted.
    assert pipeline.apply(bar(offset=0, seq=99)) == "expired"
    assert pipeline.stats()["expired"] == 1


def test_query_filters_range_and_returns_newest_limit_chronologically():
    pipeline = OhlcvPipeline()
    for i in range(10):
        pipeline.upsert(bar(offset=i, seq=i + 1))
    bars, total = pipeline.query(limit=3)
    assert total == 10 and [b.ts_start_ns for b in bars] == [T0 + k * NS for k in (7, 8, 9)]
    bars, total = pipeline.query(start_ns=T0 + 2 * NS, end_ns=T0 + 5 * NS)
    assert total == 3 and [b.ts_start_ns for b in bars] == [T0 + k * NS for k in (2, 3, 4)]
    assert pipeline.list_bars(raw_symbol="NOPE") == []
    with pytest.raises(ValueError):
        pipeline.query(limit=0)


def test_replace_snapshot_enforces_retention_and_stays_atomic():
    pipeline = OhlcvPipeline({"1s": 5})
    dup = pipeline.replace_snapshot([bar(offset=i, seq=i + 1) for i in range(7)] + [bar(offset=3, seq=50, close="100.9")])
    assert dup == 1 and len(pipeline.list_bars()) == 5
    assert pipeline.stats()["evicted"] == 2
    with pytest.raises(InvalidOhlcvBar):
        pipeline.replace_snapshot([bar(), object()])
    with pytest.raises(InvalidOhlcvBar):
        pipeline.replace_snapshot([bar(symbol="ESZ6"), bar(symbol="ESH7", seq=99)])
    assert len(pipeline.list_bars()) == 5


def test_bucket_end_covers_calendar_boundaries():
    jan = bucket_start_ns(T0, "1M")
    assert bucket_end_ns(jan, "1M") == bucket_start_ns(T0 + 31 * 86400 * NS, "1M")
    assert bucket_end_ns(jan, "3M") == bucket_start_ns(T0 + 91 * 86400 * NS, "3M")
    assert bucket_end_ns(T0, "1w") == T0 + 7 * 86400 * NS
    with pytest.raises(InvalidOhlcvBar):
        bucket_end_ns(T0 + 1, "1m")


def test_decimal_to_string_never_uses_scientific_notation():
    assert decimal_to_string(Decimal("0.000000001")) == "0.000000001"
    assert decimal_to_string(Decimal("4500.25")) == "4500.25"