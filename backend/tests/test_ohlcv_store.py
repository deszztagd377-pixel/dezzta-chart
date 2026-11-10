from decimal import Decimal

import pytest

from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_store import SQLiteOhlcvStore


NS = 1_000_000_000


def make_bar(
    *, start=0, event=100, sequence=1, close="101", volume="12.500",
    origin="provider", completeness="unknown", timeframe="1m",
    instrument_id=123, publisher_id=1, raw_symbol="ESZ6",
    bucket_policy="UTC_LEGACY",
):
    return OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=publisher_id, instrument_id=instrument_id,
        raw_symbol=raw_symbol, series_type="contract", timeframe=timeframe,
        ts_start_ns=start, open=Decimal("100"), high=Decimal("103"),
        low=Decimal("99"), close=Decimal(close), volume=Decimal(volume),
        ts_event_ns=event, ts_received_ns=event + 10, sequence=sequence,
        sequence_origin="local", origin=origin, completeness=completeness,
        bucket_policy=bucket_policy,
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
    assert store.apply(make_bar(event=99, sequence=99, close="99", origin="derived")) == "stale"
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


def test_legacy_schema_migrates_and_preserves_exact_rows(tmp_path):
    import sqlite3

    path = str(tmp_path / "legacy.sqlite3")
    original = make_bar(
        start=60 * NS, event=1_790_000_000_123_456_789,
        close="101.000000000000000001", volume="12.500000000000000009",
    )
    with sqlite3.connect(path) as db:
        db.execute(
            """CREATE TABLE ohlcv_bars (
                provider TEXT NOT NULL, dataset TEXT NOT NULL,
                publisher_id INTEGER NOT NULL, instrument_id INTEGER NOT NULL,
                series_type TEXT NOT NULL, timeframe TEXT NOT NULL,
                ts_start_ns INTEGER NOT NULL, raw_symbol TEXT NOT NULL,
                open TEXT NOT NULL, high TEXT NOT NULL, low TEXT NOT NULL,
                close TEXT NOT NULL, volume TEXT NOT NULL, ts_event_ns INTEGER NOT NULL,
                ts_received_ns INTEGER NOT NULL, sequence INTEGER NOT NULL,
                sequence_origin TEXT NOT NULL, origin TEXT NOT NULL,
                completeness TEXT NOT NULL, ts_provider_out_ns INTEGER,
                PRIMARY KEY(provider,dataset,publisher_id,instrument_id,
                    series_type,timeframe,ts_start_ns)
            )"""
        )
        db.execute(
            "INSERT INTO ohlcv_bars VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                original.provider, original.dataset, original.publisher_id,
                original.instrument_id, original.series_type, original.timeframe,
                original.ts_start_ns, original.raw_symbol, str(original.open),
                str(original.high), str(original.low), str(original.close),
                str(original.volume), original.ts_event_ns, original.ts_received_ns,
                original.sequence, original.sequence_origin, original.origin,
                original.completeness, original.ts_provider_out_ns,
            ),
        )
        db.execute(
            """CREATE INDEX idx_ohlcv_series_time ON ohlcv_bars(
                provider,dataset,publisher_id,instrument_id,series_type,
                raw_symbol,timeframe,ts_start_ns
            )"""
        )
        db.execute(
            """CREATE TABLE ohlcv_store_state (
                state_key TEXT PRIMARY KEY NOT NULL, int_value INTEGER NOT NULL
            )"""
        )
        db.execute("PRAGMA user_version = 5")

    migrated = SQLiteOhlcvStore(path)
    assert migrated.load_bars() == [original]
    with sqlite3.connect(path) as db:
        db.row_factory = sqlite3.Row
        policy_row = db.execute(
            "SELECT bucket_policy,calendar_id,calendar_version FROM ohlcv_bars"
        ).fetchone()
        assert tuple(policy_row) == ("UTC_LEGACY", "", "")
        meta = db.execute(
            "SELECT schema_version FROM ohlcv_schema_meta WHERE schema_key='ohlcv'"
        ).fetchone()
        assert meta["schema_version"] == 3
        primary_key_columns = [
            row["name"] for row in db.execute("PRAGMA table_info(ohlcv_bars)")
            if row["pk"]
        ]
        assert primary_key_columns[-3:] == [
            "bucket_policy", "calendar_id", "calendar_version"
        ]
        db.execute(
            """INSERT INTO ohlcv_bars (
                provider,dataset,publisher_id,instrument_id,series_type,timeframe,
                ts_start_ns,raw_symbol,open,high,low,close,volume,ts_event_ns,
                ts_received_ns,sequence,sequence_origin,origin,completeness,
                ts_provider_out_ns,bucket_policy,calendar_id,calendar_version
            )
            SELECT provider,dataset,publisher_id,instrument_id,series_type,timeframe,
                ts_start_ns,raw_symbol,open,high,low,close,volume,ts_event_ns,
                ts_received_ns,sequence,sequence_origin,origin,completeness,
                ts_provider_out_ns,'CME_SESSION_V1','CME_EQUITY_INDEX','2026-test'
            FROM ohlcv_bars WHERE bucket_policy='UTC_LEGACY'"""
        )
        assert db.execute("SELECT COUNT(*) FROM ohlcv_bars").fetchone()[0] == 2
        assert db.execute("PRAGMA user_version").fetchone()[0] == 5

    # The legacy model must not silently merge a future policy row into UTC data.
    assert migrated.load_bars() == [original]
    visible, total = migrated.query(timeframe="1m")
    assert visible == [original]
    assert total == 1

    SQLiteOhlcvStore(path)
    with sqlite3.connect(path) as db:
        assert db.execute(
            "SELECT schema_version FROM ohlcv_schema_meta WHERE schema_key='ohlcv'"
        ).fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM ohlcv_bars").fetchone()[0] == 2


