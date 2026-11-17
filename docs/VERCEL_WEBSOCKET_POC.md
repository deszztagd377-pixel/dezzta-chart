# DEZZTA CHART — Isolated Vercel WebSocket POC

Status: **CI SUCCESS; protected staging deployment READY; live HTTP/WSS acceptance pending**  
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
| HTTP health | Protected real request to `/health` | Pending |
| WebSocket upgrade | Browser panel receives `ready`, then ordered `pong` responses | Pending |
| Disconnect/reconnect | Close then reconnect obtains a new session ID and sequence restarts | Pending |
| Idle/lifetime behavior | Idle close and Vercel maximum-duration close are observed | Pending |
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
