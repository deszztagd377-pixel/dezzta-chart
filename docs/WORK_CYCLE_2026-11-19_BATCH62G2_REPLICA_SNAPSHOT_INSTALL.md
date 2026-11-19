# WORK CYCLE 62G-2 — REPLICA SNAPSHOT INSTALLATION

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline:** `35098bf07adb6a4b856dd8ce4c2034539e3e443f`  
**Cost:** ZERO COST. No deployment, paid service, Termux or modification to `main`.

## Objective

Complete the receiver-side half of the global snapshot protocol so a gateway can establish an independent local read model and advance its global checkpoint only when the entire snapshot has been validated and committed.

## Implementation

Added `SQLiteOhlcvReplicaStore` to `backend/app/ohlcv_store.py`.

### Identity and checkpoint

- A stable `replica_id` is created once for each gateway SQLite database.
- A durable checkpoint stores upstream source ID, replica ID, applied cursor, snapshot generation, retention floor, schema version and protocol version.
- Snapshot envelope format version 2 carries the complete per-timeframe bar-retention policy as well as the global outbox retention floor; the policy is persisted in the replica checkpoint.
- Replica `source_id()` is blocked because the local gateway is not the authoritative source.
- Replica `apply()` is blocked so the authoritative writer path cannot accidentally create an outbox echo.
- Replica `export_global_snapshot()` is blocked so a local read model cannot masquerade as a new authoritative source.
- A first install is refused unless the target is a dedicated empty OHLCV read-model database; existing bars or source outbox state are protected.

### Snapshot install algorithm

1. Validate the snapshot envelope and digest before taking the target writer lock.
2. Open the local target SQLite connection and begin `BEGIN IMMEDIATE`.
3. Reject a source mismatch or a snapshot cursor below the current checkpoint.
4. Re-open the snapshot and verify the header again, closing the file verify/use race.
5. Delete the previous local read model inside the transaction.
6. Stream bar records and validate exact field set and strict types.
7. Reconstruct each record through `OhlcvBar` validation.
8. Insert in bounded batches (default 500; allowed 1–5,000).
9. Recompute SHA-256 over the exact header line and canonical bar records, and validate row count and manifest.
10. Write the replica checkpoint inside the same transaction.
11. Commit. Any failure before commit rolls back the prior-bar deletion, all inserted rows and the checkpoint update.

### Strict data fidelity

- Decimal price and volume fields must be JSON strings. Numeric JSON values are rejected even if the envelope checksum is valid; this avoids lossy binary-float conversion.
- Nanosecond and other integer fields must be actual integers; booleans are rejected.
- Optional provider-out timestamp must be integer or null.
- The exact 23-field canonical bar schema is required.
- OhlcvBar validation enforces timeframe, origin, completeness, bucket policy, calendar identity and OHLC constraints.
- CME session calendar ID/version remains part of the installed identity.

## Regression coverage

Five new test groups:

1. Successful installation across UTC and CME series; exact Decimal and nanosecond fidelity; checkpoint contents; stable replica ID after restart; no outbox echo; source-writer apply blocked.
2. Wrong-source and stale-cursor snapshots rejected without mutation.
3. A semantically invalid snapshot with a valid recomputed digest fails after an earlier batch has been inserted; rollback preserves the old bars and checkpoint.
4. Numeric JSON decimal values rejected despite a valid manifest digest.
5. An existing authoritative database cannot be reused as a replica target; its bars and outbox remain intact. Replica snapshot export is blocked.

## Capacity and operational analysis

- Python staging memory is bounded by the configured insert batch, not total snapshot rows.
- The target replacement is a single SQLite transaction, so readers observe the old committed model until the new model and checkpoint commit together.
- The target writer lock remains held while the snapshot is streamed and inserted. Large installs can increase writer wait and WAL growth. Measure snapshot bytes, row count, install duration, writer wait and WAL growth before owner-host rollout.
- This does not share SQLite WAL across hosts.
- This does not expose a public snapshot endpoint or wire the replica into application startup.
- No Redis Streams publisher or consumer is enabled.

