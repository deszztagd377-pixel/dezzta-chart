# DEZZTA CHART — Batch 62J-77
## Normalized SMA correction + WebSocket and Gate 10 checkpoint

**Date:** 21 November 2026  
**Source/test HEAD:** e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8  
**Branch:** phase-2/market-data-foundation

## 1. Defect and correction

SMA previously maintained a raw rolling sum. That can overflow before division even though the mean is representable. For two inputs equal to Number.MAX_VALUE, the raw sum becomes Infinity, but their arithmetic mean is still Number.MAX_VALUE.

The corrected implementation normalizes each rolling window by its maximum absolute input before summing. This preserves the mathematical mean for large same-sign and cancellation cases while retaining source-index alignment and warm-up nulls.

Regression tests include:
- [MAX_VALUE, MAX_VALUE] -> finite MAX_VALUE mean.
- [MAX_VALUE, MAX_VALUE, -MAX_VALUE] -> finite normalized mean near 1/3 of MAX_VALUE.
- A sliding two-value window over large positive/negative values -> MAX_VALUE, zero and -MAX_VALUE at the expected indices.

The first CI attempt failed because the old test still required SMA to throw and a huge-magnitude assertion used an inappropriate absolute tolerance. The test contract was corrected; no failing artifact was left as the branch head.

**Performance note:** this robust implementation is O(N × P), where N is bar count and P is period. For fixed SMA20 this is 20 window values per bar. If the app later exposes arbitrary large SMA periods, replace it with a separately benchmarked O(N) scaled rolling algorithm before shipping that option.

## 2. Exact-head CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829) | SUCCESS |
| CodeQL | [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826) | SUCCESS |
| Full Git History Secret Audit | [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841) | SUCCESS |
| Android debug APK build | [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773) | SUCCESS |

- Frontend: **253/253 tests across 29 files**.
- Backend: **1,249 passed in 48.11 seconds**.
- Frontend build and source/bundle secret scans passed.
- npm audit: 0 vulnerabilities; backend dependency audit: no known vulnerabilities.
- Bounded SQLite outbox benchmark, backend container build, shared Redis guard/persistent-volume smoke, Trivy image scan and report export/upload all completed.
- Android debug APK artifact ID 14696311954, size 3,877,454 bytes, expires 28 November 2026. SHA-256: cc7288ac77fa0c28f2cfeebba7f9703003f15a970b1575618e1998548887ed7a. CI build integrity is not physical-device acceptance.

## 3. WebSocket production acceptance

Repository-side WebSocket snapshot/replay/live handoff, durable cursor ordering, slow-consumer overflow/resnapshot behavior, exact-series identity isolation, Redis replica apply-before-ACK and CI failure-matrix scope remain complete for their defined automated scope.

Production acceptance is still blocked by a real external dependency: there is no active owner-controlled backend host and no public HTTPS/WSS endpoint. Production Redis TLS/ACL, verified snapshot installation receipts, durable host storage, backups, certificate renewal and real browser/Android WebView testing cannot be demonstrated from GitHub CI. The APK is not a substitute for a reachable server. Do not mark production acceptance complete or fabricate host evidence.

## 4. Gate 10 / Gate 31 / Gate 38

- Gate 10: **0/10 formally closed**.
- 🟨🟩 host/owner-verification-only: Gates 8, 30, 34, 35 and 39.
- 🟧 further integration: Gates 20, 25, 31, 36 and 38.
- Gate 31: local AES-256-GCM/PBKDF2 backup support exists; separate off-host destination and independent recovery-key custody remain absent.
- Gate 38: bounded process-local HTTP metrics and local SQLite incident journal exist; central collector/dashboard, cross-worker aggregation, WebSocket metrics, retention/rotation and independent operator notification remain absent.

## 5. Indicator ledger

SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared indicator hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥. The numerical correction improves SMA calculation correctness only. No overlay/pane/toggle/legend renderer completion is claimed. Full formulas, warm-up indices, invariants and remaining work are in docs/INDICATOR_PROGRESS_LEDGER.md.

## 6. Project accounting and cost

Stage 1: 30/40 criteria = **75% provisional**. Stages 2–6 and overall percentage remain unscored because approved aggregate weights/denominators are absent. ZERO COST: no paid hosting, deployment, Vercel/Cloudflare operation, production credentials, Termux/device operation or main branch modification.
