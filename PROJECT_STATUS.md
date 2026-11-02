# DEZZTA CHART — Project Status

Last audited: 2026-11-02
Repository: deszztagd377-pixel/dezzta-chart
Baseline branch: main
Working branch: phase-2/market-data-foundation

## Overall progress

- Estimated overall progress toward the intended full application: 18.20%.
- Progress is a weighted milestone estimate, not a code-line percentage or a claim of scientific measurement. Decimal precision is recorded to two places for consistent tracking.
- Latest increment from the 18.00% baseline: +0.20 percentage points for the tested frontend OHLCV snapshot validator and series-specific chart adapter. No credit is assigned yet for live API fetching, instrument selection UI, chart integration, or a real provider feed.
- Phase 2 foundation now includes market-data DTOs, transport documentation, Python/FastAPI scaffold, futures instrument catalog, and a pure Databento definition-record adapter. Provider retrieval, live ingestion, persistence, recovery, and chart integration remain unimplemented.

## Current foundation

- React 18, TypeScript 5, Vite 4.
- Lightweight Charts 5 is installed.
- Existing candlestick chart currently uses hard-coded sample OHLC values from January 2024.
- Existing chart interaction includes zoom/scroll, pinch scaling, drag scrolling, and crosshair configuration. Interaction options have focused unit coverage.
- A timeframe type and selector exist for second, minute, hour, day, week, and month intervals.
- An OHLCV aggregation utility and Vitest unit tests exist.
- GitHub Actions runs frontend unit tests, a production build, and backend tests. The latest branch-head run must pass before a change is called verified.
- CI must pass on the latest branch head before this change is considered verified.

## Verified limitations

- No live market-data provider session is configured. The repository contains a provider-neutral FastAPI backend scaffold and read-only endpoints, but no provider is currently populating them.
- The timeframe selector updates React state, but the chart currently only changes the seconds-visible display option; it does not yet load or aggregate data for the selected timeframe.
- Watchlist now displays an explicitly offline, read-only supported-product catalog fixture for ES/NQ/GC; no expiry-specific contracts are fabricated.
- The existing sample candles are not real market data.
- Global indicator requirement: every indicator must be designed for compatibility across all supported chart timeframes, including second-based intervals. This is a target to validate per indicator, not a claim that every calculation is automatically valid on every timeframe.
- Performance requirement: minimize avoidable latency, rendering work, memory growth, and UI blocking; test responsiveness under representative data loads. Zero bugs or zero lag cannot be guaranteed, so regression testing and explicit error handling are mandatory.
- Candle timer requirement: show a remaining-time countdown at the right side of the chart, aligned near the price scale. Derive it from candle interval boundaries and a synchronized clock; never hardcode a countdown or imply exchange-synchronized time when only the device clock is available.
- Data freshness requirement: clearly distinguish source-event time, receive time, and display time. Do not label sample, delayed, or unsynchronized data as live/real-time. End-to-end freshness depends on provider, network, backend, and device.
- Watchlist contains a read-only offline ES/NQ/GC catalog fixture. Settings exposes the grid visibility preference and reset behavior; broader account, chart-layout, and indicator settings are not implemented.
- Drawing tools, indicator tier navigation, Volume Profile, Footprint, Heatmap, Liquidation Maps, persistence, and Android packaging are not implemented.
- No package-lock.json was present in the audited repository tree.

## Phase 2 — Market Data Foundation

Status: provider and initial instrument scope selected; transport contract, backend scaffold, instrument catalog, and pure definition-record adapter added. No live provider session has been configured.

### Selected provider and data requirements

