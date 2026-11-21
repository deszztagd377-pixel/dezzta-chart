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
