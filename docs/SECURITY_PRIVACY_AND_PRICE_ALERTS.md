# DEZZTA CHART — Security, Privacy, Drawing Tools, and Price Alerts

Status: approved product requirements; implementation not yet started
Working branch: `phase-2/market-data-foundation`
Baseline commit audited: `7709f49ce526b37585df88410c5c10b4aac3fe6e`

## 1. Security and privacy guard

### Product promise and limits
The product must use defense in depth and privacy by design. It must never claim that an APK is impossible to hack, trace, reverse engineer, or compromise. The goal is to reduce attack surface, prevent unauthorized access, detect abnormal activity, minimize collected data, and recover safely.

### Privacy requirements
- No advertising SDK, cross-app tracking SDK, hidden analytics, device fingerprinting, or collection of contacts/location/IMEI unless a future feature has a clear need, explicit consent, and a documented retention policy.
- Collect the minimum account and operational data required to provide the service.
- Do not log access tokens, refresh tokens, API keys, private user content, or full sensitive request bodies.
- Provide clear controls and a retention/deletion policy for account data and diagnostic logs.
- Explain that network operators, hosting providers, identity providers, and market-data vendors may process connection or service metadata under their own policies; the app cannot promise that no external party can observe any network activity.

### Backend security controls
- Firebase Authentication remains the approved prototype identity provider, behind a provider-neutral identity-verifier interface.
- Verify Firebase ID tokens server-side, including signature, issuer/project audience, expiry, account state, and revocation at the defined exchange boundary.
- Exchange a verified ID token for a short-lived, signed WebSocket ticket. Never ship backend signing keys or provider secrets in the APK, frontend bundle, URLs, or logs.
- Authorize every requested dataset/publisher/instrument/symbol/timeframe against verified instrument definitions and explicit per-user entitlements. Deny by default when entitlement data is absent.
- Use TLS only in production; exact-origin CORS; strict request validation; bounded message sizes, queues, subscriptions, and connection counts; per-user/IP rate limits; replay protection; signing-key rotation; and safe error responses.
- Add security headers for HTTP responses, dependency and container scanning, secret scanning, audit-safe security events, backup/restore tests, and incident response procedures.
- Protect Android credentials using platform-supported secure storage; never store provider keys in the APK. Use release signing, dependency updates, and obfuscation as defense-in-depth, not as a substitute for server authorization.
- Do not expose debug endpoints, stack traces, internal database paths, or secrets in production responses.

### Data Guard / anti-tracking acceptance criteria
- No third-party tracking or advertising SDKs by default.
- No hidden device fingerprinting or unnecessary permissions.
- Network requests are limited to documented service endpoints; privacy-sensitive telemetry is opt-in or disabled.
- User data is encrypted in transit; persistent production storage must use provider-supported encryption at rest and tested backups.
- The service distinguishes liveness, authentication, provider connectivity, data freshness, and stream continuity. A green health check must not imply that market data is live.

### Current gaps from audit
- WebSocket authentication currently uses one shared static backend token; it is not a user session and has no user/series entitlement scope.
- A Firebase Admin verifier abstraction now exists and requests revoked-token checking, but production credentials/project configuration and live Firebase integration have not been verified. There is still no user entitlement store, scoped ticket issuer, or rate-limit layer.
- Existing backend storage and market-data stream state are not yet a complete multi-instance durable production system.
- The current APK/web build must not be described as hardened or production-secure until these controls are implemented and tested.

### Identity verifier implementation checkpoint\n- `backend/app/identity.py` implements a provider-neutral verified principal and Firebase Admin ID-token verifier. It fails closed when the project is not configured, requests revocation checking, validates issuer/audience/subject/auth_time claims, and normalizes SDK failures.\n- The verifier is initialized in backend application state but is not exposed through a public authentication endpoint yet. No client-supplied owner ID is trusted by an API because alert CRUD routes remain disabled.\n- Firebase Admin uses Application Default Credentials in the backend environment. Never commit a service-account JSON file or embed Firebase Admin credentials in the frontend/APK.\n- Before enabling endpoints, configure the correct Firebase project and workload identity/ADC, verify a real token in a controlled environment, and add endpoint-level authorization tests.\n\n## 2. Chart interaction and horizontal drawing tool

