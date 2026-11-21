# DEZZTA CHART — Work Cycle 62J-97
## Production-staggered SQLite metrics benchmark and Gate 10 reconciliation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `8deeba557f7be6ea5cb66fb0bfb55955aafc5a41`  
**Documentation commits:** `7daf6dc7daac4ec3c7efc4e10478c917ac190216`, `fc6111ac7a7105143338e20eef7bf91b79424fd9`, `42a88ef1dae4bd466e41cfadf754cd71672e9a27`; `main` remains untouched.

## 1. Scope and source audit

This batch extends Gate 38's local synthetic benchmark. It does not modify the WebSocket protocol, market-data relay, Redis publisher/gateway, authentication, indicator calculations, chart renderer or deployment configuration.

The new benchmark case mirrors the production metrics worker's startup phase:
- Worker phase is the first eight hexadecimal characters of the worker UUID interpreted as an integer modulo 15.
- Each worker's normal flush cadence is 15 seconds.
- Sixteen workers are exercised with 32 flushes each: **16 × 32 = 512 successful flushes expected**.
- CI scales wall-clock sleeps by a configurable factor while preserving 15-second logical timestamps. Therefore the run is a deterministic concurrency/cadence model, not a 7.5-minute real-time soak test.
- The report checks 899 logical series, worker count, aggregate request count, SQLite integrity, retries, total flush latency, writer-lock wait, transaction/commit duration and local DB/WAL/SHM sizes.
- The simultaneous 1/4/16-thread stress cases and separate four-process contention case remain distinct benchmark profiles.

Source review confirmed that `backend/app/main.py` uses the same UUID-prefix modulo-15 startup phase and 15-second normal cadence. The benchmark does not change production scheduling.

## 2. Exact-head CI status

Exact-head run [44914991306](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991306) on `8deeba557f7be6ea5cb66fb0bfb55955aafc5a41` completed **SUCCESS** at 21 November 2026 21:42 WIB.

Completed successfully in the workflow:
- Frontend unit tests.
- Frontend source and production-bundle secret scans.
- Frontend build.
- Android host-preflight and preview-publisher tests.
- Backend tests.
- SQLite outbox benchmark and artifact upload.
- Existing SQLite metrics benchmark and artifact upload, including the new production-staggered case.
- Backend dependency audit.
- Backend container build.
- Shared Redis guard / persistent-volume smoke test.

Final Trivy scan, vulnerability report export/upload, dependency-audit enforcement and cleanup also completed successfully. The downloaded Trivy report artifact [14710634254](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991306) was parsed directly: **0 vulnerabilities** in both Alpine OS packages and Python packages, including zero HIGH/CRITICAL.

Exact-head CodeQL [44914991295](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991295) — **SUCCESS**.  
Exact-head Full Git History Secret Audit [44914991439](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44914991439) — **SUCCESS**.


## 2A. Read-back benchmark results

The CI artifact `synthetic-metrics-collector-benchmark` (artifact 14710929657) was downloaded and parsed. All benchmark assertions passed:

| Profile | Flushes | p95 | p99 | Max | Lock retries |
|---|---:|---:|---:|---:|---:|
| 1 thread | 32/32 | 7.36 ms | 9.51 ms | 9.51 ms | 0 |
| 4 threads | 128/128 | 86.91 ms | 274.07 ms | 296.15 ms | 3 |
| 16 simultaneous threads | 512/512 | 371.91 ms | 610.31 ms | 1,922.15 ms | 68 |
| 4 OS processes | 128/128 | 85.67 ms | 237.86 ms | 270.85 ms | 1 |
| 16 startup-staggered threads | 512/512 | 19.98 ms | 86.72 ms | 120.73 ms | 0 |

The 16-worker staggered case verified 16/16 workers, 512/512 flushes, 899/899 series, aggregate request count 512 and SQLite integrity `ok`. Its deterministic worker phase offsets were within 0–14 seconds. With 0.01 wall-clock cadence scaling, it models the logical 15-second production cadence; it is not a real-time soak test.

