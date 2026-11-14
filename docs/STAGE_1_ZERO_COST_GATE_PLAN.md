# Stage 1 — Zero-cost plan for the ten external acceptance gates

Decision: owner-mandated ZERO MONEY. This plan is a constraint-resolution design, not proof that any production gate has passed. No cloud project, account, service, trial, billing plan, payment method, domain, VM, volume, runner, API, or subscription may be created or enabled by following this document.

## Non-negotiable execution guard

- Use only hardware, storage, network access, and accounts the owner already has, with no incremental charge or billable overage.
- Before any external account or service is considered, verify current terms, payment-method requirement, quota exhaustion behavior, auto-upgrade/trial conversion, and a reliable disable path. Unknown means DO NOT ENABLE.
- Never request passwords, OTPs, API keys, payment details, or recovery secrets in chat or commit secrets to the repository.
- No paid market-data provider, paid hosting, paid Redis, paid Firebase upgrade, paid KMS, paid backup bucket, paid monitoring, paid email/SMS, paid domain/CDN, paid runner, or trial.
- If the existing equipment/network cannot support the required control safely, mark it constrained/deferred. Do not weaken security controls or mislabel a local CI test as production evidence.

## Gate-by-gate disposition and zero-cost path

### 8 — Production secret storage and leakage verification
**Current status: external verification required.**
- Candidate zero-cost path: owner-controlled host using OS-protected service credentials (for example systemd credentials) or a root-owned secrets file with restrictive permissions, injected only into the backend process. Keep secrets out of source control, frontend build arguments, logs, crash reports, and command-line arguments.
- Required evidence: host configuration review, permission/ownership check, process-environment exposure review, frontend bundle scan, log scan, and repository-history secret scan.
- Do not claim this gate passed until the actual host and secret-injection path are inspected. Do not introduce a paid secret manager.

### 20 — Real Firebase sign-in, revocation, entitlement, browser and Android integration
**Current status: external verification required; billing/terms preflight first.**
- Candidate: use only a Firebase configuration that is demonstrably no-billing and does not require a payment method or billing upgrade, after current terms/quotas and shutdown behavior are checked. The Firebase Emulator Suite may support local development tests, but emulator tests are not proof of real provider integration.
- Required evidence: real sign-in, revoked/expired token rejection, entitlement denial, reconnect, browser WSS and Android WSS results against the selected backend.
- If no-billing eligibility cannot be established, keep production Firebase integration disabled and this gate deferred. Never upgrade to Blaze.

### 25 — Managed Redis TLS, access controls, persistence and failover
**Current status: external verification required; managed paid Redis prohibited.**
- Candidate: owner-hosted Redis on existing hardware, bound to a private interface, TLS enabled, ACL-authenticated, firewall-restricted, and supervised by the host OS. Preserve atomic Lua guards, lease expiry/release, shared limits, and fail-closed behavior.
- This requires a reviewed single-host topology and tests for restart, loss of Redis, TLS certificate validation, ACL denial, and concurrent admission. Do not replace shared Redis with an in-memory limiter.
- If existing hardware cannot host it reliably, keep production shared-guard acceptance deferred.

### 30 — Production-like backup restore drill
**Current status: external verification required.**
- Candidate: use SQLite Online Backup API on the owner-controlled host, copy the backup to a new database path on existing local storage, run integrity checks, and verify representative application-level rows and replay/outbox continuity.
- Required evidence: timestamped backup/restore report, source and target database identity, integrity output, record-count/key checks, and recovery time.
- CI smoke tests alone do not close this production-like restore gate.

### 31 — Encrypted off-host backup and key recovery
**Current status: external verification required.**
- Candidate: encrypt backups with a reviewed open-source local tool such as age before copying to a second owner-controlled device already available. Keep the recovery key separate from the backup and repository; document offline recovery and rotation.
- Required evidence: encrypted file inspection, separate key custody, restore on the second device, integrity and application-level verification, retention/deletion test.
- If a second device or safe key custody is unavailable without spending money, defer. Do not use a paid bucket or paid KMS.

### 34 — Production persistent volume
**Current status: external verification required.**
- Candidate: dedicated directory/partition on existing host storage, mounted at the documented data path, owned by UID/GID 10001, with restrictive permissions and backup coverage.
- Required evidence: mount and filesystem details, ownership/mode, restart and process-replacement persistence test, disk-full behavior, and recovery procedure.
- Docker CI named-volume tests are useful repository evidence but are not proof of a real host volume.

