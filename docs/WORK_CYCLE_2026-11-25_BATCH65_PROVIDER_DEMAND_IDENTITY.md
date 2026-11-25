# DEZZTA CHART — Work Cycle 65: Provider-demand identity correction

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent HEAD: `8b8218d53a7baeb8c13446ba7b91514e4f7312f8`  
Scope: provider-demand key correctness, offline route fixture, regression tests and indicator-ledger reconciliation  
Cost: ZERO COST  
`main`: untouched • Vercel deployment: deferred • Live provider: not enabled

## 1. Confirmed defect and correction

The provider-neutral `ProviderDemandKey` previously contained source, venue, instrument and channel only. The provider-demand blueprint requires upstream identity to distinguish provider, dataset, schema/channel, input symbology and source instrument. Dataset and input symbology were missing, so otherwise identical requests could be incorrectly coalesced across upstream namespaces.

This cycle adds required `dataset` and `symbology` identity fields, validates them with the other canonical key fields, and passes the exact dataset plus explicit `raw_symbol` symbology from the offline-fixture WebSocket route.

The change remains limited to the offline fixture. It does not connect the coordinator to Databento, Firebase, Redis, or any live market-data session.

## 2. Regression coverage added

`backend/tests/test_provider_demand.py` verifies that:
- the same source/venue/instrument/channel with a different dataset creates a distinct upstream key;
- the same source/venue/dataset/instrument/channel with a different input symbology creates a distinct upstream key;
- each key starts and stops independently;
- existing same-key multi-subscriber sharing, idempotency, start rollback, stop retry, cancellation and pending-release reconciliation remain covered;
- malformed/oversized dataset and symbology values are rejected.

The route fixture now uses the requested dataset in the demand identity rather than dropping it.

## 3. Acceptance boundary

This fixes a repository-level identity collision risk in the coordinator foundation. It does not close provider integration:
- real SDK dynamic subscribe/unsubscribe remains unverified;
- provider-side subscription acknowledgements remain unimplemented;
- cross-process shared provider demand remains unimplemented;
- recurring-$0 data entitlement and redistribution rights remain unverified;
- provider live source remains intentionally disconnected.

No Databento SDK API was guessed. No credentials, network connection, paid feed, or external service was used.

## 4. First CI attempt and correction

The first exact-head Automated Tests run exposed two integration fixtures in `backend/tests/test_api.py` that still constructed the old four-field key. The new coordinator tests passed; the failures were stale expected-key fixtures, not runtime failures. Both fixtures now include the exact `SYNTHETIC.V1` dataset and `raw_symbol` symbology. The key validation matrix also now explicitly covers whitespace and overlength values for dataset and symbology.

## 5. Exact-head CI — corrected commit accepted

The corrected source/test commit `a065e8b2b5b1736aba076d7b12940ae317989e49` completed all four required workflows successfully:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | 45545244972 | SUCCESS — 41/41 steps |
| CodeQL Security Analysis | 45545244878 | SUCCESS — Python 8/8 and JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45545245144 | SUCCESS — 7/7 steps |
| Full Git History Secret Audit | 45545244917 | SUCCESS — 6/6 steps |

Backend pytest: **1,424 passed, 1 skipped, 6 warnings in 64.04 seconds**. The single skipped case is the isolated Redis TLS integration fixture, which is separately exercised by the workflow's Redis TLS CA/hostname enforcement step. The Trivy image report was generated and uploaded; no blanket zero-vulnerability claim is made.

The initial commit `08b974b2e6222a4bc31b7826e9b5245a227c3e40` had two stale test fixtures that still constructed the old four-field key. Both were corrected in the source/test follow-up commit above. Its Automated Tests workflow then passed. All four workflows for the corrected commit are terminal SUCCESS; no job remains running.

## 6. Indicator progress — no implementation changes

This cycle changes no indicator calculation, hook, chart renderer, visual design, or indicator test. The ledger is reconciled to the new source/test HEAD only; no indicator completion credit is awarded.

| Indicator / subsystem | Verified foundation | Chart rendering / lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close mean; first valid index 19 | Overlay/legend/toggle/lifecycle not integrated | 🟨 FOUNDATION |
| EMA20 | SMA seed; alpha 2/21; first valid index 19 | Overlay/legend/toggle/lifecycle not integrated | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides not integrated | 🟨 FOUNDATION |
| MACD12/26/9 | MACD index 25; signal/histogram index 33 | Pane, lines, histogram and zero guide not integrated | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Bands/fill/legend/toggle not integrated | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable snapshot/cache/trust gate; 7 hook test declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Renderer gated by Stage 4; two user visual references retained | 🟧 GATED |
| Volume Profile | Calculation and value-area acceptance incomplete | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL acceptance incomplete | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range/recalculation lifecycle incomplete | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity source and aggregation unaccepted | Not integrated; user visual reference pending | 🟥 OPEN |
| Liquidation Maps | Provenance/methodology/uncertainty unaccepted | Not integrated | 🟥 OPEN |

### Calculation contracts retained

- SMA20: first valid index 19.
- EMA20: SMA-seeded, alpha = 2/21, first valid index 19.
- RSI14 Wilder: first valid index 14.
- MACD12/26/9: MACD line index 25; signal/histogram index 33.
- Bollinger20,2: population standard deviation, first valid index 19.
- Warm-up values remain null; calculations remain prefix-causal and aligned to exact candle timestamps and canonical series identity.
- DEMO/loading/error/unavailable states must not expose stale or synthetic indicator output.
- Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced cluster layout.

Focused declaration inventory remains 28 (21 calculation + 7 hook). This is not indicator completion. `CandlestickChart.tsx` remains unintegrated. Aggregate indicator completion remains NOT SCORED.

## 7. Project dashboard

| Stage / meter | Current evidence | Status |
|---|---|---|
| Stage 1 | 30/40 = 75% provisional inherited baseline; not rescored here | 🟨 |
| Stage 2 | Provider-demand identity foundation improved; no approved denominator | 🟦 ACTIVE / NOT SCORED |
| Stage 3 | No approved denominator | ⬜ NOT SCORED |
| Stage 4 | Official stage/blueprint review gate remains | 🟪 GATED |
| Stage 5 | No approved denominator | ⬜ NOT SCORED |
| Stage 6 | No approved denominator | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed in current scorecard | 🟥 OPEN |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved study denominator/weights | ⚪ NOT SCORED |
| Significant progress / IP3S | Formula not approved/applied | ⚪ NOT SCORED |

## 8. Next work order — unchanged

1. Continue repository-verifiable WebSocket regression and provider-demand integration design.
2. Resolve recurring-$0 provider rights and one exact SDK/API contract before any live adapter.
3. Gate 25: owner-host authenticated snapshot transfer, receipt retrieval after restart, and durable per-gateway high-water ACK.
4. Gate 36: public WSS/TLS and production multi-instance acceptance only after deployment authorization.
5. Firebase production sign-in, revocation, entitlement and browser/Android lifecycle acceptance.
6. Redis destructive retention remains blocked until gateway inventory, PEL policy, durable floor ACK, dedicated authority and crash-safe reconciliation are proven.
7. Indicator UI remains behind Stage 4 and approved scoped blueprint.

No paid service, production credential, deployment, destructive Redis trim, Vercel action or `main` update occurred.
