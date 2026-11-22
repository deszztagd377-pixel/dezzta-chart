# Batch 62J-108 — WebSocket authentication contract regression guard

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Scope: Gate 20 / Gate 25 / Gate 36 repository-side regression prevention  
Cost: ZERO COST

## 1. Work completed

Added `backend/tests/test_websocket_documentation_contract.py` with two regression checks:

1. The backend README must document the actual HTTPS ticket-exchange endpoint, Firebase Bearer header, one-time WebSocket auth frame, source-defined ticket TTL, and non-production-only direct-token compatibility.
2. The endpoint and production legacy-auth rejection must remain present in the backend source.

This test directly guards against the documentation drift found and corrected in Batch 62J-107. It does not alter authentication behavior, runtime activation, secrets, market-data access, or client behavior.

## 2. Acceptance boundary

Repository-side ticket implementation and tests remain distinct from real production acceptance:

- Gate 20: real Firebase-project signed-token, revocation and entitlement E2E remains open.
- Gate 25: owner-host dedicated Redis `rediss://`, separate ACL identities, secret rotation, persistence/failover, and authenticated global snapshot installation/receipts remain open.
- Gate 36: public HTTPS/WSS hostname, certificate/SAN/chain, reverse-proxy Upgrade/timeouts, public WSS E2E, browser and Android WebView acceptance remain open.

The CI test is a repository regression guard. It cannot certify a public host, Firebase project, Redis deployment, or physical Android session.

## 3. Indicator progress — full status checkpoint

No indicator formula, data contract, calculation source, shared hook, renderer, chart UI, or indicator test changed. No indicator progress credit is awarded.

| Indicator/subsystem | Status | Calculation / first valid index | Remaining implementation/acceptance |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Arithmetic mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 FOUNDATION | SMA-seeded EMA; alpha = 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 FOUNDATION | Wilder-smoothed gains/losses over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 FOUNDATION | EMA12 − EMA26; MACD index 25; signal/histogram index 33 | Pane, two lines, histogram, zero guide, toggle, legend/current values, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 FOUNDATION | 20-close mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer/lifecycle tests |
| Shared Indicator Hook | 🟨 FOUNDATION | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / REFERENCE-GATED | Simulated educational accumulator; not exchange-native bid/ask truth | User reference image and reviewed blueprint, validated source/data contract, cluster renderer and lifecycle tests. OFF keeps normal candle spacing; explicit ON alone enables spaced clusters |
| Heatmap | 🟥 NOT IMPLEMENTED | No validated zero-cost data contract | Zero-cost source feasibility, user reference, approved blueprint, renderer, legend/scale, toggle and lifecycle tests |
| Liquidation Maps | 🟥 NOT IMPLEMENTED | No validated zero-cost source/calculation contract | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer, scale/legend and lifecycle tests |

Mandatory invariants: warm-up values are null (never zero); candle-index alignment; no future-candle repaint; stale-series clearing on symbol/venue/dataset/chart/timeframe changes; no fabricated bid/ask or liquidation data. Footprint OFF preserves standard candle spacing. Footprint and Heatmap visual implementation remain blocked on user-provided reference image(s) and approved blueprint. Overall indicator percentage remains unscored without approved weights and denominator.

## 4. Project progress checkpoint

- Gate 10: 0/10 formally closed.
- Host/operator verification-only: Gates 8, 30, 34, 35, 39.
- Integration/acceptance: Gates 20, 25, 31, 36, 38.
- Stage 1: 30/40 = 75% provisional.
- Stages 2–6 and overall project percentage: unscored; no approved denominators/weights.
- No gate closure is claimed by this regression test.

## 5. Verification accounting

- Added one focused backend regression-test file.
- No runtime source or client source changed.
- No indicator source or indicator test changed.
- No Termux/device action, deployment, paid service, Vercel/Cloudflare operation, or production credential use.
- `main` untouched.
- CI is expected to run from the branch push. Its result must be checked against the exact resulting commit before calling this test passed.
