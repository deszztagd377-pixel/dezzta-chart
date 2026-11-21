# Work Cycle Batch 62J-91 — disk-full test liveness assertion correction

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent:** `bcffeb23c0170df9ffea516d555d5e548fb2f453`

## Failure analysis
Automated Tests [44905465144](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465144) reported 1,270 passed / 1 failed. The SQLite storage-exhaustion assertion correctly raised `sqlite3.OperationalError: database or disk is full`, and the aggregate rollback assertion passed.

The failing assertion expected one live worker at `snapshot(now=1801)`, but the last successful checkpoint was timestamp 900 and the stale threshold is 90 seconds. Since the failed flush at 1800 rolled back, last_seen remained 900; at 1801 the worker was correctly stale. The test now inspects at 901, where the checkpoint age is one second, proving that the failed flush did not advance it.

## Other tests
- App-level failure isolation: PASSED; collector degraded while HTTP health, authenticated metrics scrape and authenticated WebSocket status remained responsive.
- Read-only failure/recovery: PASSED.
- CodeQL [44905465128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905465128): SUCCESS.
- Full Git History Secret Audit [44905464959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905464959): SUCCESS.
- Corrected exact-head Automated Tests pending.

Only a test observation timestamp changed. No production collector or WebSocket behavior changed. Gate 38 remains 🟧 OPEN. Gate 10 remains 0/10 formally closed; Stage 1 remains 75% provisional; overall project remains unscored. ZERO COST; no deployment, Termux/device action or `main` modification.