### Interaction
- Crosshair/touch interaction displays the selected candle's time and OHLC values, with the selected price clearly aligned to the right price scale.
- A compact `+` drawing action creates a horizontal price line at the selected crosshair price.
- Horizontal line style choices: solid, dashed, dotted. Style changes must update the actual chart primitive, not just a decorative control.
- Users can select, move, restyle, hide/show, and delete their own horizontal lines.
- Drawing coordinates must remain correct through zoom, pan, timeframe changes, and chart resize.
- Drawings are associated with canonical instrument identity, not just a display ticker. No drawing should silently transfer to a different venue's same-named instrument.
- Persist locally first; account sync may be added only after authenticated ownership and durable storage exist.

### Technical constraints
- Use Lightweight Charts v5 supported price-line/series APIs; do not fake a horizontal line with DOM overlays.
- Keep chart lifecycle cleanup correct: remove subscriptions and primitives on teardown; avoid duplicate event handlers.
- Preserve normal candle spacing when Footprint is OFF. Footprint ON may use its separate cluster-spacing layout only when that feature is implemented.
- Crosshair labels must use the chart's actual price/time coordinate conversion and the active series price formatter.

## 3. Price-zone alerts

### Product behavior
- User can create at most **five saved alert zones across the entire account**, shared globally by all instruments/pairs and venues. Example: 2 zones on XAUUSD + 3 zones on BTCUSD = 5 total; a sixth zone on any pair is rejected server-side.
- A zone is a price interval with lower and upper bounds, associated with one canonical instrument and venue. A point alert can be represented by equal bounds plus a configured tick tolerance, but must not be silently treated as a broad range.
- Trigger when a verified incoming market price enters the zone. Record the event once per entry; re-arm only after price leaves the zone, with explicit duplicate suppression and cooldown policy.
- Notify the user on Android through push notifications when the app is backgrounded or closed. In-app/local notifications are supplemental, not the only delivery mechanism.
- Alert payloads identify instrument, venue, zone, trigger price, source timestamp, and event time. Do not include secrets.
- Alerts are notification-only; they must never place, route, or execute trades.

### Required architecture
- Persist alert definitions and delivery state in a durable backend database.
- A continuously running backend worker evaluates alerts against verified provider events; it must not rely on the phone keeping the app open.
- Use Firebase Cloud Messaging for Android push delivery after account/device-token registration and explicit notification permission.
- Validate and deduplicate source events; handle reconnects, delayed/out-of-order data, provider gaps, and stale feeds. Do not trigger from demo candles or stale data.
- Show alert status such as active, paused, triggered, delivery failed, or data unavailable. If feed freshness is outside the configured threshold, pause evaluation and report the reason rather than silently triggering.
- Enforce the five-zone account-wide limit server-side in the same transaction as zone creation, not only in the UI. Count every non-deleted saved zone regardless of instrument or state (active, paused, triggered, or delivery-failed); only explicit deletion frees a slot. Protect ownership and CRUD operations with authenticated authorization.

### Server requirement
A backend is required for dependable alerts while the APK is closed. Push delivery also requires a push service and valid Android app configuration. Local-only alerts cannot guarantee background monitoring or delivery.

## 4. Implementation order and release gates

1. Security baseline: threat model, privacy inventory, dependency/secret checks, secure headers, request limits, rate limiting, and safe production configuration.
2. Firebase identity verification and provider-neutral principal interface.
3. Durable user entitlement and alert storage; enforce the account-wide five-zone quota atomically across all pairs; deny-by-default authorization.
4. Short-lived scoped WebSocket tickets, revocation policy, per-series authorization, replay protection, and connection limits.
5. Crosshair OHLC/price-scale readout and horizontal-line drawing controls with interaction tests.
6. Server-side alert evaluator, event deduplication/re-arm behavior, FCM registration and delivery, and failure-state tests.
7. Android permission, background/closed-app delivery, device testing, security review, backup/restore drill, and release signing.

No production security or alert-delivery milestone is complete merely because a design document or unit test exists. Every stage must be implemented, tested, and independently verified before progress is credited.
