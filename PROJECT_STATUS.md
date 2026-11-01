# DEZZTA CHART — Project Status

Last audited: 2026-11-01
Repository: deszztagd377-pixel/dezzta-chart
Baseline branch: main
Working branch: phase-2/market-data-foundation

## Overall progress

- Estimated overall progress toward the intended full application: 15%.
- This is a planning estimate based on completed product capabilities, not a measured code-line percentage.
- Product implementation progress in Phase 2: 0% at the start of this branch; repository audit and planning only.

## Current foundation

- React 18, TypeScript 5, Vite 4.
- Lightweight Charts 5 is installed.
- Existing candlestick chart currently uses hard-coded sample OHLC values from January 2024.
- Existing chart interaction includes zoom/scroll and crosshair configuration.
- A timeframe type and selector exist for second, minute, hour, day, week, and month intervals.
- An OHLCV aggregation utility and Vitest unit tests exist.
- GitHub Actions runs unit tests and a production build.
- The latest run for the audited main commit completed successfully.

## Verified limitations

- No live market-data provider or backend is currently configured in the repository.
- The timeframe selector updates React state, but the chart currently only changes the seconds-visible display option; it does not yet load or aggregate data for the selected timeframe.
- The existing sample candles are not real market data.
- Watchlist and Settings navigation currently changes only the selected navigation item; there are no implemented pages behind them.
- Drawing tools, Footprint, Heatmap, persistence, and Android packaging are not implemented in the audited tree.
- No package-lock.json was present in the audited repository tree.

## Phase 2 — Market Data Foundation

Status: provider, initial instrument scope, and deployment direction selected; implementation not started.

### Selected provider and data requirements

- Primary provider: Databento.
- Primary CME dataset target: `GLBX.MDP3`, subject to account entitlement, instrument coverage, and exchange licensing.
- Target schema: `mbo` (Market by Order / Level 3), retaining the event-level order updates delivered by the provider.
- Initial instrument scope explicitly selected by the project owner:
  - `ES` — E-mini S&P 500 Futures.
  - `NQ` — E-mini Nasdaq-100 Futures.
  - `GC` — Gold Futures.
- These are futures product roots, not single fixed-expiry contracts. Contract resolution must use Databento instrument definitions/symbology and must account for expirations and rollovers; do not hard-code a stale contract month.
- Databento documents parent symbology for futures roots (for example, `ES.FUT`) and continuous-contract symbology for rolling contracts. The implementation must choose and document the appropriate representation for charting, and must filter/identify outright futures versus spreads using instrument definitions rather than assuming every parent-symbol result is an outright contract.
- The project owner prioritizes strict data accuracy and lossless handling. The system must not intentionally sample, aggregate, conflate, or discard valid MBO events in the ingestion path.
- Never claim “100% raw exchange bytes” or absolute zero processing: Databento documents its Live service as a normalized feed with parsing, normalization, and book construction. Preserve the provider-delivered DBN records and event metadata before any application-specific transformations where licensing and storage terms permit.
- Databento's official Live Raw API uses a binary protocol over TCP/IP sockets, not WebSockets. The backend will connect to Databento using its official Raw API/client library. The app-facing DEZZTA CHART service may publish received events to clients over our own WebSocket connection.
- Deployment decision: ordinary cloud backend initially, prioritizing development efficiency. No Aurora I colocation or dedicated cross-connect in this phase.
- Cloud deployment does not itself guarantee lossless end-to-end delivery. The backend must implement bounded buffering, backpressure, durable capture where appropriate, sequence/quality monitoring, reconnect/replay or MBO snapshot recovery, and explicit gap detection. If data integrity cannot be maintained, mark the stream degraded and recover rather than silently presenting incomplete data as complete.
- Credentials remain server-side and must never be embedded in the React bundle or Android app.

### Target architecture

1. Databento Live Raw API (TCP) → secure backend ingestion service in ordinary cloud hosting.
2. Subscribe to the selected ES, NQ, and GC futures product roots using verified Databento symbology and instrument definitions; resolve active/continuous contracts explicitly and safely across rollovers.
3. Preserve incoming provider records and timestamps; validate sequence/quality indicators and detect gaps without silently filtering valid events.
4. Maintain/rebuild MBO book state and derive chart-facing data in separate downstream stages; retain a clear distinction between original provider records and derived values.
5. Backend → authenticated DEZZTA CHART WebSocket → React/Android clients.
6. Historical data and recovery use Databento's supported historical/intraday replay and MBO snapshot mechanisms as applicable.

Planned engineering sequence:
1. Confirm account entitlement, exchange licensing, supported ES/NQ/GC instrument coverage, and operating budget with the account owner.
2. Verify contract symbology, instrument definitions, expiration/roll rules, and the exact Databento SDK/API supported for the chosen backend runtime.
3. Define normalized event contracts while preserving original provider record metadata.
4. Build and test secure backend ingestion and WebSocket fan-out with replay, reconnect, gap detection, and backpressure.
5. Connect historical candle loading and timeframe aggregation to the existing chart.
6. Verify data integrity under disconnects, bursts, and recovery; document any transformations and limitations before claiming lossless behavior.

## Non-negotiable product constraints

- Preserve normal candlestick spacing when Footprint mode is OFF.
- Only Footprint ON may activate a dedicated spaced-candle/cluster layout.
- Do not implement Footprint or Heatmap visuals before the project owner supplies their reference images.
- Preserve existing working chart interactions and avoid unrelated visual redesign.
- Do not assume a market-data provider, API, feed entitlement, or bid/ask capability that has not been verified.

## Change log

### 2026-11-01
- Created the Phase 2 working branch from the audited main branch.
- Completed a read-only inspection of all files in the repository tree.
- Recorded Databento as primary provider, ordinary cloud hosting, strict data-accuracy priority, MBO target schema, and TCP-ingest-to-app-WebSocket architecture.
- Confirmed the initial futures product scope: ES, NQ, and GC.
- Recorded the need for instrument-definition-based contract resolution and rollover handling; no fixed expiry contract is hard-coded.
- No product source files changed; market-data implementation remains unstarted.
