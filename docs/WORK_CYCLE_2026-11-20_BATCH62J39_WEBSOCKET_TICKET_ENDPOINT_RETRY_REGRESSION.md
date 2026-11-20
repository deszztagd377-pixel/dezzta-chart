# Batch 62J-39 — WebSocket ticket-endpoint retry regression

**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Starting HEAD:** `5bf56f04e499962a80720470f5dc6def2e263bbd`  
**Scope:** WebSocket ticket request failure/reconnect acceptance, Gate 10 evidence reconciliation and indicator ledger maintenance. ZERO COST.

## 1. Gap identified

Batch 62J-38 introduced a 10,000 ms abortable HTTPS ticket request deadline and tested timeout before response headers and while reading the JSON body. The supervisor already had a regression test for a transient Firebase ID-token-provider failure, but no isolated test demonstrated the next boundary: a failure from the HTTPS ticket endpoint itself.

These are distinct failure points:
- ID-token acquisition may fail before the HTTP request begins.
- Ticket endpoint fetch/body processing may fail after a valid ID token is obtained.
- A successful ticket response is required before constructing the WebSocket.

## 2. Change

Added one regression test to `src/services/ohlcvStreamSupervisor.test.ts`:

1. First `requestWebSocketTicket` invocation rejects with a simulated ticket-request timeout.
2. No WebSocket is constructed for the failed attempt.
3. Supervisor transitions to `reconnecting`.
4. The test advances to one millisecond before the deterministic 50 ms initial reconnect delay (100 ms minimum × 0.5 jitter because random() returns 0) and confirms no second attempt has started.
5. At exactly 100 ms, the supervisor retries, obtains a fresh ID token, and calls the HTTPS ticket endpoint again.
6. The second ticket request succeeds and only then is the WebSocket constructed.
7. The test stops the supervisor and cleans up timers.

The test verifies the endpoint receives the expected base URL and fresh token on both attempts. It uses deterministic fakes; it does not contact Firebase or a public backend.

No production WebSocket code, auth protocol, reconnect policy, dependencies, or provider settings changed.

## 3. First CI finding and correction

The first exact-head run exposed an incorrect test expectation, not a runtime defect. The supervisor uses bounded jitter: `delay = floor(exponential × (0.5 + random × 0.5))`. With `minReconnectDelayMs = 100` and deterministic `random() = 0`, the first delay is `100 × 0.5 = 50 ms`, not 100 ms. The regression test initially advanced 99 ms and correctly observed that the retry had already occurred. The assertion was corrected to check at 49 ms and then at 50 ms. This preserves the production backoff policy and tests its exact deterministic lower-bound behavior.

## 4. Exact-head validation

The first run on the initial test commit exposed the test-only jitter timing assumption described above. After correcting the test to 49 ms / 50 ms, exact source/test HEAD `13d0b48adf8fbd040b22689e83160b2945f07a5c` passed all workflows:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests & Build | [44719780403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44719780403) | SUCCESS |
| CodeQL JavaScript/TypeScript + Python | [44719780163](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44719780163) | SUCCESS |
| Full Git History Secret Audit | [44719780242](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44719780242) | SUCCESS |
| Android debug APK build | [44719780305](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44719780305) | SUCCESS; preview publication skipped |

- Frontend: **243 tests passed across 29 files**.
- Backend: **1,172 passed, 6 warnings in 43.42 seconds**.
- Frontend production build, frontend secret scans, backend dependency audit: SUCCESS.
- Backend container image build: SUCCESS.
- Shared Redis guard + persistent-volume smoke test: SUCCESS.
- Container image scan and vulnerability-report export: SUCCESS.
- Android debug APK assembled, SHA-256 calculated and uploaded as a short-lived CI artifact; no preview release was published.

The successful exact-head result verifies the retry regression and the unchanged repository suite. It does not prove public WSS, real Firebase project behavior, or owner-device acceptance.

## 5. Gate 10 reconciliation

- Gate 25/36: automated WebSocket E matrix is complete for its defined CI scope; owner-host Redis TLS/ACL and public WSS/browser/Android acceptance remain open.
- Gate 30: repository-side SQLite restore-drill coverage is strong; actual owner Android database path and fresh-path restore acceptance remain external.
- Gate 38: bounded process-local metrics and sanitized scrape foundation exist; production dashboard, multi-replica aggregation, retention and host disk-pressure acceptance remain open.
- Gate 39: durable outbox/retry and sanitized local operator reporting exist; bounded FCM process isolation is still only a reviewed proposal, and production incident acknowledgement/escalation is not proven.

Gate 10 remains **10/10 🟧 ORANGE / 0 CLOSED**. No external host/device acceptance is inferred from CI.

## 6. Complete indicator dashboard

| Indicator | State | Verified calculation/data foundation | First valid output | Remaining |
|---|---|---|---:|---|
| SMA 20 | 🟨 | Rolling arithmetic mean | Candle 19 | Overlay, toggle, legend/value, stale clearing, render tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21 | Candle 19 | Overlay, toggle, legend/value, stale clearing, render tests |
| RSI 14 | 🟨 | Wilder-smoothed gains/losses | Candle 14 | 0–100 pane, 30/70 guides, toggle, legend, render tests |
| MACD 12/26/9 | 🟨 | EMA12−EMA26; EMA9 signal; histogram difference | MACD 25; signal/histogram 33 | Dedicated pane, lines, histogram, zero guide, toggle, render tests |
| Bollinger 20,2 | 🟨 | 20-close mean ± 2 population standard deviations | Candle 19 | Three-line overlay, toggle, legend/value, stale clearing |
| Shared Indicator Hook | 🟨 | Validated backend snapshot; no DEMO fallback | Snapshot-dependent | Active chart binding, loading/error, stale clearing, isolation |
| Footprint | 🟧 | SIMULATED educational accumulator only | Candle/price-level dependent | Owner reference, reviewed blueprint, ON-only spaced cluster renderer |
| Heatmap | 🟥 | No implementation verified | N/A | Owner reference, blueprint, validated source/calculation, renderer |
| Liquidation Maps | 🟥 | No validated data/calculation contract | N/A | Data-source feasibility, reference/blueprint, calculation, renderer |

No indicator formula or UI changed. No indicator percentage is invented.

## 7. Project progress accounting

- Stage 1: **30/40 = 75% provisional**.
- Stages 2–6: unscored.
- Overall project percentage: unestablished pending approved M1–M8 weights.
- Indicator aggregate: unestablished pending approved weights/denominator.
- Gate 10: **10/10 ORANGE / 0 closed**.

## 8. Change boundary

Changed files:
- `src/services/ohlcvStreamSupervisor.test.ts`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/INDICATOR_PROGRESS_LEDGER.md`
- `docs/WORK_CYCLE_2026-11-20_BATCH62J39_WEBSOCKET_TICKET_ENDPOINT_RETRY_REGRESSION.md` (this report)

No deployment, preview publication, paid service, dependency change, Termux operation, or main branch modification.
