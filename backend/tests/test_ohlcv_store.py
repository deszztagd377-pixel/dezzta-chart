from decimal import Decimal

import pytest

from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_store import SQLiteOhlcvStore, SQLiteOhlcvReplicaStore


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



def test_cme_session_bars_restore_with_calendar_identity(tmp_path):
    from dataclasses import replace
    from app.ohlcv import BUCKET_POLICY_CME_SESSION_V1

    path = str(tmp_path / "cme-restore.sqlite3")
    store = SQLiteOhlcvStore(path)
    daily = replace(
        make_bar(timeframe="1d"),
        bucket_policy=BUCKET_POLICY_CME_SESSION_V1,
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2026.11.1",
    )
    assert store.apply(daily) == "inserted"

    restored = SQLiteOhlcvStore(path).load_bars()
    assert restored == [daily]
    assert restored[0].calendar_id == "CME_EQUITY_INDEX"
    assert restored[0].calendar_version == "2026.11.1"

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




def test_query_snapshot_returns_bars_and_outbox_watermark_from_same_committed_state(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "snapshot-watermark.sqlite3"))
    first = make_bar(start=0, event=100, sequence=1)
    second = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
    )
    assert store.apply(first) == "inserted"
    snapshot_one = store.query_snapshot(
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        provider="databento", raw_symbol="ESZ6", timeframe="1m",
        series_type="contract", bucket_policy="UTC_LEGACY", limit=1,
    )
    assert snapshot_one["cursor"] == snapshot_one["high_water"] == 1
    assert snapshot_one["total"] == 1
    assert [bar.close for bar in snapshot_one["bars"]] == [Decimal("101")]

    assert store.apply(second) == "inserted"
    snapshot_two = store.query_snapshot(
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        provider="databento", raw_symbol="ESZ6", timeframe="1m",
        series_type="contract", bucket_policy="UTC_LEGACY",
    )
    assert snapshot_two["cursor"] == snapshot_two["high_water"] == 2
    assert snapshot_two["total"] == 2
    assert [bar.close for bar in snapshot_two["bars"]] == [
        Decimal("101"), Decimal("102"),
    ]




def test_query_snapshot_keeps_bars_and_watermark_consistent_during_concurrent_write(
    tmp_path, monkeypatch,
):
    import sqlite3
    import threading

    path = str(tmp_path / "snapshot-concurrent.sqlite3")
    store = SQLiteOhlcvStore(path)
    first = make_bar(start=0, event=100, sequence=1)
    second = make_bar(start=60 * NS, event=101, sequence=2, close="102")
    assert store.apply(first) == "inserted"

    state_read = threading.Event()
    continue_snapshot = threading.Event()
    original_connect = sqlite3.connect
    outcome = {}

    class PausingConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            result = super().execute(sql, parameters)
            if (
                threading.current_thread().name == "snapshot-reader"
                and sql.startswith("SELECT state_key,int_value FROM ohlcv_outbox_state")
            ):
                state_read.set()
                if not continue_snapshot.wait(timeout=5):
                    raise TimeoutError("snapshot test read barrier timed out")
            return result

    def connect_with_pausing_factory(*args, **kwargs):
        kwargs["factory"] = PausingConnection
        return original_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_with_pausing_factory)

    def read_snapshot():
        try:
            outcome["snapshot"] = store.query_snapshot(
                dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
                provider="databento", raw_symbol="ESZ6", timeframe="1m",
                series_type="contract", bucket_policy="UTC_LEGACY",
            )
        except Exception as exc:
            outcome["error"] = exc

    reader = threading.Thread(target=read_snapshot, name="snapshot-reader")
    reader.start()
    try:
        assert state_read.wait(timeout=5), "snapshot reader did not establish its read view"
        assert store.apply(second) == "inserted"
    finally:
        continue_snapshot.set()
        reader.join(timeout=5)

    assert not reader.is_alive()
    assert "error" not in outcome
    snapshot = outcome["snapshot"]
    assert snapshot["cursor"] == snapshot["high_water"] == 1
    assert snapshot["total"] == 1
    assert [bar.close for bar in snapshot["bars"]] == [Decimal("101")]
    latest = store.query_snapshot(
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        provider="databento", raw_symbol="ESZ6", timeframe="1m",
        series_type="contract", bucket_policy="UTC_LEGACY",
    )
    assert latest["cursor"] == latest["high_water"] == 2
    assert latest["total"] == 2

