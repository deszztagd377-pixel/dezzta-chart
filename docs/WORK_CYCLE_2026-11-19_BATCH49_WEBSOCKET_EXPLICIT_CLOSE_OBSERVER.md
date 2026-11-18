# Batch 49 — Explicit WebSocket close observer fallback

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source SHA:** `a8589e816b349d72db3d9093fd4b71eb01288813`  
**Parent:** `33f988dddb2cb55291299d63884d069648555b6a`

## Scope
Close the remaining transport lifecycle notification gap in the public `connection.close()` method. No backend protocol or production deployment changes.

## Defect
The explicit close method previously swallowed an exception from `socket.close()` and set local state to `closed`, but did not call `onClose`. That could leave a consumer waiting for a native close event that might never arrive. The method also did not synthesize a callback if the socket was already in CLOSED state before the native close event was delivered.

## Fix
- Track whether the platform close request throws.
- Always set local state to `closed`.
- On close-request failure or an already-CLOSED socket, invoke the existing idempotent close notifier once with abnormal-close code `1006` and a sanitized reason.
- If a close request succeeds and the socket is still CLOSING, preserve native close-event ordering.
- If a native event arrives after a synthetic notification, the notifier guard suppresses duplicate callback delivery.

## Regression test
A new test replaces the fake socket's `close()` with a throwing implementation, invokes explicit `connection.close()`, and verifies:
1. no exception escapes;
2. connection state becomes `closed`;
3. `onClose` is called once with code `1006` and reason `Client close request failed`.

## Validation — exact source SHA
Automated Tests: [44421919543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919543).

At documentation time:
- Frontend dependency audit: PASS.
- Frontend unit tests: PASS (exact count pending completed job log).
- Frontend production build and source/bundle credential scans: PASS.
- Android preflight/publisher tests: PASS.
- Backend pytest: PASS (exact count pending completed job log).
- Backend dependency audit: PASS.
- Backend container build: IN PROGRESS.
- Android APK: [44421919500](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919500) SUCCESS.
- CodeQL: [44421919553](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919553) SUCCESS.
- Git-history secret audit: [44421919501](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919501) SUCCESS.
- Redis/persistent-volume smoke, Trivy, and overall CI conclusion: not yet confirmed.

## Gate disposition
- Gate 36 remains OPEN pending real public WSS, Android WebView, 330-second owner-observed session, effective host configuration and cross-instance fan-out evidence.
- Gate 10 remains 0/10 formally closed. Open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 1 remains 75% provisional (300/400 ticks; 30/40 criteria). No progress tick is awarded for this code/test/doc batch.
- Stages 2–6 unscored; overall project percentage not established.
- ZERO COST; no deployment; no Termux; `main` untouched.
