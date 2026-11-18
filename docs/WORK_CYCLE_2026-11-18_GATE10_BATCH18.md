# Work Cycle Batch 18 — exact-head CI, WebSocket read-back and overall progress indicator

**Date:** 18 November 2026, 18:05 WIB  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Audited source:** `64f348cebccbfb3fad2b9efe5a066d28962970f6`  
**Cost:** ZERO COST • no Termux • no paid service • no production promotion

## 1. Exact-head CI read-back

Automated Tests run [44287587066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587066) completed with FAILURE at the final frontend dependency-audit enforcement step.

Passing steps:
- Frontend unit tests and production build.
- Frontend source and built-bundle credential scans.
- Android host preflight and immutable preview publisher tests.
- Backend pytest: **1,014 passed**.
- Synthetic SQLite outbox benchmark and artifact upload.
- Backend dependency audit.
- Backend container image build.
- Redis/persistent-volume smoke test.
- Trivy container scan and report export/upload.

The final enforcement failed because npm audit returned five High findings through development-only `picomatch@4.0.7`. The workflow is correctly fail-closed. No override, forced version change, suppression or waiver was applied.

CodeQL run [44287587070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587070) passed for Python and JavaScript/TypeScript.

## 2. Vercel deployment restriction resolved for this source

Both exact-SHA preview deployments are READY:
- WSS POC: `dpl_8iPQZm1Z2QJ4Dc8hjUPgSsPanPYb`
- Frontend: `dpl_FqhfGebn7fU6f7udkPFmByyG1WTY`

No billing activation, paid upgrade, SSO weakening or production promotion. Earlier rate limit does not apply to this current source deployment.

## 3. WebSocket evidence

Protected WSS `/health` returned HTTP 200 and synthetic-only JSON. Root page returned HTTP 200 and contains the browser WebSocket client and bounded probe controls.

The available HTTP connector cannot negotiate a WebSocket Upgrade. Therefore no actual WSS handshake, ping/pong, 330-second foreground run, platform close attribution, Android WebView test, Fluid Compute effective setting or cross-instance fan-out is claimed. Gate 36 remains open.

## 4. Correct overall-project accounting

The project progress specification says the M1–M8 weighting ledger is unapproved and unscored. Therefore:
- Stage 1 remains 75% provisional (300/400 ticks).
- Stages 2–6 remain NOT SCORED.
- Overall current percentage is NOT ESTABLISHED.
- 20.9% is the most recent owner-confirmed historical checkpoint only, not a newly verified current percentage.

Do not average 75% with five unscored stages. Do not award progress for docs, commits, deployment alone or code volume. A current overall percentage requires approved milestone weights and verified criterion mapping.

## 5. Gate 10

Still 0/10 formally closed. Open: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39. No new external acceptance evidence closes a gate in this batch.

## 6. Files updated

- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/STAGE_1_ACCEPTANCE_MATRIX.md`
- `docs/VERCEL_WEBSOCKET_POC.md`
- `docs/assets/project-progress-dashboard-batch18.svg`
- `docs/WORK_CYCLE_2026-11-18_GATE10_BATCH18.md`

Documentation and dashboard only; no application source/runtime behavior changed. `main` untouched.