def test_query_snapshot_validates_limit_before_reading(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "snapshot-limit.sqlite3"))
    with pytest.raises(ValueError, match="limit"):
        store.query_snapshot(limit=True)
    with pytest.raises(ValueError, match="limit"):
        store.query_snapshot(limit=0)

def test_global_outbox_batch_pages_all_series_in_cursor_order(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-global.sqlite3"))
    first = make_bar(start=0, event=100, sequence=1)
    second = make_bar(start=60 * NS, event=101, sequence=2, instrument_id=456, raw_symbol="NQZ6")
    third = make_bar(start=120 * NS, event=102, sequence=3)
    assert store.apply(first) == "inserted"
    assert store.apply(second) == "inserted"
    assert store.apply(third) == "inserted"

    page_one = store.read_outbox_batch(after_cursor=0, limit=2)
    assert page_one["status"] == "ok"
    assert [event["cursor"] for event in page_one["events"]] == [1, 2]
    assert [event["bar"]["rawSymbol"] for event in page_one["events"]] == ["ESZ6", "NQZ6"]
    assert page_one["has_more"] is True
    assert page_one["next_cursor"] == 2

    page_two = store.read_outbox_batch(after_cursor=page_one["next_cursor"], limit=2)
    assert page_two["status"] == "ok"
    assert [event["cursor"] for event in page_two["events"]] == [3]
    assert page_two["events"][0]["eventId"]
    assert page_two["has_more"] is False
    assert page_two["next_cursor"] == page_two["high_water"] == 3


def test_global_outbox_batch_rejects_expired_and_ahead_cursors(tmp_path, monkeypatch):
    import app.ohlcv_store as store_module

    monkeypatch.setattr(store_module, "OUTBOX_MAX_EVENTS", 2)
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-global-retention.sqlite3"))
    for index in range(3):
        assert store.apply(make_bar(start=index * 60 * NS, event=100 + index, sequence=index + 1)) == "inserted"

    expired = store.read_outbox_batch(after_cursor=0)
    assert expired["status"] == "resnapshot_required"
    assert expired["reason"] == "cursor_expired"
    assert expired["retention_floor"] == 1
    ahead = store.read_outbox_batch(after_cursor=4)
    assert ahead["status"] == "resnapshot_required"
    assert ahead["reason"] == "cursor_ahead"


def test_global_outbox_batch_requires_resnapshot_on_missing_cursor(tmp_path):
    import sqlite3

    cases = (
        ("middle-page", 2, 3),
        ("page-lookahead", 2, 1),
        ("tail", 4, 3),
    )
    for name, missing_cursor, page_size in cases:
        path = str(tmp_path / f"outbox-gap-{name}.sqlite3")
        store = SQLiteOhlcvStore(path)
        for index in range(4):
            assert store.apply(make_bar(
                start=index * 60 * NS, event=100 + index, sequence=index + 1,
            )) == "inserted"

        # Simulate an integrity defect without changing the durable high-water.
        with sqlite3.connect(path) as db:
            db.execute("DELETE FROM ohlcv_outbox WHERE cursor=?", (missing_cursor,))

        result = store.read_outbox_batch(after_cursor=0, limit=page_size)
        assert result["status"] == "resnapshot_required"
        assert result["reason"] == "cursor_gap"
        assert result["events"] == []
        assert result["next_cursor"] == result["high_water"] == 4


def test_global_outbox_batch_validates_cursor_and_page_size(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-global-validation.sqlite3"))
    with pytest.raises(ValueError, match="after_cursor"):
        store.read_outbox_batch(after_cursor=True)
    with pytest.raises(ValueError, match="limit"):
        store.read_outbox_batch(after_cursor=0, limit=0)


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

def test_outbox_event_lookup_does_not_confuse_same_timestamp_derived_revisions(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "outbox-revision-lookup.sqlite3"))
    open_bar = make_bar(
        start=60 * NS, event=100, sequence=7, origin="derived",
        completeness="open",
    )
    complete_bar = make_bar(
        start=60 * NS, event=100, sequence=7, origin="derived",
        completeness="complete",
    )

    assert store.apply(open_bar) == "inserted"
    open_event = store.outbox_event_for_bar(open_bar)
    assert open_event is not None
    assert open_event["cursor"] == 1

    assert store.apply(complete_bar) == "replaced"
    complete_event = store.outbox_event_for_bar(complete_bar)
    assert complete_event is not None
    assert complete_event["cursor"] == 2

    # A delayed callback for the earlier revision must not be mapped to the
    # newer outbox event just because its timestamps, sequence and OHLCV match.
    assert store.outbox_event_for_bar(open_bar) == open_event


def test_global_snapshot_exports_every_retained_series_with_verified_manifest(tmp_path):
    import json
    from dataclasses import replace

    path = str(tmp_path / "global-source.sqlite3")
    store = SQLiteOhlcvStore(path)
    legacy = make_bar(
        start=0, close="101.000000000000000001",
        volume="12.500000000000000009",
    )
    fixed = replace(
        make_bar(start=0, bucket_policy="UTC_FIXED_V1"),
        bucket_policy="UTC_FIXED_V1",
    )
    cme = replace(
        make_bar(start=0, timeframe="1d"),
        bucket_policy="CME_SESSION_V1",
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2026.11.1",
    )
    assert store.apply(legacy) == "inserted"
    assert store.apply(fixed) == "inserted"
    assert store.apply(cme) == "inserted"

    destination = tmp_path / "global.snapshot.jsonl"
    exported = store.export_global_snapshot(str(destination), batch_size=1)
    verified = SQLiteOhlcvStore.verify_global_snapshot(str(destination))
    records = [json.loads(line) for line in destination.read_text().splitlines()]
    bars = [record["data"] for record in records if record["record"] == "bar"]

    assert exported["cursor"] == exported["high_water"] == 3
    assert exported["row_count"] == verified["row_count"] == 3
    assert verified["source_id"] == store.source_id()
    assert exported["format_version"] == verified["format_version"] == 2
    assert exported["bar_retention"] == verified["bar_retention"] == store.retention
    assert SQLiteOhlcvStore(str(tmp_path / "global-source.sqlite3")).source_id() == store.source_id()
    assert {bar["bucket_policy"] for bar in bars} == {
        "UTC_LEGACY", "UTC_FIXED_V1", "CME_SESSION_V1",
    }
    cme_row = next(bar for bar in bars if bar["bucket_policy"] == "CME_SESSION_V1")
    assert cme_row["calendar_id"] == "CME_EQUITY_INDEX"
    assert cme_row["calendar_version"] == "2026.11.1"
    legacy_row = next(bar for bar in bars if bar["bucket_policy"] == "UTC_LEGACY")
    assert legacy_row["close"] == "101.000000000000000001"
    assert legacy_row["volume"] == "12.500000000000000009"

    # Header metadata is included in the digest; a forged watermark is rejected.
    original = destination.read_text()
    changed_header = original.replace('"high_water":3', '"high_water":2', 1)
    destination.write_text(changed_header)
    with pytest.raises(ValueError, match="manifest"):
        SQLiteOhlcvStore.verify_global_snapshot(str(destination))

    # A changed payload must also fail the streaming manifest integrity check.
    changed_payload = original.replace(
        "101.000000000000000001", "101.000000000000000002", 1,
    )
    destination.write_text(changed_payload)
    with pytest.raises(ValueError, match="manifest"):
        SQLiteOhlcvStore.verify_global_snapshot(str(destination))


def test_global_snapshot_pins_bars_and_watermark_during_concurrent_write(
    tmp_path, monkeypatch,
):
    import sqlite3
    import threading

    path = str(tmp_path / "global-snapshot-concurrent.sqlite3")
    store = SQLiteOhlcvStore(path)
    first = make_bar(start=0, event=100, sequence=1)
    second = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
        instrument_id=456, raw_symbol="NQZ6",
    )
    assert store.apply(first) == "inserted"

    state_read = threading.Event()
    continue_export = threading.Event()
    original_connect = sqlite3.connect
    outcome = {}

    class PausingConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            result = super().execute(sql, parameters)
            if (
                threading.current_thread().name == "snapshot-exporter"
                and sql.startswith("SELECT state_key,int_value FROM ohlcv_outbox_state")
            ):
                state_read.set()
                if not continue_export.wait(timeout=5):
                    raise TimeoutError("global snapshot export barrier timed out")
            return result

    def connect_with_pausing_factory(*args, **kwargs):
        kwargs["factory"] = PausingConnection
        return original_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_with_pausing_factory)

    def export_snapshot():
        try:
            outcome["result"] = store.export_global_snapshot(
                str(tmp_path / "pinned.snapshot.jsonl"), batch_size=1,
            )
        except Exception as exc:
            outcome["error"] = exc

    exporter = threading.Thread(target=export_snapshot, name="snapshot-exporter")
    exporter.start()
    try:
        assert state_read.wait(timeout=5), "snapshot export did not pin its read view"
        assert store.apply(second) == "inserted"
    finally:
        continue_export.set()
        exporter.join(timeout=5)

    assert not exporter.is_alive()
    assert "error" not in outcome
    snapshot = SQLiteOhlcvStore.verify_global_snapshot(
        str(tmp_path / "pinned.snapshot.jsonl")
    )
    assert snapshot["cursor"] == snapshot["high_water"] == 1
    assert snapshot["row_count"] == 1
    assert store.outbox_high_water() == 2
    assert store.stats()["bars"] == 2


