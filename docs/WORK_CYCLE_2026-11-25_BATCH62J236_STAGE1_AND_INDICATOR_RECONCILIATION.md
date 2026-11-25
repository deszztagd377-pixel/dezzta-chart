# DEZZTA CHART — Batch 62J-236
## Stage 1 blocker reconciliation and source-verified indicator inventory

**Date:** 25 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent exact HEAD:** `2553b942fbcb99d2a9f9b078ad2ff3be5d242912`  
**Source/test baseline:** `bd4904b52d29b3ec456da91014e90922fec35f21`  
**Cost:** ZERO COST  
**Vercel:** no deployment  
**Main:** untouched  
**Delivery planning target:** approximately 24 December 2026

## 1. Exact-parent CI closure

The parent documentation commit has four terminal-success workflows on the exact same SHA:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | 45526623643 | SUCCESS — 41/41 steps |
| CodeQL | 45526623850 | SUCCESS — Python 8/8, JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45526623693 | SUCCESS — 7/7 steps |
| Full Git History Secret Audit | 45526623570 | SUCCESS — 6/6 steps |

Backend pytest: **1,394 passed, 1 skipped, 6 warnings in 64.11 seconds**. The one skip is `tests/test_shared_guard_tls_integration.py`, because the isolated Redis TLS CI fixture is not configured. Do not report this as a passing real Redis TLS acceptance test.

The container smoke test passed backend health JSON validation, Redis ACL authentication and AOF persistence across restart, fail-closed behavior during Redis outage, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection. These are CI/container-fixture results, not owner-host production proof.

## 2. Stage 1: exact remaining blockers

The acceptance matrix contains 40 criteria. Its provisional evidence meter remains **30/40 = 75%**. The ten outstanding criteria are:

| Criterion | Required evidence still missing | Status |
|---|---|---|
| 8 | Actual owner-host secret injection, file owner/mode, UID 10001 readability, runtime exposure, rotation and log/crash checks | 🟨 |
| 20 | Real no-billing Firebase sign-in, expiry/revocation, entitlement denial, ticket exchange, browser and Android reconnect | 🟥 |
| 25 (Stage 1 criterion) | Self-hosted Redis TLS certificate validation, ACL, private binding/firewall, persistence, restart, outage and recovery on existing hardware | 🟥 |
| 30 | Actual application DB restore into a fresh target database with application-level readback on the owner's runtime | 🟨 |
| 31 | Encrypted off-host backup, separate key custody, retention/access policy and recovery restore | 🟥 |
| 34 | Real persistent storage mount/ownership/permissions, restart durability, disk pressure and recovery | 🟨 |
| 35 | Backend runtime/health/secret injection on existing owner-controlled hardware; public route only if no incremental cost | 🟨 |
| 36 | Authenticated HTTPS/WSS through a real reverse proxy from browser and Android clients, reconnect/resnapshot and cross-instance behavior | 🟥 |
| 38 | Durable owner-host metrics, retention, backup/restore, disk pressure, firewall, token rotation, dashboard and independent alert/ACK/recovery | 🟧 |
| 39 | Zero-cost local alert path, incident owner, escalation, acknowledgement and recovery drill | 🟨 |

**Gate 10:** 0/10 formally closed. CI success, synthetic tests and documentation do not close owner-host/device criteria.

**Naming distinction:** Stage 1 criterion #25 is Redis TLS/ACL/persistence. Project Gate 25 is the separate Ed25519 signed-snapshot installation/receipt/high-water-ACK path. Project Gate 25 still needs owner-host private-key custody, authenticated transfer to every gateway, receipt retrieval after restart, re-verification and durable per-gateway high-water ACK.

## 3. Owner device constraint and practical priority

The project acceptance notes record a single-device environment: Infinix GT20 / Android 15, without a second phone, PC or laptop. This changes which external checks can be performed without cost:

- Criterion 30 is the strongest phone-only candidate if, and only if, the actual backend database is on the phone and its real path/process context can be established. A phone-side copy of a remote database is not acceptable.
- Criterion 20 can only advance if an already-existing Firebase project is verified no-billing and a real backend route is available. Never enable billing to force this.
- Criteria requiring an independently operated host, a second device, off-host key custody or production reverse proxy remain constrained/deferred until an already-existing zero-cost environment can prove them.
- Do not buy hardware, storage, domain, hosting, Redis, Firebase billing, monitoring, backup or market-data service. Do not weaken the criteria to inflate the percentage.

## 4. Indicator inventory — source verified

### 4.1 Calculation engine

| Indicator | Formula / method | First valid index | Current status |
|---|---|---:|---|
| SMA20 | Arithmetic mean of the latest 20 closes | 19 | 🟨 Calculation only |
| EMA20 | SMA-seeded EMA, α = 2/(20+1) = 2/21 | 19 | 🟨 Calculation only |
| RSI14 Wilder | First 14 close-to-close changes seed average gain/loss; subsequent Wilder recurrence | 14 | 🟨 Calculation only |
| MACD12/26/9 | EMA12 − EMA26; EMA9 of initialized MACD values; histogram = MACD − signal | MACD 25; signal/histogram 33 | 🟨 Calculation only |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | 🟨 Calculation only |

Warm-up values are `null`; no fabricated values are emitted. The engine rejects non-finite inputs/results, uses numerically safer mean handling, and has prefix-causality tests so future candles do not rewrite earlier outputs. The MACD histogram identity, RSI bounds/seed recurrence, Bollinger symmetry/translation behavior, and supported timeframe calculation paths have explicit tests.

### 4.2 Shared hook

`useMarketIndicators`:
- selects the exact canonical market-series snapshot;
- returns values only for backend-origin `ready` or `degraded` snapshots;
- returns null for demo, loading, unavailable, error or empty snapshots;
- caches calculations by immutable snapshot object in a WeakMap;
- freezes returned arrays/points to prevent shared mutation;
- recalculates when a new immutable snapshot revision arrives;
- isolates different canonical series and shares one result across panels using the same snapshot revision.

**Critical integration gap:** `CandlestickChart.tsx` imports `useMarketDataSeriesSnapshot`, but not `useMarketIndicators`. It creates and updates only the candlestick series. No visible SMA/EMA overlays, RSI/MACD panes, Bollinger bands, toggles or legends are wired to this hook. Therefore the six calculation/hook components remain foundation-only, not chart-complete.

### 4.3 Exact test declaration inventory

`src/indicators/indicatorCalculations.test.ts` — 21 test declarations:
1. aligns SMA and EMA to source bars and preserves warm-up nulls
2. calculates Wilder RSI with explicit flat and rising edge cases
3. keeps MACD signal warm-up separate from MACD values
4. uses population standard deviation for Bollinger bands
5. exposes a single multi-indicator calculation entry point
6. calculates every shared indicator on every supported chart timeframe
7. rejects invalid periods and non-finite values
8. keeps every indicator prefix-causal so future candles cannot change earlier values
9. handles falling-only RSI and period-one moving averages at exact source indices
10. fails closed instead of emitting infinite values from finite extreme inputs
11. keeps RSI numerically stable when gain/loss magnitudes are very large but finite
12. computes representable SMA means without overflowing the intermediate sum
13. keeps Bollinger population deviation finite for large same-sign prices
14. preserves small residuals between large cancelling SMA inputs
15. preserves small residuals in the Bollinger middle band under cancellation
16. matches the Wilder RSI seed and recursive smoothing on alternating gains and losses
17. rejects a non-finite close at the shared multi-indicator boundary
18. keeps RSI bounded and finite across a deterministic mixed market path
19. preserves the MACD histogram identity at every initialized source index
20. keeps Bollinger width translation-invariant and bands symmetric around the mean
21. keeps every study in warm-up state when history is shorter than its slowest period

