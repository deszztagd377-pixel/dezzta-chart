"""Per-WebSocket validation of cumulative OHLCV consumer acknowledgements.

This ledger is intentionally an in-memory, connection-scoped validation layer.
It records an event only after the caller successfully sends it on that socket,
then resolves the client's sequence+digest ACK to the exact durable event cursor.
It does not persist receipts, establish consumer identity, or provide fencing;
those controls must be enforced before a production ACK capability is advertised.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

MAX_SQLITE_CURSOR = (1 << 63) - 1
MAX_JS_SAFE_INTEGER = (1 << 53) - 1
MAX_EVENT_ID_LENGTH = 128
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_CURSOR_RE = re.compile(r"^[1-9][0-9]{0,18}$")


class OhlcvAckProtocolError(ValueError):
    """Base class for invalid or untrusted OHLCV acknowledgement messages."""


class OhlcvAckWindowFull(OhlcvAckProtocolError):
    """The client has too many unacknowledged events; it must resnapshot."""


class OhlcvAckUnknownEvent(OhlcvAckProtocolError):
    """The ACK does not identify an event sent on this WebSocket."""


class OhlcvAckDigestMismatch(OhlcvAckProtocolError):
    """The ACK digest does not match the exact event sent on this socket."""


class OhlcvAckStale(OhlcvAckProtocolError):
    """The ACK moves the committed sequence or cursor backwards."""


@dataclass(frozen=True, slots=True)
class OhlcvAckedEvent:
    stream_id: str
    sequence: int
    cursor: int
    event_id: str
    event_digest: str


class OhlcvAckEventLedger:
    """Bounded event ledger for validating cumulative ACKs on one socket.

    Call record_sent_event() only after send_json() succeeds. ACKs are
    cumulative: acknowledging sequence N confirms all recorded events through
    N were processed in order. The caller must durably commit the returned
    event cursor before sending market_data.acknowledged to the client.
    """

    def __init__(self, stream_id: str, *, max_pending_events: int = 4096) -> None:
        if not isinstance(stream_id, str) or not _ID_RE.fullmatch(stream_id):
            raise ValueError("stream_id is invalid.")
        if type(max_pending_events) is not int or not 1 <= max_pending_events <= 100_000:
            raise ValueError("max_pending_events must be between 1 and 100000.")
        self.stream_id = stream_id
        self.max_pending_events = max_pending_events
        self._pending: dict[int, OhlcvAckedEvent] = {}
        self._last_registered_sequence = 0
        self._last_registered_cursor = 0
        self._last_acked: OhlcvAckedEvent | None = None

    @staticmethod
    def _parse_event(event: Any, expected_stream_id: str) -> OhlcvAckedEvent:
        if not isinstance(event, dict):
            raise OhlcvAckProtocolError("OHLCV event must be an object.")
        if event.get("type") != "market_data.ohlcv.update" or event.get("version") != 1:
            raise OhlcvAckProtocolError("Only version 1 OHLCV update events can be acknowledged.")
        stream_id = event.get("streamId")
        if stream_id != expected_stream_id:
            raise OhlcvAckProtocolError("OHLCV event belongs to a different WebSocket stream.")
        sequence = event.get("sequence")
        if type(sequence) is not int or not 1 <= sequence <= MAX_JS_SAFE_INTEGER:
            raise OhlcvAckProtocolError("OHLCV event sequence is invalid.")
        cursor_value = event.get("cursor")
        if not isinstance(cursor_value, str) or not _CURSOR_RE.fullmatch(cursor_value):
            raise OhlcvAckProtocolError("ACK-capable OHLCV events require a positive decimal cursor.")
        cursor = int(cursor_value)
        if cursor > MAX_SQLITE_CURSOR:
            raise OhlcvAckProtocolError("OHLCV event cursor exceeds the SQLite-safe range.")
        event_id = event.get("eventId")
        if not isinstance(event_id, str) or not _ID_RE.fullmatch(event_id):
            raise OhlcvAckProtocolError("OHLCV event ID is invalid.")
        digest = event.get("digest")
        if not isinstance(digest, str) or not _DIGEST_RE.fullmatch(digest):
            raise OhlcvAckProtocolError("OHLCV event digest is invalid.")
        return OhlcvAckedEvent(
            stream_id=stream_id,
            sequence=sequence,
            cursor=cursor,
            event_id=event_id,
            event_digest=digest,
        )

    def record_sent_event(self, event: Any) -> OhlcvAckedEvent:
        """Record a durable event after successful delivery to this socket."""
        parsed = self._parse_event(event, self.stream_id)
        if parsed.sequence <= self._last_registered_sequence:
            raise OhlcvAckStale("Sent event sequence must increase strictly.")
        if parsed.cursor <= self._last_registered_cursor:
            raise OhlcvAckStale("Sent event cursor must increase strictly.")
        if len(self._pending) >= self.max_pending_events:
            raise OhlcvAckWindowFull("Unacknowledged event window is full; resnapshot required.")
        self._pending[parsed.sequence] = parsed
        self._last_registered_sequence = parsed.sequence
        self._last_registered_cursor = parsed.cursor
        return parsed

    def acknowledge(self, message: Any) -> tuple[OhlcvAckedEvent, bool]:
        """Resolve a client ACK to the exact sent event; return (event, duplicate)."""
        if not isinstance(message, dict):
            raise OhlcvAckProtocolError("OHLCV ACK must be an object.")
        if set(message) != {"type", "version", "sequence", "eventDigest"}:
            raise OhlcvAckProtocolError("OHLCV ACK fields do not match protocol version 1.")
        if message.get("type") != "market_data.ack" or message.get("version") != 1:
            raise OhlcvAckProtocolError("Unsupported OHLCV ACK message.")
        sequence = message.get("sequence")
        if type(sequence) is not int or not 1 <= sequence <= MAX_JS_SAFE_INTEGER:
            raise OhlcvAckProtocolError("OHLCV ACK sequence is invalid.")
        digest = message.get("eventDigest")
        if not isinstance(digest, str) or not _DIGEST_RE.fullmatch(digest):
            raise OhlcvAckProtocolError("OHLCV ACK digest is invalid.")

        if self._last_acked is not None and sequence == self._last_acked.sequence:
            if digest != self._last_acked.event_digest:
                raise OhlcvAckDigestMismatch("Duplicate ACK digest conflicts with the committed event.")
            return self._last_acked, True
        if self._last_acked is not None and sequence < self._last_acked.sequence:
            raise OhlcvAckStale("ACK sequence is older than the committed sequence.")

        event = self._pending.get(sequence)
        if event is None:
            raise OhlcvAckUnknownEvent("ACK does not match an event sent on this WebSocket.")
        if event.event_digest != digest:
            raise OhlcvAckDigestMismatch("ACK digest does not match the event sent on this WebSocket.")
        if self._last_acked is not None and event.cursor <= self._last_acked.cursor:
            raise OhlcvAckStale("ACK cursor is older than the committed cursor.")

        for pending_sequence in tuple(self._pending):
            if pending_sequence <= sequence:
                del self._pending[pending_sequence]
        self._last_acked = event
        return event, False

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def last_acked(self) -> OhlcvAckedEvent | None:
        return self._last_acked
