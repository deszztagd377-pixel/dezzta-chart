# Work Cycle 2026-11-21 — Batch 62J-94: SQLite tail-latency phase instrumentation

## Scope
- Active branch: `phase-2/market-data-foundation`; parent HEAD: `5d77340057c1b99c9cf0e235a56136385963b72e`.
- No deployment, paid service, host, Termux/device operation, or `main` change.
- WebSocket protocol, auth, replay, snapshot, cursor and Redis paths are untouched.
- Indicator formulas, contracts, hook, renderer and UI are untouched.

## Rationale
Batch 62J-93 reduced bucket SELECT statements from 899 to 1 per flush, but tail latency remained mixed. End-to-end p99 and retry counts alone cannot identify whether delay comes from SQLite's single-writer lock or work performed after acquiring it.

## Changes
1. `SQLiteMetricsCollector.flush()` now returns:
   - `lock_wait_ms`: time immediately before bounded `BEGIN IMMEDIATE` acquisition through successful acquisition. Includes SQLite's 250 ms busy timeout and explicit backoff.
   - `transaction_ms`: time from successful acquisition through commit. Includes transaction reads, Python aggregation/JSON encoding, SQL writes, retention/capacity work and commit.
2. The 1/4/16-thread and four-OS-process benchmark reports p50/p95/p99/mean/max for both phases beside end-to-end flush latency.
3. Tests assert timing fields are non-negative and benchmark output includes every sample for all concurrency cases.

## Interpretation and acceptance
The two phases do not sum exactly to end-to-end latency because input flattening/encoding and connection/bootstrap occur outside these boundaries. This is diagnostic instrumentation, not an optimization, SLA or owner-host result. Exact-head CI must pass before accepting the instrumentation. Next optimization decision must be based on whether lock wait or transaction duration dominates, without weakening atomicity, checkpoint ordering, rollback, retention or failure isolation.

## Indicator progress
No indicator code changed; no progress credit. SMA20 🟨 (20-close arithmetic mean; first valid index 19); EMA20 🟨 (SMA-seeded, alpha 2/21; index 19); RSI14 🟨 (Wilder smoothing; index 14); MACD 12/26/9 🟨 (MACD index 25; signal/histogram index 33); Bollinger20,2 🟨 (mean ±2 population SD; index 19); Shared Indicator Hook 🟨 foundation; Footprint 🟧 simulated/gated pending user visual reference, approved blueprint and ON-only spaced cluster renderer; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Renderer, toggle, legend, stale-clearing, identity/timeframe and data-source work remains as detailed in the indicator ledger. Warm-up remains null, values candle-index aligned, no future-candle repaint, identity changes clear stale series; Footprint OFF preserves normal candle spacing. Aggregate indicator % remains unscored without approved weights/denominators.

## Project accounting
Stage 1 remains 30/40 criteria = 300/400 ticks = 75% provisional. Gate 10 remains 0/10 formally closed pending external acceptance evidence. Overall project % remains unscored. ZERO COST; no deploy, Termux or device operation.
