# DEZZTA CHART — Batch 62J-105
## WebSocket final production-acceptance pack (zero-cost, no deployment)

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited source/test checkpoint:** `a18e963d4cd067fe22ec8d03c653418e003c7fde`  
**Scope:** Gate 20 / Gate 25 / Gate 36 WebSocket acceptance dependencies  
**Cost boundary:** ZERO COST. No new provider, paid hosting, Vercel/Cloudflare deployment, production credential exchange, or Termux operation.

## 1. Executive decision

The WebSocket implementation is **repository-side implemented and CI-verified for the covered protocol/failure matrix**, but it is **not production-accepted and must not be called 100% complete**.

The remaining work is not a missing collection of unit tests. It is evidence from the owner-controlled runtime and real clients:

1. public HTTPS/WSS and reverse-proxy upgrade behavior;
2. production Redis TLS/ACL, persistence, failover and secret lifecycle;
3. verified source snapshot installation on every gateway and live cross-instance fan-out;
4. real browser and Android WebView foreground/background/reconnect acceptance;
5. actual Firebase project token/revocation/entitlement acceptance.

This pack consolidates the evidence required to close those boundaries without manufacturing production success or introducing a paid service.

## 2. Repository evidence already present

At the audited source/test checkpoint:

- Automated Tests: run [44970436441](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436441) — SUCCESS; frontend 255/255 across 29 test files, backend 1,289 passed.
- CodeQL: run [44970436417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436417) — SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit: run [44970436377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44970436377) — SUCCESS.
- Renewal failure coverage includes invalid/expired ticket rejection, ticket-store outage fail-closed behavior, cross-account renewal rejection, entitlement recheck, sanitized errors, digest-keyed ticket storage, NX semantics, 90-second TTL and concurrent single-use consumption.
- Shared Redis guard uses atomic Lua operations for HTTP limits, WebSocket leases, renewal/release and ticket consumption; production TLS configuration requires certificate and hostname verification.
- Client coverage includes HTTPS-to-WSS URL construction, authentication, snapshot/replay sequence validation, heartbeat/pong timeout, ticket renewal acknowledgement, terminal auth/authorization handling, close-event isolation and reconnect supervisor behavior.
- Source publisher lifecycle and gateway replica/snapshot primitives exist, but the default ASGI app intentionally does not activate a production publisher role without exact owner-provided runtime binding and snapshot prerequisites.

**CI evidence is repository evidence only.** It does not prove a public endpoint, production Redis, installed gateway snapshot, real fan-out or Android WebView behavior.

## 3. Acceptance dependency graph

```text
Firebase identity + entitlement (Gate 20)
                 |
                 v
Short-lived one-use WebSocket ticket
                 |
                 v
Public HTTPS/WSS + reverse proxy (Gate 36)
                 |
                 v
Dedicated Redis TLS/ACL + durable stream (Gate 25)
                 |
       +---------+----------+
       |                    |
       v                    v
Source publisher      Gateway replica groups
       |                    |
       v                    v
Durable outbox ----> Verified snapshot + cursor
                            |
                            v
                    Local WebSocket hub
                            |
                            v
              Browser / Android WebView client
```

A Redis stream alone is not a broadcast topology. Every gateway that must receive every event needs its own consumer group. A single shared group load-balances messages among consumers and does not broadcast each message to every gateway.

## 4. Gate 36 — public HTTPS/WSS acceptance

### Preconditions

- A public hostname and owner-controlled TLS certificate exist.
- Certificate SAN covers the exact hostname; chain and expiry are valid.
- Reverse proxy forwards WebSocket Upgrade and Connection headers and preserves the intended path.
- Production client receives an HTTPS backend base URL and therefore constructs WSS. Production plaintext WS must be rejected.
- Proxy idle/read timeouts exceed the configured heartbeat interval plus timeout with documented margin.
- No ticket, bearer token, Redis URL, cookie, or private key is placed in URL query parameters or logs.

### Required observations

| ID | Test | Pass condition | Evidence |
|---|---|---|---|
| WSS-01 | TLS handshake | Valid chain, hostname and certificate dates | Redacted TLS inspection output |
| WSS-02 | Upgrade | HTTP upgrade reaches the intended ASGI route | Proxy/access log with secrets redacted |
| WSS-03 | Authentication | Valid one-use ticket receives authenticated status; invalid/expired ticket is rejected | Client event log + server close code |
| WSS-04 | Subscription | Entitled canonical instrument receives a snapshot with stream ID and watermark | Redacted protocol trace |
| WSS-05 | Replay | Valid cursor replays contiguous events; retention gap requests resnapshot | Cursor/count trace |
| WSS-06 | Live delivery | A committed source update reaches the subscribed client | Correlated source event ID and client event ID |
| WSS-07 | Heartbeat | Ping receives pong; missed pong terminates the connection and supervisor recovers | Timestamped heartbeat trace |
| WSS-08 | Renewal | Same verified account renews before ticket expiry; invalid/cross-account renewal is terminal | Renewal request/ack/close trace |
| WSS-09 | Network interruption | Reconnect uses a fresh Firebase token and cursor/snapshot recovery; no silent sequence gap | Redacted reconnect trace |
| WSS-10 | Certificate renewal | Renewal procedure is demonstrated without an outage outside the owner's accepted maintenance window | Certificate and proxy event record |

