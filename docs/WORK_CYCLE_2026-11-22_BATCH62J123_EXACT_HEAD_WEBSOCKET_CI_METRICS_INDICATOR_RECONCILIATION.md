# Work cycle — Batch 62J-123 exact-head WebSocket CI, SQLite contention and indicator reconciliation

**Date:** 22 November 2026  
**Branch:** phase-2/market-data-foundation  
**Exact tested source/test HEAD:** 589aceadd40b3b3e10e950566081101b2dd49003  
**CI:** Automated Tests #1960 [44985059074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074) SUCCESS; CodeQL [44985059102](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059102) SUCCESS; Full Git History Secret Audit [44985059070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059070) SUCCESS.

## 1. Scope and exact change

The prior Automated Tests run failed at concurrent SQLite connection setup while applying PRAGMA synchronous=NORMAL. The bounded retry correction is in backend/app/metrics_collector.py; the repeated concurrent regression test is in backend/tests/test_metrics_collector.py. Exact tested HEAD is 589aceadd40b3b3e10e950566081101b2dd49003. Git compare from indicator baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 shows 10 commits/17 changed paths; the only source/test changes in the full range are those two backend files. No indicator code changed.

## 2. Exact-head workflow result

All three workflows for the exact tested SHA completed successfully. Automated Tests completed 36/36 job steps, with no failed steps. The workflow includes frontend tests/build and secret scans; backend tests and dependency audit; ephemeral Redis TLS CA/hostname fixture; synthetic SQLite outbox and metrics benchmarks; container build; shared Redis guard and persistent CI volume smoke; Trivy scan/report; and dependency-audit enforcement.

Links: [Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074), [CodeQL](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059102), [Full Git History Secret Audit](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059070).

## 3. Synthetic metrics artifact — exact measurements

Artifact [14739815366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739815366), full 899 logical-series envelope:

| Profile | Successful flushes | Retries | p95 flush | p95 writer-lock wait | Integrity |
|---|---:|---:|---:|---:|---|
| 1 thread | 32/32 | 0 | 14.34 ms | 0.015 ms | ok |
| 4 threads | 128/128 | 4 | 46.92 ms | 35.57 ms | ok |
| 16 simultaneous threads | 512/512 | 187 | 627.74 ms | 572.23 ms | ok |
| 4 independent processes | 128/128 | 3 | 141.71 ms | 128.70 ms | ok |
| 16 startup-staggered threads | 512/512 | 26 | 266.53 ms | 250.93 ms | ok |

All flushes succeeded in these synthetic profiles and all reported integrity checks were ok. However, 16 simultaneous workers exhibit material lock contention. This is CI runner/filesystem-specific synthetic telemetry, not a production persistent-volume, real traffic, multi-host or SLO test. Retain the same-host best-effort classification; do not infer supported production capacity. A single-writer queue/aggregation design would be a separately scoped architecture decision.

## 4. Container security artifact

Trivy artifact [14739224531](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739224531) independently inspected: dezzta-chart-backend:ci, Alpine 3.24.4, amd64, digest sha256:5240158d55f11863aa41a49fbf4d00705d437519fcbdb0659164efc435ee58c0, size 571,352,064 bytes. The report lists zero vulnerabilities in the scanned Alpine OS and Python package result groups. This is point-in-time and scoped to this image/database; it is not a permanent guarantee or ARM64 evidence.

The Docker workflow uses plain docker build on ubuntu-latest, not a verified multi-platform Buildx build. ARM64 build and runtime smoke remain unverified.

## 5. WebSocket production acceptance

Repository-side implementation and CI are not owner-host acceptance. Keep Gate 10 at **0/10 formally closed** and Stage 1 at **30/40 = 75% provisional**. The following evidence remains absent:

- Gate 8: owner-host secret injection, file permissions, rotation and log redaction.
- Gate 20: real Firebase project valid/expired/revoked/wrong-project signed-token E2E and entitlement grant/revoke/renewal.
- Gate 25: owner-host Redis TLS CA/hostname, ACL, secret rotation, persistence/restart/failover, authenticated global snapshot bytes/hash and per-gateway install receipts with exact generation/cursor alignment.
- Gate 30: live database backup/restore and integrity readback.
- Gate 31: encrypted off-host backup and independently held recovery-key custody.
- Gate 34: persistent volume UID/GID 10001, restart and disk-pressure validation.
- Gate 35: verified public hostname, trusted TLS chain and renewal.
- Gate 36: public HTTPS ticket exchange/WSS reverse proxy, browser and Android WebView lifecycle, replay/resnapshot and duplicate suppression.
- Gate 38: real dashboard, retention, alerting and disk-pressure behavior.
- Gate 39: actual external alert delivery, human acknowledgement and escalation.

Source publisher and gateway snapshot callbacks remain owner trust boundaries: validate actual snapshot bytes, SHA-256, source/generation/cursor and authenticated installation receipts independently. CI Redis and ephemeral runner volumes do not close these gates. No public endpoint, Firebase project, Redis host or production storage has been provisioned.

## 6. Indicator reconciliation

No indicator calculation, data contract, hook, chart renderer, chart UI, Footprint/Heatmap or indicator-test source changed. No indicator progress is awarded. Full current matrix:

| Study | Status | First valid output | Main remaining work |
|---|---|---:|---|
| SMA20 | 🟨 Foundation | index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | index 19 | Overlay, toggle, legend/value, stale clearing, render/lifecycle tests |
| RSI14 Wilder | 🟨 Foundation | index 14 | 0–100 pane, 30/70 guides, toggle, legend/value, stale clearing, render tests |
| MACD12/26/9 | 🟨 Foundation | MACD 25; signal/histogram 33 | Pane, lines, histogram, zero guide, toggle, legend, stale clearing, render tests |
| Bollinger20,2 | 🟨 Foundation | index 19 | Upper/middle/lower overlay, toggle, values, stale clearing, render tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, per-series isolation, renderer integration |
| Footprint | 🟧 Simulated/reference-gated | Synthetic only | User reference + reviewed blueprint, validated source contract, ON-only spaced clusters, readable bid/ask cells; OFF preserves ordinary spacing |
| Heatmap | 🟥 Not implemented | None | Zero-cost source feasibility, reference, data contract, reviewed blueprint, renderer/legend/scale/toggle/tests |
| Liquidation Maps | 🟥 Not implemented | None | Zero-cost source/formula feasibility, reference/blueprint, renderer/scale/legend/tests |

Shared invariants: warm-up values are null, never zero; align to source candle index; no future-candle repaint; clear stale series on symbol/venue/dataset/chart/timeframe changes; never fabricate liquidity or liquidation data. Footprint/Heatmap visual implementation remains blocked until user reference images are supplied and the scoped blueprint is reviewed. No aggregate indicator percentage without approved weights/denominator. Stage 1 project accounting is not indicator progress.

## 7. ZERO COST and next sequence

No paid service, deployment, cloud resource, account, production credential, device/Termux operation or main-branch modification. Preserve the green exact-head CI. Continue read-only ARM64 feasibility checks without provisioning. Keep owner-host gates open until real evidence is supplied. Treat 16-worker SQLite contention as a known observability risk and scope any architectural remedy separately.
