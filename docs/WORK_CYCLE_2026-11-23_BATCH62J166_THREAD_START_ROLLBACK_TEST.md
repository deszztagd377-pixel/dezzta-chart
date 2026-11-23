# WORK CYCLE — Batch 62J-166: Consumer Thread Startup Rollback Test

Date: 23 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent/source HEAD: `31bf4fb2a0a35dc999e6c3f410b8e018276c0fec`  
Scope: Redis worker lifecycle regression coverage only.

## Finding

Batch 62J-164 made worker startup transactional and already covered lease-heartbeat initialization failure and ownership loss. One rollback branch remained without a dedicated test: lease heartbeat starts successfully, but `threading.Thread.start()` raises before the consumer can run.

## Change

Added `test_worker_start_stops_heartbeat_when_consumer_thread_cannot_start`.

The test injects a deterministic thread-start failure and verifies:
- lease heartbeat call order is exactly start → stop;
- the original thread-start exception is propagated;
- worker state returns to `stopped`;
- diagnostic error type is `RuntimeError`;
- no live worker thread is retained;
- the stop event is set;
- consumer work never starts.

No production worker code was changed because the inspected rollback branch already performs these actions. This batch adds missing executable evidence rather than changing verified behavior.

## Test / CI

Submitted to exact-HEAD GitHub Actions. No local test execution is claimed. Acceptance waits for all four required workflows on this commit. Any failure will be inspected and repaired before the batch is marked accepted.

## Changed files

1. `backend/tests/test_ohlcv_redis_worker_lifecycle.py`
2. `docs/WORK_CYCLE_2026-11-23_BATCH62J166_THREAD_START_ROLLBACK_TEST.md`
3. `docs/INDICATOR_PROGRESS_LEDGER.md`
4. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`

## Indicator progress

No indicator code, formula, hook, renderer, UI, or test changed. Indicator progress credit: **0**.

| Indicator / subsystem | Status | Foundation / next acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; chart overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19; chart overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; 0–100 pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference + reviewed blueprint + valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference + reviewed blueprint + validated depth contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/contract and reviewed implementation required |

Preserve warm-up nulls, exact candle alignment, prefix causality/no future repaint, invalid/gapped-data rejection, stale-output clearing, and Footprint OFF normal candle spacing. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.

## Overall project progress

- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest binding improved by Batch 165; cross-host authenticated receipt and key lifecycle remain.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; stage weights and denominator are not approved.

ZERO COST. No paid services or external resources. `main` untouched.
