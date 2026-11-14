# DEZZTA CHART — Indicator UI implementation blueprint

Status: **PARKED — Stage 4 preparation draft; not active during Stage 1**  
Implementation authorization: **NOT GRANTED**. Revisit this document only when the official roadmap reaches Stage 4 and the applicable owner review/acceptance gates are satisfied.  
Scope: standard educational chart indicators only. This blueprint does not authorize trading, order execution, signal recommendations, or any broker integration.

## Roadmap placement

- The official project roadmap has six stages. The current active stage remains **Stage 1 — Foundation, Security & Data Integrity**.
- Visible indicator controls, chart overlays and oscillator panes belong to **Stage 4 — Indicators & Analytics**, not Stage 1.
- The branch name `phase-2/market-data-foundation` is not evidence that the official project has advanced to Stage 2.
- The separate 40% overall-project gate applies to broader professional UI/feature expansion. It does not authorize skipping stages or implementing indicator UI during Stage 1.
- This file is retained only as a future preparation draft. No implementation work should be started from it during Stage 1.

## 1. Existing verified foundation

- `src/indicators/indicatorCalculations.ts` already calculates SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, and Bollinger Bands 20,2.
- `src/indicators/useMarketIndicators.ts` reads the shared market-data snapshot and returns no indicator values unless the source is a non-empty validated backend series in `ready` or `degraded` state.
- `src/services/marketDataStore.ts` owns immutable, identity-bound OHLCV bars and increments a revision for each accepted snapshot/update.
- `src/components/CandlestickChart.tsx` currently creates only the candlestick series. It does not import or render `useMarketIndicators`.
- `lightweight-charts` is declared as `^5.0.0`; exact installed type/API signatures must be inspected from the lockfile and dependency package before any chart-series or pane implementation. Do not guess API signatures.

## 2. Proposed Stage 4 user-facing scope

### Main price pane — default OFF

- SMA 20: one overlay line.
- EMA 20: one overlay line.
- Bollinger Bands 20,2: upper, middle, and lower overlay lines.
- Each indicator has an explicit, accessible toggle.
- Legend/current-value display identifies the indicator and its latest available value; during warm-up it displays a neutral “waiting for enough bars” state.

### Separate oscillator panes — default OFF

- RSI 14 Wilder: its own pane, 0–100 scale, with 30 and 70 guide levels.
- MACD 12/26/9: its own pane, MACD and signal lines, histogram, and zero guide.
- Pane creation/removal must use the exact Lightweight Charts v5 API verified from the installed package. Preserve the chart's normal layout when both oscillators are OFF.

### Controls and mobile layout

- A compact indicator control row is placed within the chart view without covering the latest candles or the market-data status badge.
- Controls remain usable on a narrow mobile viewport; horizontal scrolling is preferable to shrinking labels into unreadable text.
- All toggles are keyboard-operable and expose `aria-pressed`/accessible names.
- Proposed initial state: every indicator OFF, preserving the current candlestick-only experience. Owner confirmation is required at the Stage 4 review gate.

## 3. Data and lifecycle contract

1. Every calculation consumes only the exact immutable bars from the currently active shared market-data snapshot.
2. Never calculate or draw indicator values from DEMO candles, cached prior instruments, loading states, unavailable states, or errors.
3. The indicator hook should expose the same snapshot's bars and last-change metadata alongside identity, status, source, revision, and calculated arrays; do not create a second data fetch.
4. Convert each indicator point using the timestamp of its corresponding source bar. Source timestamps are Unix epoch seconds.
5. On instrument/timeframe identity change, loading, unavailable, error, or empty backend data: clear all indicator series immediately so no stale values remain.
6. Preserve a user's toggle selection across a data refresh only if the active identity remains valid; do not preserve plotted values across identity changes.
7. For normal newest-bar updates, use an incremental series update only when the snapshot revision and timestamp prove continuity. For snapshots, missed revisions, and historical corrections, replace the full ordered series.
8. Keep warm-up `null` values out of plotted points without shifting timestamps or misaligning bars.

## 4. Performance and correctness safeguards

- Do not recreate the chart instance on each market-data revision.
- Create chart series once per chart lifecycle; update data/visibility through the supported API.
- Measure recalculation and render cost with the supported maximum history size before optimizing.
- If full-array recalculation causes measurable mobile jank, design a separately reviewed incremental calculation path with parity tests against the current full calculation engine.
- Do not add a fallback to demo or synthetic values when backend data is missing.
- No indicator may create entry/exit signals, recommendations, automated actions, or broker requests.

## 5. Required acceptance tests before Stage 4 completion

- Each toggle changes only its own series visibility.
- All controls default OFF and the existing candlestick-only layout is unchanged.
- SMA/EMA/Bollinger values align to exact source timestamps and warm-up boundaries.
- RSI output begins at source index 14; scale and 30/70 guides are correct.
- MACD line begins at index 25; signal and histogram begin at index 33.
- DEMO/loading/unavailable/error states display no indicator values.
- Switching instrument or timeframe clears prior indicator series before new validated bars arrive.
- Snapshot replacement, incremental newest-bar update, and historical correction all keep indicator data aligned.
- Enabling/disabling panes does not corrupt candlestick spacing, viewport, crosshair, resize behavior, or chart cleanup.
- Mobile viewport and keyboard/accessibility tests pass.
- Existing calculation tests remain green and new chart integration tests pass.

## 6. Explicitly out of scope

- Footprint, Heatmap, and Liquidation Maps. Each remains separately gated on the owner's reference image(s), a dedicated scoped blueprint, and owner review.
- Provider order-flow data, exchange subscriptions, trade execution, broker connections, auto-trading, copy-trading, or paid services.
- Changing existing indicator formulas or defaults without a separate review.

## 7. Stage 4 approval gate

This is a future proposal only. No chart UI, pane, overlay, hook, or calculation source is changed by retaining this document. Implementation must not begin during Stage 1. At the Stage 4 entry/review gate, the owner must review and approve the scope, initial all-OFF behavior, exact data lifecycle contract and acceptance tests before implementation.
