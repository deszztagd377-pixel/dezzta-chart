# DEZZTA CHART — Work Cycle 62J-70/71
## Source publisher runtime factory, snapshot alignment and production WSS guard

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `5575f5d820dd26d16a7170cb2c55e9c707c2afc1`

## Batch 62J-70 — Source publisher runtime factory

Added:
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_runtime.py`
- Updates to `backend/app/ohlcv_redis_config.py` and `backend/tests/test_ohlcv_redis_config.py`
- Source relay variables in `backend/.env.example`

The factory is explicitly injected into the source FastAPI app. It does not automatically enable the default ASGI application and does not reuse the shared security-guard Redis URL.

Production requirements are enforced before client creation:
- Dedicated ACL URL with username/password, `rediss://`, Redis DB 0 and exact stream key.
- 3-second connection timeout, 5-second socket timeout, 15-second health-check interval.
- TLS certificate-chain and hostname verification.
- Stable non-empty source publisher owner ID.
- Existing durable SQLite checkpoint; the helper never initializes or guesses a cursor.

The host snapshot verifier must return the global source ID, stream key, generation and cursor, the full required gateway ID list, and one installation receipt per gateway. Every receipt must match the same source, stream, generation and cursor. A missing, duplicate or mismatched receipt stops startup before a Redis client is created.

Publisher and gateway ACL command allow-lists include `+ping` for readiness. Publisher permissions remain `+ping +xadd +xrange`; gateway permissions remain separate and include the consumer and lease operations.

## Batch 62J-71 — Production HTTPS/WSS client guard

Updated:
- `src/services/ohlcvWebSocketTicket.ts`
- `src/services/ohlcvWebSocketTicket.test.ts`
- `src/services/ohlcvWebSocketClient.ts`
- `src/services/ohlcvWebSocketClient.test.ts`

Production frontend builds reject HTTP ticket endpoints and `ws://` market-data URLs before network/socket creation. HTTPS ticket exchange and WSS connections remain accepted. Development behavior is unchanged.

## Exact-head CI

- Automated Tests [44868539276](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44868539276) — **SUCCESS**.
- CodeQL [44868539309](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44868539309) — **SUCCESS**.
- Full Git History Secret Audit [44868539423](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44868539423) — **SUCCESS**.
- Android APK Build [44868539288](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44868539288) — **SUCCESS**, build only.
- Frontend tests: **249/249**, 29 files.
- Backend tests: **1,246 passed**.
- Workflow steps: **33/33 succeeded**.
- Backend image build, shared Redis/persistent-volume smoke, container scan, vulnerability-report export and artifact upload: **SUCCESS**.

## Full indicator progress ledger

| Indicator | State | Calculation / first valid index | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 Foundation | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated snapshot, candle-index aligned | Identity/timeframe binding, loading/error, stale clearing, series isolation |
| Footprint | 🟧 Simulated / gated | Educational simulation only | User visual reference, approved blueprint, ON-only spaced clusters, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | No approved data/calculation contract | Visual reference, free-source feasibility, validated contract, blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation | Free-source feasibility, validated calculation, blueprint/reference and renderer |

Correctness rules remain mandatory: warm-up slots are null, not zero; outputs align to candle indexes; future candles cannot alter earlier values; symbol/venue/dataset/chart/timeframe changes invalidate stale series. Footprint OFF retains normal candle spacing; only explicit ON activates the spaced cluster layout. Footprint and Heatmap visual work remains blocked on user reference images and blueprint approval.

## Gate 10 dashboard

| Gate | State | Remaining acceptance |
|---:|---|---|
| 8 — Secrets | 🟨 Host verification only | Actual secret injection, owner/mode, UID/GID readability, process exposure, rotation |
| 20 — Firebase | 🟧 Open | Real no-billing auth, revocation, entitlement, browser/Android flow |
| 25 — Redis | 🟧 Open | Live TLS, ACL, credential lifecycle, persistence, failover and network isolation |
| 30 — Restore | 🟧 Open | Restore drill on actual live database path |
| 31 — Off-host backup | 🟧 Open | Independent destination/key custody and restore |
| 34 — Persistent volume | 🟧 Open | Actual mount, ownership, restart persistence, disk-pressure recovery |
| 35 — HTTPS | 🟧 Open | Public endpoint, certificate, hostname and renewal |
| 36 — WSS | 🟧 Open | Public reverse proxy, browser and Android WebView/device acceptance |
| 38 — Monitoring | 🟧 Open | Collector/dashboard, retention, access control and disk-pressure evidence |
| 39 — Incident response | 🟧 Open | Operator visibility, escalation, acknowledgement and recovery drill |

Gate 10: **0/10 formally closed**. Stage 1: **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored pending approved denominators/weights.

## Production WebSocket acceptance — still external

Repository code and automated acceptance are not the same as production host acceptance. Remaining external proof includes actual gateway snapshot installation receipts, persistent host volumes, production Redis TLS/ACL, gateway runtime configuration, public HTTPS/WSS proxy, and browser plus Android WebView/device execution. The source publisher stays 🟨🟩 HOST VERIFICATION PENDING; Gate 25 and Gate 36 stay 🟧 OPEN.

ZERO COST. No production deployment, paid service, production credential, Termux/device operation, Vercel/Cloudflare operation or `main` modification.
