# Batch 62J-96 — revert regressive SQLite retry jitter

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Revert parent:** `5bb2f3f5e173b5278f09a736880edcb2277d6447`  
**Restored implementation:** exact Gate 38 collector/test contents from accepted diagnostic commit `6c191d96ec12b4effd1fd5957e0a31a4e2bee8a8`

## Decision

The 62J-95 deterministic per-worker retry-jitter experiment is rejected. Its code and test are reverted. Batch 62J-94's accepted phase instrumentation remains unchanged.

## Measured comparison

Same synthetic CI workflow shape, 899 logical series, 32 flushes per worker:

| Workload | Metric | 62J-94 baseline | 62J-95 jitter | Change |
|---|---|---:|---:|---:|
| 16 threads | p95 | 390.277 ms | 599.624 ms | +53.6% |
| 16 threads | p99 | 625.336 ms | 1,125.048 ms | +79.9% |
| 16 threads | max | 878.721 ms | 2,042.702 ms | +132.4% |
| 16 threads | retries | 105 | 181 | +72.4% |
| 4 threads | p95 | 120.249 ms | 190.787 ms | +58.7% |
| 4 processes | p95 | 62.234 ms | 139.278 ms | +123.8% |
| 4 processes | p99 | 275.777 ms | 279.107 ms | +1.2% |
| 4 processes | retries | 1 | 3 | +200% |

The 62J-95 attempt did not meet the no-regression requirement. The jitter strategy is not retained.

## Remaining interpretation

62J-94 remains the accepted diagnostic baseline: it separates writer-lock wait from transaction body/commit. Its benchmark runs simultaneous workers and is a stress case, not a faithful reproduction of the production startup phase staggering in `backend/app/main.py`. Before changing production scheduling or lock policy, the next benchmark should separately model the actual worker cadence and keep the simultaneous case as a worst-case stress profile.

## Validation and scope

The revert must pass exact-head Automated Tests, CodeQL and full Git-history secret audit. No WebSocket, auth, Redis, indicator, deployment or host changes are part of this revert. ZERO COST; no Termux/device operation; `main` untouched.

## Indicator and project accounting

No indicator implementation changed. SMA20/EMA20/RSI14/MACD12/26/9/Bollinger20,2/shared hook remain 🟨 foundation; Footprint 🟧 gated; Heatmap and Liquidation Maps 🟥 not implemented. Full formulas, warm-up indices and renderer gaps remain in the indicator ledger. No indicator progress credit. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed; overall project % remains unscored.
