# DEZZTA CHART — Vercel Backend Feasibility & Phone-Only Deployment Plan

Audit date: 2026-11-17  
Repository: `deszztagd377-pixel/dezzta-chart`  
Branch: `phase-2/market-data-foundation`  
Audited code baseline: `8a4e297efa6c07b8e130b81fbb271c9085ba707e`  
Policy: **ZERO COST — no laptop/PC requirement**

## Executive decision

A laptop or desktop computer is **not required** to continue repository development or deploy a managed backend. The owner works from an Android phone; GitHub and Vercel can handle repository and deployment operations remotely.

Vercel is now a technically credible backend candidate: WebSocket support became generally available on 2026-10-20, and its Python runtime supports FastAPI (currently documented as Beta). This corrects the earlier assumption that Vercel deployment only covers the frontend or cannot serve WebSockets.

However, the existing FastAPI backend must **not** be pointed at Vercel and declared production-ready without changes. The current backend relies on local SQLite files, process-local in-memory WebSocket fan-out, and lifecycle-managed background tasks. Vercel Functions are bounded, may be recycled, and have only a read-only filesystem plus temporary `/tmp` scratch space. These properties break the assumptions behind the current durable SQLite and single-process stream hub.

**Decision:** pursue a Vercel-managed backend proof-of-concept, not a direct production deployment. Keep the existing backend security rules and data contracts. Do not introduce paid services or weaken durability/authentication to force a deployment.

## Current repository facts

1. Frontend is React + TypeScript + Vite at repository root.
2. Backend is a separate FastAPI application under `backend/`, with dependencies in `backend/requirements.txt`.
3. The repository has no root `api/` Python Function entrypoint or root `vercel.json` in the audited baseline.
4. The README documents Vercel frontend build-time configuration through `VITE_*` variables. Those variables are public client configuration and must never contain service-account credentials, provider keys, Redis passwords, or other backend secrets.
5. Production settings require Firebase project identity and TLS Redis with ACL username/password. Redis security must remain fail-closed.
6. OHLCV bars and outbox events are persisted through SQLite adapters at `instrument_registry_db_path`.
7. `OhlcvStreamHub` keeps subscriptions and queues in process memory. The Redis shared guard currently protects limits/leases; it is not proof of cross-instance event pub/sub.
8. The upstream paid market-data provider remains disabled under ZERO COST. No demo fixture may be labelled as live exchange data.

## Verified platform capabilities and limits

| Capability | Current platform evidence | Consequence |
|---|---|---|
| Vercel WebSockets | Generally available since 2026-10-20 | A Vercel-hosted WSS endpoint is now a valid architecture candidate |
| Python runtime | Generally available; current guidance supports FastAPI/ASGI | A small compatibility POC is still required before production |
| Function lifecycle | Connections are pinned to an instance and bounded by function max duration | Client reconnect, backoff, re-authentication and replay are mandatory |
| Filesystem | Read-only except temporary `/tmp` scratch storage | Local SQLite files cannot be treated as durable production storage |
| Instance state | Separate instances can handle different connections | Process-local subscription maps cannot provide global fan-out |
| Free plan limits | Plan-specific execution, duration and usage quotas apply | Measure expected load; never assume unlimited free service |

Official references:
- WebSocket GA: https://vercel.com/changelog/websocket-support-is-now-generally-available
- WebSocket lifecycle and shared state: https://vercel.com/kb/guide/do-vercel-serverless-functions-support-websocket-connections
- Python runtime/FastAPI: https://vercel.com/docs/functions/runtimes/python
- Filesystem and runtime limits: https://vercel.com/docs/functions/runtimes
- Function duration: https://vercel.com/docs/functions/limitations

## Blocking compatibility work

### A. Python FastAPI WebSocket proof

- Create a minimal isolated function entrypoint only after confirming the exact Vercel project root/build configuration.
- Prove HTTP health, Firebase token verification, WebSocket upgrade, authenticated subscribe, disconnect, reconnect and replay on the actual free deployment.
- Verify the Python runtime's WebSocket support directly; general WebSocket GA and Python FastAPI support are separate documented capabilities and must not be conflated.
- Keep the existing frontend and current backend routes unchanged until the POC passes.
- Confirm the function duration ceiling and ensure the client reconnects before/after forced function closure.

### B. Durable state and cross-instance fan-out

The current SQLite files cannot live in Vercel's temporary filesystem. The current in-memory stream hub is also instance-local.

Required before a production migration:
1. Select a genuinely free, durable store with documented quotas and no billing requirement for the intended usage.
2. Store OHLCV bars and outbox cursor/events durably, preserving exact decimal text and nanosecond timestamps.
3. Make subscription fan-out cross-instance, using an authenticated shared pub/sub or coordination mechanism.
4. Preserve replay/live handoff ordering, cursor monotonicity, overflow-to-resnapshot behavior, provider/dataset identity isolation, and authorization rechecks.
5. Preserve backup/export, encryption, recovery, retention and access controls.
6. Prove Redis ACL/TLS and outage fail-closed behavior if Redis remains in the production topology.

