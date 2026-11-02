# DEZZTA CHART — OHLCV streaming protocol v1

## Scope

This document and the matching frontend parser define the first transport-neutral
OHLCV update contract. They do not establish a live WebSocket connection or claim
that the backend currently broadcasts these events.

## Event envelope

A stream update uses:

- `type`: `market_data.ohlcv.update`
- `version`: integer `1`
- `streamId`: identifier for one server-side subscription session
- `eventId`: non-empty event identifier for diagnostics/deduplication
- `sequence`: positive safe integer, monotonic within `streamId`
- `emittedAtNs`: server emission timestamp in Unix nanoseconds, decimal string
- `operation`: currently `upsert`
- `isFinal`: whether the bar is finalized; false means a revision may follow
- `series`: exact dataset/publisher/instrument/raw-symbol/timeframe identity
- `bar`: the existing canonical OHLCV bar DTO

Example shape (illustrative values only; not market data):

```json
{
  "type": "market_data.ohlcv.update",
  "version": 1,
  "streamId": "subscription-identifier",
  "eventId": "event-identifier",
  "sequence": 42,
  "emittedAtNs": "1793577601000000000",
  "operation": "upsert",
  "isFinal": false,
  "series": {
    "dataset": "GLBX.MDP3",
    "publisherId": 1,
    "instrumentId": 123,
    "rawSymbol": "ESZ6",
    "timeframe": "1s"
  },
  "bar": {
    "dataset": "GLBX.MDP3",
    "provider": "databento",
    "publisherId": 1,
    "instrumentId": 123,
    "rawSymbol": "ESZ6",
    "seriesType": "contract",
    "timeframe": "1s",
    "tsStartNs": "1793577600000000000",
    "open": "6000.125",
    "high": "6001.250",
    "low": "5999.875",
    "close": "6000.750",
    "volume": "12",
    "tsEventNs": "1793577600999000000",
    "tsReceivedNs": "1793577601000000000",
    "sequence": 7,
    "sequenceOrigin": "local",
    "origin": "provider",
    "completeness": "open"
  }
}
```

The outer `sequence` is the stream delivery sequence. The nested `bar.sequence`
is the existing local ingestion/revision sequence. They are different counters
with different scopes and must never be substituted for one another.

## Validation and ordering

The frontend parser reuses the existing snapshot bar validator. It therefore
checks decimal-string syntax, nanosecond timestamps, supported timeframe,
OHLCV boundaries using exact integer decimal arithmetic, and exact equality
between the declared series and the bar identity.

The sequence guard is initialized with a verified snapshot watermark:

- next sequence: accept and advance the watermark
- same sequence: duplicate; ignore
- lower sequence: stale/out-of-order; ignore
- higher-than-next sequence: gap; do not advance or apply the event
- another stream or series: reject

A detected gap requires a fresh, validated snapshot plus its matching stream
watermark before the guard is reset. Do not simply jump the watermark to the
received event: that would silently lose missing updates.

## Implemented backend lifecycle

The backend now accepts an authenticated `market_data.subscribe` version 1
message with the exact dataset/publisher/instrument/raw-symbol/timeframe
identity. It performs the snapshot query and registers a per-series subscriber
synchronously on the same asyncio event loop, without an await between those
operations. The returned snapshot carries a per-subscription `streamId` and
initial `watermark`; subsequent accepted updates are numbered from that
watermark. This is the atomic handoff boundary for the current single-process,
single-writer in-memory design.

Accepted base bars and accepted derived-timeframe revisions are published to
matching subscribers. Each subscriber has a bounded queue. On overflow, the
subscription is marked and the WebSocket closes with code 1013 so the client
must reconnect and obtain a fresh snapshot; the server does not silently skip
an update to keep the socket alive. Client disconnects remove subscriptions.

## Remaining lifecycle work

1. Frontend WebSocket client: authentication, exact-series subscription,
   snapshot validation, sequence guard initialization, and accepted update
   publication into the shared market-data store.
2. Client heartbeat/ping cadence, bounded reconnect/backoff, stale-feed status,
   and automatic snapshot resynchronization after sequence gaps or close 1013.
3. Tests for full WebSocket update delivery, disconnect cleanup, overflow close,
   and concurrent client behavior under a running provider ingestion loop.
4. Durable replay/recovery across backend restarts is not implemented. Every
   reconnect currently receives a fresh in-memory snapshot and new stream ID.

The HTTP snapshot endpoint remains independently available and does not yet
carry a stream watermark; the atomic watermark is currently supplied by the
WebSocket subscription snapshot response. No production provider connection,
order-book/MBO stream, or end-to-end live frontend integration is claimed.
