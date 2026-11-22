# WORK CYCLE 62J-160 — Render-pure keyed snapshots and panel ownership leases

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Code HEAD before this report: `dfb607a294d2297c14ea6f86d7f51b1d01dd2759`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Objective

Continue the keyed per-series chart-state foundation without changing the active single-supervisor transport model prematurely. This cycle addresses two separate correctness concerns:

1. React external-store reads must be pure and must not mutate the LRU cache during render/consistency checks.
2. Chart-panel ownership needs generation-safe leases so stale React effect cleanup cannot release a newer owner for the same series.

These are frontend state/ownership primitives. They do not claim multiple live WebSocket supervisors, provider-side reference counting, or dynamic upstream subscription.

## Changes

### 1. Render-pure keyed snapshot reads

Files:
- `src/services/marketDataSeriesStore.ts`
- `src/services/useMarketDataSeriesSnapshot.ts`
- `src/services/marketDataSeriesStore.test.ts`

Added `peekSnapshot(identity)`:
- Validates canonical series identity.
- Returns the current immutable snapshot when registered.
- Returns one stable empty loading snapshot when the series has not yet been registered.
- Does not create an entry.
- Does not change Map insertion order or LRU recency.

The React hook now uses `peekSnapshot` as the `useSyncExternalStore` snapshot getter. Its subscribe callback creates/registers the keyed entry after commit; React then rechecks the snapshot after subscription. This keeps render reads free of cache mutation while preserving a stable immutable snapshot reference.

The existing `getSnapshot` method remains available for imperative callers that intentionally want to register/touch a series entry.

Regression test added:
- Repeated reads for an unknown identity return the same stable object and do not allocate cache entries.
- Reading an existing series does not make it more recent in the LRU order.
- A later insertion evicts the true least-recently-used inactive entry.

### 2. React multi-panel hook coverage

File:
- `src/services/useMarketDataSeriesSnapshot.test.ts`

Added simultaneous-panel test coverage:
- Two chart panels can subscribe to different canonical series.
- Publishing one series updates only its panel.
- Publishing the second series updates only the second panel.
- Removing one panel releases only that panel's listener.
- The remaining panel continues to receive updates.
- The test compares stable status and candle values rather than assuming a global revision counter resets to one.

The test file also explicitly configures the React act environment so updates are executed under the expected test contract.

### 3. Generation-safe per-series panel lease registry

Files:
- `src/services/marketDataSeriesLeaseRegistry.ts`
- `src/services/marketDataSeriesLeaseRegistry.test.ts`

Added `MarketDataSeriesLeaseRegistry` and a shared registry instance.

Contract:
- Leases are keyed by the canonical ten-dimension series identity.
- Each panel owner has a non-empty owner ID.
- Multiple unique panels can own the same series.
- The same owner ID reacquiring the same series receives a newer generation instead of increasing the unique-owner count.
- A stale lease release cannot remove a newer generation.
- Release is idempotent.
- Final-owner cleanup runs once when the final current-generation owner releases.
- Different canonical series remain isolated even when their panel owner IDs match.
- Cleanup callback exceptions cannot break React effect cleanup.
- Owner count and series count are exposed for deterministic tests/diagnostics.

**Important boundary:** the registry is not yet connected to `startOhlcvStreamSupervisor`. It is a tested ownership primitive only. No provider connection or upstream demand is started or stopped by this class.

### 4. Bounded per-series history and lower-allocation live updates

Files:
- `src/services/marketDataStore.ts`
- `src/services/marketDataSeriesStore.ts`
- `src/services/marketDataStore.test.ts`
- `src/services/marketDataSeriesStore.test.ts`

The backend enforces `MAX_OHLCV_RESPONSE_BARS = 5,000`, and the frontend snapshot client accepts no more than 5,000 bars. Both frontend stores now enforce the same hard ceiling:
- Default maximum: 5,000 bars per canonical series.
- Configurable store instances may use a lower positive limit, but cannot exceed 5,000.
- Oversized snapshots fail closed before mutating the existing store.
- New live bars retain the newest bounded window by evicting the oldest bar.
- A late update older than the retained window is rejected rather than silently reinserted and immediately discarded.
- Unchanged frozen bar objects are structurally shared across revisions; only the revised/new bar is cloned and frozen. This avoids cloning every candle object on each live update.

