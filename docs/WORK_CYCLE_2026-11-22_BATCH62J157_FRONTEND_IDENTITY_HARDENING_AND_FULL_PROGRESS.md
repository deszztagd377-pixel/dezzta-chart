# WORK CYCLE 62J-157 — Frontend series identity hardening and CI acceptance

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Code HEAD: `64999a2c71428395de6ac2c9faf20d0210fc8004`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Work completed

### 1. Frontend canonical series identity validation

Files changed:
- `src/services/marketDataStore.ts`
- `src/services/marketDataStore.test.ts`

The shared market-data store previously validated required dataset/symbol/numeric IDs but allowed malformed provider/series-type/bucket-policy values and exchange calendar metadata that the frontend does not yet support.

Added one validation boundary, `validateSeriesIdentity`, used for both full snapshot publication and incremental update publication.

It now checks:
- dataset and raw symbol are non-empty strings;
- publisher and instrument IDs are positive safe integers;
- provider is a non-empty string (default remains Databento);
- series type is exactly `contract` or `continuous`;
- timeframe is supported even when an explicit bucket policy is supplied;
- bucket policy is supported by the frontend (`UTC_LEGACY` or `UTC_FIXED_V1`);
- exchange calendar metadata is rejected until a session-aware bucket policy is supported.

The check occurs before store mutation. Invalid update identity leaves the current snapshot object unchanged. This prevents the frontend from accepting a series identity that the current frontend bucket-policy model cannot represent.

The backend's authoritative validation was not weakened. No provider API, dependency, key, paid service, or production deployment changed.

### 2. Regression coverage

Added a focused store regression test covering:
- unsupported exchange calendar metadata;
- blank provider;
- unsupported series type;
- unsupported session bucket policy;
- unsupported timeframe despite an explicit otherwise-supported bucket policy;
- malformed incremental-update identity does not mutate the active snapshot.

Existing market-data store tests continue to cover immutability, chronology, OHLCV boundaries, exact-series update matching, bucket-policy mismatch and stale state clearing.

### 3. Commit sequence

- `330c2849eaaf69828db4314778cabdecb3f18f14` — initial identity validation and regression coverage.
- `64999a2c71428395de6ac2c9faf20d0210fc8004` — explicit timeframe validation even when a bucket policy is supplied.

Final code HEAD for this cycle: `64999a2c71428395de6ac2c9faf20d0210fc8004`.

## CI acceptance on exact code HEAD

All required workflows completed successfully on `64999a2c71428395de6ac2c9faf20d0210fc8004`:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | `45022496456` | 🟩 SUCCESS |
| CodeQL | `45022496458` | 🟩 SUCCESS |
| OCI ARM64 Image Readiness | `45022496440` | 🟩 SUCCESS |
| Full Git History Secret Audit | `45022496525` | 🟩 SUCCESS |
| Android APK Build (zero-cost CI) | `45022496459` | 🟩 SUCCESS |

Automated Tests included frontend unit tests/build, backend tests, isolated Redis TLS CA/hostname checks, synthetic outbox and metrics-collector benchmarks, backend dependency audit, container image build/smoke test and image scan. No failing steps were reported.

### Android artifact

The Android debug APK was assembled, identified as an APK, checksummed, and uploaded as a short-lived CI artifact.

- APK SHA-256: `9d764c50ca1cf5a391c5f318d8a13c97fa67aa768e5407721a9c5665fefee8ec`
- Artifact: `dezzta-chart-android-debug-apk`
- Artifact ID: `14753894695`
- [Open the exact CI run and download its APK artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45022496459/artifacts/14753894695)

This is a debug APK artifact from CI, not a public Play Store release, not a signed production release, and not proof that it has been installed or accepted on the user's phone. The immutable preview release step was skipped by workflow policy.

OCI ARM64 success is a native ARM64 image build and smoke-test result only. It is not an OCI VM, public backend hostname, TLS/WSS endpoint, or deployed service.

## WebSocket progress

Verified foundations:
- authenticated short-lived ticket and reconnect renewal;
- exact canonical series identity on subscription;
- bounded per-client queues;
- backend exact-series fan-out and ten-dimension mismatch rejection;
- replay/live boundary, cursor and watermark behavior;
- independent subscriber disconnect cleanup;
- frontend store rejects unsupported/malformed series identities before mutation.

Remaining blockers:
1. Frontend market-data store and supervisor are still singletons; independent simultaneous chart panels are not supported.
2. Backend provider ingestion remains process/configuration scoped, not chart-demand scoped.
3. Dynamic upstream subscribe/unsubscribe capability has not been verified against an exact pinned SDK version.
4. Shared upstream provider refcounting and reconnect reconciliation are not implemented.
5. A recurring ZERO COST CME source with exact coverage and app display/redistribution rights remains unverified/unavailable.
6. Public hostname, reverse proxy, WSS certificate, live Firebase, Android foreground/background/process-death/network-handover and public-network acceptance remain external gates.

