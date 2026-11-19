# ADR — Cross-instance WebSocket fan-out through the durable OHLCV outbox

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Status:** Batch 62A implementation groundwork; distributed relay and owner acceptance remain OPEN  
**Cost:** ZERO COST. No new hosted service or deployment is authorized.

## Verified context

- `SQLiteOhlcvStore.apply()` commits accepted candle revisions and outbox events in one SQLite transaction.
- The outbox has stable event IDs, monotonic global integer cursors, exact series identity and a bounded 100,000-event retention window.
- `replay_outbox()` is exact-series scoped for client reconnect; it is not a global relay API.
- `OhlcvStreamHub` is process-local.
- The database is opened by local filesystem path and configured for WAL. Do not assume a WAL SQLite file is safe as a multi-host shared network database.
- Therefore, a second app process does not automatically receive local hub events.

## Decision

Keep SQLite outbox as the source of truth. A bounded global outbox reader is the relay input. A future relay may publish committed events to Redis Streams; every app instance consumes through its own consumer group and forwards validated events to its local hub. Redis is transport, not a second canonical candle database.


## Additional blocker discovered during Batch 62B architecture audit

Redis fan-out alone is not a complete multi-instance WebSocket data plane. Each app process constructs its own SQLiteOhlcvStore, OhlcvPipeline, instrument registry, and process-local OhlcvStreamHub. A second process can consume a Redis event and still lack authoritative bars for a consistent initial snapshot. Sharing the WAL SQLite file between hosts is not an acceptable shortcut.

Before wiring Redis Streams into application startup, choose and test a complete topology:
1. **Authoritative writer + replicated local read models:** one identified ingestion owner writes the authoritative SQLite outbox; every gateway maintains a local replica from the durable stream. Replica application must be idempotent, must not re-emit source outbox events, and must expose a snapshot watermark consistent with its applied cursor.
2. **Authoritative snapshot service:** gateways obtain snapshots and entitlement-scoped history from a separately defined authenticated source API while Redis Streams carries live updates. That API and its security/availability contract do not currently exist.

The first option is the preferred zero-cost CI path, but requires single-writer ownership, source identity, replica-apply transaction, cursor/watermark contract, entitlement consistency, and recovery/resnapshot protocol. Do not implement partial fan-out without solving the snapshot read model.

## Batch 62B Redis process-level security evidence

The existing Redis CI service is zero-cost. Batch 62B adds a test using two independently spawned backend processes and separate Redis clients. Expected result: exactly one process consumes a single-use ticket and exactly one process acquires the shared per-account lease. This is CI evidence only, not owner-managed multi-instance acceptance. No Stream ACL permissions are added until the stream key schema and commands are reviewed.



## Batch 62C — atomic snapshot + watermark primitive

A second multi-instance prerequisite is now implemented at the SQLite storage boundary: `SQLiteOhlcvStore.query_snapshot()` reads the selected bar set, total count, outbox high-water cursor, and retention floor inside one SQLite read transaction. Since `apply()` commits a bar revision and its outbox event/state in one write transaction, this gives a future local replica/gateway a stable snapshot boundary to resume from.

The method intentionally does **not** switch the live WebSocket route from its current in-memory pipeline. That route still relies on event-loop-confined snapshot registration; swapping it before a replica read model and authorization/catalog synchronization exist would be unsafe. The primitive is foundational and tested, not production multi-instance fan-out.

The Redis process test was also tightened: a process that fails to consume the single-use ticket no longer attempts an authenticated account lease. Exactly one process must consume the ticket and that same process must be the sole lease winner.



### Snapshot transaction concurrency proof

Batch 62D adds a deterministic concurrency regression: a snapshot reader establishes its SQLite read view after reading outbox state, a separate writer commits a new bar/outbox event while the reader is paused, and the reader must return the earlier bars **and** earlier cursor. A subsequent snapshot must return both revisions and the newer cursor. This specifically verifies that the watermark and bar rows do not come from different database moments.



## Batch 62D CI verification

Exact source HEAD `c2008868538cbf57fcff8f806e7c9b775785ef6e` passed all three workflows:
- Automated Tests + Build run `44495306834`: 1,048 backend tests and 236 frontend tests / 28 files; build, benchmark, dependency audits, container build/smoke and Trivy report all succeeded.
- CodeQL run `44495306746`: Python and JavaScript/TypeScript succeeded.
- Full Git History Secret Audit run `44495306805`: succeeded.
- Trivy image scan reported zero vulnerabilities across 69 image/package targets in the generated table; report artifact was uploaded.

