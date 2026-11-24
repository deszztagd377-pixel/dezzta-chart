# Work Cycle — 24 November 2026 — Batch 62J-205
## Gate 25 snapshot digest/checkpoint evidence correction

**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Parent:** `3c914d7ac5a6590645379b24b324bb450239b4c4`  
**Code/test checkpoint inspected:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Cost:** ZERO COST • **main:** untouched

## 1. Finding

The current-source audit found a stale statement in `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`. It said the mutable replica checkpoint did not contain a snapshot SHA-256. That is no longer accurate for the current source/test checkpoint.

## 2. Verified current implementation

- `SQLiteOhlcvReplicaStore` creates/migrates `ohlcv_replica_checkpoint.snapshot_sha256`.
- `install_global_snapshot()` verifies the snapshot before the write lock, then reads and hashes the exact file again while inserting bars under a write transaction.
- It checks the manifest row count and digest against the recomputed digest and preflight metadata.
- The checkpoint digest is written in the same transaction as snapshot replacement and checkpoint advancement.
- `checkpoint()` and `load_snapshot()` expose the digest.
- Gateway runtime compares callback metadata to the durable checkpoint digest before creating the Redis client.
- `test_gateway_runtime_rejects_callback_digest_not_bound_to_durable_checkpoint` rejects a forged callback digest and proves Redis client construction does not occur.

## 3. Remaining distinction / Gate 25 is not closed

A mutable checkpoint digest is not an immutable receipt. The checkpoint describes the latest installed generation and is updated when a newer snapshot is installed; it does not preserve an append-only history of every installation.

The owner-host snapshot installer callback still performs authenticated transfer and supplies the per-gateway receipt map. The publisher validator checks source, stream, generation, cursor and digest fields but does not itself authenticate or retrieve the remote receipts. Durable owner-controlled receipt custody, signer/key provenance, immutable per-generation storage, and crash-safe receipt retention remain open.

This correction narrows the gap but does not close Gate 25 or authorize the proposed receipt schema/runtime migration.

## 4. Documentation changes

- Corrected the ADR context so it accurately describes the current mutable checkpoint digest.
- Marked the Batch 62J-135 statement as historical/superseded rather than current truth.
- Added the Batch 62J-205 source-backed correction with exact implementation boundaries.
- Synchronized the project status/master progress/current indicator docs and updated the color dashboard batch label.

## 5. Project accounting

| Meter | Verified state | Status |
|---|---:|---|
| Stage 1 | 30/40 • 300/400 • 75% provisional | 🟨 ACTIVE |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Gate 25 | Checkpoint digest binding implemented; immutable authenticated receipt custody still missing | 🟥 OPEN |
| Stages 2–6 | Not opened/scored | 🟦 / ⬜ PARKED |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Indicator aggregate | No approved denominator | ⚪ NOT SCORED |
| Cost | No new dependency/hosting/provider | 🟩 ZERO COST |

No code, tests, dependencies, secrets, runtime configuration, schema, hosting or deployment changed. The correction is documentation-only. `main` remains untouched.
