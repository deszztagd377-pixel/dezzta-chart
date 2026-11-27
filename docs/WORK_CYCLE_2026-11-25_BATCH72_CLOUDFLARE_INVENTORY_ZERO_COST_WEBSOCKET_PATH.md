# DEZZTA CHART — Work Cycle 72: Cloudflare deployment reality check and zero-cost WebSocket path
Date: 25 November 2026
Branch: `phase-2/market-data-foundation`
Audited source HEAD: `6a6e9e82ed2de725bef94e8ed1fa7f28c60e0a49`
Parent: `6a6e9e82ed2de725bef94e8ed1fa7f28c60e0a49`
Scope: verify the user's Cloudflare hosting correction against the repository and connected Cloudflare account; distinguish synthetic proof from deployed production infrastructure; define the zero-cost next path.
Runtime/source changes: none. No resource was created, changed, or deployed.
Cost: ZERO COST preserved.

## 1. Executive result

The user is correct that Cloudflare is already part of the DEZZTA CHART architecture. The repository contains a Cloudflare Worker + SQLite Durable Object proof and CI exercises it. However, the proof is intentionally synthetic-only and is not the production backend or a deployed WSS service.

A read-only inventory of the Cloudflare account currently connected to this session found no deployed Worker scripts, no Pages projects, no Cloudflare Tunnels, no Durable Object namespaces, no Queues, no D1 databases, no KV namespaces, no zones, and no Worker custom domains. The account has no `workers.dev` subdomain yet. The Containers API reports that deploying Cloudflare Containers requires the Workers Paid plan, so Containers are excluded from the ZERO COST design.

This inventory describes only the currently connected Cloudflare account. It does not prove that another Cloudflare account or an independently configured project does not exist.

## 2. Repository evidence

- `cloudflare/wrangler.jsonc` names the project `dezzta-chart-synthetic-proof`, sets `main` to `proof/worker.mjs`, disables `workers_dev` and preview URLs, sets `PROOF_MODE=synthetic-only`, allows localhost origins only, and binds the SQLite-backed `SeriesCoordinatorDO` class.
- `cloudflare/proof/worker.mjs` implements deterministic synthetic bars, hashed single-use proof tickets, a 50-bar synthetic snapshot, sequence continuity, per-series WebSocket fan-out, authentication timeout, and Durable Object hibernation-safe socket attachments.
- The source comment explicitly says this is an isolated experiment: it is not wired to the production FastAPI app, Firebase, a market-data provider, or the UI. It creates no provider connection or recurring timer.
- `.github/workflows/ci.yml` runs Node checks, the synthetic Worker tests, a pinned local workerd/Miniflare runtime test, and Durable Object hibernation/alarm/per-series isolation tests.
- The backend production entrypoint remains `uvicorn app.main:app` in `backend/Dockerfile`. Cloudflare Workers cannot run this Python container as-is. Cloudflare Containers are not a ZERO COST option because the account API reports that they require Workers Paid.

Therefore, the repository has a tested Cloudflare proof, not a deployed Cloudflare production server.

## 3. Zero-cost Cloudflare capability boundary

Current official Cloudflare documentation says:
- Workers Free includes up to 100,000 requests/day and 10 ms CPU time per invocation.
- SQLite-backed Durable Objects are available on Workers Free, with free quotas of 100,000 DO requests/day, 13,000 GB-s/day, 100,000 SQL row writes/day, and 5 GB total SQLite storage.
- When a Workers Free quota is exceeded, operations of that type fail rather than silently becoming paid usage. These are ceilings, not a capacity guarantee for the full DEZZTA CHART workload.
- Cloudflare Tunnel is available on all plans and supports WebSockets, but it connects Cloudflare to an already-running origin machine via `cloudflared`; it is not itself a Python application host.
- Cloudflare Containers require Workers Paid and are explicitly excluded.

Official references:
- Workers pricing: https://developers.cloudflare.com/workers/platform/pricing/
- Workers limits: https://developers.cloudflare.com/workers/platform/limits/
- Durable Objects pricing: https://developers.cloudflare.com/durable-objects/platform/pricing/
- Cloudflare Tunnel: https://developers.cloudflare.com/tunnel/
- Tunnel WebSocket support: https://developers.cloudflare.com/cloudflare-one/faq/cloudflare-tunnels-faq/

## 4. Correct architecture choices — no deployment until confirmed

Two technically distinct routes remain:

