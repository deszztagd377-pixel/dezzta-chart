from decimal import Decimal

import pytest

from app.ohlcv import OhlcvBar
from app.ohlcv_store import SQLiteOhlcvStore
from app.ohlcv_redis_publisher import (
    RedisAppendUnconfirmed,
    RedisOhlcvPublisher,
    RedisOhlcvStreamAppender,
    RedisStreamConflict,
    SQLiteOhlcvPublisherCheckpoint,
)


NS = 1_000_000_000


def make_bar(*, start=0, event=100, sequence=1, close="101"):
    return OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=123, series_type="contract",
        timeframe="1m", ts_start_ns=start, raw_symbol="ESZ6",
        open=Decimal("100"), high=Decimal("103"), low=Decimal("99"),
        close=Decimal(close), volume=Decimal("12.5"),
        ts_event_ns=event, ts_received_ns=event + 10, sequence=sequence,
        sequence_origin="local", origin="provider", completeness="unknown",
    )


def append_bar(store, *, index=0):
    return store.apply(make_bar(
        start=index * 60 * NS, event=100 + index, sequence=index + 1,
        close=str(101 + index),
    ))


def make_event(cursor, event_id="stable-event-1"):
    return {
        "type": "market_data.ohlcv.update",
        "version": 1,
        "eventId": event_id,
        "operation": "upsert",
        "series": {},
        "bar": {},
        "cursor": cursor,
    }


def setup_checkpoint(tmp_path, *, snapshot_cursor=0):
    store = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    checkpoint = SQLiteOhlcvPublisherCheckpoint(store)
    state = checkpoint.initialize_from_snapshot(snapshot_cursor, now_ms=1_000)
    return store, checkpoint, state


def test_checkpoint_initializes_only_from_retained_snapshot_watermark(tmp_path):
    store, checkpoint, state = setup_checkpoint(tmp_path)
    assert state["source_id"] == store.source_id()
    assert state["stream_key"] == "dezzta:market-data:ohlcv:v1"
    assert state["published_cursor"] == 0
    assert state["last_stream_id"] == "0-0"
    assert state["lease_epoch"] == 0
    assert checkpoint.initialize_from_snapshot(0, now_ms=2_000) == state


def test_checkpoint_rejects_snapshot_older_than_retention_floor(tmp_path):
    store, checkpoint, _ = setup_checkpoint(tmp_path)
    # Use the real source retention boundary without changing production limits.
    with store._connect() as db:
        db.execute(
            "UPDATE ohlcv_outbox_state SET int_value=2 WHERE state_key='retention_floor'"
        )
        db.execute(
            "UPDATE ohlcv_outbox_state SET int_value=3 WHERE state_key='high_water'"
        )
    with pytest.raises(RuntimeError, match="fresh snapshot"):
        checkpoint.initialize_from_snapshot(1, now_ms=2_000)


def test_lease_excludes_second_owner_and_epoch_fences_expired_owner(tmp_path):
    _, checkpoint, _ = setup_checkpoint(tmp_path)
    first = checkpoint.acquire_lease("publisher-A", now_ms=10_000, ttl_ms=1_000)
    assert first["lease_epoch"] == 1
    assert checkpoint.acquire_lease("publisher-B", now_ms=10_500, ttl_ms=1_000) is None

    renewed = checkpoint.acquire_lease("publisher-A", now_ms=10_500, ttl_ms=1_000)
    assert renewed["lease_epoch"] == 1
    second = checkpoint.acquire_lease("publisher-B", now_ms=11_501, ttl_ms=1_000)
    assert second["lease_epoch"] == 2
    assert second["lease_owner"] == "publisher-B"
    assert checkpoint.release_lease("publisher-A", epoch=1, now_ms=11_502) is False


