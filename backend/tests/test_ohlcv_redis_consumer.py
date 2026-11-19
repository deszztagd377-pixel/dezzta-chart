from __future__ import annotations

import os
import uuid

import pytest

from app.ohlcv import OhlcvBar
from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore
from app.ohlcv_redis_publisher import RedisOhlcvStreamAppender
from app.ohlcv_redis_consumer import (
    RedisOhlcvReplicaConsumer,
    ReplicaResnapshotRequired,
)

from decimal import Decimal

NS = 1_000_000_000
STREAM_KEY = "dezzta:market-data:ohlcv:v1"


def make_bar(index=0):
    return OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=123, series_type="contract",
        timeframe="1m", ts_start_ns=index * 60 * NS, raw_symbol="ESZ6",
        open=Decimal("100"), high=Decimal("103"), low=Decimal("99"),
        close=Decimal(str(101 + index)), volume=Decimal("12.5"),
        ts_event_ns=100 + index, ts_received_ns=110 + index,
        sequence=index + 1, sequence_origin="local", origin="provider",
        completeness="unknown",
    )


def real_redis():
    redis_url = os.environ.get("REDIS_TEST_URL")
    if not redis_url:
        pytest.skip("REDIS_TEST_URL is not configured.")
    redis_module = pytest.importorskip("redis")
    client = redis_module.Redis.from_url(redis_url, decode_responses=True)
    client.ping()
    stream_key = f"{STREAM_KEY}:{uuid.uuid4().hex}"
    return client, stream_key


def make_snapshot(source, destination):
    return source.export_global_snapshot(str(destination))


def make_replica(source, snapshot_path, db_path):
    replica = SQLiteOhlcvReplicaStore(str(db_path))
    replica.install_global_snapshot(
        str(snapshot_path),
        expected_source_id=source.source_id(),
    )
    return replica


def append_and_publish(source, redis, stream_key, index):
    assert source.apply(make_bar(index)) == "inserted"
    event = source.read_outbox_batch(
        after_cursor=index,
        limit=1,
    )["events"][0]
    appender = RedisOhlcvStreamAppender(
        redis,
        stream_key=stream_key,
        source_id=source.source_id(),
    )
    return appender.append_confirmed(event)


def make_consumer(redis, replica, stream_key, consumer_name, *, idle_ms=0):
    return RedisOhlcvReplicaConsumer(
        redis,
        replica,
        stream_key=stream_key,
        consumer_name=consumer_name,
        pending_idle_ms=idle_ms,
        batch_size=10,
    )


def test_real_redis_consumer_applies_durably_then_acknowledges(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "replica.sqlite3")
    consumer = make_consumer(redis, replica, stream_key, "gateway-worker-1")
    try:
        assert append_and_publish(source, redis, stream_key, 0) == "appended"
        result = consumer.consume_once()
        assert result["applied"] == 1
        assert result["acknowledged"] == 1
        assert replica.checkpoint()["applied_cursor"] == 1
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0
        assert consumer.consume_once()["status"] == "idle"
    finally:
        redis.delete(stream_key)
        redis.close()


class _AckReplyLostRedis:
    def __init__(self, client):
        self.client = client
        self.fail_ack_once = True

    def __getattr__(self, name):
        return getattr(self.client, name)

    def xack(self, stream, group, message_id):
        if self.fail_ack_once:
            self.fail_ack_once = False
            raise ConnectionError("simulated ACK reply loss before ACK command")
        return self.client.xack(stream, group, message_id)


def test_real_redis_pending_reclaim_replays_after_durable_apply_before_ack(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "replica.sqlite3")
    first = make_consumer(
        _AckReplyLostRedis(redis), replica, stream_key, "gateway-worker-old",
    )
    restarted = make_consumer(redis, replica, stream_key, "gateway-worker-new")
    try:
        append_and_publish(source, redis, stream_key, 0)
        with pytest.raises(ConnectionError, match="ACK reply loss"):
            first.consume_once()
        assert replica.checkpoint()["applied_cursor"] == 1
        assert redis.xpending(stream_key, first.group_name)["pending"] == 1

        recovered = restarted.consume_once()
        assert recovered["reclaimed"] == 1
        assert recovered["duplicate"] == 1
        assert recovered["acknowledged"] == 1
        assert redis.xpending(stream_key, first.group_name)["pending"] == 0
        assert replica.checkpoint()["applied_cursor"] == 1
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_gap_stays_pending_until_snapshot_recovery(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "replica.sqlite3")
    consumer = make_consumer(redis, replica, stream_key, "gateway-gap-worker")
    try:
        # Deliberately publish cursor 2 without cursor 1.
        assert source.apply(make_bar(0)) == "inserted"
        assert source.apply(make_bar(1)) == "inserted"
        event = source.read_outbox_batch(after_cursor=1, limit=1)["events"][0]
        RedisOhlcvStreamAppender(
            redis, stream_key=stream_key, source_id=source.source_id(),
        ).append_confirmed(event)

        with pytest.raises(ReplicaResnapshotRequired, match="cursor_gap"):
            consumer.consume_once()
        assert replica.checkpoint()["applied_cursor"] == 0
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 1
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_each_gateway_has_an_independent_broadcast_group(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica_a = make_replica(source, snapshot_path, tmp_path / "replica-a.sqlite3")
    replica_b = make_replica(source, snapshot_path, tmp_path / "replica-b.sqlite3")
    consumer_a = make_consumer(redis, replica_a, stream_key, "gateway-a")
    consumer_b = make_consumer(redis, replica_b, stream_key, "gateway-b")
    try:
        append_and_publish(source, redis, stream_key, 0)
        assert consumer_a.group_name != consumer_b.group_name
        assert consumer_a.consume_once()["applied"] == 1
        assert consumer_b.consume_once()["applied"] == 1
        assert replica_a.checkpoint()["applied_cursor"] == 1
        assert replica_b.checkpoint()["applied_cursor"] == 1
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_group_reset_starts_after_installed_snapshot_watermark(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_zero = tmp_path / "snapshot-zero.jsonl"
    make_snapshot(source, snapshot_zero)
    replica = make_replica(source, snapshot_zero, tmp_path / "replica.sqlite3")
    consumer = make_consumer(redis, replica, stream_key, "gateway-reset-worker")
    try:
        append_and_publish(source, redis, stream_key, 0)
        assert consumer.consume_once()["applied"] == 1

        append_and_publish(source, redis, stream_key, 1)
        # Force an unconsumed entry to remain pending, then install a snapshot
        # that already includes it. Group reset must discard obsolete pending.
        consumer.redis.xreadgroup(
            consumer.group_name,
            consumer.consumer_name,
            {stream_key: ">"},
            count=1,
        )
        snapshot_one = tmp_path / "snapshot-one.jsonl"
        make_snapshot(source, snapshot_one)
        replica.install_global_snapshot(
            str(snapshot_one),
            expected_source_id=source.source_id(),
        )
        consumer.reset_group_after_snapshot()
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0

        append_and_publish(source, redis, stream_key, 2)
        result = consumer.consume_once()
        assert result["applied"] == 1
        assert replica.checkpoint()["applied_cursor"] == 3
    finally:
        redis.delete(stream_key)
        redis.close()
