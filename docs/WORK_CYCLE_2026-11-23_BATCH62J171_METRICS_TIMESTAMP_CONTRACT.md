# Batch 62J-171 — Gate 38 metrics timestamp contract hardening

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base HEAD:** `0d1ef247aa68fd0946293b91f76e3af3fd608086`  
**Scope:** Gate 38 local metrics collector input validation; ZERO COST.

## Finding

Both `SQLiteMetricsCollector.flush()` and `snapshot()` converted caller-supplied `now` directly with `float()`. This admitted values outside the declared numeric timestamp contract, including booleans (`True` becomes epoch second 1) and numeric strings. That can silently shift retention windows, stale-worker calculations, and bucket assignment instead of rejecting malformed caller input.

## Change

- Added one shared timestamp validator used by both write and read paths.
- Accepts only finite, non-negative `int`/`float` epoch seconds; explicitly rejects booleans and strings.
- Preserves `None` as the documented system-clock default.
- Keeps validation before SQLite connection creation, so malformed input cannot create or mutate the database.
- Corrected the flush result annotation to include its measured floating-point timing fields.

## Regression coverage

Added a parameterized matrix across both `flush` and `snapshot` for:
- `True` and `False`;
- numeric string and textual NaN;
- floating NaN and infinity;
- negative timestamp.

Every case must raise `MetricsCollectorError("invalid_timestamp")` before a database file exists. Existing worker idempotency, rollback, concurrency, retention, capacity, restart-persistence and disk-full recovery tests remain unchanged.

## Gate and system impact

- Gate 38: local collector input boundary is stricter; owner-host durable volume, backup/restore, retention operations, external alert delivery and recovery drill remain OPEN.
- Gate 36: no public WSS, Firebase, reverse proxy or physical Android validation is claimed.
- Gate 25: no receipt/key lifecycle or cross-host trust change in this batch.
- WebSocket: no transport protocol or client lifecycle change; metrics ingestion input contract only.
- Indicators: no calculation, hook, chart binding, renderer, settings or visual change; zero indicator implementation credit.

## Changed files

1. `backend/app/metrics_collector.py`
2. `backend/tests/test_metrics_collector.py`
3. `docs/WORK_CYCLE_2026-11-23_BATCH62J171_METRICS_TIMESTAMP_CONTRACT.md`
4. `docs/INDICATOR_PROGRESS_LEDGER.md`
5. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`

## Acceptance boundary

Automated Tests, CodeQL, Full Git History Secret Audit and OCI ARM64 image readiness must pass on the exact final commit. OCI readiness is CI evidence only, not a cloud deployment. No paid service, cloud account, production credential, domain, deployment, external provider entitlement, or device action is introduced. `main` remains untouched. Target date remains **24 December 2026**, not a guaranteed completion claim.