def test_global_snapshot_rejects_unsafe_destination_and_invalid_batch_size(tmp_path):
    store = SQLiteOhlcvStore(str(tmp_path / "global-snapshot-validation.sqlite3"))
    with pytest.raises(ValueError, match="destination_path"):
        store.export_global_snapshot("")
    with pytest.raises(ValueError, match="batch_size"):
        store.export_global_snapshot(str(tmp_path / "invalid.snapshot"), batch_size=True)
    with pytest.raises(ValueError, match="batch_size"):
        store.export_global_snapshot(str(tmp_path / "invalid.snapshot"), batch_size=0)
    with pytest.raises(ValueError, match="overwrite"):
        store.export_global_snapshot(store.database_path)


def test_replica_installs_global_snapshot_atomically_without_outbox_echo(tmp_path):
    from dataclasses import replace

    source = SQLiteOhlcvStore(str(tmp_path / "authoritative.sqlite3"))
    legacy = make_bar(
        start=0, close="101.000000000000000001",
        volume="12.500000000000000009",
    )
    cme = replace(
        make_bar(start=0, timeframe="1d", instrument_id=456, raw_symbol="ESZ6"),
        bucket_policy="CME_SESSION_V1",
        calendar_id="CME_EQUITY_INDEX",
        calendar_version="2026.11.1",
    )
    assert source.apply(legacy) == "inserted"
    assert source.apply(cme) == "inserted"

    snapshot_path = tmp_path / "replica.snapshot.jsonl"
    exported = source.export_global_snapshot(str(snapshot_path), batch_size=1)
    replica_path = str(tmp_path / "gateway-replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(replica_path)
    replica_id = replica.replica_id()

    installed = replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=source.source_id(), batch_size=1,
    )
    assert installed["status"] == "installed"
    assert installed["installed_rows"] == 2
    assert installed["cursor"] == exported["high_water"] == 2
    assert replica.load_bars() == [legacy, cme]
    assert replica.checkpoint() == {
        "source_id": source.source_id(),
        "replica_id": replica_id,
        "applied_cursor": 2,
        "snapshot_generation": exported["generation_id"],
        "retention_floor": exported["retention_floor"],
        "bar_retention": source.retention,
        "schema_version": 3,
        "protocol_version": 3,
    }
    # Imported bars are read-model state, never new source outbox events.
    assert replica.outbox_high_water() == 0
    with pytest.raises(RuntimeError, match="cannot use source-writer apply"):
        replica.apply(legacy)
    with pytest.raises(RuntimeError, match="cannot export an authoritative source"):
        replica.export_global_snapshot(str(tmp_path / "replica-must-not-export.jsonl"))

    restarted = SQLiteOhlcvReplicaStore(replica_path)
    assert restarted.replica_id() == replica_id
    assert restarted.checkpoint() == replica.checkpoint()
    assert restarted.load_bars() == [legacy, cme]


