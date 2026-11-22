# DEZZTA CHART — Indicator Progress Audit and Acceptance Register

**Audit date:** 22 November 2026  
**Audited source/test baseline:** `0074f1d0b0e421f32800294742f92d9bc9c8a2c6`  
**Branch:** `phase-2/market-data-foundation`

> **Current conclusion:** SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and the shared indicator hook have tested calculation/data foundations, but none is a completed user-facing chart feature. Footprint is an offline educational simulation only. Heatmap and Liquidation Maps are not implemented. Aggregate indicator percentage is unscored because approved weights and a completion denominator do not exist.

## 1. Status vocabulary

| Status | Meaning |
|---|---|
| 🟩 Accepted | Formula/data contract, user-facing behavior, lifecycle, tests and applicable acceptance evidence all meet the agreed scope |
| 🟨 Foundation | Calculation or shared-data foundation exists and has tests; user-facing integration or acceptance remains |
| 🟧 Gated / partial | Limited prototype or simulation exists, or implementation is blocked by explicit owner/reference/roadmap prerequisites |
| 🟥 Not implemented | No implementation is verified in the audited source tree |
| ⬜ Not assessed | Evidence is insufficient to assign a completion state |

No study in this audit is 🟩 Accepted as a finished chart feature. A passing unit test proves only the tested calculation or contract; it does not prove rendered UI, live data, mobile behavior or production acceptance.

## 2. Canonical indicator matrix

| Study / subsystem | Status | Existing implementation | First valid output / source | Remaining work |
|---|---|---|---|---|
| SMA 20 | 🟨 Foundation | Rolling arithmetic mean of 20 closes | Candle index 19 | Overlay, independent toggle, legend/latest value, identity transitions, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | EMA seeded by first 20-close SMA; alpha = 2/21 | Candle index 19 | Overlay, independent toggle, legend/latest value, identity transitions, render/lifecycle tests |
| RSI 14 Wilder | 🟨 Foundation | Close-to-close gains/losses; initial 14-change averages then Wilder smoothing | Candle index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, identity transitions, render/lifecycle tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal over valid MACD values; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, two lines, histogram, zero guide, toggle, legend/latest values, identity transitions, render tests |
| Bollinger 20,2 | 🟨 Foundation | 20-close mean ± 2 × population standard deviation | Candle index 19 | Upper/middle/lower overlay, toggle, displayed values, identity transitions, render tests |
| Shared market-indicator hook | 🟨 Foundation | Reads shared validated snapshot and calculates five studies | Only non-empty backend bars in ready/degraded state | Dedicated hook tests, chart binding, loading/error lifecycle, stale clearing, per-series isolation, renderer integration |
| Footprint | 🟧 Simulation only / gated | Offline bounded accumulator for synthetic events; provenance SIMULATED | Synthetic event-time bucket and integer price tick; not exchange data | Owner reference, reviewed blueprint, validated source contract if live data proposed, explicit toggle, ON-only spaced clusters, OFF-layout regression, interaction/performance/lifecycle tests |
| Heatmap | 🟥 Not implemented | No implementation found in audited source tree | No validated source or calculation | Owner reference, zero-cost source feasibility, validated data contract, reviewed blueprint, renderer, legend/scale, toggle and tests |
| Liquidation Maps | 🟥 Not implemented | No implementation found in audited source tree | No validated source or calculation | Zero-cost source feasibility, validated calculation/data contract, owner reference/blueprint, renderer, scale/legend, toggle and tests |

## 3. Formula and numerical contracts

All five calculations consume the `close` values of the exact selected OHLCV series. Result arrays retain source length and index alignment. Warm-up entries are `null`, not zero, and are never shifted left.

### SMA 20

[
SMA_{20}(t)=\frac{1}{20}\sum_{i=0}^{19}C_{t-i}
]

First valid result: index 19. The implementation uses normalized/stable mean arithmetic to reduce intermediate overflow and cancellation loss.

### EMA 20

The first EMA value is seeded with the arithmetic mean of the first 20 closes. Thereafter:

[
EMA_t=\alpha C_t+(1-\alpha)EMA_{t-1},\qquad \alpha=\frac{2}{21}
]

First valid result: index 19. Do not silently change this seed convention.

### RSI 14 — Wilder

Let (Delta_t=C_t-C_{t-1}), (G_t=\max(Delta_t,0)), and (L_t=\max(-Delta_t,0)). Initial average gain/loss uses the first 14 price changes. Subsequent values use Wilder smoothing:

[
AG_t=\frac{13AG_{t-1}+G_t}{14},\qquad
AL_t=\frac{13AL_{t-1}+L_t}{14}
]

[
RSI_t=100-\frac{100}{1+AG_t/AL_t}
]

First valid result: index 14 because 14 close-to-close changes require 15 closes. Explicit edge semantics: no loss with positive gain gives 100; no gain with positive loss gives 0; both zero (flat series) gives 50. The ratio is normalized for large finite magnitudes.