A public endpoint test must be run against the intended host. A local TestClient or mocked WebSocket cannot satisfy WSS-01 through WSS-10.

## 5. Gate 25 — production Redis and fan-out acceptance

### Security and availability

- Use a dedicated Redis ACL identity for each runtime role; do not reuse the HTTP/WebSocket guard identity for publisher or consumer roles unless the reviewed command/key scope explicitly permits it.
- Production connection must use `rediss://`; certificate verification and hostname verification must remain enabled.
- Credentials are injected through the host's secret mechanism, not Git, client bundles, logs, chat or command history.
- Verify credential rotation and rollback with a planned, redacted change record.
- Verify the actual mounted persistent volume, restart persistence, AOF policy and recovery behavior.
- Execute failover/recovery against the intended owner-managed Redis deployment; a CI Redis container is not a substitute.

### Snapshot and gateway consistency

For every gateway instance:

1. Obtain the exact global snapshot artifact from the approved source.
2. Verify SHA-256 against the independently communicated manifest digest.
3. Install the snapshot before the gateway consumer is marked ready.
4. Record source ID, replica ID, snapshot generation, applied cursor and retention floor.
5. Verify the installed replica checkpoint matches the publisher's source ID and expected generation/cursor.
6. Start the gateway's independent consumer group only after hydration succeeds.
7. Verify each gateway receives the same test event exactly once at its local hub (duplicate delivery must be deduplicated by stable event ID/cursor).
8. Restart one gateway and verify pending-message reclaim and replay/resnapshot behavior.
9. Simulate a Redis interruption and verify the source outbox remains durable and publisher cursor does not skip.
10. Exercise failover and confirm that no gateway silently advances beyond its applied checkpoint.

**Required invariants**

- One authoritative source writer for the configured source ID.
- SQLite source outbox commit remains independent of Redis availability.
- Stream append/checkpoint behavior is idempotent and ordered.
- Each gateway has an independent consumer group.
- Consumers acknowledge only after successful local hand-off.
- Pending messages are reclaimable after consumer process loss.
- Retention-floor gaps cause explicit resnapshot; never silently skip history.
- Snapshot bars and watermark represent one consistent source database view.
- Replica imports do not echo events into the source outbox.

## 6. Gate 20 — Firebase identity and entitlement acceptance

Use a real owner-controlled Firebase project configured without enabling paid services for this test. Do not place tokens or service-account material in the repository or chat.

Required cases:

| Case | Expected result |
|---|---|
| Valid signed token, correct project/audience | Identity accepted and scoped ticket issued |
| Expired token | HTTP authentication rejection; no ticket |
| Revoked token | Rejected according to the configured revocation-check policy |
| Wrong project/audience/issuer | Rejected; no ticket |
| Malformed/oversized token | Rejected without leaking parser details |
| Entitlement absent | Subscription denied with the documented authorization close behavior |
| Entitlement revoked during session | Renewal/subscription recheck denies continued access |
| Renewal ticket for another subject | Existing socket closes with 4401 |
| Identity provider unavailable | Fail closed; no unverified identity or ticket |

Record project ID/audience as non-secret identifiers only. Redact user identifiers and all tokens from evidence.

## 7. Browser and Android WebView acceptance

### Browser

- Verify initial foreground connection, ticket exchange, authentication, snapshot, replay and live update.
- Verify heartbeat and ticket renewal across a session that exceeds one ticket TTL.
- Hide the document: current stream must stop and stale snapshot must no longer be eligible for indicator calculations.
- Restore visibility: obtain a fresh identity token, create a new connection and establish a fresh validated snapshot/watermark.
- Toggle offline/online and verify the same recovery contract.
- Verify unmount/owner stop cancels reconnect timers and listeners.

### Android WebView

Run on the actual supported Android device/WebView version, not only jsdom:

- cold start and foreground connect;
- background the app long enough for WebView timer suspension;
- return to foreground and confirm a fresh connection/snapshot rather than trusting the old socket;
- switch Wi-Fi/mobile network and recover;
- lock/unlock the device;
- rotate/recreate Activity if supported by the app;
- verify no duplicate stream owner, no stale candle series, no duplicate event application and no runaway reconnect loop;
- verify logs do not contain bearer tokens, WebSocket tickets, Firebase ID tokens or Redis credentials.

