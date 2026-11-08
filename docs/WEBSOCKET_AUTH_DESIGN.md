# DEZZTA CHART — WebSocket client authentication design gate

## Current verified state — audited 2026-11-08

- The backend route `/ws/market-data` authenticates the first JSON frame with a Firebase ID token through `FirebaseIdentityVerifier`; it no longer accepts the legacy `MARKET_DATA_WS_TOKEN` setting.
- Firebase Admin verification requests revocation checking and validates the expected project issuer/audience and required identity claims. Unit tests use an injected verifier/fake Admin SDK; a real Firebase-project signed-token E2E has **not** been completed.
- The React root is wrapped in `AuthProvider`. An `AuthPanel` component exists, but `App.tsx` does not currently render it; therefore a complete user-facing sign-in journey is not yet integrated into the visible app.
- The frontend contains an authenticated WebSocket client and stream supervisor. The chart integration obtains Firebase ID tokens, requests a fresh token on reconnect, validates snapshot/watermark and sequence continuity, and publishes accepted data through the shared market-data store. This is code-level integration, not proof of a deployed backend/provider connection.
- The legacy static token must never be placed in `VITE_*` variables, frontend source, local storage, a public config endpoint, or an Android package.
- CORS/Origin validation is defense in depth, not authentication. Native clients may not send an Origin header, so the backend must still require valid credentials.

## Additional security finding and current authorization boundary

The current subscription path resolves the provider/dataset/publisher/instrument mapping, validates the mapped raw symbol and canonical instrument ID, confirms the canonical instrument is active, and checks the verified principal's explicit entitlement before sending a snapshot. Mapping and entitlement are rechecked every 60 seconds during an active subscription; authorization drift closes the connection.

The route also accepts a missing Origin header. This is necessary for some native clients and is not itself a defect, but it means Origin checks cannot be treated as a security boundary. Require a valid credential and enforce authorization for every subscription.

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

## Remaining security and integration gates

- A real Firebase project and authorized test accounts must be used to verify valid, expired, revoked, and wrong-project signed tokens end to end. Existing injected-verifier tests are not a substitute.
- The `AuthPanel` is not mounted by `App.tsx`; integrate and test the visible sign-in/session experience before claiming an end-user authentication flow.
- The client currently sends Firebase ID tokens directly in the initial WebSocket auth frame. A separate short-lived, narrowly scoped WebSocket ticket and signing-key lifecycle have not been implemented; decide whether this additional exchange is required by the production threat model before deployment.
- A long-lived connection is rechecked for instrument entitlement and mapping every 60 seconds. Firebase token expiry/revocation during an established connection still requires a bounded connection-lifetime/re-authentication policy.
- No public backend deployment, real provider feed, or end-to-end client connection against production infrastructure is verified.

Do not enable production frontend streaming until the real-token E2E, visible auth flow, connection-lifetime policy, TLS deployment, and operational controls have been reviewed and tested.


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
