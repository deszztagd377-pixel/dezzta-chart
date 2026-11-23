from __future__ import annotations

import asyncio
import json
import os
import select
import secrets
import socket
import threading
import time
import urllib.request
from urllib.parse import urlparse
import uuid

import pytest

from app.ohlcv import OhlcvBar
from app.ohlcv_store import SQLiteOhlcvReplicaStore, SQLiteOhlcvStore
from app.ohlcv_redis_publisher import RedisOhlcvStreamAppender
from app.ohlcv_redis_replay import (
    read_redis_replay_page, replay_replica_history, RedisReplayResnapshotRequired,
)
from app.ohlcv_event_loop import EventLoopCallbackDispatcher
from app.ohlcv_replica_bridge import (
    forward_replica_event, hydrate_replica_pipeline, subscribe_replica_snapshot,
)
from app.ohlcv import OhlcvPipeline
from app.ohlcv_stream import OhlcvStreamHub
from app.ohlcv_redis_worker import RedisOhlcvGatewayWorker
from app.ohlcv_redis_consumer import (
    RedisOhlcvReplicaConsumer,
    ReplicaResnapshotRequired,
)

from decimal import Decimal

NS = 1_000_000_000
STREAM_KEY = "dezzta:market-data:ohlcv:v1"


def make_bar(index=0, *, instrument_id=123, raw_symbol="ESZ6"):
    return OhlcvBar(
        provider="databento", dataset="GLBX.MDP3",
        publisher_id=1, instrument_id=instrument_id, series_type="contract",
        timeframe="1m", ts_start_ns=index * 60 * NS, raw_symbol=raw_symbol,
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


def make_consumer(
    redis, replica, stream_key, consumer_name, *, idle_ms=0, on_event_applied=None,
):
    return RedisOhlcvReplicaConsumer(
        redis,
        replica,
        stream_key=stream_key,
        consumer_name=consumer_name,
        pending_idle_ms=idle_ms,
        batch_size=10,
        on_event_applied=on_event_applied,
    )


class _PendingScanRedis:
    def __init__(self, autoclaim_responses):
        self.autoclaim_responses = list(autoclaim_responses)
        self.autoclaim_calls = []
        self.read_calls = []
        self.ack_calls = []

    def xgroup_create(self, stream, group, id, mkstream):
        return True

    def xreadgroup(self, group, consumer, streams, **kwargs):
        cursor = next(iter(streams.values()))
        self.read_calls.append(cursor)
        return []

    def xautoclaim(
        self, stream, group, consumer, min_idle_ms, *, start_id, count,
    ):
        self.autoclaim_calls.append(start_id)
        return self.autoclaim_responses.pop(0)

    def xack(self, *args):
        self.ack_calls.append(args)
        return 1


def test_consumer_requires_snapshot_when_xautoclaim_reports_deleted_pending_entry(
    tmp_path,
):
    source = SQLiteOhlcvStore(str(tmp_path / "deleted-pending-source.sqlite3"))
    snapshot_path = tmp_path / "deleted-pending-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(
        source, snapshot_path, tmp_path / "deleted-pending-replica.sqlite3",
    )
    redis = _PendingScanRedis([("0-0", [], ["1-0"])])
    consumer = make_consumer(
        redis, replica, "test:deleted-pending", "gateway-deleted-pending",
    )

    with pytest.raises(ReplicaResnapshotRequired, match="pending stream entries were deleted"):
        consumer.consume_once()

    assert redis.autoclaim_calls == ["0-0"]
    assert redis.read_calls == ["0"]
    assert redis.ack_calls == []
    assert replica.checkpoint()["applied_cursor"] == 0


def test_consumer_finishes_xautoclaim_scan_before_reading_new_stream_entries(
    tmp_path,
):
    source = SQLiteOhlcvStore(str(tmp_path / "pending-scan-source.sqlite3"))
    snapshot_path = tmp_path / "pending-scan-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(
        source, snapshot_path, tmp_path / "pending-scan-replica.sqlite3",
    )
    redis = _PendingScanRedis([
        ("5-0", [], []),
        ("0-0", [], []),
    ])
    consumer = make_consumer(
        redis, replica, "test:pending-scan", "gateway-pending-scan",
    )

    first = consumer.consume_once()
    assert first["status"] == "pending_scan"
    assert redis.autoclaim_calls == ["0-0"]
    assert redis.read_calls == ["0"]

    second = consumer.consume_once()
    assert second["status"] == "idle"
    assert redis.autoclaim_calls == ["0-0", "5-0"]
    assert redis.read_calls == ["0", "0", ">"]
    assert redis.ack_calls == []


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
        old_group_name = consumer.group_name
        snapshot_one = tmp_path / "snapshot-one.jsonl"
        make_snapshot(source, snapshot_one)
        replica.install_global_snapshot(
            str(snapshot_one),
            expected_source_id=source.source_id(),
        )
        class NoGroupDestroyRedis:
            def __getattr__(self, name):
                if name == "xgroup_destroy":
                    raise AssertionError("runtime consumer must not destroy Redis groups")
                return getattr(redis, name)

        consumer.redis = NoGroupDestroyRedis()
        consumer.reset_group_after_snapshot()
        assert consumer.group_name != old_group_name
        assert redis.xpending(stream_key, old_group_name)["pending"] == 1
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0

        append_and_publish(source, redis, stream_key, 2)
        result = consumer.consume_once()
        assert result["applied"] == 1
        assert replica.checkpoint()["applied_cursor"] == 3
    finally:
        redis.delete(stream_key)
        redis.close()



def _consume_gateway_process(redis_url, stream_key, replica_path, consumer_name, result_queue):
    import redis as redis_module

    client = redis_module.Redis.from_url(redis_url, decode_responses=True)
    try:
        replica = SQLiteOhlcvReplicaStore(replica_path)
        consumer = make_consumer(client, replica, stream_key, consumer_name)
        result = consumer.consume_once()
        result_queue.put({
            "result": result,
            "applied_cursor": replica.checkpoint()["applied_cursor"],
        })
    except BaseException as exc:
        result_queue.put({"error": repr(exc)})
        raise
    finally:
        client.close()


