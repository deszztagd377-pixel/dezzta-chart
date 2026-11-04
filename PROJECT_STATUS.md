# DEZZTA CHART — Project Status

Last audited: 2026-11-04
Repository: deszztagd377-pixel/dezzta-chart
Baseline branch: main
Working branch: phase-2/market-data-foundation

## Overall progress

- Estimated overall progress toward the intended full application: 19.60%.
- Progress is a weighted milestone estimate, not a code-line percentage or a claim of scientific measurement. Decimal precision is recorded to two places for consistent tracking.
- Latest increment: +0.20 percentage points (19.40% → 19.60%) for Firebase ID-token verification on the backend WebSocket route, exact canonical-instrument/provider-mapping validation, deny-by-default per-account entitlement checks, 60-second authorization rechecks, regression coverage, and security documentation. This is backend security groundwork only; no frontend WebSocket client, sign-in UI, live provider delivery, or deployment credit is included.
- Phase 2 includes the FastAPI backend, verified-definition catalog lifecycle, optional Databento SDK source adapters, bounded OHLCV ingestion, validated HTTP snapshots, and an authenticated backend WebSocket broadcaster with atomic snapshot/watermark handoff. The frontend still uses HTTP snapshots; its WebSocket client/authentication/reconnect integration, durable coverage/gap recovery, backend deployment, and verified live provider delivery remain outstanding. Instrument definitions and normalized OHLCV base/derived bars now have durable SQLite storage and restart restoration.

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

- No live market-data provider session is configured. Optional Databento source adapters and the provider lifecycle exist behind explicit server-side flags, but the current deployment has no provider credentials/session and no real provider delivery is claimed.
- The selected timeframe is included in the chart's read-only backend OHLCV snapshot request. The chart displays backend bars only after exact-series validation; until a backend is deployed and trusted bars are available, the clearly labelled DEMO fixture remains visible. Backend OHLCV WebSocket broadcast is implemented, but the frontend has not connected to it; end-to-end streaming is not implemented.
- Watchlist now displays an explicitly offline, read-only supported-product catalog fixture for ES/NQ/GC; no expiry-specific contracts are fabricated.
- The existing sample candles are not real market data.
- Global indicator requirement: every indicator must be designed for compatibility across all supported chart timeframes, including second-based intervals. This is a target to validate per indicator, not a claim that every calculation is automatically valid on every timeframe.
- Performance requirement: minimize avoidable latency, rendering work, memory growth, and UI blocking; test responsiveness under representative data loads. Zero bugs or zero lag cannot be guaranteed, so regression testing and explicit error handling are mandatory.
- Candle timer requirement: show a remaining-time countdown at the right side of the chart, aligned near the price scale. Derive it from candle interval boundaries and a synchronized clock; never hardcode a countdown or imply exchange-synchronized time when only the device clock is available.
- Data freshness requirement: clearly distinguish source-event time, receive time, and display time. Do not label sample, delayed, or unsynchronized data as live/real-time. End-to-end freshness depends on provider, network, backend, and device.
- Watchlist contains a read-only offline ES/NQ/GC catalog fixture. Settings exposes the grid visibility preference and reset behavior; broader account, chart-layout, and indicator settings are not implemented.
- Drawing tools, indicator tier navigation, Volume Profile, Footprint, Heatmap, Liquidation Maps, chart-layout/settings persistence, and Android packaging are not implemented.
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

- No production live or historical provider session, provider download, or subscription is configured or verified.
- Databento SDK source adapters and the normalized bounded OHLCV ingestion path are implemented, but provider access is disabled by default and no real account/session has been validated. Do not enable provider flags without a separate review of entitlement, exchange licensing, explicit symbols, historical query costs, and operational limits.
- Backend OHLCV WebSocket broadcast and snapshot/watermark handoff are implemented. The frontend still requests HTTP snapshots and publishes validated bars into the shared store; it does not yet authenticate, subscribe, reconnect, resynchronize, or apply stream updates. No visible indicator controls/panes have been built yet. The frontend requires `VITE_MARKET_DATA_API_BASE_URL` to reach a deployed backend.
- Historical provider definition refresh now feeds the durable journal/synchronizer when explicitly invoked by the provider lifecycle. There is no periodic refresh scheduler, and no real provider account/session has been validated.
- Databento definition events, canonical instruments, point-in-time provider mappings, and metadata revisions are persisted in SQLite with replay-safe transitions. OHLCV base and derived bars are also persisted with bounded per-series retention, exact decimal text, nanosecond timestamps, and a durable local-sequence high-water mark. The in-memory catalog and coverage tracker remain process-local; durable coverage intervals, historical gap detection/backfill orchestration, and frontend stream replay remain unimplemented.
- The authenticated WebSocket supports exact-series OHLCV snapshot subscriptions and bounded in-memory updates for accepted base and derived bars. The underlying bars now survive backend restart in SQLite, but the WebSocket event stream itself is not a durable event log and does not replay missed client updates. It does not provide order-book/MBO events.
- No brokerage or order-execution integration.
- No Footprint, Heatmap, or Liquidation Maps implementation; these three Exclusive Indicators are reserved for one coordinated Claude-assisted workflow after the project owner supplies visual references for each.
- Mid Tier is undecided. Earlier candidates such as VWAP, ATR, ADX/DMI, Stochastic, CCI, OBV, MFI, Ichimoku Cloud, Supertrend, and Keltner Channels are discussion-only and are not approved members. Volume Profile is not in Mid Tier.
- Low Tier must contain exactly 15 common/popular TradingView-style indicators. RSI, MACD, and Bollinger Bands are the only exact names recovered from prior approval; the other 12 names must be confirmed before their implementation. Do not leave the category empty or invent a claimed owner-approved list.
- A separate Tools-menu Volume Profile tool is also planned: it displays a compact profile visualization at the chart side, without the full indicator's data-value presentation; users can move/resize its selected chart range and the profile recalculates for that range.
- Indicator navigation is planned as three categories: Low Tier (exactly 15 common indicators), Mid Tier (owner selection pending), and Exclusive Indicator Pro (Footprint PRO 2GD, Heatmap, Liquidation Maps, and full Volume Profile with detailed values). Tools are a separate entry point, not another indicator category.
- Exclusive Indicators remain owner-controlled: only the project owner can add new members to this tier.
- These are recorded product requirements only; no indicator or Tools UI implementation has started.

