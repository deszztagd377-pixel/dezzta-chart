# WORK CYCLE 62J-158 — Canonical series identity unification and CI acceptance

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Code HEAD: `8deaccab7eece191e57dc18eba03f235a020d016`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Objective

Remove duplicated canonical-series comparison logic between the frontend market-data store and the authenticated WebSocket supervisor. Make identity equality collision-safe and prove that all ten identity dimensions participate in the same comparison contract.

This is a data-integrity prerequisite for the future multi-chart keyed-store/owner-lease migration. It does not enable multiple concurrent chart panels or upstream provider demand management.

## Files changed

1. `src/services/marketDataStore.ts`
   - Added `getMarketSeriesIdentityKey(identity)`.
   - Key is a JSON-serialized ordered tuple, not delimiter concatenation. Delimiter characters inside dataset/symbol values therefore cannot merge distinct identities.
   - Defaults are normalized: provider `databento`, series type `contract`, timeframe-derived bucket policy, and empty calendar ID/version.
   - Added `isSameMarketSeriesIdentity(left, right)` as the shared comparison function.
   - Store update routing now uses the shared comparator.

2. `src/services/marketDataStore.test.ts`
   - Added normalized-default equivalence coverage.
   - Added distinct-key/equality coverage for all ten identity dimensions:
     provider, series type, dataset, publisher ID, instrument ID, raw symbol, timeframe, bucket policy, calendar ID, calendar version.
   - Added delimiter-collision regression coverage.
   - Corrected the explicit default policy fixture for `1m`: the canonical policy is `UTC_FIXED_V1`, not `UTC_LEGACY`.

3. `src/services/ohlcvStreamSupervisor.ts`
   - Removed its duplicate local identity comparator.
   - Uses `isSameMarketSeriesIdentity` from the shared store contract.

No API endpoint, provider SDK, production data source, credential, paid service, or deployment was added. No indicator formula or renderer changed.

## Commit sequence

- `70f39b03a581c92ae7325a7725d0f49668800210` — centralize canonical series identity key/comparator and update store/supervisor.
- `d856e3b8f9818765d33e75e3479a7c7d9906d46b` — route the supervisor's remaining update-path comparison through the shared comparator.
- `8deaccab7eece191e57dc18eba03f235a020d016` — correct the `1m` default-policy test fixture and cover all ten identity dimensions.

Final code HEAD: `8deaccab7eece191e57dc18eba03f235a020d016`.

## Exact-HEAD CI acceptance

All five required workflows completed successfully on the exact code HEAD `8deaccab7eece191e57dc18eba03f235a020d016`:

| Workflow | Run ID | Result |
|---|---:|---|
| Automated Tests | `45023753817` | 🟩 SUCCESS |
| CodeQL Security Analysis | `45023752699` | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | `45023752559` | 🟩 SUCCESS |
| Full Git History Secret Audit | `45023752618` | 🟩 SUCCESS |
| Android APK Build (zero-cost CI) | `45023752627` | 🟩 SUCCESS |

Automated Tests completed frontend unit tests and build, backend tests, isolated Redis TLS CA/hostname checks, synthetic SQLite outbox benchmark, same-host SQLite metrics collector benchmark, backend dependency audit, backend container build/smoke test/image scan, and frontend dependency audit. No failing steps remained.

### Android debug artifact

- APK SHA-256: `89a9497aea1c80f05d6c531fd4b40e1d684c9d6dcb91ef38b8a78d4cd106fb26`
- Artifact name: `dezzta-chart-android-debug-apk`
- Artifact ID: `14755380616`
- Uploaded artifact digest: `92b7beeb53270c74c5be2d325c60167937448a9cf8075ac859687498a30c8f0e`
- [Open the exact CI run and APK artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45023752627/artifacts/14755380616)

This is an Android debug APK artifact from CI. It is not a public Play Store release, not a production-signed release, and not proof of installation or acceptance on a physical Android device. The immutable preview release step was skipped by workflow policy.

OCI ARM64 success means native ARM64 image build, smoke test, and image scan passed. It does not mean an OCI VM or public backend/WSS endpoint was provisioned.

## WebSocket and multi-chart status

### Verified foundations

- Authenticated short-lived WebSocket tickets and renewal.
- Exact canonical series subscription identity.
- Backend bounded per-client queues and exact-series fan-out.
- Cursor/replay/watermark boundary and sequence validation.
- Independent subscriber disconnect cleanup.
- Frontend snapshot/update validation and stale-series clearing.
- Frontend store and supervisor now share one collision-safe ten-dimension identity comparator.
- Existing supervisor tests cover replacement ownership, stale callback rejection, stop during pending authentication, reconnect, sequence gaps, and late message suppression.

### Still open