Relative to the simultaneous 16-thread stress case, the staggered synthetic profile reduced p95 by **94.63%**, p99 by **85.79%** and maximum flush latency by **93.72%**; lock retries fell from 68 to 0. The staggered p99 remains 86.72 ms, so tail latency is not declared eliminated. The separate four-process case still recorded one retry.

Staggered-case peak DB+WAL+SHM size was **3,169,952 bytes**; after WAL checkpoint it was **1,126,400 bytes**. These are CI-runner observations, not a production storage budget. Snapshot payload was **105,586 / 262,144 bytes = 40.28%**, leaving 156,558 bytes of the configured cap.

The benchmark's simultaneous and staggered cases are both synthetic profiles. Their difference supports retaining production staggering; it does not justify changing retry policy, production cadence, storage cap or declaring a production SLO.

## 3. Engineering interpretation and limits

The new staggered case tests whether the observed production start-phase distribution changes lock contention compared with the deliberately simultaneous stress case. It does not establish a production-host SLO, a physical disk-capacity budget, cross-host SQLite support or an acceptable operator recovery process.

Do not tune retry policy, production cadence or storage limits from this case alone. Compare the artifact's p95/p99/max, retry count and DB/WAL/SHM sizes against the accepted 62J-94 diagnostic baseline and the simultaneous/process cases. Any regression must be retained as evidence and corrected before acceptance.

Gate 38 remains 🟧 OPEN until exact-head CI and the remaining host/operator acceptance are complete: owner-controlled persistent volume, retention/backup, host access control, dashboard/monitoring visibility and recovery acceptance.

## 4. WebSocket and Gate 10 status

The repository-side automated WebSocket protocol/failure-matrix scope remains complete for its defined CI coverage. The current branch still contains the source publisher runtime factory, snapshot identity/cursor verification, gateway installation-receipt contract, Redis relay/replica handoff, reconnect/replay and lifecycle protections.

Production WSS is **not accepted**: there is no owner-controlled production backend host, live dedicated OHLCV Redis endpoint, installed gateway snapshot receipts, public HTTPS/WSS reverse proxy or real production browser/Android WebView session. These are host/provider/device proofs and cannot be manufactured by another source-only commit. No deployment or production credential operation is performed.

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 Host/operator verification only: Gates 8, 30, 34, 35 and 39.
- 🟧 Additional integration/acceptance still required: Gates 20, 25, 31, 36 and 38.

Yellow-green is not gate closure. It means repository-side preparation is complete for the documented scope and the remaining evidence must come from the owner-controlled host/provider/operator. Bright green is reserved for completed acceptance evidence.

## 5. Indicator ledger and project accounting

No indicator calculation, hook, renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

| Indicator / subsystem | Status | Formula / first valid candle index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Visible overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 price changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 Simulated / gated | Synthetic accumulator, not exchange-native bid/ask truth | User reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance acceptance |
| Heatmap | 🟥 Not implemented | No validated zero-cost data contract | User reference image, free-source feasibility, data contract, blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No validated source/formula contract | Zero-cost source feasibility, validated calculation/data contract, reference/blueprint and renderer |

Correctness invariants: warm-up slots are null, not zero; output stays candle-index aligned; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; only explicit ON activates the dedicated spaced-cluster layout. Footprint and Heatmap visual work remains gated on the user's reference images and reviewed blueprints.

Stage 1 remains **30/40 criteria = 300/400 ticks = 75% provisional**. Gate 10 remains 0/10 formally closed. Stages 2–6 remain unscored. Overall project percentage and aggregate indicator percentage remain unscored because approved weights/denominators are not established.

## 6. Cost and branch controls

ZERO COST. No paid service, deployment, Vercel/Cloudflare operation, production credential, Termux/device operation or `main` modification. No production host state is inferred or claimed.
