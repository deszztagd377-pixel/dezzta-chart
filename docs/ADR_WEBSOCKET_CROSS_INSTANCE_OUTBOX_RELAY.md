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
