
# WebSocket Multi-ASGI Integration Blueprint

Repository: deszztagd377-pixel/dezzta-chart
Branch: phase-2/market-data-foundation
Batch: 62J-19
Status: Design boundary documented; implementation requires owner review.
Cost policy: ZERO COST. No paid object storage, hosting, market-data provider, or deployment.

## 1. Objective

Prove that two independently started FastAPI/ASGI gateway processes serve the same OHLCV stream through one Redis Stream while maintaining independent durable SQLite replica databases. Each gateway must receive the same ordered event history and recover safely after process or Redis failure.

## 2. Verified current architecture

- Authoritative OHLCV events and outbox live in source SQLite.
- Publisher uses a durable SQLite checkpoint and fenced lease, then appends deterministic cursor IDs to Redis.
- Each gateway replica has a distinct Redis consumer group and SQLite replica store.
- Consumer commits to replica SQLite before callback and XACK.
- Callback dispatcher moves synchronous worker-thread callbacks onto the owning ASGI event loop.
- Replica bridge can hydrate a pipeline and register a snapshot watermark.
- Existing WebSocket handler in main.py is source-store/pipeline-backed.
- FastAPI lifespan currently does not own the Redis OHLCV worker.
- Snapshot installation currently expects a local snapshot artifact.

## 3. Required component boundaries

### 3.1 Snapshot bootstrap contract

A gateway may not construct its Redis consumer or accept replica-backed WebSocket subscriptions until it has installed and verified a snapshot. Required metadata:
- source identity;
- snapshot generation;
- source high-water cursor;
- retention floor;
- exact series/data contract version;
- manifest row count and SHA-256;
- successful atomic replica installation.

The same snapshot generation must initialize the consumer's generation-scoped group. A snapshot that cannot be proven to match the authoritative source must fail startup closed.

### 3.2 Snapshot transport decision — owner approval required

No production transport is selected yet:

| Candidate | Cost/operational profile | Limitation |
|---|---|---|
| Shared read-only filesystem artifact | Zero incremental service cost when gateways share an existing host/volume | Does not solve independent multi-host deployment unless storage is already shared and durable |
| Authenticated snapshot export endpoint | Can work across hosts using existing backend network | Requires source endpoint, authorization, bounded transfer, retry and artifact integrity design |
| Existing owner-controlled object storage | Potentially suitable for multi-host immutable artifacts | Must confirm genuinely free quota/plan; no paid service may be assumed |
| Redis-resident snapshot chunks | Avoids another service | Snapshot size, memory pressure, retention, atomic generation publication and ACL complexity make this a poor default |

Do not place large snapshots in Redis Streams. Do not assume a paid storage provider. Owner must select actual deployment topology and approve transport before implementation.

### 3.3 Replica-backed WebSocket adapter

The gateway must use one coherent read model:
- initial snapshot and checkpoint are read atomically from replica SQLite;
- hub subscription is registered against that same cursor boundary;
- replay is fetched from Redis only when needed and merged with live callback events using cursor fences;
- no mixing of source-store snapshot cursor with replica-store live cursor;
- stale generation, gap, trim, or failed merge returns sanitized resnapshot-required and closes/reconnects safely.

Existing source-backed behavior remains default until replica mode is explicitly enabled and passes acceptance tests.

### 3.4 FastAPI lifespan ownership

Each ASGI process owns:
- one Redis client configured with that instance's least-privilege credentials;
- one replica SQLite store at a unique path;
- one event-loop dispatcher bound to that process's running loop;
- one sequential consumer worker for that replica's generation-scoped group;
- one replica pipeline/hub/read adapter.

Startup order:
1. Validate configuration and required credentials.
2. Install/verify snapshot and generation.
3. Build replica store, pipeline/hub and snapshot subscription adapter.
4. Create Redis client and consumer.
5. Start worker and verify healthy startup.
6. Mark replica-backed route ready.

Shutdown order:
1. Stop accepting new replica-backed subscriptions.
2. Signal worker stop and await bounded termination.
3. Close dispatcher admission.
4. Close Redis client.
5. Release local resources.

Any startup failure must close already-created resources and keep replica-backed readiness false. A worker that fails to stop within its deadline must not be reported as stopped.

## 4. Two-ASGI CI harness

Use existing Redis 7 CI service; do not add paid infrastructure or a second Redis service. Start two independent ASGI server processes with:
- distinct bind ports;
- shared ephemeral Redis URL and stream key;
- separate replica SQLite paths;
- identical source snapshot generation;
- separate consumer groups derived from replica identities;
- test-only credentials/configuration.

The test must connect to both WebSocket endpoints and verify:
- both initial snapshots expose the same cursor;
- both receive the same event IDs and monotonically increasing cursors;
- no duplicate cursor is emitted;
- a replay/live boundary event is delivered exactly once;
- each replica checkpoint equals the final delivered cursor.