**Route A — Cloudflare-native edge + backend migration.**
Use a Workers Free entrypoint for HTTPS/WSS and SQLite Durable Objects for per-series coordination, ticket lifecycle, socket hibernation, and durable coordination state. The existing Python FastAPI backend cannot be dropped into this runtime. Required production API/identity/data logic must be deliberately ported or replaced with supported Worker-compatible modules. Provider connectivity, entitlements, durable snapshot/receipt semantics, and free-quota capacity must be validated before this can be accepted.

**Route B — Cloudflare edge + existing owner-operated origin.**
Use Workers/DO for edge WSS and coordination, with Cloudflare Tunnel forwarding to an existing owner-operated FastAPI origin. This requires a real always-on origin machine, a running `cloudflared` connector, and a configured Tunnel/hostname. No such Tunnel or origin was visible in the connected account inventory. Do not infer that a Cloudflare Tunnel exists merely because the domain/account uses Cloudflare.

No route is selected yet. Do not create a Worker, DO namespace, Tunnel, hostname, secret, or paid plan without confirming the intended existing Cloudflare project/account and deployment target. Do not set `workers_dev=true` or deploy the synthetic proof as if it were production.

## 5. WebSocket and Project Gate 25 consequences

The Cloudflare Durable Object proof provides useful groundwork for WSS connection lifecycle and per-series coordination, but it does not close:
- Firebase identity verification and entitlement binding;
- production one-time ticket issuance and revocation;
- live-provider data provenance and lawful zero-cost provider access;
- source-to-gateway signed snapshot transfer;
- authenticated persisted receipt retrieval;
- durable per-gateway high-water ACK ledger, fencing and restart reconciliation;
- public HTTPS/WSS browser and Android lifecycle acceptance.

Cloudflare Durable Objects may be a suitable location for a future durable ACK coordinator, but that is a design candidate only. It must not be treated as interchangeable with the existing Redis stream, SQLite replica checkpoint, or owner-signed immutable receipt. Redis `XACK` is not the owner-accepted high-water ACK. `XTRIM`, `XDEL`, and consumer-group destruction remain blocked.

## 6. Stage and indicator accounting

- Official active stage: Stage 1 — Foundation, Security & Data Integrity.
- Stage 1: 30/40 = 75% provisional 🟨.
- Gate 10: 0/10 formally closed 🟥; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain Stage 1 acceptance items.
- Stage 2: 🟦 PREPARATORY only; the branch name is not a stage transition.
- Stage 3: ⚪ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5: ⚪ NOT SCORED.
- Stage 6: ⚪ NOT SCORED.
- Overall project, aggregate indicator completion and IP3S: ⚪ NOT SCORED; no approved weighted denominator/formula.

### Complete indicator inventory

| Indicator/subsystem | Calculation/data foundation | Rendering/interaction/lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides and lifecycle absent | 🟨 FOUNDATION |
| MACD12/26/9 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram and zero guide absent | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Bands, fill, legend and lifecycle absent | 🟨 FOUNDATION |
| Shared Indicator Hook | Immutable keyed snapshot/cache/trust gate; 7 focused declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Stage 4 gated; two supplied references define visual target | 🟧 GATED |
| Volume Profile | Binning/value-area behavior not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Lawful depth source, aggregation and decay not accepted | Not integrated; visual reference gate remains | 🟥 OPEN |
| Liquidation Maps | Provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

Focused declarations remain 28 = 21 calculation + 7 shared-hook. This is not a pass count or completion percentage. No indicator source or UI changed in Batch 72; indicator completion credit is zero.

Global calculation invariants remain: warm-up nulls, prefix causality, no future-candle lookahead/repaint, exact timestamp and canonical series alignment, stale output cleared on identity changes, and no calculations for demo/loading/unavailable/error/empty snapshots. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual implementation remains reference-gated.

## 7. Next work order

1. Confirm the exact Cloudflare account/project and whether an existing Worker/Pages/Tunnel is expected to be present there.
2. Select Route A or Route B from actual available resources, not assumption.
3. Produce a scoped runtime and identity/transport contract with a zero-cost quota budget.
4. Only after review, implement and test the Cloudflare production composition; keep the synthetic proof isolated.
5. Add durable per-gateway receipt/ACK ledger, fencing, restart and stale-owner tests.
6. Verify real signed snapshot transfer and receipt re-verification.
7. Complete Stage 1 host/security acceptance and Gate 36 browser/Android WSS E2E.
8. Keep Redis destructive retention blocked until every gateway's durable high-water ACK is accepted.
9. Keep indicator UI behind Stage 4 and its scoped blueprint/user-review gate.

Delivery planning target remains around 24 December 2026. ZERO COST, `main` untouched, Vercel deferred, no paid data/hosting/monitoring, and no production deployment in this cycle.



---

