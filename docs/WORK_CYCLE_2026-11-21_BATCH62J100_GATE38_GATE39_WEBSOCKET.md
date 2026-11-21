# DEZZTA CHART — Work Cycle 62J-100
## Gate 38 cold-start contention correction + Gate 39 escalation verification + WebSocket cancellation accounting

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Accepted source/test HEAD:** `9e9a3d099f30faa2b641b8c991187394de783960`  
**Main branch:** untouched.  
**Cost:** ZERO COST. No paid provider, deployment, Termux, physical-device operation or production credential.

## 1. Scope and outcome

This batch continued after the 62J-99 audit and covered three related repository workstreams:

1. Gate 38: reproduce and correct the standalone 16-worker SQLite metrics benchmark's cold-start schema-lock failure.
2. Gate 39: verify that the incident escalation scheduler actually runs within the FastAPI lifespan and emits sanitized escalation events.
3. Gate 36/WebSocket: verify active-connection telemetry is decremented when the ASGI task is cancelled, not only after an orderly close frame.

The initial benchmark failure was investigated from the full GitHub Actions log. It occurred in `SQLiteMetricsCollector._connect()` during first-use schema initialization, before the worker's flush transaction. It was not a market-data or WebSocket protocol failure.

## 2. Gate 38 correction

Changed:
- `backend/app/metrics_collector.py`
- `backend/tests/test_metrics_collector.py`

The cold-start bootstrap retry loop was increased from 7 to 12 bounded attempts. Per-attempt SQLite busy timeout remains 250 ms; capped backoff remains 10, 20, 40, 80, 160 ms, then 250 ms for subsequent delays.

Conservative retry-wait bound:
- Busy-timeout component: 12 × 0.250 s = 3.00 s.
- Backoff component: 0.01 + 0.02 + 0.04 + 0.08 + 0.16 + (6 × 0.25) = 1.81 s.
- Combined bounded wait: 3.00 + 1.81 = **4.81 seconds**.

This is a theoretical upper bound for the bounded bootstrap retry path, not a startup SLO or measured production latency. Schema statements remain idempotent (`IF NOT EXISTS` / `INSERT OR IGNORE`); non-lock errors and exhausted retries still fail closed.

A new test launches 16 independent collector instances behind a barrier, each cold-booting and flushing against the same file-backed SQLite database. It verifies all 16 flushes, worker count, aggregated request count and `PRAGMA integrity_check = ok`. This is a 16-thread same-process cold-start test; it is not represented as a 16-process or multi-host test.

## 3. CI correction record — fully transparent

Three source/test candidates were observed:

- `ef0d5d0e743c5194c34788d21a6b51b437e283de`: the new Gate 39 and WebSocket tests passed and backend tests passed, but the standalone full-cardinality metrics benchmark failed with `sqlite3.OperationalError: database is locked` during cold-start schema bootstrap. This candidate is not accepted.
- `1171df891357f493da5ad726e8dd172aecd8fff6`: the 12-attempt retry correction prevented the cold-start lock failure. The newly added test then failed on an incorrect test assertion: the small fixture contains 12 series (1 HTTP + 1 latency + 10 WebSocket), not 899. The CI run had 1,279 passed and 1 failed. The source correction is retained; the bad assertion candidate is not accepted.
- `9e9a3d099f30faa2b641b8c991187394de783960`: corrected the test expectation to 12. Exact-head CI passed. The 899-series full-cardinality standalone benchmark also completed and its artifact was downloaded and parsed. This is the accepted source/test head.

No failed candidate is described as green.

## 4. Gate 38 full-cardinality benchmark — artifact read-back

Exact-head Automated Tests run [44918802298](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802298) produced synthetic metrics artifact **14713211332**, downloaded and parsed directly.

Declared series:
- 762 HTTP request series.
- 127 HTTP latency histogram series.
- 10 WebSocket series.
- Total: 762 + 127 + 10 = **899 logical series**, under the 900-series hard limit.
- Snapshot payload: **105,586 / 262,144 bytes = 40.28%** of configured cap.

| Profile | Flushes | p95 | p99 | Max | Lock retries |
|---|---:|---:|---:|---:|---:|
| 1 thread | 32/32 | 13.19 ms | 13.75 ms | 13.75 ms | 0 |
| 4 threads | 128/128 | 93.70 ms | 503.71 ms | 505.53 ms | 4 |
| 16 simultaneous threads | 512/512 | 580.90 ms | 876.84 ms | 1,674.60 ms | 164 |
| 4 independent OS processes | 128/128 | 189.85 ms | 283.65 ms | 309.32 ms | 2 |
| 16 startup-staggered threads | 512/512 | 281.33 ms | 355.51 ms | 568.17 ms | 30 |

All profiles verified 899/899 logical series, expected worker counts, expected aggregate request totals and SQLite integrity `ok`.

Within this same CI run, 16 startup-staggered threads versus 16 simultaneous threads:
- p95 improved by **51.57%**.
- p99 improved by **59.45%**.
- maximum flush latency improved by **66.07%**.
- lock retries decreased from **164 to 30**, an **81.71% reduction**.

