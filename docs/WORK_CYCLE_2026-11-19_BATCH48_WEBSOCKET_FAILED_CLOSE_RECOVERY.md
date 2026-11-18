## Latest work cycle — Batch 48 (WebSocket failed-close recovery)

**Implementation commit:** `8eef475b2562506a0afd69f64c1ec19f860ec295`  
**Lifecycle-order correction commit / exact-head CI SHA:** `0b0e710e7e5f9565157e4051bae0619bb4c48123`  
**Parent:** `b458cc38fbf87fa9e738ee33f01af522d55e1b25`.

### 1. Defect found
A deeper failure-path audit found that transport `fail()` could set its local state to `closed` after `socket.close()` threw, but the supervisor still depended on the platform's native `close` event to receive `onClose` and schedule a reconnect. If the close request itself failed, that native event was not guaranteed. The UI could remain `reconnecting` without a retry timer.

### 2. Implementation
- Added an idempotent `notifyClose(code, reason)` guard so consumer close observers are invoked at most once, even if a synthetic failure notification is followed by a late native event.
- When `fail()` calls `socket.close(1011, ...)` and that call throws, transport now reaches its local `closed` state and sends a synthetic terminal `onClose(1011, "OHLCV stream failure")`. The supervisor can then schedule its bounded reconnect.
- When `socket.close()` succeeds, the transport preserves the existing native close-event ordering; it does **not** notify early. This is important because the supervisor must continue waiting for the actual close event on the normal path.
- The native close listener now sets transport state to `closed` before delivering the idempotent close notification.
- No wire protocol, backend, authentication, entitlement, replay cursor, sequence rules, heartbeat cadence, retry formula, hosting, or deployment configuration changed.

### 3. Regression tests and correction trail
- Transport regression: force `socket.close()` to throw during a protocol failure; verify terminal state, one synthetic 1011 close notification, and no duplicate notification when a late native close event arrives.
- Supervisor regression: force a transport error and then make the fake platform `socket.close()` throw; verify the supervisor schedules and opens a second connection after the deterministic 50 ms jittered delay.
- First CI attempt on `8eef475b...` correctly caught a behavior regression: the first implementation notified `onClose` even when `socket.close()` succeeded, violating the existing test that requires waiting for the native close event. Corrected in `0b0e710e...`: synthetic notification is now limited to the actual close-request-exception path. The corrected exact-head run is authoritative.

### 4. Exact-head CI evidence
Corrected source SHA: `0b0e710e7e5f9565157e4051bae0619bb4c48123`.

- Automated Tests [44419292784](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292784): **SUCCESS**.
- Frontend Vitest: **234 passed across 28 files**.
- Backend pytest: **1,032 passed in 40.49 seconds**.
- Frontend dependency audit: **PASS**. The previous `GHSA-fc5q-39xc-vjpf` advisory was withdrawn on 18 November 2026; the exact-head npm audit step now passes. No package downgrade, speculative override, suppression, lockfile manipulation, or threshold weakening was used. Upstream advisory record: [GitHub Advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf); maintainer discussion: [picomatch PR #235](https://github.com/micromatch/picomatch/pull/235).
- Frontend production build and source/bundle credential scans: PASS (77 source files and 5 bundle files scanned).
- Android preflight and immutable publisher tests: PASS.
- Backend dependency audit: PASS.
- Backend container build and shared Redis ACL + persistent-volume smoke: PASS. Smoke covered backend health, persisted Redis ACL authentication, AOF data across restart, fail-closed API outage behavior, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection.
- Trivy image scan/report: completed successfully; report artifact [14482290116](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292784/artifacts/14482290116). This is a CI image scan, not external production-host acceptance.
- Synthetic SQLite outbox benchmark artifact [14481880886](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292784/artifacts/14481880886): synthetic-only; it is not production market-data performance evidence.
- CodeQL [44419292719](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292719): SUCCESS.
- Full Git History Secret Audit [44419292875](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292875): SUCCESS.
- Android debug APK [44419292989](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292989): SUCCESS; artifact [14480328998](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292989/artifacts/14480328998). Preview release was skipped; no release was published.

### 5. Gate and progress disposition
- Gate 36 remains OPEN: public WSS roundtrip, Android WebView transport/lifecycle, effective host configuration, owner-observed 330-second session/close attribution, and cross-instance fan-out still require external acceptance evidence.
- Gate 10 remains **0/10** formally closed; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. No tick is awarded for this source/test/documentation batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST maintained. No deployment, paid service, or Termux use. `main` untouched.

