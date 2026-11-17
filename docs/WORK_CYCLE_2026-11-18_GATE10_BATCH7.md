# DEZZTA CHART — Gate 10 Batch 7: WebSocket Lifetime and Vercel Hobby Limits

Date: 2026-11-18  
Working branch: `phase-2/market-data-foundation`  
Scope: Gate 36 — isolated synthetic WebSocket POC  
Cost policy: ZERO COST; no plan upgrade, paid service, or billing activation.

## Executive result

The Vercel WebSocket platform blocker is now narrowed to a documented runtime-lifetime constraint, not an inability to deploy or an unsupported transport.

- The dedicated FastAPI WebSocket POC deployment is **READY** and remains protected by SSO for all deployment targets.
- The main Vite frontend deployment is also **READY**.
- Vercel WebSocket support is generally available as of 2026-10-20.
- Vercel documents that a WebSocket connection is pinned to the Function instance and closes when the Function reaches its maximum duration. Clients must reconnect; durable shared state cannot rely on one Function instance's memory.
- The Vercel team plan remains Hobby. With Fluid Compute, the documented Hobby default and maximum function duration are both **300 seconds (5 minutes)**. Hobby cannot raise this maximum.
- The source POC explicitly requests Fluid Compute using `poc/vercel_ws/vercel.json` with `"fluid": true`. The project settings API read-back still does not expose an independently verifiable effective Fluid Compute flag.

**Gate 36 remains OPEN.** The browser HTTP health, WebSocket handshake, ping/pong, manual reconnect with a fresh session, and idle timeout have already been owner-observed and recorded in the prior report. This batch does not claim a platform maximum-duration close, independent runtime setting read-back, Android Capacitor WebView acceptance, or production cross-instance fan-out.

## Verified repository and deployment state

- Exact active branch head at audit time: `de90b32a87111458f9225cc5151a59420f1fe8fb`.
- The branch is `phase-2/market-data-foundation`; `main` was not modified.
- Dedicated WSS POC: `dpl_5soNcXQGktR397joj26jcwe7Voas`, **READY**, source commit `cfc56b7ba050201823952ea1b67dd38182dc9bfb`.
- Main Vite frontend: `dpl_BzAaDUru7yhSX2pEWRt8EGxLLpdk`, **READY**, source commit `545334d9a594b58c19168df1b059f44ed520949c`.
- POC deployment protection: SSO enabled for **all** deployment targets.
- Frontend deployment protection: SSO enabled for all targets except custom domains.
- Both projects are non-production preview projects (`live=false`); no production alias was promoted in this audit.

The latest POC deployment is from the last source/test commit, not the latest docs-only commit. The frontend deployment is also an earlier known-good build. READY confirms those specific deployments; it does not prove remaining account quota or guarantee that a future build cannot encounter a rate limit.

## WebSocket lifetime calculation

| Item | Hobby / POC value | Meaning |
|---|---:|---|
| Fluid Compute default function duration | 300 s | Default maximum request/function lifetime |
| Fluid Compute Hobby maximum | 300 s | No Hobby headroom to increase it |
| Equivalent time | 5 min | Expected upper bound for a single function invocation |
| POC application idle timeout | 25 s | Current POC closes an idle socket well before the platform limit |
| Gap between idle close and platform cap | 275 s | A quiet connection cannot currently reach the platform cap |

The POC's existing 25-second idle timeout means that simply leaving the browser tab open will **not** test Vercel's 300-second maximum. A valid maximum-duration probe must keep the synthetic connection active at intervals shorter than 25 seconds, record connection-open time, and capture the close event. The probe must remain synthetic-only and protected by SSO.

## Safe bounded test design

The next platform-lifetime probe must be isolated to the disposable POC and must not connect production market data.

1. Keep the current 25-second server idle timeout unchanged unless a test-specific configuration explicitly requires otherwise.
2. Use a test-only client heartbeat interval with a comfortable margin below 25 seconds (for example, 10 seconds) so the server does not close the connection for idleness.
3. Record the browser-side monotonic connection start time, each synthetic pong, and the final WebSocket close code/reason. Do not log credentials, tokens, owner IDs, or private account data.
4. Prefer a temporary, lower `maxDuration` override on the POC preview (for example, 60 seconds) to prove the platform-triggered close with a bounded observation window. This tests the platform close mechanism but **does not** independently prove the full 300-second Hobby ceiling.
5. If the 60-second cap is not independently confirmed in the build/runtime configuration, do not claim a platform close test. Use a single controlled 300-second maximum-duration observation only after confirming the current Hobby usage allowance and ensuring no paid billing is activated.
6. Keep SSO enabled for every deployment target. Do not create a protection-bypass URL, public test route, custom domain, or production alias.
7. After a platform close, the production client design must reconnect with bounded exponential backoff, resubscribe to the exact stream, resume from a durable cursor, deduplicate replay/live overlap, and resnapshot if replay is unavailable.

A 60-second preview cap is a proposed test configuration, not yet applied. No deployment or long-lived connection test was triggered in this batch.

## Architectural consequence for DEZZTA CHART

A Vercel Hobby WebSocket can be used for short-lived realtime sessions, but it must not be treated as a permanent socket or durable worker.

Required client/server behavior before production acceptance:

- Client reconnect state machine: disconnected → connecting → authenticated → subscribed → recovering → live.
- Bounded exponential retry with jitter; stop retrying on permanent authentication/entitlement denial.
- Reauthenticate and re-check entitlement after reconnect.
- Restore the last acknowledged durable cursor; request replay and detect gaps.
- Deduplicate replayed events and queued live events using stable cursor/sequence identity.
- Force a fresh snapshot when the cursor is expired, invalid, or replay backlog exceeds a safe bound.
- Keep cross-instance state, leases, quotas, and fan-out outside Function process memory.
- Do not treat a synthetic POC ping/pong as proof of production market-data delivery.

This aligns with the existing backend's durable outbox/replay and exact-series subscription design, but production acceptance still requires the actual shared-store and host evidence.

## Work completed in this batch

- Re-read the active branch head and confirmed it is still the expected docs checkpoint.
- Re-read the isolated POC implementation and its explicit Fluid Compute request.
- Re-read both Vercel project records and both latest deployment records.
- Confirmed the current Hobby duration ceiling from Vercel's published Fluid Compute documentation.
- Identified why the current 25-second idle timeout prevents a 300-second platform-lifetime test.
- Produced this bounded test plan without changing runtime code, Vercel settings, deployment state, billing, or the production application.

## Gate 10 and project progress accounting

No acceptance ticks are awarded in this batch.

- Stage 1: **300/400 ticks = 75% provisional**.
- Gate 10: **0/10 external criteria formally closed**.
- Still-open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Gate 36: browser transport sub-checks remain passed; platform maximum-duration close, effective Fluid Compute read-back, Android WebView acceptance, production cross-instance fan-out, and cost/operational acceptance remain open.
- Stages 2–6: **NOT SCORED**.
- Overall 20.90%: historical checkpoint only; not recalculated.
- ZERO COST preserved. No Termux use or installation is needed for this remote repository/configuration audit.

The six-stage colored dashboard and Stage 1 ten-gate dashboard remain the authoritative project-process progress visuals. This document is a supporting work-cycle report, not a replacement dashboard and not an in-APK indicator.

## Files changed

- `docs/WORK_CYCLE_2026-11-18_GATE10_BATCH7.md` — added.

## Verification boundary

This is a documentation-only commit. It does not claim that a new source test ran, a new Vercel deployment was created, the maximum-duration close was observed, or Gate 36 was closed.
