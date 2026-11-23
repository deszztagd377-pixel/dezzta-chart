# Batch 62J-172 — WebSocket replica relay wire-format hardening

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base HEAD:** `d5cd1418a3a0b449d503803da6527bd3a4c982bc`  
**Scope:** Gate 25/36 local replica-to-WebSocket event validation; ZERO COST.

## Finding

The frontend snapshot/stream parser requires nanosecond timestamps to be decimal strings and OHLCV values to use canonical decimal-string syntax. The backend replica relay's `_bar_from_event()` previously coerced event JSON values using `int()` and `Decimal()`, which could accept numeric JSON values, booleans, signed/fractional timestamp strings, exponent notation or non-canonical decimal forms. This created an avoidable parser differential at the backend replica trust boundary.

## Change

- Added strict unsigned ASCII decimal-string parsing for `tsStartNs`, `tsEventNs`, `tsReceivedNs`, and optional `tsProviderOutNs`.
- Added canonical decimal-string parsing for `open`, `high`, `low`, `close`, and `volume`, matching the frontend's `^-?(?:0|[1-9]\\d*)(?:\\.\\d+)?$` contract.
- Preserved `null` for an absent provider-output timestamp.
- Rejected malformed values before constructing or mutating the in-memory pipeline.
- Added parameterized regression tests for invalid timestamp and decimal representations and a positive provider-output timestamp case.
- Updated `docs/OHLCV_STREAM_PROTOCOL.md` with the backend relay validation boundary.

## Regression coverage

- Timestamp fields reject numeric JSON, booleans, negative/fractional strings and non-ASCII digit strings.
- Decimal fields reject numeric JSON, booleans, exponent notation, non-finite tokens and leading-zero non-canonical values.
- Valid decimal-string provider-output timestamps remain accepted.
- Existing durable cursor deduplication, snapshot/replay handoff, pipeline divergence, and mixed-series rejection tests remain.

## Prior batch verification

Batch 62J-171 exact HEAD `d5cd1418a3a0b449d503803da6527bd3a4c982bc` passed all four workflows:
- Automated Tests [45161627257](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627257): SUCCESS; 1,336 backend tests passed, 1 skipped, 6 warnings; 306 frontend tests passed.
- CodeQL [45161627265](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627265): SUCCESS.
- Full Git History Secret Audit [45161627305](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627305): SUCCESS.
- OCI ARM64 Image Readiness [45161627212](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45161627212): SUCCESS.

These results do not apply to this new commit; Batch 62J-172 requires its own exact-HEAD CI.

## Acceptance boundary

This is local wire-format consistency hardening. It does not prove public WSS, Firebase production authentication, reverse proxy/certificate lifecycle, Android WebView behavior, upstream dynamic subscription pooling, provider rights, or Gate 25/36 closure. No indicator implementation credit is awarded. `main` untouched.
