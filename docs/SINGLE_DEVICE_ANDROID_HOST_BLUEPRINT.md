# DEZZTA CHART — Single-device Android host feasibility blueprint

Date: 2026-11-13
Working branch: `phase-2/market-data-foundation`
Status: **PROPOSAL — OWNER REVIEW REQUIRED; NO PRODUCTION CLAIM**

## 1. Owner constraints

- One existing device only: Infinix GT20 running Android 15.
- No PC, laptop, NAS, dedicated server, paid hosting, paid Redis, paid domain, paid runner, trial, billing upgrade, or new hardware.
- Preserve the existing authentication, Redis shared-guard, SQLite durability, WebSocket authorization, and fail-closed behavior. No in-memory production fallback, plaintext Redis, fabricated market data, or disabled security controls.
- Do not put backend secrets in the APK, frontend bundle, screenshots, or chat.
- Push notifications are outside Stage 1 and remain deferred to their planned later stage.

## 2. Current repository facts

- The Android workflow generates a temporary Capacitor wrapper during CI; the repository currently has no checked-in `android/` project or persistent Capacitor configuration.
- The installable APK currently packages the built web frontend. It does not bundle or supervise the Python backend or Redis.
- The backend is a Python 3.12 FastAPI service currently packaged for Alpine Linux in Docker.
- Production configuration requires Firebase project identity and a TLS Redis URL. Redis failure is intentionally fail-closed.
- SQLite backup and authenticated encryption helpers have automated tests, but host-level backup/restore and off-host key recovery have not been proven.
- Databento live and historical ingestion remain disabled under the zero-money policy. The APK's sample OHLC must never be represented as CME market data.

## 3. Candidate topology to test — one Android phone only

The candidate is a **local, owner-operated development/test stack**, not an internet-facing always-on production server:

1. Android app: existing Capacitor/WebView client.
2. Python runtime: Termux-managed Python environment, if the required Python wheels and native dependencies install and pass repeatable tests on Android/arm64.
3. FastAPI backend: bound only to loopback initially; never expose an unauthenticated public listener.
4. Redis: a locally built/available Redis-compatible server only if its Android build, TLS support, ACL support, persistence, and supervision are verified. No substitution with an in-memory limiter.
5. TLS: local CA/certificate with strict hostname validation for loopback testing. Android WebView trust behavior must be explicitly tested; do not disable certificate validation.
6. SQLite: database and backup paths inside Termux's private app storage, not a shared world-readable directory.
7. Reverse proxy: local-only proxy with WebSocket upgrade support, bounded timeouts, strict origin allowlist, and TLS verification.
8. Monitoring: bounded local logs and a local health/status view with secret redaction and rotation.
9. Lifecycle: explicit start/stop, restart recovery, Android process-kill behavior, battery optimization behavior, and disk-pressure behavior must be measured.

No assumption is made that Termux has a suitable Redis package, that the backend's dependencies all support Android, or that Android will keep all processes alive. Those are proof-of-concept questions.

## 4. Ten external acceptance gates — proposed single-device disposition

| Gate | Candidate proof on the phone | Limitation / pass condition |
|---|---|---|
| 8 — Secret injection | Private Termux home, restrictive file permissions, process-only environment, bundle/log/history scans | Must prove no secret appears in APK, frontend bundle, logs, or command output |
| 20 — Firebase | No-billing Firebase web/Android sign-in, real token expiry/revocation and entitlement tests | Emulator-only tests do not count; no billing upgrade or phone/SMS billing |
| 25 — Redis TLS/ACL | Redis bound to loopback, TLS certificate and hostname checks, ACL denial, persistence and restart tests | Redis must genuinely support TLS and ACL; no plaintext or in-memory fallback |
| 30 — Restore drill | SQLite Online Backup API to a separate local path, restore to fresh DB, integrity and application-row checks | Must test real Termux-host files and record measured recovery |
| 31 — Encrypted off-host backup | No compliant off-host target is currently available under the stated one-device/no-money constraint | **Cannot pass as off-host** using only another directory on the same phone. Keep open unless a genuinely separate, already-owned target is identified without cost |
| 34 — Persistent volume | Private persistent Termux storage, owner/mode checks, restart, process replacement and disk-full tests | Android storage lifecycle and uninstall/data-clear behavior must be documented; no claim of Docker volume equivalence |
| 35 — HTTPS backend | Local-only HTTPS endpoint behind local proxy, trusted CA and hostname validation | A local certificate does not establish publicly reachable production HTTPS; internet-facing deployment remains unproven |
| 36 — WSS proxy | Browser/WebView and Android client through local TLS proxy; origin/auth/entitlement/reconnect tests | Must prove actual client path and rejection cases; local-only test is not public deployment proof |
| 38 — Monitoring | Bounded local logs, health counters, retention/rotation, access restriction, redaction | No external monitoring or remote durability; must survive/recover from service restart |
| 39 — Alert/incident response | Local health alarm/runbook and induced-failure acknowledgement exercise | Reliable remote delivery cannot be claimed; push notifications remain deferred |

