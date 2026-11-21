## Batch 62J-81 — Gate 38 zero-cost collector design (21 November 2026)

- Exact-head baseline 3eadda21f795abe5af195eedf0c81727d31f6436 rechecked: Automated Tests run 44895224507 SUCCESS; CodeQL run 44895224465 SUCCESS for JS/TS and Python; full Git-history secret audit run 44895224498 SUCCESS.
- Current source still has bounded process-local request and WebSocket metrics. The protected endpoint remains token-gated; the WebSocket middleware records lifecycle metadata only.
- The existing Redis client is coupled to shared security guards. It is not reused for telemetry because doing so couples monitoring availability to auth/rate-limit operations and could exceed its ACL scope.
- The existing SQLite incident journal is not a time-series collector. The market-data registry database is not used for high-frequency metrics writes.
- Added GATE38_METRICS_COLLECTOR_BLUEPRINT.md: same-host multi-worker aggregation using a dedicated SQLite metrics DB on a supported local persistent volume; 15-second snapshots; transactional deltas; 15-minute buckets; 90-second worker-heartbeat expiry; 7-day bounded retention; hard worker/cardinality/payload/row/disk limits.
- Load estimate at 100 requests/s: 8,640,000 request-level write opportunities/day/worker versus 5,760 periodic flushes/day/worker, a 1,500x operation-count reduction. This is an estimate, not a benchmark.
- This is a documentation/design checkpoint only. Source implementation requires explicit blueprint review under the project's major-implementation rule.
- Gate 38 remains 🟧 OPEN pending implementation, tests, exact-head CI, host volume/access/retention/disk-pressure evidence and independent operator notification/recovery acceptance.
- No indicator code changed and no indicator progress is awarded. Complete formulas, warm-up indices, remaining renderer work, and Footprint/Heatmap visual gates remain in INDICATOR_PROGRESS_LEDGER.md.
- ZERO COST; no deployment, production credentials, Redis ACL change, main modification, Termux or device operation.

---

## Batch 62J-80 — send-confirmed WebSocket lifecycle metrics

**Reviewed branch:** phase-2/market-data-foundation  
**Change scope:** backend/app/observability.py and backend/tests/test_observability.py

The observer now updates accepted-handshake and close-code metrics only after the downstream ASGI send call returns successfully. A failed send no longer produces false-positive acceptance/close telemetry. The middleware finally block still finalizes the connection, decrements the active count and records completion even when the application/transport raises.

Regression cases cover failure at the accept frame and failure at the close frame after a successful accept. These cases assert active=0 and completed=1, with accepted and close-class counters reflecting only successful downstream sends.

No WebSocket payload/protocol/auth/replay/snapshot behavior changed. Gate 38 remains 🟧 OPEN: metrics are process-local, not centrally aggregated or durably retained. The production acceptance boundary described below remains unchanged.

---

# WebSocket Production Wiring Audit

**Audit date:** 21 November 2026  
**Active branch:** `phase-2/market-data-foundation`  
**Source checkpoint reviewed:** `da9b2ad025ac5c49f75c95dbdd5f516573107f87`  
**Scope:** source SQLite outbox -> Redis Streams -> gateway replica -> authenticated WebSocket

## Executive result

The initial audit found that the repository contained substantial publisher and consumer primitives but lacked a source publisher lifecycle hook. Batch 62J-69 has since implemented that lifecycle hook and exact runtime-binding checks. The production data path is still not activated by the module-level default ASGI app and is not host-accepted; do not deploy this checkpoint as proof of live fan-out.

The initial audit found two independent integration gaps:

