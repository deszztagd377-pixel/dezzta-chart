# DEZZTA CHART — Work Cycle 62J-61: Gate 39 restart recovery and incident deduplication

**Date:** 21 November 2026
**Branch:** `phase-2/market-data-foundation`
**Source/test HEAD:** `f60faa44c4ce18f04f08e93462422b51363c3d5e`
**Scope:** Gate 39 durable incident recovery and concurrent SQLite writer regression coverage
**Cost:** zero; no deployment or external service

## 1. Defect and impact

The alert-delivery incident journal persists to SQLite, but `LocalAlertReporter._last_state` is process-local memory. After a backend restart, a new reporter starts with `_last_state = None`. If the worker's first post-restart batch is healthy, the old implementation does not call `resolve_category()`. An incident created by the previous process can therefore remain `open` and continue to be escalated even though delivery has recovered.

## 2. Source correction

File changed: `backend/app/alert_operations.py`.

- Added `_journal_reconciled` to track whether the durable journal has been reconciled by the current reporter process.
- On the first healthy batch after startup, the reporter calls `resolve_category('alert_delivery')` even when it has no in-memory degraded state.
- A positive resolved-row count emits one sanitized recovery event. An empty journal produces no false recovery event.
- Successful reconciliation is remembered so subsequent healthy batches do not repeatedly write to SQLite.
- If the journal update fails, the reporter does not mark reconciliation complete; a later healthy batch can retry. The failure remains sanitized in logs.
- Existing transition-based recovery still runs after a degraded state within the same process.

## 3. Regression coverage

File changed: `backend/tests/test_incident_store.py`.

1. `test_new_reporter_reconciles_persisted_incident_after_process_restart`: creates an open incident with one store, starts a fresh reporter against a new store instance for the same SQLite path, submits healthy batches, and verifies the incident becomes resolved with exactly one recovery log.
2. `test_concurrent_store_instances_deduplicate_active_incident_writes`: four independent store instances issue 10 writes each for one fingerprint. Expected final state: one active incident row and `occurrence_count = 4 × 10 = 40`.

The store uses `BEGIN IMMEDIATE` and a partial unique index on active fingerprints. The new test verifies those existing concurrency protections under multiple independent connections.

## 4. Exact-head verification

- Automated Tests [44854569804](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44854569804): **SUCCESS**; frontend **247/247 across 29 files**; backend **1,220 passed in 49.35 seconds**; all 33 workflow steps succeeded.
- CodeQL [44854569759](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44854569759): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44854569709](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44854569709): **SUCCESS**.
- Backend dependency audit, container build, Redis shared-guard/persistent-volume smoke, Trivy scan and vulnerability report export succeeded.

## 5. Indicator progress — unchanged and fully tracked

| Indicator | Status | Formula / seed | First valid index | Remaining work |
|---|---|---|---:|---|
| SMA20 | 🟨 | 20-close arithmetic mean | 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 | SMA-seeded; alpha 2/21 | 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 | Wilder smoothing over 14 close-to-close changes | 14 | 0–100 pane, 30/70 guides, toggle, legend, render/lifecycle tests |
| MACD12/26/9 | 🟨 | EMA12 − EMA26; EMA9 signal | MACD 25; signal/histogram 33 | Dedicated pane, lines, histogram, zero guide, toggle, legend and render tests |
| Bollinger20,2 | 🟨 | 20-close mean ± 2 population standard deviations | 19 | Three-line overlay, toggle, current values, stale clearing, render tests |
| Shared Indicator Hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Snapshot-dependent | Active chart identity/timeframe binding, loading/error states, stale clearing, cross-series isolation |
| Footprint | 🟧 | SIMULATED educational accumulator | Candle/price-level dependent | Owner reference image, reviewed blueprint, ON-only spaced cluster renderer, bid/ask cells and performance tests |
| Heatmap | 🟥 | Data source/calculation contract not approved | N/A | Owner reference, reviewed blueprint, validated data contract and renderer |
| Liquidation Maps | 🟥 | No validated liquidation dataset/calculation contract | N/A | Source feasibility, approved calculation, reference/blueprint and renderer |

Correctness contracts remain unchanged: candle-index alignment; warm-up outputs are null, never fabricated zeros; symbol/venue/dataset/timeframe changes invalidate stale values. Footprint OFF must preserve normal candlestick spacing; only explicit ON may use the dedicated spaced-cluster layout. Footprint/Heatmap visuals remain gated on the owner's reference images and reviewed blueprints.

## 6. Gate and project accounting

- Gate 39 has improved repository-level behavior but remains OPEN pending owner-host route restriction, operator-token injection/rotation, real alert visibility, acknowledgement/escalation and incident recovery drill.
- WebSocket E remains complete for the defined automated dual-ASGI/Redis failure matrix. Public WSS, production Redis TLS/ACL and browser/Android acceptance remain external.
- Stage 1 remains **30/40 = 300/400 = 75% provisional**. Gate 10 remains **0/10 formally closed**; open gates: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- No Stage 1 tick is awarded. Overall project and aggregate indicator percentages remain unscored pending approved weights and denominator.

## 7. ZERO COST and device boundary

No paid notification provider, deployment, Vercel/Cloudflare operation, Termux command, production credential, physical-device test, or `main` branch modification occurred. The code correction and regression tests ran in GitHub CI only.