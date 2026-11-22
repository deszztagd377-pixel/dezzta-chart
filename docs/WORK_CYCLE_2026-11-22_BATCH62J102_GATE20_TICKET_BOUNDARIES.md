# DEZZTA CHART — Work Cycle 62J-102
## Gate 20 ticket endpoint failure boundaries + Gate 10 evidence reconciliation

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `140df3f33fcebb9154f8ad26f40986ec73e2336f`  
**ZERO COST.** No deployment, paid service, Termux or production credential.

## Work completed

Three FastAPI integration tests were added to `backend/tests/test_api.py` (45 additions, zero deletions):
- Missing Bearer identity to `POST /v1/auth/websocket-ticket` returns 401.
- Missing/unavailable ticket store returns 503 and cannot issue a ticket.
- Internal ticket-store exception returns a generic 503 without leaking Redis credentials or exception details.

The test assertion was checked against the actual `require_verified_principal` API contract before accepting the final candidate. An intermediate test candidate contained an incorrect expected 401 detail and was superseded; only the exact final HEAD below is green.

## Configuration and security audit

Production Redis configuration was fully inspected. The normal Settings path already requires `REDIS_URL` in production, requires `rediss://`, and requires ACL username/password. The in-memory ticket store is a development fallback; no configuration defect was found and no unnecessary production code was changed.

Existing test evidence also covers digest-keyed ticket storage, TTL, single-use atomic consumption, subject binding, purpose validation, cross-client/process atomicity, encrypted backup/restore, fresh-path restore, schema and row hashes, foreign-key/integrity checks, and symlink rejection.

## Exact-head validation

Source/test HEAD: `140df3f33fcebb9154f8ad26f40986ec73e2336f`.

- Automated Tests [44969044429](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44969044429): SUCCESS.
- Frontend: 255 passed / 29 test files.
- Backend: 1,284 passed in 46.77 s.
- CodeQL [44969044418](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44969044418): SUCCESS.
- Full Git History Secret Audit [44969044471](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44969044471): SUCCESS.
- Outbox and full-cardinality SQLite metrics benchmarks: SUCCESS.
- Backend dependency audit, container build, Redis ACL/AOF + persistent-volume container smoke and Trivy scan: SUCCESS.
- Trivy artifact `14732364657`: 0 HIGH/CRITICAL findings in scanned Alpine OS and Python package targets, within configured scope.

## Gate 38 benchmark

Artifact `14732279593`; synthetic operational counters only.

Series = 762 request + 127 latency + 10 WebSocket = 899. Limit = 900. Utilization = 899/900 = 99.89%; one series slot remains.

| Profile | Flushes | p95 | p99 | Max | Retries |
|---|---:|---:|---:|---:|---:|
| 1 thread | 32/32 | 11.60 ms | 20.04 ms | 20.04 ms | 0 |
| 4 threads | 128/128 | 110.64 ms | 273.44 ms | 282.61 ms | 2 |
| 16 simultaneous threads | 512/512 | 342.89 ms | 595.76 ms | 1,258.36 ms | 67 |
| 4 OS processes | 128/128 | 110.26 ms | 237.08 ms | 267.35 ms | 1 |

Every profile verified 899/899 series, expected worker counts, aggregate request totals and SQLite integrity `ok`. Sixteen-thread peak DB+WAL+SHM = 6,235,232 bytes; post-checkpoint = 1,126,400 bytes. This is CI-runner synthetic evidence, not production SLA or host-volume acceptance. Contention remains visible: 67 retries in the 16-thread case.

## Gate 10

**0/10 formally closed.**

- 🟨🟩 host/operator verification only: Gates 8, 30, 34, 35, 39.
- 🟧 integration/acceptance open: Gates 20, 25, 31, 36, 38.

Gate 20 has stronger repository-side failure handling, but real Firebase signed-token E2E and final threat-model review remain. Gate 25 requires owner-host Redis TLS/ACL and authenticated snapshot/failover acceptance. Gate 31 requires independent off-host backup, offline key custody and key-recovery restore. Gate 36 requires public HTTPS/WSS, reverse proxy, live Redis and browser/Android WebView acceptance. Gate 38 requires owner-host persistent volume, private perimeter, dashboard/notifications and recovery drill.

CI Redis container smoke is not owner-host verification. No gate is closed based only on these tests.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored without approved denominators/weights.

## Indicator progress

No indicator implementation changed; no progress credit is awarded.

- SMA20 🟨 — mean of 20 closes; first valid index 19. Remaining overlay, toggle, legend/current value, stale clearing, renderer tests.
- EMA20 🟨 — SMA-seeded EMA, alpha 2/21; first valid index 19. Remaining overlay, toggle, legend/current value, stale clearing, renderer tests.
- RSI14 🟨 — Wilder smoothing over 14 close changes; first valid index 14. Remaining 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests.
- MACD 12/26/9 🟨 — EMA12−EMA26; MACD index 25, signal/histogram index 33. Remaining pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests.
- Bollinger20,2 🟨 — 20-close mean ±2×population SD; first valid index 19. Remaining three-line overlay, toggle, values, stale clearing, renderer tests.
- Shared Indicator Hook 🟨 — validated candle-index-aligned snapshot. Remaining chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation.
- Footprint 🟧 — simulated educational accumulator, not exchange-native bid/ask truth. User reference image and reviewed blueprint required before visual implementation. OFF keeps normal candle spacing; explicit ON enables spaced clusters.
- Heatmap 🟥 — not implemented; requires user reference, zero-cost source feasibility, validated data contract, blueprint and renderer.
- Liquidation Maps 🟥 — not implemented; requires zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer.

Invariants: warm-up values null, never zero; candle-index alignment; no future-candle repaint; stale clearing on symbol/venue/dataset/chart/timeframe changes. Stage 4 remains gated.

No `main` changes, no Vercel/Cloudflare deployment, no paid service, no Termux and no physical-device action.
