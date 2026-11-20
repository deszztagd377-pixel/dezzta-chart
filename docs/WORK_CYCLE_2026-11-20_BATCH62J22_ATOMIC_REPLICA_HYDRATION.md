# Work Cycle 62J-22 — atomic replica hydration consistency

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Base commit:** 3d93cbcd9a73a9d901b0407094e8bed462401b16  
**Scope:** SQLite replica hydration correctness; no production route activation, deployment, paid infrastructure or changes to main.

## Finding

The existing hydrate_replica_pipeline() obtained its checkpoint through checkpoint() and its bars through load_bars(). Those methods each opened a separate SQLite connection and read transaction. A replica consumer could commit a new event between the two reads. In that interleaving, hydration could combine the old applied_cursor with bars that already included the new event.

That state is unsafe: the in-memory read model and durable cursor would no longer represent the same committed snapshot. It could distort the snapshot/live boundary and make replay or duplicate suppression decisions incorrect.

## Change

1. Added SQLiteOhlcvReplicaStore.load_snapshot().
2. The method opens one SQLite read transaction, reads the complete replica checkpoint, reads all retained bars from the same WAL snapshot, materializes the result, then commits the read transaction.
3. hydrate_replica_pipeline() now consumes only this atomic result and validates non-negative integer cursor/floor values before replacing the in-memory pipeline.
4. Added regression coverage proving hydration does not use the former independent checkpoint/bar reads.
5. Added fail-closed coverage for an empty replica without a verified checkpoint.

## Consistency calculation

The invariant is: bars_snapshot and checkpoint_snapshot must both be observed at the same SQLite transaction snapshot T.

Previously, the reads could occur at T1 and T2 with a consumer commit C between them. The checkpoint could describe state before C while the bars included C. The new explicit read transaction ensures C is either visible to both reads or neither.

## Validation boundary

- Source SQLite remains the default WebSocket path.
- This batch does not wire the Redis consumer into FastAPI lifespan.
- This batch does not choose production snapshot distribution or provision Redis TLS/ACL credentials.
- No two-ASGI acceptance is claimed.
- No Vercel/Cloudflare deployment, paid service or Termux work.
- All ten project gates remain 🟧 ORANGE / OPEN; no gate is closed by this code change.
- Indicator status is unchanged; see docs/INDICATOR_PROGRESS_LEDGER.md.

CI must pass on the exact resulting commit before the code is marked verified.