Do not implement a disconnected reference counter and label it provider demand control. Do not scrape public quote pages or reuse personal-use display data.

## Complete indicator progress ledger

No indicator formula, hook, or renderer changed in this work cycle. Indicator implementation credit for this cycle: zero. The market-data identity hardening is shared data-integrity work, not an indicator completion claim.

| Indicator / subsystem | Status | Verified foundation | Remaining work / acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; warm-up nulls; candle-index alignment; prefix-causality regression | Calendar-aware gap semantics, chart overlay, enable/disable control, legend/latest value, stale clearing, lifecycle/render/performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha (2/21); first valid index 19; warm-up and causality coverage | Calendar-aware gap semantics, overlay, toggle, legend/latest value, lifecycle/render tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; rising/falling/flat/alternating regression cases | Gap reset semantics, dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal and histogram first valid index 33 | Gap semantics, dedicated pane, MACD/signal lines, histogram, zero guide, controls and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations; first valid index 19; numeric stability coverage | Gap semantics, upper/middle/lower overlay, toggle, latest values and render tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot gating and aligned calculation foundation | Keyed per-series store, calendar-aware input contract, hook tests, chart binding, stale clearing and renderer integration |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator only | User-provided visual reference, reviewed scoped blueprint, valid bid/ask data provenance/rights, dedicated cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted depth/liquidity renderer | User-provided visual reference, validated depth/liquidity contract, reviewed blueprint, renderer and lifecycle tests |
| Liquidation Maps | 🟥 Not implemented | No accepted provenance-backed calculation/renderer | Defensible data provenance, validated calculation contract, reviewed blueprint, visualization and tests |

### Indicator invariants — mandatory

- Warm-up values remain null; never substitute zero.
- Outputs remain aligned to original candle indices.
- Prefix causality: future candles must not change prior outputs.
- Non-finite, invalid, or missing observations must not silently become zero or valid input.
- Missing in-session candles must be distinguished from expected overnight, weekend, holiday, and scheduled session breaks.
- Do not use a guessed fixed-seconds gap threshold for session-aware instruments.
- No synthetic zero-price bars.
- Indicator state/output must clear or recompute on contract, venue, dataset, timeframe, bucket-policy, or calendar identity changes.
- Footprint OFF preserves the normal candlestick layout and spacing.
- Only explicit Footprint ON may activate the dedicated spaced-candle/cluster layout.
- Footprint and Heatmap visual implementation remains gated on user-supplied reference image(s) and a reviewed scoped blueprint.
- Documentation, CI, benchmarks, and data plumbing do not count as formula or renderer completion.

## Project stage dashboard

| Stage | Progress | Status / basis |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 Existing scored baseline; not re-scored by this cycle |
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Provider demand lifecycle and rights-cleared source remain open |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Multi-chart ownership and chart acceptance remain open |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Formula foundation exists; integration/rendering incomplete |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ No approved denominator |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ Debug APK CI artifact exists; external device/public deployment acceptance incomplete |

**Overall project progress: NOT SCORED.** No approved project-wide weights and denominator exist. Do not invent a total percentage.

**Gate 10:** Work remains in the Gate 10 workstream. Formal external acceptance remains 0/10 closed. CI success is necessary evidence, not proof of public deployment, real-device acceptance, data redistribution rights, or production operations.

## Significant progress in this cycle

- Frontend series identity is now validated at both snapshot and incremental-update boundaries.
- Invalid metadata cannot mutate the current market-data snapshot.
- Unsupported timeframe cannot bypass validation by supplying an explicit bucket policy.
- Backend fixture correction and frontend identity hardening both pass the full CI acceptance run.
- Native ARM64 image smoke test and zero-cost Android debug APK CI build succeeded.
- No paid service, provider credential, paid hosting, or cloud VM was added.

## Next engineering sequence

1. Preserve the passing CI baseline.
2. Design and test a keyed per-series market-data store before migrating the singleton supervisor.
3. Add independent chart-panel owner leases and generation guards; prove two-panel same-series and different-series behavior before wiring UI.
4. Verify real upstream provider lifecycle capabilities and pin the SDK only after documentation/runtime evidence; do not claim demand refcounting until connected to that lifecycle.
5. Define a typed, calendar-aware candle-gap contract before indicators bridge session gaps.
6. Integrate SMA/EMA/Bollinger overlays and RSI/MACD panes after the data/gap contract is tested.
7. Keep Footprint/Heatmap visual work behind the user's references and blueprint review.

Delivery target remains 24 December 2026. ZERO COST remains a hard constraint.