## 5. Failure acceptance matrix

| Scenario | Required invariant |
|---|---|
| Gateway A restarts | A reinstalls/validates its snapshot and reclaims or starts the correct generation; B remains uninterrupted |
| Consumer worker restarts | Pending entries are reclaimed; durable cursor never moves backward |
| Redis unavailable | No ACK or false cursor advancement; worker enters bounded degraded/retry state |
| Redis recovers | Both gateways converge to same retained high-water cursor |
| Snapshot generation changes | Old generation is fenced; new group begins after verified snapshot watermark |
| Retention overtakes replica | Replica fails closed and requests fresh snapshot |
| Callback/ASGI loop stalls | No ACK before callback completion; worker shutdown reports timeout honestly |
| One gateway is slower | Independent group prevents fast gateway from consuming slow gateway's delivery |
| Two consumers accidentally start for one replica | Local lifecycle guard prevents duplicate worker ownership |

## 6. Production security acceptance

Before production enablement:
- Redis TLS certificate validation enabled;
- per-instance least-privilege ACL identity;
- runtime consumer cannot destroy groups or trim streams;
- publisher identity limited to required append/checkpoint operations;
- secrets injected from protected environment/secret manager, never committed;
- credential rotation tested without data loss;
- network target and certificate identity verified by owner.

No production credentials or ACL changes are created by this blueprint.

## 7. Exit criteria

The WebSocket multi-instance task is not complete until:
1. both real ASGI processes pass integration harness;
2. all failure-matrix tests pass in CI;
3. latest exact branch SHA has successful Automated Tests and CodeQL;
4. production TLS/ACL and owner-side topology evidence are recorded;
5. public WSS/browser/Android checks pass before external gate closure.

Passing isolated Redis consumer tests is necessary but insufficient. Documentation or CI success cannot close Gate 25/36 without external acceptance evidence.

## 8. Non-goals and safeguards

- No changes to main.
- No Vercel/Cloudflare deployment or promotion.
- No paid storage, hosting, subscription or data feed.
- No production startup wiring before snapshot transport and lifecycle approval.
- No Footprint/Heatmap visual implementation before user references and blueprint review.
- No claim that work continues asynchronously after a response.

## 9. Current implementation reconciliation — 21 November 2026

This section supersedes the earlier implementation-state bullets in sections 2 and 3.4 where they say the FastAPI lifespan does not own the Redis worker or that the WebSocket route is always source-store-backed.

Inspected runtime/source-test checkpoint: `56317eff2b71886040acb998bf692814622feedf`.

- FastAPI lifespan now supports an **opt-in injected** `replica_runtime_factory`. It validates the replica store, dedicated Redis client, stream key, consumer bindings and generation-scoped group.
- Startup acquires the consumer ownership lease before Redis group initialization, hydrates the pipeline from the verified local replica, creates the event-loop dispatcher, and starts the managed Redis worker.
- Shutdown uses a bounded worker stop. Lease release occurs only after the worker has stopped successfully.
- The WebSocket route uses `subscribe_replica_snapshot` and replica Redis replay when a replica runtime is injected; otherwise it retains the source-store path.
- The Redis consumer, lease, worker, replica bridge and replay components have individual regression coverage. Exact documentation branch HEAD `290c4fe1b4a125e9a41b410d942e807db22c58aa` passed all four GitHub check runs: Test and Build, CodeQL JavaScript/TypeScript, CodeQL Python, and full reachable Git-history secret audit. Test totals: frontend 245/245 across 29 files; backend 1,218 passed, 6 warnings.

### 9.1 Still-open acceptance

A full test that launches two independent FastAPI/ASGI server processes, gives each a separate SQLite replica and consumer group, connects two WebSocket clients, and proves identical cursor/event delivery was not found in the inspected backend test inventory. Component tests are not a substitute for this end-to-end proof.

Snapshot transport and installation are still not a complete owner-approved deployment contract. The runtime factory is opt-in and requires a verified snapshot/generation. Do not guess a production snapshot path, share a SQLite WAL database across hosts, or enable replica mode by default.

Production Redis TLS/ACL/network/failover, actual host topology and supervision, public HTTPS/WSS, browser/Android reconnect tests, and real provider delivery remain owner-side acceptance items.

### 9.2 Required next batch

Implement the CI-only two-ASGI-process harness using the existing Redis 7 CI service and temporary test resources. Prove identical snapshot watermark, ordered events/cursors, replay/live boundary handoff exactly once, independent checkpoint convergence, and restart/outage/retention/lease-loss behavior. Keep production replica mode disabled until the snapshot topology is explicitly approved and owner-side evidence is available.

**Current accounting:** WebSocket component reliability tests are green; full two-ASGI acceptance remains open. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional. No indicator progress is awarded. ZERO COST; no deployment or `main` change.