### MACD 12/26/9

[
MACD_t=EMA_{12}(C)_t-EMA_{26}(C)_t
]

MACD first exists at index 25, when EMA26 is first valid. The signal is EMA(9) seeded over the first nine valid MACD values. Signal and histogram first exist at index 33:

[
Histogram_t=MACD_t-Signal_t
]

MACD, signal and histogram have separate nullable fields; a valid MACD value does not imply the signal/histogram are ready.

### Bollinger Bands 20,2

The middle band is the 20-close mean. Deviation uses **population** variance (division by 20), not sample variance:

[
Upper_t=Mean_{20,t}+2\sigma_{population,t},\qquad
Lower_t=Mean_{20,t}-2\sigma_{population,t}
]

All three bands first exist at index 19. The implementation normalizes values before variance calculation and rejects non-finite results.

### Shared numerical safety

- Periods must be positive safe integers; MACD fast period must be smaller than slow period.
- Non-finite inputs and non-finite intermediate/output values are rejected.
- Bollinger deviation multiplier must be finite and non-negative.
- Warm-up is explicitly nullable.
- Extreme finite values, cancellation and representable-mean boundaries have regression tests.
- Prefix-causality tests compare each study on historical prefixes with the same prefix of a full-series calculation. Future candles must not alter earlier outputs.

## 4. Data lineage and lifecycle

Required lineage:

`validated instrument catalog + selected timeframe`
→ `authenticated backend snapshot/stream`
→ `protocol and exact-series validation`
→ `marketDataStore`
→ `CandlestickChart` and `useMarketIndicators()`
→ `indicator calculations`.

The audited store identity includes provider, series type, dataset, publisher ID, instrument ID, raw symbol, timeframe, bucket policy and calendar identity/version. The store validates chronological OHLCV boundaries, freezes published snapshots/bars, and refuses non-empty bars in demo/loading/unavailable/error states. The hook exposes identity, status, source, revision and calculated arrays. It returns no indicator arrays unless source is backend, status is ready/degraded and bars are non-empty.

**Integration distinction:** the hook exists, but `CandlestickChart.tsx` at the audited baseline does not import or call `useMarketIndicators()`. The chart creates one candlestick series. No indicator overlay, oscillator pane, toggle or legend is wired into current chart UI. This is a data/calculation foundation, not completed chart integration.

Required lifecycle behavior:
1. Consume only the exact validated backend snapshot for the selected canonical instrument/timeframe; never calculate from DEMO candles.
2. Clear plotted values immediately on instrument, provider/venue, dataset, timeframe, bucket-policy/calendar identity changes and loading/unavailable/error/empty states.
3. Preserve source candle index/timestamp alignment when filtering nullable warm-up points.
4. Preserve toggle preference across refresh only for the same valid identity; never retain plotted values across identity changes.
5. Snapshot replacement and historical corrections require an ordered full-series update; incremental updates only when revision/timestamp continuity is proven.
6. No future-candle repaint: value at index (t) may depend only on bars through (t).
7. Gaps, invalid bars and unavailable values must never be silently replaced with zero.

## 5. Visual acceptance scope

### Price pane — proposed default OFF
- SMA20: one overlay line.
- EMA20: one overlay line.
- Bollinger20,2: upper, middle and lower overlay lines.
- Each has an independent accessible toggle and legend/latest-value display.
- During warm-up, show a neutral waiting state rather than a fabricated value.

### Oscillator panes — proposed default OFF
- RSI14: separate 0–100 pane with 30 and 70 guides.
- MACD12/26/9: separate pane with MACD and signal lines, histogram and zero guide.
- Verify pane/series APIs against the exact installed Lightweight Charts v5 dependency and lockfile; do not guess method signatures.

### Cross-cutting acceptance
- Each toggle controls only its own series.
- Initial OFF state preserves the current candlestick-only experience.
- Toggling does not corrupt candle spacing, scale, viewport, crosshair, resize or cleanup.
- Narrow mobile layouts remain usable; labels remain readable.
- Controls are keyboard operable and expose accessible names/state.
- Instrument/timeframe change clears stale series before new validated bars arrive.
- Snapshot replacement, newest-bar update, historical correction, reconnect and empty/error transitions are covered by integration tests.
- Performance is measured on maximum retained history and a representative mobile viewport.
- No trading signals, order execution, broker integration or buy/sell recommendations are in scope.

## 6. Footprint / Heatmap / Liquidation Maps constraints

### Footprint

`src/education/simulatedFootprint.ts` is an offline educational accumulator. It groups synthetic events by event-time interval and integer price tick, separates buy/sell/unknown quantities, calculates delta only as buy volume minus sell volume, rejects duplicate IDs and invalid quantities/timestamps, and fails closed at bounded event-ledger capacity. Snapshots carry `dataOrigin: 'SIMULATED'`.

