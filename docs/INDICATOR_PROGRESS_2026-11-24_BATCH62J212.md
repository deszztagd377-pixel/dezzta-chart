# DEZZTA CHART — Indicator Progress Ledger (24 November 2026)

**Batch:** 62J-212  
**Branch:** `phase-2/market-data-foundation`  
**Source audit HEAD:** `4832f628e5fe616dfe2902be83a8529e540c8ea2`  
**Indicator source delta in this batch:** none  
**Cost:** ZERO COST

## 1. Status legend and accounting

- 🟩 Accepted: source, tests, and required integration/acceptance evidence verified.
- 🟦 Implemented foundation: reusable calculation/data foundation exists, but user-visible acceptance is incomplete.
- 🟨 Partial: implementation exists but important functional acceptance remains.
- 🟧 Gated/prototype: partial or synthetic implementation only; required data contract, references, or approval remains.
- 🟥 Not implemented / blocking prerequisite.
- ⬜ Not scored / inventory not approved.

**Aggregate indicator progress: NOT SCORED.** No owner-approved denominator, weighting, or per-study completion rubric exists. The 24 indicator-specific tests are not 24 completed indicators and are not a completion percentage.

## 2. Verified indicator implementation matrix

| Study / subsystem | Verified foundation | Test evidence | Visible chart state | Current status |
|---|---|---|---|---|
| SMA 20 | 20-close arithmetic mean; overflow-resistant mean; first valid source index 19 | Calculation suite | No overlay, toggle, legend, or lifecycle integration in CandlestickChart | 🟦 Foundation |
| EMA 20 | SMA-seeded EMA; multiplier 2/21; first valid index 19 | Calculation suite | No overlay, toggle, legend, or lifecycle integration | 🟦 Foundation |
| RSI 14 Wilder | First 14 close-to-close changes seed average gain/loss; Wilder recurrence; first valid index 14 | Calculation suite | No 0–100 pane, 30/70 guides, toggle, or legend | 🟦 Foundation |
| MACD 12/26/9 | EMA12 minus EMA26; EMA9 signal; histogram; MACD index 25, signal/histogram index 33 | Calculation suite | No oscillator pane, lines, histogram, zero guide, or toggle | 🟦 Foundation |
| Bollinger 20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Calculation suite | No bands, fill, toggle, or latest values | 🟦 Foundation |
| Shared Indicator Hook | Exact canonical backend snapshot; aligned studies; WeakMap cache shared by immutable snapshot; non-backend/error states suppressed | 7 hook tests | Hook is not imported/called by CandlestickChart | 🟦 Foundation |
| Volume Profile (Mid Tier) | No production implementation/test module verified in current source tree | No dedicated acceptance suite verified | No profile renderer, price bins, POC/VAH/VAL, range controls, or visible UI | 🟥 Open |
| Complete Volume Profile (Exclusive Pro) | No complete implementation verified | No dedicated acceptance suite verified | Detailed value/profile renderer not implemented | 🟥 Open |
| Compact movable-range Volume Profile Tool | Product requirement only; distinct from the full indicator | No implementation suite verified | No chart-side movable/resizable range tool | 🟥 Open |
| Footprint PRO 2GD | Educational synthetic/offline aggregation only; not exchange-native bid/ask truth | Separate simulated-footprint tests do not prove production order-flow correctness | Production cluster renderer not accepted | 🟧 Prototype / gated |
| Heatmap | No accepted order-book depth/liquidity engine verified | No dedicated production acceptance suite | No renderer; depth feed contract and owner reference remain prerequisites | 🟥 Open |
| Liquidation Maps | No defensible calculation/provenance/runtime implementation verified | No dedicated production acceptance suite | No map renderer; methodology and data provenance remain prerequisites | 🟥 Open |

## 3. Calculation and shared-hook test inventory

The two focused suites contain **24 named tests total**.

### Calculation engine — 17 tests

1. SMA/EMA candle-index alignment and warm-up nulls.
2. Wilder RSI flat and rising edge cases.
3. MACD signal warm-up separation.
4. Bollinger population standard deviation.
5. Shared multi-indicator calculation entry point.
6. All five calculations across supported chart timeframes.
7. Invalid periods and non-finite input rejection.
8. Prefix causality: future candles cannot change earlier outputs.
9. Falling-only RSI and period-one moving averages.
10. Fail-closed handling of non-finite results from extreme finite values.
11. RSI stability with very large finite gain/loss magnitudes.
12. Overflow-resistant representable SMA means.
13. Finite Bollinger deviation for large same-sign prices.
14. Preservation of small residuals in large cancelling SMA inputs.
15. Preservation of small residuals in the Bollinger middle band.
16. Wilder RSI seed and recurrence on alternating gains/losses.
17. Rejection of non-finite close values at the shared calculation boundary.

### Shared hook — 7 tests

1. No output without a selected backend series.
2. Calculation from the exact selected keyed snapshot.
3. Recalculation on a new immutable snapshot revision.
4. Isolation of simultaneous panels by canonical series.
5. One frozen result shared across panels using the same snapshot revision.
6. Degraded backend data retained; demo/error snapshots suppressed.
7. Output cleared when the selected series becomes unavailable.

## 4. Cross-timeframe and numerical acceptance requirements

The five calculations have tests over the currently supported chart timeframes. This does not automatically prove all future timeframes or every second-based interval.