def test_replica_snapshot_rejects_wrong_source_and_stale_cursor(tmp_path):
    import json

    source = SQLiteOhlcvStore(str(tmp_path / "replica-source.sqlite3"))
    assert source.apply(make_bar()) == "inserted"
    snapshot = tmp_path / "source.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))

    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica-target.sqlite3"))
    with pytest.raises(ValueError, match="source identity"):
        replica.install_global_snapshot(
            str(snapshot), expected_source_id="not-the-source",
        )
    assert replica.checkpoint() is None
    assert replica.load_bars() == []

    replica.install_global_snapshot(str(snapshot))
    with pytest.raises(ValueError, match="older than"):
        # Re-exporting the same source at a lower watermark is constructed below.
        stale_path = tmp_path / "stale.snapshot.jsonl"
        lines = snapshot.read_text().splitlines()
        header = json.loads(lines[0])
        header["high_water"] = 0
        import hashlib
        digest = hashlib.sha256()
        header_line = json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
        digest.update(header_line + b"\n")
        manifest = {"record": "manifest", "row_count": 0, "sha256": digest.hexdigest()}
        stale_path.write_text(
            header_line.decode() + "\n"
            + json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
        )
        replica.install_global_snapshot(str(stale_path))


def test_replica_snapshot_semantic_failure_rolls_back_bars_and_checkpoint(tmp_path):
    import hashlib
    import json

    source = SQLiteOhlcvStore(str(tmp_path / "replica-rollback-source.sqlite3"))
    original = make_bar()
    assert source.apply(original) == "inserted"
    initial_path = tmp_path / "initial.snapshot.jsonl"
    source.export_global_snapshot(str(initial_path))
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica-rollback-target.sqlite3"))
    replica.install_global_snapshot(str(initial_path))
    before_checkpoint = replica.checkpoint()
    before_bars = replica.load_bars()

    second = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
        instrument_id=456, raw_symbol="NQZ6",
    )
    assert source.apply(second) == "inserted"
    valid_path = tmp_path / "valid-next.snapshot.jsonl"
    source.export_global_snapshot(str(valid_path))
    source_lines = valid_path.read_text().splitlines()
    header = json.loads(source_lines[0])
    records = [json.loads(line) for line in source_lines[1:-1]]
    malformed = next(
        item for item in records
        if item["record"] == "bar" and item["data"]["instrument_id"] == 456
    )
    malformed["data"]["close"] = "999"

    digest = hashlib.sha256()
    header_line = json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
    digest.update(header_line + b"\n")
    encoded_records = []
    for record in records:
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
        digest.update(encoded + b"\n")
        encoded_records.append(encoded.decode())
    manifest = {
        "record": "manifest",
        "row_count": len(records),
        "sha256": digest.hexdigest(),
    }
    forged_but_checksummed = tmp_path / "semantic-invalid.snapshot.jsonl"
    forged_but_checksummed.write_text(
        header_line.decode() + "\n"
        + "\n".join(encoded_records) + "\n"
        + json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
    )

    # The envelope/checksum is valid; canonical OHLCV validation fails after
    # the old rows have been deleted and a first new row may already be staged.
    assert SQLiteOhlcvStore.verify_global_snapshot(str(forged_but_checksummed))["row_count"] == 2
    with pytest.raises(ValueError, match="invalid canonical OHLCV bar"):
        replica.install_global_snapshot(str(forged_but_checksummed), batch_size=1)

    assert replica.checkpoint() == before_checkpoint
    assert replica.load_bars() == before_bars
    assert replica.outbox_high_water() == 0


