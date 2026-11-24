from __future__ import annotations

import json

import pytest

from app.ohlcv_redis_replay import (
    RedisReplayResnapshotRequired,
    read_redis_replay_page,
    replay_replica_history,
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


def test_replica_replay_uses_fixed_checkpoint_watermark_and_global_scan():
    other = dict(IDENTITY, instrumentId=999, rawSymbol="NQZ6")
    redis = FakeRedis([
        make_entry(1),
        make_entry(2, identity=other),
        make_entry(3),
        make_entry(4, identity=other),
    ])
    result = replay_replica_history(
        redis, stream_key="ohlcv",
        checkpoint={"source_id": SOURCE, "applied_cursor": 4, "retention_floor": 0},
        after_cursor=0, series_identity=IDENTITY, scan_limit=2,
    )
    assert result["status"] == "ok"
    assert [event["cursor"] for event in result["events"]] == [1, 3]
    assert result["next_cursor"] == result["through_cursor"] == 4
    assert result["scanned"] == 4


@pytest.mark.parametrize(
    ("after_cursor", "checkpoint", "reason"),
    [
        (2, {"source_id": SOURCE, "applied_cursor": 5, "retention_floor": 3}, "cursor_expired"),
        (6, {"source_id": SOURCE, "applied_cursor": 5, "retention_floor": 0}, "cursor_ahead"),
    ],
)
def test_replica_replay_requires_snapshot_for_invalid_client_cursor(
    after_cursor, checkpoint, reason,
):
    class NoCallRedis:
        def xrange(self, *args, **kwargs):
            raise AssertionError("Redis must not be queried for an invalid cursor")

    result = replay_replica_history(
        NoCallRedis(), stream_key="ohlcv", checkpoint=checkpoint,
        after_cursor=after_cursor, series_identity=IDENTITY,
    )
    assert result["status"] == "resnapshot_required"
    assert result["reason"] == reason
    assert result["events"] == []


def test_replica_replay_returns_no_partial_events_when_event_cap_is_exceeded():
    redis = FakeRedis([make_entry(1), make_entry(2), make_entry(3)])
    result = replay_replica_history(
        redis, stream_key="ohlcv",
        checkpoint={"source_id": SOURCE, "applied_cursor": 3, "retention_floor": 0},
        after_cursor=0, series_identity=IDENTITY,
        max_events=2, scan_limit=3,
    )
    assert result["status"] == "resnapshot_required"
    assert result["reason"] == "replay_event_limit_exceeded"
    assert result["events"] == []


def test_replica_replay_bounds_global_scan_even_when_series_is_sparse():
    other = dict(IDENTITY, instrumentId=999, rawSymbol="NQZ6")
    redis = FakeRedis([
        make_entry(1, identity=other),
        make_entry(2, identity=other),
        make_entry(3, identity=other),
        make_entry(4, identity=other),
    ])
    result = replay_replica_history(
        redis, stream_key="ohlcv",
        checkpoint={"source_id": SOURCE, "applied_cursor": 4, "retention_floor": 0},
        after_cursor=0, series_identity=IDENTITY,
        max_scanned=3, scan_limit=2,
    )
    assert result["status"] == "resnapshot_required"
    assert result["reason"] == "replay_scan_limit_exceeded"
    assert result["events"] == []


def test_replica_replay_empty_cursor_interval_does_not_query_redis():
    class NoCallRedis:
        def xrange(self, *args, **kwargs):
            raise AssertionError("Redis must not be queried at the replica watermark")

    result = replay_replica_history(
        NoCallRedis(), stream_key="ohlcv",
        checkpoint={"source_id": SOURCE, "applied_cursor": 5, "retention_floor": 0},
        after_cursor=5, series_identity=IDENTITY,
    )
    assert result["status"] == "ok"
    assert result["events"] == []
    assert result["next_cursor"] == 5


def test_replica_replay_validates_stream_and_series_even_at_empty_interval():
    class NoCallRedis:
        def xrange(self, *args, **kwargs):
            raise AssertionError("Redis must not be queried for an empty interval")

    checkpoint = {"source_id": SOURCE, "applied_cursor": 5, "retention_floor": 0}
    with pytest.raises(ValueError, match="stream_key is required"):
        replay_replica_history(
            NoCallRedis(), stream_key=" ", checkpoint=checkpoint,
            after_cursor=5, series_identity=IDENTITY,
        )
    with pytest.raises(ValueError, match="canonical series identity"):
        replay_replica_history(
            NoCallRedis(), stream_key="ohlcv", checkpoint=checkpoint,
            after_cursor=5, series_identity={},
        )



@pytest.mark.parametrize(
    ("after_cursor", "expected_status", "expected_reason"),
    [
        (9, "resnapshot_required", "cursor_expired"),
        (10, "ok", None),
        (11, "ok", None),
    ],
)
def test_replica_replay_retention_floor_boundary_is_inclusive(
    after_cursor, expected_status, expected_reason,
):
    # The retention floor is the oldest cursor a client may resume AFTER.
    # Equality is valid; only a cursor strictly below the floor has expired.
    redis = FakeRedis([make_entry(11), make_entry(12)])
    result = replay_replica_history(
        redis,
        stream_key="ohlcv",
        checkpoint={
            "source_id": SOURCE,
            "applied_cursor": 12,
            "retention_floor": 10,
        },
        after_cursor=after_cursor,
        series_identity=IDENTITY,
        scan_limit=2,
    )
    assert result["status"] == expected_status
    assert result["reason"] == expected_reason
    if expected_status == "ok":
        assert [event["cursor"] for event in result["events"]] == list(
            range(after_cursor + 1, 13)
        )
        assert result["next_cursor"] == 12
    else:
        assert result["events"] == []


@pytest.mark.parametrize(
    "checkpoint",
    [
        {"source_id": SOURCE, "applied_cursor": True, "retention_floor": 0},
        {"source_id": SOURCE, "applied_cursor": -1, "retention_floor": 0},
        {"source_id": SOURCE, "applied_cursor": 2},
        {"source_id": SOURCE, "applied_cursor": 2, "retention_floor": 3},
        {"source_id": SOURCE, "applied_cursor": 2, "retention_floor": -1},
    ],
)
def test_replica_replay_rejects_malformed_checkpoint_matrix(checkpoint):
    class NoCallRedis:
        def xrange(self, *args, **kwargs):
            raise AssertionError("Malformed checkpoints must fail before Redis access")

    with pytest.raises(ValueError):
        replay_replica_history(
            NoCallRedis(),
            stream_key="ohlcv",
            checkpoint=checkpoint,
            after_cursor=0,
            series_identity=IDENTITY,
        )


def test_replay_page_exact_scan_limit_advances_to_next_contiguous_page():
    redis = FakeRedis([make_entry(1), make_entry(2), make_entry(3)])
    first = read_redis_replay_page(
        redis,
        stream_key="ohlcv",
        source_id=SOURCE,
        after_cursor=0,
        through_cursor=3,
        series_identity=IDENTITY,
        scan_limit=2,
    )
    assert first["scanned"] == 2
    assert first["next_cursor"] == 2
    assert first["has_more"] is True

    second = read_redis_replay_page(
        redis,
        stream_key="ohlcv",
        source_id=SOURCE,
        after_cursor=first["next_cursor"],
        through_cursor=3,
        series_identity=IDENTITY,
        scan_limit=2,
    )
    assert second["scanned"] == 1
    assert second["next_cursor"] == 3
    assert second["has_more"] is False
    assert [
        event["cursor"] for event in first["events"] + second["events"]
    ] == [1, 2, 3]
