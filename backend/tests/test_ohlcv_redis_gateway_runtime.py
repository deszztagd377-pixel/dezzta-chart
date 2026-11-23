from __future__ import annotations

import pytest

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
    snapshot_path = tmp_path / "global-snapshot.jsonl"
    metadata = source.export_global_snapshot(str(snapshot_path))
    return snapshot_path, metadata


def test_gateway_runtime_factory_installs_snapshot_before_creating_tls_client(tmp_path):
    snapshot_path, metadata = _source_snapshot(tmp_path)
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
    )

    runtime = factory()
    checkpoint = runtime["replica_store"].checkpoint()

    assert checkpoint["source_id"] == metadata["source_id"]
    assert checkpoint["snapshot_generation"] == metadata["generation_id"]
    assert checkpoint["applied_cursor"] == metadata["high_water"]
    assert runtime["snapshot_evidence"]["snapshot_sha256"] == metadata["sha256"]
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
    snapshot_path, metadata = _source_snapshot(tmp_path)
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
        production=True,
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
    snapshot_path, metadata = _source_snapshot(tmp_path)
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
                "APP_ENV": "production",
                "OHLCV_REDIS_GATEWAY_URL": "redis://gateway:secret@redis.example:6379/0",
                "OHLCV_REDIS_REPLICA_DATABASE_PATH": "/var/lib/dezzta/replica.sqlite",
                "OHLCV_REDIS_SOURCE_ID": "source-1",
                "OHLCV_REDIS_GATEWAY_CONSUMER_NAME": "gateway-1",
            },
        )


def test_gateway_runtime_rejects_callback_digest_not_bound_to_durable_checkpoint(tmp_path):
    snapshot_path, metadata = _source_snapshot(tmp_path)
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
    )

    with pytest.raises(RuntimeError, match="does not match"):
        factory()
    assert clients == []
