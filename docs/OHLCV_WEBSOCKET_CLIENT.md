# OHLCV WebSocket client transport

## Current scope

`src/services/ohlcvWebSocketClient.ts` implements the authenticated client-side transport for the backend `/ws/market-data` endpoint. It is deliberately a transport service, not yet wired into `CandlestickChart`: the current application does not yet provide a verified Firebase identity-token lifecycle to this component. Do not pass a placeholder token or enable unauthenticated subscriptions.

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

- Firebase client SDK integration and verified token refresh.
- Wiring the transport into the chart lifecycle and merging updates by candle timestamp.
- Reconnect backoff, visibility/network awareness, and UI connection-state presentation.
- End-to-end browser/device verification against a deployed backend with configured Firebase identity, instrument entitlement, and live Databento data.

The transport and its unit tests do not claim that the frontend is receiving live market data today.
