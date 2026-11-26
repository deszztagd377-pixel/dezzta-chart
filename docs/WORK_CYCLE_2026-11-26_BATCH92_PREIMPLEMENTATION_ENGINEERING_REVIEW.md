# DEZZTA CHART — Batch 92 Pre-Implementation Engineering Review

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited HEAD:** `8c94b27e5cccb2de64417aad38829dbf86086ebe`  
**Scope:** read-only source/design audit; no runtime code, schema, dependencies, deployment, or production settings changed.  
**Cost:** ZERO COST.

## 1. Verified source facts

- `cloudflare/proof/worker.mjs` still accepts the next sequence through `acceptNextSequence()`, which writes only the legacy `sequence:<seriesKey>` KV key.
- The emitted event is constructed after that cursor transaction; event payload and digest are not persisted atomically with the high-water mark.
- The current fan-out iterates authenticated sockets after cursor acceptance. A process interruption between cursor advancement and fan-out therefore has no durable event row to replay.
- SQLite schema version 1 already creates `series_state`, `series_events`, and `consumer_receipts`; the event and receipt tables are not yet the runtime source of truth.
- `series_events` has a primary key on (series_key, generation_id, sequence), a 64-character lowercase hex digest constraint, and an 8,192-byte payload ceiling.
- `series_state` has `series_key` as its sole primary key and stores one active `generation_id` plus high-water and retention floor.
- Existing legacy KV cursor and ticket keys are intentionally preserved by the additive migration.

## 2. Design gaps that must be resolved before Batch 92 runtime edits

### B92-D01 — Legacy cursor handoff

The new SQLite state begins empty while legacy `sequence:<seriesKey>` may already be at 50 or higher. Batch 92 must define a one-time, race-safe bootstrap rule that imports the legacy cursor into `series_state` before accepting any new event. It must never initialize high-water to zero or 50 when the preserved legacy cursor is greater. The bootstrap must be idempotent and tested across DO reconstruction.

### B92-D02 — Generation cardinality

The current schema permits only one `series_state` row per `series_key`, while event rows are generation-keyed. Confirm the intended invariant explicitly: one active generation per series key, with prior generations retained only as immutable event history; or concurrent generation rows are required, in which case a later schema migration is needed. Do not silently change the schema or overwrite a generation.

### B92-D03 — Atomicity boundary

The implementation must use one SQLite transaction for event insert and high-water update. The legacy KV cursor must not be advanced separately before or after that commit as a second source of truth. Specify how the legacy cursor is treated after cutover (read-only compatibility mirror or retired read path); avoid a dual-write that can diverge after a crash.

### B92-D04 — Replay byte accounting

The 8,192-byte SQL constraint applies to each stored payload. Replay pages also need a separate maximum serialized response-byte limit, deterministic accounting including JSON framing/metadata, and a forward-progress rule when the next single event cannot fit. Do not return an empty nonterminal page that causes clients to retry forever.

### B92-D05 — Digest/payload canonical identity

Use the Batch 91 canonical digest function and exact canonical envelope bytes. Define whether idempotency compares the canonical serialized payload as well as the digest; if so, ensure serialization is deterministic and test that the same logical envelope cannot produce byte drift due to object-key order or number formatting.

## 3. Additional deterministic cases to add to the 22-case Batch 92 matrix

| ID | Scenario | Required assertion |
|---|---|---|
| B92-T23 | Bootstrap SQLite state from legacy cursor 50 | State high-water is 50 before sequence 51 is accepted |
| B92-T24 | Bootstrap from legacy cursor greater than 50 | Exact cursor is preserved; no rewind or replay collision |
| B92-T25 | Repeat bootstrap after DO eviction | Idempotent; no state reset or duplicate event |
| B92-T26 | Bootstrap races with first event | Exactly one serialized initialization; event sequence remains contiguous |
| B92-T27 | Active generation changes | Explicit policy enforced; no silent overwrite or cross-generation replay |
| B92-T28 | Replay page next event exceeds remaining byte budget | Explicit bounded response/error with forward-progress semantics |
| B92-T29 | Event transaction succeeds but fan-out throws | Persisted row and high-water remain committed; replay returns that exact event |
| B92-T30 | Legacy KV and SQLite cursor intentionally disagree after cutover | SQLite source-of-truth policy is enforced; no fallback that rewinds committed state |

## 4. Recommended implementation order after formal Batch 91 acceptance

1. Freeze and record the generation-cardinality and legacy-cursor handoff decisions.
2. Add test-only deterministic failure injection around SQL insert, high-water update, transaction commit, and post-commit fan-out.
3. Implement one transaction boundary for payload + digest + high-water.
4. Add bounded ordered replay with retention-floor and integrity-hole behavior.
5. Run Node unit tests, pinned Miniflare/workerd tests, and actual Durable Object runtime tests.
6. Verify exact-head CI 4/4 on the new source/test SHA before acceptance.

## 5. Gate and status

- Batch 91 implementation: source/test checkpoint exists and exact-source CI evidence is documented.
- Batch 91 formal acceptance: still requires owner review of canonical fields, digest encoding, route mapping, and synthetic-only compatibility.
- Batch 92 runtime implementation: **NOT STARTED / BLOCKED** until Batch 91 formal acceptance is explicitly recorded.
- Batch 92 test design: existing 22 cases plus the 8 supplemental cases above are prepared; this is design evidence, not runtime proof.
- No source/test completion, CI pass, WebSocket production readiness, or project completion is inferred from this audit.
- `main` remains untouched. No paid service, provider feed, deployment, Cloudflare resource creation, production secret, broker/order endpoint, or destructive retention operation was used.
- Planning target remains approximately **24 December 2026**, not a guaranteed release date.
