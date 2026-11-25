# DEZZTA CHART — Work Cycle 87: Indicator + WebSocket Evidence Reconciliation

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Audited source/test HEAD: `471eb4413a716922b20a5503fe5165607e77947f`  
Cost ceiling: ZERO COST  
Planning target: around 24 December 2026

## 1. Scope and safety boundary

This cycle audits the latest confirmed branch head and reconciles the indicator, Worker proof, CI and stage dashboards. It does not deploy Cloudflare resources, connect a paid market-data provider, modify production configuration, or touch `main`.

The confirmed branch comparison reports `phase-2/market-data-foundation` identical to source/test HEAD `471eb4413a716922b20a5503fe5165607e77947f` (0 ahead / 0 behind). The source/test head is therefore a stable audit anchor for this cycle.

The branch's latest source change is the Cloudflare proof regression-test commit. The current work package is documentation-only; it must not be represented as new runtime or indicator implementation.

## 2. WebSocket / Cloudflare proof — exact current state

### Repository artifacts verified

- `cloudflare/wrangler.jsonc` blob: `b25de82ed9e82d294b92a336c89b3b45153738a0`
- `cloudflare/proof/worker.mjs` blob: `b124b6886454d788f6a83d4cd2e4e692bacc7205`
- `cloudflare/proof/worker.node-test.mjs` blob: `6238c8c3df1520a16b95c23ff8459c61a06a5fe0`

### Implemented in the synthetic proof source

- Synthetic-only execution mode; no real exchange/provider market data.
- Worker health/status surfaces explicitly identify the synthetic-only data source.
- SQLite Durable Object class `SeriesCoordinatorDO` with migration tag `v1`.
- One-time, series-bound, purpose-bound tickets; atomic consume and expiry checks.
- Sequence watermark initialization and strictly next-sequence acceptance.
- Snapshot watermark alignment with the next live synthetic event.
- Hibernation-safe WebSocket attachments and restoration validation.
- Exact-series fan-out and per-socket send-failure isolation.
- Authentication deadline alarm; unauthenticated connection timeout.
- Maximum 64 sockets per series; maximum 8 unauthenticated sockets per series.
- JSON body cap 2,048 bytes; strict declared Content-Length validation; streaming cancellation after cap; fatal UTF-8 decoding.
- Wrangler disables Workers.dev and preview URLs; no production route is configured.

### Regression test inventory

`cloudflare/proof/worker.node-test.mjs` contains **31 test declarations**. The latest additions include oversized streamed-body cancellation, declared oversized Content-Length rejection, invalid UTF-8 rejection, and unauthenticated socket-capacity enforcement.

**Evidence limit:** test declarations are not proof that tests passed. The current connector query for the audited source SHA returned no combined status checks and no workflow-run records. Do not claim the current head is CI-green. The workflow-run connector is known to expose only pull-request-triggered runs, so its empty result does not establish that no push workflow exists. No CI rerun or new push is created by this documentation-only cycle.

### Production gaps remain open

- No evidence that this synthetic Worker is deployed.
- No verified public route, production WSS hostname, TLS termination or existing origin mapping.
- No integration with FastAPI, Firebase identity, live providers, signed production snapshots or the chart UI.
- No owner-accepted durable per-gateway receipt/high-water ACK ledger.
- No public browser/Android WebSocket end-to-end evidence.
- No Cloudflare resource creation or deployment is authorized by this cycle.

The synthetic proof is a useful isolated protocol experiment, not the production WebSocket solution. Do not close Project Gate 25 or Gate 36.

## 3. Indicator source and test audit

### Exact files and blob identities

| Artifact | Blob SHA | Audited result |
|---|---|---|
| `src/indicators/indicatorCalculations.ts` | `507284fb286c633144b497b9d98c8c810250a8db` | Six exported calculation entry points |
| `src/indicators/indicatorCalculations.test.ts` | `5da008e045829876c78b82e612f73d7bd590b1c1` | 21 test declarations |
| `src/indicators/useMarketIndicators.ts` | `40188569cfc1d823bef2d814404c7bd5bb577c0c` | Shared snapshot hook and WeakMap result cache |
| `src/indicators/useMarketIndicators.test.ts` | `3681bb9b66dd39da8606c7c58c56a3993ef8d80b` | 7 test declarations |
| `src/components/CandlestickChart.tsx` | `d2ec7c1e825a969b055e3e4d0109290f6f951348` | No import/call of `useMarketIndicators` |

