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


# DEZZTA CHART — Batch 62J-224
## Exact-HEAD CI acceptance, Gate 25 production-boundary audit, and indicator ledger checkpoint

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited code/test/documentation HEAD:** `fd7b4fd42f7253d3f155b40cad45b76e14e39568`  
**Cost:** ZERO COST • **main:** untouched • **Vercel:** deployment deferred  
**Delivery target:** approximately 24 December 2026 (planning target only)

## 1. Exact-HEAD CI acceptance — Batch 223

All four required GitHub Actions workflows reached terminal SUCCESS and every reported check-run matched the exact SHA `fd7b4fd42f7253d3f155b40cad45b76e14e39568`.

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | [45416341004](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45416341004) | SUCCESS |
| CodeQL Security Analysis | [45416341144](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45416341144) | SUCCESS |
| OCI ARM64 Image Readiness | [45416341215](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45416341215) | SUCCESS |
| Full Git History Secret Audit | [45416340964](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45416340964) | SUCCESS |

Exact check-run evidence:
- Automated Tests / Test and Build: `138523475848` — completed SUCCESS.
- CodeQL JavaScript/TypeScript: `138523486230` — completed SUCCESS.
- CodeQL Python: `138523487270` — completed SUCCESS.
- OCI ARM64 / Build and smoke-test native ARM64 backend: `138523457714` — completed SUCCESS.
- Full Git History Secret Audit / Scan complete reachable Git history: `138526794517` — completed SUCCESS.

The four workflow run objects and all five listed check runs reported the same exact HEAD. This closes the Batch 223 CI-pending item. The result is repository CI evidence; it is not external production-host or real-device acceptance.

## 2. Batch 223 implementation accepted at repository CI level

The previous batch corrected a real multi-panel shared-supervisor ownership mismatch:
- `src/services/ohlcvSeriesSupervisorRegistry.ts` stores the active endpoint and canonical instrument mapping.
- New owners for an already active series are rejected if either value conflicts.
- `src/services/ohlcvSeriesSupervisorRegistry.test.ts` verifies endpoint and canonical mapping conflicts and verifies that the original owner/series remain intact.

The exact-head CI above passed after those changes. No claim is made that this closes public WSS, Firebase production E2E, owner-host receipt custody, or device lifecycle acceptance.

## 3. Gate 25 — source-backed audit and remaining boundary