def test_replica_snapshot_rejects_numeric_decimal_fields_even_with_valid_digest(tmp_path):
    import hashlib
    import json

    source = SQLiteOhlcvStore(str(tmp_path / "replica-types-source.sqlite3"))
    assert source.apply(make_bar()) == "inserted"
    snapshot = tmp_path / "typed.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))
    lines = snapshot.read_text().splitlines()
    header = json.loads(lines[0])
    record = json.loads(lines[1])
    record["data"]["close"] = 101.25

    digest = hashlib.sha256()
    header_line = json.dumps(header, sort_keys=True, separators=(",", ":")).encode()
    digest.update(header_line + b"\\n")
    record_line = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    digest.update(record_line + b"\\n")
    manifest = {
        "record": "manifest", "row_count": 1, "sha256": digest.hexdigest(),
    }
    invalid = tmp_path / "numeric-decimal.snapshot.jsonl"
    invalid.write_text(
        header_line.decode() + "\\n" + record_line.decode() + "\\n"
        + json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\\n"
    )

    assert SQLiteOhlcvStore.verify_global_snapshot(str(invalid))["row_count"] == 1
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica-types-target.sqlite3"))
    with pytest.raises(ValueError, match="exact-decimal fields must be strings"):
        replica.install_global_snapshot(str(invalid))
    assert replica.checkpoint() is None
    assert replica.load_bars() == []


