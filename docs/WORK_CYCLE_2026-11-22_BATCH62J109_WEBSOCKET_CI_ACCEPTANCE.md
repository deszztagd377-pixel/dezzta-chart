# DEZZTA CHART — Batch 62J-109
## WebSocket CI regression correction + production acceptance evidence reconciliation

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Commit:** `81b741946f1512fb264936e37406d7560f24456f`  
**Parent:** `b7d61f8d42546806c83bf56d0d2373be57dca9fc`  
**Cost boundary:** ZERO COST. No deployment, paid service, production credential, Vercel/Cloudflare operation, Termux/device action, or `main` modification.

## 1. Work completed

The previous exact-head Automated Tests run on Batch 62J-108 failed one new documentation-contract assertion while 1,290 other backend tests passed. Inspection established that `backend/README.md` already contained the correct HTTP Bearer header and one-time WebSocket auth frame. The regression test normalized the README to lowercase for endpoint/header/TTL assertions but compared the JSON frame against the original case-sensitive string. This made the test inconsistent with its own normalization strategy.

Changed exactly one source-controlled file:

- `backend/tests/test_websocket_documentation_contract.py`: compare the documented auth-frame literal against `normalized`, not `readme`.

No runtime behavior, protocol, auth semantics, client, Redis configuration, indicator implementation, or deployment configuration changed. The patch reduces a false-negative test failure without weakening the contract: the exact serialized JSON structure remains asserted, but case normalization is applied consistently to the README text.

## 2. Exact-head CI acceptance

All three workflows ran against the exact commit above:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44973890901](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890901) | **SUCCESS** |
| CodeQL Python + JavaScript/TypeScript | [44973890847](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890847) | **SUCCESS** |
| Full Git History Secret Audit | [44973890902](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44973890902) | **SUCCESS** |

Automated Tests completed every step, including frontend unit tests/build and secret scanning, backend tests and dependency audit, backend container image build, shared Redis guard + persistent-volume smoke test, container image scan/report, and synthetic SQLite outbox/metrics collector benchmarks. The job reported no failed steps.

## 3. WebSocket production acceptance boundary

This batch verifies repository CI only. It does not close production acceptance. The remaining external evidence remains:

1. Gate 36: owner-controlled public hostname, valid TLS/SAN/chain, reverse-proxy Upgrade/Connection/path/timeout checks, public WSS handshake and reconnect.
2. Gate 25: dedicated owner-host Redis `rediss://`, certificate/hostname verification, distinct ACL identities, persistence/AOF, restart/failover and secret-rotation evidence.
3. Gate 25/36: authenticated authoritative snapshot transfer, source/generation/cursor/SHA-256 verification, and a matching installation receipt for every required gateway before publisher activation.
4. Gate 20: actual Firebase project token signature/revocation and entitlement E2E, including ticket exchange and renewal.
5. Gate 36: real browser and Android WebView acceptance: foreground/background, network transition, snapshot/replay, heartbeat, renewal, reconnect, and duplicate-stream prevention.

The repository already contains fail-closed publisher and gateway runtime factories. They require owner-injected snapshot verifier/installer callbacks and validated evidence; no environment-only shortcut, fake receipt, hardcoded credential, or mock may be used to claim production acceptance.

APK distribution and backend reachability are separate: a free APK download link can distribute the client package, but every device still needs a reachable HTTPS/WSS backend and active owner-operated relay. No hosting or deployment was performed in this batch.

## 4. Gate 10 and project progress

- Gate 10: **0/10 formally closed**. Five host/operator-only tracks: Gates 8, 30, 34, 35, 39. Five integration/acceptance tracks: Gates 20, 25, 31, 36, 38.
- Stage 1: **30/40 = 75% provisional**. This batch resolves one CI regression but does not alter the Stage 1 denominator or award a new percentage point.
- Stages 2–6 and total project percentage remain unscored until approved weights and denominators exist.
- The CI issue is closed for this commit; production WebSocket acceptance remains open.

## 5. Complete indicator progress — no implementation delta

No indicator code or test changed in this batch. Consequently, no indicator receives progress credit.

| Indicator | Formula / first valid candle index | Status | Remaining acceptance |
|---|---|---|---|
| SMA20 | Arithmetic mean of 20 closes; index 19 | 🟨 Foundation | Visible overlay, independent toggle, legend/current value, stale-series clearing, renderer/lifecycle tests |
| EMA20 | SMA-seeded EMA; alpha = 2/(20+1) = 2/21; index 19 | 🟨 Foundation | Visible overlay, independent toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | Wilder-smoothed average gains/losses over 14 close changes; index 14 | 🟨 Foundation | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, renderer tests |
| MACD 12/26/9 | EMA12 − EMA26; MACD index 25; signal/histogram index 33 | 🟨 Foundation | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, stale clearing, renderer tests |
| Bollinger20,2 | 20-close mean ± 2 × population SD; index 19 | 🟨 Foundation | Upper/middle/lower overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | Validated candle-index-aligned indicator snapshot | 🟨 Foundation | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, per-series isolation, renderer integration |
| Footprint | Current educational accumulator is simulated, not exchange-native bid/ask truth | 🟧 Reference-gated | User reference image + reviewed blueprint before visual implementation; validated source/data contract; cluster renderer, toggle, scale/interaction, performance/lifecycle tests. OFF preserves normal spacing; ON enables spaced clusters |
| Heatmap | Not implemented; no validated zero-cost source/data contract yet | 🟥 Not implemented | User reference, zero-cost source feasibility, validated contract, reviewed blueprint, renderer, legend/scale, toggle, lifecycle tests |
| Liquidation Maps | Not implemented; do not infer or fabricate liquidation levels | 🟥 Not implemented | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer, scale/legend, toggle, lifecycle tests |

**Shared invariants:** warm-up outputs are null, never zero; output arrays align to source candle indices; no future-candle repaint; stale series clear on symbol/venue/dataset/chart/timeframe changes; invalid bars and gaps are not silently converted to zero. Footprint OFF preserves standard candle spacing; only explicit ON selects spaced cluster layout. User-supplied visual references and reviewed blueprints remain mandatory for Footprint/Heatmap/Liquidation visual work.

Aggregate indicator percentage remains unscored because no approved weights/denominator exist. See `docs/INDICATOR_PROGRESS_LEDGER.md` for the maintained full ledger.

## 6. Next engineering sequence

1. Preserve the green exact-head CI baseline; any new patch must be isolated and fully revalidated.
2. Continue repository-side WebSocket acceptance only where a concrete code/test gap can be demonstrated without inventing host trust, credentials, or deployment.
3. For public WSS/Firebase/Android evidence, request only non-secret endpoint/project/device test coordination when genuinely required; never request passwords, private keys, tokens, or Redis credentials in chat.
4. Keep zero-cost boundary and do not deploy to Vercel/Cloudflare.

**Disposition:** Batch 62J-109 is committed and exact-head CI accepted. Production WebSocket acceptance remains open; no Gate 10 closure is claimed.
