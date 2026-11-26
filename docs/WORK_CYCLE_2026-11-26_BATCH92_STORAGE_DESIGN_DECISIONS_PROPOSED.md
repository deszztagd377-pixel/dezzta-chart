# DEZZTA CHART — Batch 92 Storage Design Decision Record (Proposed)

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline:** Batch 91 runtime source/test SHA `2d0d7e9a2bf1190961126105d65f77d9926e6789`  
**Scope:** architecture decision proposal only; no runtime/schema/dependency/deployment changes.  
**Cost:** ZERO COST.

## Decision DRAFT-01 — One active generation per series key

**Recommendation:** retain the v1 `series_state` primary key on `series_key` and enforce exactly one active generation for a given series key. The current protocol contract declares `GENERATION_ID = "synthetic-v1"`; the existing `series_state` schema is already shaped around one active generation. Historical event rows may remain keyed by generation, but a generation transition must be an explicit administrative/protocol operation and must not be inferred from a missing state row.

**Reasoning:** adding concurrent generations would contradict the current state-table key and require a schema migration plus changes to snapshot, subscription, cursor and replay routing. No current synthetic proof requirement demonstrates a need for concurrent generations. Avoiding a schema migration reduces risk and preserves the additive v1 schema.

**Required invariant:** for a given `series_key`, every accepted event belongs to the active `generation_id`; any request naming another generation is rejected without mutation. A future generation rotation must be separately versioned and tested.

## Decision DRAFT-02 — Legacy cursor bootstrap and cutover

**Recommendation:** perform a one-time, idempotent bootstrap under the Durable Object's existing protocol-exclusive queue, before snapshot watermark reads or event writes. Read legacy `sequence:<seriesKey>`; validate it as an integer in [50, 1,000,000,000]; if absent, use snapshot watermark 50. Insert initial `series_state` with the fixed `synthetic-v1` generation and imported high-water. If a state row already exists, never lower or overwrite its high-water. If an existing row has another generation or invalid bounds, fail closed.

The KV read and SQLite transaction are not a cross-store atomic transaction. Safety therefore depends on: (a) serializing every path that can mutate or read the series cursor through the same DO-local protocol queue during cutover; (b) making bootstrap idempotent; and (c) ensuring no legacy cursor writer remains active outside the new transaction path after the code cutover. A crash between KV read and SQL insert is safe because retry repeats the import; a crash after SQL insert is safe because retry sees the state row.

**Cutover:** SQLite becomes the sole source of truth after bootstrap. The legacy KV cursor is read only during bootstrap and must not be dual-written after the SQLite event transaction is enabled. Snapshot, subscribe, emit, and replay must all use SQLite high-water after cutover. Ticket KV records remain separate and unchanged.

**Important:** this is a source-level cutover performed by a single Worker revision, not a rolling multi-version deployment plan. Do not deploy a mixed old/new writer fleet.

## Decision DRAFT-03 — Atomic event commit

One SQLite transaction must:
1. Read and validate the active series state and generation.
2. Validate next sequence = high-water + 1 (or exact duplicate semantics).
3. Insert the canonical serialized event payload and SHA-256 digest.
4. Update `series_state.high_water` and `updated_at_ms`.
5. Commit both writes together.

No socket send, network await, digest computation, or external operation belongs inside the SQL transaction. Build and canonicalize the envelope before entering the synchronous transaction. Fan-out only the canonical payload read from/identical to the committed row, after commit. Fan-out failure must not roll back or erase the committed event.

## Decision DRAFT-04 — Replay response byte budget

The 8,192-byte database payload ceiling is per event and is not a safe replay response ceiling. Proposed replay limits: maximum 100 events per page and maximum 64 KiB UTF-8 serialized response bytes, including envelope fields, JSON punctuation, commas and metadata. A single stored event that cannot fit in an otherwise empty page must produce an explicit non-retryable `event_exceeds_page_budget` error and preserve the cursor; never return an empty page with `hasMore=true`.

The exact 64 KiB limit is a conservative application-level design proposal, not a Cloudflare platform limit. Confirm against the Worker response budget and client contract before implementation.

## Decision DRAFT-05 — Canonical bytes and duplicate semantics

Reuse the existing `createSyntheticUpdateEnvelope` and canonical digest implementation. Serialize once with a deterministic canonical representation before SQL insert. Store those exact bytes as TEXT. On duplicate sequence, require both digest equality and exact payload-byte equality; same sequence with different bytes is a conflict. Do not recompute an alternate digest or rebuild an event from a sequence during replay.

## Test implications

In addition to B92-T01..T30, verify:
- State bootstrap at absent, 50, 51, and maximum valid legacy cursor.
- Invalid legacy values fail closed without SQL writes.
- Concurrent bootstrap calls converge to one state row.
- Snapshot, subscribe, emit and replay cannot observe mixed KV/SQLite watermarks.
- A simulated failure after bootstrap read but before SQL insert is recoverable on retry.
- A state row with a generation other than `synthetic-v1` fails closed.
- A committed event survives fan-out exceptions and DO eviction.
- Byte accounting matches `new TextEncoder().encode(JSON.stringify(response)).byteLength` exactly.

## Status and gate

These are **proposed decisions**, not owner-approved protocol changes. They do not close Batch 91 formal acceptance. Batch 92 runtime remains gated until the owner explicitly accepts Batch 91. This document is architecture preparation only; no code or schema has been modified.
