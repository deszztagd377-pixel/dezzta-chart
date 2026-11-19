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
