from __future__ import annotations

from decimal import Decimal
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.snapshot_attestation import export_raw_public_key
from app.ohlcv import OhlcvBar

from app import ohlcv_redis_gateway_runtime as gateway_runtime
from app.ohlcv_redis_gateway_runtime import (
    build_gateway_replica_runtime_factory,
    gateway_replica_runtime_factory_from_environment,
)
from app.ohlcv_store import SQLiteOhlcvStore


class FakeRedis:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def _snapshot_installer(snapshot_path, source_id):
    def install(store):
        return store.install_global_snapshot(
            str(snapshot_path),
            expected_source_id=source_id,
        )
    return install


def _source_snapshot(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite"))
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
    snapshot_path = tmp_path / "global-snapshot.jsonl"
    private_key = Ed25519PrivateKey.generate()
    key_id = "test-source-key"
    metadata = source.export_global_snapshot(
        str(snapshot_path), signing_key=private_key, signing_key_id=key_id,
    )
    return snapshot_path, metadata, {key_id: export_raw_public_key(private_key)}


def test_gateway_runtime_factory_installs_snapshot_before_creating_tls_client(tmp_path):
    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    captured = {}
    client = FakeRedis()

    def redis_factory(url, **options):
        captured["url"] = url
        captured["options"] = options
        return client

    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:gateway-secret@redis.example:6380/0",
        database_path=str(tmp_path / "gateway.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-process-1",
        snapshot_installer=_snapshot_installer(snapshot_path, metadata["source_id"]),
        production=True,
        redis_client_factory=redis_factory,
        trusted_snapshot_keys=trusted_keys,
    )

    runtime = factory()
    checkpoint = runtime["replica_store"].checkpoint()

    assert checkpoint["source_id"] == metadata["source_id"]
    assert checkpoint["snapshot_generation"] == metadata["generation_id"]
    assert checkpoint["applied_cursor"] == metadata["high_water"]
    assert runtime["snapshot_evidence"]["snapshot_sha256"] == metadata["sha256"]
    assert runtime["snapshot_evidence"]["authenticated_source_id"] == metadata["source_id"]
    assert runtime["snapshot_evidence"]["replica_id"] == checkpoint["replica_id"]
    assert runtime["snapshot_evidence"]["verification_state"] == "OWNER_SIGNATURE_VERIFIED"
    assert runtime["snapshot_evidence"]["key_id"] == "test-source-key"
    assert runtime["consumer"].replica_store is runtime["replica_store"]
    assert runtime["consumer"].redis is client
    assert runtime["consumer"].stream_key == runtime["stream_key"]
    assert runtime["consumer"].block_ms == 1_000
    assert captured["url"].startswith("rediss://")
    assert captured["options"]["ssl_cert_reqs"] == "required"
    assert captured["options"]["ssl_check_hostname"] is True
    assert captured["options"]["socket_connect_timeout"] == 3.0
    assert captured["options"]["socket_timeout"] == 5.0


def test_gateway_runtime_factory_rejects_source_mismatch_before_redis_creation(tmp_path):
    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    clients = []

    def redis_factory(url, **options):
        clients.append(url)
        return FakeRedis()

    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "gateway.sqlite"),
        expected_source_id="unexpected-source",
        consumer_name="gateway-process-1",
        snapshot_installer=_snapshot_installer(snapshot_path, metadata["source_id"]),
        production=True,
        redis_client_factory=redis_factory,
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(RuntimeError, match="does not match"):
        factory()
    assert clients == []


def test_gateway_runtime_factory_rejects_unverified_installer_result(tmp_path):
    clients = []
    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "gateway.sqlite"),
        expected_source_id="source-1",
        consumer_name="gateway-process-1",
        snapshot_installer=lambda store: {"status": "installed"},
        production=False,
        redis_client_factory=lambda url, **options: clients.append(url),
    )
    with pytest.raises(RuntimeError, match="checkpoint is missing"):
        factory()
    assert clients == []