def _publish_source_process(redis_url, source_path, stream_key, owner, barrier, result_queue):
    import redis as redis_module

    from app.ohlcv_redis_publisher import (
        RedisOhlcvPublisher,
        SQLiteOhlcvPublisherCheckpoint,
    )

    client = redis_module.Redis.from_url(redis_url, decode_responses=True)
    try:
        source = SQLiteOhlcvStore(source_path)
        checkpoint = SQLiteOhlcvPublisherCheckpoint(
            source, stream_key=stream_key,
        )
        publisher = RedisOhlcvPublisher(
            source,
            checkpoint,
            client,
            owner=owner,
            lease_ttl_ms=10_000,
            batch_size=10,
        )
        barrier.wait(timeout=20)
        result_queue.put({"owner": owner, "result": publisher.publish_available()})
    except BaseException as exc:
        result_queue.put({"owner": owner, "error": repr(exc)})
        raise
    finally:
        client.close()


def test_two_independent_processes_broadcast_to_two_durable_gateway_replicas(tmp_path):
    import multiprocessing

    redis, stream_key = real_redis()
    redis_url = os.environ["REDIS_TEST_URL"]
    source = SQLiteOhlcvStore(str(tmp_path / "multi-process-source.sqlite3"))
    snapshot_path = tmp_path / "multi-process-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica_a_path = str(tmp_path / "gateway-a.sqlite3")
    replica_b_path = str(tmp_path / "gateway-b.sqlite3")
    make_replica(source, snapshot_path, replica_a_path)
    make_replica(source, snapshot_path, replica_b_path)
    append_and_publish(source, redis, stream_key, 0)

    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue()
    processes = [
        context.Process(
            target=_consume_gateway_process,
            args=(redis_url, stream_key, replica_a_path, "gateway-a-process", result_queue),
        ),
        context.Process(
            target=_consume_gateway_process,
            args=(redis_url, stream_key, replica_b_path, "gateway-b-process", result_queue),
        ),
    ]
    try:
        for process in processes:
            process.start()
        results = [result_queue.get(timeout=30) for _ in processes]
        for process in processes:
            process.join(timeout=30)
            assert process.exitcode == 0
        assert all("error" not in result for result in results)
        assert all(result["result"]["applied"] == 1 for result in results)
        assert all(result["applied_cursor"] == 1 for result in results)
        assert len({result["result"]["received"] for result in results}) == 1
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
        redis.delete(stream_key)
        redis.close()




def test_two_gateway_processes_switch_snapshot_generation_and_converge_at_next_cursor(tmp_path):
    import multiprocessing

    redis, stream_key = real_redis()
    redis_url = os.environ["REDIS_TEST_URL"]
    source = SQLiteOhlcvStore(str(tmp_path / "generation-source.sqlite3"))
    snapshot_zero = tmp_path / "generation-zero.jsonl"
    make_snapshot(source, snapshot_zero)

    replica_paths = [
        str(tmp_path / "generation-gateway-a.sqlite3"),
        str(tmp_path / "generation-gateway-b.sqlite3"),
    ]
    replicas = [
        make_replica(source, snapshot_zero, path)
        for path in replica_paths
    ]
    old_consumers = [
        make_consumer(redis, replicas[index], stream_key, f"generation-old-{index}")
        for index in range(2)
    ]
    old_groups = [consumer.group_name for consumer in old_consumers]

    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue()
    processes = []
    try:
        assert old_consumers[0].ensure_group() is True
        assert old_consumers[1].ensure_group() is True
        assert old_groups[0] != old_groups[1]

        # Both old-generation replicas apply cursor 1.
        assert append_and_publish(source, redis, stream_key, 0) == "appended"
        assert old_consumers[0].consume_once()["applied"] == 1
        assert old_consumers[1].consume_once()["applied"] == 1
        assert [replica.checkpoint()["applied_cursor"] for replica in replicas] == [1, 1]

        # Cursor 2 is delivered to, but deliberately left pending in, each old group.
        assert append_and_publish(source, redis, stream_key, 1) == "appended"
        for consumer in old_consumers:
            pending = redis.xreadgroup(
                consumer.group_name,
                consumer.consumer_name,
                {stream_key: ">"},
                count=1,
            )
            assert pending
            assert pending[0][1][0][0] == "2-0"
            assert redis.xpending(stream_key, consumer.group_name)["pending"] == 1

        # Install the same verified source snapshot/watermark (cursor 2) in both
        # independent durable replicas before either new-generation worker starts.
        snapshot_two = tmp_path / "generation-two.jsonl"
        make_snapshot(source, snapshot_two)
        for replica in replicas:
            replica.install_global_snapshot(
                str(snapshot_two),
                expected_source_id=source.source_id(),
            )
        assert [replica.checkpoint()["applied_cursor"] for replica in replicas] == [2, 2]

        new_consumers = [
            make_consumer(
                redis,
                SQLiteOhlcvReplicaStore(path),
                stream_key,
                f"generation-new-{index}",
            )
            for index, path in enumerate(replica_paths)
        ]
        new_groups = [consumer.group_name for consumer in new_consumers]
        assert all(new_groups[index] != old_groups[index] for index in range(2))
        assert new_groups[0] != new_groups[1]
        assert new_consumers[0].ensure_group() is True
        assert new_consumers[1].ensure_group() is True
        assert all(redis.xpending(stream_key, group)["pending"] == 0 for group in new_groups)

        # The next source cursor must be consumed by both independently spawned
        # processes from their new generation groups, while old pending stays isolated.
        assert append_and_publish(source, redis, stream_key, 2) == "appended"
        processes = [
            context.Process(
                target=_consume_gateway_process,
                args=(
                    redis_url,
                    stream_key,
                    replica_paths[index],
                    f"generation-process-{index}",
                    result_queue,
                ),
            )
            for index in range(2)
        ]
        for process in processes:
            process.start()

        results = [result_queue.get(timeout=30) for _ in processes]
        for process in processes:
            process.join(timeout=30)
            assert process.exitcode == 0

        assert all("error" not in result for result in results)
        assert all(result["result"]["applied"] == 1 for result in results)
        assert all(result["applied_cursor"] == 3 for result in results)
        assert [SQLiteOhlcvReplicaStore(path).checkpoint()["applied_cursor"] for path in replica_paths] == [3, 3]
        assert all(redis.xpending(stream_key, group)["pending"] == 1 for group in old_groups)
        assert all(redis.xpending(stream_key, group)["pending"] == 0 for group in new_groups)
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
        redis.delete(stream_key)
        redis.close()

