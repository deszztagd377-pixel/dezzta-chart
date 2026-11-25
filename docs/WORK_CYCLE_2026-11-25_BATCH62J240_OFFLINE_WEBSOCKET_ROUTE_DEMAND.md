# Offline WebSocket route demand integration — Batch 62J-240 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Parent HEAD:** `4262019813feff3f524101684eea36b945f0b513`  
**Scope:** authenticated WebSocket route ↔ local synthetic/offline demand lease lifecycle.  
**ZERO COST:** local in-memory adapter only. **Vercel:** no deployment. **main:** untouched.

## Implemented boundary

- `create_app` owns an `InMemoryOfflineProviderAdapter` and `ProviderDemandCoordinator`.
- Only the explicit `provider=offline-fixture` identity acquires a demand lease.
- Lease acquisition occurs after canonical mapping, active-instrument, calendar and entitlement checks.
- Demand key is deterministic from source, synthetic venue, canonical instrument ID and OHLCV timeframe.
- The route's existing `finally` cleanup unsubscribes the downstream stream and releases the offline lease, including disconnect and early-return paths after acquisition.
- Other provider identities do not acquire this adapter. No network client, provider SDK, live feed, external ACK or recurring data service is enabled.

## Regression evidence added

`backend/tests/test_api.py` adds a route-level test with two authenticated synthetic subscribers:
- first subscriber starts exactly one offline demand;
- second subscriber shares that demand (subscriber count 2, still one start);
- second disconnect leaves first lease active;
- final disconnect releases the last lease and stops the in-memory adapter;
- final lease count and adapter active set are both zero.

This is local single-process lifecycle evidence only. It does not close provider lifecycle, provider ACK, multi-process ownership, public WSS/TLS or production E2E gates.

## WebSocket blocker status

| Item | Status | Evidence |
|---|---|---|
| Offline coordinator primitive + token integrity | 🟩 | Existing coordinator tests and Batch 62J-239 lease-forgery regression |
| Synthetic route acquire/release lifecycle | 🟩 | Batch 62J-240 route-level two-subscriber/disconnect regression (subject to exact-HEAD CI) |
| Route ↔ external provider lifecycle | 🟥 | Deliberately not connected; outside offline-only boundary |
| Dynamic external subscribe/unsubscribe ACK | 🟥 | No external provider contract or ACK verification |
| Cross-process / multi-host demand ownership | 🟨 | In-memory coordinator is one process only |
| Public WSS/TLS and client E2E (Gate 36) | 🟥 | External endpoint, identity, TLS and device evidence absent |
| Gate 25 external snapshot receipt/high-water ACK | 🟥 | Owner-host custody and durable gateway ACK evidence absent |
| Redis destructive retention | 🟧 | No destructive trimming/deletion until all pending-entry and gateway acceptance proofs exist |

## Indicator progress — no false completion credit

No indicator calculation engine or renderer was changed in this batch. Existing verified foundations and chart integration gaps remain:

| Indicator | Calculation foundation | Chart integration | Overall |
|---|---|---|---|
| SMA20 | 🟩 20-close arithmetic mean; first valid index 19 | 🟥 overlay/legend/visibility/lifecycle not accepted | 🟨 Foundation |
| EMA20 | 🟩 SMA-seeded; α=2/21; first valid index 19 | 🟥 overlay/legend/visibility/lifecycle not accepted | 🟨 Foundation |
| RSI14 Wilder | 🟩 14-change seed + Wilder recurrence; first valid index 14 | 🟥 dedicated 0–100 pane and guides not accepted | 🟨 Foundation |
| MACD12/26/9 | 🟩 MACD first index 25; signal/histogram index 33 | 🟥 pane, lines, histogram and zero guide not accepted | 🟨 Foundation |
| Bollinger20,2 | 🟩 20-close mean ± 2 population SD; first valid index 19 | 🟥 upper/middle/lower overlay and fill not accepted | 🟨 Foundation |
| Shared Indicator Hook | 🟨 keyed snapshot/cache and trust-gating foundation | 🟥 not integrated into CandlestickChart | 🟨 Foundation |
| Footprint PRO 2GD | 🟨 synthetic/offline accumulator | 🟥 renderer gated; reference match not implemented | 🟧 Gated |
| Volume Profile | 🟥 complete calculation not verified | 🟥 not integrated | 🟥 Open |
| Complete Volume Profile | 🟥 complete calculation not verified | 🟥 not integrated | 🟥 Open |
| Movable-range Volume Profile | 🟥 range selection/calculation lifecycle not verified | 🟥 not integrated | 🟥 Open |
| Heatmap | 🟥 depth/liquidity engine not accepted | 🟥 not integrated; user reference still required | 🟥 Open |
| Liquidation Maps | 🟥 methodology/provenance not accepted | 🟥 not integrated | 🟥 Open |

Numerical invariants: SMA/EMA/Bollinger first valid index 19; RSI14 index 14; MACD line index 25 and signal/histogram index 33 under first-valid-MACD seeding. Warm-up remains null; outputs must be prefix-causal, timestamp-aligned and cleared on series changes. Footprint OFF must preserve ordinary candles; ON alone selects spaced clusters.

## Project dashboard

| Stage / measure | Status |
|---|---|
| Stage 1 | 🟨 30/40 = 75% provisional inherited baseline |
| Stage 2 — data infrastructure | 🟦 Active; no approved denominator |
| Stage 3 — chart engine/timeframe | ⬜ Not scored |
| Stage 4 — indicators/analytics | 🟪 Gated; aggregate not scored |
| Stage 5 — professional UI/tools | ⬜ Not scored |
| Stage 6 — hardening/APK | ⬜ Not scored |
| Gate 10 | 🟥 0/10 formally closed |
| Overall project | ⚪ NOT SCORED — no approved weighted denominator |
| Aggregate indicator completion | ⚪ NOT SCORED — no approved denominator |
| Significant progress / IP3S | ⚪ NOT SCORED — no approved formula |

Target remains around **24 December 2026** as a planning target, not a guarantee. No paid service, Vercel deployment, live data connection, main-branch update or destructive Redis retention is part of this batch.

---

