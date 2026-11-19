# WORK CYCLE 62G-1 — GLOBAL SNAPSHOT EXPORT

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Approved architecture:** Batch 62G integrated eight-point WebSocket cycle  
**Cost:** ZERO COST. No Vercel/Cloudflare deployment, paid service, or Termux.

## Scope completed

This is the first executable slice of the approved global snapshot protocol. It implements source-side export and integrity verification, not replica installation or relay activation.

### Source identity

- Added `ohlcv_store_identity`, an additive OHLCV-owned table.
- Generates a stable UUID-like source ID once per SQLite database.
- Existing databases receive the ID on initialization.
- Does not modify the shared registry `PRAGMA user_version` and does not change the OHLCV table schema version.

### Consistent bounded export

`SQLiteOhlcvStore.export_global_snapshot(destination_path, batch_size=500)`:

1. Opens a SQLite read transaction.
2. Reads outbox high-water and retention floor first, pinning the read view.
3. Reads stable source identity in the same view.
4. Streams every row from `ohlcv_bars` in deterministic primary-key order.
5. Uses `fetchmany(batch_size)`; default is 500 and accepted range is 1–5,000.
6. Emits a JSONL header, canonical bar records and a footer manifest.
7. Computes SHA-256 over the canonical header and every canonical bar-record line, protecting the source ID and watermark as well as bar payloads; records row count.
8. Flushes and fsyncs the temporary output.
9. Commits the source read transaction, then atomically renames the completed temporary file into place.

No default calendar filter is applied. UTC legacy, UTC fixed and calendar-qualified CME session records are included.

### Verification

`SQLiteOhlcvStore.verify_global_snapshot(snapshot_path)` streams the file and validates:
- Header format/version, non-empty source/generation identity, non-negative watermark, and retention-floor ordering.
- Record ordering.
- Manifest row count.
- SHA-256 of canonical bar records.
- Absence of trailing records after the manifest.

A changed bar record is rejected. The verifier does not load the entire file into memory.

## Correctness model

Let (H) be the source outbox high-water read at the beginning of the pinned transaction. Every bar in the exported file is read from that same SQLite snapshot. Therefore the snapshot checkpoint candidate is exactly (H), not a per-instrument cursor.

The file is not installable as a replica until the next slice implements:
- Source identity binding and target replica identity.
- Full row schema/identity validation.
- Atomic staging and local snapshot swap.
- Checkpoint write in the same target transaction as the installed bars.
- Incremental replay strictly after (H).

The snapshot exporter does not publish a WebSocket event, append to outbox, or activate Redis.

## Resource and failure handling

- Python memory is bounded by the configured fetch batch, rather than total row count (N).
- The output file is first written under a unique temporary name on the destination filesystem.
- A failure before rename removes the temporary file and leaves any prior destination file untouched.
- A pinned WAL reader can delay checkpoint/truncation. WAL growth and export duration must be measured under concurrent ingestion before production rollout.
- Disk-space preflight and snapshot artifact retention policy remain to be designed before owner-host use.
- The exporter is a local internal transfer artifact; no public HTTP endpoint is added.

## Regression tests added

1. Multi-policy export including CME session/calendar identity, exact Decimal strings, source ID stability, row count, manifest and tamper rejection.
2. Concurrent write after watermark pinning: export remains at cursor 1 with one bar while the live source advances to cursor 2.
3. Argument safety: empty destination, boolean/zero batch size and destination equal to source DB are rejected.

## Files changed in this work cycle

- `backend/app/ohlcv_store.py`
- `backend/tests/test_ohlcv_store.py`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- This report.

## Commit sequence

- `a4ef6eca4ffe5dd15cb829f10090d54934216cf7` — source identity + snapshot export/verification.
- `708532eb6b2edd4029176b2b95be822995305059` — corrected JSONL newline encoding before tests were added.
- `0cbc8b53afde575362050fbb88fdfe3dba8dedbf` — three snapshot regression tests.
- `498e644e1cc6037c02ea5c25935babc2e886a224` — include header metadata in SHA-256 and strictly validate watermarks.
- `6463c968e25c86b6c07099dcc99c4415cd3c4b8d` — reject forged header watermark as well as payload tampering.
- `089fa6d5557d8ee1981fa9660b605d4a86ed56d0` — project progress and indicator ledger checkpoint.

The code was inspected after the newline correction. Exact-head CI remains the authority for runtime validation; no CI success is claimed in this report until run statuses are checked.

## Project / Gate 10 status

- Stage 1 remains 75% provisional (30/40 criteria, 300/400 ticks).
- Gate 10 remains 0/10 formally closed.
- Stages 2–6 remain NOT SCORED.
- Overall project percentage remains NOT ESTABLISHED because M1–M8 weights are unapproved.
- This source snapshot slice is not owner-host evidence and does not close Gate 25 or 36.
- Full indicator formulas, warm-up indexes, test boundary and remaining visual work remain in `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

## Next step

Implement replica-side snapshot validation and atomic install into a separate local SQLite read model. Only after this install/checkpoint transaction is tested should the work cycle move to transactional event apply and Redis Streams.
