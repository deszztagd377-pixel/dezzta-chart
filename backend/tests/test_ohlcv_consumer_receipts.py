from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import sqlite3

import pytest

from app.ohlcv_consumer_receipts import (
    OhlcvConsumerReceiptConflict,
    OhlcvConsumerReceiptError,
    OhlcvConsumerReceiptStale,
    SQLiteOhlcvConsumerReceiptStore,
)


SUBJECT = "firebase-user-123"
CONSUMER = "device-instance-123"
SERIES = "a" * 64
STREAM = "stream-generation-1"
EVENT_1 = "event-1"
DIGEST_1 = hashlib.sha256(b"event-1").hexdigest()


def make_store(tmp_path, *, clock=lambda: 1_700_000_000_000_000_000):
    return SQLiteOhlcvConsumerReceiptStore(
        str(tmp_path / "market.sqlite3"),
        clock_ns=clock,
    )


def commit(store, *, cursor=41, event_id=EVENT_1, digest=DIGEST_1,
           stream=STREAM, sequence=1, subject=SUBJECT, consumer=CONSUMER,
           series=SERIES, fencing_token=1):
    return store.commit_receipt(
        account_subject=subject,
        consumer_id=consumer,
        series_key=series,
        cursor=cursor,
        event_id=event_id,
        event_digest=digest,
        stream_id=stream,
        sequence=sequence,
        fencing_token=fencing_token,
    )


def test_first_receipt_is_durable_and_scoped_to_identity(tmp_path):
    store = make_store(tmp_path)
    result = commit(store)
    assert result == {
        "accepted": True,
        "duplicate": False,
        "committed_cursor": "41",
        "receipt_version": 1,
        "fencing_token": 1,
    }

    reopened = make_store(tmp_path)
    receipt = reopened.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt is not None
    assert receipt["committed_cursor"] == "41"
    assert receipt["event_id"] == EVENT_1
    assert receipt["event_digest"] == DIGEST_1
    assert receipt["receipt_version"] == 1
    assert receipt["fencing_token"] == 1


