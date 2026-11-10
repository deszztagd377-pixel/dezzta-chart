# Stage 1 — Production Acceptance Matrix

Branch: `phase-2/market-data-foundation`

This matrix separates repository implementation from evidence that must come from a real deployment. A source-code check or a test file is **not** proof that the corresponding production control has passed. Do not mark an item complete without attaching reproducible evidence (CI run, deployment output, restore report, or monitoring test result).

## Status legend

- **Implemented / test present** — relevant code and/or regression coverage exists in this branch; execution on the current branch still needs recorded CI evidence.
- **External verification required** — requires a real provider, deployment, managed service, client, or operational exercise.
- **Approval / design required** — must not be implemented or enabled until the owner approves the scope and threat model.

## Forty-point acceptance checklist

### A. Configuration and secret handling

1. **Implemented / test present** — production startup requires a Redis URL.
2. **Implemented / test present** — production startup requires a Firebase project ID.
3. **Implemented / test present** — production Redis configuration requires the `rediss://` scheme.
4. **Implemented / test present** — production CORS origins must be exact HTTPS origins; wildcard origins are rejected.
5. **Implemented / test present** — shared HTTP/WebSocket limits reject booleans, non-integers, zero, and negative values.
6. **Implemented / test present** — Redis and provider credentials are excluded from settings representations.
7. **Implemented / test present** — safe provider defaults keep live and historical ingestion disabled.
8. **External verification required** — confirm production secrets are stored only in the hosting provider's secret manager and are absent from frontend bundles, logs, build output, and repository history.

### B. Identity and WebSocket authorization

9. **Implemented / test present** — Firebase Admin verifies signed ID tokens.
10. **Implemented / test present** — token verification requests revocation checking.
11. **Implemented / test present** — issuer, audience, subject, and authentication-time claims are validated.
12. **Implemented / test present** — conflicting Firebase `uid` and JWT `sub` claims are rejected.
13. **Implemented / test present** — malformed tokens, claims, SDK failures, and provider initialization errors fail closed with normalized messages.
14. **Implemented / test present** — browser WebSocket origins are checked against the exact allowlist before acceptance.
15. **Implemented / test present** — WebSocket authentication is required before authenticated subscriptions proceed.
16. **Implemented / test present** — instrument entitlement is checked against the verified principal, not a client-supplied account identity.
17. **Implemented / test present** — identity and authorization are periodically revalidated during a connection.
18. **Implemented / test present** — shared WebSocket admission enforces global and per-account connection limits.
19. **Implemented / test present** — expiring shared leases and release paths are implemented for WebSocket connections.
20. **External verification required** — exercise real Firebase sign-in, token expiry/revocation, entitlement denial, reconnect, and browser plus Android WebSocket flows against the deployed backend.

### C. Shared guards and service resilience

21. **Implemented / test present** — Redis health is required during shared-guard startup.
22. **Implemented / test present** — HTTP rate limiting fails closed when Redis operations fail.
23. **Implemented / test present** — WebSocket admission and lease operations fail closed on Redis errors.
24. **Implemented / test present** — shared counters and leases use atomic Redis Lua scripts.
25. **External verification required** — validate managed Redis TLS certificate checking, access controls, private networking, persistence policy, and failover behavior from the selected backend region.

### D. SQLite durability and backup

26. **Implemented / test present** — SQLite snapshots use the Online Backup API for transactionally consistent copies.
27. **Implemented / test present** — backup output is checked with `PRAGMA integrity_check`.
28. **Implemented / test present** — backup publication uses a temporary file and atomic replacement; a failed backup preserves the previous destination.
29. **Implemented / test present** — POSIX backup files are restricted to owner-only permissions, and failure to set permissions prevents publication.
30. **External verification required** — perform and record a restore drill from a real production-like backup into a fresh database, verifying application-level records as well as SQLite integrity.
31. **External verification required** — encrypt backups before off-host transfer, store encryption keys separately, enforce retention/access policy, and prove a restore using the documented key-recovery procedure.

### E. Container and deployment

32. **Implemented / test present** — the backend container runs the application as UID/GID `10001:10001`.
33. **Implemented / test present** — the CI workflow contains a Docker smoke test for volume ownership, SQLite integrity, restart persistence, and rate-limit behavior.
34. **External verification required** — provision the selected production persistent volume and verify mount path, owner, permissions, restart durability, and replacement behavior on that provider.
35. **External verification required** — deploy the backend with production configuration and verify HTTPS health checks, startup failure behavior, and backend-only secret injection.
36. **External verification required** — verify the deployed WSS handshake and authenticated subscription flow from supported web and Android clients through the real reverse proxy.

### F. Operations and production acceptance

37. **Implemented / test present** — the market-data status endpoint exposes bounded application-level operational state; it is not external monitoring.
38. **External verification required** — configure external metrics/log collection, retention, dashboards, and access controls.
39. **External verification required** — configure alert routing and demonstrate delivery to the responsible operator; document incident ownership, escalation, and recovery steps.
40. **Owner-approved design — complete (2026-11-10)** — the owner explicitly approved the detailed replay cursor model, outbox retention policy, reconnect semantics, benchmark plan, and short-lived scoped WebSocket-ticket threat model in [WEBSOCKET_RELIABILITY_DESIGN.md](WEBSOCKET_RELIABILITY_DESIGN.md). This closes the owner-approval criterion. Durable outbox/replay implementation still requires incremental code review and regression evidence; ticket exchange additionally remains gated on an independent security review before ticket code is added.

