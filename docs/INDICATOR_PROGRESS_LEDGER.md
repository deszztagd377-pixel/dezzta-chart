[object Object]

## 62J-20 — 20 November 2026: exact-head indicator and WebSocket source audit

**Audited branch HEAD:** `a91a104db0acc6391d1511f65e881642b766d81e`  
**Runtime code checkpoint:** `468d0aa4a348d997dc7affb71374bc8712cfc39d`  
**Exact-head CI:** Automated Tests `44644831052` SUCCESS • CodeQL `44644831073` SUCCESS • Full Git History Secret Audit `44644831088` SUCCESS.

No indicator source, calculation test, chart renderer or WebSocket runtime code changed in this audit. The following status is therefore a reconciliation, not an implementation-progress award.

| Indicator / subsystem | Status | Source-level evidence | Remaining acceptance |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling arithmetic mean; first valid index 19; calculation tests | Stage 4 overlay, independent toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Stage 4 overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI 14 | 🟨 | Wilder smoothing over 14 close-to-close changes; first valid index 14 | Stage 4 0–100 pane, 30/70 guides, toggle, legend, lifecycle/render tests |
| MACD 12/26/9 | 🟨 | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Stage 4 dedicated pane, two lines, histogram, zero guide, toggle and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Stage 4 upper/middle/lower overlay, toggle, latest values and render tests |
| Shared indicator hook | 🟨 | Reads only validated backend snapshot; no DEMO/loading/error values | Stage 4 active chart binding, loading/error UI, stale identity/timeframe invalidation, cross-series tests |
| Footprint | 🟧 | Deterministic educational accumulator; explicitly SIMULATED | Owner reference image and reviewed blueprint; OFF preserves normal candles, explicit ON alone enables spaced clusters |
| Heatmap | 🟥 | No verified implementation | Owner reference, approved data contract/blueprint, calculations, renderer and tests |
| Liquidation Maps | 🟥 | No validated dataset/calculation contract | Source feasibility, approved data/calculation contract, renderer and tests |

### Verified chart integration boundary

The shared indicator hook exists but is not consumed by `CandlestickChart.tsx`. The chart currently creates a candlestick series only. The indicator UI blueprint is explicitly PARKED for Stage 4; visible indicator controls, overlays and oscillator panes must not be started during Stage 1. This is a roadmap constraint, not a technical claim that the calculations are missing.

### WebSocket cross-domain boundary

The current production WebSocket route remains source-SQLite/pipeline-backed. Redis replica workers are not lifespan-owned or route-wired. The two-process consumer tests do not prove two ASGI servers. Do not award indicator progress from Redis/CI success and do not wire mixed source/replica cursor domains.

### Accounting

- Stage 1 remains 30/40 = 75% provisional.
- Gate 10 remains 10/10 ORANGE and 0/10 closed.
- Overall project and indicator aggregate percentages remain unscored until denominators/weights are approved.
- No deployment, paid service, `main` change or Termux operation occurred.

