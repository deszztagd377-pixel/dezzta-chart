# DEZZTA CHART — Work Cycle 2026-11-18 Batch 40

## Cross-gate source audit and dependency blocker reassessment

**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Audit base SHA:** `2096356c4034dc2233f6c48a04a4d7579271ff52`  
**Main:** untouched  
**Cost:** ZERO COST  
**Termux:** not required  
**Deployment:** none created

### 1. Dependency blocker — disposition

The frontend dependency audit still fails on five High findings rooted in `picomatch@4.0.7`. The exact package paths are `vite → fdir → picomatch` and `vitest → tinyglobby → picomatch`. The package is resolved only in development tooling; the repository's dependency-boundary test verifies it is not part of the production dependency graph.

Current npm registry metadata still identifies 4.0.7 as latest. GHSA-fc5q-39xc-vjpf covers versions through 4.0.7 and does not list a fixed release. The upstream fix discussion is disputed and the proposed fix was not merged. Therefore there is no defensible patched version to install at this audit point. A Vitest major downgrade, older affected version, speculative override, local package patch, suppression, or audit-threshold change would either introduce unreviewed risk or misrepresent the security state. **No dependency files were changed.**

Operational containment: keep the package confined to trusted build/test tooling, do not accept untrusted user-supplied glob patterns in server/runtime paths, and retain fail-closed audit enforcement until a maintainer-supported resolution or a fully reviewed tooling replacement exists.

### 2. Gate 8 — runtime secrets

Source reviewed: `backend/app/config.py`, `backend/tests/test_config_security.py`, and `docs/SECURITY_CONFIGURATION.md`.

Verified in source/tests:
- secret-bearing settings fields are excluded from settings representations;
- alert-device encryption key is loaded from an absolute protected file;
- key file must be regular, bounded, canonical base64, exactly 32 bytes, and deny group/other POSIX access;
- missing, malformed, wrong-length, or permissively readable key files fail closed;
- frontend `VITE_*` values are explicitly treated as public configuration, not backend secrets.

Not accepted yet: actual owner-host injection, deployed runtime/bundle/log leakage checks on that host, and independent operational evidence. **Gate 8 remains OPEN.**

### 3. Gate 20 — identity and entitlement

Source reviewed: `backend/app/identity.py`, `backend/tests/test_identity.py`, `backend/app/entitlements.py`, `backend/tests/test_entitlements.py`, `src/auth/AuthProvider.tsx`, `src/auth/AuthProvider.test.tsx`, and `src/services/firebase.ts`.

Verified in source/tests:
- Firebase Admin ID-token verification explicitly requests `check_revoked=True`;
- issuer and audience must match the configured Firebase project;
- identity subject and auth_time are validated; malformed/oversized tokens fail closed;
- SDK errors are normalized to prevent credential/token detail leakage;
- entitlements default-deny and are scoped to verified account subject plus canonical instrument UUID;
- grant, revoke, regrant, unknown-instrument rejection, account isolation, and persistence have tests;
- frontend Firebase initialization rejects a mismatched pre-existing default app.

Not accepted yet: signed real Firebase-project E2E for valid, expired, revoked, and wrong-project tokens, plus deployed sign-in/session acceptance. Fake verifier and mocked frontend tests are not substitutes. **Gate 20 remains OPEN.**

### 4. Remaining gate evidence map

| Gate | Source/CI evidence present | Missing external acceptance |
|---|---|---|
| 25 | Production requires rediss + ACL; CI Redis smoke passed | Owner-controlled TLS/ACL, restart/failure recovery |
| 30 | Backup/restore source and synthetic integrity tests | Restore on intended host, post-restore read/write proof |
| 31 | Encryption/backup code and tests | Off-host copy, independent key custody, retention, drill |
| 34 | Persistent-volume smoke in CI | Existing host mount, ownership, disk pressure, restart durability |
| 35 | Production HTTPS CORS and secret-source constraints | Actual HTTPS certificate and host runtime secret proof |
| 36 | Browser lifecycle and React integration tests | Deployed WSS, Android WebView, 330s platform observation, Fluid read-back, fan-out |
| 38 | Authenticated process-local metrics routes and runbook | Host collector, retention/rotation, dashboard access, disk-pressure proof |
| 39 | Sanitized local alert events and runbook | Named adult operator, no-cost alert receipt, isolated recovery drill |

### 5. Progress and accounting

- Stage 1: **75% provisional** — 300/400 ticks; 30/40 criteria.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights and criterion mapping remain unapproved.
- No source review, unit test, CI success, or documentation edit awards a progress tick or closes a gate.

### 6. Cost and operational constraints

No Vercel deploy, Cloudflare resource, paid service, billing activation, publication, or Termux operation was performed. The phone-only owner must not be asked to administer production secrets, host operations, or incident response; those require the designated responsible adult system owner/authorized maintainer.

**Conclusion:** Gates 8 and 20 have meaningful source-level safeguards but remain externally unaccepted. The dependency audit remains blocked because no supported patched picomatch release is available. No unsafe workaround was applied.
