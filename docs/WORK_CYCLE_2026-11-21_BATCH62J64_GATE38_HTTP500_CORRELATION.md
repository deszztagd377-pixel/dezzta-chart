# DEZZTA CHART — Work Cycle 62J-64
## Gate 38: HTTP 500 request-correlation and redaction hardening
**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source commit:** `fdf70fc71afd5603fa92f74931cfbd0afd47f7bb`  
**Test commit / source-test HEAD:** `54a319c9165a47b03a3ab02039e4bdeeae783e3a`

### Defect identified
The HTTP middleware recorded an unhandled exception as status class `5xx`, but discarded the request ID returned by the observation helper when re-raising. The resulting generic server-error response had no matching `X-Request-ID`, weakening operator correlation between a client failure and the bounded process-local metrics/log record.

### Change delivered
- On unhandled HTTP exceptions, middleware now stores the generated correlation ID in `request.state.request_id` before re-raising.
- A generic exception handler returns `{"detail":"Internal server error."}` and preserves the same `X-Request-ID`.
- The response applies `Cache-Control: private, no-store, max-age=0`, `Pragma: no-cache`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: no-referrer`.
- No raw exception text is returned. The existing metrics observation continues to use the route template and status class, not query strings, headers, client addresses or path parameter values.

### Regression test
Added `test_unhandled_http_error_keeps_request_id_and_redacts_sensitive_context` in `backend/tests/test_api.py`. It injects a controlled endpoint exception and checks:
1. Response status is 500 and body is exactly the generic error detail.
2. Response contains a 32-character request ID.
3. The private exception message is absent from the response.
4. The internal metrics snapshot contains exactly one GET / 5xx row for the test route.
5. The structured HTTP log contains the correlation ID but none of the query, Authorization, private-header-value or exception-message sentinels.

### Exact-head verification
- Automated Tests [44858630448](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44858630448): **SUCCESS** — frontend 247/247 tests across 29 files; backend **1,225 passed in 59.22 seconds**; all 33/33 workflow steps succeeded.
- CodeQL [44858630295](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44858630295): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44858630302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44858630302): **SUCCESS**.
- Backend container build, shared Redis guard/persistent-volume smoke, Trivy scan and vulnerability report export passed within the Automated Tests workflow.

### Gate and project accounting
- Gate 38 remains **🟧 OPEN**. CI does not prove owner-host firewall/reverse-proxy isolation, actual operator-token injection/rotation, collector/dashboard access, bounded host-log retention/rotation, disk-pressure recovery or production credential-redaction review. Metrics remain process-local, not durable cross-process telemetry.
- Gate 30's WAL-aware capacity-preflight source/test checkpoint `0afaa3af5f4b2fe4fdc9a9779dc36dbb16b88543` separately passed Automated Tests [44857959302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44857959302), CodeQL [44857959330](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44857959330) and Secret Audit [44857959338](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44857959338). Gate 30 remains open pending a real owner-host restore drill.
- Stage 1 remains **30/40 = 300/400 = 75% provisional**. No acceptance tick is awarded.
- Gate 10 remains **0/10 formally closed**: gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open.
- Overall project and aggregate indicator percentages remain unscored; M1–M8 and indicator acceptance weights are not approved.
- Indicator status unchanged: SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; shared hook 🟨; Footprint 🟧 SIMULATED/reference-gated; Heatmap 🟥; Liquidation Maps 🟥. No indicator implementation credit is awarded.
- ZERO COST. No deployment, paid service, Termux/device operation, production credentials, or `main` modification.
