# Batch 62J-139 — Gate 36 browser lifecycle and WebSocket acceptance reconciliation

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Audited exact HEAD: `d473a533deaec58e1abb07a2f5a2a911f941dfed`  
Scope: source/test audit, two focused client regression tests, acceptance-gap isolation and project/indicator reconciliation. No runtime or schema code was changed.

## 1. Exact-HEAD CI verification

All three workflow runs below identify the same branch and exact commit `d473a533deaec58e1abb07a2f5a2a911f941dfed`:

- Automated Tests [44993051427](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44993051427): **SUCCESS**.
- CodeQL [44993051424](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44993051424): **SUCCESS** — Python and JavaScript/TypeScript analysis jobs both succeeded.
- Full Git History Secret Audit [44993051426](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44993051426): **SUCCESS**.

The latest branch commit query also resolved to the same SHA. This is repository CI evidence only; it does not prove a public WSS deployment, live Firebase project, owner-host Redis, or Android-device acceptance.

## 2. Client WebSocket source audit

Files inspected:
- `src/services/ohlcvWebSocketClient.ts`
- `src/services/ohlcvWebSocketClient.test.ts`
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`
- `src/services/ohlcvStreamLifecycle.ts`
- `src/services/ohlcvStreamLifecycle.test.ts`
- `src/services/ohlcvWebSocketTicket.ts`
- `src/services/ohlcvWebSocketTicket.test.ts`
- `docs/WEBSOCKET_AUTH_DESIGN.md`

### Verified implemented behavior

1. **Transport security:** production URL construction requires HTTPS input and converts it to WSS; embedded URL credentials are rejected before socket creation.
2. **Ticket exchange:** Firebase ID token is sent over HTTPS POST to the normalized ticket endpoint; request uses `cache: no-store`, `credentials: omit`, `redirect: error`, and an abort deadline. Production rejects plaintext HTTP before fetch.
3. **Ticket validation:** response requires a bounded ticket string, `purpose=market-data`, and the expected 90-second lifetime. A 401 remains distinguishable for terminal authentication handling.
4. **WebSocket authentication:** the socket receives the short-lived ticket, not the Firebase ID token. Exact canonical instrument and series are sent in the subscription request.
5. **Snapshot/replay boundary:** snapshot stream ID and watermark are validated. Resume cursors are decimal strings, preserving values beyond JavaScript's safe integer range. Replay completion is required before normal live subscription resumes.
6. **Continuity:** sequence/cursor validation rejects protocol gaps rather than silently applying out-of-order updates. The supervisor reconnects using the last accepted cursor and preserves the last validated chart state while recovering.
7. **Renewal and liveness:** the client renews its single-use ticket, requires an acknowledgement, and uses bounded heartbeat/pong handling. Timeout and send failures enter cleanup.
8. **Failure isolation:** status, error and close observers are isolated so a throwing UI callback cannot prevent transport cleanup. The supervisor waits for the authoritative close event to avoid overlapping sockets.
9. **Terminal policy:** authentication, authorization, malformed-subscription and protocol-policy closes are not retried unchanged. The 4403 Origin-vs-entitlement diagnostic correction remains in place.
10. **Browser lifecycle policy helper:** `getOhlcvStreamLifecycle()` permits connection only when online and visible; offline takes precedence over hidden, and prerender/other non-visible states are treated as hidden.

### Existing test evidence

- WebSocket client tests exercise production plaintext rejection, authentication/subscription, snapshot/update, large durable cursor replay, renewal acknowledgement, heartbeat/error cleanup and invalid protocol cases.
- Supervisor tests exercise token/ticket acquisition, reconnect and backoff, cursor replay, store preservation, sequence-gap recovery, terminal close classes, delayed/failed close handling, and observer exceptions.
- Lifecycle helper tests cover active, offline, hidden, combined offline+hidden, and prerender states.
- Ticket tests cover normalized HTTPS request options, 401 propagation, request/body timeout, malformed payloads, production HTTP rejection, missing token and credential-bearing URL rejection.

These are automated unit/simulation tests. They are not equivalent to a real production browser behind the intended reverse proxy or a physical Android WebView under operating-system lifecycle changes.

## 3. Gate 36 acceptance gap — precise separation

**Gate 36 remains OPEN.** Browser lifecycle event wiring is present and covered by component integration tests. The remaining gap is real Android WebView and public production acceptance, plus narrower race-condition tests. This is not a reason to weaken authentication or add speculative ticket claims.

| Acceptance item | Current evidence | Remaining proof |
|---|---|---|
| WSS transport policy | Production client rejects non-HTTPS base URL | Public hostname, valid certificate chain, reverse-proxy upgrade and timeout behavior |
| Firebase token exchange | Injected verifier/client tests and HTTPS ticket flow | Real Firebase project with valid, expired, revoked and wrong-project tokens |
| Ticket semantics | Subject + purpose, single-use, 90-second TTL; renewal acknowledgement | Owner/product threat-model decision on series/Origin binding; no automatic scope expansion |
| Browser foreground/background | Policy helper + CandlestickChart event wiring and mocked-supervisor integration tests | Real browser sleep/wake and physical-device acceptance; rapid event-ordering race coverage |
| Android WebView | Shared client code exists | Real app/WebView foreground/background, process death, network handover and resume tests |
| Replay after interruption | Local socket and TCP fault-path CI evidence | Public-network interruption with duplicate/gap/resnapshot evidence |
| Operations | CI logs and test assertions | Owner-host logs, alert delivery, operator runbook and recovery drill |

### Acceptance sequence — verified integration and remaining boundary

A. **Browser lifecycle integration — implemented and unit-tested**
- `CandlestickChart` registers `online`, `offline` and `visibilitychange` listeners and derives the policy through `getOhlcvStreamLifecycle()`.
- Its stream effect depends on `shouldConnect` and `reason`; a hidden/offline transition runs the effect cleanup and calls `supervisor.stop()`.
- Returning visible+online creates a new supervisor; the component lifecycle tests assert stop/recreate behavior, initially hidden/offline behavior, and unmount cleanup.
- Therefore browser event wiring is **not** an outstanding gap. Do not duplicate or rewrite this existing integration.

B. **Remaining repository-only hardening candidates**
- Add focused tests for rapid visibility/network event ordering and stale callbacks after supervisor teardown.
- Exercise stop while Firebase token acquisition or HTTPS ticket exchange is pending, ensuring no socket is opened and no stale snapshot/update reaches the store.
- Verify cleanup under repeated mount/unmount and simultaneous hidden/offline transitions without overlapping supervisors.
- Before changing code, inspect the existing supervisor cancellation and store-publication guards; preserve the current correct behavior.

C. **Android acceptance**
- Keep as a separate platform acceptance lane; browser DOM lifecycle tests do not close Android WebView acceptance.
- Physical WebView foreground/background, process death, OS suspension and network handover remain untested in this cycle.
- No device or Termux operations are performed.

D. **External production acceptance**
- Requires an owner-controlled public endpoint, real Firebase project and operator access. This cycle does not create accounts, deploy services, provision resources or request credentials.

## 4. Test-only hardening added after the source audit

Two regression tests were added on source/test commit `3cb7cb9b26be220e23314d9dad2f3ed31734baf4`:

1. `src/services/ohlcvStreamSupervisor.test.ts` — `does not open a socket when stop occurs while ticket issuance is pending`. It holds the injected ticket request open, stops the supervisor, resolves the ticket late, and asserts that no WebSocket is created and no reconnect is scheduled.
2. `src/components/CandlestickChart.lifecycle.test.tsx` — `coalesces rapid offline, hidden and return events without overlapping supervisors`. It exercises offline → hidden → online-while-hidden → visible, verifies one new supervisor only after both conditions are active, and verifies cleanup on unmount.

These are test-only additions. No production runtime behavior was changed. The test commit's CI is the acceptance authority; until its exact-SHA Automated Tests and CodeQL complete successfully, these new tests remain pending and receive no CI pass credit.

## 5. Gate 25 and Gate 38 — parallel blockers retained

- **Gate 25 OPEN:** durable immutable snapshot installation receipt and authenticated provenance remain unimplemented; source/generation/cursor checkpoint binding exists, but snapshot digest is not anchored to a durable immutable receipt. Owner trust model, key lifecycle, receipt retention and owner-host Redis restart/backup/failover remain unresolved.
- **Gate 38 OPEN:** owner-host metrics persistence, disk pressure, restart/backup/retention, operator dashboard, alert delivery and recovery drill remain unproven.
- Do not count a passing CI run as closure of any owner-host criterion.

## 6. Technical indicator progress — full ledger

No indicator runtime, calculation, test, hook, renderer or UI source changed in Batch 62J-139. No implementation credit is awarded.

| Indicator/component | Status | Verified state / acceptance still required |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid candle index 19; chart integration and full renderer acceptance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha = 2/21; first valid index 19; chart integration and full renderer acceptance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing foundation; first valid index 14; chart integration and numerical edge-case acceptance remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal and histogram first valid index 33; chart integration remains |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations; first valid index 19; chart integration remains |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; not fully chart-integrated |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth; visual work waits for user reference image(s) and reviewed blueprint |
| Heatmap | 🟥 Not implemented | Visual implementation waits for user reference image(s) and reviewed blueprint |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence |

### Shared indicator acceptance invariants

- Warm-up periods remain `null`; no fabricated early values.
- Every result remains aligned to its originating candle index.
- Prefix-causality: adding future candles must not alter earlier outputs.
- Invalid, missing or gapped source bars must not be silently converted to zero.
- Stale output must be cleared when symbol, venue, dataset, chart or timeframe identity changes.
- Renderer integration, lifecycle cleanup and performance remain separate from calculation correctness.
- Footprint OFF preserves standard candlestick layout and spacing. Only explicit Footprint ON enables the dedicated spaced cluster layout.
- Footprint and Heatmap visual implementation must not begin before the user supplies reference image(s) and reviews the scoped blueprint.
- No aggregate indicator percentage is published because indicator weights and a completion denominator have not been approved.

## 7. Project-wide progress indicator

Legend: 🟩 formally accepted/closed; 🟨 partially implemented or provisional; 🟧 prototype; 🟥 not implemented; ⬜ not scored/not officially opened.

| Stage | Progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = 75% | 🟨 Provisional; not all external acceptance closed |
| 2. Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| 3. Chart Engine & Timeframe | Not scored | ⬜ Not officially opened |
| 4. Indicators & Analytics | Not scored | ⬜ Not officially opened |
| 5. Professional UI & Interactive Tools | Not scored | ⬜ Not officially opened |
| 6. Hardening, Validation & APK Release | Not scored | ⬜ Not officially opened |

**Overall project: NOT SCORED.** The approved six-stage weights and total acceptance denominator do not exist yet. Stage 1's 75% cannot be represented as an overall project percentage.

**Gate 10: 0/10 external criteria formally closed.** This is the formal external-acceptance counter, not the number of internal tests.

## 8. IP3S — Indicator Proses Peningkatan Proyek Signifikan

IP3S measures the verified quality of this work cycle, not project completion. The score is **PENDING** until Automated Tests and CodeQL complete on the exact source/test commit; do not reuse the earlier 79/100 audit-only score as accepted delivery.

| Dimension | Score | Basis |
|---|---:|---|
| Verified engineering delta | 10/25 | Source-backed audit confirms existing event wiring and integration tests; no runtime or test source change |
| Exact-HEAD CI evidence | 20/20 | All three workflows succeeded on the exact audited SHA |
| Blocker isolation/reduction | 14/20 | Confirms browser policy is wired and integration-tested; isolates Android/public WSS and race-test boundaries |
| Canonical documentation | 20/20 | Full Gate 36 matrix, Gate 25/38 boundaries, indicator ledger and stage status recorded |
| ZERO COST and scope integrity | 15/15 | No paid resource, deployment, credentials, device work or main-branch change |
| **IP3S total** | **79/100** | Cycle delivery score only; not project completion |

## 9. Branch, cost and change integrity

- Audited branch: `phase-2/market-data-foundation`.
- Exact audited HEAD: `d473a533deaec58e1abb07a2f5a2a911f941dfed`.
- `main` untouched.
- Batch 62J-139 adds two test-only regressions and this documentation; no production runtime or schema changes.
- ZERO COST: no paid hosting, domain, market-data API, cloud resource, deployment, account creation or publication fee.
- No production credentials, private keys or shared secrets requested or written.
- No Android device or Termux operation performed.

## 10. Next engineering unit

The next source-backed, zero-cost unit is **B — lifecycle race-condition acceptance**: inspect and test stop-during-token-fetch, stop-during-ticket-request, rapid hide/show + offline/online ordering, and stale-socket callback suppression. The current browser event wiring and supervisor cleanup must be preserved. Android WebView and public WSS remain separate external acceptance lanes. No speculative patch is authorized by this report.
