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


## Latest Vercel deployment and build-context read-back — 2026-11-17

- Vercel team plan: **Hobby**.
- Project: `dezzta-chart-ws-poc`; project ID `prj_yVSD5vtqiPxpSYBGE6hxXDRCIWs2`.
- Latest deployment observed: `dpl_39dRJ6Ki9gU1PrXcN8YU4kQ7zCzW`; state **READY**; source commit `b789e229290290c91143077449a83ec94098162f`; branch `phase-2/market-data-foundation`.
- Project protection read-back: SSO **enabled for all deployment targets**.
- Build log: **Python 3.12 from `poc/vercel_ws/.python-version`**; dependencies installed from **`poc/vercel_ws/requirements.txt`**. This is direct build-log evidence that the intended POC subdirectory was used.
- The project settings response does not expose `resourceConfig.fluid`. The source `vercel.json` requests `fluid: true`, but effective Fluid Compute remains **NOT INDEPENDENTLY VERIFIED**.
- Runtime-log query for the latest deployment over 50 minutes returned no records. No logs in that window are not evidence of connection failure.
- Gate 36 remains OPEN; no Stage 1 ticks are awarded.


## Latest exact-head preview status — Batch 6 — 2026-11-17

- Source commit: `cfc56b7ba050201823952ea1b67dd38182dc9bfb`.
- The Vercel FastAPI WSS POC preview status context completed **SUCCESS**.
- The main Vite frontend preview status context returned **FAILURE: Vercel build-rate limit**. This was a platform deployment-rate restriction, not a source test failure. No paid plan upgrade, deployment bypass, or retry loop was attempted.
- The POC preview status is not a production WSS acceptance test. Maximum-duration behavior, effective Fluid Compute read-back, Android Capacitor WebView WSS against the authenticated production backend, cross-instance fan-out, and cost acceptance remain open.


## Batch 7 — Hobby function lifetime and bounded maximum-duration test plan — 2026-11-18

- The current dedicated FastAPI POC and main Vite deployments were independently read back as **READY**. The POC remains protected by SSO for all deployment targets; both projects remain preview-only (`live=false`).
- Vercel's published Fluid Compute limits specify Hobby default and maximum Function duration as **300 seconds (5 minutes)**. WebSocket sessions close when their Function invocation reaches its configured maximum duration. This is expected platform lifecycle behavior, not a transport failure.
- Current POC idle timeout is **25 seconds**. A passive browser connection therefore closes from the POC's own idle policy long before the platform's 300-second ceiling. A platform lifetime test must send synthetic heartbeat pings at intervals shorter than 25 seconds and capture elapsed time plus the close event.
- A temporary POC-only `maxDuration` cap (suggested 60 seconds) is a bounded test option; it has **not** been configured or deployed. It would prove the platform-enforced close mechanism at the temporary cap, not prove the full 300-second Hobby ceiling.
- Do not use production market data, production credentials, a public bypass URL, or a custom domain for this test. Keep SSO enabled. Do not trigger a 300-second observation until Hobby usage allowance and zero-billing constraints are confirmed.
- Production clients must reconnect with bounded backoff, reauthenticate/recheck entitlement, resume from a durable cursor, deduplicate replay/live overlap, and resnapshot on replay gaps. Function memory cannot be the durable cross-instance state layer.
- Gate 36 remains OPEN. No platform max-duration close or independent effective Fluid Compute setting read-back is claimed. Android WebView WSS and production cross-instance fan-out remain open.
- Supporting report: [Batch 7](WORK_CYCLE_2026-11-18_GATE10_BATCH7.md).


## Bounded 330-second synthetic lifetime probe

The POC page now offers an explicit owner-started lifetime probe. It sends one synthetic ping every 10 seconds, records browser monotonic elapsed time and close code/reason, and automatically stops at 330 seconds. The existing server idle timeout remains 25 seconds, so the heartbeat has a 15-second nominal margin. The existing rate cap permits 12 messages per 10-second window; this probe emits approximately one per window. The 330-second bound provides a 30-second observation margin beyond Vercel Hobby Fluid Compute's documented 300-second maximum while ensuring the browser-side probe itself cannot run indefinitely.

