# Indicator progress reconciliation — Batch 72 (25 November 2026)

**Audited source HEAD:** `6a6e9e82ed2de725bef94e8ed1fa7f28c60e0a49`.  
**Indicator source/UI changes:** none. **Completion credit this cycle: 0.**  
**Complete inventory:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint PRO 2GD remains 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps remain 🟥 OPEN.  
**Focused declarations:** 28 = 21 calculation + 7 shared-hook; this is a declaration count, not passed tests or completion percentage.  
**Integration status:** `CandlestickChart.tsx` still does not integrate `useMarketIndicators`. Stage 4 remains gated.  
**Mathematical invariants:** warm-up nulls; prefix causality; no future-candle lookahead/repaint; exact timestamp/canonical series alignment; clear stale output on identity changes; no calculations for demo/loading/unavailable/error/empty snapshots.  
**Footprint:** OFF preserves standard candle spacing; explicit ON alone uses spaced clusters. The two supplied Footprint references remain authoritative visual targets. Heatmap visual implementation remains reference-gated.  
**Cloudflare note:** the synthetic Worker/DO proof does not change indicator status or count as production market-data provenance. See Batch 72 Cloudflare inventory document.  
**Aggregate indicator completion:** ⚪ NOT SCORED; no approved weighted denominator exists.

---

# Indicator progress reconciliation — Batch 71 (25 November 2026)

**Audited source/test baseline:** `19de41d3dc613a11a0441e65a075f7a1ed5cc685` (Batch 70 documentation-only commit; no indicator source changes).  
**Exact-HEAD CI:** 4/4 SUCCESS; backend 1,426 passed, 1 skipped, 6 warnings.  
**Indicator completion credit this cycle:** none.

| Indicator / subsystem | Calculation/data foundation | Chart rendering, interaction and lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides and lifecycle absent | 🟨 FOUNDATION |
| MACD12/26/9 | MACD first index 25; signal/histogram first index 33 | Dedicated pane, lines, histogram and zero guide absent | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Upper/middle/lower overlays, fill and lifecycle absent | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable backend snapshot/cache/trust gate; 7 hook test declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Stage 4 gated; two supplied references define visual target | 🟧 GATED |
| Volume Profile | Full binning/value-area behavior not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Lawful depth source, aggregation and decay not accepted | Not integrated; reference gate remains | 🟥 OPEN |
| Liquidation Maps | Provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

## Calculation acceptance contracts

- SMA20: arithmetic mean of 20 closes; first valid index 19.
- EMA20: SMA-seeded EMA, alpha = 2/21; first valid index 19.
- RSI14 Wilder: seed from 14 close-to-close changes, then Wilder recurrence; first valid index 14.
- MACD12/26/9: MACD first valid index 25; signal/histogram first valid index 33.
- Bollinger20,2: 20-close mean ± 2 population standard deviations; first valid index 19.

Global invariants: warm-up nulls; prefix causality; no future-candle lookahead/repaint; exact timestamp and canonical series alignment; clear stale output on instrument/timeframe changes; no calculations for demo/loading/unavailable/error/empty backend snapshots.

Focused test declarations remain **28 = 21 calculation + 7 shared-hook**. These are declaration counts, not passed test counts or completed indicators. `CandlestickChart.tsx` still does not integrate `useMarketIndicators`. Footprint OFF preserves ordinary candle spacing; explicit ON alone uses spaced clusters. Heatmap visuals remain gated on the user's reference.

Aggregate indicator completion: ⚪ NOT SCORED because no approved weighted denominator exists. Visible indicator UI remains behind official Stage 4 and its scoped blueprint/user-review gate. The separate 40% overall-project threshold does not waive this stage gate.

---

# Indicator progress reconciliation — Work Cycle 65 (25 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Parent source/test HEAD:** `8b8218d53a7baeb8c13446ba7b91514e4f7312f8`  
**Current source/test HEAD:** `a065e8b2b5b1736aba076d7b12940ae317989e49`  
**Exact-head CI:** 4/4 workflows SUCCESS; Automated Tests 1,424 passed, 1 skipped, 6 warnings in 64.04s.

This cycle changes provider-demand identity only. It does not change indicator calculations, hooks, chart rendering or visual design, and awards no indicator completion credit. The exact source/test HEAD above passed all four required CI workflows.

| Indicator / subsystem | Calculation / data foundation | Chart rendering, interaction and lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, legend, toggle and lifecycle absent | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, legend, toggle and lifecycle absent | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides and lifecycle absent | 🟨 FOUNDATION |
| MACD12/26/9 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram and zero guide absent | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Bands, fill, legend and lifecycle absent | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable snapshot/cache/trust gating; 7 hook test declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated by Stage 4; two supplied references retained | 🟧 GATED |
| Volume Profile | Full binning/value-area calculation not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity source, aggregation and decay not accepted | Not integrated; visual reference pending | 🟥 OPEN |
| Liquidation Maps | Data provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

## Mathematical acceptance contracts

- SMA20: mean of 20 closes; first valid source index 19.
- EMA20: SMA seed, then alpha 2/21; first valid index 19.
- RSI14 Wilder: 14 close-to-close changes for seed; first valid index 14.
- MACD12/26/9: MACD first valid index 25; EMA9 signal and histogram first valid index 33.
- Bollinger20,2: 20-close mean ± 2 population standard deviations; first valid index 19.

Global invariants: warm-up remains null; prefix-causality; no lookahead/repaint; exact timestamp and series identity alignment; clear stale output on identity changes; no output for DEMO/loading/unavailable/error/empty states. Footprint OFF preserves ordinary candle spacing; only explicit ON uses spaced clusters. Heatmap visual implementation remains reference-gated.

Focused test declarations remain 28 (21 calculation + 7 hook), not 28 completed indicators. Aggregate indicator completion remains NOT SCORED because no approved weighted denominator exists.

---

# Indicator progress reconciliation — Batch 62J-244 (25 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Audited documentation HEAD:** `47a62428c4d1ee19ded9f52ae8d7f8a488b13d50`  
**Source/test baseline:** `c80b9ef05fa531f36f4b41673030447f15c97e47`  
**Exact-HEAD CI:** 4/4 workflows SUCCESS on documentation HEAD `47a62428c4d1ee19ded9f52ae8d7f8a488b13d50`; Automated Tests 1,419 passed, 1 skipped, 6 warnings.

## Indicator completion ledger

| Indicator / subsystem | Calculation / data foundation | Chart rendering, interaction and lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, legend, visibility toggle, scale behavior and lifecycle absent | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, legend, visibility toggle and lifecycle absent | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change initialization and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides and lifecycle absent | 🟨 FOUNDATION |
| MACD12/26/9 | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram and zero guide absent | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, fill, legend and lifecycle absent | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable backend snapshot, shared cache, trust gating and stale-output clearing; 7 hook test declarations | Not imported/called by CandlestickChart | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Dedicated renderer gated; supplied two Footprint references define future visual target | 🟧 GATED |
| Volume Profile | Full binning/value-area calculation not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection and recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity source, aggregation and decay methodology not accepted | Not integrated; visual reference gate remains | 🟥 OPEN |
| Liquidation Maps | Data provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

## Source/test evidence

- `src/indicators/indicatorCalculations.ts`: 21 named calculation-test declarations.
- `src/indicators/useMarketIndicators.ts`: keyed immutable snapshot hook; only exposes values for non-empty backend snapshots in ready/degraded state.
- `src/indicators/useMarketIndicators.test.ts`: 7 hook-test declarations.
- `src/components/CandlestickChart.tsx`: no import or call to `useMarketIndicators`; no indicator series, overlay, pane, toggle or legend is connected.
- The current automated workflow on the exact documentation HEAD passed all 41 Automated Tests steps. Backend pytest: 1,419 passed, 1 skipped, 6 warnings. The skipped test is the isolated shared-guard Redis TLS fixture, not a chart-indicator test.

The focused declaration inventory is 28 tests (21 calculation + 7 hook). It is not a completion percentage. The indicator calculation source and chart renderer were not modified in Batch 62J-244.

## Calculation contracts

| Study | Definition | First valid source index |
|---|---|---:|
| SMA20 | Arithmetic mean of latest 20 closes | 19 |
| EMA20 | SMA seed, then EMA with alpha 2/21 | 19 |
| RSI14 Wilder | Seed from 14 close-to-close changes, then Wilder recurrence | 14 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal seeded from first valid MACD | MACD 25; signal/histogram 33 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 |

Global invariants:
- Warm-up outputs remain null.
- Prefix-causality: appending future candles cannot change prior indicator values.
- No future-candle lookahead or repaint.
- Every value remains aligned to its exact source candle timestamp and canonical series identity.
- Instrument/timeframe identity changes clear stale output before new values appear.
- DEMO, loading, unavailable, error and empty backend states expose no indicator calculations.
- Corrections, reconnects and live updates must preserve candle-to-indicator alignment.

## Visual and interaction acceptance

- SMA/EMA/Bollinger: price-pane overlays, per-indicator toggles, accessible controls, legend/current values, axis behavior and update lifecycle.
- RSI: separate 0–100 pane with 30/70 guides and accessible visibility control.
- MACD: separate pane with MACD/signal lines, histogram and zero guide.
- All controls default OFF to preserve the existing candlestick-only experience.
- Avoid chart recreation on every data revision; use only verified Lightweight Charts v5 APIs present in the installed dependency/lockfile.
- No indicator display from demo candles or stale instruments.
- Footprint OFF preserves ordinary candle spacing; explicit ON alone switches to spaced candle clusters and bid/ask cells.
- Heatmap visual work must use the user's supplied reference before implementation.
- Liquidation Maps must distinguish estimated levels from exchange-observed facts.
- Volume Profile family requires agreed bin size, session boundaries, value-area percentage, POC tie-breaking and movable-range semantics.

## Stage gate and progress accounting

The official roadmap remains at Stage 1. `docs/INDICATOR_UI_BLUEPRINT.md` is a parked Stage 4 preparation draft; the broader 40% expansion threshold does not permit skipping the official stage gate. Major chart indicator UI remains gated pending official Stage 4 entry and scoped blueprint/user review.

There are 12 indicator/study rows, but no approved weighted completion denominator. Therefore:
- Aggregate indicator completion: **NOT SCORED** ⚪.
- Calculation foundations do not equal chart-complete indicators.
- No row is upgraded to green without rendering, interaction, lifecycle and regression evidence.

**Batch 62J-244 awards no indicator completion credit.** This cycle reconciles evidence and exact-head CI only.

---

# Indicator progress reconciliation — Batch 62J-243 (25 November 2026)

**Source/test HEAD audited:** `c80b9ef05fa531f36f4b41673030447f15c97e47`  
**Branch:** `phase-2/market-data-foundation`  
**Exact-HEAD CI:** 4/4 workflows SUCCESS on source/test HEAD `c80b9ef05fa531f36f4b41673030447f15c97e47`; Automated Tests reports 1,419 passed, 1 skipped, 6 warnings.

## Current indicator inventory

| Indicator | Calculation foundation | Chart rendering / lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, legend, visibility toggle and series lifecycle not wired | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, legend, visibility toggle and series lifecycle not wired | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides and lifecycle not wired | 🟨 FOUNDATION |
| MACD12/26/9 | MACD begins index 25; signal/histogram begin index 33 | Dedicated pane, lines, histogram, zero guide and lifecycle not wired | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlays, fill, legend and lifecycle not wired | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable snapshot/cache and trust gating; 7 hook test declarations | Not imported/called by CandlestickChart | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Renderer gated; supplied visual references govern future implementation | 🟧 GATED |
| Volume Profile | Full binning/value-area calculation not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | User range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity source, aggregation and decay not accepted | Not integrated; visual reference gate remains | 🟥 OPEN |
| Liquidation Maps | Data provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

## Verified source and test evidence

- `src/indicators/indicatorCalculations.ts`: 21 test declarations for the shared calculation engine.
- `src/indicators/useMarketIndicators.ts`: 7 hook test declarations; values are withheld unless the exact shared snapshot is non-empty validated backend data in ready/degraded state.
- `src/components/CandlestickChart.tsx`: audited source does not import or call `useMarketIndicators`; no indicator overlay, pane, toggle or legend is connected.
- `src/components/CandlestickChart.lifecycle.test.tsx`: 7 chart lifecycle test declarations; these do not constitute indicator rendering acceptance.

Test declaration counts are inventory evidence only. The exact-HEAD CI result is the pass/fail evidence for the current source commit.

## Calculation acceptance rules

| Study | Definition | First valid source index |
|---|---|---:|
| SMA20 | Arithmetic mean of the latest 20 closes | 19 |
| EMA20 | SMA seed, then EMA with alpha (2/21) | 19 |
| RSI14 | Wilder 14-change initialization and recurrence | 14 |
| MACD12/26/9 | EMA12 minus EMA26; signal EMA9 from first valid MACD | MACD 25; signal/histogram 33 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 |

Global rules:
- Warm-up values are null; do not fabricate early values.
- Prefix-causality is mandatory: adding future candles cannot change prior outputs.
- No future-candle lookahead or repaint.
- Values remain aligned to source timestamps and the exact selected series.
- Instrument/timeframe identity changes clear old outputs before new values are shown.
- DEMO, loading, unavailable, error and empty backend states expose no indicator calculations.

## Visual and interaction acceptance

- SMA/EMA/Bollinger: price-pane overlays, per-indicator visibility, accessible controls, legend/current value, axis/scale behavior and update lifecycle.
- RSI: separate pane, 0–100 scale, 30/70 guides, accessible visibility control.
- MACD: separate pane, MACD/signal lines, histogram and zero guide.
- All controls default OFF so the current candlestick-only experience is preserved.
- Do not recreate the chart on each data revision. Use verified Lightweight Charts v5 APIs from the installed package/lockfile; never invent API signatures.
- On snapshot replacement, live update, correction, reconnect, or series switch, keep every plotted point aligned to the matching source bar.
- No calculations or displays from DEMO candles or stale prior instruments.

## Reference-driven indicator gates

- Footprint: the user's two saved Footprint references define the intended dark layout, red/green bid-ask cells, price-aligned volume bars, numeric labels, highlighted rows and deliberate cluster spacing. Ordinary candles and spacing remain unchanged while Footprint is OFF; only explicit ON selects spaced clusters.
- Heatmap: keep visual implementation gated until the user supplies/identifies the reference for the implementation task.
- Liquidation Maps: require a separate provenance and estimation-methodology review; never label estimated levels as exchange-observed.
- Volume Profile family: define bin size, session boundaries, value-area percentage, POC tie-breaking, and movable-range behavior before chart integration.

## Roadmap gate and progress accounting

`docs/INDICATOR_UI_BLUEPRINT.md` is a parked Stage 4 preparation draft. The official roadmap is still at Stage 1. The 40% broader UI/feature gate does not authorize skipping official roadmap stages. Visible indicator UI implementation remains parked until official Stage 4 entry and owner review/acceptance.

The inventory has 12 indicator/study rows, but this is not a completion denominator. Calculation, data provenance, rendering, interaction, lifecycle and regression evidence must be scored separately. Therefore:
- Aggregate indicator completion: **NOT SCORED** ⚪.
- A calculation foundation does not make an indicator chart-complete.
- No indicator is upgraded to green merely because its formula or unit tests exist.

This batch changes WebSocket cleanup/recovery only. No indicator calculation engine or chart renderer was changed.

---

# Indicator ledger reconciliation — Batch 62J-243 (25 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Project HEAD at reconciliation:** `e759472218f6bb8167996236f658c0d6306128a9`  
**Scope:** explicit per-indicator calculation/integration evidence and unchanged math acceptance criteria.

## Indicator status

| Indicator | Calculation / methodology foundation | Chart rendering and lifecycle | Current status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, legend, visibility toggle and series lifecycle not accepted | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, legend, visibility toggle and series lifecycle not accepted | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides and lifecycle not accepted | 🟨 FOUNDATION |
| MACD12/26/9 | MACD begins index 25; signal and histogram begin index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide and lifecycle not accepted | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, fill, legend and lifecycle not accepted | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed snapshot/cache and trust-gating foundation | Not integrated into CandlestickChart; stale-key and toggle lifecycle acceptance open | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Dedicated renderer gated; visual references must be followed; normal candles must remain unchanged when OFF | 🟧 GATED |
| Volume Profile | Full calculation, binning and value-area behavior not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Full session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | User-selected range and recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity source, aggregation and decay methodology not accepted | Not integrated; user visual reference gate remains | 🟥 OPEN |
| Liquidation Maps | Provenance, estimation methodology and confidence limitations not accepted | Not integrated | 🟥 OPEN |

## Calculation acceptance criteria

- SMA20: mean of the current 20 closes; first non-null result at index 19.
- EMA20: SMA seed over the first 20 closes; alpha (2/21); first non-null at index 19.
- RSI14: Wilder initialization from 14 price changes; first non-null at index 14.
- MACD12/26/9: EMA12 minus EMA26; first MACD at index 25; signal EMA9 and histogram first valid at index 33 under first-valid-MACD seeding.
- Bollinger20,2: 20-close mean and population standard deviation; first valid at index 19.
- All warm-up outputs must be null; calculations must be prefix-causal; no future-candle lookahead; values must be timestamp-aligned; series identity changes must clear stale values.

## Visual and interaction gates

- SMA/EMA/Bollinger: overlay rendering, toggles, legend, axis handling and update lifecycle remain unaccepted.
- RSI/MACD: separate panes, correct scale, guide lines, labels and update lifecycle remain unaccepted.
- Footprint: user-provided Footprint references govern visual implementation. Footprint OFF = ordinary candlesticks and ordinary spacing; Footprint ON = spaced cluster layout with legible bid/ask cells.
- Heatmap: do not begin visual implementation before using the user's Heatmap reference.
- Volume Profile family: define bin size, value-area percentage, POC tie-breaking, session boundaries and movable-range behavior before chart integration.
- Liquidation Maps: do not imply exchange-observed liquidation levels where only estimates or synthetic data are available.

## Progress accounting

The 12 rows above are a scope inventory, not a numeric completion denominator. Calculation foundations do not count as completed chart indicators. No aggregate percentage is published until each indicator has weighted calculation, data provenance, chart rendering, interaction, lifecycle and regression criteria. Aggregate indicator progress remains **NOT SCORED ⚪**.

This batch changes WebSocket recovery code and documentation only; no indicator engine or renderer was changed. The indicator states above are therefore not upgraded by the WebSocket commits.

# Offline WebSocket route demand integration — Batch 62J-240 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Parent HEAD:** `4262019813feff3f524101684eea36b945f0b513`  
**Scope:** authenticated WebSocket route ↔ local synthetic/offline demand lease lifecycle.  
**ZERO COST:** local in-memory adapter only. **Vercel:** no deployment. **main:** untouched.

## Implemented boundary

- `create_app` owns an `InMemoryOfflineProviderAdapter` and `ProviderDemandCoordinator`.
- Only the explicit `provider=offline-fixture` identity acquires a demand lease.
- Lease acquisition occurs after canonical mapping, active-instrument, calendar and entitlement checks.
- Demand key is deterministic from source, synthetic venue, canonical instrument ID and OHLCV timeframe.
- The route's existing `finally` cleanup unsubscribes the downstream stream and releases the offline lease, including disconnect and early-return paths after acquisition.
- Other provider identities do not acquire this adapter. No network client, provider SDK, live feed, external ACK or recurring data service is enabled.

## Regression evidence added

`backend/tests/test_api.py` adds a route-level test with two authenticated synthetic subscribers:
- first subscriber starts exactly one offline demand;
- second subscriber shares that demand (subscriber count 2, still one start);
- second disconnect leaves first lease active;
- final disconnect releases the last lease and stops the in-memory adapter;
- final lease count and adapter active set are both zero.

This is local single-process lifecycle evidence only. It does not close provider lifecycle, provider ACK, multi-process ownership, public WSS/TLS or production E2E gates.

## WebSocket blocker status

| Item | Status | Evidence |
|---|---|---|
| Offline coordinator primitive + token integrity | 🟩 | Existing coordinator tests and Batch 62J-239 lease-forgery regression |
| Synthetic route acquire/release lifecycle | 🟩 | Batch 62J-240 route-level two-subscriber/disconnect regression (subject to exact-HEAD CI) |
| Route ↔ external provider lifecycle | 🟥 | Deliberately not connected; outside offline-only boundary |
| Dynamic external subscribe/unsubscribe ACK | 🟥 | No external provider contract or ACK verification |
| Cross-process / multi-host demand ownership | 🟨 | In-memory coordinator is one process only |
| Public WSS/TLS and client E2E (Gate 36) | 🟥 | External endpoint, identity, TLS and device evidence absent |
| Gate 25 external snapshot receipt/high-water ACK | 🟥 | Owner-host custody and durable gateway ACK evidence absent |
| Redis destructive retention | 🟧 | No destructive trimming/deletion until all pending-entry and gateway acceptance proofs exist |

## Indicator progress — no false completion credit

No indicator calculation engine or renderer was changed in this batch. Existing verified foundations and chart integration gaps remain:

| Indicator | Calculation foundation | Chart integration | Overall |
|---|---|---|---|
| SMA20 | 🟩 20-close arithmetic mean; first valid index 19 | 🟥 overlay/legend/visibility/lifecycle not accepted | 🟨 Foundation |
| EMA20 | 🟩 SMA-seeded; α=2/21; first valid index 19 | 🟥 overlay/legend/visibility/lifecycle not accepted | 🟨 Foundation |
| RSI14 Wilder | 🟩 14-change seed + Wilder recurrence; first valid index 14 | 🟥 dedicated 0–100 pane and guides not accepted | 🟨 Foundation |
| MACD12/26/9 | 🟩 MACD first index 25; signal/histogram index 33 | 🟥 pane, lines, histogram and zero guide not accepted | 🟨 Foundation |
| Bollinger20,2 | 🟩 20-close mean ± 2 population SD; first valid index 19 | 🟥 upper/middle/lower overlay and fill not accepted | 🟨 Foundation |
| Shared Indicator Hook | 🟨 keyed snapshot/cache and trust-gating foundation | 🟥 not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | 🟨 synthetic/offline accumulator | 🟥 renderer gated; reference match not implemented | 🟧 Gated |
| Volume Profile | 🟥 complete calculation not verified | 🟥 not integrated | 🟥 Open |
| Complete Volume Profile | 🟥 complete calculation not verified | 🟥 not integrated | 🟥 Open |
| Movable-range Volume Profile | 🟥 range selection/calculation lifecycle not verified | 🟥 not integrated | 🟥 Open |
| Heatmap | 🟥 depth/liquidity engine not accepted | 🟥 not integrated; user reference still required | 🟥 Open |
| Liquidation Maps | 🟥 methodology/provenance not accepted | 🟥 not integrated | 🟥 Open |

Numerical invariants: SMA/EMA/Bollinger first valid index 19; RSI14 index 14; MACD line index 25 and signal/histogram index 33 under first-valid-MACD seeding. Warm-up remains null; outputs must be prefix-causal, timestamp-aligned and cleared on series changes. Footprint OFF must preserve ordinary candles; ON alone selects spaced clusters.

## Project dashboard

| Stage / measure | Status |
|---|---|
| Stage 1 | 🟨 30/40 = 75% provisional inherited baseline |
| Stage 2 — data infrastructure | 🟦 Active; no approved denominator |
| Stage 3 — chart engine/timeframe | ⬜ Not scored |
| Stage 4 — indicators/analytics | 🟪 Gated; aggregate not scored |
| Stage 5 — professional UI/tools | ⬜ Not scored |
| Stage 6 — hardening/APK | ⬜ Not scored |
| Gate 10 | 🟥 0/10 formally closed |
| Overall project | ⚪ NOT SCORED — no approved weighted denominator |
| Aggregate indicator completion | ⚪ NOT SCORED — no approved denominator |
| Significant progress / IP3S | ⚪ NOT SCORED — no approved formula |

Target remains around **24 December 2026** as a planning target, not a guarantee. No paid service, Vercel deployment, live data connection, main-branch update or destructive Redis retention is part of this batch.

---

# Current exact-head reconciliation — Batch 62J-239 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Parent HEAD before this batch:** `1929394bb557cd86369416b1d1ccfe283677b820`  
**Purpose:** correct lease-token integrity, add regression coverage, reconcile indicator and project status.  
**ZERO COST:** maintained. **Vercel:** no deployment. **main:** untouched.

> This entry supersedes older checkpoint summaries below where their HEAD or workflow state differs. The parent SHA had 4/4 workflows completed successfully; this batch's new commit requires fresh exact-HEAD CI.

## Current indicator status

| Indicator | Calculation foundation | Chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close mean; first valid index 19 | Not accepted | 🟨 FOUNDATION |
| EMA20 | SMA-seeded; alpha 2/21; first valid index 19 | Not accepted | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed; first valid index 14 | Not accepted | 🟨 FOUNDATION |
| MACD12/26/9 | MACD index 25; signal/histogram index 33 | Not accepted | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Not accepted | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable snapshot/cache and trust-gating foundation | Not integrated into CandlestickChart | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Renderer gated; supplied visual references retained | 🟧 GATED |
| Volume Profile | Not fully verified | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Not fully verified | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Not fully verified | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity engine not accepted; reference gate remains | Not integrated | 🟥 OPEN |
| Liquidation Maps | Methodology/provenance/renderer not accepted | Not integrated | 🟥 OPEN |

No indicator source or chart renderer is changed by Batch 62J-239. Test declaration counts are not completed-indicator counts. Warm-up values remain null; future-candle lookahead and stale-series carryover are prohibited.

## WebSocket / external acceptance

| Item | Status |
|---|---|
| Offline provider-demand lease coordinator | 🟩 Local primitive; lease-token integrity hardened in this batch |
| Coordinator ↔ authenticated WebSocket route | 🟥 Not wired |
| Coordinator ↔ provider lifecycle | 🟥 Not wired |
| Dynamic provider subscribe/unsubscribe acknowledgement | 🟥 Not verified |
| Cross-process / multi-host demand ownership | 🟨 Local-only; production acceptance open |
| Gate 36 public WSS/TLS and client E2E | 🟥 External acceptance open |
| Gate 25 owner-host snapshot/receipt/high-water ACK | 🟥 External acceptance open |
| Redis destructive retention | 🟧 Blocked pending gateway and pending-entry proof |

These statuses are intentionally conservative. Local fake/offline tests do not prove provider-side acknowledgements, public TLS, production identity, multi-host failover, owner-host custody or durable gateway acceptance.

## Project dashboard

- Stage 1: 30/40 = 75% provisional inherited baseline 🟨
- Stage 2: active, unscored 🟦
- Stage 3: unscored ⬜
- Stage 4: gated 🟪
- Stage 5: unscored ⬜
- Stage 6: unscored ⬜
- Gate 10: 0/10 formally closed 🟥
- Overall project: NOT SCORED ⚪ (no approved weighted denominator)
- Indicator aggregate: NOT SCORED ⚪
- IP3S / significant progress: NOT SCORED ⚪

Target delivery: around 24 December 2026 (planning target).

---

# Exact-HEAD CI closure — Batch 62J-237 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Exact audited HEAD:** `fa83c322df377b2c852ffac1fb499898db3b891e`  
**Source/test baseline:** `bd4904b52d29b3ec456da91014e90922fec35f21` (unchanged; this batch only updated documentation).

## CI result — 4/4 terminal SUCCESS on the exact HEAD

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | 45527447791 | 🟩 SUCCESS — 41/41 steps |
| CodeQL | 45527447840 | 🟩 SUCCESS — Python 8/8 and JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45527447819 | 🟩 SUCCESS — 7/7 |
| Full Git History Secret Audit | 45527447878 | 🟩 SUCCESS — 6/6 |

Backend pytest: **1,394 passed, 1 skipped, 6 warnings in 64.34s**. The skipped test is `tests/test_shared_guard_tls_integration.py`, whose isolated Redis TLS fixture was not configured for that test invocation. Do not treat the skip as owner-host Redis TLS acceptance.

The same Automated Tests run completed the backend container smoke test:
- backend health JSON valid;
- Redis ACL rejects unauthenticated access, incorrect password and unrelated SET;
- Redis AOF data and ACL persist through Redis restart;
- API request protection fails closed during Redis outage and recovers after restart;
- backend runs as UID/GID 10001;
- mounted SQLite volume ownership, integrity and restart persistence pass;
- HTTP rate-limit rejection passes.

Backend dependency audit reported no known vulnerabilities. Container image vulnerability scan completed and its JSON report was uploaded as artifact `14983702058`; this checkpoint does not claim a clean image scan without separately inspecting that report. No failed workflow steps; no workflow remains running for this HEAD.

## Engineering boundary and next work

