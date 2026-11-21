## Batch 62J-87 checkpoint — no indicator changes (21 November 2026)

Gate 38 received bounded SQLite writer-lock acquisition retry and a retry-accounting regression test. This is backend telemetry infrastructure only; indicator formulas, data contracts, hook, renderer, UI and indicator tests are unchanged. No indicator progress credit is awarded.

---

## Batch 62J-86 checkpoint — no indicator changes (21 November 2026)

The Gate 38 SQLite initialization fix and full-cardinality benchmark work do not change indicator formulas, contracts, hook, renderer, UI or indicator tests. No indicator progress credit is awarded. The complete calculation and visual-completion matrix in this ledger remains authoritative.

---

## Batch 62J-85 checkpoint — no indicator changes (21 November 2026)

Gate 38 full-cardinality benchmark and storage-write-failure regression are backend observability work only. No indicator calculation, data contract, shared hook, renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

| Indicator/subsystem | Status | Calculation / first valid index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Arithmetic mean of the current close and previous 19 closes; first valid index 19 | Standard chart overlay, toggle, legend/current value, stale-series clearing, renderer/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha = 2/(20+1) = 2/21; first valid index 19 | Overlay, toggle, legend/current value, stale-series clearing, renderer/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder-smoothed average gains/losses over 14 price changes; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12 − EMA26; first MACD index 25; 9-period signal seeded from MACD series, signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 FOUNDATION | 20-close mean ± 2 × population standard deviation; first valid index 19 | Upper/middle/lower overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated candle-index-aligned indicator snapshot | Full symbol/venue/dataset/chart/timeframe identity binding, loading/error lifecycle, stale clearing, cross-series isolation |
| Footprint | 🟧 SIMULATED / GATED | Current accumulator is not exchange-native bid/ask truth | User-provided visual reference, reviewed blueprint, ON-only spaced candle/cluster layout, bid/ask cells, source/data contract and performance acceptance |
| Heatmap | 🟥 NOT IMPLEMENTED | No validated zero-cost source/data contract | User reference, zero-cost source feasibility, data contract, reviewed blueprint, renderer and performance tests |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated source/formula contract | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer and tests |

**Shared invariants:** warm-up values are `null`, never synthetic zero; values align to candle indices; no future-candle repaint; changing symbol, venue, dataset, chart or timeframe clears stale series. Footprint OFF preserves ordinary candle spacing. Only explicit Footprint ON may activate the dedicated spaced cluster layout. Do not begin Footprint or Heatmap visual implementation before the user's reference image(s) and approved scoped blueprint.

Aggregate indicator percentage remains unscored because approved per-indicator weights and completion denominators are not established.

---

## Batch 62J-84 checkpoint — no indicator changes (21 November 2026)

Gate 38 collector tests and its SQLite worker benchmark did not change indicator formulas, data contracts, shared hook, chart renderer, UI or indicator tests. No indicator progress credit is awarded.

| Indicator/subsystem | Status | Calculation / first valid index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; α=2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder smoothing; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 FOUNDATION | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error, stale clear, series isolation |
| Footprint | 🟧 GATED | Simulated accumulator only | User visual reference, reviewed blueprint, ON-only spaced cluster layout, bid/ask cells and performance acceptance |
| Heatmap | 🟥 NOT IMPLEMENTED | No validated zero-cost data contract | User reference, source feasibility, contract, blueprint and renderer |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated formula/source | Zero-cost source feasibility, calculation contract, reference and renderer |

Warm-up remains `null`, not zero; outputs remain candle-index aligned; future-candle repaint is prohibited; identity/timeframe changes must clear stale data. Footprint OFF must preserve normal candle spacing; only explicit ON enables spaced clusters.

---

## Batch 62J-83 checkpoint — indicator implementation unchanged (21 November 2026)

Gate 38 backend observability work did not alter indicator formulas, data contracts, hooks, renderers, UI, or indicator tests. No indicator progress credit is awarded. The existing status table below remains authoritative.



## Batch 62J-82 checkpoint — no indicator changes (21 November 2026)

The exact-head CI for the Gate 38 documentation checkpoint completed SUCCESS, but no indicator source, formula, hook, chart renderer, UI or indicator test changed. No indicator progress credit is awarded. Full formula definitions, warm-up indices, renderer work and invariants remain recorded in this ledger.

| Indicator/subsystem | Status | Calculation / first valid index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; α=2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder smoothing; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 FOUNDATION | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / GATED | Educational accumulator, not exchange-native bid/ask truth | User reference, approved blueprint, ON-only spaced clusters, bid/ask cells, performance tests |
| Heatmap | 🟥 NOT IMPLEMENTED | No approved data source/contract | User reference, zero-cost source feasibility, validated data contract, blueprint, renderer |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated dataset/formula | Zero-cost source feasibility, validated calculation, reference/blueprint, renderer |

Invariants: warm-up values are null, never zero; outputs align with candle indices; no future-candle repaint; identity/timeframe changes clear stale series; Footprint OFF preserves normal candle spacing and only explicit ON enables spaced clusters. Footprint and Heatmap visual implementation remain gated on user-provided references and blueprint review. Aggregate indicator percentage remains unscored without approved weights.

---
## Batch 62J-81 checkpoint — 21 November 2026

No indicator calculation, data contract, hook, chart renderer, UI, or indicator test file changed during the Gate 38 architecture work. No indicator progress credit is awarded.

| Indicator/subsystem | State | Formula / first valid index | Remaining implementation |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Arithmetic mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale-series clearing, renderer/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha = 2/21; index 19 | Overlay, toggle, legend/current value, stale-series clearing, renderer/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder smoothing over 14 close changes; index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 FOUNDATION | Mean ± 2 × population standard deviation; index 19 | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated backend snapshot, candle-index aligned; no DEMO fallback | Active chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / GATED | Educational simulated accumulator; not exchange-native bid/ask truth | User visual reference, approved blueprint, ON-only spaced cluster layout, bid/ask cells, performance acceptance |
| Heatmap | 🟥 NOT IMPLEMENTED | No approved data source/calculation contract | User visual reference, zero-cost source feasibility, validated data contract, blueprint, renderer |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, validated calculation, reference/blueprint, renderer |

### Calculation and rendering invariants

- Warm-up values remain null, never synthetic zeroes.
- All outputs remain aligned to source candle indices.
- No future-candle data may repaint prior indicator values.
- Symbol, venue, dataset, chart, or timeframe identity changes must clear stale series.
- Footprint OFF must preserve standard candlestick layout and ordinary spacing. Only explicit Footprint ON may activate the dedicated spaced cluster layout.
- Footprint and Heatmap visual implementation remain blocked until the user supplies the relevant reference images and reviews the scoped blueprint.
- Liquidation Maps remain blocked until a zero-cost source and validated calculation/data contract exist.
- No aggregate indicator percentage is assigned because no approved weights/denominator exist.

This checkpoint records no change to the complete historical indicator ledger or formula contracts.

---

## Batch 62J-80 checkpoint — no indicator status change (21 November 2026)

This batch corrects WebSocket lifecycle accounting only. No indicator formula, chart renderer, indicator hook, UI toggle or data contract changed. Therefore no indicator completion credit is awarded. The complete formula, warm-up, numerical-invariant and remaining-work ledger follows unchanged below. Current statuses remain: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.

## Batch 62J-79 — bounded WebSocket lifecycle observability (21 November 2026)

**Source/test HEAD:** `2274f9adc5ac9907ea508800a2d962d9a7c14a84`  
**Branch:** `phase-2/market-data-foundation`

- Added a pure ASGI lifecycle observer for `/ws/market-data`. It counts connection starts, current active connections, completed connections, accepted connections, peer disconnects, close-code classes and cumulative duration.
- The observer deliberately does not inspect WebSocket payloads, authorization headers, tickets, IP addresses, symbols, account IDs or query strings.
- Cardinality is fixed: close codes are reduced to five classes (`1xxx`, `2xxx`, `4xxx`, `5xxx`, `other`). Counters saturate at the largest exactly representable JSON integer; duration samples are finite and capped at one day.
- Metrics are exposed only inside the existing bearer-token-protected `/internal/metrics` endpoint, nested under `websocket`; no new public endpoint or credential was added.
- Added middleware tests for accepted/closed lifecycle, peer disconnect and route isolation.
- This is process-local telemetry only. It does not create cross-worker aggregation, central collection, dashboards, durable metrics retention, off-host log storage or external operator notification. Gate 38 remains 🟧 OPEN.
- WebSocket protocol, authentication, replay, queue and data payload contracts are unchanged. No production host or public WSS endpoint was created.

**Exact-head verification:** Automated Tests [44894262277](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262277), CodeQL [44894262276](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262276), and Full Git History Secret Audit [44894262301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262301) are running against this source/test HEAD. Frontend unit tests, backend tests and both CodeQL language analyses have passed; remaining build, container and audit steps are pending. No full CI acceptance is claimed yet.

**ZERO COST:** no hosting, paid provider, Vercel/Cloudflare deployment, production credential, Termux/device command or `main` modification.

---

## Batch 62J-78 — compensated SMA cancellation accuracy (21 November 2026)

**Latest source/test HEAD:** f70f0bcfe2208b4fbfb37440fe8dc3b740e8fbcc  
**Branch:** `phase-2/market-data-foundation`

- Re-audit found a cancellation-order edge case in the normalized SMA from Batch 62J-77: `[Number.MAX_VALUE, 1, -Number.MAX_VALUE]` normalized to approximately `[1, 5.56e-309, -1]`; ordinary left-to-right reduction rounded away the small residual and returned zero instead of the representable mean (1/3).
- Added an error-free floating-point expansion sum for normalized window values before dividing by the period and restoring scale. The expansion is used only when normalized positive/negative terms substantially cancel; ordinary windows keep the fast normalized-sum path. Bollinger middle-band means share this stable mean helper; the normalized population-variance pass remains intact.
- Added order-permutation regression coverage for both `[MAX_VALUE, 1, -MAX_VALUE]` and `[MAX_VALUE, -MAX_VALUE, 1]`; both must return a finite value close to (1/3).
- Complexity: ordinary fast path O(N × P); cancellation fallback is O(N × P²) worst-case because an expansion can hold up to P partials. For fixed SMA20, each fallback window has 20 values and at most 400 partial comparisons. No arbitrary-period UI is introduced.
- EMA, RSI, MACD, WebSocket protocol, host configuration and chart renderer behavior are unchanged. Bollinger's middle-band mean now uses the shared compensated mean; its normalized population-variance formula and bands remain unchanged.
- **Acceptance status:** exact source/test HEAD is f70f0bcfe2208b4fbfb37440fe8dc3b740e8fbcc. Full Git History Secret Audit [44893239399](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44893239399) and CodeQL [44893239414](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44893239414) passed; Automated Tests [44893239425](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44893239425) and Android APK build [44893239420](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44893239420) are still running. No full acceptance claim is made until all finish.
- Indicator visual progress is unchanged: SMA20 remains 🟨 foundation, not a completed overlay. Warm-up index 19, candle-index alignment and prefix causality remain required.

### Full indicator ledger (unchanged visual scope)

| Indicator / component | Status | Calculation / first valid index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Compensated normalized mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing; index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; line index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot, candle-index aligned | Chart/symbol/timeframe identity, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 Simulated / gated | Simulated accumulator; not exchange-native bid/ask truth | User reference image, reviewed blueprint, ON-only spaced cluster layout, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | Data source/calculation contract not approved | User reference image, zero-cost source feasibility, data contract, blueprint, renderer |
| Liquidation Maps | 🟥 Not implemented | No validated dataset/calculation contract | Zero-cost source feasibility, calculation contract, blueprint/reference, renderer |