- Primary provider selected for future evaluation: Databento.
- Primary CME dataset target: `GLBX.MDP3`, subject to account entitlement, exchange licensing, and approved use.
- The previously proposed MBO schema is a technical data-format target only; no live feed is configured or being consumed.
- Initial instrument metadata scope: ES, NQ, and GC product identifiers.
- These are futures product roots, not fixed-expiry contracts. Any future instrument metadata must be resolved from verified provider definitions rather than fabricated symbols or hard-coded contract months.
- Databento definition records expose fields such as `raw_symbol`, `instrument_id`, `publisher_id`, `instrument_class`, `expiration`, `min_price_increment`, and `ts_event`. Expiration and fixed-point price values use nanosecond and 1e-9 units respectively. See [Databento instrument definitions](https://databento.com/docs/schemas/instrument-definitions).
- Databento supports raw, instrument-ID, parent, and continuous symbology; these have distinct mapping behavior. See [Databento Live API](https://databento.com/docs/api-live?lang=python).
- Credentials must never be embedded in frontend code or Android packages.

### Completed in this phase

- FastAPI health/status endpoints and authenticated app-facing WebSocket scaffold.
- Provider-neutral `InstrumentCatalog` with outright-futures validation, expiry sorting, root filtering, atomic full-snapshot replacement, timestamp-ordered upserts/deletes, and tombstones against stale resurrection.
- `GET /v1/instruments` endpoint with honest empty-catalog behavior before provider definitions exist.
- Frontend instrument-catalog DTO and offline fixture for ES/NQ/GC, with tests confirming that no unverified contract metadata is invented.
- Read-only Watchlist catalog panel clearly marked OFFLINE FIXTURE; chart tab remains separate.
- Pure `databento_definitions.py` adapter that maps DBN-like definition objects into validated plain mappings without networking or credentials.
- Provider-neutral in-memory OHLCV pipeline with nanosecond timestamps, exact Decimal OHLCV values, timeframe bucket validation, atomic snapshot replacement, duplicate-snapshot replacement, and stale revision protection.
- Versioned frontend OHLCV transport DTO preserving timestamp and decimal precision as strings.
- Frontend OHLCV snapshot runtime validator and chart-boundary adapter: validates the versioned envelope, decimal-string values, nanosecond timestamps, OHLCV invariants, and chronological order per instrument series; converts to chart numbers only at the rendering boundary and requires an exact series identity.
- Read-only `GET /v1/ohlcv` snapshot endpoint; returns an explicit unavailable state while no provider adapter has populated the pipeline.
- Unit tests for catalog normalization, fixed-point values, nanosecond expirations, adapter field mapping, byte-symbol decoding, required-field checks, ordering, update/delete lifecycle, and stale-event rejection.

### Not implemented

- No live or historical provider connection, download, or subscription.
- No provider adapter currently converts market events or provider OHLCV records into the normalized OHLCV pipeline; the new pipeline is an ingestion boundary, not a live feed.
- No OHLCV WebSocket broadcast, HTTP fetch lifecycle, instrument-selection UI, or selected-timeframe chart integration yet. The pure frontend DTO validator/adapter exists but is not wired to the chart.
- No provider definition refresh scheduler or production population of the catalog.
- Lifecycle operations are currently in-memory only; no provider event consumer or persistent catalog store is connected.
- No market-data event broadcast, persistent storage, replay, or recovery.
- No brokerage or order-execution integration.
- No Footprint, Heatmap, or Liquidation Maps implementation; these three Exclusive Indicators are reserved for one coordinated Claude-assisted workflow after the project owner supplies visual references for each.
- Mid Tier is planned to contain approximately 10 intermediate/advanced indicators, not just Volume Profile. Volume Profile is one confirmed member; the remaining list will be proposed for owner approval before implementation. Candidate examples for discussion: VWAP, ATR, ADX/DMI, Stochastic, CCI, OBV, MFI, Ichimoku Cloud, Supertrend, and Keltner Channels. These are product categorization candidates, not implementation commitments.
- Low Tier is for common/general indicators such as RSI, MACD, Bollinger Bands, Moving Averages, and similar widely available studies.
- A separate Tools-menu Volume Profile tool is also planned: it displays a compact profile visualization at the chart side, without the full indicator's data-value presentation; users can move/resize its selected chart range and the profile recalculates for that range.
- Indicator navigation is planned as three categories: Low Tier (general indicators), Mid Tier (Volume Profile), and Exclusive (Footprint, Heatmap, Liquidation Maps). Tools are a separate entry point, not another indicator category.
- Exclusive Indicators remain owner-controlled: only the project owner can add new members to this tier.
- These are recorded product requirements only; no indicator or Tools UI implementation has started.

## Planned engineering sequence

1. Keep this stage provider-neutral and validate the adapter against documented record fields and fixtures.
2. Review the frontend contract and add a read-only instrument metadata display using fixture data.
3. Add the planned Low Tier / Mid Tier / Exclusive indicator navigation and separate Tools entry point when the chart UI phase begins.
4. Implement Volume Profile Mid Tier and the compact movable-range Volume Profile Tool after the project owner supplies visual references.
5. Reserve Footprint, Heatmap, and Liquidation Maps for one Claude-assisted Exclusive Indicators phase after their visual references are supplied.
6. Continue backend quality, observability, and local test coverage.

## Non-negotiable product constraints

- Preserve normal candlestick spacing when Footprint mode is OFF.
- Only Footprint ON may activate a dedicated spaced-candle/cluster layout.
- Do not implement Footprint, Heatmap, or Liquidation Maps visuals before the project owner supplies reference images; their combined large implementation task is intended for Claude.
- Keep Volume Profile Mid Tier separate from the compact movable-range Volume Profile Tool in the Tools menu.
- All indicator implementations must include timeframe-compatibility tests, including second intervals where supported, plus performance and regression checks.
- Candle countdown belongs on the right edge near the price scale and must use interval-boundary calculations with explicit clock/data freshness semantics.
- Preserve existing working chart interactions and avoid unrelated visual redesign.
- Never fabricate provider data, contract expiry, or feed status.

## Change log

### 2026-11-02 — Frontend OHLCV contract adapter
- Added runtime validation for the versioned OHLCV snapshot envelope and every bar; validates decimal strings, nanosecond timestamps, OHLCV boundaries using exact BigInt decimal comparison (no pre-render floating-point rounding), safe identifiers/sequences, and feed-state values.
- Chronology is validated per series identity (dataset, publisher, instrument, raw symbol, timeframe), because distinct series may legitimately share a bucket timestamp.
- Added an exact-identity chart adapter. Decimal and nanosecond strings are converted to JavaScript numbers only at the chart boundary; bars from other instruments/timeframes are excluded.
- Added regression tests for valid precision-preserving payloads, malformed values, invalid OHLC boundaries including sub-floating-point precision differences, negative volume, duplicate same-series timestamps, mixed-series timestamps, exact identity filtering, and unavailable snapshots.
- GitHub Actions run #98 passed frontend tests, production build, and backend tests.
- This is a tested adapter only: no HTTP request lifecycle, instrument picker, live provider connection, or chart data replacement has been enabled.
- Working branch head for this implementation: `5f8ee7ab78537105d5d51d7c700e41f3ebfcc8a4`.
- Overall estimated progress: 18.20% (+0.20 percentage points from the documented 18.00% baseline).


### 2026-11-02 — Chart interaction and viewport regression coverage
- Extracted chart interaction options into `src/utils/chartOptions.ts`; added tests for drag scrolling, pinch/wheel scaling, grid visibility, and second-display configuration.
- Added `getMeasurableChartSize` to reject zero, negative, or non-finite viewport dimensions before calling the chart resize API.
- Added viewport measurement regression tests. These are pure unit tests; they do not replace physical Android rotation, touch-gesture, or tab-switch validation.
- Latest working-branch commit at this audit: `51edcd05597eb80054a7cb6b2db245af98c75e9c`.
- CI run #91 and Vercel status for this change are being verified separately.


### 2026-11-02 — Mobile layout and chart lifecycle hardening
- Added a chart initialization error state with an accessible alert and a loading status; cleanup disconnects the resize observer and removes the chart instance.
- Preserved the lifecycle guard so queued resize callbacks do not update the chart after teardown.
- Added viewport-fit support and top/bottom device safe-area spacing for the header and bottom navigation.
- Latest audited working-branch commit: `51edcd05597eb80054a7cb6b2db245af98c75e9c` (viewport measurement guard; CI run #91 is being verified).
- GitHub Actions and Vercel checks for that commit were verified successful. Direct visual verification on a physical Android device is still outstanding.
- The overall progress estimate remains 18%; these reliability guards and tests improve foundation quality but do not yet deliver a major user-facing capability.


### Timeframe engine audit — 2026-11-01
- Audited the current timeframe engine, selector, chart component, and app wiring.
- Fixed duplicate source-candle snapshot handling: when multiple valid OHLCV snapshots share a timestamp, aggregation now uses the last supplied snapshot rather than incorrectly summing repeated cumulative volume and mixing revisions.
- Added regression coverage for duplicate-timestamp snapshots and input immutability.
- Important limitation confirmed: the current chart fixture contains daily date-only OHLC values and no volume field. It cannot honestly produce second/minute/hour candles or volume-based calculations. The timeframe selector still does not represent a functional multi-resolution data pipeline; chart integration is deferred until a properly timestamped base-resolution OHLCV fixture/data contract is available. No synthetic or fabricated market data will be presented as live.

### 2026-11-01
- Created the Phase 2 working branch from the audited main branch.
- Added typed frontend market-data contracts and transport documentation.
- Added FastAPI backend scaffold and authenticated status WebSocket.
- Added provider-neutral futures instrument catalog with validation, sorting, filtering, and tests.
- Added pure Databento definition-record adapter and tests; no provider client or network connection was created.

### 2026-11-01 — Instrument lifecycle and indicator product requirements
- Added timestamp-ordered catalog upserts and deletions, plus tombstones to reject stale resurrection events.
- Documented complete-snapshot replacement semantics and added lifecycle regression tests.
- Recorded the planned Low Tier / Mid Tier / Exclusive indicator categories and the separate Tools-menu Volume Profile tool.
- Recorded Footprint, Heatmap, and Liquidation Maps as one Claude-assisted Exclusive Indicators workstream pending user visual references.

### 2026-11-01 — Global indicator, timing, and performance requirements
- Recorded the cross-timeframe compatibility target for all indicators, including second-based intervals, with validation required for each calculation.
- Recorded performance, regression-testing, and explicit error-handling requirements; no absolute zero-lag/zero-bug guarantee is made.
- Recorded right-side candle-expiry countdown placement and synchronized-clock/data-freshness requirements.
- Expanded Mid Tier planning to approximately 10 indicators; Volume Profile is confirmed and the candidate list requires owner approval.
- Recorded common indicators as Low Tier and confirmed that additions to Exclusive Indicators are controlled only by the project owner.

### 2026-11-01 — Frontend instrument catalog fixture
- Added typed frontend catalog snapshot contract and an explicit offline fixture for ES, NQ, and GC product roots.
- Added fixture tests proving that no expiry-specific contract or active contract is fabricated.
- Added a read-only Watchlist catalog panel, clearly marked OFFLINE FIXTURE; chart rendering remains in its own tab.


### 2026-11-01 — OHLCV pipeline foundation
- Added provider-neutral in-memory OHLCV bar validation and ingestion with exact decimal values and nanosecond timestamps.
- Added UTC-aligned second/minute/hour/day/week/month/quarter bucket validation.
- Added atomic snapshot replacement, last-supplied duplicate snapshot semantics, and event-time/sequence stale-revision protection.
- Added a versioned frontend OHLCV DTO and a read-only snapshot API that reports unavailable while no provider adapter is connected.
- Added backend unit and API regression tests. Local isolated OHLCV unit checks: 14 passed; full repository CI remains unverified until the latest GitHub Actions run is confirmed.


### Phase 2 update — OHLCV provider adapter (working copy of phase-2/market-data-foundation)
- Added: multi-dimensional bar identity + local `sequence_origin`, point-in-time instrument resolver,
  Databento OHLCV record adapter (exact fixed-point), tiered UTC aggregation with completeness labels,
  bounded single-writer ingestion with visible overflow/gap handling, provider lifecycle manager,
  bounded historical window backfill, retention + `/v1/ohlcv` filters, root allow-list config.
- Verified by execution (local shim runner, see backend/README): pure-Python unit tests.
- NOT verified: real FastAPI/pytest run, CI, and every call into the real `databento` SDK
  (`databento_sources.py` and the duck-typed record attributes are UNKNOWN until exercised with a key).
- Not done: Databento SymbolMapping ingestion, exchange trading-day sessions, WebSocket broadcast,
  continuous contracts, persistence, MBO/footprint/heatmap.
- Overall progress figure above is intentionally left unchanged; it is the project owner's estimate.

### Audit corrections prepared after Claude patch review
- Databento live close wait uses the documented `block_for_close()` method.
- Instrument definitions are required before live normalization; startup now attempts an explicitly enabled definitions refresh when the resolver is empty.
- Coverage is keyed per provider/dataset/publisher/instrument/series/symbol. Live OHLCV observations no longer imply continuous coverage because no-trade intervals produce no record.
- Overflow gaps are aggregated by instrument identity instead of a bounded 1,024-entry event list; retry budget resets only after a stable session.
- Snapshot replacement rejects conflicting raw symbols for one instrument identity; undefined timestamp sentinel is rejected.
- These changes still require native CI and real SDK verification. Overall progress remains unchanged.
