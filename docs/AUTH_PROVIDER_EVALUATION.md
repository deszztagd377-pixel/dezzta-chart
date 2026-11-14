# DEZZTA CHART — Managed authentication provider evaluation

Audit date: 2026-11-02
Working branch: `phase-2/market-data-foundation`

## Decision scope

The project owner approved the architecture direction: managed user authentication, backend verification of the user session, and a short-lived WebSocket ticket issued by the backend. This approval does **not** select or authorize deployment of a specific identity vendor.

The identity provider authenticates the account. It does not supply market data, guarantee feed accuracy, or replace the backend's per-series authorization. The backend remains responsible for verifying each requested dataset, publisher, instrument, raw symbol, and timeframe against trusted instrument definitions and the user's entitlements.

## Candidate comparison

| Candidate | Useful fit | Important limitations / operational notes |
|---|---|---|
| Firebase Authentication | Web and Android client SDKs; Firebase Admin SDK for Python can verify ID tokens and optionally check revocation. Most Authentication options are included in the no-cost Spark plan. | Firebase ID tokens last about one hour; refresh tokens maintain sessions and can be revoked. The backend must still exchange a verified ID token for a separate, narrowly scoped WebSocket ticket. Phone/SMS auth has separate billing. |
| Supabase Auth | JWT-based sessions; asymmetric signing keys and JWKS support; Python client has a verified-claims flow. Free tier currently includes 50,000 MAU. | Free projects can pause after a week of low activity. The documented Free plan is suitable for development/testing, not a dependable always-on production dependency without a paid plan or an alternate operational arrangement. |
| Clerk | Managed sign-in UI and JWT templates; custom template token lifetime defaults to 60 seconds; Hobby currently advertises a free tier up to 50,000 monthly retained users. | Hobby has a fixed 7-day session lifetime; advanced inactivity/maximum-lifetime controls require a paid production plan. Adds a distinct provider-specific session model. |

## Current recommendation — Firebase Authentication as first candidate

Firebase Authentication is the leading candidate for the next implementation spike because the application targets both a React web client and a future Android app, while the current backend is Python/FastAPI. Firebase documents first-party Android and web token retrieval, and its Python Admin SDK verifies token signature, issuer, project, expiry, and optionally revocation. The Spark plan currently includes most Authentication options without requiring payment information.

The project owner approved Firebase Authentication as the primary provider for the authentication prototype on 2026-11-02. This approves the prototype direction, not production launch, billing, or credential provisioning. Before implementation, verify the exact sign-in methods, account recovery, age-appropriate account setup, regional/legal requirements, quotas, billing settings, and the current terms/pricing. Do not enable phone/SMS sign-in by default. Do not add a billing account or paid plan without the project owner's explicit approval.

Official references:
- Firebase pricing and Spark/Blaze plans: https://firebase.google.com/pricing
- Firebase ID-token verification, including Python: https://firebase.google.com/docs/auth/admin/verify-id-tokens
- Firebase session lifetime and revocation: https://firebase.google.com/docs/auth/admin/manage-sessions
- Supabase pricing: https://supabase.com/pricing
- Supabase Free project pausing: https://supabase.com/docs/guides/platform/free-project-pausing
- Supabase session and access-token lifetime: https://supabase.com/docs/guides/auth/sessions
- Clerk pricing: https://clerk.com/pricing
- Clerk JWT templates and token lifetime: https://clerk.com/docs/guides/sessions/jwt-templates

## Approved prototype provider

Use Firebase Authentication for the first prototype behind a provider-neutral `IdentityVerifier` interface. The backend must accept only Firebase client ID tokens, verify them using the Admin SDK with the configured project ID, and resolve a stable Firebase UID. Add tests for malformed, expired, wrong-project/audience, disabled, and revoked identities. Revocation checks should be applied at the appropriate session/token-exchange boundary with an explicit performance policy; do not assume signature validation alone detects revocation.

Do not commit service-account JSON or any Firebase private key. Use a managed secret store or protected backend environment configuration in deployment. Do not add a `VITE_*` secret. Do not configure billing or enable paid services without explicit approval. Keep provider-specific code isolated so a future provider migration does not change the market-data authorization contract.

## Required token-exchange architecture

1. The frontend obtains a user ID token from the managed identity SDK. It never receives a backend signing secret.
2. The frontend sends that ID token to a backend HTTPS endpoint. The backend verifies signature, issuer, audience/project, expiry, and revocation policy using the provider's supported verification mechanism.
3. The backend resolves the authenticated principal and checks account state and server-side entitlements.
4. The backend issues a short-lived WebSocket ticket for the exact allowed data service and series. The ticket must have a narrow audience, expiry, subject, unique identifier, and explicit series scope.
5. The WebSocket endpoint verifies the ticket's signature, issuer, audience, expiry, and scope before accepting a subscription. It must independently verify that the series is a current verified instrument and that the principal is entitled to it.
6. The ticket is never stored as a long-lived credential, placed in a URL, written to logs, or embedded in the app bundle. Reconnect obtains a new ticket.
7. Rate limits, connection limits, replay protection, signing-key rotation, revocation strategy, and audit-safe logs are required before production.

The identity-provider access token and the WebSocket ticket are separate credentials with different purposes and lifetimes. A valid user token alone must not authorize every market-data series.

## Longevity and data continuity requirements

Managed authentication alone cannot make the whole application reliable for years. Production readiness also requires:
- Durable database storage for verified instrument definitions, user entitlements, and required application state.
- Durable OHLCV storage or a provider-backed historical recovery path; in-memory-only bars are not sufficient.
- Snapshot plus sequence-aware stream recovery after network loss, backend restart, queue overflow, or provider reconnect.
- Automated backups, tested restore procedures, retention policy, and documented recovery objectives.
- Provider entitlement/licensing review, source-event and receive timestamps, freshness/staleness alarms, gap detection, and explicit degraded/unavailable states.
- Dependency/security updates, secret rotation, monitoring, incident procedures, and export/migration paths to reduce vendor lock-in.
- Separate health checks for service liveness, auth, provider connection, instrument definitions, data freshness, and stream continuity.

No vendor or architecture can promise zero downtime or permanent accuracy. The engineering target is detectable failure, safe recovery, traceable data provenance, and no silent presentation of stale/demo data as live.

## Implementation gate

Do not replace the static `MARKET_DATA_WS_TOKEN` with a browser-visible token or start production frontend WebSocket integration yet. The next implementation step is to prototype the selected identity provider behind a provider-neutral backend interface, add unit tests for valid/expired/wrong-audience/revoked identities, then implement scoped ticket issuance and per-series authorization. The provider choice must be explicitly confirmed before adding vendor SDKs or credentials.

No credentials, provider secrets, user data, or billing configuration are stored in this document.