def test_checkpoint_advances_one_deterministic_cursor_under_current_lease(tmp_path):
    store, checkpoint, _ = setup_checkpoint(tmp_path)
    assert append_bar(store) == "inserted"
    batch = store.read_outbox_batch(after_cursor=0, limit=10)
    event = batch["events"][0]
    lease = checkpoint.acquire_lease("publisher-A", now_ms=20_000)
    advanced = checkpoint.record_confirmed_append(
        "publisher-A", epoch=lease["lease_epoch"], expected_cursor=0,
        event=event, stream_id="1-0", now_ms=20_010,
    )
    assert advanced["published_cursor"] == 1
    assert advanced["last_event_id"] == event["eventId"]
    assert advanced["last_stream_id"] == "1-0"


def test_checkpoint_rejects_gap_wrong_stream_id_and_stale_lease(tmp_path):
    store, checkpoint, _ = setup_checkpoint(tmp_path)
    assert append_bar(store) == "inserted"
    event = store.read_outbox_batch(after_cursor=0, limit=10)["events"][0]
    lease = checkpoint.acquire_lease("publisher-A", now_ms=30_000, ttl_ms=100)

    with pytest.raises(ValueError, match="exactly one contiguous"):
        checkpoint.record_confirmed_append(
            "publisher-A", epoch=lease["lease_epoch"], expected_cursor=0,
            event={**event, "cursor": 2}, stream_id="2-0", now_ms=30_010,
        )
    with pytest.raises(ValueError, match="deterministic cursor ID"):
        checkpoint.record_confirmed_append(
            "publisher-A", epoch=lease["lease_epoch"], expected_cursor=0,
            event=event, stream_id="1-1", now_ms=30_010,
        )
    with pytest.raises(RuntimeError, match="expired or fenced"):
        checkpoint.record_confirmed_append(
            "publisher-A", epoch=lease["lease_epoch"], expected_cursor=0,
            event=event, stream_id="1-0", now_ms=30_101,
        )
    assert checkpoint.state()["published_cursor"] == 0


def test_checkpoint_compare_and_swap_prevents_double_advance(tmp_path):
    store, checkpoint, _ = setup_checkpoint(tmp_path)
    assert append_bar(store, index=0) == "inserted"
    assert append_bar(store, index=1) == "inserted"
    events = store.read_outbox_batch(after_cursor=0, limit=10)["events"]
    lease = checkpoint.acquire_lease("publisher-A", now_ms=40_000)

    checkpoint.record_confirmed_append(
        "publisher-A", epoch=lease["lease_epoch"], expected_cursor=0,
        event=events[0], stream_id="1-0", now_ms=40_010,
    )
    # Replay the already-confirmed cursor with the stale expected watermark.
    # The event itself remains authoritative and valid; only the checkpoint CAS
    # must reject the second advancement.
    with pytest.raises(RuntimeError, match="compare-and-swap"):
        checkpoint.record_confirmed_append(
            "publisher-A", epoch=lease["lease_epoch"], expected_cursor=0,
            event=events[0], stream_id="1-0", now_ms=40_020,
        )
    assert checkpoint.state()["published_cursor"] == 1



class FakeRedisStream:
    def __init__(self):
        self.streams = {}
        self.fail_after_append_once = False
        self.unavailable = False

    def xadd(self, name, fields, *, id):
        if self.unavailable:
            raise ConnectionError("redis unavailable")
        stream = self.streams.setdefault(name, {})
        if id in stream or (stream and id <= max(stream)):
            raise RuntimeError("stream ID is not greater than the top item")
        stream[id] = dict(fields)
        if self.fail_after_append_once:
            self.fail_after_append_once = False
            raise ConnectionError("reply lost after Redis committed XADD")
        return id

    def xrange(self, name, *, min, max, count):
        if self.unavailable:
            raise ConnectionError("redis unavailable")
        stream = self.streams.get(name, {})
        return [
            (entry_id, dict(fields))
            for entry_id, fields in sorted(stream.items())
            if min <= entry_id <= max
        ][:count]