Staggered retries did not reach zero. This benchmark therefore does not claim contention is eliminated. CI-runner contention is variable; these figures are synthetic observations, not a production SLO, host disk budget, multi-host guarantee or reason to change production cadence.

Peak DB+WAL+SHM:
- 16 simultaneous: 6,235,232 bytes.
- 16 staggered: 5,724,352 bytes.
- Both 16-worker profiles post-checkpoint: 1,126,400 bytes.

## 5. Gate 39 incident escalation integration

Changed:
- `backend/tests/test_api.py`

The new lifespan test injects a deterministic due incident and verifies that the real application background escalation loop calls the store and emits one sanitized `operator_incident_escalated` record. It confirms that the event contains only incident ID, severity, summary code and escalation level; it does not contain provider response, user identity or credential data.

Existing `SQLiteIncidentStore` tests continue to cover:
- Durable persistence and deduplication.
- Acknowledgement stopping escalation.
- Bounded escalation levels at 5, 15 and 30 minutes from incident creation.
- Reopening after a new occurrence.
- Resolution and 30-day resolved-record retention.
- Fail-closed capacity handling.
- Concurrent writes and restart reconciliation.

The operator-facing reporter remains local logger + same-host SQLite. No remote pager, push service, email, SMS or independent notification channel is implemented. Gate 39 remains 🟨🟩 host/operator verification only; no external operator receipt or response drill is claimed.

## 6. WebSocket lifecycle accounting

Changed:
- `backend/tests/test_observability.py`

A new cancellation test runs `WebSocketMetricsMiddleware`, waits until the connection is counted active, cancels the ASGI task, and verifies the middleware's `finally` path:
- started = 1.
- active = 0.
- completed = 1.
- accepted = 0.
- close-code class = `other` because no close frame was successfully sent.

This verifies gauge cleanup on task cancellation. It does not claim production WSS acceptance. Gate 36 remains 🟧 until the real HTTPS/WSS endpoint, TLS/reverse proxy, live Redis gateway and browser/Android WebView session are accepted.

## 7. Exact-head CI and security

On exact source/test HEAD `9e9a3d099f30faa2b641b8c991187394de783960`:
- Automated Tests [44918802298](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802298): **SUCCESS**.
- CodeQL [44918802275](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802275): **SUCCESS**.
- Full Git History Secret Audit [44918802271](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44918802271): **SUCCESS**.
- Frontend: **255 tests passed across 29 files**.
- Backend: **1,280 tests passed in 54.66 seconds**.
- Frontend build, source/bundle secret checks and Android host-preflight/preview-publisher tests: SUCCESS.
- Outbox and full-cardinality SQLite metrics benchmark plus artifact uploads: SUCCESS.
- Backend dependency audit, backend container build and shared Redis guard/persistent-volume smoke: SUCCESS.
- Trivy artifact **14713530156** was downloaded and parsed. Both scanned targets (Alpine OS and Python packages) contained **0 HIGH/CRITICAL vulnerabilities** in the configured scan scope.

The CI container smoke is not a production deployment. No Vercel/Cloudflare deploy was performed.

## 8. Changed files and commits

Source/test files changed:
- `backend/app/metrics_collector.py`
- `backend/tests/test_metrics_collector.py`
- `backend/tests/test_api.py`
- `backend/tests/test_observability.py`

Accepted source/test HEAD: `9e9a3d099f30faa2b641b8c991187394de783960`.

The three source/test candidate commits above remain in branch history to preserve the failure/fix audit trail. The latest candidate is the only accepted exact-head result.

## 9. Gate 10 and project accounting

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 Host/operator verification only: Gates 8, 30, 34, 35, 39.
- 🟧 Integration/acceptance still open: Gates 20, 25, 31, 36, 38.

Gate 38 repository-side cold-start and full-cardinality CI evidence improved, but host volume, monitoring perimeter, operator access, dashboard/notification and recovery drill remain external. No gate closure tick is awarded.

Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved denominators and weights.

## 10. Complete indicator ledger — unchanged

No indicator formula, calculation, data contract, shared hook, renderer, chart UI or indicator test changed. **No indicator progress credit is awarded.**

| Indicator / subsystem | Status | Formula / first valid candle index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Visible overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 Simulated/reference-gated | Synthetic educational accumulator, not exchange-native bid/ask truth | User reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance acceptance |
| Heatmap | 🟥 Not implemented | No validated source/calculation contract | User reference image, zero-cost source feasibility, validated contract, reviewed blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No validated source/calculation contract | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer |

Correctness invariants remain: warm-up values null (never zero); candle-index alignment; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves normal candle spacing; only explicit ON activates spaced clusters. Footprint and Heatmap visual work remains gated on owner references and reviewed blueprints.

## 11. Cost and operational boundary

ZERO COST. No paid provider, subscription, hosting, Vercel/Cloudflare deployment, production credential, Termux command, physical-device action or `main` modification. No user action is required for this repository-side batch.
