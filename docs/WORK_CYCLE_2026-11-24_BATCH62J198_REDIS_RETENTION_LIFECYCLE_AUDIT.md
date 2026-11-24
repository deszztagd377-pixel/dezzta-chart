# Work Cycle — 24 November 2026 — Batch 62J-198: Redis retention lifecycle audit and safe trim design

**Branch:** phase-2/market-data-foundation  
**Audited code HEAD:** 9f9260efe674886bf2232b896a726461b51614e5 (source paths are unchanged at the later documentation-only checkpoints)  
**Scope:** source-level retention lifecycle audit and implementation contract. No runtime source, tests, ACL, Redis instance, or deployment was changed.  
**ZERO COST:** maintained.  
**main:** untouched.

## 1. Important correction: there are two different retention layers

The earlier audit correctly found no Redis Stream XTRIM operation, but the source-side SQLite outbox already has a bounded retention floor. These must not be conflated.

### A. Authoritative SQLite OHLCV/outbox retention — IMPLEMENTED

Source: backend/app/ohlcv_store.py

- OUTBOX_MAX_EVENTS is 100,000.
- Each accepted market-data write inserts the outbox event, advances high_water, checks the current retention_floor, deletes outbox rows at/below the new floor when the window is exceeded, and advances retention_floor in the same SQLite transaction.
- The floor is monotonic: update uses MAX(existing_floor, new_floor).
- A normal AUTOINCREMENT cursor is contiguous, and floor advancement shares the same transaction as the event insert.
- Bar-history retention is separately bounded by configured timeframe caps.
- Outbox readers take a consistent SQLite read transaction for high_water, retention_floor and replay rows.
- A cursor below the floor returns resnapshot_required; a gap in the retained global cursor interval also fails closed.

This is a source-level bounded outbox implementation. It is not Redis stream retention.

### B. Redis Stream retention — NOT IMPLEMENTED

Source paths:
- backend/app/ohlcv_redis_config.py
- backend/app/ohlcv_redis_publisher.py
- backend/app/ohlcv_redis_consumer.py
- backend/app/ohlcv_redis_replay.py
- backend/app/ohlcv_redis_runtime.py
- backend/app/ohlcv_redis_gateway_runtime.py

Findings:
- Publisher appends deterministic cursor IDs using XADD and exact-ID XRANGE read-back; no XTRIM or XDEL is used.
- Publisher ACL is intentionally limited to PING, XADD and XRANGE.
- Gateway ACL is limited to the consumer/group, ACK, read and lease operations; it has no XTRIM/XDEL/XGROUP DESTROY authority.
- Redis replay validates a checkpoint retention_floor and applied_cursor and returns all-or-resnapshot when the cursor is expired, stream history has gaps/trimmed entries, or replay bounds are exceeded.
- Consumer groups are generation-scoped. After a new snapshot, a new group is installed; old generation groups and pending deliveries are deliberately retained for separately authorized cleanup.
- No project-owned Redis Stream retention janitor, trim controller, or group cleanup worker was found in the audited runtime.

Therefore Redis Stream memory can grow beyond the 100,000-event SQLite outbox window. This is a real storage/operations gap, but adding a trim call to the publisher or gateway would violate least privilege and can destroy replay continuity.

## 2. Why naïve XTRIM is unsafe

A single fixed MAXLEN does not prove that every registered gateway and reconnecting client can still replay from its last durable cursor.

Failure modes include:
1. The source SQLite floor advances while the Redis publisher is behind. The publisher then requires a new authoritative snapshot; trimming by guessed length can remove a non-contiguous cursor range or race with republishing.
2. A gateway replica may still be applying an older stream cursor. Trimming past that cursor can make the consumer unable to catch up.
3. Consumer-group pending entries may reference trimmed stream entries. Redis 7.x trim reference behavior must be selected explicitly; leaving dangling PEL references or deleting them can have different recovery consequences.
4. A new snapshot may be installed on one gateway while another gateway still owns an older snapshot generation and pending group.
5. A crash between publishing a retention floor and trimming, or between trimming and publishing the floor, can make the floor lie about actual replay availability.
6. The source global cursor advances across unrelated series. Retention must be global and cursor-contiguous; per-series trim boundaries are invalid.
7. Client WebSocket replay and replica consumer replay are different readers. A policy based only on the Redis consumer group's last-delivered ID does not protect reconnect clients.

## 3. Required design before any Redis trim implementation

Use a separately scoped retention controller, not publisher or gateway credentials. The contract must include:

### Authoritative floor
- Read the source SQLite high_water and retention_floor from one consistent read snapshot.
- The desired Redis trim floor cannot exceed the authoritative source retention_floor.
- The controller must also account for every required gateway's durable applied_cursor and installed snapshot generation.
- A gateway that cannot meet the retention window must be marked for a verified snapshot reinstall before its old replay dependency is discarded.
- Do not use wall-clock age as a substitute for global cursor continuity.