## Planned engineering sequence

1. **Completed foundation:** populate the durable canonical instrument registry, point-in-time provider mappings, and versioned metadata from strictly normalized provider definitions; journal source events before processing and recover pending events after restart. Live credentials, provider delivery, and scheduled refresh remain separate validations.
2. Define a trusted, admin-only entitlement grant process for canonical instruments; keep client-facing grant endpoints disabled.
3. Connect the approved Firebase app sign-in/session flow so the frontend can obtain and refresh Firebase ID tokens. The exact sign-in methods and public Firebase app configuration must be supplied/approved before UI integration.
4. Implement the frontend WebSocket client with the verified ID-token provider, canonical instrument ID, exact-series subscription, snapshot validation, sequence guard, heartbeat, bounded reconnect, and fresh-snapshot recovery.
5. Publish accepted stream updates through the shared market-data store so the chart and all indicators consume one exact instrument/timeframe series; then smoke-test the backend and frontend against a deployed API origin with provider features disabled.
6. Build the three indicator-tier navigation categories and visible indicator controls/overlays/panes on top of `useMarketIndicators`, with timeframe compatibility and performance tests. Low Tier requires the approved 15-item list; Mid Tier remains pending owner selection.
7. Implement the full Exclusive Volume Profile and the separate compact movable-range Volume Profile Tool as distinct features.
8. Integrate Footprint PRO 2GD, Heatmap, and Liquidation Maps in the coordinated Claude-assisted workflow after the owner supplies the required visual references and the complete source/reference package is available.

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


### 2026-11-02 — HTTP OHLCV client foundation
- Added `src/services/ohlcvClient.ts`: read-only GET client for the existing `/v1/ohlcv` endpoint, using the backend's exact snake_case query parameter names.
- Requests require a complete series identity (dataset, publisher ID, instrument ID, raw symbol, timeframe); no contract identity or API URL is fabricated.
- Added request timeout, caller cancellation, no-store caching, HTTP/network/JSON/schema/configuration error classification, and validated conversion through the existing OHLCV adapter.
- Snapshot outcomes distinguish ready, degraded, and unavailable. A non-live feed state is never reported as confirmed ready; a response with no bars matching the exact requested series is unavailable.
- Added `src/services/ohlcvClient.test.ts` with 13 tests covering query construction, exact series isolation, ready/degraded/unavailable states, malformed responses, HTTP/network failures, timeout, cancellation, and invalid configuration.
- GitHub Actions run #101 initially exposed a test-harness unhandled-rejection timing issue in the timeout test. The test was corrected to attach its rejection assertion before advancing fake timers; the corrected latest run is #102.
- Latest implementation commit: `1f8f9fc7075902879cbc27363d1bd9fbe2516ba2`; timeout-test correction commit: `945601c2cee56db39956d174b527e8b8150f24b4`.
- Remaining: no backend base URL or verified selected contract is configured in the frontend; the client is not yet wired into the chart. DEMO candles remain clearly labeled and unchanged. No live data is claimed.


### 2026-11-02 — Verified instrument catalog and selection lifecycle
- Added `src/types/instrumentCatalogApi.ts` for the backend's provider-backed catalog response and outright futures contract metadata.
- Added `src/services/instrumentCatalogClient.ts` to call the existing read-only `GET /v1/instruments?root=...` endpoint with timeout, cancellation, no-store caching, and explicit configuration/network/HTTP/JSON/schema errors.
- Added runtime validation for supported roots, outright futures class, raw-symbol/root consistency, positive safe provider identifiers, ISO expiration dates, decimal tick-size strings, dataset consistency, catalog counts, and duplicate contract identities.
- The catalog validator accounts for backend semantics: `state` describes the global catalog before an optional root filter, so a ready global catalog may legitimately return zero contracts for one selected root.
- Rebuilt Watchlist as a functional ES/NQ/GC filter with contract search (symbol, expiry, instrument ID), explicit contract selection, selected-metadata display, clear selection, loading/empty/error states, and retry. Requests are cancelled when the selected product changes; the App retains the selected metadata while navigating between tabs.
- Added `.env.example` with the non-secret `VITE_MARKET_DATA_API_BASE_URL` setting. No API key or provider credential is exposed to the frontend.
- Added focused parser and HTTP client tests, including invalid calendar dates, state/count consistency, empty root-filtered results, duplicate identities, cancellation, timeout, and request construction.
- The chart deliberately remains on its clearly labelled DEMO fixture. Contract selection is metadata-only until a backend URL, verified OHLCV series, and chart data lifecycle are connected. No live market data is claimed.
- Latest code commits: `eade18471527f9fb9e4cff5733c5de7127676398`, `f8b0c9295ad8937b02e14fa1419db25337e4ec69`, `9e601f68026dee400f3b90698335b0094f364e27`, `5616ca598251320c27f644e3f40f3a99c8bfad67`.
- Final CI and deployment status must be confirmed on the latest documentation commit before this stage is called fully verified.