The concurrency regression proved a reader paused after its SQLite outbox-state read returns the old bar set with cursor 1 while a concurrent writer commits cursor 2; a subsequent snapshot returns both bars with cursor 2. This is local snapshot transaction evidence, not multi-instance production acceptance.


## Delivery contract

1. Relay reads globally ordered outbox pages after a durable cursor.
2. Cursor, retention floor and page rows are read in one SQLite read transaction.
3. Relay publishes in cursor order; stable outbox event ID is the deduplication identity.
4. Delivery is at-least-once. A crash after Redis append but before checkpoint may repeat an event; consumers deduplicate by event ID/cursor before local hub publication.
5. Each app instance needs an independent consumer group. A shared group distributes events among instances and does not broadcast to all.
6. Consumers acknowledge only after successful local hand-off. Pending entries must be reclaimable after process death.
7. Retention must account for active groups. If a cursor falls behind the SQLite retention floor, require explicit recovery/resnapshot; never silently advance.
8. Queue overflow retains current behavior: disconnect/resnapshot the slow client rather than silently dropping updates.
9. Validate canonical series identity and event schema before forwarding. Preserve decimal strings, provenance, completeness and timestamps.
10. Redis outage must not roll back committed candle/outbox transactions. Relay resumes from its durable cursor.

## Idempotent relay append

Redis Stream IDs may be derived monotonically from positive outbox cursors (for example `<cursor>-0`). On retry, if that ID already exists, verify its stored event ID/cursor before treating the append as already committed. Do not swallow arbitrary duplicate-ID errors.

Stream append and relay checkpoint must be atomic in Redis (e.g. narrowly scoped Lua) or recoverable through deterministic IDs plus verification. ACL permissions must be scoped to the stream key and required group commands; do not broaden existing guard-key patterns.

## Implementation sequence

- **62A — implemented:** global bounded outbox reader + tests for all-series ordering, pagination, retention expiry and ahead-cursor rejection.
- **62B:** relay publisher, deterministic IDs, idempotent retry, durable checkpoint and fail-closed behavior.
- **62C:** per-instance consumer groups, pending reclaim, deduplication and local-hub forwarding.
- **62D:** two real backend processes on isolated CI Redis; kill/restart relay and consumers; verify no silent loss and explicit resnapshot.
- **62E:** owner independent Redis, public WSS, WebView foreground/background, 330-second attribution and cross-instance evidence.

## Capacity model

For event rate `λ` events/s and maximum relay outage `T` seconds, backlog headroom must be at least `B = λ × T`, plus safety margin. Do not set stream retention until event rate, outage target, payload size and consumer lag are measured. The existing 100,000-event SQLite retention is a hard recovery boundary, not a promise of any outage duration.

Two-instance test profile: 2 instances × 10 subscribers × 3 timeframes = 60 local subscriptions, run for 330 seconds. Record p50/p95/p99 delivery latency, cursor lag, pending count, duplicate count, reconnect count, and memory/stream growth. This is a test profile, not a production capacity claim.

## Acceptance

- Every committed event reaches both instance groups or explicit resnapshot is required.
- Duplicate relay delivery never duplicates candle application.
- Out-of-order events are detected; cursor gaps are not silently ignored.
- Relay/consumer restarts recover pending work.
- Redis outage creates bounded lag, not loss of committed source events.
- Retention exhaustion produces explicit resnapshot/alert.
- No cross-series contamination; decimal values and timestamps remain exact.
- Tests require no paid infrastructure or production credentials.

## Boundaries

Do not share a WAL SQLite file across arbitrary hosts; do not use Redis Pub/Sub as durable delivery; do not use one shared consumer group for all app instances; do not claim production Gate 36 closure from CI; do not deploy merely to manufacture acceptance evidence.


## Batch 62E — exact-head audit and topology gate

Current branch HEAD e36240032aec2539e8bb0fec3c037248133648f9 has all three exact-head workflows successful: Automated Tests run 44496224508, CodeQL run 44496224516 and Full Git History Secret Audit run 44496224538. This is CI/source evidence only.

The backend application factory still creates one OhlcvPipeline, one process-local OhlcvStreamHub and one file-backed SQLiteOhlcvStore per app process. This confirms the architecture blocker: a Redis relay without an authoritative writer and idempotent per-instance read-model replication cannot guarantee consistent initial snapshots.

