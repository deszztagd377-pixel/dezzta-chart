# WORK CYCLE 62J-159 — Keyed per-series market-data store

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Objective

Create a bounded, immutable keyed snapshot store that can safely hold independent market-data series for multiple chart panels. Keep the existing singleton store and current chart/supervisor behavior unchanged until a separately tested migration is ready.

This work establishes a reusable per-series state boundary. It does NOT yet wire chart panels or WebSocket supervisors to the new store and does NOT claim that simultaneous multi-chart transport is already working.

## Files changed

### 1. `src/services/marketDataStore.ts`

Exported the existing canonical identity and OHLCV validation functions so the keyed store reuses the same contract rather than copying validation logic:

- `validateMarketSeriesIdentity`
- `validateMarketDataBars`

The existing legacy store behavior remains unchanged.

### 2. `src/services/marketDataSeriesStore.ts`

Added `MarketDataSeriesStore` and the shared `marketDataSeriesStore` instance.

Capabilities:
- Keyed by the canonical collision-safe 10-dimension series identity.
- Separate immutable snapshot and listener set for each series.
- Two chart panels subscribing to the same identity observe the same keyed series.
- Different identities cannot overwrite each other's snapshot or listener notifications.
- Snapshot and incremental update validation reuses the existing shared validators.
- Incremental updates replace an existing timestamp or insert a late timestamp in chronological order.
- Listener exceptions are isolated so one unmounted/throwing panel cannot block another panel.
- Unsubscribe is idempotent.
- Releasing the final listener does not erase a still-valid cached snapshot.
- Bounded cache defaults to 32 series.
- LRU eviction may remove only entries with zero active subscribers.
- Active panel subscriptions pin their series against eviction.
- If all cache entries are pinned, a new series request fails explicitly rather than silently evicting active chart state.
- Rejected snapshots/updates are validated before cache mutation; invalid writes cannot evict a valid series.
- `hasSeries`, `getSeriesCount`, `getCapacity`, and `getSubscriberCount` expose deterministic cache diagnostics.

The store is transport-agnostic. It does not open sockets, authenticate users, request provider subscriptions, or claim upstream demand management.

### 3. `src/services/marketDataSeriesStore.test.ts`

Added 13 focused tests covering:
1. Different series snapshot/listener isolation.
2. Two panels sharing the same series snapshot.
3. Idempotent release of one panel while another remains subscribed.
4. Per-series update routing and chronological insertion of late bars.
5. Isolation across supported canonical identity dimensions.
6. Immutable snapshot, identity, and bar references.
7. Invalid updates leave snapshots and listeners unchanged.
8. LRU eviction of inactive series while active series remain pinned.
9. Capacity exhaustion when every entry has active subscribers.
10. Positive safe-integer cache capacity validation.
11. Listener exceptions do not block healthy listeners.
12. Final unsubscribe preserves a reusable cached snapshot.
13. Rejected writes cannot evict an existing valid series.

Calendar identity fields remain part of the canonical key, but non-empty calendar metadata is intentionally rejected by the current validator until a session-aware bucket policy is implemented. Tests assert this explicit boundary rather than pretending calendar-aware series are supported.

## Commit sequence

- `fe1a2ec2899f80f88997d51ec83f1f4756ee56e7` — export shared identity/bar validators.
- `77575a65c62a993847cc49cec396b1ae266c6da0` — add keyed per-series store.
- `0a36e1ecbad13b82dc15ca5765da8c3d583ad930` — add isolation and subscription tests.
- `bcdac2d52a2a3ce50f652b488510616169cd40ee` — add bounded LRU cache and active-subscriber pinning.
- `f88d5b538c3ca78b73f95c19237a3afbe557070a` — test bounded cache behavior.
- `9ebd11cff6bc3655119b328c82cb75496028cc57` — add non-mutating series presence inspection.
- `c8defab49ce88665d9e0b49c2b78266f6beba5f5` — refine LRU and identity tests.
- `984ebc30a49d7e379488d5d6251cebb572019c9b` — align calendar tests with the current supported contract.
- `8ba39e76e20d40c923e6282a8e5fd4fc8f4da983` — prevent rejected writes from evicting cached series.
- `964f9f9ecf8f2d69de7d5df83da3f32090cc7dc4` — regression test for non-mutating rejected writes.

Final code HEAD before this documentation commit: `964f9f9ecf8f2d69de7d5df83da3f32090cc7dc4`.

## Safety and correctness boundaries