A free quota is not a promise of unlimited usage. If no service satisfies both zero cost and the security/durability requirements, keep live backend delivery marked unavailable rather than silently switching to an insecure or paid fallback.

### C. Background tasks and provider lifecycle

Vercel Functions are not an always-on VM. Do not rely on a process-lifespan task to run continuously for provider ingestion or notification delivery. Those jobs need an explicitly supported scheduled/queue mechanism with a proven free quota, or must remain disabled. No paid or unlicensed feed is to be activated.

### D. Mobile client

The Android APK remains frontend-first. It must:
- use HTTPS/WSS only for production endpoints;
- obtain Firebase ID tokens through the existing identity flow;
- reconnect with bounded exponential backoff and jitter;
- re-authenticate and resubscribe after reconnect;
- resume from the last durable cursor and handle `resnapshot_required`;
- display DEMO/OFFLINE/UNAVAILABLE accurately;
- never disable certificate validation.

## Gate 10 implications

| Gate | What this Vercel audit changes | What remains open |
|---:|---|---|
| 8 — Secrets | Managed secret injection is a possible route | Verify Vercel secret scope, no frontend exposure and no billing |
| 20 — Firebase | No change to existing Firebase verification code | Real project sign-in, expiry/revocation and entitlement acceptance |
| 25 — Redis | Vercel does not remove the Redis security requirement | Free durable/shared Redis-compatible service, TLS/ACL, restart/outage proof |
| 30 — Restore | Vercel `/tmp` is not a backup destination | Durable off-instance backup and target restore drill |
| 31 — Encryption | Existing authenticated encryption remains relevant | Separate key custody and free durable backup destination |
| 34 — Storage | Local SQLite is incompatible with serverless persistence | Durable external store and recovery acceptance |
| 35 — HTTPS | Vercel can terminate HTTPS for deployed functions | Verify backend health route and exact deployed origin |
| 36 — WSS | Vercel WebSockets are GA; no PC or always-on VM is inherently required | Python FastAPI WSS POC, shared state, production Android/browser reconnect and latency proof |
| 38 — Monitoring | Vercel-managed logs may help operational visibility | Durable metrics, retention, alert thresholds, dashboard and zero-cost proof |
| 39 — Notifications | No continuous worker can be assumed | Free scheduled delivery path, receipt/acknowledgement and recovery drill |

No gate is closed by this feasibility audit. Platform capability is not the same as project integration or owner acceptance.

## Safe implementation sequence

1. Keep the frontend Vercel project and current FastAPI backend unchanged.
2. Verify the current Vercel project root, build settings, framework detection and free usage constraints from its deployment configuration.
3. Build a tiny isolated Python FastAPI HTTP + WebSocket POC with no secrets, no market data, no persistent writes and no background worker.
4. Validate the POC deployment and WebSocket lifecycle using the Android phone.
5. Select and test the durable shared store only after documenting its actual free quota, TLS/ACL model, retention and export path.
6. Design a scoped migration of SQLite adapters and stream fan-out. Preserve existing contracts and add compatibility tests before changing production routes.
7. Add Android reconnect/replay acceptance and production health/WSS probes.
8. Update Gate 10 evidence only after each external acceptance check passes.

## Owner/device requirements

- No laptop or desktop PC is required for this plan.
- The owner already has Termux installed on the Android phone, but no Termux command is needed for this repository-side audit.
- A previous Termux repository-signature/keyring mismatch remains unresolved; do not update package sources, install packages, downgrade cryptography, or bypass signature verification.
- No credentials, tokens, passwords, service-account JSON, or private keys should be sent in chat.
- No paid Vercel upgrade, paid Redis, paid hosting, paid monitoring, paid data provider, or Play Store publication fee is allowed.

## Progress accounting

- Stage 1 remains **300/400 ticks = 75% provisional** (30/40 provisional criteria).
- Gate 10 remains **0/10 formally closed** until external evidence is accepted.
- Stages 2–6 remain **NOT SCORED**.
- Overall **20.90% remains a historical owner-confirmed checkpoint**, not a newly calculated total.
- This audit earns **zero acceptance ticks**; it corrects architecture direction and documents the next verifiable work.


## 2026-11-17 — Verified Python GA, repository boundary and free-tier blockers

### Runtime status correction

The Python runtime is now **Generally Available (GA)**, announced 2026-10-15. Vercel WebSockets became **Generally Available (GA)** on 2026-10-20. The earlier Beta label in historical notes is superseded. Current Vercel guidance explicitly describes Python ASGI WebSockets, including FastAPI, on Fluid Compute.

The POC still has to verify the target project's Fluid Compute setting and actual deployed behavior. A platform capability is not proof that this repository's current project is configured for it.

### Existing Vercel project boundary

