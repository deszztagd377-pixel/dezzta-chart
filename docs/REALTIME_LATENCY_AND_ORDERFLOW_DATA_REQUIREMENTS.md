# Real-Time Latency and Order-Flow Data Requirements

Status: engineering contract; live-provider measurements are NOT YET VERIFIED.
Branch: phase-2/market-data-foundation

## 1. Latency objectives

The project will evaluate two end-to-end objectives:

- Ideal objective: <= 1,000 ms from provider gateway emission to the chart rendering the corresponding update.
- Operational objective: <= 1,500 ms for the same measured path.
- Above 1,500 ms: expose a delayed/degraded state. Never relabel delayed data as real-time.
- These are engineering objectives, not guarantees. Report p50, p95, p99, maximum, sample count, and measurement-window duration. Averages alone are insufficient.

Do not claim that the objectives pass based only on backend queue or processing timings.

## 2. Required measurement boundaries

Record independent timestamps at these boundaries:

1. Provider gateway emission: Databento `ts_out` when explicitly enabled and verified for the installed SDK/schema.
2. Backend callback receive: wall-clock timestamp plus monotonic timestamp captured immediately at callback entry.
3. Backend pipeline apply: monotonic timestamp after validated pipeline application.
4. WebSocket enqueue/send: monotonic timestamp at the server-side fan-out boundary.
5. Browser/phone receive: client monotonic timestamp when the WebSocket message is received.
6. Chart render: client animation-frame timestamp after the update has been applied to the chart.

Use monotonic clocks for durations within one process. Do not subtract monotonic timestamps from different machines. Cross-machine measurements require verified clock synchronization and an explicit uncertainty budget. Keep provider event time, provider gateway-send time, backend receive time, and client render time as separate fields.

The existing `callback_to_apply` metric measures only callback-to-pipeline-apply inside the backend. It is not end-to-end latency.

## 3. OHLCV semantics and limitations

Databento OHLCV records represent aggregate bars. For OHLCV schemas, `ts_event` marks the inclusive start of the aggregation interval. Intervals without trades produce no OHLCV record. Therefore:

- Do not infer feed failure solely from a missing OHLCV bar.
- Do not use the bar's interval-start timestamp as its gateway emission timestamp.
- Preserve late records in their original event-time bucket.
- Keep historical backfill separate from live freshness and latency samples.
- A 1-second OHLCV chart is not a substitute for event-level trades or order-book data.

## 4. Separate data paths for advanced visualizations

### Footprint

Footprint requires transaction-level data with the fields and semantics needed to classify traded volume by price and aggressor side. OHLCV alone does not contain bid/ask volume-at-price and cannot produce a trustworthy bid/ask footprint.

Before implementation, verify the selected provider schema, side/aggressor semantics, corrections, trade conditions, instrument mapping, and replay behavior. Unknown side must remain unknown; do not guess.

### Heatmap

A market-depth heatmap requires order-book updates or depth snapshots, with deterministic handling of add/modify/cancel/clear events, book state, sequence integrity where the selected schema supplies it, and snapshot/recovery behavior. OHLCV cannot reconstruct historical resting liquidity.

Do not label an OHLCV-derived visualization as an order-book heatmap.

## 5. Sequence, gaps, and reconnect recovery

Sequence numbers are schema-specific. Databento documents an original venue sequence field for applicable order-book records; do not assume that field exists on OHLCV bars.

For OHLCV recovery, follow the provider's documented replay model using per-instrument, per-schema `ts_event` and the count of records already seen at the last timestamp. Deduplicate replay overlap without dropping legitimate records that share a timestamp. Track reconnect boundaries and any provider-reported gap/replay-completed signals.

The current local ingestion sequence is an arrival-order identifier only. It must never be presented as a provider sequence or proof of gap-free market data.

## 6. Current implementation limitations (audit)

At the time this contract was added:

