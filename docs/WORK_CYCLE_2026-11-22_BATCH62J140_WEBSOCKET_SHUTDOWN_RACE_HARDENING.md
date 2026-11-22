# Batch 62J-140 — WebSocket shutdown and late-event race hardening

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Source/test HEAD: `90fd29cbf7d98ee80ff6ba477bc4f016ec729fd5`  
Scope: one source-backed WebSocket lifecycle correction, two regression tests, full Gate 36/25/38 and project/indicator reconciliation. ZERO COST.

## 1. Engineering finding and correction

During review of `src/services/ohlcvWebSocketClient.ts`, the ticket-renewal timer was found to launch an asynchronous renewal request. The success path already checked that the connection remained subscribed before sending a renewed ticket. The rejection path did not perform the equivalent lifecycle check before classifying the rejection as an authentication or transport failure.

If the client intentionally closed while renewal was pending, a late rejection could therefore invoke the error path after teardown. The supervisor ignored that callback once stopped, but the transport itself could still emit a misleading post-shutdown error to a direct consumer.

### Runtime correction

In the renewal request catch branch, the client now returns immediately when connection state is no longer `subscribed`. This makes both intentional close and other terminal lifecycle transitions suppress late renewal failures.

The correction:
- does not suppress errors while the connection is still subscribed;
- retains the existing 401 terminal-authentication behavior for an active connection;
- retains renewal ticket validation and acknowledgement timeout;
- does not change reconnect policy, authentication, authorization, ticket scope, or server behavior;
- does not add dependencies, schema changes, external services, or credentials.

Changed runtime file: `src/services/ohlcvWebSocketClient.ts`.

## 2. Regression tests added

1. `src/services/ohlcvWebSocketClient.test.ts` — `ignores a late ticket-renewal rejection after intentional connection close`.
   - Opens and authenticates a fake socket.
   - Completes a validated snapshot.
   - Holds ticket renewal pending.
   - Intentionally closes the connection.
   - Rejects the renewal request after close.
   - Asserts closed state, one normal close, and no false `onError` callback.

2. `src/services/ohlcvStreamSupervisor.test.ts` — `does not republish late snapshot or update messages after supervisor stop`.
   - Establishes a backend snapshot in the store.
   - Stops the supervisor and verifies the store enters the stopped/unavailable state.
   - Delivers late snapshot and update messages through the fake socket.
   - Asserts the stale messages do not repopulate the store.

Previously added in Batch 62J-139 and retained:
- Stop while ticket issuance is pending: no socket opens after late ticket resolution.
- Rapid offline/hidden/online/visible transitions: no overlapping browser supervisors.

## 3. Source/test commit sequence

- Runtime guard: `cca5f539fada52fdee374507ff652576641195ae`.
- Renewal rejection regression test: `e363105fa175e70476f486bd381fa80a8c3f1b22`.
- Late snapshot/update suppression regression test and current source/test HEAD: `90fd29cbf7d98ee80ff6ba477bc4f016ec729fd5`.

All commits are on `phase-2/market-data-foundation`. `main` was not modified. Documentation is maintained separately from source/test acceptance so the exact source/test SHA remains identifiable.

## 4. CI evidence for source/test HEAD

At the source/test HEAD `90fd29cbf7d98ee80ff6ba477bc4f016ec729fd5`:
- Automated Tests [44994083255](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083255): **IN PROGRESS** at audit time.
- CodeQL [44994083173](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083173): **IN PROGRESS** at audit time.
- Full Git History Secret Audit [44994083185](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083185): **SUCCESS**.
- Android debug APK build [44994083097](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44994083097): **IN PROGRESS** at audit time.

No new regression test is marked CI-accepted until Automated Tests completes successfully on this source/test commit. CodeQL is also pending. The APK workflow is a zero-cost CI debug build, not a production release or Play Store publication.

## 5. WebSocket acceptance status

### Gate 36 — OPEN

| Acceptance item | Repository evidence | Remaining acceptance |
|---|---|---|
| Secure transport | Production rejects plaintext; HTTPS ticket exchange and WSS URL normalization are tested | Public hostname, certificate chain, reverse-proxy upgrade and timeout |
| Firebase ticket | Short-lived purpose-bound ticket; ID token not sent over WebSocket | Real project valid/expired/revoked/wrong-project token tests |
| Renewal | Single-use renewal ticket, acknowledgement, bounded timeout; late rejection after intentional close now ignored | Real browser/Android session renewal under sleep and network transition |
| Snapshot/replay | Validated stream watermark, decimal-string cursor, replay completion and sequence guard | Public-network interruption, server restart and resnapshot proof |
| Browser lifecycle | online/offline/visibility listeners, cleanup, reconnect, rapid transition tests | Real browser sleep/wake and physical-device behavior |
| Android WebView | Shared client and browser lifecycle policy | Foreground/background, process death, OS suspension and network handover |
| Operations | CI tests and workflow evidence | Owner-host telemetry, alert delivery, runbook and recovery drill |