def test_replica_install_refuses_to_replace_an_authoritative_database(tmp_path):
    authoritative_path = str(tmp_path / "must-not-be-replaced.sqlite3")
    authoritative = SQLiteOhlcvStore(authoritative_path)
    original = make_bar()
    assert authoritative.apply(original) == "inserted"

    replica_view = SQLiteOhlcvReplicaStore(authoritative_path)
    other_source = SQLiteOhlcvStore(str(tmp_path / "other-authority.sqlite3"))
    assert other_source.apply(make_bar(instrument_id=456, raw_symbol="NQZ6")) == "inserted"
    snapshot = tmp_path / "other-source.snapshot.jsonl"
    other_source.export_global_snapshot(str(snapshot))

    with pytest.raises(RuntimeError, match="dedicated empty OHLCV read-model"):
        replica_view.install_global_snapshot(str(snapshot))

    assert authoritative.load_bars() == [original]
    assert authoritative.outbox_high_water() == 1


def test_replica_applies_contiguous_outbox_events_idempotently_without_echo(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "event-source.sqlite3"))
    initial = make_bar()
    assert source.apply(initial) == "inserted"
    snapshot = tmp_path / "event-initial.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))

    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "event-replica.sqlite3"))
    replica.install_global_snapshot(str(snapshot))
    next_bar = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
        instrument_id=456, raw_symbol="NQZ6",
    )
    assert source.apply(next_bar) == "inserted"
    page = source.read_outbox_batch(after_cursor=1, limit=10)
    assert page["status"] == "ok"
    event = page["events"][0]
    assert event["cursor"] == 2

    applied = replica.apply_replica_event(
        event, source_id=source.source_id(), retention_floor=page["retention_floor"],
    )
    assert applied["status"] == "applied"
    assert applied["applied_cursor"] == 2
    assert replica.load_bars() == [initial, next_bar]
    assert replica.checkpoint()["applied_cursor"] == 2
    assert replica.outbox_high_water() == 0

    duplicate = replica.apply_replica_event(
        event, source_id=source.source_id(), retention_floor=page["retention_floor"],
    )
    assert duplicate["status"] == "duplicate"
    assert replica.checkpoint()["applied_cursor"] == 2
    assert replica.load_bars() == [initial, next_bar]


def test_replica_event_gap_conflict_stale_and_source_validation(tmp_path):
    import copy
    import sqlite3

    source = SQLiteOhlcvStore(str(tmp_path / "event-order-source.sqlite3"))
    assert source.apply(make_bar()) == "inserted"
    snapshot = tmp_path / "event-order.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))
    replica_path = str(tmp_path / "event-order-replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(replica_path)
    replica.install_global_snapshot(str(snapshot))

    second = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
        instrument_id=456, raw_symbol="NQZ6",
    )
    third = make_bar(
        start=120 * NS, event=102, sequence=3, close="103",
        instrument_id=789, raw_symbol="YMZ6",
    )
    assert source.apply(second) == "inserted"
    assert source.apply(third) == "inserted"
    page = source.read_outbox_batch(after_cursor=1, limit=10)
    event2, event3 = page["events"]

    gap = replica.apply_replica_event(event3, source_id=source.source_id())
    assert gap == {
        "status": "resnapshot_required",
        "reason": "cursor_gap",
        "expected_cursor": 2,
        "received_cursor": 3,
        "applied_cursor": 1,
    }
    assert replica.checkpoint()["applied_cursor"] == 1
    assert replica.load_bars() == [make_bar()]

    with pytest.raises(ValueError, match="source identity"):
        replica.apply_replica_event(event2, source_id="different-source")
    malformed = copy.deepcopy(event2)
    malformed["bar"]["close"] = 101.5
    with pytest.raises(ValueError, match="decimal and string fields"):
        replica.apply_replica_event(malformed, source_id=source.source_id())

    assert replica.apply_replica_event(event2, source_id=source.source_id())["status"] == "applied"
    assert replica.apply_replica_event(event3, source_id=source.source_id())["status"] == "applied"
    assert replica.checkpoint()["applied_cursor"] == 3
    assert replica.load_bars() == [make_bar(), second, third]

    duplicate = replica.apply_replica_event(event2, source_id=source.source_id())
    assert duplicate["status"] == "duplicate"
    conflicting = copy.deepcopy(event2)
    conflicting["eventId"] = "different-event-id"
    with pytest.raises(ValueError, match="conflicts with an already applied event"):
        replica.apply_replica_event(conflicting, source_id=source.source_id())

    with sqlite3.connect(replica_path) as db:
        db.execute("DELETE FROM ohlcv_replica_applied_events WHERE cursor=2")
    stale = replica.apply_replica_event(event2, source_id=source.source_id())
    assert stale["status"] == "stale"
    assert replica.checkpoint()["applied_cursor"] == 3
    assert replica.outbox_high_water() == 0


