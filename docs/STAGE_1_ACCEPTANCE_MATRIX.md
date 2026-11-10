> **OWNER CONSTRAINT — ZERO MONEY (2026-11-10):** All Stage 1 acceptance work must comply with [ZERO_COST_POLICY.md](ZERO_COST_POLICY.md). Do not provision Fly.io, paid Redis, paid market-data APIs, paid backup/monitoring, paid email/SMS, paid runners, or any trial/plan that can create a charge. Earlier Fly.io deployment research is superseded and must not be executed. If a criterion cannot be satisfied at zero incremental cost, record it as constrained/deferred rather than purchasing a service.

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


## Latest verified checkpoint — 2026-11-10 (commit 26a9ed8)

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `26a9ed840449cab9abeb573d5029b02d8fcbe998`
- Automated Tests & Build: [run 42810062870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42810062870) — **success**.
- CodeQL Security Analysis: [run 42810062624](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42810062624) — **success** for JavaScript/TypeScript and Python.
- Verified steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret scanner and production credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume smoke test, Trivy image scan, vulnerability-report export/upload.
- The backend test suite initially exposed one invalid test fixture (close=999 while high=103). The fixture was corrected to a valid but different close=102, preserving the intended exact-payload mismatch test. The rerun passed.
- Implementation: durable outbox cursor and persisted event ID now propagate into the WebSocket snapshot and live notification path. The callback resolves the exact stored event for each source/derived bar revision rather than assuming the global latest cursor belongs to that bar.
- Still outstanding: WebSocket reconnect cursor input and durable replay delivery, expired-cursor resnapshot protocol at the socket layer, replay authorization/pagination integration, and sustained throughput/reconnect benchmarks.
- Feed coverage is not all-pair by default: `DATABENTO_LIVE_SYMBOLS` defaults empty and the live source subscribes only to explicitly configured raw contract symbols. The current default allowed roots are ES, NQ, and GC. Real-time coverage requires lawful provider entitlement, credentials, and explicit configured symbols.
- This CI/CodeQL evidence does not satisfy real production Firebase/managed Redis integration, provisioned production volume, encrypted off-host backup/restore, deployed HTTPS/WSS, external monitoring/alert delivery, or market-data licensing/provider coverage.

**Checklist remains 30/40 with 10 external production gates outstanding.** The durable cursor bridge is a partial implementation increment and does not close the full reconnect/replay acceptance requirement. Stage 1 remains **not production-accepted**.


## Latest verified implementation checkpoint — durable WebSocket replay (2026-11-10)

- Branch: `phase-2/market-data-foundation`
- Exact code commit tested: `38174c9c4e6280669649cb4677426809c37d9cf5`
- Automated Tests & Build: [run 42812016639](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812016639) — **success**.
- CodeQL Security Analysis: [run 42812016650](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812016650) — **success** for JavaScript/TypeScript and Python.
- Verified: frontend dependency audit/unit tests/build/secret scans; backend pytest/dependency audit; Docker image build; Redis + persistent-volume smoke test; Trivy image scan; vulnerability report export/upload.
- Implementation now accepts an optional decimal-string reconnect cursor, authorizes the exact series before replay, performs bounded exact-series replay, and hands off to live updates with a new contiguous stream sequence. Expired/ahead cursors, replay storage errors, and excessive backlog explicitly fall back to a fresh snapshot.
- Frontend stream client and supervisor now preserve the last accepted durable cursor across transient socket reconnects, apply replay events through the existing validated update path, and retain the current chart while reconnecting. Cursor values remain strings to avoid JavaScript integer precision loss.
- Added backend and frontend regression coverage for replay ordering, exact series identity, cursor-ahead resnapshot, cursor precision, replay/live transition, and supervisor reconnect.
- This remains repository evidence, not production browser/Android WSS proof. Sustained throughput/reconnect benchmarks and real production provider latency/gap evidence remain outstanding.

**Checklist accounting remains 30/40, with 10 external production verification gates outstanding.** No external gate is marked complete by source-code changes or CI alone. Stage 1 remains **not production-accepted**.


## Latest verified checkpoint — reconnect cursor hardening (2026-11-10)

- Branch: `phase-2/market-data-foundation`
- Exact code commit: `9cb7a876bca9215b7792312aa908b3ad60e0b5a6`
- Automated Tests & Build: [run 42812627122](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812627122) — **success**.
- CodeQL Security Analysis: [run 42812627082](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812627082) — **success** for JavaScript/TypeScript and Python.
- Latest regression hardening rejects non-ASCII digit cursor strings, decimal strings, and values outside signed SQLite 64-bit range; malformed cursors are rejected with the expected WebSocket close code.
- Verified workflow steps include frontend dependency audit/unit tests/build/secret scans, backend pytest/dependency audit, Docker image build, Redis + persistent-volume smoke test, Trivy scan, and vulnerability-report export/upload.
- These checks validate repository behavior only. They do not prove every market pair is configured or entitled, every timeframe has live provider coverage, or production Firebase/Redis/HTTPS/WSS, backup restore, monitoring, and alert delivery have passed.

