# DEZZTA CHART — Complete Indicator Progress Ledger

**Checkpoint:** 19 November 2026  
**Branch:** \`phase-2/market-data-foundation\`  
**Indicator implementation status:** unchanged by WebSocket Batch 62H-2.  
**Interpretation:** statuses describe verified implementation boundaries, not a guessed completion percentage. No indicator weights or acceptance percentages have been approved, so per-indicator or total-indicator percentages are intentionally not fabricated.

## Color legend

- 🟩 **Verified** — implementation and required tests verified for the stated scope.
- 🟨 **Foundation** — calculation/data foundation exists; visible chart integration or lifecycle acceptance remains.
- 🟧 **Gated** — work is intentionally blocked on required reference/blueprint/owner input.
- 🟥 **Not implemented** — no implementation verified.
- ⬜ **Not assessed** — evidence is insufficient to assign a status.

## Indicator dashboard

| Indicator / subsystem | Current state | Calculation / data contract | First valid output | Remaining acceptance work |
|---|---|---|---:|---|
| SMA 20 | 🟨 Foundation | Rolling arithmetic mean of 20 closes | Candle index 19 | Chart overlay, visibility toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | SMA-seeded EMA; alpha \(2/21\) | Candle index 19 | Chart overlay, visibility toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 Foundation | Wilder-smoothed close-to-close gains/losses | Candle index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, render/lifecycle tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, render/lifecycle tests |
| Bollinger 20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations | Candle index 19 | Three-line overlay, toggle, legend/current values, stale clearing, render/lifecycle tests |
| Shared indicator hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Depends on validated snapshot | Bind to active chart identity/timeframe, loading/error states, stale-result clearing, no cross-symbol/timeframe leakage |
| Footprint | 🟧 Gated | Deterministic educational accumulator; data explicitly SIMULATED, not exchange-native order flow | Depends on selected candle/price levels | User reference image, reviewed blueprint, explicit-ON cluster renderer, bid/ask cells, tests and performance |
| Heatmap | 🟥 Not implemented | Data source and calculation contract not approved | Not applicable | User reference image, reviewed blueprint, source/data contract, calculation, renderer, controls and tests |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | Not applicable | Data-source feasibility, reference/blueprint, calculation, renderer, controls and tests |

## Formula and correctness contracts

### SMA 20

\[
SMA_t = \frac{1}{20}\sum_{i=0}^{19} C_{t-i}
\]

- Requires 20 valid closing prices.
- Warm-up outputs before index 19 must be null/unavailable, not zero.
- Must remain aligned with the candle index.
- Remaining UI work: visible overlay, on/off control, legend and latest value, stale clearing when symbol/timeframe changes.

### EMA 20

\[
\alpha = \frac{2}{20+1} = \frac{2}{21}
\]

\[
EMA_t = \alpha C_t + (1-\alpha)EMA_{t-1}
\]

- Seed uses the initial 20-period SMA.
- First valid value is index 19.
- Warm-up values must be null.
- Remaining UI work matches the SMA overlay lifecycle.

### RSI 14

- Uses close-to-close change, positive gains and absolute losses.
- Initial average gain/loss is formed from 14 changes.
- Subsequent averages use Wilder smoothing.
- First valid RSI output is index 14.
- Calculation edge fixtures exist; the dedicated pane, 0–100 scale, 30/70 guides, toggle, legend and chart lifecycle tests remain.

### MACD 12/26/9

\[
MACD_t = EMA_{12,t} - EMA_{26,t}
\]

\[
Signal_t = EMA_9(MACD)_t
\]

\[
Histogram_t = MACD_t - Signal_t
\]

- MACD first becomes valid at index 25.
- Signal and histogram first become valid at index 33.
- Warm-up values remain null.
- Remaining work: dedicated pane, both lines, histogram bars, zero reference line, toggle, legend and render tests.

### Bollinger Bands 20,2

\[
Middle_t = SMA_{20,t}
\]

\[
Upper_t = Middle_t + 2\sigma_{population}
\]

\[
Lower_t = Middle_t - 2\sigma_{population}
\]

- Uses population standard deviation, not sample standard deviation.
- First valid band is index 19.
- Remaining work: upper/middle/lower overlays, toggle, current values, stale clearing and rendering tests.

## Shared data and lifecycle requirements

1. Indicator arrays must align to candle indexes; no independent array shifting.
2. Warm-up positions must be null/unavailable, not fabricated values.
3. Only validated backend snapshots may feed the shared indicator hook. No demo fallback.
4. Symbol, venue, dataset, timeframe and chart identity changes must invalidate stale results.
5. Loading and error states must be visible and must not leave old indicator values displayed as if current.
6. Each indicator must have an independent visibility control and correct chart layer/pane.
7. Current values and legends must reflect the active series and last valid candle.
8. Calculation fixtures do not prove chart rendering, provider correctness, or real-time synchronization.

The current calculation test suite covers alignment/warm-up, RSI edge cases, MACD signal warm-up, Bollinger population deviation, the shared calculation entry point, 18 timeframe labels and invalid inputs. This is calculation-level evidence only; it does not prove visual integration.

## Footprint, Heatmap and Liquidation gates

- Footprint remains explicitly SIMULATED and educational until a validated exchange-native bid/ask source is available.
- Footprint OFF must preserve ordinary candlestick layout and normal spacing.
- Only when Footprint is explicitly ON may the chart switch to the dedicated spaced-candle/cluster layout.
- Do not begin Footprint or Heatmap visual implementation before the user supplies the corresponding reference image and reviews the scoped blueprint.
- Heatmap and Liquidation Maps must not be represented as live market-derived features without a validated data source and calculation contract.

## Project-level accounting (separate from indicator completion)

| Project measure | Current evidence | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria = 300/400 ticks | 🟨 75% provisional |
| Gate 10 | 0/10 formally closed | 🟥 All ten remain OPEN |
| Stages 2–6 | Not scored | ⬜ |
| Overall project percentage | M1–M8 weights unapproved | ⬜ Not established |
| Indicator aggregate percentage | No approved weights/acceptance denominator | ⬜ Not established |

WebSocket publisher work does not award indicator progress, Stage ticks or Gate closure. CI success is not owner-side acceptance.

## Indicator work order after the current WebSocket reliability gate

1. Preserve the existing calculation contracts and tests.
2. Audit the shared hook and chart identity/timeframe lifecycle.
3. Complete SMA/EMA overlay controls, legend/current values and stale clearing.
4. Complete RSI and MACD panes with scales/guides and correct warm-up behavior.
5. Complete Bollinger overlay and lifecycle.
6. Add render-level and chart-switch regression tests.
7. Only then begin gated Footprint/Heatmap/Liquidation design after the required references and blueprint review.

No paid provider, hosting, deployment, or Termux is required for this documentation or calculation-level work.
