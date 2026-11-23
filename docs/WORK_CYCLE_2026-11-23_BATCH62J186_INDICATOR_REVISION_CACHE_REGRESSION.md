# DEZZTA CHART — Batch 62J-186
## Indicator recalculation on immutable live-snapshot revisions

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test base:** `bb0c100e33797462b1f520176f0ca4dbd685af07`  
**Protected branch:** `main` untouched  
**Cost:** ZERO COST; deterministic frontend unit test only.

## 1. Gap addressed

The indicator hook caches one frozen calculation result per immutable `MarketDataSnapshot` object using a WeakMap. The keyed store creates a new immutable snapshot revision after a validated incremental bar update. The existing hook tests proved same-snapshot result sharing and state clearing, but did not directly prove that a later live bar update invalidates the previous calculation and recalculates the rolling indicators against the new snapshot.

## 2. Regression added

**Test:** `recalculates from a new immutable snapshot revision after a live bar update`

- Publish a 40-bar backend snapshot and verify revision 1 / SMA20 latest value 130.5.
- Publish one valid, chronologically later bar through `MarketDataSeriesStore.publishUpdate()`.
- Verify the hook observes revision 2 and the new 20-bar rolling mean is 134.5.

The expected calculation is independently transparent: the update replaces the oldest value in the rolling 20-bar window with the new close. This proves the hook does not keep returning the old cached result after an immutable snapshot revision.

## 3. Scope and acceptance boundary

Only `src/indicators/useMarketIndicators.test.ts` changes in this batch. No calculation formula, cache implementation, backend source, renderer, chart UI, settings, or indicator visual was changed.

This improves regression evidence for:
- exact snapshot revision observation;
- cache invalidation by immutable snapshot identity;
- incremental update propagation into indicator calculation;
- rolling SMA alignment after a new source bar.

It does not complete actual chart overlay/pane rendering, toggles, legends, settings integration, accessibility, identity lifecycle across every selector, or performance acceptance. The Shared Indicator Hook remains 🟨 Foundation.

## 4. Indicator ledger

- SMA20 🟨 Foundation — latest revision recalculation now has an explicit rolling-window regression.
- EMA20 🟨 Foundation — formula unchanged; first valid index 19.
- RSI14 Wilder 🟨 Foundation — formula unchanged; first valid index 14.
- MACD12/26/9 🟨 Foundation — formula unchanged; MACD first index 25, signal/histogram first index 33.
- Bollinger20,2 🟨 Foundation — formula unchanged; first valid index 19.
- Shared Indicator Hook 🟨 Foundation — explicit ready/degraded versus demo/error trust boundary and immutable revision recalculation tests.
- Footprint 🟧 Synthetic prototype only — visual implementation remains blocked pending user reference image(s), reviewed blueprint and verified bid/ask source contract.
- Heatmap 🟥 Not implemented — visual implementation remains blocked pending user reference image(s), reviewed blueprint and validated depth/liquidity contract.
- Liquidation Maps 🟥 Not implemented — provenance/methodology and implementation remain outstanding.

No aggregate indicator percentage is awarded; study weights and denominator are not approved.

## 5. Project progress

No stage score changes:
- Stage 1: 30/40 = 75% provisional 🟨.
- Stage 2: not scored; provider-demand, recurring-zero-cost data entitlement, public WSS and production identity remain open.
- Stages 3–6: not scored.
- Gate 10: 0/10 external criteria formally closed 🟥.
- Overall project: **NOT SCORED**; approved weighted denominator unavailable.
- Delivery target: **24 December 2026**, planning target only.

Preserve warm-up nulls, exact source-index alignment, prefix causality/no future repaint, invalid/gapped data rejection and stale-output clearing on identity changes.
