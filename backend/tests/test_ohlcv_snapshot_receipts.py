import hashlib
import json
import sqlite3

import pytest

from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore


def _export_empty_snapshot(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    metadata = source.export_global_snapshot(str(snapshot_path))
    return snapshot_path, metadata


def test_snapshot_install_persists_content_only_receipt_atomically(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica.sqlite3"))

    installed = replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=metadata["source_id"]
    )

    receipts = replica.snapshot_receipts()
    assert len(receipts) == 1
    receipt = receipts[0]
    assert receipt["source_id"] == metadata["source_id"]
    assert receipt["replica_id"] == replica.replica_id()
    assert receipt["generation_id"] == metadata["generation_id"]
    assert receipt["high_water_cursor"] == metadata["high_water"]
    assert receipt["canonical_sha256"] == metadata["sha256"]
    assert receipt["row_count"] == metadata["row_count"]
    assert receipt["retention_floor"] == metadata["retention_floor"]
    assert receipt["bar_retention"] == metadata["bar_retention"]
    assert receipt["verification_state"] == "CONTENT_ONLY_UNAUTHENTICATED"
    assert receipt["authenticated_source_id"] is None
    assert receipt["key_id"] is None
    assert receipt["attestation"] is None
    assert replica.snapshot_receipt(
        receipt["source_id"], receipt["replica_id"], receipt["generation_id"]
    ) == receipt
    assert replica.snapshot_receipt("missing", receipt["replica_id"], "missing") is None
    assert installed["receipt_verification_state"] == "CONTENT_ONLY_UNAUTHENTICATED"
    assert replica.checkpoint()["snapshot_sha256"] == receipt["canonical_sha256"]


def test_snapshot_receipt_retry_is_idempotent_and_does_not_duplicate(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica.sqlite3"))

    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=metadata["source_id"]
    )
    before = replica.snapshot_receipts()
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=metadata["source_id"]
    )
    after = replica.snapshot_receipts()

    assert len(after) == 1
    assert after == before


def test_snapshot_receipts_reject_update_and_delete(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    path = str(tmp_path / "replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(path)
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=metadata["source_id"]
    )

    connection = sqlite3.connect(path)
    try:
        with pytest.raises(
            sqlite3.IntegrityError, match="snapshot_receipt_is_immutable"
        ):
            connection.execute(
                """UPDATE ohlcv_replica_snapshot_receipts
                SET verification_state='TRUSTED'"""
            )
        with pytest.raises(
            sqlite3.IntegrityError, match="snapshot_receipt_is_immutable"
        ):
            connection.execute("DELETE FROM ohlcv_replica_snapshot_receipts")
    finally:
        connection.close()


def test_failed_snapshot_install_creates_no_checkpoint_or_receipt(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    damaged_path = tmp_path / "damaged.jsonl"
    damaged_path.write_bytes(snapshot_path.read_bytes() + b'{"record":"unexpected"}\n')
    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica.sqlite3"))

    with pytest.raises(ValueError):
        replica.install_global_snapshot(
            str(damaged_path), expected_source_id=metadata["source_id"]
        )

    assert replica.checkpoint() is None
    assert replica.snapshot_receipts() == []


def test_pre_receipt_checkpoint_remains_unattested_after_table_recreation(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    path = str(tmp_path / "replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(path)
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=metadata["source_id"]
    )
    checkpoint_before = replica.checkpoint()

    connection = sqlite3.connect(path)
    try:
        connection.execute("DROP TABLE ohlcv_replica_snapshot_receipts")
        connection.commit()
    finally:
        connection.close()

    migrated = SQLiteOhlcvReplicaStore(path)
    assert migrated.checkpoint() == checkpoint_before
    assert migrated.snapshot_receipts() == []



def test_checkpoint_failure_rolls_back_receipt_and_snapshot_rows(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    path = str(tmp_path / "replica.sqlite3")
    replica = SQLiteOhlcvReplicaStore(path)

    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """CREATE TRIGGER reject_replica_checkpoint
            BEFORE INSERT ON ohlcv_replica_checkpoint
            BEGIN
                SELECT RAISE(ABORT, 'injected_checkpoint_failure');
            END"""
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="injected_checkpoint_failure"):
        replica.install_global_snapshot(
            str(snapshot_path), expected_source_id=metadata["source_id"]
        )

    assert replica.checkpoint() is None
    assert replica.snapshot_receipts() == []
    assert replica.stats()["bars"] == 0


def test_same_generation_with_different_canonical_digest_is_rejected(tmp_path):
    snapshot_path, metadata = _export_empty_snapshot(tmp_path)
    original_lines = snapshot_path.read_text(encoding="utf-8").splitlines()
    header = json.loads(original_lines[0])
    manifest = json.loads(original_lines[1])

    # Re-serialize the same semantic header with different canonical bytes.
    alternate_header = json.dumps(header, sort_keys=True, separators=(", ", ": "))
    alternate_digest = hashlib.sha256((alternate_header + "\n").encode("utf-8")).hexdigest()
    manifest["sha256"] = alternate_digest
    conflicting_path = tmp_path / "same-generation-different-content.jsonl"
    conflicting_path.write_text(
        alternate_header + "\n"
        + json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    replica = SQLiteOhlcvReplicaStore(str(tmp_path / "replica.sqlite3"))
    replica.install_global_snapshot(
        str(snapshot_path), expected_source_id=metadata["source_id"]
    )
    receipt_before = replica.snapshot_receipts()
    checkpoint_before = replica.checkpoint()

    with pytest.raises(ValueError, match="conflicts with its immutable installation receipt"):
        replica.install_global_snapshot(
            str(conflicting_path), expected_source_id=metadata["source_id"]
        )

    assert replica.snapshot_receipts() == receipt_before
    assert replica.checkpoint() == checkpoint_before
