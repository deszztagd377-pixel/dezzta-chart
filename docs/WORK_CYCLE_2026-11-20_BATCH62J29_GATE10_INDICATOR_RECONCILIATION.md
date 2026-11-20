# Batch 62J-29 — Exact-head CI, Gate 10 and indicator reconciliation

**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent / audited HEAD:** `ea3626cd9e174d0f9a06af2b0fe2550c830e0559`  
**Scope:** read-only reconciliation of latest CI, WebSocket E boundary, Gate 10 evidence and complete indicator dashboard. No runtime behavior changed.

## 1. Exact-head CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44705774297](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774297) | SUCCESS |
| CodeQL (JavaScript/TypeScript + Python) | [44705774202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774202) | SUCCESS |
| Full Git History Secret Audit | [44705774189](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44705774189) | SUCCESS |

Backend pytest: **1,164 passed**. Frontend tests/build, dependency checks, backend container build and container smoke completed successfully.

## 2. WebSocket failure matrix E

The current dual-ASGI process test injects a single `ConnectionError` at each Redis client's `xreadgroup` method boundary. Both workers recover, both WebSocket clients receive cursor 1, reconnect replay returns cursor 1, one process restarts with its durable SQLite replica, and both replicas converge at cursor 2.

This is not a real Redis server shutdown or TCP network partition. The following remain open:
1. Real TCP/network interruption affecting both live gateway processes, followed by reconnection and cursor parity.
2. Coordinated snapshot-generation replacement across both replica databases/processes, including generation-scoped group switch and next-cursor parity.
3. Production snapshot distribution and rotation contract.
4. Production Redis TLS, least-privilege ACL and credential rotation.
5. Browser and Android WebSocket acceptance, including platform/runtime behavior.
6. Retention/trim policy, authorized cleanup and operational recovery runbook/drill.

A–D remain implemented and repository/CI-verified for the explicit opt-in replica path. E remains **PARTIALLY VERIFIED**. No production readiness claim is made.

## 3. Gate 10 reconciliation

| Gate | Status | Evidence still required |
|---:|---|---|
| 8 | 🟧 OPEN | Actual host secret injection, restrictive permissions and runtime leakage review |
| 20 | 🟧 OPEN | Real no-billing Firebase sign-in, revocation, entitlement and browser/Android path |
| 25 | 🟧 OPEN | Owner-controlled Redis TLS/ACL, persistence, outage and recovery |
| 30 | 🟧 OPEN | Restore drill on the intended owner-controlled target |
| 31 | 🟧 OPEN | Off-host encrypted artifact and separate recovery-key custody |
| 34 | 🟧 OPEN | Actual host volume, restart, disk-pressure and recovery evidence |
| 35 | 🟧 OPEN | Owner-host HTTPS endpoint and certificate validation |
| 36 | 🟧 OPEN | Browser/Android WSS, platform lifetime, effective runtime config and cross-instance proof |
| 38 | 🟧 OPEN | Protected host collector/dashboard, bounded retention and disk-pressure evidence |
| 39 | 🟧 OPEN | Responsible adult operator, verified escalation and observed acknowledgement/recovery drill |

**10/10 ORANGE; 0/10 formally closed.** CI and documentation cannot supply owner-host/provider/device/operator evidence. Where the required control cannot be safely met at zero incremental cost, it remains deferred/open; no paid plan or weakened security control is introduced.

## 4. Complete indicator progress

| Indicator | Status | Calculation/data foundation | Remaining visual acceptance |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling arithmetic mean; first valid index 19 | Overlay, toggle, legend/current value, stale clearing and render tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/current value, stale clearing and render tests |
| RSI 14 Wilder | 🟨 | Wilder-smoothed gains/losses; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing and render tests |
| MACD 12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Dedicated pane, two lines, histogram, zero guide, toggle and render tests |
| Bollinger 20,2 | 🟨 | SMA20 ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, legend/current values, stale clearing and render tests |
| Shared indicator hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Active chart identity/timeframe binding, loading/error UI and cross-series isolation |
| Footprint | 🟧 | Deterministic educational aggregation, explicitly SIMULATED | Owner reference + reviewed blueprint; explicit ON-only spaced cluster layout; OFF preserves normal candles |
| Heatmap | 🟥 | No verified implementation | Owner reference, reviewed blueprint, data/calculation contract, renderer and tests |
| Liquidation Maps | 🟥 | No validated source/calculation contract | Source feasibility, reference/blueprint, calculations, renderer and tests |

No indicator percentage is fabricated. Calculation foundations are not equivalent to chart-visible features. Stage 4 remains parked while Stage 1 is active.

## 5. Project accounting and constraints

- Stage 1: **30/40 = 300/400 = 75% provisional**.
- Gate 10: **10/10 ORANGE; 0/10 closed**.
- Stages 2–6: not scored.
- Overall project percentage: not established; M1–M8 weights remain unapproved.
- ZERO COST: no paid service, hosting, data, deployment or billing action.
- Termux: not needed for this CI/documentation cycle. Existing Termux readiness record still marks native backend/encryption acceptance incomplete; no device installation command is required here.
- `main` remains untouched.

## 6. Changed files in this documentation-only commit

- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` — exact-head CI, E boundary, Gate 10 and colored dashboard refresh.
- `docs/INDICATOR_PROGRESS_LEDGER.md` — latest exact-head evidence boundary; indicator statuses unchanged.
- `docs/WORK_CYCLE_2026-11-20_BATCH62J29_GATE10_INDICATOR_RECONCILIATION.md` — this report.

No backend/frontend runtime source or tests were changed in Batch 62J-29.