### 2026-11-02 — Selected contract and timeframe chart data lifecycle
- Connected the selected catalog contract and selected timeframe to the existing validated `fetchOhlcvSnapshot` client.
- Every request carries dataset, publisher ID, instrument ID, raw symbol, and timeframe from the selected verified contract; the client continues to validate the full response before conversion.
- Switching contract or timeframe aborts the previous request. The chart first resets to its explicitly labelled DEMO fixture, so bars from the previous contract cannot remain visible while a new request is pending.
- Validated backend bars replace the demo fixture only when a non-empty exact-series result is available. Degraded feed results are labelled DEGRADED; unavailable and request errors leave the DEMO fixture visible with an explicit reason.
- Added `src/utils/candlestickSeriesData.ts` and tests to convert adapter epoch-second values into Lightweight Charts UTC timestamps without a milliseconds conversion.
- Added a non-secret `VITE_MARKET_DATA_API_BASE_URL` configuration path. The value is currently not configured in the deployed frontend, so production will honestly show the API configuration error and keep the DEMO chart until a backend URL is provided.
- Latest integration commit: `56a265ebc68b72402a3907f0ed644ab8281547b1`. The final branch-head CI and Vercel deployment are being verified.


### 2026-11-02 — Portable backend deployment foundation
- Added `backend/Dockerfile`: Python 3.12 slim image, runtime dependencies installed from the backend manifest, non-root runtime user, platform `PORT` support, and `/health` container health check.
- Added `docs/BACKEND_DEPLOYMENT.md` with reproducible build/run/smoke-test commands, exact-origin CORS guidance, Vercel API-base configuration, and secret-handling boundaries.
- Updated backend documentation to accurately distinguish implemented optional Databento source/provider lifecycle code from an actually configured or verified production provider session. Corrected stale claims that provider adapters did not exist.
- Extended GitHub Actions to build the backend container image after frontend tests/build and backend tests. This validates image construction, not a hosted deployment or external provider connectivity.
- Provider switches remain off by default; no API key, WebSocket token, or other secret was added to the repository.
- Hosting provider intentionally not selected: cost, region, availability/sleep behavior, and account controls must be reviewed before deployment.
- The latest Vercel status for the shared-indicator commit is failure with the platform message `upgradeToPro=build-rate-limit`; this is a hosting/build-rate limit, not evidence of a source compilation error. The latest GitHub Actions run result is not exposed by the available run-status response and is not claimed as passed here.
- Overall estimated progress: 19.05% (+0.20 percentage points for a reproducible backend container foundation and CI build step; no credit for actual backend deployment).


### 2026-11-02 — Shared chart and indicator data foundation
- Added `src/services/marketDataStore.ts` as the single in-memory source of truth for exact-series OHLCV bars, identity, status, detail, and monotonically increasing revision. Snapshots and bar objects are immutable; invalid identities, chronology, OHLCV boundaries, and non-ready bar publication are rejected.
- Connected `CandlestickChart` to publish only validated non-empty backend bars. Contract/timeframe switches synchronously clear old indicator input; DEMO candles remain chart-only and are never exposed to indicator calculations.
- Added `useMarketDataSnapshot()` for React consumers and `useMarketIndicators()` so indicator calculations are derived only from the same backend series selected by the chart.
- Added a reusable calculation foundation for SMA, EMA, Wilder RSI, MACD, and Bollinger Bands. Outputs align to source bars and retain null warm-up values; input validation is applied even when the available history is shorter than the warm-up period.
- Added unit tests for shared-store immutability, subscriber notifications, exact identity, stale-series clearing, invalid bars, calculation alignment, warm-up periods, edge cases, and invalid inputs.
- Added `docs/INDICATOR_DATA_ARCHITECTURE.md` defining the single-source-of-truth flow and future streaming integration contract.
- Important limitation: the current frontend still requests HTTP snapshots. Continuous live streaming, visible indicator UI, provider connectivity, and real-time Android validation are not implemented or claimed. The store is the shared integration point for future validated stream updates.
- Overall estimated progress: 19.40% (+0.35 percentage points for tested shared data architecture and reusable indicator calculations; no credit for visible indicator features or live streaming).

- Latest audited shared-indicator branch head at that earlier checkpoint: `aaed0226b8f55d7526c31b461238b357d05276a0`. The current stream-protocol work is recorded below; `main` remains untouched.

