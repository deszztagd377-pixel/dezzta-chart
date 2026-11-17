# DEZZTA CHART — Isolated Vercel WebSocket POC

Status: **protected live HTTP health + synthetic WSS ping/pong observed; exact-HEAD CI SUCCESS; Gate 36 remains OPEN**  
Date: 2026-11-17  
Working branch: `phase-2/market-data-foundation`

## Purpose

Prove only the platform transport path for FastAPI ASGI over Vercel Fluid Compute. This is a disposable synthetic probe, not the DEZZTA CHART production backend.

The POC is isolated under `poc/vercel_ws/` so the existing Vite project, its root settings, routing and frontend deployment remain untouched. The separate Vercel project is configured with this directory as its Root Directory and SSO protection is enabled for all deployment targets. Its staging deployment is READY; live transport acceptance remains pending.

## Implemented

- FastAPI app at the recognized project-root entrypoint `index.py`.
- `GET /`: a small browser test panel with connect, ping and disconnect controls.
- `GET /health`: no-store synthetic-only health response.
- `WS /ws`: ready message, bounded JSON ping/pong, monotonic sequence, session ID, message-size cap, message-rate cap, idle timeout and graceful disconnect.
- No production credentials, Firebase, Redis, market data, SQLite, outbox, provider adapter, or notification worker.
- Python 3.12 selected by `.python-version`.
- Automated tests cover health, no-store headers, browser panel, WebSocket handshake, ordered ping/pong, invalid payload, oversize payload, rate limiting and idle close.

## Security boundary

The POC relies on **Vercel deployment SSO protection** at the edge. The separate project must be configured with SSO scope `all` before any deployment is created. Do not create a protection-bypass URL. Do not add a custom domain. If SSO cannot be enforced on the Hobby project, do not deploy this endpoint publicly.

The endpoint accepts only synthetic ping messages and sends synthetic pong responses. It must not be connected to real account or market-data traffic.

## Acceptance checklist

| Check | Required evidence | State |
|---|---|---|
| Repository unit tests | Automated Tests & Build run `44062060115` | **SUCCESS** |
| Separate Vercel project | Dedicated FastAPI project; build log confirms `poc/vercel_ws` source | **READY** |
| Deployment protection | SSO enabled for all deployment targets; no custom domain | **VERIFIED** |
| Fluid Compute | Update request set `true`; project read-back omits field | **NOT INDEPENDENTLY VERIFIED** |
| HTTP health | Protected real request to `/health` | **PASS — owner-device event http_health, status 200, ok=true, expected synthetic-only payload** |
| WebSocket upgrade | Browser panel receives `ready`, then ordered `pong` responses | **PASS — owner-device ready followed by pong, browser-1, sequence 1, matching session ID** |
| Disconnect/reconnect | Owner performs manual disconnect then reconnect; new session ID and fresh-session ping/pong | **PASS — owner explicitly confirmed pressing Disconnect then Connect between two distinct ready/pong sessions; second session used a new ID and restarted at sequence 1. The browser log omitted an explicit Closed (1000) event, so the action is owner-confirmed rather than visible in the event trace** |
| Idle/lifetime behavior | Idle close and Vercel maximum-duration close are observed | **PARTIAL — owner-device idle_timeout observed; Vercel maximum-duration close not tested** |
| Cross-instance behavior | Separate sessions do not rely on process-local shared state; this POC intentionally has none | Pending |
| Cost | Project remains Hobby and usage stays within no-billing allowance | Pending |

## Explicit limitations

A passing TestClient suite proves the ASGI app behavior locally in CI; it does not prove the deployed Vercel WebSocket upgrade, SSO interaction, maximum connection lifetime, or Android client behavior. Those remain external acceptance tests.

The POC deliberately does not solve cross-instance market-data fan-out. Production requires a separate zero-cost durable/shared messaging and storage design satisfying TLS, ACL, private access, backup and recovery gates. No paid service may be introduced to make this POC pass.

## Stage 1 accounting

This POC adds testable repository evidence for Gate 36 but does not close Gate 36 or award any Stage 1 ticks. Stage 1 remains 300/400 = 75% provisional; Gate 10 remains 0/10 formally closed until external acceptance evidence is recorded.