1. **Initial finding — source publisher lifecycle absent (superseded by Batch 62J-69).** `backend/app/ohlcv_redis_publisher.py` implements `SQLiteOhlcvPublisherCheckpoint`, `RedisOhlcvStreamAppender`, and `RedisOhlcvPublisher.publish_available()`. The publisher class explicitly documents that it is not connected to FastAPI startup. `backend/app/main.py` imports the gateway consumer worker but not the source publisher. Its `publish_persisted_bar()` reads the durable outbox event and calls only `stream_hub.publish()`; it does not append that event to Redis Streams.
2. **Gateway runtime remains injection-only.** `create_app()` accepts an optional `replica_runtime_factory`; the module-level `app = create_app()` supplies none. Therefore the default ASGI entry point starts the provider/local-SQLite path, not the replica consumer path. A gateway host needs an explicit, verified factory and a preinstalled replica snapshot.

These gaps are separate: wiring the source publisher does not automatically provision gateway snapshots or activate the replica runtime.

## Existing verified components

- Durable source OHLCV outbox with contiguous global cursors.
- SQLite publisher checkpoint with lease owner/epoch fencing and compare-and-swap cursor advancement.
- Redis appender with deterministic stream IDs (`<cursor>-0`) and exact-ID read-back after ambiguous XADD replies.
- Bounded publisher batches and explicit fresh-snapshot requirement when source outbox retention overtakes the publisher cursor.
- Atomic global snapshot export/verification and replica snapshot installation.
- Independent per-gateway Redis consumer groups, apply-before-ACK, durable local SQLite replica checkpoint, replay, ownership lease and resnapshot-required handling.
- Replica hydration and atomic snapshot-to-live subscription bridge.
- FastAPI gateway worker startup validates snapshot hydration, ownership lease and Redis consumer-group readiness before accepting traffic.

## Required implementation sequence

### WS-PUB — remaining host-side activation

The FastAPI lifecycle hook is implemented and CI-verified. Remaining activation requirements are owner-host tasks:

- Inject a source-only `publisher_runtime_factory`; the default module-level app deliberately remains disabled.
- Build the publisher against the exact `SQLiteOhlcvStore` instance supplied by FastAPI. Runtime startup rejects a different store, checkpoint, source ID, Redis client or stream key.
- Require a pre-existing checkpoint or initialize it only from the exact global snapshot watermark already installed on every target gateway. Never infer or invent the cursor.
- Use a dedicated least-privilege publisher ACL client and finite connect/socket timeouts; production must use `rediss://`.
- Verify the owner-host durable volume, Redis ACL and snapshot generation before enabling the feature.
- The sanitized lifecycle state is held in application state; it is not a public status route and does not expose credentials or exception messages.

### WS-SNAP — snapshot generation coordination

Do not initialize the publisher checkpoint from an arbitrary current cursor. The checkpoint watermark must match the exact global snapshot generation installed on every target gateway. Snapshot export, integrity verification, distribution, installation, generation activation, publisher checkpoint initialization/rebase and rollback need an explicit ordered operator workflow.

### WS-GW — gateway runtime configuration

Provide a host-injected gateway runtime factory that:
- Opens a dedicated least-privilege Redis client.
- Opens the persistent local replica SQLite path.
- Requires a verified snapshot before constructing the consumer.
- Uses the generation-scoped group and owner lease.
- Closes resources safely on every startup-failure and shutdown path.

Keep source publisher and gateway consumer as separate application roles unless a reviewed architecture explicitly proves a combined role safe.

## Acceptance matrix

| Test | Required evidence |
|---|---|
| Publisher bootstrap | Missing checkpoint fails closed; valid snapshot checkpoint starts |
| Event relay | Source outbox cursor N becomes exactly Redis Stream ID N-0 |
| Ambiguous XADD | Lost reply is resolved by exact-ID read-back without double append |
| Redis outage | Source commit remains durable; publisher retries without advancing cursor |
| Retention gap | Publisher enters resnapshot-required; no cursor is skipped |
| Wake-up and backlog | New bars wake relay; process restart drains retained backlog |
| Shutdown | Publisher task stops and dedicated Redis client closes |
| Snapshot alignment | Publisher cursor equals the installed gateway snapshot watermark |
| Two gateways | Both independent replica groups receive the same ordered source events |
| Replay continuity | Restart/reconnect resumes from durable cursors without gaps or duplicate client delivery |
| Host acceptance | Real TLS/ACL, persistent volumes, public WSS, browser and Android WebView verified |

