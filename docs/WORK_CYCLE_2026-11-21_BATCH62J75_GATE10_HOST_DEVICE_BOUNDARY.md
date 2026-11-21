# DEZZTA CHART — Batch 62J-75
## Gate 10 host/device acceptance boundary and WebSocket CI reconciliation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test HEAD:** `f3264c7ee0db573b4ff999c558506c4efe3e59d5`

## 1. Exact-head verification

- Automated Tests [44875028851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028851): SUCCESS.
- CodeQL [44875028870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028870): SUCCESS.
- Full Git History Secret Audit [44875028765](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028765): SUCCESS.
- Backend: **1,249 passed in 49.05 seconds**.
- Redis ACL integration and existing end-to-end publisher/gateway ACL integration: PASSED.
- Backend container build, Redis shared-guard/AOF persistent-volume smoke, image scan and vulnerability report export/upload: SUCCESS.

The ACL integration test confirms DB-0 operation without `+select` and denies explicit `SELECT 1`. The previous Batch 62J-73 claim that `+select` was required is superseded by Batch 62J-74.

## 2. WebSocket production acceptance

**Repository-side automated WebSocket E/failure-matrix acceptance is complete for the defined CI scope. Production WebSocket acceptance is not complete.**

The repository and CI can prove source-level behavior and isolated Redis/container behavior. They cannot create or attest to an owner-controlled production host. The project currently has GitHub + CI only, no active backend server, no public HTTPS/WSS endpoint and no live Redis provider endpoint.

Still external:
- Actual global snapshot artifact transfer and SHA-256 verification.
- Authenticated install receipt for every required gateway.
- Owner-host dedicated Redis TLS/ACL, secret injection/rotation, persistence/failover/retention.
- Public HTTPS/WSS reverse proxy, certificate and renewal.
- Real browser and Android WebView acceptance against that endpoint.

No production readiness claim is made.

## 3. Gate 10 status board

Gate 10 contains ten gates. **0/10 are formally closed.** Yellow-green means source/CI work is complete for the listed scope and only owner-host/provider/operator evidence remains; it is not a passed gate. Bright green is reserved for complete acceptance evidence.

| Gate | Status | Remaining proof |
|---:|---|---|
| 8 — Secrets | 🟨🟩 Host verification only | Real host secret injection, file ownership/mode, process exposure and runtime leakage review |
| 20 — Firebase | 🟧 Open | Real no-billing Firebase project, auth/revocation/entitlement and browser/Android flow |
| 25 — Redis | 🟧 Open | Owner-injected snapshot verifier/receipts plus live dedicated Redis TLS/ACL, secret lifecycle, persistence and failover |
| 30 — Restore | 🟨🟩 Host verification only | Restore drill on the actual owner-controlled backend database path |
| 31 — Off-host backup | 🟧 Open | Independent backup destination, separate recovery-key custody, retention and restore |
| 34 — Persistent volume | 🟨🟩 Host verification only | Actual host mount, ownership, restart persistence and disk-pressure recovery |
| 35 — HTTPS | 🟨🟩 Host verification only | Actual HTTPS endpoint, certificate/hostname and renewal path |
| 36 — WSS | 🟧 Open | Public reverse proxy plus real browser and Android WebView acceptance |
| 38 — Monitoring | 🟧 Open | Collector/dashboard, cross-process aggregation, retention and access-control integration |
| 39 — Incident response | 🟨🟩 Host/operator verification only | Live operator visibility, acknowledgement/escalation and controlled recovery drill |

### What "host verification only" means

It does **not** mean simply opening the Android APK.

It means verifying the actual deployed infrastructure or owner-operated process:
- Host: backend process, environment, Redis connection, TLS certificate, firewall/reverse proxy.
- Storage: real persistent mount, ownership, backup destination, recovery path.
- Operations: actual secret injection/rotation, logs, alerts, operator acknowledgement and incident recovery.

Opening the APK is a separate device/client acceptance test. For Gate 36, that test becomes meaningful only after a real public HTTPS/WSS endpoint exists. The test will then cover sign-in, HTTPS ticket exchange, WSS connection, OHLCV subscription, reconnect/resnapshot and Android WebView lifecycle. No phone-side Termux command is required at this stage.

## 4. Indicator progress — full current ledger

| Indicator | Status | Formula/foundation | Remaining |
|---|---|---|---|
| SMA20 | 🟨 | Mean of 20 closes; first valid candle index 19 | Overlay, toggle, legend/current value, stale clearing, renderer tests |
| EMA20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/current value, stale clearing, renderer tests |
| RSI14 | 🟨 | Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend, renderer tests |
| Bollinger20,2 | 🟨 | Mean ± 2 × population SD; first valid index 19 | Three-line overlay, toggle, displayed values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 | Validated, candle-index-aligned snapshot | Identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 | Simulated/gated | User visual reference, approved blueprint, ON-only spaced cluster layout, bid/ask cells, performance acceptance |
| Heatmap | 🟥 | Not implemented | User reference, zero-cost source feasibility, validated data contract, blueprint and renderer |
| Liquidation Maps | 🟥 | Not implemented | Zero-cost source feasibility, validated calculation/data contract, blueprint/reference and renderer |

Invariants: warm-up is `null`, never zero; values align to candle indices; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters.

No indicator implementation progress is awarded by backend/host-gate work.

## 5. Project accounting

- Stage 1: **30/40 = 75% provisional**.
- Stages 2–6: not scored.
- Overall project percentage: not scored; approved aggregate weights/denominators do not exist.
- Gate 10: **0/10 formally closed**.

## 6. Cost and device boundary

ZERO COST. No paid hosting, deployment, production credentials, Vercel/Cloudflare operation, Termux or device action, and no `main` modification. The user does not need to fix or run any code now.