Interpretation is strict: a platform-originated close around 300 seconds is evidence of the Function maximum; a 25-second close is an idle/heartbeat failure; a client-initiated close at 330 seconds is only the probe safety timeout and must not be reported as a Vercel maximum-duration close. The probe is synthetic-only, opt-in, SSO-protected, and has not yet been executed against a new deployment. No server idle timeout was increased.

Regression contract: `backend/tests/test_vercel_ws_probe_contract.py` checks heartbeat-vs-idle arithmetic, the bounded duration, and the presence of elapsed-time/close instrumentation.


## Updated preview deployment — 2026-11-18

The bounded heartbeat probe source is deployed to a protected Vercel preview and read back as **READY**: `dpl_EV3ScKYRdCA2X4seYFktuuoQgDx6` from source commit `08263d49ab12fd2195515d673b9e84588dcbac57`. Preview URL: `https://dezzta-chart-ws-qywwkeiui-deszztagd377-pixel.vercel.app`. The deployment is isolated synthetic-only; it is not a production alias. The actual 330-second observation remains pending, so no platform maximum-duration behavior is claimed yet.


## Batch 12 — preview and probe measurement integrity — 18 November 2026

The exact source commit 9feb6cca8a51f563cae199eb33a6f57402eb3237 was independently read back as READY on the protected WSS preview. The deployment configuration includes fluid: true; this confirms the committed setting, not a measured platform maximum duration.

The exact-head CI run passed all backend pytest tests, including the WebSocket POC protocol tests, and completed the synthetic backend container smoke test. Trivy's uploaded report contained zero HIGH and zero CRITICAL findings for the backend image.

The bounded 330-second browser probe is opt-in and synthetic-only. A further measurement-integrity guard now invalidates and closes an active probe if the page becomes hidden. Background tabs and screen-off states can throttle browser timers; such an interval must not be treated as platform-duration evidence. Keep the page visible for the full observation. A client-initiated close at 330 seconds is still not evidence that Vercel itself terminated the connection at 300 seconds.

Remaining Gate 36 evidence: a real foreground 330-second run with close code/reason/elapsed-time read-back, effective Fluid Compute read-back from the deployed runtime, native Android WebView WSS, cross-instance fan-out, and owner acceptance of the zero-cost operating model. No production data or credentials are connected.

## Batch 13 exact-head deployment and CI read-back — 18 November 2026

Source commit `c3bcb0c6011f1f7228be17d16d227f325d7cbb29` has both protected previews in **READY** state:
- WSS POC: `dpl_HYCzptpjB6ZkWGjmDhqAz1QkDozc` — https://dezzta-chart-ws-haperxrzp-deszztagd377-pixel.vercel.app
- Frontend: `dpl_2f6nmwUWNWC1iLBaMBn4AMeZwBwv` — https://dezzta-chart-1e4eknez2-deszztagd377-pixel.vercel.app

Exact-head CI:
- Backend pytest: 1,013 passed in 29.73s, including all WebSocket POC and probe contract tests.
- Frontend tests/build and credential scans passed.
- Backend container build and persistent-volume/Redis ACL smoke test passed.
- Trivy report: zero HIGH and zero CRITICAL.
- CodeQL and full Git History Secret Audit passed.
- Overall workflow remains failed only because the final npm audit enforcement correctly blocks five High dev-dependency findings through picomatch 4.0.7.

The 330-second probe remains opt-in and synthetic-only. Its hidden-page invalidation is covered by the regression contract. The exact preview being READY is not evidence that the 330-second run was performed, that Vercel itself closed at 300 seconds, or that native Android WebView/cross-instance fan-out works. Do not close Gate 36 on deployment status alone.


## Batch 14 — exact-head verification refresh — 2026-11-18

Verification target: `4256c5e3ccab82255d115beaf961afd4794a3a42`.