## Safety and cost constraints

- No Vercel or Cloudflare deployment is required for repository-side implementation or CI.
- No paid Redis service is assumed. Use only an already available, owner-controlled Redis endpoint; otherwise keep the relay disabled.
- No production credentials, snapshot files or encryption keys belong in Git or chat.
- Do not run a production host migration or alter persistent data as part of a code-only change.
- Do not modify `main`.
- Do not mark host-only gates green based on source tests or CI.

## Current project accounting

- Gate 10: 0/10 formally closed.
- Gate 8: yellow host-verification-only; all other Gate 10 entries remain open.
- Stage 1: 30/40 criteria = 300/400 ticks = 75% provisional.
- Overall project and aggregate indicator percentages: unscored pending approved weights and denominators.
- Indicator formulas/foundations remain unchanged by this audit. Existing indicator implementation status remains as documented in `PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

## Audit disposition

**WebSocket repository primitives:** substantially implemented and CI-verified for the defined automated failure matrix.  
**Source-to-Redis publisher lifecycle hook:** implemented and exact-head CI-verified; source runtime factory, snapshot watermark alignment, dedicated Redis ACL and host activation remain 🟨🟩 pending.  
**Redis-to-gateway replica integration:** opt-in factory exists; default ASGI entry point is not wired.  
**Production acceptance:** open; public WSS, production Redis TLS/ACL topology, snapshot distribution/rotation/rollback, browser and Android WebView acceptance remain unverified.  
**Initial audit code changes:** none. Batch 62J-69 adds the subsequent FastAPI publisher lifecycle and runtime-binding validation.


## Batch 62J-69 — source publisher lifecycle integration (21 November 2026)

**Source change:** FastAPI now accepts a dedicated, owner-injected `publisher_runtime_factory` for the source application role. Lifespan validates that the publisher, dedicated Redis client and exact stream key agree; performs Redis PING before provider ingestion starts; runs bounded synchronous publisher batches through `asyncio.to_thread`; wakes on persisted-bar callbacks; and polls once per second to recover retained backlog after restart. Transient failures use bounded 1–30 second exponential backoff. A typed retention-gap exception transitions the worker to terminal `resnapshot_required` without advancing the checkpoint. Shutdown waits up to 15 seconds and closes the dedicated client only after the publisher task has stopped.

**Role isolation:** one FastAPI app cannot be configured with both source publisher and gateway replica runtime factories. The module-level default app remains publisher-disabled unless its owner explicitly injects a source runtime factory. No Redis URL, credentials, snapshot cursor or snapshot artifact is inferred by application code.

**Host gate:** the source runtime factory must construct `SQLiteOhlcvPublisherCheckpoint` against the durable source database, require an existing checkpoint or initialize it only from the exact global snapshot watermark already installed on every target gateway, and use a dedicated publisher ACL client with finite socket/connect timeouts. The code cannot prove remote snapshot installation; this remains an owner-host prerequisite. Publisher lifecycle wiring is therefore **🟨🟩 HOST-FACTORY / SNAPSHOT VERIFICATION PENDING**, not production-green. Do not enable the source publisher until snapshot and ACL preconditions are satisfied.

**Verification boundary:** lifecycle contract tests cover Redis readiness, task startup, graceful client close, source/gateway role separation and runtime binding mismatch. The runtime also rejects a publisher bound to a different SQLite store or checkpoint/source ID. Exact-head CI on `6f49951c253a7e7b995b4bdd52eba8153edaef77` passed: Automated Tests [44866818528], CodeQL [44866818498] and Full Git History Secret Audit [44866818495] all SUCCESS; frontend 247/247, backend 1,241 passed, and all 33 workflow steps succeeded. Backend container build, Redis ACL/AOF + persistent-volume smoke, container scan and vulnerability-report export also succeeded. No deployment, live Redis connection, production host, Termux command, paid service, or `main` change was performed.



## Batch 62J-70/71 — dedicated source runtime and production transport enforcement

### Source publisher runtime (62J-70)

Added `backend/app/ohlcv_redis_runtime.py`:
- Separate dedicated publisher ACL URL; does not reuse the shared HTTP/WebSocket guard URL.
- Production validation requires `rediss://`, dedicated ACL username/password and database 0.
- Redis client uses 3-second connect timeout, 5-second socket timeout, 15-second health-check interval, TLS certificate-chain verification and hostname verification.
- The durable publisher checkpoint must already exist. The factory never creates an arbitrary cursor.
- Before creating a Redis client, an owner-injected snapshot verifier must prove exact source ID, stream key, generation and cursor equality between the global manifest and one installation receipt per required gateway.
- Missing gateway receipts, duplicate/empty gateway identities, or any generation/cursor/source/stream mismatch fail closed.
- Environment helper remains opt-in; default module-level ASGI app is not silently enabled.