A fresh root inspection confirms the root `package.json` is a Vite/React frontend and the repository has no root `vercel.json` or root `api/` entrypoint. Do not inject a root API route or replace the frontend routing blindly. That could alter the existing frontend deployment.

Safe POC boundary:
- Keep the existing Vite project and production backend untouched.
- Use a dedicated POC subdirectory as the Root Directory of a separate Vercel project, or another explicitly isolated project configuration.
- Confirm project root, framework/build settings, Fluid Compute, and free-plan usage before deploying.
- Do not add production credentials, Firebase auth, market data, durable writes, or background workers to the echo POC.
- Prove HTTP health, WebSocket upgrade/echo, connection lifetime, disconnect and reconnect from the Android phone.

### Zero-cost storage screening

| Candidate | Verified free allowance | Security/recovery blocker | Gate disposition |
|---|---|---|---|
| Upstash Redis Free | 256 MB, 500K commands/month, 10 GB/month bandwidth | ACL is available only on paid databases; IP allowlist excludes Free | Reject for Gate 25 |
| Cloud Firestore Spark | 1 GiB, 50K reads/day, 20K writes/day, 20K deletes/day, 10 GiB outbound/month | Managed backup, restore, PITR and clone require billing; quota exhaustion shuts the product off for the rest of the period | Does not close Gates 30/31 |
| Firestore as record storage | Small prototype may fit Spark quotas | No demonstrated complete cross-instance WebSocket fan-out + separately controlled encrypted off-host backup + restore path | Not selected |

References:
- Python GA: https://vercel.com/changelog/python-on-vercel-is-now-generally-available
- Python ASGI/FastAPI runtime: https://vercel.com/docs/functions/runtimes/python
- WebSocket GA: https://vercel.com/changelog/websocket-support-is-now-generally-available
- Python WebSocket/Fluid Compute guidance: https://vercel.com/i/wsgi-vs-asgi
- Upstash Free pricing: https://upstash.com/pricing/redis
- Upstash ACL availability: https://upstash.com/docs/redis/features/security
- Upstash IP allowlist availability: https://upstash.com/docs/redis/help/production-checklist
- Firestore Spark quotas and billing-required backup/restore/PITR: https://firebase.google.com/docs/firestore/quotas
- Spark quota shutdown behavior: https://firebase.google.com/docs/projects/billing/firebase-pricing-plans

**Decision:** no provider currently proves all required properties together: zero cost, durable OHLCV/outbox storage, cross-instance fan-out, TLS/ACL/private access, encrypted off-host backup and tested recovery. Do not select Upstash Free for Gate 25 or represent Firestore Spark as a complete backup solution.


## 2026-11-17 — Live connector and exact-commit deployment verification

The Vercel account connection is now active and has been read successfully through the Vercel integration.

Verified account/project facts:
- Vercel team plan: **Hobby** (zero-cost plan; do not upgrade).
- Project: `dezzta-chart`, framework: **Vite**.
- Linked Git repository: `deszztagd377-pixel/dezzta-chart`.
- Exact branch: `phase-2/market-data-foundation`.
- Exact commit at the time of the first connector read: `056cdd0a838ce2c47b4206af3801d6778af05675` (historical checkpoint).
- The follow-up documentation commit `8a4e297efa6c07b8e130b81fbb271c9085ba707e` was automatically deployed by the existing Git integration as a Vercel preview and reached **READY**: `https://dezzta-chart-4nil5h92d-deszztagd377-pixel.vercel.app`.
- No manual redeploy or forced deployment was requested. The deployment target remains preview, not verified production.

The available project read response confirms the Vite framework and project identity but does not expose the saved `rootDirectory` or Fluid Compute setting. Those two settings therefore remain **UNVERIFIED**; absence from the connector response is not evidence that either setting is enabled or disabled. Do not create or deploy a Python entrypoint in this Vite project until those settings can be inspected or an isolated second project is explicitly prepared.

The deployment being READY proves that this exact branch commit built and deployed as a Vite preview. It does **not** prove a Python FastAPI runtime, HTTP backend health route, authenticated WebSocket upgrade, reconnect, cross-instance fan-out, durable storage, or production WSS.

The Vercel project is on Hobby. All subsequent POC design must remain within the existing no-billing allowance; do not upgrade, enable paid products, or add paid integrations.


## 2026-11-17 — Follow-up documentation commit deployment

The evidence refresh itself was committed as `8a4e297efa6c07b8e130b81fbb271c9085ba707e` on `phase-2/market-data-foundation`. The connected Vercel Git integration automatically created preview deployment `dpl_FGQfAqGjFnimCpBGDaAsW3uP9H2Z`, which reached **READY**. Preview URL: https://dezzta-chart-4nil5h92d-deszztagd377-pixel.vercel.app

This is still a Vite frontend preview. It does not change the unresolved backend/WSS POC, durable-store, or cross-instance fan-out requirements. Root Directory and Fluid Compute remain unverified because the connected project-read response did not expose those fields.
