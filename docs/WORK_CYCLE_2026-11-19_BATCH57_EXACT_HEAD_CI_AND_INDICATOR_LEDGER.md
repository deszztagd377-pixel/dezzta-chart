# BATCH 57 — Exact-head CI closure and indicator acceptance reconciliation

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Verified source HEAD:** `66c8a6741b1abe4d1e89ef0d5ad6ce0abb72a77d`  
**Cost:** ZERO COST • **Deployments:** none • **Termux:** not required • `main`: untouched

## 1. Exact-head CI evidence

All four push-triggered workflows associated with the exact source HEAD completed successfully:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44475945219](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945219) | SUCCESS |
| CodeQL Python + JavaScript/TypeScript | [44475945132](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945132) | SUCCESS |
| Full Git History Secret Audit | [44475945214](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945214) | SUCCESS |
| Android debug APK CI build | [44475945152](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945152) | SUCCESS |

Automated Tests job: all 32 steps succeeded. Frontend Vitest: **236 passed across 28 files**. Backend pytest: **1,040 passed in 34.00 seconds**. Frontend `npm audit --audit-level=high`: **0 vulnerabilities**. Backend dependency audit: **no known vulnerabilities**. Frontend source credential scan checked 78 files; bundle scan checked 5 files. Backend container smoke verified health, scoped Redis ACL authentication, Redis AOF persistence across restart, fail-closed behavior during Redis outage, reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection. Trivy scan/report completed and the report was uploaded; this does not substitute for production-host acceptance.

The Android workflow built the debug APK in CI. No APK was published or installed on the owner's device.

## 2. WebSocket Batch 56C — source and CI disposition

Verified changes at this HEAD:
- WebSocket principal is initialized before the authentication handshake wait; the finally path releases the global lease with a null subject when no principal was established.
- Missed periodic ticket renewal closes with transient code 1013, allowing a fresh ticket on reconnect; actual Firebase HTTP 401 remains terminal.
- Initial HTTPS ticket endpoint 401 stops the supervisor rather than retrying indefinitely.
- Frontend regression covers terminal initial-ticket 401; backend regression covers lease release when the initial auth frame times out.
- The supervisor retains bounded reconnect behavior and obtains a fresh Firebase ID token/ticket on each new connection attempt.

**Disposition:** source-level Batch 56C and exact-head automated CI are PASS. Gate 36 remains OPEN because public authenticated WSS, Firebase production valid/expired/revoked/wrong-project E2E, Android WebView foreground/background, 330-second attribution, and cross-instance fan-out have not been externally demonstrated. The synthetic POC remains synthetic-only.

## 3. Gate 10 — formal status unchanged

**0/10 formally closed; 10/10 remain OPEN.** CI success is supporting repository evidence, not owner-host acceptance.

| Gate | Internal evidence | Remaining acceptance blocker |
|---:|---|---|
| 8 | Repository/runtime configuration | Owner-host secret injection, protected mounts, runtime log/readback |
| 20 | HTTPS single-use ticket endpoint and WSS renewal | Real Firebase project valid/expired/revoked/wrong-project E2E |
| 25 | Redis atomic ticket consumption and scoped ACL | Independent owner Redis, multi-instance and outage drill |
| 30 | SQLite backup/restore implementation and CI tests | Actual owner target-database restore drill |
| 31 | Authenticated encryption and restore tests | Zero-cost off-host copy, separate key custody, retention and off-host restore |
| 34 | Container volume and restart smoke | Owner-host volume/restart/disk-pressure evidence |
| 35 | HTTPS/WSS configuration source | Public ingress, certificate renewal and external scan |
| 36 | Ticket protocol and lifecycle source tests | Browser/WebView, 330-second attribution and cross-instance fan-out |
| 38 | Local metrics/alert components | Durable cross-instance collector, retention and protected access |
| 39 | Local incident reporting components | Named operator, escalation channel and acknowledgement drill |