def test_legacy_receipt_schema_migrates_and_requires_positive_fence_on_takeover(tmp_path):
    database = tmp_path / "market.sqlite3"
    db = sqlite3.connect(database)
    db.execute(
        """CREATE TABLE ohlcv_consumer_receipts (
            account_subject TEXT NOT NULL,
            consumer_id TEXT NOT NULL,
            series_key TEXT NOT NULL,
            committed_cursor INTEGER NOT NULL CHECK(committed_cursor > 0),
            event_id TEXT NOT NULL,
            event_digest TEXT NOT NULL CHECK(length(event_digest) = 64),
            stream_id TEXT NOT NULL,
            sequence INTEGER NOT NULL CHECK(sequence > 0),
            receipt_version INTEGER NOT NULL CHECK(receipt_version > 0),
            updated_at_ns INTEGER NOT NULL CHECK(updated_at_ns >= 0),
            PRIMARY KEY(account_subject, consumer_id, series_key)
        )"""
    )
    db.execute(
        """INSERT INTO ohlcv_consumer_receipts(
            account_subject,consumer_id,series_key,committed_cursor,event_id,
            event_digest,stream_id,sequence,receipt_version,updated_at_ns
        ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (SUBJECT, CONSUMER, SERIES, 41, EVENT_1, DIGEST_1, STREAM, 1, 1, 1),
    )
    db.commit()
    db.close()

    store = SQLiteOhlcvConsumerReceiptStore(str(database))
    migrated = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert migrated is not None
    assert migrated["fencing_token"] == 0

    takeover = commit(store, cursor=41, fencing_token=1, stream="stream-generation-2")
    assert takeover["accepted"] is True
    assert takeover["duplicate"] is True
    assert takeover["fencing_token"] == 1

    upgraded = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert upgraded["fencing_token"] == 1
    assert upgraded["stream_id"] == "stream-generation-2"


def test_duplicate_ack_is_idempotent_across_reconnect_generation(tmp_path):
    store = make_store(tmp_path)
    commit(store)
    result = commit(
        store, stream="stream-generation-2", sequence=1, fencing_token=2,
    )
    assert result["accepted"] is True
    assert result["duplicate"] is True
    assert result["receipt_version"] == 2
    receipt = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt["stream_id"] == "stream-generation-2"


def test_same_fencing_token_cannot_take_over_a_new_stream_generation(tmp_path):
    store = make_store(tmp_path)
    commit(store, cursor=41, fencing_token=5)

    with pytest.raises(OhlcvConsumerReceiptStale, match="stream generation"):
        commit(
            store,
            cursor=41,
            stream="stream-generation-2",
            sequence=1,
            fencing_token=5,
        )

    receipt = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt["stream_id"] == STREAM
    assert receipt["fencing_token"] == 5


def test_same_fencing_token_cannot_rewrite_sequence_for_committed_event(tmp_path):
    store = make_store(tmp_path)
    commit(store, cursor=41, sequence=3, fencing_token=5)

    with pytest.raises(OhlcvConsumerReceiptStale, match="sequence changed"):
        commit(store, cursor=41, sequence=1, fencing_token=5)

    receipt = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt["sequence"] == 3
    assert receipt["fencing_token"] == 5


def test_higher_fencing_token_takes_over_without_regressing_cursor(tmp_path):
    store = make_store(tmp_path)
    commit(store, cursor=41, fencing_token=4)

    takeover = commit(
        store,
        cursor=41,
        stream="stream-generation-2",
        sequence=1,
        fencing_token=5,
    )
    assert takeover["accepted"] is True
    assert takeover["duplicate"] is True
    assert takeover["receipt_version"] == 2
    assert takeover["fencing_token"] == 5

    receipt = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt["committed_cursor"] == "41"
    assert receipt["fencing_token"] == 5
    assert receipt["stream_id"] == "stream-generation-2"


def test_stale_fencing_token_cannot_advance_a_new_owner_receipt(tmp_path):
    store = make_store(tmp_path)
    commit(store, cursor=41, fencing_token=8)
    with pytest.raises(OhlcvConsumerReceiptStale, match="fencing token"):
        commit(
            store,
            cursor=42,
            event_id="event-42",
            digest=hashlib.sha256(b"event-42").hexdigest(),
            sequence=2,
            fencing_token=7,
        )
    receipt = store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt["committed_cursor"] == "41"
    assert receipt["fencing_token"] == 8


def test_higher_fence_cannot_regress_the_committed_cursor(tmp_path):
    store = make_store(tmp_path)
    commit(store, cursor=45, event_id="event-45",
           digest=hashlib.sha256(b"event-45").hexdigest(),
           sequence=5, fencing_token=3)
    with pytest.raises(OhlcvConsumerReceiptStale, match="cursor"):
        commit(store, cursor=44, event_id="event-44",
               digest=hashlib.sha256(b"event-44").hexdigest(),
               sequence=4, fencing_token=4)


def test_receipt_cursor_must_advance_monotonically(tmp_path):
    store = make_store(tmp_path)
    commit(store, cursor=41)
    result = commit(
        store, cursor=45, event_id="event-45",
        digest=hashlib.sha256(b"event-45").hexdigest(), sequence=5,
    )
    assert result["committed_cursor"] == "45"
    assert result["receipt_version"] == 2
    with pytest.raises(OhlcvConsumerReceiptStale):
        commit(store, cursor=44, event_id="event-44",
               digest=hashlib.sha256(b"event-44").hexdigest(), sequence=4)


def test_same_cursor_with_different_event_is_rejected(tmp_path):
    store = make_store(tmp_path)
    commit(store)
    with pytest.raises(OhlcvConsumerReceiptConflict):
        commit(
            store,
            event_id="different-event",
            digest=hashlib.sha256(b"different-event").hexdigest(),
        )


def test_receipts_are_isolated_by_account_consumer_and_series(tmp_path):
    store = make_store(tmp_path)
    commit(store)
    assert commit(store, subject="firebase-user-456")["receipt_version"] == 1
    assert commit(store, consumer="another-device")["receipt_version"] == 1
    assert commit(store, series="b" * 64)["receipt_version"] == 1
    assert store.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )["committed_cursor"] == "41"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"cursor": True},
        {"cursor": 0},
        {"cursor": -1},
        {"cursor": 1 << 63},
        {"sequence": True},
        {"sequence": 0},
        {"sequence": 1 << 53},
        {"fencing_token": True},
        {"fencing_token": 0},
        {"fencing_token": -1},
        {"fencing_token": 1 << 63},
        {"digest": "not-a-digest"},
        {"series": "A" * 64},
        {"consumer": "not a safe id"},
        {"stream": "stream\nforged"},
    ],
)
def test_invalid_receipt_fields_fail_closed(tmp_path, kwargs):
    store = make_store(tmp_path)
    with pytest.raises(OhlcvConsumerReceiptError):
        commit(store, **kwargs)


def test_series_identity_digest_is_order_independent_and_rejects_nan():
    identity = {"provider": "databento", "dataset": "GLBX.MDP3", "timeframe": "1s"}
    reordered = {"timeframe": "1s", "dataset": "GLBX.MDP3", "provider": "databento"}
    assert SQLiteOhlcvConsumerReceiptStore.series_key_for(identity) == (
        SQLiteOhlcvConsumerReceiptStore.series_key_for(reordered)
    )
    with pytest.raises(OhlcvConsumerReceiptError):
        SQLiteOhlcvConsumerReceiptStore.series_key_for({"bad": float("nan")})


def test_concurrent_receipts_never_move_cursor_backwards(tmp_path):
    store_a = make_store(tmp_path)
    store_b = make_store(tmp_path)

    def write(cursor):
        return commit(
            store_a if cursor == 41 else store_b,
            cursor=cursor,
            event_id=f"event-{cursor}",
            digest=hashlib.sha256(f"event-{cursor}".encode()).hexdigest(),
            sequence=cursor - 40,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(write, 41), executor.submit(write, 42)]
        for future in futures:
            try:
                future.result()
            except OhlcvConsumerReceiptStale:
                pass

    receipt = store_a.get_receipt(
        account_subject=SUBJECT,
        consumer_id=CONSUMER,
        series_key=SERIES,
    )
    assert receipt["committed_cursor"] == "42"
