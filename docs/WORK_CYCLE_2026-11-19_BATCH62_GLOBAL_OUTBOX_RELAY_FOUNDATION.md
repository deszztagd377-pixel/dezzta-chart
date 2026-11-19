# Batch 62 — Global OHLCV outbox relay foundation

**Parent:** `45a887ae65e556d4457602467c4963f8d195d270`  
**Branch:** `phase-2/market-data-foundation`  
**Scope:** global outbox reader + regression tests + architecture decision and indicator ledger reconciliation.  
**Cost:** ZERO COST • no deployment • no Termux • `main` untouched.

## Change set

1. Added `SQLiteOhlcvStore.read_outbox_batch(after_cursor, limit)`.
   - Reads global outbox events across all series in monotonic cursor order.
   - Reads retention floor, high-water and event page in one SQLite read transaction.
   - Returns stable event ID, cursor, decoded payload and bounded pagination state.
   - Returns explicit `resnapshot_required` for expired/ahead cursors.
   - Does not weaken exact-series `replay_outbox()`.
2. Added regression tests for mixed-series ordering, pagination, high-water progression, retention expiry, ahead cursors and input validation.
3. Added cross-instance fan-out ADR: SQLite outbox remains source of truth; Redis Streams is a future relay/fan-out transport with per-instance consumer groups and at-least-once deduplication.
4. Reconciled the current dashboard and complete indicator ledger. No indicator completion credit or Gate closure is awarded.

## Acceptance boundary

This is relay groundwork, not a distributed relay implementation. Redis publishing, checkpoint idempotency, consumer groups, pending recovery and two-process backend tests remain 62B–62D. Owner-side Gate 25/36 acceptance remains OPEN.

The 100,000-event SQLite retention is a hard recovery boundary. If the relay cursor falls behind the retention floor, require explicit resnapshot/reconciliation; never silently advance.

## Exact-head validation

Automated Tests, CodeQL and Full Git History Secret Audit must pass on this exact commit. No result is pre-claimed. Gate 10 remains 0/10 closed; Stage 1 remains 75% provisional; Stages 2–6 unscored; overall score not established.
