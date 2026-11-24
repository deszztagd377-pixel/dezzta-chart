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
    assert receipt["verification_state"] == "CONTENT_ONLY_UNAUTHENTICATED"
    assert receipt["authenticated_source_id"] is None
    assert receipt["key_id"] is None
    assert receipt["attestation"] is None
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
