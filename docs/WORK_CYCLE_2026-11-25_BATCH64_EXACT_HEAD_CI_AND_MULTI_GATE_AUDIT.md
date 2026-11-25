# Work Cycle 64 — exact-HEAD CI reconciliation and multi-gate engineering audit (25 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Parent / audited HEAD:** `6b4eedc2387e5e8a300e78c713861e2efa156678`  
**Scope:** exact-HEAD CI evidence reconciliation, WebSocket/Gate 25/Gate 36/provider/Redis retention audit, and indicator progress reconciliation.  
**Source changes:** none in this cycle. No source patch was made because the remaining open acceptance items require external owner-host, public endpoint, provider-rights, or production identity evidence; inventing those integrations would violate fail-closed and ZERO COST constraints.

## 1. Exact-HEAD CI — verified terminal state

All four workflows below reference the exact parent HEAD `6b4eedc2387e5e8a300e78c713861e2efa156678` and are terminal SUCCESS:

| Workflow | Run ID | Job / steps | Result |
|---|---:|---:|---|
| Automated Tests | 45541050465 | Test and Build, 41/41 steps | 🟩 SUCCESS |
| CodeQL Security Analysis | 45541050505 | JavaScript/TypeScript 8/8; Python 8/8 | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | 45541050539 | ARM64 build/smoke job, 7/7 steps | 🟩 SUCCESS |
| Full Git History Secret Audit | 45541050527 | History scan, 6/6 steps | 🟩 SUCCESS |

Automated Tests log: **1,419 passed, 1 skipped, 6 warnings in 51.92s**. The skipped test is `tests/test_shared_guard_tls_integration.py:22` because the isolated Redis TLS fixture was not configured for that invocation. The distinct CI Redis TLS CA/hostname enforcement step completed successfully; neither fact establishes owner-host or public production TLS acceptance.

All five reported jobs and every listed step are completed. No workflow/job from these four exact-HEAD runs remains running. The Automated Tests job also completed frontend unit tests/build, backend tests, container smoke tests, and security/dependency audit steps. ARM64 readiness is a build/smoke test, not production deployment acceptance.

**Historical correction:** the previous Batch 62J-244 ledger entry named older documentation HEAD `47a62428...` and cited 1,419/1/6 from a prior run. The current exact-head evidence is now explicitly tied to `6b4eedc2387e5e8a300e78c713861e2efa156678`; do not conflate the two commits.

## 2. WebSocket and external gate status

| Gate / workstream | Status | Verified boundary / remaining work |
|---|---|---|
| Gate 25 owner-host snapshot custody | 🟥 OPEN | Ed25519 signing/verifying, canonical payload and private-key file safety exist. Still requires owner-host key custody, authenticated delivery to each gateway, durable receipt retrieval after restart, and durable per-gateway high-water ACK. |
| Gate 36 public HTTPS/WSS | 🟥 OPEN | Internal ticket/auth, replay, watermark, reconnect and isolation foundations exist. Public endpoint, reverse proxy, production TLS and multi-instance acceptance remain unverified; deployment remains deferred. |
| Firebase/client production acceptance | 🟥 OPEN | Config validation and initialization tests exist. Real sign-in, expiry/revocation, entitlement denial, ticket exchange and browser/Android lifecycle acceptance remain outstanding. |
| Provider demand → real adapter | 🟥 OPEN | Coordinator remains deliberately offline-fixture only. No verified zero-cost provider contract with lawful display/redistribution scope and exact dynamic subscribe/unsubscribe ACK contract. |
| Redis destructive retention | 🟧 BLOCKED | Do not enable XTRIM/XDEL. Require gateway inventory, pending-entry proof, durable per-gateway floor ACK, crash-safe reconciliation and dedicated ACL. |
| Repository WebSocket regression | 🟩 VERIFIED BASELINE | Exact-head automated tests passed; continue regression coverage without implying production acceptance. |

No paid provider, production credential, external public endpoint, destructive trim, or deployment was activated.

## 3. Indicator progress — full current inventory

