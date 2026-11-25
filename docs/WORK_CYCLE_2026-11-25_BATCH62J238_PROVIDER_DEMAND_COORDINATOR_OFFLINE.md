# Provider-demand coordinator — implementation slice (Batch 62J-238)

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Scope: provider-neutral ownership primitive + deterministic offline adapter + regression tests  
Cost: ZERO COST  
Live data: not connected, not configured, not invoked

## Source-backed problem

The authenticated WebSocket route currently registers a downstream `OhlcvStreamHub` subscription after validating the exact requested series. Its `finally` block removes that downstream subscription. This correctly isolates client queues, but it does not acquire/release upstream provider demand.

Separately, application lifespan starts `ProviderManager` at process startup. Its live source is controlled by configuration and a static symbol tuple. Consequently, downstream subscriber count and upstream provider lifecycle are separate. The existing source adapter has no verified dynamic subscribe/unsubscribe contract, and recurring live access is not accepted under ZERO COST.

## Implemented slice

Added `backend/app/provider_demand.py` with:

- Immutable upstream identity: source, venue, instrument and channel.
- Async adapter contract limited to `start(key)` / `stop(key)`; it does not expose a data socket or market event API.
- One lease per subscriber + upstream key; duplicate acquire is idempotent.
- First acquire performs one adapter start; later equivalent acquires share that start.
- Intermediate release removes only that subscriber.
- Last release performs one adapter stop.
- Unknown/already-released leases are safe no-ops.
- Failed start publishes no ownership.
- Failed final stop retains the final lease so shutdown can be retried without falsely reporting the upstream stopped.
- An asyncio lock serializes 0→1 and 1→0 transitions and concurrent ownership changes.

Added `InMemoryOfflineProviderAdapter`, which records lifecycle calls and performs no network I/O or data ingestion. It is a deterministic test fixture, not a production feed.

Added `backend/tests/test_provider_demand.py` covering shared upstream, idempotency, one owner with multiple keys, unknown release, start rollback, stop retry, concurrent acquire, invalid canonical keys and invalid subscriber identity.

## Deliberately not wired

This slice is not connected to `main.py`, `ProviderManager`, `OhlcvStreamHub`, WebSocket authentication, Firebase, Redis, or any live provider. That is intentional: the current provider adapter has no verified dynamic subscription semantics, and ZERO COST has not approved a recurring source. Wiring a local ref counter to a process-scoped fixed-symbol provider would create false acceptance.

## Acceptance boundary

Repository-local tests can prove lease accounting and adapter lifecycle ordering only. They cannot prove:
- dynamic subscription support in a real SDK;
- provider-side acknowledgement of subscribe/unsubscribe;
- continuity through provider reconnect/restart;
- multi-process shared demand;
- public WSS/TLS, production Firebase or physical client lifecycle;
- recurring-$0 source entitlement, data rights, or capacity.

Next safe steps: run the complete backend test suite and exact-HEAD CI; then audit how a future coordinator would be owned across backend processes before any runtime wiring. Keep live-source integration blocked until an independently approved, recurring-$0 and rights-compatible source plus verified adapter contract exists.

## Indicator progress ledger

This slice changes no indicator code, chart renderer, calculations, formulas, UI, or indicator test files. No indicator integration credit is awarded. The latest source inventory remains 28 focused test declarations (21 calculation engine + 7 shared hook); these are test declarations, not 28 completed indicators.

