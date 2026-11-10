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
