# DEZZTA CHART — Work Cycle 62J-145
## Real TLS/WSS transport, Origin enforcement and multi-user disconnect isolation

Date: 22 November 2026
Branch: phase-2/market-data-foundation
Parent source/test baseline: f8e41ad68656e82a82d30cf40f720f3ec98ac337
ZERO COST: no cloud account/resource, deployment, paid service, production credential, payment method, device operation or main change.

## 1. Engineering objective

Move WebSocket validation beyond an in-process ASGI TestClient by exercising the backend through a real loopback TCP listener with Uvicorn TLS and a real WebSocket client. The test remains isolated and self-contained: it generates an ephemeral test CA and server certificate in pytest temporary storage, binds only to 127.0.0.1 on an OS-selected ephemeral port, and shuts down the server and listener after the test.

## 2. Runtime/test changes

One backend test file changed: backend/tests/test_api.py.

The integration test creates an ephemeral X.509 CA and a localhost server certificate with DNS and IP subject alternative names, starts Uvicorn with TLS, and connects with the websockets client using a trust context containing only the ephemeral test CA.

The test verifies:
- Trusted certificate chain and hostname verification succeed.
- A real WSS handshake and HTTP Upgrade complete.
- The allowed HTTPS Origin is accepted.
- A disallowed Origin receives HTTP 403 and is not upgraded.
- A client without the ephemeral CA trust fails certificate verification.
- Test-mode authentication, exact series subscription and a four-bar OHLCV snapshot work over the encrypted socket.
- The application-level text ping receives the exact versioned market_data.pong response.

The same TLS listener then serves two distinct test identities:
- User A and User B have separate verified subjects and separately granted entitlement to the same canonical instrument.
- Both create independent WSS connections and subscriptions.
- The test observes two active subscriptions.
- User B closes its WSS connection.
- The test waits up to five seconds for the asynchronous ASGI disconnect cleanup to complete and verifies the subscription count returns to one.
- User A's connection still responds to ping with pong after User B has disconnected.

The existing TestClient multi-user regression remains in place as a separate lower-level check.

## 3. Authentication boundary — important limitation

This WSS harness deliberately uses the backend's non-production legacy test-token path with a fake identity verifier. The backend explicitly rejects this path when APP_ENV is production.

Therefore this test proves TLS, HTTP Upgrade, Origin enforcement, authenticated test-mode session routing, snapshot delivery, application heartbeat, and multi-user disconnect isolation. It does NOT yet prove the complete production HTTPS Firebase ID-token → one-time ticket endpoint → ticket-authenticated WSS handshake → ticket renewal flow over the same TLS listener. That is the next implementation target.

No Firebase production project, real signed token, provider key, user secret or entitlement service was provisioned.

## 4. Exact-HEAD CI evidence

Final source/test HEAD: f8e41ad68656e82a82d30cf40f720f3ec98ac337.

- Automated Tests run 45005536779: SUCCESS.
- CodeQL run 45005536789: SUCCESS.
- Full Git History Secret Audit run 45005537134: SUCCESS.
- OCI ARM64 Readiness run 45005536741: SUCCESS.

Automated Tests reported 1,297 passed, 1 skipped, 0 failed, with 6 warnings. The skipped test is the standalone Redis TLS integration test when its dedicated fixture environment variables are absent from the general pytest invocation; the workflow runs that isolated Redis TLS CA/hostname/ACL/AOF fixture as a separate successful step before the backend suite.

Additional successful workflow evidence:
- Frontend unit tests and frontend build.
- Frontend dependency audit: zero reported vulnerabilities.
- Backend pip-audit: no known vulnerabilities found.
- Isolated Redis TLS listener: trusted CA accepted; wrong CA, wrong hostname and plaintext downgrade rejected.
- Redis ACL: unauthenticated, incorrect-password and unrelated SET operations rejected.
- Redis AOF and persisted ACL survived a container restart.
- Backend tests: 1,297 passed, 1 skipped.
- Synthetic SQLite outbox benchmark and same-host metrics collector benchmark completed.
- Backend container build and shared-Redis/persistent-volume smoke test passed.
- Container ran as UID/GID 10001; mounted volume and SQLite ownership verified.
- Redis outage caused API protection to fail closed; after Redis restart the backend recovered and durable data remained available.
- Trivy HIGH/CRITICAL scan reported zero vulnerabilities in the scanned Alpine 3.24.4 OS and Python package targets.
- Native ARM64 readiness workflow passed on the GitHub-hosted ARM64 runner.

These are repository CI and local synthetic integration results. They do not constitute a public WSS endpoint, production Firebase acceptance, owner-host Redis acceptance, an OCI VM deployment, or Android WebView acceptance.

## 5. Work-cycle corrections discovered by CI

Two test-harness issues were repaired before final acceptance:
1. The first certificate builder used an X.509 API method not exposed by the installed cryptography 50.0.2 builder. It was replaced with the supported naive-UTC builder API.
2. The first real-network disconnect assertion checked the subscription count immediately after the client-side close context returned. ASGI final cleanup is asynchronous; the regression now waits a bounded five seconds for the server-side unsubscribe and then asserts the exact count. The subsequent exact-HEAD run passed.

