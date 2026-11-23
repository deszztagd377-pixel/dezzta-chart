# Batch 62J-181/182 — CME session identity frontend integration

Date: 23 November 2026  
Branch: `phase-2/market-data-foundation`  
Base documentation checkpoint: `b82c8ed061493c60414ec9e225629d0dfec88f40`  
Implementation checkpoint: `af3746fc39ac75a842a0199ad09304b008f19107`  
Exact-HEAD CI: **NOT YET VERIFIED**  
Main: untouched  
Cost: zero; no hosted deployment, paid data, paid runtime, or paid service introduced.

## Objective

Remove the backend/frontend OHLCV identity mismatch for CME session-aligned higher-timeframe bars while preserving all existing UTC identities and fail-closed behavior.

## Confirmed backend contract

- `CME_SESSION_V1` is valid only for `1d`, `1w`, `1M`, and `3M`.
- CME session series require both a non-empty `calendar_id` and exact `calendar_version`.
- ES/NQ use canonical calendar `CME_EQUITY_INDEX`; GC uses `COMEX_GOLD`.
- Intraday intervals remain `UTC_FIXED_V1`.
- Existing legacy daily/higher series remain `UTC_LEGACY`.
- A loaded calendar version is exposed only when the runtime registry resolves exactly one release for the calendar ID. If no release or multiple releases are present, the catalog reports no usable version; the frontend falls back to UTC identity.
- The repository's calendar fixture `test-only-2024.01` is explicitly synthetic test data, not an official CME schedule.

## Implementation completed in this batch

1. Extended the frontend OHLCV bucket-policy type to include `CME_SESSION_V1`.
2. Updated REST OHLCV bar parsing to accept CME metadata only for the four supported higher timeframes and only with both calendar ID and version.
3. Updated the shared market-data store to enforce the same policy/timeframe/calendar invariants.
4. Updated the WebSocket stream DTO parser to validate calendar metadata and preserve exact series-version matching.
5. Added regression tests for CME snapshot parsing, stream parsing, invalid timeframe rejection, incomplete metadata rejection, and calendar-version isolation.
6. Added keyed-store tests proving different calendar releases cannot share a market-data snapshot.
7. Extended `GET /v1/instruments` to return the canonical instrument's `session_calendar_id` and the loaded `session_calendar_version`, while keeping both null for unmapped instruments.
8. Extended the frontend catalog DTO with optional nullable calendar fields for compatibility with older responses.
9. Added a bucket-identity selector that chooses `CME_SESSION_V1` only for 1D/1W/1M/3M when both exact calendar fields are present. Incomplete metadata falls back to the pre-existing UTC policy and empty calendar fields.
10. Wired `CandlestickChart` to use the exact loaded catalog calendar identity for its canonical series and WebSocket supervisor.
11. Added backend catalog API tests for loaded test-fixture version exposure and null calendar identity for unmapped contracts.
12. Added chart lifecycle tests for loaded-calendar selection and safe fallback when the calendar version is unavailable.

## Files changed

- `backend/app/main.py`
- `backend/tests/test_api.py`
- `src/types/instrumentCatalogApi.ts`
- `src/types/ohlcv.ts`
- `src/services/marketDataStore.ts`
- `src/services/marketDataStore.test.ts`
- `src/services/marketDataSeriesStore.test.ts`
- `src/services/ohlcvStreamProtocol.ts`
- `src/services/ohlcvStreamProtocol.test.ts`
- `src/utils/ohlcvAdapter.ts`
- `src/utils/ohlcvAdapter.test.ts`
- `src/utils/ohlcvBucketPolicy.ts`
- `src/utils/ohlcvBucketPolicy.test.ts`
- `src/components/CandlestickChart.tsx`
- `src/components/CandlestickChart.lifecycle.test.tsx`

The implementation checkpoint is 15 commits ahead of the previous documentation checkpoint and zero commits behind it. The last commit is `af3746fc39ac75a842a0199ad09304b008f19107`.

## Verification boundary

The prior code/test checkpoint `07186190e98a4e9418664990a1a84acbc6fb3e13` is verified green:
- Automated Tests run `45173027719`: success; synthetic Worker 25/25, frontend 306/306 tests and build, backend tests, container smoke and dependency checks passed.
- Full Git History Secret Audit run `45173027724`: success.
- CodeQL run `45173027753`: success for Python and JavaScript/TypeScript.
- OCI ARM64 run `45173027840`: success.

These runs apply to `07186190...`, not the new `af3746...` implementation. The current GitHub connector's combined-status response returned no entries for the newer push checkpoint, and its workflow-run helper returns pull-request-triggered runs only. Therefore the new exact-HEAD CI result remains **unverified**; it is not marked green.

## Remaining work — do not promote scores yet

1. Verify exact-HEAD CI for this implementation. Fix any failure before accepting the batch.
2. Run the CME frontend parser/store/chart tests and backend catalog API test on the exact head.
3. Add a zero-cost, pinned local Cloudflare runtime integration test using the actual Worker/ Durable Object runtime. Synthetic Node doubles are not equivalent to `WebSocketPair`, Durable Object hibernation, attachment restoration, or runtime alarm behavior.
4. Exercise CME session identity through the actual WebSocket request, snapshot, incremental update, SQLite persistence and replay paths using only test-only schedules.
5. Keep official CME calendar activation blocked until an authoritative schedule release and independently trusted checksum are available. The test fixture must never be used as production data.
6. Continue remaining WebSocket gates: upstream dynamic provider subscription/reference counting, cross-host receipt/key lifecycle, production Firebase auth, public WSS, and Android real-network acceptance.
7. Preserve the zero-cost rule. Do not introduce paid hosting, market-data access, databases, storage, monitoring, domains, or notification services.

## Project and indicator progress — unchanged

- Stage 1 Foundation, Security & Data Integrity: 🟨 **30/40 = 75% provisional**.
- Stage 2 Market Data Infrastructure: 🟦 Synthetic-only proof; **NOT SCORED** pending runtime acceptance.
- Stage 3 Chart Engine & Timeframe: ⬜ **NOT SCORED**.
- Stage 4 Indicators & Analytics: ⬜ **NOT SCORED**.
- Stage 5 Professional UI & Interactive Tools: ⬜ **NOT SCORED**.
- Stage 6 Hardening, Validation & APK Release: ⬜ **NOT SCORED**.
- Gate 10 external acceptance: 🟥 **0/10 formally closed**.
- Gate 25 snapshot/replica custody: 🟧 **OPEN**.
- Gate 36 public WSS/Firebase/Android lifecycle: 🟥 **OPEN**.
- Gate 38 owner-host telemetry persistence/restore/operations: 🟧 **OPEN**.
- Gate 39 operational alert acknowledgement/recovery: 🟥 **OPEN**.
- Overall project: **NOT SCORED**; approved weighted denominator is still unavailable.
- Delivery target: **24 December 2026**, planning target only.

Indicator statuses are unchanged: SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 synthetic prototype only, Heatmap 🟥 not implemented, Liquidation Maps 🟥 not implemented.

No indicator calculation, renderer, UI, or acceptance gate was changed in this batch. No indicator credit or percentage increase is awarded for market-data infrastructure work.