def test_gateway_runtime_factory_rejects_plaintext_production_redis_before_install(tmp_path):
    called = []
    with pytest.raises(ValueError, match="rediss:// TLS"):
        build_gateway_replica_runtime_factory(
            redis_url="redis://gateway:secret@redis.example:6379/0",
            database_path=str(tmp_path / "gateway.sqlite"),
            expected_source_id="source-1",
            consumer_name="gateway-process-1",
            snapshot_installer=lambda store: called.append(store),
            production=True,
        )
    assert called == []


def test_gateway_runtime_factory_closes_client_if_consumer_construction_fails(tmp_path, monkeypatch):
    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    client = FakeRedis()

    def fail_consumer(*args, **kwargs):
        raise RuntimeError("simulated consumer construction failure")

    monkeypatch.setattr(gateway_runtime, "RedisOhlcvReplicaConsumer", fail_consumer)
    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "gateway.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-process-1",
        snapshot_installer=_snapshot_installer(snapshot_path, metadata["source_id"]),
        production=True,
        redis_client_factory=lambda url, **options: client,
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(RuntimeError, match="simulated consumer construction failure"):
        factory()
    assert client.closed is True


def test_gateway_environment_factory_is_opt_in_and_requires_host_evidence():
    assert gateway_replica_runtime_factory_from_environment(
        snapshot_installer=lambda store: {},
        environ={},
    ) is None

    with pytest.raises(ValueError, match="rediss:// TLS"):
        gateway_replica_runtime_factory_from_environment(
            snapshot_installer=lambda store: {},
            environ={
                "OHLCV_REDIS_ENABLED": "true",
                "OHLCV_REDIS_ROLE": "gateway",
                "APP_ENV": "production",
                "OHLCV_REDIS_GATEWAY_URL": "redis://gateway:secret@redis.example:6379/0",
                "OHLCV_REDIS_REPLICA_DATABASE_PATH": "/var/lib/dezzta/replica.sqlite",
                "OHLCV_REDIS_SOURCE_ID": "source-1",
                "OHLCV_REDIS_GATEWAY_CONSUMER_NAME": "gateway-1",
            },
        )


def test_gateway_runtime_rejects_callback_digest_not_bound_to_durable_checkpoint(tmp_path):
    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    clients = []

    def installer_with_forged_digest(store):
        installed = store.install_global_snapshot(
            str(snapshot_path),
            expected_source_id=metadata["source_id"],
        )
        return {**installed, "sha256": "0" * 64}

    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "gateway-forged-digest.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-process-1",
        snapshot_installer=installer_with_forged_digest,
        production=True,
        redis_client_factory=lambda url, **options: clients.append(url),
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(RuntimeError, match="does not match"):
        factory()
    assert clients == []



@pytest.mark.parametrize(
    ("checkpoint_change", "expected_fragment"),
    [
        ({"replica_id": "forged-replica"}, "does not match"),
        ({"schema_version": 999}, "does not match"),
        ({"protocol_version": 999}, "does not match"),
        ({"retention_floor": -1}, "does not match"),
        ({"retention_floor": 1}, "does not match"),
        ({"bar_retention": {}}, "does not match"),
    ],
)
def test_gateway_runtime_rejects_inconsistent_checkpoint_before_redis_creation(
    tmp_path, checkpoint_change, expected_fragment,
):
    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    clients = []

    def installer_with_corrupt_checkpoint(store):
        installed = store.install_global_snapshot(
            str(snapshot_path),
            expected_source_id=metadata["source_id"],
        )
        checkpoint = store.checkpoint()
        checkpoint.update(checkpoint_change)
        store.checkpoint = lambda: checkpoint
        return installed

    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "gateway-inconsistent-checkpoint.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-process-1",
        snapshot_installer=installer_with_corrupt_checkpoint,
        production=True,
        redis_client_factory=lambda url, **options: clients.append(url),
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(RuntimeError, match=expected_fragment):
        factory()
    assert clients == []


def test_production_gateway_requires_an_owner_pinned_snapshot_key():
    with pytest.raises(ValueError, match="requires OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON"):
        build_gateway_replica_runtime_factory(
            redis_url="rediss://gateway:secret@redis.example:6380/0",
            database_path="/tmp/dezzta-missing-trust.sqlite",
            expected_source_id="source-1",
            consumer_name="gateway-1",
            snapshot_installer=lambda store: {},
            production=True,
            redis_client_factory=lambda url, **options: FakeRedis(),
        )


