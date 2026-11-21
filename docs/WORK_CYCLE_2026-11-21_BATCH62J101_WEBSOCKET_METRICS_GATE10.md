# DEZZTA CHART — Work Cycle 62J-101
## WebSocket accepted-counter semantics + Gate 10 continuation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test commit:** `db010cf76d6da2b1e950156f05bb18606b4fff2d`  
**Main:** untouched.  
**Cost:** ZERO COST.

## 1. WebSocket defect found and corrected

The prior implementation updated `connections_accepted` only from `finish()`. That meant a successfully accepted, still-active socket was missing from the cumulative accepted counter. This was a semantic defect in the metric, not a test-only discrepancy.

The accepted counter now increments immediately after the downstream ASGI send successfully completes a `websocket.accept` frame. The middleware sets its per-connection accepted flag and counts that event once. If the downstream send raises, the accepted counter is not incremented. `finish()` now handles lifecycle completion, active-gauge decrement, peer disconnect, close-code class and duration; it no longer delays or duplicates accepted counting.

## 2. Regression coverage

Added an application-level FastAPI integration test using the real registered middleware and authenticated WebSocket route. It checks:
- While the authenticated socket is open: started = 1, active = 1, completed = 0, accepted = 1.
- After orderly client closure: started = 1, active = 0, completed = 1, accepted = 1.

Existing middleware tests continue to cover failed accept send, failed close send, peer disconnect, unrelated routes and ASGI task cancellation. The app-level test closes the gap between isolated middleware tests and FastAPI wiring.

## 3. Candidate and CI audit trail

- Candidate `0857936d9129e51fad37dc921e895c79219f2108` failed backend tests: 1,280 passed and 1 failed. The failure showed accepted was 0 while the connection was already active.
- Intermediate candidate `13924cca3b3edff5e6fe41b43df6489924bf3a7b` temporarily changed the test expectation to match the old delayed counter. That interpretation was rejected after reviewing metric semantics; it is not accepted.
- Corrected source/test commit: `db010cf76d6da2b1e950156f05bb18606b4fff2d`.
- Automated Tests [44923590787](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590787): **SUCCESS** on exact source/test HEAD; 255 frontend tests passed across 29 files; 1,281 backend tests passed in 48.87 seconds. Synthetic outbox and 899-series SQLite metrics benchmarks, backend dependency audit, container build, shared Redis guard/persistent-volume smoke and configured HIGH/CRITICAL Trivy scan all succeeded.
- CodeQL [44923590774](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590774): **SUCCESS**.
- Full Git History Secret Audit [44923590739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44923590739): **SUCCESS**.
- CI is attached to source/test HEAD `db010cf76d6da2b1e950156f05bb18606b4fff2d`. The subsequent documentation-only commits use `[skip ci]` and do not change source/test behavior.

## 4. WebSocket / Gate 10 disposition

The repository-side lifecycle metric issue is corrected in the current candidate. Gate 36 is still 🟧 because repository tests cannot establish owner-host TLS/reverse proxy, public HTTPS/WSS, live Redis gateway, or browser/Android WebView acceptance.

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 host/operator verification only: Gates 8, 30, 34, 35, 39.
- 🟧 integration/acceptance open: Gates 20, 25, 31, 36, 38.

| Gate | Current evidence | Remaining acceptance |
|---|---|---|
| 8 | Repository baseline and CI evidence | Owner-host/operator verification |
| 20 | Firebase Admin verifier, deny-by-default entitlement, short-lived single-use ticket and revocation tests | Real Firebase signed-token E2E for valid/expired/revoked/wrong-project; review subject/purpose ticket scope against production threat model |
| 25 | Gateway runtime, TLS guards, snapshot/checkpoint/source/cursor/hash validation | Owner-host Redis TLS/ACL, authenticated snapshot transfer receipt, persistence/failover |
| 30 | Repository backup/restore verification | Owner-host restore drill and operator evidence |
| 31 | AES-256-GCM backup and fresh-path restore tests | Independent off-host copy, offline key custody and key-recovery restore |
| 34 | Repository/CI acceptance evidence | Owner-host/operator verification |
| 35 | Repository/CI acceptance evidence | Owner-host/operator verification |
| 36 | WebSocket auth/replay/reconnect/lifecycle tests and corrected accepted metric | Public HTTPS/WSS, reverse proxy, live Redis and browser/Android WebView acceptance |
| 38 | 899-series same-host SQLite collector, contention/failure-isolation tests and synthetic benchmark | Persistent host volume, private access perimeter, dashboard, notification and recovery drill |
| 39 | Incident escalation lifespan test and sanitized event | Independent operator notification, receipt and response drill |

Gate labels above are not closure credits. External host evidence is still required before any gate moves to closed.

Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored because approved weights/denominators do not exist.

## 5. Complete indicator progress

No indicator implementation changed in this cycle. No indicator credit is awarded.

| Indicator / subsystem | Status | Calculation / first valid candle index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Visible overlay, independent toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 close changes; index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, MACD/signal lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 × population SD; index 19 | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 Simulated/reference-gated | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance acceptance |
| Heatmap | 🟥 Not implemented | No validated source/calculation contract | User reference image, zero-cost source feasibility, validated contract, reviewed blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No validated source/calculation contract | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint and renderer |

Correctness invariants: warm-up values are null, never zero; values align to candle indexes; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; only explicit ON enables spaced clusters. Aggregate indicator percentage remains unscored without approved denominators. Stage 4 visible-indicator work remains behind its gate.

## 6. Cost and operational boundary

ZERO COST. No paid provider, subscription, hosting, Vercel/Cloudflare deployment, production credential, Termux command, physical-device action or `main` modification.