**Invariants:** warm-up values stay null; no future-candle repaint; all outputs align to source candle indices; identity/timeframe changes clear stale series; Footprint OFF preserves standard candle spacing and only explicit ON enables spaced clusters. No indicator percentage is fabricated.

---

## Latest indicator status — Batch 62J-77 (21 November 2026)

**Source/test HEAD:** e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8 on phase-2/market-data-foundation.  
**Exact-head CI:** Automated Tests [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829): **SUCCESS** — frontend **253/253 across 29 files**; backend **1,249 passed in 48.11s**. CodeQL [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826), Full Git History Secret Audit [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841), and Android debug APK build [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773): **SUCCESS**.

### Batch 62J-77 — SMA intermediate-overflow correction

- Raw rolling sums could overflow even when the arithmetic mean was representable. Example: two finite MAX_VALUE inputs have a finite mean equal to MAX_VALUE, although their unscaled sum is Infinity.
- SMA now computes each rolling window with a normalized scale before summing. It fails closed only when the resulting mean is non-finite, rather than when an avoidable intermediate sum overflows.
- Tests cover repeated MAX_VALUE, cancellation across large opposite-sign values, and subsequent sliding windows.
- First CI exposed two test expectation defects: the legacy assertion still expected SMA to throw, and a large-scale ratio assertion used an unsuitable absolute tolerance. Both were corrected. Final exact-head CI passed.
- Complexity: O(N × P) for N input bars and period P because each rolling window is normalized independently. Standard SMA20 work is 20N window-value visits. This is numerically robust for the current fixed period-20 indicator; if arbitrary very large periods become a chart feature, optimize to a verified O(N) scaled rolling recurrence before enabling that UI.

### Full indicator ledger

| Indicator / component | Status | Calculation / validity contract | Remaining implementation |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Normalized mean of each 20-close window; first valid index 19; finite output guard | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19; normalized seed and finite recurrence | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing; first valid index 14; normalized gain/loss ratio | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33; finite difference guards | Pane, lines, histogram, zero guide, toggle, legend, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ± 2 × population SD; first valid index 19; normalized variance | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot, candle-index aligned | Chart/symbol/timeframe identity, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / gated | Educational simulated accumulator; not exchange-native bid/ask truth | User reference image, reviewed blueprint, explicit-ON spaced cluster layout, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | Source/calculation contract not approved | User reference image, zero-cost source feasibility, data contract, blueprint, renderer |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, calculation contract, blueprint/reference, renderer |

**Correctness invariants:** warm-up values remain null, never zero; output stays candle-index aligned; appending future candles cannot change prior values; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters.

**Progress accounting:** numerical-safety work strengthens the calculation foundation but does not complete visual overlays, panes, toggles, legends or renderers. No per-indicator percentage is fabricated. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.

---

## Latest indicator status — Batch 62J-76 (21 November 2026)

**Source/test HEAD:** 57b918feafd1b259b008b5efe1272199a29facff on phase-2/market-data-foundation.  
**Exact-head CI:** Automated Tests [44876347017](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347017): **SUCCESS** — frontend **252/252 across 29 files**; backend **1,249 passed in 50.02s**. CodeQL [44876347037](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347037) and Full Git History Secret Audit [44876347101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347101): **SUCCESS**.

### Numerical correctness work

- **SMA:** validates every input and rejects non-finite rolling sums/outputs instead of returning Infinity or NaN.
- **EMA:** uses a scale-normalized seed mean and convex-combination recurrence to reduce intermediate overflow; every emitted value must remain finite.
- **RSI:** uses incremental arithmetic means for initial gains/losses, Wilder-equivalent smoothing without multiplying large averages by the period, and a normalized gain/loss ratio. Non-finite price changes fail closed.
- **MACD:** rejects non-finite fast/slow differences and histogram outputs.
- **Bollinger 20,2:** calculates population mean and variance on normalized values, then rejects non-finite deviation or band outputs.
- Three regression tests cover extreme finite values, large but finite RSI gain/loss ratios, and constant large same-sign Bollinger inputs.
- A first CI attempt caught an overly strict floating-point equality assertion (74.99999999999999 vs 75); the test was corrected to use a 10-digit toBeCloseTo tolerance. The corrected source/test HEAD passed exact-head CI.

### Full indicator ledger

| Indicator / component | Status | Calculation / validity contract | Remaining implementation |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; first valid index 19; non-finite intermediates rejected | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19; normalized seed and finite recurrence | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing; first valid index 14; normalized gain/loss ratio | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33; finite difference guards | Pane, lines, histogram, zero guide, toggle, legend, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ± 2 × population SD; first valid index 19; normalized variance | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot, candle-index aligned | Chart/symbol/timeframe identity, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / gated | Educational simulated accumulator; not exchange-native bid/ask truth | User reference image, reviewed blueprint, explicit-ON spaced cluster layout, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | Source/calculation contract not approved | User reference image, zero-cost source feasibility, data contract, blueprint, renderer |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, calculation contract, blueprint/reference, renderer |

**Correctness invariants:** warm-up values remain null, never zero; output stays candle-index aligned; appending future candles cannot change prior values; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters.

**Progress accounting:** numerical-safety work strengthens the calculation foundation but does not complete visual overlays, panes, toggles, legends or renderers. No per-indicator percentage is fabricated. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.

---

## Latest indicator status — Batch 62J-68 (21 November 2026)

**Latest source/config/test HEAD:** `da9b2ad025ac5c49f75c95dbdd5f516573107f87` on `phase-2/market-data-foundation`.  
**Exact-head CI:** Automated Tests [44863517983](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517983): **SUCCESS** — frontend 247/247; backend 1,238 passed in 49.89s; 32/32 workflow steps. CodeQL [44863518025](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863518025) and Full Git History Secret Audit [44863517962](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517962): **SUCCESS**.

No indicator calculation, formula, shared hook, renderer, chart UI, or indicator test changed in Batch 62J-68. The Gate 8 security loader hardening and Docker build-context work are not indicator implementation. **No indicator completion credit is awarded.**

| Indicator / component | Status | Calculation / validity contract | Remaining implementation |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of 20 closes; first valid candle index 19 | Candle overlay, toggle, legend/current value, stale-value clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/(20+1) = 2/21; first valid index 19 | Candle overlay, toggle, legend/current value, stale-value clearing, render/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 close-to-close changes; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; MACD first valid index 25; EMA9 signal and histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend, renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 × population standard deviation; first valid index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback; outputs candle-index aligned | Chart/symbol/timeframe identity binding, loading/error states, stale clearing, per-series isolation |
| Footprint | 🟧 SIMULATED / gated | Educational simulated accumulator; not exchange-native bid/ask truth | Owner reference image, reviewed blueprint, explicit-ON spaced cluster renderer, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | Data source and calculation contract not approved | Owner reference image, source feasibility, validated data contract, reviewed blueprint, renderer |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, validated calculation contract, reviewed blueprint/reference, renderer |

**Correctness invariants**
- Warm-up slots are `null`, never fabricated zero values; every output aligns to candle indexes.
- Appending future candles must not alter prior indicator values (prefix causality).
- Symbol, venue, dataset, chart identity or timeframe changes must invalidate stale values and isolate series.
- Footprint OFF preserves ordinary candlestick spacing. Only explicit Footprint ON activates the dedicated spaced cluster layout.
- Footprint and Heatmap visual work remains blocked until the user's own reference images are supplied and the scoped blueprint is reviewed.
- No aggregate indicator percentage is assigned: there is no approved indicator weighting/acceptance denominator.

**Project accounting:** Stage 1 remains 30/40 criteria = 300/400 ticks = **75% provisional**; Gate 10 remains **0/10 formally closed**; Gate 8 is 🟨 host-verification-only and the other nine gates remain 🟧 OPEN. Overall project and aggregate indicator percentages remain unscored. ZERO COST; no deployment, paid service, Termux/device operation, production credential, or `main` modification.

---

# DEZZTA CHART — Complete Indicator Progress Ledger

## Exact-head Gate 30 and indicator status — Batch 62J-62 (21 November 2026)

- Current source/test HEAD: `0fa2497cbf791e043e1ff314b7f138de2bf23106` on `phase-2/market-data-foundation`.
- Automated Tests [44856652183](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44856652183): **SUCCESS** — frontend **247 tests across 29 files**; backend **1,221 passed in 43.47s**; all 33 workflow steps succeeded.
- CodeQL [44856652218](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44856652218): **SUCCESS**.
- Full Git History Secret Audit [44856652241](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44856652241): **SUCCESS**.
- Gate 30 source increment: added WAL-aware capacity estimation and fail-closed filesystem capacity checks before creating backup/restore artifacts. A regression test verifies inadequate capacity leaves the source unchanged and creates no output artifacts.
- Gate 30 remains OPEN until a timestamped owner-host drill proves the live backend database path, free-space preflight, integrity, foreign-key, schema/row hashes, domain readback, outbox continuity, and post-restore write/read/cleanup.
- No indicator calculation, formula, shared hook, chart renderer, indicator UI, or indicator test changed in Batch 62J-62. No indicator completion credit is awarded.
- Indicator dashboard remains unchanged: SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared indicator hook 🟨; Footprint 🟧 SIMULATED/reference-gated; Heatmap 🟥; Liquidation Maps 🟥.
- Formula contracts remain: SMA20 and SMA-seeded EMA20 first valid at index 19; RSI14 Wilder first valid at index 14; MACD line at index 25 and signal/histogram at index 33; Bollinger20,2 population deviation first valid at index 19. Warm-up values remain null and aligned to candle indexes.
- Stage 1 remains 30/40 = 300/400 = **75% provisional**; Gate 10 remains **0/10 formally closed**; Gate 8 is 🟨 host-verification-only and the other nine gates remain 🟧 OPEN. Overall project and aggregate indicator percentages remain unscored.
- ZERO COST: no deployment, paid service, Termux/device operation, production credential, or `main` modification.


---

## Indicator correctness expansion — Batch 62J-59 (21 November 2026)

- Exact source/test HEAD: 56dd8a3a9ebd9fb635357af5285980c461a5de0f on phase-2/market-data-foundation.
- Exact-head Automated Tests [44853126329](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126329): **SUCCESS** — frontend **247/247 tests across 29 files**; backend **1,218 passed in 49.51s**. Frontend build, bundle secret scans, frontend dependency audit, backend dependency audit, bounded SQLite outbox benchmark, backend container build, Redis shared-guard + persistent-volume smoke test, Trivy scan and vulnerability report upload all succeeded.
- Exact-head CodeQL [44853126331](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126331): **SUCCESS**.
- Exact-head Full Git History Secret Audit [44853126419](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126419): **SUCCESS**.
- Android debug APK build [44853126386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44853126386): **SUCCESS**; artifact ID 14686087699, 3,877,412 bytes, retention 7 days; APK SHA-256 `543977791596e59e314611a5431f01dd4431d84f0fb0855f49ccd79ffd57e101`. CI build is not Android device acceptance.
- Added regression coverage in src/indicators/indicatorCalculations.test.ts for prefix causality across SMA20, EMA20, RSI14, MACD12/26/9 and Bollinger20,2. Prefixes ending at 1, 14, 15, 19, 20, 26, 34, 35, 48 and 64 candles must exactly equal the corresponding prefix of the full-series calculation.
- This guards the no-future-leak requirement needed for historical chart inspection and planned Candle Replay. Appending later candles must not retroactively alter earlier indicator points.
- Added falling-only RSI output and period-one SMA/EMA/RSI boundary tests. Existing warm-up, formula, population-deviation, timeframe and invalid-input tests remain.
- No production calculation, hook, renderer, chart UI or formula changed. This is additional correctness evidence, not visual integration or a completed indicator.
- Dashboard remains: SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥.
- No aggregate indicator percentage is assigned. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 closed; overall project remains unscored.
- ZERO COST: no deployment, paid service, production data, credentials, Termux/device operation, or main-branch modification.

