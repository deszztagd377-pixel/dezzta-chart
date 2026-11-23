# Batch 62J-170 — Gateway checkpoint identity and protocol fail-closed validation

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base HEAD:** `56f9fb3e034f837fa3cc59f75de9960b46b5f09f`  
**Scope:** Gate 25 local gateway replica startup validation. ZERO COST; no deployment, provider, UI, indicator formula, or external service changes.

## Finding

The gateway runtime previously compared the installer receipt with checkpoint source ID, snapshot generation, applied cursor, and SHA-256. The durable checkpoint also carries replica identity, replica schema/protocol versions, retention floor, and per-timeframe retention caps. Those fields were not all validated before Redis client creation. A malformed or stale checkpoint could therefore pass the gateway's first validation boundary and only fail later during consumer activity, or use an inconsistent replica identity for its Redis consumer group.

## Correction

- Exposed read-only public constants for the replica schema/protocol compatibility contract.
- Before creating Redis, require the checkpoint replica ID to match the replica identity table.
- Require exact supported schema and protocol versions.
- Require retention floor to be an integer in the inclusive range `0..applied_cursor`.
- Require the retention map to contain exactly every supported timeframe, with integer caps no lower than the store's minimum retention.
- Keep the existing source/generation/cursor/digest equality checks and fail-closed behavior.

## Regression coverage

Added a parameterized test for five invalid checkpoint cases: replica ID mismatch, unsupported schema version, unsupported protocol version, negative retention floor, and incomplete retention map. Each case asserts Redis client creation is never reached.

The existing valid snapshot installation, source mismatch, missing checkpoint, forged digest, TLS-only production Redis, and Redis-client cleanup tests remain in place.

## Changed files

1. `backend/app/ohlcv_store.py`
2. `backend/app/ohlcv_redis_gateway_runtime.py`
3. `backend/tests/test_ohlcv_redis_gateway_runtime.py`
4. `docs/WORK_CYCLE_2026-11-23_BATCH62J170_GATEWAY_CHECKPOINT_CONTRACT.md`
5. `docs/INDICATOR_PROGRESS_LEDGER.md`
6. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`

## Verification boundary

This batch strengthens local fail-closed startup validation. It does not establish authenticated cross-host immutable receipt transfer, remote key lifecycle, owner-host Redis durability, or Gate 25 closure. No indicator implementation credit is awarded.

Exact-HEAD Automated Tests, CodeQL, OCI ARM64 image-readiness, and full Git-history secret-audit must all pass before this batch is accepted. OCI readiness remains CI image evidence, not a cloud deployment.

## Project and indicator accounting

- Stage 1: 30/40 = 75% provisional 🟨.
- Stages 2–6: NOT SCORED / not officially opened ⬜.
- Gate 10: 0/10 external criteria formally closed 🟥.
- Gate 25: OPEN 🟧; local checkpoint validation improved, external authenticated receipt/key lifecycle remains.
- Gate 36: OPEN 🟥; public production WSS, real Firebase, reverse proxy, and physical Android WebView/network acceptance remain.
- Gate 38: OPEN 🟥; owner-host metrics persistence, backup/retention, alerting, and recovery acceptance remain.
- Overall project: NOT SCORED; approved stage weights and denominator remain unavailable.
- Indicators: unchanged; full state is recorded in the indicator ledger.

ZERO COST preserved. `main` untouched.