The publisher and gateway ACL command matrices now include `+ping` for their readiness checks. Other command permissions remain separated by role. Tests assert the exact allow-lists.

### Production HTTPS/WSS enforcement (62J-71)

- Production frontend builds reject a plaintext HTTP ticket endpoint before issuing the Firebase bearer request.
- Production frontend builds reject a plaintext `ws://` market-data endpoint before creating the WebSocket.
- HTTPS maps to WSS. Development mode retains its prior HTTP/WS behavior for local work.
- Added frontend regressions for both rejected production plaintext paths.

### Exact-head verification

Source/test HEAD: `5575f5d820dd26d16a7170cb2c55e9c707c2afc1`.

- Automated Tests [44868539276] — SUCCESS; frontend **249/249 across 29 files**, backend **1,246 passed**, all **33/33 workflow steps**.
- CodeQL [44868539309] — SUCCESS.
- Full Git History Secret Audit [44868539423] — SUCCESS.
- Android APK Build (zero-cost CI) [44868539288] — SUCCESS. This confirms build output only, not installation or runtime acceptance on a physical Android device.
- Frontend/backend dependency audits, backend container build, Redis shared-guard/persistent-volume smoke, container scan, vulnerability-report export and artifact upload — SUCCESS.

### Production acceptance boundary

Repository-side source publisher runtime construction and production transport guards are implemented and CI-verified. **Production WebSocket acceptance is not yet complete.** The remaining evidence requires owner-controlled runtime access:
- Actual snapshot manifest and signed/controlled installation receipts for every target gateway.
- Durable source SQLite path, checkpoint watermark and actual gateway replica volumes.
- Live Redis TLS handshake, ACL enforcement, persistence, failover and private network restrictions.
- Owner-host secret injection, rotation and rollback.
- Gateway runtime factory configured on the target host.
- Public HTTPS/WSS reverse proxy, hostname/certificate/renewal.
- Browser end-to-end and actual Android WebView/device acceptance.

The snapshot-verifier callback is a strict contract; the repository cannot probe the user's remote hosts. No host acceptance is inferred from CI. Gate 25 and Gate 36 remain 🟧 OPEN. Source publisher remains 🟨🟩 HOST VERIFICATION PENDING. Gate 8 remains 🟨 HOST VERIFICATION ONLY.

### Indicator and project accounting

