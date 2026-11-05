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
- Keep the WebSocket Origin allowlist explicit. Origin checks supplement, but do
  not replace, token verification.
- HTTP authentication uses a Firebase Bearer ID token verified by the backend.
  The `GET /v1/ohlcv` route also resolves the exact provider mapping and checks
  that the verified account has an entitlement for the active canonical
  instrument.
- The WebSocket subscription path independently verifies Firebase identity and
  checks instrument entitlement. Do not weaken either path to make them match.
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
- CI currently installs frontend packages with `npm install`, runs frontend
  tests and a production build, installs Python development dependencies,
  runs backend tests, and builds the backend container.
- The audited repository did not contain a `package-lock.json`. A lockfile
  and reproducible `npm ci` workflow should be introduced only after a
  deliberate dependency-resolution review.
- The current CI workflow does not yet show dedicated dependency vulnerability,
  secret-scanning, or container-image scanning steps. Add these after selecting
  and validating suitable scanners and their failure thresholds.

## 6. Remaining release checklist

- [ ] Inspect frontend source and production bundle for accidental credentials.
- [ ] Confirm backend secrets are configured only in the deployment secret store.
- [ ] Verify HTTPS/WSS, trusted Origin allowlist, and deployment headers.
- [ ] Decide whether health, status, and instrument-catalogue endpoints are public.
- [ ] Smoke-test Firebase sign-in, token refresh, expiry, and revocation.
- [ ] Test HTTP and WebSocket entitlement denial, revocation, reconnect, and
      exact instrument/timeframe switching.
- [ ] Add and test rate limits, request-size bounds, and abuse monitoring.
- [ ] Add dependency, secret, and container security scans to CI.
- [ ] Review SQLite file permissions, backup encryption, retention, and recovery.
- [ ] Verify monitoring and incident-response procedures before production use.

A passing CI run demonstrates only that the configured checks passed for the
specific commit. It does not establish production security or guarantee that
all vulnerabilities have been found.
