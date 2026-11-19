"""Bridge durable gateway replicas into the local OHLCV pipeline and WebSocket hub.

The replica SQLite database is authoritative across restarts. Hydrate the
in-memory pipeline from that read model before accepting live Redis events.
For each committed/duplicate Redis event, apply it to the pipeline and fan it
out using the global durable cursor so ACK-reply retries cannot double-notify
subscribers.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.ohlcv import OhlcvBar, OhlcvPipeline
from app.ohlcv_store import SQLiteOhlcvReplicaStore
from app.ohlcv_stream import OhlcvStreamHub


class ReplicaPipelineDivergence(RuntimeError):
    """The durable replica event cannot be represented in the live pipeline."""


def hydrate_replica_pipeline(
    replica_store: SQLiteOhlcvReplicaStore,
    pipeline: OhlcvPipeline,
) -> dict[str, int]:
    """Replace in-memory bars from the verified durable replica checkpoint."""
    if not isinstance(replica_store, SQLiteOhlcvReplicaStore):
        raise TypeError("replica_store must be a SQLiteOhlcvReplicaStore.")
    if not isinstance(pipeline, OhlcvPipeline):
        raise TypeError("pipeline must be an OhlcvPipeline.")
    checkpoint = replica_store.checkpoint()
    if checkpoint is None:
        raise RuntimeError("A verified replica snapshot is required before hydration.")
    bars = replica_store.load_bars()
    pipeline.replace_snapshot(bars)
    return {
        "bar_count": len(bars),
        "applied_cursor": int(checkpoint["applied_cursor"]),
        "retention_floor": int(checkpoint["retention_floor"]),
    }



def subscribe_replica_snapshot(
    replica_store: SQLiteOhlcvReplicaStore,
    stream_hub: OhlcvStreamHub,
    *,
    dataset: str,
    publisher_id: int,
    instrument_id: int,
    raw_symbol: str,
    timeframe: str,
    limit: int,
    bucket_policy: str,
    calendar_id: str = "",
    calendar_version: str = "",
    provider: str = "databento",
    series_type: str = "contract",
) -> tuple[Any, list[OhlcvBar], int, dict[str, Any]]:
    """Read replica bars+checkpoint atomically, then register the matching hub.

    There must be no await between this call and returning to the WebSocket
    handler. The SQLite read transaction supplies both the bars and cursor;
    hub registration occurs synchronously on the event-loop thread. Thus a
    consumer callback that committed before the read is represented in the
    snapshot, while a callback committed after it is delivered as a live event.
    """
    if not isinstance(replica_store, SQLiteOhlcvReplicaStore):
        raise TypeError("replica_store must be a SQLiteOhlcvReplicaStore.")
    if not isinstance(stream_hub, OhlcvStreamHub):
        raise TypeError("stream_hub must be an OhlcvStreamHub.")
    snapshot = replica_store.query_snapshot(
        provider=provider,
        dataset=dataset,
        publisher_id=publisher_id,
        instrument_id=instrument_id,
        series_type=series_type,
        raw_symbol=raw_symbol,
        timeframe=timeframe,
        bucket_policy=bucket_policy,
        calendar_id=calendar_id,
        calendar_version=calendar_version,
        limit=limit,
    )
    cursor = snapshot.get("cursor")
    retention_floor = snapshot.get("retention_floor")
    source_id = snapshot.get("source_id")
    bars = snapshot.get("bars")
    total = snapshot.get("total")
    if (
        type(cursor) is not int or cursor < 0
        or type(retention_floor) is not int or retention_floor < 0
        or not isinstance(source_id, str) or not source_id
        or not isinstance(bars, list)
        or type(total) is not int or total < len(bars)
    ):
        raise RuntimeError("Replica snapshot returned an invalid checkpoint/read-model result.")
    subscription, snapshot_bars, snapshot_total = stream_hub.subscribe_snapshot_bars(
        bars,
        total=total,
        dataset=dataset,
        publisher_id=publisher_id,
        instrument_id=instrument_id,
        raw_symbol=raw_symbol,
        timeframe=timeframe,
        limit=limit,
        bucket_policy=bucket_policy,
        calendar_id=calendar_id,
        calendar_version=calendar_version,
        durable_cursor=cursor,
        provider=provider,
        series_type=series_type,
    )
    return subscription, snapshot_bars, snapshot_total, {
        "cursor": cursor,
        "high_water": snapshot.get("high_water"),
        "retention_floor": retention_floor,
        "source_id": source_id,
    }


def _bar_from_event(event: dict[str, Any]) -> OhlcvBar:
    if not isinstance(event, dict) or set(event) != {
        "type", "version", "eventId", "operation", "series", "bar", "cursor",
    }:
        raise ValueError("Replica event envelope does not match the canonical contract.")
    if (
        event["type"] != "market_data.ohlcv.update"
        or type(event["version"]) is not int or event["version"] != 1
        or event["operation"] != "upsert"
    ):
        raise ValueError("Replica event type, version or operation is unsupported.")
    if type(event["cursor"]) is not int or event["cursor"] < 1:
        raise ValueError("Replica event cursor must be a positive integer.")
    if not isinstance(event["eventId"], str) or not event["eventId"]:
        raise ValueError("Replica event ID must be a non-empty string.")
    payload = event["bar"]
    if not isinstance(payload, dict) or set(payload) != {
        "dataset", "provider", "publisherId", "instrumentId", "rawSymbol",
        "seriesType", "timeframe", "bucketPolicy", "calendarId",
        "calendarVersion", "tsStartNs", "open", "high", "low", "close",
        "volume", "tsEventNs", "tsReceivedNs", "tsProviderOutNs",
        "sequence", "sequenceOrigin", "origin", "completeness",
    }:
        raise ValueError("Replica event bar does not match the canonical contract.")
    return OhlcvBar(
        provider=payload["provider"],
        dataset=payload["dataset"],
        publisher_id=payload["publisherId"],
        instrument_id=payload["instrumentId"],
        series_type=payload["seriesType"],
        timeframe=payload["timeframe"],
        ts_start_ns=int(payload["tsStartNs"]),
        raw_symbol=payload["rawSymbol"],
        open=Decimal(payload["open"]),
        high=Decimal(payload["high"]),
        low=Decimal(payload["low"]),
        close=Decimal(payload["close"]),
        volume=Decimal(payload["volume"]),
        ts_event_ns=int(payload["tsEventNs"]),
        ts_received_ns=int(payload["tsReceivedNs"]),
        sequence=payload["sequence"],
        sequence_origin=payload["sequenceOrigin"],
        origin=payload["origin"],
        completeness=payload["completeness"],
        ts_provider_out_ns=(
            None if payload["tsProviderOutNs"] is None
            else int(payload["tsProviderOutNs"])
        ),
        bucket_policy=payload["bucketPolicy"],
        calendar_id=payload["calendarId"],
        calendar_version=payload["calendarVersion"],
    )


def forward_replica_event(
    event: dict[str, Any],
    pipeline: OhlcvPipeline,
    stream_hub: OhlcvStreamHub,
) -> str:
    """Apply a durable event locally and fan it out once per subscriber cursor.

    The consumer calls this after the replica SQLite transaction commits and
    before Redis ACK. A retry after an ACK reply loss is safe: the pipeline
    reports duplicate and the hub suppresses the already-emitted durable cursor.
    """
    if not isinstance(pipeline, OhlcvPipeline):
        raise TypeError("pipeline must be an OhlcvPipeline.")
    if not isinstance(stream_hub, OhlcvStreamHub):
        raise TypeError("stream_hub must be an OhlcvStreamHub.")
    bar = _bar_from_event(event)
    result = pipeline.apply(bar)
    if result not in {"inserted", "replaced", "duplicate"}:
        raise ReplicaPipelineDivergence(
            f"Durable replica event cannot be applied to the live pipeline: {result}."
        )
    stream_hub.publish(
        bar,
        durable_cursor=event["cursor"],
        durable_event_id=event["eventId"],
    )
    return result
