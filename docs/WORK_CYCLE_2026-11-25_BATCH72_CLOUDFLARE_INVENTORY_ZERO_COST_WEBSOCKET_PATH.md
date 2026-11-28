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

---

## Repository synthetic WebSocket source reconciliation — 27 November 2026

This is a separate repository-source finding. It does not change the Cloudflare account inventory above and does not establish production deployment.

**Exact inspected source baseline:** PR #11 base `4979bd4a69dfd37b4571a125790150931c4154ee` (`phase-2/market-data-foundation`).

| File | Inspected blob SHA |
|---|---|
| `cloudflare/proof/worker.mjs` | `e8b4b5b5c4c35c5b7915ff46df00ced39e894f88` |
| `cloudflare/proof/worker.node-test.mjs` | `13f33364301f7e60a82b3aa8f095d0bb6f3f61e4` |
| `cloudflare/proof/worker.durable-object.runtime.mjs` | `ef9a58f0f1f7c220366b330079e432c916df585b` |
| `cloudflare/proof/worker.miniflare-test.mjs` | `87f7367211467f773ca61b1a9f7fa024348f49b0` |
| `cloudflare/wrangler.jsonc` | `b25de82ed9e82d294b92a336c89b3b45153738a0` |

### Implemented in the synthetic proof source

The current source is materially ahead of the earlier Batch 89–93 source-audit snapshot:

- Application-level SQLite schema migrations are at version 3. Tables include `series_state`, `series_events`, `consumer_receipts`, and immutable `series_identity`.
- `commitCanonicalEvent` persists the canonical event payload/digest and advances series high-water in one `transactionSync` transaction. The emit path awaits commit before socket fan-out.
- `readDurableReplayPage` reads cursor-exclusive contiguous events and enforces 100-event and 65,536-byte response limits. Subscription replay is capped at 10 pages.
- WebSocket subscribe/replay is serialized against event commit/fan-out through the Durable Object protocol queue.
- A durable receipt write primitive `commitConsumerReceipt` exists, and the proof-only HTTP path can invoke it.

Accordingly, the source status must not continue to say that the event log/replay/receipt schema is entirely absent. Batch 90 schema and substantial Batch 92 event/replay code now exist in the inspected synthetic proof. This is source implementation evidence, not production acceptance.

### Remaining protocol and safety gaps

- The only exposed ACK route is `/__proof/ack`, protected by the shared synthetic proof bearer token. Its `consumerId` is accepted from the request body; it is not derived from a verified Firebase principal.
- The WebSocket message handler implements subscribe/replay but has no ACK message branch. ACK is not yet part of the authenticated production WebSocket protocol.
- `commitConsumerReceipt` has no direct named test coverage in the inspected Node or Durable Object test files. The Durable Object runtime tests verify receipt-table schema, but schema presence is not behavioral ACK acceptance.
- `compactDurableEvents` deletes rows through a supplied sequence and advances the retention floor atomically, but the inspected function does not enforce a floor bounded by the minimum durable receipt of all required consumers. No direct named compaction test was found. Keep destructive retention disabled for production.
- The Worker remains explicitly `PROOF_MODE=synthetic-only`; the Wrangler config retains `workers_dev: false` and `preview_urls: false`. The proof uses a synthetic subject and synthetic market data. It is not a Firebase-authenticated live market-data service.
- The connected Cloudflare account inventory above has no deployed Durable Object namespace for this proof Worker. The separately deployed `dezzta-chart-runner-relay` is a preflight dispatcher, not this WebSocket service.

### CI evidence for the documentation PR's tested base

PR #11 head commit `cb67a6fe30a3a9faadb053b4ed3c9d73f5ee72a1` was tested against the inspected base above:

- Automated Tests run [45942073009](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45942073009): terminal **SUCCESS**, 41/41 workflow steps, no failed steps.
- CodeQL run [45942072797](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45942072797): terminal **SUCCESS**, Python and JavaScript/TypeScript analyses completed.

These runs validate the checked-out PR merge context and its configured CI suites. They do not add missing ACK/compaction behavioral tests, do not prove Firebase identity binding, and do not constitute public WSS or Android E2E acceptance.

