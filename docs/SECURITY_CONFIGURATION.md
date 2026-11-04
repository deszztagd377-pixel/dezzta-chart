# DEZZTA CHART — Security Configuration Baseline

This document defines the minimum secret-handling and deployment rules for the
market-data application. It is a configuration baseline, not a claim that the
application has completed a production security review.

## 1. Public frontend configuration

Vite variables prefixed with `VITE_` are compiled into browser-delivered code.
Treat every such value as public and inspect the production bundle before
release.

Allowed examples:
- `VITE_MARKET_DATA_API_BASE_URL`: public backend origin; it is not a credential.
- Non-sensitive UI feature flags.

Never place any of the following in frontend source, `VITE_*` variables,
query strings, browser storage, or client logs:
- `DATABENTO_API_KEY` or any provider API key.
- Firebase Admin service-account private keys or JSON credentials.
- Database credentials, signing secrets, private tokens, or backend-only keys.

A Firebase project ID is an identifier, not an Admin credential. Firebase
client configuration, when added, must use the Firebase client SDK and the
project's intended authentication/security rules; it must not contain Admin
private keys.

## 2. Backend secret handling

- Keep provider credentials in the backend deployment's secret manager or
  protected runtime environment.
- Use the platform's workload identity / Application Default Credentials for
  Firebase Admin where supported. If a service-account key is unavoidable,
  store it only as a backend secret, restrict its permissions, and rotate it.
- Never commit runtime `.env` files, service-account JSON, SQLite databases,
  or private key files.
- Do not log ID tokens, provider keys, Authorization headers, or full secret
  configuration objects.
- Return generic authentication errors to clients; retain sensitive exception
  details only in appropriately protected server-side diagnostics.

## 3. Transport and authentication

- Production deployments must use HTTPS and WSS.
- Keep the WebSocket Origin allowlist explicit and limited to trusted app
  origins. Origin checks are an additional browser control, not a replacement
  for token verification.
- Verify Firebase ID tokens on the backend. Never trust a client-supplied UID
  or account owner identifier.
- Do not put bearer tokens in URLs. Send them only in the documented
  authentication message/header over TLS.
- Frontend token refresh, session lifecycle, and authenticated HTTP snapshot
  access must be completed before private/licensed market data is exposed.

## 4. Data-access boundary still requiring a decision

The current `GET /v1/ohlcv` snapshot endpoint is unauthenticated, while the
WebSocket subscription path verifies Firebase identity and instrument
entitlements. This means snapshot bars are currently publicly readable by
anyone who can reach the backend. Before production use with private or
licensed data, add verified HTTP authentication and the same per-instrument
entitlement checks, then integrate Firebase sign-in/token refresh in the
frontend. Do not weaken the WebSocket authorization to make the two paths
match.

The instrument catalogue and market-data status endpoints also need an
explicit public/private classification before production launch.

## 5. Build and repository protections

- Production Vite source maps are disabled by default in `vite.config.ts`.
- `.gitignore` excludes `.env.*` files while allowing a deliberately
  sanitized `.env.example`.
- Ignoring a file does not remove a secret that was already committed. If a
  credential is ever exposed, revoke/rotate it at the issuing provider and
  review repository history and deployment logs.

## 6. Release checklist

- [ ] Confirm no provider/Admin credentials exist in frontend source or build output.
- [ ] Confirm backend secrets are configured only in the deployment secret store.
- [ ] Confirm production uses HTTPS/WSS and a narrow Origin allowlist.
- [ ] Add authenticated HTTP snapshot access and entitlement checks.
- [ ] Complete Firebase frontend sign-in and token refresh without persistent
      plaintext token storage.
- [ ] Test token expiry/revocation, entitlement revocation, reconnect, and
      contract/timeframe switching.
- [ ] Run dependency, secret, and deployment configuration scans.
- [ ] Verify backups, database permissions, retention, monitoring, and recovery.

