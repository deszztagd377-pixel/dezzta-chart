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
