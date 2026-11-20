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
4. The test advances to one millisecond before the configured 100 ms minimum reconnect delay and confirms no second attempt has started.
5. At exactly 100 ms, the supervisor retries, obtains a fresh ID token, and calls the HTTPS ticket endpoint again.
6. The second ticket request succeeds and only then is the WebSocket constructed.
7. The test stops the supervisor and cleans up timers.

The test verifies the endpoint receives the expected base URL and fresh token on both attempts. It uses deterministic fakes; it does not contact Firebase or a public backend.

No production WebSocket code, auth protocol, reconnect policy, dependencies, or provider settings changed.

## 3. Validation boundary

The exact resulting commit triggers Automated Tests/Build, CodeQL, and Full Git History Secret Audit. These workflows must all conclude SUCCESS before the batch is declared CI-green. Existing passing evidence from Batch 62J-38 is not substituted for exact-head validation.

## 4. Gate 10 reconciliation

- Gate 25/36: automated WebSocket E matrix is complete for its defined CI scope; owner-host Redis TLS/ACL and public WSS/browser/Android acceptance remain open.
- Gate 30: repository-side SQLite restore-drill coverage is strong; actual owner Android database path and fresh-path restore acceptance remain external.
- Gate 38: bounded process-local metrics and sanitized scrape foundation exist; production dashboard, multi-replica aggregation, retention and host disk-pressure acceptance remain open.
- Gate 39: durable outbox/retry and sanitized local operator reporting exist; bounded FCM process isolation is still only a reviewed proposal, and production incident acknowledgement/escalation is not proven.

Gate 10 remains **10/10 🟧 ORANGE / 0 CLOSED**. No external host/device acceptance is inferred from CI.

## 5. Complete indicator dashboard

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

## 6. Project progress accounting

- Stage 1: **30/40 = 75% provisional**.
- Stages 2–6: unscored.
- Overall project percentage: unestablished pending approved M1–M8 weights.
- Indicator aggregate: unestablished pending approved weights/denominator.
- Gate 10: **10/10 ORANGE / 0 closed**.

## 7. Change boundary

Expected changed files:
- `src/services/ohlcvStreamSupervisor.test.ts`
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
- `docs/INDICATOR_PROGRESS_LEDGER.md`
- `docs/WORK_CYCLE_2026-11-20_BATCH62J39_WEBSOCKET_TICKET_ENDPOINT_RETRY_REGRESSION.md`

No deployment, preview publication, paid service, dependency change, Termux operation, or main branch modification.