The source/test baseline still has the provider-demand gap: the authenticated WebSocket path validates canonical series and entitlement, then registers downstream fan-out; cleanup releases the downstream stream. No provider-demand acquire/release coordinator is wired into that lifecycle. The provider adapter remains a static configured-symbol session. A future coordinator must be provider-neutral and tested first with deterministic fake/offline sources; do not activate or provision any live market-data provider under ZERO COST. No SDK dependency change or live-source integration is authorized by this documentation update.

Major provider-coordinator implementation remains behind scoped blueprint review. Existing WebSocket work is not being declared complete: Gate 36 public WSS/TLS, real client lifecycle, Firebase E2E and multi-instance acceptance remain external. Project Gate 25 owner-host signed-snapshot transfer, persisted receipts after restart and durable per-gateway high-water ACK remain external.

## Indicator ledger

The source inventory remains **28 test declarations**: 21 calculation-engine + 7 shared-hook. Calculation foundations remain separate from chart integration:
- SMA20, EMA20, RSI14 Wilder, MACD12/26/9 and Bollinger20,2: 🟨 calculation foundations; no accepted visible chart integration.
- Shared Indicator Hook: 🟨 snapshot/trust/cache foundation; not called by `CandlestickChart.tsx`.
- Footprint PRO 2GD: 🟧 synthetic/offline only; visual implementation remains gated and must preserve ordinary candles when OFF.
- Volume Profile, Complete Volume Profile, movable-range VP, Heatmap and Liquidation Maps: 🟥 incomplete/not integrated.
- Aggregate indicator completion: ⚪ NOT SCORED; no approved denominator.

Math invariants remain: SMA/EMA/Bollinger first valid index 19; RSI14 Wilder index 14; MACD12/26/9 MACD index 25 and signal/histogram index 33; warm-up values null; prefix-causal outputs; no future-candle repaint.

## Project progress

| Stage / measure | Status |
|---|---|
| Stage 1 | 🟨 30/40 = 75% provisional |
| Stage 2 | 🟦 Active engineering / NOT SCORED |
| Stage 3 | ⬜ NOT SCORED |
| Stage 4 | 🟪 GATED |
| Stage 5 | ⬜ NOT SCORED |
| Stage 6 | ⬜ NOT SCORED |
| Gate 10 | 🟥 0/10 formally closed |
| Overall project | ⚪ NOT SCORED — no approved weighted denominator |
| Significant progress / IP3S | ⚪ NOT SCORED — no approved formula |
| Aggregate indicators | ⚪ NOT SCORED |

Stage 1's ten remaining criteria are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. The two separate items named #25 remain distinct: Stage 1 criterion #25 is Redis TLS/ACL/persistence acceptance; Project Gate 25 is signed-snapshot installation/receipt/high-water ACK acceptance.

**Controls:** ZERO COST; no paid services; no deployment; no Vercel; `main` untouched; no destructive Redis retention. APK planning target remains approximately **24 December 2026**.

---

# Latest verified indicator and project checkpoint — Batch 62J-236 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Verified documentation parent:** `2553b942fbcb99d2a9f9b078ad2ff3be5d242912`  
**Source/test baseline:** `bd4904b52d29b3ec456da91014e90922fec35f21` (unchanged by Batch 62J-235/236 documentation updates)  
**Exact-parent CI:** 4/4 terminal SUCCESS on `2553b942fbcb99d2a9f9b078ad2ff3be5d242912`:
- Automated Tests `45526623643`: 41/41 steps; backend pytest **1,394 passed, 1 skipped, 6 warnings in 64.11s**.
- CodeQL `45526623850`: Python 8/8 and JavaScript/TypeScript 8/8.
- OCI ARM64 `45526623693`: 7/7 steps.
- Full Git History Secret Audit `45526623570`: 6/6 steps.
The single skip is the separately configured Redis TLS integration fixture, which was not configured in CI. It does not count as production Redis acceptance. All four workflows are terminal and exact-SHA matched.

**Indicator source audit:** `indicatorCalculations.test.ts` has 21 `it(...)` declarations; `useMarketIndicators.test.ts` has 7. The verified total is **28**. The hook calculates only for backend-origin ready/degraded snapshots, caches by immutable snapshot identity, and clears demo/loading/unavailable/error output. `CandlestickChart.tsx` does not import/call `useMarketIndicators`; visible chart integration remains incomplete. See [Batch 62J-236](WORK_CYCLE_2026-11-25_BATCH62J236_STAGE1_AND_INDICATOR_RECONCILIATION.md).

**Stage 1:** 30/40 = 75% provisional 🟨; 10 remaining criteria are 8, 20, 25, 30, 31, 34, 35, 36, 38, 39. Gate 10 = 0/10 formally closed 🟥. Stage 1 checklist criterion #25 is Redis TLS/ACL/persistence; separately tracked Project Gate 25 is Ed25519 snapshot receipt/high-water ACK. They are distinct blockers.
**Project:** Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.
**Controls:** ZERO COST; `main` untouched; no Vercel deployment; no destructive Redis retention; APK target approximately 24 December 2026.

---

# Latest verified checkpoint — Batch 62J-235 (25 November 2026)

**Active branch:** phase-2/market-data-foundation  
**Latest documentation checkpoint before SDK addendum:** 3178f4f78ff12aeff24d2d9f6d2a601633051bbd  
**Unchanged code/test baseline:** bd4904b52d29b3ec456da91014e90922fec35f21  
**Exact audited HEAD CI:** 4/4 terminal SUCCESS — Automated Tests 45521703215; CodeQL 45521703291; OCI ARM64 45521703194; Full Git History Secret Audit 45521703184.  
**Provider-demand finding:** client-side per-series ownership and backend downstream fan-out exist, but the provider adapter still starts from a static symbol tuple and has no dynamic demand coordinator. Official Databento docs identify Live.unsubscribe() as available from SDK 0.89.0; current requirements permit 0.88, so a dynamic implementation must raise the minimum to at least 0.89 and pin/test an exact version. Gateway acknowledgement/error messages must be observed; a local unsubscribe call alone is not proof of removal. This narrows API uncertainty but does not verify installed runtime or permit paid Databento usage. Provider upstream reference counting remains 🟥 OPEN.  
**Indicator inventory:** 21 calculation test declarations + 7 shared-hook declarations = 28. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation only; CandlestickChart does not call the hook. Footprint PRO 2GD 🟧 synthetic/reference-gated. Volume Profile, Complete Volume Profile, movable-range VP, Heatmap and Liquidation Maps 🟥 not integrated/acceptance incomplete. Aggregate indicator completion ⚪ NOT SCORED.  
**Project:** Stage 1 30/40 = 75% provisional 🟨 (inherited); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 formally closed 🟥; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.  
**External gates:** Gate 25 owner-host transfer/receipt/high-water ACK 🟥 OPEN; Gate 36 public WSS/TLS/runtime 🟥 OPEN; Firebase production E2E 🟥 OPEN; physical browser/Android lifecycle and multi-instance failover 🟥 OPEN; Redis destructive retention 🟧 BLOCKED.  
**Controls:** ZERO COST; main untouched; no Vercel deployment; no destructive Redis operation; APK target approximately 24 December 2026.

---

# Latest verified checkpoint — Batch 62J-235 (25 November 2026)

**Active branch:** phase-2/market-data-foundation  
**Audited documentation HEAD:** 2bd311e1479659c418e5b8623826114f5dfb86f7  
**Unchanged code/test baseline:** bd4904b52d29b3ec456da91014e90922fec35f21  
**Exact audited HEAD CI:** 4/4 terminal SUCCESS — Automated Tests 45521703215; CodeQL 45521703291; OCI ARM64 45521703194; Full Git History Secret Audit 45521703184. All four runs and jobs completed on the exact audited HEAD.  
**Provider-demand finding:** client-side per-series panel/supervisor ownership and backend downstream exact-series fan-out exist, but DatabentoLiveSource subscribes only to a static symbol tuple at startup and exposes no dynamic add/remove API. The SDK range is databento>=0.88,<1 and its adapter source explicitly marks real SDK calls UNVERIFIED. Provider-upstream reference counting/dynamic subscribe-unsubscribe remain 🟥 OPEN. See [Batch 62J-235](WORK_CYCLE_2026-11-25_BATCH62J235_PROVIDER_DEMAND_AND_INDICATOR_GATE.md).  
**Indicator inventory:** 21 calculation test declarations + 7 shared-hook declarations = 28. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation only; CandlestickChart does not call the hook. Footprint PRO 2GD 🟧 synthetic/reference-gated. Volume Profile, Complete Volume Profile, movable-range VP, Heatmap and Liquidation Maps 🟥 not integrated/acceptance incomplete. Aggregate indicator completion ⚪ NOT SCORED.  
**Project:** Stage 1 30/40 = 75% provisional 🟨 (inherited); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 formally closed 🟥; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.  
**External gates:** Gate 25 owner-host transfer/receipt/high-water ACK 🟥 OPEN; Gate 36 public WSS/TLS/runtime 🟥 OPEN; Firebase production E2E 🟥 OPEN; physical browser/Android lifecycle and multi-instance failover 🟥 OPEN; Redis destructive retention 🟧 BLOCKED.  
**Controls:** ZERO COST; main untouched; no Vercel deployment; no destructive Redis operation; APK target approximately 24 December 2026.

---

# Latest verified CI closure — Batch 62J-233 (25 November 2026)

**Active branch:** phase-2/market-data-foundation  
**Code/test SHA:** bd4904b52d29b3ec456da91014e90922fec35f21  
**Code/test CI:** 4/4 terminal SUCCESS on that exact SHA:
- Automated Tests run 45520805106 — 41/41 steps, backend pytest 1,394 passed / 1 skipped / 6 warnings in 66.76s. FIFO non-blocking regression test PASSED.
- CodeQL run 45520805120 — Python 8/8 + JavaScript/TypeScript 8/8 steps.
- OCI ARM64 run 45520805221 — 7/7 steps.
- Full Git History Secret Audit run 45520805267 — 6/6 steps.
All workflows are terminal; no active run remains for the code/test SHA.

**Source change:** POSIX private-key loader now uses O_NOFOLLOW + O_NONBLOCK before fstat; FIFO/device paths cannot block before regular-file validation. Permission error wording reflects the true no-group/world-access invariant.
**Gate 25:** repository-side file boundary hardened. Owner-host custody, authenticated remote snapshot transfer, persisted receipt retrieval from every gateway, restart re-verification, and durable per-gateway high-water ACK remain 🟥 OPEN.
**WebSocket:** Gate 36 public HTTPS/WSS, reverse proxy/TLS, production runtime, Firebase production sign-in/entitlement/revocation E2E and real browser/Android lifecycle/multi-instance acceptance remain 🟥 OPEN. Redis destructive retention remains 🟧 BLOCKED.
**Indicators:** 28 focused indicator declarations = 21 calculation + 7 shared-hook; no new indicator tests or UI integrations in this batch. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 foundation-only; Footprint PRO 2GD 🟧 synthetic/reference-gated; Volume Profile variants, Heatmap and Liquidation Maps 🟥 incomplete/not integrated. Aggregate completion ⚪ NOT SCORED.
**Project:** Stage 1 30/40 = 75% provisional 🟨 (inherited); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 🟥; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.
**Controls:** ZERO COST; main untouched; no Vercel deployment; no destructive Redis action; APK target around 24 December 2026.

---

# Latest verified update — Batch 62J-232 (25 November 2026)

**Branch:** phase-2/market-data-foundation  
**Parent:** 821b3b6602fa2568bf2e103bb725651b1a60de6c  
**Change:** POSIX key loading adds O_NONBLOCK beside O_NOFOLLOW so FIFO/device paths cannot block before fstat rejects non-regular files. Added POSIX FIFO regression test. Permission diagnostic now accurately describes owner-only/no group-world access rather than implying exactly 0600.  
**CI:** pending exact new SHA; parent CI is not inherited.  
**Gate 25:** repository file-open boundary hardened; owner-host custody, authenticated remote transfer, per-gateway receipt retrieval, restart re-verification and durable high-water ACK remain 🟥 OPEN.  
**Indicator inventory:** 28 focused declarations = 21 calculation + 7 shared-hook; FIFO regression is backend security coverage and excluded. SMA20/EMA20/RSI14/MACD/Bollinger/Shared Hook 🟨 foundation; Footprint 🟧 gated; Volume Profile variants/Heatmap/Liquidation Maps 🟥 incomplete/not integrated. Aggregate ⚪ NOT SCORED.  
**Project:** Stage 1 30/40 = 75% provisional 🟨; Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 0/10 🟥; overall ⚪ NOT SCORED; IP3S ⚪ NOT SCORED.  
**Controls:** ZERO COST; main untouched; no Vercel deployment; no destructive Redis action; APK target around 24 December 2026.

---

# Latest indicator reconciliation — Batch 62J-229 (24 November 2026)

**Focused suite inventory:** 28 named test declarations = 21 calculation-engine + 7 shared-hook tests. The count is a source inventory, not a count of completed indicators or a completion percentage. CI is the pass/fail authority.  
**Visible chart integration:** no indicator is yet accepted as a visible chart feature. Calculation/data foundations remain separate from chart renderer, toggle, legend, accessibility, lifecycle and multi-panel acceptance.

| Indicator / subsystem | Calculation/data foundation | Visible chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides absent | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; MACD index 25, signal/histogram index 33 | Pane, lines, histogram and zero guide absent | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay, fill, toggle and latest values absent | 🟨 Foundation |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating and stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated; two owner reference images recorded | 🟧 Gated |
| Volume Profile | Complete production calculation not verified | Not integrated | 🟥 Open |
| Complete Volume Profile | Complete production calculation not verified | Not integrated | 🟥 Open |
| Movable-range VP Tool | Range-selection/calculation lifecycle not verified | Not integrated | 🟥 Open |
| Heatmap | Accepted depth/liquidity engine not verified | Not integrated; reference/data contract gate remains | 🟥 Open |
| Liquidation Maps | Accepted methodology/provenance not verified | Not integrated | 🟥 Open |

**Footprint invariant:** OFF preserves ordinary candlestick layout and normal spacing. Explicit ON alone activates the dedicated spaced-candle/cluster layout. Do not begin visual implementation before the required stage gate, scoped blueprint and user review. Heatmap also remains reference-gated.

**Aggregate indicator completion: ⚪ NOT SCORED.** No approved denominator or weights exist. The 28 test declarations cannot be converted into a percent.
---


# Latest verified update — 24 November 2026 (Batch 62J-229)

**Active branch:** phase-2/market-data-foundation  
**Parent HEAD:** 79f93831bd08d1468b8954d2782970309326d46d  
**Current batch:** hardened owner-host Ed25519 private-key file loading; exact-head CI for the resulting commit must be checked independently.  
**Source/test:** backend/app/snapshot_attestation.py; backend/tests/test_snapshot_attestation.py.  
**Security delta:** key loading now uses a no-follow file descriptor on POSIX, verifies a regular file and service-user ownership, enforces owner-only permissions, and caps PEM input at 64 KiB. Regression coverage rejects symlinks, non-regular paths and oversized files.  
**Gate 25:** repository-side key-file boundary hardened; real owner-host custody, authenticated remote transfer, each gateway's persisted receipt retrieval, restart re-verification and durable per-gateway high-water ACK remain 🟥 OPEN. This patch does not close Gate 25.  
**WebSocket:** Gate 25 🟥 OPEN; Gate 36 public HTTPS/WSS and production runtime 🟥 OPEN; Firebase production sign-in/entitlement/revocation E2E 🟥 OPEN; real browser/Android lifecycle and production multi-instance acceptance 🟥 OPEN. Redis destructive retention remains 🟧 BLOCKED pending every safety prerequisite.  
**Indicator ledger:** 21 calculation tests + 7 shared-hook tests = 28 focused named test declarations. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation-only; Footprint PRO 2GD 🟧 synthetic/reference-gated; Volume Profile, Complete Volume Profile, movable-range VP, Heatmap and Liquidation Maps 🟥 incomplete/not integrated. Aggregate indicator completion remains ⚪ NOT SCORED.  
**Project meters:** Stage 1 = 30/40 criteria = 75% provisional 🟨 (inherited baseline; not rescored by this patch); Stage 2 🟦 active / NOT SCORED; Stage 3 ⬜ NOT SCORED; Stage 4 🟪 gated pending stage gate and reviewed blueprint; Stage 5 ⬜ NOT SCORED; Stage 6 ⬜ NOT SCORED; Gate 10 = 0/10 formally closed 🟥; overall project ⚪ NOT SCORED; IP3S/significant progress ⚪ NOT SCORED.  
**Cost/deployment:** ZERO COST; main untouched; no Vercel deployment; delivery target approximately 24 December 2026 (planning target only).

---

# Latest verified work — 24 November 2026 (Batch 62J-223)

**Active branch:** `phase-2/market-data-foundation`  
**Code/test HEAD:** `92b8ef0936d374f81df6d09e67a4752494100d40`  
**Documentation work-cycle:** [Batch 62J-223](WORK_CYCLE_2026-11-24_BATCH62J223_SHARED_SERIES_OWNER_GUARD_AND_INDICATOR_RECONCILIATION.md)  
**Exact-head CI:** PENDING / NOT YET VERIFIED for the new code/test HEAD; earlier parent results are not inherited.  
**Change:** the shared OHLCV supervisor registry now rejects a same-series owner whose transport endpoint or canonical instrument mapping conflicts with the active supervisor. A regression test covers both mismatch paths and confirms the existing owner remains intact.  
**Changed source/test:** `src/services/ohlcvSeriesSupervisorRegistry.ts`; `src/services/ohlcvSeriesSupervisorRegistry.test.ts`.  
**Indicator ledger:** 17 calculation-engine tests + 7 shared-hook tests = 24 focused named cases. SMA20/EMA20/RSI14/MACD12/26/9/Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps 🟥 not implemented. Visible chart integration remains unimplemented; indicator aggregate remains NOT SCORED.  
**WebSocket:** Gate 25 and Gate 36 remain OPEN; Redis destructive retention remains BLOCKED.  
**Progress:** Stage 1 = 30/40 criteria = 75% provisional 🟨; Stage 2 active engineering but NOT SCORED 🟦; Stages 3–6 NOT SCORED ⬜; Gate 10 = 0/10 formally closed 🟥; overall project NOT SCORED ⚪; IP3S for this batch NOT SCORED ⚪.  
**Cost/deployment:** ZERO COST; `main` untouched; no Vercel deployment; target approximately 24 December 2026 (planning target only).

---

# Latest indicator progress — Batch 62J-212 (24 November 2026)

**Latest source audit HEAD:** `4832f628e5fe616dfe2902be83a8529e540c8ea2`.  
**Detailed current matrix:** [INDICATOR_PROGRESS_2026-11-24_BATCH62J212.md](INDICATOR_PROGRESS_2026-11-24_BATCH62J212.md).

Current state remains: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook are calculation/data foundations only; `CandlestickChart.tsx` does not yet bind the shared hook or render visible study overlays/panes. Standard Volume Profile, Complete Volume Profile, and the separate compact Tools profile have no production implementation verified in the current source tree. Footprint remains synthetic/educational only; Heatmap and Liquidation Maps are not implemented. Low Tier has 15 planned slots but its exact final list is not approved; Mid Tier has Volume Profile plus approximately ten pending studies; Exclusive Indicator Pro contains Footprint PRO 2GD, Heatmap, Liquidation Maps, and Complete Volume Profile.

The two owner-supplied Footprint references remain saved in ChatGPT Saved Reference Images and are not binary assets committed to Git. Footprint OFF must preserve normal candlesticks and spacing; Footprint ON alone may activate spaced candle clusters. No visual implementation is authorized before its scoped blueprint and owner review.

The focused indicator suites still contain 24 named tests (17 calculation + 7 shared-hook). Aggregate indicator progress remains **NOT SCORED** because no denominator or weights have been approved. Stage 1 remains 30/40 = 75% provisional; overall project remains NOT SCORED. ZERO COST.

---

## Owner Footprint visual reference intake — Batch 62J-206 (24 November 2026)

**Owner reference images received:** 2/2 and saved in the persistent Reference Images collection as:
- `Footprint Indicator Reference 1`
- `Footprint Indicator Reference 2`

Both images show a dark footprint chart: green positive and red negative bid/ask-style volume cells aligned to price levels; numeric volume labels; horizontal bars whose lengths communicate relative magnitude; candle-adjacent volume ladders; highlighted price rows; and separated candle clusters. A violet accent is also visible in the supplied references; its semantic meaning is intentionally unspecified pending owner review.

**Visual contract captured from the supplied references (draft, not implementation authorization):**
1. Preserve the existing ordinary candlestick layout and ordinary candle spacing whenever Footprint is OFF.
2. Only explicit Footprint ON may activate a dedicated footprint/cluster layout with additional horizontal space between candles and adjacent price-level volume cells.
3. Render price-level rows in a vertically aligned ladder, with readable numeric labels and proportional horizontal volume bars.
4. Use distinct positive/negative visual treatment (reference green/red), retain dark panel styling, and preserve highlighted price-row treatment.
5. Do not infer the meaning of violet marks, highlighted rows, or any market statistic from appearance alone. Their data semantics require a separately reviewed contract.
6. Keep all displayed footprint values explicitly SIMULATED until a validated exchange-native bid/ask source and classification contract exist. The current educational aggregation engine is not evidence of real order-flow data.
7. The two images are visual references only; they do not establish a data provider, aggressor classification, tick size, aggregation interval, POC/VAH/VAL semantics, or trading interpretation.

**Gate and roadmap boundary:** Owner references are now supplied, so the prior missing-reference prerequisite is cleared. The existing indicator/Footprint visual implementation remains parked: official project stage is still Stage 1, and the existing Stage 4/Footprint blueprint review and approval gates remain in force. No visual implementation, chart-layout change, dependency, provider, paid service, or production claim is authorized by this intake. The next allowed action is preparation of a scoped Footprint blueprint for owner review when its roadmap gate is reached.

**Progress accounting:** reference intake/documentation only; no indicator implementation credit; no Stage 1 acceptance tick; indicator aggregate remains NOT SCORED. ZERO COST; `main` untouched.

## Latest indicator checkpoint — Batch 62J-204 (24 November 2026)

**Source/test checkpoint:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Documentation parent:** `4eef1fe3547d70257a39e00e9d4f49934dc3db2a`  
**Indicator code delta:** none. This batch reconciles the current source, exact test inventory, visible chart integration state, and progress records; it does not award implementation credit.

The two indicator-specific suites contain **24 named tests**: 17 calculation-engine tests and 7 shared-hook tests. The count was obtained from the current `it()` declarations in `src/indicators/indicatorCalculations.test.ts` and `src/indicators/useMarketIndicators.test.ts`. It is a focused indicator-suite count, not the total frontend test count and not proof that production chart acceptance has passed.

| Study / subsystem | Verified calculation or data foundation | First valid source index | Visible chart acceptance | Status |
|---|---|---:|---|---|
| SMA 20 | Rolling 20-close arithmetic mean with overflow-resistant normalized summation | 19 | Overlay, toggle, legend/latest value, identity clearing and lifecycle not integrated | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; multiplier `2/21` | 19 | Overlay, toggle, legend/latest value, identity clearing and lifecycle not integrated | 🟨 Foundation |
| RSI 14 (Wilder) | Seed from first 14 close-to-close changes, then Wilder recurrence; explicit flat/rising/falling edge handling | 14 | Dedicated 0–100 pane, 30/70 guides, toggle and legend not integrated | 🟨 Foundation |
| MACD 12/26/9 | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | Dedicated pane, lines, histogram, zero guide, toggle and legend not integrated | 🟨 Foundation |
| Bollinger 20,2 | 20-close mean ± 2 population standard deviations | 19 | Upper/middle/lower bands, fill, toggle and latest values not integrated | 🟨 Foundation |
| Shared indicator hook | Exact keyed immutable backend snapshot; shared WeakMap calculation cache per snapshot object; non-backend/untrusted states suppress output | Per study | Hook is not imported or called by `CandlestickChart.tsx` | 🟨 Foundation |
| Footprint | Deterministic synthetic/offline aggregation fixtures only; not exchange-native bid/ask truth | N/A | Visual work requires owner reference image(s) and reviewed blueprint; OFF keeps normal candles, ON alone uses spaced clusters | 🟧 Gated |
| Heatmap | No accepted depth/liquidity renderer verified | N/A | Not implemented; owner reference and validated depth contract required | 🟥 Open |
| Liquidation Maps | No accepted calculation/runtime renderer verified | N/A | Not implemented; data provenance and reviewed blueprint required | 🟥 Open |

### Exact indicator test inventory

**Calculation engine — 17 tests**
1. SMA/EMA source alignment and warm-up nulls.
2. Wilder RSI flat and rising edge cases.
3. MACD signal warm-up separation.
4. Bollinger population standard deviation.
5. Shared multi-indicator calculation entry point.
6. All shared calculations across supported chart timeframes.
7. Invalid periods and non-finite values.
8. Prefix causality (future candles cannot change earlier outputs).
9. Falling-only RSI and period-one moving averages.
10. Fail-closed handling of infinite results from finite extreme inputs.
11. RSI stability for very large finite gain/loss magnitudes.
12. Overflow-resistant representable SMA means.
13. Finite Bollinger deviation for large same-sign prices.
14. Preservation of small residuals between large cancelling SMA inputs.
15. Preservation of small residuals in the Bollinger middle band.
16. Wilder RSI seed and recursive smoothing on alternating gains/losses.
17. Rejection of non-finite close values at the shared calculation boundary.

**Shared hook — 7 tests**
1. No indicator output without a selected backend series.
2. Calculation from the exact selected keyed snapshot.
3. Recalculation from a new immutable snapshot revision after a live update.
4. Isolation of simultaneous panels by canonical series.
5. One frozen calculation result shared across panels on the same snapshot revision.
6. Degraded backend data retained while demo/error snapshots are suppressed.
7. Indicator output cleared when the selected series becomes unavailable.

### Numerical and lifecycle invariants verified in source/tests

- Outputs preserve source-candle indexing; warm-up slots remain `null`.
- SMA20/EMA20/Bollinger20 first become valid at index 19; RSI14 at index 14; MACD line at index 25 and signal/histogram at index 33.
- Prefix-causality tests compare every study's prefix output with the corresponding prefix of the full series.
- Invalid periods and non-finite input are rejected; numerical kernels include large-magnitude/cancellation regression cases.
- The hook calculates only for exact canonical-series snapshots in backend `ready` or `degraded` state; demo/loading/unavailable/error states do not expose indicator output.
- Immutable snapshot identity is used for shared calculation caching; calculated arrays/points are frozen before publication.

### Integration boundary — still red

`CandlestickChart.tsx` currently imports `useMarketDataSeriesSnapshot`, not `useMarketIndicators`, and creates a single `CandlestickSeries`. Consequently, none of SMA/EMA/RSI/MACD/Bollinger is yet a visible, user-toggleable chart feature. No progress credit is awarded for UI integration, accessibility, settings persistence, multi-panel rendering, resize/lifecycle behavior, or production performance until implemented and tested.

Footprint and Heatmap visual work remain gated on owner-provided reference images and a scoped blueprint review. No speculative indicator UI, new dependency, paid provider, hosting, or deployment is introduced in this batch.

**Indicator aggregate progress: NOT SCORED.** There is no approved per-study weighting or acceptance denominator. The 24 focused tests are evidence of calculation/hook foundations, not a completion percentage.


---

# Historical indicator checkpoint — 24 November 2026 (Batch 62J-199)

**Branch:** `phase-2/market-data-foundation`  
**Verified source/test HEAD:** `23bf2da93ec8b4c935d2898a993f4d1c80ce9a7d`.  
**Documentation HEAD:** `3e6572658ab47836023d44e70efc02f704639ca2`; its exact-head CI also completed 4/4 SUCCESS.  
**Batch report:** [Batch 62J-199](WORK_CYCLE_2026-11-24_BATCH62J199_REDIS_ACL_DESTRUCTIVE_BOUNDARY_AND_INDICATOR_AUDIT.md).  
**Indicator implementation delta:** none. Batch 62J-199 hardens Redis destructive-command ACL regression tests and updates evidence documentation only; it changes no indicator formula, numeric kernel, shared hook calculation, chart binding, renderer, pane, toggle, legend or indicator-specific test. **Indicator credit: zero.**

| Indicator / subsystem | Status | Verified foundation | First valid index | Remaining acceptance |
|---|---|---|---:|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of the latest 20 closes | 19 | Candlestick overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; multiplier 2/21 | 19 | Overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change average then Wilder-smoothed gain/loss recurrence | 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | Pane, lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations | 19 | Upper/middle/lower overlay, toggle, latest values, identity clearing, lifecycle, render/performance |
| Shared Indicator Hook | 🟨 Foundation | Immutable canonical-series snapshot; shared calculation cache per snapshot revision; backend trust-state gate | Per study | Actual chart binding, stale clearing on identity/timeframe changes, settings, legend, accessibility and performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | N/A | Owner reference image, reviewed blueprint, verified bid/ask contract, spaced-cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | N/A | Owner reference image, validated depth contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted calculation/runtime renderer | N/A | Defensible data provenance/calculation contract, blueprint, renderer and tests |