## Latest deployed evidence — 2026-11-17

- First explicitly targeted staging deployment: `dpl_EJgJNiLxZxupJYSGo4M2SH14oYTF` — **READY**.
- Latest branch preview from commit `ce079f8402a08b2d3bcdf64c3c80f41b8230fffd`: `dpl_Ns63oEgDLBVYaSBrjcFefiNGXKY3` — **READY**.
- Both deployments belong to `dezzta-chart-ws-poc`; SSO is enabled for all deployment targets. No custom domain or bypass share URL was created.
- Build logs confirm Python 3.12 and requirements loaded from `poc/vercel_ws/`.
- Fluid Compute was explicitly requested in project settings, but the available read-back omits that flag. It remains **not independently verified**.
- Runtime logs returned no records for the latest POC deployment during the last 50-minute window. No protected HTTP or WebSocket test request has yet been observed.
- Main Vite preview from the same code commit is READY (`dpl_3NqxWPshEa9cNVKjmFiYtrs23gjJ`).

The first create-deployment request inherited the production target and was canceled before completion; it is not the accepted deployment. The actual staging deployment and latest preview are protected by SSO.

### CI evidence

On source commit `ce079f8402a08b2d3bcdf64c3c80f41b8230fffd`:
- Automated Tests & Build: SUCCESS (`44063590646`).
- CodeQL: SUCCESS (`44063590667`).
- Full Git History Secret Audit: SUCCESS (`44063590758`).
- Android debug APK build: SUCCESS (`44063590583`).

Gate 36 remains OPEN until a protected HTTP health request, WebSocket upgrade, ordered ping/pong, disconnect/reconnect and connection-lifetime test are observed.


## Follow-up probe-panel correction and latest exact-head evidence — 2026-11-17

Commit f372e3ff6fb68e9747bc6b4069be120e7a5213f1 corrects the browser panel's log separator so each ready/pong/error event is displayed on a separate line. A regression assertion in backend/tests/test_vercel_ws_poc.py protects the expected JavaScript newline literal.

Exact-HEAD verification:
- Automated Tests & Build run [44070243153](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44070243153): **SUCCESS**; 211 frontend tests and 993 backend tests passed. Frontend build/secret scan, backend dependency audit, synthetic outbox benchmark, backend container build, Redis shared-guard + persistent-volume smoke test, and image scan/report upload all passed.
- CodeQL [44070243169](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44070243169): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44070243157](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44070243157): **SUCCESS**.
- Trivy image scan filtered to HIGH/CRITICAL reported zero findings for the Alpine OS image and every listed Python package target.
- Dedicated Vercel POC preview dpl_GXoAVpfXF7raiWJCVZrmf4PyPLmw from this exact commit: **READY**, region iad1; SSO protection remains enabled for all deployment targets. No bypass/share URL or custom domain was added.
- A 30-minute runtime-log query returned no records. This is not a failed connection test; it means no request was observed in that query window. Protected HTTP/WSS, ping/pong, disconnect/reconnect, lifetime and Android browser acceptance remain pending.

The Android owner reports that the debug APK installed and launched on the Infinix device. This confirms package installation and app startup only. It does not verify screen rendering, backend connectivity, Firebase identity, market data, or end-to-end security. The APK binary remains built from app-code commit ce079f8402a08b2d3bcdf64c3c80f41b8230fffd; the later f372e3f change touches only the isolated POC and its test, not the Android app.

Gate 36 remains OPEN. Stage 1 remains 300/400 = 75% provisional; Gate 10 remains 0/10 formally closed. No ticks are awarded for CI, preview readiness, or installation alone.


## Explicit Fluid Compute configuration — 2026-11-17

