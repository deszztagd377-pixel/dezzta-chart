# DEZZTA CHART — Batch 62J-208: Indicator Reference and Progress Reconciliation

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Status:** documentation-only reconciliation  
**Cost:** ZERO COST

## 1. Reference asset custody

The owner supplied two original Footprint visual reference images in the ChatGPT conversation and explicitly requested persistent reuse. They are recorded in the Saved Reference Images collection as:

- `Footprint Indicator Reference 1`
- `Footprint Indicator Reference 2`

These are the owner's source-of-truth visual references. This repository report does not contain the binary image assets and does not claim that they were uploaded into Git. When Stage 4 visual implementation is opened, the original saved assets must be made available as actual visual inputs to the implementation workflow; a text-only description or generic substitute image is not an acceptable replacement. Do not ask the owner to re-upload while the saved assets remain accessible.

## 2. Footprint visual and behavior acceptance

The implementation must match the original references, including:
- red/green bid/ask volume cells and numeric labels;
- price-level alignment and horizontal volume bars;
- highlighted price rows and the reference's color semantics;
- candle-cluster placement and deliberate horizontal spacing;
- dark chart presentation and legible density at target mobile sizes.

Behavioral invariants:
- Footprint OFF preserves the ordinary candlestick layout and normal candle spacing.
- Footprint ON activates a dedicated spaced-candle/cluster layout with sufficient room for footprint cells.
- Synthetic/demo aggregation must never be represented as exchange-native bid/ask truth.
- The real bid/ask or trade-side data contract and its provenance must be verified before production acceptance.
- Visual implementation requires a scoped blueprint and owner review before major coding.

## 3. Current indicator ledger

| Indicator / subsystem | Calculation foundation | Visible chart acceptance | Status |
|---|---|---|---|
| SMA 20 | 20-close mean; first valid index 19; named tests | Overlay, toggle, legend/latest value, lifecycle and render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded; alpha 2/21; first valid index 19; named tests | Overlay, toggle, legend/latest value, lifecycle and render tests | 🟨 Foundation |
| RSI 14 Wilder | Wilder smoothing; first valid index 14; named tests | Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | MACD first valid index 25; signal/histogram index 33; named tests | Dedicated pane, lines, histogram, zero guide, toggle and lifecycle/render tests | 🟨 Foundation |
| Bollinger 20,2 | Mean ±2 population SD; first valid index 19; named tests | Bands, fill, toggle, values and lifecycle/render tests | 🟨 Foundation |
| Shared Indicator Hook | Identity-bound snapshot-backed aligned study output | Actual chart binding, stale-output clearing, settings and legend | 🟨 Foundation |
| Footprint | Deterministic synthetic/offline prototype | Owner references now recorded; reviewed blueprint, verified bid/ask contract and cluster renderer still required | 🟧 Gated |
| Heatmap | No implementation verified | Owner reference, depth/liquidity contract, blueprint and renderer required | 🟥 Open |
| Liquidation Maps | No implementation verified | Defensible data provenance, calculation contract, blueprint and renderer required | 🟥 Open |

The calculation foundation currently has 17 named calculation-engine test cases and 7 shared-hook test cases (24 named cases total, per the latest inspected ledger). This is not 24 visible indicators and does not imply chart integration.

## 4. Three indicator tiers

The planned product organization remains three tabs:
1. Low Tier — 15 popular/standard indicators.
2. Mid Tier — Volume Profile and approximately 10 additional studies, with final inventory to be defined.
3. Exclusive Indicator Pro — advanced owner-selected studies, including Footprint PRO 2GD, Heatmap, Liquidation Maps, and Complete Volume Profile as previously classified.

The exact inventory, data entitlements, formulas, and visual references for each exclusive study must be tracked individually. Do not infer a study's formula or visual design from its name.

## 5. Progress accounting

- Footprint reference prerequisite: 🟩 owner references recorded in persistent Saved Reference Images.
- Footprint visual implementation: 🟧 gated; no implementation credit.
- Heatmap: 🟥 not implemented; visual reference still pending.
- Liquidation Maps: 🟥 not implemented; methodology/provenance pending.
- SMA/EMA/RSI/MACD/Bollinger/shared hook: 🟨 calculation foundations; visible chart integration remains outstanding.
- Aggregate indicator progress: NOT SCORED; no approved denominator/weights.
- Stage 4 remains parked under the official stage sequence.
- ZERO COST; no dependency or paid data provider added.