**Test evidence on the verified source/test HEAD:**
- `indicatorCalculations.test.ts`: 17 tests — warm-up alignment, SMA/EMA, Wilder RSI, MACD warm-up, population deviation, timeframe alignment, invalid/non-finite input, prefix causality and numerical stability.
- `useMarketIndicators.test.ts`: 7 tests — backend-only data, exact keyed snapshots, immutable revision recalculation, canonical-series isolation, shared frozen results, degraded/demo/error trust states and unavailable clearing.
- Full frontend CI: 320 tests passed across 34 files.
- Full backend CI: 1,359 passed, 1 skipped, 6 non-failing warnings.
- The visible `CandlestickChart` still creates only the candlestick series; the shared indicator hook is not yet connected to overlays or oscillator panes.

**Invariants:** warm-up stays null; output aligns to source candle indexes/timestamps; prefix causality prevents future-candle repaint; invalid/gapped input is rejected; stale values clear on identity/timeframe changes. Footprint OFF preserves ordinary candle spacing; only explicit ON enables the spaced cluster layout. Footprint/Heatmap visuals remain blocked on owner reference images and scoped blueprint review.

**Aggregate indicator progress: NOT SCORED.** No approved per-study weights or acceptance denominator exist. Visible indicator work remains parked for official Stage 4.

---

# Latest indicator checkpoint — 24 November 2026 (Batch 62J-190)

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `8606cb460f641b0b831081aeed8aae6a6149c91d`.  
**Indicator implementation delta:** none. Batches 62J-189/190 harden WebSocket replay and reconnect continuity; they change no indicator formula, numeric kernel, hook calculation, chart binding, renderer, pane, toggle, legend or indicator-specific test. **Indicator credit: zero.** Exact-HEAD CI is 5/5 SUCCESS; frontend 320 tests passed, backend 1,348 passed, 1 skipped, 6 non-failing warnings.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity clearing, lifecycle, render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot; aligned multi-study calculation; trust-state and immutable-revision regression coverage | Actual chart binding, stale clearing across identity changes, settings/legend, accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | Owner reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible provenance/calculation contract, blueprint, renderer and tests |

**Aggregate indicator progress: NOT SCORED.** Study weights and acceptance denominator remain unapproved. Preserve warm-up nulls, exact candle-index alignment, prefix causality/no future repaint, invalid/gapped-input rejection and stale-output clearing on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual implementation remains gated on owner reference images and scoped blueprint review.

---

# Latest indicator checkpoint — 24 November 2026 (Batch 62J-189)

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `713449822022e555b6fe98964952814b012f3520`.  
**Batch report:** [Batch 62J-189](WORK_CYCLE_2026-11-24_BATCH62J189_REPLAY_CHECKPOINT_FLOOR_INTEGRITY.md).  
**Indicator implementation delta:** none. The batch hardens WebSocket replay continuity; it changes no indicator formula, calculation kernel, hook, chart binding, renderer, pane, toggle, legend, or indicator-specific test. **Indicator credit: zero.** Exact-HEAD Automated Tests remained RUNNING at report creation; CodeQL, OCI ARM64 and Secret Audit were SUCCESS.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; immutable revision regression | Candlestick overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity clearing, lifecycle, render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity clearing, lifecycle, render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot; aligned multi-study calculation; trust-state and immutable-revision regression coverage | Actual chart binding, stale clearing across identity changes, settings/legend, accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | Owner reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible provenance/calculation contract, blueprint, renderer and tests |

**Aggregate indicator progress: NOT SCORED.** Study weights and acceptance denominator remain unapproved. Preserve warm-up nulls, exact candle-index alignment, prefix causality/no future repaint, invalid/gapped-input rejection and stale-output clearing on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual implementation remains gated on owner reference images and scoped blueprint review.

---

# Latest indicator checkpoint — 24 November 2026 (Batch 62J-188)

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `22c9ab4a0e97383520670a9af42a2f9ef35f6d62`.  
**Exact-HEAD CI:** five workflows SUCCESS; Automated Tests 319/319 frontend tests across 34 files and 1,347 backend tests passed (1 skipped, 6 non-failing warnings). See [Batch 62J-188 report](WORK_CYCLE_2026-11-24_BATCH62J188_WEBSOCKET_RESNAPSHOT_CURSOR_INTEGRITY.md).  
**Indicator formula/renderer/UI changes in Batch 62J-188:** none. This batch fixes WebSocket resnapshot cursor continuity only.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; immutable revision recalculation regression | Candlestick overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, lines, histogram, zero guide, toggle, legend and lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot; trust-boundary and immutable revision regression coverage | Actual chart binding, stale clearing across all identity changes, settings/legend, accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | Owner reference image(s), reviewed blueprint, valid bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible provenance/calculation contract, blueprint, renderer and tests |

**Aggregate indicator progress: NOT SCORED.** Study weights and acceptance denominator are not approved. Keep warm-up nulls, exact candle-index alignment, prefix causality/no future repaint, invalid/gapped-input rejection, and stale-output clearing on identity changes. Footprint OFF retains standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visuals remain gated on owner reference images and scoped blueprint review.

---

# Latest indicator checkpoint — 24 November 2026 (Batch 62J-187)

**Branch:** `phase-2/market-data-foundation`  
**Latest source HEAD:** `1b3f39ea8f3a6cfd56425fc799b58ee8e0d0991b`.  
**Exact-HEAD CI:** five workflows SUCCESS on the same source HEAD; Automated Tests [45215527228](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527228), CodeQL [45215526929](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526929), OCI ARM64 [45215526908](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526908), Android APK [45215527101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215527101), Secret Audit [45215526995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45215526995).
**Indicator formula/renderer/UI changes in this source commit:** none. The latest source change is a scoped package.json Miniflare undici dependency override only.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; immutable revision recalculation regression | Candlestick overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Pane, lines, histogram, zero guide, toggle, legend and lifecycle/render |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot; trust-boundary and immutable revision regression coverage | Actual chart binding, stale clearing across all identity changes, settings/legend, accessibility/performance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask truth | Owner reference image(s), reviewed blueprint, valid bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible provenance/calculation contract, blueprint, renderer and tests |

**Aggregate indicator progress: NOT SCORED.** Study weights and acceptance denominator are not approved. Keep warm-up nulls, exact candle-index alignment, prefix causality/no future repaint, invalid/gapped-input rejection, and stale-output clearing on identity changes. Footprint OFF retains standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visuals remain gated on owner reference images and scoped blueprint review.

**Recent regression evidence:** Batch 62J-185 covers backend trust-state transitions (ready/degraded accepted; demo/error suppressed with stale clearing). Batch 62J-186 covers recalculation after an immutable live-snapshot revision. Prior exact-head frontend suite: 315/315 across 34 files. These are test-evidence improvements, not visible-feature completion.

**Full cycle report:** [Batch 62J-187](WORK_CYCLE_2026-11-24_BATCH62J187_EXACT_HEAD_CI_APK_INDICATOR_RECONCILIATION.md).

---

# Latest indicator checkpoint — 23 November 2026

**Branch:** `phase-2/market-data-foundation`  
**Latest source/test HEAD:** `d2057e9997b50cb6aab04258fd90de37d35a6816`.  
**Exact-HEAD CI:** all four workflows SUCCESS on `4a87b90e08da04cd22faf74d578a5ce2f2734c15`; frontend 315/315 across 34 files.  
**Indicator formula/renderer/UI changes:** none. Two hook regressions improve acceptance evidence only.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; rolling result recalculated after a new immutable snapshot revision | Candlestick overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Exact backend snapshot; aligned multi-study output; frozen result shared by panels on same snapshot; ready/degraded accepted, demo/error suppressed; immutable revision recalculation regression | Actual chart binding, stale clearing across all identity changes, settings/legend integration, lifecycle/accessibility/performance acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/calculation contract, reviewed blueprint, renderer and tests |

**Mandatory invariants:** warm-up outputs remain null; exact source-candle index alignment; prefix causality/no future repaint; reject invalid/non-finite/gapped input; clear stale output on symbol, venue, dataset, chart identity, or timeframe changes. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters. Footprint and Heatmap visual implementation remains blocked until the owner supplies reference image(s) and reviews the scoped blueprint.

**Aggregate indicator progress:** **NOT SCORED**. Study weights and denominator have not been approved; no combined percentage is invented.

---

# CURRENT INDICATOR LEDGER — Batch 62J-177 (23 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Latest code/test HEAD:** `264b54fbb87b96133d13dd7f82089bde4cd9d47f`  
**Indicator source/formula changes:** none. **Indicator renderer/UI changes:** none.  
**Reason for reconciliation:** synthetic-only WebSocket cursor integrity work does not earn indicator implementation credit.

## Current complete indicator status

| Study / subsystem | Status | Mathematical/data foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of 20 closes; first valid index 19 | Candlestick overlay, visibility toggle, legend/current value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/current value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial mean of 14 close-to-close changes; Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero line, toggle/legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Exact-snapshot aligned multi-study output; null outside backend ready/degraded | Hook tests, chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Synthetic prototype only | Educational synthetic accumulator; not exchange-native bid/ask volume | User visual reference(s), reviewed blueprint, verified data contract, cluster layout and renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User visual reference(s), reviewed blueprint, validated data contract, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render/data contract | Defensible provenance/methodology, reviewed blueprint, renderer and tests |

## Mathematical and rendering invariants

1. Warm-up outputs remain `null`, never zero.
2. Every output remains aligned to the exact source-candle index.
3. Prefix causality: appending future candles cannot change any prior output.
4. Invalid/non-finite bars and gaps are not silently converted to zero.
5. Stale outputs clear when symbol, venue, dataset, chart identity or timeframe changes.
6. No future-candle leakage or repainting.
7. Calculation, rendering, interaction, lifecycle, accessibility and performance are separate acceptance dimensions.
8. Footprint OFF preserves ordinary candle spacing; only explicit ON activates the dedicated spaced-cluster layout.
9. Footprint and Heatmap visual implementation remains blocked until the user supplies reference image(s) and reviews a scoped blueprint.
10. Aggregate indicator completion remains **NOT SCORED** because per-study weights and denominator are not approved.

**Batch 62J-177 decision:** all indicator statuses remain unchanged. No percentage or implementation credit is awarded from WebSocket cursor hardening. Full technical cycle evidence: `docs/WORK_CYCLE_2026-11-23_BATCH62J177_SYNTHETIC_WEBSOCKET_CURSOR_INTEGRITY.md`.

---

# CURRENT INDICATOR LEDGER — Batch 62J-148 (22 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Test source commit:** `79d88d9aa5261dde3f2e31d1e742d45f461e43c2`  
**Runtime formula changes:** none. **Visual/UI implementation changes:** none.

## New regression coverage

`src/indicators/indicatorCalculations.test.ts` now verifies:
1. Wilder RSI period-2 seed and recurrence on `[1, 2, 1, 2, 1]`, with exact aligned output `[null, null, 50, 75, 37.5]`.
2. `calculateIndicators` rejects a non-finite close at source bar index 7 with the explicit error `Bar 7 has a non-finite close value.`

These are test-coverage improvements only. They do not promote any study to chart-rendered or user-configurable status. Acceptance credit remains pending exact-HEAD CI.

## Complete indicator status

| Study / subsystem | Status | Mathematical / data foundation | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, visibility toggle, legend/current value, identity/lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Overlay, toggle, legend/current value, identity/lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean; Wilder recurrence; first valid index 14; mixed gain/loss regression added | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero line, toggle/legend/latest values, lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/lifecycle/render/performance tests |
| Shared Indicator Hook | 🟨 Foundation | Exact market-data snapshot; null outside backend ready/degraded; aligned multi-study output | Hook tests, actual chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask volume | User reference image(s), reviewed blueprint, verified bid/ask data, cluster layout and renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), verified order-book/depth contract, blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted data/renderer contract | Defensible liquidation source/provenance, calculation methodology, blueprint, renderer and tests |

## Shared mathematical and rendering invariants

- Warm-up remains `null`, never zero.
- Values remain aligned to the exact source candle index.
- Prefix-causal: adding future candles cannot alter prior output.
- Non-finite or invalid bars are rejected; gaps are not silently converted to zero.
- Clear stale study outputs when symbol, venue, dataset, chart identity or timeframe changes.
- No repaint using future candles.
- Chart display, toggles, legends, values, lifecycle, accessibility and performance must each be tested.
- Footprint OFF keeps ordinary candle spacing; explicit ON alone activates the spaced cluster layout.
- Footprint/Heatmap visuals require user reference image(s) and scoped blueprint review.
- No aggregate indicator completion percentage until per-study weights and denominator are approved.

**Indicator completion:** NOT SCORED as an aggregate. Status colors are evidence states, not percentages.

---

## Batch 62J-147 reconciliation — 22 November 2026

- No indicator source, formula, calculation test, hook, chart renderer or UI was changed.
- All indicator implementation statuses remain unchanged: SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 (synthetic/reference-gated), Heatmap 🟥, Liquidation Maps 🟥.
- The detailed formula, first-valid-index, numerical safety, prefix-causality, chart-integration and visual acceptance matrix remains in `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md`. This ledger must not reduce those acceptance requirements to a generic "foundation" label.
- On-demand market-data architecture is Stage 2 and gives no indicator implementation credit. Stage 4 visual implementation remains subject to the approved roadmap and visual-reference gates.
- Aggregate indicator completion remains NOT SCORED because per-study weights and a denominator are not approved.

# CURRENT INDICATOR LEDGER — Batch 62J-146 (22 November 2026)

Repository audit baseline: `06a3c3c9e5b5ecd2ff4c8c29e0e472972c1c6e7e` on `phase-2/market-data-foundation`.
Documentation addition: `docs/ADR_ON_DEMAND_MARKET_DATA_SUBSCRIPTIONS.md`.
No indicator formula, calculation kernel, shared hook, renderer, chart UI or indicator test source changed in this batch. On-demand market-data architecture documentation and WebSocket authentication tests earn **zero indicator implementation credit**.

## Complete indicator status

| Indicator/component | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | Flat/monotonic/zero-loss edge cases, chart integration and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Numerical edge cases, chart integration, identity invalidation and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Variance/flat-series edge cases, chart integration and lifecycle |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output | Full chart integration, visible settings/legend/current values and stale-output clearing |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, licensed bid/ask data contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime/render implementation | User reference image(s), reviewed blueprint, validated depth/liquidity data contract and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/contract, reviewed design, renderer and tests |

## Mathematical and data-integrity invariants

1. Warm-up outputs remain null, never fabricated zero.
2. Every output remains aligned to the originating candle index.
3. Prefix causality: appending future candles cannot alter earlier indicator outputs.
4. Invalid, missing or gapped bars are never silently converted to zero.
5. Stale outputs clear on symbol, venue, dataset, chart and timeframe identity changes.
6. Calculation, rendering, interaction, lifecycle, accessibility and performance are separate acceptance dimensions.
7. Footprint OFF preserves ordinary candle spacing; only explicit ON activates the dedicated spaced-cluster layout.
8. Footprint and Heatmap visual implementation remains blocked until the user supplies reference image(s) and reviews the scoped blueprint.
9. Aggregate indicator completion remains **NOT SCORED** because weights and denominator are unapproved.

## Project accounting

- Stage 1: 30/40 = 75% provisional.
- Stage 2–6: NOT SCORED / not officially opened.
- Gate 10: 0/10 external criteria formally closed.
- Overall project: NOT SCORED; approved six-stage weights and denominator do not exist.
- This cycle awards zero indicator implementation credit.

---

# CURRENT INDICATOR LEDGER — Batch 62J-143 (22 November 2026)

No indicator formula, calculation kernel, shared hook, renderer, UI or indicator-specific test changed in Batch 62J-143. Google-only authentication UI and foreground WebSocket lifecycle work earns **zero indicator implementation credit**.

| Indicator/component | Status | Verified foundation and remaining work |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; numeric edge cases, chart integration, lifecycle and performance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; first valid index 19; numeric edge cases, chart integration, lifecycle and performance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; flat/monotonic/zero-loss cases and chart integration remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; edge cases and chart integration remain |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; variance edge cases and chart integration remain |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; full chart integration and identity invalidation remain |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth; reference image(s) and reviewed blueprint required before visuals |
| Heatmap | 🟥 Not implemented | Reference image(s), validated data contract and reviewed blueprint required before visuals |
| Liquidation Maps | 🟥 Not implemented | No accepted implementation; data provenance, data contract and renderer remain |

## Shared technical acceptance invariants

1. Warm-up values remain null, never zero.
2. Every output remains aligned to the originating candle index.
3. Prefix causality: appending future candles cannot alter prior outputs.
4. Invalid, missing or gapped bars are never silently converted to zero.
5. Stale outputs clear on symbol, venue, dataset, chart and timeframe identity changes.
6. Calculation, rendering, interaction, lifecycle and performance are separate acceptance dimensions.
7. Footprint OFF preserves standard candle spacing; only explicit ON activates the dedicated spaced-cluster layout.
8. Footprint and Heatmap visual implementation is blocked until user reference image(s) are supplied and the scoped blueprint is reviewed.
9. Aggregate indicator completion remains **NOT SCORED** because weights and denominator are unapproved.

## Project and acceptance context

Stage 1 = 30/40 = 75% provisional. Stages 2–6 are NOT SCORED/not officially opened. Gate 10 = 0/10 external criteria formally closed. Overall project = NOT SCORED. Batch 62J-143 did not change indicator implementation. Exact-HEAD CI is pending on source HEAD `bd83d40bdf58262922462d67cde3da6c1f4a4387`; IPS35 remains pending.

Full cycle: [WORK_CYCLE_2026-11-22_BATCH62J143_GOOGLE_ONLY_FOREGROUND_WEBSOCKET.md](WORK_CYCLE_2026-11-22_BATCH62J143_GOOGLE_ONLY_FOREGROUND_WEBSOCKET.md).

---

# CURRENT INDICATOR LEDGER — Batch 62J-142 (22 November 2026)

This snapshot supersedes earlier dated summaries below.

No indicator formula, calculation source, hook, renderer, UI or indicator test changed in Batch 62J-142. Hosting evaluation and documentation updates earn **zero technical-indicator implementation credit**.

| Indicator/component | Status | Verified foundation and remaining work |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; chart integration and edge-case acceptance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; first valid index 19; chart integration and edge-case acceptance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; numerical edge cases and chart integration remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; chart integration remains |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19; chart integration remains |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; full chart integration remains |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth; user reference image(s) and reviewed blueprint required before visuals |
| Heatmap | 🟥 Not implemented | User reference image(s), validated data contract and reviewed blueprint required before visuals |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence; data contract and renderer remain |

## Shared technical acceptance invariants

1. Warm-up values remain null, never zero.
2. Every output remains aligned to the originating candle index.
3. Prefix causality: appending future candles cannot alter previously computed indicator values.
4. Invalid, missing or gapped bars are never silently converted to zero.
5. Stale outputs clear on symbol, venue, dataset, chart and timeframe identity changes.
6. Calculation, chart rendering, interaction, lifecycle and performance are separate acceptance dimensions.
7. Footprint OFF preserves standard candle spacing; only explicit ON activates the dedicated spaced-cluster layout.
8. Footprint and Heatmap visual implementation is blocked until user reference image(s) are supplied and the scoped blueprint is reviewed.
9. Aggregate indicator completion remains **NOT SCORED** because weights and denominator are unapproved.

## Project context

Stage 1 = 30/40 = 75% provisional. Stages 2–6 are NOT SCORED/not officially opened. Gate 10 = 0/10 external criteria formally closed. Overall project = NOT SCORED. Exact-HEAD Automated Tests, CodeQL, Secret Audit and OCI ARM64 readiness all passed on starting HEAD `ad3fa4413cdc827d49e6ec05731f0cd90360c75d`; documentation commit `ddc3d169359bab366fbcede6bee6dd64b1552181` requires its own CI run. IPS35 remains pending.

Full cycle: [WORK_CYCLE_2026-11-22_BATCH62J142_ZERO_COST_WEBSOCKET_HOSTING_OPTIONS.md](WORK_CYCLE_2026-11-22_BATCH62J142_ZERO_COST_WEBSOCKET_HOSTING_OPTIONS.md).

---

# CURRENT INDICATOR LEDGER — Batch 62J-141 (22 November 2026)

This section supersedes earlier dated snapshots below when reporting the latest state.

No indicator formula, hook, renderer, UI or indicator test source changed in Batch 62J-141. WebSocket supervisor ownership and OCI ARM64 readiness work earns **zero technical-indicator implementation credit**.

| Indicator/component | Status | Verified foundation and remaining work |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; chart integration and edge-case acceptance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; first valid index 19; chart integration and edge-case acceptance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; numerical edge cases and chart integration remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; chart integration remains |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19; chart integration remains |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; full chart integration remains |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth; reference image(s) and reviewed blueprint required before visuals |
| Heatmap | 🟥 Not implemented | Reference image(s), validated data contract and reviewed blueprint required before visuals |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence; data contract and renderer remain |

Shared invariants: warm-up nulls; candle-index alignment; prefix causality/no future repaint; invalid/gapped bars never silently converted to zero; stale output cleared on symbol/venue/dataset/chart/timeframe changes; calculation, rendering, interaction, lifecycle and performance are distinct acceptance dimensions. Footprint OFF preserves standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visuals require user references and reviewed blueprints.

Aggregate technical-indicator percentage: **NOT SCORED** because weights and denominator are unapproved.

Project stage context: Stage 1 = 30/40 = 75% provisional; Stage 2–6 NOT SCORED/not officially opened; Gate 10 = 0/10 external criteria formally closed; overall project NOT SCORED. IPS35 final score pending exact documentation-HEAD CI; native ARM64 image/runtime smoke acceptance passed in run 45000816460.

Full cycle: [WORK_CYCLE_2026-11-22_BATCH62J141_WEBSOCKET_SUPERVISOR_OCI_ARM64.md](WORK_CYCLE_2026-11-22_BATCH62J141_WEBSOCKET_SUPERVISOR_OCI_ARM64.md).

---

# Batch 62J-135 — Gate 25 source audit, exact-head CI acceptance and IP3S reconciliation
Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Starting HEAD: `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`
Scope: documentation and acceptance design only; no runtime/schema/test source changes.

## Verified repository and CI state

Branch ref was verified at starting HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`; `main` was not touched.

Exact-HEAD workflows at the time of this final documentation update:
- Automated Tests [44991805066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805066): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- CodeQL [44991805111](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991805111): **SUCCESS**, exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b`.
- Full Git History Secret Audit [44992252234](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992252234): **SUCCESS** on the final documentation HEAD when checked.
- Automated Tests [44992252218](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992252218): **IN PROGRESS** on the final documentation HEAD at report finalization.
- CodeQL [44992252244](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44992252244): **PENDING** on the final documentation HEAD at report finalization.
- Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **SUCCESS** on source/test commit `ecf7decb8e823effe09a6be8a9973bb98619ae92`; this is CI debug-build evidence, not a production release and not a build on the later docs-only HEAD.

The exact-HEAD Automated Tests job completed successfully. The workflow job's completed steps include frontend dependency audit/unit tests/build, backend dependency installation/tests, isolated Redis TLS CA/hostname enforcement fixture, bounded synthetic SQLite outbox and metrics checks, backend container build/smoke, vulnerability scan/report and dependency audit enforcement. Earlier exact HEAD `7920c591a07e32c7af6c07dc1aa9af6216fdf19b` had Automated Tests, CodeQL and Secret Audit SUCCESS. After this batch's docs-only commits, only Secret Audit had completed on the final documentation HEAD; Automated Tests and CodeQL remained pending/in progress. CI success does not prove owner-host Redis persistence/failover or public WSS.

## Gate 25 — source-backed installation receipt audit

Files inspected at the starting HEAD:
- `backend/app/ohlcv_store.py`
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_replica_bridge.py`
- `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`

Confirmed behavior:
1. `SQLiteOhlcvReplicaStore.install_global_snapshot()` preflights the snapshot, then opens a write transaction, re-reads the snapshot and validates its manifest/content while inserting rows. Snapshot replacement and checkpoint update commit or roll back together.
2. The replica checkpoint persists source ID, replica ID, applied cursor, snapshot generation, retention metadata and schema/protocol versions. It does not persist the snapshot SHA-256 or an immutable installation receipt.
3. `build_gateway_replica_runtime_factory()` checks installer status, source ID, generation, high-water cursor, digest syntax and checkpoint alignment before creating the Redis client. The digest is returned as runtime `snapshot_evidence`; the code does not compare it to a durable receipt because no such receipt is currently stored.
4. Source-side `_validate_snapshot_evidence()` validates the snapshot manifest and requires a matching receipt for each configured gateway, including source, stream, generation, cursor and SHA-256. The callback is explicitly responsible for authenticating/reading those owner-host receipts. This validator does not itself contact or authenticate remote gateways.
5. Existing tests prove snapshot-before-Redis construction, source mismatch rejection, unverified installer rejection, production plaintext Redis rejection, and cleanup on consumer-construction failure. They do not prove durable gateway receipt persistence, signature verification, immutable receipt conflict semantics, crash/restart receipt consistency, or owner-host custody.

### Gate 25 status: OPEN

The missing feature is not simply a hash column. The acceptance contract must bind:
- authenticated authoritative source identity;
- exact snapshot generation, high-water cursor and canonical digest;
- replica identity and receipt schema;
- authenticated installer/attestation identity;
- durable immutable receipt history;
- atomicity between snapshot rows, checkpoint replacement and receipt insertion.

A SHA-256 digest establishes content identity only when compared against a trusted value. It does not independently establish who supplied the snapshot.

### Required implementation acceptance matrix (design only)

| Case | Expected result |
|---|---|
| Valid authenticated manifest and matching content | Install and persist receipt atomically |
| Altered bytes or recomputed digest mismatch | Reject; preserve prior rows/checkpoint/receipts |
| Unknown signer, wrong key or invalid signature | Reject before accepting snapshot |
| Source or replica identity mismatch | Reject |
| Same source/replica/generation and same digest | Idempotent; preserve original receipt |
| Same generation with different digest | Hard conflict; fail closed |
| New generation with valid cursor progression | Add a new immutable receipt |
| Failure before transaction commit | No partial snapshot/checkpoint/receipt state |
| Process interruption around commit then restart | Recover to either prior complete state or new complete state |
| Legacy checkpoint without receipt | Mark LEGACY_UNATTESTED; never fabricate provenance |
| Normal event cursor advancement | Preserve historical installation receipt |
| Repeated migration/rollback | Idempotent and backward-compatible; never downgrade verified provenance |

### Recommended implementation sequence — no implementation performed

1. Approve the trust model: owner-pinned public key and signed manifest, or equivalent authenticated owner-controlled transfer. Decide signature format, key ID, rotation and revocation policy.
2. Define immutable receipt schema and uniqueness key `(source_id, replica_id, generation_id)`; define explicit legacy state and retention/archival policy.
3. Add transactional receipt insertion to the same SQLite transaction as snapshot rows/checkpoint replacement.
4. Add read-only receipt query and bind gateway runtime evidence to the persisted receipt, not only the installer return value.
5. Make source-side verification consume authenticated receipt records with explicit gateway identity and custody.
6. Add failure-injection tests for tampering, signer/key errors, generation conflicts, transaction rollback, process termination, restart, migration and retention.
7. Re-run full CI on exact branch HEAD. Owner-host transfer, key custody, Redis persistence/restart/failover remain separately required external acceptance.

No runtime/schema implementation was started because the ADR is design-only and the trust/key lifecycle decisions are not yet approved.

## WebSocket acceptance gates

- Gate 25: **OPEN** — durable immutable replica installation receipt, authenticated transfer provenance and owner-host Redis persistence/restart/failover.
- Gate 36: **OPEN** — public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session, Android WebView lifecycle and real network handover.
- Gate 38: **OPEN** — owner-host metrics persistence, disk-pressure/restart/backup/retention, operator dashboard, external alert delivery and recovery drill.
- Gate 10: **0/10 external criteria formally closed**.

The 4403 close-reason diagnostic correction from Batch 62J-134 is CI-accepted; it does not close Gate 36 or Gate 25.

## Technical indicator progress ledger

No indicator runtime, test, calculation, hook, renderer or UI source changed in this batch. No indicator implementation credit is awarded.

| Indicator/component | Current status | Verified scope / limitation |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; not chart-integrated |
| Footprint | 🟧 Prototype/foundation only | Synthetic educational accumulator; not exchange-native bid/ask truth |
| Heatmap | 🟥 Not implemented | Visual implementation blocked pending user reference image and reviewed blueprint |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

Shared requirements remain: warm-up nulls, candle-index alignment, prefix causality/no future-candle repaint, invalid/gapped bars not silently converted to zero, stale-output clearing on symbol/venue/dataset/chart/timeframe changes, and renderer/lifecycle validation. Footprint OFF must preserve ordinary candlestick spacing; only explicit ON enables the dedicated spaced cluster layout. Footprint and Heatmap visual implementation must wait for the user's reference image(s) and reviewed blueprint.

No aggregate indicator completion percentage is assigned because indicator weights and denominator are not approved.

## Project-wide progress indicator

| Stage | State |
|---|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = **75% provisional** |
| 2. Market Data Infrastructure | **NOT SCORED / not officially opened** |
| 3. Chart Engine & Timeframe | **NOT SCORED / not officially opened** |
| 4. Indicators & Analytics | **NOT SCORED / not officially opened** |
| 5. Professional UI & Interactive Tools | **NOT SCORED / not officially opened** |
| 6. Hardening, Validation & APK Release | **NOT SCORED / not officially opened** |

Overall project: **NOT SCORED**. Six-stage weights and the overall acceptance denominator have not been approved. Do not derive an overall percentage from Stage 1 alone.

## IP3S — Indicator Proses Peningkatan Proyek Signifikan

IP3S measures this work cycle's verified delivery quality, not project completion.

| Dimension | Score | Rationale |
|---|---:|---|
| Verified engineering delta | 18/25 | Batch 62J-134 corrected a real false WebSocket 4403 diagnostic and added regression coverage; this batch completed source-backed Gate 25 acceptance analysis, but made no new runtime change |
| Exact-HEAD test/CI evidence | 14/20 | Automated Tests, CodeQL and Secret Audit all SUCCESS on exact HEAD |
| Blocker reduction | 12/20 | Gate 25 trust/receipt gap and implementation acceptance cases are now isolated; gate remains open |
| Canonical documentation | 20/20 | Gate 25 source audit, matrix, indicator ledger and project-stage state reconciled |
| Scope/cost integrity | 15/15 | ZERO COST; correct branch; no credentials, deployment, device work or main changes |
| **IP3S total** | **79/100** | Cycle delivery score only; not overall completion |

## Cost, safety and branch integrity

ZERO COST. No paid service, hosting, domain, API, cloud resource, account, deployment, production credential, secret, Android device or Termux action. No runtime/schema/test source edits in Batch 62J-135. `main` untouched.


---

## Batch 62J-134 — WebSocket close-reason accuracy fix (22 November 2026)

Source/test commit: `ecf7decb8e823effe09a6be8a9973bb98619ae92` on `phase-2/market-data-foundation`.

### Engineering change
Backend source uses WebSocket close code 4403 for both:
- Origin policy rejection: reason `Origin not allowed` before authentication.
- Canonical instrument/series entitlement denial: reason such as `Instrument access denied` or `Instrument access revoked`.

Previously the client supervisor mapped every 4403 to an entitlement failure. That produced a false diagnosis for a frontend Origin configuration error. The supervisor now classifies 4403 by the server-provided close reason:
- Origin rejection → “WebSocket Origin is not allowlisted” diagnostic.
- Other 4403 reasons → entitlement denial/revocation diagnostic.
Both remain terminal and do not trigger an automatic reconnect loop.

Regression tests cover both branches, verify the error and snapshot detail, and verify no retry. Files changed:
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`

