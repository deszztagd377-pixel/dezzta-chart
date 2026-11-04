# DEZZTA CHART — WebSocket client authentication design gate

## Current verified state

- The backend route `/ws/market-data` currently compares an initial JSON auth-frame token against the server-side `MARKET_DATA_WS_TOKEN` using constant-time comparison.
- The token is a single static backend secret. It is not a user session, is not scoped to one instrument, and has no expiry or rotation protocol.
- The current frontend has no WebSocket client and no login/session provider.
- The static token must never be placed in `VITE_*` variables, frontend source, local storage, a public config endpoint, or an Android package.
- CORS/Origin validation is defense in depth, not authentication. Native clients may not send an Origin header, so the backend must still require valid credentials.

## Additional security finding from the current backend audit

The current route validates that the requested series identity is syntactically well-formed and uses the configured dataset, but it does not yet prove that the authenticated principal is entitled to the requested publisher/instrument/raw-symbol/timeframe tuple. The current shared static token has no principal identity or per-series claims. Before any production client is connected, authorization must be enforced against verified instrument definitions and the user's granted data entitlements. Do not treat a valid token alone as permission to subscribe to every series.

The current route also accepts a missing Origin header. This is necessary for some native clients and is not itself a defect, but it means Origin checks cannot be treated as a security boundary. Require a valid credential and enforce authorization for every subscription.

## Required production properties

1. TLS-only WebSocket transport (`wss://`) outside local development.
2. A separately authenticated app session before token issuance.
3. Short-lived, narrowly scoped access tokens, ideally scoped to the requested data service and authorized series; never a long-lived shared application secret.
4. Server-side signature/issuer/audience/expiry validation, key rotation, and revocation strategy.
5. Rate limits and connection/subscription limits per authenticated identity.
6. No credentials in URLs, logs, telemetry, error messages, or analytics.
7. Explicit authorization for each requested dataset/instrument/timeframe; validating syntactic identity alone is not authorization.
8. Re-authentication on reconnect; the client must obtain a fresh short-lived token rather than persist one indefinitely.

## Architecture options requiring product-owner approval

### Option A — Managed identity provider

Use a managed authentication service to establish the user's app session. The backend verifies that session and mints a short-lived WebSocket ticket. This reduces custom password/session code but introduces a provider, account setup, and possible cost/plan constraints.

### Option B — Server-side gateway / BFF

A trusted server-side gateway authenticates the app session and proxies WebSocket traffic or issues short-lived scoped tickets. No static backend token is exposed to browser JavaScript. This adds hosting and operational complexity.

### Option C — First-party account/session system

Build a backend-owned login/session system with secure cookies or refresh-token rotation, then mint short-lived WebSocket tickets. This gives control but adds substantial security-sensitive implementation and maintenance work; it should not be improvised as a quick patch.

## Recommended implementation boundary

Keep the future frontend stream client transport-neutral and inject an asynchronous `getAccessToken()` function. The client may send only the short-lived token returned by that provider in the first WebSocket auth frame. Do not implement a production token issuer until an authentication architecture is approved and its threat model is reviewed.

The client must validate the server snapshot and its stream ID/watermark before accepting updates. It must apply only the next sequence for the exact selected series. On a gap, queue overflow, reconnect, or series change, it must stop applying updates and obtain a fresh snapshot before resuming. All accepted updates must flow through the shared `marketDataStore`; indicators must not open their own sockets.

## Not yet approved or implemented

- No managed identity provider has been selected.
- No user login/session system or token-exchange endpoint exists.
- No short-lived WebSocket ticket format or signing-key lifecycle exists.
- No authenticated-principal-to-series authorization check exists in the WebSocket subscription path.
- No frontend WebSocket client, reconnect loop, or stream-to-store update path exists.
- No public deployment or real provider feed is verified.

Do not enable production frontend streaming until the authentication decision and its tests are complete.


## 2026-11-04 implementation update — Firebase WebSocket authentication

- The first `auth` frame now carries a Firebase ID token. The backend verifies it through the approved `FirebaseIdentityVerifier` (including Firebase Admin's revoked-token check) in a worker thread. Invalid tokens close with 4401; unavailable identity verification fails closed with 1013.
- Each subscription must include `canonicalInstrumentId` as well as the exact provider series identity.
- Before taking a snapshot, the server resolves the provider/dataset/publisher/instrument mapping at the current time, checks the mapped raw symbol and canonical ID, confirms that the canonical instrument is active, and checks the verified principal's explicit entitlement. Missing, expired, mismatched, inactive, or ungranted mappings are denied with 4403.
- Mapping and entitlement are rechecked every 60 seconds during an active subscription. Revoked access or a mapping change closes the connection; the client must authenticate and subscribe again.
- The snapshot/watermark handoff and bounded stream queue remain unchanged after authorization succeeds.
- The legacy `MARKET_DATA_WS_TOKEN` setting remains for configuration compatibility, but the WebSocket route no longer reads or accepts it.

## Remaining integration gates

- The frontend still has no Firebase sign-in/session UI and no WebSocket client. It must obtain a Firebase ID token through the approved app-auth flow, then send that token in the initial auth frame and include the verified canonical instrument ID in each subscription.
- Verified futures-definition ingestion must populate canonical instruments and point-in-time provider mappings before a user can be granted access to a contract. The offline ES/NQ/GC fixture is not sufficient to authorize a live subscription.
- No production Firebase project credentials, real user session, provider feed, deployed backend, or end-to-end client connection has been validated in this change.
- A long-lived connection is rechecked for instrument entitlement and mapping every 60 seconds. Firebase token expiry/revocation during an established connection still requires a bounded connection-lifetime/re-authentication policy before production deployment.