No indicator formula, calculation, hook, renderer or chart UI changed. The complete indicator ledger remains in `PROJECT_PROGRESS_INDICATOR_CURRENT.md`:
- SMA20 🟨, first valid candle index 19.
- EMA20 🟨, SMA-seeded with alpha 2/21, first valid index 19.
- RSI14 🟨, Wilder smoothing, first valid index 14.
- MACD12/26/9 🟨, MACD index 25 and signal/histogram index 33.
- Bollinger20,2 🟨, population standard deviation, first valid index 19.
- Shared Indicator Hook 🟨.
- Footprint 🟧 SIMULATED / GATED.
- Heatmap 🟥 NOT IMPLEMENTED.
- Liquidation Maps 🟥 NOT IMPLEMENTED.

Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; Stages 2–6 and overall project percentage remain unscored. ZERO COST; no production deployment, paid service, Termux/device operation, Vercel/Cloudflare operation or `main` change.


## Batch 62J-72 — snapshot artifact digest binding

The source publisher runtime now requires the exact SHA-256 digest returned by the verified global snapshot manifest and requires every gateway installation receipt to bind to that same digest. The runtime rejects malformed/missing digests and any gateway receipt mismatch before creating the Redis client.

The digest contract is grounded in the existing snapshot exporter/verifier:
- `SQLiteOhlcvStore.export_global_snapshot()` writes a SHA-256 digest over the canonical header and every canonical bar record, and returns it with the snapshot generation, source ID and high-water cursor.
- `SQLiteOhlcvStore.verify_global_snapshot()` recomputes the digest from the artifact and validates the manifest digest and row count.
- The host verifier must invoke that verifier on the actual snapshot artifact and authenticate the installation receipt source. It then maps the export/verifier `generation_id`, `cursor`, and `sha256` into the runtime evidence contract (`snapshot_generation`, `snapshot_cursor`, `snapshot_sha256`); each receipt must contain the matching `snapshot_sha256`.

This is stronger artifact identity binding, not proof of remote installation or receipt authenticity. No receipt-signing format or storage backend is invented by this change. Host-side verification remains external.

Regression coverage now includes:
- Missing publisher checkpoint fails before Redis client creation.
- Gateway cursor mismatch fails before Redis client creation.
- Gateway snapshot digest mismatch fails before Redis client creation.
- Malformed manifest digest fails before Redis client creation.
- Matching source, stream, generation, cursor and digest can construct the dedicated TLS client with certificate and hostname verification.

**Gate status:** Gate 25 🟧 OPEN (live Redis TLS/ACL, persistence, failover and credential lifecycle remain unverified). Gate 36 🟧 OPEN (public HTTPS/WSS reverse proxy and browser/Android runtime acceptance remain unverified). Source publisher activation remains 🟨🟩 host-verification pending.


## Batch 62J-74 — exact-head CI acceptance and Redis ACL least-privilege correction

### Exact CI evidence

The Automated Tests workflow completed successfully on head `3e3428910e3226f3d4365808f3a36a3138674231` (run [44874341856](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341856)). Backend pytest reported **1,249 passed in 57.10 seconds**. The new Redis ACL integration test and the existing full publisher/consumer ACL integration test both passed. CodeQL (run [44874341916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341916)) and full Git-history secret audit (run [44874341885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341885)) also succeeded.

The existing CI Docker smoke additionally verified:
- Redis ACL rejects unauthenticated access, wrong passwords and unrelated SET operations.
- Redis AOF data and its ACL file survive a Redis container restart on a named volume.
- The backend returns the expected fail-closed 503 during Redis outage and recovers after Redis returns.
- Non-root application UID/GID, persistent-volume/database ownership, SQLite integrity and backend restart persistence.
- HTTP rate-limit enforcement.
- Backend container image scan and vulnerability-report export/upload succeeded.

This is repository/CI simulation evidence, not production-host acceptance. The Redis AOF/volume smoke is for the shared guard service and does not prove production persistence/failover of the dedicated OHLCV relay stream.

### Redis ACL correction — supersedes Batch 62J-73 SELECT claim