### 35 — Production HTTPS backend deployment
**Current status: external verification required; no hosting purchase.**
- Candidate: backend on existing owner-controlled hardware, bound to loopback/private network behind a reverse proxy. HTTPS may be exposed only if a domain and network path already exist without incremental cost and their renewal/usage terms are verified. Otherwise keep access LAN-only with a locally trusted TLS setup for controlled testing.
- Required evidence: TLS certificate/hostname verification, HTTPS health checks, secure startup failure behavior, backend-only secret injection, and restart behavior.
- No Fly.io, paid VM, paid domain, CDN, or billing activation.

### 36 — Production WSS reverse-proxy verification
**Current status: external verification required.**
- Candidate: WSS through the same owner-hosted reverse proxy, with origin allowlist, authentication before subscription, token/entitlement revalidation, correct upgrade headers, bounded timeouts, and reconnect/replay behavior.
- Required evidence: real browser and Android client tests across the proxy, unauthorized origin/token rejection, reconnect replay, resnapshot fallback, and proxy restart behavior.
- Local WebSocket tests do not prove production proxy behavior.

### 38 — External metrics, logs, retention, dashboards and access control
**Current status: external verification required; paid observability prohibited.**
- Candidate: self-hosted open-source metrics/logging/dashboard on the same existing hardware, or a minimal local health/log dashboard if resources are constrained. Keep retention bounded and protect access.
- Required evidence: emitted metrics/logs, dashboard access controls, retention/rotation behavior, disk-pressure behavior, and a test showing sensitive credentials are redacted.
- If the host cannot safely run this without added hardware or service cost, use bounded local logs and explicitly defer external monitoring acceptance.

### 39 — Alert delivery and incident response
**Current status: external verification required; paid delivery prohibited.**
- Candidate: local dashboard alert plus documented operator runbook and manual escalation using only already-available no-cost channels after their terms are checked. Do not assume email/SMS/push is free.
- Required evidence: induced failure, alert observed by the responsible operator, acknowledgement/escalation record, and tested recovery steps.
- If reliable delivery cannot be achieved at zero incremental cost, mark delivery constrained/deferred rather than enabling paid email/SMS.

## Release decision

All ten gates remain **OPEN / EXTERNAL VERIFICATION REQUIRED** until the evidence above exists on the actual owner-controlled environment. This plan does not increase the 30/40 checklist count and does not declare Stage 1 production accepted. A local CI pass, a written plan, or an open-source license is not proof of deployed operation or zero infrastructure cost.

The 18 configured chart timeframes remain required, including 1-second. Provider/feed availability, licensing, latency, and history must be proven separately; no simulated or delayed feed may be represented as live.


## Owner-confirmed device constraint and phone-only disposition — 2026-11-13

**Authoritative owner environment:** one device only — Infinix GT20 (Android 15). The owner has no second phone, PC, or laptop. This is an existing constraint and must not be asked again. No new hardware, paid host, cloud trial, external storage purchase, or billing activation may be proposed as a prerequisite.

The earlier candidate paths that assume "another existing owner-controlled host" or a "second device" are not available in the owner's current environment. The following phone-only classification supersedes those assumptions while preserving the original acceptance requirements; it does not waive or redefine production criteria.