---

**Checkpoint:** 21 November 2026 — Batch 62J-59 indicator prefix-causality and boundary regression coverage; exact-head CI complete
**Branch:** `phase-2/market-data-foundation`  
**Current source/test HEAD:** `56dd8a3a9ebd9fb635357af5285980c461a5de0f`
**Indicator implementation status:** calculation formulas, hook, chart and renderer remain unchanged. Batch 62J-59 adds regression tests only; it does not award visual-integration or formula-implementation completion.
**Interpretation:** statuses describe verified implementation boundaries, not a guessed completion percentage. No indicator weights or acceptance percentages have been approved, so per-indicator or total-indicator percentages are intentionally not fabricated.


## Exact-head evidence refresh — Batch 62J-57 (21 November 2026)

- **Branch HEAD:** `fd6b6f09b928150a7543df9f212bcdb4026c0b4b` on `phase-2/market-data-foundation`.
- **Automated Tests:** [44851517437](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44851517437) — **SUCCESS**.
- **CodeQL:** [44851517382](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44851517382) — **SUCCESS** for JavaScript/TypeScript and Python.
- **Full Git History Secret Audit:** [44851517387](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44851517387) — **SUCCESS**.
- These exact-head workflows close the repository CI verification gap for the current WebSocket reconciliation. They do not establish public WSS, production Redis, owner-host persistence, Android WebView acceptance, or provider-backed market-data delivery.
- **No indicator source, calculation, hook, chart renderer, or indicator test changed. No indicator completion credit is awarded by WebSocket CI.**
- Dashboard remains: SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared indicator hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥.
- Formula contracts remain unchanged: SMA20 and SMA-seeded EMA20 first valid at index 19; RSI14 Wilder first valid at index 14; MACD12/26/9 line first valid at 25 and signal/histogram at 33; Bollinger20,2 population deviation first valid at 19. Warm-up positions remain null and candle-index aligned.
- Footprint remains SIMULATED; Footprint and Heatmap visual implementation remain blocked on owner reference images and reviewed blueprints. Liquidation Maps remain blocked on a validated data/calculation contract.
- No indicator aggregate percentage is published because weights and the acceptance denominator are unapproved. Stage 1 remains 30/40 = 300/400 = 75% provisional; Gate 10 remains 0/10 formally closed; overall project percentage remains unscored.
- ZERO COST: no deployment, paid service, Termux/device operation, production credential use, or `main` modification occurred.

---

## Branch documentation checkpoint — Batch 62J-58 (21 November 2026)

- Status-refresh parent checkpoint: `b96631e4108aadbe80dc118720312081e7b0eddf`; the subsequent status-label reconciliation is documentation-only.
- Exact parent source/test and documentation checkpoint `fd6b6f09b928150a7543df9f212bcdb4026c0b4b` passed Automated Tests, CodeQL and Full Git History Secret Audit (runs 44851517437, 44851517382 and 44851517387).
- Current-head Automated Tests [44852130975](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44852130975) and CodeQL [44852130903](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44852130903) are pending/in progress at this documentation checkpoint; Full Git History Secret Audit [44852130916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44852130916) is **SUCCESS**.
- No indicator source, formula, hook, renderer, test, or calculation contract changed. The indicator dashboard remains exactly as stated in Batch 62J-57; no indicator progress credit is awarded.
- ZERO COST maintained. No deployment, Termux/device operation, production credentials, or main-branch modification occurred.

---

## Exact-head evidence refresh — Batch 62J-48 (20 November 2026)

- Branch: `phase-2/market-data-foundation`; exact source/test HEAD: `0d548aa398cf3efb7952b65e2fb9723e330ddeb6`.
- Automated Tests & Build [44755071944](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44755071944): **SUCCESS**.
- Frontend: **245/245 tests across 29 files**.
- Backend: **1,202 passed, 6 warnings in 44.40 seconds**.
- Frontend dependency audit: **0 vulnerabilities**. Backend dependency audit: **no known vulnerabilities found**.
- CodeQL [44755071870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44755071870): **SUCCESS**.
- Full Git History Secret Audit [44755071865](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44755071865): **SUCCESS**.
- The two commits since the previous checkpoint add four backend regression tests for in-memory ticket single-use/subject binding, exact TTL expiry, wrong-purpose consumption, and entitlement revocation during renewal. Runtime indicator and chart files are unchanged.
- **No indicator state changed.** Passing WebSocket/backend CI validates repository tests; it does not render an indicator in the chart or prove real market-data correctness.
- Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 closed; no indicator or overall-project percentage is inferred.


## Exact-head evidence refresh — Batch 62J-53 (21 November 2026)

- Exact source/test HEAD: `56317eff2b71886040acb998bf692814622feedf` on `phase-2/market-data-foundation`.
- Automated Tests [44774049019](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774049019): **SUCCESS** — frontend **245/245 tests across 29 files**; backend **1,218 passed, 6 warnings in 35.76 seconds**.
- CodeQL [44774050265](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774050265): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44774048914](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774048914): **SUCCESS**.
- Backend CI also completed the bounded synthetic outbox benchmark, dependency audit, container build, Redis ACL/AOF plus persistent-volume smoke test, and container vulnerability scan/report export.
- The 1,218 backend tests include the Redis lease/consumer regression suite. The integration suite ran against the CI Redis service; the run completed with no skipped tests reported in the pytest summary.
- The indicator calculation engine, indicator hook and chart rendering code were not changed. The 245 frontend tests are repository-wide and are **not** evidence that the indicators are visually integrated or accepted against live market data.
- **Indicator state remains unchanged:** SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, shared indicator hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. See the full calculation contracts and remaining acceptance work below.
- Stage 1 remains 30/40 = 300/400 ticks = **75% provisional**; Gate 10 remains **0/10 formally closed**. No new Stage 1 tick or indicator percentage is awarded.
- No deployment, paid service, Vercel/Cloudflare operation, Termux/device command, or `main` modification occurred.

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
| Gate 10 | 0/10 formally closed | 🟧 All ten remain OPEN; active/in progress |
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


## Live evidence refresh — 19 November 2026

Indicator implementation remains unchanged by WebSocket Batch 62J-2. The exact-head CI repair commit `9eb936778f75caa4b0c5aaa512f8e3091be8ad1b` now has Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS (runs `44548655650`, `44548655582`, `44548655649`). This validates the bridge/test repository state, not chart-visible indicator rendering, provider quality or real-time indicator synchronization. Do not increase any indicator status on the strength of WebSocket CI.

| Indicator / subsystem | Status | Verified foundation | Still required |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19; calculation fixtures | Overlay, toggle, legend/latest value, stale clearing, chart render/lifecycle tests |
| EMA 20 | 🟨 | SMA seed, alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, stale clearing, chart render/lifecycle tests |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing, render tests |
| MACD 12/26/9 | 🟨 | EMA12−EMA26; MACD index 25, signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Three-line/band overlay, toggle, legend/latest values, stale clearing and render tests |
| Shared indicator hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Active chart binding, loading/error UI, identity/timeframe stale clearing and cross-series isolation tests |
| Footprint | 🟧 | Deterministic educational accumulator; explicitly SIMULATED | Owner reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance/render tests |
| Heatmap | 🟥 | No implementation verified | Owner reference, reviewed blueprint, source contract, calculations, renderer, controls and tests |
| Liquidation Maps | 🟥 | No validated data/calculation contract | Source feasibility, reference/blueprint, calculation, renderer, controls and tests |

Formula/warm-up contract remains unchanged: SMA20 and EMA20 first output at 19; RSI14 at 14; MACD at 25 with signal/histogram at 33; Bollinger20,2 at 19. Warm-up slots remain null and index-aligned. Footprint OFF retains normal candle spacing; explicit ON alone may switch to the spaced cluster layout. Footprint and Heatmap visuals remain blocked until the user's reference image(s) and reviewed blueprint are available. No per-indicator percentages are invented.


## 19 November 2026 — WebSocket integration evidence boundary

The 62J-3 callback-recovery tests and 62J-4 replica snapshot read-model work do not alter indicator calculations or chart rendering. Therefore all indicator statuses and warm-up indices above remain unchanged. The replica snapshot query now returns its applied cursor from the same SQLite read transaction as its bars, which is a prerequisite for reliable chart snapshot/live handoff, not proof that indicators are synchronized in the browser. Keep SMA/EMA/RSI/MACD/Bollinger at 🟨 until chart bindings, UI state, stale-series clearing and render/lifecycle tests pass. Keep Footprint 🟧 pending user references and reviewed blueprint; Heatmap and Liquidation Maps remain 🟥.


## 19 November 2026 — Batch 62J-5 replay-read-model boundary

Added a bounded Redis replay reader with strict global cursor continuity, exact ten-field series filtering, canonical event/source/ID validation, and fail-closed behavior on missing or trimmed cursor history. This is WebSocket transport infrastructure only. It does not change indicator calculation, chart rendering, provider validation or client synchronization evidence. Keep SMA20/EMA20/RSI14/MACD12/26/9/Bollinger20,2 and Shared Indicator Hook at 🟨; Footprint at 🟧; Heatmap and Liquidation Maps at 🟥. No indicator percentage is awarded.


## 19 November 2026 — Batch 62J-6 event-loop dispatch boundary

Added an event-loop dispatcher that marshals synchronous Redis worker callbacks onto the owning asyncio loop, awaits sync/async callback completion, propagates callback failures before ACK, and rejects same-loop blocking. A real-Redis integration test connects this adapter to replica-to-hub fan-out. This remains transport/lifecycle infrastructure; no indicator calculation, chart binding, visual rendering, or indicator lifecycle acceptance changed. All indicator statuses remain as listed above.


## Batch 62J-7 — 19 November 2026: replica snapshot/replay boundary

The replica snapshot/hub handoff and bounded reconnect replay are transport consistency foundations only. No indicator formula, active chart binding, indicator UI, pane/overlay rendering or chart lifecycle acceptance changed. Preserve the statuses and warm-up indices above: SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED and waiting for owner reference/blueprint), Heatmap 🟥, Liquidation Maps 🟥. Do not award indicator percentage for WebSocket work.


## Batch 62J-8 — 19 November 2026: Gate 25 ACL hardening boundary