**Checklist remains 30/40 with 10 external production verification gates outstanding.** The reconnect cursor hardening does not close any external gate. Stage 1 remains **not production-accepted**.


## Verified implementation — replay I/O event-loop isolation (2026-11-10)

- Candidate code commit: `dac22020bfe10e48cef58f5125ee3e6d341bc969` on `phase-2/market-data-foundation`.
- The SQLite durable replay page read is executed with `asyncio.to_thread`, preventing the bounded synchronous SQLite query from occupying the ASGI event-loop thread. Subscription-before-replay and queue handoff remain unchanged.
- Exact branch-head verification commit: `63469d9cb4d4557e4e3c992056ea2a732a1e5ea2`. This commit descends from the replay candidate and was tested as a whole.
- Automated Tests & Build: [run 42815030378](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030378) — **success**. Frontend unit tests/build/secret scans, backend pytest/dependency audit, Docker build, Redis + persistent-volume smoke test, Trivy scan and report export all passed.
- CodeQL Security Analysis: [run 42815030406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030406) — **success** for JavaScript/TypeScript and Python.
- No external production gate is closed by this code change or by repository CI alone.

## Market-data coverage and timeframe readiness — explicit acceptance blockers

This is an additional operational/functional acceptance track; it does not change the 40-point checklist count above.

- The live adapter currently requests the Databento `ohlcv-1s` schema and subscribes only to the explicit `DATABENTO_LIVE_SYMBOLS` raw-contract allowlist. The setting defaults to empty. Therefore the repository does not provide all-pair LIVE coverage by default.
- Supported timeframe identifiers include `1s, 5s, 15s, 30s, 45s, 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 4h, 1d, 1w, 1M, 3M`. Most are intended to be derived from accepted child bars; a timeframe being listed is not proof that a live series is currently produced.
- The aggregator deliberately fails closed for `CME_SESSION_V1` bars until verified session-aligned bucket bounds are available. In particular, it currently skips derivation for CME-session bars rather than risk assigning futures bars to incorrect UTC/session buckets. UTC-fixed derivation also stops before daily/weekly/monthly periods. This means the code must not be represented as delivering every timeframe for CME futures.
- `backend/app/databento_sources.py` explicitly labels its official SDK wrappers **UNVERIFIED**; the real SDK calls have not yet been exercised with valid provider credentials in CI or a production-like environment.
- Before claiming all-pair/all-timeframe LIVE readiness, require: (1) real SDK connection and callback verification for the pinned SDK version, (2) approved provider entitlements and a complete configured instrument universe, (3) exchange-calendar-aware intraday and higher-timeframe bucket derivation with DST/holiday/early-close tests, (4) per-instrument/per-timeframe gap and completeness checks, and (5) measured event-to-client latency and reconnect recovery across every supported timeframe.

**No source-code shortcut is accepted for these requirements.** Existing fail-closed behavior is intentional protection against fabricated or misaligned candles. Replay I/O event-loop isolation was verified on ancestor commit `63469d9cb4d4557e4e3c992056ea2a732a1e5ea2` by successful Automated Tests and CodeQL runs 42815030378 and 42815030406. The current calendar publication timestamp hardening is a separate change and remains pending its own exact-commit CI; neither change proves feed coverage or timeframe derivation.


## Latest verified branch-head checkpoint — 2026-11-10

- Branch: `phase-2/market-data-foundation`
- Exact branch head: `63469d9cb4d4557e4e3c992056ea2a732a1e5ea2`
- Automated Tests & Build: [run 42815030378](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030378) — **success**.
- CodeQL Security Analysis: [run 42815030406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030406) — **success**.
- The exact branch head includes the replay I/O isolation candidate and its prior implementation history. Workflow jobs were inspected individually; every listed job and step completed successfully.
- Checklist accounting remains 30/40 with 10 external production verification gates outstanding. Market-data provider, symbol-universe, SDK, calendar-aware timeframe, and latency requirements remain additional functional acceptance blockers. Stage 1 remains **not production-accepted**.


## Stage 1 integrated functional workstream — session-aware timeframe derivation

This is an additional functional acceptance track **inside Stage 1**, not a separate stage and not a replacement for any of the 40 production checklist criteria. The owner approved the engineering blueprint on 2026-11-10 for staged implementation.

