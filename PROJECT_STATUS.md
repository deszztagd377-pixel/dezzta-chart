# DEZZTA CHART — Project Status

Last audited: 2026-11-01
Repository: deszztagd377-pixel/dezzta-chart
Baseline branch: main
Working branch: phase-2/market-data-foundation

## Overall progress

- Estimated overall progress toward the intended full application: 18%.
- This is a planning estimate based on completed product capabilities, not a measured code-line percentage.
- Phase 2 foundation now includes market-data DTOs, transport documentation, Python/FastAPI scaffold, futures instrument catalog, and a pure Databento definition-record adapter. Provider retrieval, live ingestion, persistence, recovery, and chart integration remain unimplemented.

## Current foundation

- React 18, TypeScript 5, Vite 4.
- Lightweight Charts 5 is installed.
- Existing candlestick chart currently uses hard-coded sample OHLC values from January 2024.
- Existing chart interaction includes zoom/scroll and crosshair configuration.
- A timeframe type and selector exist for second, minute, hour, day, week, and month intervals.
- An OHLCV aggregation utility and Vitest unit tests exist.
- GitHub Actions runs unit tests and a production build.
- CI must pass on the latest branch head before this change is considered verified.

## Verified limitations

- No live market-data provider or backend is currently configured in the repository.
- The timeframe selector updates React state, but the chart currently only changes the seconds-visible display option; it does not yet load or aggregate data for the selected timeframe.
- Watchlist now displays an explicitly offline, read-only supported-product catalog fixture for ES/NQ/GC; no expiry-specific contracts are fabricated.
- The existing sample candles are not real market data.
- Global indicator requirement: every indicator must be designed for compatibility across all supported chart timeframes, including second-based intervals. This is a target to validate per indicator, not a claim that every calculation is automatically valid on every timeframe.
- Performance requirement: minimize avoidable latency, rendering work, memory growth, and UI blocking; test responsiveness under representative data loads. Zero bugs or zero lag cannot be guaranteed, so regression testing and explicit error handling are mandatory.
- Candle timer requirement: show a remaining-time countdown at the right side of the chart, aligned near the price scale. Derive it from candle interval boundaries and a synchronized clock; never hardcode a countdown or imply exchange-synchronized time when only the device clock is available.
- Data freshness requirement: clearly distinguish source-event time, receive time, and display time. Do not label sample, delayed, or unsynchronized data as live/real-time. End-to-end freshness depends on provider, network, backend, and device.
- Watchlist and Settings navigation currently changes only the selected navigation item; there are no implemented pages behind them.
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
- Unit tests for catalog normalization, fixed-point values, nanosecond expirations, adapter field mapping, byte-symbol decoding, required-field checks, ordering, update/delete lifecycle, and stale-event rejection.

### Not implemented

- No live or historical provider connection, download, or subscription.
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
