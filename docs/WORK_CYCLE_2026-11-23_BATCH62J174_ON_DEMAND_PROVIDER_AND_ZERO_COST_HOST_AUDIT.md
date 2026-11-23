# DEZZTA CHART — Batch 62J-174
## Latest-head WebSocket, provider-demand, and zero-cost host alignment audit

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Documentation parent HEAD:** `17b5db699da4e1e1b3b17b1e8fe6d0f48cd4b8d2`  
**Latest fully CI-verified code/test HEAD:** `a9d001885b0b524bc33427add30584e1984680bf`  
**Scope:** Stage 2 on-demand provider-demand gap, Stage 1/ Gate 25/36 host and transport boundary, ZERO COST  
**Protected branch:** `main` untouched

## 1. Exact checkpoint reconciliation

The previously remembered checkpoint `1eff552c68487e7411ac423f289c07a4856d2074` is stale. The active branch has advanced by 230 commits beyond that checkpoint. The latest branch HEAD at audit time is `17b5db699da4e1e1b3b17b1e8fe6d0f48cd4b8d2`.

The branch HEAD is one documentation-only commit ahead of the latest fully CI-verified code/test commit `a9d001885b0b524bc33427add30584e1984680bf`. That final code/test commit is the corrected Batch 62J-172 relay parser implementation. The documentation-only branch-head commit reconciles the indicator ledger, current project dashboard, and Batch 62J-172 CI report; it does not modify runtime or test source.

Exact-code-head workflow evidence was independently re-read:
- Automated Tests run [45162694296](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694296): SUCCESS. 1,347 backend tests passed, 1 skipped, 6 warnings; 306 frontend tests passed. Redis TLS fixture, outbox/metrics benchmarks, backend container build/smoke, dependency audit and image scan completed.
- CodeQL run [45162694141](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694141): SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit run [45162694099](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694099): SUCCESS.
- OCI ARM64 Image Readiness run [45162694385](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45162694385): SUCCESS; native ARM64 image build and unprivileged/persistent-volume smoke passed.

All four run job summaries were checked and completed successfully. This is CI/build evidence only. It is not an OCI deployment, a public hostname, a production WSS endpoint, or an owner-host acceptance result. The documentation-only branch HEAD must not be represented as a newly tested source commit.

## 2. Client-side on-demand status — implemented locally