Record Android version, WebView package/version, app build SHA, test timestamps, close codes, reconnect count and result. Do not collect personal account data in the evidence bundle.

## 8. Evidence record and closure rules

For each test, retain:

- test ID and UTC timestamp;
- application commit/build identifier;
- redacted host/runtime role identifier;
- gateway replica ID and snapshot generation where relevant;
- expected result and observed result;
- relevant close code, cursor, event ID and duration;
- pass/fail and operator sign-off;
- sanitized log excerpt or screenshot with secrets and personal data removed.

A gate can be marked green only when every mandatory case for that gate has a passing evidence record. A failed or unexecuted case remains open. Do not convert a CI pass, mock, local test, or documentation checklist into production acceptance.

### Gate 36 closure

Requires WSS-01 through WSS-10 plus browser and Android WebView cases to pass on the intended public host.

### Gate 25 closure

Requires Redis TLS/ACL, secret rotation, snapshot digest/installation receipts for every required gateway, independent consumer-group fan-out, persistence restart, outage recovery, pending reclaim and failover acceptance.

### Gate 20 closure

Requires real Firebase signed-token and entitlement cases, including expiry, revocation, wrong project and renewal subject binding.

### Gate 10 accounting

Gates 20, 25 and 36 remain OPEN until their owner-host evidence is reviewed. Gates 31 and 38 have separate off-host backup and monitoring/recovery acceptance requirements. Gates 8, 30, 34, 35 and 39 remain host/operator-verification tracks. No gate is closed by this document.

## 9. Work-cycle decision

- No runtime source patch was made: the audited repository matrix already covers the code-controlled protocol failures; the remaining blockers require owner-host and physical-client evidence.
- No duplicate synthetic tests were added merely to increase test counts.
- No Vercel/Cloudflare deployment, paid service, production credential access, Termux command or `main` modification occurred.
- No WebSocket completion percentage is invented. Repository/CI status and production acceptance are tracked separately.

## 10. Indicator progress reference — unchanged by this backend cycle

No indicator calculation, shared hook, chart renderer, indicator UI or indicator test changed in this cycle. Indicator progress credit is therefore **zero** for this batch.

The authoritative complete formula/warm-up/remaining-work ledger remains:
`docs/INDICATOR_PROGRESS_LEDGER.md`.

Current indicator states:
- SMA20 🟨 — calculation foundation; renderer, overlay, toggle, legend and stale clearing remain.
- EMA20 🟨 — SMA-seeded EMA foundation, alpha 2/21; renderer and lifecycle remain.
- RSI14 🟨 — Wilder smoothing foundation; 0–100 pane and 30/70 guides remain.
- MACD 12/26/9 🟨 — MACD valid from index 25, signal/histogram from index 33; pane/renderer remain.
- Bollinger20,2 🟨 — population SD foundation; three-line overlay remains.
- Shared Indicator Hook 🟨 — validated aligned snapshot foundation; chart identity/lifecycle integration remains.
- Footprint 🟧 — educational simulation only; reference image and approved blueprint required before visual implementation.
- Heatmap 🟥 — not implemented; zero-cost source feasibility, reference and approved blueprint required.
- Liquidation Maps 🟥 — not implemented; validated zero-cost data/calculation contract required.

Shared invariants: warm-up values are null, never zero; candle-index alignment; no future-candle repaint; stale series cleared on identity/timeframe changes. Footprint OFF retains normal candle spacing; explicit ON alone enables spaced clusters.

No overall project or aggregate indicator percentage is assigned without approved stage weights and denominators.

## 11. Reconciliation against existing multi-process CI evidence (Batch 62J-25 / 62J-31)

The following repository-side acceptance is **already implemented and CI-verified** and must not be misreported as missing:

### Two independent ASGI gateways and live fan-out

Batch 62J-25 runs two independent Uvicorn/FastAPI operating-system processes. Each process owns a separate replica SQLite database, Redis client and consumer identity while reading the same Redis 7 stream. Both real WebSocket clients authenticate and subscribe through `/ws/market-data`; one source event is appended once; both clients receive the same durable cursor and both replica checkpoints advance. The test also verifies cursor-0 snapshot delivery and cursor-0-to-1 reconnect replay through the actual route.

### Dual-gateway Redis TCP interruption and snapshot-generation replacement

Batch 62J-31 adds two repository/CI scenarios:

- Each gateway's established Redis TCP path is independently severed and reconnect attempts are rejected during a controlled outage. Both paths are restored without restarting either ASGI process. Both clients receive cursor 1 and both durable replica checkpoints converge to cursor 1.
- Two independently identified replica databases install the same verified snapshot generation at cursor 2. New generation-scoped consumer processes apply cursor 3 on both replicas. Old pending entries remain isolated in the old groups; new groups have no pending entries.

