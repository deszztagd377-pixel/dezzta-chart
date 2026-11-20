from __future__ import annotations

import asyncio
import json
import os
import secrets
import socket
import time
import urllib.request
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
            "+xgroup|create", "+xautoclaim", "+xreadgroup",
            "+xack", "+xrange",
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
            gateway.close()
        admin.execute_command("ACL", "DELUSER", publisher_user, gateway_user)
        admin.delete(stream_key, other_key)
        admin.close()


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


def _run_asgi_replica_gateway_process(
    redis_url, stream_key, replica_path, registry_path, consumer_name, port,
):
    import redis as redis_module
    import uvicorn

    from app.config import Settings
    from app.identity import IdentityVerificationError, VerifiedPrincipal
    from app.main import create_app
    from app.ohlcv_redis_consumer import RedisOhlcvReplicaConsumer
    from app.symbology import CanonicalInstrument, ProviderInstrumentMapping

    replica = SQLiteOhlcvReplicaStore(replica_path)
    redis_client = redis_module.Redis.from_url(
        redis_url, decode_responses=True, socket_connect_timeout=3, socket_timeout=3,
    )
    consumer = RedisOhlcvReplicaConsumer(
        redis_client, replica, stream_key=stream_key,
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
            "redis_client": redis_client,
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
                open_timeout=10, close_timeout=3, ping_interval=None,
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
        redis.delete(stream_key)
        redis.close()
