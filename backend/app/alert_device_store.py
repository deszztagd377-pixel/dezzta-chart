"""Encrypted, account-scoped storage for mobile push-notification tokens.

This adapter deliberately requires an owner-injected 256-bit key. It never
persists plaintext FCM tokens and exposes no HTTP routes by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import closing
import os
from pathlib import Path
import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_MAX_OWNER_LENGTH = 128
_MAX_INSTALLATION_LENGTH = 128
_MAX_TOKEN_LENGTH = 4096
_MAX_DEVICES_PER_OWNER = 10


class AlertDeviceStoreError(RuntimeError):
    """Base error for secure alert-device persistence."""


class AlertDeviceQuotaExceeded(AlertDeviceStoreError):
    """An account has reached its active device registration limit."""


@dataclass(frozen=True, slots=True)
class StoredAlertDevice:
    installation_id: str
    created_at_utc: str
    updated_at_utc: str


class SQLiteAlertDeviceStore:
    """AES-256-GCM encrypted FCM-token storage in the shared SQLite database."""

    def __init__(self, database_path: str, *, encryption_key: bytes) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("database_path is required.")
        if database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable device tokens.")
        if not isinstance(encryption_key, bytes) or len(encryption_key) != 32:
            raise ValueError("encryption_key must contain exactly 32 bytes.")
        self.database_path = str(Path(database_path).expanduser())
        self._cipher = AESGCM(encryption_key)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS alert_device_tokens (
                    owner_id TEXT NOT NULL CHECK(length(owner_id) BETWEEN 1 AND 128),
                    installation_id TEXT NOT NULL CHECK(length(installation_id) BETWEEN 1 AND 128),
                    token_ciphertext BLOB NOT NULL,
                    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    revoked_at_utc TEXT,
                    PRIMARY KEY(owner_id, installation_id)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_alert_device_owner_active
                ON alert_device_tokens(owner_id, revoked_at_utc, updated_at_utc)
                """
            )

    @staticmethod
    def _validate_identity(owner_id: str, installation_id: str) -> tuple[str, str]:
        if not isinstance(owner_id, str) or not 1 <= len(owner_id.strip()) <= _MAX_OWNER_LENGTH:
            raise ValueError("owner_id must contain 1 to 128 characters.")
        if (
            not isinstance(installation_id, str)
            or not 1 <= len(installation_id.strip()) <= _MAX_INSTALLATION_LENGTH
        ):
            raise ValueError("installation_id must contain 1 to 128 characters.")
        return owner_id.strip(), installation_id.strip()

    def _encrypt(self, owner_id: str, installation_id: str, token: str) -> bytes:
        nonce = os.urandom(12)
        associated_data = (owner_id + "\0" + installation_id).encode("utf-8")
        ciphertext = self._cipher.encrypt(nonce, token.encode("utf-8"), associated_data)
        return nonce + ciphertext

    def _decrypt(self, owner_id: str, installation_id: str, value: bytes) -> str:
        if not isinstance(value, bytes) or len(value) < 29:
            raise AlertDeviceStoreError("Stored device token ciphertext is invalid.")
        associated_data = (owner_id + "\0" + installation_id).encode("utf-8")
        try:
            return self._cipher.decrypt(value[:12], value[12:], associated_data).decode("utf-8")
        except Exception as exc:
            raise AlertDeviceStoreError("Stored device token could not be authenticated.") from exc

    def register(
        self, *, owner_id: str, installation_id: str, fcm_token: str
    ) -> StoredAlertDevice:
        owner, installation = self._validate_identity(owner_id, installation_id)
        if (
            not isinstance(fcm_token, str)
            or not fcm_token.strip()
            or len(fcm_token) > _MAX_TOKEN_LENGTH
            or any(ord(char) < 0x21 or ord(char) == 0x7f for char in fcm_token)
        ):
            raise ValueError("fcm_token is invalid.")
        encrypted = self._encrypt(owner, installation, fcm_token.strip())
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                """
                SELECT revoked_at_utc FROM alert_device_tokens
                WHERE owner_id = ? AND installation_id = ?
                """,
                (owner, installation),
            ).fetchone()
            if existing is None:
                active_count = connection.execute(
                    """
                    SELECT COUNT(*) FROM alert_device_tokens
                    WHERE owner_id = ? AND revoked_at_utc IS NULL
                    """,
                    (owner,),
                ).fetchone()[0]
                if active_count >= _MAX_DEVICES_PER_OWNER:
                    raise AlertDeviceQuotaExceeded(
                        "An account can register at most 10 active alert devices."
                    )
                connection.execute(
                    """
                    INSERT INTO alert_device_tokens(owner_id, installation_id, token_ciphertext)
                    VALUES (?, ?, ?)
                    """,
                    (owner, installation, encrypted),
                )
            else:
                if existing["revoked_at_utc"] is not None:
                    active_count = connection.execute(
                        """
                        SELECT COUNT(*) FROM alert_device_tokens
                        WHERE owner_id = ? AND revoked_at_utc IS NULL
                        """,
                        (owner,),
                    ).fetchone()[0]
                    if active_count >= _MAX_DEVICES_PER_OWNER:
                        raise AlertDeviceQuotaExceeded(
                            "An account can register at most 10 active alert devices."
                        )
                connection.execute(
                    """
                    UPDATE alert_device_tokens
                    SET token_ciphertext = ?, updated_at_utc = CURRENT_TIMESTAMP,
                        revoked_at_utc = NULL
                    WHERE owner_id = ? AND installation_id = ?
                    """,
                    (encrypted, owner, installation),
                )
            row = connection.execute(
                """
                SELECT installation_id, created_at_utc, updated_at_utc
                FROM alert_device_tokens WHERE owner_id = ? AND installation_id = ?
                """,
                (owner, installation),
            ).fetchone()
            connection.commit()
            return StoredAlertDevice(
                installation_id=row["installation_id"],
                created_at_utc=row["created_at_utc"],
                updated_at_utc=row["updated_at_utc"],
            )
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            raise
        finally:
            connection.close()

    def revoke(self, *, owner_id: str, installation_id: str) -> bool:
        owner, installation = self._validate_identity(owner_id, installation_id)
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                UPDATE alert_device_tokens
                SET revoked_at_utc = CURRENT_TIMESTAMP, updated_at_utc = CURRENT_TIMESTAMP
                WHERE owner_id = ? AND installation_id = ? AND revoked_at_utc IS NULL
                """,
                (owner, installation),
            )
            return cursor.rowcount == 1

    def active_count(self, *, owner_id: str) -> int:
        if not isinstance(owner_id, str) or not 1 <= len(owner_id.strip()) <= _MAX_OWNER_LENGTH:
            raise ValueError("owner_id must contain 1 to 128 characters.")
        with closing(self._connect()) as connection:
            return connection.execute(
                """
                SELECT COUNT(*) FROM alert_device_tokens
                WHERE owner_id = ? AND revoked_at_utc IS NULL
                """,
                (owner_id.strip(),),
            ).fetchone()[0]

    def token_for_delivery(self, *, owner_id: str, installation_id: str) -> str | None:
        owner, installation = self._validate_identity(owner_id, installation_id)
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT token_ciphertext FROM alert_device_tokens
                WHERE owner_id = ? AND installation_id = ? AND revoked_at_utc IS NULL
                """,
                (owner, installation),
            ).fetchone()
        if row is None:
            return None
        return self._decrypt(owner, installation, row["token_ciphertext"])
