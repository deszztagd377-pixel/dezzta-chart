# DEZZTA CHART — Batch 62J-74
## Exact-head WebSocket CI acceptance and Redis ACL least-privilege correction

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Verified CI head:** `3e3428910e3226f3d4365808f3a36a3138674231`

## 1. Verified results

- Automated Tests: [run 44874341856](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341856) — SUCCESS.
- CodeQL: [run 44874341916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341916) — SUCCESS.
- Full Git-history secret audit: [run 44874341885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341885) — SUCCESS.
- Backend pytest: **1,249 passed in 57.10 seconds**.
- New Redis ACL integration test: PASSED.
- Existing full Redis publisher/gateway ACL end-to-end test: PASSED.
- Backend container build, Redis/persistent-volume smoke, container vulnerability scan, vulnerability-report export and artifact upload: SUCCESS.

## 2. Redis ACL least-privilege correction

The previous Batch 62J-73 diagnosis that redis-py requires `+select` for a database-0 URL was incorrect. The existing real-Redis ACL integration test already demonstrated successful DB-0 operation without that grant.

The correction:
- Removes `+select` from `PUBLISHER_ACL_COMMANDS` and `GATEWAY_ACL_COMMANDS`.
- Retains URL validation that only permits the default DB 0.
- Adds explicit assertions that publisher and gateway identities cannot issue `SELECT 1`.
- Retains PING, publisher XADD/XRANGE, gateway group/read/ack/claim and lease Lua command tests.
- Retains command and key-scope denials.

This is a least-privilege tightening. It avoids granting an unnecessary command that could otherwise permit runtime database switching.

## 3. What the CI simulation now proves

### Redis ACL integration

The isolated Redis 7 service verifies the actual Redis ACL engine, two distinct ephemeral runtime identities, allowed publisher/gateway commands, exact key scope, lease operations, and prohibited commands. Generated passwords are runtime-only, never stored in source or printed, and temporary ACL users/keys are cleaned up.

### Existing WebSocket/relay integration

The same backend suite also passes real Redis tests for deterministic publisher cursor IDs, exact payload read-back, per-gateway consumer groups, durable apply-before-ACK, snapshot-generation group reset, replay, callback retry and lease ownership. The full failure-matrix repository scope remains CI-verified.

### Container and persistent-volume smoke

The existing workflow uses an isolated Redis container with a named data volume, AOF persistence and an ACL file. It verifies:
1. Unauthenticated Redis access is rejected.
2. Incorrect ACL password is rejected.
3. Unrelated SET commands are rejected.
4. AOF data and the ACL file survive Redis container restart.
5. Backend request protection fails closed with 503 during Redis outage.
6. Backend recovers after Redis restarts.
7. Backend process runs as non-root UID/GID 10001.
8. Mounted volume and SQLite database ownership are correct.
9. SQLite integrity and backend data survive backend container restart.
10. HTTP rate-limit enforcement rejects the follow-up request.

This volume smoke covers the shared HTTP/WebSocket guard Redis service. It is not proof of dedicated OHLCV stream production persistence/failover.

## 4. WebSocket production acceptance boundary

Repository-side automated WebSocket E/failure-matrix acceptance is complete for the defined CI scope. Production acceptance remains incomplete because no owner-controlled backend host exists.

Still host-bound:
- Actual global snapshot artifact transfer, verification and installation on every required gateway.
- Authenticated installation receipts bound to the exact snapshot SHA-256.
- Production Redis TLS certificate/hostname validation, ACL identities, private network policy and secret rotation.
- Dedicated OHLCV Redis stream persistence, failover, retention and recovery.
- Public HTTPS/WSS reverse proxy, certificate lifecycle and authenticated ticket exchange.
- Browser and Android WebView/device acceptance against the real public endpoint.
- Real backup target, monitoring retention, operator acknowledgement and recovery drills for the corresponding gates.

No production endpoint, credentials or remote host state is fabricated.

## 5. Gate 10 control board

- Gate 8 — 🟨🟩 HOST-VERIFICATION-ONLY.
- Gate 20 — 🟧 OPEN: real Firebase project/client configuration and Android acceptance.
- Gate 25 — 🟧 OPEN: live dedicated Redis TLS/ACL, persistence/failover and secret lifecycle.
- Gate 30 — 🟧 OPEN: owner-device/host restore acceptance; repository restore tests are not device acceptance.
- Gate 31 — 🟧 OPEN: off-host backup destination, independent key custody, retention and recovery.
- Gate 34 — 🟧 OPEN: actual host persistent-volume and restart acceptance.
- Gate 35 — 🟧 OPEN: public HTTPS certificate/proxy and renewal.
- Gate 36 — 🟧 OPEN: public authenticated WSS plus browser/Android acceptance.
- Gate 38 — 🟧 OPEN: host collector/dashboard, bounded log retention and operator access.
- Gate 39 — 🟧 OPEN: real alert receiver, named operator, acknowledgement/escalation and incident recovery.

**Gate 10:** 0/10 formally closed. CI improvements do not award formal closure ticks.

## 6. Project and indicator accounting

- Stage 1: 30/40 = 75% provisional.
- Stages 2–6: not scored.
- Overall project percentage: not scored; approved aggregate weights/denominators are not defined.
- Indicator aggregate percentage: not scored; no approved weighted denominator exists.

Complete indicator ledger:
- SMA20 — 🟨 foundation; mean of 20 closes; first valid candle index 19. Overlay, toggle, legend/current value, stale clearing and renderer tests remain.
- EMA20 — 🟨 foundation; SMA-seeded, alpha 2/21; first valid index 19. Overlay, toggle, legend/current value, stale clearing and renderer tests remain.
- RSI14 — 🟨 foundation; Wilder smoothing; first valid index 14. 0–100 pane, 30/70 guides, toggle, legend and renderer tests remain.
- MACD 12/26/9 — 🟨 foundation; MACD first index 25, signal/histogram index 33. Pane, lines, histogram, zero guide, toggle, legend and renderer tests remain.
- Bollinger20,2 — 🟨 foundation; mean ± 2 × population SD; first valid index 19. Three-line overlay, toggle, values, stale clearing and renderer tests remain.
- Shared Indicator Hook — 🟨 foundation; validated candle-index-aligned snapshot. Identity/timeframe binding, loading/error lifecycle, stale clearing and series isolation remain.
- Footprint — 🟧 simulated/gated; awaits user's visual reference, approved blueprint, ON-only spaced cluster layout, bid/ask cells and performance acceptance.
- Heatmap — 🟥 not implemented; awaits user's visual reference, zero-cost source feasibility, validated contract, blueprint and renderer.
- Liquidation Maps — 🟥 not implemented; awaits zero-cost source feasibility, validated calculation/data contract, blueprint/reference and renderer.

Invariants: warm-up is `null`, not zero; values align to candle indices; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; explicit ON alone enables spaced clusters.

## 7. Cost/device boundary

ZERO COST. No paid hosting, deployment, Vercel/Cloudflare operation, production credentials, Termux/device action or `main` modification.