**Disposition:** Batch 90 — source schema implemented in synthetic proof, production migration/deployment unaccepted. Batch 92 — durable synthetic event commit/replay implemented, production provider/runtime integration unaccepted. Batch 93 — receipt storage primitive and proof-only HTTP ACK path exist; authenticated consumer binding, WebSocket ACK, bounded retention-by-receipt, behavioral coverage and production recovery remain YELLOW / OPEN. Stage 1 and Gate 10 accounting are unchanged.

---

## Batch 94 execution checkpoint — 27 November 2026

**Answer: Batch 94 has started. It is in progress, not complete.** Two parallel PR workstreams are open against `phase-2/market-data-foundation` (`4979bd4a69dfd37b4571a125790150931c4154ee`):

1. **PR #7 — durable replay after Durable Object eviction:** branch `work/batch94-gate-batch93-eviction-test`, head `0b44fb4474071ea2e26d39deddddebcf1083e289`. Adds an integration test that emits sequence 51, evicts/reconstructs the Durable Object, inspects persisted high-water/event payload/digest, then authenticates a new socket and checks replay-started, event update, and replay-complete. Automated Tests run [45928293821](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45928293821) — **SUCCESS**. CodeQL [45928293846](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45928293846), secret audit [45928293783](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45928293783), and OCI ARM64 readiness [45928293763](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45928293763) — all **SUCCESS**. PR remains open and mergeable.

2. **PR #10 — zero-cost provider eligibility gate:** branch `audit/batch94-zero-cost-provider-gate`, head `4ebeb0a147d1cf474ef8a2ec9a2578a53326897d`. Records the provider acceptance criteria and official-source screening for Coinbase, Kraken, Binance Spot streams, and Binance Vision datasets. Automated Tests [45939059711](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939059711), CodeQL [45939060366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939060366), secret audit [45939059764](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939059764), and OCI ARM64 readiness [45939059713](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939059713) — all **SUCCESS**. PR remains open and mergeable.

### Batch 94 acceptance position

- Replay-after-eviction has a passing automated integration test in PR #7; this is synthetic Durable Object runtime evidence, not public WSS or production Firebase/provider acceptance.
- Provider eligibility remains **YELLOW**: no candidate is approved for the exact multi-user DEZZTA CHART display/redistribution scope and zero-cost requirements.
- PR #7 and PR #10 are separate, unmerged branches. Do not describe either as integrated into the foundation branch until merge evidence exists.
- No changes to `main`; no provider secrets, paid trials, deployments, or Cloudflare resources were created.
- Latest audit found no in-progress Actions in either `dezzta-chart` or `dezzta-chart-runner`.

**Batch 94 overall: IN PROGRESS / YELLOW.** Next engineering sequence: preserve PR #7 eviction proof, then add behavioral receipt/ACK/compaction invariants; keep provider selection gated until authoritative terms and free-tier limits satisfy every acceptance criterion. The 24 December 2026 target remains unchanged.


---

## Live continuation audit — 27 November 2026 (session update)

This update records the live GitHub state after the prior Batch 94 checkpoint. It supersedes earlier head-SHA and CI snapshots where they differ. No merge, main-branch write, Cloudflare mutation, provider credential access, paid subscription, or recurring automation was performed.

### Pull-request state and CI evidence

