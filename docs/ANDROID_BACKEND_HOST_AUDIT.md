# DEZZTA CHART — Android Backend Host Architecture Audit

Audit date: 2026-11-14  
Branch: `phase-2/market-data-foundation`  
Source checkpoint: `6c58daea1312e78d51956323ca03a2a9b6375e20`  
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

The only topology worth a controlled feasibility test under the one-device constraint is a manually started, loopback-only Termux backend with the APK as client. This is **not approved for implementation yet**.

Before integration code changes, prove:
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