These tests establish cross-process fan-out, reconnect/replay, controlled TCP-path recovery, and coordinated snapshot-generation behavior **inside the defined CI topology**.

They do **not** establish a Redis server shutdown/failover, public-host network recovery, production snapshot distribution, real production TLS/ACL rotation, Android WebView acceptance, or public WSS readiness.

### Redis ACL and persistence evidence boundary

The CI Redis 7 integration tests exercise separate least-privilege publisher/gateway ACL identities, allowed and denied command/key scopes, consumer-group operations, leases, publish/consume/replay and DB-0 restrictions. The container smoke also verifies AOF/ACL-file persistence for the shared guard Redis service across container restart.

Do not conflate that shared-guard Redis smoke with the dedicated OHLCV relay's production persistence/failover acceptance. The latter remains host-bound.

## 12. Runtime activation boundary — exact reason production cannot be declared complete

The repository has fail-closed builders:
- `build_source_publisher_runtime_factory()` in `backend/app/ohlcv_redis_runtime.py`;
- `build_gateway_replica_runtime_factory()` in `backend/app/ohlcv_redis_gateway_runtime.py`.

They validate distinct publisher/gateway ACL identities, production `rediss://`, snapshot source/generation/cursor/SHA-256 evidence, and gateway installation metadata. The source builder additionally requires matching installation receipts from every required gateway before creating the Redis publisher client.

The FastAPI app accepts these as explicit owner-injected `publisher_runtime_factory` and `replica_runtime_factory` dependencies. They are intentionally **not silently activated by environment variables alone**: the owner must provide an authenticated snapshot verifier/installer and prove that every gateway has installed the same authoritative snapshot. No generic code path can safely invent that trust relationship.

Therefore the exact production activation blockers are:
1. No owner-controlled authenticated snapshot transport/installer and receipt authority is available in this repository checkpoint.
2. No production publisher/gateway Redis host, DNS name, TLS chain, ACL credentials or rotation evidence is available here.
3. No intended public HTTPS/WSS hostname and reverse-proxy endpoint is available for end-to-end acceptance.
4. No physical Android WebView session against that public endpoint has been performed.

These are not solved by adding a mock, hardcoding credentials, or enabling the relay with an unverified environment flag. Such a change would weaken the fail-closed design.

## 13. Current disposition after reconciliation

- Repository-side multi-process fan-out and controlled TCP recovery: **PASS for the documented CI scenarios**.
- Repository-side publisher/gateway runtime factories and snapshot receipt validation: **IMPLEMENTED; owner callback and host activation still required**.
- Public WSS / TLS / proxy / certificate renewal: **NOT ACCEPTED**.
- Dedicated production Redis persistence/failover/secret rotation: **NOT ACCEPTED**.
- Real browser and Android WebView acceptance: **NOT ACCEPTED**.
- No source code was changed in this reconciliation. No production gate is closed by the documentation update.


## 14. Batch 62J-107 — authentication documentation reconciliation (22 November 2026)

A source-to-documentation check found that `backend/README.md` still claimed the one-use WebSocket-ticket exchange was not implemented and documented direct Firebase-token authentication as the current handshake. This was stale. The current source exposes `POST /v1/auth/websocket-ticket`, issues a purpose-bound 90-second ticket, consumes it on the WebSocket handshake, and permits direct-token WebSocket fallback only outside production. The repository includes ticket lifecycle and renewal failure-matrix tests.

The README was corrected to describe the HTTP Bearer-token exchange and the one-use ticket frame, while explicitly preserving the production requirements for shared Redis-backed ticket storage. No runtime source, client source, tests, or indicator code changed. No CI run was triggered; prior CI evidence remains tied to its recorded source/test HEAD.

This correction closes no production gate. Gate 20 still needs real Firebase-project token/revocation/entitlement E2E; Gate 25 still needs owner-host Redis TLS/ACL, persistent failover and verified snapshot distribution; Gate 36 still needs public HTTPS/WSS, reverse-proxy and browser/Android WebView acceptance. Full indicator matrix and exact progress remain in `docs/WORK_CYCLE_2026-11-22_BATCH62J107_WEBSOCKET_AUTH_DOC_RECONCILIATION.md` and `docs/INDICATOR_PROGRESS_LEDGER.md`.


## 15. Batch 62J-108 — regression guard for ticket documentation (22 November 2026)

Added `backend/tests/test_websocket_documentation_contract.py` to assert that the README's documented HTTP ticket endpoint, Firebase Bearer exchange, one-time auth frame, TTL and non-production direct-token compatibility remain aligned with the backend source. This prevents recurrence of the documentation drift recorded in Batch 62J-107. The test is repository-side only and does not establish real Firebase, production Redis, public WSS, or Android WebView acceptance. No indicator implementation changed and no indicator progress credit is awarded. CI must be checked against the exact batch commit before this test is called passing.