- Existing `marketDataStore` remains the active source for the current single-chart path.
- Existing `ohlcvStreamSupervisor` remains singleton-owned.
- New keyed store is implemented and tested in isolation but is not yet wired into `CandlestickChart` or the WebSocket supervisor.
- No dynamic provider subscription, upstream reference counting, provider API, data vendor, API key, or paid service was added.
- No market-data source is represented as free unless its exact coverage and app redistribution rights are proven.
- Cache capacity is 32 keyed series by default. Active subscribers are never evicted; if every slot is active, new series acquisition fails closed.
- The LRU limit bounds number of cached series, not the number of bars per series. Per-series history/window limits remain a separate follow-up requirement before broad chart-panel expansion.
- The store does not yet implement an owner lease that controls transport lifecycle. Listener subscription and upstream provider demand are deliberately separate concepts.

## WebSocket and multi-chart status

### Completed foundations
- Authenticated short-lived WebSocket tickets and renewal.
- Exact canonical series subscription identity.
- Backend bounded per-client queues and exact-series fan-out.
- Cursor/replay/watermark and sequence validation.
- Subscriber disconnect cleanup.
- Frontend shared ten-dimension canonical identity comparator.
- New keyed immutable per-series snapshot store.
- Per-series listener isolation and bounded cache with active-subscriber pinning.

### Still open
1. Migrate chart snapshot selectors to keyed store without changing current single-chart behavior.
2. Add per-panel owner leases/generation guards and test two panels on same/different series.
3. Migrate supervisor ownership from singleton to per-series only after keyed-store integration tests pass.
4. Add per-series transport cleanup/reconnect reconciliation.
5. Verify provider SDK add/remove-symbol lifecycle using exact pinned SDK docs/version.
6. Implement provider demand only when wired to an actual verified provider lifecycle.
7. Resolve a recurring ZERO COST CME source with exact instrument coverage and application redistribution rights.
8. Complete public hostname, reverse proxy, WSS certificate, live Firebase and real-device lifecycle/network acceptance.
9. Add per-series bar-window retention before unrestricted multi-chart usage.

## Indicator progress ledger

No indicator formula or renderer changed in this cycle. Indicator implementation credit: zero. The keyed store is a prerequisite for reliable per-series indicator inputs, not indicator completion.

| Indicator / subsystem | Status | Verified foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; candle-index alignment; numeric and prefix-causality tests | Calendar/session-aware gap contract, overlay, toggle, legend/latest value, stale clearing, lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19; warm-up, numeric and causality tests | Gap/reset semantics, overlay, toggle, legend/latest value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; flat/rising/falling/alternating and numerical-stability tests | Gap/reset semantics, 0–100 pane, 30/70 guides, toggle, legend/latest value, renderer tests |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; causality tests | Gap semantics, dedicated pane, MACD/signal lines, histogram, zero guide, controls and renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; numeric stability and causality tests | Gap semantics, upper/middle/lower overlay, toggle, latest values and renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot gating and aligned calculations; new keyed store now available but not integrated | Hook tests, keyed-store binding, calendar-aware gap semantics, stale clearing, renderer integration |
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
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Keyed store foundation exists; provider demand lifecycle and rights-cleared recurring-$0 source remain open |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Keyed store not yet wired into chart panels; multi-chart ownership remains open |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Calculation foundations exist; gap semantics, hook integration and renderers incomplete |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ No approved denominator |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ Exact-HEAD CI and debug APK acceptance still pending; physical-device and public release acceptance incomplete |

**Overall project progress: NOT SCORED.** No approved project-wide weights/denominator exist. Do not invent an aggregate percentage.

**Gate 10:** Work remains in the Gate 10 workstream. Formal external acceptance remains 0/10 criteria closed. CI success is necessary evidence, not proof of public deployment, real-device acceptance, data redistribution rights, or production operations.

## Next engineering sequence

1. Preserve the exact-HEAD green CI baseline once all required workflows pass.
2. Add a keyed React snapshot hook with stable subscribe/getSnapshot functions.
3. Migrate one chart panel behind an explicit feature boundary; preserve legacy behavior as fallback until tests pass.
4. Add panel owner leases and generation guards; verify two same-series panels and two different-series panels.
5. Migrate WebSocket supervisor ownership per series after chart-store migration is green.
6. Define per-series retention/window limits and stale cleanup.
7. Define calendar-aware gap annotations and per-indicator gap/reset semantics.
8. Integrate SMA/EMA/Bollinger overlays and RSI/MACD panes only after the keyed data/gap contracts pass.
9. Keep Footprint/Heatmap visual work behind the user's references and blueprint review.

Delivery target remains 24 December 2026. ZERO COST remains a hard constraint.
