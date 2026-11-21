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