The earlier Batch 62J-73 note incorrectly stated that redis-py needs `+select` when connecting to database 0. The existing real-Redis end-to-end ACL test used a `/0` URL without `+select` and passed. Database 0 is the Redis default; the client does not need a SELECT command to use it.

Batch 62J-74 removes `+select` from both publisher and gateway command allow-lists. The new integration test explicitly verifies:
- Both clients connect through the DB-0 URL and PING successfully.
- Publisher/gateway allowed stream and lease operations work.
- Explicit `SELECT 1` is rejected for both roles.
- Publisher and gateway prohibited commands and out-of-scope key access remain rejected.

This tightens least privilege. URL parsing still rejects non-zero database paths.

### Production boundary and gates

WebSocket E is complete for the defined automated repository failure matrix. Production acceptance still requires owner-controlled evidence for actual global snapshot artifact distribution and authenticated per-gateway receipts, production Redis TLS/ACL topology and secret rotation, dedicated OHLCV stream persistence/failover/retention, public HTTPS/WSS reverse proxy, browser and Android WebView runtime acceptance.

Gate 8 remains 🟨🟩 host-verification-only. Gate 25 and Gate 36 remain 🟧 OPEN; Gates 20, 30, 31, 34, 35, 38 and 39 remain 🟧 OPEN. Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.

See `PROJECT_PROGRESS_INDICATOR_CURRENT.md` for the complete indicator ledger and current accounting. ZERO COST; no deployment, production credentials, Termux, Vercel/Cloudflare operation or `main` modification.


## Batch 62J-75 — exact-head CI confirmation and host/device acceptance boundary

Exact-head CI for `f3264c7ee0db573b4ff999c558506c4efe3e59d5` completed successfully:
- Automated Tests [44875028851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028851) — SUCCESS; 1,249 backend tests passed in 49.05 seconds.
- CodeQL [44875028870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028870) — SUCCESS.
- Full Git History Secret Audit [44875028765](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028765) — SUCCESS.
- Redis ACL integration verified DB-0 operation with no `+select`; explicit `SELECT 1` is denied for publisher and gateway roles.
- Backend container build, Redis shared-guard/AOF persistent-volume smoke, image vulnerability scan and report export/upload — SUCCESS.

The ACL correction supersedes the Batch 62J-73 diagnosis: database 0 is the default in the redis-py client path used by this repository; granting `+select` was unnecessary and has been removed. This is a least-privilege improvement.

### WebSocket acceptance disposition

The repository-side automated WebSocket E/failure matrix is complete for its defined CI scope. The real-host production acceptance cannot be completed because this project currently has GitHub + CI only and no owner-controlled backend server. The CI Redis service and Docker smoke are ephemeral and do not create a public WSS endpoint.

### Gate 10 host/device classification

- 🟨🟩 Host/owner verification only: Gate 8 (secret injection/runtime exposure), Gate 30 (restore on actual owner-controlled database path), Gate 34 (actual persistent volume/restart/disk pressure), Gate 35 (real HTTPS certificate/proxy/renewal), Gate 39 (live operator visibility, acknowledgement/escalation and recovery).
- 🟧 Additional integration still open: Gate 20 (real Firebase project and browser/Android auth/revocation), Gate 25 (owner-injected snapshot verifier/receipts and live dedicated Redis TLS/ACL topology), Gate 31 (off-host backup destination and independent key custody), Gate 36 (public WSS plus browser/Android WebView acceptance), Gate 38 (collector/dashboard/retention integration).

Yellow-green is not acceptance or closure. Gate 10 remains 0/10 formally closed; only complete external evidence can turn a gate bright green.

**Host verification is not an APK-only test.** It requires evidence from the actual server/provider/storage/operator environment. Opening the APK is a separate client acceptance step. For Gate 36, Android/browser testing should occur only after a real public HTTPS/WSS endpoint is available. No Termux or phone-side command is required at this stage.