### 2026-11-02 — OHLCV stream protocol foundation (not yet connected)
- Added `src/services/ohlcvStreamProtocol.ts` with a versioned provider-neutral OHLCV update envelope, runtime validation, exact series-to-bar identity checks, and a per-stream sequence guard.
- Stream delivery sequence is deliberately separate from the nested local OHLCV bar revision sequence; the two counters have different scopes and cannot be substituted.
- Sequence decisions explicitly distinguish accepted-next, duplicate, stale/out-of-order, gap, wrong stream, and wrong series. A gap does not advance the watermark; only a verified snapshot watermark may reset it.
- Reuses the existing strict OHLCV snapshot validator so streamed bars inherit decimal-string, nanosecond, timeframe, OHLCV-boundary, and identity checks.
- Added focused tests for envelope/version validation, invalid identity and OHLCV payloads, duplicate/stale/gap handling, snapshot watermark reset, and stream/series isolation.
- Added `docs/OHLCV_STREAM_PROTOCOL.md` with the event shape, sequence semantics, atomic snapshot/watermark handshake requirements, bounded-queue policy, and recovery milestones.
- This is protocol and frontend validation groundwork only. No WebSocket OHLCV broadcast, frontend socket client, atomic snapshot watermark, reconnect loop, or stream-to-store publication is implemented yet. The existing backend WebSocket remains status-only.
- Overall progress remains 19.40% until the new tests/build and branch-head CI are independently verified; no credit is assigned for a live stream or user-visible indicator feature.
- Latest protocol implementation commit: `3b3cdb8eefbde740f8e44435fde6b9ebc96d6edb`; architecture documentation follow-up: `841acb7248e86a78ead0109c25ecd9341c7f4c46`. Immediately before this status refresh, the branch comparison was 149 commits ahead of `main`, 0 behind. The latest visible Vercel status remains a build-rate-limit failure; the available GitHub workflow-run lookup does not expose push-triggered runs, so CI is not claimed as passed.

### 2026-11-02 — Backend OHLCV WebSocket broadcast and snapshot handoff
- Added `backend/app/ohlcv_stream.py`: bounded per-series fan-out with an independent monotonic sequence per subscriber, unique stream/event IDs, exact series filtering, canonical decimal-string serialization, and explicit slow-consumer overflow state.
- Added an authenticated WebSocket subscription message (`market_data.subscribe`, version 1). The server returns a versioned OHLCV snapshot carrying `streamId` and `watermark`, then emits ordered `market_data.ohlcv.update` events.
- Snapshot query and subscription registration are synchronous on the same asyncio event loop, with no await between them. This is an atomic snapshot/watermark boundary relative to the current single-writer in-memory ingestion design.
- Connected accepted base-bar revisions to the stream hub. Updated the aggregation layer so accepted derived timeframe bar revisions are also broadcast to matching subscriptions; this is required for chart timeframes such as 5s/1m that are derived from base 1s data.
- Each client queue is bounded (256 updates). Queue overflow marks the subscriber for close with WebSocket code 1013, requiring a fresh snapshot; updates are not silently dropped while the connection remains active.
- Added backend tests for snapshot/watermark handoff, exact-series isolation, slow-consumer overflow, derived timeframe updates, authenticated snapshot delivery, invalid subscription rejection, and delivery from a fake live-ingestion callback.
- Updated backend README and stream/data architecture documentation.
- Important limitations: frontend WebSocket authentication/subscription/client reconnect is not implemented; the frontend has not yet applied stream updates to `marketDataStore`. Delivery is in-memory only and cannot replay across backend restart. No provider credentials/session or actual market feed are enabled or verified. No MBO/order-book feed is provided.
- Overall progress remains 19.40% until branch-head CI and the new backend tests are independently verified. No live-data or end-to-end frontend streaming credit is assigned.
- Latest code/test commit: `d9c9ed67ca52884247fb293d3adefa77ca010924`; final WebSocket status cleanup: `91284c5789ebb540fb09264b32e4f9a521f50eda`. Branch comparison at this status refresh: 168 commits ahead of `main`, 0 behind; `main` remains untouched. Latest visible Vercel status is failure with `upgradeToPro=build-rate-limit` (platform build-rate limit, not proof of a source compile failure). The available GitHub workflow-run lookup exposes no push-triggered run, so CI is not claimed as passed.


### 2026-11-02 — Backend OHLCV WebSocket broadcast and snapshot handoff audit
- Verified the active working branch is `phase-2/market-data-foundation`; comparison reports 172 commits ahead of `main` and 0 behind. `main` was not modified.
- Verified backend route `/ws/market-data` authenticates, accepts a version 1 exact-series subscription, sends a validated OHLCV snapshot with a stream ID and watermark, and then sends ordered updates.
- Verified `OhlcvStreamHub` uses bounded per-subscriber queues and forces a reconnect/resnapshot after overflow rather than silently skipping updates. Accepted base and derived timeframe revisions are wired into the hub.
- Verified frontend protocol parsing and sequence-guard groundwork exists, but no frontend WebSocket client is connected to the chart or shared store.
- Security gate: the backend currently uses one static server-configured WebSocket token. This is acceptable only as a controlled local/test scaffold; it must not be copied into the browser bundle or Android package. A production client requires a short-lived, narrowly scoped token delivered through a separately authenticated session or server-side gateway. No login/session provider is currently selected.
- CI status: not verified on the current branch head. The available commit-workflow lookup returned no push-triggered run; no test pass is claimed from this audit.
- Backend deployment and provider delivery remain unverified. Databento credentials/session are not configured; no real market feed is claimed.
- Overall progress remains 19.40%; no credit is assigned for frontend streaming, live provider delivery, deployment, or visible indicator UI.


