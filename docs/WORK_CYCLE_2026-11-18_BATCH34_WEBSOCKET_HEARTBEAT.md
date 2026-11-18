# DEZZTA CHART — Batch 34: WebSocket idle-heartbeat correction

**Date:** 18 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Parent audited HEAD:** `09c2a651ccd0999ea17118cbdbcef868de7ccc45`  
**Scope:** client/server heartbeat contract, regression tests, Gate 36 acceptance boundary, progress-indicator correction  
**Cost:** ZERO COST  
**Deployment:** none  
**Main:** untouched

## 1. Confirmed defect

The backend `/ws/market-data` receive loop accepts the literal text frame `ping`, rate-limits it to at most 20 messages per 10-second window, and responds with JSON `market_data.pong`. The production frontend transport previously handled incoming `market_data.pong` but never sent the matching client ping frame.

That left the connection without an application-level idle heartbeat. This is a source-level protocol gap, not proof that every idle connection had already been dropped.

## 2. Fix prepared

- Add a default 20,000 ms heartbeat interval after a validated snapshot or successful replay completion.
- Send the exact text frame `ping` required by the backend protocol.
- Require `market_data.pong` within 10,000 ms; timeout fails the transport closed so the existing supervisor can reconnect with a fresh identity token and durable cursor.
- Validate custom interval/timeout bounds; interval must be at least 1,000 ms and timeout must be at least 1,000 ms and shorter than the interval.
- Clear heartbeat and pong timers on protocol failure, remote close, and explicit client stop.
- Add regression tests for ping transmission, pong acknowledgement, timeout failure, and timer cleanup.
- Update the WebSocket client contract documentation.

## 3. Rate and timing calculation

Backend allowance: 20 pings per 10 seconds. Default client cadence: 1 ping per 20 seconds.

`20 seconds / 10 seconds = 2` server windows per client ping, or at most 0.5 ping/10 seconds in steady state. This is 2.5% of the server's 20-ping/10-second ceiling. A 10-second pong deadline is half the send interval; the current transport fails closed on a missed pong and delegates recovery to the supervisor.

## 4. Gate 36 status

The source-level client heartbeat gap is addressed by this candidate. The following remain external acceptance items and are not claimed complete:

- real public WSS Upgrade and ping/pong on the intended host;
- Android WebView acceptance and foreground/background transition checks;
- owner-observed 330-second session and attribution of the close event;
- effective Fluid Compute configuration read-back;
- cross-instance live fan-out (the current hub queues remain process-local).

No deployment was performed. The existing Vercel synthetic-only POC is not promoted as production proof.

## 5. Exact-head CI baseline before this candidate

For parent `09c2a651ccd0999ea17118cbdbcef868de7ccc45`:
- Automated Tests run [44308452242](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44308452242): **FAILURE** only at final frontend dependency-audit enforcement.
- CodeQL [44308451979](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44308451979): **SUCCESS**.
- Full Git History Secret Audit [44308452071](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44308452071): **SUCCESS**.

The final audit blocker is the five High dependency paths through dev-only `picomatch@4.0.7` (GHSA-fc5q-39xc-vjpf / CVE-2026-112366). The advisory currently provides no patched version. Do not downgrade Vite, force-install, hand-patch, add speculative overrides, suppress, or waive the finding. The candidate's own exact-head CI result must be read after the commit is pushed.

## 6. Progress accounting — unchanged

- Stage 1: **75% provisional** = 300/400 ticks = 30/40 criteria.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; approved M1–M8 weights and criterion mapping are still absent.
- Historical overall checkpoint: **20.9% — historical only, not recomputed**.

No progress tick or gate closure is awarded by this client fix alone. Gate 36 remains open until external acceptance evidence is collected.

## 7. Zero-cost and owner-device boundary

No paid broker, provider, database, host, storage, Vercel deployment, Cloudflare resource, plan change, or publication action is introduced. Termux is not required for this source-level change or GitHub CI. If a future Android-native WSS acceptance test genuinely requires Termux, the reason and exact commands will be explained before requesting any owner action.

## 8. Files in this batch

- `src/services/ohlcvWebSocketClient.ts` — client heartbeat and cleanup.
- `src/services/ohlcvWebSocketClient.test.ts` — heartbeat regression coverage.
- `docs/OHLCV_WEBSOCKET_CLIENT.md` — protocol and test boundary.
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` — corrected exact-head CI references and latest progress state.
- `docs/assets/project-progress-dashboard-batch34.svg` — colored dashboard, same conservative progress accounting.