### Crash-safe ordering
- Persist a monotonic pending-retention intent containing source_id, stream key, target floor, source high_water and generation.
- Verify all required gateway installations/acknowledgements for the new floor.
- Publish a durable committed retention floor only when the recovery protocol can prove that replay requests below it must resnapshot.
- Execute an idempotent trim bounded by the committed cursor using the explicitly selected Redis 7.x reference policy.
- Reconcile intent, committed floor and actual first retained stream ID after restart; if they disagree, fail closed and force a snapshot/rebuild rather than guessing.
- Do not advance the committed floor beyond entries actually guaranteed to remain available.
- A crash at every transition must be covered by restart/retry tests.

### Consumer groups and PEL
- Enumerate known generation-scoped groups from a durable owner-controlled registry, not by assuming Redis group enumeration is the only source of truth.
- Define when an old generation is no longer required and who authorizes its cleanup.
- Explicitly test pending-entry behavior for the selected XTRIM reference mode.
- Do not grant XGROUP DESTROY or XDEL to runtime publisher/gateway identities.
- Group deletion and PEL cleanup require a separately authorized maintenance operation after a verified snapshot transition and retention horizon.

### Least-privilege ACL
- Publisher remains append/read-back only.
- Gateway remains read/group/ack/lease only.
- A dedicated retention identity receives only the exact stream key and exact trim/read/metadata commands proven necessary by tests.
- The retention identity must not receive broad key patterns, FLUSH*, CONFIG, arbitrary EVAL, XDEL, or group-destroy authority unless a separately reviewed, narrowly scoped operation proves it unavoidable.
- Password and TLS requirements remain independent per role; no credential reuse.

## 4. Required tests

Before enabling trim, add real Redis integration tests for:
1. Exact floor boundary: retain floor+1 through high_water; reject replay from below floor.
2. Empty stream and floor == high_water.
3. Trim at a cursor boundary with deterministic IDs of the form cursor-0.
4. Global cursor gaps and unrelated-series events.
5. Publisher behind the source floor and required fresh-snapshot recovery.
6. One fast gateway and one lagging gateway.
7. Gateway snapshot-generation transition while old pending entries exist.
8. XTRIM PEL reference semantics for each chosen trim mode.
9. Crash after intent, after floor commit, during trim, and after trim before completion acknowledgement.
10. Idempotent controller restart and reconciliation of actual first/last Redis IDs.
11. ACL negative tests proving publisher/gateway cannot trim and retention role cannot write arbitrary stream events or touch unrelated keys.
12. Replay and live consumer handoff concurrent with retention advancement.

Tests must use a real ephemeral Redis 7.x container with the exact ACL identities. Fake Redis tests remain useful unit tests but cannot be the sole acceptance evidence.

## 5. Current engineering disposition

| Area | Status |
|---|---|
| SQLite per-timeframe bar retention | 🟩 Implemented |
| SQLite global outbox retention, 100,000 events | 🟩 Implemented; floor and delete share transaction |
| Publisher detects source floor/gap and requires resnapshot | 🟩 Implemented |
| Redis deterministic append/read-back | 🟩 Implemented |
| Redis replay contiguous cursor and fail-closed behavior | 🟩 Implemented |
| Redis stream trim/retention controller | 🟥 Not implemented |
| Gateway floor coordination for trim | 🟥 Not implemented |
| Generation-group/PEL cleanup lifecycle | 🟥 Not implemented; old groups intentionally retained |
| Real Redis retention/failover acceptance on owner host | 🟥 Not verified |

**Decision:** no runtime patch is safe until the owner-controlled gateway inventory, authoritative floor publication and PEL policy are defined. Retaining Redis history for longer is safer than deleting events with an unproven cursor contract.

## 6. Relationship to Stage 1 and project progress

This audit improves the precision of the engineering backlog; it does not close a Stage 1 criterion.

- Stage 1 remains 30/40 = 75% provisional.
- Gate 10 remains 0/10 formally closed.
- Open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.
- Stages 2–6 remain NOT SCORED.
- Overall project percentage remains NOT SCORED.
- Indicator statuses remain unchanged: SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and shared hook are 🟨 foundation; Footprint 🟧 prototype; Heatmap and Liquidation Maps 🟥 not implemented.
- No Footprint/Heatmap visuals before owner references and scoped blueprint review.
- Delivery target remains 24 December 2026, planning target only.

## 7. Inspected code evidence

- backend/app/ohlcv_store.py — OUTBOX_MAX_EVENTS, transactional floor advancement, outbox read snapshot and resnapshot_required.
- backend/app/ohlcv_redis_config.py — exact publisher/gateway ACL command allowlists.
- backend/app/ohlcv_redis_publisher.py — deterministic XADD/read-back, source floor detection and resnapshot requirement.
- backend/app/ohlcv_redis_replay.py — checkpoint floor checks, contiguous cursor validation and all-or-resnapshot behavior.
- backend/app/ohlcv_redis_consumer.py — durable apply-before-ACK and generation-scoped group behavior.
- backend/app/ohlcv_redis_runtime.py — source publisher runtime construction and snapshot evidence validation.
- backend/app/ohlcv_redis_gateway_runtime.py — verified snapshot install and gateway checkpoint validation.

No runtime code, tests, dependencies, credentials, ACL, deployments, owner devices or paid services were changed.