The dedicated project Root Directory is `poc/vercel_ws`. This directory now contains a version-controlled `vercel.json` with `"fluid": true`, so the WebSocket POC explicitly requests Fluid Compute at the deployment level rather than relying only on an earlier dashboard/API setting. A regression test parses this file and asserts the setting is true. Vercel documents the `fluid` property for per-deployment configuration and supports Python runtime; see [Fluid Compute configuration](https://vercel.com/docs/fluid-compute) and [Vercel project configuration](https://vercel.com/docs/project-configuration/vercel-json).

This removes ambiguity in the repository configuration, but it is not proof that a live WebSocket handshake works. The next exact-commit deployment must be READY, then the protected HTTP health request and WSS connect/ready/ping/pong/disconnect/reconnect/lifetime checks must still be observed. Keep SSO enabled for all deployment targets and do not create a bypass URL.


## Latest exact-HEAD verification — 2026-11-17

- Source commit: `ad2abeba3f6372eee97e23dc1fd738e9d2578fd0` on `phase-2/market-data-foundation`.
- Automated Tests & Build [44071698421](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44071698421): **SUCCESS**, including frontend/backend tests, frontend build and secret scans, backend benchmark, container build, Redis/persistent-volume smoke test, image scan and report export/upload.
- CodeQL [44071698260](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44071698260): **SUCCESS**. Full Git History Secret Audit [44071698322](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44071698322): **SUCCESS**.
- Latest deployment `dpl_7xdoEjEo1sWdeusHTse8Zp3rzDnD`: **READY**, exact source SHA above; URL: https://dezzta-chart-ws-9wlnhsgf4-deszztagd377-pixel.vercel.app.
- SSO remains enabled. No public bypass/share URL or custom domain was created. Vercel dashboard access does not itself prove the preview is authorized for the owner account.
- The explicit `fluid: true` source config is regression-tested. Runtime Fluid setting is not independently read back.
- Still pending: authenticated HTTP health request, WebSocket ready/ping/pong, manual disconnect/reconnect, maximum connection lifetime, browser/Android acceptance, and production cross-instance fan-out. Gate 36 stays OPEN until these are observed.


## Owner-device browser smoke test — 2026-11-17

The project owner opened the SSO-protected preview in a browser and reported the following visible result:

- Browser panel showed **Connected**.
- Server handshake event: `type=ready`, `mode=synthetic-only`, session ID `bcb292945f444cf79f593fa65027ce56`.
- Browser sent synthetic ping with ID `browser-1`; server returned `type=pong`, `sequence=1`, matching session ID.
- This is owner-reported browser evidence of a successful authenticated WebSocket connect and one bidirectional ping/pong exchange. It is not a server-side independent trace and does not validate production market-data traffic.
- Still pending: authenticated `/health` result, manual disconnect followed by a fresh reconnect/session, short-lived connection close behavior and lifetime measurement, repeatability, and cross-instance production fan-out.
- Gate 36 remains OPEN; no Stage 1 ticks or formal gate closure are awarded from this single smoke test.


## Owner-device reconnect and idle-timeout evidence — 2026-11-17

The owner repeated the browser test after the first successful connect/ping exchange and reported:

- The prior connection was displayed as `Closed (1000)`, consistent with the manual disconnect completing with a normal WebSocket close code.
- A subsequent connection produced a new `ready` event with session ID `47f6768472b44268a51cb8caec4f65a5`, distinct from the first session ID `bcb292945f444cf79f593fa65027ce56`.
- The new session later emitted `type=idle_timeout` for that same session ID, and the panel returned to a closed state.
- This is owner-reported evidence that a fresh session was created after disconnect and that the server's idle-timeout close path was observed. The owner did not report sending a ping on this second session, so a second-session pong and sequence reset are **not** claimed.
- The exact preview deployment used for this second test was not identified in the report. The latest documentation commit's dedicated preview is separately confirmed READY.

Gate 36 remains OPEN. Remaining acceptance includes a protected `/health` response, ping/pong on the fresh session, a measured maximum-duration/lifetime close, repeatability, Android-native client behavior, independent Fluid Compute runtime confirmation, and production cross-instance fan-out. No Stage 1 ticks are awarded.


## Browser probe repeat-session improvement — 2026-11-17

The browser panel now sends one bounded synthetic ping automatically whenever it receives a new ready message. It resets the browser ping counter for each fresh session, so the first automatic ping on every session uses browser-1; the server response should be pong with sequence 1 and the same session ID. The manual ping button remains available for additional ordered exchanges.

Regression coverage now verifies that two separate TestClient WebSocket sessions receive distinct session IDs and each starts the server-side pong sequence at 1. A browser-panel assertion protects the automatic fresh-session ping behavior.

This is a testability improvement and repository-level regression coverage. It is not owner-device evidence of a deployed second-session pong, maximum Vercel connection duration, /health, Android-native WSS, or cross-instance fan-out. Gate 36 remains OPEN; no Stage 1 ticks are awarded.


## Protected HTTP health probe in the browser panel — 2026-11-17

The browser panel now requests the same-origin /health endpoint with no-store caching and same-origin credentials when the page loads. It writes the HTTP status, success flag and returned JSON into the existing event log. Because the panel itself is behind deployment SSO, the health request reuses the already-authorized browser session; no bypass secret or public route is introduced. A sanitized error event is logged if the request fails.

A regression assertion checks that the panel retains this health probe. This is still only test-harness implementation: it does not prove a live health response until the owner opens the latest protected deployment and the event log shows http_health with HTTP 200 and the expected synthetic-only payload. Gate 36 remains OPEN and no ticks are awarded.


## Owner-device protected HTTP + fresh WebSocket round-trip — 2026-11-17

The owner opened the latest protected preview and supplied this event sequence:

- http_health: HTTP **200**, ok=true, payload status=ok, service=dezzta-ws-poc, mode=synthetic-only, production_data_connected=false.
- ready: WebSocket session ID d576d71e45684042adcca47624a86c4b, mode synthetic-only.
- pong: ID browser-1, sequence **1**, with the same session ID as ready.
- idle_timeout: emitted for that same session ID; expected short-lived idle closure.

This owner-device evidence now verifies the protected same-origin HTTP health request and a deployed browser WebSocket handshake plus successful automatic synthetic ping/pong round trip on the same session. It also confirms the configured idle-timeout path. The payload explicitly reports that production data is not connected.

Exact-head CI for the latest source commit 07530d74c43b98de7b9a3f44b1c05eec5db9987e:
- Automated Tests & Build [44076533920](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44076533920): **SUCCESS**; frontend/backend tests, audits, container build, Redis/persistent-volume smoke test and image scan/report steps completed.
- CodeQL [44076533946](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44076533946): **SUCCESS**.
- Full Git History Secret Audit [44076533891](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44076533891): **SUCCESS**.

Remaining Gate 36 acceptance: capture a single explicit manual close-to-reconnect trace with a fresh session and first pong, observe the Vercel maximum-duration close, independently read back the Fluid Compute runtime setting, test the native Android client, and validate production cross-instance fan-out. This POC remains synthetic-only; it does not prove production data delivery or fan-out. Gate 36 stays OPEN, no Stage 1 ticks are awarded, and Gate 10 remains 0/10 formally closed.


## Owner-confirmed manual disconnect → reconnect with fresh-session pong — 2026-11-17

After the earlier two-session event log, the owner explicitly confirmed that they pressed **Disconnect** and then **Connect** between the two sessions. The supplied browser log contains:

- First session: `ready` and `pong`, session ID `cc666ac1083f422e8ed11ef5be19b5a2`, first pong sequence 1.
- After the owner-confirmed manual Disconnect → Connect action, second session: `ready` and `pong`, new session ID `b6bad24977f94799bfd4f573a884b0ac`, first pong sequence 1.
- The second session subsequently emitted `idle_timeout` for its own session ID.
- The explicit `Closed (1000)` event is not present in this particular combined log. The manual action is confirmed by the owner, while the new ready/session ID and fresh-session pong are visible in the log.

This closes the browser-panel manual reconnect + fresh-session ping/pong sub-check as **owner-confirmed**. It does not close Gate 36. Still pending: observed Vercel maximum-duration close, independent Fluid Compute runtime read-back, native Android WSS behavior, production cross-instance fan-out, and remaining cost/operational acceptance. The POC remains synthetic-only and is not connected to production market data. No Stage 1 ticks are awarded by this evidence alone; Gate 36 remains OPEN and Gate 10 remains 0/10 formally closed.