No production host, endpoint, TLS certificate, backup destination, Firebase project or credentials were fabricated or requested. ZERO COST; no deployment, no paid service, no `main` modification.


## Batch 62J-76 — exact-head verification and adjacent Gate 31/38 boundaries

Source/test HEAD 57b918feafd1b259b008b5efe1272199a29facff passed Automated Tests [44876347017](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347017), CodeQL [44876347037](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347037), Full Git History Secret Audit [44876347101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347101), and Android debug APK build [44876347021](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347021). Frontend 252/252 tests across 29 files; backend 1,249 passed in 50.02 seconds. The Android artifact is a CI build only, not device acceptance.

WebSocket repository/CI failure-matrix status remains complete for its defined automated scope. Production acceptance remains unavailable because no active backend host or public HTTPS/WSS endpoint exists. Do not infer production acceptance from the CI Redis service or container smoke.

Gate 31 remains open: repository encryption is AES-256-GCM/PBKDF2-based, but there is no independently controlled off-host destination or separate recovery-key custody. Gate 38 remains open: HTTP metrics are bounded and process-local, incident records persist in local SQLite, but central collection/dashboard, cross-worker aggregation, metrics retention/rotation, WebSocket telemetry and independent operator notification remain absent. The new Gate 38 runbook documents these boundaries.

Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35 and 39 are host/owner-verification-only 🟨🟩; Gates 20, 25, 31, 36 and 38 remain 🟧. Stage 1 is 30/40 = 75% provisional; overall project remains unscored. ZERO COST; no host, credentials, deployment, Termux or device operation.


## Batch 62J-77 — exact-head WebSocket/indicator acceptance checkpoint

Source/test HEAD e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8 passed Automated Tests [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829), CodeQL [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826), Full Git History Secret Audit [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841), and Android debug APK build [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773). Frontend 253/253 tests across 29 files; backend 1,249 passed in 48.11 seconds. Backend container build, Redis shared-guard/persistent-volume smoke and Trivy scan/export all succeeded.

SMA raw rolling-sum intermediate overflow was corrected using normalized window means; tests cover finite MAX_VALUE means and large cancellation. Full details are in docs/WORK_CYCLE_2026-11-21_BATCH62J77_NORMALIZED_SMA_AND_ACCEPTANCE.md and docs/INDICATOR_PROGRESS_LEDGER.md.

Repository WebSocket automated scope remains complete. Production acceptance remains blocked by absent owner-controlled host/public HTTPS-WSS endpoint and missing real production Redis/snapshot receipts. Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36, 38 remain 🟧. Stage 1 is 75% provisional; overall project remains unscored. ZERO COST; no host, credentials, deployment, Termux or device operation.


## Batch 62J-79 — WebSocket lifecycle metrics extension (21 November 2026)

- `backend/app/observability.py` now includes `WebSocketMetrics` and `WebSocketMetricsMiddleware`, scoped only to `/ws/market-data`.
- Captured fields: started, active, completed, accepted, peer disconnect count, five fixed close-code classes and cumulative duration. No payload/header/user data is read.
- Existing bearer-protected `/internal/metrics` response now includes a `websocket` object alongside HTTP metrics. No new public route.
- Tests cover accepted/closed lifecycle, peer disconnect and route isolation.
- The new metrics are process-local and reset at process start. They are not central telemetry, durable retention or an operator dashboard. Gate 38 remains 🟧 OPEN.
- Source/test HEAD: `2274f9adc5ac9907ea508800a2d962d9a7c14a84`. Frontend/backend tests and CodeQL analyses passed in the current run; remaining Automated Tests workflow steps were still running at documentation time. Full Git History Secret Audit passed. Exact links: [Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262277), [CodeQL](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262276), [Secret Audit](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262301).
- No WebSocket protocol, auth, replay, snapshot or market-data payload contract was changed. No public WSS/production acceptance claim is made.