This is a diagnostic correctness fix only; it does not weaken authentication, authorization, Origin enforcement, or reconnect policy.

### Exact-commit CI status
- Automated Tests run [44991640588](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640588): **IN PROGRESS** at documentation time; frontend unit tests and frontend build passed, Redis TLS fixture passed, backend tests still running.
- CodeQL run [44991640593](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640593): **SUCCESS** (JavaScript/TypeScript and Python).
- Full Git History Secret Audit run [44991640577](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640577): **SUCCESS**.
- Zero-cost Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **IN PROGRESS**; web build and Android wrapper setup passed, APK assembly still running.

Do not call the new regression tests accepted until Automated Tests completes successfully. No APK artifact is claimed until its workflow reports success.

### Remaining WebSocket acceptance
- Gate 25 OPEN: immutable snapshot installation digest/provenance receipt, owner-authenticated transfer and owner-host Redis acceptance.
- Gate 36 OPEN: public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session and Android WebView foreground/background/process-death/network handover.
- Gate 38 OPEN: owner-host metrics persistence, disk pressure/restart/backup/retention and operator dashboard/alert/recovery.
- Redis TLS/AOF restart: isolated CI fixture PASS on the preceding exact-head docs baseline; owner-host failover/backup/restore remains untested.

### Indicator and project indicators
No indicator source or tests changed; indicator implementation status receives no credit:
- SMA20 🟨 foundation (first valid index 19).
- EMA20 🟨 SMA-seeded alpha 2/21 (first valid index 19).
- RSI14 Wilder 🟨 foundation (first valid index 14).
- MACD12/26/9 🟨 foundation (MACD index 25; signal/histogram index 33).
- Bollinger20,2 🟨 foundation (first valid index 19).
- Shared Indicator Hook 🟨 backend snapshot/alignment only; not chart-integrated.
- Footprint 🟧 synthetic educational accumulator only; wait for user visual reference and reviewed blueprint.
- Heatmap 🟥 not implemented; wait for user visual reference and reviewed blueprint.
- Liquidation Maps 🟥 not implemented.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED; Gate 10 remains 0/10 external criteria formally closed. Overall project remains NOT SCORED until stage weights and acceptance denominator are approved.

IP3S for this batch is **PENDING** until exact-commit Automated Tests completes. This prevents unverified source changes from receiving CI-evidence credit. ZERO COST; no deployment, paid service, production credentials, device/Termux operations or `main` changes.

---

## Batch 62J-132 — exact-baseline CI acceptance and indicator reconciliation (22 November 2026)

**Source/test baseline:** `d549d99318abbeb156f716a4e2cf749eef226ca9` on `phase-2/market-data-foundation`. This is the commit tested by the three successful workflows; the documentation follow-up commit is a separate HEAD and must receive its own CI check.

- Automated Tests [44989988543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988543): **SUCCESS**.
- CodeQL [44989988481](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988481): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44989988510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988510): **SUCCESS**.
- Automated Tests include backend tests, real Redis TLS fixture, synthetic outbox/metrics benchmarks, backend dependency audit, backend container build, persistent-volume/shared-Redis-guard smoke test, image scan and frontend dependency audit enforcement.
- Trivy 0.76.2 scan of backend image digest `sha256:2943078f07ff217aedcdea4577b1edfed2c0355abbef37fa68d558110a71b643`: **0 OS vulnerabilities, 0 Python package vulnerabilities, 0 reported misconfigurations** in the exported CI report. Point-in-time CI image evidence only.
- Synthetic outbox: 1,000 bars; persist p95 4.155 ms / p99 5.943 ms; two replay readers p95 1.659 ms / p99 1.910 ms. Not a WebSocket or production SLO test.
- Synthetic metrics collector (899 logical series): four-process p95 flush 139.854 ms, p99 277.444 ms, 3 retries; 16-worker staggered-process p95 287.759 ms, p99 524.206 ms, 44 retries; 16-thread p95 594.880 ms, p99 844.445 ms, 213 retries. SQLite integrity remained `ok`; writer-lock contention is material at high fan-out. This is operational telemetry storage, not OHLCV WebSocket delivery.
- **Correction:** backend container persistent-volume smoke test does not prove Redis AOF durability/restart/failover. Those remain open.

### WebSocket acceptance
- Gate 25: **OPEN** — snapshot digest is not anchored in an immutable receipt; authenticated owner-host transfer/receipt custody and owner-host Redis persistence/restart/failover remain unproven. Proposed ADR: `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`.
- Gate 36: **OPEN** — public hostname/reverse proxy/WSS certificate lifecycle, live Firebase, production browser and Android WebView/network-handover acceptance remain unproven. Series/Origin ticket binding remains a threat-model item.
- Real TLS fixture covers trusted CA, wrong CA, hostname mismatch, plaintext downgrade rejection and shared-guard ticket/lease operations; CI-only evidence.

### Technical indicator ledger — unchanged implementation status
SMA20 🟨 foundation (first index 19); EMA20 🟨 SMA-seeded alpha 2/21 (first index 19); RSI14 Wilder 🟨 (first index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (first index 19); Shared Indicator Hook 🟨 backend alignment only; Footprint 🟧 synthetic educational accumulator and reference-gated; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. No indicator code/test changed, so no implementation credit.

Preserve warm-up nulls, candle alignment, no future-candle repaint, stale clearing on identity/timeframe changes and standard candle spacing while Footprint is OFF. Footprint/Heatmap visual work remains gated on user reference images and reviewed blueprint.

### Project progress and IP3S
- Stage 1: 30/40 = **75% provisional**. Stages 2–6 NOT SCORED. Gate 10 = 0/10 formally closed. Overall project = **NOT SCORED** because approved stage weights/denominator do not exist.
- **IP3S Batch 62J-132: 67/100** (cycle quality only): engineering delta 0/25; exact-baseline CI 20/20; blocker/evidence reduction 12/20; documentation 20/20; ZERO COST/scope integrity 15/15. Not overall completion.
- ZERO COST, docs/evidence only; no runtime/test source, no deployment, no paid services, no secrets, no device/Termux and no `main` changes.

## Batch 62J-131 — WebSocket replica recovery, exact-head CI and project progress (22 November 2026)

**Verified branch HEAD:** `5be3cff9c19064cbcc9ad686aaf359efb4e5c03d` on `phase-2/market-data-foundation`.

**Exact-head CI — all SUCCESS:**
- Automated Tests [44989326413](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326413)
- CodeQL [44989326466](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326466)
- Full Git History Secret Audit [44989326442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326442)

### New source-to-test acceptance evidence

- Publisher: 21 named tests cover deterministic cursor IDs, canonical payloads, ambiguous XADD/lost-reply recovery, conflict rejection, checkpoint fencing, retention and snapshot rebase. The publisher advances its durable checkpoint only after confirmed append or exact read-back.
- Consumer: 20 named tests cover SQLite apply-before-ACK, callback retry/idempotence, own-pending-first recovery, XAUTOCLAIM, independent gateway groups, multi-process broadcast, lease-loss-before-ACK, ACL separation and snapshot-generation convergence.
- Worker: 5 tests cover bounded retry/backoff, terminal resnapshot and ownership-loss behavior, and bounded shutdown.
- Replay: 11 tests cover global cursor scanning, fixed replica watermark, history gaps, retention/cursor-ahead, series validation and bounded all-or-resnapshot behavior.
- Stream hub: 10 tests cover atomic snapshot/live boundary, exact-series isolation, slow-consumer resnapshot and replay merge.
- Browser supervisor: 22 tests cover ticket/token retries, bounded reconnect, cursor replay, sequence-gap resnapshot, terminal auth/entitlement/policy rejection and close/stop races.
- A real TCP-path interruption test launches two ASGI gateway processes behind independent fault proxies, severs their Redis TCP paths, rejects reconnects during outage, restores connectivity, and verifies both clients receive the same cursor and both replica checkpoints converge. This is CI-local/ephemeral evidence, not public WSS or owner-host acceptance.

### Production boundary

Gate 25 remains OPEN: the installer is owner-supplied; its digest is format-checked and propagated but not anchored in the durable replica checkpoint. Authenticated owner-host snapshot transfer/receipts, Redis TLS/ACL/persistence/restart/failover remain unproven.

Gate 36 remains OPEN: ticket auth, series authorization, reconnect/replay and local TCP fault recovery are covered in repository tests. Public hostname/reverse proxy/TLS, live Firebase, real browser production session, Android WebView lifecycle and real public network handover remain unproven. Series/Origin ticket binding remains a threat-model decision, not an assumed defect.

### Indicator ledger

No indicator source/test changed; no implementation credit:
- SMA20 🟨 foundation, first valid index 19.
- EMA20 🟨 SMA-seeded, alpha 2/21, first valid index 19.
- RSI14 Wilder 🟨 foundation, first valid index 14.
- MACD12/26/9 🟨 foundation, MACD index 25; signal/histogram index 33.
- Bollinger20,2 🟨 foundation, first valid index 19.
- Shared Indicator Hook 🟨 backend snapshot/alignment foundation, not chart-integrated.
- Footprint 🟧 synthetic educational only; reference-image and reviewed-blueprint gate.
- Heatmap 🟥 not implemented.
- Liquidation Maps 🟥 not implemented.

Preserve warm-up nulls, candle-index alignment, no future-candle repaint, stale clearing on identity/timeframe changes and Footprint OFF normal candle spacing. Do not assign aggregate indicator percentage without approved weights/denominator.

### Project progress

Stage 1 = 30/40 = **75% provisional**. Stage 2–6 remain NOT SCORED/not officially opened. Gate 10 = **0/10 formally closed**. Overall project = **NOT SCORED** until six-stage weights and denominator are approved.

### IP3S — Indicator Proses Peningkatan Proyek Signifikan

Batch 62J-131 = **61/100** (cycle delivery quality only): engineering delta 0/25; exact-head CI 20/20; blocker reduction 8/20; canonical documentation 18/20; scope/cost integrity 15/15. This is not project completion.

**ZERO COST:** documentation-only; no runtime/test change, paid resource, deployment, credential, device/Termux work or main-branch change.

Full report: [WORK_CYCLE_2026-11-22_BATCH62J131_WEBSOCKET_REPLICA_ACCEPTANCE_IP3S.md](WORK_CYCLE_2026-11-22_BATCH62J131_WEBSOCKET_REPLICA_ACCEPTANCE_IP3S.md).

---

## Batch 62J-125 — WebSocket test-evidence mapping and production acceptance gap review (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Reviewed documentation/source baseline:** 4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d  
**CI on this baseline:** Automated Tests run [44986546422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546422), CodeQL [44986546414](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546414), and Full Git History Secret Audit [44986546413](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546413) all SUCCESS on exact SHA `4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d`.

### New source/test evidence mapped

- Redis ticket issuance stores only a SHA-256 digest-keyed ticket record with account subject and purpose, 90-second TTL and create-only `SET NX`. Lua consume performs GET+DEL atomically. Tests cover digest-keying, subject binding, exact TTL, malformed/corrupt/wrong-purpose rejection, one-use consume, Redis TTL/consume integration, and a multi-process ticket+account-lease test.
- HTTPS ticket endpoint requires a verified principal and returns ticket, expiry and purpose. WebSocket handshake rejects disallowed non-empty Origin, consumes ticket before accepting its subject as principal, and applies separate exact-series/canonical-instrument entitlement authorization. Ticket does not itself bind the requested series or Origin; retain this as a threat-model review item.
- Firebase verifier tests require revoked-token checking and validate subject/claims using test doubles. These are not live Firebase-project credential, revocation, entitlement grant/revoke/renew E2E tests.
- Redis gateway tests verify snapshot installation precedes Redis client construction, installed source/generation/high-water cursor/hash match the durable local checkpoint, source mismatch fails before Redis construction, and production plaintext Redis is rejected. The callback is still owner-supplied; repository tests do not authenticate remote transfer receipts or prove independent gateway receipt custody.
- Replay tests verify global cursor advancement across unrelated series, missing cursor/history-gap fail-closed behavior, fixed checkpoint watermark, retention expiry/cursor-ahead rejection, and bounded scan/event limits with resnapshot response.
- Browser WebSocket tests cover ticket auth, exact-series subscribe, snapshot/update, durable cursor replay before live updates, renewal acknowledgement, heartbeat/error cleanup and reconnect supervisor recovery. These are simulated browser-socket tests, not public reverse-proxy or real browser/network deployment evidence.
- Server source checks Origin allowlist, performs periodic entitlement recheck and Redis lease renewal, and closes fail-closed on Redis/lease failure. Backend tests cover Redis outage and lease renewal failure. CI Redis is ephemeral.
- Android host preflight and immutable preview-publisher tests run in CI; they do not constitute Android device/WebView foreground-background, process-death, network handover or reconnect acceptance.

### Acceptance status — unchanged

Gate 25 remains OPEN pending owner-host snapshot transport authentication, independently authenticated per-gateway installation receipts, byte/hash custody and exact generation/high-water alignment under real Redis persistence/restart/failover.

Gate 36 remains OPEN pending verified public HTTPS/WSS endpoint, reverse proxy/TLS, real Firebase project, browser and Android WebView lifecycle tests, reconnect/replay/resnapshot and duplicate suppression across real network interruption, plus operator logs/alerts. Subject/purpose ticket binding and separate series authorization remain as implemented; adding series/Origin into ticket claims is a threat-model decision requiring explicit design review, not an assumed code change.

Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. CI/source tests do not close production owner-host gates.

### Indicator reconciliation — no implementation credit

No indicator implementation or test changed. Canonical statuses remain:
- SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2, and Shared Indicator Hook: 🟨 foundation, not fully chart-integrated.
- Footprint: 🟧 synthetic educational accumulator only; visual implementation waits for user reference image(s) and reviewed blueprint.
- Heatmap and Liquidation Maps: 🟥 not implemented.

Warm-up null semantics, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF normal candle spacing remain requirements. No aggregate percentage is assigned without approved weights/denominator.

### Cost and scope

ZERO COST. No source changes, external services, paid hosting, domains, deployment, cloud resource, account, production credentials, Android device action or Termux work. `main` untouched. This batch is documentation-only.

---

## Batch 62J-124 — exact-head CI, SQLite contention and WebSocket acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact source/test HEAD:** 332fd0dacdcd383a27744ea4b9f76d7cbe418cdc  
**Automated Tests #1962 [run 44986046696](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696): SUCCESS**; **CodeQL [run 44986046674](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046674): SUCCESS**; **Full Git History Secret Audit [run 44986046694](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046694): SUCCESS**. All three workflows target the same exact SHA.

### Exact-head CI and artifact evidence
- Automated Tests job completed successfully: frontend dependency audit/tests/build and bundle secret scans; Android host preflight and preview publisher tests; backend dependency installation and tests; isolated Redis TLS CA/hostname fixture; synthetic SQLite outbox and metrics benchmarks; backend container build; shared-Redis-guard/persistent-CI-volume smoke; Trivy scan/report; dependency audit enforcement. All 30 main job steps completed successfully.
- Synthetic metrics artifact [14739229002](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739229002) was downloaded and independently inspected. Full 899 logical-series envelope; 1 worker: 32/32 flushes, 0 retries, p95 flush 8.19 ms, SQLite integrity ok; 4 threads: 128/128, 2 retries, p95 flush 110.61 ms, p95 writer-lock wait 79.22 ms; 16 simultaneous threads: 512/512, 82 retries, p95 flush 371.19 ms, p95 writer-lock wait 314.04 ms; 4 independent processes: 128/128, 2 retries, p95 flush 84.23 ms, integrity ok. All synthetic flushes succeeded and integrity was ok. The 16-thread case still shows material lock contention; jitter improved the exact benchmark compared with the immediately preceding run's 187 retries / 627.74 ms p95 flush, but the runs are CI-runner-specific and not a controlled performance comparison or production SLO.
- Metrics artifact records synthetic operational counters only, not market data. It explicitly excludes production persistent-volume and multi-host claims. Do not infer production capacity or supported worker count from it.
- Trivy artifact [14739587046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739587046) was inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, digest sha256:274264c0115b75b9c538a9c383140f393c9c8545eb73b4b1d48269384ab240ff, size 571,353,088 bytes. The report lists zero vulnerabilities and zero misconfigurations in the scanned Alpine OS and Python package result groups. This is point-in-time scanner evidence for this exact amd64 image/database only; it is not an ongoing guarantee or ARM64 evidence.
- Synthetic outbox artifact [14739104428](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739104428) was generated by CI but is not used here to make additional performance claims.

### Source change and scope boundary
Commit 332fd0dacdcd383a27744ea4b9f76d7cbe418cdc changes exactly backend/app/metrics_collector.py and backend/tests/test_metrics_collector.py. It raises bounded BEGIN-lock retry attempts to 16 and adds randomized backoff to desynchronize concurrent SQLite writers. The exact-head backend tests and synthetic benchmark passed. This is a metrics-collector resilience change only: no WebSocket transport, Firebase authentication, ticket, Redis market-data publisher/consumer, snapshot/replay, cursor, browser client, Android client, indicator formula, hook, renderer or indicator test was changed.

### WebSocket acceptance — repository evidence versus production evidence
- The source publisher and gateway replica runtime factories remain separate injected ASGI roles. The source publisher checkpoint/outbox and gateway replica consumer remain repository-side components; the gateway worker uses an ownership lease, sequential consumption, bounded retry on callback errors, and terminal resnapshot-required/ownership-lost states.
- The gateway snapshot installer is an owner-supplied authenticated transfer callback. The code validates installed metadata against its durable local checkpoint before Redis consumer construction; this does not independently authenticate remote snapshot bytes or receipts. The source activation verifier similarly remains an owner-supplied trust boundary.
- WebSocket tickets are short-lived (90 seconds) and single-use in the reviewed ticket path. Firebase ID-token exchange is over HTTPS; the Firebase token is not placed in a WSS URL or raw authentication frame. The ticket currently binds account subject and purpose; canonical series and Origin are not embedded in the ticket itself. Series authorization is performed separately. Retain series/Origin binding as an explicit threat-model and owner-review item before production exposure, not as a claim that this commit fixed it.
- Production gates remain unclosed: owner-host secret injection/rotation and redaction; real Firebase project token and entitlement E2E; owner-host Redis TLS/CA/hostname/ACL/persistence/failover and authenticated snapshot installation receipts; live database backup/restore; encrypted off-host backup/key custody; persistent volume ownership/restart/disk-pressure; verified public hostname/TLS; public HTTPS ticket exchange and WSS reverse proxy with real browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression evidence; real dashboards/retention/alerts and human acknowledgement.
- **Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional.** CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. No stage transition is authorized.

### Indicator progress reconciliation — no credit
No indicator source or tests changed in this commit. Keep the canonical matrix unchanged:
- SMA20 — 🟨 foundation; 20-close mean, first valid index 19.
- EMA20 — 🟨 foundation; SMA-seeded EMA, alpha 2/21, first valid index 19.
- RSI14 Wilder — 🟨 foundation; 14 close changes, first valid index 14.
- MACD12/26/9 — 🟨 foundation; MACD first valid index 25; signal/histogram index 33.
- Bollinger20,2 — 🟨 foundation; 20-close mean ±2 population standard deviations, first valid index 19.
- Shared Indicator Hook — 🟨 foundation; validated backend snapshot and candle-index-aligned calculation output, not chart-integrated.
- Footprint — 🟧 synthetic educational accumulator only; visual work remains blocked on user reference image(s) and reviewed blueprint.
- Heatmap — 🟥 not implemented.
- Liquidation Maps — 🟥 not implemented.

Warm-up values remain null, never zero; outputs align to source candle indices; no future-candle repaint; identity/timeframe changes clear stale series. Footprint OFF must preserve standard candlestick spacing; only explicit ON uses spaced cluster layout. No aggregate indicator percentage without approved weights and denominator. CI, benchmarks and documentation award zero indicator implementation progress.

### Cost and change boundary
ZERO COST maintained: no paid service, hosting, deployment, domain, cloud resource, account, production credential, device/Termux operation or external endpoint was created. No main-branch change. This batch is documentation-only after the already-tested source commit.

**Next safe sequence:** preserve this green exact-head CI; continue the read-only WebSocket owner-evidence audit and ARM64 build feasibility review without provisioning; keep all owner-host production gates open until real evidence and authorized adult account-owner review exist. Do not respond to remaining SQLite contention by blindly increasing retry limits; a single-writer/queue design would require a separate scoped architecture decision and measured acceptance criteria.

---

# Indicator progress ledger — Batch 62J-122 reconciliation

## Batch 62J-122 — exact-head WebSocket CI, artifact and runtime-boundary audit (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Audited exact HEAD:** 4c3e9f9f4cd8317c5cd03357b51aae06d289a804  
**Automated Tests [run 44984396895](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895): SUCCESS**; **CodeQL [run 44984396918](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396918): SUCCESS**; **Full Git History Secret Audit [run 44984396926](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396926): SUCCESS**. All three runs target the exact audited HEAD.

### CI evidence and limitations
- Frontend: 29 Vitest files, 255 tests passed.
- Backend: 1,294 passed, 1 skipped. The skipped test was the real Redis TLS/shared-guard integration test because REDIS_TEST_URL was not configured. The workflow's separate container smoke did exercise a CI Redis instance; this does not turn the skipped integration case into a pass.
- Container smoke passed: health endpoint, Redis ACL authentication, AOF data surviving Redis restart, fail-closed API behavior during Redis outage, backend reconnection, non-root UID/GID 10001, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection.
- Trivy report artifact [14739352623](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739352623) was independently inspected. Exact image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, image digest sha256:28fc78838f596968e3825ac2f46ffd3a1c7b688e029c62b53fcad2cd8bc09f85, reported **0 vulnerabilities** in Alpine OS and Python package result groups. Image size: 571,350,016 bytes (~571 MB). This is point-in-time scanner output for this exact amd64 image and database, not a permanent guarantee and not ARM64 evidence.
- Synthetic outbox artifact [14738863888](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14738863888): 1,000 synthetic bars/events; persist p95 2.655 ms; concurrent replay-page p95 1.305 ms with two reader threads. Local single-process SQLite microbenchmark only, not a real provider or WebSocket load/SLO test.
- Synthetic metrics collector artifact [14739436712](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739436712): 899 logical series; one thread 32/32 flushes, 0 retries, p95 flush 8.10 ms; four threads 128/128, 2 retries, p95 flush 112.97 ms and writer-lock p95 105.38 ms; 16 threads 512/512, 65 retries, p95 flush 350.53 ms and writer-lock p95 315.97 ms; four independent processes 128/128, 1 retry, p95 flush 60.23 ms; staggered 16-worker case 512/512, 0 retries. SQLite integrity was ok in all reported cases. This demonstrates contention in concurrent same-host SQLite workloads, but is not a production host or multi-host benchmark. Do not infer multi-worker capacity or SLO from it.

### WebSocket runtime boundary audit
- Source and gateway runtime factories remain explicitly injected into separate ASGI app roles. The app rejects simultaneously injecting both roles into one instance.
- Production settings require Redis TLS URL and Firebase project ID; the shared guard is mandatory in production. The non-production in-memory ticket store is not production acceptance.
- Source publisher activation requires a host-supplied snapshot verifier callback. Its evidence must bind source ID, stream key, generation, cursor, SHA-256 and one matching installation receipt per required gateway. The callback remains a trust boundary: the owner must independently verify snapshot bytes and authenticate each receipt; repository shape validation cannot probe remote gateways.
- Gateway activation requires an owner-supplied snapshot installer and validates its returned metadata against the durable local replica checkpoint before creating the Redis client/consumer. This does not independently establish remote source authenticity; owner transport and evidence custody remain external.
- Replica worker obtains a generation-scoped lease before group access, ensures group readiness before serving, and runs one sequential consumer per replica identity. Existing lease and consumer code fail closed on unverifiable/lost ownership, apply-before-ACK, reclaim pending messages, and require resnapshot on history gaps.
- No source change was made in this batch. These are source-review findings, not new runtime acceptance tests.

### Production disposition
Public hostname/TLS/reverse proxy, real Firebase signed-token and entitlement E2E, owner-host Redis ACL/secret rotation/persistence/failover, authenticated global snapshot receipts, public browser WSS and Android WebView lifecycle evidence remain absent. Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. CI container Redis and ephemeral volume evidence does not close owner-host gates.

### Indicator ledger reconciliation
Compare from indicator implementation baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 through 4c3e9f9f4cd8317c5cd03357b51aae06d289a804 contains documentation paths only; no indicator calculation, hook, renderer, UI, formula or indicator test implementation changed. Therefore this batch awards **zero indicator implementation progress**. Keep SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook at 🟨 foundation; Footprint 🟧 simulated/reference-gated; Heatmap and Liquidation Maps 🟥 not implemented. No aggregate percentage without approved weights/denominator. Footprint/Heatmap visual work remains blocked on user references and reviewed blueprint; Footprint OFF preserves ordinary candle spacing.

### Cost and change boundary
Documentation-only update. No deployment, host, resource, provider, paid service, account or credential was created or used. No main-branch changes, no device/Termux work, and no runtime or test files modified. ZERO COST maintained.

**Next safe sequence:** finish exact-head evidence review; design a zero-cost ARM64 build/smoke verification separately from amd64; retain the SQLite concurrency warning; and keep production gates open until owner-controlled evidence exists.
---
# Canonical indicator status — Batch 62J-121 (22 November 2026)

## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

# Canonical indicator status — Batch 62J-120 (22 November 2026)

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).


## Batch 62J-119 — WebSocket acceptance and indicator ledger exact-head reconciliation (22 November 2026)

