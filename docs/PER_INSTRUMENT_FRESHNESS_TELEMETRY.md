# Per-instrument freshness telemetry

Status: implemented as bounded observation telemetry; not a provider-health guarantee.

## Purpose

The backend now records the last successfully applied live OHLCV observation for each provider instrument key:

`(dataset, publisher_id, instrument_id, raw_symbol)`.

Each observation includes event-time high-water mark, receive timestamp, age since last observation (measured with a monotonic clock), and accepted live-record count. The tracker is bounded to 2,048 instrument keys by default and evicts the least-recently-updated key when capacity is exceeded.

## Important semantic boundary

OHLCV is trade/event driven. A symbol may legitimately produce no bar during a quiet interval. Therefore:

- The tracker reports `health: observed`, not `healthy` or `live`.
- It does not label an instrument stale merely because no OHLCV record arrived.
- Provider connection state remains a separate signal in ProviderManager.
- Per-instrument last-observed age is telemetry, not proof that a quote is current.
- Historical backfill does not update live-observation telemetry.
- Event timestamps retain their event-time meaning; receive time is measured separately.

A future provider adapter may add a provider-specific heartbeat or quote stream with documented semantics. Only then can the application define a meaningful instrument-level freshness threshold for that source. Thresholds must be source- and instrument-class-aware, not one global timeout applied to every pair.

## Current output

The ingestion status includes `instrument_observations`:
- tracked count and capacity;
- eviction counter;
- each instrument's canonical provider identifiers, event and receive timestamps;
- monotonic age since the latest accepted live observation;
- accepted live record count;
- explicit `not_inferred_from_OHLCV_silence` classification.

## Tests

Coverage verifies separate instrument keys, bounded retention, and the rule that quiet OHLCV intervals are not automatically classified stale.

## Not yet implemented / release gates

1. Provider-specific heartbeat/quote health with documented provider semantics.
2. Provider-native sequence/gap detection, after confirming the exact SDK schema exposes a documented sequence field. The local ingest sequence is not a provider sequence.
3. WebSocket delivery and client-render freshness metrics.
4. Per-provider and per-asset-class thresholds validated with staging measurements.
5. End-to-end 2.5-second latency certification.

No claim is made that all instruments are subscribed, that every pair has live coverage, or that an observation guarantees an executable current quote.