Each study must retain:
- Exact source candle index/timestamp alignment.
- Null warm-up values; no forward-fill of uninitialized output.
- Prefix causality; adding future candles must not alter earlier values.
- Rejection of non-finite and invalid inputs.
- Identity/timeframe change clearing so stale values cannot remain on a newly selected series.
- Deterministic behavior for repeated calculations.
- Bounded CPU/memory cost and regression/performance tests before broad chart rollout.

First-valid source indexes:
- SMA20: 19.
- EMA20: 19.
- RSI14 Wilder: 14.
- MACD12/26/9: MACD line 25; signal and histogram 33.
- Bollinger20,2: 19.

## 5. Chart integration acceptance — still outstanding

The current `CandlestickChart.tsx` imports `useMarketDataSeriesSnapshot`, not `useMarketIndicators`, and constructs a single `CandlestickSeries`. Therefore none of SMA/EMA/RSI/MACD/Bollinger is currently a visible, user-toggleable chart feature.

Required integration work:
1. Add overlay rendering for SMA/EMA and Bollinger bands.
2. Add separate oscillator panes for RSI and MACD with correct scales/guides.
3. Add user-visible toggles, legends, latest values, and clear disabled/loading/error states.
4. Bind all studies to the exact canonical series and clear output synchronously on identity/timeframe changes.
5. Verify multiple chart panels, chart resize, panel lifecycle, empty/warm-up data, and mobile density.
6. Add visual regression, accessibility, performance, and supported-timeframe tests.
7. Preserve existing candlestick behavior and avoid adding dependencies without a demonstrated need.

No UI integration credit is assigned before these checks pass.

## 6. Owner-defined tier inventory

### Low Tier — 15 popular/standard indicators

The category size is 15. The exact final owner-approved list is not yet present in the current acceptance record. RSI, MACD, and Bollinger Bands are exact names recovered from earlier owner approval; SMA and EMA have calculation foundations but are not silently substituted into the approved list. The remaining selections must be confirmed before the category is treated as finalized.

### Mid Tier

Volume Profile is part of the planned Mid Tier, together with approximately ten additional studies. The final additional inventory is not approved. Do not infer formulas or membership from candidate discussions.

### Exclusive Indicator Pro

- Footprint PRO 2GD.
- Heatmap.
- Liquidation Maps.
- Complete Volume Profile.

Only the project owner may add members to this tier.

### Separate Tools entry point

A compact Volume Profile tool is planned separately from the full Volume Profile indicator. It should display a compact chart-side profile and recalculate when the user moves/resizes its selected range. It must not be counted as implementation of Complete Volume Profile.

## 7. Footprint visual reference and behavior contract

The owner supplied two original references, persisted as:
- `Footprint Indicator Reference 1`
- `Footprint Indicator Reference 2`

They show a dark chart, red/green bid/ask-style cells, numeric volume labels, proportional horizontal bars, price-level alignment, highlighted rows, and deliberate candle-cluster spacing. The Saved Reference Images are not binary files committed to Git; they must be supplied as actual visual inputs when implementation begins. Do not replace them with generic imagery or ask for re-upload while the saved references remain accessible.

Behavior invariants:
- Footprint OFF preserves the standard candlestick layout and normal spacing.
- Only explicit Footprint ON activates the dedicated spaced-candle/cluster layout.
- Synthetic/demo aggregation remains labelled synthetic; it cannot be represented as exchange-native bid/ask or aggressor truth.
- Tick size, aggressor classification, exchange feed, row aggregation, highlighted-row semantics, and any POC/VAH/VAL meanings require a reviewed data contract.
- Visual implementation requires a scoped blueprint and owner review.

## 8. Heatmap and Liquidation Maps blockers

**Heatmap:** requires an owner reference image, validated depth/liquidity feed contract, price/time aggregation, update cadence, stale-depth behavior, snapshot/replay contract, and visual/performance tests. OHLCV bars alone are insufficient to claim order-book depth.

**Liquidation Maps:** requires defensible data provenance and methodology. Estimated liquidation levels must not be represented as observed exchange liquidation events unless the source actually provides those events. Requires a reviewed calculation contract, reference, renderer, and tests.

## 9. Stage, project, and cost indicators

| Area | Status | Accounting |
|---|---|---|
| Stage 1 | 🟨 Provisional | 30/40 criteria = 75%; not re-audited in this batch |
| Stage 2 | 🟧 Active | Market-data foundation; no aggregate percentage |
| Stage 3 | ⬜ Not scored | Official stage sequence preserved |
| Stage 4 | ⬜ Parked | Major indicator UI/visual implementation remains gated |
| Aggregate indicators | ⬜ NOT SCORED | No approved denominator/weights |
| Overall project | ⬜ NOT SCORED | No approved project-wide denominator |
| Cost | 🟩 ZERO COST | No paid data, hosting, subscriptions, or deployment |

**No overall completion percentage is inferred from individual test counts or the number of source files.** Target delivery planning remains around 24 December 2026, not the end of December.

## 10. Next ordered work

1. Finish and accept Stage 2 market-data/WebSocket foundations and their external production evidence.
2. Complete the owner-reviewed Gate 25 authentication/trust boundary without destructive Redis retention shortcuts.
3. Finalize the exact Low Tier list and Mid Tier inventory.
4. At the official Stage 4 gate, approve the indicator UI blueprint and integrate the five calculation foundations into the chart.
5. Implement standard and Complete Volume Profile as distinct features, plus the separate compact Tools profile.
6. Prepare scoped Footprint/Heatmap/Liquidation blueprints with owner references and validated data contracts before visual implementation.

No paid service, deployment, or `main` branch change is authorized by this ledger.