- Automated Tests [44278716234](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716234) completed **FAILURE** only at final frontend dependency-audit enforcement.
- Backend pytest: **1,014 passed in 30.07s**; WebSocket lifecycle/probe contracts passed.
- Frontend tests/build and credential scans, Android preflight/publisher tests, synthetic outbox benchmark, backend audit, image build, Redis/persistent-volume smoke test and Trivy report steps passed.
- CodeQL [44278716261](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716261) and Full Git History Secret Audit [44278716240](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716240) passed.
- Exact-source WSS preview READY: `dpl_AtEV8yH6S5MwGApGaHQ8HagJTJsK`, https://dezzta-chart-ws-4eo7d8j18-deszztagd377-pixel.vercel.app.
- Exact-source frontend preview READY: `dpl_2Jc2So3HmvEQ6yeESjrXbMLorivz`, https://dezzta-chart-bevptgcvw-deszztagd377-pixel.vercel.app.
- Five High npm audit findings remain through dev-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. The final enforcement failure is correct; no suppression or forced downgrade was applied.
- No owner-observed foreground 330-second run, platform-originated maximum-duration close, effective Fluid Compute read-back, native Android WebView WSS or cross-instance fan-out is recorded. Gate 36 remains OPEN.
- No production promotion, no SSO weakening, no paid resources, and no Termux requirement.



## Batch 16 — protected HTTP read-back and current deployment restriction — 18 Nov 2026

- Audited branch head `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.
- The last READY WSS preview `dpl_C9bGENGcUpmgTFaxyyPNjg1Ehapv` (source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`) returned HTTP 200 from `/health` with synthetic-only mode and production_data_connected=false.
- The root page returned HTTP 200 and includes the bounded 330-second probe and 10-second heartbeat UI.
- These are HTTP checks only. No live WebSocket upgrade/round-trip or owner-observed 330-second foreground run has been performed. A client close at 330 seconds is not proof of Vercel's 300-second platform close.
- Effective Fluid Compute read-back, native Android WebView WSS, cross-instance fan-out and cost/operational acceptance remain open. Gate 36 remains OPEN.
- For branch head `a5e90f75329c937a4ef11d560bab3b434e7f24e8`, both Vercel project status contexts report `build-rate-limit`; exact-SHA deployment lookup returned zero deployments. Previous READY previews remain tied to `72a959f...`; do not report current head as deployed.
- GitHub CI [44280286764](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286764): 1,014 backend tests passed in 31.94s and all build/security/infra steps passed except the final npm audit enforcement (five High dev-only picomatch findings). CodeQL and full history secret audit passed.


## Batch 17 — exact active branch and deployment restriction — 18 Nov 2026

- Active branch head read directly from GitHub: `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a`; parent `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.
- Exact-head Vercel status contexts for WSS POC and frontend both report **“Deployment rate limited — retry in 24 hours.”**
- Exact-SHA Vercel deployment lookup returned zero deployment records for both projects. The current branch head is not deployed.
- Latest previously observed READY preview records are source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`; they must not be represented as the current branch deployment.
- No retry loop, billing activation, paid plan upgrade, SSO weakening or production promotion was performed.
- Existing HTTP 200 checks are limited to protected health/page delivery in synthetic-only mode. No actual WebSocket handshake/round-trip, owner-visible 330-second foreground test, platform-originated close, Android WebView, Fluid Compute effective setting or cross-instance fan-out is claimed.
- Gate 36 remains OPEN. No Termux needed for this repository/CI/Vercel read-back cycle.


## Batch 18 — exact-head READY deployment and HTTP read-back — 18 Nov 2026

- Source SHA: `64f348cebccbfb3fad2b9efe5a066d28962970f6`.
- WSS POC deployment `dpl_8iPQZm1Z2QJ4Dc8hjUPgSsPanPYb`: **READY**.
- Protected `/health`: HTTP 200, `status=ok`, `mode=synthetic-only`, `production_data_connected=false`.
- Protected root page: HTTP 200; browser client includes Connect, Disconnect, synthetic ping and bounded 330-second probe controls.
- HTTP fetch did not negotiate WebSocket Upgrade. No actual WSS handshake, ping/pong, 330-second foreground observation, platform close attribution, Android WebView, Fluid Compute effective setting or cross-instance fan-out is claimed.
- Gate 36 remains OPEN. No production data is connected.
