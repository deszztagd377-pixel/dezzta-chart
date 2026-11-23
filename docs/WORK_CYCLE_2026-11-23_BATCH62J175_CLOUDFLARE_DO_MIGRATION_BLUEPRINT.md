# DEZZTA CHART — Batch 62J-175
## Cloudflare Workers + Durable Objects migration blueprint (review gate)

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base HEAD:** `29aa6335a7efa74d9b98000ee863c96086dc05d8`  
**Related audit:** `docs/WORK_CYCLE_2026-11-23_BATCH62J174_ON_DEMAND_PROVIDER_AND_ZERO_COST_HOST_AUDIT.md`  
**Status:** DESIGN BLUEPRINT — owner review required before runtime implementation  
**Scope:** Stage 2 WebSocket hosting migration; ZERO COST  
**Protected branch:** `main` untouched

## 1. Purpose and decision reconciliation

The earlier `docs/ZERO_COST_BACKEND_LONGEVITY_BLUEPRINT.md` was authored against baseline `1eff552c68487e7411ac423f289c07a4856d2074`, is explicitly marked OWNER REVIEW REQUIRED, and says not to use Vercel or Cloudflare as the proposed host. That statement is a historical proposal constraint, not a verified implementation decision.

The later owner-directed hosting choice carried forward for DEZZTA CHART is:
- Primary candidate: Cloudflare Workers + Durable Objects.
- Fallback candidate: Render Free.
- Both remain subject to current quotas and terms. Neither is promised to stay free forever.
- No payment method, billing activation, account provisioning, deployment, domain, production credential, or provider entitlement is authorized by this blueprint.

This addendum supersedes the earlier host-selection prohibition only for architecture evaluation. It does not supersede the earlier hard constraints on zero cost, portable data, tested restore, least-privilege security, fail-closed behavior, no secrets in the client, and no production claim without evidence.

## 2. Existing FastAPI contract to preserve

The current backend is not a small single-route WebSocket service. `backend/app/main.py` currently exposes:

| Existing route | Current responsibility | Migration priority |
|---|---|---|
| `GET /health` | Secret-free process liveness | POC |
| `GET /v1/auth/session` | Verified Firebase principal/session | POC |
| `POST /v1/auth/websocket-ticket` | Purpose-bound, single-use, 90-second WSS ticket | POC |
| `GET /v1/market-data/status` | Provider and feed readiness status | POC |
| `GET /v1/ohlcv` | Exact-series snapshot after identity and entitlement checks | POC |
| `GET /v1/instruments` | Instrument catalogue and canonical provider mapping | POC |
| `/ws/market-data` | Ticket auth, exact-series subscribe, snapshot/replay/live events, sequence validation, heartbeat and renewal | POC |
| `POST /v1/alerts/devices` | Encrypted FCM device registration | Deferred |
| `DELETE /v1/alerts/devices/{installation_id}` | Account-owned device revocation | Deferred |
| `GET /internal/metrics` | Operator-token protected metrics | Deferred; never public |
| `GET /internal/alert-delivery` | Operator-token protected alert worker status | Deferred; never public |
| `GET /internal/incidents` | Operator incident listing | Deferred; never public |
| `POST /internal/incidents/{incident_id}/acknowledge` | Incident acknowledgement | Deferred; never public |
| `POST /internal/incidents/{incident_id}/resolve` | Incident resolution | Deferred; never public |

The current source also owns instrument registry, account entitlements, session-calendar releases, OHLCV persistence, replay outbox/cursors, snapshot/replica checkpoints, Redis TLS/ACL guards, metrics, alert delivery, incident records and encrypted device-token storage. A Worker/DO proof must not pretend these responsibilities disappear when the HTTP routes move.

## 3. Target architecture proposal

### 3.1 Stateless Worker — HTTP and edge boundary

Responsibilities:
- Serve static application assets only if the same Worker deployment is explicitly selected for frontend hosting.
- Validate request method, path, content type, request size, CORS and exact allowed Origin.
- Verify Firebase identity before issuing a session or WSS ticket.
- Route WebSocket upgrades to the correct Durable Object shard.
- Expose only the approved public API surface.
- Keep internal metrics and operator incident endpoints disabled or behind a separate operator-only boundary.
- Apply bounded request/connection admission controls before consuming DO resources.

The Worker must not contain provider secrets, service-account JSON, Redis credentials, backup keys, FCM server credentials or other privileged values in source or client-visible variables.

### 3.2 Durable Objects — session and series coordination

Do not use one global Durable Object for every user and series.

Proposed logical partitioning:
- An authentication/ticket authority owns atomic single-use ticket issue/consume and short-lived session admission. Its state must be bounded and expire safely.
- A series coordinator is deterministically selected from the canonical market-series identity or a reviewed bounded shard key.
- The series coordinator owns the set of authenticated downstream WebSocket connections for that series, per-client subscription state, reference counts, bounded queues, slow-consumer eviction and last-owner release.
- A separate bounded operator/metrics partition may be considered later; it is not part of the first proof.