1. Frontend store remains a single module-global snapshot, not a keyed map of series snapshots.
2. Supervisor remains a single module-global owner; starting another chart selection supersedes the prior supervisor.
3. Independent simultaneous multi-chart panels are therefore not supported yet.
4. Backend provider ingestion remains process/configuration scoped, not chart-demand scoped.
5. Databento adapter uses fixed constructor-provided symbols; dynamic add/remove behavior is not verified against a pinned SDK version.
6. Provider reference counting/reconciliation is not implemented because it must be connected to a real provider lifecycle, not a disconnected local counter.
7. A recurring ZERO COST CME source with exact instrument coverage and application display/redistribution rights remains unverified/unavailable.
8. Public hostname, reverse proxy, WSS certificate, live Firebase, and real Android foreground/background/process-death/network-handover/public-network acceptance remain external gates.

Do not scrape public quote pages or reuse personal-use display data. A local demand coordinator cannot make a paid upstream source free.

## Complete indicator progress ledger

No indicator formula, calculation test, hook, or renderer changed in this work cycle. Indicator implementation credit for this cycle: zero.

| Indicator / subsystem | Status | Verified foundation | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; candle-index alignment; numeric and prefix-causality tests | Calendar-aware gap contract, chart overlay, toggle, legend/latest value, stale clearing, lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha 2/21; first valid index 19; warm-up, numeric and causality tests | Calendar-aware gap/reset semantics, overlay, toggle, legend/latest value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; flat/rising/falling/alternating and numerical stability tests | Gap/reset semantics, 0–100 pane, 30/70 guides, toggle, legend/latest value, renderer tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; causality tests | Gap semantics, dedicated pane, MACD/signal lines, histogram, zero guide, controls and renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19; numeric stability and causality tests | Gap semantics, upper/middle/lower overlay, toggle, latest values and renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Backend-only snapshot gating and aligned calculations | Keyed per-series snapshot input, calendar-aware gap contract, hook tests, chart binding, stale clearing and renderer integration |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator only | User-provided visual reference image(s), reviewed scoped blueprint, validated bid/ask data provenance/rights, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User-provided visual reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and lifecycle tests |
| Liquidation Maps | 🟥 Not implemented | No accepted provenance-backed calculation/renderer | Defensible data provenance, validated calculation contract, reviewed blueprint, visualization and tests |

### Indicator invariants

- Warm-up outputs remain null; never substitute zero.
- Outputs remain aligned to original candle indices.
- Prefix causality: future candles must not alter earlier outputs.
- Non-finite, invalid, or missing observations must not silently become zero or valid input.
- Expected overnight/weekend/holiday/scheduled session breaks must be distinguished from missing in-session candles.
- No arbitrary fixed-seconds gap threshold for session-aware futures calendars.
- No synthetic zero-price bars.
- Indicator outputs must clear/recompute on contract, venue, dataset, timeframe, bucket policy, or calendar identity changes.
- Footprint OFF preserves normal candlestick spacing. Only explicit Footprint ON may use a dedicated spaced-candle/cluster layout.
- Footprint and Heatmap visuals remain gated on the user's reference image(s) and a reviewed scoped blueprint.
- Documentation, CI, benchmarks, and market-data plumbing do not count as indicator formula or renderer completion.

## Project stage dashboard

| Stage | Progress | Status / evidence |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 Existing scored baseline; this cycle does not re-score it |
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Provider demand lifecycle and rights-cleared recurring-$0 source remain open |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Keyed multi-chart store/ownership and chart acceptance remain open |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Calculation foundations exist; gap semantics, hook integration and renderers incomplete |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ No approved denominator |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ CI debug APK exists; physical-device and public release acceptance incomplete |

**Overall project progress: NOT SCORED.** No approved project-wide weights and denominator exist. Do not invent a total percentage.

**Gate 10:** Work remains in the Gate 10 workstream. Formal external acceptance remains 0/10 criteria closed. CI success is necessary evidence, not proof of public deployment, real-device acceptance, redistribution rights, or production operations.

## Significant progress this cycle

- Store and supervisor now share one collision-safe canonical series identity contract.
- All ten identity dimensions have explicit regression coverage.
- Delimiter-based identity collisions are covered.
- The incorrect 1m bucket-policy fixture assumption was corrected.
- Full exact-HEAD CI passed, including backend tests, frontend build/unit tests, security scans, ARM64 image smoke test, and Android debug APK build.
- No paid provider, hosting, subscription, credential, or cloud VM was introduced.

## Next engineering sequence

1. Preserve the exact-HEAD green CI baseline.
2. Implement a keyed per-series market-data store with immutable snapshots and per-series listeners; keep legacy single-chart behavior until migration tests pass.
3. Add idempotent panel owner leases and generation guards; test two same-series panels, two different-series panels, one-panel release, final release, and stale late events.
4. Only then migrate the supervisor from singleton ownership to per-series transport ownership.
5. Verify provider SDK lifecycle capabilities and exact pin before any upstream demand coordinator.
6. Define calendar-aware candle-gap annotations and per-indicator gap/reset semantics before chart indicator integration.
7. Integrate SMA/EMA/Bollinger overlays and RSI/MACD panes after the keyed data/gap contracts pass.
8. Keep Footprint/Heatmap visual work behind the user's references and blueprint review.

Delivery target remains 24 December 2026. ZERO COST remains a hard constraint.