**Verified parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750` on `phase-2/market-data-foundation`. This checkpoint was created only after all three workflows for that exact SHA completed successfully.

**Exact-head CI:**
- Automated Tests #1954 — [run 44982930281](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281): **SUCCESS**. Frontend unit tests/build, backend tests, isolated Redis TLS/CA/hostname enforcement fixture, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke test using shared Redis guard and persistent volume, Trivy image scan/report export/upload, and dependency-audit enforcement all completed successfully.
- CodeQL [run 44982930379](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930379): **SUCCESS**.
- Full Git History Secret Audit [run 44982930324](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930324): **SUCCESS**.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281/artifacts/14739265202). The workflow completed the configured HIGH/CRITICAL scan and uploaded the JSON report. Do not infer a zero-vulnerability result without reviewing the artifact contents.

These results verify the repository workflow and its CI service topology only. The CI Redis instance, ephemeral runner volume, and container smoke are not the intended OCI host or production Redis service.

**WebSocket repository evidence:** source-side publisher and gateway runtime factories, durable SQLite outbox, atomic snapshot/watermark primitives, Redis Streams publisher/consumer, per-gateway consumer groups, replica snapshot installation checks, fail-closed runtime construction, ticket authentication/renewal, reconnect/replay and client failure-matrix tests are present in the audited source. The latest CI validates the covered repository paths. The default FastAPI app intentionally does not invent owner-specific publisher/replica factories or trust snapshot receipts; those must be injected from a verified owner-controlled host setup.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS endpoint, production Firebase token/entitlement evidence, owner-host Redis TLS/ACL/persistence/rotation/failover, authenticated global snapshot manifest and per-gateway installation receipts, or real browser + Android WebView lifecycle evidence has been supplied. A successful CI container smoke cannot close those host/client gates.

**ZERO COST boundary:** no OCI account or resource was created, no deployment or public endpoint was started, no paid resource or trial-credit dependency was introduced, no credentials were requested, no device/Termux operation occurred, and `main` was not touched. OCI remains a conditional candidate subject to actual Always Free eligibility and adult account-owner approval.

**Indicator disposition — no source change and no progress credit:** the source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains the calculation baseline. The comparison through parent HEAD `6d5a05d611615972d5826002442a65e74c179750` is documentation-only; no indicator formula, hook, chart renderer, UI, or indicator test source changed. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formula definitions, warm-up indices, numerical safeguards, data identity, stale-series invariants, UI acceptance and reference prerequisites remain in the canonical audit and ledger. Aggregate indicator percentage remains unscored without approved weights and denominator.

**Project accounting:** Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI or documentation-only checkpoint. No progress is awarded from CI alone.

**Next zero-cost sequence:** preserve the green exact-head CI; finish ARM64 build/configuration readiness without provisioning; have the adult account owner verify OCI eligibility, capacity and all possible charges; only then, with explicit authorization, consider an Always Free-only host. Collect actual host and client evidence for Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Close Gate 10 only after evidence review and operator sign-off.

---



The source-backed current indicator audit is maintained in [INDICATOR_PROGRESS_AUDIT_2026-11-22.md](INDICATOR_PROGRESS_AUDIT_2026-11-22.md). This section is the authoritative current checkpoint; older entries below are historical snapshots and must not override it.

## Batch 62J-117 — exact-head CI and indicator ledger reconciliation (22 November 2026)

**Verified branch HEAD:** `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02` (`phase-2/market-data-foundation`). The source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains valid: GitHub comparison from that baseline to this HEAD contains documentation-only changes, with no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source changes.

**Exact-head workflows on `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02`:**
- Automated Tests [run #1952 / 44981803844](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844): **SUCCESS**; all 61 reported workflow steps completed successfully, including frontend tests/build, backend tests, Redis TLS CA/hostname fixture, backend container build, persistent-volume Redis smoke test, image scan/report and dependency audits.
- CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808): **SUCCESS**.
- Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851): **SUCCESS**.
- These are exact-head repository CI/security results. They do not constitute production Firebase, owner-host Redis, public WSS, browser or Android WebView acceptance.

**Indicator disposition — unchanged, zero progress credit:** SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 (synthetic/reference-gated), Heatmap 🟥, Liquidation Maps 🟥. The five calculation foundations and their first-valid indices remain as recorded in the canonical audit; none is accepted as a finished visible chart feature. The chart integration, controls, legends/current values, pane/overlay rendering, stale-series clearing and lifecycle/render acceptance remain outstanding as listed per study. Footprint OFF must preserve ordinary candle spacing; only explicit ON may switch to spaced clusters. Footprint, Heatmap and Liquidation Maps visual work remains gated by user-provided reference image(s) and reviewed blueprint.

**Accounting:** no indicator or project completion credit is awarded by WebSocket CI or this documentation reconciliation. Aggregate indicator percentage remains unscored without approved weights and denominator. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed. Gates 20, 25 and 36 remain open for real Firebase/entitlement evidence, owner-host Redis TLS/ACL/persistence/recovery and public HTTPS/WSS proxy plus browser/Android acceptance. No deployment or production readiness is claimed.

**Cost/scope:** ZERO COST. No paid hosting/provider, OCI provisioning, credentials, deployment, Termux/device action or `main` modification.


- Audited source/test baseline: `0074f1d0b0e421f32800294742f92d9bc9c8a2c6`.
- SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨: calculation foundations and 15 calculation tests exist; none is a finished visible chart feature.
- Shared market-indicator hook 🟨: validated-backend-only hook exists, but the chart does not call it and no dedicated hook test file was found.
- Footprint 🟧: synthetic offline educational accumulator only; not live exchange order flow. OFF preserves ordinary candle spacing; explicit ON alone may enable spaced clusters.
- Heatmap 🟥 and Liquidation Maps 🟥: no implementation found.
- `CandlestickChart.tsx` creates only a candlestick series; no indicator overlay, oscillator pane, toggle or legend is wired.
- Frontend baseline CI: 255/255 tests across 29 files. This is not 255 indicator tests. Backend: 1,294 passed, 1 skipped. Automated Tests, CodeQL and Full Git History Secret Audit passed on baseline.
- Visible indicator work belongs to official Stage 4. The project remains Stage 1 at 30/40 = 75% provisional; the 40% blueprint milestone does not authorize skipping stages.
- Aggregate indicator percentage remains **unscored** until approved per-indicator weights and a completion denominator exist. No progress credit is awarded by this docs-only batch.

See the audit for formulas, first-valid indices, numerical safeguards, data lineage, lifecycle invariants, visual acceptance criteria, reference prerequisites, exact CI evidence and ordered next work.

---

## Batch 62J-104 checkpoint — indicator implementation unchanged (22 November 2026)

The five-track Gate 10 audit and exact-head CI acceptance did not modify indicator calculations, candle data contracts, shared indicator hook, chart renderer, chart UI or indicator tests. **No indicator progress credit is awarded.** Exact source/test HEAD `a18e963d4cd067fe22ec8d03c653418e003c7fde` passed Automated Tests (backend 1,289; frontend 255/255), CodeQL and full reachable Git-history secret audit. These are backend/CI results, not visible indicator acceptance.

Current indicator matrix remains:

- **SMA20 🟨 Foundation** — arithmetic mean of 20 closes; first valid candle index 19. Remaining: visible overlay, independent toggle, legend/current value, stale-series clearing, renderer and lifecycle tests.
- **EMA20 🟨 Foundation** — SMA-seeded EMA, α = 2/(20+1) = 2/21; first valid index 19. Remaining: visible overlay, toggle, legend/current value, stale clearing, renderer and lifecycle tests.
- **RSI14 🟨 Foundation** — Wilder-smoothed average gains/losses over 14 close changes; first valid index 14. Remaining: dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing and renderer tests.
- **MACD 12/26/9 🟨 Foundation** — EMA12 − EMA26; MACD first valid index 25, signal/histogram first valid index 33. Remaining: dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, stale clearing and renderer tests.
- **Bollinger20,2 🟨 Foundation** — 20-close mean ± 2 × population standard deviation; first valid index 19. Remaining: upper/middle/lower visible overlay, toggle, displayed values, stale clearing and renderer tests.
- **Shared Indicator Hook 🟨 Foundation** — validated candle-index-aligned indicator snapshot. Remaining: chart identity/timeframe binding, loading/error lifecycle, stale clearing, per-series isolation and renderer integration.
- **Footprint 🟧 Simulated/reference-gated** — current accumulator is simulated/educational, not exchange-native bid/ask truth. Before visual implementation: user-provided reference image and reviewed blueprint. OFF preserves ordinary candle spacing; explicit ON switches to spaced cluster layout with readable bid/ask cells. Remaining: validated source/data contract, cluster renderer, toggle, scale/interaction, performance and lifecycle acceptance.
- **Heatmap 🟥 Not implemented** — requires zero-cost source feasibility, user reference image, validated data contract, reviewed blueprint, renderer, legend/scale, toggle and lifecycle tests.
- **Liquidation Maps 🟥 Not implemented** — requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer, scale/legend, toggle and lifecycle tests. Do not fabricate liquidation levels from unavailable data.

**Shared correctness invariants:** warm-up outputs remain null (never zero); every output aligns to the source candle index; no future-candle repaint; stale series clear on symbol, venue, dataset, chart or timeframe changes; calculation gaps and invalid source bars must not be silently converted into zero values. Footprint OFF must preserve standard candle layout. Visible indicator implementation remains behind the approved stage gate and the required reference/blueprint prerequisites.

Aggregate indicator percentage remains unscored because approved weights and denominators do not exist.

---

## Batch 62J-103 checkpoint — indicator state unchanged (22 November 2026)

WebSocket ticket renewal failure-matrix and Redis ticket-contract tests are backend authentication/transport work. No indicator formula, calculation module, market-data indicator contract, shared indicator hook, chart renderer, chart UI, or indicator test changed. **No indicator progress credit is awarded.** Source/test HEAD: `a18e963d4cd067fe22ec8d03c653418e003c7fde`.

Current complete indicator matrix and acceptance criteria:

- **SMA20 🟨 Foundation** — arithmetic mean of the latest 20 closes; first valid candle index 19. Remaining: visible chart overlay, independent enable/disable toggle, legend/current value, stale-series clearing, renderer and lifecycle tests.
- **EMA20 🟨 Foundation** — SMA-seeded EMA with α = 2/(20+1) = 2/21; first valid index 19. Remaining: visible overlay, toggle, legend/current value, stale clearing, renderer and lifecycle tests.
- **RSI14 🟨 Foundation** — Wilder-smoothed average gains/losses over 14 close changes; first valid index 14. Remaining: dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing and renderer tests.
- **MACD 12/26/9 🟨 Foundation** — EMA12 − EMA26; MACD first valid index 25, signal and histogram first valid index 33. Remaining: dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, stale clearing and renderer tests.
- **Bollinger20,2 🟨 Foundation** — 20-close mean ± 2 × population standard deviation; first valid index 19. Remaining: upper/middle/lower visible overlay, toggle, displayed values, stale clearing and renderer tests.
- **Shared Indicator Hook 🟨 Foundation** — validated candle-index-aligned indicator snapshot. Remaining: binding to chart identity/timeframe, loading/error lifecycle, stale clearing, per-series isolation and renderer integration.
- **Footprint 🟧 Simulated/reference-gated** — current accumulator is simulated/educational, not exchange-native bid/ask truth. Before visual implementation: user-provided reference image and reviewed blueprint. Required behavior: OFF preserves ordinary candle spacing; explicit ON switches to spaced cluster layout with readable bid/ask cells. Remaining: validated source/data contract, cluster renderer, toggle, scale/interaction, performance and lifecycle acceptance.
- **Heatmap 🟥 Not implemented** — requires zero-cost source feasibility, user reference image, validated data contract, reviewed blueprint, renderer, legend/scale, toggle and lifecycle tests.
- **Liquidation Maps 🟥 Not implemented** — requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer, scale/legend, toggle and lifecycle tests. Do not fabricate liquidation levels from unavailable data.

**Shared correctness invariants:** warm-up outputs remain null (never zero); every output aligns to the source candle index; no future-candle repaint; stale series clear on symbol, venue, dataset, chart or timeframe changes; calculation gaps and invalid source bars must not be silently converted into zero values. Footprint OFF must preserve standard candle layout. Visible indicator implementation remains behind the approved stage gate and the required reference/blueprint prerequisites.

Aggregate indicator percentage remains unscored because approved weights and denominators do not exist.

---

## Batch 62J-98 checkpoint — indicator state unchanged (21 November 2026)

Gate 25 gateway runtime construction, WebSocket transport audit and Gate 38 observability benchmarking are backend infrastructure work. No indicator formula, calculation module, data contract, shared hook, chart renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

Current complete indicator matrix:
- SMA20 🟨 — mean of 20 closes; first valid index 19. Remaining: chart overlay, independent toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing over 14 price changes; first valid index 14. Remaining: 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33. Remaining: pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests.
- Bollinger20,2 🟨 — mean ±2 × population standard deviation; first valid index 19. Remaining: upper/middle/lower overlay, toggle, values, stale clearing, renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining: chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation.
- Footprint 🟧 — simulated, not exchange-native bid/ask truth. Requires user visual reference, reviewed blueprint, explicit ON-only spaced cluster layout, bid/ask cells and performance acceptance. OFF must preserve ordinary candle spacing.
- Heatmap 🟥 — not implemented. Requires user reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented. Requires zero-cost source feasibility, validated calculation/data contract, reference/blueprint and renderer.

Shared invariants: warm-up values are null, never zero; outputs align to candle indexes; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Aggregate indicator percentage remains unscored because approved weights/denominators do not exist. Stage 4 visual work remains behind the official stage gate.

---

## Batch 62J-97 checkpoint — indicator state unchanged (21 November 2026)

Gate 38's production-staggered SQLite metrics benchmark is backend observability work only. No indicator formula, data contract, shared hook, renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

Current complete indicator state:
- SMA20 🟨 — mean of 20 closes; first valid index 19. Visible overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests remain.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests remain.
- RSI14 🟨 — Wilder smoothing; first valid index 14. Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests remain.
- MACD 12/26/9 🟨 — MACD first valid index 25; signal/histogram index 33. Pane, MACD/signal lines, histogram, zero guide, toggle, legend and renderer tests remain.
- Bollinger20,2 🟨 — mean ±2 × population standard deviation; first valid index 19. Upper/middle/lower overlay, toggle, displayed values, stale clearing and renderer tests remain.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Full chart identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation remain.
- Footprint 🟧 — simulated/reference-gated; requires the user's visual reference, reviewed blueprint, explicit ON-only spaced cluster layout, bid/ask cells and performance acceptance. OFF must preserve ordinary candle spacing.
- Heatmap 🟥 — not implemented; requires the user's visual reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented; requires zero-cost source feasibility, validated calculation/data contract, reference/blueprint and renderer.

Shared invariants: warm-up values are null, never zero; outputs align to candle indexes; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. No aggregate indicator percentage is published without an approved denominator. Stage 4 visual-indicator work remains behind the official stage gate.

---

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


## Batch 62J-96 checkpoint — no indicator changes (21 November 2026)

The Gate 38 retry-jitter experiment was rejected and reverted after a measured synthetic benchmark regression. The accepted diagnostic instrumentation from 62J-94 remains. No indicator formula, data contract, shared hook, renderer, UI or indicator test changed. **No indicator progress credit is awarded.** The complete indicator matrix and invariants remain unchanged.


## Batch 62J-99 indicator checkpoint — unchanged (21 November 2026)

This cycle audited Gate 25/36 gateway and WSS integration, Gate 38 telemetry, Gate 20 Firebase identity/entitlements and Gate 31 encrypted backup/recovery. No indicator calculation, data contract, shared hook, renderer, UI or indicator test changed. **No indicator progress credit is awarded.**

- SMA20 🟨 — mean of 20 closes; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing over 14 close changes; first valid index 14. Remaining: 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33. Remaining: pane, lines, histogram, zero guide, toggle, legend, stale clearing and renderer tests.
- Bollinger20,2 🟨 — mean ±2 × population SD; first valid index 19. Remaining: three-line overlay, toggle, values, stale clearing and renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining: chart identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint 🟧 — synthetic educational accumulator, not exchange-native bid/ask truth. Requires user reference, reviewed blueprint, ON-only spaced cluster layout, bid/ask cells and performance acceptance. OFF preserves normal candle spacing.
- Heatmap 🟥 — not implemented. Requires user reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented. Requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer.

Invariants: warm-up values null, never zero; candle-index alignment; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Aggregate indicator percentage remains unscored without approved weights/denominators. Stage 4 visible-indicator work remains behind the official stage gate.


## Batch 62J-100 indicator checkpoint — unchanged (21 November 2026)

Gate 38 SQLite bootstrap retry hardening, Gate 39 incident escalation integration tests and WebSocket cancellation-metric tests did not modify any indicator formula, calculation module, data contract, shared hook, renderer, chart UI or indicator test. **No indicator progress credit is awarded.**

- SMA20 🟨 — mean of 20 closes; first valid index 19. Remaining: visible overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing over 14 close changes; first valid index 14. Remaining: 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33. Remaining: pane, lines, histogram, zero guide, toggle, legend, stale clearing and renderer tests.
- Bollinger20,2 🟨 — mean ±2 × population SD; first valid index 19. Remaining: three-line overlay, toggle, values, stale clearing and renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining: chart identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint 🟧 — synthetic educational accumulator, not exchange-native bid/ask truth. Requires user reference, reviewed blueprint, ON-only spaced clusters, bid/ask cells and performance acceptance. OFF preserves normal candle spacing.
- Heatmap 🟥 — not implemented. Requires user reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented. Requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer.

Invariants unchanged: warm-up values null, never zero; candle-index alignment; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Aggregate indicator percentage remains unscored without approved weights/denominators. Stage 4 visible-indicator work remains behind the official stage gate.



## Batch 62J-101 checkpoint — no indicator implementation changes (21 November 2026)

The WebSocket accepted-counter correction and Gate 10 source/host-boundary audit changed backend observability only. No indicator formula, calculation module, data contract, shared hook, renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

- SMA20 🟨 — arithmetic mean of 20 closes; first valid index 19. Remaining: visible overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha = 2/21; first valid index 19. Remaining: overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing over 14 close changes; first valid index 14. Remaining: 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33. Remaining: pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests.
- Bollinger20,2 🟨 — 20-close mean ±2 × population standard deviation; first valid index 19. Remaining: three-line overlay, toggle, values, stale clearing, renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining: chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation.
- Footprint 🟧 — simulated educational accumulator, not exchange-native bid/ask truth. Requires user reference, reviewed blueprint, ON-only spaced clusters, bid/ask cells and performance acceptance. OFF preserves ordinary candle spacing.
- Heatmap 🟥 — not implemented. Requires user reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented. Requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer.

Invariants: warm-up values remain null (never zero); outputs remain candle-index aligned; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves normal candle spacing; only explicit ON activates spaced clusters. Aggregate indicator percentage remains unscored without approved weights/denominators; Stage 4 visible-indicator work remains behind the official stage gate.



## Batch 62J-101 CI completion — backend-only change (21 November 2026)

The WebSocket accepted-counter lifecycle correction passed exact-head CI: 255 frontend tests across 29 files and 1,281 backend tests in 48.87 seconds; CodeQL and full Git History Secret Audit also succeeded. This confirms the backend metric correction only. No indicator formulas, calculations, data contracts, shared hook, renderer, chart UI or indicator tests changed. **No indicator progress credit is awarded.** The complete indicator matrix and correctness invariants above remain unchanged.


## Batch 62J-102 reconciliation — no indicator code changed (22 November 2026)

The cycle added Gate 20 WebSocket ticket endpoint failure-boundary tests and audited Gate 10 evidence. No indicator calculation, formula, data contract, shared hook, renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

The complete matrix remains:
- SMA20 🟨 — mean of 20 closes; first valid index 19. Remaining overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing over 14 close changes; first valid index 14. Remaining 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD index 25, signal/histogram index 33. Remaining pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests.
- Bollinger20,2 🟨 — 20-close mean ±2×population SD; first valid index 19. Remaining three-line overlay, toggle, values, stale clearing, renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation.
- Footprint 🟧 — simulated educational accumulator, not exchange-native bid/ask truth. Requires user reference image and reviewed blueprint before visual work; OFF preserves ordinary candle spacing; explicit ON enables spaced clusters.
- Heatmap 🟥 — not implemented; requires user reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented; requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer.

Invariants: warm-up values null, never zero; candle-index alignment; no future-candle repaint; stale clearing on symbol/venue/dataset/chart/timeframe change. Stage 4 visible-indicator implementation remains gated. Aggregate indicator percentage remains unscored without approved weights/denominators.

## Batch 62J-106 — Production WebSocket acceptance reconciliation (22 November 2026)

This cycle reconciled the production-acceptance pack against the existing two-process and dual-gateway CI evidence. No indicator calculation, formula, data contract, shared hook, chart renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

The complete indicator matrix remains unchanged:
- SMA20 🟨 — arithmetic mean of 20 closes; first valid index 19. Remaining overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining overlay, toggle, legend/current value, stale clearing and renderer/lifecycle tests.
- RSI14 🟨 — Wilder smoothing over 14 close changes; first valid index 14. Remaining 0–100 pane, 30/70 guides, toggle, legend, stale clearing and renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD first valid index 25; signal/histogram first valid index 33. Remaining pane, lines, histogram, zero guide, toggle, legend, stale clearing and renderer tests.
- Bollinger20,2 🟨 — 20-close mean ±2×population SD; first valid index 19. Remaining three-line overlay, toggle, values, stale clearing and renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining chart identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation.
- Footprint 🟧 — simulated educational accumulator, not exchange-native bid/ask truth. User visual reference and reviewed blueprint are mandatory before visual implementation; OFF preserves normal candle spacing; explicit ON enables spaced clusters.
- Heatmap 🟥 — not implemented; requires user reference, zero-cost source feasibility, validated data contract, reviewed blueprint and renderer.
- Liquidation Maps 🟥 — not implemented; requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer.

Invariants remain: warm-up values null, never zero; candle-index alignment; no future-candle repaint; stale clearing on symbol/venue/dataset/chart/timeframe changes. Stage 4 visible-indicator work remains gated. Aggregate indicator percentage remains unscored without approved weights and denominator.

WebSocket CI work, even when it verifies real two-process fan-out, does not count as indicator UI or calculation completion.


## Batch 62J-108 checkpoint — no indicator implementation changes (22 November 2026)

A focused backend regression test was added to prevent future drift between the WebSocket ticket source contract and `backend/README.md`. It does not touch indicator formulas, data contracts, calculations, hooks, renderers, UI, or indicator tests. No indicator progress credit is awarded. Statuses remain SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD 12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥 and Liquidation Maps 🟥. See `docs/WORK_CYCLE_2026-11-22_BATCH62J108_WEBSOCKET_CONTRACT_GUARD.md` for the full formula, first-valid-index and remaining-work matrix.


## Batch 62J-109 — CI failure correction and exact-head verification (22 November 2026)

- Active branch: `phase-2/market-data-foundation`; exact commit: `81b741946f1512fb264936e37406d7560f24456f`.
- Corrected `backend/tests/test_websocket_documentation_contract.py`: the auth-frame assertion now compares against the already-lowercased README string, consistent with the case-insensitive endpoint/header/TTL assertions. The README content itself was correct; this was a test assertion normalization defect.
- Exact-head Automated Tests [44973890901](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890901): **SUCCESS**. All workflow steps completed, including frontend unit tests/build, backend tests, backend dependency audit, container image build, shared Redis guard + persistent-volume smoke test, image scan/report, and bounded synthetic SQLite/metrics benchmarks. No failed steps.
- Exact-head CodeQL [44973890847](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890847): **SUCCESS** for Python and JavaScript/TypeScript.
- Exact-head Full Git History Secret Audit [44973890902](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890902): **SUCCESS**.
- This closes the regression-test/CI issue only. It does not establish public HTTPS/WSS, production Redis host failover, authenticated snapshot transport/receipts, live Firebase-project E2E, or browser/Android WebView acceptance.
- Gate 10 remains **0/10 formally closed**. Host/operator-only: Gates 8, 30, 34, 35, 39. Integration/acceptance: Gates 20, 25, 31, 36, 38. Stage 1 remains **30/40 = 75% provisional**; no overall project percentage without approved stage weights/denominators.
- Indicator implementation unchanged: no formula, calculation, data contract, shared hook, renderer, chart UI or indicator test changed. No indicator progress credit. Full formula/index/prerequisite matrix remains below in this ledger and is not re-scored.
- ZERO COST. No deployment, paid service, production credential, Vercel/Cloudflare operation, Termux/device operation, or `main` modification.

## Batch 62J-123 — exact-head SQLite concurrency fix, CI artifacts and acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact tested source/test HEAD:** 589aceadd40b3b3e10e950566081101b2dd49003  
**Automated Tests [run 44985059074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074): SUCCESS**; **CodeQL [run 44985059102](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059102): SUCCESS**; **Full Git History Secret Audit [run 44985059070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059070): SUCCESS**. All three workflows target the exact tested HEAD. Automated Tests completed all 36 job steps with no failed steps.

### CI and artifact evidence
- Frontend unit tests/build, source and production-bundle credential scans, Android host preflight, backend dependency audit/tests, isolated Redis TLS CA/hostname fixture, synthetic SQLite outbox and metrics benchmarks, backend image build, shared-Redis/persistent-volume container smoke, Trivy scan/report export and dependency-audit enforcement all completed successfully.
- Synthetic metrics artifact [14739815366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739815366): full 899-series envelope. One worker: 32/32 flushes, 0 retries, p95 flush 14.34 ms. Four threads: 128/128, 4 retries, p95 flush 46.92 ms. Sixteen simultaneous threads: 512/512, 187 retries, p95 flush 627.74 ms and writer-lock p95 572.23 ms. Four independent processes: 128/128, 3 retries, p95 flush 141.71 ms. Startup-staggered 16-worker case: 512/512, 26 retries, p95 flush 266.53 ms and writer-lock p95 250.93 ms. SQLite integrity reported ok for every case.
- The benchmark confirms no lost flushes in these synthetic cases and exposes material same-file SQLite writer contention at higher concurrency. It is runner/filesystem-specific, uses synthetic operational counters, and is not production load, persistent-volume, multi-host or SLO evidence. Do not infer production capacity from it.
- Synthetic outbox artifact [14739423041](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739423041) is attached to this exact run; it remains local synthetic benchmark evidence, not live provider/WebSocket load acceptance.
- Trivy artifact [14739224531](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739224531) was independently inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, architecture amd64, digest sha256:5240158d55f11863aa41a49fbf4d00705d437519fcbdb0659164efc435ee58c0, size 571,352,064 bytes (~571.35 MB). The report contains 0 vulnerabilities in the scanned Alpine OS and Python package result groups. This is a point-in-time result for this exact amd64 image and scanner database, not a permanent guarantee, not a scan of every possible target, and not ARM64 evidence.
- Backend and frontend exact-head CI success proves the repository's configured tests and CI service topology only. The CI Redis fixture and ephemeral runner volume do not constitute owner-host acceptance.

### SQLite corrective change and remaining risk
- Commit 529031d3a6ae0d07cfcd2f38a5d7e02fffd81063 adds bounded retry for lock-only errors while applying connection-local PRAGMA synchronous=NORMAL to fresh SQLite connections. Commit 589aceadd40b3b3e10e950566081101b2dd49003 adds a 16-independent-collector, eight-round repeated concurrent-flush regression test.
- Exact-head backend tests and full CI pass. The prior fatal database-is-locked failure at connection PRAGMA setup was not reproduced in this run.
- The benchmark still shows substantial contention at 16 simultaneous workers (187 retries). Keep the collector classified as bounded same-host best-effort telemetry; do not claim high-concurrency production readiness. A single-writer queue/aggregation redesign would be a separate scoped architecture change, not silently bundled into this fix.

### WebSocket production acceptance disposition
- Source/gateway separation, Redis Streams consumer/replay, generation-scoped leases, apply-before-ACK, pending reclaim, fail-closed ownership and snapshot/replay recovery remain repository implementation evidence. Owner-supplied source snapshot verification and gateway installation callbacks remain trust boundaries requiring independent authentication of snapshot bytes, SHA-256, generation, cursor and per-gateway receipts.
- Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI result.
- Still missing owner-controlled evidence: Gate 8 secret injection/permissions/rotation/log redaction; Gate 20 real Firebase signed-token and entitlement grant/revoke/renew E2E; Gate 25 owner-host Redis TLS/CA/hostname, ACL, persistence/restart/failover, secret rotation and authenticated global snapshot/receipt alignment; Gate 30 live DB backup/restore; Gate 31 encrypted off-host backup and independent recovery-key custody; Gate 34 persistent volume UID/GID 10001/restart/disk-pressure; Gate 35 public hostname/trusted TLS/renewal; Gate 36 public HTTPS ticket exchange/WSS proxy, browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression; Gate 38 real dashboards/retention/alerts/disk pressure; Gate 39 external alert delivery, human acknowledgement and escalation.
- No public HTTPS/WSS endpoint, production Firebase project, owner-host Redis or production storage has been provisioned or verified. CI must not be used to close these gates.

### Architecture and zero-cost constraints
- Current workflow uses plain docker build on GitHub-hosted ubuntu-latest; Dockerfile base is python:3.12-alpine3.24. Exact artifact metadata is linux/amd64. ARM64 build and runtime smoke remain unverified; no multi-platform claim is made.
- Keep Redis private with strict TLS CA/hostname verification and least-privilege ACLs. Keep HTTPS ticket exchange before WSS; Firebase ID tokens must not be put in WSS URLs or raw WebSocket auth frames. Preserve separate source publisher and gateway replica roles and exact global snapshot/watermark alignment.
- ZERO COST: no deployment, host, account, resource, paid service, trial-credit dependency, production credential, Vercel/Cloudflare operation or device/Termux action. main remains untouched.

### Exact current indicator matrix at source/test HEAD 589aceadd40b3b3e10e950566081101b2dd49003

| Study / subsystem | Status | Calculation / first valid output | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of 20 closes; index 19 | Chart overlay, independent toggle, legend/latest value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; index 19 | Overlay, toggle, legend/latest value, stale clearing, renderer/lifecycle tests |
| RSI14 Wilder | 🟨 Foundation | Wilder-smoothed gains/losses over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend/latest value, stale clearing, renderer tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 × population SD; index 19 | Upper/middle/lower overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, per-series isolation and renderer integration |
| Footprint | 🟧 Simulated/reference-gated | Offline synthetic accumulator only; not exchange-native bid/ask truth | User reference + reviewed blueprint, validated source contract, ON-only spaced clusters, readable bid/ask cells, OFF-layout regression, interaction/performance/lifecycle tests |
| Heatmap | 🟥 Not implemented | No validated zero-cost source/data contract | User reference, source feasibility, data contract, reviewed blueprint, renderer, legend/scale/toggle/tests |
| Liquidation Maps | 🟥 Not implemented | No validated source/formula contract | Zero-cost source feasibility, validated calculation/data contract, reference/blueprint, renderer, scale/legend/tests |

**Shared invariants:** warm-up remains null, never zero; outputs align to source candle indices; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series; invalid bars and gaps are not silently converted to zero. Footprint OFF preserves standard candle spacing. No indicator completion credit is awarded by WebSocket CI, backend metrics fixes or documentation.

No aggregate indicator percentage is published without approved per-study weights and a completion denominator. Stage 1 30/40 provisional is project-stage accounting, not indicator completion. Stage 4 visible indicators remain behind the approved stage gate. Do not begin Footprint or Heatmap visual implementation before the user supplies reference image(s) and the scoped blueprint is reviewed.


## Batch 62J-126 reconciliation — WebSocket owner-host evidence and CI completion

- Exact parent `5b0cc02be04efbef3971aa313836eb171e877117` has Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS (runs 44986957808, 44986957788 and 44986957739 respectively).
- Additional audit confirms repository backup/restore validation is not owner-host recovery proof; encrypted off-host destination and independent recovery-key custody remain absent. Process-local metrics/local-log alerts do not prove central retained dashboards, external alert delivery, human acknowledgement or escalation. Android CI remains host-only, and backend container evidence is linux/amd64 only; ARM64 is unverified.
- WebSocket Gate 25/36 remain open; Gate 38/39 remain open. Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 provisional. No production acceptance is inferred from CI.
- Indicator statuses and requirements are unchanged. No source/test/formula/hook/renderer/UI changes and **zero indicator progress credit**. Six foundation studies/shared hook 🟨; Footprint 🟧 reference-gated; Heatmap and Liquidation Maps 🟥.
- Documentation-only, ZERO COST; `main` untouched.

## Batch 62J-127 — WebSocket acceptance reconciliation

Exact-parent CI for b7d0482ff8fa5906c006460583ad3b175f4c282c: Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS (runs 44987388625, 44987388511 and 44987388505). Operational-response audit distinguishes implemented user price-alert FCM delivery from local operator incident escalation: FCM uses owner-scoped encrypted device tokens and runtime ADC, while operator escalation currently writes local logs; no external operator paging/receipt is proven. Same-host SQLite metrics aggregation exists (15-minute buckets, 7-day retention) alongside process-local counters, but no central dashboard/off-host monitoring proof exists. Gates 8, 20, 38 and 39 remain open. Gate 10 is 0/10; Stage 1 is 30/40 provisional. Indicator statuses are unchanged and receive zero progress credit; six foundations/shared hook 🟨, Footprint 🟧 reference-gated, Heatmap/Liquidation Maps 🟥. Documentation-only, ZERO COST.


## Batch 62J-129 reconciliation — 22 November 2026

No indicator source, tests, calculations, hook, renderer or chart UI changed. No indicator implementation progress is credited. Current matrix remains: SMA20 🟨 (20-close mean, first valid index 19); EMA20 🟨 (SMA-seeded, alpha 2/21, index 19); RSI14 Wilder 🟨 (14 close changes, index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram 33); Bollinger20,2 🟨 (20-close mean ±2 population SD, index 19); Shared Indicator Hook 🟨 (validated aligned output, not chart-integrated); Footprint 🟧 (simulated educational accumulator, visual work gated on user reference and reviewed blueprint); Heatmap 🟥; Liquidation Maps 🟥.

Shared acceptance remains: warm-up nulls, candle-index alignment, prefix causality/no future-candle repaint, stale-series clearing on identity/timeframe changes, visible toggles/legends/current values, chart renderer/lifecycle tests. Footprint OFF preserves normal candle spacing; only explicit ON enables spaced clusters. Footprint/Heatmap visuals remain blocked until the user supplies reference image(s) and reviews the scoped blueprint. No aggregate indicator percentage without approved weights and denominator.

## IP3S — Indicator Proses Peningkatan Proyek Signifikan (introduced 22 November 2026)

IP3S is a per-work-cycle delivery-quality score, **not** an overall project completion percentage. Weights and full-credit rules:

| Dimension | Weight | Full-credit condition |
|---|---:|---|
| Verified engineering delta | 25 | Tested runtime/source improvement or independently verified acceptance evidence |
| Test/CI evidence | 20 | Relevant checks pass on exact HEAD; limitations are explicit |
| Blocker reduction | 20 | A real acceptance blocker is closed or its exact owner/action is isolated |
| Canonical documentation | 20 | Source-backed findings, status and next acceptance criteria are reconciled |
| Scope/cost integrity | 15 | Correct branch, honest evidence claims, ZERO COST and authorization boundaries respected |

Score each dimension from 0–100% and apply its weight. Documentation alone earns no runtime implementation points; CI cannot close owner-host or real-device gates. A newly clarified blocker earns only decision-readiness credit, not gate-closure credit.

**Batch 62J-129: 58/100** (0/25 engineering delta + 20/20 exact-head CI + 8/20 blocker reduction + 15/20 canonical documentation + 15/15 scope/cost integrity). This is a work-cycle quality score, not project completion. Keep it separate from Stage 1 30/40 = 75% provisional and Gate 10 0/10 formally closed.


## Batch 62J-137 reconciliation — 22 November 2026

WebSocket Gate 25 source/test audit refined the trust boundary: gateway runtime compares source/generation/cursor to durable checkpoint, but callback-returned SHA-256 is only syntax-checked because the replica has no durable immutable receipt. Publisher-side gateway installation mappings are validated as a consistent envelope, while actual gateway receipt authentication/retrieval is explicitly delegated to the owner-host callback. Local tests do not prove remote receipt authenticity or custody.

Receipt migration proposal is additive and separate from mutable checkpoint state. Existing checkpoints without receipts must remain LEGACY_UNATTESTED; never synthesize historical digest or attestation. Snapshot rows, checkpoint and receipt must commit atomically; same identity tuple + same digest is idempotent, while same tuple + conflicting digest/manifest fails closed. Generation ordering must use an explicit source/cursor policy, not lexical UUID order. Fourteen focused migration, conflict, rollback, restart, runtime-binding and owner-host tests are specified in the Batch 62J-137 report. No implementation/schema change was made.

No indicator source, tests, calculations, hook, renderer or chart UI changed. Indicator matrix remains unchanged: SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 foundation; Footprint 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps 🟥 unimplemented. No indicator progress credit or aggregate percentage.

Stage 1 remains 30/40 = 75% provisional; Stages 2–6 NOT SCORED/not officially opened; overall project NOT SCORED; Gate 10 remains 0/10 external criteria formally closed. WebSocket Gates 25, 36 and 38 remain OPEN. IP3S Batch 62J-137 is PENDING exact-HEAD CI; no numeric score until checks complete. ZERO COST; no deployment/credentials/device work; main untouched. See [Batch 62J-137](WORK_CYCLE_2026-11-22_BATCH62J137_GATE25_RECEIPT_TRUST_AND_MIGRATION.md).


## Batch 62J-138 reconciliation — 22 November 2026

Gate 25 acceptance sequence is now ordered into four executable layers: (A) legacy SQLite migration/idempotence, (B) atomic receipt transaction/idempotent replay/conflict rollback/restart, (C) gateway startup binding to a durable receipt before Redis creation, and (D) publisher owner-host receipt authentication/key lifecycle/replay/recovery. Source review confirms gateway factory currently compares callback source/generation/cursor with checkpoint and checks SHA-256 syntax, but has no durable digest receipt to compare. Publisher validates the evidence envelope while relying on the owner callback for authenticated remote receipt retrieval. Existing tests cover envelope mismatch and fail-closed startup but not durable receipt binding or owner-host trust. This is an acceptance gap, not proof of an unauthenticated remote exploit. No runtime/schema/test code changed.

No indicator implementation changed: SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic prototype/reference-gated; Heatmap and Liquidation Maps remain 🟥 unimplemented. No implementation progress credit.

Stage 1 remains 30/40 = 75% provisional; Stages 2–6 NOT SCORED/not officially opened; overall project NOT SCORED; Gate 10 0/10 external criteria formally closed. WebSocket Gates 25, 36 and 38 remain OPEN. IP3S Batch 62J-138 PENDING exact-HEAD CI; no numeric score until checks finish. ZERO COST; no paid services, deployment, credentials, device or Termux work; main untouched. See [Batch 62J-138](WORK_CYCLE_2026-11-22_BATCH62J138_GATE25_EXECUTABLE_ACCEPTANCE_SEQUENCE.md).


---

## Batch 62J-140 — WebSocket shutdown race hardening (22 November 2026)

No indicator calculation or renderer source changed. This WebSocket cycle receives **zero indicator implementation credit**.

| Indicator/component | Status | Verified state |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing foundation; first valid index 14 |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; not chart-integrated |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth |
| Heatmap | 🟥 Not implemented | Reference image(s) and reviewed blueprint required before visual implementation |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

Shared invariants: warm-up nulls; candle-index alignment; prefix causality/no future repaint; invalid/gapped bars never silently become zero; stale output cleared on symbol/venue/dataset/chart/timeframe changes. Footprint OFF preserves normal candle spacing; explicit ON alone switches to spaced cluster layout. Footprint and Heatmap visual implementation waits for user reference image(s) and reviewed blueprint.

Project-wide stage indicator:
- Stage 1 Foundation/Security/Data Integrity: 🟨 30/40 = 75% provisional.
- Stage 2 Market Data Infrastructure: ⬜ NOT SCORED/not officially opened.
- Stage 3 Chart Engine/Timeframe: ⬜ NOT SCORED/not officially opened.
- Stage 4 Indicators/Analytics: ⬜ NOT SCORED/not officially opened.
- Stage 5 Professional UI/Interactive Tools: ⬜ NOT SCORED/not officially opened.
- Stage 6 Hardening/Validation/APK Release: ⬜ NOT SCORED/not officially opened.
- Overall project: NOT SCORED until six-stage weights and denominator are approved.
- Gate 10: 0/10 external criteria formally closed.

IPS35/IP3S cycle score: PENDING exact-source-commit Automated Tests and CodeQL. Score dimensions: engineering delta 25; exact-commit automated/security CI 20; blocker isolation 20; canonical documentation 20; ZERO COST/scope integrity 15. No numeric score before CI acceptance.


## Batch 62J-144 — indicator reconciliation (22 November 2026)

No indicator formulas, numeric kernels, shared hook, renderer, UI or indicator tests changed. No indicator implementation credit is awarded.

| Indicator/component | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | Flat/monotonic/zero-loss edge cases, chart integration and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Numerical edge cases, chart integration, identity invalidation and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Variance/flat-series edge cases, chart integration and lifecycle |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output | Full chart integration, visible settings/legend/current values and stale-output clearing |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, licensed bid/ask data contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime/render implementation | User reference image(s), reviewed blueprint, validated depth/liquidity data contract and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/contract, reviewed design, renderer and tests |

Shared invariants: warm-up nulls; exact source-index alignment; prefix causality/no future-candle repaint; invalid/missing/gapped bars never silently become zero; stale-output clearing on symbol/venue/dataset/chart/timeframe changes; formula/rendering/interaction/lifecycle/accessibility/performance are separate acceptance dimensions. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual work remains blocked pending user reference image(s) and reviewed blueprint. Aggregate indicator completion remains NOT SCORED because weights and denominator are unapproved.

WebSocket-only lifecycle and auth test repairs receive zero indicator progress credit. See [Batch 62J-144 report](WORK_CYCLE_2026-11-22_BATCH62J144_MULTI_USER_WEBSOCKET_LIFECYCLE.md).


## Batch 62J-145 — indicator reconciliation (22 November 2026)

No indicator calculation, numeric kernel, shared hook, renderer, chart UI or indicator tests changed. The real TLS/WSS and multi-user transport test work receives **zero indicator implementation credit**.

| Indicator/component | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | Flat/monotonic/zero-loss edge cases, chart integration and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Numerical edge cases, chart integration, identity invalidation and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Variance/flat-series edge cases, chart integration and lifecycle |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output | Full chart integration, visible settings/legend/current values and stale-output clearing |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, licensed bid/ask data contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime/render implementation | User reference image(s), reviewed blueprint, validated depth/liquidity data contract and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/contract, reviewed design, renderer and tests |

Shared invariants remain: warm-up nulls; exact source-index alignment; prefix causality/no future-candle repaint; invalid/missing/gapped bars never silently become zero; stale-output clearing on symbol/venue/dataset/chart/timeframe changes; calculation/rendering/interaction/lifecycle/accessibility/performance are separate acceptance dimensions. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual work remains blocked pending user reference image(s) and reviewed blueprint. Aggregate indicator completion remains NOT SCORED because weights and denominator are unapproved.

See Batch 62J-145 work-cycle report. No progress percentage or color status changed for any indicator.


---

## Batch 62J-164 reconciliation — 23 November 2026

No indicator calculation, formula, shared hook, chart binding, renderer, UI, or indicator-specific test was changed. This backend WebSocket lifecycle correction earns **zero indicator implementation credit**.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance acceptance |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance acceptance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle/legend/value, identity/lifecycle/render acceptance |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, lines, histogram, zero guide, toggle/legend/value, lifecycle/render acceptance |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Three-line overlay, toggle/values, identity/lifecycle/render/performance acceptance |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and aligned calculation output | Hook tests, actual chart binding, stale clearing, settings/legend and identity lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, valid bid/ask source contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted data/renderer contract | Defensible provenance/calculation contract, reviewed blueprint, renderer and tests |

Invariants remain: warm-up nulls; exact candle-index alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Footprint/Heatmap visual work remains gated on user references and reviewed blueprint.

Indicator aggregate: **NOT SCORED** (no approved weights/denominator). Stage 1: 30/40 = 75% provisional. Stages 2–6: NOT SCORED/not officially opened. Gate 10: 0/10 external criteria formally closed. Overall project: NOT SCORED. CI for Batch 62J-164: pending exact HEAD. ZERO COST and main-branch protection remain in force.


---

## Batch 62J-165 — durable snapshot digest binding (23 November 2026)


No indicator formula, numeric kernel, shared hook, chart binding, renderer, UI, or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity/lifecycle/render/performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle/legend/value and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Three-line overlay, toggle/values, identity/lifecycle/render/performance |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and aligned calculation output | Hook tests, chart binding, stale clearing, settings/legend and identity lifecycle |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, valid bid/ask source contract, cluster renderer |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer/tests |
| Liquidation Maps | 🟥 Not implemented | No accepted data/renderer contract | Defensible provenance/calculation contract, reviewed blueprint, renderer/tests |

Shared invariants: warm-up nulls; exact candle-index alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Footprint/Heatmap visual work remains gated on user references and reviewed blueprint. Aggregate indicator progress remains NOT SCORED because approved weights and denominator do not exist.


---

## Batch 62J-166 — indicator reconciliation (23 November 2026)


No indicator code, formula, hook, renderer, UI, or test changed. Indicator progress credit: **0**.

| Indicator / subsystem | Status | Foundation / next acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; chart overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19; chart overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; 0–100 pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference + reviewed blueprint + valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference + reviewed blueprint + validated depth contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/contract and reviewed implementation required |

Preserve warm-up nulls, exact candle alignment, prefix causality/no future repaint, invalid/gapped-data rejection, stale-output clearing, and Footprint OFF normal candle spacing. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.


---

## Batch 62J-167 — indicator reconciliation (23 November 2026)


No indicator formula, numeric kernel, shared hook, chart binding, renderer, UI or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator / subsystem | Status | Foundation / remaining acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; chart overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA-seeded, alpha 2/21; first valid index 19; chart overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference + reviewed blueprint + valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference + reviewed blueprint + validated depth contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/contract and reviewed implementation required |

Preserve warm-up nulls, exact candle alignment, prefix causality/no future repaint, invalid/gapped-data rejection, stale-output clearing, and Footprint OFF standard candle spacing. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.


---

## Batch 62J-168 — indicator reconciliation (23 November 2026)


No indicator formula, kernel, hook, chart binding, renderer, UI, or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator | Status | Foundation / remaining acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA seed, alpha 2/21; first valid index 19; overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 population SD; first valid index 19; three-line overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference, reviewed blueprint and valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference, reviewed blueprint and validated depth/liquidity contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/calculation contract and reviewed implementation required |

Invariants: warm-up nulls; exact candle alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.


---

## Batch 62J-169 — indicator reconciliation (23 November 2026)


No indicator formula, numeric kernel, hook, chart binding, renderer, UI or indicator-specific test changed. Indicator implementation credit: **0**.

| Indicator | Status | Foundation / remaining acceptance |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19; overlay/toggle/legend/lifecycle remain |
| EMA20 | 🟨 Foundation | SMA seed, alpha 2/21; first valid index 19; overlay/toggle/legend/lifecycle remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; pane, 30/70 guides and lifecycle remain |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; pane/lines/histogram/zero guide remain |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 population SD; first valid index 19; three-line overlay/toggle/value/lifecycle remain |
| Shared Indicator Hook | 🟨 Foundation | Validated aligned backend output; chart binding, stale clearing and settings/legend remain |
| Footprint | 🟧 Prototype only | Synthetic accumulator; user reference, reviewed blueprint and valid bid/ask contract required |
| Heatmap | 🟥 Not implemented | User reference, reviewed blueprint and validated depth/liquidity contract required |
| Liquidation Maps | 🟥 Not implemented | Defensible data provenance/calculation contract and reviewed implementation required |

Invariants: warm-up nulls; exact candle alignment; prefix causality/no future repaint; reject invalid/gapped data; clear stale outputs on identity changes. Footprint OFF preserves standard candle spacing; explicit ON alone activates spaced clusters. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.


---

## Batch 62J-170 reconciliation — 23 November 2026

No indicator source, calculation, numerical test, shared hook, chart binding, renderer, toggle, legend, or pane changed in this backend Gate 25 batch. **Indicator implementation credit: zero.** The complete indicator states remain:

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, visibility toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle and render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation, lifecycle, render and performance tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot and aligned multi-study calculation output | Hook tests, actual chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance and calculation contract, reviewed blueprint, renderer and tests |

### Invariants and visual gates

- Warm-up outputs remain null, never fabricated zero.
- Values remain aligned to the exact source candle index.
- Prefix-causal: adding future candles cannot alter earlier output.
- Invalid/non-finite/gapped bars are rejected, not converted to zero.
- Stale outputs clear on symbol, venue, dataset, chart identity, or timeframe changes.
- No future-candle repaint.
- Calculation, rendering, interaction, lifecycle, accessibility, and performance are separate acceptance dimensions.
- Footprint OFF preserves ordinary candle spacing; explicit ON alone activates spaced clusters.
- Footprint and Heatmap visual implementation remains blocked until user reference image(s) are supplied and the scoped blueprint is reviewed.
- Aggregate indicator completion remains NOT SCORED because study weights and denominator are not approved.

This backend batch changes none of the above states. Indicator status colors are evidence states, not completion percentages.


---

## Batch 62J-171 — indicator reconciliation (23 November 2026)

No indicator source, formula, numerical kernel, hook, chart binding, renderer, pane, settings, or indicator-specific test changed in this Gate 38 metrics validation batch. **Indicator implementation credit: zero.**

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, visibility toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle and render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation, lifecycle, render and performance tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot and aligned multi-study calculation output | Hook tests, actual chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance and calculation contract, reviewed blueprint, renderer and tests |

### Preserved invariants and visual gates

- Warm-up outputs remain null, never fabricated zero.
- Values remain aligned to exact source candle indices; prefix causality and no future repaint remain mandatory.
- Invalid/non-finite/gapped bars must be rejected, not converted to zero.
- Stale outputs must clear on symbol, venue, dataset, chart identity, or timeframe changes.
- Calculation, rendering, interaction, lifecycle, accessibility, and performance remain separate acceptance dimensions.
- Footprint OFF preserves ordinary candle spacing; explicit ON alone activates spaced clusters.
- Footprint and Heatmap visual implementation remains blocked until user reference image(s) are supplied and the scoped blueprint is reviewed.
- Aggregate indicator completion remains NOT SCORED because study weights and denominator are not approved.


---

## Batch 62J-172 — WebSocket replica relay wire-format hardening (23 November 2026)

No indicator source, formula, numeric kernel, hook, chart binding, renderer, pane, settings, or indicator-specific tests changed. **Indicator implementation credit: zero.**

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, visibility toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle and render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation, lifecycle, render and performance tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot and aligned multi-study calculation output | Hook tests, actual chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance and calculation contract, reviewed blueprint, renderer and tests |

Preserve warm-up nulls, exact source-index alignment, prefix causality/no future repaint, invalid/gapped-data rejection, stale-output clearing on identity changes, and Footprint OFF standard candle spacing. Footprint/Heatmap visual implementation remains gated on user reference image(s) and reviewed blueprint. Aggregate indicator progress remains NOT SCORED without approved weights/denominator.


---

## Batch 62J-173 — indicator reconciliation (23 November 2026)

No indicator source, formula, numeric kernel, hook, chart binding, renderer, pane, settings, or indicator-specific test changed in the WebSocket replica relay hardening cycle. **Indicator implementation credit: zero.**

| Indicator / subsystem | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Candlestick overlay, visibility toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value, identity invalidation, lifecycle, render and performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle and render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; EMA9 signal/histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/latest values, lifecycle and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation, lifecycle, render and performance tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot and aligned multi-study calculation output | Hook tests, actual chart binding, stale-output clearing, settings/legend integration, identity/lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, verified bid/ask source contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance and calculation contract, reviewed blueprint, renderer and tests |

Invariants: warm-up nulls; exact source-index alignment; prefix causality/no future repaint; invalid/gapped-data rejection; stale-output clearing on identity changes; Footprint OFF preserves standard candle spacing. Footprint/Heatmap visuals remain gated on user reference images and blueprint review. Aggregate indicator progress remains NOT SCORED without approved weights and denominator.


---

## Batch 62J-176 — synthetic Worker/DO proof reconciliation (23 November 2026)

**Code/test HEAD:** `f9a6242c83c065799d1ed02f8c8870d8c9ef5ffe`  
**Infrastructure proof:** isolated synthetic-only Cloudflare Worker/Series Durable Object source, 16 passing Node tests, exact-HEAD Automated Tests + CodeQL + secret audit + OCI ARM64 readiness all successful.  
**Indicator implementation delta:** none.

This infrastructure batch does not alter any indicator formula, warm-up rule, source-index alignment, calculation hook, chart binding, overlay, pane, renderer, legend, setting, or indicator-specific regression test. Therefore all existing indicator acceptance statuses remain unchanged; no indicator implementation credit is awarded.

| Indicator / subsystem | Current status | Existing foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Chart overlay, toggle, legend/latest value, identity invalidation, lifecycle and render/performance tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Chart overlay, toggle, legend/latest value, identity invalidation, lifecycle and render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Initial 14-change mean and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value and lifecycle/render tests |
| MACD 12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Dedicated pane, lines/histogram/zero guide, toggle, legend/latest values and lifecycle/render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity invalidation and lifecycle/render tests |
| Shared Indicator Hook | 🟨 Foundation | Snapshot-backed aligned multi-study calculation | Hook tests, actual chart binding, stale-output clearing, settings/legend and lifecycle acceptance |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | Owner visual reference, reviewed blueprint, verified bid/ask data contract, spaced cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | Owner visual reference, validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible provenance/calculation contract, reviewed blueprint, renderer and tests |

**Global invariants remain mandatory:** warm-up values stay null; no future-candle leakage/repainting; invalid/gapped data rejected; stale output cleared on identity changes; Footprint OFF preserves ordinary candle spacing; Footprint ON alone activates the dedicated spaced cluster layout. Footprint and Heatmap visual implementation remain blocked until the owner supplies references and reviews the blueprint.

**Credit decision:** WebSocket/Worker infrastructure progress is not indicator progress. No status promotion or percentage increase is permitted from Batch 62J-176.


## Batch 62J-178 — 23 November 2026: WebSocket authentication timeout reconciliation

**Latest code/test HEAD:** `264b54fbb87b96133d13dd7f82089bde4cd9d47f`  
**Indicator calculation/renderer/UI modifications:** none. **Indicator credit:** zero.

All statuses remain unchanged:
- SMA20 🟨 Foundation
- EMA20 🟨 Foundation
- RSI14 Wilder 🟨 Foundation
- MACD12/26/9 🟨 Foundation
- Bollinger20,2 🟨 Foundation
- Shared Indicator Hook 🟨 Foundation
- Footprint 🟧 Synthetic prototype only
- Heatmap 🟥 Not implemented
- Liquidation Maps 🟥 Not implemented

The WebSocket timeout change does not increase indicator progress. Keep warm-up values null, exact index alignment, prefix causality, invalid/gap rejection, stale-output clearing, and no future-candle leakage. Footprint OFF retains ordinary candle spacing; Footprint ON alone enables spaced clusters. Footprint/Heatmap visuals remain blocked pending user reference images and blueprint review. Aggregate indicator completion remains **NOT SCORED**.

Full technical record: `docs/WORK_CYCLE_2026-11-23_BATCH62J178_WEBSOCKET_AUTH_TIMEOUT.md`.


---

## Batch 62J-179 — 23 November 2026: WebSocket hardening impact

- SMA20 🟨 Foundation — unchanged; 20-close mean, first valid index 19.
- EMA20 🟨 Foundation — unchanged; SMA seed, alpha 2/21, first valid index 19.
- RSI14 Wilder 🟨 Foundation — unchanged; initial 14-change average and Wilder recurrence, first valid index 14.
- MACD 12/26/9 🟨 Foundation — unchanged; EMA12−EMA26, first MACD index 25, signal/histogram index 33.
- Bollinger20,2 🟨 Foundation — unchanged; 20-close mean ±2 population standard deviations, first valid index 19.
- Shared Indicator Hook 🟨 Foundation — unchanged; exact-snapshot alignment foundation only.
- Footprint 🟧 Synthetic prototype only — unchanged; user reference image(s) and scoped blueprint review remain mandatory before visual implementation.
- Heatmap 🟥 Not implemented — unchanged; user reference image(s) and scoped blueprint review remain mandatory.
- Liquidation Maps 🟥 Not implemented — unchanged; methodology/provenance and blueprint remain outstanding.

No indicator code or visual implementation was changed in Batch 62J-179. Core invariants remain warm-up null, exact candle-index alignment, prefix causality/no future leakage, invalid/gap rejection, stale-output clearing on identity/timeframe changes, and separate calculation/render/interaction/lifecycle/accessibility/performance acceptance. Footprint OFF preserves standard candle spacing; ON alone enables spaced clusters. Indicator aggregate remains **NOT SCORED**.

Batch 62J-179 addressed two adjacent WebSocket safeguards only: constructor resilience when closing malformed restored sockets throws, and complete attachment validation before synthetic fan-out. Full technical record: `docs/WORK_CYCLE_2026-11-23_BATCH62J179_WEBSOCKET_RESTORED_SOCKET_HARDENING.md`.


### Batch 62J-180 — CI regression correction

The latest CI failure on `2591e6071ba966114895256e51aa3fb99ea8001f` was traced to a malformed test callback: an `await` appeared inside a synchronous test function. Fixed by marking the test callback `async`, committed as `ae9a6368f824e4c2fac2b1c9d18ad2fba9fc41ca`. This changes test syntax only; indicator implementation and mathematical foundations are unchanged. Re-run status is pending verification. All indicator statuses and invariants listed above remain unchanged.


### Batch 62J-180 — alarm assertion follow-up

The async test callback correction allowed all 25 cases to execute. CI then reported 24/25: the alarm test expected the pending socket deadline even though the expired socket had an earlier deadline. The implementation's earliest-deadline scheduling was correct; the assertion was wrong. The test now expects the expired socket's deadline before alarm processing, then verifies rescheduling to the pending deadline afterward. Fix commit: `b0cc4682156e65ce94f8f4203899f3e7baee3070`. Indicator code and statuses remain unchanged.


### Batch 62J-180 — final CI result

The corrected branch checkpoint `07186190e98a4e9418664990a1a84acbc6fb3e13` completed successfully. Synthetic Worker test step: **25 passed, 0 failed**. Frontend unit tests/build, backend tests, backend container smoke test, dependency audits, secret-history audit, CodeQL (JavaScript/TypeScript and Python), and OCI ARM64 readiness all succeeded. This CI result validates the existing indicator ledger documentation only; no indicator calculation or renderer implementation changed in this batch. Indicator statuses and invariants remain unchanged.


---

## Batch 62J-181/182 — CME session identity frontend integration (23 November 2026)

Market-data infrastructure work only. No indicator calculation, warm-up rule, index alignment, chart renderer, pane, overlay, setting, legend, or indicator-specific test was changed. Therefore indicator statuses and credit remain unchanged:

- SMA20 🟨 Foundation
- EMA20 🟨 Foundation
- RSI14 Wilder 🟨 Foundation
- MACD12/26/9 🟨 Foundation
- Bollinger20,2 🟨 Foundation
- Shared Indicator Hook 🟨 Foundation
- Footprint 🟧 Synthetic prototype only
- Heatmap 🟥 Not implemented
- Liquidation Maps 🟥 Not implemented

The frontend now validates and preserves exact `CME_SESSION_V1` calendar identity for 1D/1W/1M/3M only when both calendar ID and a uniquely loaded version are supplied. This does not increase indicator progress. Aggregate indicator completion remains **NOT SCORED**.


---

## Batch 62J-209 — checkpoint reconciliation and indicator evidence (24 November 2026)

This entry records documentation and evidence status only. No indicator runtime, calculation, renderer, chart layout, or test implementation changed.

### Reference custody
- Original user-provided images `Footprint Indicator Reference 1` and `Footprint Indicator Reference 2` are recorded in ChatGPT Saved Reference Images.
- The Git repository contains the reference descriptions and acceptance requirements, not the original binary images. Do not claim the binaries are committed to Git.
- At Stage 4, supply the actual saved image assets to the implementation agent as visual inputs. Do not substitute generic/generated examples.

### Status by indicator
- SMA 20, EMA 20, RSI 14 Wilder, MACD 12/26/9, Bollinger 20,2, Shared Indicator Hook: 🟨 calculation/shared-hook foundation only; visible chart integration and acceptance remain outstanding.
- Footprint PRO 2GD: 🟧 synthetic/offline prototype and reference requirements recorded; real bid/ask provenance, reviewed blueprint, and dedicated renderer remain outstanding.
- Heatmap: 🟥 not implemented; owner visual reference and depth/liquidity data contract outstanding.
- Liquidation Maps: 🟥 not implemented; methodology, data provenance, and owner visual reference outstanding.
- Volume Profile / Complete Volume Profile: tier classification is recorded; implementation status must be established from code/tests before claiming completion.

### Accounting rules
- Named calculation/shared-hook test count previously recorded: 17 calculation cases + 7 hook cases = 24 named cases. This is not a count of visible indicators or full chart integrations.
- No aggregate indicator completion percentage is published because an approved weighted denominator is absent.
- No indicator progress credit is added in this batch.


---

## Batch 62J-215 — indicator status carry-forward (24 November 2026)

The exact-HEAD implementation through `fa8dca9abdb0f7b9aef8c10025346eb8c35023ab` did not modify indicator calculation, shared-hook, or chart-renderer source. Focused test inventory remains 17 calculation cases + 7 shared-hook cases = 24 named cases; these are not 24 completed indicators. `CandlestickChart.tsx` still imports neither `useMarketIndicators` nor `calculateIndicators` and continues to render one ordinary candlestick series.

- SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2: 🟦 calculation foundations only; visible chart integration remains outstanding.
- Shared Indicator Hook: 🟦 exact-snapshot/cache foundation; visible chart integration remains outstanding.
- Volume Profile (Mid Tier): 🟥 no production implementation verified.
- Complete Volume Profile (Exclusive Pro): 🟥 no complete implementation verified.
- Compact movable-range Volume Profile Tool: 🟥 requirement only; separate from Complete Volume Profile.
- Footprint PRO 2GD: 🟧 synthetic/offline prototype; exact saved owner references and ON-only spaced cluster behavior remain mandatory.
- Heatmap: 🟥 no accepted depth/liquidity engine or renderer.
- Liquidation Maps: 🟥 no defensible production methodology/provenance or renderer.

Low Tier inventory (15 studies) and Mid Tier additional inventory (~10 studies) remain incomplete owner decisions. Aggregate indicator completion remains NOT SCORED. General CI, backend test counts, and security scans award no indicator progress credit. See [Batch 62J-215 project reconciliation](WORK_CYCLE_2026-11-24_BATCH62J215_GATE25_EXACT_HEAD_CI_AND_INDICATOR_RECONCILIATION.md) and [Batch 62J-212 full indicator matrix](INDICATOR_PROGRESS_2026-11-24_BATCH62J212.md).


## Batch 62J-216 — indicator carry-forward (24 November 2026)

No indicator calculation, hook, or chart renderer source changed. Focused test inventory remains 17 calculation cases + 7 shared-hook cases = 24 named cases, not 24 completed indicators. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2, and the shared hook remain 🟦 foundations only. Footprint PRO 2GD remains 🟧 synthetic/offline prototype; Volume Profile, Complete Volume Profile, compact movable-range Volume Profile Tool, Heatmap, and Liquidation Maps remain 🟥. Low Tier and Mid Tier final inventories remain incomplete owner decisions. Aggregate indicator completion remains NOT SCORED. See [Batch 62J-216](WORK_CYCLE_2026-11-24_BATCH62J216_TRANSIENT_NPM_AUDIT_HARDENING.md).


---

## Batch 62J-225 — exact-head reconciliation and current production blockers (24 November 2026)

**Audited branch:** `phase-2/market-data-foundation`  
**Pre-documentation HEAD:** `2d56e8c079801bcbaa1c47963844c31736476589`  
**Exact-HEAD CI:** 4/4 configured workflows terminal SUCCESS  
**Scope:** documentation reconciliation only; no runtime source, tests, dependencies, secrets, deployment, or paid services changed.

### Exact-HEAD workflow evidence

All four workflow runs report the exact SHA `2d56e8c079801bcbaa1c47963844c31736476589` and terminal `completed / success`:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | [45417603350](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417603350) | 🟩 SUCCESS |
| CodeQL Security Analysis | [45417602448](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417602448) | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | [45417606609](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417606609) | 🟩 SUCCESS |
| Full Git History Secret Audit | [45417602216](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45417602216) | 🟩 SUCCESS |

No workflow was queued or in progress in the exact-SHA query. This is GitHub CI evidence, not public production WSS, live market-data, owner-host or Android physical-device acceptance.

### WebSocket / Gate 25 / infrastructure status

- 🟩 Repository foundations: protocol validation, ticket/authentication enforcement, reconnect/sequence/replay and Redis replica/recovery logic; Batch 223 shared-series owner consistency has exact-head CI acceptance.
- 🟩 Gate 25 repository-side checks: owner-pinned Ed25519 allow-list, persisted receipt signature re-verification, identity/key binding, durable checkpoint digest comparison and fail-closed validation before Redis client construction.
- 🟥 Gate 25 external acceptance remains OPEN: owner private-key custody, authenticated owner-host callback transport, actual signed snapshot transfer, retrieval of each gateway's persisted immutable receipt, restart-time re-verification and multi-gateway durable high-water acknowledgement.
- 🟥 Gate 36 remains OPEN: public HTTPS/WSS and reverse proxy/TLS, independent runtime/Fluid Compute read-back, Android-native WSS lifecycle and production multi-instance fan-out.
- 🟥 Firebase production sign-in/revocation/entitlement E2E remains OPEN.
- 🟥 Redis destructive retention remains BLOCKED until gateway inventory/retirement, pending-entry policy, per-gateway durable floor acknowledgements, separate retention authority and crash-safe trim/reconcile are accepted. XTRIM/XDEL and consumer-group destruction remain unauthorized.
- No external host credentials, private keys, production endpoint or second device were available to verify. Do not convert repository tests or synthetic preview evidence into production acceptance.

### Indicator ledger — no score inflation

| Indicator | Verified foundation | Visible chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close mean; first valid index 19 | Not integrated | 🟨 Foundation |
| EMA20 | SMA-seeded; alpha 2/21; first valid index 19 | Not integrated | 🟨 Foundation |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | No 0–100 pane/30–70 guides | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; signal EMA9; histogram identity; MACD index 25, signal/histogram 33 | No pane/lines/histogram | 🟨 Foundation |
| Bollinger20,2 | Population standard deviation; mean ± 2σ; first valid index 19 | No three-line overlay/fill | 🟨 Foundation |
| Shared Indicator Hook | Exact keyed immutable snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Owner references recorded; renderer gated | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP tool | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | No accepted depth/liquidity engine and renderer | Not integrated; owner reference/data contract required | 🟥 Open |
| Liquidation Maps | No accepted methodology/provenance/renderer | Not integrated | 🟥 Open |

Focused test inventory remains 17 calculation-engine + 7 shared-hook = 24 named tests; it is not a completion percentage. Footprint OFF must preserve ordinary candle spacing; explicit ON alone enables the spaced-cluster layout. Indicator visual expansion remains behind the official Stage 4 gate, scoped blueprint and owner review. Aggregate indicator completion remains **NOT SCORED** because no approved denominator/weights exist.

### Official progress accounting

- Stage 1: **30/40 criteria = 300/400 ticks = 75% provisional**; previously recorded, not independently re-audited in this documentation cycle.
- Gate 10: **0/10 formally closed**; external acceptance remains OPEN.
- Stage 2: active engineering, denominator not approved — 🟦 NOT SCORED.
- Stages 3–6: ⬜ NOT SCORED.
- Overall project: ⚪ NOT SCORED; no approved weighted denominator.
- Aggregate indicators: ⚪ NOT SCORED.
- IP3S/significant progress: ⚪ NOT SCORED; no approved scoring formula applied.

Do not extrapolate Stage 1's provisional 75% to total project completion. No Stage 1 ticks or indicator credit are awarded by this documentation reconciliation.

### Execution order retained

1. Continue only source-backed repository work that does not cross the owner-review boundary.
2. Gate 25 next requires real owner-host authenticated transfer and durable remote receipt/restart evidence; no callback-only simulation is sufficient.
3. Then public WSS/TLS and Firebase production E2E.
4. Then browser/Android real-device lifecycle and production multi-instance recovery.
5. Keep Redis destructive retention blocked until its independent safety contract passes.
6. Keep indicator UI work behind Stage 4 and its approved blueprint/review.

**Constraints:** ZERO COST; active branch only; `main` untouched; no Vercel deployment; target remains approximately 24 December 2026 as a planning target, not a guarantee.


---

## Batch 62J-226 — indicator test-count correction (24 November 2026)

A fresh declaration-level audit of the current branch source supersedes the earlier current-count statements in this document. Counting each `it(...)` declaration in the two focused suites gives:

- `src/indicators/indicatorCalculations.test.ts`: **21 named tests**.
- `src/indicators/useMarketIndicators.test.ts`: **7 named tests**.
- **Current focused indicator total: 28 named tests (21 + 7).**

This is a source declaration count, not a claim that 28 indicators are implemented or that all 28 passed independently. Exact-head Automated Tests workflow is the pass/fail authority. Older batch entries recording 17 + 7 = 24 are retained as historical counts at their respective earlier source revisions and must not be read as the current count. Indicator aggregate completion remains NOT SCORED; no visual-integration credit is awarded. The calculations and hook remain foundations until chart binding, controls, pane/overlay rendering, identity/lifecycle clearing and render-level acceptance are complete.


---

## Batch 62J-227 — exact-HEAD CI closure, WebSocket boundary re-audit, and indicator ledger synchronization (24 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Audited source/documentation HEAD:** `435dc3faa564d2afae6b5e7a3cb717c6232d4d08`  
**Exact-HEAD CI:** 4/4 configured workflows terminal SUCCESS  
**Cost:** ZERO COST • **main:** untouched • **Vercel:** no deployment  
**Delivery target:** approximately 24 December 2026 (planning target, not a guarantee)

### 1. Exact-HEAD CI — all workflows terminal

The branch HEAD was checked before this documentation update. All four workflow runs below reference the exact SHA `435dc3faa564d2afae6b5e7a3cb717c6232d4d08`, and each run plus its job steps is terminal SUCCESS:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | [45427397505](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397505) | 🟩 SUCCESS |
| CodeQL Security Analysis | [45427397419](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397419) | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | [45427397478](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397478) | 🟩 SUCCESS |
| Full Git History Secret Audit | [45427397474](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45427397474) | 🟩 SUCCESS |

Automated Tests completed all 39/39 listed steps, including frontend unit tests/build, backend tests, isolated Redis TLS CA/hostname fixture, synthetic Worker/Workerd and Durable Object checks, Android host/release preflight checks, dependency audits, backend container build/smoke and image scan/report steps. CodeQL completed Python and JavaScript/TypeScript. ARM64 completed all 7/7 steps. Secret-history audit completed all 6/6 steps. No exact-HEAD workflow remained queued or in progress at the time of this audit.

This closes the CI wait from Batch 62J-226. It does not establish public production WSS, Firebase production E2E, owner-host snapshot transport, or physical-device acceptance.

### 2. WebSocket / Gate 25 source boundary re-audit

Read current branch source:
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/snapshot_attestation.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- the latest Gate 25 and cross-path acceptance records.

Confirmed repository-side controls include owner-pinned Ed25519 trust keys, deterministic snapshot attestation verification, immutable persisted receipt re-verification, authenticated source/key binding, checkpoint/receipt cursor and digest equality, retention/schema/protocol validation, and fail-closed ordering before Redis client construction. The runtime closes a Redis client if consumer construction fails. No new source defect was established by this targeted re-audit; no speculative runtime edit was made.

External acceptance remains open and cannot be manufactured in repository tests:
1. Authenticated owner-host snapshot transfer and retrieval of each gateway's persisted immutable receipt.
2. Restart/re-verification and durable high-water acknowledgement from every gateway.
3. Public HTTPS/WSS endpoint, reverse proxy and TLS proof.
4. Firebase production sign-in, entitlement and revocation E2E.
5. Browser/Android lifecycle, process-death recovery, network handover and production multi-instance failover.
6. Redis destructive retention only after gateway inventory/retirement, pending-entry policy, per-gateway floor acknowledgements, separate authority and crash-safe trim/reconcile are proven.

No production secrets, private keys, host, domain, paid service, or destructive Redis operation was introduced. XTRIM/XDEL and consumer-group destruction remain unauthorized.

### 3. Indicator inventory — declaration-level recount

A fresh source count at `435dc3faa564d2afae6b5e7a3cb717c6232d4d08` confirms:
- `src/indicators/indicatorCalculations.test.ts`: **21** named `it(...)` tests.
- `src/indicators/useMarketIndicators.test.ts`: **7** named `it(...)` tests.
- Focused indicator total: **28 named tests (21 + 7)**.

The exact-HEAD Automated Tests workflow succeeded. The count is test inventory, not indicator count or a completion percentage.

| Indicator / subsystem | Verified calculation or data foundation | Visible chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid source index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 Foundation |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides absent | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; MACD index 25, signal/histogram 33 | Pane, lines, histogram, zero guide absent | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay, fill, toggle and latest values absent | 🟨 Foundation |
| Shared Indicator Hook | Exact keyed immutable backend snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Visual renderer remains gated; user references recorded | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP tool | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | No accepted depth/liquidity engine and renderer | Not integrated; reference and validated depth contract still required | 🟥 Open |
| Liquidation Maps | No accepted methodology/provenance and renderer | Not integrated | 🟥 Open |

Footprint OFF must preserve normal candlestick spacing; explicit ON alone activates the dedicated spaced-cluster layout. Footprint and Heatmap visuals remain reference/blueprint gated. Major indicator chart integration remains behind the official Stage 4 gate and scoped user-reviewed blueprint. The older 24-test count in historical batch entries remains historical; this 28-test recount is the current source inventory. **Aggregate indicator progress remains NOT SCORED.**

### 4. Official progress dashboard — no score inflation

| Meter | Verified value | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 criteria = 300/400 ticks = 75% provisional | 🟨 Active; inherited baseline, not re-scored in this batch |
| Stage 2 — Market Data Infrastructure | Active engineering; no approved denominator | 🟦 Active / NOT SCORED |
| Stage 3 | Not officially opened/scored | ⬜ NOT SCORED |
| Stage 4 | Waiting on stage gate / approved blueprint | 🟪 Gated / NOT SCORED |
| Stage 5 | Not officially opened/scored | ⬜ NOT SCORED |
| Stage 6 | Not officially opened/scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 Open |
| Overall project | No approved six-stage weighted denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved indicator denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved scoring formula applied | ⚪ NOT SCORED |

Do not extrapolate Stage 1's provisional 75% to total project completion. This documentation/CI batch awards no stage ticks, no indicator integration credit and no external WebSocket gate closure.

### 5. Execution order retained

Continue repository-verifiable work first; then real owner-host authenticated transfer and durable receipt/restart proof (Gate 25); then public WSS/TLS and Firebase production E2E; then browser/Android lifecycle and multi-instance recovery; then Redis retention only after its safety contract. Indicator UI remains behind Stage 4 and its blueprint/review gate. No branch change, deployment, or paid service is authorized by this record.


---

## Batch 62J-228 — WebSocket color taxonomy and parent-gate roll-up correction (24 November 2026)

**Audited HEAD:** `f3ca6becff4d72ba1638e4cf0233366f5d3368bb`  
**Branch:** `phase-2/market-data-foundation`  
**Exact-HEAD CI:** 4/4 terminal SUCCESS  
**Scope:** status semantics and acceptance accounting; no runtime source changed  
**Cost:** ZERO COST • `main` untouched • Vercel deployment deferred

### Why a WebSocket sub-status can be yellow/green while the overall gate is red

There was no demonstrated code regression between the previous yellow/partial indication and the red end-to-end gate indication. The colors had been used at different scopes without a clear legend. A repository-side capability can be green or yellow while the parent production-acceptance gate remains red because external proof is still missing. These are separate dimensions, not a downgrade of the same test result.

The following color legend is now authoritative for new progress entries:

| Color | Meaning | What it does not mean |
|---|---|---|
| 🟩 Green | The named criterion is implemented and verified at the stated scope, with evidence | Does not automatically close its parent production gate |
| 🟨 Yellow | Partial foundation or repository-side capability exists; additional integration/acceptance remains | Does not mean production acceptance is complete |
| 🟧 Orange | Gated or blocked on a prerequisite, owner input, reference, or safety condition | Does not imply a code failure |
| 🟥 Red | The named acceptance criterion or parent end-to-end gate remains unmet/open | Does not mean already-green repository tests regressed |
| 🟦 Blue | Active work or CI currently running | Not a pass/fail result |
| 🟪 Purple | Stage/blueprint gate prevents implementation from starting | Not a defect report |
| ⬜ Grey | Not started / not yet assessed | Not evidence of failure |
| ⚪ Neutral | No approved denominator or score | Never convert to a guessed percentage |

### Canonical WebSocket roll-up at this HEAD

| Scope | Current status | Evidence / remaining acceptance |
|---|---|---|
| Browser protocol, ticket/authentication, replay and reconnect foundations | 🟩 Repository-verified | Existing source and exact-HEAD CI coverage |
| Redis replica, replay, recovery and consumer lifecycle foundations | 🟩 Repository-verified | Existing backend suites and synthetic Redis fixtures |
| Gate 25 owner-pinned Ed25519 verification, immutable receipt re-verification, source/key binding and fail-before-Redis | 🟩 Repository-verified | Batch 62J-221 source/test contract and exact-HEAD CI |
| Gate 25 owner-host private-key custody, authenticated remote transfer, each gateway's persisted receipt retrieval, restart re-verification and per-gateway durable high-water ACK | 🟥 External acceptance open | Requires actual owner-controlled host/gateway evidence; repository callback tests cannot prove remote custody or network authentication |
| Gate 25 parent acceptance | 🟥 OPEN | Parent gate closes only after all required external owner-host evidence is accepted |
| Gate 36 public HTTPS/WSS, reverse proxy/TLS, production runtime and physical Android lifecycle | 🟥 OPEN | Requires public endpoint and real deployment/device evidence |
| Firebase production sign-in, entitlement and revocation E2E | 🟥 OPEN | Requires owner-controlled Firebase project evidence |
| Browser/Android process-death, network handover, production multi-instance failover | 🟨/🟥 PARTIAL / OPEN | Repository foundations exist; deployed browser and real-device/host acceptance incomplete |
| Redis destructive retention | 🟧 BLOCKED | No XTRIM/XDEL/group destruction until gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile are proven |
| Whole WebSocket production end-to-end | 🟥 NOT COMPLETE | Parent status is determined by outstanding external acceptance, not the green repository rows |

**Important:** A green sub-row does not make Gate 25 or the complete WebSocket green. Likewise, a red parent gate does not invalidate a previously successful unit test or CI run. Future dashboards must show the scope next to every colored status.

### Exact-HEAD CI read-back

At `f3ca6becff4d72ba1638e4cf0233366f5d3368bb`, all configured workflows are terminal SUCCESS, with every reported job step completed and no failed steps:

- Automated Tests: [45428878737](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878737) — 41/41 steps.
- Full Git History Secret Audit: [45428878666](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878666) — 6/6 steps.
- CodeQL: [45428879181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428879181) — JavaScript/TypeScript 8/8 and Python 8/8.
- OCI ARM64: [45428878741](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45428878741) — 7/7 steps.

This 4/4 result applies to this exact HEAD only. It is repository CI, not external production acceptance.

### Indicator progress reconciliation — no score inflation

| Indicator / subsystem | Current evidence | Chart/UI state | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay/toggle/legend/latest value/lifecycle absent | 🟨 Foundation |
| EMA20 | SMA-seeded EMA, alpha 2/21; first valid index 19 | Overlay/toggle/legend/latest value/lifecycle absent | 🟨 Foundation |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | Pane and 30/70 guides absent | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; first MACD index 25, signal/histogram index 33 | Pane/lines/histogram/zero guide absent | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay/fill/toggle/latest values absent | 🟨 Foundation |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating, stale-output clearing | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated; two user reference images on record | 🟧 Gated |
| Volume Profile / Complete VP / movable-range VP | No complete production implementation verified | Not integrated | 🟥 Open |
| Heatmap | Depth/liquidity engine and accepted renderer not verified | Visual implementation remains gated; user reference/data contract outstanding | 🟥 Open |
| Liquidation Maps | Methodology/provenance and renderer not accepted | Not integrated | 🟥 Open |

Focused test declaration inventory remains **28 total = 21 calculation tests + 7 shared-hook tests**. This is not a count of completed indicators or a completion percentage. All 28 are declarations in the two focused test files; exact-HEAD CI is the pass/fail authority. Older 24-count notes are historical source snapshots, not current inventory.

Footprint OFF must retain standard candle spacing; explicit ON alone enables the spaced-cluster layout. Footprint/Heatmap visual work and major chart integration remain behind the required stage/blueprint/user-review gates. Aggregate indicator progress stays NOT SCORED.

### Project progress dashboard — unchanged scores

| Meter | Current value | Status |
|---|---:|---|
| Stage 1 Foundation | 30/40 = 75% provisional; inherited baseline, not independently re-audited in this cycle | 🟨 |
| Stage 2 Market Data Infrastructure | Active; denominator not approved | 🟦 NOT SCORED |
| Stage 3 Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 Indicators & Analytics | Stage gate / blueprint required | 🟪 NOT SCORED |
| Stage 5 Professional UI & Interactive Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 Hardening, Validation & APK Release | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved formula applied | ⚪ NOT SCORED |

No stage tick, indicator integration credit, Gate 25 external acceptance, or overall percentage is awarded by this documentation/status correction.

### Work order remains unchanged

1. Continue repository-verifiable work and exact-HEAD CI.
2. Close Gate 25 with actual owner-host authenticated transfer, persisted receipt retrieval, restart verification and durable high-water ACK from every gateway.
3. Close public WSS/TLS and Firebase production E2E.
4. Complete browser/Android lifecycle and production multi-instance recovery.
5. Consider Redis destructive retention only after all independent safety prerequisites pass.
6. Keep indicator chart UI behind Stage 4 and its scoped approved blueprint/user review.

No paid service, production credential, domain, deployment, or destructive Redis action was used. APK planning target remains approximately 24 December 2026, not end-of-month.



# Offline WebSocket fixture correction — Batch 62J-241 (25 November 2026)

**Parent HEAD:** `d7581d72bfa9b34856c58e9cc807cc5d6ee84c2a`  
**Scope:** correct the synthetic route regression fixture to satisfy canonical instrument metadata validation.  
**ZERO COST:** no external service or network adapter introduced.

## CI failure diagnosis

The exact-HEAD Automated Tests run failed in one newly added route-level test before it reached the WebSocket handshake. The test constructed a `CanonicalInstrument` with an empty `session_calendar_id`; the canonical identity contract rejects an explicitly supplied empty string. This is a fixture construction defect, not evidence of a coordinator, route, lease, or adapter runtime failure.

The fixture now supplies the non-empty test-only identifier `SYNTHETIC_24X7`. Its requested series continues to use the UTC fixed bucket policy with empty request calendar identity, so no production calendar release is selected or required. No production instrument validation rule is weakened.

## Regression scope retained

The test still verifies two authenticated offline-fixture WebSocket subscribers share one in-memory demand, the first disconnect leaves the second lease active, and the final disconnect releases the last lease and empties the adapter active set. No live provider is invoked.

## Verification disposition

The prior SHA `d7581d72bfa9b34856c58e9cc807cc5d6ee84c2a` had 3/4 workflows successful; Automated Tests failed with 1 failed, 1,410 passed, 1 skipped. This correction requires fresh exact-HEAD CI. Do not inherit the parent result as success.

## Indicator ledger

No indicator calculation or rendering code changes in this batch. Existing calculation foundations, chart-integration gaps, Footprint visual gate and Heatmap reference gate remain unchanged. No completion credit is added.

## WebSocket status

Synthetic/offline route acquire/release code is present. Its route regression remains **🟨 pending exact-HEAD CI** until the corrected test passes. External provider lifecycle, provider ACK, cross-process demand ownership and public WSS/client acceptance remain open; this batch does not claim those gates.

## Project constraints

No Vercel deployment, no `main` update, no live market-data integration, no paid service and no destructive Redis retention change. Target remains around 24 December 2026 as a planning target.


---

# Exact-HEAD reconciliation — Work Cycle 64 (25 November 2026)

**Audited HEAD:** `6b4eedc2387e5e8a300e78c713861e2efa156678` on `phase-2/market-data-foundation`. The four workflows on this exact SHA are terminal SUCCESS: Automated Tests run 45541050465 (41/41 steps; **1,419 passed, 1 skipped, 6 warnings in 51.92s**), CodeQL run 45541050505 (JavaScript/TypeScript 8/8 and Python 8/8), OCI ARM64 run 45541050539 (7/7), and Full Git History Secret Audit run 45541050527 (6/6). All jobs/steps are completed; none remains running.

The single skipped test is `tests/test_shared_guard_tls_integration.py:22` because the isolated Redis TLS fixture was not configured for that invocation. A separate CI Redis TLS CA/hostname enforcement step passed, but neither result establishes owner-host or public production TLS acceptance. This exact-head result supersedes the earlier ledger's stale exact-head CI reference; historical Batch 62J-244 statements remain historical and are not rewritten.

**No indicator source, tests, or chart integration changed.** The full inventory and statuses remain as listed in the preceding current reconciliation. `CandlestickChart.tsx` still does not import/call `useMarketIndicators`; calculation declarations remain 21 + 7 hook declarations, not completion. SMA20/EMA20/RSI14/MACD12-26-9/Bollinger20,2/shared hook 🟨 foundation; Footprint PRO 🟧 gated; Volume Profile family/Heatmap/Liquidation Maps 🟥 open. Aggregate indicator completion ⚪ NOT SCORED because no approved denominator exists.

External Gate 25, Gate 36 and Firebase/client production acceptance remain 🟥 OPEN; Redis destructive retention remains 🟧 BLOCKED. CI success is repository evidence, not production gate closure. See `docs/WORK_CYCLE_2026-11-25_BATCH64_EXACT_HEAD_CI_AND_MULTI_GATE_AUDIT.md` for the complete evidence and ordered next actions.


---

# Indicator reconciliation — Work Cycle 66 (25 November 2026)

**Source/test scope:** concurrent offline provider-demand release regression tests.  
**Indicator source changes:** none. **Indicator completion credit:** zero.

The two new concurrency tests affect only `backend/tests/test_provider_demand.py`. No calculation engine, shared indicator hook, chart component, renderer, indicator UI or indicator-specific test was changed.

The full indicator status remains:
- 🟨 SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook: calculation/data foundation only; chart rendering and lifecycle acceptance remain open.
- 🟧 Footprint PRO 2GD: synthetic/offline foundation; visual implementation remains Stage 4 gated and must follow the two supplied references. OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters.
- 🟥 Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps: acceptance incomplete; no implementation completion is claimed.

Mathematical contracts remain unchanged: SMA/EMA/Bollinger first valid index 19; RSI14 index 14; MACD line index 25 and signal/histogram index 33. Warm-up nulls, prefix causality, no lookahead, exact candle timestamp alignment and stale-output clearing remain mandatory.

Focused indicator test declaration inventory remains 28 (21 calculation + 7 shared-hook declarations). This count is not a passed-test count and not an indicator completion percentage. Aggregate indicator completion remains ⚪ NOT SCORED because no approved weighted denominator exists.


---

# Work Cycle 69 indicator reconciliation — 25 November 2026

**Audited project HEAD:** `c746478cba0bbec95c663d9f9986e9863866538c`  
**Exact-HEAD CI:** 4/4 SUCCESS.  
**Indicator source changes:** none. **Indicator completion credit:** none.

The WebSocket offline-demand route/lifespan audit does not alter indicator math, hook behavior, renderer, chart UI, or indicator test coverage. Existing indicator statuses remain:

| Indicator / subsystem | Status | Remaining acceptance |
|---|---|---|
| SMA20 | 🟨 FOUNDATION | Chart overlay, toggle, legend/latest value and lifecycle |
| EMA20 | 🟨 FOUNDATION | Chart overlay, toggle, legend/latest value and lifecycle |
| RSI14 Wilder | 🟨 FOUNDATION | Dedicated 0–100 pane, 30/70 guides and lifecycle |
| MACD12/26/9 | 🟨 FOUNDATION | Dedicated pane, MACD/signal lines, histogram and zero guide |
| Bollinger20,2 | 🟨 FOUNDATION | Upper/middle/lower overlays, fill, legend and lifecycle |
| Shared Indicator Hook | 🟨 FOUNDATION | Integration into CandlestickChart and complete trust/lifecycle acceptance |
| Footprint PRO 2GD | 🟧 GATED | Stage 4 blueprint/review and reference-matched renderer; offline accumulator is not exchange-native bid/ask |
| Volume Profile | 🟥 OPEN | Accepted binning, POC/value-area algorithm and chart integration |
| Complete Volume Profile | 🟥 OPEN | Session/range methodology and POC/VAH/VAL acceptance |
| Movable-range Volume Profile | 🟥 OPEN | User range interaction, recalculation and lifecycle |
| Heatmap | 🟥 OPEN | Lawful depth source, aggregation/decay methodology and supplied visual reference |
| Liquidation Maps | 🟥 OPEN | Data provenance, estimation methodology and confidence limits |

Mathematical invariants remain mandatory: null warm-up; prefix causality; no future-candle lookahead; exact timestamp/series alignment; stale-output clearing on identity change; no indicator output from demo/loading/unavailable/error snapshots. Footprint OFF retains ordinary candle spacing; explicit ON alone selects spaced-cluster layout.

Focused declarations remain 21 calculation + 7 shared-hook tests; these are declaration counts, not pass counts or completed indicators. Aggregate indicator completion remains ⚪ NOT SCORED because no approved weighted denominator exists.


---

# Work Cycle 70 indicator reconciliation — 25 November 2026

**Audited source HEAD:** `f0c474fa25f973b1069bb0cef95b9b4fc7611127`  
**Exact-HEAD CI:** 4/4 SUCCESS; Automated Tests 41/41 steps; backend pytest 1,426 passed, 1 skipped, 6 warnings.  
**Indicator source changes:** none. **Indicator completion credit:** none.

The Gate 25 runtime-wiring audit changes no indicator math, hooks, chart rendering, UI or indicator tests. Current status remains:

| Indicator / subsystem | Status | Remaining acceptance |
|---|---|---|
| SMA20 | 🟨 FOUNDATION | Chart overlay, toggle, legend/latest value and lifecycle |
| EMA20 | 🟨 FOUNDATION | Chart overlay, toggle, legend/latest value and lifecycle |
| RSI14 Wilder | 🟨 FOUNDATION | Dedicated 0–100 pane, 30/70 guides and lifecycle |
| MACD12/26/9 | 🟨 FOUNDATION | Dedicated pane, MACD/signal lines, histogram and zero guide |
| Bollinger20,2 | 🟨 FOUNDATION | Upper/middle/lower overlays, fill, legend and lifecycle |
| Shared Indicator Hook | 🟨 FOUNDATION | Integration into CandlestickChart and complete trust/lifecycle acceptance |
| Footprint PRO 2GD | 🟧 GATED | Stage 4 blueprint/review and reference-matched renderer; offline accumulator is not exchange-native bid/ask |
| Volume Profile | 🟥 OPEN | Accepted binning, POC/value-area algorithm and chart integration |
| Complete Volume Profile | 🟥 OPEN | Session/range methodology and POC/VAH/VAL acceptance |
| Movable-range Volume Profile | 🟥 OPEN | User range interaction, recalculation and lifecycle |
| Heatmap | 🟥 OPEN | Lawful depth source, aggregation/decay methodology and supplied visual reference |
| Liquidation Maps | 🟥 OPEN | Data provenance, estimation methodology and confidence limits |

Mathematical invariants remain: warm-up nulls, prefix causality, no future-candle lookahead, exact timestamp/series alignment, stale-output clearing on identity change, and no output from demo/loading/unavailable/error snapshots. Footprint OFF retains standard candle spacing; explicit ON alone enables spaced clusters.

Focused declarations remain 21 calculation + 7 shared-hook tests; they are not completed-indicator counts. Aggregate indicator completion remains ⚪ NOT SCORED because no approved weighted denominator exists.


## Batch 72 exact-head CI closure — 25 November 2026

**Audited commit:** `a342a2abe8f70315445343e123e661ea37c52050` on `phase-2/market-data-foundation`. All four required workflows are now terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45599485761 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45599485734 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45599485776 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45599485759 | 🟢 SUCCESS | 6/6 |

Automated Tests log confirms **1,426 passed, 1 skipped, 6 warnings in 59.44 seconds**. The skipped test is the isolated Redis TLS integration fixture because it is not configured. Therefore this is not owner-host Redis TLS acceptance. Container smoke checks passed for health, Redis ACL/AOF persistence across restart, fail-closed API response during Redis outage, backend reconnect, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection. OCI ARM64, CodeQL and full-history secret audit passed. No failure was recorded.

**Evidence boundary:** these are GitHub CI results only. They do not prove a live Cloudflare deployment, public WSS, Firebase identity, real market-data provider, owner-host Redis TLS, Android/browser production lifecycle, or production snapshot transfer/ACK. The CI success does not change Stage 1 30/40 provisional or Gate 10 0/10. Indicator implementation status and completion credit are unchanged.


## Batch 73 exact-head CI closure and dedicated Redis TLS acceptance — 25 November 2026

**Audited commit:** `c3effcd4f48f03ef9cbe28edf59787ed74f4bc88` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45601263082 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45601263013 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45601262998 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45601263240 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 48.77 seconds**. In addition, the dedicated TLS step generated an ephemeral test CA, trusted server certificate for DNS:localhost, wrong CA and a TLS-only Redis listener; it ran `tests/test_shared_guard_tls_integration.py` separately and the result was **1 passed in 0.07s**. That test verified successful CA/hostname validation and ACL-backed shared-guard operations, rejection of wrong hostname, untrusted CA and plaintext downgrade. The same TLS listener then proved AOF data, TLS-only listener and ACL survived a real container restart. The later general pytest run reports the TLS test skipped because its short-lived fixture variables are intentionally scoped to the preceding dedicated step; this does not negate the dedicated 1/1 pass.

The same run also passed frontend tests/build and secret scanning, Cloudflare synthetic proof tests, Durable Object runtime tests, backend dependency audit, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke tests and container vulnerability scan. CodeQL, native ARM64 and full reachable-history secret audit passed. No CI failure was recorded.

**Evidence boundary remains:** isolated CI Redis TLS acceptance is not owner-host Redis TLS deployment acceptance. CI still does not prove production Cloudflare deployment, public WSS, Firebase identity/entitlement, live provider rights/data, production snapshot transfer/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10 formally closed. Indicator completion credit unchanged.


## Batch 74 exact-head CI closure — 25 November 2026

**Audited commit:** `9671ce0b9c1c54b1127fe55a03e5008611c6fc2e` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45602155645 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45602155744 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45602155670 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45602155558 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 48.66 seconds**. Dedicated Redis TLS integration: **1 passed in 0.07 seconds** using an ephemeral CA, DNS:localhost certificate, wrong CA and TLS-only Redis listener. Wrong-hostname, untrusted-CA and plaintext downgrade cases were rejected; authenticated shared-guard operations succeeded. Redis AOF data, TLS-only listener and ACL survived an actual container restart. The later general suite's one skip is expected because the temporary TLS fixture variables are scoped to the dedicated preceding step. Container health, fail-closed Redis outage/reconnect, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit smoke checks passed. Frontend tests/build/secret scan, Cloudflare synthetic Worker/DO runtime tests, backend dependency audit, synthetic SQLite benchmarks, backend container build and vulnerability scan passed.

This CI success does not prove owner-host TLS, production Cloudflare deployment/public WSS, Firebase identity, live provider rights/data, production snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator status and completion credit are unchanged.


## Batch 75 exact-head CI closure — 25 November 2026

**Audited commit:** `fd200b617a87d04693a08d04be26ad4991a0f978` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45603007729 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45603007940 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45603007601 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45603008057 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 71.47 seconds**. Dedicated Redis TLS integration: **1 passed in 0.11 seconds**. Ephemeral CA/server certificate/TLS-only Redis fixture verified trusted CA + DNS hostname, ACL-backed shared-guard operations, rejection of wrong hostname, untrusted CA and plaintext downgrade; AOF data, TLS-only listener and ACL survived an actual container restart. The later general pytest invocation skips the TLS test because fixture environment variables are intentionally scoped to the preceding dedicated step. Backend container health/outage/reconnect, non-root runtime, persistent volume, SQLite integrity/restart and rate-limit smoke checks passed. Frontend tests/build/secret scan, Cloudflare synthetic Worker/DO tests, dependency audit, synthetic SQLite benchmarks, image build/scan, CodeQL, ARM64 and full-history secret audit passed.

Evidence remains CI-only: not owner-host TLS acceptance, production Cloudflare deployment/public WSS, Firebase identity, live provider rights/data, production snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator completion credit unchanged.


## Batch 76 exact-head CI closure — 25 November 2026

**Audited source commit:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45604020771 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45604020613 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45604020280 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45604020286 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 57.78 seconds**. Dedicated Redis TLS integration: **1 passed in 0.08 seconds**. It used an ephemeral CA, DNS:localhost certificate and TLS-only Redis listener; trusted CA/hostname and ACL-backed shared-guard operations passed; wrong hostname, untrusted CA and plaintext downgrade were rejected. AOF data, TLS-only listener and ACL survived a real Redis container restart. The general pytest suite's one skip is expected because fixture variables are scoped to the dedicated preceding step. Backend container smoke tests, frontend build/tests/secret scan, Cloudflare synthetic Worker/DO tests, backend dependency audit, synthetic SQLite benchmarks, container vulnerability scan, CodeQL, ARM64 and full-history secret audit all passed.

This is CI evidence only. It does not prove owner-host TLS, production Cloudflare deployment/public WSS, Firebase identity/entitlement, live provider rights/data, production signed snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator completion credit unchanged.

The following documentation-only reconciliation commit does not change runtime/source files; CI is not rerun for that documentation-only commit because the exact source tree above already passed all four workflows.


---

## INDICATOR LEDGER — Batch 78 reconciliation (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Documentation HEAD before Batch 78:** `fb4fb9843535b0dae1cc733d65df9de653dd88ba`  
**Last source/test SHA:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`  
**Batch 78 report:** [Recovery, monitoring and five-batch reconciliation](WORK_CYCLE_2026-11-25_BATCH78_RECOVERY_MONITORING_RECONCILIATION.md)

