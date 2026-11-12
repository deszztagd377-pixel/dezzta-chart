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