The consumer now uses snapshot-generation-scoped Redis groups so routine snapshot replacement does not require destructive XGROUP DESTROY permission. This is transport/security infrastructure only. All indicator statuses, formulas and warm-up indices remain unchanged: SMA20 🟨 (19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. No indicator progress is awarded.


## Batch 62J-9 — 19 November 2026: Redis ACL evidence boundary

A real Redis 7 ACL integration test now exercises restricted publisher and gateway identities, including positive publish/consume/replay and negative command/key-scope checks. This advances WebSocket transport security evidence only. It does not alter indicator calculations, chart rendering or indicator lifecycle acceptance. Keep SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. No indicator percentage is awarded.


## Batch 62J-10 — 19 November 2026: pending event ordering boundary

The Redis consumer now retries its own pending entry before reading new entries, preserving callback/fan-out cursor order after transient callback failure. This is WebSocket transport correctness only; no indicator calculation or visual acceptance changed. SMA20 🟨 (19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥 remain unchanged.


## Batch 62J-11 — 19 November 2026: worker lifecycle evidence boundary

A managed Redis gateway worker now provides bounded thread lifecycle, event-loop dispatch, retry/backoff and fail-closed resnapshot state. This is transport lifecycle evidence only; no indicator calculation, chart binding or visible rendering changed. All indicator statuses and warm-up indices remain unchanged: SMA20 🟨 (19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.


## Batch 62J-12 — 19 November 2026: dedicated Redis config boundary

The separate OHLCV relay configuration contract is added with distinct publisher/gateway ACL credentials, exact key scope, DB0-only and production TLS validation. It is not startup-wired and does not change indicator calculations or visuals. Indicator statuses and formula warm-up indices remain unchanged.


## Batch 62J-13 — 19 November 2026: snapshot/replay/live evidence boundary

A tested replay/live merge helper now drops events already covered by replay, resequences only newer live events, and fails closed on overflow or identity/cursor mismatch. Real Redis 7 integration covers the snapshot cursor-1, replay cursor-1, live cursor-2 handoff. This is transport correctness only; indicator statuses and warm-up indices remain unchanged.


## Batch 62J-14 — 19 November 2026: main route handoff boundary

The source-SQLite WebSocket reconnect path now uses the tested replay/live merge helper and closes with a resnapshot-required signal if handoff validation or queue capacity fails. This does not alter indicator calculations or rendering; all indicator statuses and warm-up indices remain unchanged.


## Batch 62J-14 — 20 November 2026: exact-head CI and indicator boundary

Exact branch head `407d2b38882e92cdf6db5b7df6c44350b6cd746d` passed Automated Tests (backend 1,153 passed; frontend 236 passed across 28 files), CodeQL (Python and JavaScript/TypeScript), and Full Git History Secret Audit. The WebSocket route handoff change is transport-only. No indicator formulas, warm-up positions, chart overlays/panes, controls or lifecycle acceptance changed. Keep the dashboard statuses unchanged: SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED; owner reference/blueprint required), Heatmap 🟥, Liquidation Maps 🟥. No indicator progress percentage is awarded for WebSocket infrastructure.


## 62J-16 status refresh — 20 November 2026

The WebSocket worker lifecycle and callback deadline regression tests were expanded in code batch 62J-16. This is infrastructure reliability work only and **does not change any indicator implementation status or completion percentage**.

| Indicator / subsystem | Status after 62J-16 | Reason |
|---|---|---|
| SMA 20 | 🟨 Foundation | No indicator code or chart overlay changed |
| EMA 20 | 🟨 Foundation | No indicator code or chart overlay changed |
| RSI 14 | 🟨 Foundation | No indicator pane or lifecycle change |
| MACD 12/26/9 | 🟨 Foundation | No indicator pane or rendering change |
| Bollinger 20,2 | 🟨 Foundation | No overlay or rendering change |
| Shared indicator hook | 🟨 Foundation | No chart binding or stale-state lifecycle change |
| Footprint | 🟧 Gated | User visual reference and reviewed blueprint still required |
| Heatmap | 🟥 Not implemented | User visual reference, blueprint and validated data contract still required |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract |

No weighted indicator completion percentage is introduced. Formula/warm-up contracts and visual acceptance criteria above remain unchanged.


## 20 November 2026 — 62J-16 verification reconciliation

No indicator calculation, chart renderer, indicator hook, or indicator UI source was changed in 62J-16. Therefore every indicator row above retains its previous status and acceptance requirements. WebSocket CI success is infrastructure evidence only and must not be counted as indicator completion.

The descendant code/documentation HEAD `468d0aa4a348d997dc7affb71374bc8712cfc39d` completed all three GitHub Actions workflows successfully: Automated Tests run `44642566787`, CodeQL run `44642566989`, and Full Git History Secret Audit run `44642566911`. This confirms the current indicator calculation/test code remains build- and CI-compatible at that repository HEAD; it does not demonstrate visible chart rendering, real-time synchronization, provider correctness, or completion of any indicator acceptance item.

| Indicator / subsystem | Reconciled status | Explicit boundary |
|---|---|---|
| SMA 20 | 🟨 Foundation | Calculation foundation only; overlay/toggle/legend/stale clearing/render tests remain |
| EMA 20 | 🟨 Foundation | SMA-seeded calculation only; visible integration remains |
| RSI 14 | 🟨 Foundation | Wilder calculation only; dedicated pane and guides remain |
| MACD 12/26/9 | 🟨 Foundation | Calculation/warm-up only; MACD/signal/histogram pane remains |
| Bollinger 20,2 | 🟨 Foundation | Population-deviation calculation only; visible band remains |
| Shared indicator hook | 🟨 Foundation | Validated snapshot foundation; chart identity/timeframe lifecycle remains |
| Footprint | 🟧 Gated | Wait for user's reference image and reviewed blueprint; SIMULATED data only |
| Heatmap | 🟥 Not implemented | Wait for reference image, approved data contract and blueprint |
| Liquidation Maps | 🟥 Not implemented | No validated data/calculation contract |

No indicator percentage is published because there is no approved per-indicator acceptance denominator or weighting. Stage 1 provisional 75% and Gate 10 0/10 closure remain separate project measures; neither is an indicator completion score.


## 62J-18 — Gate status color clarification (20 November 2026)

The project owner clarified that all ten gates are ORANGE, not RED. This ledger uses two independent attributes:
- **Closure:** all ten gates remain OPEN (0/10 accepted/closed).
- **Work state/color:** 🟧 ORANGE means active/in progress; it does not mean closed, and it does not mean the gate is blocked/abandoned.

The ten orange/open gates are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. No acceptance evidence is fabricated and no gate is marked green.

Indicator statuses remain unchanged. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation. Footprint remains 🟧 Gated and SIMULATED pending user reference and approved blueprint. Heatmap and Liquidation Maps remain 🟥 Not implemented pending references/data contracts. WebSocket CI does not increase indicator completion.


## 62J-19 reconciliation — 20 November 2026

No indicator implementation or calculation changed in this WebSocket engineering batch. Indicator status remains exactly as recorded above; WebSocket CI success does not increase indicator completion.

Current indicator acceptance sequence:
1. Shared indicator hook: active chart identity/timeframe binding, loading/error lifecycle, stale-result invalidation and cross-series isolation.
2. SMA20 and EMA20 chart overlays: independent toggles, aligned candle-index data, legend/current values and stale clearing.
3. RSI14 pane: 0–100 scale, 30/70 guides, toggle and lifecycle tests.
4. MACD12/26/9 pane: MACD and signal lines, histogram, zero guide, toggle and lifecycle tests.
5. Bollinger20,2 overlay: upper/middle/lower lines, toggle, current values and lifecycle tests.
6. Footprint and Heatmap visual work remains gated by the user's reference images and reviewed blueprint. Footprint remains SIMULATED; Footprint OFF must preserve standard candle spacing.
7. Liquidation Maps remains unimplemented until a validated source and calculation contract exists.

Do not assign percentages to indicators or the whole project until acceptance denominators and weights are explicitly approved. Gate 10 remains 10/10 ORANGE and 0/10 closed.


## 62J-21 — 20 November 2026: documentation integrity and CI reconciliation

The complete indicator ledger was restored from parent revision `a91a104db0acc6391d1511f65e881642b766d81e` after the previous documentation update was found to contain an object-string placeholder in place of the original ledger. The formulas, warm-up indices, indicator statuses, visual gates and work order remain unchanged.

Exact branch HEAD `99bc549e95341310945b987ab4ae11a86c962ea9` completed all three workflows successfully:
- Automated Tests run `44680830387`: SUCCESS — frontend tests/build, backend tests, dependency audits, synthetic outbox benchmark, backend container build, Redis ACL/persistent-volume smoke test, vulnerability scan and report export all passed.
- CodeQL run `44680830205`: SUCCESS — Python and JavaScript/TypeScript jobs.
- Full Git History Secret Audit run `44680830208`: SUCCESS.

This validates repository state at that exact SHA. It does not prove two independent ASGI gateways, production snapshot transport, production Redis TLS/ACL rotation, public WSS, browser/Android acceptance, or external gate closure. No runtime code changed. No indicator progress is awarded for CI or documentation repair.

## 62J-22 — 20 November 2026: WebSocket replica hydration consistency audit

The WebSocket engineering audit found and corrected a consistency race in replica startup hydration. Previously, hydrate_replica_pipeline() read the replica checkpoint and retained bars through two separate SQLite connections/transactions. A Redis consumer commit between those reads could pair a pre-commit cursor with post-commit bars, making the in-memory pipeline state inconsistent with its durable watermark.

The replica store now exposes load_snapshot(), which reads the checkpoint and all retained bars inside one SQLite read transaction. The bridge hydrates from that single snapshot and validates the cursor fields before replacing the in-memory pipeline. Regression coverage asserts hydration no longer calls the two independent read methods and fails closed when no verified checkpoint exists.

**Indicator accounting:** no indicator calculation, chart renderer, or indicator acceptance item changed in this batch. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation; Footprint remains 🟧 Gated/SIMULATED; Heatmap and Liquidation Maps remain 🟥 Not implemented. WebSocket correctness work does not increase indicator completion.

## 62J-23 — 20 November 2026: opt-in FastAPI replica runtime and WebSocket read path

FastAPI now accepts an explicit owner-injected replica runtime factory. When supplied, startup validates the replica store, dedicated Redis client, consumer/store/client/stream identity, atomically hydrates the in-memory pipeline from the verified snapshot, then starts exactly one managed consumer worker for that app instance. The source provider is not started in replica mode, preventing competing local ingestion.

The /ws/market-data route now selects one read domain per application instance: source SQLite remains the default when no runtime factory is supplied; opt-in replica mode uses the replica snapshot/checkpoint and bounded Redis replay. It does not combine source SQLite cursors with replica live events. Existing authentication, exact-series entitlement checks, ping/lease behavior and queue semantics remain shared.

Regression tests cover replica-mode snapshot delivery, startup hydration-before-worker ordering, provider suppression, Redis client cleanup and fail-closed startup without a verified snapshot. The runtime factory is deliberately not environment-enabled: snapshot bootstrap and owner-provisioned Redis TLS/ACL remain explicit deployment responsibilities.

**Indicator accounting:** no indicator formulas or visible chart components changed. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 Foundation; Footprint remains 🟧 Gated/SIMULATED; Heatmap and Liquidation Maps remain 🟥 Not implemented.

## 62J-24 — 20 November 2026: replica runtime readiness hardening

Replica-mode FastAPI startup now validates that the injected consumer exposes ensure_group() and awaits consumer-group bootstrap before starting the worker or accepting application traffic. This verifies the dedicated Redis connection and group readiness during startup rather than allowing a disconnected consumer to appear ready while retrying in the background. Regression coverage checks both successful group bootstrap and fail-closed cleanup on a simulated Redis bootstrap outage.

The replica WebSocket snapshot test fixture now uses UTC_FIXED_V1 for the 1-second timeframe, matching bucket_policy_for_timeframe() and the exact series identity contract. The earlier CI failure was a test-fixture policy mismatch, not a runtime data-loss failure. No indicator implementation or status changed.

## 62J-25 — 20 November 2026: two independent ASGI gateway process acceptance

Added a real multi-process acceptance test that launches two independent Uvicorn/FastAPI gateway processes. Each process opens its own SQLite replica database, its own Redis client and consumer identity, and the same shared Redis stream. Both authenticate and subscribe through the actual /ws/market-data route. A source event is then appended once; the test requires both WebSocket clients to receive cursor 1 and both independent replica checkpoints to advance to 1.

This validates the opt-in FastAPI lifecycle, replica snapshot, live Redis consumer, event-loop dispatcher and WebSocket fan-out together across separate OS processes. It uses the existing CI Redis 7 service and local temporary SQLite files; no paid infrastructure or public deployment is involved.

Indicator calculations and chart UI remain unchanged. No indicator progress is awarded for transport acceptance.

62J-25 test-fixture note: the process acceptance uses the existing make_bar() helper, which emits UTC_LEGACY for backward compatibility. Its WebSocket series identity now explicitly requests UTC_LEGACY so the test validates exact matching rather than mixing it with the default UTC_FIXED_V1 selector.

62J-25 harness note: the initial child process failed before server startup because the test harness used incorrect module ownership for CanonicalInstrument and ProviderInstrumentMapping. The imports now use app.instrument_identity and app.instrument_registry, matching the repository's actual structure.

## 62J-26 — 20 November 2026: replica-backed WebSocket reconnect replay acceptance

Extended the two-process ASGI integration scenario with a reconnecting client that presents an older durable cursor. The actual WebSocket route must replay the retained Redis event from cursor 0 through cursor 1, mark the event as replayed, and complete at the same watermark. This verifies that replica snapshot/checkpoint state and Redis replay use the same cursor domain at the application boundary.

Indicator calculation and visible chart status remain unchanged.


## 62J-27 — 20 November 2026: WebSocket exact-head reconciliation

The exact branch head `5c5205ebc5d6b58b8e177854edb79f93ba9ea118` passed Automated Tests (`44686658866`), CodeQL (`44686658770`) and Full Git History Secret Audit (`44686658757`). The new reconnect assertion extends the real two-ASGI-process test: after both replicas receive live cursor 1, a reconnecting client requests from cursor 0 and the actual replica-backed WebSocket route returns replay cursor 1 and replay completion at cursor 1.

This is transport/reconnect evidence only. No indicator formulas, indicator hook, chart renderer, pane, overlay, control, or visual acceptance item changed. Keep SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook at 🟨 Foundation; Footprint at 🟧 Gated/SIMULATED; Heatmap and Liquidation Maps at 🟥 Not implemented. No indicator aggregate percentage is assigned without an approved denominator.


## WebSocket transport evidence update — Batch 62J-28 (20 November 2026)

The indicator implementation and readiness states above are unchanged. The following transport evidence is recorded separately and does not award indicator progress:

- Code/test commit: ea19ce5ae6623ac09b23d36069960a5368dab3b0.
- Exact-head Automated Tests [44704944924](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944924): SUCCESS; backend pytest **1,164 passed in 40.74 seconds**.
- CodeQL [44704944956](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944956): SUCCESS.
- Full Git History Secret Audit [44704944887](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44704944887): SUCCESS.
- The real two-ASGI-process Redis 7 test injects one transient Redis read error independently in both gateway workers, waits for their successful retry, verifies both WebSocket clients receive cursor 1, then exercises replay reconnect and process restart with cursor parity at 2.
- Existing snapshot-generation replacement coverage remains green; the consumer switches to a new generation-scoped group at the installed snapshot watermark and does not destroy the old group.

**Limit:** the injected read failure is at the Redis client boundary. It is not a real Redis server/network outage. Production snapshot distribution, cross-process snapshot replacement parity, Redis TLS/ACL/credential rotation, and public browser/Android WSS acceptance remain outstanding. WebSocket E is still partially verified. Gate 10 remains 10 ORANGE / 0 closed. Indicator status remains exactly as recorded above.


## Batch 62J-29 — 20 November 2026: exact-head CI and project-control boundary

The current branch HEAD `ea3626cd9e174d0f9a06af2b0fe2550c830e0559` passed all three exact-head workflows:
- Automated Tests [44705774297](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774297) — SUCCESS; backend pytest 1,164 passed, frontend tests/build and container build/smoke passed.
- CodeQL [44705774202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774202) — SUCCESS for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44705774189](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774189) — SUCCESS.

This is WebSocket/repository infrastructure evidence, not indicator rendering acceptance. Indicator statuses remain unchanged: SMA20 🟨 (first valid index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED; owner reference and reviewed blueprint required), Heatmap 🟥, Liquidation Maps 🟥. No aggregate indicator percentage is claimed.

Historical status at the Batch 62J-29 checkpoint: WebSocket E was PARTIALLY VERIFIED. This statement is superseded by Batch 62J-31 below, which completed the defined automated E failure matrix. Production snapshot distribution, production Redis TLS/ACL/credential rotation and external WSS/device acceptance remain separate open operational requirements.

Gate 10 remains **10/10 🟧 ORANGE / 0/10 formally closed**: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. CI cannot substitute for owner-host, provider, device or operator acceptance. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 are unscored; overall project percentage remains unestablished. ZERO COST is unchanged. No Termux work was required for this cycle.



## Batch 62J-31 — 20 November 2026: dual-gateway TCP outage and snapshot-generation acceptance

Exact source/test HEAD `cf6219a1f0fbea5a0daf8378ef47af386f8446fa` passed Automated Tests [44708222353], CodeQL [44708222403] and Full Git History Secret Audit [44708222417]. Backend pytest: **1,166 passed** (6 warnings); frontend: **236 passed across 28 files**.

New WebSocket tests verify (1) a controlled TCP path interruption that severs and rejects Redis connections independently for two live ASGI gateways, followed by recovery without restarting either gateway and cursor-1 parity, and (2) coordinated installation of the same cursor-2 snapshot into two durable replicas, independent new-generation consumer processes applying cursor 3, parity at cursor 3, and isolation of old pending entries. This completes the automated E failure-matrix scenarios defined for dual-gateway network recovery and cross-replica snapshot generation. It is not a Redis server shutdown test and does not establish production WSS readiness.

Indicator statuses remain unchanged: SMA20 🟨 (first valid index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (25; signal/histogram 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED; owner reference and reviewed blueprint required), Heatmap 🟥, Liquidation Maps 🟥. WebSocket work does not award indicator progress.

Gate 10 remains 10/10 🟧 ORANGE / 0/10 closed. The TCP and snapshot tests strengthen Gate 25 repository evidence, but owner-host Redis TLS/ACL/persistence/recovery are still required. Gate 36 still needs public authenticated WSS and browser/Android acceptance. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project percentage not established. ZERO COST maintained. No deployment, paid service, Termux action or main-branch modification.


## Batch 62J-32 — 20 November 2026: Gate 25/36 source and CI evidence audit

This is a source/documentation audit only. No runtime code or deployment configuration changed.

### Gate 25 — Redis shared guard and OHLCV relay

**Verified repository/CI evidence**
- Production `Settings` requires `REDIS_URL`, rejects plaintext `redis://`, and requires an ACL username/password.
- `RedisSharedGuard` configures Redis TLS with `ssl_cert_reqs="required"` and `ssl_check_hostname=True` for `rediss://`.
- `backend/tests/test_shared_guard_tls.py` asserts both certificate-chain and hostname verification options, and confirms plaintext Redis does not silently receive TLS options.
- CI creates a disposable Redis 7 instance with the default user disabled, an ephemeral ACL password, exact HTTP/WebSocket guard key patterns, a restricted command list, AOF `appendonly yes` / `appendfsync always`, and a persisted ACL file on a temporary volume.
- CI verifies unauthenticated access, an incorrect password and an unrelated `SET` are denied; stops Redis and verifies the API fails closed with HTTP 503; restarts Redis and verifies the AOF canary and ACL policy persist; then restarts the backend and verifies recovery.
- Redis 7 publisher/gateway ACL integration tests verify separate least-privilege command/key permissions and prohibit destructive group operations.

**Important implementation boundary**
- The separate `OhlcvRedisRelayConfig` validates production `rediss://`, distinct publisher/gateway ACL usernames and passwords, and exact stream key scope.
- That relay config is intentionally not wired into application startup yet. Its module docstring explicitly defers activation until snapshot transport and owner-controlled ACL credentials are ready.
- The CI Docker smoke test for the shared security guard uses an isolated plaintext Redis endpoint in a private test-only Docker network. The TLS unit test verifies client options but does not establish a live TLS handshake against an owner-controlled Redis host.

**Gate 25 disposition:** repository configuration and disposable Redis 7 ACL/AOF/outage/recovery evidence are materially improved and verified. Gate 25 remains 🟧 OPEN because the owner-host TLS endpoint/certificate, host ACL provisioning, publisher/gateway credential injection/rotation, target-host network restrictions, and live OHLCV relay activation/acceptance are not evidenced. No production relay was enabled.

### Gate 36 — public WSS and clients

- The backend route uses a purpose-bound single-use ticket. `POST /v1/auth/websocket-ticket` verifies Firebase Bearer over HTTPS and issues a 90-second ticket; the client renews every 45 seconds by default and the backend requires the same subject plus an exact-series entitlement recheck.
- Current ticket binding is subject + purpose, not canonical series or Origin/client context. Exact-series access is checked separately before snapshot delivery and on renewal.
- Backend API and frontend transport tests cover issue, invalid Bearer, ticket authentication and same-subject renewal acknowledgement.
- Public owner-host reverse-proxy handshake, browser acceptance, Android WebView acceptance and deployed cross-instance public endpoint tests remain unavailable.

**Gate 36 disposition:** 🟧 OPEN. No public WSS endpoint was deployed or tested, and no browser/Android result is fabricated.

### Gate 10 and project accounting

All ten external gates remain 🟧 ORANGE / OPEN: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Formal closure remains **0/10**.

Indicator progress is unchanged:
- SMA20 🟨 — rolling mean; first valid index 19.
- EMA20 🟨 — SMA-seeded, alpha 2/21; first valid index 19.
- RSI14 🟨 — Wilder smoothing; first valid index 14.
- MACD12/26/9 🟨 — MACD first index 25; signal/histogram first index 33.
- Bollinger20,2 🟨 — population standard deviation; first valid index 19.
- Shared Indicator Hook 🟨 — validated backend snapshot only; chart binding/lifecycle remains.
- Footprint 🟧 — SIMULATED only; user reference and reviewed blueprint required before visual implementation.
- Heatmap 🟥 — not implemented.
- Liquidation Maps 🟥 — no validated data/calculation contract.

Stage 1 remains 30/40 criteria = 300/400 ticks = **75% provisional**. Stages 2–6 remain unscored. Overall project percentage remains unestablished. ZERO COST maintained. No Termux requirement, deployment, paid service, production activation, or `main` modification.

## Batch 62J-33 — 20 November 2026: Gate 10 restore-drill CLI acceptance hardening

**Starting source/test HEAD:** `5bfa0d231469ef711fb4a7162e3a2d5a49715e8c`.
**Starting exact-head CI:** Automated Tests `44710864296` SUCCESS; CodeQL `44710864281` SUCCESS; Full Git History Secret Audit `44710864297` SUCCESS.

### WebSocket sequence closure

- Batch 62J-31 provides the two previously missing automated E scenarios: controlled dual-gateway TCP-path interruption/recovery and coordinated snapshot-generation replacement across two durable replicas with cursor parity.
- E is complete for the defined automated failure-matrix scope. It is not a Redis server shutdown test and does not establish public WSS, production relay activation, production TLS/ACL rotation or external device acceptance.
- Gate 25 and Gate 36 remain ORANGE because those are independent operational acceptance requirements.

### Gate 30 — repository-side restore-drill evidence

The existing `run_restore_drill` already opens the source database read-only and uses SQLite Online Backup API; refuses existing backup/restore destinations; checks integrity, foreign keys, required application tables, full row-content hashes and schema hashes; verifies application-domain readback for instruments, mappings, entitlements, alerts, coverage, OHLCV and outbox high-water; performs a committed post-restore write/read/cleanup; and returns a timestamped path-redacted report with a verifiable SHA-256 digest.

**This batch adds two CLI-level tests:**
1. Failure output is JSON, reports only the error class, and withholds absolute paths and low-level exception detail.
2. Success output is valid JSON with a verifiable report digest, application-domain readback, no path/account leakage, and proof that source bytes remain unchanged.

These tests strengthen the command-line interface intended for a later owner-device drill. They do not execute against the owner's live Android database and do not close Gate 30.

### Gate 10 board — all still OPEN / ORANGE

| Gate | Repository/CI evidence advanced | External acceptance still missing |
|---|---|---|
| 8 | Full-history secret scan and frontend bundle scans | Owner-host secret injection, permissions and runtime log inspection |
| 20 | Firebase verifier/ticket source and API tests | Real no-billing Firebase project, revocation and browser/Android integration |
| 25 | Redis 7 ACL/AOF/fail-closed recovery and dual-gateway TCP-path tests | Owner-host TLS certificate, ACL, rotation, network restrictions and relay snapshot contract |
| 30 | SQLite backup/restore integration, application readback and CLI privacy tests | Actual live Android DB path, fresh-path restore report and recovery-time evidence |
| 31 | Authenticated encryption/decryption and tamper/wrong-key tests | Off-host copy and separate key recovery; one-device constraint remains |
| 34 | CI persistent-volume smoke | Owner-device/host persistent storage, permissions and disk-pressure drill |
| 35 | Backend container and startup/security checks | Owner-controlled HTTPS endpoint and certificate/hostname acceptance |
| 36 | Ticketed WebSocket auth/renewal and automated E matrix | Public WSS reverse-proxy plus browser/Android acceptance |
| 38 | Bounded request metrics and cardinality/redaction foundations | Actual dashboard access control, retention and disk-pressure drill |
| 39 | Durable alert/outbox and retry foundations | No-cost operator delivery, acknowledgement and incident-response exercise |

### Indicator progress — unchanged and explicitly separated

| Indicator | Status | Verified foundation / boundary |
|---|---|---|
| SMA 20 | 🟨 | Rolling arithmetic mean; first valid candle index 19; chart overlay not integrated |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19; chart overlay not integrated |
| RSI 14 | 🟨 | Wilder smoothing; first valid index 14; oscillator pane not integrated |
| MACD 12/26/9 | 🟨 | MACD first index 25; signal/histogram first index 33; pane not integrated |
| Bollinger 20,2 | 🟨 | Population standard deviation; first valid index 19; three-line overlay not integrated |
| Shared Indicator Hook | 🟨 | Validated shared backend snapshot; chart binding/lifecycle acceptance remains |
| Footprint | 🟧 | SIMULATED only; implementation awaits owner reference image and reviewed blueprint |
| Heatmap | 🟥 | Not implemented; awaits owner reference image and reviewed blueprint |
| Liquidation Maps | 🟥 | No validated data/calculation contract |

No indicator completion percentage is invented. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 remain unscored; overall project percentage remains unestablished. Gate 10 remains 10/10 ORANGE / 0 closed. ZERO COST maintained; no deployment, paid service, Termux action or `main` change.

### Next execution boundary

Gate 30 remains the highest-value phone-only acceptance candidate, but its live source database path must be positively identified before any device operation. No Termux command is required for the repository/CI work in this batch. Gate 31 remains constrained by the documented Android package/keyring issue and the lack of a second device/off-host destination. Do not lower security or claim a live-device restore from CI.


## 20 November 2026 — Batch 62J-34 Gate 8/38/39 evidence update

The internal operator scrape routes are now explicitly excluded from request metrics and HTTP request logs: `/internal/metrics` and `/internal/alert-delivery`. This avoids self-observation noise while preserving their exact Bearer-token gate and no-store responses. New API regression coverage checks missing/wrong credentials, authenticated access, response cache policy, query/token non-disclosure, and that internal scrapes do not appear as application traffic.

Alert outbox regression coverage now checks capped exponential backoff with exact nanosecond boundaries and the SQLite signed-int64 overflow path. Retry delays in the fixture are 100 ns on attempt one and capped at 150 ns on attempt two (uncapped exponential would be 200 ns); the event is not claimable one nanosecond before its due time and becomes claimable exactly at the due time. A retry timestamp beyond signed-int64 is converted to a terminal failure rather than reaching SQLite as an overflowing integer.

Indicator status remains unchanged: SMA20 🟨 (first index 19), EMA20 🟨 (19), RSI14 🟨 (14), MACD12/26/9 🟨 (MACD index 25; signal/histogram index 33), Bollinger20,2 🟨 (19), Shared Indicator Hook 🟨, Footprint 🟧 (SIMULATED; owner reference and reviewed blueprint required), Heatmap 🟥, Liquidation Maps 🟥. No indicator code changed and no indicator percentage is awarded.

Gate 10 remains 10/10 ORANGE and 0 CLOSED. Repository tests cannot satisfy owner-host secret injection, external dashboard/retention controls, actual operator acknowledgement/escalation, or device/host restore acceptance. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 remain unscored; overall project percentage remains unestablished because M1–M8 weights are not approved.

## 20 November 2026 — Batch 62J-35 Gate 39 partial fan-out retry contract

Added a regression test for the multi-device delivery boundary: when recipient A accepts an alert and recipient B returns a retryable provider failure, the durable event remains retryable and the next attempt may send to A again. Every attempt carries the same immutable event_id, which is the client-side deduplication key. This explicitly tests the documented at-least-once behavior rather than incorrectly claiming exactly-once provider delivery.

This is adapter-level evidence with a deterministic fake sender. It does not prove Firebase production delivery, Android notification deduplication, bounded provider latency, operator acknowledgement/escalation, or an owner-host incident drill. Gate 39 remains 🟧 OPEN. No indicator implementation changed; indicator statuses and formula warm-up contracts remain unchanged. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project percentage not established. Gate 10 remains 10/10 🟧 ORANGE / 0 closed. ZERO COST; no deployment, paid service, Termux action or main-branch change.


## 20 November 2026 — Batch 62J-36 Gate 39 FCM timeout/shutdown audit

The Batch 62J-35 exact-head CI suite passed all three workflows. A source audit then identified an unresolved delivery bound: Firebase Admin initialization does not set `httpTimeout`, so the SDK default is 120 seconds per HTTP request; the event sender fans out sequentially to as many as 10 active installations; and lifespan shutdown awaits the worker after setting its stop event, which is observed only after the current batch returns. This means neither total event time nor graceful shutdown has a strict application-level bound. The SDK's retry policy can extend elapsed time beyond one request timeout.

No `asyncio.wait_for` cancellation patch was applied: cancelling the await on `asyncio.to_thread` does not terminate its running thread and could allow provider sends to continue after lease expiry, creating a reclaim/duplicate-delivery race. A safe follow-up must define and test provider request/retry bounds, calculate a lease budget for the maximum recipient fan-out plus acknowledgement margin, and specify shutdown semantics. Gate 39 remains 🟧 OPEN. Indicator statuses/formula warm-up indices unchanged; no indicator credit. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall percentage unestablished. Gate 10 remains 10/10 ORANGE / 0 closed. ZERO COST; no deployment, Termux, dependency change, or main-branch modification. See `WORK_CYCLE_2026-11-20_BATCH62J36_GATE39_FCM_TIMEOUT_SHUTDOWN_AUDIT.md` for full evidence and calculations.


## 20 November 2026 — Batch 62J-37 Gate 38 metrics audit and Gate 39 design proposal

Gate 38 source audit confirms a 127-series process-local metrics cap (including overflow), fixed latency buckets, sanitized labels and durations, detached snapshots, lock-protected recording, authenticated no-store scrape endpoints, and exclusion of internal scrape requests from application logs/counters. Production dashboard/access control, cross-replica aggregation, log retention/rotation, disk-pressure handling and live host redaction remain open. Gate 38 stays 🟧.

Gate 39 design proposal is documented in docs/WORK_CYCLE_2026-11-20_BATCH62J37_GATE38_METRICS_GATE39_BOUNDED_WORKER_DESIGN.md. It proposes a parent-supervised child process for synchronous FCM fan-out, a monotonic event deadline, parent-only acknowledgement/token revocation, and lease arithmetic lease >= event deadline + SQLite busy timeout + explicit margin. Candidate values are explicitly provisional. This is a major runtime design and **must not be implemented before owner review and approval**. Gate 39 stays 🟧.

No indicator code or status changed. SMA20/EMA20 first valid index 19; RSI14 index 14; MACD index 25 and signal/histogram index 33; Bollinger20,2 index 19. Footprint remains SIMULATED and gated; Heatmap and Liquidation Maps remain unimplemented. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project percentage and indicator aggregate remain unestablished. Gate 10 remains 10/10 ORANGE / 0 CLOSED. ZERO COST; no deployment, paid service, Termux or main branch modification.


## 20 November 2026 — Batch 62J-38 WebSocket ticket deadline and Android update-readiness audit

The WebSocket ticket HTTPS request now has a 10,000 ms AbortController deadline that remains active through response-body parsing. The request continues to send Firebase ID tokens only in the Authorization header, uses no-store/credentials-omit/redirect-error, and preserves 401 status for the reconnect supervisor. Six tests cover normalized endpoint/request policy, 401 propagation, no-response timeout, body-read timeout, invalid payload, and invalid credentials/URL.

Exact source/test HEAD `734cd20d7525e9d67f6a045dc13a98410e26cdd0` passed Automated Tests & Build, CodeQL (JavaScript/TypeScript and Python), Full Git History Secret Audit, and Android debug APK build. Frontend: 242 tests across 29 files. Backend: 1,172 passed, 6 warnings in 62.95 seconds. Container image build, Redis/persistent-volume smoke, image scan and vulnerability report export passed. No preview release was published.

Android readiness audit: current workflow builds a debug APK, stores a short-lived CI artifact with SHA-256, and supports only explicit opt-in preview publication. It is not a production update channel. A durable release requires an owner-controlled persistent signing key, protected CI secret injection, signed manifest/hash verification, version/schema policy, backup/key custody, and Android package-installer user confirmation. Silent sideload installation is not available to an ordinary app. Public GitHub Releases are the proposed zero-cost distribution path; Play Store publication remains deferred. A 100-year runtime guarantee is impossible; long-term maintainability controls are specified in the Batch 62J-38 work-cycle report. Termux was not used; owner notification/approval is required before any later phone-side signing-key operation.

WebSocket E automated matrix remains complete for defined CI scope. Production WSS, owner-host Redis TLS/ACL and browser/Android acceptance remain open. Gate 10 stays 10/10 ORANGE / 0 CLOSED.

Indicator states remain unchanged: SMA20 🟨 (index 19), EMA20 🟨 (index 19), RSI14 🟨 (index 14), MACD12/26/9 🟨 (MACD 25; signal/histogram 33), Bollinger20,2 🟨 (index 19), Shared Hook 🟨, Footprint 🟧 SIMULATED, Heatmap 🟥, Liquidation Maps 🟥. No indicator UI or formula implementation was added. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall and indicator aggregate percentages remain unestablished.


## 20 November 2026 — Batch 62J-39 WebSocket ticket-endpoint retry regression

Added a supervisor-level regression test for transient HTTPS WebSocket-ticket endpoint failure. The first request fails before socket construction; the supervisor enters reconnecting state, observes its configured bounded backoff, obtains a fresh Firebase ID token, retries ticket acquisition, and only then constructs the next WebSocket. This explicitly complements the pre-existing transient ID-token-provider failure test and the Batch 62J-38 10-second abortable ticket request/header/body timeout tests. No WebSocket runtime code, protocol or production configuration changed.

Exact resulting-head CI must finish Automated Tests/Build, CodeQL and full-history secret audit successfully before this test is marked verified. Gate 39 FCM worker architecture remains a proposal pending owner review; Gate 30 live Android DB restore and Gate 38 host observability remain external acceptance items. Gate 10 remains 10/10 ORANGE / 0 closed.

Indicator status and calculation contracts remain unchanged: SMA20 🟨 (first index 19), EMA20 🟨 (alpha 2/21; first index 19), RSI14 Wilder 🟨 (index 14), MACD12/26/9 🟨 (MACD index 25; signal/histogram 33), Bollinger20,2 🟨 (population standard deviation; index 19), Shared Indicator Hook 🟨, Footprint 🟧 SIMULATED and gated, Heatmap 🟥, Liquidation Maps 🟥. No indicator implementation credit. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall/indicator aggregate percentages unestablished.


Batch 62J-39 test-harness correction: the first CI attempt showed that the deterministic reconnect delay is 50 ms, not 100 ms, because the existing supervisor uses `floor(exponential * (0.5 + random * 0.5))`. The regression test now asserts the exact lower-bound delay (49 ms: no retry; 50 ms: retry). No production reconnect logic was changed. Corrected exact-head CI is pending.


### Batch 62J-39 exact-head CI result

Source/test HEAD `13d0b48adf8fbd040b22689e83160b2945f07a5c` passed Automated Tests & Build (run 44719780403), CodeQL JavaScript/TypeScript + Python (44719780163), Full Git History Secret Audit (44719780242), and Android debug APK build (44719780305). Frontend: 243 tests across 29 files. Backend: 1,172 passed, 6 warnings in 43.42 seconds. Backend container build, shared Redis/persistent-volume smoke, container image scan and vulnerability report export passed. Android preview release was skipped. This does not close owner-host acceptance gates or award indicator completion.


## Batch 62J-40 — FCM deadline / indicator boundary

The Gate 39 worker now uses a disposable spawned child for each event fan-out, bounded to 60 seconds, with process termination and a 90-second minimum lease when enabled (60 s event + 4 s maximum cleanup + 10 s acknowledgement = 74 s calculated; 16 s reserve at the minimum). This changes notification-worker reliability only.

**No indicator implementation changed.** Preserve all statuses and formula contracts:
- SMA20 🟨 — rolling arithmetic mean; first valid index 19; chart overlay/toggle/legend/stale clearing/render tests remain.
- EMA20 🟨 — SMA-seeded, alpha 2/21; first valid index 19; visual integration remains.
- RSI14 🟨 — Wilder smoothing; first valid index 14; dedicated pane, 0–100 scale, 30/70 guides and lifecycle tests remain.
- MACD12/26/9 🟨 — MACD first index 25; signal/histogram first index 33; pane/lines/histogram/zero guide remain.
- Bollinger20,2 🟨 — population standard deviation; first valid index 19; band overlay and lifecycle tests remain.
- Shared Indicator Hook 🟨 — validated backend snapshot foundation; active chart binding, loading/error, stale invalidation and series isolation remain.
- Footprint 🟧 — SIMULATED only; wait for owner reference image and reviewed blueprint; OFF retains normal candles, explicit ON alone enables spaced cluster layout.
- Heatmap 🟥 — not implemented; wait for owner reference, reviewed blueprint and validated data contract.
- Liquidation Maps 🟥 — no validated data/calculation contract.

No indicator percentage is awarded. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall M1–M8 and indicator aggregate percentages remain unestablished. Gate 10 closure remains 0/10 until external acceptance evidence is recorded.


## Batch 62J-40 exact-head CI evidence

The FCM child-process isolation source/test HEAD `54ff8d29db51c87c3b5e3d0a2105e780a9287087` passed Automated Tests & Build (44722147998), CodeQL JS/TS + Python (44722148055), and Full Git History Secret Audit (44722148046). Backend tests: 1,180 passed, 6 warnings in 36.91 seconds. Backend image build, shared Redis/persistent-volume smoke, image scan and vulnerability-report export passed. This does not establish real Firebase delivery or owner-host Gate 39 incident-response acceptance.


### Batch 62J-41 — 20 November 2026

Gate 39 FCM deadline accounting was hardened: the monotonic 60-second budget now starts before synchronous process startup, so spawn time is deducted from the remaining IPC wait. A regression test simulates startup exceeding the budget and checks that the child is terminated. Limitation: the synchronous `Process.start()` call itself cannot be preempted if the host/OS blocks inside process creation. This is source/test hardening only; exact-head CI must pass before verification, and Gate 39 remains open for external operator alert/acknowledgement/escalation and recovery acceptance. Indicator statuses remain unchanged; no indicator credit. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project and indicator aggregate percentages remain unestablished.

## Batch 62J-42 — Gate 39 persistent incident journal and operator acknowledgement

Approved scope implemented on `phase-2/market-data-foundation`:

- Added a bounded SQLite incident journal in the existing owner-configured durable database. Only fixed operational fingerprints, categories, severity, summary codes, timestamps and state are accepted; free-form payloads and identifiers are rejected.
- Active incidents deduplicate by fingerprint. Repeated occurrences increment a capped counter; a new occurrence after acknowledgement reopens the incident and resets escalation.
- Lifecycle states are `open`, `acknowledged`, and `resolved`. Acknowledgement stops escalation; worker recovery resolves the active alert-delivery category.
- Capacity is capped at 1,000 rows. Resolved rows older than 30 days are pruned when a new incident is recorded. If all rows are unresolved at capacity, writes fail closed without deleting active incidents.
- Added a separate `OPERATOR_INCIDENT_TOKEN` (32–256 non-whitespace characters, redacted from settings representations), distinct from `OBSERVABILITY_METRICS_TOKEN`.
- Added internal routes: `GET /internal/incidents?limit=...`, `POST /internal/incidents/{id}/acknowledge`, and `POST /internal/incidents/{id}/resolve`. They use constant-time Bearer-token comparison and no-store responses, and are not registered unless the operator token is configured.
- Added a local escalation loop polling every 15 seconds. Open incidents escalate after 5, 10, and 15-minute successive waits (three bounded levels) via sanitized structured logs. No hosted monitoring, email, SMS or paid service is used.
- Alert-worker degradation/error transitions create incidents; a healthy transition resolves the category. Journal failures do not stop delivery.

Security boundary: the token is an application-level control, not a network perimeter. Owner-host firewall/reverse-proxy policy must restrict these routes to trusted operator access. Replicas have independent local SQLite journals unless a supported shared database is deliberately configured; no cross-replica aggregation is claimed. Acknowledgement attribution is the shared operator role, not individual identity. Host restart, access-control and incident recovery drills remain required, so Gate 39 stays 🟧 OPEN pending exact-head CI and owner-host acceptance.

Indicator statuses and calculations are unchanged. SMA20/EMA20/RSI14/MACD/Bollinger/Shared Hook remain 🟨; Footprint remains 🟧 SIMULATED pending owner reference and blueprint; Heatmap and Liquidation Maps remain 🟥. Stage 1 remains 30/40 = 75% provisional; Stages 2–6 unscored; overall project and indicator aggregate percentages remain unestablished. No Termux, device operation, deployment, paid service or `main` change occurred.


## CI evidence refresh — Batch 62J-42 source verification

The source commit `417276d2838a9a93f1306d05efe5a1cdc8df66a9` completed all three exact-head GitHub Actions workflows successfully:

- Automated Tests & Build: run `44726505742` — SUCCESS. Frontend tests/build, backend tests, backend dependency audit, synthetic outbox benchmark, backend container build, persistent-volume/shared-Redis smoke test, and container scan/report steps completed without failure.
- CodeQL Security Analysis: run `44726505502` — SUCCESS.
- Full Git History Secret Audit: run `44726505520` — SUCCESS.

This closes the source/CI verification portion of Batch 62J-42 only. Gate 39 remains 🟧 OPEN for owner-host validation: restrict internal routes at the network boundary, inject and rotate the separate operator token, verify journal persistence across the actual host restart, and perform a controlled incident → escalation → acknowledgement → recovery drill. No live host access or real operator acceptance is inferred from CI.


## Gate 39 lease-budget arithmetic correction — 20 November 2026

The Batch 62J-40 default lease reserve is **46 seconds**, not 48: 120 s lease − 60 s event deadline − 4 s maximum process cleanup − 10 s acknowledgement allowance = 46 s. The enabled-worker minimum lease remains 90 s, leaving 16 s at the minimum configuration. This correction is documentation-only and does not change indicator status.


## Batch 62J-43 — Gate 39 incident journal edge-case hardening (20 November 2026)

Source/test HEAD: `b576bbaa6e8b22af2f11e1e3f06565250ac193a1`.

Three additional tests now cover: (1) journal capacity exhaustion fails closed without deleting an unresolved incident, (2) only resolved incidents older than the 30-day retention threshold are pruned, and (3) sanitized worker exceptions are journaled and resolved after recovery without persisting raw exception messages.

A pre-fix CI run `44739073900` exposed one regression: Python exception class names contain uppercase letters while the journal fingerprint grammar is lowercase-only. The reporter now lowercases only the fingerprint component while preserving the sanitized error code in logs. The failed intermediate run had 1,195 passed and 1 failed; it is superseded by the exact-head passing run below.

Exact-head CI for `b576bbaa6e8b22af2f11e1e3f06565250ac193a1`:
- Automated Tests: run `44739362168` — SUCCESS; 1,196 backend tests passed, 6 warnings in 43.97 seconds.
- CodeQL Security Analysis: run `44739362102` — SUCCESS.
- Full Git History Secret Audit: run `44739362274` — SUCCESS.
- Backend container build, shared Redis/persistent-volume smoke test, container scan and vulnerability report export: SUCCESS.

Lease arithmetic correction: 120 - 60 - 4 - 10 = **46 seconds** default reserve; at the 90-second minimum, reserve = **16 seconds**. The dashboard and ledger now use the corrected values.

Gate 39 remains 🟧 OPEN because CI does not prove owner-host route isolation, operator-token injection/rotation, journal survival on the actual host restart, or a real induced-failure → escalation → acknowledgement → recovery drill. No live Firebase delivery or external notification channel is claimed. No indicator formula or visual implementation changed.


## Batch 62J-44 — Gate 38 bounded metrics hardening (20 November 2026)

No indicator source, calculation, chart UI, or formula changed in this batch. Indicator status and warm-up contracts remain exactly as listed above. This is deliberate: Stage 1 remains active, and indicator overlays/panes are Stage 4 scope.

- The observability metrics implementation now saturates request, histogram and bucket counters at 2^53 - 1, preserving exact JSON integer representation.
- Accumulated duration is capped at 86,400,000 × (2^53 - 1) milliseconds, a finite bound derived from the existing one-day per-sample cap.
- Added a regression test that seeds each accumulator at its ceiling, records another sample, and verifies no counter, bucket or duration exceeds its ceiling.
- Existing controls remain: 127 total metric series including overflow, allowlisted methods, finite status classes, normalized route labels, process-local metrics, token-gated endpoint, constant-time Bearer comparison, no-store responses and omission of raw URL/query/path parameters/headers/client address from request logs.
- Latest source commit: 040c479bb01fd3d6d8f293aab7831164343ecac8. Latest regression-test commit: a6acf605a44fe356602f92e8bc8e31d1f8e547b6. Exact-head CI is pending and must be checked before calling the batch verified.
- Verification follow-up: code + Gate 30 runbook checkpoint `f26a0717098a008037144e38d28e5b4eafd35564` (docs-only descendant of the source/test tree) completed Automated Tests `44744035644`, CodeQL `44744035708`, and Full Git History Secret Audit `44744035692` with SUCCESS. The successful automated job validates the current source/test tree; the source/test commit's earlier run was cancelled during rapid pushes. No runtime source changed in the docs-only descendant.
- Gate 38 remains 🟧 OPEN for host firewall/reverse-proxy restriction, real operator-token injection/rotation, bounded host-log/collector retention, disk-pressure behavior, real credential-redaction review and dashboard access acceptance.
- Stage 1 remains 30/40 = 75% provisional; no tick is added without explicit mapping to an approved criterion. Gate 10 remains 10/10 🟧 / 0 closed. No overall project or aggregate indicator percentage is invented.
- ZERO COST; no deployment, paid service, main-branch change, Termux or device operation.


## Batch 62J-45 — 20 November 2026: Gate 30 preparation boundary

Added `docs/GATE30_OWNER_HOST_RESTORE_DRILL_RUNBOOK.md` after source inspection of `backend/app/sqlite_restore_drill.py`, `backend/app/sqlite_backup.py`, `backend/app/config.py` and the restore-drill regression suite. The live database path is configured by `INSTRUMENT_REGISTRY_DB_PATH`, defaulting to `./data/instrument_registry.sqlite3` relative to the backend process working directory. The actual injected value, host, working directory and mounted volume are runtime-only facts not available from repository source. The runbook defines the source read-only boundary, distinct fresh output paths, conservative free-space calculation, conjunctive acceptance checks, privacy-safe evidence retention and stop conditions. No device/Termux operation occurred. Gate 30 remains 🟧 OPEN; no Stage 1 tick is awarded. Indicator implementation and all indicator statuses remain unchanged.

## Exact-head indicator accounting refresh — Batch 62J-55 (21 November 2026)

- Runtime/source-test checkpoint remains `56317eff2b71886040acb998bf692814622feedf`; subsequent branch commits in this batch are documentation-only.
- No indicator calculation, hook, chart, renderer, or indicator test files changed during the WebSocket reconciliation.
- No indicator completion credit is awarded for the backend WebSocket CI results.
- SMA 20 🟨, EMA 20 🟨, RSI 14 🟨, MACD 12/26/9 🟨, Bollinger 20,2 🟨, shared indicator hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Footprint and Heatmap visual implementation remain blocked pending the user's respective reference images and reviewed blueprints. Footprint OFF must preserve the ordinary candlestick layout/spacing; the dedicated spaced cluster layout is only for explicit Footprint ON.
- No indicator weights/denominator have been approved; aggregate indicator percentage remains unscored.
- Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed; overall project percentage remains unestablished.
- ZERO COST; no deployment, Termux/device action, or `main` modification.


## Exact-head indicator and CI reconciliation — Batch 62J-56 (21 November 2026)

- **Branch HEAD:** `96bfea52d9920b7d5d49ed85c0536610a6afd037`; branch `phase-2/market-data-foundation`.
- **Exact-head Automated Tests:** [run 44849892717](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44849892717) **SUCCESS**. Frontend **245/245 tests across 29 files**; backend **1,218 passed in 48.17 seconds**. Pytest emitted no warnings summary. All 31 listed workflow job steps completed successfully, including frontend build, source/bundle secret scans, Android host-preflight and preview-publisher tests, SQLite outbox benchmark, dependency audits, backend container build, Redis ACL/AOF + persistent-volume smoke test, Trivy scan and vulnerability-report upload.
- The only code change in this batch is four `legacy=True` options on synchronous WebSocket test clients in `backend/tests/test_ohlcv_redis_consumer.py`. It addresses the test-client deprecation warnings; no production WebSocket, indicator calculation, shared hook, chart renderer or database code changed.
- The dual-ASGI WebSocket failure matrix remains **COMPLETE for the defined automated scope** from Batches 62J-25/28/31. Production snapshot distribution/rotation, production Redis TLS/ACL/credential lifecycle, public WSS and browser/Android acceptance remain external.
- **No indicator progress is awarded by this CI run.** Status is unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, shared indicator hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Calculation contracts remain: SMA20 and SMA-seeded EMA20 first valid at candle index 19; RSI14 Wilder smoothing first valid at index 14; MACD12/26/9 first MACD at 25 and signal/histogram at 33; Bollinger20,2 using population standard deviation first valid at 19. Warm-up slots remain null and candle-index aligned.
- Footprint remains explicitly simulated/educational until validated exchange-native bid/ask data is available. Footprint OFF must preserve ordinary candle layout/spacing; only explicit ON may use the dedicated spaced-cluster layout. Footprint and Heatmap visuals remain gated on the user's reference images and reviewed blueprints. Liquidation Maps remain blocked on a validated data/calculation contract.
- Stage 1 remains **30/40 criteria = 300/400 ticks = 75% provisional**. Ten criteria (8, 20, 25, 30, 31, 34, 35, 36, 38, 39) remain OPEN, 0/10 formally closed. No acceptance tick is awarded by this cycle.
- No indicator aggregate percentage or overall-project percentage is published: neither has an approved weighting/acceptance denominator. Stages 2–6 remain unscored.
- ZERO COST maintained: no deployment, paid service, Vercel/Cloudflare operation, Termux/device operation, production credentials, or `main` modification.


## Batch 62J-88 — backend-only cycle; indicator state unchanged (21 November 2026)

- Exact-head baseline `8424e5eefeecbd06c6534bc34d166f4749ba4055` passed Automated Tests (frontend 255/255 across 29 files; backend 1,268 passed), CodeQL (both languages) and full Git-history secret audit.
- This cycle adds separate-process metrics contention coverage and read-only failure/recovery coverage; no indicator calculation, hook, renderer, chart UI or market-data contract changed.
- SMA20 🟨: arithmetic mean of last 20 closes; first valid candle index 19. Remaining: overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- EMA20 🟨: SMA-seeded EMA; alpha 2/21; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- RSI14 🟨: Wilder smoothing; first valid index 14. Remaining: 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests.
- MACD12/26/9 🟨: MACD index 25; signal/histogram index 33. Remaining: pane, MACD/signal lines, histogram, zero guide, toggle and legend.
- Bollinger20,2 🟨: mean ±2 × population standard deviation; first valid index 19. Remaining: three-line overlay, toggle, displayed values, stale clearing and renderer tests.
- Shared Indicator Hook 🟨: validated candle-index-aligned snapshot. Remaining: identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint 🟧: simulated/gated. Requires user's visual reference, reviewed blueprint, ON-only spaced cluster layout, bid/ask cells and performance acceptance. OFF preserves standard candle spacing.
- Heatmap 🟥: not implemented. Requires user's visual reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥: not implemented. Requires zero-cost source feasibility, validated formula/data contract, reference/blueprint and renderer.
- Warm-up null, candle-index aligned, no future-candle repaint, stale series cleared on identity/timeframe change. No aggregate indicator percentage without an approved denominator.
- Stage 1 30/40 = 75% provisional; Gate 10 0/10 formally closed; overall project percentage remains unscored.


## Batch 62J-89 — test-harness correction; no indicator change (21 November 2026)

The first CI attempt for Batch 62J-88 exposed an unconditional leftover `AssertionError` immediately after the concurrent worker's successful `collector.flush()`. This was a test-edit residue, not collector retry exhaustion. The read-only test and separate-process benchmark contract both passed in that run. The assertion has been removed; exact-head CI is pending. Indicator formula, hook, renderer, UI and data contract remain unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, shared hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Stage 1 remains 75% provisional; Gate 10 remains 0/10 formally closed.


## Batch 62J-90 — indicator state unchanged; Gate 38 reliability tests extended

- Exact-head baseline `2650c70e977b22a4c70a5e0e292dcc3a8a59082c` passed frontend 255/255 and backend 1,269 tests; CodeQL and full-history secret audit passed.
- Full-cardinality 899-series thread/process benchmark passed. Four separate OS processes completed 128/128 flushes, 899/899 series, integrity `ok`; p95 243.724 ms, p99 278.107 ms, 4 retries.
- 16-thread case: 512/512 flushes, p95 654.798 ms, p99 921.534 ms, max 2,769.913 ms, 251 retries. This is synthetic CI evidence and indicates contention tail remains.
- New tests add real SQLite page-limit exhaustion rollback/recovery and app-level proof that collector failure does not block HTTP/WebSocket. Pending exact-head CI.
- No indicator formula, hook, renderer, UI or market-data contract changed. SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed; overall project remains unscored.


## Batch 62J-91 — indicator state unchanged

The disk-full test timing correction changes only its observation timestamp: the failed write was rolled back, and the worker checkpoint remains at 900, so liveness is inspected at 901 rather than 1801. App-level HTTP/WebSocket failure isolation and read-only recovery tests passed. No indicator formula, hook, renderer, UI or data contract changed. SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥. Stage 1 75% provisional; Gate 10 0/10 closed; overall unscored.


## Batch 62J-92 — exact-head CI acceptance; indicators unchanged

Exact HEAD `427e5952d2f209ae1f40405223d8d0a4c7d8408c` passed Automated Tests (frontend 255/255 across 29 files; backend 1,271 passed in 39.80s), CodeQL (both languages) and Full Git History Secret Audit. Gate 38's full-cardinality thread/process benchmark, read-only recovery, SQLite page-limit `SQLITE_FULL` rollback/recovery and application-level HTTP/WebSocket failure isolation all passed. This is backend reliability evidence only; no indicator calculation or renderer changed.

- SMA20 🟨 — arithmetic mean of last 20 closes; first valid candle index 19. Remaining: overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing; first valid index 14. Remaining: 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests.
- MACD12/26/9 🟨 — MACD first valid index 25; signal/histogram index 33. Remaining: pane, MACD/signal lines, histogram, zero guide, toggle and legend.
- Bollinger20,2 🟨 — mean ±2 × population standard deviation; first valid index 19. Remaining: three-line overlay, toggle, displayed values, stale clearing and renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining: identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint 🟧 — simulated/gated; requires user's visual reference, reviewed blueprint, ON-only spaced clusters, bid/ask cells and performance acceptance. OFF preserves standard candle spacing.
- Heatmap 🟥 — not implemented; requires user's visual reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented; requires zero-cost source feasibility, validated formula/data contract, reference/blueprint and renderer.

Warm-up values remain null (never zero), values candle-index aligned, no future-candle repaint, and identity/timeframe changes clear stale series. No aggregate indicator percentage is published without an approved denominator. Stage 1 remains 30/40 = 75% provisional; Gate 10 0/10 formally closed; overall project percentage unscored.


## Batch 62J-93 — indicator progress carry-forward (21 November 2026)

The Gate 38 SQLite batch-read optimization changed backend observability storage only. It did not modify indicator formulas, hook, chart UI, renderer or market-data contracts. Indicator progress therefore remains unchanged:

- **SMA20 — 🟨 foundation:** arithmetic mean of the last 20 closes; first valid candle index 19. Remaining: visible overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- **EMA20 — 🟨 foundation:** SMA-seeded EMA, alpha (2/21); first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- **RSI14 — 🟨 foundation:** Wilder smoothing; first valid index 14. Remaining: dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests.
- **MACD12/26/9 — 🟨 foundation:** MACD first valid index 25; signal and histogram first valid index 33. Remaining: dedicated pane, MACD/signal lines, histogram, zero guide, toggle and legend.
- **Bollinger20,2 — 🟨 foundation:** mean ±2 × population standard deviation; first valid index 19. Remaining: upper/middle/lower overlay, toggle, displayed values, stale clearing and renderer tests.
- **Shared Indicator Hook — 🟨 foundation:** validated candle-index-aligned backend snapshot. Remaining: identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- **Footprint — 🟧 simulated/reference-gated:** bounded synthetic data only. Requires the owner's visual reference, reviewed blueprint, explicit ON-only spaced cluster layout, bid/ask cells and performance acceptance. OFF must preserve normal candle spacing.
- **Heatmap — 🟥 not implemented:** requires owner visual reference, zero-cost source feasibility, validated data contract, reviewed blueprint, calculation and renderer tests.
- **Liquidation Maps — 🟥 not implemented:** requires zero-cost source feasibility, validated calculation/data contract, owner reference/blueprint and renderer tests.

Warm-up values remain null (never zero); outputs align to candle indices; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. No aggregate indicator percentage is published without an approved denominator. Stage 4 visible-indicator work remains behind the official stage gate; no stage was skipped.


## Batch 62J-94 checkpoint — no indicator changes (21 November 2026)

Gate 38 added SQLite tail-latency phase diagnostics only. No indicator formulas, data contracts, shared hook, renderer, UI or indicator tests changed. **No indicator progress credit is awarded.** The complete status table, formulas, warm-up indices, remaining renderer work, Footprint reference/blueprint gate, Heatmap/Liquidation source gates and shared invariants remain unchanged.


## Batch 62J-95 checkpoint — no indicator changes (21 November 2026)

SQLite retry de-synchronization is Gate 38 telemetry infrastructure only. No indicator formula, data contract, shared hook, renderer, UI or indicator tests changed. **No indicator progress credit is awarded.** The complete indicator matrix and shared invariants remain unchanged.