def test_production_gateway_rejects_unsigned_snapshot_before_redis_creation(tmp_path):
    source = SQLiteOhlcvStore(str(tmp_path / "unsigned-source.sqlite"))
    snapshot_path = tmp_path / "unsigned.snapshot.jsonl"
    metadata = source.export_global_snapshot(str(snapshot_path))
    private_key = Ed25519PrivateKey.generate()
    trusted_keys = {"test-source-key": export_raw_public_key(private_key)}
    clients = []

    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "unsigned-replica.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-1",
        snapshot_installer=_snapshot_installer(snapshot_path, metadata["source_id"]),
        production=True,
        redis_client_factory=lambda url, **options: clients.append(url),
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(ValueError, match="trusted owner signature"):
        factory()
    assert clients == []



def test_gateway_environment_factory_parses_ed25519_public_key_allowlist(tmp_path):
    import json

    private_key = Ed25519PrivateKey.generate()
    trusted_keys = {"test-source-key": export_raw_public_key(private_key)}
    factory = gateway_replica_runtime_factory_from_environment(
        snapshot_installer=lambda store: {},
        environ={
            "OHLCV_REDIS_ENABLED": "true",
            "APP_ENV": "production",
            "OHLCV_REDIS_GATEWAY_URL": "rediss://gateway:secret@redis.example:6380/0",
            "OHLCV_REDIS_REPLICA_DATABASE_PATH": str(tmp_path / "gateway.sqlite"),
            "OHLCV_REDIS_SOURCE_ID": "source-1",
            "OHLCV_REDIS_GATEWAY_CONSUMER_NAME": "gateway-1",
            "OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON": json.dumps(trusted_keys),
        },
        redis_client_factory=lambda url, **options: FakeRedis(),
    )
    assert callable(factory)


def test_production_gateway_rejects_invalid_snapshot_signature_before_redis_creation(tmp_path):
    import json

    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    lines = snapshot_path.read_text(encoding="utf-8").splitlines()
    manifest = json.loads(lines[-1])
    signature = manifest["attestation"]["signature"]
    manifest["attestation"]["signature"] = ("A" if signature[0] != "A" else "B") + signature[1:]
    snapshot_path.write_text(
        lines[0] + "\n"
        + "\n".join(lines[1:-1]) + ("\n" if len(lines) > 2 else "")
        + json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    clients = []
    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "invalid-signature-replica.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-1",
        snapshot_installer=_snapshot_installer(snapshot_path, metadata["source_id"]),
        production=True,
        redis_client_factory=lambda url, **options: clients.append(url),
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(ValueError, match="attestation verification failed"):
        factory()
    assert clients == []



def test_gateway_runtime_reverifies_persisted_receipt_signature_before_redis(tmp_path):
    import sqlite3

    snapshot_path, metadata, trusted_keys = _source_snapshot(tmp_path)
    clients = []

    def installer_then_tamper_receipt(store):
        installed = store.install_global_snapshot(
            str(snapshot_path), expected_source_id=metadata["source_id"],
        )
        with sqlite3.connect(store.database_path) as db:
            db.execute(
                "DROP TRIGGER ohlcv_replica_snapshot_receipts_no_update"
            )
            db.execute(
                """UPDATE ohlcv_replica_snapshot_receipts
                SET attestation=? WHERE source_id=?""",
                (
                    b'{"algorithm":"Ed25519","key_id":"test-source-key","signature":"AAAA"}',
                    metadata["source_id"],
                ),
            )
        return installed

    factory = build_gateway_replica_runtime_factory(
        redis_url="rediss://gateway:secret@redis.example:6380/0",
        database_path=str(tmp_path / "tampered-receipt.sqlite"),
        expected_source_id=metadata["source_id"],
        consumer_name="gateway-1",
        snapshot_installer=installer_then_tamper_receipt,
        production=True,
        redis_client_factory=lambda url, **options: clients.append(url),
        trusted_snapshot_keys=trusted_keys,
    )

    with pytest.raises(RuntimeError, match="Persisted gateway snapshot receipt attestation is invalid"):
        factory()
    assert clients == []
