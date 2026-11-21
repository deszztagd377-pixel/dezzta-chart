"""Fail-closed construction of the dedicated source OHLCV publisher runtime."""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any
from urllib.parse import urlsplit

from app.ohlcv_redis_config import DEFAULT_OHLCV_STREAM_KEY, OhlcvRedisRelayConfig, _parse_acl_url
from app.ohlcv_redis_publisher import RedisOhlcvPublisher, SQLiteOhlcvPublisherCheckpoint
from app.ohlcv_store import SQLiteOhlcvStore


def _validate_snapshot_evidence(
    evidence: object, *, source_id: str, checkpoint_cursor: int, stream_key: str,
) -> dict[str, Any]:
    """Validate manifest plus one matching installation receipt per required gateway.

    The owner-host callback must read authoritative manifest/receipt data.
    This function validates the evidence contract; it cannot probe remote hosts.
    """
    if not isinstance(evidence, Mapping):
        raise RuntimeError("A verified global snapshot manifest is required.")
    generation = evidence.get("snapshot_generation")
    cursor = evidence.get("snapshot_cursor")
    required = evidence.get("required_gateway_ids")
    installations = evidence.get("gateway_installations")
    if (
        not isinstance(generation, str) or not generation.strip()
        or evidence.get("source_id") != source_id
        or evidence.get("stream_key") != stream_key
        or type(cursor) is not int or cursor != checkpoint_cursor
        or not isinstance(required, (list, tuple))
        or not isinstance(installations, Mapping)
    ):
        raise RuntimeError("Snapshot evidence does not match the publisher source and checkpoint.")
    if (
        not required
        or any(not isinstance(item, str) or not item.strip() for item in required)
        or len(set(required)) != len(required)
        or set(installations) != set(required)
    ):
        raise RuntimeError("Every required gateway must confirm the same installed snapshot generation.")
    for gateway_id in required:
        receipt = installations[gateway_id]
        if (
            not isinstance(receipt, Mapping)
            or receipt.get("source_id") != source_id
            or receipt.get("stream_key") != stream_key
            or receipt.get("snapshot_generation") != generation
            or type(receipt.get("snapshot_cursor")) is not int
            or receipt.get("snapshot_cursor") != cursor
        ):
            raise RuntimeError("A gateway snapshot receipt does not match the global snapshot manifest.")
    return {
        "source_id": source_id,
        "stream_key": stream_key,
        "snapshot_generation": generation,
        "snapshot_cursor": cursor,
        "verified_gateway_count": len(required),
    }


def build_source_publisher_runtime_factory(
    *,
    redis_url: str,
    owner: str,
    snapshot_verifier: Callable[[SQLiteOhlcvStore, Mapping[str, Any]], Mapping[str, Any]],
    stream_key: str = DEFAULT_OHLCV_STREAM_KEY,
    production: bool = False,
    redis_client_factory: Callable[..., Any] | None = None,
) -> Callable[[SQLiteOhlcvStore], dict[str, Any]]:
    """Build the source app's publisher_runtime_factory; never invent a cursor."""
    if type(production) is not bool:
        raise ValueError("production must be a boolean.")
    if not isinstance(owner, str) or not owner.strip() or len(owner) > 128:
        raise ValueError("A stable, unique publisher owner ID is required.")
    if not callable(snapshot_verifier):
        raise ValueError("A host snapshot verifier is required before publisher activation.")
    OhlcvRedisRelayConfig(stream_key=stream_key)
    _parse_acl_url(redis_url, name="OHLCV_REDIS_PUBLISH_URL", production=production)

    options: dict[str, Any] = {
        "decode_responses": True,
        "socket_connect_timeout": 3.0,
        "socket_timeout": 5.0,
        "health_check_interval": 15,
        "retry_on_timeout": False,
    }
    if urlsplit(redis_url).scheme == "rediss":
        options.update(ssl_cert_reqs="required", ssl_check_hostname=True)

    def runtime_factory(source_store: SQLiteOhlcvStore) -> dict[str, Any]:
        if not isinstance(source_store, SQLiteOhlcvStore):
            raise TypeError("The source publisher requires the authoritative SQLiteOhlcvStore.")
        checkpoint = SQLiteOhlcvPublisherCheckpoint(source_store, stream_key=stream_key)
        state = checkpoint.state()
        if state is None:
            raise RuntimeError("Publisher checkpoint is missing; install and verify the global snapshot first.")
        if state.get("stream_key") != stream_key:
            raise RuntimeError("Publisher checkpoint stream does not match configured stream.")
        evidence = _validate_snapshot_evidence(
            snapshot_verifier(source_store, state),
            source_id=source_store.source_id(),
            checkpoint_cursor=state["published_cursor"],
            stream_key=stream_key,
        )
        if redis_client_factory is None:
            import redis
            client = redis.Redis.from_url(redis_url, **options)
        else:
            client = redis_client_factory(redis_url, **options)
        try:
            if client is None or not callable(getattr(client, "ping", None)):
                raise RuntimeError("Publisher Redis client must provide a PING operation.")
            publisher = RedisOhlcvPublisher(
                source_store, checkpoint, client, owner=owner,
            )
        except Exception:
            close = getattr(client, "close", None)
            if callable(close):
                close()
            raise
        return {
            "publisher": publisher,
            "redis_client": client,
            "stream_key": stream_key,
            "snapshot_evidence": evidence,
        }

    return runtime_factory


def source_publisher_runtime_factory_from_environment(
    *,
    snapshot_verifier: Callable[[SQLiteOhlcvStore, Mapping[str, Any]], Mapping[str, Any]],
    environ: Mapping[str, str] | None = None,
    redis_client_factory: Callable[..., Any] | None = None,
) -> Callable[[SQLiteOhlcvStore], dict[str, Any]] | None:
    """Create a source factory only when OHLCV_REDIS_ENABLED is explicitly true."""
    source = os.environ if environ is None else environ
    enabled = source.get("OHLCV_REDIS_ENABLED", "false").strip().lower()
    if enabled in {"", "0", "false", "no", "off"}:
        return None
    if enabled not in {"1", "true", "yes", "on"}:
        raise ValueError("OHLCV_REDIS_ENABLED must be a boolean value.")
    return build_source_publisher_runtime_factory(
        redis_url=source.get("OHLCV_REDIS_PUBLISH_URL", ""),
        owner=source.get("OHLCV_REDIS_PUBLISHER_OWNER", ""),
        stream_key=source.get("OHLCV_REDIS_STREAM_KEY", DEFAULT_OHLCV_STREAM_KEY),
        production=source.get("APP_ENV", "development").strip().lower() == "production",
        snapshot_verifier=snapshot_verifier,
        redis_client_factory=redis_client_factory,
    )
