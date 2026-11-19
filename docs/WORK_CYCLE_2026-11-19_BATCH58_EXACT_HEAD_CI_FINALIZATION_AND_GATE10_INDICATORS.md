

# BATCH 58 — Post-commit exact-head CI closure and Gate 10/indicator reconciliation

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Verified parent HEAD:** `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`  
**Cost:** ZERO COST • **Deployments:** none • **Termux:** not required • `main`: untouched

## 1. Exact-head CI completion for Batch 57 documentation commit

The push-triggered workflows for exact HEAD `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d` have now completed:

| Workflow | Run | Final result |
|---|---:|---|
| Automated Tests + Build | [44482698128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44482698128) | SUCCESS |
| CodeQL Security Analysis | [44482698127](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44482698127) | SUCCESS |
| Full Git History Secret Audit | [44482698387](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44482698387) | SUCCESS |

Automated test job completed successfully. Frontend Vitest reports **28 test files passed**; backend pytest reports **1,040 passed in 34.00 seconds**. Frontend npm audit reports **0 vulnerabilities**; backend dependency audit reports **no known vulnerabilities**. The exact-head workflow completed successfully, including the configured backend/container and build checks. CodeQL and full-history secret audit are successful at the same SHA.

**Scope correction:** Android debug APK CI success documented for source HEAD `66c8a6741b1abe4d1e89ef0d5ad6ce0abb72a77d` is parent-baseline evidence, not an Android build run for documentation-only HEAD `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`. Do not report it as a fourth workflow on `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`.

## 2. WebSocket Batch 56C disposition

The source-level lifecycle hardening remains validated by frontend/backend regression coverage and exact-head CI on the source baseline. No newly confirmed repository-only blocker was found in this review. Do not make speculative changes to the stable close/reconnect state machine.

Gate 36 remains OPEN until independently observed public authenticated WSS upgrade, real Firebase project token-state E2E, Android WebView foreground/background behavior, 330-second session attribution, and cross-instance fan-out are recorded. The synthetic POC is not production acceptance. No deployment was initiated to manufacture evidence.

## 3. Gate 10 acceptance register — unchanged

**Formal closure: 0/10. Open: 10/10.**

| Gate | Internal repository evidence | External/owner acceptance still required |
|---:|---|---|
| 8 | Configuration and runtime code | Owner-host secret injection, protected mounts, runtime log/readback |
| 20 | Single-use HTTPS ticket endpoint and WSS renewal | Real Firebase valid/expired/revoked/wrong-project E2E |
| 25 | Atomic Redis ticket consumption and ACL tests | Independent owner Redis, multi-instance and outage drill |
| 30 | SQLite backup/restore implementation and CI smoke | Restore against actual owner-controlled database |
| 31 | Local encryption/snapshot/restore helpers | Zero-cost off-host copy, separate key custody, retention and off-host restore |
| 34 | Container persistent-volume and restart smoke | Owner-host volume, restart and disk-pressure evidence |
| 35 | HTTPS/WSS configuration source | Public ingress, certificate renewal and external scan |
| 36 | Ticket protocol and lifecycle regression suite | Public WSS, Android WebView, 330-second attribution, cross-instance fan-out |
| 38 | Local observability components | Durable cross-instance collector, retention and protected access |
| 39 | Local alert/incident components | Named operator, escalation route and acknowledgement drill |

## 4. Indicator progress — full technical ledger

The five calculation foundations are implemented and unit-tested. This does not mean the user-facing indicators are complete. No visual indicator UI was added in this batch because Stage 1 remains active and Stage 4 implementation is gated by the approved roadmap.

