# DEZZTA CHART — Batch 62J-185
## Indicator hook backend-snapshot trust-boundary regression

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test base:** `6927818f3950042d213c250e8003530aa771bfad`  
**Protected branch:** `main` untouched  
**Cost:** ZERO COST; local frontend unit test only.

## 1. Gap addressed

The shared indicator hook intentionally calculates only from snapshots whose source is `backend` and whose status is `ready` or `degraded`. Demo, loading, unavailable, and error states must not expose indicator values.

The existing tests covered an unselected series, ready backend data, per-series isolation, shared frozen calculation results, and clearing after an unavailable transition. They did not explicitly prove both sides of the `degraded` acceptance boundary or that a previously calculated result is cleared when a live series changes to demo/error.

## 2. Regression added

**Test:** `keeps degraded backend indicators but clears demo and error snapshots`

The test drives one mounted hook through four consecutive snapshots:
1. `ready + backend` → indicators are calculated.
2. `degraded + backend` with validated bars → indicators remain available.
3. `demo + demo` → indicator output becomes null/empty.
4. `error + none` → indicator output remains null/empty.

This proves that degraded-but-real backend data remains usable while demo and failed data cannot be mistaken for accepted market data, and that stale calculations disappear on state transition.

## 3. Scope and accounting

Only `src/indicators/useMarketIndicators.test.ts` changes in this batch. No indicator formula, warm-up rule, numerical kernel, chart renderer, pane, legend, setting, or user-facing UI changed.

Indicator status remains:
- SMA20 🟨 Foundation.
- EMA20 🟨 Foundation.
- RSI14 Wilder 🟨 Foundation.
- MACD12/26/9 🟨 Foundation.
- Bollinger20,2 🟨 Foundation.
- Shared Indicator Hook 🟨 Foundation; backend-only ready/degraded trust boundary now has explicit transition regression coverage.
- Footprint 🟧 Synthetic prototype only.
- Heatmap 🟥 Not implemented.
- Liquidation Maps 🟥 Not implemented.

The added test improves acceptance evidence for the Shared Indicator Hook; it does not complete actual chart binding, settings, legend, pane/overlay rendering, identity lifecycle, accessibility, or performance acceptance. No aggregate indicator percentage is awarded.

## 4. CI acceptance

The exact source/test commit is `d37420a4151322a19d388c45bc1398d169fab69c`. The final documentation commit for this batch must receive exact-HEAD CI. Until then, this regression is **implemented but pending CI**, not accepted.

## 5. Project status impact

No stage or overall percentage changes:
- Stage 1: 30/40 = 75% provisional 🟨.
- Stage 2: not scored; upstream provider demand, recurring-zero-cost data entitlement, production identity and public WSS remain open.
- Stages 3–6: not scored.
- Gate 10: 0/10 external criteria formally closed 🟥.
- Overall project: **NOT SCORED** because no approved weighted denominator exists.
- Delivery target: **24 December 2026**, planning target only.

The indicator integrity invariants remain mandatory: warm-up nulls, exact source-index alignment, prefix causality/no future repaint, invalid/gapped input rejection, and stale-output clearing on identity changes. Footprint OFF retains standard candle spacing; Footprint ON alone enables spaced clusters. Footprint/Heatmap visual work remains gated on user reference images and scoped blueprint review.
