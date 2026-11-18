# Work Cycle — Batch 39: WebSocket Lifecycle Integration Acceptance

**Date:** 18 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent exact HEAD:** `09a81b455fb12b15515899d366bb9b2f1318fb54`  
**Scope:** Component-level lifecycle regression tests and progress-document HEAD reconciliation.  
**Cost boundary:** ZERO COST; no deployment, no Cloudflare resource, no billing, no paid services, no Termux.

## Finding

Batch 38 introduced a pure lifecycle policy and wired browser online/visibility events into `CandlestickChart`. Its five tests proved the policy truth table, but did not mount the component to verify that React effect cleanup actually stops the supervisor and a later foreground/online transition creates a replacement.

## Change

Added `src/components/CandlestickChart.lifecycle.test.tsx` using jsdom, React DOM `act`, a mocked Lightweight Charts surface, and a mocked stream supervisor. The tests cover:
1. Initial online + visible mount creates one supervisor.
2. Offline event stops the current supervisor and makes the market-data snapshot unavailable with an offline reason.
3. Online event recreates the supervisor.
4. Hidden visibility stops the supervisor and marks backend data unavailable with a background reason.
5. Visible transition recreates the supervisor.
6. Component unmount stops the current supervisor.
7. Initially offline mount does not create a supervisor until online.
8. Initially hidden mount does not create a supervisor until visible.

No production code changes or dependency changes are included in Batch 39. The existing Batch 38 source behavior is being verified at the component boundary.

## Validation and acceptance boundary

- Exact-head CI completed on `b389070bea42e84e4efba7c778a2026c51ef5545`, a fixture-sharing follow-up descendant of the lifecycle test commit. Frontend: **225/225 tests passed across 28 files**. Backend: **1,032 passed in 52.01s**.
- Automated Tests [44324423988](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324423988): **FAILURE only at step 27**, the final npm audit enforcement. All functional/build/container/Redis/persistent-volume/Trivy steps before it passed. Android APK [44324423899](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324423899), CodeQL [44324424075](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324424075), and Full Git History Secret Audit [44324424084](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324424084) all **SUCCESS**.
- npm audit still reports five High findings through development-only `picomatch@4.0.7` (GHSA-fc5q-39xc-vjpf). CI includes a passing test that verifies this advisory-bearing package is dev-only. No patched version is listed by the advisory; no downgrade, override, patch, suppression, waiver, or audit weakening was applied.
- The test mocks chart rendering and WebSocket transport. It validates React lifecycle ownership, not browser-native WebSocket frames, Android WebView behavior, a deployed WSS Upgrade, platform close attribution, Fluid Compute read-back, or cross-instance fan-out.
- Gate 36 remains OPEN until external runtime evidence is captured.

## Prior Batch 38 exact-head evidence

Source commit: `90f2bea6dfc1e2834c5e9d2aed352c854b905c39`; following documentation-only HEAD correction: `09a81b455fb12b15515899d366bb9b2f1318fb54`.

- Automated Tests [44321645937](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645937): final failure only at frontend npm audit enforcement; 222 frontend and 1,032 backend tests passed, with frontend build, credential scans, backend audit, container build, Redis/persistent-volume smoke and Trivy report successful.
- Android APK [44321645986](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645986): SUCCESS.
- CodeQL [44321646301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321646301): SUCCESS.
- Full Git History Secret Audit [44321645942](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645942): SUCCESS.
- Five High npm findings remain through development-only `picomatch@4.0.7`. Advisory GHSA-fc5q-39xc-vjpf lists no patched version; forced downgrade of Vitest is not accepted.

## Progress and zero-cost accounting

- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10 remains **0/10 formally closed**; open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6 remain **NOT SCORED**.
- Overall current project percentage remains **NOT ESTABLISHED**; historical 20.9% is not a current calculation.
- No ticks or gate closures are awarded for a test-only batch.
- No Termux required. No deploy, Cloudflare resource, paid service, billing activation, production promotion, or `main` modification.
