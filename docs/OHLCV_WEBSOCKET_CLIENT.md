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

## Recovery and safety

- Duplicate, stale, wrong-stream, wrong-series, malformed, or skipped-sequence events are not applied.
- A sequence gap fails the session and closes the socket. The caller must reconnect and receive a new atomic snapshot; the client does not silently skip missing updates.
- Server-directed close (including slow-client queue overflow) requires a fresh connection and snapshot.
- Contract/timeframe changes must close the previous connection before opening a new one.
- No provider credentials are sent to the browser. The only credential passed to the socket is the short-lived verified user identity token.
- Transport callbacks receive validated snapshots and chart-boundary candle numbers. Exact decimal strings and nanosecond timestamps remain strings until the existing chart adapter converts them.

## Not yet complete

- Deployed browser/device verification against a test backend with Firebase identity and instrument entitlement configured.
- Network/visibility transition behavior and operational heartbeat/timeout validation.
- External provider credentials, exchange entitlements, and actual provider delivery remain unverified and are not enabled by this client integration.

The transport and its unit tests establish code-level integration only; they do not prove that the deployed frontend is receiving live exchange market data.


## Shared-store incremental update boundary

`src/services/marketDataStore.ts` now exposes `publishMarketDataUpdate({ identity, bar })` as the application-state boundary for one validated candle update.

- Call it only after `connectOhlcvStream` has validated the event and its per-stream sequence guard has accepted the next sequence.
- It requires the exact currently active backend series identity. Updates are rejected while the store is in DEMO, loading, unavailable, or error state.
- A candle with an existing UTC timestamp replaces that candle (supporting open-candle revisions); a new timestamp is inserted in chronological order.
- The resulting full series is revalidated before the immutable snapshot is published to subscribers.
- This is a tested store capability, not yet a claim that the WebSocket transport is wired into the chart or Firebase authentication.