A client disconnect removes only that client's ownership. It must never stop a different user's socket or another active series. Duplicate acquisition and stale React cleanup must remain idempotent.

### 3.3 Hibernation-safe WebSocket lifecycle

Use the Durable Objects Hibernation WebSocket API for inbound browser/Android WebSocket sessions. Do not use the ordinary pinned WebSocket API when hibernation is required.

Persist or serialize all state required after hibernation:
- verified account subject and ticket/session identifier;
- exact canonical series identity and entitlement version;
- subscription/owner lease generation;
- stream ID, snapshot generation, watermark and replay cursor;
- protocol version and bounded connection metadata.

In-memory maps are caches only. The constructor must rebuild state from durable storage and serialized attachments. Do not rely on a module-global map surviving hibernation or eviction.

The current app-level text heartbeat (`ping`/`pong`) must be reviewed against the DO hibernation API. Cloudflare's protocol-level ping/pong and `setWebSocketAutoResponse()` have different billing/wakeup behavior from application text messages. Preserve the existing protocol until a versioned, tested change is approved.

### 3.4 Provider connection boundary — unresolved by design

The current Python `DatabentoLiveSource` creates an outbound provider WebSocket, subscribes once to a fixed symbol tuple and runs a process-level supervisor. It is not a drop-in Durable Object implementation.

Cloudflare's Durable Object hibernation support is for inbound WebSocket server connections. Outbound WebSockets do not hibernate; a DO holding an outbound provider connection cannot be assumed to sleep while that source remains open. The first proof must therefore use synthetic, deterministic events only.

A future provider connector must be a separately selected component with:
- verified dynamic subscribe/unsubscribe or an explicitly bounded restart/reconcile contract;
- exact instrument coverage and provider licensing/display/redistribution rights;
- recurring-$0 eligibility;
- source identity, timestamp, sequence, and replay semantics;
- bounded reconnect and rate controls.

No provider connection is enabled by this blueprint. The existing Databento live source remains disabled for the recurring-zero-cost baseline.

## 4. Storage proposal and quota calculation

The current FastAPI backend relies on multiple SQLite stores and Redis. Cloudflare does not directly host that Python process. The Worker/DO port needs a deliberate storage design.

Candidate responsibilities:
- Durable Object SQLite: ticket/session state, per-series active owner leases, connection attachments, and small coordination metadata.
- D1 or partitioned Durable Object SQLite: canonical instrument/entitlement records, OHLCV bars, outbox/cursors, snapshots and operational records only after a measured schema/transaction review.
- Redis-specific shared guards must be replaced only by a reviewed atomic DO design; do not simply replace Redis with KV.
- Existing encrypted backup, key custody, receipt, checkpoint and restore semantics must remain explicit. A storage API migration is not a restore drill.

### Current documented Workers Free quotas

These are mutable vendor quotas, not a guarantee:
- Workers Free: 100,000 requests/day; 10 ms CPU time per invocation.
- Durable Objects Free: 100,000 requests/day and 13,000 GB-s/day; HTTP requests, RPC sessions, WebSocket messages and alarms count toward request usage. Incoming WebSocket messages have a 20:1 request-accounting ratio for billing.
- SQLite-backed Durable Objects Free: 5 million row reads/day, 100,000 row writes/day and 5 GB total stored data.
- Workers Free supports SQLite-backed Durable Objects; the key-value-backed DO storage option is not available on the Free plan.

### Minimum-write calculation

If a single exact series writes one finalized OHLCV bar per second for 24 hours:

`86,400 seconds/day × 1 bar/second = 86,400 bar-row writes/day`

Quota utilization before outbox, checkpoint, entitlement, index, metadata or revision writes:

`86,400 / 100,000 × 100 = 86.4%`

Two continuously active one-second series at the same one-row-per-second lower bound:

`2 × 86,400 = 172,800 writes/day`

`172,800 / 100,000 × 100 = 172.8%`

This is a conservative capacity warning, not a measured write count for the current backend. The actual write amplification must be measured from the current store and expected active-chart schedule. It shows why simply placing every bar and every event into one Free SQLite-backed DO is not an accepted design.

The first proof must measure:
- rows written per finalized bar and per in-progress bar revision;
- rows read per snapshot and replay page;
- bytes per snapshot, attachment and replay event;
- DO active duration while sockets are open;
- incoming WebSocket messages per connection per minute;
- reconnect bursts and daily active series;
- retained rows and cleanup writes.

Configure no-billing/hard usage limits. If an operation would exceed the accepted free quota, fail closed and show unavailable/degraded state rather than silently activate paid usage.

Official references:
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- https://developers.cloudflare.com/durable-objects/concepts/durable-object-lifecycle/

## 5. Render Free fallback boundary

Render Free can run Python/FastAPI and accept WebSockets, but its limitations make it a fallback for a synthetic/stateless proof, not an unchanged production home for the current persistence design:

