# DEZZTA CHART — Market-data latency and integrity

Status: engineering checkpoint; no production latency SLO has been certified.

## Objective

Market data must be timely and trustworthy. The system must measure delays it can observe, expose missing/degraded states, and never relabel stale or sample data as live. Low latency is not a guarantee against trading losses.

## Current pipeline boundary

The backend currently has a Databento OHLCV-1s adapter, a bounded callback buffer, a single-writer ingestion loop, a normalized OHLCV pipeline, and WebSocket fan-out. The Databento SDK wrapper is explicitly marked unverified against the real SDK and has not yet been validated with production credentials/network access. Configured live symbols are explicit contract symbols; the default allowed roots ES/NQ/GC are not evidence that all global pairs are supported.

## Latency instrumentation checkpoint

`OhlcvIngestionService.status().live_latency` reports rolling measurements over the last 256 accepted live records:

- `queue_delay`: monotonic time from provider callback enqueue to backend processing start.
- `processing`: monotonic time spent converting and applying the normalized bar to the in-memory pipeline.
- `callback_to_apply`: sum of the two above, a backend-local measurement.
- Each distribution includes sample count, p50, p95, and maximum in milliseconds.
- Historical backfill does not pollute live latency samples.
- Event timestamp vs backend wall-clock differences are not presented as network latency because clock synchronization is not yet certified. Negative differences are counted as possible clock-skew observations.

These metrics do not measure provider-to-backend network transit, backend-to-phone transit, rendering delay, or exchange-to-screen end-to-end latency. Those require synchronized clocks, provider timestamps/sequence metadata, client receive/render telemetry, and real-device testing.

## Required next reliability work

1. Verify the exact Databento SDK version, live subscription signatures, reconnect behaviour, and record schemas against a controlled real account.
2. Track provider sequence numbers where available; detect duplicates, out-of-order records, and sequence gaps per instrument.
3. Add explicit per-instrument last-event/last-receive freshness, while accounting for instruments with no trades in a given interval.
4. Add a client-side receive/render timestamp path and correlate event IDs without trusting client clocks as authoritative.
5. Define measured p50/p95/p99 budgets only after staging benchmarks on the target hosting region and Android devices.
6. Implement provider coverage and canonical instrument mapping before claiming support for any pair.
7. Add multi-provider or reconnect/backfill recovery where licensing and provider APIs allow; expose gaps rather than filling them with fabricated bars.

## Data integrity rules

- Preserve source event timestamps and provider sequence metadata when available.
- Never substitute demo/sample bars into an active live series without a persistent visible DEMO status.
- Do not trigger price alerts from stale, out-of-order, incomplete, or unverified records.
- On buffer overflow or slow-client queue overflow, record a gap and mark the stream degraded; require a resnapshot/backfill.
- A quiet OHLCV interval is not proof of a missing feed: some instruments have no trades. Freshness policy must distinguish no-trade periods from a dead connection.
- Do not promise zero latency, zero loss, or universal all-pair coverage.

## Current release gate

This checkpoint only adds backend-local ingestion latency observability. It does not certify the provider SDK, network latency, real-time all-pair coverage, WebSocket user authorization, production operation, or trading suitability.
