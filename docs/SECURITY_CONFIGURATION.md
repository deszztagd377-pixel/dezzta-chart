# DEZZTA CHART — Security Configuration Baseline

This document records the current security controls and remaining release checks.
It is not a certification or a claim that the application is production-secure.

## 1. Public frontend configuration

Vite variables prefixed with `VITE_` are compiled into browser-delivered code.
Treat every such value as public and inspect the production bundle before release.

Allowed examples:
- `VITE_MARKET_DATA_API_BASE_URL`: public backend origin; not a credential.
- Non-sensitive UI feature flags.

Never place provider API keys, Firebase Admin private keys, database credentials,
signing secrets, or backend-only tokens in frontend source, `VITE_*` variables,
URLs, browser storage, or client logs.

Firebase client configuration is not an Admin credential. Admin credentials must
remain server-side and must never be packaged into the browser app or Android APK.

## 2. Backend secret handling

- Keep provider credentials in a deployment secret manager or protected runtime
  environment.
- Prefer workload identity / Application Default Credentials for Firebase Admin.
  If a service-account key is unavoidable, restrict and rotate it.
- Never commit runtime `.env` files, service-account JSON, SQLite databases,
  private keys, or credential backups.
- Never log ID tokens, provider keys, Authorization headers, or secret objects.
- Return generic authentication errors to clients; protect detailed diagnostics.

## 3. Transport and authentication

- Production deployments must use HTTPS and WSS.
- Environment-loaded CORS configuration accepts only exact bare HTTP(S)
  origins; wildcard origins, paths, credentials, query strings, fragments, and
  malformed origins are rejected. When `APP_ENV=production`, every configured
  CORS origin must use HTTPS. This is configuration validation, not a substitute
  for deployment-side HTTPS/WSS and Origin smoke tests.
- Keep the WebSocket Origin allowlist explicit. Origin checks supplement, but do
  not replace, token verification.
- In `APP_ENV=production`, startup requires both a TLS `REDIS_URL` and a non-empty `FIREBASE_PROJECT_ID`; the backend refuses to start with an incomplete identity-verification configuration.
- `FIREBASE_PROJECT_ID` identifies the Firebase project and is not an Admin credential. The Firebase Admin SDK must still obtain valid server-side application credentials through the deployment runtime.
- HTTP authentication uses a Firebase Bearer ID token verified by the backend.
  The `GET /v1/ohlcv` route also resolves the exact provider mapping and checks
  that the verified account has an entitlement for the active canonical
  instrument.
- The authenticated OHLCV snapshot endpoint bounds identifier ranges and query-string field lengths (dataset, symbol, timeframe, provider metadata, nanosecond timestamps, and response limit) before handler execution. These input bounds reduce oversized or malformed query work; they are not request-rate limiting.
- OHLCV `start_ns` and `end_ns` values are also capped at the maximum signed 64-bit integer (`9223372036854775807`), matching the timestamp range supported by the backend's integer storage contract. A 19-digit value above that limit is rejected with HTTP 422 rather than being passed into query/storage code.
- The WebSocket subscription path independently verifies Firebase identity and
  checks instrument entitlement. Do not weaken either path to make them match.
