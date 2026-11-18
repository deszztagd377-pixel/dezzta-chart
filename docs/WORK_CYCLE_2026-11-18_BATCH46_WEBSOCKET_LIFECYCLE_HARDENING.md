# Batch 46 — WebSocket lifecycle observer and socket failure hardening

- **Repository:** `deszztagd377-pixel/dezzta-chart`
- **Branch:** `phase-2/market-data-foundation`
- **Implementation commit:** `4f746496b23cc9208804023bbb554a4e07c6480b`
- **Parent:** `8fecf72ece008455c82221ffbabd59ea0b945cfd`
- **ZERO COST:** yes; no deployment, paid service, or Termux action.

## 1. Defect analysis

Batch 45 hardened the terminal `fail(error)` path against a throwing `onError` callback. A source re-audit found additional lifecycle observers and native socket calls with equivalent exception paths:

1. `onStatus` could throw during a state transition and interrupt the current WebSocket event handler.
2. `onClose` could throw before the close handler completed its terminal state transition.
3. The initial authentication `socket.send()` ran outside a guarded block; a synchronous platform exception could escape the `open` event callback and leave the connection waiting for its handshake timeout.
4. Explicit `connection.close()` could fail before the local state was marked closed if the platform rejected `socket.close()`.

## 2. Implemented correction

- `setState` updates local state first, then calls `onStatus` inside a best-effort guard.
- The `open` handler catches synchronous authentication-send failures and routes them through the controlled terminal `fail()` path.
- The `close` event isolates `onClose`; observer failure cannot block the local closed-state transition.
- Explicit `close()` catches a platform close exception and still sets local state to `closed`.
- Existing `onError` isolation remains.
- Snapshot/update/cursor observer failures continue to fail the stream closed; the client does not silently discard a market-data update and continue as if it were delivered.

## 3. Regression coverage

Three new tests were added to `src/services/ohlcvWebSocketClient.test.ts`:

- Throwing `onStatus` observer does not interrupt authentication/subscription progression.
- Authentication `socket.send()` exception becomes a reported terminal transport failure, with a 1011 close request.
- Throwing `onClose` observer and throwing platform `socket.close()` do not escape explicit shutdown; connection state ends as `closed`.

## 4. Exact-head CI evidence

Source SHA `4f746496b23cc9208804023bbb554a4e07c6480b`:

| Check | Result |
|---|---:|
| Frontend Vitest | 231 passed / 28 files |
| Backend pytest | 1,032 passed / 30.78 s |
| Frontend production build | PASS |
| Frontend source/bundle secret scan | PASS — 77 source files |
| Backend dependency audit | PASS |
| Backend container build | PASS |
| Shared Redis guard + persistent-volume smoke | PASS |
| Trivy container report | 0 vulnerabilities |
| Android debug APK | PASS |
| CodeQL JS/TS + Python | PASS |
| Full Git-history secret audit | PASS |
| Final frontend npm audit enforcement | FAIL — five High picomatch findings |

- Automated Tests: [44334598973](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973)
- Android APK: [44334599093](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334599093), artifact [14441570921](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334599093/artifacts/14441570921)
- CodeQL: [44334598939](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598939)
- Full Git-history secret audit: [44334598934](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598934)
- Trivy report artifact: [14439909868](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973/artifacts/14439909868)
- Synthetic outbox benchmark artifact: [14440682369](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973/artifacts/14440682369). Synthetic-only; not production market-data performance evidence.

### Dependency audit blocker

The only failed CI step is `npm audit --audit-level=high`: five High findings for `GHSA-fc5q-39xc-vjpf` in `picomatch`, reached through Vite/fdir and Vitest/tinyglobby. npm recommends `npm audit fix --force`, but the log explicitly says this would install `vitest@3.1.4` as a breaking change. No downgrade, speculative override, advisory suppression, lockfile manipulation, or audit-threshold weakening was applied. Keep the audit fail-closed until a compatible upstream fix is published.

## 5. Scope and gate disposition

No wire protocol, server route, heartbeat interval, replay cursor, sequence semantics, identity verification, entitlement, retry policy, host configuration, or production deployment changed.

- Gate 36 remains OPEN: public WSS roundtrip, Android WebView transport/lifecycle, effective host configuration, owner-observed 330-second session and close attribution, and cross-instance fan-out remain external acceptance requirements.
- Gate 10 remains 0/10 formally closed. Open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 1 remains 75% provisional (300/400 ticks; 30/40 criteria); this batch earns no tick.
- Stages 2–6 remain NOT SCORED; overall percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- `main` untouched. No deployment or Termux required.