## Evidence required before Stage 1 can be marked 100%

- A successful GitHub Actions run for the exact release candidate commit, including frontend tests/build/security scan, backend pytest, dependency audit, Docker build, persistent-volume restart smoke test, and Trivy scan.
- A successful production-like Firebase + Redis + HTTPS/WSS integration run.
- A documented persistent-volume restart check and encrypted off-site backup restore drill.
- Evidence of monitoring and alert delivery, plus an approved incident/recovery procedure.
- Owner approval of the scoped replay/benchmark/ticket blueprint (completed 2026-11-10); independent security review remains mandatory before implementing ticket exchange.

**Current disposition:** Stage 1 is not production-accepted. The branch contains substantial implementation and regression coverage, but external acceptance evidence listed above is still outstanding. A green frontend deployment check alone does not satisfy these gates.

## Recorded CI evidence

The following CI evidence is recorded for the current checkpoint:

- Commit: `fcfa7c9c59520d55cba4554a6d4a9f45ba3ed26d`
- Workflow run: [DEZZTA CHART — Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42801624127)
- Run conclusion: **success** (2026-11-10)
- Verified workflow steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume container smoke test, Trivy container scan, vulnerability-report export and upload.
- This is CI evidence for the listed repository checks only. It does **not** prove real Firebase project integration, managed Redis provider configuration, production volume provisioning, encrypted off-site backup/restore, deployed HTTPS/WSS, external monitoring/alert delivery, or owner approval of the remaining design scope.

The CI workflow succeeding does not change the external acceptance status above. Stage 1 remains **not production-accepted** until every required external gate and the owner-reviewed design decision have reproducible evidence.

## Latest verified checkpoint — 2026-11-10

- Release-candidate branch: `phase-2/market-data-foundation`
- Commit: `969e5c9868c79006a1efc632a307cf8873ef03ad`
- Automated Tests & Build: [run 42804110006](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42804110006) — **success**.
- Verified workflow steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume container smoke test, Trivy container scan, vulnerability-report export and upload.
- CodeQL Security Analysis: [run 42804110246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42804110246) — **success** for both JavaScript/TypeScript and Python analysis jobs.
- The latest code change is documentation-only: it aligns the deployment guide's production startup example and hosting configuration with the already-required `FIREBASE_PROJECT_ID` setting. No runtime code was changed by this commit.
- These green workflows provide repository CI and static-analysis evidence for this exact commit. They do not satisfy the external deployment, managed Redis/Firebase integration, backup encryption/restore, production WSS, monitoring/alerting, or owner-approval gates listed above. Stage 1 therefore remains **not production-accepted**.


## Latest verified checkpoint — 2026-11-10 (commit 93d144c)

- Release-candidate branch: `phase-2/market-data-foundation`
- Exact tested commit: `93d144cc837be96ccb27a7bbb89d97be1b6035a3`
- Automated Tests & Build: [run 42805150877](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42805150877) — **success**.
- Verified steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume smoke test, Trivy image scan, vulnerability report export/upload.
- CodeQL Security Analysis: [run 42805150519](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42805150519) — **success** for JavaScript/TypeScript and Python.
- The owner approved the four design objectives on 2026-11-10. A scoped technical blueprint has been added in `docs/WEBSOCKET_RELIABILITY_DESIGN.md`; implementation remains gated on review of the detailed cursor/retention choices and ticket threat model.
- CI and CodeQL are repository evidence only. They do not prove production Firebase/managed Redis integration, provider entitlement/real-time market-data quality, production volume provisioning, encrypted off-site backup/restore, deployed HTTPS/WSS, monitoring/alert delivery, or market-data provider cost/availability.
- The design blueprint explicitly keeps live and historical provider ingestion disabled by default. No provider credentials, paid services, runtime behavior, or authentication flow were changed in this checkpoint.
- Stage 1 remains **not production-accepted** until all external gates and the scoped design review have reproducible evidence.


## Latest verified checkpoint — 2026-11-10 (commit bb60452)

- Branch: `phase-2/market-data-foundation`
- Commit: `bb604521d37262bdeb6745111c012a088429863a`
- Automated Tests & Build: [run 42807415946](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42807415946) — **success**.
- Verified: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume smoke test, Trivy image scan, vulnerability-report export/upload.
- Code change: corrected the WebSocket subscription identity type annotation to use the same 10-field canonical series identity returned by `identity_for`; runtime behavior was not changed.
- Owner approval: the detailed WebSocket reliability blueprint was explicitly approved on 2026-11-10. The separate security review remains required before ticket-exchange code.
- The green CI run is repository evidence only. It does not satisfy the external Firebase/managed Redis integration, real deployment volume, encrypted off-host backup/restore, deployed HTTPS/WSS, monitoring/alert delivery, or market-data licensing/provider gates.

**Current checklist accounting:** 30/40 criteria have repository implementation/test evidence or completed owner approval; 10/40 remain external production verification gates. This is a checklist count, not a production-readiness percentage. Stage 1 remains **not production-accepted**.
