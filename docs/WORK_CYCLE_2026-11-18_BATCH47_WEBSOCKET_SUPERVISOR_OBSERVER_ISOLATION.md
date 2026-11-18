# Batch 47 — WebSocket supervisor observer isolation

- **Repository:** `deszztagd377-pixel/dezzta-chart`
- **Branch:** `phase-2/market-data-foundation`
- **Implementation commit:** `bec43c87a2b8022c2cd8bf83e1aad884158ab271`
- **Test timing correction:** `6b82a3dd4ac20d0b6ee4e1b2b43b7f211de7f4dc`
- **ZERO COST:** yes; no deployment, paid service, or Termux action.

## 1. Defect

A source-level review after Batch 46 found the supervisor still invoked consumer callbacks without isolation:

- `onStatus` runs during reconnect scheduling. If it throws, execution can stop before `reconnectTimer` is created; a transient network failure can therefore stall instead of retrying.
- `onError` is called for empty identity tokens, transport errors, connection setup failures, and terminal policy/auth/entitlement errors. If it throws, the supervisor's own recovery/error path can be interrupted.

## 2. Correction

- `setStatus()` writes `currentStatus` first, then invokes `onStatus` inside a guarded best-effort block.
- A dedicated `reportError()` invokes the consumer error observer inside a guarded best-effort block.
- All supervisor-level error notifications now use `reportError()`.
- The underlying transport still owns socket cleanup and protocol failure behavior. The supervisor remains responsible for bounded reconnect scheduling and fresh-token acquisition.

## 3. Regression test and correction trail

New test: `continues reconnecting when supervisor status and error observers throw`.

The test:
1. Establishes a valid snapshot/subscribed stream.
2. Configures both consumer observers to throw.
3. Triggers a transport error.
4. Confirms no exception escapes and supervisor status becomes `reconnecting`.
5. Advances the deterministic retry clock and confirms a second socket is opened.

The first test draft used 99 ms as the pre-retry observation window. With `minReconnectDelayMs=100` and deterministic `random()=0`, the production jitter formula gives `100 × 0.5 = 50 ms`. CI correctly caught the test's incorrect expectation. The corrected assertion waits 49 ms (no second socket), then 1 ms (second socket opens). This timing correction was committed separately and the corrected SHA is the authoritative validation target.

## 4. Exact-head CI

Corrected source SHA: `6b82a3dd4ac20d0b6ee4e1b2b43b7f211de7f4dc`.

- Automated Tests: [44336190424](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190424) — **FAILURE only at final npm audit enforcement**. Frontend 232/232; backend 1,032/1,032; frontend build, credential scans, backend dependency audit, container build, Redis/persistent-volume smoke, and Trivy (0 vulnerabilities) passed.
- Git-history Secret Audit: [44336190330](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190330) — SUCCESS.
- CodeQL: [44336190195](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190195) — SUCCESS for JavaScript/TypeScript and Python.
- Android APK: [44336190344](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190344) — SUCCESS; artifact [14441103214](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190344/artifacts/14441103214).
- Batch 46's exact-head result [44334598973](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973): 231 frontend and 1,032 backend tests passed; sole failure was five High picomatch advisory findings at final npm audit enforcement. Batch 47 changes no frontend dependencies.

## 5. Gate/progress disposition

- Gate 36 remains OPEN pending public WSS, Android WebView, host effective config, owner-observed long-session/close attribution, and cross-instance fan-out acceptance.
- Gate 10 remains 0/10 formally closed; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain open.
- Stage 1 remains 75% provisional (300/400 ticks; 30/40 criteria). No tick for this source/test/docs batch.
- Stages 2–6 NOT SCORED; overall project percentage NOT ESTABLISHED until M1–M8 weighting/mapping is approved.
- No production deployment, no paid services, no Termux, and `main` untouched.