def test_two_independent_publisher_processes_share_one_fenced_source_lease(tmp_path):
    import multiprocessing

    from app.ohlcv_redis_publisher import SQLiteOhlcvPublisherCheckpoint

    redis, stream_key = real_redis()
    redis_url = os.environ["REDIS_TEST_URL"]
    source_path = str(tmp_path / "multi-publisher-source.sqlite3")
    source = SQLiteOhlcvStore(source_path)
    checkpoint = SQLiteOhlcvPublisherCheckpoint(source, stream_key=stream_key)
    checkpoint.initialize_from_snapshot(0, now_ms=1_000)
    assert source.apply(make_bar(0)) == "inserted"

    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    result_queue = context.Queue()
    processes = [
        context.Process(
            target=_publish_source_process,
            args=(redis_url, source_path, stream_key, f"publisher-{index}", barrier, result_queue),
        )
        for index in range(2)
    ]
    try:
        for process in processes:
            process.start()
        results = [result_queue.get(timeout=30) for _ in processes]
        for process in processes:
            process.join(timeout=30)
            assert process.exitcode == 0
        assert all("error" not in result for result in results)
        assert sum(result["result"].get("published", 0) for result in results) == 1
        assert redis.xlen(stream_key) == 1
        assert redis.xrange(stream_key, min="-", max="+")[0][0] == "1-0"
        assert checkpoint.state()["published_cursor"] == 1
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
        redis.delete(stream_key)
        redis.close()


def test_real_redis_callback_failure_keeps_durable_event_pending_until_retry(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "replica.sqlite3")
    callback_calls = []

    def fail_once(event):
        callback_calls.append(event["cursor"])
        if len(callback_calls) == 1:
            raise RuntimeError("simulated local hub callback failure")

    first = make_consumer(
        redis, replica, stream_key, "gateway-callback-old",
        on_event_applied=fail_once,
    )
    recovered_events = []
    restarted = make_consumer(
        redis, replica, stream_key, "gateway-callback-new",
        on_event_applied=lambda event: recovered_events.append(event["cursor"]),
    )
    try:
        append_and_publish(source, redis, stream_key, 0)
        with pytest.raises(RuntimeError, match="local hub callback failure"):
            first.consume_once()

        # Replica durability is committed before callback, but Redis ACK is not.
        assert replica.checkpoint()["applied_cursor"] == 1
        assert redis.xpending(stream_key, first.group_name)["pending"] == 1
        assert callback_calls == [1]

        recovered = restarted.consume_once()
        assert recovered["reclaimed"] == 1
        assert recovered["duplicate"] == 1
        assert recovered["acknowledged"] == 1
        assert recovered_events == [1]
        assert redis.xpending(stream_key, first.group_name)["pending"] == 0
        assert replica.checkpoint()["applied_cursor"] == 1
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_callback_is_retried_after_ack_reply_loss(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "source.sqlite3"))
    snapshot_path = tmp_path / "snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "replica.sqlite3")
    first_notifications = []
    retry_notifications = []
    first = make_consumer(
        _AckReplyLostRedis(redis), replica, stream_key, "gateway-ack-loss-old",
        on_event_applied=lambda event: first_notifications.append(event["cursor"]),
    )
    restarted = make_consumer(
        redis, replica, stream_key, "gateway-ack-loss-new",
        on_event_applied=lambda event: retry_notifications.append(event["cursor"]),
    )
    try:
        append_and_publish(source, redis, stream_key, 0)
        with pytest.raises(ConnectionError, match="ACK reply loss"):
            first.consume_once()

        assert first_notifications == [1]
        assert replica.checkpoint()["applied_cursor"] == 1
        assert redis.xpending(stream_key, first.group_name)["pending"] == 1

        recovered = restarted.consume_once()
        assert recovered["reclaimed"] == 1
        assert recovered["duplicate"] == 1
        assert recovered["acknowledged"] == 1
        assert retry_notifications == [1]
        assert redis.xpending(stream_key, first.group_name)["pending"] == 0
        assert replica.checkpoint()["applied_cursor"] == 1
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_replay_pages_global_cursor_and_filters_exact_series(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "replay-source.sqlite3"))
    appender = RedisOhlcvStreamAppender(
        redis, stream_key=stream_key, source_id=source.source_id(),
    )
    identity = {
        "provider": "databento", "dataset": "GLBX.MDP3",
        "publisherId": 1, "instrumentId": 123,
        "seriesType": "contract", "rawSymbol": "ESZ6",
        "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
        "calendarId": "", "calendarVersion": "",
    }
    try:
        for index, bar in enumerate((
            make_bar(0),
            make_bar(1, instrument_id=999, raw_symbol="NQZ6"),
            make_bar(2),
        ), start=1):
            assert source.apply(bar) == "inserted"
            event = source.read_outbox_batch(
                after_cursor=index - 1, limit=1,
            )["events"][0]
            assert appender.append_confirmed(event) == "appended"

        first = read_redis_replay_page(
            redis, stream_key=stream_key, source_id=source.source_id(),
            after_cursor=0, through_cursor=3,
            series_identity=identity, scan_limit=2,
        )
        assert [event["cursor"] for event in first["events"]] == [1]
        assert first["next_cursor"] == 2
        assert first["has_more"] is True

        second = read_redis_replay_page(
            redis, stream_key=stream_key, source_id=source.source_id(),
            after_cursor=first["next_cursor"], through_cursor=3,
            series_identity=identity, scan_limit=2,
        )
        assert [event["cursor"] for event in second["events"]] == [3]
        assert second["next_cursor"] == 3
        assert second["has_more"] is False

        redis.xdel(stream_key, "2-0")
        with pytest.raises(RedisReplayResnapshotRequired, match="expected 2"):
            read_redis_replay_page(
                redis, stream_key=stream_key, source_id=source.source_id(),
                after_cursor=0, through_cursor=3,
                series_identity=identity, scan_limit=10,
            )
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_consumer_dispatches_hub_callback_on_owner_event_loop(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "event-loop-source.sqlite3"))
    snapshot_path = tmp_path / "event-loop-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(
        source, snapshot_path, tmp_path / "event-loop-replica.sqlite3",
    )
    pipeline = OhlcvPipeline()
    hydration = hydrate_replica_pipeline(replica, pipeline)
    hub = OhlcvStreamHub()
    subscription, snapshot_bars, _ = hub.subscribe_snapshot(
        pipeline,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", limit=10,
        durable_cursor=hydration["applied_cursor"],
    )
    assert snapshot_bars == []

    append_and_publish(source, redis, stream_key, 0)

    async def scenario():
        loop = asyncio.get_running_loop()
        dispatcher = EventLoopCallbackDispatcher(
            loop, lambda event: forward_replica_event(event, pipeline, hub),
        )
        consumer = make_consumer(
            redis, replica, stream_key, "gateway-event-loop-worker",
            on_event_applied=dispatcher.dispatch,
        )
        return await asyncio.to_thread(consumer.consume_once)

    try:
        result = asyncio.run(scenario())
        assert result["applied"] == 1
        assert result["acknowledged"] == 1
        assert replica.checkpoint()["applied_cursor"] == 1
        assert subscription.queue.qsize() == 1
        message = subscription.queue.get_nowait()
        assert message["cursor"] == "1"
        assert message["eventId"]
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_relay_acl_separates_publisher_and_gateway_permissions(tmp_path):
    admin, stream_key = real_redis()
    redis_module = pytest.importorskip("redis")
    publisher_user = "dezzta-publisher-" + uuid.uuid4().hex[:12]
    gateway_user = "dezzta-gateway-" + uuid.uuid4().hex[:12]
    publisher_password = secrets.token_urlsafe(24)
    gateway_password = secrets.token_urlsafe(24)
    other_key = stream_key + ":outside"
    publisher = gateway = None
    try:
        admin.execute_command(
            "ACL", "SETUSER", publisher_user, "reset", "on",
            ">" + publisher_password, "~" + stream_key,
            "+xadd", "+xrange",
        )
        admin.execute_command(
            "ACL", "SETUSER", gateway_user, "reset", "on",
            ">" + gateway_password, "~" + stream_key,
            "~dezzta:ohlcv:gateway-lease:*",
            "+xgroup|create", "+xautoclaim", "+xreadgroup",
            "+xack", "+xrange", "+set", "+eval", "+get", "+pexpire", "+del",
        )
        redis_url = os.environ["REDIS_TEST_URL"]
        publisher = redis_module.Redis.from_url(
            redis_url, username=publisher_user, password=publisher_password,
            decode_responses=True,
        )
        gateway = redis_module.Redis.from_url(
            redis_url, username=gateway_user, password=gateway_password,
            decode_responses=True,
        )

        source = SQLiteOhlcvStore(str(tmp_path / "acl-source.sqlite3"))
        snapshot_path = tmp_path / "acl-snapshot.jsonl"
        make_snapshot(source, snapshot_path)
        replica = make_replica(
            source, snapshot_path, tmp_path / "acl-replica.sqlite3",
        )
        assert source.apply(make_bar(0)) == "inserted"
        event = source.read_outbox_batch(after_cursor=0, limit=1)["events"][0]

        appender = RedisOhlcvStreamAppender(
            publisher, stream_key=stream_key, source_id=source.source_id(),
        )
        assert appender.append_confirmed(event) == "appended"

        consumer = make_consumer(
            gateway, replica, stream_key, "acl-gateway-worker",
        )
        from app.ohlcv_redis_lease import RedisOhlcvConsumerLease
        lease = RedisOhlcvConsumerLease(gateway, group_name=consumer.group_name)
        lease.acquire()
        consumer.ownership_guard = lease
        consumer.ensure_group()
        result = consumer.consume_once()
        assert result["applied"] == 1
        assert result["acknowledged"] == 1
        assert replica.checkpoint()["applied_cursor"] == 1

        identity = {
            "provider": "databento", "dataset": "GLBX.MDP3",
            "publisherId": 1, "instrumentId": 123,
            "seriesType": "contract", "rawSymbol": "ESZ6",
            "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
            "calendarId": "", "calendarVersion": "",
        }
        replay = replay_replica_history(
            gateway, stream_key=stream_key,
            checkpoint=replica.checkpoint(), after_cursor=0,
            series_identity=identity,
        )
        assert replay["status"] == "ok"
        assert [item["cursor"] for item in replay["events"]] == [1]

        no_permission = redis_module.exceptions.NoPermissionError
        with pytest.raises(no_permission):
            publisher.xgroup_create(stream_key, "unauthorized-publisher", id="0-0")
        with pytest.raises(no_permission):
            gateway.xadd(stream_key, {"unauthorized": "publisher-command"})
        with pytest.raises(no_permission):
            gateway.xgroup_destroy(stream_key, consumer.group_name)
        with pytest.raises(no_permission):
            publisher.xadd(other_key, {"outside": "publisher-key"})
        with pytest.raises(no_permission):
            gateway.xrange(other_key)
    finally:
        if publisher is not None:
            publisher.close()
        if gateway is not None:
            if "lease" in locals():
                lease.release()
            gateway.close()
        admin.execute_command("ACL", "DELUSER", publisher_user, gateway_user)
        admin.delete(stream_key, other_key)
        admin.close()