| Indicator | Formula/data contract | Calculation readiness | Visible UI / acceptance |
|---|---|---|---|
| SMA 20 | Rolling arithmetic mean of 20 closes; first valid index 19 | 🟢 Foundation + tests | 🟡 Overlay, toggle, legend, latest value and render/lifecycle tests pending |
| EMA 20 | SMA-seeded EMA; first valid index 19 | 🟢 Foundation + tests | 🟡 Overlay, toggle, legend, latest value and render/lifecycle tests pending |
| RSI 14 Wilder | Wilder-smoothed average gain/loss; first valid index 14 | 🟢 Foundation + tests | 🟡 Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle tests pending |
| MACD 12/26/9 | EMA12−EMA26; MACD first valid index 25; signal/histogram index 33 | 🟢 Foundation + tests | 🟡 Dedicated pane, signal line, histogram, zero guide and lifecycle tests pending |
| Bollinger 20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | 🟢 Foundation + tests | 🟡 Three-line overlay, fill, toggle, legend and lifecycle tests pending |
| Shared `useMarketIndicators()` | Validated non-empty backend snapshot; no DEMO fallback | 🟡 Hook foundation | 🟡 Visible controls and stale-series clearing on symbol/timeframe changes pending |
| Footprint | Bounded deterministic offline simulation only | 🟡 Simulated foundation | 🟡 Reference image + approved blueprint + dedicated ON-only cluster layout required |
| Heatmap | No verified implementation | 🔴 Not implemented | 🔴 Reference image + approved blueprint + data/render/test implementation required |
| Liquidation Maps | No verified implementation | 🔴 Not implemented | 🔴 Reference image + approved blueprint + data/render/test implementation required |

### Formula and integrity checks

- SMA 20: arithmetic mean over exactly 20 valid closes; warm-up slots remain null.
- EMA 20: initial SMA seed followed by α = 2/(20+1); warm-up slots remain null.
- RSI 14: Wilder smoothing, aligned to source candle indexes; flat-series handling must remain deterministic.
- MACD 12/26/9: EMA12 minus EMA26; signal EMA9 begins only after nine valid MACD values; histogram is MACD minus signal.
- Bollinger 20,2: population standard deviation, divisor 20; upper/lower bands are mean ± 2σ.
- Every output must preserve candle-index alignment and use null during warm-up; no fabricated values or demo fallback.
- The existing unit-test coverage validates formula behavior against fixtures, not live provider data quality or visible chart integration.

### Visual constraints and feature gate

- Footprint OFF must preserve ordinary candlestick layout and normal spacing.
- Only explicit Footprint ON may switch to the dedicated spaced-candle/cluster layout.
- Footprint and Heatmap reference images must be supplied by the owner before visual implementation; Liquidation Maps also require an approved scoped visual/data blueprint.
- Do not begin Stage 4 UI expansion during Stage 1. Keep the existing roadmap gate and require blueprint review before major implementation.

## 5. Project progress accounting

- Stage 1: **75% provisional — 30/40 criteria; 300/400 ticks**. No increase awarded by this CI/documentation batch.
- Gate 10: **0/10 formally closed; 10 OPEN**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** pending approved M1–M8 weights and criterion mapping. Historical 20.9% remains historical only.
- CI exact HEAD `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`: **3/3 workflows PASS** (Automated Tests, CodeQL, Full Git History Secret Audit).
- ZERO COST maintained; no Vercel/Cloudflare deployment, no paid service, no billing change, no production promotion, no Termux action, and no `main` modification.

## 6. Next multi-gate work sequence

1. Gate 20/25: prepare owner-controlled Firebase/Redis acceptance evidence matrix; no mock is accepted as production proof.
2. Gate 36: retain stable source; run public WSS and WebView acceptance only when existing deployment/runtime access permits without creating a paid or quota-consuming deployment.
3. Gate 30/31/34: consolidate restore, key custody, off-host retention and volume acceptance into one evidence pack. Do not assume an off-host free destination exists.
4. Gate 8/35: verify existing host configuration/readback before considering any deployment.
5. Gate 38/39: specify durable collector retention, protected access and incident acknowledgement evidence.
6. Keep indicator UI parked; preserve calculations and the full readiness ledger until Stage 4 authorization.

**Batch 58 disposition:** exact-head CI closed successfully. No source-code change was justified by the inspected evidence; no gate was falsely closed. Documentation/dashboard are refreshed to reflect final CI state.
