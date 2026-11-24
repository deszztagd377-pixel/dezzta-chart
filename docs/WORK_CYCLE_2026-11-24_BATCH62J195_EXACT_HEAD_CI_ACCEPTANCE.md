# Work cycle — 24 November 2026 — Batch 62J-195: Exact-HEAD CI acceptance and indicator status

**Branch:** `phase-2/market-data-foundation`  
**Verified source/test HEAD:** `0ee74b9c21a7799a5e619a63dc83b01efb248936`  
**Previous audit:** [Batch 62J-193](WORK_CYCLE_2026-11-24_BATCH62J193_REPLAY_LIVE_HANDOFF_REGRESSION.md)  
**ZERO COST:** maintained. No paid data source, hosting, provider, subscription, production activation, or publication.

## 1. Exact-HEAD CI — terminal result

All four GitHub Actions workflows for exact HEAD `0ee74b9c...` reached terminal SUCCESS. This is not an inference from a partial job.

| Workflow | Run | Terminal result |
|---|---:|---|
| Automated Tests | 45307203622 | SUCCESS |
| CodeQL Security Analysis | 45307203666 | SUCCESS |
| OCI ARM64 Image Readiness | 45307203752 | SUCCESS |
| Full Git History Secret Audit | 45307203738 | SUCCESS |

### Automated Tests details

- Frontend dependency installation and audit: passed.
- Synthetic Cloudflare Worker isolated proof: passed.
- Pinned local `workerd` runtime: passed.
- Durable Object hibernation, alarms, and per-series isolation: passed.
- Frontend unit tests: passed.
- Frontend build: passed.
- Frontend bundle secret scans (pre-bundle and production bundle): passed.
- Read-only Android host preflight: passed.
- Immutable Android preview release publisher tests: passed.
- Backend dependency installation and audit: passed; pip-audit reported no known vulnerabilities.
- Redis TLS fixture and CA/hostname enforcement: passed.
- Backend suite: **1,359 passed, 1 skipped, 6 warnings** in 53.54 seconds.
- Synthetic SQLite outbox benchmark: passed with 1,000 bars inserted/replayed, 1,000 persistence latency samples, four replay-page latency samples, and two concurrent reader threads each replaying 1,000 events. This is explicitly a local synthetic benchmark, not a production provider/WebSocket or multi-process load test.
- Synthetic metrics collector benchmark: passed for 1, 4, and 16 workers; SQLite integrity was `ok` and aggregated request counts matched `workers × 32`.
- Backend container build: passed.
- Container smoke test: passed. Evidence includes health JSON, Redis ACL authentication persistence, AOF data across restart, fail-closed API outage response, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection.
- Trivy container scan: **0 HIGH/CRITICAL vulnerabilities reported** for the Alpine OS target and scanned Python package metadata targets.
- Container vulnerability report artifact uploaded successfully.
- Cleanup and container shutdown: passed.

The six backend warnings are non-failing dependency deprecation warnings from the websockets/Uvicorn legacy integration. They are recorded, not misreported as test failures. No warning suppression was added.

### CI artifacts

- Container vulnerability report: artifact ID `14881951118`.
- Synthetic outbox benchmark: artifact ID `14880639395`.
- Synthetic metrics collector benchmark: artifact ID `14880604478`.

## 2. Replay/WebSocket test acceptance

The following newly added regression cases were included in the successful exact-HEAD run:
- Retention-floor inclusive boundary: below/equal/above.
- Malformed checkpoint matrix: bool-as-int, negative applied cursor, missing retention floor, floor greater than applied cursor, negative floor.
- Exact scan-limit page continuation with contiguous cursor advancement.
- Replay/live interleaving around fixed watermark 43: queued cursors 42 and 43 deduplicated, cursor 44 retained once and resequenced.
- Malformed and non-monotonic queued cursors rejected with resnapshot required.

Existing coverage also confirms:
- Atomic snapshot and subscription registration boundary.
- Exact canonical-series routing and bucket-policy isolation.
- Two same-series subscribers do not interfere when one disconnects.
- Queue saturation requires resnapshot rather than silently skipping sequence numbers.
- Replay cursor must not precede the immutable snapshot cursor.
- Replica checkpoint and event/bar series identity validation.

These are deterministic repository-level tests. They do not claim a production provider feed, real production host WSS session, or physical Android background/network-transition acceptance.

## 3. Indicator progress ledger — full current status

