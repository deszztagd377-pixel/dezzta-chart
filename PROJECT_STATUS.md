# DEZZTA CHART — Project Status

Last audited: 2026-11-01
Repository: deszztagd377-pixel/dezzta-chart
Baseline branch: main
Working branch: phase-2/market-data-foundation

## Overall progress

- Estimated overall progress toward the intended full application: 17%.
- This is a planning estimate based on completed product capabilities, not a measured code-line percentage.
- Phase 2 foundation progress: market-data DTOs, contract documentation, Python/FastAPI backend scaffold, and validated instrument-catalog foundation are in place; provider definition retrieval, live ingestion, event broadcasting, persistence, recovery, and chart integration remain unimplemented.

## Current foundation

- React 18, TypeScript 5, Vite 4.
- Lightweight Charts 5 is installed.
- Existing candlestick chart currently uses hard-coded sample OHLC values from January 2024.
- Existing chart interaction includes zoom/scroll and crosshair configuration.
- A timeframe type and selector exist for second, minute, hour, day, week, and month intervals.
- An OHLCV aggregation utility and Vitest unit tests exist.
- GitHub Actions runs unit tests and a production build.
- The latest audited CI run completed successfully before this instrument-catalog change; the current commit still requires CI verification.

## Verified limitations

- No live market-data provider or backend is currently configured in the repository.
- The timeframe selector updates React state, but the chart currently only changes the seconds-visible display option; it does not yet load or aggregate data for the selected timeframe.
- The existing sample candles are not real market data.
- Watchlist and Settings navigation currently changes only the selected navigation item; there are no implemented pages behind them.
- Drawing tools, Footprint, Heatmap, persistence, and Android packaging are not implemented.
- No package-lock.json was present in the audited repository tree.

## Phase 2 — Market Data Foundation

Status: provider, initial instrument scope, and deployment direction selected; transport-contract, backend, and instrument-catalog scaffolds added; live integration not started.

### Selected provider and data requirements

- Primary provider: Databento.
- Primary CME dataset target: `GLBX.MDP3`, subject to account entitlement, instrument coverage, and exchange licensing.
- Target schema: `mbo` (Market by Order / Level 3), retaining the event-level order updates delivered by the provider.
- Initial instrument scope explicitly selected by the project owner:
  - `ES` — E-mini S&P 500 Futures.
  - `NQ` — E-mini Nasdaq-100 Futures.
  - `GC` — Gold Futures.
- These are futures product roots, not single fixed-expiry contracts. Contract resolution must use Databento instrument definitions/symbology and must account for expirations and rollovers; do not hard-code a stale contract month.
- Databento supports multiple symbology types, including raw symbols, publisher instrument IDs, parent products, and continuous-contract aliases. A continuous alias is not a substitute for maintaining the explicit contract-to-instrument mapping needed by this application. See the official [Live API documentation](https://databento.com/docs/api-live?lang=python).
- The project owner prioritizes strict data accuracy and lossless handling. The system must not intentionally sample, aggregate, conflate, or discard valid MBO events in the ingestion path.
- Never claim “100% raw exchange bytes” or absolute zero processing: Databento documents its Live service as a normalized feed. Preserve provider-delivered DBN records and event metadata before application-specific transformations where licensing and storage terms permit.
- Databento's official Live Raw API uses a binary protocol over TCP/IP, not WebSockets. The backend connects to Databento using its official client; the app-facing service may publish events over our own WebSocket.
- Deployment decision: ordinary cloud backend initially. No colocation or dedicated cross-connect in this phase.
- Cloud hosting does not itself guarantee lossless delivery. The backend must implement bounded buffering, backpressure, durable capture where appropriate, sequence/quality monitoring, reconnect/replay or MBO snapshot recovery, and explicit gap detection.
- Credentials remain server-side and must never be embedded in the React bundle or Android app.

### Target architecture

1. Databento Live Raw API (TCP) → secure backend ingestion service.
2. Resolve selected ES, NQ, and GC outright futures from verified instrument definitions; never fabricate expiry symbols or silently treat spreads as outright contracts.
3. Preserve incoming provider records and timestamps; validate sequence/quality indicators and detect gaps without silently filtering valid events.
4. Maintain/rebuild MBO book state and derive chart-facing data in separate downstream stages.
5. Backend → authenticated DEZZTA CHART WebSocket → React/Android clients.
6. Historical data and recovery use supported historical/intraday replay and MBO snapshot mechanisms as applicable.

### Completed in this phase

- FastAPI backend health/status endpoints and authenticated app-facing WebSocket scaffold.
- Provider-neutral `InstrumentCatalog` validates expiry-specific ES/NQ/GC outright-futures definitions.
- Contract definitions are sorted by expiry and can be filtered by root.
- Unknown roots, unsupported symbols, missing expiry, malformed identifiers, and non-outright instruments are rejected.
- No front contract is auto-selected; rollover policy remains intentionally unimplemented until validated.
- HTTP endpoint `GET /v1/instruments` exposes catalog state and honestly returns an empty contract list until a provider definition source is added.
- Unit tests cover definition normalization, invalid definitions, sorting, catalog replacement, and API responses.

### Planned engineering sequence

1. Confirm account entitlement, exchange licensing, supported instrument coverage, and operating budget with the account owner.
2. Verify contract symbology, instrument definitions, expiration/roll rules, and the SDK/API supported for the backend runtime.
3. Build a reproducible Python backend environment using verified official client and WebSocket server versions.
4. Implement secure backend ingestion and WebSocket fan-out with replay, reconnect, gap detection, and backpressure.
5. Connect historical candle loading and timeframe aggregation to the existing chart.
6. Verify data integrity under disconnects, bursts, and recovery; document transformations and limitations.

## Non-negotiable product constraints

- Preserve normal candlestick spacing when Footprint mode is OFF.
- Only Footprint ON may activate a dedicated spaced-candle/cluster layout.
- Do not implement Footprint or Heatmap visuals before the project owner supplies their reference images.
- Preserve existing working chart interactions and avoid unrelated visual redesign.
- Do not assume a provider, API, feed entitlement, or bid/ask capability that has not been verified.

## Change log

### 2026-11-01
- Created the Phase 2 working branch from the audited main branch.
- Recorded Databento as primary provider, ordinary cloud hosting, MBO target schema, and TCP-ingest-to-app-WebSocket architecture.
- Confirmed initial product scope: ES, NQ, and GC.
- Added typed frontend market-data contracts and market-data transport documentation.
- Added the FastAPI backend scaffold, authenticated WebSocket status channel, and Python CI test stage.
- Added a provider-neutral futures instrument catalog with validation, expiry sorting, root filtering, API exposure, and tests.
- No live provider ingestion, provider definition retrieval, storage, or chart integration has been implemented.
