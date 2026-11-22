# WORK CYCLE 62J-161 — Chart migration to keyed snapshots and WebSocket bridge

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Code HEAD: `e07cbaeda84b554c1faff0a0b8bd1a97a7f31548`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Objective

Connect the keyed per-series store to the actual chart data path without removing the legacy singleton publication path yet. The authenticated WebSocket supervisor now mirrors validated snapshot/update/reset events into the keyed store, and `CandlestickChart` reads its selected series through `useMarketDataSeriesSnapshot`.

This is a staged migration. The supervisor remains singleton-owned, so independent simultaneous chart transports are NOT yet supported.

## Files changed

### 1. `src/services/ohlcvStreamSupervisor.ts`

- Added store bridge helpers for snapshot, update and reset operations.
- Every validated snapshot is published to the legacy store and the keyed series store.
- Every validated incremental update is published to both stores.
- Loading, unavailable, terminal-authentication, protocol-policy and stop states are mirrored to the keyed store.
- The legacy store remains populated during the migration so existing consumers and regression tests are preserved.

### 2. `src/services/ohlcvStreamSupervisor.test.ts`

- Added assertions that an authenticated snapshot appears in the keyed series store.
- Verifies supervisor stop clears the keyed snapshot to unavailable.
- Verifies a replacement timeframe receives its own keyed loading/snapshot state.
- Verifies delayed callbacks from the superseded socket do not overwrite the replacement series.

### 3. `src/components/CandlestickChart.tsx`

- Derives a memoized canonical identity from the selected contract and timeframe.
- Reads the selected series through `useMarketDataSeriesSnapshot`.
- Uses the shared canonical identity comparator instead of a hand-written subset of identity fields.
- Keeps existing full-snapshot replacement versus incremental newest-candle update behavior.
- Mirrors chart loading/unavailable resets into both legacy and keyed stores.
- Reads the keyed snapshot for subscribed-state details.
- Demo candles remain separate from backend indicator input.

No indicator formula or renderer was changed.

## Commit sequence

- `85641d49ce3510e29814666e8912312268d5cf8d` — mirror validated stream state into keyed store.
- `58aea25530803f121eb522143b7713326d5729e9` — mirror terminal authentication rejection.
- `627617b8a62756f109aa4e63638c66563211268e` — test supervisor-to-keyed-store bridge.
- `e07cbaeda84b554c1faff0a0b8bd1a97a7f31548` — migrate CandlestickChart snapshot consumption to keyed store.

Final code HEAD: `e07cbaeda84b554c1faff0a0b8bd1a97a7f31548`.

## Exact code-HEAD CI acceptance

All five required workflows completed successfully for code HEAD `e07cbaeda84b554c1faff0a0b8bd1a97a7f31548`:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | `45027498126` | 🟩 SUCCESS |
| CodeQL Security Analysis | `45027498081` | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | `45027498010` | 🟩 SUCCESS |
| Full Git History Secret Audit | `45027498066` | 🟩 SUCCESS |
| Android APK Build (zero-cost CI) | `45027498143` | 🟩 SUCCESS |

Automated Tests passed frontend unit tests/build, backend tests, Redis TLS CA/hostname enforcement, SQLite outbox and metrics benchmarks, backend dependency audit, backend container build/smoke test and image scan. No failing steps remained.

### Android debug artifact

- Run: [Android APK CI run](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45027498143)
- Artifact: [dezzta-chart-android-debug-apk](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45027498143/artifacts/14756123215)
- Artifact ID: `14756123215`
- Uploaded archive SHA-256 digest: `a1eae19ecf22d31190826f5e8f72f2bd176137b9cc22cbbff85a76ac92e5daef`

This is a debug APK from CI, not a production-signed release or proof of physical-device installation/acceptance. The immutable preview release step was skipped by workflow policy.

OCI ARM64 success means the native ARM64 image build, smoke test, and image scan passed. It does not mean an OCI VM or public backend/WSS endpoint was provisioned.

## WebSocket and multi-chart status