- The authenticated OHLCV WebSocket accepts only the documented `ping` client message after subscription. It closes connections that exceed 20 pings in a rolling 10-second window or send an unsupported client message. The container's Uvicorn command caps WebSocket messages at 64 KiB and its inbound WebSocket queue at 16 messages. These are per-connection protocol limits, not a global per-IP/account connection limiter.
- WebSocket subscription identity fields are bounded before registry lookup: raw symbols are limited to 128 characters, timeframes to 16 characters, and canonical instrument IDs to the UUID-width 36-character form. These checks bound individual fields; they do not replace provider mapping or entitlement validation.
- HTTP responses from `/health` and `/v1/*` set `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a restrictive `Referrer-Policy`, and a `Permissions-Policy` disabling camera, microphone, and geolocation. They also set `Cache-Control: private, no-store, max-age=0`, `Pragma: no-cache`, and `Expires: 0` so health/API responses, including authentication errors and market-data payloads, are not stored by compliant HTTP caches. This does not replace TLS at the deployment edge, CSP for a separately hosted frontend, or rate limiting.
- Never trust a client-supplied UID or account owner identifier.
- Never put bearer tokens in URLs. Send them in the Authorization header for
  HTTP or the documented authentication message over WSS.
- Frontend Firebase sign-in and token refresh are present as code, but the
  deployed environment and end-to-end production session lifecycle still need
  a deployment smoke test.

## 4. Public endpoint classification

The current backend exposes these unauthenticated read endpoints:
- `GET /health`: liveness only; intended to reveal minimal service status.
- `GET /v1/market-data/status`: provider and ingestion status metadata.
- `GET /v1/instruments`: supported instrument catalogue metadata.

Before production deployment, explicitly approve these endpoints as public or
add authentication as appropriate. Review whether status metadata reveals
operational details that should remain private.

The `GET /v1/ohlcv` endpoint is not public: it requires a verified Firebase
Bearer identity and per-instrument entitlement checks. The WebSocket path also
requires verified identity and instrument entitlement.

## 5. Build and repository protections

- Production Vite source maps are disabled by default in `vite.config.ts`.
- `.gitignore` excludes environment files while allowing a sanitized
  `.env.example`. Ignore rules do not remove secrets already committed.
- CI installs frontend dependencies with `npm ci` from the committed
  `package-lock.json`, then runs `npm audit --audit-level=high`, frontend
  unit tests, scans frontend TypeScript/JavaScript source before bundling,
  builds the production bundle, and scans the generated bundle. The scanner
  reports finding categories and paths only; it never prints matched values.
  These high-confidence patterns are defense-in-depth and cannot prove the
  absence of every possible secret format.
- CI installs Python development dependencies, runs backend tests, performs
  `pip-audit` against `backend/requirements-dev.txt`, and builds the backend
  container image.
- CodeQL runs for JavaScript/TypeScript and Python on pushes to the project
  branches, pull requests to `main`, and a weekly schedule.
- These checks are verified on individual commits; they do not replace
  container image vulnerability scanning or runtime monitoring. The repository
  is public, user-owned, and was created after GitHub's default rollout for
  secret scanning and push protection on new public repositories. Those
  controls are expected to be enabled by default, but repository administrators
  can disable them; their current settings and alert inventory have not been
  independently verified through the repository settings interface.
- The Python dependency inputs are still range-based and do not yet have a
  committed fully resolved lockfile.

## 6. Remaining release checklist

- [x] Add an automated production-bundle scan for private-key material, common high-confidence secret formats, and backend-only credential identifiers. The scan is a defense-in-depth check, not a substitute for source review or deployment secret-store inspection.
- [x] Add automated high-confidence credential-pattern scans for frontend TS/JS source before bundling and for the generated production bundle.
- [ ] Review frontend source and scan output manually for accidental credentials; regex scans cannot prove absence of unknown secret formats.
- [ ] Confirm backend secrets are configured only through an owner-controlled, no-billing host secret-injection mechanism; no production host has been verified.
- [x] Spot-audit the successful Criterion 8 CI job output for high-confidence private-key/token/credential-bearing URL patterns; zero matches were found in that job's log. This does not verify deployed runtime logs.
- [ ] Verify HTTPS/WSS, trusted Origin allowlist, and deployment headers.
- [ ] Decide whether health, status, and instrument-catalogue endpoints are public.
- [x] Implement server-side Firebase Admin ID-token verification with project issuer/audience checks, bounded token input, revocation checking, normalized errors, and unit coverage for invalid claims and SDK initialization.
- [ ] Smoke-test Firebase sign-in, token refresh, expiry, and revocation against the production Firebase project and runtime Admin credentials; repository unit tests do not replace this deployed end-to-end verification.
- [ ] Test HTTP and WebSocket entitlement denial, revocation, reconnect, and
      exact instrument/timeframe switching.
- [x] Implement Redis-backed HTTP rate limits, WebSocket connection caps/leases, bounded query and WebSocket fields, and per-connection ping limits; unit coverage exists for the shared-guard behavior.
- [ ] Verify those controls against the deployed managed Redis service and real client traffic; configure abuse monitoring, alert thresholds, and incident response.
- [x] Add frontend and backend dependency vulnerability audits to CI.
- [x] Add CodeQL analysis for JavaScript/TypeScript and Python.
- [ ] Verify current repository secret-scanning and push-protection settings, inspect alert inventory, and audit reachable Git history; these settings and historical scan results have not been independently verified.
- [x] Add container-image vulnerability scanning through the pinned Trivy CI step (HIGH/CRITICAL OS and library findings fail the build).
- [ ] Review SQLite file permissions, backup encryption, retention, and recovery.
- [ ] Verify monitoring and incident-response procedures before production use.

A passing CI run demonstrates only that the configured checks passed for the
specific commit. It does not establish production security or guarantee that
all vulnerabilities have been found.
