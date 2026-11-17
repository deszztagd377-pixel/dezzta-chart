# DEZZTA CHART — Isolated Vercel WebSocket POC

Status: **repository implementation prepared; protected Vercel deployment and live browser verification pending**  
Date: 2026-11-17  
Working branch: `phase-2/market-data-foundation`

## Purpose

Prove only the platform transport path for FastAPI ASGI over Vercel Fluid Compute. This is a disposable synthetic probe, not the DEZZTA CHART production backend.

The POC is isolated under `poc/vercel_ws/` so the existing Vite project, its root settings, routing and frontend deployment remain untouched. The separate Vercel project must use this directory as its Root Directory and SSO protection must be enabled before its first deployment.

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
| Repository unit tests | Exact-HEAD CI test results | Pending |
| Separate Vercel project | Dedicated project, Root Directory `poc/vercel_ws`, Hobby plan | Pending |
| Deployment protection | SSO enabled before first deployment | Pending |
| Fluid Compute | Read-back confirms enabled | Pending |
| HTTP health | Deployed `/health` returns the exact synthetic-only payload | Pending |
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
