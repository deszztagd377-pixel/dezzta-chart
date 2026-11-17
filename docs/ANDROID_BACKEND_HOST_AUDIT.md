# DEZZTA CHART — Android Backend Host Architecture Audit

Audit date: 2026-11-14  
Branch: `phase-2/market-data-foundation`  
Source checkpoint: `8a4e297efa6c07b8e130b81fbb271c9085ba707e`  
Status: **FEASIBILITY AUDIT COMPLETE — DEVICE HOST POC NOT EXECUTED**

## Executive finding

The current Capacitor APK workflow packages the built frontend only. It does not bundle, start, supervise, or persist FastAPI or Redis. APK installation alone therefore cannot provide authenticated backend market data.

A one-phone local backend remains a candidate only. It is not yet accepted because Android/Bionic runtime compatibility, Redis TLS/ACL/persistence, encryption dependencies, Android certificate trust, Firebase lifecycle, SQLite durability, and Android process lifecycle have not been proven together on the actual device.

## Verified architecture facts

1. `.github/workflows/android-apk.yml` creates a temporary Capacitor wrapper in CI and packages frontend `dist`; it does not install or supervise Python or Redis.
2. The backend is a separate FastAPI/Python service. The CI container targets Alpine Linux; passing Linux container tests do not establish Android/Bionic compatibility.
3. Production config requires Firebase project identity and a TLS Redis URL with non-empty ACL username/password. Redis shared guards intentionally fail closed. Plaintext Redis or an in-memory production fallback is prohibited.
4. Backend requires `cryptography>=50,<51`. The previously reported Google Play Termux build has a repository-signature/keyring mismatch, and the device Python environment previously lacked the required cryptography module. No package operation is safe until signed repository metadata is trusted.
5. `VITE_MARKET_DATA_API_BASE_URL` is public build-time frontend configuration, never a secret. HTTP and WebSocket clients must use the same approved backend origin; WSS derives from HTTPS and uses Firebase ID-token authentication.
6. SQLite CI tests do not prove Termux private-storage permissions, Android process recovery, or real on-device database durability.
7. Market-data provider access remains disabled under ZERO COST. A successful backend handshake must not be represented as live exchange data without a verified provider source.

## Blocker matrix

| Area | Evidence | Disposition |
|---|---|---|
| APK packaging | Frontend-only Capacitor debug workflow | Packaging exists; full app acceptance open |
| Backend runtime | Alpine container tests only | Android/Bionic POC required |
| Termux package trust | Play Store build signing/keyring mismatch | Blocked; preserve trusted source and signatures |
| Python encryption | Required cryptography version not verified/importable on device | Blocked; no downgrade or crypto replacement |
| Redis | CI TLS/ACL/shared-guard tests; Android Redis unverified | Blocked; no plaintext/in-memory substitute |
| Firebase | Server verification/unit tests; real device lifecycle unproven | Open |
| HTTPS/WSS | Client/server code exists; Android certificate trust and local proxy unproven | Open |
| SQLite | CI backup/restore identity checks pass | Device path and real restore open |
| Android lifecycle | No verified reboot/background/force-stop recovery | Open |
| Market data | Provider disabled; no zero-cost licensed feed verified | Unavailable by design until source approved |

## Zero-cost topology assessment

**A dedicated laptop/PC is not required for the project workflow.** The owner develops from an Android phone, and repository changes/deployments can be handled through GitHub and Vercel. Termux is already installed on the phone, but it is not the preferred always-on production host. A phone-local backend would stop when Android suspends or terminates the process and is not suitable as the assumed public service.\n\nThe preferred cloud-host candidate is a Vercel-managed Python backend with native WebSocket support, subject to the compatibility and persistence proof in [VERCEL_BACKEND_FEASIBILITY.md](VERCEL_BACKEND_FEASIBILITY.md). Vercel announced WebSocket support as generally available on 2026-10-20. Its Python runtime became generally available on 2026-10-15 and current guidance supports FastAPI. The current FastAPI application is **not deployable unchanged** because its SQLite files and in-process stream hub are not durable/shared across serverless instances. This is a scoped architecture migration, not a request for new hardware.\n\nTermux remains a development/preflight option only. The known package-signature/keyring issue remains a no-go for package changes until trusted repository metadata is available.

