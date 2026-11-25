# Batches 90–95 — Durable WebSocket Delivery and Zero-Origin Acceptance Design

**Date:** 25 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Architecture:** Cloudflare Native / Zero-Origin  
**Status:** Owner-approved architecture; implementation specification only. No production acceptance is claimed.

## 1. Purpose and sequencing

This is one coordinated design package for the interdependent WebSocket work, not six disconnected mini-projects. It consolidates schema, API, event persistence, replay, acknowledgement, provider gate and E2E acceptance so the same invariants are applied end-to-end.

Implementation dependency chain:

`Batch 89 runtime gate → Batch 90 schema → Batch 91 API contract → Batch 92 event commit/replay → Batch 93 ACK/receipt/recovery → Batch 94 provider gate → Batch 95 public WSS/device E2E`.

Parallel work is permitted only for independent contract/test preparation. Runtime implementation must not skip its predecessor's acceptance gate.

## 2. Source audit baseline

The inspected synthetic proof currently:
- stores only `sequence:<series>` as the event cursor;
- accepts only the next sequence in a storage transaction;
- constructs the synthetic event after cursor acceptance;
- fans out to sockets after cursor acceptance;
- has no persisted event payload/digest replay source;
- accepts authenticated `ping` and rejects other authenticated messages;
- has no ACK, RESUME, or durable consumer receipt ledger;
- restores serialized socket attachments, which is not equivalent to replay/cursor durability.

The proof remains isolated, synthetic-only, localhost-origin restricted, with Worker deployment/preview disabled. These constraints must remain unchanged until a separately approved production acceptance decision.

## 3. Batch 90 — logical SQLite data model

The following is a logical schema contract. It deliberately does not prescribe an unverified Cloudflare SQL API call or migration syntax; concrete DDL must be validated in the pinned local runtime before implementation is accepted.

### 3.1 `series_state`

| Field | Logical type | Constraint / meaning |
|---|---|---|
| series_key | TEXT | Primary key; canonical validated series identity |
| generation_id | TEXT | Non-empty generation identifier |
| high_water | INTEGER | Last committed sequence; non-negative safe integer |
| retention_floor | INTEGER | Lowest sequence still replayable |
| updated_at_ms | INTEGER | Server commit timestamp |

Invariant: `0 <= retention_floor <= high_water`. State generation changes only through an explicit resnapshot/reset protocol, never silently during replay.

### 3.2 `series_events`

| Field | Logical type | Constraint / meaning |
|---|---|---|
| series_key | TEXT | Part of composite primary key |
| generation_id | TEXT | Part of composite primary key |
| sequence | INTEGER | Part of composite primary key; contiguous within generation |
| event_digest | TEXT | Canonical digest of exact serialized event bytes |
| payload | TEXT/BLOB | Bounded canonical event payload |
| committed_at_ms | INTEGER | Commit timestamp |

Primary key: `(series_key, generation_id, sequence)`.

A duplicate sequence with the same digest is idempotent only if its stored payload identity matches. A duplicate sequence with a different digest is a hard conflict. A sequence gap is rejected without changing state. Retention deletion and retention-floor advancement must be atomic with the relevant state update.

### 3.3 `consumer_receipts`

| Field | Logical type | Constraint / meaning |
|---|---|---|
| series_key | TEXT | Part of primary key |
| consumer_id | TEXT | Authenticated stable consumer identity |
| generation_id | TEXT | Generation acknowledged |
| committed_sequence | INTEGER | Monotonic acknowledged cursor |
| event_digest | TEXT | Digest at acknowledged cursor |
| receipt_version | INTEGER | Strictly increasing receipt revision |
| updated_at_ms | INTEGER | Server commit timestamp |

Primary key: `(series_key, consumer_id)`.

Consumer identity must come from authenticated server-side identity, not a client-supplied display label or synthetic fixed subject. Receipt state is durable and queryable after DO eviction.

### 3.4 Migration constraints

- Migration must be additive and versioned; never drop or rewrite existing ticket/sequence state without a tested compatibility plan.
- Existing `v1` migration and existing synthetic proof behavior must remain reproducible.
- Schema migration, initial series state, event commit, receipt commit and rollback behavior must be exercised in the actual local DO SQLite runtime.
- No production migration or Cloudflare resource creation is authorized by this document.

