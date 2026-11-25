# Provider-demand lease integrity and checkpoint reconciliation — Batch 62J-239

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent HEAD: `1929394bb557cd86369416b1d1ccfe283677b820`  
Scope: lease-token integrity hardening, regression tests, exact-HEAD CI, indicator-ledger reconciliation  
Cost: ZERO COST  
Live market data: not connected or enabled by this work cycle

## Changes

### 1. Provider-demand lease integrity

`backend/app/provider_demand.py` now distinguishes a lease object from a string lease ID:

- A `DemandLease` object must exactly match the coordinator's stored immutable lease record.
- A copied or forged object with the same random ID but different subscriber/key is rejected.
- String lease IDs remain accepted for internal recovery paths.
- Unsupported input types are rejected as safe no-ops.
- A rejected token does not mutate owner maps, subscriber counts, or adapter state.

This closes an authorization/ownership integrity gap in the local coordinator. It does not create authentication or cross-process ownership.

### 2. Regression tests

`backend/tests/test_provider_demand.py` adds:
- forged lease object cannot release the original subscriber's lease;
- non-lease/non-string values cannot mutate ownership.

The tests also assert that the genuine owner can still release its lease and the offline adapter reaches an empty active set.

## Deliberate integration boundary

The existing authenticated WebSocket route creates and removes downstream `OhlcvStreamHub` subscriptions. The provider manager is process-lifecycle/static-configuration driven. The newly hardened coordinator remains an offline ownership primitive and is not wired to the live provider manager or WebSocket route.

That separation is intentional. Connecting this coordinator to the configured live source without a verified dynamic subscribe/unsubscribe and provider acknowledgement contract would falsely mark the lifecycle as accepted. No live market-data service, derivatives venue, or recurring feed is enabled.

## WebSocket blocker disposition

| Blocker | Status | Evidence / reason |
|---|---|---|
| Coordinator ↔ WebSocket route | 🟥 OPEN | Route lifecycle has not acquired/released coordinator leases; only downstream hub subscription cleanup is wired |
| Coordinator ↔ provider lifecycle | 🟥 OPEN | ProviderManager remains process-start/static-config based; no verified dynamic adapter lifecycle |
| Dynamic subscribe/unsubscribe | 🟥 OPEN | SDK-level subscribe/unsubscribe acknowledgement contract not verified |
| Cross-process demand ownership | 🟨 PARTIAL / NOT ACCEPTED | Local coordinator serializes within one asyncio process only; no shared durable owner registry or multi-host acceptance |
| Public WSS/TLS and production E2E (Gate 36) | 🟥 OPEN | Requires external public endpoint, TLS/proxy, identity/entitlement, Android/WebView and failover evidence |
| Gate 25 external snapshot acceptance | 🟥 OPEN | Requires owner-host key custody, authenticated gateway receipt transfer, restart/reverification and durable per-gateway high-water ACK |
| Redis destructive retention | 🟧 BLOCKED | No XTRIM/XDEL/group destruction until all gateway ACK, pending-entry, retirement and crash-reconciliation evidence is complete |

Do not change these statuses to green based only on offline unit tests.

## Exact-HEAD CI

The parent commit `1929394bb557cd86369416b1d1ccfe283677b820` was independently verified with all four workflows terminal-success:
- Automated Tests — run 45529700445
- CodeQL — run 45529700446
- OCI ARM64 Image Readiness — run 45529700477
- Full Git History Secret Audit — run 45529700450

This CI evidence belongs to the parent SHA. The new lease-integrity commit must receive its own exact-HEAD CI before it is considered verified.

## Indicator progress ledger

No indicator calculation or renderer source was changed in this batch. No new indicator completion credit is awarded.

| Indicator | Calculation foundation | Chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, visibility, legend/latest value and lifecycle not accepted | 🟨 FOUNDATION |
| EMA20 | SMA-seeded recurrence; alpha 2/21; first valid index 19 | Overlay, visibility, legend/latest value and lifecycle not accepted | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed and Wilder recurrence; first valid index 14 | Dedicated 0–100 pane and 30/70 guides not accepted | 🟨 FOUNDATION |
| MACD12/26/9 | MACD first valid index 25; signal/histogram index 33 | Dedicated pane, lines, histogram and zero guide not accepted | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Three-line overlay, fill and latest values not accepted | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed snapshot/cache and trust gating foundations | Not integrated into CandlestickChart | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only | Visual renderer remains gated; supplied references recorded | 🟧 GATED |
| Volume Profile | Complete production calculation not verified | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Complete production calculation not verified | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/calculation lifecycle not verified | Not integrated | 🟥 OPEN |
| Heatmap | Accepted depth/liquidity engine not verified | Not integrated; reference/data-contract gate remains | 🟥 OPEN |
| Liquidation Maps | Methodology, provenance and renderer not accepted | Not integrated | 🟥 OPEN |

### Numerical invariants

- SMA20: mean of closes (C_{t-19}...C_t), first valid index 19.
- EMA20: α = 2/(20+1) = 2/21, SMA-seeded, first valid index 19.
- RSI14: seed from 14 close-to-close changes, Wilder recurrence, first valid index 14.
- MACD12/26/9: EMA12−EMA26, first MACD index 25; EMA9 signal and histogram first index 33 under first-valid-MACD seeding.
- Bollinger20,2: mean ± 2 population standard deviations, first valid index 19.
- Warm-up values remain null; no lookahead, timestamp shift, or stale-series carryover.

Footprint OFF retains ordinary candlestick spacing; explicit ON alone selects the spaced-cluster renderer. Heatmap remains reference-gated. No indicator visual work begins without the relevant approved reference and scoped blueprint.

## Project progress dashboard

| Stage / meter | Value | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional inherited baseline | 🟨 |
| Stage 2 — Market Data Infrastructure | Active; no approved denominator | 🟦 NOT SCORED |
| Stage 3 — Chart Engine & Timeframe | No approved score | ⬜ NOT SCORED |
| Stage 4 — Indicators & Analytics | Gated; no approved aggregate denominator | 🟪 GATED |
| Stage 5 — Professional UI & Interactive Tools | No approved score | ⬜ NOT SCORED |
| Stage 6 — Hardening, Validation & APK Release | No approved score | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed (inherited ledger) | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved indicator denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved scoring formula | ⚪ NOT SCORED |

## Constraints retained

- ZERO COST only; no paid hosting, subscriptions, or paid data sources.
- No Vercel deployment.
- `main` remains untouched.
- No live data connection or live trading integration.
- No destructive Redis retention.
- Target delivery remains around 24 December 2026; this is a planning target, not a completion guarantee.
