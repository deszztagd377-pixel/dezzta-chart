# Work Cycle — 24 November 2026 — Batch 62J-204
## Indicator ledger reconciliation, test inventory verification, and documentation integrity repair

**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Parent documentation HEAD:** `4eef1fe3547d70257a39e00e9d4f49934dc3db2a`  
**Code/test checkpoint:** `b71bf86c31fadd2895a2b4f18991b6742847e1a1`  
**Cost:** ZERO COST • **main:** untouched • **delivery target:** approximately 24 December 2026

## 1. Scope and method

This batch is based on live GitHub source and document reads. It inspects the two indicator-specific Vitest suites, the shared calculation implementation, the shared hook, the chart integration boundary, and the current progress records. It does not modify application code or award progress without visible implementation and test evidence.

## 2. Indicator test inventory

The current source contains 17 `it()` cases in `src/indicators/indicatorCalculations.test.ts` and 7 in `src/indicators/useMarketIndicators.test.ts`, totaling **24 named indicator-specific cases**. The complete test names and coverage themes are recorded in `docs/INDICATOR_PROGRESS_LEDGER.md` and `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

The count is strictly the two inspected suites. It is not the full frontend suite count, does not imply all application tests were run in this batch, and does not establish production UI acceptance.

## 3. Calculation and hook evidence

- SMA20: arithmetic mean of 20 closes; first valid source index 19.
- EMA20: SMA-seeded recurrence with multiplier 2/21; first valid index 19.
- RSI14: first 14 close-to-close changes seed the Wilder averages; recurrence thereafter; first valid index 14.
- MACD12/26/9: EMA12 minus EMA26; EMA9 signal and MACD-minus-signal histogram; first MACD index 25, signal/histogram index 33.
- Bollinger20,2: 20-close mean ±2 population standard deviations; first valid index 19.
- Shared hook: only exact keyed backend snapshots in ready/degraded state produce values; immutable snapshot object identity backs shared WeakMap caching; demo/loading/unavailable/error states suppress output.

The two suites include warm-up alignment, supported-timeframe alignment, prefix causality, invalid/non-finite input rejection, large-magnitude numerical stability, cancellation residual preservation, keyed-series isolation, immutable revision recalculation, frozen shared results and trust-state clearing.

## 4. Critical chart integration finding

`src/components/CandlestickChart.tsx` does not import or call `useMarketIndicators`. It imports `useMarketDataSeriesSnapshot` and creates one `CandlestickSeries`. Therefore the five conventional studies are not yet visible chart features: there are no integrated overlays/panes, toggles, legends/latest values, or user settings in this chart component. This is a real integration blocker, not a calculation-kernel failure.

No indicator UI was added because Stage 4 remains gated and the agreed Footprint/Heatmap visual workflow requires owner-supplied reference images plus scoped blueprint review. Footprint remains synthetic/offline only; Heatmap and Liquidation Maps remain unimplemented.

## 5. Documentation defects corrected

- The indicator ledger's prior top checkpoint still identified Batch 62J-199 and source/test SHA `23bf2da...`; it is now clearly marked historical and a new Batch 62J-204 current checkpoint records source/test SHA `b71bf86...`.
- The current ledger now records all five formula foundations, first-valid indices, all 24 named tests, trust/cache behavior, chart integration gap, and gated/unimplemented studies.
- `PROJECT_STATUS.md`, `docs/PROJECT_PROGRESS.md`, `docs/PROJECT_MASTER_PROGRESS_2026-11-24.md`, and `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` now identify Batch 62J-204 as the latest documentation maintenance and point to the parent documentation HEAD.
- Four concatenated duplicate Markdown headings introduced in the prior documentation update were repaired.
- The project dashboard already identified Batch 62J-203 and was not changed.

## 6. Progress accounting — no speculative credit

| Meter | Verified state | Status |
|---|---:|---|
| Stage 1 | 30/40 criteria • 300/400 ticks • 75% provisional | 🟨 ACTIVE |
| Gate 10 | 0/10 formally closed; criteria 8,20,25,30,31,34,35,36,38,39 remain open | 🟥 OPEN |
| Stages 2–6 | Not officially opened/scored | 🟦 / ⬜ PARKED |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Indicator aggregate | No approved study/UI acceptance denominator | ⚪ NOT SCORED |
| Conventional indicators | Calculation/hook foundations; no chart integration | 🟨 FOUNDATION |
| Footprint | Synthetic prototype; visual gate remains | 🟧 GATED |
| Heatmap / Liquidation Maps | Not implemented | 🟥 OPEN |
| Cost | No new dependencies, hosting, provider, or deployment | 🟩 ZERO COST |

The 75% value is only the provisional Stage 1 criterion meter. It is not overall project completion or indicator completion. The 24 named tests do not create a percentage.

## 7. WebSocket / remaining Stage 1 priorities

This batch does not claim to close the external acceptance blockers recorded in Batch 62J-203. The remaining workstreams are:
1. Owner-host WSS/TLS and reverse-proxy acceptance.
2. Real Firebase sign-in, revocation and entitlement end-to-end evidence.
3. Authenticated production snapshot transfer and durable receipt custody.
4. Android real-device reconnect, resnapshot and foreground/background lifecycle acceptance.
5. Browser production lifecycle and reconnect acceptance.
6. Production cross-instance and platform-lifetime proof.
7. Redis Stream retention protocol specification and crash-safe state-machine tests before any destructive trim implementation.

Owner-controlled runtime credentials and device evidence must be supplied through the owner's secure environment; no secrets should be pasted into chat. No paid service is proposed.

## 8. Acceptance

- Exact indicator-specific named test inventory reconciled to 17 + 7 = 24.
- Calculation formula foundations and warm-up indices documented.
- Chart integration gap stated accurately; no visible-feature claim is made.
- Stale indicator checkpoint and duplicate headings repaired across current project records.
- No application code, tests, dependencies, secrets, infrastructure, or paid services changed.
- All changes remain on `phase-2/market-data-foundation`; `main` untouched.
