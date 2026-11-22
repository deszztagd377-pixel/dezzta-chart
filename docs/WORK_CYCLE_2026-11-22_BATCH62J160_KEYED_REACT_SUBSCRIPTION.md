# WORK CYCLE 62J-160 — Keyed React market-data subscription

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Code HEAD: `c4f0ce0d21fdab3f39af587e9ac65e7b3540363c`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Objective

Expose the new keyed per-series market-data store to React through a stable `useSyncExternalStore` hook. The hook must subscribe to one canonical series key, preserve stable callbacks when callers recreate an equivalent identity object, and detach from the previous series when the selected identity changes.

This is a React binding foundation only. The existing `CandlestickChart` and authenticated WebSocket supervisor still use the legacy singleton store. The hook is not yet the live chart data path.

## Files changed

1. `src/services/useMarketDataSeriesSnapshot.ts`
   - Added `useMarketDataSeriesSnapshot(identity | null)`.
   - Uses `useSyncExternalStore` for concurrent-safe external-store subscriptions.
   - Uses the canonical identity key as the callback dependency boundary.
   - Equivalent newly-created identity objects do not cause unnecessary subscription replacement.
   - A changed canonical key rebinds the listener to the new series.
   - Null selection returns a stable immutable empty snapshot.
   - Uses the keyed series store; no transport or provider behavior is introduced.

2. `src/services/useMarketDataSeriesSnapshot.test.ts`
   - Added React/jsdom tests for stable null selection.
   - Verifies selected-series subscription counts.
   - Verifies updates to another series do not rerender the selected panel.
   - Verifies an equivalent identity object retains one subscription.
   - Verifies changing series releases the old listener and subscribes to the new key.

No existing chart rendering, WebSocket, provider SDK, indicator formula, or market-data source was changed.

## Commit sequence

- `b6bc4b38270ad1187f1f2beb314b8704bb397c61` — add keyed React snapshot hook.
- `3511c326620761ad9d1b799506f926f778bfb849` — add hook subscription tests.
- `d7016fe46094b3c4bfd03b74922fa3db6262758e` — make hook test assertions type-safe.
- `c4f0ce0d21fdab3f39af587e9ac65e7b3540363c` — use configured TypeScript-compatible array indexing in tests.

Final code HEAD: `c4f0ce0d21fdab3f39af587e9ac65e7b3540363c`.

## Exact code-HEAD CI acceptance

All five required workflows completed successfully for code HEAD `c4f0ce0d21fdab3f39af587e9ac65e7b3540363c`:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | `45026460686` | 🟩 SUCCESS |
| CodeQL Security Analysis | `45026460673` | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | `45026460698` | 🟩 SUCCESS |
| Full Git History Secret Audit | `45026460670` | 🟩 SUCCESS |
| Android APK Build (zero-cost CI) | `45026460695` | 🟩 SUCCESS |

Automated Tests completed frontend unit tests (including the new hook tests), frontend build, backend tests, isolated Redis TLS CA/hostname checks, synthetic SQLite outbox and metrics benchmarks, dependency audits, backend container build/smoke test and image scan. No failed steps remained.

### Android debug artifact

- Run: [Android APK CI run](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45026460695)
- Artifact: [dezzta-chart-android-debug-apk](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45026460695/artifacts/14754824776)
- Artifact ID: `14754824776`
- Uploaded archive SHA-256 digest: `10e2d4d11e06ecaceb5249327dca43321164db521b8d90bd29d9f8f5ea1e0271`

This is an Android debug APK artifact from CI. It is not a production-signed release, public Play Store release, or proof of physical-device installation/acceptance. The immutable preview release step was skipped by workflow policy.

OCI ARM64 success means the native ARM64 image build, smoke test, and image scan passed. It does not mean an OCI VM or public backend/WSS endpoint was provisioned.

## Keyed store + React hook status

### Implemented and tested
- Per-series immutable snapshots keyed by canonical 10-dimension identity.
- Independent listener sets for independent series.
- Shared snapshot for multiple panels selecting the same series.
- Per-series incremental update routing and chronological late-bar insertion.
- Idempotent listener cleanup.
- Active-subscriber cache pinning and bounded LRU cache (default 32 series).
- Fail-closed capacity behavior when all entries are actively subscribed.
- Rejected writes validated before cache mutation.
- Stable React subscription callbacks keyed by canonical identity.
- Null selection returns a stable empty snapshot.
- Hook selection changes detach from old series and attach to the new series.

### Still not wired into the live chart
1. `CandlestickChart` still consumes legacy `useMarketDataSnapshot`.
2. `ohlcvStreamSupervisor` still owns a single global stream and publishes to the legacy singleton store.
3. The new keyed store and hook do not yet create or manage WebSocket connections.
4. No upstream provider reference counting or dynamic provider subscription was added.
5. Per-series bar-window/history retention is still open. The 32-entry limit bounds series count, not bars within each series.
6. Multi-chart panels are not yet accepted as complete until chart and supervisor migration tests pass.

## Complete indicator progress ledger

No indicator formula or renderer changed in this cycle. Indicator implementation credit: zero. The keyed store and hook are data plumbing prerequisites, not indicator completion.

| Indicator / subsystem | Status | Verified foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; candle-index alignment; numeric and prefix-causality tests | Calendar/session-aware gap contract, overlay, toggle, legend/latest value, stale clearing, lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19; warm-up, numeric and causality tests | Gap/reset semantics, overlay, toggle, legend/latest value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; flat/rising/falling/alternating and numerical-stability tests | Gap/reset semantics, 0–100 pane, 30/70 guides, toggle, legend/latest value, renderer tests |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33; causality tests | Gap semantics, dedicated pane, MACD/signal lines, histogram, zero guide, controls and renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19; numeric stability and causality tests | Gap semantics, upper/middle/lower overlay, toggle, latest values and renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Legacy backend snapshot hook plus new keyed-series React hook; keyed hook tests pass but live chart not migrated | Chart binding to keyed snapshots, calendar-aware gap semantics, stale clearing, shared hook integration and renderer tests |
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
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Keyed store and hook foundations exist; provider demand lifecycle and rights-cleared recurring-$0 source remain open |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Live chart still on legacy store; multi-chart ownership and chart migration remain open |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Calculation foundations exist; gap semantics, live hook integration and renderers incomplete |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ No approved denominator |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ CI debug APK built; physical-device and public release acceptance incomplete |

**Overall project progress: NOT SCORED.** No approved project-wide weights/denominator exist. Do not invent an aggregate percentage.

**Gate 10:** Work remains in the Gate 10 workstream. Formal external acceptance remains 0/10 criteria closed. CI success is necessary evidence, not proof of public deployment, real-device acceptance, redistribution rights, or production operations.

## Next engineering sequence

1. Preserve the exact-code-HEAD green CI baseline.
2. Migrate the chart's snapshot reader behind a tested keyed-store adapter while preserving the legacy fallback.
3. Add panel owner leases and generation guards; verify two panels on the same series and two panels on different series.
4. Bridge the supervisor into the keyed store without yet removing legacy publication; verify exact-series fan-out and stale callback rejection.
5. Migrate supervisor ownership per series only after chart-store integration tests pass.
6. Add per-series bar-window/history retention and cache telemetry.
7. Define calendar-aware gap annotations and per-indicator gap/reset semantics.
8. Integrate SMA/EMA/Bollinger overlays and RSI/MACD panes only after keyed data/gap contracts pass.
9. Keep Footprint/Heatmap visual work behind the user's references and blueprint review.

Delivery target remains 24 December 2026. ZERO COST remains a hard constraint.