| Gate | What can be advanced with the single phone | What still prevents production acceptance |
|---:|---|---|
| 8 — secrets | Repository/frontend bundle/log scanning and local permission design can be reviewed from the phone/CI | No separately operated production host with an audited OS secret-injection mechanism |
| 20 — Firebase | Browser and Android client paths can both be exercised on the same phone if an already-existing no-billing Firebase project and test identities are available | No verified no-billing project plus actual backend deployment/token-revocation path is evidenced; never enable billing to obtain it |
| 25 — Redis | CI already exercises Redis-backed Lua limits and fail-closed behavior; additional isolated integration coverage can be added in CI | No stable, independently operated Redis host on the phone; one Android device cannot prove host-level failover/high availability. Do not replace Redis with in-memory state |
| 30 — restore drill | **Best phone-only candidate.** SQLite Online Backup API uses Python/SQLite standard library and can restore to a fresh path on the same phone. Existing evidence includes SQLite integrity/readback smoke and CI application-record restore tests | Need one consolidated owner-device report covering representative application records, fresh-database restore, integrity, and post-restore reads. Same-device restore is not off-host disaster recovery |
| 31 — encrypted off-host backup | Encryption design and CI tests can be reviewed; the current Android backup encryption dependency remains documented | Off-host copy and independent key recovery cannot be demonstrated with only one device and no verified existing external destination. Termux Play Store package/keyring mismatch also blocks cryptography>=50,<51 on-device |
| 34 — persistent volume | Android app-private/Termux storage can be tested for persistence across process restarts | Android app storage is not equivalent to a separately mounted production host volume with host-level ownership, disk-pressure and recovery controls |
| 35 — HTTPS backend | A loopback-only backend/TLS experiment can be designed for same-device testing | No verified production host, public HTTPS endpoint, or trusted deployment certificate/renewal path |
| 36 — WSS proxy | Same-phone local client/proxy tests may be possible after a reviewed local proxy topology exists | No production reverse-proxy endpoint and no external host restart/network evidence |
| 38 — monitoring | Bounded local logs/metrics and a local dashboard can be developed/tested on the phone or in CI | No independent monitoring host/operator path; same-device dashboard is not external production monitoring |
| 39 — alerts | Local alert records and a manual on-device acknowledgement workflow can be tested | No independently reachable operator delivery/escalation channel is evidenced; push/notification delivery remains deferred to its planned stage |

### Phone-only execution order

1. Advance criterion 30 first using the existing SQLite standard-library backup path. Keep encrypted/off-host recovery (criterion 31) separate; do not make it a prerequisite for testing unencrypted local restore.
2. Continue CI-only hardening for Redis ACL/TLS/failure behavior and backend secret-leak checks without pretending ephemeral CI resources are production hosts.
3. Design a loopback-only HTTPS/WSS experiment only if it can be implemented and validated without changing the production fail-closed requirements or introducing a major unapproved UI change.
4. Treat criteria 8, 20, 25, 31, 34, 35, 36, 38 and 39 as constrained for production acceptance until the missing host, account, storage or operator evidence exists. Their local subtests may improve confidence but do not close production gates.

### Explicit decision boundary

The owner wants Stage 1 completed at zero cost, but the current 40-item matrix defines production/operational acceptance. With one Android phone and no PC/second device, **a truthful 40/40 production-acceptance result is not currently achievable** unless an already-available, genuinely zero-cost external resource is independently verified. Do not fabricate a second host, reinterpret CI as production, lower security controls, or change the 40-item definition to force 100%.

A separate owner-approved decision could later redefine Stage 1 as a phone-only development/demo milestone, but that would be a scope change and must not be presented as the existing production Stage 1 being complete. No such scope change is assumed here.

## Criterion 25 repository-side hardening update — 2026-11-14

The backend configuration now enforces the repository-side production baseline:

- Production `REDIS_URL` must use `rediss://` TLS.
- Production URL must include a non-empty Redis ACL username and password; no-auth and partial-auth configurations fail startup validation.
- `RedisSharedGuard` configures CA-chain validation and hostname verification for `rediss://`.
- Settings diagnostics exclude the complete Redis URL, including ACL credentials.
- Regression tests cover missing username, missing password, missing both, credential redaction, and TLS certificate/hostname validation.
- Exact tested commit `ed62578eafad89b0d27ec233c06e5503c9f00123`: [Automated Tests #43538598583](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43538598583) succeeded; 798 backend tests passed. The isolated Redis/persistent-volume smoke test and Trivy HIGH/CRITICAL scan also succeeded with zero findings.

**External acceptance remains OPEN.** The CI Redis instance is ephemeral. It does not prove the real host's private binding, firewall policy, least-privilege ACL user, persistent configuration, restart/failover recovery, or deployed TLS certificate. With the owner's single-phone/no-PC constraint and ZERO COST rule, do not invent a host or enable paid infrastructure to close this gate.



## Ten-gate work-cycle audit — 2026-11-14 — repository head `4ab3579`

This section records work actually present on the branch, what the current CI can prove, and the remaining external acceptance boundary. It does not award ticks.

| Criterion | Repository-side progress verified | Remaining external evidence / disposition |
|---:|---|---|
| 8 — production secrets | Frontend source and built-bundle scans; settings redaction tests; full reachable-history Gitleaks scan. Gitleaks #43566090680 passed on `4ab3579`. | Still requires owner-host secret-injection, deployed log/build-output inspection, and GitHub native secret-scanning/push-protection setting and alert inventory. |
| 20 — Firebase | Firebase Admin token/revocation and authorization logic plus fail-closed tests exist. | No verified no-billing Firebase project, production backend, real sign-in/revocation/entitlement/reconnect run, or browser/Android deployed WSS evidence. No billing upgrade. |
| 25 — Redis | Production config enforces `rediss://`, ACL username/password, CA-chain and hostname validation; CI Redis ACL/failure/persistence smoke coverage exists. | Still requires a real owner-hosted Redis TLS endpoint, private binding/firewall/ACL review, persistent config, restart and failure/recovery evidence. Ephemeral CI Redis is not production. |
| 30 — restore drill | Existing OHLCV/outbox restore test is extended by a shared-database recovery test covering instrument registry, entitlements, alert zones, coverage intervals/gaps, OHLCV, durable outbox cursor/event identity, integrity, and a post-restore write. | CI test is not the owner-device report. A timestamped run against a real application database on the target environment remains required; no production data is fabricated. |
| 31 — encrypted off-host backup | AES-256-GCM/PBKDF2 streaming encryption, authenticated header, private atomic publication, wrong-key/tamper rejection and restore tests exist. | No second device or verified no-cost off-host destination/key custody; Android crypto dependency is blocked by the Play Store repository signing mismatch. |
| 34 — persistent volume | Container runs UID/GID 10001; CI named-volume ownership, SQLite integrity and restart persistence tests pass. | Still requires actual owner-host mount, mount path/owner/mode, disk-pressure, restart/process-replacement and recovery evidence. |
| 35 — HTTPS deployment | Production configuration and portable container/health-check preparation exist. | No verified host, TLS hostname/certificate lifecycle, backend-only secret injection or deployed HTTPS health check. |
| 36 — WSS reverse proxy | Authenticated WebSocket route, origin checks, entitlement checks, revalidation and reconnect/replay code have repository tests. | No real reverse proxy and no deployed browser plus Android WSS handshake/reconnect/resnapshot test. |
| 38 — monitoring | Bounded operational state/latency counters and market-data status endpoint exist. | No host-side collection, dashboard access-control, retention/rotation, disk-pressure or deployed redaction evidence. |
| 39 — alerts and incident response | Alert-zone validation and durable SQLite storage exist. | No verified operator-facing delivery path, acknowledgement/escalation exercise, or recovery/incident record. Local records are not alert delivery. |

### Current action result

- The repository-side test expansion for criterion 30 is pending exact-commit CI.
- Criteria 8 and 25 have strong repository-side coverage, but no owner-host production proof.
- Criteria 20, 31, 34, 35, 36, 38 and 39 remain constrained by absent verified external project/host/storage/operator resources under the ZERO MONEY and single-phone constraints.
- No external gate is marked complete. Stage 1 remains 300/400 ticks (75% provisional), and the ten open criteria remain open.
- The next evidence-bearing opportunity is the criterion 30 owner-device restore report. The integrated test does not substitute for that report.


## Criterion 20 — Firebase prototype implementation update — 2026-11-14

The earlier prototype-only implementation note is superseded by the current source state and owner-approved setup:

- The owner registered the DEZZTA CHART Firebase Web App and supplied its public web configuration in the earlier project work.
- The owner selected the Firebase Spark/no-billing path and explicitly excluded payment-card/billing upgrades.
- Google Sign-In and Email/Password sign-in methods were enabled in the Firebase project.
- Frontend integration is present: `src/services/firebase.ts` reads the four `VITE_FIREBASE_*` public configuration values and rejects a mismatched pre-existing default app; `src/auth/AuthProvider.tsx` owns the auth observer, email registration/sign-in, Google redirect, sign-out and ID-token retrieval; `src/main.tsx` mounts the provider; `src/components/SettingsPanel.tsx` exposes the account panel.
- The authenticated market-data client obtains a fresh ID token for every stream connection/reconnect. The backend verifies Firebase ID tokens with revocation checking, validates issuer/audience/subject/authentication time, checks per-instrument entitlements and periodically revalidates token and entitlement state during active WebSocket subscriptions.
- Automated tests cover client initialization, email/Google action wiring, token-observer lifecycle, backend claim validation, revocation-check invocation, entitlement denial/revocation, WebSocket reconnect and fail-closed behavior.

**Remaining acceptance boundary:** the source tests use mocks for Firebase SDK and identity-verifier behavior. The actual Firebase project billing state, deployed frontend environment values, backend Admin SDK credential injection, real sign-in, real expired/revoked-token rejection, entitlement denial and reconnect must still be exercised against a running backend from the supported browser and Android client paths. The Firebase project being registered and auth methods being enabled is not itself that integration evidence. Keep Spark/no-billing; do not enable Blaze or phone/SMS billing.



## Exact-commit CI evidence — 2026-11-14 — `e599b45d480c29f195d53047cf9b301182a74de0`

- Automated Tests workflow #43566762952: **completed successfully**. Frontend dependency audit, unit tests, production build and bundle secret scans passed; backend tests passed including the expanded shared-application-database restore test; bounded SQLite outbox benchmark passed; backend dependency audit passed; container image build passed; Redis shared-guard + persistent-volume smoke test passed; Trivy image scan/report completed; workflow cleanup completed.
- CodeQL workflow #43566763073: **completed successfully** (Python and JavaScript/TypeScript).
- Full Git History Secret Audit #43566762971: **completed successfully**.
- Exact branch HEAD at this checkpoint: `e599b45d480c29f195d53047cf9b301182a74de0`.
- The restore regression now passes in CI. It strengthens criterion 30 repository-side evidence only; it does not substitute for an owner-device/production restore report.
- The Redis and persistent-volume CI smoke tests strengthen criteria 25 and 34 repository-side evidence only; they do not prove owner-host production network, TLS, ACL, mount or restart behavior.
- No external gate was closed and no Stage 1 ticks were awarded by CI alone. Stage 1 remains **300/400 = 75% provisional**.

Workflow evidence:
- Automated Tests: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43566762952
- CodeQL: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43566763073
- Gitleaks: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43566762971


## External-gate execution checkpoint — 2026-11-14 — exact HEAD `d64ad3fa1620f75b363b4f32e3df01b06a62c2d2`

### Repository/CI entry prerequisites — all green on the same HEAD

- Automated Tests #43568751544 — **SUCCESS**.
- CodeQL #43568751559 — **SUCCESS** (Python and JavaScript/TypeScript).
- Full Git History Secret Audit #43568751546 — **SUCCESS**.
- The Automated Tests workflow completed the Redis/shared-guard and persistent-volume smoke test and Trivy scan/report steps. These are CI environment checks, not owner-host production proof.

### Ten-gate live disposition

| Gate | Repository/CI evidence now available | Actual acceptance still missing |
|---:|---|---|
| 8 | Frontend source/bundle secret scans, settings redaction tests, exact-HEAD full-history Gitleaks success | Audit of the real owner-host secret injection, deployed logs/build outputs, and repository security-setting/alert inventory |
| 20 | Firebase client lifecycle and backend token/revocation/entitlement logic with fail-closed tests; owner previously selected Spark/no-billing and enabled sign-in methods | Confirm current no-billing project state and execute real sign-in, expiry/revocation, entitlement denial and reconnect through a deployed backend from browser and Android |
| 25 | Production config enforces Redis TLS and ACL credentials; CI Redis guard/failure/persistence smoke passes | Real owner-host private binding/firewall, least-privilege ACL, trusted TLS certificate, persistent config and restart/failure/recovery evidence |
| 30 | Exact-HEAD CI full shared-database restore test verifies registry, entitlement, alert zones, coverage/gaps, OHLCV, outbox cursor/event identity, integrity and post-restore writes | Timestamped restore drill against the actual application database available on the owner's device, with application-level readback |
| 31 | AES-256-GCM/PBKDF2 encryption implementation and tamper/wrong-key tests exist | Secure off-host destination and separate key custody/recovery; current Google Play Termux signing-key mismatch blocks the required crypto dependency on-device |
| 34 | Container UID/GID 10001 and CI named-volume ownership/restart persistence smoke pass | Actual owner-host mount, ownership/mode, process restart, disk-pressure and recovery evidence |
| 35 | Container health endpoint, startup fail-closed behavior and backend-only configuration are covered in repository/CI | Actual owner-controlled backend host, HTTPS certificate/hostname lifecycle, health check and secret injection |
| 36 | Authenticated WebSocket, origin, entitlement, revalidation and reconnect/replay logic have regression coverage | Real reverse-proxy WSS handshake and browser plus Android authentication/reconnect/resnapshot run |
| 38 | Bounded application operational counters/status endpoint and CI build are present | Actual host-side log/metric collection, dashboard access control, retention/rotation, disk-pressure and secret-redaction evidence |
| 39 | Durable alert-zone validation/storage exists | Operator-visible no-cost alert delivery, acknowledgement/escalation and tested incident recovery record |

### First execution target: criterion 30

Criterion 30 is the first practical target under the owner's confirmed single-device/no-PC constraint. Its SQLite snapshot/restore mechanism is separate from backup encryption; it must not be blocked by, or used to conceal, criterion 31's Termux cryptography issue.

Acceptance evidence must be generated from the actual application database on the target device and include:
1. Timestamp and device/runtime identification without secrets.
2. Source database identity represented safely (do not publish personal paths or database contents).
3. Consistent snapshot and restore into a new database path.
4. SQLite `integrity_check` and foreign-key check results.
5. Application-level readback for every available durable domain: canonical instrument registry, entitlements, alert zones, coverage/gaps, OHLCV bars and outbox/replay cursor/event identity.
6. A post-restore read/write verification on the restored copy, not on the source database.
7. Result totals, failure details and report hash.

No existing source database may be overwritten or deleted. The test must use a fresh restore destination and must not expose database rows, account identifiers, credentials or encryption secrets in the report.

The CI test already proves the repository implementation can exercise these domains using a synthetic fixture. It does not prove the owner's live database is available, that a device restore was performed, or that the target environment is production-like. Therefore criterion 30 remains OPEN and earns no ticks until the device report is independently reviewed.

### Termux handling during gate execution

- Criterion 30 uses SQLite/Python standard-library restore functionality; it does not require installing `cryptography` or changing APT sources.
- Criterion 31 remains blocked by the Google Play Termux repository/keyring signing mismatch and lack of verified off-host/key-custody resources.
- Preserve the working Google Play Termux source and the `cryptography>=50,<51` requirement. No repository switch, unverified key import, signature bypass, dependency downgrade, migration, uninstall or app-data clearing is authorized.

### Stage and progress accounting

- Official stage: **Stage 1 — unchanged**.
- Stage 1 checklist: **30/40 criteria; 300/400 ticks = 75% provisional**.
- External gates: **10/10 remain open**.
- Overall project: **20.9% historical owner-confirmed checkpoint**; no fresh weighted total is approved.
- CI success, documentation updates and local subtests add no Stage 1 ticks by themselves.


## Gate 10 execution batch 1 — criterion 30 restore safety

Owner authorization to begin the ten external gates was received on 2026-11-14. The ten gates are now an active execution register; this does not waive any external evidence requirement.

### Implemented repository improvement

Added `restore_consistent_sqlite_backup(backup_path, destination_path)` to `backend/app/sqlite_backup.py`.

Safety properties:
- Read-only backup source.
- Restore to a separate fresh destination.
- Refuses an already-existing destination and uses same-directory hard-link publication so a concurrent destination cannot be overwritten.
- Validates SQLite `integrity_check` and `foreign_key_check` before publication.
- POSIX restore artifact is owner-only (0600) and file-flushed before publication.
- Destination directory is flushed after publication; durability uncertainty is surfaced as an error.
- Temporary files are cleaned on failure.
- Filesystems without hard-link support fail closed; no overwrite-prone fallback is used.

Added regression tests for successful restore, existing-destination preservation, foreign-key rejection, same/missing path rejection, cleanup and owner-only permissions.

### Acceptance boundary

This implementation strengthens the local restore mechanism for criterion 30. It does not itself close criterion 30. Closure still requires:
1. Exact-HEAD CI success for the implementation and tests.
2. Restore of the actual owner-controlled application database into a fresh destination on the target device/environment.
3. SQLite integrity and foreign-key checks.
4. Application-level readback for registry, entitlements, price alerts, coverage/gaps, OHLCV and durable outbox/replay state as applicable.
5. Post-restore write verification on the restored copy.
6. Timestamped, secret-free evidence report reviewed against the acceptance matrix.

The original database must not be modified, replaced or deleted. Do not count synthetic CI fixtures as owner-device evidence. No tick is awarded at implementation time.

### Remaining gate execution order

After criterion 30's target-device proof is obtained, work proceeds through criteria 20, 8, 25, 34, 35, 36, 38, 39 and 31, while repository-side preparation for all gates continues in parallel where it does not require external access. Criteria 31 retains the separate Google Play Termux signing-key and off-host key-custody blocker.


## Gate 10 execution batch 2 — CI passed, restore failure paths hardened — 2026-11-14

Exact implementation commit `13f489aebffa193affcb8eae619503e78e512b29` now has all three required CI workflows green:
- Automated Tests #43569886961 — SUCCESS.
- CodeQL #43569886954 — SUCCESS.
- Full Git History Secret Audit #43569886911 — SUCCESS.

The restore helper implementation has therefore passed repository CI on its exact commit. This does not close criterion 30 because actual owner-device application database restore evidence is still required.

Additional tests are being added for fail-closed behavior when POSIX permission setting fails, file flush fails, or atomic hard-link publication is unavailable. No test may overwrite the source database or publish an incomplete destination.

Termux was re-audited: upstream issues #1642 and #1648 remain open; the latest visible Play Store app release remains `googleplay.2026.10.09`. No verified compatible signing-key fix exists. No Termux command is required for this batch.

Stage 1 remains 300/400 = 75% provisional; all ten external gates remain open pending their respective evidence. Stages 2–6 remain NOT SCORED. The process indicator remains documentation-only, not an APK feature.


## Gate 10 batch 2 — exact-HEAD CI reconciliation — 2026-11-14

**Audited source HEAD:** `4e741f10d5c27dba7994742a45d08f2d1c590415`

All three required repository workflows completed successfully on this exact HEAD:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [#43570345495](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345495) | **SUCCESS** |
| CodeQL | [#43570345625](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345625) | **SUCCESS** |
| Full Git History Secret Audit | [#43570345516](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345516) | **SUCCESS** |

The Automated Tests workflow completed backend and frontend validation, production build and secret scans, backend dependency checks, container build, shared Redis guard/persistent-volume smoke test, image vulnerability scan/report, and cleanup. The new restore failure-path tests were included in this exact-HEAD run.

### Concrete repository-side remediation now verified

- Fresh-destination SQLite restore refuses to overwrite an existing destination.
- Restore validation checks SQLite integrity and foreign-key consistency.
- Publication is fail-closed when owner-only permissions cannot be set, the restored file cannot be flushed, or atomic hard-link publication is unavailable.
- Failure-path tests assert that no destination is published and temporary artifacts are cleaned up.
- The Termux audit record preserves the verified Google Play package-source/keyring state and does not propose an unsafe repository switch.

### Gate disposition after this CI run

No external criterion is closed and no acceptance ticks are awarded by CI alone.

| Criterion | Current status | Remaining acceptance evidence |
|---:|---|---|
| 8 | OPEN | Owner-host secret injection/log inspection and repository security-setting/alert inventory |
| 20 | OPEN | Real no-billing Firebase project/backend sign-in, expiry/revocation, entitlement denial and browser/Android reconnect drill |
| 25 | OPEN | Owner-host Redis TLS certificate, private binding/firewall, ACL, persistence and recovery |
| 30 | OPEN | Timestamped owner-device restore of the actual application database, application-domain readback and post-restore write on the restored copy |
| 31 | OPEN | Encrypted off-host backup, separate key custody, retention/access policy and successful key-recovery restore |
| 34 | OPEN | Actual owner-host persistent volume mount, ownership/permissions, restart, disk-pressure and recovery |
| 35 | OPEN | Owner-controlled HTTPS deployment, health/startup failure and backend-only secret injection |
| 36 | OPEN | Real reverse-proxy WSS handshake/auth/reconnect/resnapshot from browser and Android |
| 38 | OPEN | Self-hosted metrics/logs/dashboard, bounded retention, access control and redaction |
| 39 | OPEN | No-incremental-cost alert delivery, acknowledgement/escalation and incident recovery exercise |

Stage 1 remains **300/400 = 75% provisional**. Stage 2 remains unopened. The next practical owner-device evidence target remains criterion 30; it must use a fresh destination and must never overwrite or delete the source database.
