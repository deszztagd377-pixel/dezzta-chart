"""Fail-closed construction of a gateway replica runtime.

The owner supplies the authenticated snapshot-transfer/install callback. This
module verifies the installed snapshot metadata against the durable local
checkpoint before creating a Redis client or consumer. It does not invent
snapshot trust, remote receipts, or production credentials.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from app.ohlcv_redis_config import (
    DEFAULT_OHLCV_STREAM_KEY,
    OhlcvRedisRelayConfig,
    _parse_acl_url,
)
from app.ohlcv_redis_consumer import RedisOhlcvReplicaConsumer
from app.ohlcv_store import SQLiteOhlcvReplicaStore


def build_gateway_replica_runtime_factory(
    *,
    redis_url: str,
    database_path: str,
    expected_source_id: str,
    consumer_name: str,
    snapshot_installer: Callable[[SQLiteOhlcvReplicaStore], Mapping[str, Any]],
    stream_key: str = DEFAULT_OHLCV_STREAM_KEY,
    production: bool = False,
    redis_client_factory: Callable[..., Any] | None = None,
) -> Callable[[], dict[str, Any]]:
    """Build the FastAPI replica_runtime_factory for one owner-operated gateway.

    snapshot_installer must transfer the authoritative snapshot through the
    owner's authenticated mechanism and call store.install_global_snapshot().
    Its returned install metadata is checked against the durable checkpoint.
    """
    if type(production) is not bool:
        raise ValueError("production must be a boolean.")
    if not isinstance(database_path, str) or not database_path.strip():
        raise ValueError("A persistent gateway replica database path is required.")
    if not isinstance(expected_source_id, str) or not expected_source_id.strip():
        raise ValueError("A configured authoritative source ID is required.")
    if len(expected_source_id) > 128:
        raise ValueError("The authoritative source ID is too long.")
    if not isinstance(consumer_name, str) or not consumer_name.strip() or len(consumer_name) > 128:
        raise ValueError("A stable gateway consumer name is required.")
    if not callable(snapshot_installer):
        raise ValueError("An authenticated snapshot installer callback is required.")

    OhlcvRedisRelayConfig(stream_key=stream_key)
    _parse_acl_url(
        redis_url,
        name="OHLCV_REDIS_GATEWAY_URL",
        production=production,
    )

    options: dict[str, Any] = {
        "decode_responses": True,
        "socket_connect_timeout": 3.0,
        "socket_timeout": 5.0,
        "health_check_interval": 15,
        "retry_on_timeout": False,
    }
    if redis_url.strip().lower().startswith("rediss://"):
        options.update(ssl_cert_reqs="required", ssl_check_hostname=True)

    def runtime_factory() -> dict[str, Any]:
        replica_store = SQLiteOhlcvReplicaStore(database_path)
        redis_client = None
        try:
            install = snapshot_installer(replica_store)
            if not isinstance(install, Mapping) or install.get("status") != "installed":
                raise RuntimeError("Gateway snapshot installer did not return verified install metadata.")

            checkpoint = replica_store.checkpoint()
            if not isinstance(checkpoint, dict):
                raise RuntimeError("Gateway replica snapshot checkpoint is missing.")

            generation = install.get("generation_id")
            cursor = install.get("high_water")
            digest = install.get("sha256")
            if (
                install.get("source_id") != expected_source_id
                or not isinstance(generation, str) or not generation.strip()
                or type(cursor) is not int or cursor < 0
                or not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
                or checkpoint.get("source_id") != expected_source_id
                or checkpoint.get("snapshot_generation") != generation
                or checkpoint.get("applied_cursor") != cursor
            ):
                raise RuntimeError("Installed gateway snapshot metadata does not match its durable checkpoint.")

            if redis_client_factory is None:
                import redis
                redis_client = redis.Redis.from_url(redis_url, **options)
            else:
                redis_client = redis_client_factory(redis_url, **options)
            if redis_client is None:
                raise RuntimeError("Gateway Redis client factory returned no client.")

            consumer = RedisOhlcvReplicaConsumer(
                redis_client,
                replica_store,
                stream_key=stream_key,
                consumer_name=consumer_name,
                block_ms=1_000,
            )
            return {
                "replica_store": replica_store,
                "consumer": consumer,
                "redis_client": redis_client,
                "stream_key": stream_key,
                "snapshot_evidence": {
                    "source_id": expected_source_id,
                    "snapshot_generation": generation,
                    "snapshot_cursor": cursor,
                    "snapshot_sha256": digest,
                    "replica_id": checkpoint["replica_id"],
                },
            }
        except Exception:
            close = getattr(redis_client, "close", None)
            if callable(close):
                close()
            raise

    return runtime_factory


def gateway_replica_runtime_factory_from_environment(
    *,
    snapshot_installer: Callable[[SQLiteOhlcvReplicaStore], Mapping[str, Any]],
    environ: Mapping[str, str] | None = None,
    redis_client_factory: Callable[..., Any] | None = None,
) -> Callable[[], dict[str, Any]] | None:
    """Create a gateway factory only when OHLCV_REDIS_ENABLED is explicit."""
    source = os.environ if environ is None else environ
    enabled = source.get("OHLCV_REDIS_ENABLED", "false").strip().lower()
    if enabled in {"", "0", "false", "no", "off"}:
        return None
    if enabled not in {"1", "true", "yes", "on"}:
        raise ValueError("OHLCV_REDIS_ENABLED must be a boolean value.")
    return build_gateway_replica_runtime_factory(
        redis_url=source.get("OHLCV_REDIS_GATEWAY_URL", ""),
        database_path=source.get("OHLCV_REDIS_REPLICA_DATABASE_PATH", ""),
        expected_source_id=source.get("OHLCV_REDIS_SOURCE_ID", ""),
        consumer_name=source.get("OHLCV_REDIS_GATEWAY_CONSUMER_NAME", ""),
        snapshot_installer=snapshot_installer,
        stream_key=source.get("OHLCV_REDIS_STREAM_KEY", DEFAULT_OHLCV_STREAM_KEY),
        production=source.get("APP_ENV", "development").strip().lower() == "production",
        redis_client_factory=redis_client_factory,
    )
