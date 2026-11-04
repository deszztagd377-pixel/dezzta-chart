from decimal import Decimal

import pytest

from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_store import SQLiteOhlcvStore


NS = 1_000_000_000


def make_bar(
    *, start=0, event=100, sequence=1, close="101", volume="12.500",
    origin="provider", completeness="unknown", timeframe="1m",
    instrument_id=123, publisher_id=1, raw_symbol="ESZ6",
):
    return OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=publisher_id, instrument_id=instrument_id,
        raw_symbol=raw_symbol, series_type="contract", timeframe=timeframe,
        ts_start_ns=start, open=Decimal("100"), high=Decimal("103"),
        low=Decimal("99"), close=Decimal(close), volume=Decimal(volume),
        ts_event_ns=event, ts_received_ns=event + 10, sequence=sequence,
        sequence_origin="local", origin=origin, completeness=completeness,
    )


def test_exact_decimal_and_nanosecond_values_survive_store_restart(tmp_path):
    path = str(tmp_path / "market.sqlite3")
    store = SQLiteOhlcvStore(path)
    original = make_bar(
        start=60 * NS, event=1_790_000_000_123_456_789,
        close="101.000000000000000001", volume="12.500000000000000009",
    )
    assert store.apply(original) == "inserted"

    restarted = SQLiteOhlcvStore(path)
    restored = restarted.load_bars()
    assert restored == [original]
    assert restored[0].close == Decimal("101.000000000000000001")
    assert restored[0].volume == Decimal("12.500000000000000009")
    assert restored[0].ts_event_ns == 1_790_000_000_123_456_789


def test_duplicate_revision_stale_and_provider_precedence_match_pipeline(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "market.sqlite3"))
    derived = make_bar(origin="derived", completeness="open")
    assert store.apply(derived) == "inserted"
    assert store.apply(derived) == "duplicate"
    assert store.apply(make_bar(event=99, sequence=99, close="99")) == "stale"
    provider = make_bar(event=101, sequence=2, close="102", origin="provider")
    assert store.apply(provider) == "replaced"
    assert store.apply(make_bar(event=102, sequence=3, close="103", origin="derived")) == "provider_precedence"
    assert store.load_bars() == [provider]


def test_derived_completeness_revision_with_equal_order_is_allowed(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "market.sqlite3"))
    open_bar = make_bar(origin="derived", completeness="open")
    complete_bar = make_bar(origin="derived", completeness="complete")
    assert store.apply(open_bar) == "inserted"
    assert store.apply(complete_bar) == "replaced"
    assert store.load_bars() == [complete_bar]


def test_retention_is_per_exact_series_and_prunes_oldest(tmp_path):
    store = SQLiteOhlcvStore(
        str(tmp_path / "market.sqlite3"),
        retention={"1m": 5},
    )
    for i in range(7):
        assert store.apply(make_bar(start=i * 60 * NS, event=100 + i, sequence=i + 1)) in ("inserted", "replaced")
    assert store.apply(make_bar(
        start=0, event=999, sequence=999, instrument_id=456, raw_symbol="NQZ6"
    )) == "inserted"
    rows = store.load_bars()
    es = [bar for bar in rows if bar.instrument_id == 123]
    nq = [bar for bar in rows if bar.instrument_id == 456]
    assert [bar.ts_start_ns for bar in es] == [2 * 60 * NS, 3 * 60 * NS, 4 * 60 * NS, 5 * 60 * NS, 6 * 60 * NS]
    assert len(nq) == 1


def test_query_filters_and_limit_return_chronological_newest_bars(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "market.sqlite3"))
    for i in range(4):
        store.apply(make_bar(start=i * 60 * NS, event=100 + i, sequence=i + 1))
    bars, total = store.query(timeframe="1m", limit=2)
    assert total == 4
    assert [bar.ts_start_ns for bar in bars] == [2 * 60 * NS, 3 * 60 * NS]
    assert store.stats() == {"bars": 4, "series": 1}


def test_store_can_share_registry_database_without_changing_registry_schema_version(tmp_path):
    from app.instrument_registry import SQLiteInstrumentRegistry

    path = str(tmp_path / "shared.sqlite3")
    registry = SQLiteInstrumentRegistry(path)
    store = SQLiteOhlcvStore(path)
    assert registry.list_instruments(active_only=False) == []
    assert store.load_bars() == []
    import sqlite3
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 5


def test_pipeline_can_be_restored_from_persisted_store(tmp_path):
    path = str(tmp_path / "market.sqlite3")
    store = SQLiteOhlcvStore(path)
    expected = [
        make_bar(start=0, event=100, sequence=1),
        make_bar(start=60 * NS, event=101, sequence=2),
    ]
    for bar in expected:
        assert store.apply(bar) == "inserted"
    pipeline = OhlcvPipeline()
    assert pipeline.replace_snapshot(store.load_bars()) == 0
    assert pipeline.list_bars() == expected


def test_local_sequence_high_water_mark_survives_bar_retention_and_restart(tmp_path):
    path = str(tmp_path / "market.sqlite3")
    store = SQLiteOhlcvStore(path, retention={"1m": 5})
    for i in range(7):
        assert store.apply(make_bar(
            start=i * 60 * NS, event=100 + i, sequence=i + 1
        )) == "inserted"
    assert len(store.load_bars()) == 5
    assert store.max_local_sequence() == 7
    restarted = SQLiteOhlcvStore(path, retention={"1m": 5})
    assert restarted.max_local_sequence() == 7


def test_late_bar_older_than_persisted_retention_window_is_expired(tmp_path):
    store = SQLiteOhlcvStore(
        str(tmp_path / "market.sqlite3"), retention={"1m": 5}
    )
    for i in range(5):
        assert store.apply(make_bar(
            start=(i + 1) * 60 * NS, event=100 + i, sequence=i + 1
        )) == "inserted"
    assert store.apply(make_bar(
        start=60 * NS, event=999, sequence=999, close="102"
    )) == "replaced"  # existing identity can still receive a valid revision
    assert store.apply(make_bar(
        start=0, event=1_000, sequence=1_000, close="102"
    )) == "expired"
    assert len(store.load_bars()) == 5