| Indicator / subsystem | Verified foundation | Visible chart integration | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle not accepted | 🟨 Foundation |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle not accepted | 🟨 Foundation |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane and 30/70 guides not accepted | 🟨 Foundation |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal; histogram identity; MACD index 25, signal/histogram index 33 | Pane, lines, histogram and zero guide not accepted | 🟨 Foundation |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | Three-line overlay, fill, toggle and latest values not accepted | 🟨 Foundation |
| Shared Indicator Hook | Keyed immutable snapshot, shared cache, trust gating and stale-output clearing | Not integrated into `CandlestickChart.tsx` | 🟨 Foundation |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Renderer remains gated; user reference images recorded | 🟧 Gated |
| Volume Profile | Complete production calculation not verified | Not integrated | 🟥 Open |
| Complete Volume Profile | Complete production calculation not verified | Not integrated | 🟥 Open |
| Movable-range Volume Profile | Range-selection/calculation lifecycle not verified | Not integrated | 🟥 Open |
| Heatmap | Accepted depth/liquidity engine not verified | Not integrated; reference/data-contract gate remains | 🟥 Open |
| Liquidation Maps | Methodology/provenance and renderer not accepted | Not integrated | 🟥 Open |

### Mathematical acceptance invariants retained

- SMA20: arithmetic mean of 20 closes; first valid source index 19.
- EMA20: SMA-seeded recurrence with alpha = 2/(20+1) = 2/21; first valid source index 19.
- RSI14: Wilder seed from 14 price changes; first valid source index 14.
- MACD12/26/9: MACD line first valid index 25; signal and histogram first valid index 33 when the signal EMA is seeded from the first valid MACD value.
- Bollinger20,2: 20-close mean ± 2 population standard deviations; first valid source index 19.
- Warm-up values remain null; no synthetic fill values, timestamp shifting, future-candle lookahead, or stale-identity carryover.

Footprint OFF must preserve standard candlestick spacing; explicit ON alone enables the dedicated spaced-cluster layout. Footprint visuals remain behind the Stage 4 gate and scoped review. Heatmap remains reference-gated. No indicator formula or chart integration was changed here.

## Project progress dashboard

| Stage / meter | Verified value | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional; inherited baseline, not re-scored in this batch | 🟨 |
| Stage 2 — Market Data Infrastructure | Active repository work; no approved denominator; not officially scored | 🟦 NOT SCORED |
| Stage 3 — Chart Engine & Timeframe | Not formally scored | ⬜ NOT SCORED |
| Stage 4 — Indicators & Analytics | Implementation gate / blueprint review required | 🟪 GATED |
| Stage 5 — Professional UI & Interactive Tools | Not formally scored | ⬜ NOT SCORED |
| Stage 6 — Hardening, Validation & APK Release | Not formally scored | ⬜ NOT SCORED |
| Gate 10 | 0/10 formally closed | 🟥 OPEN |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicator completion | No approved indicator denominator/weights | ⚪ NOT SCORED |
| IP3S / significant progress | No approved scoring formula applied | ⚪ NOT SCORED |

The coordinator code is a bounded Stage 2 engineering slice, not proof that the official Stage 2 entry gate has been approved. No Stage 1 ticks, Stage 2 score, indicator integration credit, Gate 25 external acceptance, or Gate 36 production acceptance is claimed.

## Remaining WebSocket blockers

- 🟨 Repository: existing authenticated exact-series downstream subscription and per-subscriber fan-out remain separate from upstream provider demand.
- 🟨 Repository: new local 0↔1 lease accounting is implemented; its exact-HEAD CI result must be recorded separately.
- 🟥 Integration: coordinator is intentionally not wired into WebSocket route or process-level provider lifecycle.
- 🟥 Provider contract: no verified dynamic subscribe/unsubscribe and provider acknowledgement.
- 🟥 Cross-process: no shared ownership/reconciliation across backend instances.
- 🟥 Gate 25: owner-host snapshot transfer, durable receipt retrieval/reverification and per-gateway high-water ACK remain external.
- 🟥 Gate 36: public WSS/TLS, production runtime, Firebase E2E and real browser/Android lifecycle remain external.
- 🟧 Redis destructive retention remains blocked until all independent safety prerequisites pass.

ZERO COST remains mandatory. `main` untouched. No Vercel deployment. No destructive Redis retention. APK planning target remains approximately 24 December 2026.