### Gate 25 — OPEN

- Snapshot rows and checkpoint are transactionally installed.
- Checkpoint currently does not anchor the snapshot digest in a durable immutable installation receipt.
- Authenticated source/replica provenance, key lifecycle, immutable receipt conflict semantics, migration and owner-host Redis persistence/restart/backup/failover remain acceptance blockers.
- No schema or cryptographic trust model was guessed or changed.

### Gate 38 — OPEN

- Owner-host metrics persistence, disk-pressure handling, restart/backup/retention, operator dashboard, external alert delivery and recovery drill remain unproven.

### Gate 10

`0/10` external acceptance criteria formally closed. Internal unit tests and CI do not automatically close owner-host or production criteria.

## 6. Technical indicator progress — complete current ledger

No indicator calculation, indicator hook, renderer or indicator UI source changed in Batch 62J-140. No indicator implementation credit is awarded by this WebSocket cycle.

| Indicator/component | Status | Verified foundation and remaining work |
|---|---|---|
| SMA20 | 🟨 Foundation | Arithmetic mean of 20 closes; first valid index 19; chart integration, edge cases and renderer acceptance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha (2/21); first valid index 19; chart integration and edge-case acceptance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing foundation; first valid index 14; numerical edge cases and chart integration remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; chart integration remains |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations; first valid index 19; chart integration remains |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; full chart integration remains |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth; visual work waits for user reference image(s) and reviewed blueprint |
| Heatmap | 🟥 Not implemented | Wait for user reference image(s) and reviewed blueprint before visual implementation |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

### Mandatory shared indicator invariants

- Warm-up values remain `null`; never fill them with fabricated values.
- Each output remains aligned to the originating candle index.
- Prefix-causality: adding future candles cannot change earlier indicator values.
- Invalid/missing/gapped bars cannot silently become zero.
- Stale output is cleared when symbol, venue, dataset, chart or timeframe identity changes.
- Calculation correctness, chart rendering, interaction, lifecycle and performance are distinct acceptance dimensions.
- Footprint OFF preserves ordinary candle spacing; explicit ON alone enables the spaced cluster layout.
- Footprint and Heatmap visual work requires user-supplied reference images and a reviewed scoped blueprint.
- No combined indicator percentage is published because weights and denominator have not been approved.

## 7. Project-wide progress indicator

Legend: 🟩 formally accepted/closed; 🟨 partial/provisional; 🟧 prototype; 🟥 not implemented; ⬜ not scored/not officially opened.

| Stage | Current progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored | ⬜ |
| 3. Chart Engine & Timeframe | Not scored | ⬜ |
| 4. Indicators & Analytics | Not scored | ⬜ |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ |

**Overall project: NOT SCORED.** Six-stage weights and a project-wide acceptance denominator are not approved. Stage 1's 75% must not be represented as overall completion.

**Gate 10: 0/10** external acceptance criteria formally closed.

## 8. IPS35 / IP3S — Indicator Proses Peningkatan Proyek Signifikan

The user-facing project indicator is named **IPS35** (also previously called IP3S). It measures verified cycle delivery quality, not total project completion.

**Current score: PENDING exact-source-commit CI.** The runtime correction and two regression tests exist in source, but Automated Tests and CodeQL must finish on `90fd29cbf7d98ee80ff6ba477bc4f016ec729fd5` before the cycle earns CI acceptance points.

Scoring dimensions retained for final evaluation:
- Engineering delta: 25 points.
- Exact-commit automated/security CI: 20 points.
- Blocker isolation/reduction: 20 points.
- Complete canonical documentation: 20 points.
- ZERO COST, branch and scope integrity: 15 points.

Do not publish a final numeric score before the exact-commit CI evidence is complete.

## 9. ZERO COST and integrity

- No paid hosting, API, domain, subscription, cloud resource or deployment.
- No account creation or production credentials.
- No private keys, shared secrets or tokens added to code, tests or documentation.
- No device or Termux operation.
- No dependency added for this fix.
- No database/schema migration.
- `main` untouched.
- All source/test work remains on `phase-2/market-data-foundation`.

## 10. Next engineering unit

After exact-commit CI succeeds, proceed to the next repository-only WebSocket acceptance slice: verify stale socket callbacks across repeated supervisor replacement and selection/timeframe changes. Preserve the current store identity guards and avoid broad refactoring. Android WebView and public WSS remain separate external acceptance lanes. Gate 25 implementation remains approval-gated on trust model and immutable receipt policy.