The series-count cache remains capped at 32 by default. Combined default bound: at most 32 cached series × 5,000 bars per series, with active subscriber pinning. This is a deterministic object-count bound, not a measured RAM guarantee.

Regression coverage verifies 5,000-bar retention in the legacy store, configurable smaller windows in the keyed store, rejection of oversized snapshots, rejection of too-old corrections, and object-reference reuse for unchanged bars.

### 5. Documentation correction

Updated `docs/WORK_CYCLE_2026-11-22_BATCH62J159_KEYED_SERIES_STORE.md` to reflect the existing chart binding accurately:
- `CandlestickChart` already reads keyed snapshots through `useMarketDataSeriesSnapshot`.
- The current supervisor remains globally singleton-owned.
- The supervisor still dual-publishes validated events to the legacy and keyed stores.
- Simultaneous multi-series transport ownership remains open.
- The hook and keyed chart binding are no longer incorrectly listed as unimplemented.

## Regression/test coverage

- Keyed series store: 17 focused tests, including pure reads and bounded-window behavior.
- Legacy shared store: 13 tests, including the 5,000-bar hard limit.
- React keyed snapshot hook: 3 tests, including two simultaneous panels.
- Panel lease registry: 7 tests, including normalized owner IDs.
- Existing supervisor test suite remains in place for its current single-owner behavior.

A prior Automated Tests run failed because the newly added React test assumed `revision` always started at one. The store correctly retains monotonically increasing revisions after reset. The test was corrected to assert canonical status and candle values instead. No production code change was made to falsify or reset revision history.

## Commit sequence

- `f2c0fdedc846ef198429407037daab5ecc04d4b4` — add pure keyed snapshot read.
- `001ec1e698d31adaee35cab35c0206e7c5e335a8` — use pure reads in React hook.
- `d4e0bb8415606cd11a6308e8cc14b1a7aab5fa33` — test pure read/LRU behavior.
- `f12a5e023d5638409d7693dd592a2ec7cda88f73` — correct Batch 159 integration documentation.
- `2e39b01d957e24388df3c4ee7d6c15310069bc3f` — correct test assumptions and act environment.
- `11dfc45a490f79a926808b14f5917190dbad1a5d` — finalize status/value assertions in multi-panel test.
- `39f616915f6f3e4fdd35f9ca61bc35fcfb3373b3` — add generation-safe panel lease registry.
- `3cd0d9035a6ceb1b88db5dcf01126acb00e64c67` — add lease-registry regression tests.
- `5a82e2b969ba5e22342331f1efd6f38a3f6e608d` — normalize panel owner IDs.
- `c920babddd2cb81e1714ee6e0c8ff8163742d5e0` — normalize owner presence lookup.
- `050efdaf79560c4abd5b7dbd55013bc7f49868ad` — test owner-ID normalization.
- `f6ad76c09b1829a736f571b7dfc639cbb97a8856` — cap legacy history and reuse frozen bars.
- `0771a88bfff0cc40f19109a53916076a998f837b` — cap keyed history and reuse frozen bars.
- `b8a653b31a06b9ff08a987790f1f282decf2e811` — test keyed history retention and structural sharing.
- `dfb607a294d2297c14ea6f86d7f51b1d01dd2759` — test legacy 5,000-bar retention.

## WebSocket and multi-chart status

### Completed
- Authenticated short-lived WebSocket tickets and renewal.
- Exact canonical series subscription.
- Backend bounded per-client queues and exact-series fan-out.
- Cursor replay, watermark and sequence validation.
- Subscriber disconnect cleanup.
- Frontend ten-dimension canonical identity.
- Keyed immutable per-series store with bounded 32-series LRU.
- Each series retains at most 5,000 bars by default, matching the backend hard response ceiling.
- Live revisions structurally share unchanged frozen bars instead of recloning the full history.
- Active chart listeners pin their cache entry.
- React hook reads the selected canonical series.
- React panel isolation test coverage.
- Generation-safe per-series panel lease primitive.

