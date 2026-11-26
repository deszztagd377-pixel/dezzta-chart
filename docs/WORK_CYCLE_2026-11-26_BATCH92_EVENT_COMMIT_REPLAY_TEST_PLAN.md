# DEZZTA CHART — Batch 92 Atomic Event Commit and Replay Test Plan

**Date:** 26 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Status:** TEST DESIGN ONLY — Batch 91 formal acceptance remains a prerequisite for Batch 92 runtime implementation.  
**Architecture:** Cloudflare Native / Zero-Origin; synthetic proof only; ZERO COST.

## 1. Purpose

Prepare deterministic Batch 92 tests without changing runtime behavior or bypassing Batch 91 acceptance. The current Worker accepts a sequence by updating the legacy `sequence:<seriesKey>` storage key, then constructs an event and fans it out. The new SQLite schema already contains logical `series_state` and `series_events` tables, but the event path does not yet use them as the durable source of truth.

Batch 92 must make event payload, canonical digest and high-water atomic. Fan-out must happen only after commit. Replay must read the persisted log, not reconstruct an event from a cursor.

## 2. Existing state to preserve

- Existing schema migration version 1 and legacy `sequence:<seriesKey>` / `ticket:<digest>` keys must remain compatible.
- Existing canonical Batch 91 event envelope and digest function must be reused; do not introduce a second digest representation.
- Series generation is explicit. A generation mismatch must not silently reset or reinterpret sequence state.
- Current synthetic proof remains synthetic-only; providerConnected=false; no live provider or production route.
- No production deployment, resource creation, paid service, application `main` edit or destructive retention action.

## 3. Proposed storage transaction contract

One SQLite transaction for each accepted event:
1. Validate exact canonical synthetic series identity, generation ID, canonical unsigned sequence, event envelope and maximum payload bytes before mutation.
2. Build the canonical event and compute the server-side digest using the Batch 91 canonical digest input.
3. Read `series_state` for (series_key, generation_id) and the current high-water/retention floor.
4. First event for a new series may initialize the state only through a documented, compatibility-safe initialization path; do not infer a new generation from missing data without an explicit rule.
5. For `sequence = high_water + 1`, insert `series_events` row and update `series_state.high_water` in the same transaction.
6. For exact duplicate sequence, return idempotent duplicate only when both stored digest and canonical payload identity match.
7. For same sequence with different digest or payload, reject hard conflict without state mutation.
8. For sequence gap, stale sequence, unsafe integer, wrong generation, oversized payload or invalid digest, reject without mutation.
9. After transaction commit succeeds, and only then, fan out the exact persisted canonical payload.
10. If fan-out fails after commit, leave the event committed and recoverable by replay.

The transaction must not write the legacy cursor first and the payload later. The durable row and high-water are the atomic source of truth.

## 4. Deterministic failure-injection matrix

| ID | Scenario | Required assertion |
|---|---|---|
| B92-T01 | Valid next event | Event row and high-water commit together |
| B92-T02 | Failure after event INSERT, before state UPDATE | Transaction rollback leaves neither row nor advanced high-water |
| B92-T03 | Failure after state UPDATE, before transaction commit | Transaction rollback leaves neither row nor advanced high-water |
| B92-T04 | Failure after commit, before fan-out | Event remains replayable; no duplicate commit on retry |
| B92-T05 | Same sequence, same digest and payload | Idempotent duplicate; exactly one logical row |
| B92-T06 | Same sequence, different digest | Conflict; original row and high-water unchanged |
| B92-T07 | Same sequence and digest but payload bytes differ | Conflict; digest alone cannot mask payload identity mismatch |
| B92-T08 | Sequence gap | Reject; no row and no high-water mutation |
| B92-T09 | Sequence regression / stale sequence | Reject; no mutation |
| B92-T10 | Wrong generation | Explicit generation mismatch; no cross-generation replay |
| B92-T11 | Invalid canonical series or malformed cursor | Fail closed before transaction mutation |
| B92-T12 | Payload exceeds hard byte ceiling | Reject before persistence |
| B92-T13 | Replay from cursor c | First returned sequence is c+1 and every row is contiguous |
| B92-T14 | Replay page reaches page-size or byte ceiling | Return bounded page with correct next cursor |
| B92-T15 | Cursor equals high-water | Empty page, stable high-water and no fabricated event |
| B92-T16 | Cursor above high-water | Explicit invalid/future cursor response; no silent clamp |
| B92-T17 | Cursor below retention floor | Explicit resnapshot_required with generation, high-water and floor |
| B92-T18 | Missing row inside claimed committed range | Integrity failure; never skip the hole |
| B92-T19 | Series A replay request against series B | No cross-series rows |
| B92-T20 | Durable Object reconstruction after eviction | Event rows and high-water remain queryable |
| B92-T21 | Concurrent commits for same series | Exactly one next-sequence winner; no duplicate/gap state |
| B92-T22 | Concurrent commits for separate series | Independent progress without cross-series contamination |

## 5. Replay response contract

Replay must return:
- exact `seriesKey` and `generationId`;
- `fromCursor`, `throughCursor`, count, current high-water and retention floor;
- ordered canonical event payloads;
- next cursor / completion cursor;
- explicit `resnapshot_required` when generation differs or requested cursor is below retention floor.

A page is valid only when the first event is cursor+1, each subsequent event increments by exactly one, and the final event is not above the committed high-water. Page size and total serialized bytes have hard ceilings. No cursor jump or missing event may be silently accepted.

## 6. Runtime test placement

- Extend `cloudflare/proof/worker.node-test.mjs` for pure validation, idempotency and conflict behavior.
- Extend `cloudflare/proof/worker.durable-object.runtime.mjs` for actual SQLite transaction rollback, concurrency, eviction and replay behavior.
- Extend `cloudflare/proof/worker.miniflare-test.mjs` for the pinned workerd runtime's public Worker-to-DO path and post-commit fan-out.
- Keep failure injection test-only; no public request field may select an arbitrary failure point.
- Add exact assertions against persisted SQL rows and high-water after every injected failure.

## 7. Acceptance gate

Batch 92 may be marked accepted only when:
- Batch 91 formal acceptance has been explicitly recorded.
- Every required test above is implemented or formally dispositioned with a justified rationale.
- Exact-head CI 4/4 passes on the Batch 92 source/test SHA.
- CI logs prove rollback, replay, concurrency and eviction behavior in the pinned local Durable Object runtime.
- Fan-out occurs strictly after transaction commit.
- No synthetic fixture is described as live provider data.
- No application `main`, production deployment or paid resource is touched.

## 8. Current disposition

**Batch 92 runtime implementation: NOT STARTED / BLOCKED by Batch 91 formal acceptance.**  
**Batch 92 test design: PREPARED in this document.**  
**No runtime source or schema migration was changed by this work cycle.**