## 4. Batch 92 — atomic event commit and replay

### 4.1 Atomic commit algorithm

For each candidate event:
1. Validate canonical series, generation, bounded sequence and payload size before storage mutation.
2. Canonicalize the exact event envelope and compute its digest server-side.
3. Enter one database transaction.
4. Read series generation and high-water.
5. If the sequence equals high-water + 1, insert payload/digest and advance high-water in the same transaction.
6. If the sequence already exists with the same digest and payload identity, return idempotent duplicate without re-advancing state.
7. If the sequence exists with another digest, reject conflict.
8. If sequence is greater than high-water + 1, reject gap.
9. Commit; only after successful commit may socket fan-out begin.

If any statement fails, neither the event row nor high-water may become visible. Fan-out is never the source of truth.

### 4.2 Bounded replay contract

Request identity includes series, generation and an exclusive cursor. The server:
- rejects malformed/unsafe cursors;
- returns only contiguous rows after the cursor;
- applies a hard page-size and payload-byte ceiling;
- returns the next cursor and current high-water;
- returns explicit `resnapshot_required` when cursor is below retention floor or generation mismatches;
- never silently skips a missing sequence;
- never returns rows from another series or generation.

Replay page invariant: if page begins at cursor `c`, the first sequence is `c+1`; each following sequence increments by one; page end is no greater than committed high-water.

## 5. Batch 93 — ACK, durable receipt, RESUME

### 5.1 ACK validation

ACK must bind all of:
- authenticated consumer identity;
- canonical series;
- current generation;
- committed sequence;
- exact digest stored for that sequence;
- sequence not above high-water;
- receipt version expected by the transactional update.

Reject stale generation, unknown sequence, wrong digest, future cursor, malformed cursor, unauthenticated identity and receipt regression.

### 5.2 Receipt idempotency and concurrency

- Repeating the exact same ACK is idempotent and does not create a second logical advancement.
- A lower sequence is rejected as regression.
- Same sequence with a different digest is rejected.
- Competing ACK updates serialize through the same durable transaction/conditional write.
- Receipt version advances only when accepted state advances; version overflow is rejected.
- A receipt read after DO eviction must return the committed durable state.

### 5.3 RESUME state machine

1. Authenticate consumer and bind it to the requested series.
2. Compare requested generation and cursor with durable series state.
3. If generation differs or cursor is below retention floor, return `resnapshot_required` with current generation/high-water and no partial replay.
4. Otherwise return a bounded contiguous replay page.
5. Client applies events in sequence order and persists its local cursor only after successful application.
6. Client sends ACK for the highest fully applied event and its exact digest.
7. On disconnect, reconnect resumes from the last durable local cursor; duplicate replay is handled idempotently.

### 5.4 Hibernation and eviction

Socket attachments may contain only the minimum validated routing/session hints. Durable identity, generation, replay cursor and receipt truth must be recoverable from durable storage. Attachment restoration alone does not prove authorization continuity or replay continuity.

## 6. Batch 91 — provider-neutral API contract

Define provider-independent envelopes before provider-specific ingress:
- `series.identity`: canonical series key and generation;
- `snapshot`: generation, high-water, retention floor, canonical bars and provenance;
- `event`: series, generation, sequence, event time, bounded payload, digest;
- `replay.request/response`: cursor, page bound, next cursor, high-water, resnapshot reason;
- `ack.request/response`: consumer, series, generation, sequence, digest, receipt version;
- `error`: stable machine-readable code, retryability and correlation identifier.

Synthetic proof provenance must remain explicit and must never be presented as live market data. Provider adapters may not bypass canonical validation, digesting, event persistence, replay, or receipt rules.

## 7. Batch 94 — zero-cost provider gate

No provider is selected by assumption. Before integration, evidence must establish:
- lawful use and redistribution rights for the intended use;
- documented API/WebSocket protocol and authentication;
- actual free-tier limits, expiry and attribution obligations;
- compatibility with the Worker runtime and resource limits;
- no required card, paid upgrade, trial conversion or recurring subscription;
- acceptable rate limits and reconnect behavior;
- provenance and timestamp semantics.

