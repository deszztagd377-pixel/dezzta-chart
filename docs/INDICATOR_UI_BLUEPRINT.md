# DEZZTA CHART — Indicator UI implementation blueprint

Status: **DRAFT — owner review required before implementation**  
Scope: standard educational chart indicators only. This blueprint does not authorize trading, order execution, signal recommendations, or any broker integration.

## 1. Existing verified foundation

- `src/indicators/indicatorCalculations.ts` already calculates SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, and Bollinger Bands 20,2.
- `src/indicators/useMarketIndicators.ts` reads the shared market-data snapshot and returns no indicator values unless the source is a non-empty validated backend series in `ready` or `degraded` state.
- `src/services/marketDataStore.ts` owns immutable, identity-bound OHLCV bars and increments a revision for each accepted snapshot/update.
- `src/components/CandlestickChart.tsx` currently creates only the candlestick series. It does not import or render `useMarketIndicators`.
- `lightweight-charts` is declared as `^5.0.0`; exact installed type/API signatures must be inspected from the lockfile and dependency package before any chart-series or pane implementation. Do not guess API signatures.

## 2. Proposed user-facing scope

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
- Proposed initial state: every indicator OFF, preserving the current candlestick-only experience. Owner confirmation is required.

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

## 5. Required acceptance tests before completion

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

## 7. Approval gate

This document is a proposed implementation plan only. No chart UI, pane, overlay, hook, or calculation source is changed by adding this blueprint. Implementation begins only after the owner reviews and approves this scope and the initial all-OFF behavior.