`src/indicators/useMarketIndicators.test.ts` — 7 test declarations:
1. returns no indicator output without a selected backend series
2. calculates indicators from the exact selected keyed snapshot
3. recalculates from a new immutable snapshot revision after a live bar update
4. keeps simultaneous panel calculations isolated by canonical series
5. shares one frozen calculation result across panels on the same snapshot revision
6. keeps degraded backend indicators but clears demo and error snapshots
7. clears indicator output when the selected series becomes unavailable

**Total: 21 + 7 = 28 named declarations.** Backend Gate 25 security tests are excluded from this indicator count.

### 4.4 Advanced indicator backlog

| Indicator / subsystem | Foundation | Visible chart integration | Status |
|---|---|---|---|
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Dedicated renderer and cluster layout not integrated | 🟧 |
| Volume Profile | Complete calculation/acceptance not verified | Not integrated | 🟥 |
| Complete Volume Profile | Complete calculation/acceptance not verified | Not integrated | 🟥 |
| Movable-range Volume Profile | Range selection and calculation lifecycle not verified | Not integrated | 🟥 |
| Heatmap | Accepted depth/liquidity data contract not verified | Not integrated; visual reference/blueprint gate | 🟥 |
| Liquidation Maps | Methodology and provenance not accepted | Not integrated | 🟥 |

Footprint OFF must preserve standard candlestick spacing. Only explicit Footprint ON may activate spaced candle clusters. Footprint/Heatmap visual work remains behind scoped blueprint and owner review. The user's two Footprint references are already recorded; Heatmap reference remains outstanding.

Aggregate indicator completion is **NOT SCORED** because no approved indicator denominator/weights exist.

## 5. Project progress dashboard

| Area | Progress | Status |
|---|---:|---|
| Stage 1 | 30/40 = 75% provisional | 🟨 Active, not production-accepted |
| Stage 2 | No approved denominator | 🟦 Active engineering / NOT SCORED |
| Stage 3 | No approved denominator | ⬜ NOT SCORED |
| Stage 4 | Formal stage gate and reviewed blueprint required | 🟪 GATED |
| Stage 5 | No approved denominator | ⬜ NOT SCORED |
| Stage 6 | No approved denominator | ⬜ NOT SCORED |
| Gate 10 | 0/10 closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved denominator | ⚪ NOT SCORED |
| IP3S / significant progress | No approved formula applied | ⚪ NOT SCORED |

Do not infer overall project completion from Stage 1's 75%.

## 6. WebSocket next engineering sequence

1. Complete Project Gate 25 owner-host signed snapshot transfer, per-gateway receipt retrieval after restart, re-verification and durable high-water ACK.
2. Complete Stage 1 criterion #25 Redis TLS/ACL/private binding/persistence/restart proof on existing owner hardware.
3. Complete Stage 1 host/device criteria in the approved zero-cost order.
4. Only after Gate 25 and Stage 1 prerequisites, proceed to public HTTPS/WSS, TLS/reverse proxy and production runtime proof (Gate 36).
5. Complete Firebase no-billing sign-in/entitlement/revocation E2E and browser/Android lifecycle.
6. Keep Redis destructive retention blocked until all gateway inventory, retirement, PEL, durable floor ACK, separate retention authority and crash-safe trim/reconcile requirements are accepted.
7. Provider upstream demand reference counting remains a separate Stage 2 blocker. Its coordinator/SDK implementation is gated on the scoped blueprint review and a pinned/tested SDK contract. Databento remains potentially billable; do not activate it under ZERO COST.

## 7. Execution controls

- No source/runtime code was changed in Batch 62J-236.
- No dependency change, provider activation, secret handling, external account, paid service, production deployment or Vercel deployment.
- `main` remains untouched.
- No Redis `XTRIM`, `XDEL` or consumer-group destruction.
- All documentation changes must receive exact-HEAD CI before being reported as verified.
- APK target remains approximately 24 December 2026, planning target only.

**Batch result:** Stage 1 blockers and indicator inventory reconciled; exact-parent CI 4/4 SUCCESS; owner-host/device production acceptance remains open; overall project and aggregate indicator completion remain unscored.
