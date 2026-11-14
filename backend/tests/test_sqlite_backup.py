import os
import sqlite3
import stat

import pytest

from app.sqlite_backup import create_consistent_sqlite_backup


def test_backup_captures_committed_wal_data_and_passes_integrity_check(tmp_path):
    source = tmp_path / "live.sqlite3"
    destination = tmp_path / "snapshots" / "market.sqlite3"

    with sqlite3.connect(source) as database:
        assert database.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        database.execute("CREATE TABLE bars (id INTEGER PRIMARY KEY, close TEXT NOT NULL)")
        database.execute("INSERT INTO bars (close) VALUES (?)", ("101.000000000000000001",))

    result = create_consistent_sqlite_backup(source, destination, pages=1)

    assert result == destination.resolve()
    with sqlite3.connect(destination) as backup:
        assert backup.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert backup.execute("SELECT close FROM bars").fetchall() == [
            ("101.000000000000000001",)
        ]


def test_backup_rejects_same_source_and_destination(tmp_path):
    source = tmp_path / "market.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")

    with pytest.raises(ValueError, match="must be different"):
        create_consistent_sqlite_backup(source, source)


@pytest.mark.parametrize("pages", [0, -1, True, 1.5, "10"])
def test_backup_rejects_invalid_page_batch_size(tmp_path, pages):
    source = tmp_path / "market.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")

    with pytest.raises(ValueError, match="positive integer"):
        create_consistent_sqlite_backup(source, tmp_path / "backup.sqlite3", pages=pages)


def test_backup_rejects_missing_source_without_creating_destination(tmp_path):
    destination = tmp_path / "backup.sqlite3"

    with pytest.raises(FileNotFoundError):
        create_consistent_sqlite_backup(tmp_path / "missing.sqlite3", destination)

    assert not destination.exists()


def test_failed_backup_preserves_previous_destination_and_removes_temporary_file(tmp_path):
    source = tmp_path / "not-a-database.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    source.write_text("not a SQLite database", encoding="utf-8")
    destination.write_bytes(b"previous-good-backup")

    with pytest.raises(sqlite3.DatabaseError):
        create_consistent_sqlite_backup(source, destination)

    assert destination.read_bytes() == b"previous-good-backup"
    assert list(tmp_path.glob(".backup.sqlite3.*.sqlite-backup.tmp")) == []


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits are required")
def test_backup_is_published_with_owner_only_permissions(tmp_path):
    source = tmp_path / "live.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")
        database.execute("INSERT INTO sample VALUES (1)")

    create_consistent_sqlite_backup(source, destination)

    assert stat.S_IMODE(destination.stat().st_mode) == 0o600


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits are required")
def test_backup_fails_closed_when_owner_only_permissions_cannot_be_set(
    tmp_path, monkeypatch
):
    from app import sqlite_backup

    source = tmp_path / "live.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")
        database.execute("INSERT INTO sample VALUES (1)")
    destination.write_bytes(b"previous-good-backup")

    def deny_chmod(*args, **kwargs):
        raise PermissionError("permission change denied")

    monkeypatch.setattr(sqlite_backup.os, "chmod", deny_chmod)

    with pytest.raises(PermissionError, match="permission change denied"):
        create_consistent_sqlite_backup(source, destination)

    assert destination.read_bytes() == b"previous-good-backup"
    assert list(tmp_path.glob(".backup.sqlite3.*.sqlite-backup.tmp")) == []


@pytest.mark.skipif(os.name != "posix", reason="POSIX fsync semantics are required")
def test_backup_fails_closed_when_snapshot_cannot_be_flushed(tmp_path, monkeypatch):
    from app import sqlite_backup

    source = tmp_path / "live.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")
        database.execute("INSERT INTO sample VALUES (1)")
    destination.write_bytes(b"previous-good-backup")

    def deny_fsync(*args, **kwargs):
        raise OSError("snapshot flush failed")

    monkeypatch.setattr(sqlite_backup.os, "fsync", deny_fsync)

    with pytest.raises(OSError, match="snapshot flush failed"):
        create_consistent_sqlite_backup(source, destination)

    assert destination.read_bytes() == b"previous-good-backup"
    assert list(tmp_path.glob(".backup.sqlite3.*.sqlite-backup.tmp")) == []


@pytest.mark.skipif(os.name != "posix", reason="POSIX directory fsync is required")
def test_backup_flushes_parent_directory_after_atomic_replace(tmp_path, monkeypatch):
    from app import sqlite_backup

    source = tmp_path / "live.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")
        database.execute("INSERT INTO sample VALUES (7)")

    flushed_directories = []

    def record_directory_flush(directory):
        flushed_directories.append(directory)

    monkeypatch.setattr(sqlite_backup, "_fsync_directory", record_directory_flush)

    create_consistent_sqlite_backup(source, destination)

    assert flushed_directories == [destination.parent.resolve()]
    with sqlite3.connect(destination) as database:
        assert database.execute("SELECT value FROM sample").fetchone() == (7,)


