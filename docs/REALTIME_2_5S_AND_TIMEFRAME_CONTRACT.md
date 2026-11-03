# DEZZTA CHART — 2.5-second latency and timeframe contract

Status: target policy and regression contract; end-to-end latency is not yet certified.

## Product requirement

- Target maximum observed event-to-screen delay: **2.5 seconds**.
- All supported timeframes, including **1s, 5s, 15s, 30s, and 45s**, must remain selectable and correctly bucketed when records arrive late.
- A late record is still assigned to its original event-time candle. Receive time must never replace event time.
- A late update may revise an older candle and its derived parent candles. It must not be shifted into the newest candle, duplicated, or used to fabricate missing intervals.
- If an update is measured above 2.5 seconds, the UI must identify the feed as delayed/degraded. It must not silently present the update as fresh.

## What 2.5 seconds means

The product target is end-to-end: provider event timestamp -> provider delivery -> backend callback/queue -> normalization and aggregation -> WebSocket delivery -> client receive -> chart render.

The existing `live_latency` metrics cover only backend callback-to-apply. They do **not** measure provider transit, WebSocket transit, phone scheduling, or chart rendering. Therefore they cannot yet prove the 2.5-second target.

A trustworthy end-to-end measurement requires:
1. A provider event timestamp with documented semantics and verified clock synchronization.
2. Backend receive and apply timestamps from monotonic clocks.
3. WebSocket emitted timestamp and event ID.
4. Client receive and render timestamps from a monotonic clock.
5. Staging measurements on the intended hosting region and Android devices.

Until those pieces exist, 2.5 seconds is an engineering target, not a service guarantee. Clock skew must be detected; an unsynchronized wall-clock subtraction must never be labelled network latency.

## Timeframe correctness under delayed arrival

- Candle identity and bucket placement use the provider's event-time timestamp.
- Receive time is telemetry only; it never changes `ts_start_ns`.
- A late 1-second record can revise its original 1-second bar. Aggregation recomputes affected 5-second, 15-second, 30-second, 45-second, minute, and higher-timeframe parents from the same event-time bucket hierarchy.
- Existing bars are revised idempotently; volume is replaced, not added twice.
- Missing source intervals remain missing. No synthetic candles are inserted to make the chart look continuous.
- Out-of-order arrival is allowed when the pipeline can safely apply the event-time revision; stale revisions remain rejected by the pipeline ordering rules.

## Degraded-state behaviour

- A measured event-to-screen delay above 2.5 seconds is shown as delayed/degraded once end-to-end measurement is available.
- Provider disconnect, queue overflow, unverified timestamps, sequence gaps (when the provider exposes usable sequence metadata), or client queue overflow must be visible and must not be disguised as a live/healthy feed.
- A quiet instrument is not automatically stale: OHLCV records may be absent when no trades occur. Connection health and per-instrument last observed trade must be reported separately.
- No alerts may trigger from stale, out-of-order, incomplete, or unverified data.

## Regression coverage added

`test_late_arrival_preserves_original_one_second_bucket_and_derived_timeframes` verifies that a 1-second bar received 2.5 seconds after its event time remains in its original 1-second bucket and contributes to the correct 5-second and 1-minute buckets.

This test verifies event-time correctness only. It does not simulate a real provider, network, WebSocket, Android render, or certify the 2.5-second end-to-end target.

## Remaining release gates

1. Verify Databento SDK and OHLCV record semantics against the actual installed SDK and a controlled live account.
2. Verify whether the selected provider schema exposes a documented per-instrument sequence number. The current OHLCV adapter assigns a **local ingest sequence**; it must not be mistaken for a provider sequence or used to claim provider gap detection.
3. Add bounded per-instrument freshness/connection-health telemetry without treating no-trade periods as feed failures.
4. Add WebSocket and Android receive/render timing, then benchmark p50/p95/p99 and every >2.5s breach.
5. Only after measured staging results should the 2.5-second target be considered release-ready.
6. Add provider coverage and canonical instrument mapping before claiming support for all pairs.

No absolute latency, uninterrupted feed, universal pair coverage, or trading outcome is guaranteed.
