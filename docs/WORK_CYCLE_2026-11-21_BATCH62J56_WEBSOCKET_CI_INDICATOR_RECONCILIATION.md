# Work Cycle 62J-56 — WebSocket exact-head CI reconciliation and indicator ledger refresh

**Date:** 21 November 2026  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Exact branch HEAD:** `96bfea52d9920b7d5d49ed85c0536610a6afd037`  
**Automated Tests:** [GitHub Actions run 44849892717](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44849892717) — **SUCCESS**

## 1. Objective and scope

Close the pending verification of the previous WebSocket test-client compatibility cleanup, reconcile stale WebSocket dashboard statements against the latest accepted two-ASGI/Redis failure-matrix evidence, and refresh the indicator/project progress records without inventing acceptance credit.

## 2. WebSocket test cleanup and verification

Four synchronous WebSocket test-client connections in `backend/tests/test_ohlcv_redis_consumer.py` now pass `legacy=True` alongside `ping_interval=None`. The change responds to the deprecation warning emitted by the synchronous client API in the preceding test run. It is test-only: no production route, protocol, publisher, consumer, Redis configuration, chart or indicator source was changed.

Exact-head CI results:
- Frontend: **245 passed / 245**, across 29 test files.
- Backend: **1,218 passed** in **48.17 seconds**. Pytest produced no warnings summary.
- All 31 listed job steps completed successfully.
- Passed checks include frontend dependency audit, frontend source/bundle credential scans, Android preflight and immutable preview publisher tests, SQLite outbox benchmark, backend dependency audit, backend container image build, Redis ACL/AOF and persistent-volume smoke test, container vulnerability scan and report upload.

CodeQL and full reachable-history secret audit successes most recently recorded for runtime/source-test HEAD `56317eff2b71886040acb998bf692814622feedf` remain valid for that earlier checkpoint. This report does not claim they were rerun on `96bfea52d9920b7d5d49ed85c0536610a6afd037`.

## 3. WebSocket acceptance boundary

The automated two-ASGI failure matrix is **complete for the defined repository/CI scope**:
- independent ASGI processes and replica SQLite/consumer identities;
- authenticated live delivery and durable checkpoint convergence;
- reconnect replay boundary;
- gateway process restart continuity;
- independent Redis TCP-path interruption and recovery without gateway restart;
- coordinated snapshot-generation replacement and cursor convergence.

This completion is not production acceptance. Remaining external work is limited to:
1. owner-provisioned snapshot distribution, rotation, rollback, retention and authorized cleanup;
2. actual production Redis TLS/ACL/network policy, credential rotation, persistence, supervision and failover evidence;
3. accepted HTTPS/WSS reverse proxy and browser/Android client end-to-end acceptance;
4. operator-side recovery and incident evidence.

Do not repeat the automated two-ASGI failure matrix as unimplemented. Do not close Gates 25, 34, 35 or 36 using CI-only evidence.

## 4. Indicator progress — exact state, no false credit

| Indicator / subsystem | Status | Verified calculation/data foundation | First valid output | Remaining work |
|---|---|---|---:|---|
| SMA 20 | 🟨 Foundation | 20-close rolling arithmetic mean | Index 19 | Chart overlay, independent toggle, legend/current value, stale clearing and render/lifecycle tests |
| EMA 20 | 🟨 Foundation | EMA seeded by SMA20; alpha = 2/21 | Index 19 | Overlay controls, legend/current value, stale clearing and render/lifecycle tests |
| RSI 14 | 🟨 Foundation | Wilder-smoothed close-to-close gains/losses | Index 14 | 0–100 pane, 30/70 guides, toggle, legend and render/lifecycle tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | Dedicated pane, histogram, zero guide, toggle, legend and render tests |
| Bollinger 20,2 | 🟨 Foundation | SMA20 ± 2 population standard deviations | Index 19 | Three-line overlay/band, toggle, legend/current values, stale clearing and render tests |
| Shared indicator hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Snapshot-dependent | Bind to active symbol/venue/dataset/timeframe; loading/error states; stale-result clearing and cross-series isolation |
| Footprint | 🟧 Gated | Deterministic educational accumulator, explicitly SIMULATED | Depends on candle/price levels | User reference image and reviewed blueprint; ON-only spaced clusters, bid/ask cells, tests/performance |
| Heatmap | 🟥 Not implemented | No approved source/calculation contract | — | User reference image, reviewed blueprint, validated source, calculations, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | — | Source feasibility, reference/blueprint, calculation, renderer, controls and tests |

### Calculation invariants

- SMA20 and EMA20: first valid index 19.
- RSI14: first valid index 14 using Wilder smoothing.
- MACD12/26/9: MACD first valid index 25; signal and histogram first valid index 33.
- Bollinger20,2: population standard deviation, first valid index 19.
- Warm-up positions remain null/unavailable, not zero; every output remains aligned with candle indexes.
- Shared hook consumes validated backend snapshots only. No demo fallback.
- Symbol, venue, dataset, timeframe or chart identity changes must invalidate stale indicator results.
- Footprint OFF preserves the ordinary candlestick layout and spacing. Only explicit Footprint ON may switch to spaced candle/cluster layout.
- Footprint and Heatmap visual work must not begin before the user supplies the corresponding reference image(s) and reviews the scoped blueprint.

No indicator aggregate percentage is calculated because no weighted denominator has been approved. Repository-wide frontend tests do not prove chart-visible indicator acceptance.

## 5. Project progress accounting

| Measure | Current verified state | Display |
|---|---:|---|
| Stage 1 | 30/40 criteria = 300/400 ticks | 🟨 75% provisional |
| Remaining Stage 1 | 10 criteria = 100/400 ticks | 🟧 25% not yet accepted |
| Gate 10 | 0/10 formally closed | 🟧 All ten OPEN |
| Stages 2–6 | No approved scored denominator | ⬜ Not scored |
| Overall project | M1–M8 weights/denominator unapproved | ⬜ Not established |
| Indicator aggregate | No approved weights/denominator | ⬜ Not established |

The ten remaining Stage 1 criteria are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Each is 10 ticks (2.5 percentage points of Stage 1); no criterion was accepted in this cycle. The 75% figure is provisional Stage 1 progress, not overall project progress.

## 6. Cost, device and branch safeguards

- ZERO COST: no paid data provider, host, tunnel, subscription, domain, or publication fee was introduced.
- No Vercel or Cloudflare deployment/configuration action was performed.
- No production credentials, Firebase private keys, Redis ACL secrets or encryption keys were requested or exposed.
- No Termux/device operation was run. The live backend/database host is not established by the fact that the frontend is viewable on Vercel.
- `main` remains untouched. This work is confined to `phase-2/market-data-foundation`.

## 7. Next execution order

1. Establish the actual runtime/API/database location from the deployed frontend's API configuration and the backend runtime—not from the Vercel project page alone.
2. Advance Gate 30 only after identifying the live database and confirming the owner-controlled runtime where the restore drill can safely run.
3. Keep Gate 31 separate: encrypted off-host recovery and independent key custody cannot be inferred from same-device backup.
4. Continue repository-side work only where it directly reduces one of the ten open criteria; do not rerun the completed WebSocket failure matrix without a new defect.
5. Resume indicator UI implementation only within the approved stage/blueprint gates; collect Footprint/Heatmap visual references before their visual work.

**Acceptance decision:** WebSocket automated failure-matrix scope is complete. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed. No indicator score or overall project percentage is invented.