def test_unknown_future_ohlcv_schema_version_is_rejected_without_rewriting(tmp_path):
    import sqlite3

    path = str(tmp_path / "future.sqlite3")
    SQLiteOhlcvStore(path)
    with sqlite3.connect(path) as db:
        db.execute(
            "UPDATE ohlcv_schema_meta SET schema_version=999 WHERE schema_key='ohlcv'"
        )
    with pytest.raises(RuntimeError, match="newer than supported"):
        SQLiteOhlcvStore(path)
    with sqlite3.connect(path) as db:
        assert db.execute(
            "SELECT schema_version FROM ohlcv_schema_meta WHERE schema_key='ohlcv'"
        ).fetchone()[0] == 999


def test_bucket_policy_is_persisted_and_never_overwrites_other_policy(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "policy.sqlite3"))
    legacy = make_bar(start=0, bucket_policy="UTC_LEGACY")
    fixed = make_bar(start=0, bucket_policy="UTC_FIXED_V1")
    assert store.apply(legacy) == "inserted"
    assert store.apply(fixed) == "inserted"
    assert store.load_bars() == [legacy, fixed]
    legacy_rows, legacy_total = store.query(bucket_policy="UTC_LEGACY")
    fixed_rows, fixed_total = store.query(bucket_policy="UTC_FIXED_V1")
    assert legacy_rows == [legacy] and legacy_total == 1
    assert fixed_rows == [fixed] and fixed_total == 1

