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
- The existing sample candles are not real market data.
- Watchlist and Settings navigation currently changes only the selected navigation item; there are no implemented pages behind them.
- Drawing tools, Footprint, Heatmap, persistence, and Android packaging are not implemented.
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
- Provider-neutral `InstrumentCatalog` with outright-futures validation, expiry sorting, and root filtering.
- `GET /v1/instruments` endpoint with honest empty-catalog behavior before provider definitions exist.
- Pure `databento_definitions.py` adapter that maps DBN-like definition objects into validated plain mappings without networking or credentials.
- Unit tests for catalog normalization, fixed-point values, nanosecond expirations, adapter field mapping, byte-symbol decoding, required-field checks, and ordering.

### Not implemented

- No live or historical provider connection, download, or subscription.
- No provider definition refresh scheduler or production population of the catalog.
- No market-data event broadcast, persistent storage, replay, or recovery.
- No brokerage or order-execution integration.
- No Footprint or Heatmap implementation; those complex indicator tasks are reserved for a separate Claude-assisted workflow after the project owner supplies visual references.

## Planned engineering sequence

1. Keep this stage provider-neutral and validate the adapter against documented record fields and fixtures.
2. Add safe catalog lifecycle semantics for definition updates/deletions and stale snapshots.
3. Review the frontend contract and add a read-only instrument metadata display using fixture data.
4. Continue backend quality, observability, and local test coverage.
5. Reassess external provider access only when account ownership, age-appropriate authorization, entitlement, licensing, and cost are independently confirmed.

## Non-negotiable product constraints

- Preserve normal candlestick spacing when Footprint mode is OFF.
- Only Footprint ON may activate a dedicated spaced-candle/cluster layout.
- Do not implement Footprint or Heatmap visuals before the project owner supplies reference images; their large implementation tasks are intended for Claude.
- Preserve existing working chart interactions and avoid unrelated visual redesign.
- Never fabricate provider data, contract expiry, or feed status.

## Change log

### 2026-11-01
- Created the Phase 2 working branch from the audited main branch.
- Added typed frontend market-data contracts and transport documentation.
- Added FastAPI backend scaffold and authenticated status WebSocket.
- Added provider-neutral futures instrument catalog with validation, sorting, filtering, and tests.
- Added pure Databento definition-record adapter and tests; no provider client or network connection was created.
