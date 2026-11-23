# DEZZTA CHART — Batch 62J-184
## Concurrent ticket-consumption and cursor-serialization regression coverage

**Date:** 23 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Starting verified documentation HEAD:** `008edd4c5750e1f59645273ddcacd37e232fec44`  
**Protected branch:** `main` untouched  
**Cost:** ZERO COST; tests use the existing local Cloudflare Durable Object runtime in CI only.

## 1. Verified baseline before this cycle

The starting documentation HEAD had four exact-commit workflows completed successfully:
- Automated Tests: [45183609136](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45183609136) — SUCCESS.
- Full Git History Secret Audit: [45183609188](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45183609188) — SUCCESS.
- CodeQL Security Analysis: [45183609148](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45183609148) — SUCCESS.
- OCI ARM64 Image Readiness: [45183609312](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45183609312) — SUCCESS.

The automated workflow's Durable Object runtime suite previously contained six verified tests. This cycle adds four concurrency/lifecycle regressions. The baseline is not confused with the new test commits; new exact-HEAD CI is required.

## 2. Regression A — atomic single-use ticket under concurrent authentication

**Test:** `allows exactly one winner when two sockets race to consume the same ticket`

Scenario:
1. Issue one ticket bound to one synthetic series.
2. Open two independent WebSocket connections for that same series.
3. Install both message/close observers before sending either authentication frame.
4. Send the same ticket on both sockets without awaiting the first response.
5. Require exactly one socket to receive the authenticated snapshot.
6. Require the other socket to close because the ticket has already been consumed.

Acceptance proves the test exercises the race rather than a sequential replay. It validates the existing Durable Object storage-transaction contract; it does not introduce production Firebase authentication or a production ticket authority.

## 3. Regression B — concurrent duplicate cursor submissions

**Test:** `serializes concurrent duplicate cursor submissions before fan-out`

Scenario:
1. Authenticate one synthetic subscriber and install its update observer.
2. Submit sequence 51 twice concurrently for the same series.
3. Require exactly one HTTP 200 acceptance and one HTTP 409 `sequence_conflict`.
4. Require exactly one sequence-51 update to reach the subscriber.
5. Submit contiguous sequence 52 and require acceptance and delivery.

This verifies that competing writes cannot both advance the same cursor or fan out a duplicate. It supplements the existing sequential duplicate/gap test.

## 4. Regression C — multi-socket hibernation restoration

**Test:** `restores every authenticated socket attachment after Durable Object eviction`

- Open two authenticated sockets on one synthetic series.
- Evict the Durable Object instance.
- Restore the instance and require both serialized attachments to remain valid and bound to the same series/subject/watermark.
- Send independent ping frames and require both sockets to receive pong responses.

This extends the single-socket hibernation proof to multiple live owners and verifies neither connection is silently lost during instance eviction.

## 5. Regression D — authenticated socket versus authentication timeout alarm

**Test:** `does not expire an authenticated socket when the authentication alarm runs`

- Authenticate a socket successfully.
- Move only its test attachment's connection timestamp beyond the unauthenticated timeout.
- Schedule and execute the real Durable Object alarm.
- Require the authenticated connection to remain open and answer a subsequent ping.

This guards the lifecycle boundary: the authentication alarm must expire unauthenticated sockets only, never a valid authenticated session.

## 6. Scope and non-claims

Only `cloudflare/proof/worker.durable-object.runtime.mjs` changes in the source/test scope. The file now has four added runtime regressions over the previously verified six-case suite. No production FastAPI route, Databento adapter, provider credential, market-data source, Android app, indicator calculation, chart renderer, or hosting configuration changes.

The Worker continues to label every fixture as `synthetic_only_not_market_data`. The proof does not establish public WSS, live Firebase, real exchange data, provider subscription pooling, multi-host storage, or Android network handover.

## 7. Test accounting and CI gate

| Runtime behavior | Previous verified cases | Added in this cycle |
|---|---:|---:|
| Exact-series fan-out and isolation | 1 | 0 |
| Single-use ticket replay rejection | 1 | 0 |
| Hibernation / attachment restoration | 1 | 0 |
| Alarm expiry | 1 | 0 |
| Wrong-series ticket binding | 1 | 0 |
| Sequential duplicate/gap cursor handling | 1 | 0 |
| Concurrent ticket consumption | 0 | 1 |
| Concurrent duplicate cursor submission | 0 | 1 |
| **Total** | **6** | **2** |

The suite now defines ten runtime cases. **The four new cases are pending exact-HEAD CI until the Automated Tests workflow reports success.** Do not award accepted-test credit before that result.

## 8. Indicator and project progress impact

No indicator source, formula, numeric kernel, hook, chart binding, renderer, pane, setting, legend, or indicator-specific test changed. Indicator implementation credit for this batch is **zero**.

Indicator statuses remain:
- SMA20 🟨 Foundation.
- EMA20 🟨 Foundation.
- RSI14 Wilder 🟨 Foundation.
- MACD12/26/9 🟨 Foundation.
- Bollinger20,2 🟨 Foundation.
- Shared Indicator Hook 🟨 Foundation.
- Footprint 🟧 Synthetic educational prototype only.
- Heatmap 🟥 Not implemented.
- Liquidation Maps 🟥 Not implemented.

Preserve warm-up nulls, exact source-candle alignment, prefix causality/no future repaint, invalid/gapped-data rejection, and stale-output clearing on series identity changes. Footprint OFF retains ordinary candle spacing; explicit ON alone activates spaced clusters. Footprint and Heatmap visuals remain gated on user reference images and scoped blueprint review.

Project accounting remains unchanged:
- Stage 1: 30/40 = 75% provisional 🟨.
- Stage 2: not scored; provider-demand and production-source acceptance remain open.
- Stages 3–6: not scored.
- Gate 10: 0/10 external criteria formally closed 🟥.
- Overall project: **NOT SCORED**; no approved weighted denominator exists.
- Delivery target: **24 December 2026**, planning target only.

## 9. Next engineering boundary

The provider-demand gap must not be papered over with a disconnected reference counter. The current source audit still finds process/configuration-scoped provider startup and a fixed-symbol Databento adapter; recurring-zero-cost data rights and provider subscribe/unsubscribe semantics are not verified. Continue with contract/source research and isolated tests until a valid provider capability and reviewed implementation scope exist. Do not enable a paid provider or production deployment.