| Indicator / subsystem | Calculation or data foundation | Chart rendering / interaction / lifecycle | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19; calculation tests | Overlay, legend, visibility toggle and lifecycle not integrated | 🟨 FOUNDATION |
| EMA20 | SMA seed, alpha 2/21; first valid index 19 | Overlay, legend, visibility toggle and lifecycle not integrated | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | Dedicated 0–100 pane, 30/70 guides and lifecycle not integrated | 🟨 FOUNDATION |
| MACD12/26/9 | MACD first index 25; signal/histogram first index 33 | Dedicated pane, lines, histogram, zero guide and lifecycle not integrated | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Bands/fill/legend/toggle and lifecycle not integrated | 🟨 FOUNDATION |
| Shared Indicator Hook | Identity-bound immutable backend snapshot/cache; trust-state suppression; 7 hook test declarations | `CandlestickChart.tsx` still does not import/call the hook | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Renderer remains gated; supplied two user references define visual target | 🟧 GATED |
| Volume Profile | Binning/value-area method not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Depth/liquidity source, aggregation and decay method not accepted | Not integrated; wait for user visual reference | 🟥 OPEN |
| Liquidation Maps | Provenance, estimation method and confidence limits not accepted | Not integrated | 🟥 OPEN |

**Calculation contracts:** SMA20 first valid index 19; EMA20 SMA-seeded alpha 2/21 first valid index 19; RSI14 Wilder first valid index 14; MACD12/26/9 MACD index 25 and signal/histogram index 33; Bollinger20,2 population standard deviation first valid index 19.

**Invariant set:** warm-up remains null; prefix-causal/no future lookahead; exact source timestamp and series identity alignment; stale outputs cleared on instrument/timeframe change; no indicator output for DEMO/loading/unavailable/error/empty snapshots; reconnect/correction/live update alignment preserved. Footprint OFF must preserve normal candle spacing; only explicit ON uses spaced clusters. Heatmap visual work remains reference-gated.

Focused declaration inventory remains 28 (21 calculation + 7 shared hook). These are declarations, not pass counts or indicator completion. No chart indicator integration changed in this cycle.

## 4. Progress dashboard and accounting

| Meter | Current defensible value | Status |
|---|---:|---|
| Stage 1 | 30/40 = 75% provisional inherited baseline; not re-audited here | 🟨 |
| Stage 2 | Active engineering; no approved denominator | 🟦 NOT SCORED |
| Stage 3 | No official score | ⬜ NOT SCORED |
| Stage 4 | Official indicator/UI gate remains parked | 🟪 GATED |
| Stage 5 | No official score | ⬜ NOT SCORED |
| Stage 6 | No official score | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved weighted indicator denominator | ⚪ NOT SCORED |
| Significant progress / IP3S | No approved formula applied | ⚪ NOT SCORED |

Do not infer whole-project completion from Stage 1's provisional 75%. This cycle earns no Stage tick, no indicator rendering credit and no external WebSocket gate closure. CI green means repository workflow success only.

## 5. Ordered next actions — unchanged sequence

1. Gate 25: continue repository-verifiable receipt schema/recovery and ACK contract tests; external owner-host custody and per-gateway proof remain required for closure.
2. Gate 36: prepare public WSS/TLS acceptance matrix; execute production endpoint tests only after explicit deployment authorization.
3. Firebase/client: strengthen repository-side deterministic expiry/revocation/entitlement tests where exact existing interfaces permit; production identity and device/browser E2E remain external acceptance.
4. Redis retention: add only non-destructive safety proofs and reconciliation design; keep XTRIM/XDEL disabled until every prerequisite is proven.
5. Continue WebSocket replay/reconnect/recovery regression and exact-head CI checks.
6. Provider: verify zero-cost legal display/redistribution scope and adapter contract before wiring any live source.
7. Indicators: preserve official Stage 4 gate and scoped blueprint/user review; no visual implementation before approval/reference requirements.

**Controls:** ZERO COST; `main` untouched; no Vercel deployment; no paid feed/hosting; no destructive Redis retention; target delivery planning remains around **24 December 2026**.
