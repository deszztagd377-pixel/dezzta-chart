"""Bounded, per-series OHLCV fan-out for authenticated WebSocket clients.

All methods are event-loop confined. The ingestion service calls publish only
from its single-writer asyncio consumer, and subscription setup performs the
snapshot query and registration synchronously without an await. This makes the
snapshot/watermark hand-off atomic relative to publish() on the same loop.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Any

from app.ohlcv import (
    BUCKET_POLICY_UTC_LEGACY, OhlcvBar, OhlcvPipeline, decimal_to_string,
)

STREAM_QUEUE_CAPACITY = 256
SeriesIdentity = tuple[str, str, int, int, str, str, str, str, str, str]


@dataclass(slots=True)
class OhlcvStreamSubscription:
    stream_id: str
    identity: SeriesIdentity
    queue: asyncio.Queue[dict[str, Any]]
    watermark: int = 0
    durable_cursor: int = 0
    overflowed: bool = False
    closed: bool = False


class OhlcvStreamResnapshotRequired(RuntimeError):
    """The replay/live handoff cannot be completed without a fresh snapshot."""


class OhlcvStreamHub:
    """Fan out validated bars; disconnect slow consumers instead of dropping data."""

    def __init__(self, *, queue_capacity: int = STREAM_QUEUE_CAPACITY,
                 clock_ns=time.time_ns) -> None:
        if not isinstance(queue_capacity, int) or isinstance(queue_capacity, bool) or queue_capacity < 1:
            raise ValueError("queue_capacity must be a positive integer")
        self._queue_capacity = queue_capacity
        self._clock_ns = clock_ns
        self._subscriptions: dict[str, OhlcvStreamSubscription] = {}
        # Index fan-out by the full canonical identity so unrelated markets are
        # not scanned for every accepted bar.
        self._subscriptions_by_identity: dict[
            SeriesIdentity, dict[str, OhlcvStreamSubscription]
        ] = {}

    @staticmethod
    def identity_for(bar: OhlcvBar) -> SeriesIdentity:
        return (
            bar.provider, bar.dataset, bar.publisher_id, bar.instrument_id,
            bar.series_type, bar.raw_symbol, bar.timeframe, bar.bucket_policy,
            bar.calendar_id, bar.calendar_version,
        )

    def subscribe_snapshot(
        self,
        pipeline: OhlcvPipeline,
        *,
        dataset: str,
        publisher_id: int,
        instrument_id: int,
        raw_symbol: str,
        timeframe: str,
        limit: int,
        bucket_policy: str = BUCKET_POLICY_UTC_LEGACY,
        calendar_id: str = "",
        calendar_version: str = "",
        durable_cursor: int = 0,
        provider: str = "databento",
        series_type: str = "contract",
    ) -> tuple[OhlcvStreamSubscription, list[OhlcvBar], int]:
        """Take the initial snapshot and register its stream without an await.

        The event loop cannot run ingestion.publish() between the query and
        registration, so the returned watermark is a valid atomic boundary.
        """
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("provider must be a non-empty string")
        if not isinstance(series_type, str) or not series_type.strip():
            raise ValueError("series_type must be a non-empty string")
        provider = provider.strip().lower()
        series_type = series_type.strip().lower()
        identity = (
            provider, dataset, publisher_id, instrument_id, series_type,
            raw_symbol, timeframe, bucket_policy, calendar_id, calendar_version,
        )
        if not isinstance(durable_cursor, int) or isinstance(durable_cursor, bool) or durable_cursor < 0:
            raise ValueError("durable_cursor must be a non-negative integer")
        bars, total = pipeline.query(
            dataset=dataset,
            publisher_id=publisher_id,
            instrument_id=instrument_id,
            raw_symbol=raw_symbol,
            timeframe=timeframe,
            bucket_policy=bucket_policy,
            calendar_id=calendar_id,
            calendar_version=calendar_version,
            provider=provider,
            series_type=series_type,
            limit=limit,
        )
        stream_id = uuid.uuid4().hex
        subscription = OhlcvStreamSubscription(
            stream_id=stream_id,
            identity=identity,
            queue=asyncio.Queue(maxsize=self._queue_capacity),
            durable_cursor=durable_cursor,
        )
        self._register(subscription)
        return subscription, bars, total


    def subscribe_snapshot_bars(
        self,
        bars: list[OhlcvBar],
        *,
        total: int,
        dataset: str,
        publisher_id: int,
        instrument_id: int,
        raw_symbol: str,
        timeframe: str,
        limit: int,
        bucket_policy: str = BUCKET_POLICY_UTC_LEGACY,
        calendar_id: str = "",
        calendar_version: str = "",
        durable_cursor: int = 0,
        provider: str = "databento",
        series_type: str = "contract",
    ) -> tuple[OhlcvStreamSubscription, list[OhlcvBar], int]:
        """Register a subscription from an externally consistent durable snapshot.

        Use this when bars and durable_cursor were read from one database
        transaction (for example, a gateway replica checkpoint). Unlike
        subscribe_snapshot(), this method does not query the in-memory pipeline.
        """
        if not isinstance(bars, list) or any(not isinstance(bar, OhlcvBar) for bar in bars):
            raise TypeError("bars must be a list of OhlcvBar instances")
        if type(total) is not int or total < len(bars):
            raise ValueError("total must be an integer >= the returned bar count")
        if type(limit) is not int or limit < 1 or len(bars) > limit:
            raise ValueError("limit must be positive and bars must not exceed it")
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("provider must be a non-empty string")
        if not isinstance(series_type, str) or not series_type.strip():
            raise ValueError("series_type must be a non-empty string")
        if not isinstance(durable_cursor, int) or isinstance(durable_cursor, bool) or durable_cursor < 0:
            raise ValueError("durable_cursor must be a non-negative integer")
        provider = provider.strip().lower()
        series_type = series_type.strip().lower()
        identity = (
            provider, dataset, publisher_id, instrument_id, series_type,
            raw_symbol, timeframe, bucket_policy, calendar_id, calendar_version,
        )
        if any(self.identity_for(bar) != identity for bar in bars):
            raise ValueError("Snapshot contains bars outside the requested exact series identity")
        stream_id = uuid.uuid4().hex
        subscription = OhlcvStreamSubscription(
            stream_id=stream_id,
            identity=identity,
            queue=asyncio.Queue(maxsize=self._queue_capacity),
            durable_cursor=durable_cursor,
        )
        self._register(subscription)
        return subscription, list(bars), total

    def publish(
        self, bar: OhlcvBar, *, durable_cursor: int | None = None,
        durable_event_id: str | None = None,
    ) -> None:
        """Publish only an accepted pipeline revision to matching subscribers."""
        if durable_cursor is not None and (
            not isinstance(durable_cursor, int) or isinstance(durable_cursor, bool) or durable_cursor < 1
        ):
            raise ValueError("durable_cursor must be a positive integer")
        if durable_event_id is not None and (
            not isinstance(durable_event_id, str) or not durable_event_id
            or len(durable_event_id) > 128
        ):
            raise ValueError("durable_event_id must be a non-empty string up to 128 characters")
        identity = self.identity_for(bar)
        matching_subscriptions = self._subscriptions_by_identity.get(identity)
        if not matching_subscriptions:
            # Avoid constructing/serializing an OHLCV payload when no panel is
            # listening to this exact canonical series.
            return
        event_id = durable_event_id or uuid.uuid4().hex
        emitted_at_ns = str(self._clock_ns())
        payload_bar = {
            "dataset": bar.dataset,
            "provider": bar.provider,
            "publisherId": bar.publisher_id,
            "instrumentId": bar.instrument_id,
            "rawSymbol": bar.raw_symbol,
            "seriesType": bar.series_type,
            "timeframe": bar.timeframe,
            "bucketPolicy": bar.bucket_policy,
            "calendarId": bar.calendar_id,
            "calendarVersion": bar.calendar_version,
            "tsStartNs": str(bar.ts_start_ns),
            "open": decimal_to_string(bar.open),
            "high": decimal_to_string(bar.high),
            "low": decimal_to_string(bar.low),
            "close": decimal_to_string(bar.close),
            "volume": decimal_to_string(bar.volume),
            "tsEventNs": str(bar.ts_event_ns),
            "tsReceivedNs": str(bar.ts_received_ns),
            "tsProviderOutNs": None if bar.ts_provider_out_ns is None else str(bar.ts_provider_out_ns),
            "sequence": bar.sequence,
            "sequenceOrigin": bar.sequence_origin,
            "origin": bar.origin,
            "completeness": bar.completeness,
        }
        for subscription in tuple(matching_subscriptions.values()):
            if subscription.closed or subscription.overflowed or subscription.identity != identity:
                continue
            # Durable cursors are global and monotonic. A replay after Redis ACK
            # reply loss must not enqueue the same event twice for this subscriber.
            if durable_cursor is not None and durable_cursor <= subscription.durable_cursor:
                continue
            next_sequence = subscription.watermark + 1
            message = {
                "type": "market_data.ohlcv.update",
                "version": 1,
                "streamId": subscription.stream_id,
                "eventId": event_id,
                "sequence": next_sequence,
                **({"cursor": str(durable_cursor)} if durable_cursor is not None else {}),
                "emittedAtNs": emitted_at_ns,
                "operation": "upsert",
                "isFinal": bar.completeness == "complete",
                "series": {
                    "provider": bar.provider,
                    "dataset": bar.dataset,
                    "publisherId": bar.publisher_id,
                    "instrumentId": bar.instrument_id,
                    "seriesType": bar.series_type,
                    "rawSymbol": bar.raw_symbol,
                    "timeframe": bar.timeframe,
                    "bucketPolicy": bar.bucket_policy,
                    "calendarId": bar.calendar_id,
                    "calendarVersion": bar.calendar_version,
                },
                "bar": payload_bar,
            }
            try:
                subscription.queue.put_nowait(message)
            except asyncio.QueueFull:
                # A slow client must resnapshot; never silently skip an update.
                subscription.overflowed = True
                continue
            subscription.watermark = next_sequence
            if durable_cursor is not None:
                subscription.durable_cursor = max(subscription.durable_cursor, durable_cursor)


    def merge_replay_boundary(
        self,
        subscription: OhlcvStreamSubscription,
        replay_events: list[dict[str, Any]],
        replay_end_cursor: int,
    ) -> int:
        """Discard queued events covered by replay and resequence newer live events.

        Call synchronously on the owning event loop after replay has been sent.
        The replay page must end at the fixed replica checkpoint. Any malformed
        event, queue overflow, or out-of-order live cursor requires resnapshot.
        """
        if self._subscriptions.get(subscription.stream_id) is not subscription:
            raise ValueError("subscription is not active in this hub")
        if subscription.closed:
            raise OhlcvStreamResnapshotRequired("subscription is closed")
        if subscription.overflowed:
            raise OhlcvStreamResnapshotRequired("live queue overflowed during replay")
        if not isinstance(replay_events, list):
            raise TypeError("replay_events must be a list")
        if type(replay_end_cursor) is not int or replay_end_cursor < 0:
            raise ValueError("replay_end_cursor must be a non-negative integer")

        expected_series = {
            "provider": subscription.identity[0],
            "dataset": subscription.identity[1],
            "publisherId": subscription.identity[2],
            "instrumentId": subscription.identity[3],
            "seriesType": subscription.identity[4],
            "rawSymbol": subscription.identity[5],
            "timeframe": subscription.identity[6],
            "bucketPolicy": subscription.identity[7],
            "calendarId": subscription.identity[8],
            "calendarVersion": subscription.identity[9],
        }
        previous_replay_cursor = 0
        for event in replay_events:
            if not isinstance(event, dict):
                raise ValueError("replay event must be an object")
            cursor = event.get("cursor")
            if type(cursor) is not int or cursor < 1 or cursor > replay_end_cursor:
                raise ValueError("replay event cursor is outside the replay boundary")
            if cursor <= previous_replay_cursor:
                raise ValueError("replay event cursors must be strictly increasing")
            if event.get("series") != expected_series:
                raise ValueError("replay event does not match the subscription series")
            previous_replay_cursor = cursor

        pending_live: list[tuple[int, dict[str, Any]]] = []
        previous_live_cursor = replay_end_cursor
        while not subscription.queue.empty():
            message = subscription.queue.get_nowait()
            cursor_value = message.get("cursor") if isinstance(message, dict) else None
            if (
                not isinstance(cursor_value, str)
                or not cursor_value.isascii()
                or not cursor_value.isdigit()
            ):
                subscription.overflowed = True
                raise OhlcvStreamResnapshotRequired("queued live event has no valid durable cursor")
            cursor = int(cursor_value)
            if cursor <= replay_end_cursor:
                continue
            if cursor <= previous_live_cursor:
                subscription.overflowed = True
                raise OhlcvStreamResnapshotRequired("queued live cursors are not strictly increasing")
            previous_live_cursor = cursor
            pending_live.append((cursor, message))

        next_sequence = len(replay_events)
        for _cursor, message in pending_live:
            next_sequence += 1
            message["streamId"] = subscription.stream_id
            message["sequence"] = next_sequence
            try:
                subscription.queue.put_nowait(message)
            except asyncio.QueueFull as exc:
                subscription.overflowed = True
                raise OhlcvStreamResnapshotRequired("live queue overflowed while merging replay") from exc

        subscription.watermark = next_sequence
        subscription.durable_cursor = max(
            subscription.durable_cursor,
            replay_end_cursor,
            previous_live_cursor,
        )
        return len(pending_live)

    def _register(self, subscription: OhlcvStreamSubscription) -> None:
        self._subscriptions[subscription.stream_id] = subscription
        self._subscriptions_by_identity.setdefault(subscription.identity, {})[
            subscription.stream_id
        ] = subscription

    def unsubscribe(self, stream_id: str) -> None:
        subscription = self._subscriptions.pop(stream_id, None)
        if subscription is None:
            return
        subscription.closed = True
        series_subscriptions = self._subscriptions_by_identity.get(subscription.identity)
        if series_subscriptions is not None:
            series_subscriptions.pop(stream_id, None)
            if not series_subscriptions:
                self._subscriptions_by_identity.pop(subscription.identity, None)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscriptions)

    @property
    def series_count(self) -> int:
        """Number of canonical series currently holding at least one subscriber."""
        return len(self._subscriptions_by_identity)

    def subscriber_count_for(self, identity: SeriesIdentity) -> int:
        """Return the active subscriber count for one exact canonical series."""
        return len(self._subscriptions_by_identity.get(identity, {}))
