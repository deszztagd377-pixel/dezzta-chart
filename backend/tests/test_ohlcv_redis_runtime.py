from __future__ import annotations

import pytest

from app.ohlcv_redis_publisher import SQLiteOhlcvPublisherCheckpoint
from app.ohlcv_redis_runtime import build_source_publisher_runtime_factory, source_publisher_runtime_factory_from_environment
from app.ohlcv_store import SQLiteOhlcvStore


class FakeRedis:
    def __init__(self):
        self.closed = False

    def ping(self):
        return True

    def close(self):
        self.closed = True


def make_store(tmp_path):
    return SQLiteOhlcvStore(str(tmp_path / "source-runtime.sqlite3"))


def snapshot_evidence(store, checkpoint, *, bad_gateway=False, bad_digest=False):
    required = ["gateway-a", "gateway-b"]
    snapshot_sha256 = "a" * 64
    installations = {}
    for gateway_id in required:
        installations[gateway_id] = {
            "source_id": store.source_id(),
            "stream_key": "dezzta:market-data:ohlcv:v1",
            "snapshot_generation": "snapshot-generation-0007",
            "snapshot_cursor": checkpoint["published_cursor"] + (1 if bad_gateway and gateway_id == "gateway-b" else 0),
            "snapshot_sha256": ("b" * 64) if bad_digest and gateway_id == "gateway-b" else snapshot_sha256,
        }
    return {
        "source_id": store.source_id(),
        "stream_key": "dezzta:market-data:ohlcv:v1",
        "snapshot_generation": "snapshot-generation-0007",
        "snapshot_cursor": checkpoint["published_cursor"],
        "snapshot_sha256": snapshot_sha256,
        "required_gateway_ids": required,
        "gateway_installations": installations,
    }


def test_factory_fails_closed_without_checkpoint_before_creating_redis(tmp_path):
    store = make_store(tmp_path)
    created = []
    factory = build_source_publisher_runtime_factory(
        redis_url="rediss://publisher:secret@redis.example:6380/0",
        owner="source-host-01", production=True,
        snapshot_verifier=lambda source, state: {},
        redis_client_factory=lambda *args, **kwargs: created.append(True),
    )
    with pytest.raises(RuntimeError, match="checkpoint is missing"):
        factory(store)
    assert created == []


def test_factory_rejects_gateway_snapshot_cursor_mismatch_before_redis_creation(tmp_path):
    store = make_store(tmp_path)
    checkpoint = SQLiteOhlcvPublisherCheckpoint(store)
    checkpoint_state = checkpoint.initialize_from_snapshot(0, now_ms=1000)
    created = []
    factory = build_source_publisher_runtime_factory(
        redis_url="rediss://publisher:secret@redis.example:6380/0",
        owner="source-host-01", production=True,
        snapshot_verifier=lambda source, state: snapshot_evidence(source, state, bad_gateway=True),
        redis_client_factory=lambda *args, **kwargs: created.append(True),
    )
    with pytest.raises(RuntimeError, match="gateway snapshot receipt"):
        factory(store)
    assert created == []
    assert checkpoint.state()["published_cursor"] == checkpoint_state["published_cursor"]


def test_factory_rejects_gateway_snapshot_digest_mismatch_before_redis_creation(tmp_path):
    store = make_store(tmp_path)
    checkpoint = SQLiteOhlcvPublisherCheckpoint(store)
    checkpoint.initialize_from_snapshot(0, now_ms=1000)
    created = []
    factory = build_source_publisher_runtime_factory(
        redis_url="rediss://publisher:secret@redis.example:6380/0",
        owner="source-host-01", production=True,
        snapshot_verifier=lambda source, state: snapshot_evidence(source, state, bad_digest=True),
        redis_client_factory=lambda *args, **kwargs: created.append(True),
    )
    with pytest.raises(RuntimeError, match="SHA-256"):
        factory(store)
    assert created == []


def test_factory_rejects_invalid_manifest_digest_before_redis_creation(tmp_path):
    store = make_store(tmp_path)
    checkpoint = SQLiteOhlcvPublisherCheckpoint(store)
    checkpoint.initialize_from_snapshot(0, now_ms=1000)
    created = []

    def invalid_manifest(source, state):
        evidence = snapshot_evidence(source, state)
        evidence["snapshot_sha256"] = "not-a-sha256"
        return evidence

    factory = build_source_publisher_runtime_factory(
        redis_url="rediss://publisher:secret@redis.example:6380/0",
        owner="source-host-01", production=True,
        snapshot_verifier=invalid_manifest,
        redis_client_factory=lambda *args, **kwargs: created.append(True),
    )
    with pytest.raises(RuntimeError, match="SHA-256"):
        factory(store)
    assert created == []


def test_factory_creates_dedicated_tls_client_after_all_gateway_receipts_match(tmp_path):
    store = make_store(tmp_path)
    checkpoint = SQLiteOhlcvPublisherCheckpoint(store)
    checkpoint.initialize_from_snapshot(0, now_ms=1000)
    redis_client = FakeRedis()
    captured = {}

    def redis_factory(url, **options):
        captured.update(url=url, options=options)
        return redis_client

    factory = build_source_publisher_runtime_factory(
        redis_url="rediss://publisher:secret@redis.example:6380/0",
        owner="source-host-01", production=True,
        snapshot_verifier=lambda source, state: snapshot_evidence(source, state),
        redis_client_factory=redis_factory,
    )
    runtime = factory(store)
    assert runtime["redis_client"] is redis_client
    assert runtime["publisher"].source_store is store
    assert runtime["snapshot_evidence"]["verified_gateway_count"] == 2
    assert runtime["snapshot_evidence"]["snapshot_cursor"] == 0
    assert runtime["snapshot_evidence"]["snapshot_sha256"] == "a" * 64
    assert captured["options"]["socket_connect_timeout"] == 3.0
    assert captured["options"]["socket_timeout"] == 5.0
    assert captured["options"]["ssl_cert_reqs"] == "required"
    assert captured["options"]["ssl_check_hostname"] is True


def test_production_factory_rejects_plaintext_redis():
    with pytest.raises(ValueError, match="must use rediss:// TLS"):
        build_source_publisher_runtime_factory(
            redis_url="redis://publisher:secret@redis.example:6379/0",
            owner="source-host-01", production=True,
            snapshot_verifier=lambda source, state: {},
            redis_client_factory=lambda *args, **kwargs: FakeRedis(),
        )


def test_environment_factory_is_opt_in_and_production_requires_tls():
    assert source_publisher_runtime_factory_from_environment(
        snapshot_verifier=lambda source, state: {},
        environ={"OHLCV_REDIS_ENABLED": "false"},
    ) is None
    with pytest.raises(ValueError, match="must use rediss:// TLS"):
        source_publisher_runtime_factory_from_environment(
            snapshot_verifier=lambda source, state: {},
            environ={
                "APP_ENV": "production", "OHLCV_REDIS_ENABLED": "true",
                "OHLCV_REDIS_PUBLISHER_OWNER": "source-host-01",
                "OHLCV_REDIS_PUBLISH_URL": "redis://publisher:secret@redis.example:6379/0",
            },
        )