## Addendum — 27 November 2026: connected-account inventory refresh

This addendum supersedes only the 25 November account-inventory snapshot above. It does not change the historical record or authorize deployment.

### Current read-only inventory

The connected account now contains one deployed Worker script: `dezzta-chart-runner-relay`.

- The Worker has four recorded deployments. The latest deployment is version 4, created 26 November 2026 at 11:43:55 UTC, with 100% of traffic assigned to that version.
- The script's Workers subdomain is enabled; previews are disabled. No custom Worker domains are listed.
- The account currently has zero Durable Object namespaces and zero Pages projects.
- The Worker script metadata reports `usage_model: standard`. Cloudflare's current pricing documentation says the Standard usage model is available to Workers Paid plan users. The exact account billing plan was not inspected; therefore this Worker is **not certified zero-cost** until the plan/usage model is confirmed. Do not create additional paid resources.
- The script has secret bindings named `CRON_SECRET` and `GITHUB_TOKEN`. Secret values were not read or exposed.

### What this Worker actually does

Source inspection of the deployed script shows only a `fetch` handler:
- `GET /health` returns a standby health response.
- `POST /trigger` validates a bearer secret and dispatches `workflow_dispatch` for `preflight.yml` in the separate `dezzta-chart-runner` repository.
- It does not implement a WebSocket endpoint, Durable Object binding, or a `scheduled` handler.

The runner workflow at [`.github/workflows/preflight.yml`](https://github.com/deszztagd377-pixel/dezzta-chart-runner/blob/main/.github/workflows/preflight.yml) declares only `workflow_dispatch`; it has no GitHub `schedule` trigger. Its job checks out `phase-2/market-data-foundation`, verifies the branch and `package.json`, and explicitly performs no dependency installation, build, tests, edits, or pushes.

The Worker has no Cloudflare Cron Triggers configured. The runner history contains successful manual/API `workflow_dispatch` executions at ten-minute spacing on 26 November, with the latest listed run [45836285961](https://github.com/deszztagd377-pixel/dezzta-chart-runner/actions/runs/45836285961) completed successfully at 14:10:15 UTC. The runner repository currently has no active workflow runs.

**Conclusion:** the existing relay is a deployed preflight dispatcher, not an autonomous AI engineering agent and not the DEZZTA CHART market-data WebSocket service. The observed ten-minute invocations came from an external trigger; neither the Worker nor the workflow contains a self-scheduling ten-minute trigger. Do not represent those preflight executions as code implementation or APK production.

### WebSocket production boundary

The runner relay does not satisfy the production WSS requirement. The connected Cloudflare account still has no Durable Object namespace, no Pages project, and no custom Worker domain. The separate repository's synthetic Worker proof remains a test artifact; it is not deployed by this runner relay. Production public WSS, authenticated market-data runtime, and real browser/Android acceptance remain YELLOW and unaccepted.

### Cost and change controls

- No Worker, Durable Object namespace, Pages project, domain, Cron Trigger, secret, or deployment was created, changed, or deleted during this audit.
- No secret value was retrieved.
- Because the Worker reports the Standard usage model, keep its zero-cost status YELLOW until the account plan is confirmed against Cloudflare's [official Workers pricing documentation](https://developers.cloudflare.com/workers/platform/pricing/).
- Do not add a Cron Trigger to this script: it has no `scheduled` handler, and doing so would not make it perform AI-assisted project work.
- `main` remains untouched. No active GitHub Actions run was left running by this audit.


### Follow-up verification — 27 November 2026

A further read-only verification was performed after this inventory was drafted:

- Cloudflare identity and account listing succeeded; the existing connector session remains authenticated for the account and Workers read operations.
- A read of the account billing profile returned HTTP 403 / API error 10000 because this connector session does not have an accepted `billing:read` or `billing:write` scope. This is a permission limitation, not evidence of a billing-plan value. The account's zero-cost status therefore remains **UNVERIFIED / YELLOW**. Do not attempt to bypass this with a new token or change the billing plan.
- A public `GET /health` probe from the execution environment was blocked by the environment's outbound-request policy (HTTP 403). This does not establish whether the public Worker endpoint is healthy or unhealthy; public endpoint health remains **UNVERIFIED / YELLOW**.
- A second usage-model read returned HTTP 415 because the request did not satisfy that endpoint's required `application/json` content type. The earlier successful metadata response reporting `usage_model: standard` remains the recorded evidence; no billing-plan inference is added.
- No Cloudflare resource, secret, schedule, deployment, or billing setting was modified.
- No recurring 10-minute automation is requested or being continued. The historical runner invocations are retained only as audit history; they are not a current work instruction.