## 4. Technical indicator progress ledger

This is a capability ledger, not an invented completion percentage. Stage 1 remains the active official stage. Visible indicator controls, overlays and oscillator panes remain Stage 4 work; the existing UI blueprint is parked and implementation authorization is not granted during Stage 1.

| Indicator / component | Calculation or data foundation | Visible integration / acceptance | State |
|---|---|---|---|
| SMA 20 | Close-based rolling mean; first value at index 19; unit tests | Overlay, toggle, legend/current value, identity/timeframe clearing and render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; first value at index 19; unit tests | Overlay, toggle, legend/current value, identity/timeframe clearing and render tests | 🟨 Foundation |
| RSI 14 Wilder | Wilder-smoothed gains/losses; first value at index 14; flat/rising edge tests | Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | MACD starts index 25; signal/histogram start index 33; warm-up tests | Dedicated pane, MACD/signal lines, histogram, zero guide and render tests | 🟨 Foundation |
| Bollinger 20,2 | Population standard deviation; first value at index 19; unit tests | Upper/middle/lower overlay, toggle, legend/current value and render tests | 🟨 Foundation |
| Shared `useMarketIndicators()` | Exact validated backend snapshot only; DEMO/loading/unavailable/error produce null | Visible controls and immediate stale-series clearing on identity change | 🟨 Foundation |
| Footprint | Bounded deterministic simulation, explicitly labelled `SIMULATED` | Owner reference image, reviewed blueprint, ON-only spaced cluster renderer | 🟨 Gated |
| Heatmap | No implementation verified | Reference image, reviewed blueprint, source contract, calculations, rendering and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Reference image, reviewed blueprint, source contract, calculations, rendering and tests | 🟥 Not implemented |

### Calculation contract

- SMA 20 and EMA 20 use close values; EMA is seeded from the initial SMA window.
- RSI 14 uses Wilder smoothing. Its first output is at source index 14.
- MACD uses EMA 12 minus EMA 26; its first MACD value is at index 25 and signal/histogram first become available at index 33.
- Bollinger 20,2 uses population variance (division by period), with the first complete window at index 19.
- Warm-up values are null; outputs remain aligned to original candle indexes.
- The hook reads only non-empty validated backend bars in ready/degraded state; no demo fallback is allowed.
- Current unit tests exercise all five calculations across 18 timeframe labels. This proves formula execution against fixture bars, not provider-backed data quality or visible timeframe integration.

### Visual/data integrity constraints

- Footprint OFF preserves ordinary candlestick layout and spacing.
- Only explicit Footprint ON may enable the dedicated spaced-candle/cluster layout.
- Footprint, Heatmap and Liquidation Maps visual work remains blocked on the owner's relevant reference image(s) and a reviewed scoped blueprint.
- Do not add visible indicator UI during Stage 1; preserve the Stage 4 roadmap gate.
- No indicator percentage credit is awarded from general CI, calculation tests, or documentation alone.

## 5. Progress accounting

- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks; this is not a final certification.
- Gate 10: **0/10 formally closed**, 10 OPEN.
- Stage 2–6: NOT SCORED.
- Overall project: **NOT ESTABLISHED**. Historical 20.9% is not a current weighted score.
- CI: exact-head automated tests, CodeQL, secret-history audit, and Android debug build all PASS.
- Deployment: none. Billing: none. Termux: not required. Main branch: untouched.

## 6. Next work cycle

1. Preserve Batch 56C source and use its exact-head CI as the current baseline.
2. Advance Gate 20/25 only through controlled Firebase and independent Redis acceptance evidence; do not claim production readiness from mocks.
3. Continue Gate 36 external runtime acceptance without creating another deployment merely to generate logs.
4. Batch Gate 30/31/34 evidence work around backup, key custody, and persistence; do not assume a free off-host destination exists.
5. Keep indicator UI parked until the official Stage 4 authorization gate. Continue only source/data-contract audit and documentation during Stage 1.

