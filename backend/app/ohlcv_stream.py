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
    overflowed: bool = False
    closed: bool = False


class OhlcvStreamHub:
    """Fan out validated bars; disconnect slow consumers instead of dropping data."""

    def __init__(self, *, queue_capacity: int = STREAM_QUEUE_CAPACITY,
                 clock_ns=time.time_ns) -> None:
        if not isinstance(queue_capacity, int) or isinstance(queue_capacity, bool) or queue_capacity < 1:
            raise ValueError("queue_capacity must be a positive integer")
        self._queue_capacity = queue_capacity
        self._clock_ns = clock_ns
        self._subscriptions: dict[str, OhlcvStreamSubscription] = {}

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
    ) -> tuple[OhlcvStreamSubscription, list[OhlcvBar], int]:
        """Take the initial snapshot and register its stream without an await.

        The event loop cannot run ingestion.publish() between the query and
        registration, so the returned watermark is a valid atomic boundary.
        """
        identity = (
            "databento", dataset, publisher_id, instrument_id, "contract",
            raw_symbol, timeframe, bucket_policy, calendar_id, calendar_version,
        )
        bars, total = pipeline.query(
            dataset=dataset,
            publisher_id=publisher_id,
            instrument_id=instrument_id,
            raw_symbol=raw_symbol,
            timeframe=timeframe,
            bucket_policy=bucket_policy,
            calendar_id=calendar_id,
            calendar_version=calendar_version,
            provider="databento",
            series_type="contract",
            limit=limit,
        )
        stream_id = uuid.uuid4().hex
        subscription = OhlcvStreamSubscription(
            stream_id=stream_id,
            identity=identity,
            queue=asyncio.Queue(maxsize=self._queue_capacity),
        )
        self._subscriptions[stream_id] = subscription
        return subscription, bars, total

    def publish(self, bar: OhlcvBar) -> None:
        """Publish only an accepted pipeline revision to matching subscribers."""
        identity = self.identity_for(bar)
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
        for subscription in tuple(self._subscriptions.values()):
            if subscription.closed or subscription.overflowed or subscription.identity != identity:
                continue
            next_sequence = subscription.watermark + 1
            message = {
                "type": "market_data.ohlcv.update",
                "version": 1,
                "streamId": subscription.stream_id,
                "eventId": uuid.uuid4().hex,
                "sequence": next_sequence,
                "emittedAtNs": str(self._clock_ns()),
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

    def unsubscribe(self, stream_id: str) -> None:
        subscription = self._subscriptions.pop(stream_id, None)
        if subscription is not None:
            subscription.closed = True

    @property
    def subscriber_count(self) -> int:
        return len(self._subscriptions)