def setup_publisher(tmp_path, *, clock=None, batch_size=100):
    store, checkpoint, _ = setup_checkpoint(tmp_path)
    redis = FakeRedisStream()
    publisher = RedisOhlcvPublisher(
        store,
        checkpoint,
        redis,
        owner="publisher-A",
        lease_ttl_ms=5_000,
        batch_size=batch_size,
        clock_ms=clock or (lambda: 10_000),
    )
    return store, checkpoint, redis, publisher


def test_redis_publisher_appends_ordered_events_and_advances_checkpoint(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store, index=0) == "inserted"
    assert append_bar(store, index=1) == "inserted"

    result = publisher.publish_available()
    assert result == {
        "status": "published",
        "published": 2,
        "verified_existing": 0,
        "published_cursor": 2,
        "high_water": 2,
        "has_more": False,
    }
    stream = redis.streams["dezzta:market-data:ohlcv:v1"]
    assert list(stream) == ["1-0", "2-0"]
    assert checkpoint.state()["published_cursor"] == 2


def test_redis_publisher_recovers_xadd_commit_with_lost_reply(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store) == "inserted"
    redis.fail_after_append_once = True

    result = publisher.publish_available()
    assert result["published"] == 1
    assert result["verified_existing"] == 1
    assert result["published_cursor"] == 1
    assert checkpoint.state()["published_cursor"] == 1
    assert list(redis.streams["dezzta:market-data:ohlcv:v1"]) == ["1-0"]


def test_redis_publisher_recovers_crash_after_append_before_checkpoint(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store) == "inserted"
    event = store.read_outbox_batch(after_cursor=0, limit=1)["events"][0]
    appender = RedisOhlcvStreamAppender(
        redis,
        stream_key="dezzta:market-data:ohlcv:v1",
        source_id=store.source_id(),
    )
    assert appender.append_confirmed(event) == "appended"
    assert checkpoint.state()["published_cursor"] == 0

    result = publisher.publish_available()
    assert result["verified_existing"] == 1
    assert result["published_cursor"] == 1
    assert len(redis.streams["dezzta:market-data:ohlcv:v1"]) == 1


def test_redis_publisher_rejects_existing_deterministic_id_with_conflicting_payload(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store) == "inserted"
    redis.streams["dezzta:market-data:ohlcv:v1"] = {
        "1-0": {
            "source_id": store.source_id(),
            "event_id": "different-event",
            "payload": '{"cursor":1}',
        }
    }

    with pytest.raises(RedisStreamConflict, match="different source/event/payload"):
        publisher.publish_available()
    assert checkpoint.state()["published_cursor"] == 0


def test_redis_outage_does_not_advance_publisher_checkpoint(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store) == "inserted"
    redis.unavailable = True

    with pytest.raises(RedisAppendUnconfirmed, match="outcome is uncertain"):
        publisher.publish_available()
    assert checkpoint.state()["published_cursor"] == 0


def test_redis_publisher_requires_snapshot_when_source_retention_overtakes_cursor(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store, index=0) == "inserted"
    assert append_bar(store, index=1) == "inserted"
    with store._connect() as db:
        db.execute(
            "UPDATE ohlcv_outbox_state SET int_value=1 WHERE state_key='retention_floor'"
        )

    with pytest.raises(RuntimeError, match="fresh global snapshot"):
        publisher.publish_available()
    assert checkpoint.state()["published_cursor"] == 0
    assert redis.streams == {}


def test_redis_publisher_does_not_publish_when_another_owner_holds_lease(tmp_path):
    store, checkpoint, redis, publisher = setup_publisher(tmp_path)
    assert append_bar(store) == "inserted"
    other = checkpoint.acquire_lease("publisher-B", now_ms=9_999, ttl_ms=5_000)
    assert other is not None

    result = publisher.publish_available()
    assert result == {"status": "lease_busy", "published": 0}
    assert redis.streams == {}
    assert checkpoint.state()["published_cursor"] == 0
