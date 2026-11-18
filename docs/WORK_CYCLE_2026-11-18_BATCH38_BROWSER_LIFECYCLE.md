# Work Cycle — Batch 38: Browser Network and Visibility Lifecycle

**Date:** 18 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent exact HEAD:** `0f9c5a1d291d2d601fd63a8bc2c36b95c9ae8d14`  
**Candidate source commit:** `90f2bea6dfc1e2834c5e9d2aed352c854b905c39`  
**Scope:** WebSocket lifecycle hardening, deterministic policy tests, Gate 36 evidence update.  
**Cost/device boundary:** ZERO COST; no deploy, no Cloudflare resource, no billing change, no Termux.

## 1. Finding

The chart component started an authenticated OHLCV supervisor whenever a contract was selected and the chart became ready. It did not gate that supervisor on `navigator.onLine` or `document.visibilityState`. On mobile browsers, background timer throttling and loss of network connectivity can leave an unnecessary reconnect loop running or make heartbeat behavior unreliable.

## 2. Correction

- Add a pure browser lifecycle policy: the stream may connect only when the browser reports online **and** the document is visible.
- Subscribe to `online`, `offline`, and `visibilitychange` events; remove all listeners on component cleanup.
- On offline/background transition, stop the old supervisor through the existing effect cleanup, switch the displayed series to demo-only data, clear revision cursors, and publish an unavailable snapshot with a specific pause reason.
- On return to online + visible, create a new supervisor. Existing supervisor behavior obtains a fresh Firebase ID token and a new atomic snapshot/watermark before accepting live updates.
- Add five deterministic tests for active, offline, hidden, combined constraints, and prerender/non-visible document states.

## 3. Lifecycle matrix and resource calculation

| Network | Document | Stream | Expected action |
|---|---|---|---|
| Online | Visible | Active | One supervisor may connect |
| Offline | Visible | Paused | Stop supervisor; no offline retry loop |
| Online | Hidden | Paused | Stop supervisor before background timer throttling |
| Offline | Hidden | Paused | Stop supervisor; offline reason takes precedence |
| Online | Visible after resume | Recreated | Fresh token + fresh snapshot/watermark |

The lifecycle policy has two independent boolean preconditions. Only 1 of the 4 online/visible combinations permits a live supervisor. Event listeners are three total and are all removed on unmount. No polling timer or extra network request is added while paused.

## 4. Exact-head CI outcome

Candidate SHA `90f2bea6dfc1e2834c5e9d2aed352c854b905c39` was validated by:

- Automated Tests [44321645937](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645937): final job **FAILURE only at step 27** (`Enforce frontend dependency audit result`). Frontend Vitest **222/222 across 27 files**, backend pytest **1,032 passed in 31.26s**, frontend production build, frontend source/bundle secret scans, Android preflight and publisher tests, synthetic outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke, Trivy scan/report all passed.
- Android debug APK [44321645986](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645986): **SUCCESS**; checksum verification and temporary CI artifact upload passed. Preview publication was skipped.
- CodeQL [44321646301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321646301): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44321645942](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645942): **SUCCESS**.
- The remaining npm audit failure reports five High transitive findings via `picomatch@4.0.7`; npm's proposed forced Vitest downgrade is breaking and was rejected. Keep enforcement fail-closed.
- Trivy report: 0 vulnerabilities for Alpine 3.24.4 and the listed Python package targets. Initial mirror blob retrieval failed; fallback GHCR download succeeded and artifact `14434973310` was uploaded.

## 5. Validation boundary

- The new pure policy tests are part of the frontend Vitest suite.
- The existing WebSocket client/protocol/supervisor tests remain unchanged and continue to cover reconnect, cursor replay, sequence gaps, terminal close policy, heartbeat, and explicit stop.
- Exact-head CI must validate the new source commit before this batch is called green.
- This does not prove Android WebView lifecycle behavior, a deployed WSS Upgrade, 330-second platform close attribution, Fluid Compute read-back, or cross-instance fan-out.

## 6. Batch 37 exact-head CI reconciliation

For parent Batch 37 SHA `0f9c5a1d291d2d601fd63a8bc2c36b95c9ae8d14`:

- Automated Tests [44319494393](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494393): **FAILURE only at final frontend npm audit enforcement**. Frontend tests/build, backend tests, backend dependency audit, container build, Redis/persistent-volume smoke, and Trivy report passed. Five High findings remain via development-only `picomatch@4.0.7`.
- Android debug APK [44319494274](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494274): **SUCCESS**.
- CodeQL [44319494237](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494237): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44319494266](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494266): **SUCCESS**.
- The container Trivy report records zero vulnerabilities for the Alpine OS and Python package targets scanned. Trivy's first database mirror returned a missing-blob error; fallback GHCR retrieval succeeded and the JSON report artifact was uploaded.
- The frontend audit blocker is not suppressed or weakened. npm's proposed forced downgrade is not applied.

## 7. Gate 10 reconciliation

- Gate 36 source lifecycle handling is improved by this batch, but the gate remains **OPEN** until deployed browser/Android WebView and host acceptance evidence exists.
- Gate 8, 20, 25, 30, 31, 34, 35, 38, and 39 remain externally unaccepted under the current evidence ledger.
- No gate closure or Stage 1 tick is awarded for this source/test/documentation change alone.

## 8. Progress and zero-cost disposition

- Stage 1: **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10: **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** until M1–M8 weights and criterion mapping are approved.
- No Termux required. No Vercel deployment, Cloudflare resource, paid service, billing activation, production promotion, or publication action.