## Files changed in Batch 62G-2

- `backend/app/ohlcv_store.py`
- `backend/tests/test_ohlcv_store.py`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/ADR_WEBSOCKET_CROSS_INSTANCE_OUTBOX_RELAY.md`
- `docs/WORK_CYCLE_2026-11-19_BATCH62G1_GLOBAL_SNAPSHOT_EXPORT.md`
- This report.

## Code/test commit trail

- `fe1d05f214932268d25e2292079fe6752a32880f` — initial replica store and atomic installer.
- `307e6838fa3b2604f166cabff26bcc9affc1ac8a` — correct digest framing and clarify source identity semantics.
- `ad8583a53cf68a89c368d01a8a9d51e959e83440` — install, restart, source-binding, stale-cursor and rollback tests.
- `8e73cbc9c2e57bbf517dce024045dc59cac7749f` — correct newline framing in test-generated snapshot files.
- `9c7217c3e9cf32ca7d53e1e07ec5a2b6607bc75c` — strict type checks before Decimal and timestamp construction.
- `608ccddc249a7f7183feb41ff05f15bc75601d35` — reject numeric JSON Decimal regression test.
- `0a5fe3b10e55f94de8ffdc0230be61de21e255d3` — add bar-retention policy to snapshot format v2 and replica checkpoint.
- `4885eb0be9261d6d5d35fe97d87bd40b03d151c0` — prevent replacing non-empty authoritative databases.
- `29e40aa59310b03693eb710f1b4b07106f720b7b` — return retention policy metadata from exporter.
- `7e1b3186e29999aef642982bc3e14aa552ffe323` — test snapshot format and retention policy.
- `13004e0d083c1ce0b466d22b5ed5aeefad6c4b47` — fix stale-cursor test JSON import.
- `40883b0e194d35f4e894f57862e5bc208104579c` — test authoritative database protection.
- `e4dbe1f899aa382438a144fb59e9584ae8d969bc` — align reported snapshot format version.
- `09c0f5b8e82f710c18901cd4849bedce01d1ba1f` — block snapshot export from replica stores.
- `3987c9dc46bd11ade96742c8da4867b594147051` — test replica export protection.
- `82fa07c9c41d14ab0e379e714ca4ad89d9eeab2c` — full project and indicator progress checkpoint.
- `e85860d024466973a928245b41ae4a56d35aa710` — ADR architecture update.
- `195258d7d8ecaaf1d3f001ef2538672d35665da4` — link 62G-2 follow-up from the 62G-1 report.

The implementation and tests are committed. Exact-head CI must still pass before this work is described as runtime-verified. No CI success is claimed here.

## Gate 10 and project accounting

- Stage 1 remains **75% provisional** (30/40 criteria; 300/400 ticks).
- Gate 10 remains **0/10 formally closed**.
- Stages 2–6 remain **NOT SCORED**.
- Overall project percentage remains **NOT ESTABLISHED** because M1–M8 weights are unapproved.
- No Gate 25/36 owner evidence is created by local tests.
- No Stage ticks or gate closures are awarded by this source-code batch.

## Indicator ledger

The complete indicator ledger remains in `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`, including SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20, shared indicator hook, simulated Footprint, Heatmap and Liquidation Maps. This WebSocket work does not change indicator calculations or their visual completion status. Footprint/Heatmap/Liquidation visual work remains gated on owner reference images and reviewed blueprints.

## Next dependency

Implement transactional incremental replica event apply: validate source identity, event ID, cursor and schema; apply only `E=C+1`; treat `E<=C` as duplicate/stale without regression; require resnapshot for `E>C+1`; update bar and checkpoint in one transaction; never emit source outbox events. Redis Streams follows only after this layer passes its failure matrix.