### 2026-11-02 — Frontend streaming and authentication security gate review
- Re-audited the active branch's backend WebSocket route, frontend protocol parser/sequence guard, shared market-data store, HTTP snapshot client, and CI workflow definition.
- Confirmed the frontend has no WebSocket transport client; only protocol parsing and sequence-guard groundwork exists. No live stream integration or tests are claimed.
- Identified an additional production security requirement: the current WebSocket route validates series syntax and configured dataset, but does not authorize the authenticated principal for the requested publisher/instrument/raw-symbol/timeframe tuple. A shared static token is not a user identity or a series entitlement.
- Updated `docs/WEBSOCKET_AUTH_DESIGN.md` to record this authorization gap and require per-subscription entitlement checks backed by verified instrument definitions.
- The existing CI workflow is configured for pushes to this branch, but this audit did not obtain a verified latest-head run result. CI and tests remain unverified.
- Branch comparison after the documentation commits: 172 commits ahead of `main`, 0 behind. `main` remains untouched.
- No overall progress increase: frontend WebSocket transport, secure session/token issuance, per-series authorization, deployment, and live feed are still incomplete.


### 2026-11-02 — Multi-asset product direction and Firebase authentication prototype approval
- Owner confirmed the product direction includes equities, crypto, futures, FX, indices, and further asset classes where a verified source, venue, instrument definition, data schema, and license permit coverage. "All pairs" is a long-term coverage goal, not a claim that every global symbol is automatically available from one provider.
- Added `docs/MULTI_ASSET_MARKET_DATA_ARCHITECTURE.md` defining canonical instrument identity, provider-neutral adapters, asset-specific metadata, venue/session handling, source provenance, exact-series indicator rules, licensing gates, and staged delivery.
- Audited current implementation: `backend/app/instruments.py` and `backend/app/config.py` remain futures-focused, with ES/NQ/GC allow-list defaults; current instrument catalog and resolver are in-memory. The frontend shared store still uses futures-oriented exact series identity. Multi-asset support is therefore **not implemented** yet.
- Owner approved Firebase Authentication as the primary provider for an authentication prototype. Updated `docs/AUTH_PROVIDER_EVALUATION.md` to record the approval and require a provider-neutral identity verifier. No Firebase SDK, service account, credentials, token endpoint, WebSocket ticket, or per-series authorization code has been added yet.
- Firebase's official documentation confirms client ID-token retrieval and Python Admin SDK verification; ID tokens are short-lived (about one hour), while refresh tokens maintain sessions and can be revoked. See https://firebase.google.com/docs/auth/admin/verify-id-tokens and https://firebase.google.com/docs/auth/admin/manage-sessions.
- Databento coverage is dataset/venue-specific. It documents multiple asset classes, including equities, FX, futures, and options, but this does not establish universal global coverage or all crypto spot pairs. Exact availability, entitlements, and redistribution rights must be verified per product.
- No progress increase: these commits document approved architecture and do not implement multi-asset canonical IDs, authentication, live feed, persistence, frontend streaming, or deployment. Overall progress remains 19.40%.
- `main` remains untouched. Latest branch comparison and CI status must be checked separately; no CI pass is claimed by this status note.


### 2026-11-02 — Canonical multi-asset identity schema foundation
- Added an immutable provider-neutral canonical instrument schema for equity, ETF, crypto spot/perpetual, dated futures, options, FX pairs, and indices. The schema validates UUID identity, asset/type compatibility, venue/symbol, currency pairs, expiry, option-underlying relationships, and positive finite decimal metadata.
- Added matching frontend TypeScript contract and backend validation tests. Existing futures catalog, resolver, API routes, and selected-contract flow are intentionally unchanged in this first compatibility-safe step.
- Canonical UUIDs are registry-assigned and must be persisted; they are not derived from symbols or provider IDs. Provider mappings remain a separate identity layer.
- This is schema groundwork only: no durable registry/database, provider coverage, multi-asset catalog endpoint, entitlement system, Firebase integration, or live multi-asset data is implemented.
- Tests and CI must be run against the resulting branch head before claiming verification. Overall project progress remains 19.40% until implementation and test gates are independently verified.


### 2026-11-02 — Persistent instrument registry (SQLite adapter)
- Added a file-backed SQLite registry for immutable canonical instrument records and provider-scoped point-in-time mappings.
- Enabled foreign keys on every connection, WAL, bounded busy timeout, transactional writes with BEGIN IMMEDIATE, canonical-ID idempotency/conflict checks, immutable-row trigger, and database-level overlap triggers for provider mapping validity windows.
- Added bounded/filterable registry reads, exact timestamp mapping resolution, migration-version guard, and tests for restart durability, identity immutability, mapping scope, half-open validity windows, adjacent windows, overlap rejection, and concurrent writers.
- Integrated registry initialization into FastAPI application state with a backend-only database path setting. No public registry write endpoints were exposed; Firebase identity and per-series entitlement checks remain prerequisites.
- SQLite is a single-backend durable adapter only when deployed on a persistent volume. Multi-instance production requires a planned PostgreSQL adapter/migration and backup/restore validation.
- No live provider, exchange licensing, Firebase auth, public multi-asset catalog, or end-to-end real data is claimed by this milestone.
- Project progress remains 19.40% until the new and full regression suites are verified on the resulting branch head.


