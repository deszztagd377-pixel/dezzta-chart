"""Authenticated encryption for SQLite backup artifacts.

The format is versioned and uses PBKDF2-HMAC-SHA256 + AES-256-GCM.
Decryption writes only to a private temporary file and publishes it after
GCM authentication succeeds, so unauthenticated plaintext is never exposed
at the destination path.
"""
from __future__ import annotations

import os
from pathlib import Path
import tempfile

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_MAGIC = b"DZCBK01\n"
_SALT_BYTES = 16
_NONCE_BYTES = 12
_TAG_BYTES = 16
_KEY_BYTES = 32
_ITERATIONS = 600_000
_CHUNK_BYTES = 1024 * 1024
_HEADER_BYTES = len(_MAGIC) + _SALT_BYTES + _NONCE_BYTES


def _validate_passphrase(passphrase: bytes) -> None:
    if not isinstance(passphrase, bytes) or len(passphrase) < 16:
        raise ValueError("passphrase must contain at least 16 bytes.")


def _derive_key(passphrase: bytes, salt: bytes) -> bytes:
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_BYTES,
        salt=salt,
        iterations=_ITERATIONS,
    ).derive(passphrase)


def _temporary_file(destination: Path) -> tuple[int, Path]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".encrypted-backup.tmp",
        dir=destination.parent,
    )
    return descriptor, Path(name)


def _fsync_directory(directory: Path) -> None:
    """Flush a directory entry update to stable storage on POSIX."""
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _publish_private_file(temporary: Path, destination: Path) -> None:
    if os.name == "posix":
        os.chmod(temporary, 0o600)
    os.replace(temporary, destination)
    if os.name == "posix":
        # The file contents are fsynced before this rename. Flush the parent
        # directory as well so the published name is durable across a crash.
        # If this fails, the destination may already be visible; durability is
        # uncertain and the error must be surfaced to the caller.
        _fsync_directory(destination.parent)


def encrypt_backup_file(
    source_path: str | Path,
    destination_path: str | Path,
    passphrase: bytes,
) -> Path:
    """Encrypt a backup file and atomically publish an authenticated artifact."""
    _validate_passphrase(passphrase)
    source = Path(source_path).expanduser().resolve()
    destination = Path(destination_path).expanduser().resolve()
    if source == destination:
        raise ValueError("source_path and destination_path must be different.")
    if not source.is_file():
        raise FileNotFoundError(source)

    salt = os.urandom(_SALT_BYTES)
    nonce = os.urandom(_NONCE_BYTES)
    header = _MAGIC + salt + nonce
    encryptor = Cipher(
        algorithms.AES(_derive_key(passphrase, salt)),
        modes.GCM(nonce),
    ).encryptor()
    encryptor.authenticate_additional_data(header)

    descriptor, temporary = _temporary_file(destination)
    try:
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as input_file:
            output.write(header)
            while chunk := input_file.read(_CHUNK_BYTES):
                output.write(encryptor.update(chunk))
            output.write(encryptor.finalize())
            output.write(encryptor.tag)
            output.flush()
            os.fsync(output.fileno())
        _publish_private_file(temporary, destination)
        return destination
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def decrypt_backup_file(
    source_path: str | Path,
    destination_path: str | Path,
    passphrase: bytes,
) -> Path:
    """Authenticate and decrypt an artifact before atomically publishing it."""
    _validate_passphrase(passphrase)
    source = Path(source_path).expanduser().resolve()
    destination = Path(destination_path).expanduser().resolve()
    if source == destination:
        raise ValueError("source_path and destination_path must be different.")
    if not source.is_file():
        raise FileNotFoundError(source)

    source_size = source.stat().st_size
    with source.open("rb") as input_file:
        header = input_file.read(_HEADER_BYTES)
    if len(header) != _HEADER_BYTES or not header.startswith(_MAGIC):
        raise ValueError("Encrypted backup format is not recognized.")
    if source_size < _HEADER_BYTES + _TAG_BYTES:
        raise ValueError("Encrypted backup is truncated.")

    descriptor, temporary = _temporary_file(destination)
    try:
        # Take ownership of the temporary descriptor before any operation that
        # can fail while reopening/reading the source. The context manager then
        # guarantees it is closed on every exceptional path.
        with os.fdopen(descriptor, "wb") as output:
            with source.open("rb") as input_file:
                salt_start = len(_MAGIC)
                salt = header[salt_start : salt_start + _SALT_BYTES]
                nonce = header[salt_start + _SALT_BYTES :]
                input_file.seek(-_TAG_BYTES, os.SEEK_END)
                tag = input_file.read(_TAG_BYTES)
                ciphertext_remaining = source_size - _HEADER_BYTES - _TAG_BYTES
                input_file.seek(_HEADER_BYTES)

                decryptor = Cipher(
                    algorithms.AES(_derive_key(passphrase, salt)),
                    modes.GCM(nonce, tag),
                ).decryptor()
                decryptor.authenticate_additional_data(header)

                while ciphertext_remaining:
                    chunk = input_file.read(min(_CHUNK_BYTES, ciphertext_remaining))
                    if not chunk:
                        raise ValueError("Encrypted backup is truncated.")
                    ciphertext_remaining -= len(chunk)
                    output.write(decryptor.update(chunk))
                output.write(decryptor.finalize())
            output.flush()
            os.fsync(output.fileno())

        _publish_private_file(temporary, destination)
        return destination
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
