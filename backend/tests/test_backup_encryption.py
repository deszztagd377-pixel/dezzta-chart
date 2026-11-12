import os
import stat

import pytest
from cryptography.exceptions import InvalidTag

from app.backup_encryption import decrypt_backup_file, encrypt_backup_file

PASSPHRASE = b"test-only-passphrase-32-bytes-long"


def test_backup_encryption_round_trip_and_private_permissions(tmp_path):
    source = tmp_path / "backup.sqlite3"
    encrypted = tmp_path / "offsite" / "backup.sqlite3.enc"
    restored = tmp_path / "restore.sqlite3"
    payload = (b"sqlite-backup-payload-" * 100_000) + b"end"
    source.write_bytes(payload)

    encrypt_backup_file(source, encrypted, PASSPHRASE)
    assert encrypted.read_bytes() != payload
    decrypt_backup_file(encrypted, restored, PASSPHRASE)

    assert restored.read_bytes() == payload
    if os.name == "posix":
        assert stat.S_IMODE(encrypted.stat().st_mode) == 0o600
        assert stat.S_IMODE(restored.stat().st_mode) == 0o600


def test_backup_decryption_rejects_wrong_passphrase_without_publishing(tmp_path):
    encrypted = tmp_path / "backup.enc"
    restored = tmp_path / "restore.sqlite3"
    encrypted.write_bytes(b"")
    original = tmp_path / "source.sqlite3"
    original.write_bytes(b"important database snapshot")
    encrypt_backup_file(original, encrypted, PASSPHRASE)
    restored.write_bytes(b"previous-good-restore")

    with pytest.raises(InvalidTag):
        decrypt_backup_file(encrypted, restored, b"different-passphrase-32-bytes")

    assert restored.read_bytes() == b"previous-good-restore"
    assert list(tmp_path.glob(".restore.sqlite3.*.encrypted-backup.tmp")) == []


def test_backup_decryption_detects_ciphertext_tampering(tmp_path):
    source = tmp_path / "source.sqlite3"
    encrypted = tmp_path / "backup.enc"
    restored = tmp_path / "restore.sqlite3"
    source.write_bytes(b"database content")
    encrypt_backup_file(source, encrypted, PASSPHRASE)

    damaged = bytearray(encrypted.read_bytes())
    damaged[len(damaged) // 2] ^= 0x01
    encrypted.write_bytes(damaged)

    with pytest.raises(InvalidTag):
        decrypt_backup_file(encrypted, restored, PASSPHRASE)

    assert not restored.exists()
    assert list(tmp_path.glob(".restore.sqlite3.*.encrypted-backup.tmp")) == []


@pytest.mark.parametrize("passphrase", [b"", b"short", "not-bytes", None])
def test_encryption_rejects_weak_or_invalid_passphrase(tmp_path, passphrase):
    source = tmp_path / "source.sqlite3"
    source.write_bytes(b"backup")
    with pytest.raises(ValueError, match="at least 16 bytes"):
        encrypt_backup_file(source, tmp_path / "backup.enc", passphrase)


def test_decryption_rejects_invalid_header_without_publishing(tmp_path):
    encrypted = tmp_path / "backup.enc"
    encrypted.write_bytes(b"not-a-valid-encrypted-backup-format")
    restored = tmp_path / "restore.sqlite3"

    with pytest.raises(ValueError, match="not recognized"):
        decrypt_backup_file(encrypted, restored, PASSPHRASE)

    assert not restored.exists()


def test_consistent_sqlite_backup_encrypts_and_restores_application_records(tmp_path):
    import sqlite3

    from app.sqlite_backup import create_consistent_sqlite_backup

    source = tmp_path / "live.sqlite3"
    snapshot = tmp_path / "snapshot.sqlite3"
    encrypted = tmp_path / "off-host" / "snapshot.sqlite3.enc"
    restored = tmp_path / "restore" / "market.sqlite3"

    with sqlite3.connect(source) as database:
        database.execute("PRAGMA journal_mode=WAL")
        database.execute(
            "CREATE TABLE instruments (symbol TEXT PRIMARY KEY, venue TEXT NOT NULL)"
        )
        database.execute(
            "CREATE TABLE bars (symbol TEXT NOT NULL, timestamp TEXT NOT NULL, close TEXT NOT NULL)"
        )
        database.execute(
            "INSERT INTO instruments VALUES (?, ?)", ("ES", "CME")
        )
        database.execute(
            "INSERT INTO bars VALUES (?, ?, ?)",
            ("ES", "2026-11-12T15:00:00Z", "6012.125000000000001"),
        )

    create_consistent_sqlite_backup(source, snapshot)
    encrypt_backup_file(snapshot, encrypted, PASSPHRASE)
    decrypt_backup_file(encrypted, restored, PASSPHRASE)

    with sqlite3.connect(restored) as database:
        assert database.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert database.execute(
            "SELECT symbol, venue FROM instruments"
        ).fetchall() == [("ES", "CME")]
        assert database.execute(
            "SELECT symbol, timestamp, close FROM bars"
        ).fetchall() == [
            ("ES", "2026-11-12T15:00:00Z", "6012.125000000000001")
        ]

    assert encrypted.read_bytes() != snapshot.read_bytes()
    assert list(tmp_path.rglob("*.encrypted-backup.tmp")) == []
    assert list(tmp_path.rglob("*.sqlite-backup.tmp")) == []


def test_decryption_rejects_truncated_artifact_without_replacing_destination(tmp_path):
    source = tmp_path / "source.sqlite3"
    encrypted = tmp_path / "backup.enc"
    restored = tmp_path / "restore.sqlite3"
    source.write_bytes(b"valid database snapshot")
    encrypt_backup_file(source, encrypted, PASSPHRASE)
    artifact = encrypted.read_bytes()
    header_bytes = len(b"DZCBK01\\n") + 16 + 12
    tag_bytes = 16
    encrypted.write_bytes(artifact[: header_bytes + tag_bytes - 1])
    restored.write_bytes(b"previous-good-restore")

    with pytest.raises(ValueError, match="truncated"):
        decrypt_backup_file(encrypted, restored, PASSPHRASE)

    assert restored.read_bytes() == b"previous-good-restore"
    assert list(tmp_path.glob(".restore.sqlite3.*.encrypted-backup.tmp")) == []


def test_encryption_and_decryption_reject_same_source_and_destination(tmp_path):
    source = tmp_path / "source.sqlite3"
    encrypted = tmp_path / "backup.enc"
    source.write_bytes(b"source data")

    with pytest.raises(ValueError, match="must be different"):
        encrypt_backup_file(source, source, PASSPHRASE)
    assert source.read_bytes() == b"source data"

    encrypt_backup_file(source, encrypted, PASSPHRASE)
    original_encrypted = encrypted.read_bytes()
    with pytest.raises(ValueError, match="must be different"):
        decrypt_backup_file(encrypted, encrypted, PASSPHRASE)
    assert encrypted.read_bytes() == original_encrypted
