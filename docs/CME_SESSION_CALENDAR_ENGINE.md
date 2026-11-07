# CME Session Calendar Engine

Status: **calendar primitives implemented; OHLCV aggregation integration pending**  
Last verified: 2026-11-07  
Working branch: `phase-2/market-data-foundation`

## Purpose

Daily and higher OHLCV bars for CME futures must follow exchange trading sessions, not UTC midnight boundaries. The initial product families are CME equity index futures (ES, NQ) and COMEX gold (GC). The calendar layer must distinguish a regular session, special session, early close, delayed open, explicit closure, maintenance interval, and unknown schedule coverage.

This module is a data-integrity boundary for historical/educational chart data. It does not submit orders, connect to a live trading venue, or manufacture market observations.

## Implemented primitives

- `backend/app/session_calendar.py` defines immutable `SessionRecord`, `SessionCalendar`, `SessionLookup`, and `SessionBucket` records.
- Session boundaries use timezone-aware `America/Chicago` datetimes. Conversion to epoch nanoseconds uses integer arithmetic.
- Calendar ID and product-family validation currently recognizes `CME_EQUITY_INDEX` for ES/NQ and `COMEX_GOLD` for GC.
- Each calendar release carries a version, source identifier, HTTPS source URL, publication timestamp, effective date range, and checksum.
- A date missing from the supplied release resolves to **unknown**. It is never inferred to be a regular session or a holiday.
- Weekly bounds use Monday-Sunday trading-date periods. Monthly and quarterly bounds use calendar months/quarters. Bounds are withheld unless every date in the period—including closed dates—is explicitly represented.
- Calendar tests use synthetic, explicitly constructed records for deterministic test cases only. These fixtures are not production schedules.

## Current integration boundary

The calendar module is not yet wired into the OHLCV aggregation pipeline.

Verified repository constraints at HEAD `001299360b038b1b85fdbf8c9e2cdda47afe7b5c`:

1. `backend/app/aggregation.py` intentionally skips UTC-fixed derivation from intraday bars to `1d`, `1w`, `1M`, and `3M`.
2. `backend/app/ohlcv.py` currently permits only `UTC_LEGACY` and `UTC_FIXED_V1` bucket policies.
3. `OhlcvBar` currently rejects calendar ID/version metadata under the two enabled UTC policies, so the calendar-aware policy is not yet accepted by the model.
4. The SQLite OHLCV store is already prepared to persist calendar identity: schema version 2 has `bucket_policy`, `calendar_id`, and `calendar_version` columns, and the composite primary key/index include them. Existing legacy migration and policy-isolation tests cover this storage contract. No new SQLite migration is currently indicated.
5. No authoritative, versioned CME schedule has been loaded.

Consequently, the existence of calendar primitives must not be described as active CME session aggregation.

## Required next engineering batch

1. Define a distinct session bucket policy (for example, `CME_SESSION_V1`) and its validation rules. Intraday UTC-fixed bars must retain their current behavior.
2. Permit calendar metadata only for the session policy; require a non-empty calendar ID and version, and reject mixed/mismatched identities.
3. Enable a distinct session bucket policy in `OhlcvBar` and validate its required calendar ID/version. Preserve current UTC policies and legacy bar identities.
4. Verify adapter/stream serialization retains the calendar identity fields; the SQLite OHLCV store already persists them, so do not add an unnecessary migration.
5. Extend aggregation so child event times are mapped through a matching calendar release. Only fully covered sessions may create daily or higher bars. Unknown coverage must produce no derived bar.
6. Define higher-timeframe grouping and retention behavior around exchange trading dates, including holiday/early-close weeks and calendar-version changes.
7. Add deterministic tests for calendar-aware daily/weekly/monthly/quarterly aggregation, out-of-order revisions, provider-bar precedence, incomplete schedule coverage, and no synthetic candles.
8. Load production schedules only from an authoritative source release. Record the exact source URL, publication/version, effective range, and cryptographic checksum. Do not use test fixtures as production data.

## Acceptance conditions

- No fabricated bars during closed, maintenance, or unknown periods.
- No aggregation across different calendar IDs or versions.
- Provider-sourced bars retain precedence for the same exact series identity.
- Existing UTC intraday aggregation and existing persisted UTC identities remain unchanged.
- Missing schedule data fails closed and is observable.
- All frontend/backend CI checks pass on the exact branch HEAD.

## Verification record

- Calendar primitives and tests are present at the recorded HEAD.
- GitHub Actions run [#42340030836](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42340030836) completed successfully, including frontend tests/build, backend tests, and backend container build.
- This document records the boundary and next acceptance work; it does not claim aggregation integration or authoritative CME schedule availability.