### 2026-11-02 — Provider metadata versioning design gate
- Audited the canonical identity value object, immutable SQLite registry, futures definition catalog, and in-memory point-in-time resolver before connecting provider refreshes.
- Identified a critical modeling boundary: the canonical value object contains both stable identity and mutable/provider-correctable trading metadata, while the SQLite canonical row is immutable. Directly persisting provider refreshes would either reject legitimate metadata revisions or weaken identity immutability.
- Added docs/INSTRUMENT_METADATA_VERSIONING.md defining three layers: stable canonical identity, append-only effective-time metadata revisions, and provider-scoped point-in-time mappings.
- Defined transaction, idempotency, out-of-order event, authoritative source, venue verification, migration, and unknown-history rules. No provider metadata is inferred and no historical validity is fabricated.
- This is an architecture gate only; no schema migration or provider ingestion integration is claimed. Existing ES/NQ/GC catalog and resolver remain unchanged.
- Project progress remains 19.40% until versioned metadata migration, provider integration, and regression tests are implemented and verified.

### 2026-11-04 — Branch-head verification and indicator-tier correction

- Re-verified the working branch `phase-2/market-data-foundation`. Before this documentation commit it was 302 commits ahead of `main` and 0 behind; this status-documentation commit makes the current comparison 303 ahead and 0 behind. `main` was not changed.
- Verified branch-head commit `65a63f0878476f52b22f9dae7a6f7f25b2888d77` with GitHub Actions run #293 (2026-11-03): frontend unit tests, frontend production build, backend tests, and backend Docker image build all completed successfully. This is CI evidence for that exact commit, not a claim of physical Android testing or live-provider connectivity.
- Audited the durable SQLite instrument registry: current schema version is 4, with sequential migrations v1→v2 (versioned metadata baseline), v2→v3 (relational option-underlying links), and v3→v4 (venue-scoped canonical identity uniqueness). Existing tests cover legacy migration preservation/rollback, unknown historical validity, append-only metadata revisions, half-open validity intervals, idempotent transitions, transaction rollback, out-of-order event rejection, and independent source timelines. The branch-head CI run passed the backend test job.
- The repository contains an educational simulated-footprint event fixture under `src/education/`; this is not the production Footprint engine. The production module directory `src/indicators/footprint/` and its complete engine/test integration are not yet present in the audited branch tree. Simulated educational fixtures must never be represented as real market trades or as the finished Footprint PRO 2GD indicator.
- Owner-confirmed indicator tier structure supersedes earlier planning notes: Low Tier contains exactly 15 common TradingView-style indicators; the exact 15-item selection is to be finalized before implementation. Mid Tier remains undecided until the owner supplies the preferred indicators. Exclusive Indicator Pro contains Footprint PRO 2GD, Heatmap, Liquidation Maps, and the full Volume Profile with detailed data/value presentation. Full Volume Profile is Exclusive, not Mid Tier.
- Any separate compact, movable-range Volume Profile chart tool remains a Tools feature and must not be confused with the full Exclusive Volume Profile indicator.
- Preserve the chart-layout invariant: normal candles and ordinary spacing remain unchanged while Footprint is OFF; only Footprint ON may activate the spaced-candle/cluster layout.
- Overall estimated progress remains 19.40%. No progress credit is assigned for the Footprint engine, visible 15-indicator Low Tier, tier navigation, full Volume Profile, Heatmap, Liquidation Maps, Android packaging, live provider delivery, or on-device verification until those deliverables are implemented and independently tested.
- Next engineering gate: safely persist and integrate the complete Footprint source modules, run its dedicated regression suite alongside existing frontend/backend tests, then implement the indicator-tier UI without disturbing the shared market-data foundation.

### 2026-11-04 — Firebase-authenticated WebSocket and per-instrument authorization

- Replaced the WebSocket route's shared static-token comparison with Firebase ID-token verification through the approved `FirebaseIdentityVerifier`. Verification runs in a worker thread; invalid credentials are rejected and unavailable identity verification fails closed.
- Each subscription now requires a canonical instrument UUID in addition to the exact provider series identity.
- Before snapshot/watermark registration, the backend resolves the current provider/dataset/publisher/instrument mapping, verifies the raw symbol and canonical UUID match, checks that the canonical instrument is active, and checks the verified Firebase principal's explicit SQLite entitlement. Missing or mismatched mapping, inactive instrument, or absent/revoked entitlement is denied by default.
- Active subscriptions recheck the mapping and entitlement every 60 seconds; revoked or changed access closes the connection.
- Added isolated SQLite test fixtures and regression coverage for Firebase authentication, exact-series subscription, deny-by-default entitlement behavior, and authenticated live-update delivery.
- GitHub Actions run #301 on commit `d1a7c9602e59477bcb1e7fc77da58348d9a981aa` passed frontend tests, frontend production build, backend tests (277 passed), and backend Docker image build. The documentation-only follow-up run is checked separately.
- The legacy `MARKET_DATA_WS_TOKEN` setting remains for compatibility but is no longer read by the WebSocket route.
- Remaining gates: frontend Firebase sign-in/session integration, frontend WebSocket client and reconnect/resnapshot logic, canonical identity population from verified provider definitions, token-expiry/re-authentication policy for long-lived connections, backend deployment, and real provider delivery.
- Overall progress: 19.60%. No visible indicator UI, Footprint, Heatmap, Liquidation Maps, full Volume Profile, or Android packaging credit is assigned.
- At this audit checkpoint, `phase-2/market-data-foundation` compared 311 commits ahead of `main` and 0 behind. `main` remains untouched.


