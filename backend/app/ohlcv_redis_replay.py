"""Bounded, cursor-contiguous replay from the canonical OHLCV Redis Stream.

The source outbox uses a global cursor. Redis replay must therefore scan every
global event in cursor order, advance across unrelated series, and fail closed
when any cursor in the requested interval is absent (including trimmed history).
"""
from __future__ import annotations

import json
from typing import Any


class RedisReplayResnapshotRequired(RuntimeError):
    """The requested global cursor interval is no longer completely replayable."""


_SERIES_KEYS = (
    "provider", "dataset", "publisherId", "instrumentId", "seriesType",
    "rawSymbol", "timeframe", "bucketPolicy", "calendarId", "calendarVersion",
)


def _text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, str):
        return value
    raise ValueError("Redis stream keys and values must be strings or UTF-8 bytes.")


def _decode(redis_id: Any, fields: Any, *, source_id: str) -> dict[str, Any]:
    entry_id = _text(redis_id)
    if not isinstance(fields, dict):
        raise ValueError("Redis OHLCV replay fields must be an object.")
    decoded = {_text(key): _text(value) for key, value in fields.items()}
    if set(decoded) != {"source_id", "event_id", "payload"}:
        raise ValueError("Redis OHLCV replay fields do not match the stream protocol.")
    if decoded["source_id"] != source_id:
        raise ValueError("Redis OHLCV replay source identity mismatch.")
    try:
        event = json.loads(decoded["payload"])
    except json.JSONDecodeError as exc:
        raise ValueError("Redis OHLCV replay payload is invalid JSON.") from exc
    if not isinstance(event, dict):
        raise ValueError("Redis OHLCV replay payload must be an event object.")
    canonical = json.dumps(
        event, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )
    if canonical != decoded["payload"]:
        raise ValueError("Redis OHLCV replay payload is not canonical JSON.")
    if (
        set(event) != {"type", "version", "eventId", "operation", "series", "bar", "cursor"}
        or event["type"] != "market_data.ohlcv.update"
        or type(event["version"]) is not int or event["version"] != 1
        or event["operation"] != "upsert"
        or not isinstance(event["eventId"], str) or not event["eventId"]
        or event["eventId"] != decoded["event_id"]
        or type(event["cursor"]) is not int or event["cursor"] < 1
        or entry_id != f"{event['cursor']}-0"
    ):
        raise ValueError("Redis OHLCV replay event envelope is invalid.")
    series, bar = event["series"], event["bar"]
    if (
        not isinstance(series, dict) or set(series) != set(_SERIES_KEYS)
        or not isinstance(bar, dict)
        or any(bar.get(key) != series[key] for key in _SERIES_KEYS)
    ):
        raise ValueError("Redis OHLCV replay series identity is inconsistent.")
    return event


def read_redis_replay_page(
    redis_client: Any,
    *,
    stream_key: str,
    source_id: str,
    after_cursor: int,
    through_cursor: int,
    series_identity: dict[str, Any],
    scan_limit: int = 500,
) -> dict[str, Any]:
    """Read one bounded global-cursor page, filtering output to one exact series.

    `next_cursor` is the last globally scanned cursor, not the last matching
    series event. This preserves forward progress across unrelated symbols.
    Any missing cursor in the interval requires a fresh snapshot; no silent
    cursor jump is permitted.
    """
    if redis_client is None:
        raise ValueError("redis_client is required.")
    if not isinstance(stream_key, str) or not stream_key.strip():
        raise ValueError("stream_key is required.")
    if not isinstance(source_id, str) or not source_id:
        raise ValueError("source_id is required.")
    if type(after_cursor) is not int or after_cursor < 0:
        raise ValueError("after_cursor must be a non-negative integer.")
    if type(through_cursor) is not int or through_cursor < after_cursor:
        raise ValueError("through_cursor must be an integer >= after_cursor.")
    if type(scan_limit) is not int or not 1 <= scan_limit <= 5_000:
        raise ValueError("scan_limit must be between 1 and 5000.")
    if not isinstance(series_identity, dict) or set(series_identity) != set(_SERIES_KEYS):
        raise ValueError("A complete canonical series identity is required.")

    if through_cursor == after_cursor:
        return {
            "status": "ok", "events": [], "next_cursor": after_cursor,
            "through_cursor": through_cursor, "has_more": False,
            "scanned": 0,
        }

    entries = redis_client.xrange(
        stream_key,
        min=f"{after_cursor + 1}-0",
        max=f"{through_cursor}-0",
        count=scan_limit,
    )
    if not entries:
        raise RedisReplayResnapshotRequired(
            f"Redis history is missing cursor {after_cursor + 1}."
        )

    expected = after_cursor + 1
    events: list[dict[str, Any]] = []
    last_cursor = after_cursor
    for redis_id, fields in entries:
        event = _decode(redis_id, fields, source_id=source_id)
        cursor = event["cursor"]
        if cursor != expected:
            raise RedisReplayResnapshotRequired(
                f"Redis replay cursor gap: expected {expected}, received {cursor}."
            )
        expected += 1
        last_cursor = cursor
        if event["series"] == series_identity:
            events.append(event)

    has_more = last_cursor < through_cursor
    if has_more and len(entries) < scan_limit:
        raise RedisReplayResnapshotRequired(
            f"Redis history ended at {last_cursor} before watermark {through_cursor}."
        )
    return {
        "status": "ok",
        "events": events,
        "next_cursor": last_cursor,
        "through_cursor": through_cursor,
        "has_more": has_more,
        "scanned": len(entries),
    }