Total focused indicator test declarations: **21 + 7 = 28**. This is a test inventory, not a pass count, a completed-indicator count or a percentage.

### Mathematical contracts

| Study | Contract | First valid source index |
|---|---|---:|
| SMA20 | Arithmetic mean of 20 closes | 19 |
| EMA20 | SMA-seeded EMA; alpha (2/21) | 19 |
| RSI14 Wilder | Seed from 14 close-to-close changes, then Wilder recurrence | 14 |
| MACD12/26/9 | EMA12 − EMA26; EMA9 signal seeded from first valid MACD | MACD 25; signal/histogram 33 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 |

Additional numerical safeguards present in the calculation source include positive safe-integer period validation, finite-input/output checks, scaled/stable mean handling, compensated summation for cancellation-sensitive inputs, RSI normalization, and finite-range failure rather than emitting Infinity/NaN.

The 21 calculation-test declarations explicitly cover warm-up alignment, Wilder RSI edge cases, MACD signal warm-up, population standard deviation, multi-timeframe behavior, invalid inputs, prefix causality, extreme finite values, cancellation residuals, RSI recurrence, histogram identity and Bollinger translation/symmetry. The 7 hook-test declarations cover missing selection, exact keyed snapshot selection, live revision recalculation, multi-series isolation, shared frozen results, degraded/demo/error state behavior and unavailable-series clearing.

### Integration finding

`useMarketIndicators` is not imported or called by `CandlestickChart.tsx`. Therefore the five standard studies and shared hook remain foundation-level work, not visible, interactive chart indicators. No chart UI integration is started here because Stage 4 is gated and requires its scoped blueprint/review.

## 4. Full indicator status ledger

| # | Indicator / subsystem | Calculation/data foundation | Rendering, interaction and acceptance | Status |
|---:|---|---|---|---|
| 1 | SMA20 | 20-close arithmetic mean; valid at index 19 | Chart overlay, toggle, legend and lifecycle not integrated | 🟨 FOUNDATION |
| 2 | EMA20 | SMA-seeded; alpha 2/21; valid at index 19 | Chart overlay, toggle, legend and lifecycle not integrated | 🟨 FOUNDATION |
| 3 | RSI14 Wilder | 14-change seed + Wilder recurrence; valid at index 14 | Dedicated 0–100 pane, 30/70 guides and lifecycle not integrated | 🟨 FOUNDATION |
| 4 | MACD12/26/9 | MACD valid at 25; signal/histogram at 33 | Dedicated pane, lines, histogram and zero guide not integrated | 🟨 FOUNDATION |
| 5 | Bollinger20,2 | 20-close mean ± 2 population SD; valid at index 19 | Upper/middle/lower overlays, fill, legend and lifecycle not integrated | 🟨 FOUNDATION |
| 6 | Shared Indicator Hook | Keyed immutable snapshot, trust/state gate, WeakMap shared result cache | Not wired into chart component | 🟨 FOUNDATION |
| 7 | Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Visual implementation remains gated; two supplied Footprint references are authoritative | 🟧 GATED |
| 8 | Volume Profile | Complete binning/value-area contract not accepted | No accepted chart rendering or interaction | 🟥 OPEN |
| 9 | Complete Volume Profile | Session completeness, POC/VAH/VAL methodology not accepted | No accepted complete-session rendering | 🟥 OPEN |
| 10 | Movable-range Volume Profile | User range bounds and deterministic recomputation not accepted | Range interaction/lifecycle not integrated | 🟥 OPEN |
| 11 | Heatmap | Lawful depth provenance, aggregation and decay contract not accepted | Visual work waits for user's reference image | 🟥 OPEN |
| 12 | Liquidation Maps | Data provenance, estimation method and confidence limits not accepted | No accepted rendering or interaction | 🟥 OPEN |

### Cross-indicator acceptance gates

1. Warm-up output is null until the exact mathematical first-valid index.
2. Prefix causality: adding future candles cannot alter any prior output.
3. No lookahead, future-candle repaint or timestamp shifting.
4. Exact canonical series identity and timestamp alignment.
5. Identity changes clear stale calculations immediately.
6. No indicator output for demo, loading, unavailable, error or empty backend snapshots.
7. Repeated identical input yields deterministic output.
8. Calculation must not mutate source candles.
9. Computation and memory remain bounded for supported history sizes.
10. Footprint OFF preserves normal candlestick spacing; only explicit Footprint ON switches to spaced candle clusters.
11. Footprint visual implementation must match the two saved user references.
12. Heatmap visual implementation must wait for its user-supplied reference.

