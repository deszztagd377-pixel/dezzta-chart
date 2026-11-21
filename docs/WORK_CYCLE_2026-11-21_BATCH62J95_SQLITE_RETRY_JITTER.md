# Work Cycle 2026-11-21 — Batch 62J-95: de-synchronize SQLite lock retries

## Starting evidence
- Parent source/test commit: `6c191d96ec12b4effd1fd5957e0a31a4e2bee8a8`.
- Batch 62J-94 exact-head Automated Tests passed: 1,271 backend tests; CodeQL passed for Python and JavaScript/TypeScript; full Git-history secret audit passed.
- Full-cardinality 899-series artifact (CI runner, 32 flushes/worker): at 16 threads, end-to-end p99 625.336 ms, writer-lock-wait p99 617.533 ms, transaction-body/commit p99 22.998 ms, 105 retries. At four OS processes, end-to-end p99 275.777 ms, lock-wait p99 103.635 ms, transaction p99 20.412 ms, one retry.
- This isolates lock contention as the dominant measured tail in these synthetic concurrent cases; it does not establish production-host latency.

## Change
The previous retry schedule used identical deterministic delays (10, 20, 40, 80, 160, 250, 250 ms) for every worker. Contending workers could therefore wake and retry together. The collector now derives a stable per-worker jitter factor from a BLAKE2s digest of the worker ID and scales each exponential delay by 0.5–1.0.

## Bound calculation
- Existing explicit-backoff ceiling: 10 + 20 + 40 + 80 + 160 + 250 + 250 = 810 ms = 0.81 s.
- New per-worker factor: 0.5 ≤ factor ≤ 1.0.
- New explicit-backoff total: 0 < total ≤ 0.81 s.
- SQLite busy timeout remains 250 ms per each of at most 8 BEGIN attempts: 8 × 0.25 = 2.00 s maximum.
- Total theoretical lock-acquisition wait remains ≤ 2.00 + 0.81 = 2.81 s, excluding transaction execution. No retry count, transaction atomicity, rollback, checkpoint, retention, capacity or failure-isolation policy is relaxed.
- Hash-derived jitter is deterministic per worker, so no random source, network call or additional service is required.

## Tests and acceptance
- Added deterministic jitter diversity and strict upper-bound test across 16 synthetic worker IDs.
- Exact-head CI and fresh 899-series benchmark must pass.
- Compare phase p95/p99 and retries against Batch 62J-94. If results regress, revert this source change rather than claim an improvement.
- No deployment, paid service, Termux/device operation, production credentials or `main` change.

## Indicator progress
No indicator source changed; no progress credit. SMA20 🟨 (20-close mean, first valid index 19); EMA20 🟨 (SMA-seeded, alpha 2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD 12/26/9 🟨 (MACD index 25; signal/histogram index 33); Bollinger20,2 🟨 (mean ±2 population SD, index 19); Shared Indicator Hook 🟨 foundation; Footprint 🟧 gated pending user reference, approved blueprint and ON-only spaced cluster renderer; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. Existing renderer/toggle/legend/stale-clear/identity/timeframe/data-source requirements and invariants remain as documented in the indicator ledger. Aggregate indicator % remains unscored without approved weights and denominators.

## Project accounting
Stage 1 remains 30/40 = 300/400 = 75% provisional. Gate 10 remains 0/10 formally closed. Overall project % remains unscored. No Gate 10 tick is awarded by synthetic CI. ZERO COST.
