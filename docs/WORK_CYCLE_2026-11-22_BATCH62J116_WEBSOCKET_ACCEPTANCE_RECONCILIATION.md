# DEZZTA CHART — Batch 62J-116
## WebSocket acceptance reconciliation — exact-head CI and remaining external gates

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited baseline:** `a3febdb3f7d3dd233f1cfeb8e482e986e56348e1`  
**Scope:** WebSocket repository acceptance, Gate 20 / Gate 25 / Gate 36 evidence reconciliation  
**Cost:** ZERO COST. Documentation-only; no deployment, paid provider, production credentials, Termux/device action, or `main` modification.

## 1. Decision

**Repository-side WebSocket protocol and regression acceptance is CI-green at this exact baseline. Production WebSocket acceptance remains OPEN.** No public endpoint, real Firebase project, owner-host Redis, or Android WebView session is available in this checkpoint. Do not describe the feature as production-ready or 100% complete.

## 2. Exact-head verification

| Workflow | Run | Exact-head result |
|---|---:|---|
| Automated Tests | [44981340874](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340874) | **SUCCESS** |
| CodeQL | [44981340863](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340863) | **SUCCESS** |
| Full Git History Secret Audit | [44981341220](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981341220) | **SUCCESS** |

Automated Tests completed all **36/36** workflow steps with no failed step. Frontend Vitest reported **29 test files passed**. Backend pytest reported **1,294 passed, 1 skipped**. The workflow also completed frontend build/secret scans, backend dependency audit, isolated Redis TLS/hostname/ACL fixture, backend container build, container smoke with Redis TLS/ACL and persistent-volume restart, image scan/report, and synthetic SQLite outbox/metrics benchmarks.

The smoke environment is ephemeral CI infrastructure. It is not the future OCI VM, public WSS hostname, or proof of production recovery.

## 3. WebSocket client acceptance inventory

The exact baseline contains:
- `src/services/ohlcvWebSocketClient.test.ts`: **17 tests** covering HTTPS/WSS production transport guard, ticket authentication, exact-series subscription, snapshot/update, durable cursor replay, ticket renewal acknowledgement, heartbeat/pong timeout, observer isolation, failed close recovery, sequence-gap rejection, identity validation and contract/timeframe change closure.
- `src/services/ohlcvWebSocketTicket.test.ts`: **7 tests** covering HTTPS endpoint normalization, Bearer-token exchange, 401 signal preservation, request/body deadline, malformed response, production plaintext rejection, missing credentials and embedded URL credentials.
- `src/services/ohlcvStreamSupervisor.test.ts`: **21 tests** covering shared-store publication, cursor resume, replay recovery, backoff reset, transient ticket/token retry, token acquisition timeout, fresh-token reconnect, gap recovery via fresh snapshot, terminal authentication/authorization/policy handling, close/error races, waiting for native close, cancellation, and explicit stop.
- Backend API/ticket/shared-guard/stream/publisher/replica/Redis suites run within the backend test total. Prior dedicated cycles cover digest-only ticket keys, NX single-use, 90-second TTL, concurrent consume, invalid/expired renewal, cross-account renewal, entitlement revocation, ticket-store outage and sanitized failure close behavior.

Counts above are file-local test cases, not a claim that every possible network/proxy/browser/device condition is simulated.

## 4. Acceptance matrix — current disposition

| Area | Repository evidence | External acceptance still required | State |
|---|---|---|---|
| Ticket issuance / consume | Firebase verifier path, HTTPS Bearer exchange, digest-keyed shared store, atomic single-use consume, 90s TTL, failure tests | Real Firebase project: valid, expired, revoked, wrong-project token and real entitlement | 🟧 Open |
| Client transport | HTTPS-to-WSS construction, ticket auth, protocol validation, exact-series subscription | Public DNS, certificate SAN/chain/expiry, TLS handshake and real public WSS | 🟧 Open |
| Proxy | Route and protocol contract tests | Actual reverse-proxy Upgrade/Connection/path/read-timeout/idle-timeout behavior | 🟧 Open |
| Snapshot/replay | Atomic snapshot/subscription boundary, durable cursor replay, retention-floor resnapshot, gap rejection | Verify exact snapshot bytes/hash and authenticated installation receipt on every required gateway | 🟧 Open |
| Redis shared guard | CI Redis TLS/CA/hostname/ACL fixture, AOF restart smoke, fail-closed tests | Owner-host private network, separate ACL identities, secret rotation, persistent-volume/failover/restore | 🟧 Open |
| Multi-gateway relay | Publisher/replica roles, per-gateway consumer-group design, lease fencing and source-side tests | Activate owner-injected verifier/installer; verify snapshot receipts and event fan-out across all gateways | 🟧 Open |
| Reconnect / renewal | 21 supervisor tests; cursor resume, fresh token/ticket, bounded backoff, terminal auth policy | Real network switching and real auth expiry/revocation under browser/Android lifecycle | 🟧 Open |
| Browser / Android | Client logic and unit tests | Browser tab visibility, background/foreground, Android WebView suspend/resume, Wi-Fi/mobile switch, duplicate-stream prevention | 🟧 Open |
| Observability | Metrics and bounded collector implementation/CI tests | Owner-host dashboards, alert routing, retention and recovery drill | 🟧 Open |

## 5. Security and protocol invariants retained

