## Batch 62J-134 — WebSocket close-reason accuracy fix (22 November 2026)

Source/test commit: `ecf7decb8e823effe09a6be8a9973bb98619ae92` on `phase-2/market-data-foundation`.

### Engineering change
Backend source uses WebSocket close code 4403 for both:
- Origin policy rejection: reason `Origin not allowed` before authentication.
- Canonical instrument/series entitlement denial: reason such as `Instrument access denied` or `Instrument access revoked`.

Previously the client supervisor mapped every 4403 to an entitlement failure. That produced a false diagnosis for a frontend Origin configuration error. The supervisor now classifies 4403 by the server-provided close reason:
- Origin rejection → “WebSocket Origin is not allowlisted” diagnostic.
- Other 4403 reasons → entitlement denial/revocation diagnostic.
Both remain terminal and do not trigger an automatic reconnect loop.

Regression tests cover both branches, verify the error and snapshot detail, and verify no retry. Files changed:
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`

This is a diagnostic correctness fix only; it does not weaken authentication, authorization, Origin enforcement, or reconnect policy.

### Exact-commit CI status
- Automated Tests run [44991640588](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640588): **IN PROGRESS** at documentation time; frontend unit tests and frontend build passed, Redis TLS fixture passed, backend tests still running.
- CodeQL run [44991640593](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640593): **SUCCESS** (JavaScript/TypeScript and Python).
- Full Git History Secret Audit run [44991640577](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640577): **SUCCESS**.
- Zero-cost Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **IN PROGRESS**; web build and Android wrapper setup passed, APK assembly still running.

Do not call the new regression tests accepted until Automated Tests completes successfully. No APK artifact is claimed until its workflow reports success.

### Remaining WebSocket acceptance
- Gate 25 OPEN: immutable snapshot installation digest/provenance receipt, owner-authenticated transfer and owner-host Redis acceptance.
- Gate 36 OPEN: public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session and Android WebView foreground/background/process-death/network handover.
- Gate 38 OPEN: owner-host metrics persistence, disk pressure/restart/backup/retention and operator dashboard/alert/recovery.
- Redis TLS/AOF restart: isolated CI fixture PASS on the preceding exact-head docs baseline; owner-host failover/backup/restore remains untested.

### Indicator and project indicators
No indicator source or tests changed; indicator implementation status receives no credit:
- SMA20 🟨 foundation (first valid index 19).
- EMA20 🟨 SMA-seeded alpha 2/21 (first valid index 19).
- RSI14 Wilder 🟨 foundation (first valid index 14).
- MACD12/26/9 🟨 foundation (MACD index 25; signal/histogram index 33).
- Bollinger20,2 🟨 foundation (first valid index 19).
- Shared Indicator Hook 🟨 backend snapshot/alignment only; not chart-integrated.
- Footprint 🟧 synthetic educational accumulator only; wait for user visual reference and reviewed blueprint.
- Heatmap 🟥 not implemented; wait for user visual reference and reviewed blueprint.
- Liquidation Maps 🟥 not implemented.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED; Gate 10 remains 0/10 external criteria formally closed. Overall project remains NOT SCORED until stage weights and acceptance denominator are approved.

IP3S for this batch is **PENDING** until exact-commit Automated Tests completes. This prevents unverified source changes from receiving CI-evidence credit. ZERO COST; no deployment, paid service, production credentials, device/Termux operations or `main` changes.

---

## Current verified state — audited 2026-11-22 (Batch 62J-116)

- Exact repository baseline: `a3febdb3f7d3dd233f1cfeb8e482e986e56348e1`.
- Exact-head Automated Tests [44981340874](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340874): **SUCCESS**; CodeQL [44981340863](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340863): **SUCCESS**; Full Git History Secret Audit [44981341220](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981341220): **SUCCESS**.
- Frontend: 29 test files passed; backend: 1,294 passed, 1 skipped. The automated workflow completed all 36 job steps, including backend image build, shared Redis TLS/ACL + persistent-volume smoke, image scan/report and synthetic SQLite benchmarks.
- Client test inventory at this baseline: 17 WebSocket transport tests, 7 HTTPS ticket-exchange tests, and 21 supervisor lifecycle/reconnect tests. Backend API, ticket, shared-guard, stream, publisher/replica and Redis integration suites add server-side failure coverage.
- Repository-side protocol and CI acceptance is current for the tested scenarios. It does **not** prove public WSS, real Firebase project behavior, owner-host Redis, gateway snapshot installation, browser production session, or Android WebView behavior.
- No public HTTPS/WSS endpoint or production Firebase/Redis host is recorded. Gate 20/25/36 remain open; Gate 10 remains 0/10 formally closed.
- Ticket scope remains verified subject + `market-data` purpose, single-use, 90-second TTL. It is not bound to a specific canonical series or Origin; series entitlement is separately checked before snapshot and on renewal. Origin is defense in depth, not authentication.
- The full production evidence checklist is maintained in `docs/WORK_CYCLE_2026-11-22_BATCH62J105_WEBSOCKET_FINAL_ACCEPTANCE_PACK.md`; this section supersedes older CI checkpoint dates below.

---

# DEZZTA CHART — WebSocket client authentication design gate

## Current verified state — audited 2026-11-20

- In production, `/ws/market-data` authenticates the first JSON frame with a short-lived ticket, not a Firebase ID token. The client obtains a Firebase ID token from `AuthProvider`, sends it over HTTPS to `POST /v1/auth/websocket-ticket`, and receives a purpose-bound `market-data` ticket with a 90-second TTL. Production rejects the raw-token WebSocket fallback.
- `FirebaseIdentityVerifier` uses Firebase Admin revocation checking and validates expected issuer/audience/identity claims when issuing each ticket. Backend API tests cover issuance, invalid Bearer rejection and same-subject renewal acknowledgement. A real Firebase-project signed-token E2E has **not** been completed.
- The ticket is cryptographically random, single-use and stored by digest in the Redis-backed shared guard with a TTL; an atomic Lua GET/DEL consumes it. The ticket is bound to verified subject and purpose, but is **not currently bound to an individual canonical series or origin**. Exact-series authorization is performed separately before snapshot delivery and rechecked during renewal.
- The frontend stream supervisor exchanges a fresh Firebase ID token over HTTPS for initial and renewal tickets. The WebSocket client sends only the ticket in its `auth`/`auth.renew` frames, renews every 45 seconds by default, and requires the server acknowledgement within 10 seconds. The server enforces a bounded 60-second renewal/authorization deadline.
- The React root is wrapped in `AuthProvider` from `src/main.tsx`. `src/components/SettingsPanel.tsx` renders `AuthPanel`, and `App.tsx` renders `SettingsPanel` when the Settings tab is active. This is code-level integration, not proof of a deployed backend/provider connection.
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

Keep the frontend stream client transport-neutral and inject an asynchronous Firebase ID-token provider. Exchange that token over HTTPS for a short-lived server-issued ticket; send only the ticket in the WebSocket auth frame. The existing issuer is implemented, but its production threat-model review and any decision about per-series/origin binding remain open.

The client must validate the server snapshot and its stream ID/watermark before accepting updates. It must apply only the next sequence for the exact selected series. On a gap, queue overflow, reconnect, or series change, it must stop applying updates and obtain a fresh snapshot before resuming. All accepted updates must flow through the shared `marketDataStore`; indicators must not open their own sockets.

## Remaining security and integration gates

- A real Firebase project and authorized test accounts must be used to verify valid, expired, revoked, and wrong-project signed tokens end to end. Existing injected-verifier tests are not a substitute.
- The `AuthPanel` is mounted through `SettingsPanel` and is covered by `AuthPanel.test.tsx`; `AuthProvider` observer lifecycle is covered by `AuthProvider.dom.test.tsx`. Deployed Firebase account/session behavior and real signed-token E2E remain unverified.
- The HTTPS ticket exchange and same-subject renewal are implemented. The current ticket binds subject and purpose, not an individual series or Origin; review whether the production threat model requires additional binding before deployment.
- The client obtains a fresh Firebase ID token for each ticket issue/renewal. Firebase Admin revocation checking occurs at ticket issuance; the backend consumes the ticket once, verifies the same subject on renewal, and rechecks exact-series mapping/entitlement. Real Firebase signed-token and deployed WSS E2E remain unverified.
- No public backend deployment, real provider feed, or end-to-end client connection against production infrastructure is verified.

Do not enable production frontend streaming until the real-token E2E, visible auth flow, connection-lifetime policy, TLS deployment, and operational controls have been reviewed and tested.


## Historical implementation update — 2026-11-04 (superseded by the 2026-11-20 ticket flow above)

- At that checkpoint, the first `auth` frame carried a Firebase ID token. The backend verifies it through the approved `FirebaseIdentityVerifier` (including Firebase Admin's revoked-token check) in a worker thread. Invalid tokens close with 4401; unavailable identity verification fails closed with 1013.
- Each subscription must include `canonicalInstrumentId` as well as the exact provider series identity.
- Before taking a snapshot, the server resolves the provider/dataset/publisher/instrument mapping at the current time, checks the mapped raw symbol and canonical ID, confirms that the canonical instrument is active, and checks the verified principal's explicit entitlement. Missing, expired, mismatched, inactive, or ungranted mappings are denied with 4403.
- Mapping and entitlement are rechecked every 60 seconds during an active subscription. Revoked access or a mapping change closes the connection; the client must authenticate and subscribe again.
- The snapshot/watermark handoff and bounded stream queue remain unchanged after authorization succeeds.
- The legacy `MARKET_DATA_WS_TOKEN` setting remains for configuration compatibility, but the WebSocket route no longer reads or accepts it.

## Remaining integration gates

- Superseded by the 2026-11-09 source audit: the Firebase sign-in/session panel is available in Settings, and the frontend WebSocket client/stream supervisor is integrated with `AuthProvider` and the shared market-data store. This is code-level integration only; deployed end-to-end behavior remains unverified.
- Verified futures-definition ingestion must populate canonical instruments and point-in-time provider mappings before a user can be granted access to a contract. The offline ES/NQ/GC fixture is not sufficient to authorize a live subscription.
- No production Firebase project credentials, real user session, provider feed, deployed backend, or end-to-end client connection has been validated in this change.
- A long-lived connection re-verifies the same Firebase ID token (including expiry and revocation) and rechecks instrument entitlement/mapping every 60 seconds. If the token expires, is revoked, the identity changes, or verification is unavailable, the server closes the connection; the client must obtain a fresh token and reconnect. This bounded revalidation is implemented in the WebSocket loop, but has not yet been verified against a real Firebase project.


## 2026-11-09 source-audit reconciliation

The following corrections supersede earlier statements in this document that described the visible sign-in panel or frontend WebSocket client as absent:

- `src/main.tsx` wraps the application in `AuthProvider`.
- `src/App.tsx` renders `SettingsPanel` when the Settings tab is selected.
- `src/components/SettingsPanel.tsx` renders `AuthPanel`; users can reach the Firebase sign-in, registration, and sign-out UI from Settings.
- `src/components/AuthPanel.test.tsx` covers the panel's configured/unconfigured, error, and signed-in presentation states.
- `src/auth/AuthProvider.dom.test.tsx` covers observer mount, signed-in/signed-out transitions, error handling, cleanup, StrictMode behavior, initialization failure, and unconfigured Firebase.
- The chart's stream supervisor obtains Firebase ID tokens through `AuthProvider`, requests a fresh token on reconnect, validates snapshots and sequence continuity, and publishes accepted data through the shared market-data store. This is code-level integration, not proof of a deployed backend or live provider connection.
- Still open: real Firebase signed-token E2E (valid, expired, revoked, wrong-project); production credential discovery and session behavior; threat-model review of the implemented subject/purpose-bound ticket (including whether series/Origin binding is required); and deployed HTTPS/WSS validation. The 2026-11-09 token-frame description is historical and superseded by the ticket flow above.

Do not treat the presence of UI components or mocked/injected unit tests as production authentication evidence. No production credentials or Firebase project settings were changed by this documentation correction.