def test_real_redis_lease_loss_after_apply_prevents_ack(tmp_path):
    from app.ohlcv_redis_lease import RedisOhlcvConsumerLeaseLost

    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "lease-loss-source.sqlite3"))
    snapshot_path = tmp_path / "lease-loss-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "lease-loss-replica.sqlite3")

    class LoseOwnershipBeforeAck:
        def __init__(self):
            self.checks = 0

        def assert_owned(self):
            self.checks += 1
            if self.checks == 2:
                raise RedisOhlcvConsumerLeaseLost("simulated lease loss")

    consumer = make_consumer(redis, replica, stream_key, "lease-loss-worker")
    consumer.ownership_guard = LoseOwnershipBeforeAck()
    try:
        append_and_publish(source, redis, stream_key, 0)
        with pytest.raises(RedisOhlcvConsumerLeaseLost):
            consumer.consume_once()
        assert replica.checkpoint()["applied_cursor"] == 1
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 1
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_retries_same_consumers_pending_before_reading_new_cursor(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "same-consumer-pending-source.sqlite3"))
    snapshot_path = tmp_path / "same-consumer-pending-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(
        source, snapshot_path, tmp_path / "same-consumer-pending-replica.sqlite3",
    )
    callback_calls = []

    def callback(event):
        callback_calls.append(event["cursor"])
        if len(callback_calls) == 1:
            raise RuntimeError("transient same-consumer callback failure")

    consumer = make_consumer(
        redis, replica, stream_key, "same-consumer-retry-worker",
        idle_ms=30_000, on_event_applied=callback,
    )
    try:
        append_and_publish(source, redis, stream_key, 0)
        with pytest.raises(RuntimeError, match="same-consumer callback failure"):
            consumer.consume_once()
        assert replica.checkpoint()["applied_cursor"] == 1
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 1

        # Cursor 2 is available, but cursor 1 must be retried first even though
        # the pending idle threshold has not elapsed.
        append_and_publish(source, redis, stream_key, 1)
        retry = consumer.consume_once()
        assert retry["reclaimed"] == 1
        assert retry["duplicate"] == 1
        assert retry["acknowledged"] == 1
        assert replica.checkpoint()["applied_cursor"] == 1
        assert callback_calls == [1, 1]
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0

        next_event = consumer.consume_once()
        assert next_event["applied"] == 1
        assert next_event["acknowledged"] == 1
        assert replica.checkpoint()["applied_cursor"] == 2
        assert callback_calls == [1, 1, 2]
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_gateway_worker_dispatches_and_shuts_down_cleanly(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "managed-worker-source.sqlite3"))
    snapshot_path = tmp_path / "managed-worker-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(
        source, snapshot_path, tmp_path / "managed-worker-replica.sqlite3",
    )
    pipeline = OhlcvPipeline()
    hub = OhlcvStreamHub()
    subscription, snapshot_bars, total, checkpoint = subscribe_replica_snapshot(
        replica, hub,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", bucket_policy="UTC_LEGACY",
        limit=10,
    )
    assert snapshot_bars == [] and total == 0 and checkpoint["cursor"] == 0
    append_and_publish(source, redis, stream_key, 0)

    async def scenario():
        loop = asyncio.get_running_loop()
        dispatcher = EventLoopCallbackDispatcher(
            loop, lambda event: forward_replica_event(event, pipeline, hub),
        )
        consumer = make_consumer(
            redis, replica, stream_key, "managed-gateway-worker", idle_ms=0,
        )
        worker = RedisOhlcvGatewayWorker(
            consumer, dispatcher, poll_interval_seconds=0.01,
        )
        worker.start()
        try:
            message = await asyncio.wait_for(subscription.queue.get(), timeout=3)
            assert message["cursor"] == "1"
            assert message["eventId"]
            assert replica.checkpoint()["applied_cursor"] == 1
        finally:
            assert await worker.stop_async(timeout_seconds=3)
        assert worker.state["state"] == "stopped"
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0

    try:
        asyncio.run(scenario())
    finally:
        redis.delete(stream_key)
        redis.close()


