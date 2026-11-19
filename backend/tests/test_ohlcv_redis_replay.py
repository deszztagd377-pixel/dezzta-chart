from __future__ import annotations

import json

import pytest

from app.ohlcv_redis_replay import (
    RedisReplayResnapshotRequired,
    read_redis_replay_page,
)


SOURCE = "source-1"
IDENTITY = {
    "provider": "databento",
    "dataset": "GLBX.MDP3",
    "publisherId": 1,
    "instrumentId": 123,
    "seriesType": "contract",
    "rawSymbol": "ESZ6",
    "timeframe": "1m",
    "bucketPolicy": "UTC_LEGACY",
    "calendarId": "",
    "calendarVersion": "",
}


def make_entry(cursor: int, *, identity=None):
    series = dict(identity or IDENTITY)
    bar = {
        **series,
        "tsStartNs": str(cursor * 60_000_000_000),
        "open": "100", "high": "103", "low": "99", "close": str(100 + cursor),
        "volume": "12.5", "tsEventNs": str(cursor + 100),
        "tsReceivedNs": str(cursor + 110), "tsProviderOutNs": None,
        "sequence": cursor, "sequenceOrigin": "local", "origin": "provider",
        "completeness": "unknown",
    }
    event = {
        "type": "market_data.ohlcv.update",
        "version": 1,
        "eventId": f"event-{cursor}",
        "operation": "upsert",
        "series": series,
        "bar": bar,
        "cursor": cursor,
    }
    payload = json.dumps(
        event, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )
    return (f"{cursor}-0", {
        "source_id": SOURCE,
        "event_id": f"event-{cursor}",
        "payload": payload,
    })


class FakeRedis:
    def __init__(self, entries):
        self.entries = entries

    def xrange(self, key, *, min, max, count):
        del key
        low = int(min.split("-", 1)[0])
        high = int(max.split("-", 1)[0])
        return [
            entry for entry in self.entries
            if low <= int(entry[0].split("-", 1)[0]) <= high
        ][:count]


def test_replay_advances_global_cursor_across_unrelated_series():
    other = dict(IDENTITY, instrumentId=999, rawSymbol="NQZ6")
    redis = FakeRedis([
        make_entry(1, identity=other),
        make_entry(2),
        make_entry(3, identity=other),
        make_entry(4),
    ])

    first = read_redis_replay_page(
        redis, stream_key="ohlcv", source_id=SOURCE,
        after_cursor=0, through_cursor=4,
        series_identity=IDENTITY, scan_limit=2,
    )
    assert [event["cursor"] for event in first["events"]] == [2]
    assert first["next_cursor"] == 2
    assert first["has_more"] is True
    assert first["scanned"] == 2

    second = read_redis_replay_page(
        redis, stream_key="ohlcv", source_id=SOURCE,
        after_cursor=first["next_cursor"], through_cursor=4,
        series_identity=IDENTITY, scan_limit=2,
    )
    assert [event["cursor"] for event in second["events"]] == [4]
    assert second["next_cursor"] == 4
    assert second["has_more"] is False


def test_replay_fails_closed_when_first_cursor_is_missing():
    redis = FakeRedis([make_entry(2)])
    with pytest.raises(RedisReplayResnapshotRequired, match="expected 1"):
        read_redis_replay_page(
            redis, stream_key="ohlcv", source_id=SOURCE,
            after_cursor=0, through_cursor=2,
            series_identity=IDENTITY, scan_limit=10,
        )


def test_replay_fails_closed_when_stream_ends_before_snapshot_watermark():
    redis = FakeRedis([make_entry(1), make_entry(2)])
    with pytest.raises(RedisReplayResnapshotRequired, match="before watermark 3"):
        read_redis_replay_page(
            redis, stream_key="ohlcv", source_id=SOURCE,
            after_cursor=0, through_cursor=3,
            series_identity=IDENTITY, scan_limit=10,
        )


def test_replay_rejects_series_bar_identity_mismatch():
    malformed = make_entry(1)
    event = json.loads(malformed[1]["payload"])
    event["bar"]["instrumentId"] = 999
    malformed[1]["payload"] = json.dumps(
        event, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    redis = FakeRedis([malformed])
    with pytest.raises(ValueError, match="identity is inconsistent"):
        read_redis_replay_page(
            redis, stream_key="ohlcv", source_id=SOURCE,
            after_cursor=0, through_cursor=1,
            series_identity=IDENTITY, scan_limit=10,
        )


def test_replay_empty_interval_does_not_touch_redis():
    class NoCallRedis:
        def xrange(self, *args, **kwargs):
            raise AssertionError("xrange must not be called for an empty interval")

    result = read_redis_replay_page(
        NoCallRedis(), stream_key="ohlcv", source_id=SOURCE,
        after_cursor=5, through_cursor=5,
        series_identity=IDENTITY,
    )
    assert result["status"] == "ok"
    assert result["events"] == []
    assert result["next_cursor"] == 5
    assert result["has_more"] is False
