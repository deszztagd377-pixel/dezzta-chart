# WORK CYCLE 62G-3 — ATOMIC INCREMENTAL REPLICA EVENT APPLY

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline:** Batch 62G-2 replica snapshot installation  
**Cost:** ZERO COST. No Vercel/Cloudflare deployment, paid service, Termux or modification to `main`.

## Objective

Implement the local replica apply contract so a gateway can consume authoritative global outbox events without losing cursor order, duplicating bars, regressing its checkpoint or re-emitting events into its own outbox.

## Implementation

Added `SQLiteOhlcvReplicaStore.apply_replica_event(event, source_id, retention_floor=None)`.

### Envelope and data validation

- Requires a prior installed snapshot and binds the event to the source ID stored in the replica checkpoint.
- Requires the exact version-1 `market_data.ohlcv.update` upsert envelope returned by `read_outbox_batch()`.
- Validates event ID, positive integer cursor, complete 10-field series identity and exact 23-field bar payload.
- Cross-checks every series identity field against the corresponding bar field.
- Decimal values must remain strings. Nanosecond values must be canonical non-negative integer strings; optional provider-out timestamp must be a canonical integer string or null.
- Publisher/instrument IDs and sequence must be integers; booleans are rejected.
- Reconstructs the payload through `OhlcvBar` validation before opening the write transaction.

### Cursor and idempotency contract

Let the durable replica cursor be (C), and incoming event cursor be (E):

| Condition | Result | Mutation |
|---|---|---|
| (E=C+1) | `applied` | Apply bar + ledger + checkpoint atomically |
| (Ele C), exact cursor/event ID/digest match retained | `duplicate` | None |
| (Ele C), dedupe history already aged out | `stale` | None |
| (E>C+1) | `resnapshot_required / cursor_gap` | None |
| Observed retention floor (>C) | `resnapshot_required / retention_expired` | None |
| Reused cursor/event ID with different identity or payload | Hard conflict error | Rollback / none |

The deduplication ledger stores cursor, unique event ID and SHA-256 of the canonical event. It is bounded to the latest 100,000 cursors, matching the source outbox retention window.
Replica checkpoint schema and event protocol are version 3. A stale checkpoint version fails closed; a current global snapshot must be installed before event replay resumes.

### Atomic apply transaction

For a contiguous event:

1. Begin a local SQLite write transaction.
2. Re-check source binding and current cursor.
3. Reject event-ID/cursor reuse.
4. Upsert the canonical bar without calling source-writer `apply()`.
5. Apply the same per-timeframe/per-series retention pruning policy recorded in snapshot format v2.
6. Insert the applied-event deduplication record.
7. Prune old dedupe records beyond the 100,000-cursor horizon.
8. Advance the replica cursor and monotonically observed retention floor.
9. Commit.

Bar mutation, retention pruning, dedupe record and checkpoint update share one transaction. A checkpoint failure rolls all of them back. No replica outbox event is written.

Callers may ACK a durable transport message only after `applied`, `duplicate` or `stale`. A gap/retention result requires resnapshot before ACK; conflicts and validation errors must not be ACKed.

## Regression coverage

Five event test groups:

1. Contiguous event apply, exact data, checkpoint advance, duplicate replay and no outbox echo.
2. Cursor gap, wrong source, malformed Decimal, event-ID conflict, stale event after dedupe-history pruning and non-regressing checkpoint.
3. A forced checkpoint-update failure after the bar and dedupe record have been staged; rollback preserves the old bar/checkpoint and leaves the event ledger empty.
4. Source/replica per-series retention parity after an additional event exceeds the five-bar timeframe cap.
5. An outdated checkpoint protocol is rejected without cursor advance or bar mutation.

## Current boundaries

- This is a storage primitive only. It does not yet publish to `OhlcvStreamHub`.
- Redis Streams publisher, independent per-gateway consumer groups, pending reclaim and ACK wiring are not implemented.
- No app-factory startup changes or partial relay activation.
- No SQLite WAL sharing between hosts.
- No public deployment, paid service or production credential is used.
- Exact-head CI must pass before this batch is considered runtime-verified.

## Files changed in this cycle

- `backend/app/ohlcv_store.py`
- `backend/tests/test_ohlcv_store.py`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/ADR_WEBSOCKET_CROSS_INSTANCE_OUTBOX_RELAY.md`
- `docs/WORK_CYCLE_2026-11-19_BATCH62G2_REPLICA_SNAPSHOT_INSTALL.md`
- This report.

## Main code/test commits

- `bc54265784b16daaab50bc4da64e93306105ee87` — atomic replica event apply.
- `8b60a6974210e9ba4d5999455205c543d0067740` — use conflict-safe SQL upsert.
- `92922b5c11cf640a0fb2c9512d2d09e0b56f5084` — cursor, idempotency, conflict and rollback tests.
- `4dc6e8d397ae3c62850cae38c83ccb0f783d08ab` — conflict precedence and safe ACK boundary.
- `8c5d43d9487b3fd6e85a0a6bc1233933d1491b9a` — per-series retention parity test.
- `a687a08293a29a31ea5190379e40ee4f5ab4455f` — version the replica checkpoint schema/event protocol and fail closed on outdated versions.
- `a59bfac3f3c6238a99439025d49f0ee1157ad624` — assert replica schema/protocol version 3.
- `0c2a6292728e819b2af062281817b71dbe100e70` — regression test for outdated checkpoint protocol rejection.

## Project / Gate 10 accounting

- Stage 1 remains **75% provisional** (30/40 criteria; 300/400 ticks).
- Gate 10 remains **0/10 formally closed**.
- Stages 2–6 remain **NOT SCORED**.
- Overall project percentage remains **NOT ESTABLISHED** because M1–M8 weights are unapproved.
- No Gate 25/36 owner evidence is created by local tests.
- No Stage ticks or gate closures are awarded by this code batch.

## Complete indicator progress

The full indicator ledger is maintained in `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`: SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20, shared indicator hook, Footprint (SIMULATED), Heatmap and Liquidation Maps. This WebSocket batch does not change indicator calculations or visual completion. Footprint/Heatmap/Liquidation visuals remain gated on owner reference images and reviewed blueprints.

## Next dependency

Implement the Redis Streams publisher with deterministic cursor-derived message identity, retry verification and a durable publisher checkpoint. Then implement independent consumer groups per gateway, apply-before-ACK, pending reclaim, crash recovery and two-process parity. Do not activate the relay in app startup until the complete failure matrix passes.
