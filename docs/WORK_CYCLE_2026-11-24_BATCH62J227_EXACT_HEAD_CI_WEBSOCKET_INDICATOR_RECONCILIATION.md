# DEZZTA CHART — Batch 62J-227
## Exact-HEAD CI closure, WebSocket boundary re-audit, and indicator ledger synchronization



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
