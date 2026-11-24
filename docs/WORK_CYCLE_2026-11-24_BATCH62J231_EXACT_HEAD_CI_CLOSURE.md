# DEZZTA CHART — Batch 62J-231

## Exact-HEAD CI closure and correction evidence reconciliation (24 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact code/test HEAD:** 1b7096566030f7c7775958c1fb60fbe628a3b7f1  
**Cost:** ZERO COST • main untouched • no Vercel deployment.

### 1. Exact-HEAD CI — terminal success

All four configured workflows reference the exact SHA above and reached terminal SUCCESS:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45435451481](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451481) | 🟩 SUCCESS — 41/41 steps |
| CodeQL Security Analysis | [45435451743](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451743) | 🟩 SUCCESS — Python 8/8; JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | [45435451497](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451497) | 🟩 SUCCESS — 7/7 steps |
| Full Git History Secret Audit | [45435451477](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45435451477) | 🟩 SUCCESS — 6/6 steps |

No workflow remains queued or running for this exact SHA.

### 2. Backend test evidence

The Automated Tests log reports **1,393 passed, 1 skipped, 6 warnings in 61.36 seconds**. The single skip is the separately configured Redis TLS integration fixture.

The following new tests explicitly appear as PASSED in the backend pytest log:
- test_source_signing_key_loader_rejects_symbolic_links
- test_source_signing_key_loader_rejects_non_regular_files
- test_source_signing_key_loader_rejects_oversized_files

This closes the correction gap identified after Batch 62J-229. The first source-hardening commit passed its own CI, but post-CI diff inspection found that the intended three test functions had not been included. Batch 62J-230 added them, and this report verifies their actual execution and pass result.

### 3. Source change verified

The source implementation in backend/app/snapshot_attestation.py now:
- opens the key path once and validates the opened descriptor;
- requires POSIX O_NOFOLLOW;
- requires a regular file;
- requires effective-service-user ownership on POSIX;
- rejects group/world permissions;
- reads at most 64 KiB of PEM material;
- closes the descriptor on every path;
- retains Ed25519 type validation.

No production key, credential, host detail or secret was accessed or committed.

### 4. WebSocket / Gate 25 state

| Scope | Status |
|---|---|
| Ed25519 canonical attestation and trust-key verification | 🟩 Repository verified |
| Immutable receipt persistence and checkpoint/digest binding | 🟩 Repository verified |
| Safe source-host key-file boundary and regression tests | 🟩 Repository verified; exact-HEAD CI passed |
| Owner-host private-key custody | 🟥 External acceptance open |
| Authenticated remote snapshot transfer | 🟥 External acceptance open |
| Receipt retrieval from every gateway | 🟥 External acceptance open |
| Restart re-verification and durable per-gateway high-water ACK | 🟥 External acceptance open |
| Gate 25 parent acceptance | 🟥 OPEN |
| Public HTTPS/WSS, reverse proxy/TLS and production runtime | 🟥 OPEN |
| Firebase production sign-in/entitlement/revocation E2E | 🟥 OPEN |
| Browser/Android real lifecycle and production multi-instance failover | 🟥 OPEN |
| Redis destructive retention | 🟧 BLOCKED pending all independent safety prerequisites |

CI success verifies repository tests and build/security workflows, not the owner-host and production acceptance criteria.

### 5. Indicator progress — complete inventory

The focused indicator suites remain **28 named declarations = 21 calculation-engine + 7 shared-hook tests**. Batch 229–231 changed no indicator code, so no indicator completion credit is awarded.

| Indicator / subsystem | Foundation | Chart/UI integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay/toggle/legend/lifecycle absent | 🟨 |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides absent | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; indices 25/33 | Pane, lines, histogram and zero guide absent | 🟨 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Bands/fill/toggle/latest values absent | 🟨 |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating, stale clearing | Not integrated into CandlestickChart | 🟨 |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer gated; owner reference images recorded | 🟧 |
| Volume Profile | Incomplete | Not integrated | 🟥 |
| Complete Volume Profile | Incomplete | Not integrated | 🟥 |
| Movable-range VP Tool | Incomplete | Not integrated | 🟥 |
| Heatmap | Depth/liquidity engine not verified | Not integrated; reference gate remains | 🟥 |
| Liquidation Maps | Methodology/provenance not verified | Not integrated | 🟥 |

Footprint OFF retains standard candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visual work remains behind the stage gate, scoped blueprint and user review.

**Aggregate indicator completion: ⚪ NOT SCORED.** No approved denominator/weights exist.

### 6. Project progress dashboard

| Meter | Current evidence | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 criteria = 75% provisional; inherited baseline, not rescored | 🟨 |
| Stage 2 — Market Data Infrastructure | Active; denominator not approved | 🟦 NOT SCORED |
| Stage 3 — Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 — Indicators & Analytics | Stage gate and reviewed blueprint required | 🟪 GATED |
| Stage 5 — Professional UI & Interactive Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 — Hardening, Validation & APK Release | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved six-stage weighted denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved formula applied | ⚪ NOT SCORED |

No overall percentage is inferred from Stage 1's 75%.

### 7. Next execution order

1. Continue repository-verifiable WebSocket/Redis safety work without weakening fail-closed boundaries.
2. Close Gate 25 only with actual owner-host authenticated transfer, durable receipt retrieval, restart re-verification and per-gateway high-water ACK evidence.
3. Then close public HTTPS/WSS and Firebase production E2E.
4. Then complete browser/Android lifecycle, network handover and production multi-instance failover.
5. Redis destructive retention only after gateway inventory/retirement, PEL policy, per-gateway floor ACK, separate authority and crash-safe trim/reconcile all pass.
6. Keep chart indicator UI behind the formal stage gate and scoped reviewed blueprint.

**Batch result:** exact-HEAD CI 4/4 terminal SUCCESS; all three key-loader regression tests PASSED; external Gate 25 and production WebSocket acceptance remain open; indicator and overall project completion remain NOT SCORED.
