# WORK CYCLE 62J-155 — Indicator engine integration and gap-semantics audit

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Delivery target: 24 December 2026  
ZERO COST: enforced  
`main`: untouched

## Audit scope

Read-only inspection of:
- `src/indicators/indicatorCalculations.ts`
- `src/indicators/indicatorCalculations.test.ts`
- `src/indicators/useMarketIndicators.ts`
- `src/services/marketDataStore.ts`
- `src/components/CandlestickChart.tsx`
- `src/App.tsx`

No runtime code changed. No provider or paid data source is needed for this audit.

## Verified calculation foundation

The shared calculation module currently provides:
- SMA with rolling-window arithmetic mean and null warm-up;
- EMA with SMA seed and multiplier (2/(period+1));
- RSI with Wilder seed and recursive smoothing;
- MACD with fast/slow EMA, signal EMA and histogram;
- Bollinger bands using population standard deviation.

Existing regression coverage includes:
- candle-index alignment and warm-up nulls;
- RSI flat/rising/falling/alternating cases;
- MACD and signal warm-up indices;
- Bollinger population deviation;
- all supported timeframe labels;
- prefix causality;
- non-finite close rejection;
- extreme finite-value handling and cancellation precision.

This is calculation-engine evidence only. It does not establish chart renderer completion or a usable indicator control panel.

## Confirmed integration gap

`useMarketIndicators.ts` reads the single global market-data snapshot and calculates values only for ready/degraded backend data. The inspected `CandlestickChart.tsx` and `App.tsx` do not import or invoke this hook. The chart currently renders the candlestick series; no integrated SMA/EMA overlays, RSI/MACD panes, Bollinger overlay, indicator toggle controls, or latest-value legend were verified in this path.

Therefore the five calculation foundations remain 🟨, not complete. The shared hook also remains 🟨 and not renderer-integrated.

## Gap semantics — important correctness blocker

The current calculation boundary receives candle data but does not receive a validated session-calendar gap policy. The store checks finite OHLCV values and strictly increasing timestamps, but strict ordering alone does not distinguish:
- an expected interval boundary (overnight close, weekend, holiday, scheduled break);
- a missing candle inside an active trading session;
- an intentional timeframe aggregation boundary.

Blindly treating every timestamp gap as invalid would reject legitimate session transitions. Blindly treating every adjacent row as consecutive would allow indicators to bridge missing in-session bars.

Required safe design:
1. Pass the canonical timeframe, calendar ID/version, bucket policy, and validated session schedule alongside the bars.
2. Determine expected next bucket boundaries using the same canonical calendar/bucket contract as ingestion.
3. Mark missing in-session intervals explicitly; do not synthesize zero-price/zero-volume bars.
4. Define per-indicator reset/skip behavior for a genuine gap and test it; do not silently carry smoothing state across a missing interval.
5. Preserve expected overnight/weekend/holiday transitions without false gap alarms.
6. Keep all outputs candle-index aligned and prefix-causal.
7. On calendar/timeframe/series identity change, clear prior indicator outputs before publishing the new calculation.

No arbitrary fixed-seconds gap threshold should be added: that would be wrong for session-aware futures calendars and monthly/weekly bars.

## Progress ledger correction

| Indicator / subsystem | Status | Verified | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Formula, warm-up, alignment, numerical tests | Calendar-aware gap policy, chart overlay, toggle, legend, lifecycle/render tests |
| EMA20 | 🟨 Foundation | SMA seed, alpha 2/21, warm-up and numerical tests | Gap reset semantics, overlay, toggle, legend, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder recurrence, warm-up and edge-case tests | Gap semantics, 0–100 pane, 30/70 guides, toggle/legend/render |
| MACD12/26/9 | 🟨 Foundation | MACD/signal warm-up and calculation tests | Gap semantics, dedicated pane, lines/histogram/zero guide and controls |
| Bollinger20,2 | 🟨 Foundation | Population deviation, warm-up and numeric stability tests | Gap semantics, three-line overlay, toggle/value display/render |
| Shared Indicator Hook | 🟨 Foundation | Backend-only snapshot gating and memoized calculations | Per-series store ownership, gap-aware input contract, hook tests and chart binding |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator | User visual references, reviewed blueprint, valid bid/ask provenance/rights, renderer |
| Heatmap | 🟥 Not implemented | No accepted depth renderer | User reference, depth/liquidity contract, reviewed blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted provenance-backed calculation | Valid source/provenance contract, reviewed blueprint and renderer |

Mandatory invariant status:
- Warm-up nulls and candle-index alignment: implemented/tested in calculation foundation.
- Prefix causality: regression-tested.
- Non-finite close rejection: implemented/tested.
- Calendar-aware missing-bar detection and indicator reset semantics: NOT YET IMPLEMENTED/VERIFIED.
- Stale clearing across series identity: store reset exists; hook/renderer integration still incomplete.
- Footprint OFF standard candle spacing and ON-only cluster layout: remains a required future renderer acceptance.
- Footprint/Heatmap visuals remain gated on user-supplied references and reviewed blueprint.

## Work decision

Do not add a guessed fixed interval threshold or synthesize bars. Next indicator work should first define a typed calendar-aware gap annotation contract from the already canonical session calendar and bucket policy. Then add tests for normal session close, overnight reopen, weekend/holiday, scheduled break, one missing in-session bucket, and timeframe changes. Only after that should the hook and renderers consume the result.

No indicator completion percentage is calculated because no approved weights/denominator exist.

## Project stage and gate accounting

- Stage 1 — Foundation, Security & Data Integrity: 30/40 = 75% provisional 🟨.
- Stage 2 — Market Data Infrastructure: not scored ⬜.
- Stage 3 — Chart Engine & Timeframe: not scored ⬜.
- Stage 4 — Indicators & Analytics: not scored ⬜.
- Stage 5 — Professional UI & Interactive Tools: not scored ⬜.
- Stage 6 — Hardening, Validation & APK Release: not scored ⬜.
- Overall project: NOT SCORED; denominator and approved stage weights are not defined.
- Gate 10 external acceptance: 0/10 formally closed. CI is necessary evidence, not external deployment acceptance.

## CI

The corrected test run and latest HEAD workflows are still running at the time of this audit. Do not mark them green until exact run conclusions are successful. No OCI VM or public WSS endpoint has been provisioned.