Re-read current branch source:
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/app/snapshot_attestation.py`
- `backend/app/ohlcv_store.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_snapshot_receipts.py`
- `docs/GATE25_ED25519_SNAPSHOT_AUTHENTICATION.md`
- `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`

Confirmed repository-side behavior:
1. Production gateway requires a non-empty owner-pinned Ed25519 public-key allow-list.
2. Snapshot receipt signature is re-verified from persisted immutable evidence before Redis client creation.
3. Receipt source identity and signer key ID are bound to the verified attestation.
4. Installer metadata is compared against the durable replica checkpoint and immutable receipt.
5. Invalid source, generation, cursor, digest, retention policy, replica identity, schema/protocol version or authentication state fails before Redis client creation.
6. Source publisher evidence requires an exact receipt set for all configured gateway IDs, authenticated source identity, owner-signature verification, matching stream/generation/cursor/digest, unique durable replica IDs and one consistent owner signer key ID.
7. Redis client construction happens only after snapshot/receipt validation; constructor failures close a created Redis client.

No new confirmed repository-side Gate 25 defect was found in this read-only audit. A speculative code change would weaken precision rather than improve the acceptance boundary, so none was made.

**Still OPEN (external):** owner-controlled private-key provisioning/custody, authenticated owner-host callback transport, real signed snapshot transfer, retrieval of each gateway's actual persisted receipt, restart-time re-verification and multi-gateway high-water acknowledgement. The callback is an explicit trust boundary; a callback-supplied mapping is not by itself proof that a remote gateway was contacted. No credentials, host access, or external receipt evidence are available in repository CI.

## 4. WebSocket production acceptance matrix

| Area | Status |
|---|---|
| Frontend protocol, ticket exchange, reconnect and sequence guard | 🟩 Repository foundation |
| Backend authentication, ticket and subscription enforcement | 🟩 Repository foundation |
| Redis replay, replica consumer and recovery logic | 🟩 Repository foundation |
| Shared per-series supervisor owner consistency | 🟩 Batch 223 + exact-head CI |
| Gate 25 owner-host transfer and persisted remote receipt custody | 🟥 OPEN |
| Gate 36 public HTTPS/WSS and reverse proxy/TLS | 🟥 OPEN |
| Real Firebase sign-in, revocation and entitlement E2E | 🟥 OPEN |
| Real production multi-instance failover/restart | 🟥 OPEN |
| Browser production and Android physical-device lifecycle | 🟥 OPEN |
| Redis destructive retention | 🟥 BLOCKED |

Redis `XTRIM`, `XDEL` and consumer-group destruction remain unauthorized until gateway inventory/retirement, pending-entry policy, per-gateway durable floor acknowledgements, separate retention authority and crash-safe trim/reconcile are proven.

## 5. Complete indicator progress checkpoint

| Indicator / subsystem | Verified mathematical or architectural foundation | First valid index | Visible chart integration | Status |
|---|---|---:|---|---|
| SMA20 | 20-close arithmetic mean; overflow-resistant normalized summation | 19 | No overlay/toggle/legend/latest-value lifecycle | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha = 2/21 | 19 | No overlay/toggle/legend/latest-value lifecycle | 🟨 Foundation |
| RSI14 Wilder | Initial 14-change averages and Wilder recurrence; flat/rising/falling edge cases | 14 | No 0–100 pane, 30/70 guides or toggle | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram = MACD−signal | MACD 25; signal/histogram 33 | No dedicated pane, lines, histogram or toggle | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | No three-line overlay, fill or toggle | 🟨 Foundation |
| Shared Indicator Hook | Exact keyed immutable backend snapshot, shared calculation cache, trust-state gating and stale-output clearing | Per study | Not integrated into CandlestickChart | 🟨 Foundation |
| Footprint | Synthetic/educational accumulator; not exchange-native bid/ask truth | N/A | Visual reference supplied; reviewed blueprint/stage gate still applies | 🟧 Gated |
| Heatmap | No accepted depth/liquidity renderer | N/A | Not implemented; user reference and validated depth contract required | 🟥 Open |
| Liquidation Maps | No accepted calculation/runtime renderer | N/A | Not implemented; provenance and reviewed blueprint required | 🟥 Open |

Indicator test inventory remains 17 calculation-engine tests + 7 shared-hook tests = 24 focused named tests. Test count is not a completion percentage.

Calculation acceptance includes warm-up/alignment, Wilder RSI recurrence and edge handling, MACD initialization/histogram identity, Bollinger population deviation/symmetry/translation, supported timeframes, prefix causality, non-finite inputs, large-magnitude arithmetic and insufficient history. Hook acceptance includes trusted backend state, exact keyed snapshots, live revision, panel isolation, immutable shared cache and stale-output clearing.

Footprint invariant remains: OFF preserves normal candlestick spacing; explicit ON alone enables the dedicated spaced-cluster layout. Visual indicator expansion remains behind its official stage gate, scoped blueprint and user review. Footprint and Heatmap visual implementation remain reference-gated.

**Aggregate indicator progress: NOT SCORED.** No approved per-indicator weights or denominator exists.

## 6. Official project progress

| Meter | Verified value | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 criteria = 300/400 ticks = 75% provisional | 🟨 |
| Stage 2 — Market Data Infrastructure | Active engineering; denominator not approved | 🟦 NOT SCORED |
| Stages 3–6 | Not officially scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 external criteria formally closed | 🟥 OPEN |
| Overall project | No approved weighted denominator | ⚪ NOT SCORED |
| Indicator aggregate | No approved indicator denominator | ⚪ NOT SCORED |
| IP3S / significant-progress score | No approved formula applied to this batch | ⚪ NOT SCORED |

Do not extrapolate Stage 1's provisional 75% to the whole project.

## 7. ZERO COST and next execution order

1. Keep Batch 223 exact-head CI evidence accepted.
2. Continue Gate 25 only through real owner-host authenticated transfer/receipt/restart evidence; do not fabricate host success or secrets.
3. Then complete public WSS/TLS and Firebase E2E acceptance.
4. Then perform browser/Android real-device lifecycle and production multi-instance recovery.
5. Keep Redis destructive retention blocked until its separate safety acceptance is met.
6. Continue indicator foundation work within existing scope; visible UI waits for the official stage gate and approved blueprint.

No paid service, subscription, domain, market-data provider, production host, private key or credential was provisioned. No deployment, no Vercel release, and no change to `main`.

**Batch 224 conclusion:** Batch 223 is now exact-head CI accepted (4/4 workflows SUCCESS). Gate 25's repository-side verification is strong, but real owner-host transfer and durable remote receipt custody remain external OPEN blockers. WebSocket is not 100% production-complete.
