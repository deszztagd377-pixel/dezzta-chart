# WORK CYCLE — Batch 62J-168: Replica Lease Shutdown Observability

Date: 23 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent/source HEAD: `0941c4ee4400a0ab4b2481fb12af4b47d5a293ea`  
Scope: replica shutdown resource cleanup and regression coverage.

## Finding

The ASGI lifespan shutdown path called `ownership_lease.release()` but discarded its boolean result. A Redis-side token mismatch or temporary Redis outage can make release unconfirmed. The lease is protected by a finite TTL, so expiry remains the safe fallback, but operators were not told that release was unconfirmed. The cleanup branch for a replica runtime that failed before worker creation also had less defensive Redis-client-close handling than the normal worker-stop branch.

## Correction

- Centralized best-effort lease release in the lifespan finalizer.
- Treat exceptions and a false release result as unconfirmed, never as success.
- Emit a warning that Redis TTL expiry is the fallback.
- Centralized replica Redis client close and catch/log close failures consistently.
- Run both cleanup operations after a clean worker stop and in the pre-worker startup-failure path.
- Preserve the safety rule: if the worker misses its shutdown deadline, do not release its lease or close its Redis client while its thread may still be using them.

## Regression test

Added `test_replica_shutdown_logs_unconfirmed_lease_release_and_closes_redis`. Its fake Redis confirms lease ownership and heartbeat, then deliberately returns zero for token-checked release. The test verifies the warning is emitted and the Redis client is still closed after worker shutdown. This is deterministic and requires no paid service or external Redis.

## Acceptance boundary

This covers application-level cleanup behavior. It does not prove cross-host lease recovery under a real network partition, nor does it replace TTL-based takeover tests against an externally configured Redis instance.

## Changed files

1. `backend/app/main.py`
2. `backend/tests/test_api.py`
3. `docs/WORK_CYCLE_2026-11-23_BATCH62J168_REPLICA_LEASE_SHUTDOWN.md`
4. `docs/INDICATOR_PROGRESS_LEDGER.md`
5. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`

## Indicator progress — unchanged

No indicator formula, kernel, hook, chart binding, renderer, UI, or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator | Status | Foundation / remaining acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA seed, alpha 2/21; first valid index 19; overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 population SD; first valid index 19; three-line overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference, reviewed blueprint and valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference, reviewed blueprint and validated depth/liquidity contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/calculation contract and reviewed implementation required |

Invariants: warm-up nulls; exact candle alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.

## Overall project progress

- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external acceptance criteria formally closed 🟥.
- Gate 25: OPEN 🟧 — local digest binding and receipt-set validation improved; authenticated cross-host receipt/key lifecycle remains.
- Gate 36: OPEN 🟥 — public production WSS, real Firebase, reverse proxy and physical Android WebView acceptance remain.
- Gate 38: OPEN 🟥 — owner-host metrics persistence, backup/retention, alert and recovery acceptance remain.
- Overall project: NOT SCORED; approved stage weights and denominator are unavailable.

ZERO COST. No paid service, deployment, credentials, physical device or publication fee. `main` untouched.