**Implementation gate:** do not wire Redis Streams into application startup until writer ownership, source identity, replica apply without outbox re-emission, cursor/watermark consistency, catalog/entitlement synchronization and retention-triggered resnapshot are implemented and tested together. The next safe work is 62F–62J CI-only implementation/testing, followed by owner acceptance 62K. No deployment or paid infrastructure is authorized.

The current indicator ledger and progress values are unchanged: Stage 1 75% provisional; Gate 10 0/10 closed; Stages 2–6 not scored; overall project percentage not established. No ticks are awarded for this audit.



## Batch 62G — owner-approved integrated topology and global snapshot blocker

Owner approved combining the eight architecture points into one dependency-ordered multi-work cycle. The detailed implementation contract and test matrix are recorded in `docs/WORK_CYCLE_2026-11-19_BATCH62G_INTEGRATED_WEBSOCKET_BLUEPRINT.md`.

A further source review narrowed the snapshot constraint: `query_snapshot()` is a valid scoped snapshot primitive, but its default bucket/calendar filters omit calendar-qualified CME session rows. It therefore cannot be reused unchanged as a complete replica snapshot. A per-instrument snapshot also cannot advance a global cursor. Independently paginating separate SQLite read transactions would produce a mixed-time snapshot under concurrent writes; collecting every row into one unbounded in-memory list is not an acceptable capacity assumption.

**Required correction before replica checkpointing:** add a bounded immutable snapshot generation/manifest (or equivalent stable transfer mechanism) that captures all retained series identities and one global high-water in a single source read view. The replica may publish the snapshot watermark only after all pages, counts/hashes and series coverage validate and the complete local snapshot is atomically installed.

Integrated eight-point delivery order:
1. Full retained snapshot generation and atomic installation.
2. Stable source/replica identity and local checkpoint schema.
3. Transactional idempotent replica apply without source-outbox echo.
4. Deterministic Redis Streams append and one independent consumer group per gateway.
5. Apply-before-ACK, pending reclaim and crash-safe local publication.
6. Two independent backend processes/read models with parity checks.
7. Failure/recovery matrix including Redis outage, cursor gap and retention expiry.
8. Owner-side Gate 25/36 acceptance, only with real infrastructure and browser/WebView evidence.

Cursor rules: only `E=C+1` is eligible for apply; `E<=C` is duplicate/stale and must not mutate or regress; `E>C+1` is a gap requiring resnapshot. Bar mutation and checkpoint update are one SQLite transaction. Redis ACK follows commit. Replica apply must never emit a new source outbox event.

No Redis Streams publisher/consumer is activated at application startup until all eight points have implementation and test evidence. No SQLite WAL is shared between hosts. CI/local Redis remains supporting evidence, not Gate 25/36 owner acceptance.


## Batch 62G-2 — replica snapshot installation boundary

The first two executable parts of the approved snapshot protocol now exist:

- The authoritative store exports every retained OHLCV row and a global outbox high-water from one pinned SQLite read view, using bounded JSONL streaming and a manifest digest over the header plus every bar record.
- `SQLiteOhlcvReplicaStore` maintains an independent local read model, stable per-gateway replica identity and durable upstream checkpoint.
- Replica installation preflights the file, then validates it again while replacing the target bars in one SQLite transaction. The checkpoint is written in that same transaction only after the complete manifest and every canonical bar validate.
- Decimal fields are required to remain JSON strings; nanosecond and other integer fields must be actual integers. CME calendar identity is preserved.
- Replica source-writer `apply()` is blocked to prevent accidental source-outbox echo.

This is still a local storage primitive, not an activated distributed relay. Incremental replica event apply, event-ID idempotency, cursor gap handling, Redis Streams, consumer groups, pending reclaim and app-factory wiring remain pending. Do not activate Redis or change the WebSocket runtime until those pieces and their failure tests are complete.

The snapshot envelope is format version 2 and includes the full configured per-timeframe bar-retention policy alongside the global outbox retention floor. The replica checkpoint persists both, so the cursor boundary and source retention configuration remain observable after restart. A replica may only initialize against a dedicated empty OHLCV read-model database; it refuses to overwrite existing bars or source outbox state. Replica source-writer apply and snapshot export are both blocked.

The target-side snapshot swap uses a single write transaction and bounded batches. It is atomic to SQLite readers, but a large install can hold the target writer lock for the duration and increase WAL pressure. Measure snapshot size, install duration, writer wait and WAL growth before owner-host rollout. No production deployment or paid service is authorized.