### Completed
- Authenticated short-lived WebSocket tickets and renewal.
- Exact canonical series subscription identity.
- Backend bounded per-client queues and exact-series fan-out.
- Cursor/replay/watermark and sequence validation.
- Subscriber disconnect cleanup.
- Shared ten-dimension canonical identity comparator.
- Bounded keyed per-series snapshot store with immutable bars and active-subscriber cache pinning.
- React keyed subscription hook.
- Chart now consumes its selected keyed series.
- Supervisor mirrors validated stream events into the keyed store.
- Regression coverage for store isolation, hook selection changes and supervisor bridge behavior.

### Still open — do not mark multi-chart complete
1. `activeSupervisorStop` remains a single global supervisor owner. A second chart selection still supersedes the first transport.
2. Per-panel owner leases and generation guards are not implemented.
3. The frontend store still publishes to the legacy singleton in parallel; legacy removal must wait for all consumers to migrate.
4. Per-series reconnect and transport lifecycle reconciliation are not implemented.
5. Per-series bar-window/history retention remains open. The 32-entry cache bounds series count, not bars per series.
6. Provider demand/ref-counting remains unimplemented; it must be wired to a verified provider lifecycle, not a disconnected counter.
7. Databento dynamic add/remove-symbol behavior still requires exact SDK version and lifecycle verification.
8. A recurring ZERO COST CME source with exact instrument coverage and app display/redistribution rights remains unverified/unavailable.
9. Public hostname, reverse proxy, WSS certificate, live Firebase and physical-device foreground/background/process-death/network-handover acceptance remain external gates.

## Complete indicator progress ledger

No indicator formula or renderer changed in this cycle. Indicator implementation credit: zero. The chart now consumes keyed snapshots, which improves the data-isolation foundation for indicators but does not complete indicator integration.

| Indicator / subsystem | Status | Verified foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; candle-index alignment; numeric and prefix-causality tests | Calendar/session-aware gap contract, overlay, toggle, legend/latest value, stale clearing, lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19; warm-up, numeric and causality tests | Gap/reset semantics, overlay, toggle, legend/latest value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; flat/rising/falling/alternating and numerical-stability tests | Gap/reset semantics, 0–100 pane, 30/70 guides, toggle, legend/latest value, renderer tests |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; causality tests | Gap semantics, dedicated pane, MACD/signal lines, histogram, zero guide, controls and renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; numeric stability and causality tests | Gap semantics, upper/middle/lower overlay, toggle, latest values and renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Legacy backend snapshot hook; keyed series hook now connected to CandlestickChart; store/hook/supervisor bridge tests pass | Calendar-aware gap semantics, per-indicator gap/reset behavior, stale clearing and actual indicator renderer integration |
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
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Keyed store and WebSocket bridge foundations exist; provider demand lifecycle and recurring-$0 rights-cleared source remain open |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Chart now reads keyed snapshots; per-panel leases and multi-supervisor transport remain open |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Calculation foundations exist; gap semantics, indicator renderers and full integration incomplete |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ No approved denominator |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ CI debug APK built; physical-device and public release acceptance incomplete |

**Overall project progress: NOT SCORED.** No approved project-wide weights/denominator exist. Do not invent an aggregate percentage.

**Gate 10:** Work remains in the Gate 10 workstream. Formal external acceptance remains 0/10 criteria closed. CI success is necessary evidence, not proof of public deployment, real-device acceptance, redistribution rights, or production operations.

## Next engineering sequence

1. Add per-panel owner leases keyed by canonical series, with idempotent release and generation guards.
2. Replace the singleton supervisor owner with a per-series supervisor registry only after owner-lease tests pass.
3. Verify two panels on the same series, two panels on different series, one-panel disconnect, final-owner release, and stale callback suppression.
4. Migrate remaining consumers from legacy global store; remove legacy bridge only after complete test coverage.
5. Add per-series bar-window retention and memory telemetry.
6. Define provider capability/demand lifecycle only after exact SDK behavior and ZERO COST data rights are verified.
7. Define calendar-aware gap annotations and per-indicator gap/reset semantics.
8. Integrate SMA/EMA/Bollinger overlays and RSI/MACD panes after keyed multi-chart ownership is stable.
9. Keep Footprint/Heatmap visual work behind the user's references and blueprint review.

Delivery target remains 24 December 2026. ZERO COST remains a hard constraint.