@pytest.mark.skipif(os.name != "posix", reason="POSIX directory fsync is required")
def test_directory_flush_failure_is_reported_after_valid_snapshot_is_published(
    tmp_path, monkeypatch
):
    from app import sqlite_backup

    source = tmp_path / "live.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with sqlite3.connect(source) as database:
        database.execute("CREATE TABLE sample (value INTEGER)")
        database.execute("INSERT INTO sample VALUES (9)")

    def deny_directory_flush(directory):
        raise OSError("directory flush failed")

    monkeypatch.setattr(sqlite_backup, "_fsync_directory", deny_directory_flush)

    with pytest.raises(OSError, match="directory flush failed"):
        create_consistent_sqlite_backup(source, destination)

    # Atomic replacement already happened. The valid snapshot is visible, but
    # the helper correctly reports that rename durability was not confirmed.
    with sqlite3.connect(destination) as database:
        assert database.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert database.execute("SELECT value FROM sample").fetchone() == (9,)
    assert list(tmp_path.glob(".backup.sqlite3.*.sqlite-backup.tmp")) == []


def test_consistent_backup_can_be_restored_into_a_fresh_database(tmp_path):
    source = tmp_path / "live.sqlite3"
    snapshot = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"

    with sqlite3.connect(source) as database:
        database.execute(
            "CREATE TABLE bars (id INTEGER PRIMARY KEY, close TEXT NOT NULL)"
        )
        database.execute(
            "INSERT INTO bars (close) VALUES (?)",
            ("123.450000000000000001",),
        )

    create_consistent_sqlite_backup(source, snapshot)

    with sqlite3.connect(snapshot) as backup, sqlite3.connect(restored) as target:
        backup.backup(target)

    with sqlite3.connect(restored) as database:
        assert database.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert database.execute("SELECT close FROM bars").fetchall() == [
            ("123.450000000000000001",)
        ]



def test_application_ohlcv_and_replay_outbox_survive_fresh_database_restore(tmp_path):
    """Exercise the real SQLite OHLCV store, not only a hand-made sample table.

    This test deliberately imports no encryption package so the local SQLite
    restore path can be tested independently from the Android crypto blocker.
    """
    from decimal import Decimal

    from app.ohlcv import OhlcvBar
    from app.ohlcv_store import SQLiteOhlcvStore

    source = tmp_path / "application-live.sqlite3"
    snapshot = tmp_path / "application-snapshot.sqlite3"
    restore_directory = tmp_path / "fresh-restore"
    restore_directory.mkdir()
    restored = restore_directory / "application.sqlite3"

    original = OhlcvBar(
        provider="databento",
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=123,
        raw_symbol="ESZ6",
        series_type="contract",
        timeframe="1m",
        ts_start_ns=60_000_000_000,
        open=Decimal("100"),
        high=Decimal("103"),
        low=Decimal("99"),
        close=Decimal("101.000000000000000001"),
        volume=Decimal("12.500000000000000009"),
        ts_event_ns=1_790_000_000_123_456_789,
        ts_received_ns=1_790_000_000_123_456_799,
        sequence=1,
        sequence_origin="local",
        origin="provider",
        completeness="unknown",
    )

    live_store = SQLiteOhlcvStore(str(source))
    assert live_store.apply(original) == "inserted"
    assert live_store.outbox_high_water() == 1

    create_consistent_sqlite_backup(source, snapshot)

    with sqlite3.connect(snapshot) as backup, sqlite3.connect(restored) as target:
        backup.backup(target)

    restored_store = SQLiteOhlcvStore(str(restored))
    assert restored_store.load_bars() == [original]
    assert restored_store.outbox_high_water() == 1

    event = restored_store.outbox_event_for_bar(original)
    assert event is not None
    assert restored_store.outbox_event_id(int(event["cursor"])) == event["eventId"]

    # Continue writing after restore, then replay from the restored outbox.
    # This verifies that recovery preserves both application rows and the
    # durable event sequence needed by downstream consumers.
    from dataclasses import replace

    continued = replace(
        original,
        ts_start_ns=120_000_000_000,
        open=Decimal("101"),
        high=Decimal("104"),
        low=Decimal("100"),
        close=Decimal("102"),
        volume=Decimal("13"),
        ts_event_ns=original.ts_event_ns + 60_000_000_000,
        ts_received_ns=original.ts_received_ns + 60_000_000_000,
        sequence=2,
    )
    assert restored_store.apply(continued) == "inserted"
    assert restored_store.outbox_high_water() == 2
    assert restored_store.load_bars() == [original, continued]

    replay = restored_store.replay_outbox(
        after_cursor=0,
        provider=original.provider,
        dataset=original.dataset,
        publisher_id=original.publisher_id,
        instrument_id=original.instrument_id,
        series_type=original.series_type,
        raw_symbol=original.raw_symbol,
        timeframe=original.timeframe,
        bucket_policy=original.bucket_policy,
        limit=10,
    )
    assert replay["status"] == "ok"
    assert [item["cursor"] for item in replay["events"]] == [1, 2]
    assert [item["eventId"] for item in replay["events"]] == [
        restored_store.outbox_event_id(1),
        restored_store.outbox_event_id(2),
    ]
    assert replay["next_cursor"] == 2
    assert replay["high_water"] == 2