class _TransientRedisReadOutage:
    """Inject one temporary Redis read outage while preserving the real Redis client."""

    def __init__(self, client):
        self.client = client
        self.failed_once = False

    def __getattr__(self, name):
        return getattr(self.client, name)

    def xreadgroup(self, *args, **kwargs):
        if not self.failed_once:
            self.failed_once = True
            raise ConnectionError("simulated transient Redis outage")
        return self.client.xreadgroup(*args, **kwargs)


def test_real_redis_worker_recovers_after_transient_connection_outage(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "outage-source.sqlite3"))
    snapshot_path = tmp_path / "outage-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(source, snapshot_path, tmp_path / "outage-replica.sqlite3")
    pipeline = OhlcvPipeline()
    hub = OhlcvStreamHub()
    subscription, _, _, _ = subscribe_replica_snapshot(
        replica, hub,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", bucket_policy="UTC_LEGACY",
        limit=10,
    )
    append_and_publish(source, redis, stream_key, 0)

    async def scenario():
        loop = asyncio.get_running_loop()
        dispatcher = EventLoopCallbackDispatcher(
            loop, lambda event: forward_replica_event(event, pipeline, hub),
        )
        consumer = make_consumer(
            _TransientRedisReadOutage(redis), replica, stream_key,
            "gateway-transient-outage", idle_ms=0,
        )
        worker = RedisOhlcvGatewayWorker(
            consumer, dispatcher,
            poll_interval_seconds=0.01,
            initial_backoff_seconds=0.01,
            max_backoff_seconds=0.05,
        )
        worker.start()
        try:
            message = await asyncio.wait_for(subscription.queue.get(), timeout=5)
            assert message["cursor"] == "1"
            assert replica.checkpoint()["applied_cursor"] == 1
            assert consumer.redis.failed_once is True
        finally:
            assert await worker.stop_async(timeout_seconds=3)
        assert worker.state["state"] == "stopped"
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0

    try:
        asyncio.run(scenario())
    finally:
        redis.delete(stream_key)
        redis.close()


def test_real_redis_snapshot_replay_live_handoff_preserves_boundary_sequence(tmp_path):
    redis, stream_key = real_redis()
    source = SQLiteOhlcvStore(str(tmp_path / "handoff-source.sqlite3"))
    first = make_bar(0)
    assert source.apply(first) == "inserted"
    first_event = source.read_outbox_batch(after_cursor=0, limit=1)["events"][0]
    appender = RedisOhlcvStreamAppender(
        redis, stream_key=stream_key, source_id=source.source_id(),
    )
    assert appender.append_confirmed(first_event) == "appended"

    snapshot_path = tmp_path / "handoff-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica = make_replica(
        source, snapshot_path, tmp_path / "handoff-replica.sqlite3",
    )
    pipeline = OhlcvPipeline()
    hydrate_replica_pipeline(replica, pipeline)
    hub = OhlcvStreamHub()
    subscription, snapshot_bars, total, snapshot_meta = subscribe_replica_snapshot(
        replica, hub,
        dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", timeframe="1m", bucket_policy="UTC_LEGACY",
        limit=10,
    )
    assert [bar.close for bar in snapshot_bars] == [Decimal("101")]
    assert total == 1
    assert snapshot_meta["cursor"] == 1
    replay_checkpoint = replica.checkpoint()

    second = make_bar(1)
    assert source.apply(second) == "inserted"
    second_event = source.read_outbox_batch(after_cursor=1, limit=1)["events"][0]
    assert appender.append_confirmed(second_event) == "appended"

    async def scenario():
        loop = asyncio.get_running_loop()
        dispatcher = EventLoopCallbackDispatcher(
            loop, lambda event: forward_replica_event(event, pipeline, hub),
        )
        consumer = make_consumer(
            redis, replica, stream_key, "snapshot-replay-live-worker", idle_ms=0,
        )
        worker = RedisOhlcvGatewayWorker(
            consumer, dispatcher, poll_interval_seconds=0.01,
        )
        worker.start()
        try:
            replay = await asyncio.to_thread(
                replay_replica_history,
                redis,
                stream_key=stream_key,
                checkpoint=replay_checkpoint,
                after_cursor=0,
                series_identity={
                    "provider": "databento", "dataset": "GLBX.MDP3",
                    "publisherId": 1, "instrumentId": 123,
                    "seriesType": "contract", "rawSymbol": "ESZ6",
                    "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
                    "calendarId": "", "calendarVersion": "",
                },
            )
            assert replay["status"] == "ok"
            assert [event["cursor"] for event in replay["events"]] == [1]
            deadline = asyncio.get_running_loop().time() + 3
            while subscription.queue.empty() and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.01)
            assert not subscription.queue.empty()
            merged = hub.merge_replay_boundary(
                subscription, replay["events"], replay["next_cursor"],
            )
            assert merged == 1
            live = subscription.queue.get_nowait()
            assert live["cursor"] == "2"
            assert live["sequence"] == 2
            assert live["eventId"] == second_event["eventId"]
            assert subscription.durable_cursor == 2
        finally:
            assert await worker.stop_async(timeout_seconds=3)
        assert replica.checkpoint()["applied_cursor"] == 2
        assert redis.xpending(stream_key, consumer.group_name)["pending"] == 0

    try:
        asyncio.run(scenario())
    finally:
        redis.delete(stream_key)
        redis.close()