def replay_replica_history(
    redis_client: Any,
    *,
    stream_key: str,
    checkpoint: dict[str, Any],
    after_cursor: int,
    series_identity: dict[str, Any],
    max_events: int = 10_000,
    max_scanned: int = 50_000,
    scan_limit: int = 500,
) -> dict[str, Any]:
    """Replay one exact series from a client cursor through a replica watermark.

    The replica checkpoint fixes the upper watermark. Cursor expiry, a client
    cursor ahead of the replica, Redis trimming/corruption, a non-advancing
    page, or either work cap causes an all-or-resnapshot result; partial replay
    events are never returned as a successful replay.
    """
    if not isinstance(checkpoint, dict):
        raise ValueError("checkpoint must be an object.")
    if redis_client is None:
        raise ValueError("redis_client is required.")
    if not isinstance(stream_key, str) or not stream_key.strip():
        raise ValueError("stream_key is required.")
    if not isinstance(series_identity, dict) or set(series_identity) != set(_SERIES_KEYS):
        raise ValueError("A complete canonical series identity is required.")
    source_id = checkpoint.get("source_id")
    through_cursor = checkpoint.get("applied_cursor")
    retention_floor = checkpoint.get("retention_floor")
    if not isinstance(source_id, str) or not source_id:
        raise ValueError("checkpoint source_id is required.")
    if type(through_cursor) is not int or through_cursor < 0:
        raise ValueError("checkpoint applied_cursor must be a non-negative integer.")
    if type(retention_floor) is not int or not 0 <= retention_floor <= through_cursor:
        raise ValueError("checkpoint retention_floor must be within the applied cursor.")
    if type(after_cursor) is not int or after_cursor < 0:
        raise ValueError("after_cursor must be a non-negative integer.")
    if type(max_events) is not int or not 1 <= max_events <= 10_000:
        raise ValueError("max_events must be between 1 and 10000.")
    if type(max_scanned) is not int or not 1 <= max_scanned <= 100_000:
        raise ValueError("max_scanned must be between 1 and 100000.")
    if type(scan_limit) is not int or not 1 <= scan_limit <= 5_000:
        raise ValueError("scan_limit must be between 1 and 5000.")

    def resnapshot(reason: str, *, scanned: int = 0) -> dict[str, Any]:
        return {
            "status": "resnapshot_required",
            "reason": reason,
            "events": [],
            "next_cursor": through_cursor,
            "through_cursor": through_cursor,
            "scanned": scanned,
            "source_id": source_id,
        }

    if after_cursor < retention_floor:
        return resnapshot("cursor_expired")
    if after_cursor > through_cursor:
        return resnapshot("cursor_ahead")
    if after_cursor == through_cursor:
        return {
            "status": "ok", "reason": None, "events": [],
            "next_cursor": through_cursor, "through_cursor": through_cursor,
            "scanned": 0, "source_id": source_id,
        }

    cursor = after_cursor
    scanned = 0
    events: list[dict[str, Any]] = []
    while cursor < through_cursor:
        try:
            page = read_redis_replay_page(
                redis_client,
                stream_key=stream_key,
                source_id=source_id,
                after_cursor=cursor,
                through_cursor=through_cursor,
                series_identity=series_identity,
                scan_limit=scan_limit,
            )
        except RedisReplayResnapshotRequired:
            return resnapshot("redis_history_gap_or_trimmed", scanned=scanned)
        except ValueError:
            return resnapshot("invalid_redis_replay_entry", scanned=scanned)

        page_events = page["events"]
        page_scanned = page["scanned"]
        if scanned + page_scanned > max_scanned:
            return resnapshot("replay_scan_limit_exceeded", scanned=scanned)
        if len(events) + len(page_events) > max_events:
            return resnapshot("replay_event_limit_exceeded", scanned=scanned)
        next_cursor = page["next_cursor"]
        if type(next_cursor) is not int or next_cursor <= cursor:
            return resnapshot("replay_cursor_did_not_advance", scanned=scanned)
        scanned += page_scanned
        events.extend(page_events)
        cursor = next_cursor
        if not page["has_more"] and cursor < through_cursor:
            return resnapshot("replay_ended_before_replica_watermark", scanned=scanned)

    if cursor != through_cursor:
        return resnapshot("replay_watermark_mismatch", scanned=scanned)
    return {
        "status": "ok",
        "reason": None,
        "events": events,
        "next_cursor": cursor,
        "through_cursor": through_cursor,
        "scanned": scanned,
        "source_id": source_id,
    }
