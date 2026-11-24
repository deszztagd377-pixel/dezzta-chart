import base64
import hashlib
import os
from decimal import Decimal

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.ohlcv import OhlcvBar
from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore
from app.snapshot_attestation import (
    canonical_snapshot_attestation_payload,
    export_raw_public_key,
    load_ed25519_private_key,
    load_snapshot_signing_key_from_environment,
    sign_snapshot_attestation,
    validate_trusted_public_keys,
    verify_snapshot_attestation,
)


def _metadata():
    return {
        "source_id": "source-a",
        "generation_id": "generation-1",
        "high_water": 12,
        "retention_floor": 2,
        "bar_retention": {"1m": 100, "5m": 200},
        "row_count": 2,
        "sha256": hashlib.sha256(b"snapshot").hexdigest(),
        "format_version": 2,
    }


def test_ed25519_snapshot_attestation_round_trip_and_deterministic_payload():
    private_key = Ed25519PrivateKey.generate()
    key_id = "owner-source-2026-11"
    metadata = _metadata()

    first_payload = canonical_snapshot_attestation_payload(metadata)
    second_payload = canonical_snapshot_attestation_payload(dict(reversed(list(metadata.items()))))
    assert first_payload == second_payload

    attestation = sign_snapshot_attestation(
        metadata, key_id=key_id, private_key=private_key,
    )
    trusted = {key_id: export_raw_public_key(private_key)}
    assert verify_snapshot_attestation(metadata, attestation, trusted) == key_id


def test_ed25519_snapshot_attestation_rejects_tampered_metadata_and_unknown_key():
    private_key = Ed25519PrivateKey.generate()
    attestation = sign_snapshot_attestation(
        _metadata(), key_id="trusted-key", private_key=private_key,
    )
    trusted = {"trusted-key": export_raw_public_key(private_key)}

    changed = {**_metadata(), "high_water": 13}
    with pytest.raises(ValueError, match="verification failed"):
        verify_snapshot_attestation(changed, attestation, trusted)

    with pytest.raises(ValueError, match="not trusted"):
        verify_snapshot_attestation(_metadata(), attestation, {"other-key": export_raw_public_key(private_key)})


def test_trusted_keyring_rejects_invalid_key_ids_and_public_key_bytes():
    with pytest.raises(ValueError, match="stable identifiers"):
        validate_trusted_public_keys({"invalid key": base64.b64encode(b"x" * 32).decode()})
    with pytest.raises(ValueError, match="exactly 32 raw bytes"):
        validate_trusted_public_keys({"key-1": base64.b64encode(b"x" * 31).decode()})


def test_signed_snapshot_verification_and_replica_receipt_are_owner_authenticated(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "signed-source.sqlite3"))
    assert source.apply(OhlcvBar(
        dataset="GLBX.MDP3",
        publisher_id=1,
        instrument_id=123,
        raw_symbol="ESZ6",
        timeframe="1m",
        ts_start_ns=0,
        open=Decimal("100"),
        high=Decimal("102"),
        low=Decimal("99"),
        close=Decimal("101"),
        volume=Decimal("12"),
        ts_event_ns=1,
        ts_received_ns=2,
        sequence=1,
    )) == "inserted"
    private_key = Ed25519PrivateKey.generate()
    key_id = "owner-source-key"
    trusted = {key_id: export_raw_public_key(private_key)}
    snapshot_path = tmp_path / "signed.snapshot.jsonl"

    exported = source.export_global_snapshot(
        str(snapshot_path), signing_key=private_key, signing_key_id=key_id,
    )
    verified = SQLiteOhlcvStore.verify_global_snapshot(
        str(snapshot_path), trusted_public_keys=trusted, require_authentication=True,
    )
    assert exported["signature_status"] == "SIGNED"
    assert verified["verification_state"] == "OWNER_SIGNATURE_VERIFIED"
    assert verified["key_id"] == key_id

    replica = SQLiteOhlcvReplicaStore(
        str(tmp_path / "signed-replica.sqlite3"),
        trusted_snapshot_keys=trusted,
        require_authenticated_snapshots=True,
    )
    installed = replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=exported["source_id"],
    )
    receipt = replica.snapshot_receipts()[0]
    assert installed["receipt_verification_state"] == "OWNER_SIGNATURE_VERIFIED"
    assert receipt["verification_state"] == "OWNER_SIGNATURE_VERIFIED"
    assert receipt["authenticated_source_id"] == exported["source_id"]
    assert receipt["key_id"] == key_id
    assert receipt["attestation"] is not None