Before integration code changes, prove the Vercel Python/FastAPI WebSocket path and select a durable shared store that has a verified zero-cost tier and meets the security contract. A Vercel Function's writable `/tmp` directory is scratch space, not durable SQLite storage. The existing process-local `OhlcvStreamHub` also cannot coordinate clients connected to different instances.\n\nIf the Vercel proof fails, evaluate the already-installed Termux environment as a development-only fallback; do not require a PC, weaken TLS/ACL, or expose a phone-local service as public production. Before any Termux package changes, resolve the existing signature/keyring trust failure.\n\nThe following Android-local requirements remain relevant only if a device-host POC is ever explicitly needed:
- Full Python/Bionic backend imports, including the exact cryptography version.
- A genuine Redis-compatible server with TLS, ACLs, persistence, required commands, and restart behavior.
- Private Termux SQLite storage, owner-only permissions, backup/restore, and process recovery.
- Strict local TLS hostname validation in Android WebView and WSS. Never disable certificate validation.
- Real Firebase sign-in, refresh/expiry/revocation, and entitlement denial under the no-billing project.
- Android background, force-stop, reboot, memory/storage pressure, and recovery without unacceptable battery/thermal impact.
- Honest offline/unavailable UI whenever backend or provider data is unavailable.

Phone-local backup is not off-host backup. Loopback testing cannot close off-host backup or public HTTPS/WSS claims.

## Safe next sequence

1. Keep the current Termux installation and package source unchanged while the upstream signature/keyring issue remains unresolved.
2. If an owner-approved device check is scheduled, begin with the existing read-only `scripts/android-host-preflight.sh`. It installs nothing, changes no repository, and starts no service.
3. Review that evidence before considering a narrowly scoped Python/Bionic import POC. Do not start Redis or alter production settings during the first check.
4. Treat Redis TLS/ACL feasibility as a separate no-go checkpoint. If all controls cannot be provided at zero cost, stop rather than weakening security.
5. Only after those checks pass, review a scoped implementation blueprint for lifecycle, endpoint configuration, certificate trust, database path, and APK integration.
6. Keep the frontend-only APK unpublished as a final product. Direct official download remains gated on actual-device install and backend-connected acceptance.

## Unchanged

- No Termux command, package, repository, keyring, signing key, Python package, or crypto dependency was changed.
- No paid hosting, trial, new hardware, domain, external provider data, production URL, or backend secret was introduced.
- No APK preview/final release was published.
- No ALL PAIR research or implementation was performed.
- No Stage 1 acceptance tick was awarded.

## Gate 10 accounting

This audit clarifies dependencies for criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39. It is repository architecture evidence only, not owner-device acceptance. All ten remain open.

Stage 1 remains 300/400 ticks = 75% provisional (30/40 criteria provisionally accepted). Stages 2–6 remain NOT SCORED. Overall 20.90% remains a historical checkpoint only.


## Vercel serverless backend correction — 2026-11-17

The earlier version of this audit treated a Termux-hosted backend as the only one-phone topology worth testing. That conclusion is superseded.

- Vercel WebSocket support became generally available on 2026-10-20: https://vercel.com/changelog/websocket-support-is-now-generally-available
- Vercel's Python runtime supports FastAPI, Django and Flask and became generally available on 2026-10-15: https://vercel.com/docs/functions/runtimes/python
- Vercel Functions have a read-only filesystem with writable `/tmp` scratch storage; that scratch space is not a persistent database: https://vercel.com/docs/functions/runtimes
- Function instances are bounded by maximum duration and can be recycled; clients must reconnect and resubscribe: https://vercel.com/docs/functions/limitations