def test_concurrent_connections_preserve_all_ohlcv_writes(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    path = str(tmp_path / "concurrent-market.sqlite3")
    store = SQLiteOhlcvStore(path, busy_timeout_ms=10_000)
    workers = 8
    writes_per_worker = 25

    def write_partition(worker):
        results = []
        for offset in range(writes_per_worker):
            index = worker * writes_per_worker + offset
            bar = make_bar(
                start=index * 60 * NS,
                event=10_000 + index,
                sequence=index + 1,
            )
            results.append(store.apply(bar))
        return results

    with ThreadPoolExecutor(max_workers=workers) as executor:
        partitions = list(executor.map(write_partition, range(workers)))

    assert all(result == "inserted" for partition in partitions for result in partition)
    rows, total = store.query(timeframe="1m")
    assert total == workers * writes_per_worker
    assert len(rows) == workers * writes_per_worker
    assert [bar.ts_start_ns for bar in rows] == [
        index * 60 * NS for index in range(workers * writes_per_worker)
    ]


def _replay_args(**overrides):
    values = {
        "provider": "databento",
        "dataset": "GLBX.MDP3",
        "publisher_id": 1,
        "instrument_id": 123,
        "series_type": "contract",
        "raw_symbol": "ESZ6",
        "timeframe": "1m",
        "bucket_policy": "UTC_LEGACY",
        "calendar_id": "",
        "calendar_version": "",
    }
    values.update(overrides)
    return values


def test_outbox_commits_atomically_with_bar_and_replays_exact_decimal_payload(tmp_path):
    path = str(tmp_path / "outbox.sqlite3")
    store = SQLiteOhlcvStore(path)
    bar = make_bar(
        start=60 * NS, event=1_790_000_000_123_456_789,
        close="101.000000000000000001",
        volume="12.500000000000000009",
    )
    assert store.apply(bar) == "inserted"
    assert store.outbox_high_water() == 1

    restarted = SQLiteOhlcvStore(path)
    replay = restarted.replay_outbox(after_cursor=0, **_replay_args())
    assert replay["status"] == "ok"
    assert replay["next_cursor"] == 1
    assert replay["high_water"] == 1
    assert len(replay["events"]) == 1
    event = replay["events"][0]
    assert event["cursor"] == 1
    assert event["eventId"]
    assert event["bar"]["close"] == "101.000000000000000001"
    assert event["bar"]["volume"] == "12.500000000000000009"
    assert event["bar"]["tsEventNs"] == "1790000000123456789"


def test_duplicate_stale_and_rejected_revisions_do_not_add_outbox_events(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-dedupe.sqlite3"))
    first = make_bar(event=100, sequence=1)
    assert store.apply(first) == "inserted"
    assert store.apply(first) == "duplicate"
    assert store.apply(make_bar(event=99, sequence=99, close="99")) == "stale"
    assert store.apply(make_bar(event=101, sequence=2, close="102", origin="derived")) == "provider_precedence"
    assert store.outbox_high_water() == 1


def test_outbox_failure_rolls_back_the_corresponding_bar_revision(tmp_path):
    import sqlite3

    path = str(tmp_path / "outbox-rollback.sqlite3")
    store = SQLiteOhlcvStore(path)
    with sqlite3.connect(path) as db:
        db.execute(
            """CREATE TRIGGER reject_outbox_insert BEFORE INSERT ON ohlcv_outbox
            BEGIN SELECT RAISE(ABORT, 'outbox unavailable'); END"""
        )
    with pytest.raises(sqlite3.IntegrityError, match="outbox unavailable"):
        store.apply(make_bar())
    assert store.load_bars() == []
    assert store.outbox_high_water() == 0


def test_outbox_cursor_expiry_and_bounded_retention_force_resnapshot(tmp_path, monkeypatch):
    import app.ohlcv_store as store_module

    monkeypatch.setattr(store_module, "OUTBOX_MAX_EVENTS", 2)
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-retention.sqlite3"))
    for index in range(3):
        assert store.apply(make_bar(
            start=index * 60 * NS, event=100 + index, sequence=index + 1,
            close=str(101 + index),
        )) == "inserted"

    expired = store.replay_outbox(after_cursor=0, **_replay_args())
    assert expired["status"] == "resnapshot_required"
    assert expired["reason"] == "cursor_expired"
    assert expired["retention_floor"] == 1
    replay = store.replay_outbox(after_cursor=1, **_replay_args())
    assert replay["status"] == "ok"
    assert [event["cursor"] for event in replay["events"]] == [2, 3]
    ahead = store.replay_outbox(after_cursor=4, **_replay_args())
    assert ahead["status"] == "resnapshot_required"
    assert ahead["reason"] == "cursor_ahead"


def test_outbox_replay_isolated_by_complete_series_identity(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-series.sqlite3"))
    assert store.apply(make_bar()) == "inserted"
    other = make_bar(
        start=60 * NS, event=101, sequence=2, instrument_id=456,
        raw_symbol="NQZ6",
    )
    assert store.apply(other) == "inserted"
    es = store.replay_outbox(after_cursor=0, **_replay_args())
    nq = store.replay_outbox(after_cursor=0, **_replay_args(
        instrument_id=456, raw_symbol="NQZ6",
    ))
    assert len(es["events"]) == 1
    assert es["events"][0]["bar"]["rawSymbol"] == "ESZ6"
    assert len(nq["events"]) == 1
    assert nq["events"][0]["bar"]["rawSymbol"] == "NQZ6"
    assert es["next_cursor"] == nq["next_cursor"] == 2


def test_outbox_event_lookup_resolves_exact_source_and_derived_series_revision(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-exact-event.sqlite3"))
    source = make_bar(start=0, event=100, sequence=1, timeframe="1s")
    derived = make_bar(
        start=0, event=100, sequence=1, timeframe="1m",
        origin="derived", completeness="open",
    )
    assert store.apply(source) == "inserted"
    source_event = store.outbox_event_for_bar(source)
    assert source_event is not None
    assert source_event["cursor"] == 1

    assert store.apply(derived) == "inserted"
    derived_event = store.outbox_event_for_bar(derived)
    assert derived_event is not None
    assert derived_event["cursor"] == 2
    assert derived_event["eventId"] != source_event["eventId"]

    assert store.outbox_event_for_bar(
        make_bar(start=0, event=100, sequence=1, timeframe="1s", close="102")
    ) is None