class _FailOnceXReadGroupRedis:
    """Inject one transient read failure for one independent gateway process."""

    def __init__(self, client, marker_key):
        self.client = client
        self.marker_key = marker_key
        self.failed = False

    def __getattr__(self, name):
        return getattr(self.client, name)

    def xreadgroup(self, *args, **kwargs):
        if not self.failed:
            self.failed = True
            self.client.set(self.marker_key, "triggered", ex=120)
            raise ConnectionError("simulated transient Redis read outage")
        result = self.client.xreadgroup(*args, **kwargs)
        if not getattr(self, "recovered", False):
            self.recovered = True
            self.client.set(f"{self.marker_key}:recovered", "1", ex=120)
        return result


def _run_asgi_replica_gateway_process(
    redis_url, stream_key, replica_path, registry_path, consumer_name, port,
    transient_read_failure_marker=None,
):
    import redis as redis_module
    import uvicorn

    from app.config import Settings
    from app.identity import IdentityVerificationError, VerifiedPrincipal
    from app.main import create_app
    from app.ohlcv_redis_consumer import RedisOhlcvReplicaConsumer
    from app.instrument_identity import CanonicalInstrument
    from app.instrument_registry import ProviderInstrumentMapping

    replica = SQLiteOhlcvReplicaStore(replica_path)
    redis_client = redis_module.Redis.from_url(
        redis_url, decode_responses=True, socket_connect_timeout=3, socket_timeout=3,
    )
    runtime_redis_client = (
        _FailOnceXReadGroupRedis(redis_client, transient_read_failure_marker)
        if transient_read_failure_marker is not None
        else redis_client
    )
    consumer = RedisOhlcvReplicaConsumer(
        runtime_redis_client, replica, stream_key=stream_key,
        consumer_name=consumer_name, pending_idle_ms=0, batch_size=10,
    )
    settings = Settings(
        app_env="development",
        market_data_ws_token="multi-asgi-process-test-token",
        cors_allowed_origins=("http://localhost",),
        allowed_roots=("ES",),
        instrument_registry_db_path=registry_path,
    )
    application = create_app(
        settings,
        replica_runtime_factory=lambda: {
            "replica_store": replica,
            "consumer": consumer,
            "redis_client": runtime_redis_client,
            "stream_key": stream_key,
        },
    )

    class ProcessTestVerifier:
        def verify(self, token):
            if token != "multi-asgi-process-token":
                raise IdentityVerificationError("invalid process test token")
            return VerifiedPrincipal(
                subject="multi-asgi-test-user",
                issuer="https://securetoken.google.com/process-test",
                audience="process-test",
                auth_time=1_798_000_000,
            )

    application.state.identity_verifier = ProcessTestVerifier()
    canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
    instrument = CanonicalInstrument(
        canonical_id=canonical_id, asset_class="future", instrument_type="future",
        symbol="ESZ6", venue="XCME", expiration_date="2026-12-18",
        settlement_currency="USD", contract_multiplier="50", tick_size="0.25",
        session_calendar_id="CME_EQUITY_INDEX",
    )
    mapping = ProviderInstrumentMapping(
        provider="databento", dataset="GLBX.MDP3", publisher_id=1, instrument_id=123,
        raw_symbol="ESZ6", valid_from_ns=1, valid_to_ns=None, canonical_id=canonical_id,
    )
    application.state.instrument_registry.register_instrument_with_mapping(instrument, mapping)
    application.state.instrument_entitlements.grant(
        subject="multi-asgi-test-user", canonical_instrument_id=canonical_id,
    )
    uvicorn.run(
        application, host="127.0.0.1", port=port, log_level="critical",
        access_log=False, lifespan="on",
    )


def _free_loopback_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _wait_for_asgi_health(process, port, timeout_seconds=20):
    deadline = time.monotonic() + timeout_seconds
    url = f"http://127.0.0.1:{port}/health"
    while time.monotonic() < deadline:
        if process.exitcode is not None:
            raise RuntimeError(f"ASGI gateway process exited early: {process.exitcode}")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise TimeoutError(f"ASGI gateway on port {port} did not become healthy.")



class _RedisTcpFaultProxy:
    """A local TCP forwarder that can sever/reject one gateway's Redis path."""

    def __init__(self, target_host, target_port):
        self.target = (target_host, target_port)
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(16)
        self._listener.settimeout(0.1)
        self.port = int(self._listener.getsockname()[1])
        self._stop = threading.Event()
        self._outage = threading.Event()
        self._lock = threading.Lock()
        self._active = set()
        self._rejected = 0
        self._severed = 0
        self._accept_thread = threading.Thread(
            target=self._accept_loop, name="redis-tcp-fault-proxy", daemon=True,
        )

    @property
    def url(self):
        return f"redis://127.0.0.1:{self.port}/0"

    @property
    def active_connections(self):
        with self._lock:
            return len(self._active)

    @property
    def rejected_connections(self):
        with self._lock:
            return self._rejected

    @property
    def severed_connections(self):
        with self._lock:
            return self._severed

    def start(self):
        self._accept_thread.start()

    def _accept_loop(self):
        while not self._stop.is_set():
            try:
                client, _ = self._listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            if self._outage.is_set():
                with self._lock:
                    self._rejected += 1
                client.close()
                continue
            threading.Thread(
                target=self._bridge, args=(client,), daemon=True,
            ).start()

    def _bridge(self, client):
        upstream = None
        pair = None
        try:
            if self._outage.is_set():
                with self._lock:
                    self._rejected += 1
                return
            upstream = socket.create_connection(self.target, timeout=3)
            client.setblocking(False)
            upstream.setblocking(False)
            pair = (client, upstream)
            with self._lock:
                if self._outage.is_set():
                    self._rejected += 1
                    return
                self._active.add(pair)

            while not self._stop.is_set() and not self._outage.is_set():
                readable, _, exceptional = select.select(
                    [client, upstream], [], [client, upstream], 0.05,
                )
                if exceptional:
                    break
                for current in readable:
                    data = current.recv(65536)
                    if not data:
                        return
                    destination = upstream if current is client else client
                    destination.sendall(data)
        except (OSError, ConnectionError):
            pass
        finally:
            if pair is not None:
                with self._lock:
                    self._active.discard(pair)
            for connection in (client, upstream):
                if connection is not None:
                    try:
                        connection.close()
                    except OSError:
                        pass

    def set_outage(self, enabled):
        if enabled:
            self._outage.set()
            with self._lock:
                active = list(self._active)
                self._severed += len(active)
            for pair in active:
                for connection in pair:
                    try:
                        connection.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    try:
                        connection.close()
                    except OSError:
                        pass
        else:
            self._outage.clear()

    def close(self):
        self._stop.set()
        self.set_outage(True)
        try:
            self._listener.close()
        except OSError:
            pass
        self._accept_thread.join(timeout=2)