If any criterion fails or is unclear, provider integration remains blocked. Do not substitute scraped feeds or mislabel synthetic fixtures.

## 8. Batch 95 — public WSS and device acceptance

Public WSS is not enabled until all prior gates pass. Required E2E:
- TLS and origin policy;
- authenticated browser handshake and unauthorized rejection;
- Android connection and reconnect;
- process death and network handover;
- no lost committed event across crash/reconnect;
- bounded replay and retention-floor resnapshot;
- generation mismatch handling;
- ACK/receipt persistence after DO eviction;
- duplicate delivery idempotency and strict sequence order;
- quota, payload and connection limits;
- backup/restore and operational recovery evidence.

Gate 25 and Gate 36 remain open until their full acceptance evidence is attached to the tested commit.

## 9. Combined acceptance matrix

| ID | Acceptance condition | Batch | Status |
|---:|---|---:|---|
| D01 | Existing v1 migration remains compatible; new schema initializes | 90 | 🟥 OPEN |
| D02 | Event payload, digest and high-water commit atomically | 92 | 🟥 OPEN |
| D03 | Identical duplicate is idempotent; conflicting digest rejected | 92 | 🟥 OPEN |
| D04 | Sequence gap and transaction failure do not advance state | 92 | 🟥 OPEN |
| D05 | Fan-out occurs only after durable commit | 92 | 🟥 OPEN |
| D06 | Replay is contiguous, bounded and generation-aware | 92 | 🟥 OPEN |
| D07 | Retention-floor cursor returns explicit resnapshot | 92/93 | 🟥 OPEN |
| D08 | ACK binds authenticated identity, series, generation, sequence and digest | 93 | 🟥 OPEN |
| D09 | Receipt is durable, monotonic, idempotent and race-safe | 93 | 🟥 OPEN |
| D10 | RESUME/reconnect survives hibernation and DO eviction | 93 | 🟥 OPEN |
| D11 | Provider passes legal, free-tier and runtime compatibility gates | 94 | 🟥 OPEN |
| D12 | Public WSS/browser/Android/restore E2E passes | 95 | 🟥 OPEN |

No item is marked complete by design documentation alone.

## 10. Required failure-injection tests

- Force failure between event insert and state update: transaction must roll back both.
- Force failure after durable commit but before fan-out: replay must recover the event.
- Submit same sequence/same digest twice: one logical event.
- Submit same sequence/different digest: conflict and no state mutation.
- Submit gap, negative, unsafe or oversized sequence: reject without mutation.
- Replay at exact retention floor, below floor, at high-water and beyond high-water.
- Race two ACKs for same receipt version with same and conflicting cursors.
- Recreate DO after eviction and query event log and receipt.
- Reconnect after client process death and network handover.
- Verify all failure responses are bounded and do not leak identity or payload secrets.

## 11. Execution discipline and zero-cost boundary

- Batch 89 must provide actual local runner evidence before runtime changes.
- Use the repository lockfile and pinned test dependencies; capture Node/npm versions and exact commit SHA.
- Run independent read-only audits and test design in parallel; serialize writes to shared files and storage migrations.
- Never commit unexecuted runtime code as tested.
- Never touch `main`, deploy, create Cloudflare resources, provision paid runners or use paid data.
- A missing, skipped, timed-out or logless test is OPEN, not PASS.
- CI status must be verified from the exact commit; empty status is UNKNOWN.
- Indicator calculations and UI are outside this backend work package and receive zero implementation credit.

## 12. Current state

This document consolidates the next dependent batches into one implementation contract. It is **design evidence only**:
- Batch 89: 🟨 execution gate documented; runtime evidence pending.
- Batch 90–93: 🟦 detailed implementation contract; runtime implementation not accepted.
- Batch 94–95: 🟥 external/provider and public E2E gates remain blocked.
- Gate 25 and Gate 36: 🟥 OPEN.
- No runtime source, deployment, Cloudflare resource or `main` branch is changed by this design.
