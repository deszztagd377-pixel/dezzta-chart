from __future__ import annotations

import pytest

from app.ohlcv_ack_session import (
    OhlcvAckedEvent,
    OhlcvAckDigestMismatch,
    OhlcvAckEventLedger,
    OhlcvAckProtocolError,
    OhlcvAckStale,
    OhlcvAckUnknownEvent,
    OhlcvAckWindowFull,
)


STREAM_ID = "stream-0123456789abcdef"
DIGEST_1 = "a" * 64
DIGEST_2 = "b" * 64


def event(sequence: int, cursor: int, digest: str = DIGEST_1, *, stream_id: str = STREAM_ID) -> dict:
    return {
        "type": "market_data.ohlcv.update",
        "version": 1,
        "streamId": stream_id,
        "sequence": sequence,
        "cursor": str(cursor),
        "eventId": f"event-{sequence}",
        "digest": digest,
    }


def ack(sequence: int, digest: str = DIGEST_1) -> dict:
    return {
        "type": "market_data.ack",
        "version": 1,
        "sequence": sequence,
        "eventDigest": digest,
    }


def test_ack_resolves_to_exact_event_sent_on_current_socket() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    sent = ledger.record_sent_event(event(1, 101))

    committed, duplicate = ledger.acknowledge(ack(1))

    assert committed == sent
    assert committed.cursor == 101
    assert committed.event_id == "event-1"
    assert duplicate is False
    assert ledger.pending_count == 0
    assert ledger.last_acked == sent


def test_cumulative_ack_clears_all_prior_sent_events() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))
    ledger.record_sent_event(event(2, 102))
    ledger.record_sent_event(event(3, 103, DIGEST_2))

    committed, duplicate = ledger.acknowledge(ack(3, DIGEST_2))

    assert committed.sequence == 3
    assert committed.cursor == 103
    assert duplicate is False
    assert ledger.pending_count == 0


def test_exact_duplicate_ack_is_idempotent() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))
    first = ledger.acknowledge(ack(1))
    second = ledger.acknowledge(ack(1))

    assert first[0] == second[0]
    assert first[1] is False
    assert second[1] is True


def test_duplicate_ack_with_different_digest_is_rejected() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))
    ledger.acknowledge(ack(1))

    with pytest.raises(OhlcvAckDigestMismatch):
        ledger.acknowledge(ack(1, DIGEST_2))


def test_ack_for_event_not_sent_on_this_socket_is_rejected() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    with pytest.raises(OhlcvAckUnknownEvent):
        ledger.acknowledge(ack(1))


def test_ack_digest_must_match_the_sent_event() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))

    with pytest.raises(OhlcvAckDigestMismatch):
        ledger.acknowledge(ack(1, DIGEST_2))

    # A rejected ACK does not consume the valid pending event.
    assert ledger.pending_count == 1
    assert ledger.acknowledge(ack(1, DIGEST_1))[0].cursor == 101


def test_lower_ack_after_cumulative_commit_is_stale() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))
    ledger.record_sent_event(event(2, 102))
    ledger.acknowledge(ack(2))

    with pytest.raises(OhlcvAckStale):
        ledger.acknowledge(ack(1))


def test_event_from_another_stream_cannot_enter_ledger() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    with pytest.raises(OhlcvAckProtocolError, match="different WebSocket stream"):
        ledger.record_sent_event(event(1, 101, stream_id="other-stream"))


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"type": "market_data.ohlcv.snapshot", "version": 1},
        {**event(1, 101), "cursor": None},
        {**event(1, 101), "sequence": True},
        {**event(1, 101), "version": True},
        {**event(1, 101), "digest": "A" * 64},
        {**event(1, 101), "eventId": "bad event id"},
        {**event(1, 101), "cursor": "0"},
        {**event(1, 101), "cursor": "01"},
    ],
)
def test_malformed_events_are_rejected(payload: dict) -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    with pytest.raises(OhlcvAckProtocolError):
        ledger.record_sent_event(payload)


def test_sequence_and_cursor_must_both_advance_monotonically() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))

    with pytest.raises(OhlcvAckStale):
        ledger.record_sent_event(event(3, 103))
    with pytest.raises(OhlcvAckStale):
        ledger.record_sent_event(event(2, 101))

    assert ledger.pending_count == 1


def test_pending_window_is_bounded_and_never_silently_drops_unacked_events() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID, max_pending_events=1)
    ledger.record_sent_event(event(1, 101))

    with pytest.raises(OhlcvAckWindowFull):
        ledger.record_sent_event(event(2, 102))

    assert ledger.pending_count == 1


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"type": "market_data.ack", "version": True, "sequence": 1, "eventDigest": DIGEST_1},
        {"type": "market_data.ack", "version": 1, "sequence": True, "eventDigest": DIGEST_1},
        {"type": "market_data.ack", "version": 1, "sequence": 1, "eventDigest": "bad"},
        {"type": "market_data.ack", "version": 1, "sequence": 1, "eventDigest": DIGEST_1, "cursor": "101"},
    ],
)
def test_malformed_ack_messages_are_rejected(payload: object) -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    with pytest.raises(OhlcvAckProtocolError):
        ledger.acknowledge(payload)

def test_resolve_ack_does_not_advance_ledger_before_durable_commit() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    sent = ledger.record_sent_event(event(1, 101))

    resolved, duplicate = ledger.resolve_ack(ack(1))

    assert resolved == sent
    assert duplicate is False
    assert ledger.pending_count == 1
    assert ledger.last_acked is None

    ledger.commit_ack(resolved)

    assert ledger.pending_count == 0
    assert ledger.last_acked == sent


def test_resolve_ack_can_be_retried_after_a_durable_commit_failure() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    sent = ledger.record_sent_event(event(1, 101))

    # Re-resolving is safe while the caller retries its durable transaction.
    first, first_duplicate = ledger.resolve_ack(ack(1))
    second, second_duplicate = ledger.resolve_ack(ack(1))
    assert first == second == sent
    assert first_duplicate is second_duplicate is False
    assert ledger.pending_count == 1

    ledger.commit_ack(second)
    resolved, duplicate = ledger.resolve_ack(ack(1))
    assert resolved == sent
    assert duplicate is True


def test_commit_ack_rejects_an_event_not_pending_on_this_socket() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    foreign = OhlcvAckedEvent(
        stream_id="another-stream",
        sequence=1,
        cursor=101,
        event_id="event-1",
        event_digest=DIGEST_1,
    )

    with pytest.raises(OhlcvAckUnknownEvent):
        ledger.commit_ack(foreign)


def test_commit_ack_requires_exact_pending_event() -> None:
    ledger = OhlcvAckEventLedger(STREAM_ID)
    ledger.record_sent_event(event(1, 101))
    altered = OhlcvAckEventLedger(STREAM_ID).record_sent_event(event(1, 102))

    with pytest.raises(OhlcvAckUnknownEvent):
        ledger.commit_ack(altered)

    assert ledger.pending_count == 1
    assert ledger.last_acked is None