This makes a Vercel-hosted backend a realistic candidate without a laptop/PC, but does not automatically make the current backend production-compatible. The proof still required is explicit in `VERCEL_BACKEND_FEASIBILITY.md`: Python FastAPI WebSocket compatibility on the actual Vercel plan, durable/shared OHLCV and outbox storage, cross-instance fan-out, Firebase/Redis secret injection, and client reconnect/replay acceptance.

No paid Vercel plan, paid Redis, market-data feed, new hardware, or owner credential was introduced. No Termux command was run. Stage 1 ticks remain unchanged until acceptance evidence exists.


## Python runtime GA correction — 2026-11-17

Historical Beta references in earlier notes are superseded. Vercel announced Python runtime GA on 2026-10-15 and WebSocket GA on 2026-10-20. Current guidance describes FastAPI ASGI WebSocket support on Fluid Compute. The actual project still needs an isolated POC and Fluid Compute configuration check. This platform update does not make SQLite durable or process-local fan-out cross-instance.

The root project remains a Vite/React app with no root `vercel.json` or root `api/` Python entrypoint. Keep any POC isolated from the existing frontend deployment.


## 2026-11-17 — Vercel account and deployment evidence

The Vercel connector is now connected and read access to the project is confirmed:
- Team plan: **Hobby**; zero-cost requirement remains mandatory.
- Project `dezzta-chart` is linked to `deszztagd377-pixel/dezzta-chart` and uses Vite.
- The earlier preview deployment for commit `056cdd0a838ce2c47b4206af3801d6778af05675` was **READY**; the follow-up docs commit `8a4e297efa6c07b8e130b81fbb271c9085ba707e` also reached **READY** through the existing Git integration.
- This is frontend preview deployment evidence only. It is not a backend/WSS acceptance test.
- The connector response did not expose `rootDirectory` or Fluid Compute configuration. Both remain unverified and must not be assumed.

No Termux command or package operation was required for this remote repository/Vercel audit. The existing Termux signature/keyring trust issue remains untouched.


## Follow-up exact-head deployment — 2026-11-17

The documentation correction commit `8a4e297efa6c07b8e130b81fbb271c9085ba707e` on `phase-2/market-data-foundation` was automatically deployed by Vercel and reached **READY** at https://dezzta-chart-4nil5h92d-deszztagd377-pixel.vercel.app. It remains a frontend Vite preview; it does not validate Python FastAPI or production WSS.


## Remote Vercel evidence — 2026-11-17

The connected Vercel account confirms the existing project is a Hobby-plan Vite frontend. Exact preview `dpl_5LXiSDH7jKh3dnvxfCywaRjfYbJs` is READY on `phase-2/market-data-foundation` at `3003226c982c2a51b52d6a4f5f64b1794c625ff0`; it is not backend/WSS acceptance.

SSO is enabled for `all_except_custom_domains`; password protection and trusted-IP restrictions are disabled. No setting was changed. Custom-domain protection must be assessed separately. GitHub reports this repository is public, so source and tracked history are visible regardless of Vercel protection.

The current project response did not expose Root Directory or Fluid Compute. No root Python API entrypoint or root `vercel.json` exists in the audited tree. Keep the Vite project intact; use a separate SSO-protected Hobby project for the synthetic FastAPI/WSS proof.

The build succeeded, but Vite reports a 537.43 kB minified main chunk (about 152.06 kB gzip) above the 500 kB warning threshold. npm also reports the `cache-dir` configuration warning and install-script allowlist warnings for three packages. No package scripts were approved automatically.

The connector provided metadata and build events, not an authenticated screenshot. Visual inspection is not claimed. No Termux command or package/signature change was needed. Stage 1 stays 75% provisional; Gate 10 stays 0/10 formally closed.