| Workstream | Current branch / PR | Current head | State | Latest head-associated CI |
|---|---|---|---|---|
| Durable Object eviction/replay proof | `work/batch94-gate-batch93-eviction-test`, [PR #7](https://github.com/deszztagd377-pixel/dezzta-chart/pull/7) | `80ca695e68badf87b084ce08f01878c604ac02a4` | OPEN, mergeable, not merged | Automated Tests [45944090033](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45944090033), CodeQL [45944090027](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45944090027), Secret Audit [45944090069](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45944090069), OCI ARM64 [45944089968](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45944089968): all COMPLETED / SUCCESS |
| Zero-cost provider eligibility gate | `audit/batch94-zero-cost-provider-gate`, [PR #10](https://github.com/deszztagd377-pixel/dezzta-chart/pull/10) | `4ebeb0a147d1cf474ef8a2ec9a2578a53326897d` | OPEN, mergeable, not merged | Automated Tests [45939059711](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939059711), CodeQL [45939060366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939060366), Secret Audit [45939059764](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939059764), OCI ARM64 [45939059713](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45939059713): all COMPLETED / SUCCESS |
| Cloudflare runner inventory / project audit | `audit/batch95-cloudflare-runner-inventory`, [PR #11](https://github.com/deszztagd377-pixel/dezzta-chart/pull/11) | `aedc14c3d5d897254be782156cd2bd7b96948a8b` | OPEN, mergeable, not merged | No workflow run associated with this documentation-only head; its preceding tested base is documented separately above |

All three PRs target `phase-2/market-data-foundation`. None is merged. The current branch head for PR #7 has advanced from the earlier recorded SHA; the four checks above are the runs associated with the current head, not merely the historical prior attempt.

### Verified work state

- Batch 94 is active and has a passing synthetic Durable Object eviction/replay integration test on the current PR #7 head.
- PR #10's provider screen is an eligibility gate, not approval to connect a provider. Provider selection remains blocked until terms explicitly permit the intended real-time display, redistribution/multi-user use, storage/replay, and zero-cost operating envelope.
- The source-level receipt write primitive exists, but verified Firebase-principal-to-consumer binding, WebSocket ACK handling, receipt behavioral tests, and receipt-bounded compaction are still not accepted.
- The Cloudflare runner relay remains a preflight dispatcher, not an AI coding agent, market-data gateway, or production WSS endpoint. The account billing entitlement and public endpoint health remain unverified as described in the preceding addenda.
- No production WSS + Firebase auth + Android lifecycle E2E evidence has been established.
- Stage 1 / Gate 10 closure, overall project percentage, and zero-cost certification must not be promoted based solely on successful synthetic CI.

### Next engineering stage — ordered execution plan

**Batch 94 closeout (next immediate work):**
1. Inspect the current PR #7 diff and test fixture to confirm eviction test assertions cover durable event payload, digest, high-water, replay ordering, and reconnect behavior without relying on in-memory state.
2. Add direct behavioral tests for receipt persistence: valid receipt, duplicate/idempotent receipt, stale cursor, wrong series/consumer, malformed digest, and storage failure. Tests must assert durable state, not merely table schema.
3. Add authenticated ACK protocol design and tests. The consumer identity must be derived from a verified Firebase principal/server-side mapping, never trusted from a client-supplied `consumerId`.
4. Add compaction safety tests proving the retention floor cannot advance beyond the minimum accepted durable high-water of every required consumer. Until this invariant is implemented and tested, keep destructive event deletion/trim disabled.
5. Re-run the complete relevant CI matrix on the resulting feature branch and wait for terminal outcomes. Do not call a commit tested if no workflow run exists for that exact head.

**Batch 95 — production identity and WSS contract (after Batch 94 invariants pass):**
6. Define the end-to-end identity contract: Firebase ID-token verification, issuer/audience/project checks, expiry/revocation policy, entitlement authorization, server-derived consumer/gateway identity, one-time ticket issuance, short expiry, single use, and revocation.
7. Define the production WSS protocol: subscribe, snapshot watermark, replay cursor, ordered updates, ACK, reconnect/resume, backpressure, heartbeat, close/error codes, schema versioning, and bounded message sizes.
8. Define the durable recovery model: event commit-before-fan-out, replay after object eviction/restart, receipt ledger, owner/gateway fencing, idempotency, and safe retention floor. Preserve the rule that Redis XACK is not the owner-accepted high-water ACK.
9. Select Cloudflare-native versus Cloudflare Tunnel/origin architecture only after the actual zero-cost hosting/account constraints and an always-on origin (if Route B) are evidenced. No deployment is implied by this design work.

**Batch 96 — provider and end-to-end acceptance (only after contracts are approved):**
10. Complete legal/technical provider review for the exact product scope; validate rate limits, symbol coverage, historical/replay rights, attribution, caching/storage, redistribution, and service continuity. No provider passes by assumption.
11. Implement one narrow provider adapter behind a normalized canonical market-data contract, with deterministic fixtures and explicit provenance; do not mix synthetic data with live-provider truth.
12. Test the full chain: provider -> canonical validation -> durable event log -> WSS fan-out -> authenticated Android client -> reconnect/replay -> durable ACK -> safe compaction.
13. Complete browser and Android E2E under real TLS/WSS, network interruption, token expiry, app background/foreground, process death, duplicate/out-of-order events, and Durable Object eviction.

**Stage 1 acceptance and stage transition:**
14. Close the remaining Stage 1 security/data-integrity acceptance items and Gate 10 with evidence. Only then score Stage 1 as closed and authorize the next formal stage. Indicator UI/Footprint/Heatmap work remains gated by its existing Stage 4 blueprint and review constraints.

### Schedule and capacity

The target date remains 24 December 2026. From 27 November to 24 December there are 27 calendar days. This is a constrained delivery window: prioritize a minimal, secure WSS vertical slice and defer nonessential indicator/UI scope rather than weaken identity, receipt, retention, provider-rights, or recovery gates. ZERO COST remains a hard constraint; any required paid entitlement or provider license is a blocker requiring redesign, not an assumed exception.

### Session controls

- `main` untouched; no PR merged.
- No Cloudflare resources, secrets, billing settings, domains, deployments, or schedules changed.
- No recurring 10-minute job created or re-enabled.
- PR #7 and #10 current-head CI checks are terminal SUCCESS. PR #11 latest documentation-only commit has no CI run; do not label that exact commit CI-tested.
- Batch 94 overall remains **IN PROGRESS / YELLOW**. Production WSS, Firebase identity binding, provider eligibility, zero-cost certification, Android E2E, and Stage 1 closure remain **YELLOW / NOT ACCEPTED**.


---

## Correction and continuation — PR #7 / PR #12 consumer retention work (27 November 2026)

This addendum supersedes the earlier Batch 93 statement that no direct behavioral receipt/compaction tests existed on the current Batch 94 candidate. That statement described the foundation baseline before PR #7; it is not accurate for the PR #7 head.

### PR #7 candidate now contains

- Durable Object eviction/reconstruction integration test proving the committed event payload, digest and high-water survive eviction and are replayed to a newly authenticated synthetic socket.
- Workerd/Miniflare behavioral ACK tests for first receipt, duplicate/idempotent ACK, ACK regression rejection, and digest mismatch rejection.
- Receipt-aware compaction guard against already-observed lagging receipts, with an integration test that blocks compaction at 52 while a consumer has ACKed only 51, then permits compaction through 51.
- Current PR #7 head: `80ca695e68badf87b084ce08f01878c604ac02a4`; all four current-head checks were terminal SUCCESS as recorded above.

**Important limitation in PR #7:** the compaction query considers receipts already present, but there is no authoritative required-consumer registry. A connected/required consumer that has not yet written its first receipt is invisible to that query. The source comment itself notes that a production active-consumer registry is still required. Therefore PR #7 alone does not prove safe compaction for every required consumer.

### PR #12 — required-consumer registry candidate

A new feature branch was created from the exact PR #7 head and opened as [PR #12](https://github.com/deszztagd377-pixel/dezzta-chart/pull/12).

- Branch: `work/batch94-required-consumer-registry`
- Head: `a0d1d4b01c238a1e643f36cf0b939ada067863f3`
- Adds SQLite schema migration v4 and a required-consumer registry.
- Adds a synthetic proof registration route; receipt writes require an active registered consumer.
- Compaction fails closed if the registry is empty or any active required consumer has no receipt / has a cursor below the proposed floor.
- Extends the real workerd/Miniflare integration test for empty registry, missing receipt, and lagging ACK.
- Deregistration is intentionally omitted pending a reviewed consumer lifecycle/ownership policy.

PR #12 was opened against `phase-2/market-data-foundation`; it is not merged. At the time of this note its checks are still running. It must remain YELLOW until Automated Tests, CodeQL, Secret Audit and OCI ARM64 checks all reach terminal SUCCESS. Any failure must be investigated and fixed on the feature branch, then CI rerun to terminal state.

### Corrected next-step dependency order

1. Complete PR #12 CI and review its schema migration/registry behavior. Fix any failing checks before proceeding.
2. Add explicit lifecycle policy for required-consumer registration, expiry, ownership/fencing and safe deregistration; the current synthetic registry deliberately retains registrations indefinitely.
3. Bind registration and ACK identity to verified Firebase principals/server-side gateway identities. Client-supplied consumer IDs remain untrusted.
4. Implement WebSocket ACK message handling and end-to-end authenticated ACK tests; current ACK is still a proof-only HTTP route.
5. Validate compaction under restart/eviction, concurrent ACK/compaction, generation rollover, and multiple required consumers.
6. Only then design production WSS deployment and Android/browser E2E against a legally approved provider.

**Status correction:** receipt behavioral tests and an observed-receipt compaction guard exist on PR #7. A required-consumer registry and fail-closed handling for missing receipts are proposed on PR #12 and are not yet CI-accepted. Firebase identity, production WebSocket ACK, consumer lifecycle, provider approval, public WSS and Android E2E remain YELLOW.


---

## CI closeout — Batch 94 required-consumer registry candidate (27 November 2026)

### PR #12 current head and final checks

PR #12 current head is `83a4582dd76a6ca712ae4cb18ee77b0dbb5f7d86`. All four current-head workflows reached terminal **SUCCESS**:

- [Automated Tests — run 45979657207](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979657207): SUCCESS. This includes Worker syntax/proof tests, pinned workerd/Miniflare, Durable Object hibernation/alarm/isolation tests, frontend tests/build, backend tests, Redis TLS integration, synthetic benchmarks, backend image build/smoke test, and image scan.
- [CodeQL — run 45979657185](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979657185): SUCCESS.
- [Full Git History Secret Audit — run 45979657177](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979657177): SUCCESS.
- [OCI ARM64 Image Readiness — run 45979657275](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979657275): SUCCESS.

The first attempt at PR #12 (head `a0d1d4b01c238a1e643f36cf0b939ada067863f3`) failed two Durable Object migration fixture assertions. The fixture had retained migration version 4 while simulating a v2 database and still expected schema v3. The fix updates the fixture to remove migration records >=3, expects schema v4, and includes the required-consumer table in schema assertions. The rerun on head `83a4582...` passed all four workflows. The failed attempt remains part of the audit history; it is not hidden.

### PR #11 documentation CI

The latest documentation head `6e15fc634deed2b96aa72d4c819a9f8681d3e99c` also has all four checks terminal SUCCESS:

- [Automated Tests — run 45979522475](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979522475): SUCCESS.
- [CodeQL — run 45979522468](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979522468): SUCCESS.
- [Full Git History Secret Audit — run 45979522469](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979522469): SUCCESS.
- [OCI ARM64 Image Readiness — run 45979522460](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45979522460): SUCCESS.

### Repository state at closeout

- PR #7, #10, #11 and #12 are all OPEN, mergeable, and unmerged; all target `phase-2/market-data-foundation`.
- PR #12 is a feature candidate branched from PR #7 head. Its passing checks do not merge either candidate into the foundation branch.
- No in-progress or queued GitHub Actions runs remained in either `dezzta-chart` or `dezzta-chart-runner` at the closeout audit.
- `main` remains untouched. No Cloudflare deployment/resource, provider credential, paid service, or recurring 10-minute automation was created or changed.

### Acceptance boundary

PR #12 improves the synthetic proof's required-consumer retention safety. It does not complete production consumer lifecycle, Firebase principal binding, WebSocket ACK, provider legal approval, public WSS deployment, or Android/browser E2E. Those remain YELLOW / NOT ACCEPTED. Batch 94 is therefore still **IN PROGRESS / YELLOW**, despite the candidate CI passing.
