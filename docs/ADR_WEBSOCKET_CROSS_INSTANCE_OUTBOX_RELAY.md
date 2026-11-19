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