## 5. Required proof-of-concept sequence

No production configuration or security policy changes until these tests pass:

### POC-A — Android runtime capability
- Confirm Android ABI, available storage, free memory, Termux availability and package provenance.
- Install runtime dependencies without root, billing, or unknown binary downloads.
- Confirm FastAPI, SQLite, cryptography, and all backend imports on-device.
- Record exact versions and test output; do not collect secrets.

### POC-B — Redis feasibility
- Verify a Redis server can run on Android/arm64 and supports TLS, ACLs, persistence, and required Lua commands.
- Bind only to loopback.
- Test certificate and hostname rejection, unauthorized ACL rejection, concurrent admission, restart persistence, and Redis outage fail-closed behavior.
- If any required capability is missing, stop; do not weaken the production guard.

### POC-C — Backend + storage
- Start FastAPI on loopback using the existing production security requirements where possible.
- Store SQLite under private persistent app storage.
- Test restart, process kill, database integrity, consistent backup, restore, disk-full handling, and file permissions.
- Keep all provider flags disabled and market-data responses explicitly unavailable until trusted data is configured.

### POC-D — TLS/WSS and Android client
- Configure a local TLS proxy without disabling certificate validation.
- Test browser and installed APK against the actual local endpoint.
- Test invalid origin, invalid/expired/revoked identity, entitlement denial, reconnect, proxy restart, and backend restart.
- Do not expose the listener to the public internet.

### POC-E — Operations and lifecycle
- Test Android background restrictions, battery optimization, reboot, force-stop, process replacement, storage pressure, and recovery.
- Confirm bounded logs and redaction.
- Record which services must be manually restarted and whether the app remains usable when the backend is unavailable.

## 6. Explicit no-go conditions

Stop and leave the affected acceptance gate open if:
- Redis TLS/ACL cannot be made real and verifiable on Android.
- Android kills or suspends required services in a way that violates the required availability/recovery behavior.
- The only workaround requires disabling certificate validation, weakening authentication, using plaintext Redis, an in-memory guard, or exposing secrets.
- A required Firebase capability needs billing, payment details, a paid add-on, or uncertain quota behavior.
- A required backup target is not separate from the phone and the criterion requires off-host recovery.
- Public HTTPS/WSS is claimed without a genuinely verified public network and certificate path.
- The stack materially degrades the phone's normal use or creates unsafe thermal/storage pressure.

## 7. Owner review required before implementation

This blueprint proposes a single-device **local host proof-of-concept**. It does not change the approved production architecture, the 40-point acceptance matrix, or any security control. It does not claim all ten gates can pass on one phone.

Before code changes, review and approve:
- Whether a local-only, manually started backend is acceptable as an intermediate Stage 1 test environment.
- Whether the explicitly off-host backup gate remains open until a separate zero-cost backup target exists.
- Whether public HTTPS/WSS production acceptance remains open if only local loopback TLS can be proven.

After approval, implementation must be incremental, on `phase-2/market-data-foundation`, with tests for every changed behavior. Do not touch `main`.


## Owner-confirmed distribution decision — 2026-11-14

- The near-term delivery target is a working Android APK that can be installed directly on the owner's Infinix GT20 by manual sideload.
- **Google Play Store publication is deferred** until the owner independently decides to pursue it. Do not include Play Console registration, publication fees, store listing, or release-track work in the current critical path.
- The existing `.github/workflows/android-apk.yml` builds a debug APK using a temporary Capacitor wrapper and uploads the artifact for a limited retention period. This is an installable packaging path, not a Play Store release pipeline.
- Important limitation: the current APK packages the built web frontend only. It does not bundle or supervise the Python backend or Redis. APK installation/launch success must not be described as full backend-connected product acceptance.
- Future device acceptance must verify APK artifact integrity, install on the actual Android 15 / arm64 target, launch and navigation, WebView/network behavior, lifecycle/restart, and honest offline/backend-unavailable states. Backend connectivity is a separate gate until a safe local-host topology is approved and proven.
- This distribution clarification does not redefine Stage 1's 40-point production acceptance matrix or award progress ticks.


## Direct APK download path and restore drill implementation — 2026-11-14

- The Android workflow supports a manual, opt-in, commit-specific GitHub prerelease with the APK and SHA-256 sidecar. Ordinary pushes never publish a release.
- The release publisher is covered by offline tests and refuses to overwrite assets on an existing tag.
- The current APK remains frontend-only. Do not publish it as the final app or claim backend-connected operation.
- The final official download link will be a GitHub Release asset URL after device and backend acceptance. A stable latest-download URL is reserved for the first approved non-prerelease final release.
- A reusable SQLite restore-drill module prepares criterion 30 for the actual owner-controlled database. It is deliberately not executed until the real backend process and effective database path are identified; it never overwrites the source database.
