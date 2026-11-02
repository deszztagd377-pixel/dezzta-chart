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

## Server/client lifecycle still required

Before this contract can carry production updates, implementation must add:

1. An authenticated subscription message containing the exact series identity.
2. A server-side subscription manager that filters events to that identity.
3. A per-subscription stream sequence and an atomic snapshot/watermark handshake,
   so events cannot be lost between snapshot creation and stream activation.
4. Bounded per-client queues and explicit slow-consumer handling; never silently
   discard a bar update.
5. Heartbeats, disconnect detection, reconnect with a new or resumed stream ID,
   and bounded retry/backoff.
6. Snapshot resynchronization after a gap or server restart.
7. Frontend application of accepted updates through the shared market-data store.
8. Tests for concurrent subscribe/snapshot ordering, duplicate revisions,
   out-of-order messages, overflow, reconnect, and server shutdown.

The current backend WebSocket only authenticates and sends a status message.
It does not yet implement this OHLCV event stream. The HTTP snapshot endpoint
also does not yet provide a stream watermark; that handshake must be designed
and tested before a real client subscribes.
