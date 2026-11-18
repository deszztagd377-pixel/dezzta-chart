# Batch 50 — WebSocket failure notification when socket is already CLOSED

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source SHA:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`  
**Parent:** `a483d6627a1d406aa93feced856392fa4792369b`

## Scope
Close the remaining terminal-state notification edge in the WebSocket transport. This batch does not change the backend wire protocol, authentication, entitlement checks, retry policy, heartbeat interval, or hosting configuration.

## Defect
The transport's failure path already synthesized a close notification when the platform's `socket.close()` call threw. One adjacent case remained: the socket could report `readyState === CLOSED` before its native `close` event was delivered. In that interval, the supervisor could otherwise remain waiting for the callback.

## Implementation
- The failure path now notifies the supervisor if either the close request throws or the socket is already CLOSED.
- The existing idempotent notifier ensures a late native close event cannot invoke `onClose` twice.
- Normal browser ordering is preserved: a socket whose close event is intentionally deferred remains in CLOSING state until that event is delivered.
- The supervisor fake socket was corrected to model that browser lifecycle accurately. A deferred close no longer marks the fake CLOSED prematurely.

## Regression coverage
- Transport test forces `readyState = 3`, injects a protocol failure, and verifies one synthetic `onClose(1011, "OHLCV stream ended before close event")`.
- It then delivers a late native close event and verifies the observer count remains one.
- Existing regression still verifies a throwing `socket.close()` results in one synthetic close notification.
- Existing supervisor test verifies no replacement socket is opened while the previous socket remains CLOSING.

## CI correction trail
The first attempt, [44422763320](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422763320), failed because the inserted test had a syntax error and the fake socket did not model CLOSING correctly when a close event was deferred. Both were corrected in source/test commit `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`.

## Exact-head validation
[Automated Tests 44422985332](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332): **SUCCESS**, no failed steps.

- Frontend Vitest: **234 passed across 28 files**.
- Backend pytest: **1,032 passed in 30.94 seconds**.
- Frontend npm audit: **PASS — 0 vulnerabilities**.
- Frontend production build and 77-file source/bundle credential scans: PASS.
- Android preflight and immutable publisher tests: PASS.
- Backend dependency audit and backend container build: PASS.
- Shared Redis ACL + persistent-volume smoke: PASS.
- Trivy image scan/report: PASS; artifact [14482732766](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332/artifacts/14482732766).
- Synthetic SQLite outbox benchmark artifact [14482428443](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332/artifacts/14482428443) is synthetic-only and is not production market-data performance evidence.
- Android APK [44422985353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985353): SUCCESS; artifact [14482822189](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985353/artifacts/14482822189). No preview release published.
- CodeQL [44422985334](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985334): SUCCESS.
- Full Git History Secret Audit [44422985415](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985415): SUCCESS.

## Gate and progress disposition
- Gate 36 remains OPEN pending public WSS roundtrip, Android WebView transport/lifecycle, effective host configuration, owner-observed 330-second session/close attribution, and cross-instance fan-out.
- Gate 10 remains **0/10** formally closed. Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional (300/400 ticks; 30/40 criteria)**. No tick is awarded for this code/test/documentation batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST. No deployment. No Termux. `main` untouched.