### 2026-11-04 — Databento definition metadata capture groundwork

- Expanded `backend/app/databento_definitions.py` to retain authoritative definition fields needed by the upcoming registry synchronizer: exchange, asset/security type, settlement currency, unit-of-measure quantity and unit, contract multiplier fields, activation, security update action, display factor, lot-size metadata, and underlying.
- Null-padded ASCII text fields are normalized; numeric provider values remain unchanged in this low-level adapter so fixed-point scaling is applied exactly once by a typed domain layer.
- Added focused tests for provider metadata preservation, byte decoding, invalid non-ASCII text, and existing record-order behavior.
- Databento's documented schema identifies `unit_of_measure_qty` + `unit_of_measure` as contract-size metadata, `exchange` as the exchange identifier, and definitions as point-in-time records. The adapter now captures these fields but does not yet interpret lifecycle actions or write to SQLite.
- Existing atomic provider-event persistence primitives (`SQLiteProviderDefinitionEventRepository`) remain the intended transaction boundary. Canonical UUID assignment, authoritative metadata normalization, event ordering/action processing, and provider-to-registry synchronization are still pending.
- No overall progress increase: this is metadata-capture groundwork, not durable provider integration or live-feed verification. Overall progress remains 19.60%. GitHub Actions runs for the two code commits are in progress; no pass is claimed yet. `main` remains untouched.


### 2026-11-04 — Databento adapter CI correction

- The first adapter test run failed because the new byte fixtures contained escaped text rather than actual NUL/non-ASCII bytes; the two negative tests therefore did not exercise invalid byte input.
- Corrected the adapter's null-byte trimming and corrected the test fixtures to contain actual binary byte values. The correction is committed in `0cfc3eed15bad9e03a1291345d29efff73652e37` and `d56a39e0b8c911a38a7a3c86e56a2a929357c071`.
- The branch-head workflow run `41819590174` for `d56a39e0b8c911a38a7a3c86e56a2a929357c071` has passed frontend unit tests and the frontend production build. Backend dependency installation is still running; backend tests and Docker build are not yet verified.
- No overall progress increase: Databento provider definitions are not yet synchronized into the persistent canonical registry. Overall progress remains 19.60%. `main` remains untouched.


### 2026-11-04 — Databento definition lifecycle event processing

- Added `InstrumentCatalog.apply_definition_event` for Databento Add (`A`), Modify (`M`), and Delete (`D`) records. Delete records require only provider identity and event timestamp; they no longer depend on expiry metadata.
- The adapter now requires the provider lifecycle action and retains exact provider timestamps/integers.
- `ProviderManager.refresh_definitions` now applies historical definition events in stable ascending `ts_event` order instead of treating a point-in-time event stream as a flat complete snapshot.
- Added exclusive event-time closure to `InstrumentResolver`. Modify transitions close the prior mapping before opening the new one; Delete closes the active mapping. Existing tombstones prevent delayed older Add/Modify events from resurrecting deleted instruments.
- Added regression tests for Add/Modify/Delete ordering, Delete without expiration, stale resurrection prevention, resolver mapping boundaries, and provider refresh integration.
- GitHub Actions run `41820405604` on commit `5338c0df0265515606e8bf942f65b537672d92df` passed frontend unit tests, frontend production build, backend tests, and backend Docker image build.
- This is an in-memory lifecycle-processing milestone only. Canonical UUID assignment and atomic SQLite persistence of provider mappings + metadata revisions remain pending. The canonical model also needs a deliberate distinction between Databento `unit_of_measure_qty` (contract size) and Databento `contract_multiplier` (deliverable multiplier); no field is being overloaded.
- Overall project progress remains 19.60% because durable provider-to-registry synchronization and production verification are not complete. At this checkpoint the branch was 328 commits ahead of `main` and 0 behind. `main` remains untouched.

### 2026-11-04 — SQLite schema v5 foundation (implementation pending CI)

- Working branch only: `phase-2/market-data-foundation`; `main` remains untouched.
- Added schema v5 migration to separate dated-futures identity from the legacy `contract_multiplier` field. Futures identity now uses venue/product, expiry, and settlement currency; perpetuals/options retain their prior multiplier requirements.
- The v5 migration rebuilds the generated identity key and unique index transactionally. Duplicate identities exposed by the revised rule abort and roll back the migration; no UUIDs or histories are merged.
- Added an append-only `provider_definition_events` journal with explicit source ordering, exact payload hash, durable pending/applied/quarantined states, and foreign-key linkage for applied canonical IDs.
- Added `SQLiteProviderDefinitionJournal` for idempotent append, conflict detection, deterministic pending replay, and one-way processing-state transitions. Raw Databento fixed-point values are preserved as received.
- Added regression coverage for futures identity separation and journal durability, idempotency, conflict rejection, equal-timestamp source ordering, quarantine, and immutable payloads.
- This is persistence groundwork only. The journal is not yet connected to the live Databento session or the atomic provider mapping + metadata revision pipeline. No live market data, Footprint readiness, or latency claim is implied.
- Overall progress remains 19.60% until the new migrations and tests pass CI and the provider-to-registry synchronizer is integrated and verified.