def test_authenticated_snapshot_install_rejects_unsigned_snapshot_before_checkpoint(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "unsigned-source.sqlite3"))
    snapshot_path = tmp_path / "unsigned.snapshot.jsonl"
    metadata = source.export_global_snapshot(str(snapshot_path))
    private_key = Ed25519PrivateKey.generate()
    trusted = {"owner-key": export_raw_public_key(private_key)}
    replica = SQLiteOhlcvReplicaStore(
        str(tmp_path / "unsigned-replica.sqlite3"),
        trusted_snapshot_keys=trusted,
        require_authenticated_snapshots=True,
    )

    with pytest.raises(ValueError, match="trusted owner signature"):
        replica.install_global_snapshot(
            str(snapshot_path), expected_source_id=metadata["source_id"],
        )
    assert replica.checkpoint() is None
    assert replica.snapshot_receipts() == []


def test_receipt_table_migration_preserves_content_only_history(tmp_path):
    path = str(tmp_path / "receipt-migration.sqlite3")
    store = SQLiteOhlcvReplicaStore(path)
    connection = store._connect()
    try:
        connection.execute("DROP TRIGGER IF EXISTS ohlcv_replica_snapshot_receipts_no_update")
        connection.execute("DROP TRIGGER IF EXISTS ohlcv_replica_snapshot_receipts_no_delete")
        connection.execute("DROP TABLE ohlcv_replica_snapshot_receipts")
        connection.execute(
            """CREATE TABLE ohlcv_replica_snapshot_receipts (
                source_id TEXT NOT NULL,
                replica_id TEXT NOT NULL,
                generation_id TEXT NOT NULL,
                high_water_cursor INTEGER NOT NULL CHECK(high_water_cursor >= 0),
                canonical_sha256 TEXT NOT NULL CHECK(length(canonical_sha256) = 64),
                manifest_format_version INTEGER NOT NULL CHECK(manifest_format_version >= 1),
                row_count INTEGER NOT NULL CHECK(row_count >= 0),
                verification_state TEXT NOT NULL
                    CHECK(verification_state = 'CONTENT_ONLY_UNAUTHENTICATED'),
                authenticated_source_id TEXT,
                key_id TEXT,
                attestation BLOB,
                installed_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                installer_protocol_version INTEGER NOT NULL,
                PRIMARY KEY(source_id, replica_id, generation_id)
            )"""
        )
        connection.execute(
            """INSERT INTO ohlcv_replica_snapshot_receipts(
                source_id,replica_id,generation_id,high_water_cursor,
                canonical_sha256,manifest_format_version,row_count,
                verification_state,installer_protocol_version
            ) VALUES ('source-a','replica-a','generation-a',0,?,2,0,
                'CONTENT_ONLY_UNAUTHENTICATED',3)""",
            (hashlib.sha256(b"legacy").hexdigest(),),
        )
        connection.commit()
    finally:
        connection.close()

    migrated = SQLiteOhlcvReplicaStore(path)
    receipts = migrated.snapshot_receipts()
    assert len(receipts) == 1
    assert receipts[0]["verification_state"] == "CONTENT_ONLY_UNAUTHENTICATED"
    assert receipts[0]["authenticated_source_id"] is None
    assert receipts[0]["key_id"] is None



def test_source_signing_key_environment_loads_owner_only_pem(tmp_path):
    private_key = Ed25519PrivateKey.generate()
    key_path = tmp_path / "owner.private.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    key_path.chmod(0o600)

    loaded, key_id = load_snapshot_signing_key_from_environment({
        "OHLCV_SNAPSHOT_SIGNING_KEY_FILE": str(key_path),
        "OHLCV_SNAPSHOT_SIGNING_KEY_ID": "owner-key-1",
    })
    assert key_id == "owner-key-1"
    assert export_raw_public_key(loaded) == export_raw_public_key(private_key)

    with pytest.raises(ValueError, match="configured together"):
        load_snapshot_signing_key_from_environment({
            "OHLCV_SNAPSHOT_SIGNING_KEY_FILE": str(key_path),
        })


def test_source_signing_key_loader_rejects_group_or_world_permissions(tmp_path):
    private_key = Ed25519PrivateKey.generate()
    key_path = tmp_path / "insecure.private.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    key_path.chmod(0o644)

    with pytest.raises(ValueError, match="owner-only"):
        load_ed25519_private_key(str(key_path))
