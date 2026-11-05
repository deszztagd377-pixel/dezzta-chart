# DEZZTA CHART — Branch-Head Evidence Audit

Audit date: 2026-11-05  
Audited branch: `phase-2/market-data-foundation`  
Scope: read-only source, test-inventory, and CI evidence review  
Accounting status: **evidence worksheet only; no milestone weights or progress percentage approved or recalculated**

## Exact CI evidence

- Commit: `50eb7ea59f44cf692d9cf56cc8adf3d7809ec37e`
- Workflow run: [#42056623146](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42056623146)
- Result: **success**
- Completed steps: frontend dependency installation, frontend unit tests, frontend production build, backend dependency installation, backend pytest, and backend container-image build.
- The workflow is one combined job named `Test and Build`; a successful run confirms those configured CI steps on this commit, not deployed service behavior or production readiness.

## Test inventory

Repository tree inspection found:
- **20 frontend test files** under `src/`.
- **27 backend test modules** under `backend/tests/`.

Frontend coverage includes:
- Navigation and timeframe selector rendering.
- Demo candle validation and offline instrument-catalog fixture boundaries.
- Educational simulated-footprint accumulator and deterministic fixture behavior.
- SMA, EMA, RSI, MACD, and Bollinger calculation functions.
- Instrument catalog client, shared market-data store, OHLCV adapter/client, stream protocol, WebSocket client, and stream supervisor.
- Market-data types, candle conversion, chart options, chart viewport sizing, preferences, and timeframe aggregation.

Backend test modules cover API, aggregation, identity and entitlements, instrument registry/metadata/relationships, OHLCV persistence and stream handling, coverage, ingest, provider adapters/definitions, and pipeline components.

## Verified implementation observations

### Application shell and chart
- `src/App.tsx` owns Chart/Watchlist/Settings navigation, selected timeframe, selected catalog contract, and grid preference.
- `src/components/CandlestickChart.tsx` creates and disposes the Lightweight Charts instance, responds to resize, applies chart display options, and consumes the shared market-data store.
- `src/components/BottomNav.tsx` exposes three navigation destinations.
- `src/components/TimeframeSelector.tsx` renders 18 intervals but enables only `1d`, matching the current date-only demo fixture. The other 17 remain disabled with an explanatory status note.

### Data integrity and honest source labelling
- `src/data/demoCandles.ts` validates the demo fixture's daily dates, chronological order, finite OHLC values, and high/low boundaries.
- `src/services/marketDataStore.ts` validates exact series identity, chronology, OHLCV boundaries, and keeps demo/unavailable bars out of backend indicator input.
- `src/components/InstrumentCatalogPanel.tsx` does not invent contract expiries and clearly labels metadata/canonical mapping status.
- These source-level controls do not establish that a deployed external data provider is delivering data.

### Educational calculations
- `src/indicators/indicatorCalculations.ts` provides pure SMA, EMA, RSI, MACD, and Bollinger calculations with unit tests.
- `src/indicators/useMarketIndicators.ts` is not wired into the visible chart UI in `src/App.tsx` or `src/components/CandlestickChart.tsx`; calculation helpers must not be counted as a finished user-visible indicator panel.
- `src/education/simulatedFootprint.ts` and its tests are explicitly simulation-labelled educational fixtures. They are not a live order-flow feature and must remain clearly labelled as simulated if ever surfaced in the UI.

### Settings and authentication
- `src/utils/preferences.ts` safely reads/writes the grid visibility preference, including storage-access failure handling.
- `src/auth/AuthProvider.tsx` contains Firebase email/Google sign-in and ID-token retrieval code.
- Source presence does not replace deployed Firebase configuration checks, security review, or end-to-end account testing.

## Gaps and verification boundaries

1. **Visible indicator integration:** no verified indicator panel is connected to the chart UI.
2. **Drawing and measurement:** no implemented and tested drawing/measurement workflow was found in the audited app shell.
3. **Timeframe data:** non-daily buttons are intentionally disabled because matching verified sample series are absent.
4. **Interactive component testing:** current component tests use `renderToStaticMarkup`; they verify rendered markup, not real pointer/touch interactions or state transitions in a browser DOM.
5. **Dependency reproducibility:** root `package-lock.json` is absent and CI uses `npm install`; deterministic clean-install behavior remains an open task.
6. **Security assurance:** no completed independent security review, deployed Firebase verification, or full secret/configuration audit is established by this source inspection.
7. **Device and release validation:** no physical Android acceptance report, packaged Android artifact, or release validation evidence was found in this audit.
8. **Operational claims:** CI does not establish zero latency, zero delay, external provider availability, exchange-clock synchronization, or production performance.

## Non-scoring classification worksheet

| Area | Evidence classification | Remaining proof |
|---|---|---|
| M1 — App shell/chart | Implemented foundation; broader workflow incomplete | Full user acceptance and chart workflow |
| M2 — Data contracts/persistence | Significant tested foundation | Deployed end-to-end behavior is not established |
| M3 — Authentication/security | Auth code and backend tests exist | Deployment configuration and security review |
| M4 — Interaction/tools | Basic chart controls and timeframe logic exist | Real browser interaction tests; drawing/measurement |
| M5 — Educational visualization | Pure calculations and simulated fixture tests exist | Visible, explained, non-predictive educational UI |
| M6 — Responsive/accessibility | Responsive foundations exist | Device/orientation and accessibility acceptance |
| M7 — Preferences/watchlist | Grid preference and catalog selection exist | Broader persistent settings/watchlist behavior |
| M8 — Quality/release | CI passed on the exact commit above | Lockfile, scanning, device packaging, release validation |

This worksheet intentionally assigns **no completion fractions and no earned points**. It is evidence preparation only. The proposed M1–M8 weights remain subject to owner approval before any new overall percentage is published.

## Next safe engineering priorities

1. Add a deterministic root dependency lockfile and migrate CI to a clean reproducible install, after verifying the repository's package-manager conventions.
2. Improve browser-level interaction coverage for navigation, settings persistence, chart resize, and timeframe disabled-state behavior.
3. Add an explicit, accessible educational-demo presentation for simulated fixtures only, with no predictive or buy/sell interpretation.
4. Continue security/configuration documentation and non-secret validation; never commit credentials or request secrets in chat.
5. Keep major visual redesign behind the owner's 40% planning gate and obtain review before large changes.
