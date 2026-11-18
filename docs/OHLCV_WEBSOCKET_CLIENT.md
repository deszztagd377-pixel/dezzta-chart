# OHLCV WebSocket client transport

## Current scope

`src/services/ohlcvWebSocketClient.ts` implements the authenticated client-side transport for the backend `/ws/market-data` endpoint. It is wired into the chart lifecycle through `src/services/ohlcvStreamSupervisor.ts` and `CandlestickChart.tsx`. The supervisor obtains a Firebase ID token through the authenticated app session for each connection attempt. This is code-level integration only; deployed end-to-end operation and external provider delivery are not verified.

## Handshake

1. Connect to the backend origin at `/ws/market-data` using WS/WSS derived from the configured HTTP(S) backend URL.
2. Send `{ type: "auth", token }` with a verified Firebase ID token.
3. Wait for `market_data.status` and send `market_data.subscribe` version 1 with the exact dataset, publisher ID, instrument ID, raw symbol, timeframe, and canonical instrument ID.
4. Validate the returned `market_data.ohlcv.snapshot` envelope and every bar using the same strict snapshot adapter used by HTTP.
5. Initialize the sequence guard from the server-provided `streamId` and `watermark`.
6. Validate each update and accept only the next sequence number for the exact stream and series.
7. After snapshot or replay completion, send the server's literal text-frame `ping` every 20 seconds and require `market_data.pong` within 10 seconds. Stop heartbeat timers on failure, remote close, or explicit stop.

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
