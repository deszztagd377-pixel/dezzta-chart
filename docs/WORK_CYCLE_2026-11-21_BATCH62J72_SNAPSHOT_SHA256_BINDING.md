# DEZZTA CHART — Work Cycle Batch 62J-72
## Snapshot artifact SHA-256 binding for source publisher activation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test checkpoint:** `0a8e28e0ae9b8e63f800cf4ff643a057c942ee90`

## Objective

Close a repository-level integrity gap in the source publisher bootstrap: matching only source ID, stream key, generation and cursor did not explicitly bind each gateway installation receipt to the exact bytes of the global snapshot artifact.

## Inspected source of truth

Before changing the runtime contract, inspected `backend/app/ohlcv_store.py`:

- `export_global_snapshot()` writes a format-version-2 JSONL snapshot.
- Its header contains `generation_id`, `source_id`, `high_water`, and `retention_floor`.
- The exported SHA-256 covers the canonical header line and every canonical bar-record line; the terminal manifest stores `row_count` and `sha256`.
- The export result returns `generation_id`, `source_id`, `cursor`, `high_water`, `row_count`, and `sha256`.
- `verify_global_snapshot()` recomputes the digest from the artifact and checks both the manifest digest and row count.

The implementation therefore uses the existing artifact digest rather than inventing another snapshot checksum.

## Changes

Updated:
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_runtime.py`

Runtime contract:
- Requires `snapshot_sha256` as exactly 64 lowercase hexadecimal characters.
- Requires every gateway receipt to match the same digest, in addition to the existing source ID, stream key, generation and cursor checks.
- Rejects a missing/malformed digest or any receipt mismatch before Redis client creation.
- Includes the validated digest in the returned non-secret snapshot evidence summary.

Regression coverage:
1. Missing durable checkpoint blocks Redis client creation.
2. Gateway cursor mismatch blocks Redis client creation.
3. Gateway digest mismatch blocks Redis client creation.
4. Malformed manifest digest blocks Redis client creation.
5. Exact source/stream/generation/cursor/digest match permits dedicated TLS client construction and checks the 3s connect timeout, 5s socket timeout, certificate validation and hostname validation.
6. Production plaintext Redis URL remains rejected.
7. Environment activation remains opt-in.

## Host verifier contract

The owner-controlled callback must:
1. Run `SQLiteOhlcvStore.verify_global_snapshot()` against the actual exported artifact.
2. Read the authoritative gateway installation receipts from their real source.
3. Authenticate those receipts using the actual owner-controlled trust mechanism.
4. Map the verified artifact's `generation_id`, `cursor`, and `sha256` to `snapshot_generation`, `snapshot_cursor`, and `snapshot_sha256`.
5. Require each receipt to carry the same `snapshot_sha256`.

This batch binds receipt metadata to the exact snapshot bytes. It does **not** authenticate receipts by itself and does not prove that remote gateways actually installed the snapshot. No signing format, receipt database, or host topology was fabricated.

## Verification status

CI must be checked against the exact source/test checkpoint above. Earlier successful CI for `5575f5d820dd26d16a7170cb2c55e9c707c2afc1` does not automatically verify this new change.

## Gate 10 disposition

- Gate 25 — 🟧 OPEN: live Redis TLS/ACL, credential rotation/rollback, persistence, failover and network isolation remain host evidence.
- Gate 36 — 🟧 OPEN: public HTTPS/WSS reverse proxy, certificate/hostname/renewal and browser/Android WebView acceptance remain host/device evidence.
- Source publisher activation — 🟨🟩 HOST VERIFICATION PENDING.
- Gate 10 — 0/10 formally closed; no acceptance tick awarded.
- Stage 1 — 30/40 criteria = 75% provisional.
- Stages 2–6 and overall project percentage remain unscored pending approved denominators and weights.

## Indicator ledger

No indicator source, formula, hook, renderer or UI changed in this backend-only batch. Existing progress remains:
- SMA20 — 🟨 foundation; first valid index 19.
- EMA20 — 🟨 foundation; SMA-seeded, alpha 2/21; first valid index 19.
- RSI14 — 🟨 foundation; Wilder smoothing; first valid index 14.
- MACD 12/26/9 — 🟨 foundation; MACD index 25; signal/histogram index 33.
- Bollinger20,2 — 🟨 foundation; population standard deviation; first valid index 19.
- Shared Indicator Hook — 🟨 foundation.
- Footprint — 🟧 simulated/gated; waits for user visual reference and approved blueprint.
- Heatmap — 🟥 not implemented; waits for user visual reference, free-source feasibility and approved data contract.
- Liquidation Maps — 🟥 not implemented; free-source feasibility and validated data/calculation contract required.

Correctness invariants remain: warm-up slots are null, not zero; series align to candle indices; future candles cannot repaint earlier values; identity/timeframe changes clear stale values. Footprint OFF preserves normal candle spacing; explicit ON alone activates spaced clusters.

## Cost and device boundary

ZERO COST. No deployment, paid service, production credential, Vercel/Cloudflare operation, Termux/device command, or `main` modification.