def test_two_asgi_gateways_recover_after_real_redis_tcp_path_interruption(tmp_path):
    import multiprocessing
    from websockets.sync.client import connect

    redis, stream_key = real_redis()
    redis_url = os.environ["REDIS_TEST_URL"]
    parsed = urlparse(redis_url)
    assert parsed.scheme == "redis"
    assert parsed.hostname
    assert parsed.username is None and parsed.password is None
    assert parsed.path in {"", "/0"}

    proxies = [
        _RedisTcpFaultProxy(parsed.hostname, parsed.port or 6379)
        for _ in range(2)
    ]
    for proxy in proxies:
        proxy.start()

    source = SQLiteOhlcvStore(str(tmp_path / "tcp-outage-source.sqlite3"))
    snapshot_path = tmp_path / "tcp-outage-empty-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica_paths = [
        str(tmp_path / "tcp-outage-gateway-a.sqlite3"),
        str(tmp_path / "tcp-outage-gateway-b.sqlite3"),
    ]
    registry_paths = [
        str(tmp_path / "tcp-outage-gateway-a-registry.sqlite3"),
        str(tmp_path / "tcp-outage-gateway-b-registry.sqlite3"),
    ]
    for path in replica_paths:
        make_replica(source, snapshot_path, path)

    ports = [_free_loopback_port(), _free_loopback_port()]
    context = multiprocessing.get_context("spawn")
    processes = [
        context.Process(
            target=_run_asgi_replica_gateway_process,
            args=(
                proxies[index].url,
                stream_key,
                replica_paths[index],
                registry_paths[index],
                f"tcp-outage-gateway-{index}",
                ports[index],
            ),
        )
        for index in range(2)
    ]
    sockets = []
    try:
        for process in processes:
            process.start()
        for process, port in zip(processes, ports):
            _wait_for_asgi_health(process, port)

        canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
        for port in ports:
            websocket = connect(
                f"ws://127.0.0.1:{port}/ws/market-data",
                open_timeout=10, close_timeout=3, ping_interval=None, legacy=True,
            )
            sockets.append(websocket)
            websocket.send(json.dumps({
                "type": "auth", "token": "multi-asgi-process-token",
            }))
            status = json.loads(websocket.recv(timeout=10))
            assert status["type"] == "market_data.status"
            assert status["quality"]["state"] == "connected"
            websocket.send(json.dumps({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": canonical_id,
                "series": {
                    "dataset": "GLBX.MDP3", "publisherId": 1,
                    "instrumentId": 123, "rawSymbol": "ESZ6",
                    "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
                },
            }))
            snapshot = json.loads(websocket.recv(timeout=10))
            assert snapshot["type"] == "market_data.ohlcv.snapshot"
            assert snapshot["cursor"] == "0"

        # Wait until each ASGI process has an established TCP connection through
        # its own proxy before cutting both Redis paths at the network boundary.
        active_deadline = time.monotonic() + 10
        while time.monotonic() < active_deadline:
            if all(proxy.active_connections > 0 for proxy in proxies):
                break
            time.sleep(0.02)
        assert all(proxy.active_connections > 0 for proxy in proxies)

        for proxy in proxies:
            proxy.set_outage(True)

        # The proxies sever existing sockets and reject reconnect attempts. This
        # proves the gateway Redis clients observe a real TCP path interruption.
        outage_deadline = time.monotonic() + 10
        while time.monotonic() < outage_deadline:
            if all(proxy.rejected_connections > 0 for proxy in proxies):
                break
            time.sleep(0.02)
        assert all(proxy.severed_connections > 0 for proxy in proxies)
        assert all(proxy.rejected_connections > 0 for proxy in proxies)

        for proxy in proxies:
            proxy.set_outage(False)

        assert append_and_publish(source, redis, stream_key, 0) == "appended"
        updates = [json.loads(websocket.recv(timeout=20)) for websocket in sockets]
        assert all(update["type"] == "market_data.ohlcv.update" for update in updates)
        assert [update["cursor"] for update in updates] == ["1", "1"]
        assert all(
            SQLiteOhlcvReplicaStore(path).checkpoint()["applied_cursor"] == 1
            for path in replica_paths
        )
        assert all(process.is_alive() for process in processes)
    finally:
        for websocket in sockets:
            try:
                websocket.close()
            except Exception:
                pass
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=10)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)
        for proxy in proxies:
            proxy.close()
        redis.delete(stream_key)
        redis.close()