Batches 74–77 already existed and are reconciled; they are not reimplemented. Exact-source CI recorded by Batch 77: Automated Tests 41/41 (1,426 passed, 1 skipped, 6 warnings), CodeQL 16/16, OCI ARM64 7/7, Secret Audit 6/6; dedicated Redis TLS integration 1 passed. The subsequent branch commits are documentation-only and marked `[skip ci]`; no new source CI run is claimed for them.

**Stage dashboard:** Stage 1 official active, 30/40 = 75% provisional 🟨; Gate 10 = 0/10 formally closed 🟥 (criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39). Stage 2 🟦 preparatory only; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project, aggregate indicator completion and IP3S remain ⚪ NOT SCORED because no approved weighted denominator exists.

**WebSocket/Gate 25:** production WSS, Firebase identity/entitlement, lawful zero-cost provider provenance, production ticket issuance, signed snapshot transfer, authenticated persisted receipt retrieval, durable per-gateway high-water ACK/fencing/restart reconciliation and public browser/Android E2E remain OPEN. Redis `XTRIM`, `XDEL` and consumer-group destruction remain BLOCKED until durable gateway ACK acceptance. Cloudflare Worker/DO remains synthetic-only; no production resources were created. The connected account inventory is empty, while the user has separately stated the project server is on Cloudflare; do not infer that the connected account is the hosting account or create duplicate infrastructure.

