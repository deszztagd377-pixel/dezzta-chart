# DEZZTA CHART — Work Cycle 62J-59: Indicator prefix-causality and boundary regression

**Date:** 21 November 2026
**Branch:** phase-2/market-data-foundation
**Parent source/test HEAD:** 96fe84ec537d68f5588b880a2fddafd1772a39e4
**Scope:** calculation correctness tests and indicator progress evidence only
**Cost:** zero; no deployment or external service

## 1. Exact-head baseline

The parent source/test HEAD passed Automated Tests [44852405512](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44852405512), CodeQL [44852405426](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44852405426), and Full Git History Secret Audit [44852405453](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44852405453). All three were SUCCESS.

## 2. Defect class addressed

Historical chart analysis and future Candle Replay require strict causality: an indicator value at candle index t must depend only on candles at indices 0 through t. Future candles must not change already-computed historical values.

The current calculation helpers are sequential/windowed, but this invariant was not previously tested as a cross-indicator regression property. This batch adds that missing guard.

## 3. Test changes

File changed: src/indicators/indicatorCalculations.test.ts.

- Added a deterministic 64-candle non-linear price fixture.
- Compared each prefix calculation with the same prefix of the full calculation at lengths 1, 14, 15, 19, 20, 26, 34, 35, 48 and 64.
- Applied the comparison independently to SMA20, EMA20, RSI14, MACD12/26/9 and Bollinger20,2.
- Added falling-only RSI boundary coverage: first valid output at index 2 for period 2, with values 0.
- Added period-one SMA, EMA and RSI boundary coverage.

The prefix comparison uses exact equality because each prefix and full calculation execute the same deterministic operations over the same historical inputs.

## 4. Calculation contracts preserved

| Indicator | Contract | First valid index |
|---|---|---:|
| SMA20 | Rolling arithmetic mean of 20 closes | 19 |
| EMA20 | SMA-seeded, alpha 2/21 | 19 |
| RSI14 | Wilder-smoothed gains/losses over 14 changes | 14 |
| MACD12/26/9 | EMA12 minus EMA26; EMA9 signal | MACD 25; signal/histogram 33 |
| Bollinger20,2 | 20-close mean plus/minus 2 population standard deviations | 19 |

Warm-up remains null and every output remains aligned to its source candle.

## 5. Explicit non-changes

- No production calculation formula or source changed.
- No chart overlays, oscillator panes, toggles, legends or rendering code changed.
- No Footprint or Heatmap implementation started; their owner reference images and approved blueprints remain prerequisites.
- No new market-data provider, paid service, database, deployment, Termux operation or production credential use.
- No main branch modification.
- No indicator percentage or Stage 1 acceptance tick is awarded by test-only work.

## 6. Current progress

- SMA20 🟨 Foundation
- EMA20 🟨 Foundation
- RSI14 🟨 Foundation
- MACD12/26/9 🟨 Foundation
- Bollinger20,2 🟨 Foundation
- Shared indicator hook 🟨 Foundation
- Footprint 🟧 Gated on owner reference/blueprint
- Heatmap 🟥 Not implemented
- Liquidation Maps 🟥 Not implemented

Stage 1 remains 30/40 = 75% provisional. Gate 10 remains 0/10 formally closed. Overall project progress remains unscored pending approved M1–M8 weights and denominator.

## 7. Verification boundary

The exact-head test-only commit is verified by Automated Tests [44853126329](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126329), CodeQL [44853126331](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126331), and Full Git History Secret Audit [44853126419](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126419). Frontend: 247/247 tests across 29 files. Backend: 1,218 passed in 49.51 seconds. Android debug APK build [44853126386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126386) also succeeded; this is CI evidence, not physical-device acceptance.