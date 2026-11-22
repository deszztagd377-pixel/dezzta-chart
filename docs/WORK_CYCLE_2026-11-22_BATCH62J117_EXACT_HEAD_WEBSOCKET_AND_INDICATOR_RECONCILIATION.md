# DEZZTA CHART — Batch 62J-117
## Exact-head WebSocket CI and indicator progress reconciliation

**Date:** 22 November 2026  
**Branch:** phase-2/market-data-foundation  
**Verified parent HEAD:** e76b6cd6c8f7380e5a10a7d4707028fa7da78a02  
**Scope:** repository WebSocket CI acceptance evidence, production gate disposition, indicator progress synchronization  
**Cost:** ZERO COST. Documentation only. No deployment, paid provider, OCI provisioning, production credentials, device action or main modification.

## 1. Exact-head repository CI result

All three workflows completed successfully against the same exact HEAD:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [#1952 / 44981803844](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844) | **SUCCESS** |
| CodeQL | [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808) | **SUCCESS** |
| Full Git History Secret Audit | [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851) | **SUCCESS** |

Automated Tests reports all 61 workflow steps completed successfully. Covered stages include frontend dependency audit, frontend unit tests and build, source/bundle credential scans, read-only Android host preflight tests, backend tests, Redis TLS CA/hostname fixture, synthetic SQLite outbox and metrics benchmarks, backend dependency audit, backend container build, persistent-volume Redis smoke test, container scan and vulnerability report export. These are repository-controlled CI checks; they are not proof of a live OCI host or public endpoint.

## 2. WebSocket acceptance disposition

| Gate / area | Repository evidence | Still required outside CI | Status |
|---|---|---|---|
| Gate 20 — identity and entitlement | Firebase verifier and ticket-exchange failure tests; one-use digest ticket, 90-second TTL, renewal checks | Real project signed-token cases: valid, expired, revoked, wrong project; real entitlement grant/revoke and renewal | 🟧 OPEN |
| Gate 25 — shared guard and Redis | Redis TLS CA/hostname/ACL fixture, AOF/persistent-volume restart smoke, ticket/lease tests | Owner-managed private Redis; TLS/hostname verification, least-privilege ACLs, secret rotation, host reboot, persistence, backup/restore, outage and retention | 🟧 OPEN |
| Gate 25/36 — snapshot distribution | Snapshot/replay, durable cursor and publisher/replica source-side tests | Verify exact snapshot bytes/hash and authenticated installation receipt on every required gateway; prove cursor baseline and live event fan-out | 🟧 OPEN |
| Gate 36 — public transport | HTTPS ticket exchange, WSS transport guard and protocol tests | Stable owner-controlled hostname, trusted TLS chain, public WSS handshake, reverse-proxy Upgrade/Connection/path/timeouts and certificate renewal | 🟧 OPEN |
| Gate 36 — client lifecycle | 17 transport tests, 7 ticket tests, 21 supervisor tests | Real browser and Android WebView background/foreground, Wi-Fi/mobile switch, token expiry/revocation, reconnect and duplicate-stream checks | 🟧 OPEN |
| Observability / operations | Metrics implementation and bounded synthetic collector benchmarks | Host dashboards, alert routing, retention, operator runbook and recovery drill | 🟧 OPEN |

Repository-side acceptance is CI-green for the defined test matrix. **Production WebSocket acceptance is not complete.** No host, production Redis endpoint, real Firebase project evidence, stable public hostname or public WSS endpoint is verified.

## 3. Security and operational invariants

- Production client uses HTTPS ticket issuance and WSS; plaintext remote transport is rejected.
- Firebase ID token is exchanged over HTTPS and is not placed in the WebSocket URL or auth frame. A short-lived one-use ticket is used for socket authentication.
- Ticket TTL remains 90 seconds; renewal requires explicit acknowledgement.
- Durable cursor replay is retained; sequence gaps reject and require fresh snapshot/watermark recovery. No silent skip.
- Redis is private and must never be exposed publicly.
- Production errors fail closed and do not disclose bearer tokens, tickets, Redis credentials or internal exceptions.
- Do not claim LIVE data merely because the API or socket is healthy; provider connectivity, freshness and completeness remain separate states.

## 4. Indicator progress — source-backed, unchanged

GitHub comparison from indicator source/test baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 to verified HEAD e76b6cd6c8f7380e5a10a7d4707028fa7da78a02 reports only documentation changes. No indicator formula, calculation source, hook, chart renderer, chart UI or indicator test source changed. Therefore this batch awards **zero indicator progress credit**.

| Study / subsystem | Current status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid candle index 19 | Visible overlay, independent toggle, legend/current value, identity/timeframe clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Visible overlay, independent toggle, legend/current value, identity/timeframe clearing, render/lifecycle tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing over 14 close changes; first valid index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, render/lifecycle tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, legend/current values, stale clearing and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Upper/middle/lower overlay, toggle, values, identity/timeframe clearing, render/lifecycle tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot; no implicit demo fallback | Dedicated hook tests, chart integration, loading/error lifecycle, per-series isolation and stale clearing |
| Footprint | 🟧 Simulation / reference-gated | Offline synthetic educational accumulator only; not exchange-native order flow | User reference image(s), reviewed blueprint, validated source contract, explicit toggle, ON-only spaced clusters, OFF-layout regression, performance/lifecycle tests |
| Heatmap | 🟥 Not implemented | No implementation verified | Zero-cost source feasibility, user reference, reviewed blueprint, validated data contract, renderer, scale/legend and tests |
| Liquidation Maps | 🟥 Not implemented | No implementation verified | Zero-cost source feasibility, validated calculation/data contract, user reference/blueprint, renderer, scale/legend and tests |

**Chart invariants:** warm-up values remain null, never zero; outputs retain source-candle index alignment; no future-candle repaint; stale indicator values clear when symbol, venue, dataset, chart or timeframe changes. Footprint OFF preserves ordinary candlestick spacing; only explicit ON activates a dedicated spaced-cluster layout. Do not begin Footprint or Heatmap visual work before the corresponding user reference image(s) and reviewed blueprint are available.

The complete formulas, numerical safeguards, data lineage, lifecycle requirements and acceptance matrix remain in the indicator audit. Aggregate indicator percentage remains unscored because approved weights and a denominator do not exist.

## 5. Project accounting and next sequence

- Gate 10 remains **0/10 formally closed**.
- Gates 20, 25 and 36 remain open as described above.
- Stage 1 remains **30/40 = 75% provisional**; this batch awards no stage progress.
- Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- No production acceptance, deployment or public endpoint is claimed.

Next sequence: keep repository-side CI green; prepare and review host configuration/readiness and recovery requirements; only then consider owner/guardian-managed Always Free account eligibility and explicit authorization; perform host acceptance before public WSS; finish with real browser/Android WebView acceptance. No OCI resource or account is created by this batch. Do not use trial credits or paid resources; if a lawful free hostname/TLS route is unavailable, public WSS remains blocked at Rp0.

## 6. Files updated in this documentation batch

- docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md
- docs/INDICATOR_PROGRESS_LEDGER.md
- docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md
- docs/WEBSOCKET_PRODUCTION_WIRING_AUDIT.md
- Added this reconciliation document.

No runtime code, tests, provider integration, secrets, host configuration, deployment or indicator implementation changed. Exact-head CI for the new documentation commit must be verified separately before the new commit is called CI-accepted.