## 5. WebSocket execution order — no stage skipping

The current production runtime blueprint remains the governing plan. Work order is unchanged:

1. Review the source/gateway runtime blueprint and confirm the production-host mapping.
2. Batch 80: strict source/gateway role configuration and fail-closed validation.
3. Batch 81: source publisher factory and checkpoint/lease integration.
4. Batch 82: gateway replica factory and authenticated snapshot startup.
5. Batch 83: real Redis two-gateway, restart, duplicate, outage and lease-fencing tests.
6. Batch 84: durable owner-accepted gateway receipt/high-water ACK ledger and restart reconciliation.
7. Batch 85: existing Cloudflare route/origin mapping, public WSS/TLS and browser/Android E2E.
8. Batch 86: backup/restore, observability and incident acceptance.
9. Re-run Stage 1 acceptance and close only criteria supported by exact evidence.

Do not infer a durable owner ACK from local applied cursor or Redis XACK. Keep destructive Redis trimming/deletion blocked until every required gateway has a durable accepted high-water receipt and retention-floor proof. Do not create duplicate Cloudflare infrastructure.

## 6. Project progress dashboard

| Workstream | Evidence meter | Status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 IN PROGRESS |
| Gate 10 — remaining Stage 1 acceptance | 0/10 formally closed | 🟥 OPEN |
| Stage 2 — Market Data Infrastructure | Not officially entered/scored | 🟦 PREPARATORY |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⚪ NOT SCORED |
| Stage 4 — Indicators & Analytics | Gated pending blueprint/review | 🟪 GATED |
| Stage 5 — Professional UI & Tools | Not scored | ⚪ NOT SCORED |
| Stage 6 — Hardening, Validation & APK | Not scored | ⚪ NOT SCORED |
| Project Gate 25 — signed transfer/receipt/high-water ACK | Not accepted | 🟥 OPEN |
| Gate 36 — public WSS/TLS/device E2E | Not accepted | 🟥 OPEN |
| Production Worker deployment | No deployment evidence | 🟥 OPEN |
| Indicator source foundations | 28 test declarations; UI integration absent | 🟨 FOUNDATION |
| Advanced indicators | Four open, Footprint gated | 🟥 / 🟧 |

**Overall project progress:** ⚪ NOT SCORED. An approved weighted denominator is not available.  
**Significant project progress / IP3S:** ⚪ NOT SCORED. No reproducible formula and evidence denominator are approved.  
**Aggregate indicator completion:** ⚪ NOT SCORED. Test declaration count cannot be converted into completion percentage.

Gate 10 criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Stage 1 criterion #25 (owner-host Redis TLS/ACL/persistence) is distinct from Project Gate 25 (signed snapshot transfer/receipt/high-water ACK).

## 7. CI evidence and handling

For source/test SHA `471eb4413a716922b20a5503fe5165607e77947f`, the current connector query returned:
- Combined status checks: empty.
- Pull-request-filtered workflow-run result: empty.

This is **UNKNOWN / NOT VERIFIED**, not SUCCESS and not FAIL. The workflow file triggers on push to this branch, but the available workflow-run wrapper only returns pull-request-triggered runs. Do not leave a known running workflow unattended; however, do not claim background monitoring or fabricate a terminal result where the connector cannot expose it.

This cycle adds documentation only and uses `[skip ci]` in its commit message. It intentionally does not create a new CI run or cancel any possibly active run. Runtime/test code changes must receive a fresh, exact-HEAD CI verification through an observable run source before acceptance.

## 8. Zero-cost and release controls

- No paid hosting, Workers Paid, Cloudflare Containers, paid data feed, paid monitoring, paid backup, Vercel deployment or publication fee.
- Cloudflare Free quotas must be treated as hard capacity limits, not assumed unlimited production capacity.
- No production resource creation/deployment in this cycle.
- No provider feed is enabled without lawful zero-cost access and redistribution rights.
- No destructive Redis retention operations.
- Preserve `main`; all work stays on `phase-2/market-data-foundation`.
- Target remains around **24 December 2026**, not the end of December.

## 9. Work Cycle 87 outcome

- Latest branch source/test checkpoint reconciled.
- Worker proof limits and 31 test declarations documented without misrepresenting them as passing tests.
- Indicator calculations, exact test declaration inventory and chart integration gap reconciled.
- Full 12-row indicator ledger and mathematical acceptance gates documented.
- Project/stage/Gate/overall/IP3S dashboards reconciled without invented percentages.
- No production deployment, paid service, source-code change or CI success claim made.