def test_two_independent_asgi_processes_broadcast_replica_live_event(tmp_path):
    import multiprocessing
    from websockets.sync.client import connect

    redis, stream_key = real_redis()
    redis_url = os.environ["REDIS_TEST_URL"]
    source = SQLiteOhlcvStore(str(tmp_path / "asgi-source.sqlite3"))
    snapshot_path = tmp_path / "asgi-empty-snapshot.jsonl"
    make_snapshot(source, snapshot_path)
    replica_paths = [
        str(tmp_path / "asgi-gateway-a.sqlite3"),
        str(tmp_path / "asgi-gateway-b.sqlite3"),
    ]
    registry_paths = [
        str(tmp_path / "asgi-gateway-a-registry.sqlite3"),
        str(tmp_path / "asgi-gateway-b-registry.sqlite3"),
    ]
    for path in replica_paths:
        make_replica(source, snapshot_path, path)
    ports = [_free_loopback_port(), _free_loopback_port()]
    context = multiprocessing.get_context("spawn")
    processes = [
        context.Process(
            target=_run_asgi_replica_gateway_process,
            args=(
                redis_url, stream_key, replica_paths[index], registry_paths[index],
                f"asgi-gateway-{index}", ports[index],
                f"{stream_key}:transient-read-failure:{index}",
            ),
        )
        for index in range(2)
    ]
    sockets = []
    outage_markers = [
        f"{stream_key}:transient-read-failure:{index}" for index in range(2)
    ]
    recovery_markers = [f"{marker}:recovered" for marker in outage_markers]
    try:
        for process in processes:
            process.start()
        for process, port in zip(processes, ports):
            _wait_for_asgi_health(process, port)

        # Both independent gateway processes must encounter the injected Redis
        # read failure before the source publishes the next durable cursor.
        marker_deadline = time.monotonic() + 10
        while time.monotonic() < marker_deadline:
            if all(redis.exists(marker) for marker in outage_markers) and all(
                redis.exists(marker) for marker in recovery_markers
            ):
                break
            time.sleep(0.02)
        assert all(redis.exists(marker) for marker in outage_markers)
        assert all(redis.exists(marker) for marker in recovery_markers)

        canonical_id = "0b6c5b4e-35d7-4d2f-9f6b-8c2f5f9d7a11"
        for port in ports:
            websocket = connect(
                f"ws://127.0.0.1:{port}/ws/market-data",
                open_timeout=10, close_timeout=3, ping_interval=None, legacy=True,
            )
            sockets.append(websocket)
            websocket.send(json.dumps({
                "type": "auth", "token": "multi-asgi-process-token",
            }))
            status = json.loads(websocket.recv(timeout=10))
            assert status["type"] == "market_data.status"
            assert status["quality"]["state"] == "connected"
            websocket.send(json.dumps({
                "type": "market_data.subscribe",
                "version": 1,
                "canonicalInstrumentId": canonical_id,
                "series": {
                    "dataset": "GLBX.MDP3", "publisherId": 1,
                    "instrumentId": 123, "rawSymbol": "ESZ6",
                    "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
                },
            }))
            snapshot = json.loads(websocket.recv(timeout=10))
            assert snapshot["type"] == "market_data.ohlcv.snapshot"
            assert snapshot["cursor"] == "0"

        assert append_and_publish(source, redis, stream_key, 0) == "appended"
        updates = [json.loads(websocket.recv(timeout=15)) for websocket in sockets]
        assert all(update["type"] == "market_data.ohlcv.update" for update in updates)
        assert [update["cursor"] for update in updates] == ["1", "1"]
        assert all(update["series"]["rawSymbol"] == "ESZ6" for update in updates)
        assert all(
            SQLiteOhlcvReplicaStore(path).checkpoint()["applied_cursor"] == 1
            for path in replica_paths
        )

        # Reconnect with an older durable cursor and exercise the replica Redis
        # replay path through the second, real WebSocket subscription.
        replay_ws = connect(
            f"ws://127.0.0.1:{ports[0]}/ws/market-data",
            open_timeout=10, close_timeout=3, ping_interval=None, legacy=True,
        )
        sockets.append(replay_ws)
        replay_ws.send(json.dumps({
            "type": "auth", "token": "multi-asgi-process-token",
        }))
        replay_status = json.loads(replay_ws.recv(timeout=10))
        assert replay_status["type"] == "market_data.status"
        replay_ws.send(json.dumps({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": canonical_id,
            "cursor": "0",
            "series": {
                "dataset": "GLBX.MDP3", "publisherId": 1,
                "instrumentId": 123, "rawSymbol": "ESZ6",
                "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
            },
        }))
        replay_started = json.loads(replay_ws.recv(timeout=10))
        replay_event = json.loads(replay_ws.recv(timeout=10))
        replay_complete = json.loads(replay_ws.recv(timeout=10))
        assert replay_started["type"] == "market_data.ohlcv.replay_started"
        assert replay_started["fromCursor"] == "0"
        assert replay_started["throughCursor"] == "1"
        assert replay_event["type"] == "market_data.ohlcv.update"
        assert replay_event["cursor"] == "1"
        assert replay_event["replayed"] is True
        assert replay_complete["type"] == "market_data.ohlcv.replay_complete"
        assert replay_complete["cursor"] == "1"

        # Restart one real ASGI gateway without replacing its durable replica DB.
        # The restarted process must bootstrap from cursor 1 and continue at 2.
        processes[0].terminate()
        processes[0].join(timeout=10)
        assert not processes[0].is_alive()
        processes[0] = context.Process(
            target=_run_asgi_replica_gateway_process,
            args=(
                redis_url, stream_key, replica_paths[0], registry_paths[0],
                "asgi-gateway-0-restarted", ports[0],
            ),
        )
        processes[0].start()
        _wait_for_asgi_health(processes[0], ports[0])

        restarted_ws = connect(
            f"ws://127.0.0.1:{ports[0]}/ws/market-data",
            open_timeout=10, close_timeout=3, ping_interval=None, legacy=True,
        )
        sockets.append(restarted_ws)
        restarted_ws.send(json.dumps({
            "type": "auth", "token": "multi-asgi-process-token",
        }))
        restarted_status = json.loads(restarted_ws.recv(timeout=10))
        assert restarted_status["type"] == "market_data.status"
        restarted_ws.send(json.dumps({
            "type": "market_data.subscribe",
            "version": 1,
            "canonicalInstrumentId": canonical_id,
            "cursor": "1",
            "series": {
                "dataset": "GLBX.MDP3", "publisherId": 1,
                "instrumentId": 123, "rawSymbol": "ESZ6",
                "timeframe": "1m", "bucketPolicy": "UTC_LEGACY",
            },
        }))
        restarted_replay_started = json.loads(restarted_ws.recv(timeout=10))
        restarted_replay_complete = json.loads(restarted_ws.recv(timeout=10))
        assert restarted_replay_started["type"] == "market_data.ohlcv.replay_started"
        assert restarted_replay_started["fromCursor"] == "1"
        assert restarted_replay_started["throughCursor"] == "1"
        assert restarted_replay_complete["type"] == "market_data.ohlcv.replay_complete"
        assert restarted_replay_complete["cursor"] == "1"

        assert append_and_publish(source, redis, stream_key, 1) == "appended"
        continued_updates = [
            json.loads(restarted_ws.recv(timeout=15)),
            json.loads(sockets[1].recv(timeout=15)),
        ]
        assert all(item["type"] == "market_data.ohlcv.update" for item in continued_updates)
        assert [item["cursor"] for item in continued_updates] == ["2", "2"]
        assert all(
            SQLiteOhlcvReplicaStore(path).checkpoint()["applied_cursor"] == 2
            for path in replica_paths
        )
    finally:
        for websocket in sockets:
            try:
                websocket.close()
            except Exception:
                pass
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=10)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)
        redis.delete(stream_key, *outage_markers, *recovery_markers)
        redis.close()

