# OHLCV WebSocket client transport

## Current scope

`src/services/ohlcvWebSocketClient.ts` implements the authenticated client-side transport for the backend `/ws/market-data` endpoint. It is wired into the chart lifecycle through `src/services/ohlcvStreamSupervisor.ts` and `CandlestickChart.tsx`. The supervisor obtains a fresh Firebase ID token through the authenticated app session, exchanges it for a short-lived ticket over HTTPS, and uses the ticket for the WebSocket handshake. This is code-level integration only; deployed end-to-end operation and external provider delivery are not verified.

## Handshake

1. Obtain a fresh Firebase ID token from the authenticated app session.
2. Exchange it over HTTPS using `POST /v1/auth/websocket-ticket` with the Bearer Authorization header. The response must contain a `market-data` ticket with `expiresIn: 90`.
3. Connect to the backend origin at `/ws/market-data` using WS/WSS derived from the configured HTTP(S) backend URL.
4. Send `{ type: "auth", ticket }` as the first WebSocket JSON message. The Firebase ID token is never sent in the WebSocket URL or frame.
5. Wait for `market_data.status` and send `market_data.subscribe` version 1 with the exact dataset, publisher ID, instrument ID, raw symbol, timeframe, and canonical instrument ID.
6. Validate the returned `market_data.ohlcv.snapshot` envelope and every bar using the same strict snapshot adapter used by HTTP.
7. Initialize the sequence guard from the server-provided `streamId` and `watermark`.
8. Validate each update and accept only the next sequence number for the exact stream and series.
9. After snapshot or replay completion, send the server's literal text-frame `ping` every 20 seconds and require `market_data.pong` within 10 seconds. Stop heartbeat timers on failure, remote close, or explicit stop.

## Ticket renewal

- The initial and renewal tickets are issued over HTTPS by `POST /v1/auth/websocket-ticket`, protected by Firebase Bearer verification.
- Tickets are purpose-bound to `market-data`, single-use, and expire after 90 seconds.
- The client requests a replacement ticket every 45 seconds by default, sends `{ type: "auth.renew", ticket }`, and requires `market_data.auth.renewed` within 10 seconds.
- The backend consumes the renewal ticket once, verifies it belongs to the same account subject, and rechecks the exact instrument entitlement before acknowledging it.
- Production requires the shared Redis-backed ticket store. The in-memory ticket store is only a non-production fallback.
- The Firebase ID token is sent only over HTTPS, never in a WebSocket URL or frame.

## Recovery and safety

- Duplicate, stale, wrong-stream, wrong-series, malformed, or skipped-sequence events are not applied.
- A sequence gap fails the session and closes the socket. The caller must reconnect and receive a new atomic snapshot; the client does not silently skip missing updates.
- Server-directed close (including slow-client queue overflow) requires a fresh connection and snapshot.
- Backend close code `1008` is a terminal protocol-policy rejection (unsupported client control frame or ping-rate violation). The supervisor marks the stream unavailable and does not reconnect with unchanged behavior; recreate it only after correcting the client policy/configuration or selected session.
- Contract/timeframe changes must close the previous connection before opening a new one.
- No provider credentials are sent to the browser. The only credential passed to the socket is the short-lived verified user identity token.
- Transport callbacks receive validated snapshots and chart-boundary candle numbers. Exact decimal strings and nanosecond timestamps remain strings until the existing chart adapter converts them.
- Idle-session heartbeat uses the server's text protocol (`ping`), not JSON. The default cadence is 20 seconds, below the server's 20-pings-per-10-seconds ceiling; a missing pong times out after 10 seconds and triggers the existing reconnect supervisor.

## Not yet complete

- Deployed browser/device verification against a test backend with Firebase identity and instrument entitlement configured.
- Deployed browser/device verification, Android WebView acceptance, network/visibility transition behavior, and operational heartbeat behavior on the real host. Unit tests now cover heartbeat send, pong acknowledgement, timeout, and timer cleanup.
- External provider credentials, exchange entitlements, and actual provider delivery remain unverified and are not enabled by this client integration.

The transport and its unit tests establish code-level integration only; they do not prove that the deployed frontend is receiving live exchange market data.


## Shared-store incremental update boundary

`src/services/marketDataStore.ts` now exposes `publishMarketDataUpdate({ identity, bar })` as the application-state boundary for one validated candle update.

- Call it only after `connectOhlcvStream` has validated the event and its per-stream sequence guard has accepted the next sequence.
- It requires the exact currently active backend series identity. Updates are rejected while the store is in DEMO, loading, unavailable, or error state.
- A candle with an existing UTC timestamp replaces that candle (supporting open-candle revisions); a new timestamp is inserted in chronological order.
- The resulting full series is revalidated before the immutable snapshot is published to subscribers.
- This is a tested store capability, not yet a claim that the WebSocket transport is wired into the chart or Firebase authentication.