**Recovery/monitoring:** CI verifies container-scope health, Redis ACL/AOF restart, outage fail-closed/reconnect, non-root execution, volume ownership smoke, SQLite integrity/restart, rate limiting and isolated TLS. Owner-host secret/volume/DB restore/off-host encrypted backup, independent alert/incident drill, production WSS and device recovery remain unaccepted.

**Indicators:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟥 OPEN. Focused declarations remain 28 (21 calculation + 7 hook), not completion. No indicator source/UI change and no completion credit in Batch 78. `CandlestickChart.tsx` integration remains absent. Preserve warm-up nulls, prefix causality, no lookahead/repaint, exact timestamp alignment and Footprint OFF normal candle spacing.

**Controls:** ZERO COST; `main` untouched; Vercel deferred; no paid data/hosting/monitoring/backup; no production deployment; delivery target around 24 December 2026.


---

## Batch 79 — Production WebSocket runtime wiring audit (25 November 2026)

Source audit report: [Batch 79 production runtime wiring and Gate 25 composition](WORK_CYCLE_2026-11-25_BATCH79_PRODUCTION_WEBSOCKET_RUNTIME_WIRING_AUDIT.md). Audited documentation HEAD before this report: `114d8464e085977aba2d95b3581ee49a95990c18`; last source/test SHA: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`.

**Newly isolated root cause:** the individual publisher, Redis replica consumer, SQLite replica store, Ed25519 snapshot attestation, Firebase identity, single-use ticket and WebSocket route primitives exist. However, the stock Docker command starts `uvicorn app.main:app`, and module-level `app = create_app()` supplies neither `replica_runtime_factory` nor `publisher_runtime_factory`. With no replica factory, lifespan starts the provider manager instead of the replica consumer/worker; with no publisher factory, the source relay is not started. The WebSocket handler falls back to the local source SQLite/in-memory pipeline when no replica store is injected. This is the concrete production runtime-composition gap. Source and gateway factories are intentionally mutually exclusive and must remain separate roles.

**Gate 25:** Ed25519 signed snapshot verification and atomic replica installation primitives exist, but the default app does not assemble owner-pinned trusted keys, expected source identity, signed snapshot transfer/install, dedicated gateway DB, consumer, lease and runtime lifecycle. The production runtime contract and owner-host evidence remain OPEN. Local replica cursor and Redis XACK must not be mislabeled as the owner-accepted per-gateway durable high-water receipt/ACK.

**CI boundary:** exact source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has recorded Automated Tests 41/41 (1,426 passed, 1 skipped, 6 warnings), CodeQL 16/16, OCI ARM64 7/7, Secret Audit 6/6 and dedicated Redis TLS 1 passed. Documentation HEAD `114d8464e085977aba2d95b3581ee49a95990c18` has six documentation-only commits ahead of that source SHA and no source/runtime diff; the docs-only commit has no CI runs/status because of `[skip ci]`. No new source CI is claimed.

**Progress:** Stage 1 30/40 = 75% provisional 🟨; Gate 10 0/10 formally closed 🟥 (8, 20, 25, 30, 31, 34, 35, 36, 38, 39). Stage 2 🟦 preparatory only; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project and IP3S ⚪ NOT SCORED. Indicator inventory unchanged: SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Hook 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟥 OPEN. Focused declarations 28 (21 calculation + 7 hook), not completion. No indicator source/UI changes.

**Next order:** define strict source/gateway role configuration; implement source factory; implement gateway factory with signed snapshot install before Redis initialization; add multi-process source-to-two-gateway integration and restart/fencing tests; prove per-gateway durable receipt/high-water ACK; then public Cloudflare WSS/browser/Android E2E; then owner-host backup/restore/monitoring acceptance. Keep Redis destructive retention blocked until ACK acceptance.

Controls unchanged: ZERO COST, `main` untouched, Vercel deferred, no duplicate Cloudflare resources, no paid data/hosting/monitoring/backup, planning target around 24 December 2026.


---

## Batch 80–86 unified runtime and acceptance work package (25 November 2026)

Authoritative work package: [WORK_CYCLE_2026-11-25_BATCH80_86_UNIFIED_RUNTIME_AND_ACCEPTANCE_PLAN.md](WORK_CYCLE_2026-11-25_BATCH80_86_UNIFIED_RUNTIME_AND_ACCEPTANCE_PLAN.md). Starting HEAD: `fd756cee2bf3e427a628c3089c37d07d9f75ada7`; source/test baseline: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`.

