# Work Cycle Batch 62J-90 — disk-full and app-level isolation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline HEAD:** `2650c70e977b22a4c70a5e0e292dcc3a8a59082c`

## Accepted baseline
- Automated Tests [44904944196](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944196): SUCCESS, 35/35 steps; frontend 255/255 across 29 files; backend 1,269 passed in 53.67s.
- CodeQL [44904944207](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944207): SUCCESS.
- Full Git History Secret Audit [44904944202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944202): SUCCESS.
- Process benchmark: 4 independent OS processes, 128/128 flushes, 899/899 series, SQLite integrity `ok`; p95 243.724ms, p99 278.107ms, max 415.647ms, 4 retries.
- Thread benchmark 16 workers: 512/512 flushes, 899/899 series, p95 654.798ms, p99 921.534ms, max 2,769.913ms, 251 retries. This remains an elevated contention tail.

## Changes in this cycle
1. Add a full-cardinality SQLite storage-exhaustion regression using `PRAGMA max_page_count`. The database is checkpointed and VACUUMed, then capped at its current page count; a second full 899-series bucket must fail with SQLITE_FULL. Verify transaction rollback, unchanged checkpoint/aggregate, and successful retry without double counting.
2. Add app-level isolation coverage. Force metrics flush to fail with a storage-full error; verify collector status degrades while HTTP health, authenticated metrics scrape, and authenticated WebSocket status continue to respond.
3. No production collector algorithm or WebSocket protocol/data path change.

## Acceptance state
Exact-head CI for these new tests is pending. Do not close Gate 38 until they pass. Owner-host persistent volume, permissions, restart persistence, backup/restore, retention, real disk pressure and operator recovery remain external.

Indicator state unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project percentage unscored.

ZERO COST. No deployment, paid provider, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.


## Batch 62J-91 — disk-full test liveness assertion timing correction

Automated Tests [44905465144](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465144) reported 1,270 passed / 1 failed. The SQLite `SQLITE_FULL` exception and aggregate rollback assertions passed. The only failure was the test expecting one live worker at snapshot time 1801 although the last successful checkpoint was 900 and the stale threshold is 90 seconds; the collector correctly reported zero live workers. The test now checks at timestamp 901 (checkpoint age 1 second). The app-level HTTP/WebSocket failure-isolation test and read-only recovery test passed. CodeQL [44905465128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465128) and Full Git History Secret Audit [44905464959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905464959) passed. Exact-head Automated Tests rerun pending. No collector code or indicator implementation changed.


## Batch 62J-92 — exact-head CI acceptance

The corrected disk-full liveness assertion is accepted on exact HEAD `427e5952d2f209ae1f40405223d8d0a4c7d8408c`: Automated Tests [44905839386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839386) SUCCESS (35/35 steps; frontend 255/255; backend 1,271 passed in 39.80s), CodeQL [44905839403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839403) SUCCESS, Full Git History Secret Audit [44905839442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839442) SUCCESS. The real SQLite page-limit exhaustion/rollback/recovery test, app-level HTTP/WebSocket isolation test and read-only recovery test all passed.