## Vercel Function lifetime and reconnect supervisor — 2026-11-18

Vercel Hobby with Fluid Compute documents a 300-second maximum Function duration. A WebSocket connection is pinned to the Function invocation and is expected to close when that invocation reaches its configured maximum duration. This is a normal lifecycle boundary; a client must recover without losing validated chart state.

The production client already has the core recovery supervisor in `src/services/ohlcvStreamSupervisor.ts`:

- bounded exponential reconnect delay with jitter (default 500 ms minimum and 15,000 ms maximum);
- fresh Firebase ID-token acquisition for each connection attempt;
- durable-cursor resume on the next authenticated subscription;
- chart snapshot preservation while reconnecting;
- replay validation and sequence continuity before returning to live state;
- sequence-gap recovery through a fresh connection and snapshot;
- terminal handling for authentication, authorization, and malformed-subscription close codes (4401, 4403, 4400), avoiding endless retry loops;
- cancellation of pending reconnects when the owner stops the stream.

Existing supervisor tests cover transport interruption and reconnect, fresh token acquisition, cursor replay, sequence-gap recovery, token-provider transient failures, terminal authorization rejection, close/error races, and explicit stop. These are repository-level tests; they do not prove a deployed Vercel 300-second close, native Android WebView behavior, or production cross-instance fan-out.

The isolated synthetic POC currently has a 25-second idle timeout. A passive tab will close from that application timeout long before the Hobby platform maximum. A platform-lifetime test therefore needs synthetic heartbeat traffic below the idle threshold and must capture the final close event. A temporary POC-only 60-second `maxDuration` test cap is proposed but not applied. Keep SSO enabled and do not use production data or credentials.


## Browser network and visibility lifecycle — 2026-11-18

The chart owner now binds supervisor lifetime to browser connectivity and document visibility:

- `offline` or `visibilityState !== "visible"` stops the current supervisor and clears the active backend snapshot from indicator eligibility.
- Returning online while visible creates a new supervisor, obtains a fresh Firebase ID token, and requests a new validated snapshot/watermark.
- The client does not assume that a socket or its heartbeat timers survived background suspension.
- This is browser-source behavior covered by the lifecycle policy unit tests; Android WebView and deployed-host acceptance remain part of Gate 36 and are not inferred from unit tests.


## Browser lifecycle integration coverage — Batch 39

The chart-level lifecycle behavior is now covered separately from the pure lifecycle policy:
- mount while online/visible creates one supervisor;
- offline event stops that supervisor and publishes an unavailable snapshot with an offline reason;
- online event creates a new supervisor;
- hidden visibility stops the current supervisor and publishes an unavailable background reason;
- returning visible creates a fresh supervisor;
- unmount stops the active supervisor.
- An initially offline mount is verified not to create a supervisor until the online event arrives.

These are jsdom integration tests with mocked chart rendering and transport. They verify React effect ownership and event cleanup, not native Android WebView behavior or deployed WSS acceptance.


## Real TLS/WSS transport integration — Batch 62J-145 (22 November 2026)

The backend CI now includes a real loopback TLS/WebSocket integration test. It creates an ephemeral test CA and server certificate, starts Uvicorn with TLS on an OS-selected local port, and uses the websockets client to perform an actual WSS handshake and HTTP Upgrade.

Verified in the test:
- Trusted test CA and certificate SAN validation.
- Allowed HTTPS Origin succeeds; disallowed Origin receives HTTP 403 before WebSocket upgrade.
- Untrusted CA is rejected.
- Authenticated test-mode session can subscribe to the exact series and receive a validated four-bar snapshot.
- Application text ping receives the versioned market_data.pong response.
- Two separately authenticated test identities can subscribe simultaneously; closing one removes only that client's subscription after bounded ASGI cleanup, while the other remains able to ping/pong.

The harness uses the backend's non-production legacy token path and a fake identity verifier. It does not prove the production HTTPS Firebase ID-token → one-time ticket → ticket-authenticated WSS handshake or renewal over TLS. That end-to-end ticket path remains the next test target. It also does not prove a public reverse proxy, deployed DNS/certificate, production Redis, real Firebase, or Android WebView behavior.

Exact source/test HEAD f8e41ad68656e82a82d30cf40f720f3ec98ac337 passed Automated Tests, CodeQL, Full Git History Secret Audit and OCI ARM64 readiness. Backend pytest: 1,297 passed, 1 skipped, 6 warnings. See WORK_CYCLE_2026-11-22_BATCH62J145_REAL_TLS_MULTI_USER_WEBSOCKET.md.
