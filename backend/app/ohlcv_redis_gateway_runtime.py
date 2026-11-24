"""Fail-closed construction of a gateway replica runtime.

The owner supplies the snapshot-transfer/install callback. Production
installation additionally requires an Ed25519 manifest signature verified
against the owner-pinned keyring. This module re-verifies the persisted
immutable receipt and local checkpoint before creating Redis.
"""
from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from typing import Any

from app.ohlcv_redis_config import (
    DEFAULT_OHLCV_STREAM_KEY,
    OhlcvRedisRelayConfig,
    _parse_acl_url,
)
from app.ohlcv_redis_consumer import RedisOhlcvReplicaConsumer
from app.ohlcv import MIN_RETENTION, SUPPORTED_TIMEFRAMES
from app.snapshot_attestation import (
    validate_trusted_public_keys,
    verify_snapshot_attestation,
)
from app.ohlcv_store import (
    REPLICA_PROTOCOL_VERSION,
    REPLICA_SCHEMA_VERSION,
    SQLiteOhlcvReplicaStore,
)


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
    trusted_snapshot_keys: Mapping[str, str] | None = None,
) -> Callable[[], dict[str, Any]]:
    """Build the FastAPI replica_runtime_factory for one owner-operated gateway.

    snapshot_installer transfers the authoritative snapshot and calls
    store.install_global_snapshot(). Production store configuration requires
    a valid owner signature; returned metadata and the persisted receipt are
    checked against the durable checkpoint before Redis construction.
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
    trusted_keys = dict(trusted_snapshot_keys or {})
    validate_trusted_public_keys(trusted_keys)
    if production and not trusted_keys:
        raise ValueError(
            "Production gateway requires OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON with an owner-pinned Ed25519 key."
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
        replica_store = SQLiteOhlcvReplicaStore(
            database_path,
            trusted_snapshot_keys=trusted_keys,
            require_authenticated_snapshots=production,
        )
        redis_client = None
        try:
            install = snapshot_installer(replica_store)
            if not isinstance(install, Mapping) or install.get("status") != "installed":
                raise RuntimeError("Gateway snapshot installer did not return verified install metadata.")

            checkpoint = replica_store.checkpoint()
            if not isinstance(checkpoint, dict):
                raise RuntimeError("Gateway replica snapshot checkpoint is missing.")
            receipt = replica_store.snapshot_receipt(
                str(install.get("source_id") or ""),
                replica_store.replica_id(),
                str(install.get("generation_id") or ""),
            )
            if receipt is None:
                raise RuntimeError("Gateway snapshot immutable receipt is missing.")
            if receipt["verification_state"] == "OWNER_SIGNATURE_VERIFIED":
                try:
                    persisted_attestation = json.loads(receipt["attestation"])
                    receipt_metadata = {
                        "source_id": receipt["source_id"],
                        "generation_id": receipt["generation_id"],
                        "high_water": receipt["high_water_cursor"],
                        "retention_floor": receipt["retention_floor"],
                        "bar_retention": receipt["bar_retention"],
                        "row_count": receipt["row_count"],
                        "sha256": receipt["canonical_sha256"],
                        "format_version": receipt["manifest_format_version"],
                    }
                    verified_key_id = verify_snapshot_attestation(
                        receipt_metadata, persisted_attestation, trusted_keys,
                    )
                except Exception as exc:
                    raise RuntimeError(
                        "Persisted gateway snapshot receipt attestation is invalid."
                    ) from exc
                if (
                    receipt["authenticated_source_id"] != receipt["source_id"]
                    or receipt["key_id"] != verified_key_id
                ):
                    raise RuntimeError(
                        "Persisted gateway snapshot receipt source/key binding is invalid."
                    )
            elif production:
                raise RuntimeError("Production gateway snapshot receipt is not owner-authenticated.")
            if install.get("receipt_verification_state") != receipt["verification_state"]:
                raise RuntimeError("Gateway snapshot receipt state does not match installer metadata.")

            generation = install.get("generation_id")
            cursor = install.get("high_water")
            digest = install.get("sha256")
            replica_id = checkpoint.get("replica_id")
            retention_floor = checkpoint.get("retention_floor")
            bar_retention = checkpoint.get("bar_retention")
            schema_version = checkpoint.get("schema_version")
            protocol_version = checkpoint.get("protocol_version")
            if (
                install.get("source_id") != expected_source_id
                or not isinstance(generation, str) or not generation.strip()
                or type(cursor) is not int or cursor < 0
                or not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
                or checkpoint.get("source_id") != expected_source_id
                or checkpoint.get("snapshot_generation") != generation
                or checkpoint.get("applied_cursor") != cursor
                or checkpoint.get("snapshot_sha256") != digest
                or receipt["high_water_cursor"] != cursor
                or receipt["canonical_sha256"] != digest
                or receipt["retention_floor"] != retention_floor
                or receipt["bar_retention"] != bar_retention
                or receipt["verification_state"] != install.get("receipt_verification_state")
                or not isinstance(replica_id, str) or not replica_id.strip()
                or replica_id != replica_store.replica_id()
                or type(schema_version) is not int
                or schema_version != REPLICA_SCHEMA_VERSION
                or type(protocol_version) is not int
                or protocol_version != REPLICA_PROTOCOL_VERSION
                or type(retention_floor) is not int
                or not 0 <= retention_floor <= cursor
                or not isinstance(bar_retention, dict)
                or set(bar_retention) != set(SUPPORTED_TIMEFRAMES)
                or any(
                    type(cap) is not int or cap < MIN_RETENTION[timeframe]
                    for timeframe, cap in bar_retention.items()
                )
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
                    "authenticated_source_id": receipt["authenticated_source_id"],
                    "snapshot_generation": generation,
                    "snapshot_cursor": cursor,
                    "snapshot_sha256": digest,
                    "replica_id": checkpoint["replica_id"],
                    "verification_state": receipt["verification_state"],
                    "key_id": receipt["key_id"],
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
    raw_trusted_keys = source.get("OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON", "").strip()
    if raw_trusted_keys:
        try:
            trusted_snapshot_keys = json.loads(raw_trusted_keys)
        except json.JSONDecodeError as exc:
            raise ValueError("OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON must be valid JSON.") from exc
        if not isinstance(trusted_snapshot_keys, dict):
            raise ValueError("OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON must be a JSON object.")
    else:
        trusted_snapshot_keys = {}

    return build_gateway_replica_runtime_factory(
        redis_url=source.get("OHLCV_REDIS_GATEWAY_URL", ""),
        database_path=source.get("OHLCV_REDIS_REPLICA_DATABASE_PATH", ""),
        expected_source_id=source.get("OHLCV_REDIS_SOURCE_ID", ""),
        consumer_name=source.get("OHLCV_REDIS_GATEWAY_CONSUMER_NAME", ""),
        snapshot_installer=snapshot_installer,
        stream_key=source.get("OHLCV_REDIS_STREAM_KEY", DEFAULT_OHLCV_STREAM_KEY),
        production=source.get("APP_ENV", "development").strip().lower() == "production",
        redis_client_factory=redis_client_factory,
        trusted_snapshot_keys=trusted_snapshot_keys,
    )