### Still open
1. Wire the lease registry into chart lifecycle with stable panel owner IDs.
2. Ensure a stale effect cleanup cannot stop a replacement panel's transport lease.
3. Replace the global singleton supervisor with per-series shared transport ownership.
4. Define whether same-series panels share one socket or use separate client subscriptions; verify server capacity and lifecycle.
5. Ensure a panel release does not stop another same-series panel.
6. Ensure a different-series panel does not overwrite the first panel's keyed state.
7. Reconcile reconnects, ticket renewal, sequence gaps and cleanup independently per series.
8. Resolve the legacy global-store compatibility path before enabling concurrent streams.
9. Verify dynamic upstream provider subscription and exact SDK add/remove behavior.
10. Establish a recurring ZERO COST source with exact CME coverage and app display/redistribution rights.
11. Verify the 5,000-bar retention bound against real-device memory and rendering profiles before increasing either cache dimension.
12. Complete public hostname, reverse proxy, WSS certificate, live Firebase and real Android lifecycle/network acceptance.

No paid provider, key, account, deployment, VM, or cloud resource was introduced.

## Indicator progress ledger

No indicator formula or renderer changed in this cycle. Indicator formula/renderer implementation credit: zero. The keyed store and React hook provide a better per-series input boundary, but they do not complete indicator UI.

| Indicator / subsystem | Status | Verified foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; candle-index alignment; numeric and prefix-causality tests | Calendar/session-aware gap contract, overlay, toggle, legend/latest value, stale clearing, lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19; warm-up, numeric and causality tests | Gap/reset semantics, overlay, toggle, legend/latest value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; flat/rising/falling/alternating and numerical-stability tests | Gap/reset semantics, 0–100 pane, 30/70 guides, toggle, legend/latest value, renderer tests |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; causality tests | Gap semantics, dedicated pane, MACD/signal lines, histogram, zero guide, controls and renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; numeric stability and causality tests | Gap semantics, upper/middle/lower overlay, toggle, latest values and renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot gating and aligned calculations; keyed React chart snapshot hook and pure reads | Calendar-aware gap semantics, stale clearing, indicator-to-chart renderer integration and per-indicator hook tests |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator only | User-provided visual reference image(s), reviewed blueprint, validated bid/ask provenance/rights, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User-provided visual reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and lifecycle tests |
| Liquidation Maps | 🟥 Not implemented | No accepted provenance-backed calculation/renderer | Defensible data provenance, validated calculation contract, reviewed blueprint, visualization and tests |

### Indicator invariants

- Warm-up outputs remain null; never substitute zero.
- Outputs remain aligned to original candle indices.
- Prefix causality: future candles must not alter earlier outputs.
- Invalid, non-finite, or missing observations must not silently become zero or valid input.
- Expected overnight/weekend/holiday/session breaks must be distinguished from missing in-session candles.
- No arbitrary fixed-seconds gap threshold for session-aware futures calendars.
- No synthetic zero-price bars.
- Outputs must clear/recompute on contract, venue, dataset, timeframe, bucket policy, or calendar identity changes.
- Footprint OFF preserves normal candlestick spacing; explicit Footprint ON may use a dedicated spaced-candle/cluster layout.
- Footprint and Heatmap visual work remains gated on the user's reference image(s) and a reviewed scoped blueprint.
- Documentation, CI, benchmarks, and market-data plumbing do not count as indicator formula/renderer completion.

## Project stage dashboard

| Stage | Progress | Status / evidence |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 Existing scored baseline; not re-scored in this cycle |
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Keyed series state and panel lease primitives exist; transport demand lifecycle, provider verification and recurring-$0 rights-cleared source remain open |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Keyed React chart binding exists; simultaneous multi-series transport and panel lifecycle acceptance remain open |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Calculation foundations exist; gap semantics, full indicator hook/renderer integration incomplete |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ No approved denominator |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ Exact-HEAD CI, debug APK device acceptance and public release acceptance remain separate gates |

**Overall project progress: NOT SCORED.** No approved project-wide weights/denominator exist. Do not invent an aggregate percentage.

**Gate 10:** Work remains in the Gate 10 workstream. Formal external acceptance remains 0/10 criteria closed. CI success is necessary evidence, not proof of public deployment, real-device acceptance, data redistribution rights, or production operations.

## CI evidence

The previous exact HEAD `f6e648f571f33de3b522169d537e0e7538584a68` had Automated Tests, CodeQL, OCI ARM64 and Secret Audit all successful.

The code HEAD `dfb607a294d2297c14ea6f86d7f51b1d01dd2759` has new verification runs pending/in progress at report creation. Do not infer success from earlier commits. Recheck all required workflows on the latest exact HEAD before marking this cycle verified.

Delivery target remains 24 December 2026. ZERO COST remains a hard constraint.