### 2026-11-04 — strict Databento definition normalizer

- Added `backend/app/databento_definition_normalizer.py` and focused tests for dated futures definitions, UTC expiry conversion, required authoritative fields, Delete handling, and lossless provider-term preservation.
- Root symbol and venue must come from explicit provider fields; no ticker parsing is used to fill missing identity data.
- Settlement currency uses the provider's explicit settlement override when present and otherwise the provider currency field. Fixed-point source values remain raw with explicit scales; provider-native contract multiplier remains separate from unit-of-measure quantity.
- This adapter is not yet wired to the live provider lifecycle or SQLite synchronizer. Footprint source modules are not present in the current GitHub branch, so no Footprint integration or completion is claimed.
- Overall progress remains 19.60%; CI for the latest branch head and the complete synchronizer are still pending.


### 2026-11-04 — Durable Databento definition synchronization
- Added `backend/app/databento_definition_sync.py` to connect the append-only SQLite provider-definition journal, strict Databento normalizer, canonical instrument registry, atomic mapping/metadata event repository, in-memory catalog, and point-in-time resolver.
- Wired the synchronizer into `ProviderManager.refresh_definitions` and application construction using the same SQLite database as the canonical registry.
- Add/Modify events resolve or allocate a persistent canonical UUID, validate immutable identity, then commit provider mapping and metadata revision together. Delete events close the active mapping and matching metadata interval atomically.
- Journal records are marked applied only after the registry event succeeds. Invalid, stale, unsupported, or ambiguous events are quarantined with the original payload retained. Exact event replay is idempotent.
- Added resolver restoration from persisted canonical instruments and provider mappings so provider identity mapping can survive backend restarts.
- Added integration tests for Add → Modify → Delete point-in-time behavior, exact replay, pending-event recovery, resolver restoration, invalid-event quarantine, and equal-timestamp transition rejection.
- GitHub Actions run [#41827550928](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41827550928) passed frontend unit tests, frontend production build, backend tests, and backend container image build for the replay-hardened code at commit `3e3fcd715d31c00cd2884a7f5ce5510d83daa6ff`. The earlier integration checkpoint also passed in run #41826984399.
- Core synchronizer implementation: `329be1f7df926fadea6a56d24ef2fba502229cdd`; pending-page replay hardening and its regression test: `3e3fcd715d31c00cd2884a7f5ce5510d83daa6ff`. The documentation follow-up is committed separately. `main` was not modified.
- Limitations: provider source order is derived from stable record iteration within equal timestamps because the current adapter does not expose a universal sequence field. Multiple lifecycle transitions for the same provider instrument at the exact same event timestamp cannot form positive-length half-open intervals; later conflicting transitions are quarantined rather than reordered or silently collapsed. No live Databento delivery, scheduled refresh, coverage persistence, or deployment validation is claimed.


### 2026-11-04 — Durable OHLCV persistence and restart restoration

- Added `backend/app/ohlcv_store.py`, a SQLite OHLCV repository sharing the configured instrument-registry database without changing its schema `user_version`.
- Base provider bars are persisted before in-memory pipeline acceptance. Derived timeframe bars pass a persistence gate before the aggregator mutates the in-memory pipeline or broadcasts the update.
- The store preserves exact decimal strings, integer nanosecond event/receive/provider-out timestamps, sequence origin, bar origin, and completeness.
- Persistent identity matches the pipeline's bar identity: provider, dataset, publisher, instrument, series type, timeframe, and bucket start. A conflicting raw symbol for the same identity is rejected.
- Duplicate, stale, provider-precedence, and derived-completeness revision behavior mirrors the in-memory pipeline. Late bars older than a full retained series window are rejected as expired.
- Retention is bounded per exact provider series and timeframe. The local ingest-sequence high-water mark is stored separately so process restarts do not reset sequence ordering after older bars have been pruned.
- Application construction restores retained OHLCV bars into the in-memory pipeline before provider ingestion starts. HTTP snapshots therefore read restored bars immediately after restart.
- Added tests for exact decimal/nanosecond round-trip, revision semantics, retention, late-event expiry, shared-database schema compatibility, sequence high-water recovery, and API-level restart restoration.
- Validation: GitHub Actions run [#41829548364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/41829548364) passed the frontend unit suite (117 tests), frontend production build, backend suite (322 tests), and backend container image build at code commit `9e1f47b4a2a66b478465b1fc9df362462d1e9864`. Documentation follow-up changes are checked by their own branch-head workflow.
- Scope boundary: this does not yet persist coverage intervals, maintain a durable event log for WebSocket client replay, orchestrate historical gap detection/backfill, validate live Databento delivery, or prove production performance under sustained market load. Those remain explicit follow-up work. `main` remains untouched.
