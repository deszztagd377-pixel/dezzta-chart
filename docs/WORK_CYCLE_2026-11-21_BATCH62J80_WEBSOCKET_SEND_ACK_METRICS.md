## Batch 62J-80 — WebSocket send-confirmed lifecycle accounting (21 November 2026)

**Branch:** phase-2/market-data-foundation  
**Parent source/docs HEAD:** 6f21e9ab35f2a29176c615a381f4e014ff65ea5d

### Defect corrected
The lifecycle observer previously set accepted and close_code before awaiting the downstream ASGI send. If the server transport rejected a send, private metrics could report an accepted handshake or a close code for a frame that was never successfully handed to the server.

### Change
- The observer now awaits downstream send(message) first and records websocket.accept / websocket.close only after that call returns successfully.
- The existing finally path still decrements active connections and records completion on exceptions, preventing a failed transport send from leaking the active gauge.
- No payload, authorization header, ticket, IP, account ID, symbol, query string or close reason is recorded.
- The /ws/market-data scope, five close-code classes, saturation bounds, private bearer-protected metrics endpoint and WebSocket wire protocol remain unchanged.

### Regression coverage
A new asynchronous test exercises two transport-failure cases:
1. Accept send fails: completed increments, active returns to zero, accepted remains zero, and the close class remains other.
2. Close send fails after successful accept: completed increments, active returns to zero, accepted remains one, and no unsent close code is counted.

This verifies that metrics represent successfully handed-off ASGI events rather than attempted events.

### Gate disposition
- Gate 38: 🟧 OPEN. Source-side metric correctness improves; process-local scope still lacks cross-worker aggregation, central collector/dashboard, durable retention and independent operator notification.
- WebSocket repository failure-matrix: existing automated scope remains complete; this adds send-failure accounting coverage. Production acceptance remains blocked on owner-controlled snapshot receipts, production Redis TLS/ACL/credential lifecycle, public HTTPS/WSS and real browser/Android WebView evidence.
- Gate 10: 0/10 formally closed. Host-only verification remains 🟨🟩 for Gates 8, 30, 34, 35, 39. Additional integration remains 🟧 for Gates 20, 25, 31, 36, 38.

### Indicator accounting — unchanged, full ledger retained
| Indicator | Status | Formula / first valid candle | Remaining visual/lifecycle work |
|---|---|---|---|
| SMA20 | 🟨 | Mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer tests |
| EMA20 | 🟨 | SMA-seeded EMA; alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer tests |
| RSI14 | 🟨 | Wilder smoothing; index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 | EMA12−EMA26; MACD index 25, signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 | Mean ±2 × population SD; index 19 | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 | Validated candle-index-aligned snapshot | Identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 | Simulated/gated | User visual reference, approved blueprint, ON-only spaced clusters, bid/ask cells, performance acceptance |
| Heatmap | 🟥 | Not implemented | User visual reference, zero-cost source feasibility, validated data contract, blueprint and renderer |
| Liquidation Maps | 🟥 | Not implemented | Zero-cost source feasibility, validated formula/data contract, reference and renderer |

Indicator invariants remain: warm-up is null (never zero); output is candle-index aligned; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; only explicit ON enables the spaced-cluster layout. No indicator progress is credited by this WebSocket-only change.

### Cost and branch controls
ZERO COST maintained. No hosting, paid provider, deployment, Vercel/Cloudflare operation, production credential, Termux/device operation or main modification. No production endpoint is fabricated.

**Validation:** exact-head CI will be reported only after GitHub Actions confirms completion for this commit; this work cycle does not pre-claim test success.