- Approved engineering basis: [SESSION_AWARE_AGGREGATION_BLUEPRINT.md](SESSION_AWARE_AGGREGATION_BLUEPRINT.md).
- Current CME-session aggregator remains fail-closed. The calendar artifact still needs explicit tradable segments and intraday breaks; bucket alignment must be grounded in authoritative exchange specifications.
- This workstream must be completed and tested before claiming supported futures timeframes. Approval alone does not mark it complete or production-ready.
- The 10 external production gates remain outstanding independently. The 40-point matrix will not be reduced or marked complete merely because this workstream is approved.



## Latest code hardening checkpoint — calendar publication timestamp (2026-11-10)

- Code commit: `088e91dc135e65adbb0ad176f89a5c32cfec6df4`.
- Test commit / current branch head: `1f52e8053fbd6ed50ce94b2cf93ac906ff75814e`.
- `SessionCalendar.published_at_utc` now rejects aware timestamps with non-zero UTC offsets and normalizes valid zero-offset timestamps to `timezone.utc`.
- Regression test covers conversion from America/Chicago to UTC and rejection of non-UTC offsets.
- Exact-commit Automated Tests run: [42816364225](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816364225) — queued at the latest inspection.
- Exact-commit CodeQL run: [42816364046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816364046) — analysis in progress at the latest inspection.
- This hardening does not change the 30/40 checklist evidence count or close any production gate. Do not mark it CI-verified until both workflows finish successfully.


## Latest exact-commit verification — calendar UTC test repair (2026-11-10)

- Branch: `phase-2/market-data-foundation`.
- Exact tested commit: `cc2914e95aa6646a4b5dcba9f5c76dfd60992d59`.
- The production invariant is unchanged: `published_at_utc` must have a zero UTC offset and is normalized to canonical `timezone.utc`. The regression fixture was corrected to use a zero-offset timezone for the normalization case; a Chicago (UTC-6) timestamp remains explicitly rejected.
- Automated Tests & Build: [run 42816899715](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816899715) — **success**. Every step passed, including frontend audit/tests/build/secret scans, backend pytest/dependency audit, Docker build, Redis + persistent-volume smoke test, Trivy scan, and vulnerability report export/upload.
- CodeQL: [run 42816899668](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816899668) — **success** for both Python and JavaScript/TypeScript jobs.
- This closes the pending CI verification for the UTC timestamp hardening only. It does not implement session-aware aggregation, verify the Databento SDK against a real account, or satisfy any external production gate.
- Checklist accounting remains **30/40** with **10 external production verification gates** outstanding. Stage 1 remains **not production-accepted**.


## Latest exact-commit CI verification — 2026-11-10

- Exact commit: 7b41c5a3ead82cb07f428b10474ba01267a45c60 on phase-2/market-data-foundation.
- Automated Tests & Build: [run 42817566167](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42817566167) — **success**. All steps completed successfully, including frontend dependency audit, unit tests, build, bundle-secret scans, backend pytest, backend dependency audit, Docker build, isolated Redis + persistent-volume restart smoke test, Trivy image scan, vulnerability report export, and artifact upload.
- CodeQL Security Analysis: [run 42817566002](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42817566002) — **success** for Python and JavaScript/TypeScript analysis.
- This exact-commit CI evidence supersedes the earlier pending/queued checkpoint notes above for the 7b41c5a commit. It verifies repository CI and an ephemeral CI volume/Redis test only; it does **not** prove a Fly deployment, managed Redis, production Firebase credentials, a production Fly Volume, encrypted off-host backup/restore, production WSS, or external monitoring/alert delivery.
- External production gates remain **10/40 outstanding**. Stage 1 remains **not production-accepted** and the checklist count is unchanged.


## Mandatory zero-cost acceptance overlay — owner decision 2026-11-10

- The owner has explicitly prohibited all project charges and unexpected future bills. This is a mandatory constraint across all 40 criteria, including hosting, identity, market data, backup, monitoring, alert delivery, CI, and operations.
- The Fly.io plan is superseded as an executable deployment target. Do not create an app, Machine, Volume, managed Redis instance, billing account, or trial.
- Databento live/historical access remains disabled; no paid market-data API or dataset may be used. A free source must be independently checked for lawful use, coverage, freshness, quotas, and no billing exposure before adoption.
- Firebase is permitted only if the exact selected authentication methods remain within a verified no-billing plan. Phone/SMS and billing upgrades are prohibited. If billing is required, defer the integration rather than upgrade.
- Any no-cost replacement for managed Redis or external operations tooling must preserve the existing security guarantees and be reviewed/tested before changing production requirements. No insecure in-memory fallback is allowed.
- A free tier or promotional credit alone is not evidence of zero cost. Payment methods, automatic upgrades, overages, trial conversion, and quota exhaustion behavior must be checked. Unknown billing behavior means do not enable the service.
- This overlay does not reduce the 40 criteria, does not close external gates, and does not change the current 30/40 evidence accounting. Stage 1 remains not production-accepted.