- `backend/app/ingest.py` measures backend queue delay, processing time, and callback-to-apply duration with a monotonic clock.
- It deliberately does not call event-time-to-receive delay network latency because clock synchronization has not been established.
- `backend/app/freshness.py` reports last accepted live OHLCV observations and explicitly avoids treating quiet intervals as stale.
- `backend/app/databento_sources.py` remains UNVERIFIED against a real SDK/network session, but now requests the documented `ts_out=True` Live option.
- The normalized OHLCV bar, HTTP snapshots, and WebSocket updates now preserve optional `ts_provider_out_ns` as `tsProviderOutNs`. Historical/derived bars and records without that field remain explicitly null.
- A fake-SDK unit test verifies the `ts_out=True` constructor option and the existing explicit raw-symbol subscription arguments. This verifies our wrapper contract only; it does NOT verify a real Databento connection or actual `ts_out` payloads.
- `backend/app/ohlcv_stream.py` has a bounded server fan-out queue and disconnects slow consumers, but client receive-to-render timing is not yet instrumented.
- No live credentials/network integration test or end-to-end client-render latency certification has been completed.

## 7. Acceptance criteria before calling 1.0s / 1.5s successful

1. Verify the exact installed Databento SDK version and its documented/actual behavior in a controlled integration environment.
2. Capture gateway-send, backend-receive, backend-apply, server-send, client-receive, and chart-render boundaries.
3. Validate clock synchronization and publish its uncertainty; otherwise report only per-process segments and mark cross-host end-to-end latency unavailable.
4. Test steady traffic, bursts, delayed/out-of-order records, duplicate replay, reconnect, slow-reader warnings, queue overflow, and client background/resume.
5. Report p50/p95/p99/max separately for each instrument, schema, and connection session.
6. Verify the chart marks delayed/degraded data and never silently presents stale data as live.
7. Verify 1-second, 5-second, 15-second, 1-minute, and higher timeframe aggregation from the same canonical event-time stream, including late revisions.
8. Run separate schema-specific acceptance tests for Footprint trades and Heatmap order-book state before either visualization is called accurate.

## 8. Safety and product boundary

This project is a market-data visualization and analysis system. Data quality, timestamps, and chart labels must be transparent. No latency target, feed, or visualization can guarantee that a market is free from manipulation or that a user's interpretation is correct.

## 9. Mandatory zero-cost market-data and timeframe contract (owner decision 2026-11-10)

ZERO MONEY is a hard constraint. Databento live and historical access is not an approved source under the current owner decision. Do not enable it, request a key, start a trial, attach a payment method, or silently substitute a paid provider. Any candidate public/free source must first pass a documented zero-cost preflight covering payment requirements, quota exhaustion, overages, auto-upgrade/trial conversion, terms, redistribution rights, supported instruments, event timestamp semantics, and measured freshness. Unknown billing or licensing behavior means the source stays disabled.

The complete configured timeframe set must remain supported by the data model and aggregation layer:
`1s, 5s, 15s, 30s, 45s, 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 4h, 1d, 1w, 1M, 3M`.

A 1-second base stream must remain the finest OHLCV input where a verified source provides it. Derived timeframes must use event-time bucket boundaries, preserve late revisions, replace rather than add revised volume, and never invent candles for missing intervals. A timeframe being selectable or derivable does not prove that its source data is available or current.

Bucket policy is instrument/session-specific:
- UTC-fixed intraday aggregation may derive the configured intraday tiers through 4h.
- Daily/weekly/monthly/quarterly buckets for exchange-traded instruments must use the approved, versioned exchange-session calendar and its authoritative tradable segments. Do not relabel UTC-midnight buckets as exchange sessions.
- Where the source or calendar is not verified, keep that market/timeframe combination unavailable or explicitly partial; do not fabricate a session boundary.
- Provider-supplied higher-timeframe bars retain precedence under the existing pipeline rules.

Current verified repository capability: the backend aggregation tests exercise the complete configured timeframe parent chain from 1s input, while the UTC_FIXED_V1 policy deliberately stops before session-dependent 1d/1w/1M/3M. The frontend timeframe engine tests that all configured timeframe bucket functions are recognized. These are code/test capabilities, not proof of a free real-world feed, universal instrument coverage, or the 1.0s/1.5s end-to-end latency objectives.

Release gate: no live-data claim until a specific zero-cost source, instrument universe, terms, and event-to-screen measurements are verified. If no compliant source provides a market/instrument at 1s granularity, expose that limitation rather than silently downgrading the feed or fabricating 1s bars.