def test_replica_event_bar_and_checkpoint_rollback_together_on_checkpoint_failure(tmp_path):
    import sqlite3

    source = SQLiteOhlcvStore(str(tmp_path / "event-rollback-source.sqlite3"))
    original = make_bar()
    assert source.apply(original) == "inserted"
    snapshot = tmp_path / "event-rollback.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))
    replica_path = str(tmp_path / "event-rollback-replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(replica_path)
    replica.install_global_snapshot(str(snapshot))

    next_bar = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
        instrument_id=456, raw_symbol="NQZ6",
    )
    assert source.apply(next_bar) == "inserted"
    event = source.read_outbox_batch(after_cursor=1, limit=10)["events"][0]

    with sqlite3.connect(replica_path) as db:
        db.execute(
            """CREATE TRIGGER reject_replica_checkpoint
            BEFORE UPDATE ON ohlcv_replica_checkpoint
            BEGIN SELECT RAISE(ABORT, 'forced checkpoint failure'); END"""
        )

    with pytest.raises(sqlite3.IntegrityError, match="forced checkpoint failure"):
        replica.apply_replica_event(event, source_id=source.source_id())

    assert replica.checkpoint()["applied_cursor"] == 1
    assert replica.load_bars() == [original]
    assert replica.outbox_high_water() == 0
    with sqlite3.connect(replica_path) as db:
        assert db.execute(
            "SELECT COUNT(*) FROM ohlcv_replica_applied_events"
        ).fetchone()[0] == 0


def test_replica_incremental_apply_enforces_source_bar_retention_policy(tmp_path):
    source = SQLiteOhlcvStore(
        str(tmp_path / "retention-source.sqlite3"), retention={"1m": 5},
    )
    for index in range(5):
        assert source.apply(make_bar(
            start=index * 60 * NS, event=100 + index, sequence=index + 1,
        )) == "inserted"

    snapshot = tmp_path / "retention.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "retention-replica.sqlite3"))
    replica.install_global_snapshot(str(snapshot))
    assert replica.checkpoint()["bar_retention"]["1m"] == 5

    sixth = make_bar(
        start=5 * 60 * NS, event=105, sequence=6,
    )
    assert source.apply(sixth) == "inserted"
    page = source.read_outbox_batch(after_cursor=5, limit=10)
    assert page["status"] == "ok"
    result = replica.apply_replica_event(
        page["events"][0],
        source_id=source.source_id(),
        retention_floor=page["retention_floor"],
    )
    assert result["status"] == "applied"
    assert len(source.load_bars()) == len(replica.load_bars()) == 5
    assert replica.load_bars() == source.load_bars()
    assert replica.load_bars()[0].ts_start_ns == 60 * NS


def test_replica_event_apply_requires_current_checkpoint_protocol(tmp_path):
    import sqlite3

    source = SQLiteOhlcvStore(str(tmp_path / "protocol-source.sqlite3"))
    assert source.apply(make_bar()) == "inserted"
    snapshot = tmp_path / "protocol.snapshot.jsonl"
    source.export_global_snapshot(str(snapshot))
    replica_path = str(tmp_path / "protocol-replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(replica_path)
    replica.install_global_snapshot(str(snapshot))

    next_bar = make_bar(
        start=60 * NS, event=101, sequence=2, close="102",
        instrument_id=456, raw_symbol="NQZ6",
    )
    assert source.apply(next_bar) == "inserted"
    event = source.read_outbox_batch(after_cursor=1, limit=10)["events"][0]
    with sqlite3.connect(replica_path) as db:
        db.execute(
            "UPDATE ohlcv_replica_checkpoint SET protocol_version=2"
        )

    with pytest.raises(RuntimeError, match="checkpoint version mismatch"):
        replica.apply_replica_event(event, source_id=source.source_id())
    assert replica.checkpoint()["applied_cursor"] == 1
    assert replica.load_bars() == [make_bar()]
