# DEZZTA CHART — Batch 62J-223
## Shared WebSocket series-owner guard, regression coverage, and indicator reconciliation

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent code/test checkpoint:** `2eb23dba6ddaeacb24c44cec1a046b96103ea045`  
**Source fix commit:** `6d48560d6a8f5e0450070ef646dcab36f19742bd`  
**Regression-test commit / code-test HEAD:** `92b8ef0936d374f81df6d09e67a4752494100d40`  
**Cost:** ZERO COST • **main:** untouched • **Vercel:** deployment deferred  
**Delivery target:** approximately 24 December 2026 (planning target only)

## 1. Finding and correction

The per-series WebSocket supervisor registry keyed ownership by canonical series identity. When another chart panel acquired the same identity, the registry reused the existing supervisor but did not verify that the new owner supplied the same transport endpoint and canonical instrument mapping. A conflicting configuration could therefore be silently attached to a supervisor created for a different endpoint or canonical mapping.

The registry now stores the transport `baseUrl` and `canonicalInstrumentId` alongside each active series entry. A later owner for the same series is rejected before owner registration if either value differs. Existing same-series sharing and reference-counted final-owner shutdown remain unchanged.

This is a narrow fail-closed consistency fix; it does not alter WebSocket wire protocol, authentication, market-data schemas, reconnect policy, Redis behavior, or UI.

## 2. Changed source and regression test

- `src/services/ohlcvSeriesSupervisorRegistry.ts`
  - Persisted the active transport endpoint and canonical instrument mapping in each registry entry.
  - Added a mismatch guard before adding an owner to an existing series.
- `src/services/ohlcvSeriesSupervisorRegistry.test.ts`
  - Added one regression case covering a conflicting canonical instrument ID and a conflicting endpoint.
  - Asserts both acquisitions are rejected and the existing owner/series remain intact.

No dependency, schema, secret, runtime deployment, or external provider was added.

## 3. Validation boundary

The previous parent checkpoint `2eb23dba6ddaeacb24c44cec1a046b96103ea045` had its inspected CI job groups completed successfully. Those results do **not** transfer to the new code/test HEAD `92b8ef0936d374f81df6d09e67a4752494100d40`.

**Exact-head CI for Batch 223: PENDING / NOT YET VERIFIED.** The new source and regression test have been committed to the active branch. Do not report them as passing until the exact new HEAD has terminal Automated Tests, CodeQL, OCI ARM64 and Full Git History Secret Audit results.

## 4. Indicator progress reconciliation

The branch contains two focused indicator suites with 24 named tests: 17 calculation-engine tests and 7 shared-hook tests. The calculation engine and hook remain foundations, not visible chart features.

| Indicator / subsystem | Verified foundation | First valid source index | Visible chart integration | Status |
|---|---|---:|---|---|
| SMA20 | 20-close arithmetic mean; overflow-resistant normalized summation | 19 | Overlay, toggle, legend/latest value and lifecycle not integrated | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha = 2/21 | 19 | Overlay, toggle, legend/latest value and lifecycle not integrated | 🟨 Foundation |
| RSI14 Wilder | Initial 14-change gain/loss averages plus Wilder recurrence; flat/rising/falling edge handling | 14 | Dedicated 0–100 pane, 30/70 guides, toggle and legend not integrated | 🟨 Foundation |
| MACD12/26/9 | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | Dedicated pane, lines, histogram, zero guide and toggle not integrated | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | Upper/middle/lower overlay, fill, toggle and latest values not integrated | 🟨 Foundation |
| Shared Indicator Hook | Exact keyed immutable backend snapshot; shared calculation cache; demo/loading/unavailable/error suppression | Per study | Not imported/called by `CandlestickChart.tsx` | 🟨 Foundation |
| Footprint | Synthetic/educational accumulator only; not exchange-native bid/ask truth | N/A | User-reference and reviewed-blueprint gate; OFF preserves normal candle spacing, ON alone enables spaced clusters | 🟧 Gated |
| Heatmap | No accepted depth/liquidity renderer | N/A | Not implemented; reference and validated depth contract required | 🟥 Open |
| Liquidation Maps | No accepted calculation/runtime renderer | N/A | Not implemented; provenance and reviewed blueprint required | 🟥 Open |

The 17 calculation tests cover alignment/warm-up, Wilder RSI edge cases and recurrence, MACD initialization and histogram identity, Bollinger population deviation/symmetry/translation behavior, all supported timeframes, prefix causality, non-finite inputs, large-magnitude overflow/cancellation and insufficient history. The 7 hook tests cover backend trust-state gating, exact keyed snapshots, live revision updates, panel isolation, immutable shared caching and stale-output clearing.

**Indicator aggregate: NOT SCORED.** No approved per-indicator weights or acceptance denominator exists. Test counts are evidence, not a completion percentage.

Visible chart integration remains red: `CandlestickChart.tsx` still creates a candlestick series and does not call `useMarketIndicators`. Do not begin the major indicator UI expansion before its official stage gate, scoped blueprint and user review. Footprint and Heatmap visual implementation remain reference-gated.

## 5. WebSocket and project gates

- Repository-side WebSocket protocol, auth/ticket, reconnect/replay, Redis replica and receipt-validation foundations remain substantially implemented and covered by CI.
- Gate 25 remains OPEN until authenticated owner-host snapshot transfer, immutable receipt custody, key provenance/custody and real gateway restart/recovery evidence are demonstrated.
- Gate 36 remains OPEN until public HTTPS/WSS, reverse-proxy/TLS lifecycle, real Firebase sign-in/revocation/entitlement E2E, and real browser/Android WebView/network-handover acceptance are demonstrated.
- Redis destructive retention remains BLOCKED until gateway inventory/retirement, pending-entry policy, per-gateway floor acknowledgements, separate retention authority and crash-safe trim/reconcile are proven. No XTRIM/XDEL/consumer-group destruction was introduced.

## 6. Official progress accounting

| Meter | Current verified value | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 criteria = 300/400 ticks = 75% provisional | 🟨 Active |
| Stage 2 — Market Data Infrastructure | Engineering work active; no approved denominator | 🟦 Active / NOT SCORED |
| Stages 3–6 | Not officially opened/scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 external criteria formally closed | 🟥 Open |
| Overall project | No approved six-stage weighted denominator | ⚪ NOT SCORED |
| Aggregate indicator progress | No approved per-indicator denominator | ⚪ NOT SCORED |
| IP3S / significant-progress cycle score | Not independently scored for this batch | ⚪ NOT SCORED |

Stage 1's 75% is provisional and must not be presented as total project completion. The historical overall percentages are not reused.

## 7. ZERO COST and next sequence

- No paid hosting, subscription, market-data provider, domain, KMS, cloud resource or publication fee.
- No deployment, no Vercel commit, no production credential changes.
- `main` remains untouched.
- Next: exact-head CI verification; then continue the approved owner-host authenticated receipt-transfer and recovery sequence; then external WSS/Firebase/browser/Android acceptance. Indicator visual implementation stays behind its stage/blueprint gate.

**Batch 223 conclusion:** one narrowly scoped WebSocket ownership defect was corrected and regression coverage added. CI for the new HEAD remains pending verification; production WebSocket and visible indicator completion are not claimed.