**Scope/accuracy:** this package is the detailed engineering blueprint and acceptance matrix for Batches 80–86. It does not claim runtime implementation, production deployment, public WSS, owner-host verification, or indicator completion. No source code, secrets, production data, Cloudflare resources, or deployments were changed. The major runtime composition review gate remains in force; implementation is sequenced after the scoped blueprint review. This preserves the user's no-broken-code requirement.

**Batch sequence:** 80 strict source/gateway role config and fail-closed validation; 81 source publisher factory and signed snapshot/checkpoint startup; 82 gateway replica factory with owner-pinned Ed25519 verification and install-before-Redis; 83 real Redis two-gateway process/restart/fault tests; 84 immutable per-gateway durable receipt and monotonic high-water ACK; 85 existing Cloudflare route/origin mapping and public WSS/browser/Android acceptance; 86 zero-cost recovery, monitoring, backup/restore and incident acceptance. Full test matrices, security boundaries, startup/shutdown rules, Redis ACL boundaries, and acceptance gates are in the linked package.

**Critical safeguards:** source and gateway remain separate app roles; no shared DB; gateway never receives source private key; Redis destructive `XTRIM`, `XDEL`, and consumer-group destruction remain blocked until every required gateway has an owner-accepted durable high-water ACK and restart reconciliation proof. XACK/local applied cursor are not owner acceptance. Do not create duplicate Cloudflare resources or introduce paid providers.

**Engineering parameter review:** current defaults observed in source are publisher lease 30,000 ms, publisher batch 100, consumer pending-idle 30,000 ms, consumer batch 100, gateway lease 15,000 ms with 5,000 ms default renewal, WebSocket ticket TTL 90 seconds, entitlement recheck 60 seconds. These are existing defaults, not production SLOs; validate against measured p99 latency, host scheduling and Redis RTT before acceptance.

**CI:** source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has prior exact-source evidence: Automated Tests 41/41, 1,426 passed, 1 skipped, 6 warnings; CodeQL 16/16; OCI ARM64 7/7; Secret Audit 6/6; dedicated Redis TLS 1 passed. Current documentation HEAD `fd756cee2bf3e427a628c3089c37d07d9f75ada7` is 12 commits ahead, zero behind, documentation-only by compare; no new source CI is claimed. The documentation commit uses `[skip ci]` and has no run/status. Previously recorded source jobs are terminal success; no running jobs left.

**Progress unchanged:** Stage 1 30/40 = 75% provisional 🟨; Gate 10 0/10 closed 🔴 (8, 20, 25, 30, 31, 34, 35, 36, 38, 39); Stage 2 🟦 preparatory; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project/IP3S ⚪ NOT SCORED. WebSocket runtime, Gate 25 durable ACK, public Cloudflare WSS/device E2E and owner-host recovery remain 🔴 OPEN.

**Indicator ledger unchanged:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range VP, Heatmap and Liquidation Maps 🔴 OPEN. 28 focused declarations (21 calculation + 7 hook) are not a completion percentage. No indicator source/UI changes. Keep warm-up nulls, prefix causality, no lookahead/repaint, timestamp alignment, stale-output clearing and no calculations on unavailable/demo/error/empty snapshots. Footprint OFF remains normal spacing; Footprint ON alone uses spaced clusters. Footprint references are available; Heatmap reference is still required before visual work.

Controls: ZERO COST; `main` untouched; Vercel deferred; no new/duplicate Cloudflare resources; no paid data/hosting/monitoring/backup; delivery target around 24 December 2026.


---

## Batch 80 — strict runtime role and fail-closed app binding (25 November 2026)

**Status: IMPLEMENTED + VERIFIED 🟩.** This is a bounded Batch 80 completion, not a claim that the complete source/gateway production relay is deployed.

### Implemented controls

- OHLCV_REDIS_ROLE must explicitly be source or gateway whenever OHLCV_REDIS_ENABLED=true; missing, unknown, or mismatched roles fail closed.
- create_app() validates that the declared role has its matching injected factory: source requires publisher_runtime_factory; gateway requires replica_runtime_factory. A crossed factory or enabled relay with no injected factory is rejected before application startup.
- Source and gateway factories remain mutually exclusive.
- Source and replica SQLite database targets must be absolute file paths; relative paths, symbolic-link targets, and directory targets are rejected.
- backend/.env.example now documents the role selector. Relay remains disabled by default.
- Added focused tests for missing/invalid/mismatched roles, factory-role binding, fail-closed app creation, absolute database paths, directories and symlinks.

### Changed files

- backend/app/ohlcv_redis_config.py
- backend/app/ohlcv_redis_runtime.py
- backend/app/ohlcv_redis_gateway_runtime.py
- backend/app/main.py
- backend/tests/test_ohlcv_redis_config.py
- backend/tests/test_ohlcv_redis_runtime.py
- backend/tests/test_ohlcv_redis_gateway_runtime.py
- backend/tests/test_ohlcv_redis_publisher_lifecycle.py
- backend/.env.example

### Exact verification — final source commit

Commit: 66d4c6a812d5ce2570345e1108e813b5067f5248

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [2457](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188191) | 🟩 41/41 steps; 1,433 passed, 1 skipped, 6 warnings |
| CodeQL Python | [1814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | 🟩 8/8 |
| CodeQL JavaScript/TypeScript | [1814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | 🟩 8/8 |
| Full Git History Secret Audit | [1396](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188184) | 🟩 6/6 |
| OCI ARM64 Image Readiness | [443](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188277) | 🟩 7/7 |

Automated Tests also completed the Redis TLS fixture step, backend dependency audit, backend container build, container smoke test with shared Redis guard/persistent volume, and container scan. All four workflows are terminal success; no CI job remains running. An earlier run exposed one legacy gateway fixture missing the new role; that fixture was corrected before the final successful run.

### Boundary — what is still not complete

The module-level production ASGI app does not invent owner-specific snapshot callbacks. Source publisher activation still requires an owner-provided snapshot_verifier that verifies the exact snapshot and every required gateway's durable installation receipt. Gateway activation still requires an authenticated snapshot_installer and owner-pinned Ed25519 trust keys. These callbacks are not guessed or fabricated. Therefore production publisher/gateway runtime wiring, Gate 25 owner-accepted durable high-water ACK, public Cloudflare WSS, browser/Android E2E and owner-host recovery remain 🔴 OPEN. No production deployment or Cloudflare resource was changed.

### Next ordered work

1. **Batch 81:** source publisher runtime integration, contingent on the authoritative owner snapshot-verifier and durable gateway-receipt source.
2. **Batch 82:** gateway replica runtime integration, contingent on the authenticated snapshot-transfer/install callback and owner-pinned key configuration.
3. **Batch 83:** two-gateway Redis process/restart/fencing/fault acceptance.
4. **Batch 84:** durable owner-accepted high-water ACK and restart reconciliation.
5. **Batch 85:** existing Cloudflare route/origin plus public WSS/browser/Android acceptance.
6. **Batch 86:** owner-host backup/restore, local observability and incident drills.

Do not trim/delete Redis stream entries or destroy consumer groups until every required gateway has a durable owner-accepted high-water ACK and restart reconciliation proof.

### Project and indicator progress — no percentage inflation

- Stage 1: **30/40 = 75% provisional 🟨** (unchanged; Batch 80 does not auto-close Stage 1 criteria).
- Gate 10: **0/10 formally closed 🔴**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 2: 🟦 preparatory, not officially entered/scored.
- Stage 3: ⚪ not scored.
- Stage 4: 🟪 gated.
- Stages 5–6: ⚪ not scored.
- Overall project: ⚪ NOT SCORED; approved weighted denominator is still absent.
- Significant project index/IP3S: ⚪ NOT SCORED for the same reason.

### Complete indicator ledger — source/UI unchanged in Batch 80

| Indicator | Status | Current implementation/evidence | Mathematical/acceptance boundary |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; arithmetic mean of 20 closes |
| EMA20 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; alpha 2/21; recursive seed contract tested |
| RSI14 Wilder | 🟨 FOUNDATION | Calculation foundation only | First valid index 14; Wilder smoothing; no divide-by-zero NaN leak |
| MACD12/26/9 | 🟨 FOUNDATION | Calculation foundation only | MACD line first valid index 25; signal and histogram index 33 |
| Bollinger20,2 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; population standard deviation per current contract |
| Shared Indicator Hook | 🟨 FOUNDATION | 7 focused declarations | Chart integration into CandlestickChart.tsx remains open |
| Footprint PRO 2GD | 🟧 GATED | Synthetic/offline accumulator only | Visual work must match both saved Footprint references; OFF keeps normal candle spacing, ON alone enables spaced clusters |
| Volume Profile | 🟥 OPEN | Not accepted | Price-bin volume conservation, range semantics and timestamp boundaries |
| Complete Volume Profile | 🟥 OPEN | Not accepted | Full-session completeness, POC/VA derivation and conservation |
| Movable-range Volume Profile | 🟥 OPEN | Not accepted | User-selected range bounds and deterministic recomputation |
| Heatmap | 🟥 OPEN | Visual implementation not started | Must wait for the user's Heatmap reference image |
| Liquidation Maps | 🟥 OPEN | Not accepted | Data provenance and methodology remain unapproved |

Focused declaration inventory remains **28 total = 21 calculation + 7 shared-hook declarations**. This is not an indicator completion percentage or count of accepted indicators. Batch 80 changed no indicator calculation or chart UI; indicator progress credit is therefore unchanged.

Cross-indicator acceptance remains mandatory: warm-up values null until mathematically valid; prefix causality; no future-candle lookahead/repaint; exact timestamp/series identity alignment; stale-output clearing on identity change; deterministic repeated results; bounded computation; no mutation of source candle data; no calculations for demo/loading/unavailable/error/empty snapshots.

**Controls:** ZERO COST; active branch only phase-2/market-data-foundation; main untouched; no Vercel; no paid market data, hosting, monitoring, backup, subscription or publication; no duplicate Cloudflare infrastructure. Planning target remains around **24 December 2026**.