These were test harness compatibility/timing corrections. No production WebSocket runtime behavior was weakened to make the tests pass.

## 6. Complete indicator ledger — unchanged

No indicator formula, numerical kernel, shared hook, renderer, chart UI or indicator test changed. This cycle receives zero indicator implementation credit.

| Indicator/component | Status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Numeric edge cases, chart integration, identity invalidation, lifecycle and performance |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14 | Flat/monotonic/zero-loss edge cases, chart integration and lifecycle |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33 | Numerical edge cases, chart integration, identity invalidation and lifecycle |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Variance/flat-series edge cases, chart integration and lifecycle |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output | Full chart integration, visible settings/legend/current values and stale-output clearing |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator; not exchange-native bid/ask truth | User reference image(s), reviewed blueprint, licensed bid/ask data contract, cluster renderer and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime/render implementation | User reference image(s), reviewed blueprint, validated depth/liquidity data contract and renderer |
| Liquidation Maps | 🟥 Not implemented | No accepted runtime/render implementation | Defensible data provenance/contract, reviewed design, renderer and tests |

Mandatory invariants remain:
- Warm-up values are null, never fabricated zero.
- Output aligns exactly to source candle indices.
- Prefix causality: appending future candles cannot alter earlier values.
- Invalid/missing/gapped bars are never silently converted to zero.
- Stale outputs clear on symbol, venue, dataset, chart and timeframe identity changes.
- Formula, rendering, interaction, lifecycle, accessibility and performance are separate acceptance dimensions.
- Footprint OFF preserves standard candle spacing; only explicit ON enables the dedicated spaced-cluster layout.
- Footprint and Heatmap visual implementation remains blocked until the user supplies reference image(s) and reviews the scoped blueprint.
- Aggregate indicator completion remains NOT SCORED because weights and denominator are not approved.

## 7. Project-wide progress and gates

Legend: 🟩 accepted; 🟨 partial/provisional; 🟧 prototype; 🟥 not implemented; ⬜ not scored/not opened.

| Official stage | Current progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened | ⬜ |
| 3. Chart Engine & Timeframe | Not scored / not officially opened | ⬜ |
| 4. Indicators & Analytics | Not scored / not officially opened | ⬜ |
| 5. Professional UI & Interactive Tools | Not scored / not officially opened | ⬜ |
| 6. Hardening, Validation & APK Release | Not scored / not officially opened | ⬜ |

Overall project: NOT SCORED. Approved stage weights and total denominator are unavailable. Stage 1's provisional 75% is not an overall project percentage.

Gate 10: 0/10 external criteria formally closed.
- Gate 25: OPEN — authenticated immutable snapshot-installation receipt, receipt custody, owner-host Redis TLS/ACL, persistence and restart/failover.
- Gate 36: OPEN — public hostname, trusted reverse-proxy WSS, production Firebase identity/entitlement and real browser/Android WebView lifecycle/network handover.
- Gate 38: OPEN — owner-host durable metrics, retention, dashboard, alert delivery and recovery drill.
- Gates 8, 20, 30, 31, 34, 35 and 39 remain open pending their own acceptance evidence.

IPS35/IP3S for this cycle: pending canonical documentation commit exact-HEAD CI. No score is assigned in advance.

## 8. ZERO COST and scope integrity

- Active branch remains phase-2/market-data-foundation.
- main remains untouched.
- No new runtime dependency or database/schema migration was introduced by this cycle.
- No cloud account, deployment, public hostname, production credential, payment method or paid resource was created.
- No Android device or Termux operation was performed.
- OCI ARM64 workflow is a CI build/smoke check, not an OCI installation.

## 9. Next ten engineering work items

1. Exercise the production-style HTTPS ticket endpoint and one-time ticket-authenticated WSS handshake on the same ephemeral TLS server, using a fake verifier only in test mode.
2. Add real WSS ticket-renewal coverage, including wrong-subject, expired, reused and entitlement-revoked ticket cases.
3. Exercise real WSS reconnect after abrupt transport loss, using the last durable cursor and verifying snapshot/replay ordering.
4. Verify duplicate suppression, sequence-gap rejection and resnapshot-required recovery across reconnect.
5. Add a local reverse-proxy integration harness for WSS Upgrade, forwarded headers, Origin policy and trusted-host configuration.
6. Add certificate SAN mismatch, expiry and rotation/reload negative tests for the edge transport.
7. Complete Gate 25 receipt trust policy review before any checkpoint schema or migration change.
8. Strengthen Gate 38 metrics persistence, disk-pressure, multi-worker SQLite contention and restore/alert evidence.
9. Build an Android WebView lifecycle acceptance harness for foreground/background, process recreation and network handover; physical-device evidence remains separate.
10. Preserve native ARM64 image/configuration readiness and prepare an owner-operated deployment checklist without provisioning or billing resources.

Next immediate target is item 1: test HTTPS ticket exchange and ticket-authenticated WSS end to end. Do not skip ahead to public deployment while production identity, owner-host receipt trust, reverse proxy and operational acceptance remain open.
