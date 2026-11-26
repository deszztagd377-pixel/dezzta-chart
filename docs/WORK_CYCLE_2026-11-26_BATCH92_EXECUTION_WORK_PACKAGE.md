# DEZZTA CHART — Batch 92 Execution Work Package

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**State:** READY FOR IMPLEMENTATION — active work is YELLOW until exact-head CI is green  
**Cost policy:** ZERO COST; no new paid resources or production deployment.

## Operating rule for the active dashboard

No active work item is displayed as RED. Work not yet verified is YELLOW / IN PROGRESS with an owner action, dependency, and exit criteria. GREEN is reserved for a completed implementation with passing relevant tests and exact-head CI evidence. This is a reporting convention, not a change to technical truth.

## Batch 92 workstreams

| ID | Workstream | Active state | Dependency | Exit criteria |
|---|---|---|---|---|
| B92-01 | SQLite schema v2 + immutable identity registry | YELLOW / IMPLEMENTED — VERIFY | Batch 91 accepted | Miniflare migration, trigger immutability, v1 rows and legacy KV preservation pass |
| B92-02 | Legacy cursor bootstrap and cutover | YELLOW / PARTIAL | B92-01 | Serialized first-write bootstrap; high-water never decreases; SQLite sole authority after state exists; no dual-write |
| B92-03 | Canonical event commit | YELLOW / IMPLEMENTED — VERIFY | B92-01/02 | One synchronous SQLite transaction inserts event+digest and advances high-water; fan-out only after commit; idempotent retry proven |
| B92-04 | Replay and retention | YELLOW / READY | B92-03 | Ordered cursor-exclusive pages; bounded count and bytes; explicit generation and retention errors; no silent cursor jump |
| B92-05 | WebSocket subscribe/resume integration | YELLOW / READY | B92-04 | Snapshot when no cursor; replay when cursor is valid; explicit resnapshot when cursor is expired or generation differs |
| B92-06 | Failure and concurrency tests | YELLOW / ACTIVE | B92-01..05 | Update stale key-only Node tests; then prove rollback, duplicate, conflicting duplicate, gap, fan-out failure, eviction and concurrent emit |
| B92-07 | Exact-head CI | YELLOW / FIRST RUN 3/4 | Runtime implementation | Automated Tests, CodeQL, secret audit and OCI ARM64 all terminal-success on the same tested source/test SHA |

## Required implementation sequence

**First implementation CI result (26 November 2026):** commit `cd5f08fc17c8ab35b95f26d5b591f7ed992bc746` passed CodeQL, full-history secret audit and OCI ARM64. Automated Tests failed at two Node unit tests that still submitted the retired `{seriesKey, sequence}` request shape; later Miniflare/SQLite runtime suites were skipped by fail-fast. The first Node test correction exposed two more tests that assumed the retired KV-only cursor/fan-out behavior. Those tests now assert that writes fail closed without SQLite, the legacy cursor does not advance, and no WebSocket fan-out occurs before a durable commit. No implementation status is GREEN until the corrected exact-head CI passes.


1. Add schema v2 in the existing application migration function. Do not alter Wrangler class-creation migration tags. Preserve schema v1 and the existing `series_state`, `series_events`, and `consumer_receipts` tables.
2. Add `series_identity` (or an equivalently named registry) with one immutable canonical identity per `series_key`. Store canonical fixed-field-order JSON and an identity digest. Reject a different identity for an already registered key.
3. Under the existing per-DO protocol serialization queue, read the legacy `sequence:<seriesKey>` value, validate it, and bootstrap SQLite state once. Do not perform asynchronous KV writes and SQLite writes as a pretend cross-store transaction. Once SQLite state exists, it is authoritative; legacy KV is read only for bootstrap and must not be dual-written.
4. Require full canonical `series` identity and stable `emittedAtNs` on the authenticated synthetic proof emit path. Validate the key/identity relation. Stable timestamp input makes a retried request reproduce exactly the same canonical event bytes.
5. Compute the canonical Batch 91 envelope and digest before entering `transactionSync`. In one synchronous SQLite transaction, re-read the series state, validate generation and next sequence, compare any existing row for exact digest AND exact payload bytes, insert the event row, and advance high-water. Roll back the entire transaction on any failure.
6. Only after commit, fan out the exact persisted payload string. A socket send failure must not roll back the committed event or suppress delivery attempts to other eligible sockets.
7. Implement replay as a read-only ordered query for sequences strictly greater than the supplied cursor. Return page metadata including generation, next cursor, high-water and retention floor. A cursor below the retained boundary returns an explicit resnapshot-required result; a cursor above high-water is rejected. Never silently advance a cursor.
8. Subscribe with no cursor produces a canonical snapshot. Subscribe with a valid cursor produces replay pages and then transitions to live fan-out under the same protocol serialization boundary so there is no replay/live gap or duplicate ordering ambiguity.

## Quantitative limits and rationale

- Per-event persisted payload ceiling remains 8,192 UTF-8 bytes, matching the existing schema constraint.
- Replay page hard cap: 100 events AND 65,536 UTF-8 bytes for the complete serialized response, including envelope and metadata.
- Therefore the actual page count is the smaller of 100 and the largest prefix that fits 65,536 bytes. At the 8,192-byte per-event ceiling, a page can hold at most 7 maximum-size events once framing/metadata is included; implementation must measure actual UTF-8 byte length, not estimate by JavaScript string length.
- An event that cannot fit an otherwise empty page returns a stable explicit error; it must not return an empty page with `hasMore=true`.
- Keep the current snapshot cap of 50 bars unchanged in this batch.

## Correctness invariants

- A sequence is committed at most once per `(series_key, generation_id)`.
- High-water advances if and only if the corresponding event row commits.
- A retry is idempotent only if both digest and exact canonical payload bytes match the committed row; otherwise return a sequence conflict.
- Event persistence precedes fan-out.
- Replay order is strictly ascending and cursor-exclusive.
- Generation mismatch and retention expiry are explicit protocol outcomes.
- Identity is registered once and immutable; no client-specific identity variants.
- All WebSocket state needed after hibernation is reconstructed from storage/serialized attachments, not process memory alone.

## Test and release gates

The 40-case test inventory remains a specification, not a pass count. Add the stable-`emittedAtNs` retry case and a byte-boundary page test. Run Node proof, Miniflare/workerd, Durable Object runtime and the complete repository workflow set. Record run IDs and exact tested SHA. Documentation-only commits are not evidence of runtime CI.

## Cost and platform guardrail

No new namespace, database, queue, provider, external service, paid plan, or deployment is authorized. The repository already uses SQLite-backed Durable Objects; increased persisted event volume may still affect usage-based storage/billing. Measure expected retained bytes per series before enabling long retention. If the zero-cost allowance cannot be demonstrated from the account's current quota and usage, keep runtime rollout disabled rather than assuming it is free.

## Schedule control to 24 December 2026

Reserve the first implementation window for B92-01 through B92-03, the second for B92-04/05, the third for failure injection and exact-head CI, and retain the final buffer for fixes and end-to-end verification. Do not start ACK/RESUME or public WSS until replay and persistence invariants pass. The date is a target, not a completion claim.