- 750 free instance hours per workspace per calendar month.
- Spin-down after 15 minutes without inbound HTTP traffic or WebSocket messages.
- Approximately one minute to spin back up.
- Ephemeral local filesystem; SQLite files are lost on restart, redeploy or spin-down.
- No persistent disk on Free.
- Free Postgres is 1 GB and expires 30 days after creation.
- A service may restart at any time.

A Render fallback therefore needs an independently approved durable store and an adapter that keeps FastAPI stateless. Cloudflare DO storage is not directly a network-accessible database for a Render process; a Worker/DO proxy would itself be a new service boundary and must be designed/tested. Do not claim that adding Render Free alone solves backend persistence.

Official reference: https://render.com/docs/free

## 6. Phased implementation proposal

| Phase | Deliverable | Acceptance |
|---|---|---|
| A — contract freeze | Versioned HTTP/WSS contract, Firebase identity and one-time ticket threat model, canonical series identity, exact decimal/nanosecond wire schema | Contract tests and security review; no runtime migration |
| B — synthetic Worker | Worker with `/health`, session/ticket endpoints and synthetic-only status/snapshot routes | Local tests, strict CORS/Origin, bounded input, no production secrets |
| C — ticket DO | Atomic ticket issue/consume, 90-second expiry, purpose binding, subject binding, duplicate-consume rejection | Concurrent single-use tests, expiry tests, hibernation/restart tests |
| D — series DO | Exact-series WebSocket accept/subscribe, per-client ownership, reference counting, bounded fan-out and last-owner shutdown | 2+ clients, 2+ series, disconnect isolation, duplicate acquire/release, slow consumer, hibernation restoration |
| E — snapshot/replay | Persisted generation, watermark, cursor, digest and bounded replay | Snapshot-to-live race, gap detection, duplicate replay, restart recovery, forged digest rejection |
| F — persistence and quota | Measured DO SQLite/D1 schema and storage choice | Write/read/GB-s benchmarks and quota guard; no paid overage |
| G — provider capability | Fake adapter contract first; real adapter only after recurring-$0 lawful source approval | Dynamic capability, reconnect/reconcile, last-owner release and zero inactive-series traffic |
| H — Render fallback POC | Stateless FastAPI synthetic deployment only if an independently durable store and no-billing guard are verified | Cold start, WSS reconnect, persistence failure behavior, export/restore |
| I — migration decision | Compare current FastAPI behavior with Worker/DO proof | Parity report, rollback plan, explicit owner approval before cutover |

## 7. Security and compatibility non-negotiables

- Firebase ID tokens travel only over HTTPS; never put them in a WebSocket URL or frame.
- WSS receives a short-lived, purpose-bound, single-use ticket.
- Ticket renewal rechecks the same verified account subject and current entitlement.
- Client-supplied account IDs never select ownership.
- Exact Origin checks, CORS, input limits, per-account connection limits and slow-consumer controls remain fail-closed.
- Instrument identity includes provider, dataset, publisher, instrument, series type, timeframe, bucket policy and calendar identity where applicable.
- Prices/volume remain canonical decimal strings; nanosecond timestamps remain unsigned decimal strings.
- Preserve atomic snapshot/watermark installation, immutable receipt provenance, replay cursor monotonicity, sequence continuity and resnapshot behavior.
- Do not expose internal metrics or incident routes publicly.
- No secrets in source, APK, Vite variables, logs, artifacts or chat.
- No real user token, provider key, exchange data or production record in the synthetic proof.

## 8. Explicit exclusions

This blueprint does not authorize:
- Cloudflare account creation or configuration changes;
- Render service creation or account/billing changes;
- payment card entry, billing activation, paid plans or trial usage;
- domain purchase, DNS changes or public deployment;
- live provider access, market-data credentials or paid feeds;
- production user data, production Firebase credentials or production key transfer;
- replacing the existing FastAPI backend, Redis guards or SQLite stores;
- changes to `main`;
- indicator UI or formula work.

## 9. Review gate and next exact action

**Review required before implementation.** The owner must review the following architecture decisions as a single scope:
1. Accept Worker for HTTP/API boundary and Durable Objects for inbound WebSocket/session/series coordination.
2. Accept synthetic-only proof first; no real provider connection.
3. Keep the Python/FastAPI backend as the reference implementation until parity, storage and rollback tests pass.
4. Defer production persistence selection until the row-write calculation and schema/transaction audit are complete.
5. Treat Render Free only as a stateless/synthetic fallback unless durable external storage and no-billing safeguards are independently proven.
6. Keep the existing authentication, entitlement, receipt, replay and restore guarantees unchanged.

After review, implementation begins with Phase A/B only. No large rewrite, deployment or production cutover is part of the first implementation slice.

**Batch 62J-175 result:** scoped Cloudflare/DO and Render fallback migration blueprint prepared; no runtime code, tests, manifests, credentials, service accounts, deployments, paid services or `main` changes. No project-stage or indicator acceptance ticks awarded.