Source audit of `CandlestickChart.tsx`, `ohlcvSeriesSupervisorRegistry.ts`, `ohlcvStreamSupervisor.ts`, `marketDataSeriesStore.ts`, and `ohlcvWebSocketClient.ts) confirms:

1. A chart derives a canonical series identity from dataset, publisher, instrument, raw symbol, timeframe and bucket policy.
2. Each chart panel obtains an owner lease through `OhlcvSeriesSupervisorRegistry.acquire()`.
3. Equivalent visible chart panels share one authenticated supervisor for the same canonical series. Owner count is reference-counted.
4. Releasing one panel does not close a shared supervisor while another owner remains. Releasing the last owner removes the registry entry and stops the supervisor.
5. Each active series writes into the keyed series store, isolating different chart identities.
6. The chart lifecycle pauses when hidden, offline, or page-hidden and resumes with a fresh authenticated supervisor and snapshot.
7. The WebSocket transport uses a short-lived ticket, exact-series subscription, snapshot/replay cursor, sequence validation, heartbeat, ticket renewal and reconnect recovery.

The client-side owner/ref-count boundary is real repository implementation, not merely a design proposal. Existing registry and lifecycle tests are the local evidence. It does not prove provider-side demand control.

## 3. Backend on-demand gap — still OPEN

The backend source audit confirms a material remaining gap:

- `main.py` starts `ProviderManager.start()` from application lifespan when the normal source role is selected. Provider startup is process/configuration scoped, not driven by active chart subscriber count.
- `OhlcvStreamHub` creates isolated per-client subscriptions and bounded queues, then fans accepted events to matching exact-series subscribers. This is downstream fan-out, not upstream provider pooling.
- `DatabentoLiveSource` accepts a fixed constructor-supplied symbol tuple and calls `client.subscribe(... symbols=list(self._symbols) ...)` once at source start. The repository adapter exposes `stop()`, but no verified dynamic add/remove-symbol contract.
- The Databento SDK API surface is explicitly marked unverified in source. Existing fake-SDK tests do not prove live SDK compatibility.
- The existing Databento dependency is a version range, not an exact reproducible pin.
- Databento is not an accepted recurring-zero-cost source for the current CME target. Finite credits or a paid entitlement cannot be treated as a permanent ZERO COST feed.

Therefore the complete product requirement is not finished. Client-side reference counting cannot by itself stop or reconcile a fixed upstream feed.

### Required provider-demand implementation boundary

Before wiring a coordinator into production, the provider adapter must expose a verified capability contract with exactly one declared behavior per adapter:
- dynamic subscribe/unsubscribe supported and tested;
- multiplexed stream supported with explicit filtering and routing;
- symbol-set changes require a bounded source restart/reconcile; or
- dynamic demand unsupported.

The coordinator must then:
- key demand by the provider's true upstream identity, not only the display symbol;
- use idempotent acquire/release leases and safe duplicate-owner handling;
- start upstream demand on the first eligible authorized subscriber;
- stop or reconcile only after the last subscriber for that upstream identity releases;
- preserve other users' and other series' sessions when one client disconnects;
- reconcile desired demand after provider reconnect/restart and entitlement revocation;
- preserve snapshot/watermark, durable replay, cursor monotonicity, sequence continuity and resnapshot recovery;
- prove that unopened/inactive pairs cause zero provider subscriptions and zero periodic market-data polling.

No runtime provider-demand coordinator is claimed in this batch. The existing accepted on-demand ADR remains binding; Stage 2 remains not officially opened/scored. A generic coordinator without a verified provider capability and an eligible recurring-$0 data source would create false progress.

## 4. Hosting alignment — accepted direction versus repository reality

The latest owner-approved hosting direction carried forward for this project is:
- Primary candidate: Cloudflare Workers + Durable Objects.
- Fallback candidate: Render Free.
- Neither is a guarantee of permanent free service. No paid plan, payment card, billing activation, deployment, or account change is authorized.

The repository backend is currently FastAPI/Python with SQLite and Redis assumptions. It is not a drop-in Cloudflare Worker/DO deployment. A migration requires a scoped, reviewed compatibility blueprint; do not add Cloudflare configuration or replace backend runtime code as part of this audit.

### Cloudflare Free constraints verified from current official documentation

- Workers Free currently lists 100,000 requests/day and 10 ms CPU time per invocation.
- Durable Objects are available on Workers Free, but the Free plan supports SQLite-backed Durable Objects only.
- Durable Objects Free currently lists 100,000 requests/day and 13,000 GB-s/day. Its request accounting includes HTTP requests, RPC sessions, WebSocket messages and alarms; incoming WebSocket messages use a 20:1 ratio for billing-only request accounting.
- SQLite-backed Durable Objects Free currently lists 5 million row reads/day, 100,000 row writes/day and 5 GB total stored data.
- The Hibernation WebSocket API keeps inbound client WebSockets connected while an eligible DO hibernates. In-memory state is lost across hibernation and must be restored from durable storage or serialized socket attachments.
- Outgoing WebSockets do not use the hibernation API. A DO holding an outbound provider socket cannot be assumed to hibernate like an inbound client WebSocket.

Capacity implication: even a single continuously updated 1-second series has 86,400 one-second intervals per day before counting revisions, metadata, outbox rows, reconnects or multiple series. This is already close to the 100,000-row/day write allowance. This is an interval-count illustration, not a measured workload or a claim that the current backend writes exactly one row per interval. Actual write amplification and quota scope must be measured before selecting a storage topology.

Official references:
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/

### Render Free fallback constraints verified from current official documentation

- Free web services receive 750 free instance hours per workspace per calendar month.
- A Free service spins down after 15 minutes without inbound HTTP traffic or WebSocket messages; a later request or new socket can take about one minute to recover.
- Free service local files are ephemeral. SQLite files are lost on restart, redeploy or spin-down.
- Free Render Postgres is limited to 1 GB and expires 30 days after creation.
- Free services cannot attach persistent disks or scale beyond one instance.

Consequently, Render Free can be evaluated as a temporary/stateless or synthetic-test fallback, but it cannot host the current durable SQLite/outbox design unchanged. It must not be presented as production persistence or permanent uptime.

Official reference:
- https://render.com/docs/free

## 5. Safe migration blueprint required before runtime changes

A separately reviewed blueprint must resolve these contracts before a Cloudflare/Render implementation begins:

1. **Worker boundary:** HTTP API routes, WebSocket upgrade routing, CORS/Origin policy, rate limiting, health/status semantics and secret boundaries.
2. **Identity:** Firebase ID-token verification over HTTPS, revocation/issuer/audience handling, purpose-bound single-use WSS tickets, expiry, renewal and account-subject binding. No Firebase token in a WebSocket URL or frame.
3. **Durable Objects:** shard by a deterministic canonical-series or bounded partition key; avoid a single global DO. Define owner/ref-count state, hibernation-safe restoration, connection limits, slow-consumer handling and clean last-owner release.
4. **Storage:** select DO SQLite or D1 only after measuring row-read/write amplification, retention, exact-decimal storage, nanosecond timestamps, atomic outbox/cursor updates, snapshot restore and export. Do not assume the current Python SQLite schema can be copied unchanged.
5. **Provider adapter:** verify a recurring-$0, correctly licensed data source for the exact target instrument universe and prove its actual subscribe/unsubscribe/multiplexing semantics. If no source qualifies, retain explicit unavailable/demo behavior.
6. **Replay and trust:** preserve source identity, snapshot generation, digest, installation receipt, cursor, retention floor, checkpoint fencing and cross-host key lifecycle. A digest alone is not an authenticated immutable receipt.
7. **Client compatibility:** retain the current protocol contract or document a versioned migration; prove foreground/background, network handover, ticket renewal, snapshot/replay and Android WebView recovery.
8. **Quota guard:** model expected active users, open series, messages per second, snapshot sizes, reconnect bursts, storage rows/day and compute duration/day. Configure hard no-billing limits and fail closed before any paid overage.
9. **Fallback:** document exactly which capabilities Render Free can and cannot provide; never use its ephemeral filesystem as the authoritative OHLCV/outbox store.
10. **Rollback:** keep the current FastAPI source and protocol as the reference baseline until the isolated Worker/DO proof passes; no production cutover before parity and recovery acceptance.

No service account, production key, payment method, market-data entitlement, public endpoint, deployment, domain, or device operation was used in this batch.

## 6. Gate and indicator reconciliation

| Area | Current status | Evidence boundary |
|---|---|---|
| Client on-demand owner leases | 🟨 Implemented locally | Exact-series registry and tests; not upstream provider demand |
| Backend per-client WebSocket fan-out | 🟨 Implemented locally | Per-client queue/stream isolation and tests |
| Provider-side on-demand/ref-count | 🟥 OPEN | Fixed symbol tuple and process-scoped provider startup remain |
| Public HTTPS/WSS and Firebase E2E | 🟥 OPEN | No accepted public host/client round-trip |
| Gate 25 snapshot receipt/key lifecycle | 🟧 OPEN | Local checkpoint/relay validation improved; authenticated cross-host receipt custody remains |
| Gate 36 public WSS/device acceptance | 🟥 OPEN | Public hostname, TLS/proxy, live Firebase and Android WebView/network tests absent |
| Gate 38 operations/metrics | 🟧 OPEN | Local metrics input contract improved; owner-host persistence/backup/retention/alerts/recovery absent |
| Gate 39 incident response | 🟥 OPEN | External acknowledgement and operator recovery evidence absent |

No indicator source, formula, calculation test, hook, chart binding, renderer, pane, settings or indicator-specific test changed. Indicator implementation credit is zero.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation, lifecycle, render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot and aligned multi-study calculation output | Hook tests, actual chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth | User visual reference(s), reviewed blueprint, verified bid/ask source, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User visual reference(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance and calculation contract, reviewed blueprint, renderer and tests |

Preserve warm-up nulls, exact source-index alignment, prefix causality/no future-candle repaint, invalid/gapped-data rejection, stale-output clearing on identity changes, and standard candle spacing while Footprint is OFF. Footprint and Heatmap visual implementation remains blocked until the owner supplies reference images and reviews the scoped blueprint.

## 7. Project indicators — no speculative completion credit

- Stage 1 Foundation, Security & Data Integrity: **30/40 = 75% provisional** 🟨.
- Stage 2 Market Data Infrastructure: **NOT SCORED / not officially opened** ⬜.
- Stage 3 Chart Engine & Timeframe: **NOT SCORED / not officially opened** ⬜.
- Stage 4 Indicators & Analytics: **NOT SCORED / not officially opened** ⬜.
- Stage 5 Professional UI & Interactive Tools: **NOT SCORED / not officially opened** ⬜.
- Stage 6 Hardening, Validation & APK Release: **NOT SCORED / not officially opened** ⬜.
- Gate 10: **0/10 external acceptance criteria formally closed** 🟥.
- Overall project: **NOT SCORED**. Historical 20.9% is not a fresh weighted calculation; approved stage weights and denominator remain unavailable.
- Significant engineering delta: strict replica-relay wire-format validation passed exact-head CI. It is not a public WebSocket or provider-demand completion claim.
- ZERO COST preserved. Target date remains **24 December 2026**, not a guaranteed completion date.

## 8. Next work cycle — ordered, no stage skipping

1. Complete the scoped Worker/DO migration and storage/quota blueprint from this audit; keep the existing FastAPI backend unchanged during the design review.
2. Build an isolated synthetic-only Worker + Durable Object proof after the blueprint is reviewed. No provider credentials, production user tokens, market data or billing activation.
3. Test inbound WebSocket hibernation, auth-ticket exchange, exact-series ownership/ref-count, idle close, reconnect, replay, quota exhaustion and restart recovery.
4. Separately define and test a provider capability contract. Do not wire dynamic subscribe/unsubscribe to the Databento adapter until its real SDK semantics and recurring cost are acceptable.
5. Reconcile CI and security workflows on the exact resulting source/test SHA before awarding implementation or acceptance credit.
6. Keep public WSS, Gate 25/36 and all owner-host claims open until real external evidence exists.

**Batch 62J-174 result:** repository/source audit and zero-cost host/provider blocker clarification completed; no runtime code, tests, manifests, credentials, deployment, paid service or `main` changes. This batch awards no Stage 1/Stage 2 acceptance ticks and no indicator implementation credit.
