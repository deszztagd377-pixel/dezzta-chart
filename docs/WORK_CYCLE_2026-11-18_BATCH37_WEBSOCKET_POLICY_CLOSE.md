# Work Cycle — Batch 37: Terminal WebSocket Policy-Close Handling

**Date:** 18 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent exact HEAD:** `de59c0ede125d31d2cd2cfa95c47082e44385214`  
**Scope:** WebSocket reconnect policy and regression coverage; zero-cost source-only correction.

## 1. Finding

The backend explicitly closes unsupported client control frames and ping-rate-limit violations with close code `1008`. Before this change, the supervisor treated `1008` as transient and scheduled a reconnect. Since the reconnect repeats the same client protocol and configuration, it can reproduce the policy violation indefinitely.

## 2. Correction

- Treat close code `1008` as terminal for the current supervisor instance, alongside the existing terminal authentication, entitlement, and malformed-subscription codes.
- Mark the market-data snapshot unavailable with a protocol-policy explanation.
- Surface an explicit `1008` error.
- Do not retry until the owning session/selection recreates the supervisor after correcting the client policy/configuration.
- Add a regression test proving a server `1008` close does not create a second socket, even after pending timers are advanced.

## 3. Compatibility and calculations

- Client heartbeat cadence remains 20 seconds: (1/20 = 0.05) ping/s.
- Backend rate ceiling remains 20 per rolling 10 seconds: (20/10 = 2) ping/s.
- Normal steady-state client utilization remains (0.05/2 = 2.5\%).
- Pong deadline remains 10 seconds.
- No change to snapshot/replay cursors, sequence validation, Firebase token refresh, entitlement checks, or data payloads.
- Terminal close handling prevents repeated identical policy violations; it does not hide the error or downgrade the protocol.

## 4. Validation plan

The new test verifies:
1. One socket is opened.
2. Server closes it with code `1008`.
3. Supervisor transitions to `stopped`.
4. Market-data store becomes `unavailable`.
5. Advancing pending timers does not create another socket.

Exact-head CI, CodeQL, and full-history secret audit must complete before the batch is considered validated. Source changes alone do not earn Stage 1 ticks or Gate 10 closures.

## 5. Known blocker

The frontend dependency audit currently reports five High findings through `picomatch@4.0.7`. The current graph is Vite 6.4.5 / Vitest 4.1.12. npm proposes a breaking Vitest downgrade to 3.1.4; this is not an acceptable automatic remediation. Keep the audit fail-closed and wait for a safe compatible upstream fix or a fully tested, reviewed upgrade path.

## 6. Cost, deployment, and device boundary

No deployment or Cloudflare action. No paid service, billing, provider credential, or publication action. No Termux operation is required.

## 7. Progress accounting

Stage 1 remains 75% provisional (300/400 ticks; 30/40 criteria). Gate 10 remains 0/10 formally closed. Open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39. Stages 2–6 are not scored; overall project progress is not established. No progress ticks or closures are awarded by this batch alone.