It is **not** a provider adapter, exchange-native bid/ask feed, aggressor-side classifier or production order-flow engine. Never label synthetic cells as live market truth.

Mandatory layout:
- Footprint OFF: ordinary chart layout and candle spacing remain unchanged.
- Only explicit Footprint ON may switch to a dedicated spaced-candle/cluster layout.
- ON layout reserves enough horizontal space for readable bid/ask cells; OFF must not inherit cluster spacing.
- Obtain the owner's preferred Footprint reference image and approve a scoped blueprint before visual implementation.

### Heatmap

No implementation is verified. Before work: owner reference, zero-cost source feasibility, explicit data definition/provenance, calculation contract, scoped blueprint, then renderer/legend/scale/toggle and tests. Do not fabricate liquidity, order-book depth or heat values.

### Liquidation Maps

No implementation is verified. Before work: zero-cost source feasibility, explicit validated calculation/data contract and provenance, owner reference/blueprint, then renderer/scale/legend/toggle and tests. Do not fabricate liquidation prices, leverage clusters or exchange liquidation events.

## 7. Roadmap and authorization gates

- Official roadmap has six stages. Project remains **Stage 1 — Foundation, Security & Data Integrity**; branch name does not change official stage.
- Visible indicator controls, overlays and oscillator panes belong to **Stage 4 — Indicators & Analytics**. Do not implement them during Stage 1.
- The separate 40% overall-project milestone permits scoped blueprint preparation/review; it does not authorize skipping stages or starting Stage 4 early.
- Footprint and Heatmap visuals remain reference-gated. Liquidation Maps require validated source/formula and reviewed reference/blueprint.
- Stage 1 is 30/40 = 75% provisional. This is not indicator progress and does not authorize Stage 4.
- No aggregate indicator percentage until owner-approved per-study weights and completion denominator exist. Counting formulas, tests, UI checkboxes or commits as equal units misrepresents completion.

## 8. Verified source and test evidence

Audited files:
- `src/indicators/indicatorCalculations.ts`
- `src/indicators/indicatorCalculations.test.ts`
- `src/indicators/useMarketIndicators.ts`
- `src/services/marketDataStore.ts`
- `src/services/useMarketDataSnapshot.ts`
- `src/components/CandlestickChart.tsx`
- `src/components/CandlestickChart.lifecycle.test.tsx`
- `src/education/simulatedFootprint.ts`
- `docs/INDICATOR_DATA_ARCHITECTURE.md`
- `docs/INDICATOR_UI_BLUEPRINT.md`

Evidence at baseline:
- Calculation test file contains **15 test cases**: alignment/warm-up, RSI edge cases, MACD warm-up, population deviation, common entry point, timeframe fixtures, invalid inputs, prefix causality, period-one/falling RSI, extreme numeric values, stable RSI ratios, overflow-safe SMA means, Bollinger extremes and cancellation residuals.
- Frontend CI: **255/255 tests across 29 files**. These are not 255 indicator tests.
- Backend CI: **1,294 passed, 1 skipped**. Backend tests do not close chart indicator acceptance.
- Automated Tests [44980548455](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548455): SUCCESS.
- CodeQL [44980548587](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548587): SUCCESS.
- Full Git History Secret Audit [44980548469](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548469): SUCCESS.
- Container build, Redis TLS/AOF and persistent-volume smoke, container scan/report export and dependency audits passed. These are infrastructure checks, not indicator visual acceptance.
- No dedicated `useMarketIndicators` test file was found.
- Chart lifecycle tests cover browser online/offline/visibility/cleanup, not indicator rendering/toggles.
- Timeframe fixture loops do not prove live/provider-backed availability for every interval.

## 9. Next work, in correct order

1. Keep this audit and ledger synchronized whenever indicator source, data contract, renderer, tests or roadmap gates change.
2. While Stage 1 remains active, do not start Stage 4 visual implementation. At a permitted design-review gate, obtain owner approval before implementation.
3. Once Stage 4 is authorized, add dedicated hook/identity/status transition tests; then implement SMA/EMA/Bollinger overlays and RSI/MACD panes in separately reviewable slices.
4. Verify exact installed Lightweight Charts v5 APIs before writing chart-series/pane code.
5. Implement independent controls, accessible legends/current values, stale-series clearing and mobile layout; run exact-head CI and visual/browser acceptance.
6. Keep Footprint, Heatmap and Liquidation Maps as separate reference/data-contract projects; do not bundle them into the basic indicator rollout.

## 10. Explicit non-claims

This audit does not claim live exchange data, validated support for every timeframe, visible indicator UI, mobile-device visual acceptance, trading accuracy, production deployment, or completion of any indicator. This is documentation-only and awards **zero implementation progress credit**.

**Cost boundary:** Rp0. No paid provider, hosting, domain, deployment, credentials, device action or `main` modification.