No indicator runtime, formula, chart renderer, visible settings, pane, toggle, or chart binding was modified in Batches 62J-192 through 195. Indicator implementation credit in these batches is zero. The full calculation foundation remains as follows:

| Study | Calculation foundation | First valid output | Status | Remaining acceptance |
|---|---|---:|---|---|
| SMA20 | Arithmetic mean of 20 closes | Index 19 | 🟨 Foundation | Candlestick overlay, toggle, legend/latest value, identity invalidation, render/performance tests |
| EMA20 | SMA-seeded EMA, alpha 2/21 | Index 19 | 🟨 Foundation | Candlestick overlay, toggle, legend/latest value, identity invalidation, render/performance tests |
| RSI14 Wilder | Initial 14-change average, then Wilder recurrence | Index 14 | 🟨 Foundation | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render tests |
| MACD12/26/9 | EMA12/EMA26; MACD line then EMA9 signal and histogram | MACD index 25; signal/histogram index 33 | 🟨 Foundation | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, latest values, lifecycle/render tests |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | Index 19 | 🟨 Foundation | Upper/middle/lower overlays, toggle, latest values, identity invalidation, render/performance tests |
| Shared Indicator Hook | `useMarketIndicators()` consumes validated shared backend OHLCV snapshot; trust-state suppression and aligned output | Depends on study warm-up | 🟨 Foundation | Bind to chart UI, visible controls/legend, clear stale values on all identity/timeframe changes, accessibility and performance tests |
| Footprint | Offline synthetic educational accumulator only | Not a live-market study | 🟧 Prototype | User reference image, reviewed blueprint, validated bid/ask source contract, cluster renderer and acceptance tests |
| Heatmap | No accepted depth/liquidity renderer | N/A | 🟥 Not implemented | User reference image, validated depth/liquidity contract, reviewed blueprint, renderer and tests |
| Liquidation Maps | No accepted runtime/renderer | N/A | 🟥 Not implemented | Provenance and calculation contract, reviewed blueprint, renderer and tests |

### Mandatory indicator integrity rules

1. One validated OHLCV source per selected canonical instrument/timeframe; no separate price fetch or silent symbol substitution.
2. DEMO/loading/unavailable/error states never produce live indicator values.
3. Warm-up values remain null and outputs stay aligned to source candle indexes.
4. Prefix causality: adding future candles must not rewrite finalized historical outputs.
5. Non-finite, malformed, discontinuous, or invalid input fails closed or returns an explicitly unavailable state.
6. Revisions trigger the correct recomputation; instrument/timeframe identity changes clear stale output.
7. Calculation foundation is not visible chart completion.
8. Footprint OFF preserves standard candlestick spacing. Explicit Footprint ON alone may enable the dedicated spaced candle/cluster layout.
9. Footprint and Heatmap visual implementation stays gated until the user supplies their reference image(s) and reviews the scoped blueprint.

**Indicator aggregate: NOT SCORED.** No approved weighting and denominator exist. Counting calculation foundations as completed visible indicators would overstate acceptance.

## 4. Project progress accounting

| Workstream | Evidence-based state |
|---|---|
| Stage 1 | 30/40 = **75% provisional**; this CI pass does not itself close another Stage 1 criterion |
| Stages 2–6 | NOT SCORED |
| Gate 10 | 0/10 formally closed |
| Overall project | **NOT SCORED**; approved weighted denominator unavailable |
| WebSocket replay/reconnect | 🟩 Exact-HEAD CI passed; deterministic boundary regression suite strengthened |
| Backend CI and container | 🟩 Exact-HEAD CI passed, including smoke test and scan |
| Indicator aggregate | NOT SCORED |
| Cost | ZERO COST |
| Planning delivery target | 24 December 2026 (target, not guarantee) |

The 75% figure belongs only to Stage 1; it is not the overall product percentage.

## 5. Next engineering sequence

1. Continue WebSocket end-to-end acceptance matrix: authenticated real host, reconnect, replay under real Redis retention/trim, owner-host lifecycle, and physical Android network/background transitions. Keep synthetic tests distinguished from production acceptance.
2. Continue indicator UI integration planning; do not begin Footprint/Heatmap visuals before reference images and blueprint approval.
3. Reconcile Stage 1 evidence without changing the 30/40 numerator until a specific criterion is proven closed.
4. Keep cost zero and `main` untouched.

No user-side code/document repair is requested.