## Batch 62G-3 — atomic incremental replica event apply

`SQLiteOhlcvReplicaStore.apply_replica_event()` now applies the authoritative outbox event envelope to the local read model.

- It binds every event to the source ID already stored in the replica checkpoint.
- It validates event type/version/operation, event ID, cursor, exact series identity, bar field set, Decimal strings and integer nanosecond timestamps.
- Only the next cursor `E=C+1` may be applied.
- Exact cursor + event ID + payload digest matches return `duplicate`; older events whose bounded dedupe record has aged out return `stale` without mutation.
- Cursor gaps and observed retention expiry require resnapshot. Conflicting event IDs/cursors are hard errors.
- Bar upsert, source-configured per-series retention pruning, applied-event ledger and checkpoint advance commit in one local SQLite transaction.
- Replica writes never append to its own outbox. Applied-event history is bounded to the source's 100,000-event retention horizon.
- Callers may ACK only after durable `applied`, `duplicate` or `stale` outcomes. A gap/retention result requires resnapshot; errors must not be ACKed.

Regression coverage now includes event apply, duplicate replay, conflicting IDs, stale history, cursor gaps, source mismatch, malformed decimals, source/replica retention parity and a forced checkpoint-write failure proving bar + ledger + checkpoint rollback together.

This is still a storage primitive. It is not wired to the process-local hub, Redis Streams, consumer ACK or app startup. Those steps remain blocked until the publisher/consumer recovery protocol and two-process parity tests are complete. No production deployment or paid service is authorized.


The replica checkpoint schema and event protocol are now version 3. Event replay fails closed if the stored checkpoint version does not match the current implementation; the gateway must install a current full snapshot before replay can resume. This prevents a replica with an obsolete deduplication/checkpoint contract from silently consuming new events.


## Batch 62H-0 — publisher contract and implementation guard

Repository audit confirms that Redis is already used by `RedisSharedGuard` for security limits/tickets, while OHLCV delivery still follows SQLite outbox -> process-local `OhlcvStreamHub`. These are separate concerns. The existing `read_outbox_batch()` is the global relay scan API; exact-series replay is not suitable for a global publisher.

Publisher invariants for 62H:

- Redis Stream ID is deterministic: `<global_cursor>-0`.
- Source SQLite persists a publisher checkpoint and advances it only after confirmed append or exact same-ID read-back verification.
- Crash after XADD and before checkpoint commit retries the same ID; an existing entry is success only when event ID and canonical payload match exactly.
- A single publisher must be serialized/fenced per source stream. Process-local locking is insufficient.
- No MAXLEN trimming until all consumer-group delivery and pending state can be proven safe. If source retention overtakes the publisher checkpoint, stop and require snapshot/rebuild; never skip.
- Redis outage never rolls back source bar/outbox commits.
- Every gateway uses its own consumer group. Shared groups would load-balance instead of broadcast.
- ACK follows durable replica apply; gaps, retention expiry, validation failures and transaction failures are not ACKable.
- No publisher/consumer is wired into app startup until append retry, pending reclaim, two-process parity and outage/recovery tests pass.

Implementation remains split into 62H-1 checkpoint/identity, 62H-2 deterministic append and fencing, 62H-3 tests, then 62I consumer recovery and 62J multi-process parity. 62K remains owner-side Gate 25/36 evidence. Batch 62H-0 changed documentation only; no executable behavior or gate status changed.


## Batch 62H-1 — durable publisher checkpoint and fencing

The source-local publisher checkpoint is implemented in `backend/app/ohlcv_redis_publisher.py`. It is bound to the authoritative `source_id` and a unique stream key, initializes only from a retained snapshot watermark, and stores the published cursor, deterministic last Stream ID, last event ID, lease owner/epoch/expiry and schema version in the source SQLite database.

Publisher ownership uses a transactional SQLite lease. A live lease excludes another owner; expiry takeover increments a fencing epoch. Cursor advancement is a one-event compare-and-swap and requires the deterministic `<cursor>-0` Stream ID. The API name `record_confirmed_append` is intentional: it may only be called after a successful Redis append or exact deterministic-ID read-back. Redis append and duplicate verification are not part of 62H-1; they are the next 62H-2 slice. No startup wiring, Redis ACL change, MAXLEN trimming, or deployment is included.