## Ten remaining external gates — zero-cost remediation register (2026-11-10)

The following ten criteria are audited individually. ZERO MONEY is binding, so none may be closed by purchasing a service, enabling billing, attaching a payment method, starting a trial, or accepting an overage. A repository test is not a substitute for the real-host evidence required by an external gate.

| Criterion | Current status | Zero-cost handling plan | Evidence still required |
|---|---|---|---|
| 8 — production secret storage | **Open — host not provisioned** | Use the operating system's protected secret/environment mechanism on an already-owned host; keep secrets out of Git, frontend bundles, logs, and chat. Do not buy a managed secret store. | Inspect the actual host's permissions and process environment; scan deployed artifacts/logs. |
| 20 — real Firebase identity flow | **Open — no real project verification** | Keep the integration disabled until a no-billing Firebase configuration and non-billable sign-in method are verified. Use emulator-based regression tests where possible without billing. Never enable phone/SMS or upgrade to a billing plan. | Real signed-token, expiry/revocation, entitlement-denial, reconnect and web/Android test against a verified no-billing project. If that cannot be guaranteed, defer production auth integration. |
| 25 — managed Redis TLS/access/failover | **Open — managed service prohibited** | Candidate alternative: self-host Redis on the same already-owned host, with TLS, authentication, private binding, persistence policy, and fail-closed application behavior. No in-memory fallback. | Owner-approved topology plus tests for TLS certificate validation, access restrictions, Redis outage, restart/persistence and recovery. A single local Redis instance does not prove managed failover or high availability. |
| 30 — production-like backup restore | **Open — external drill not recorded** | Run SQLite Online Backup API restore tests locally against a fresh database and verify known application-level records, not only SQLite integrity. Use existing storage only. | Dated restore report from the actual chosen host and backup location. |
| 31 — encrypted off-host backup/key recovery | **Open — no destination or key custody verified** | Candidate: client-side encryption with an open-source tool and key material held separately on storage already owned by the project owner. No paid cloud bucket, paid KMS, or new storage purchase. | Confirm existing off-host storage is available at zero incremental cost; prove encryption, access restriction, retention, key recovery, and a successful restore. If no suitable existing storage exists, keep this gate open. |
| 34 — production persistent volume | **Blocked by zero-cost decision — Fly.io superseded** | Do not create a Fly Volume. Candidate replacement is a persistent local disk/directory on an already-owned machine, with explicit permissions and a single-writer SQLite topology. | Owner confirms an existing host/storage resource; verify mount/path ownership, restart durability, replacement/recovery. No new hardware or hosting purchase. |
| 35 — production HTTPS deployment | **Blocked by zero-cost decision — Fly.io superseded** | Do not deploy to Fly or buy a domain/hosting. Candidate is a service on an already-owned host. Public HTTPS is only acceptable if an existing domain/network path and certificate can be used without charges; otherwise keep service local and mark public production deployment deferred. | Verify actual HTTPS endpoint, health/startup behavior, secret injection, and certificate renewal without creating a bill. |
| 36 — production WSS through reverse proxy | **Open — no deployed endpoint** | First run local reverse-proxy/WSS integration tests on existing hardware, preserving origin checks and authenticated subscription. No paid CDN, tunnel, proxy, or hosting. | Successful web and Android client handshake/subscription against the actual zero-cost deployment path. |
| 38 — external monitoring/logging | **Open — no external collector** | Prefer bounded local logs/metrics and a self-hosted dashboard on existing hardware. No paid observability service or usage-metered log retention. | Verify retention limits, access controls, dashboard availability, and that monitoring does not expose secrets. |
| 39 — alert delivery/incident response | **Open — delivery channel unverified** | Implement local alert records/logs and a documented manual response path first. Do not use paid SMS, email, paging, or trial services. | Demonstrate an alert reaches an already-available no-cost operator channel; test acknowledgement/escalation/recovery. Otherwise document manual-only operations and keep external delivery gate open. |

### Hard boundary before changing the architecture

- The candidate local/self-hosted alternatives are **design options**, not proof that the owner has suitable hardware, network access, backup media, a domain, or a free alert channel.
- Do not change production startup validation, weaken Redis fail-closed behavior, enable a provider, or publish a public endpoint until the zero-cost alternative has been reviewed and its security tests pass.
- The owner must not buy hardware, hosting, domains, storage, or subscriptions to close these gates. If existing resources are insufficient, the affected production capability remains deferred.
- The ten gates remain open. No percentage or checklist count is increased by this remediation register.

