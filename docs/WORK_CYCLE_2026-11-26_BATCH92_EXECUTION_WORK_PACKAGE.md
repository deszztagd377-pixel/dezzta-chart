# DEZZTA CHART — Batch 92 Execution Work Package

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**State:** IN PROGRESS — identity and atomic persistence slice is exact-head CI GREEN; replay/retention and resume remain YELLOW  
**Cost policy:** ZERO COST; no new paid resources or production deployment.

## Operating rule for the active dashboard

No active work item is displayed as RED. Work not yet verified is YELLOW / IN PROGRESS with an owner action, dependency, and exit criteria. GREEN is reserved for a completed implementation with passing relevant tests and exact-head CI evidence. This is a reporting convention, not a change to technical truth.

## Batch 92 workstreams

| ID | Workstream | Active state | Dependency | Exit criteria |
|---|---|---|---|---|
| B92-01 | SQLite schema v2/v3 + immutable identity registry | GREEN / CI VERIFIED | Batch 91 accepted | Fresh and existing-v2 migration, digest hydration, immutable triggers, snapshot registration, legacy KV preservation and DO eviction tests pass |
| B92-02 | Legacy cursor bootstrap and cutover | YELLOW / PARTIAL | B92-01 | Add seeded-legacy-cursor and interrupted-bootstrap regression; prove SQLite authority after initialization and no dual-write |
| B92-03 | Canonical event commit | GREEN / CI VERIFIED | B92-01/02 | Canonical event/digest + high-water atomic transaction, stable retry, changed timestamp conflict, identity conflict, gap and concurrency tests pass |
| B92-04 | Replay and retention | YELLOW / NOT IMPLEMENTED | B92-03 | Ordered cursor-exclusive pages; <=100 events and <=65,536 UTF-8 bytes; explicit generation/retention outcomes; compaction and failure tests |
| B92-05 | WebSocket subscribe/resume integration | YELLOW / PARTIAL | B92-04 | Snapshot when no cursor; replay when cursor is valid; atomic replay-to-live handoff; explicit resnapshot for expired/mismatched cursors |
| B92-06 | Failure and concurrency tests | YELLOW / PARTIAL | B92-01..05 | Add rollback/fan-out failure, seeded bootstrap, retention boundary, byte-page boundary and replay/live race tests |
| B92-07 | Exact-head CI | GREEN / 4 OF 4 SUCCESS | Current source/test HEAD | Automated Tests, CodeQL, secret audit and OCI ARM64 all terminal-success on the same tested source/test SHA |

## Required implementation sequence

**Exact-head CI closure (26 November 2026):** commit `0657efc142299753079823bb6d98aa12bdcf517f` passed all four required workflows: Automated Tests run 45851007304, CodeQL run 45851007316, Full Git History Secret Audit run 45851007271 and OCI ARM64 run 45851007421. Verified runtime evidence: Worker Node 33/33, Miniflare/workerd 1/1, Durable Object 18/18 (including migration of an existing v2 identity row to v3 and lazy digest hydration), frontend 35 files / 331 tests, backend 1,435 passed / 1 skipped / 6 warnings, plus frontend/backend builds, backend container smoke and vulnerability scan. The skipped backend test is the optional Redis TLS integration fixture, not a passing test. CI GREEN closes the initial identity + persistence slice only; replay/retention, full bootstrap fault cases and WebSocket replay handoff remain YELLOW.


1. Preserve application schema v2 as the immutable identity registry baseline, then apply additive schema v3 for `identity_digest`. Do not alter Wrangler class-creation migration tags. The v3 migration must handle an existing v2 table both with and without the digest column, preserve existing identity JSON, and permit only one-time digest hydration for legacy rows.
2. Maintain `series_identity` with one immutable canonical identity per `series_key`. Store canonical fixed-field-order JSON and its SHA-256 digest. Reject a different identity for an already registered key. Register identity on snapshot before a client can subscribe to that series.
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

The 45-case test inventory remains a specification, not a pass count. The current exact-head CI verifies the identity/persistence slice. Replay-specific page-byte, retention, replay/live race and additional failure-injection cases remain to be implemented and executed. Record run IDs and exact tested SHA. Documentation-only commits are not evidence of runtime CI.

## Cost and platform guardrail

No new namespace, database, queue, provider, external service, paid plan, or deployment is authorized. The repository already uses SQLite-backed Durable Objects; increased persisted event volume may still affect usage-based storage/billing. Measure expected retained bytes per series before enabling long retention. If the zero-cost allowance cannot be demonstrated from the account's current quota and usage, keep runtime rollout disabled rather than assuming it is free.

## Schedule control to 24 December 2026

Reserve the first implementation window for B92-01 through B92-03, the second for B92-04/05, the third for failure injection and exact-head CI, and retain the final buffer for fixes and end-to-end verification. Do not start ACK/RESUME or public WSS until replay and persistence invariants pass. The date is a target, not a completion claim.