Tests use temporary local SQLite and cover snapshot watermark/retention, lease contention and fencing, deterministic cursor advancement, invalid gaps/IDs/expired leases, and compare-and-swap. Exact-head CI is required before declaring this batch validated.


### 62H-1 regression test repair

The first exact-head backend run had one failing CAS test fixture (1,067 passed / 1 failed). It supplied cursor 2 with expected cursor 0, so the contiguous cursor guard correctly rejected the input before CAS. The fixture now replays the already-confirmed cursor-1 event using stale expected cursor 0 and Stream ID `1-0`, thereby exercising the intended CAS rejection. Production publisher code remains unchanged. Exact-head CI for the repair is pending.


## Batch 62H-2 — deterministic Redis Streams publisher

Implemented in `backend/app/ohlcv_redis_publisher.py` and covered by `backend/tests/test_ohlcv_redis_publisher.py`.

- The source SQLite checkpoint remains the authoritative publisher cursor.
- Redis Stream ID is deterministic `<cursor>-0`.
- Each entry stores `source_id`, `event_id` and the canonical complete JSON payload.
- On XADD error, the publisher reads back only that exact ID. It accepts an existing record only when all three fields match exactly. Conflicts fail closed; unavailable read-back leaves the SQLite checkpoint unchanged.
- The bounded publisher loop renews and checks its SQLite fencing lease before each event, then advances the checkpoint only after append confirmation and authoritative outbox equality validation.
- Source retention expiry stops publication and requires a new global snapshot.
- No MAXLEN, startup wiring, consumer group, ACK, ACL change or deployment.

Exact-head CI at `f1f998a8659d206c797bdfac14b110a3849d4d68`: 1,075 backend tests passed; 236 frontend tests across 28 files passed; frontend build/secret scans, backend container build/smoke, CodeQL and full-history secret audit passed. The container vulnerability report was uploaded as an artifact.

The publisher is an injectable synchronous adapter; the caller owns scheduling and Redis client lifecycle. It is intentionally not started by `main.py`. 62H-3 real Redis restart/integration tests and 62I consumer recovery remain mandatory before any startup integration.


## Batch 62H-3 / 62H-4 / 62I — real Redis integration and consumer

The source publisher now has a real Redis integration suite, a fenced snapshot-rebase recovery path, and a separate per-gateway consumer module. See `docs/WORK_CYCLE_2026-11-19_BATCH62H3_H4_62I_CONSUMER.md`.

### Publisher recovery

- Real Redis tests prove deterministic `<cursor>-0` IDs, exact payload read-back after lost XADD reply, conflict rejection, uncertain-outcome checkpoint safety, and verification after client reconnection.
- `SQLiteOhlcvPublisherCheckpoint.rebase_from_snapshot()` allows a forward-only recovery after a fresh snapshot has been installed. It validates source retention/high-water bounds, expected cursor CAS, rejects live leases, clears expired ownership and increments the fencing epoch.
- Snapshot rebase is an explicit operation and is not wired to app startup.

### Consumer protocol

- `RedisOhlcvReplicaConsumer` derives an independent consumer group from each persistent replica identity and source ID.
- A new group starts at the replica snapshot cursor. Existing groups survive worker restart.
- `XAUTOCLAIM` reclaims abandoned pending messages before `XREADGROUP` reads new messages.
- Each entry's source identity, field schema, canonical JSON, event ID and deterministic stream ID are verified.
- The local replica's transactional apply must return `applied`, `duplicate` or `stale` before `XACK`.
- Cursor gap, retention resnapshot request, malformed/conflicting payload, or deleted pending entry is not ACKed.
- After a successful snapshot replacement, the quiesced gateway group can be destroyed and recreated at the installed snapshot watermark.
- Redis Server 6.2+ is required for XAUTOCLAIM; the CI integration service uses Redis 7.

### Exact-head evidence

At `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`: 1,088 backend tests passed; 236 frontend tests across 28 files passed; frontend build/scans, backend dependency audit, container build/smoke, CodeQL and full-history secret audit passed. Automated Tests run `44543198371`, CodeQL `44543198283`, Secret Audit `44543198433`.

### Integration boundary

Neither publisher nor consumer is wired into `main.py`. No WebSocket hub forwarding, worker supervisor, production Redis credentials, stream trimming, or deployment is included. A real two-process/two-host parity and outage matrix remains 62J; owner Gate 25/36 acceptance remains separate.