- Production client uses HTTPS for ticket issuance and WSS for the socket; plaintext remote transport is rejected.
- Firebase ID token is not placed in the WebSocket URL or auth frame. The client exchanges it over HTTPS and sends a short-lived one-use ticket in the WebSocket frame.
- Ticket TTL is 90 seconds; the client renews on its configured schedule and waits for explicit server acknowledgement.
- Ticket is bound to verified subject and purpose, not currently to a canonical series or Origin. Series mapping and entitlement are checked separately before snapshot and during renewal. Origin validation is defense in depth; it is not authentication.
- Replay uses durable cursors; sequence gaps are rejected and recovery requires a fresh snapshot/watermark. No silent skip is accepted.
- No data is labelled LIVE merely because the API is healthy. Provider connectivity, data freshness and completeness remain independent states.
- Errors fail closed and credential/internal Redis exception details are not sent as client-facing diagnostics.

## 6. Production gate blockers — concrete next evidence

1. **Gate 20:** owner-managed Firebase project/test accounts must run signed-token cases for valid, expired, revoked and wrong-project tokens, plus entitlement grant/revoke and renewal. No credentials or ID tokens should be sent in this chat.
2. **Gate 25:** owner-managed private Redis host must prove TLS CA + hostname verification, separate least-privilege ACL identities, AOF/persistent-volume restart, secret rotation, outage behavior, restore and retention. Do not expose Redis publicly.
3. **Gate 25/36:** owner-controlled source and every required gateway must verify the same snapshot bytes/hash, authenticated install receipts, cursor baseline and live event fan-out. No mock receipt or environment-only bypass.
4. **Gate 36:** a stable owner-controlled hostname and trusted TLS chain are prerequisites for public WSS. Verify proxy Upgrade/Connection/path/timeouts, ticket handshake, heartbeat, renewal and reconnect from a real browser and Android WebView.
5. Record redacted timestamped evidence, exact source commit, host build/config revision, gateway IDs, test identity class (not token), close code and result. Never capture or share bearer tokens, one-time tickets, Redis URLs/passwords, private keys or full secret-bearing logs.

No host or public endpoint currently exists in the verified project evidence. This is a real acceptance blocker, not something more unit tests can substitute for. Keep the plan at Rp0; if no free lawful hostname/TLS route is available, public WSS remains blocked until the owner decides otherwise. Any account signup/payment verification for hosting must be handled by a parent/guardian; do not bypass age or verification controls.

## 7. Gate and project accounting

- Gate 20, Gate 25 and Gate 36 remain 🟧 OPEN.
- Gate 10 remains **0/10 formally closed**. CI success is not a Gate 10 closure.
- Stage 1 remains **30/40 = 75% provisional**. No stage percentage is awarded by this docs-only batch.
- No production acceptance or deployment is claimed.

## 8. Indicator progress reconciliation — unchanged

No indicator source, formula, hook, renderer, chart UI or indicator test changed in Batch 62J-116. **Zero indicator progress credit** is awarded.

| Indicator / subsystem | Status | Calculation foundation / first valid index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; index 19 | Visible overlay, independent toggle, legend/value, identity clearing, render/lifecycle acceptance |
| EMA20 | 🟨 | SMA-seeded EMA, alpha 2/21; index 19 | Visible overlay, independent toggle, legend/value, identity clearing, render/lifecycle acceptance |
| RSI14 Wilder | 🟨 | 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend/value, render/lifecycle acceptance |
| MACD12/26/9 | 🟨 | EMA12−EMA26; MACD index 25, signal/histogram index 33 | Dedicated pane, lines/histogram/zero guide, toggle and lifecycle acceptance |
| Bollinger20,2 | 🟨 | 20-close mean ± 2 population SD; index 19 | Three-line overlay, toggle, values and lifecycle acceptance |
| Shared Indicator Hook | 🟨 | Validated backend snapshot only | Dedicated hook tests and chart integration; hook is not yet wired into chart |
| Footprint | 🟧 | Synthetic educational accumulator only | User reference image, reviewed blueprint, validated data contract, ON-only spaced clusters; OFF keeps ordinary spacing |
| Heatmap | 🟥 | Not implemented | Zero-cost validated source, user reference, approved blueprint, renderer/scale/tests |
| Liquidation Maps | 🟥 | Not implemented | Validated source/formula, owner reference/blueprint, renderer/scale/tests |

The full formula, numerical-safety, lifecycle and visual-acceptance ledger remains in `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md` and `docs/INDICATOR_PROGRESS_LEDGER.md`. Aggregate indicator percentage remains unscored without an approved denominator and weights.

## 9. Files changed and implementation accounting

Documentation-only files updated:
- `docs/WEBSOCKET_AUTH_DESIGN.md`
- `docs/WEBSOCKET_RELIABILITY_DESIGN.md`
- `docs/WORK_CYCLE_2026-11-22_BATCH62J105_WEBSOCKET_FINAL_ACCEPTANCE_PACK.md`
- `docs/WEBSOCKET_PRODUCTION_WIRING_AUDIT.md`

Added:
- `docs/WORK_CYCLE_2026-11-22_BATCH62J116_WEBSOCKET_ACCEPTANCE_RECONCILIATION.md`

No runtime source, test source, provider integration, credentials, host config, indicator implementation, deployment or device action changed. `main` remains untouched. Exact-head CI for the resulting documentation commit must be checked before calling that new commit CI-accepted.
