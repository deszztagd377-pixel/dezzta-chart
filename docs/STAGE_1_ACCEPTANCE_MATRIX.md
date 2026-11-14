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
8. **External verification required** — confirm production secrets use an owner-controlled, no-billing host secret-injection mechanism (for example OS-protected service credentials) and are absent from frontend bundles, logs, build output, and repository history. Do not introduce a paid secret manager.

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
20. **External verification required / constrained by ZERO MONEY** — exercise real Firebase sign-in, token expiry/revocation, entitlement denial, reconnect, and browser plus Android WebSocket flows only if a no-billing configuration is verified. Otherwise keep production Firebase integration disabled and defer this gate; never enable Blaze.

### C. Shared guards and service resilience

21. **Implemented / test present** — Redis health is required during shared-guard startup.
22. **Implemented / test present** — HTTP rate limiting fails closed when Redis operations fail.
23. **Implemented / test present** — WebSocket admission and lease operations fail closed on Redis errors.
24. **Implemented / test present** — shared counters and leases use atomic Redis Lua scripts.
25. **External verification required / managed paid Redis prohibited** — validate TLS certificate checking, ACLs, private-network binding, persistence, restart and failure behavior for a self-hosted Redis instance on existing owner-controlled hardware. Do not purchase managed Redis.

### D. SQLite durability and backup

26. **Implemented / test present** — SQLite snapshots use the Online Backup API for transactionally consistent copies.
27. **Implemented / test present** — backup output is checked with `PRAGMA integrity_check`.
28. **Implemented / test present** — backup publication uses a temporary file and atomic replacement; POSIX snapshot data is flushed before publication and the parent directory is flushed after rename; pre-publication failures preserve the previous destination. Directory-flush failure is surfaced because rename durability is uncertain.
29. **Implemented / test present** — POSIX backup files are restricted to owner-only permissions, and failure to set permissions prevents publication.
30. **External verification required** — perform and record a restore drill from a real production-like backup into a fresh database, verifying application-level records as well as SQLite integrity.
31. **External verification required** — encrypt backups before off-host transfer, store encryption keys separately, enforce retention/access policy, and prove a restore using the documented key-recovery procedure.

### E. Container and deployment

32. **Implemented / test present** — the backend container runs the application as UID/GID `10001:10001`.
33. **Implemented / test present** — the CI workflow contains a Docker smoke test for volume ownership, SQLite integrity, restart persistence, and rate-limit behavior.
34. **External verification required** — configure a persistent data volume on existing owner-controlled hardware and verify mount path, owner, permissions, restart durability, disk-pressure behavior, and recovery. Do not provision a paid provider volume.
35. **External verification required / zero-cost constrained** — run the backend on existing owner-controlled hardware and verify HTTPS health checks, startup failure behavior, and backend-only secret injection. Expose it publicly only if the existing network/domain path is verified to create no incremental charge; otherwise keep it local/LAN and defer public deployment.
36. **External verification required** — verify the WSS handshake and authenticated subscription flow from supported web and Android clients through a reverse proxy on the owner-controlled host. Do not purchase hosting, domain, or CDN to satisfy this gate.

### F. Operations and production acceptance

37. **Implemented / test present** — the market-data status endpoint exposes bounded application-level operational state; it is not external monitoring.
38. **External verification required / paid observability prohibited** — configure self-hosted metrics/log collection, bounded retention, dashboards, and access controls on existing hardware, or explicitly defer if resource limits prevent safe operation.
39. **External verification required / paid delivery prohibited** — demonstrate a no-incremental-cost local alert path and document incident ownership, escalation, and recovery steps. Do not assume email/SMS/push delivery is free.
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



## Zero-cost disposition for all ten external gates — 2026-11-10

The owner-mandated ZERO MONEY policy is binding across Stage 1 and all later stages. The gate-by-gate resolution plan is documented in [STAGE_1_ZERO_COST_GATE_PLAN.md](STAGE_1_ZERO_COST_GATE_PLAN.md). It specifies no-billing candidate approaches, required evidence, and explicit defer conditions for criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39.

This plan is not production evidence and does not close any external criterion. No paid provider, hosting, managed Redis, Firebase billing upgrade, paid backup/KMS, paid monitoring/alerting, domain, trial, or paid runner is authorized. If an existing owner-controlled environment cannot meet a gate safely at zero incremental cost, keep that gate open/constrained rather than weakening controls or creating a payment obligation.


## Android debug APK — owner-reported smoke test (2026-11-13)

- The owner installed the generated debug APK on the Infinix GT20 and confirmed that the app launches and displays the chart screen.
- The owner opened Settings, cleared the app cache, relaunched the app, and reported that it remained operational without a visible issue.
- The screenshot shows the chart's explicit `DEMO DATA · SAMPLE OHLC` label. This is evidence of Android packaging and a limited UI launch/cache-relaunch smoke test only; it is **not** evidence of live CME data, Firebase authentication, backend connectivity, production WSS, notification delivery, or production readiness.
- This is owner-reported manual evidence, not an independently captured device test report. No Stage 1 criterion is closed or re-counted from this report.
- Push/local notification delivery is intentionally deferred to its planned later stage. Stage 1 must not claim notification delivery as implemented or verified.
- No app code was changed as part of recording this manual test. The existing APK build and CI evidence remain tied to their recorded commits and workflow runs.




## Latest verified checkpoint — SQLite backup durability on Android (2026-11-13)

- Branch: `phase-2/market-data-foundation`
- Exact tested branch-head commit: `58594459ee60113e75ea3c4d908e1d56ac3eec4b`
- Code changes:
  - `47c6c736` — flush the SQLite snapshot file before atomic publication; fail closed on flush failure.
  - `f2ba7bde` — flush the parent directory after atomic replacement; surface directory-flush failure instead of claiming confirmed durability.
  - `3ec67dcb` and `58594459` — regression tests for snapshot flush failure, parent-directory flush invocation, and post-replacement directory-flush failure semantics.
- Automated Tests & Build: [run 43407628746](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43407628746) — **success** for the exact branch-head commit. All 28 job steps completed successfully, including frontend unit tests/build, backend pytest, dependency audits, synthetic SQLite outbox benchmark, Docker build, Redis + persistent-volume container smoke test, Trivy image scan, and vulnerability-report export/upload.
- CodeQL Security Analysis: [run 43407628566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43407628566) — **success** for the same commit.
- Owner-device smoke test: the owner pulled the exact branch head into Termux on Android and ran the SQLite backup helper. Observed `PRAGMA integrity_check = ok`, restored/read value `DEZZTA_OK`, and `ANDROID_BACKUP_TEST: SUCCESS`. This verifies the basic backup and directory-fsync path on that device/filesystem.
- Scope limitation: the Android smoke test used a temporary local source and backup file; it is not the production-like application restore drill in criterion 30, a power-loss test, or an off-host restore. Criteria 30 and 31 remain external verification gates.
- No paid service, provider credential, production deployment, or feature removal was introduced by this work.

**Checklist accounting remains 30/40, with 10 external production verification gates outstanding.** The new Android smoke test and green CI/CodeQL runs strengthen repository/device evidence but do not close external deployment gates. Stage 1 remains **not production-accepted**.


## Latest verified checkpoint — 2026-11-13 (commit 08bdf52)

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `08bdf52cb60b2c98216df2437b3f9363cd4e2d66`
- Automated Tests & Build: [run #1006](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43413442206) — **success**.
- CodeQL Security Analysis: [run #364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43413442133) — **success** for Python and JavaScript/TypeScript.
- Backend regression suite: **774 passed in 24.03s**. Frontend tests/build, backend dependency audit, synthetic SQLite outbox benchmark, Docker build, Redis + persistent-volume smoke test, Trivy image scan, and vulnerability-report export/upload also passed.
- CME daily aggregation now consumes only validated UTC 1-hour child bars, matching the accepted ADR. Finer bars continue through the normal UTC intraday hierarchy; each 1-hour interval is re-resolved against the pinned calendar and rejected if it crosses a tradable-segment boundary. Regression tests cover direct 1-hour input, 1-second cascade through an open 1-hour child, complete 1-minute-to-1-hour-to-daily derivation, and split-session rejection.
- The synthetic CME calendar fixtures are test-only. No authoritative production CME schedule is loaded, and no live provider entitlement or production client path is established by this CI.
- The synthetic outbox benchmark now exercises concurrent replay readers alongside the single SQLite writer; it remains a single-process benchmark, not a production or multi-process SLO.
- **Acceptance accounting remains 30/40, with 10 external production gates open:** 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39. No external gate is closed by this repository-only work. Stage 1 remains **not production-accepted**.


## Owner-confirmed one-phone/no-PC constraint — 2026-11-13

The owner has one Android device (Infinix GT20, Android 15) and no second phone, PC, or laptop. This constraint supersedes all candidate remediation text above that assumes an additional owner-controlled host or second device. Do not ask the owner for a second device again and do not propose purchasing hardware or enabling paid infrastructure.

The ten open production gates remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Their phone-only feasibility is classified in STAGE_1_ZERO_COST_GATE_PLAN.md, section **Owner-confirmed device constraint and phone-only disposition**.

- Criterion **30** is the nearest same-device candidate: the SQLite Online Backup API and restore-to-fresh-path flow can run using Python/SQLite standard-library support. Existing device evidence covers integrity/readback smoke, and CI includes application-record restore tests; one consolidated application-record restore report from the owner's device is still missing. This does not satisfy off-host disaster recovery.
- Criterion **31** remains blocked by lack of a second device/verified off-host destination and the unresolved Termux Play Store cryptography>=50,<51 package/keyring mismatch.
- Localhost, CI, APK, and local-storage tests can strengthen evidence for criteria 8, 20, 25, 34, 35, 36, 38, and 39, but do not prove production host, public endpoint, independent monitoring, or operator delivery.

No criterion is closed and the 30/40 provisional accounting is unchanged by this constraint record. Do not change the production acceptance definition or claim 40/40 without owner-approved scope revision and evidence.


## Criterion 8 repository-side audit update — 2026-11-13

Repository-side defense-in-depth now includes a pre-build scan of frontend JS/JSX/TS/TSX source, the existing post-build production-bundle scan, a TSX token-pattern regression test, and backend settings \`repr()\`/\`str()\` redaction tests. The exact-HEAD CI and CodeQL runs are recorded in \`docs/PROJECT_PROGRESS.md\`; their conclusions must be checked before acceptance.

This does **not** change criterion 8 from **External verification required**. The owner-controlled host's secret-injection mechanism, deployed runtime/build logs, GitHub secret-scanning settings/alerts, and reachable repository history remain unverified. No paid secret manager or billing-enabled infrastructure may be introduced.


## Criterion 8 repository-side audit update — 2026-11-13 (verified)

The full reachable Git-history scan is now implemented in CI using Gitleaks v8.30.1, a full-depth checkout, `--log-opts="--all"`, and a SHA-256-verified release archive. Dedicated run [#43451610210](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610210) scanned **1,133 commits (~2.57 MB)** and reported **no leaks**. Integrated CI [#43451610297](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610297) and CodeQL [#43451610192](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610192) both passed on commit `efdf9a9ecfa68647586cd89f819e76469e11d3df`.

This closes the repository-side reachable-history scan subtask only. Criterion 8 remains **External verification required** until the owner-controlled production host's secret-injection mechanism and deployed logs are inspected, and GitHub native secret-scanning/push-protection settings plus alert inventory are verified. The history scan does not prove the absence of secrets in unreachable Git objects or external clones.
## Stage 1 progress tick display — 2026-11-14

This is the project's progress indicator scale requested by the owner. It is **not** a technical indicator inside the APK and does not refer to market-price ticks.

### Scale

- 40 Stage 1 acceptance criteria × 10 display ticks each = **400 total ticks**.
- 1 accepted criterion = 10 ticks = 2.5% Stage 1 progress.
- 1 tick = 0.25 percentage points of Stage 1 progress.
- A criterion receives all 10 ticks only when its complete acceptance condition and required evidence are met. No inferred fractional/sub-tick credit.

### Current audited tally

| Item | Ticks | Stage 1 share |
|---|---:|---:|
| 30 provisionally accepted/implemented criteria | **300 / 400** | **75%** |
| 10 external verification criteria still open | **100 / 400 outstanding** | **25%** |
| Total | **400 / 400** | **100% scale** |

Open criteria (0/10 ticks each): **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stage 1 remains **not production-accepted**. “300 ticks” is the finer representation of the existing provisional 30/40 tally, not a new completion award.

### Tick change policy

A future tick change must cite the criterion number, its full acceptance boundary, exact evidence/report, and exact tested commit. Repository work toward an external gate is progress in remediation but does not earn that gate's ticks before its external evidence exists. CI/documentation/commit volume alone never changes the tally. The tick scale is separate from the overall weighted project percentage and from the in-app technical indicator tracker.


## Ten-gate work-cycle audit — 2026-11-14

See [STAGE_1_ZERO_COST_GATE_PLAN.md](STAGE_1_ZERO_COST_GATE_PLAN.md) for the per-gate disposition. Repository-side test expansion now covers a single restored application database across instrument registry, entitlements, alert zones, coverage intervals/gaps, OHLCV and durable outbox, including a post-restore write. The new shared-application-database restore test passed exact-commit CI on `e599b45d480c29f195d53047cf9b301182a74de0` (Automated Tests #43566762952).

This strengthens criterion 30's repository-side evidence only. It does not satisfy the required target-environment restore drill. Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 all remain **OPEN / external verification required**; no ticks are awarded by this test or its CI result alone.


## Criterion 20 implementation status correction — 2026-11-14

The source audit confirms the Firebase client prototype is already integrated and mounted; the previous statement that the frontend had not yet been connected is stale. Owner setup context records a registered Firebase Web App on the Spark/no-billing path with Google Sign-In and Email/Password methods enabled. The source includes email registration/sign-in, Google redirect, auth-state/ID-token observer, fresh token acquisition for WebSocket reconnect, backend Firebase Admin verification with `check_revoked=True`, entitlement enforcement and periodic WebSocket revalidation.

This is **repository implementation plus owner-configured provider setup**, not a completed real-provider integration drill. Live project billing state, actual frontend runtime configuration, backend Admin credential injection, real sign-in, revocation/expiry, entitlement denial and browser/Android WSS reconnect evidence remain required. Criterion 20 stays OPEN and receives no acceptance ticks.


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


## Criterion 30 — exact-HEAD CI passed; target-device evidence still required — 2026-11-14

The fresh-destination restore implementation in `backend/app/sqlite_backup.py` passed the exact-HEAD CI workflows on `13f489aebffa193affcb8eae619503e78e512b29`:
- Automated Tests #43569886961 — SUCCESS.
- CodeQL #43569886954 — SUCCESS.
- Full Git History Secret Audit #43569886911 — SUCCESS.

The helper verifies SQLite integrity and foreign-key consistency, refuses to overwrite a destination, publishes through an atomic same-directory hard link, applies owner-only POSIX permissions, flushes the restored file and parent directory, and cleans temporary files on failure.

This is repository implementation evidence only. Criterion 30 remains **OPEN** until an actual owner-device application database restore is completed into a fresh destination, with application-level readback of the durable domains and a post-restore write on the restored copy. The source database must remain untouched. No tick is awarded by CI alone.


## Gate 10 batch 2 — restore failure-path CI evidence — 2026-11-14

Exact source HEAD: `4e741f10d5c27dba7994742a45d08f2d1c590415`

The restore helper's failure behavior is now covered by three additional regression tests:

- `test_restore_fails_closed_when_owner_only_permissions_cannot_be_set`
- `test_restore_fails_closed_when_restored_file_cannot_be_flushed`
- `test_restore_fails_closed_when_atomic_publication_is_unavailable`

Together with the five baseline restore tests, the focused restore module contains eight tests. The new tests verify fail-closed publication behavior and temporary-file cleanup for permission, flush and atomic-publication failures.

Exact-HEAD CI:
- Automated Tests [#43570345495](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345495) — **SUCCESS**.
- CodeQL [#43570345625](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345625) — **SUCCESS**.
- Full Git History Secret Audit [#43570345516](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345516) — **SUCCESS**.

This closes the repository-side test/CI subtask only. Criterion 30 remains **OPEN** until the actual owner-device application database is restored to a fresh destination, integrity and foreign-key checks pass, durable application domains are read back, and a post-restore write is verified on the restored copy. The source database must remain untouched.

No criterion tick is awarded by this CI result. Stage 1 remains **300/400 = 75% provisional** with criteria **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39** open.


## Gate 10 batch 3 — criterion 30 restore-helper regression refinement — 2026-11-14

The full shared-application-database restore test now invokes `restore_consistent_sqlite_backup()` directly rather than manually copying the snapshot. It verifies integrity and foreign-key checks, reopens every durable application store, checks representative application records, and proves a post-restore write on the restored copy.

Two additional tests cover directory-flush failure after publication and a competing process creating the destination immediately before atomic publication. The intended guarantees are tested: durability uncertainty is surfaced without pretending publication was rolled back, and a destination created by another process is never overwritten.

Exact-HEAD CI is pending. Criterion 30 remains OPEN pending the actual owner-device restore report; no acceptance ticks are awarded by these repository tests alone.


## Criterion 30 — Gate 10 batch 3 evidence boundary — 2026-11-14

The shared-application-database restore regression now invokes `restore_consistent_sqlite_backup()` directly, validates SQLite integrity and foreign-key consistency, reopens durable application stores, checks representative records across registry, entitlement, alert-zone, coverage/gap, OHLCV and outbox/replay domains, and verifies a post-restore write on the restored copy. Directory-flush failure after publication and a competing destination race are also covered.

Exact-HEAD CI on `ba01807b043de1f446b0630002ff607ac48a069a` passed Automated Tests #43571145976, CodeQL #43571145954 and Full Git History Secret Audit #43571145944. This is repository-side evidence only. Criterion 30 remains OPEN until the actual owner-device application database is restored to a fresh destination and a secret-free report verifies all available durable domains and a post-restore write. Do not overwrite or delete the source DB; do not assume the repository's default DB path is the live Android path.


## Documentation HEAD CI completion — 2026-11-14

The documentation commit `cf7044922df3cac0d2e9a52679509ea0aa957a81` has now passed all exact-HEAD workflows: Automated Tests #43571570406, CodeQL #43571570477, and Full Git History Secret Audit #43571570418 — all **SUCCESS**. This validates the documentation revision and does not change the acceptance state of any criterion. Stage 1 remains **300/400 = 75% provisional**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain OPEN pending external evidence.


## Gate 10 batch 4 — exact-HEAD CI and database-path audit — 2026-11-14

**Audited branch HEAD:** `38309c377dc8ff9f800461a7890965ac7c46b958` (`phase-2/market-data-foundation`; `main` untouched).

All three workflows for this exact HEAD are now complete:
- Automated Tests [#43571964355](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43571964355) — **SUCCESS**.
- CodeQL [#43571964368](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43571964368) — **SUCCESS**.
- Full Git History Secret Audit [#43571964397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43571964397) — **SUCCESS**.

The repository audit confirmed that the backend's shared SQLite path is configured by `INSTRUMENT_REGISTRY_DB_PATH`, defaulting to `./data/instrument_registry.sqlite3`. `create_app()` passes that same configured path to the instrument registry, price-alert store, entitlement store, OHLCV store, coverage tracker, and provider-definition synchronizer. This is the backend process's configured path, not proof of the resolved path of a running Android service.

The installable APK workflow generates a temporary Capacitor wrapper and packages the frontend. The repository has no checked-in Android host project that bundles or supervises the Python backend/Redis. Therefore, the APK installation does not by itself establish that this backend database exists on the phone. Criterion 30 still requires identifying the actual running backend process and its effective working directory/environment before any owner-device restore drill.

### Repository regression added in this batch

- `backend/tests/test_api.py`: verifies the five durable adapters exposed by `create_app()` share the exact configured SQLite path and that the database file is initialized.
- `backend/tests/test_config_security.py`: verifies `INSTRUMENT_REGISTRY_DB_PATH` is read from the backend environment.

These tests make the repository's path contract explicit. They do not prove a live Android database location and award no Stage 1 ticks by themselves.

### Acceptance and safety disposition

- Criterion 30: **OPEN** — target-device/live-backend restore report not yet available.
- Criterion 31: **OPEN / BLOCKED** — Termux Google Play repository signing-key mismatch and no verified off-host target/key-custody path.
- Termux: keep the existing working repository configuration; no package command, repository switch, key import, signature bypass, crypto downgrade, or app migration is authorized or required.
- Stage 1: **300/400 ticks = 75% provisional**; 30/40 criteria provisionally accepted; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 2–6: **NOT SCORED**. Overall project: historical owner-confirmed **20.90%** only; no newly approved weighted calculation.

No external acceptance gate is closed by this repository work or green CI alone.


## Gate 10 batch 5 — exact-HEAD CI and restore failure-path hardening (2026-11-14)

- Starting HEAD: `cabf637bf2e48cb54983a98bd854416975272df5`.
- Automated Tests & Build: [#43572423301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43572423301) — **SUCCESS**.
- CodeQL: [#43572423236](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43572423236) — **SUCCESS**.
- Full Git History Secret Audit: [#43572423268](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43572423268) — **SUCCESS**.
- All three workflows completed against the same exact HEAD. Automated Tests completed frontend tests/build and secret scans, backend pytest, dependency audit, synthetic SQLite benchmark, backend container build, Redis/persistent-volume smoke test, and image vulnerability scanning.
- Added regression coverage for a corrupt/non-SQLite restore source. The restore must raise a database error, publish no destination, and clean its temporary file.
- This is repository-side failure-path coverage only. Criterion 30 still requires the actual owner-device application database path and a consolidated restore report. Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open; no external criterion or progress tick is awarded by this batch.
- Stage 1 remains 30/40 provisional (300/400 ticks, 75%) and not production-accepted.

## Gate 10 batch 6 — exact-HEAD CI reconciliation and documentation link repair (2026-11-14)

**Exact source/test HEAD:** `8a159274eaa35339b8f68a1948f0bab002bc998c` on `phase-2/market-data-foundation`.

All three workflows completed successfully against this exact commit:
- Automated Tests [#43582913692](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43582913692) — **SUCCESS**.
- CodeQL [#43582913713](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43582913713) — **SUCCESS**.
- Full Git History Secret Audit [#43582913733](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43582913733) — **SUCCESS**.

Automated Tests passed frontend tests/build and secret scanning, Android host preflight, backend tests (including corrupt SQLite restore rejection), synthetic outbox benchmark, dependency audits, backend container build, Redis/persistent-volume smoke test, backend image scan and vulnerability-report export. No workflow failure was reported.

Documentation repair: corrected the malformed CodeQL run URL in this batch's earlier Gate 10 references. This is a documentation integrity correction, not a change to application behavior.

Acceptance accounting is unchanged:
- Stage 1: **30/40 provisional criteria = 300/400 ticks = 75% provisional**.
- External criteria still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 are not closed by CI alone. Criterion 30 still needs an owner-device restore report; criterion 31 remains blocked by the unverified Termux-compatible encrypted off-host/key-custody path.
- Stages 2–6 remain **NOT SCORED** and officially unopened.
- Overall project remains the historical **20.90%** checkpoint; no new weighted score is approved.

Termux disposition: no action required in this batch. Keep the known-good Google Play repository and signature verification unchanged. No device command, repository switch, key import, or crypto downgrade is authorized or needed.


### Criterion 30 — owner-device drill tooling (2026-11-14)

A reusable report-producing procedure is implemented in backend/app/sqlite_restore_drill.py. It snapshots the actual source database through SQLite Online Backup, restores to a fresh path through restore_consistent_sqlite_backup, checks required shared-application tables, integrity and foreign keys, compares per-table counts, reopens registry/entitlement/alert/coverage/OHLCV adapters, validates outbox event identity uniqueness, and tests a write/read/cleanup operation on the restored copy only. Automated tests use a synthetic application database and are repository evidence only. Criterion 30 remains OPEN until the tool is executed against the actual owner-controlled Android backend database and a redacted report is reviewed.


### Criterion 30 — report integrity and latest repository evidence (2026-11-14)

The owner-device drill report now includes a generated drill ID and SHA-256 over canonical redacted JSON, plus passed/failed check metadata. Automated tests validate the report hash, domain counts, source immutability, and no-overwrite behavior. Exact HEAD 86cc42f passed all three CI workflows; the complete backend suite reported 819 passing tests. This does not close criterion 30: the actual owner-controlled Android database, live process path, and device restore report are still outstanding.
 
## Gate 10 batch 7 — secret-audit false-positive remediation and exact-HEAD CI (2026-11-14)

- Audited the full-history secret-scan failure rather than suppressing it blindly. The reported finding was the public commit SHA embedded in a historical project-status metadata line, classified by Gitleaks as `generic-api-key`; the report did not establish that a credential was present.
- Added a narrow line-and-file-scoped Gitleaks allowlist for that exact metadata line. Corrected a TOML quoting/newline issue after the first remediation attempt; the failing workflow log identified the configuration parse error, and the corrected configuration was re-run.
- Exact HEAD: `462bca4342d6cb585b6b389ae5996020c4c47dd3`.
- Automated Tests #1149: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614075.
- CodeQL #507: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614165.
- Full Git History Secret Audit #88: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614104.
- The automated workflow completed frontend tests/build and source/bundle secret checks, read-only Android preflight tests, backend pytest, synthetic SQLite outbox benchmark, dependency audits, backend container build, Redis/persistent-volume smoke test, and container vulnerability scanning/report export.
- No external criterion is closed by these repository checks. Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open pending their exact host/device/provider evidence. No Stage 1 tick is awarded by this batch.
- Stage 1 remains **30/40 provisional = 300/400 ticks = 75% provisional**. Stage 2–6 remain **NOT SCORED**. Overall 20.90% remains a historical checkpoint only.
- No Termux package, repository, keyring, crypto dependency, runtime, production secret, paid service, or APK release was changed.


## Gate 10 — consolidated evidence packet contract (2026-11-14)

This section makes the remaining external gates executable as evidence requests. It does not mark any gate complete and awards no ticks by itself. Every packet must be redacted, tied to a date and exact software/configuration revision, and reviewed against the pass conditions below.

| Criterion | Minimum evidence packet | Pass condition | Immediate fail/defer condition |
|---:|---|---|---|
| 8 | Host/service secret-injection method; redacted service configuration; frontend bundle scan; repository-history scan; log/build-output scan | Secret values are injected only at runtime, never shipped to clients or emitted in logs/build artifacts/history | Any secret in a client artifact/log/history, or no verified host-side injection mechanism |
| 20 | No-billing Firebase project settings; redacted sign-in results; valid, expired, revoked, wrong-project token cases; entitlement-denial case; browser and Android reconnect results | All identity and authorization cases behave as designed without enabling paid billing | Billing state is unclear, a negative case is accepted, or any paid plan is required |
| 25 | Redis version/config fingerprint; certificate-validation result; ACL identity/permission test; private-bind check; persistence/restart/failure test | TLS verification and least-privilege ACLs succeed; Redis is not publicly exposed; persisted state survives the defined restart drill | Plaintext transport, disabled certificate validation, broad ACL, public bind, or lost required state |
| 30 | Actual backend process identity; effective working directory and DB-path source; redacted restore-drill JSON; source-before/after hash; fresh restore integrity and application readback | Correct live DB is positively identified; source remains unchanged; fresh restore passes integrity, FK, domain readback, and post-restore write/read/cleanup | DB path is guessed, source changes, output overwrites an existing file, or any verification fails |
| 31 | Encrypted artifact hash/format; separate key-custody location description (never the key); retention/access policy; successful restore result from encrypted artifact | Authenticated decryption and database restore succeed using a separately controlled recovery key, with no incremental cost | Key is stored beside the artifact, key is lost/unrecoverable, destination is not independently controlled, or paid storage is needed |
| 34 | Volume/mount identity; ownership and mode; write/read marker; restart result; disk-pressure/recovery result | Correct persistent volume remains mounted with restrictive permissions and data survives the required restart/recovery cases | Data resides only in ephemeral container storage, permissions are broad, or restart loses required data |
| 35 | Backend startup/health output; HTTPS certificate-chain result; failure-injection result; redacted runtime-secret source | Health check succeeds over verified HTTPS; startup fails closed when required config is absent; secrets remain backend-only | HTTP-only production exposure, invalid TLS, secrets in frontend, or paid public exposure required |
| 36 | Reverse-proxy config (redacted); WSS handshake; Firebase-authenticated subscription; unauthorized/expired-token rejection; web and Android client results | Both supported clients establish verified WSS and only authorized subscriptions succeed | Insecure transport outside local development, token in URL/logs, auth bypass, or only mocked client evidence |
| 38 | Self-hosted metrics/log config; retention limits; access-control test; disk/resource budget; sample redacted incident trace | Operational data is locally collected, bounded, access-controlled, and sustainable on existing hardware | Unbounded logs, exposed sensitive data, resource exhaustion, or paid observability dependency |
| 39 | Local alert route test; failure-to-alert and alert-delivery timestamps; incident owner/escalation/recovery runbook; recovery exercise | A no-cost alert is actually received and the documented recovery drill succeeds | Alert route is merely configured but untested, depends on paid delivery, or has no accountable recovery procedure |

### Gate evidence review rules

1. Keep raw secrets, Firebase tokens, Redis credentials, encryption passphrases, private keys, personal account data, and absolute private-storage paths out of chat, commits, screenshots, and reports.
2. A report must identify the tested environment and revision without disclosing secret values. Screenshots alone are insufficient where a machine-readable redacted result is available.
3. CI evidence may support a gate but cannot replace device/host/provider evidence explicitly required above.
4. A failed or unavailable check leaves the criterion OPEN; it does not earn partial ticks. Fix a safe repository-side defect before asking for any owner-device action.
5. No criterion may be closed by an assumed free tier, trial, local mock, synthetic fixture, or unverified network path.


## Gate 10 technical audit — source and CI reconciliation (2026-11-14)

Audited the active branch source and the successful CI run for exact HEAD `37641c43b8ca6c10f5284d4680a654796f0a5380`.

- **Criterion 8:** backend settings redact credential-bearing fields; frontend bundle scanning and full reachable Git-history scanning are in CI. This still does not prove owner-host secret injection or inspect a live host's logs/process environment. External host evidence remains required.
- **Criterion 20:** Firebase frontend observer/sign-in lifecycle and backend Admin token verification are present. Backend verification uses revocation checking and validates issuer, audience, subject and auth time; tests exercise mocked SDK boundaries. Actual project billing state, real sign-in, revocation/expiry, entitlement denial and supported-client integration remain external.
- **Criterion 25:** production config rejects non-TLS Redis and missing ACL credentials; the Redis client explicitly requires CA-chain and hostname validation. A regression test checks these client options. CI's Redis integration is not a substitute for the owner's actual private TLS Redis endpoint, ACL, persistence and restart/failure drill.
- **Criterion 30:** the restore-drill implementation checks required application tables, integrity, foreign keys, schema, row content hashes, domain readback, post-restore write/read and cleanup while preserving the source. CI tests exercise a synthetic fixture only. The actual Android application DB path and owner-device drill remain outstanding.
- **Criterion 31:** versioned AES-256-GCM backup encryption, PBKDF2-HMAC-SHA256 derivation, atomic publication and tamper/wrong-key rejection tests are present. Separate owner-controlled key custody, independent no-cost destination, retention/access controls and recovery drill are not proven by repository code.
- **Criterion 34:** CI's container smoke test passed volume ownership, non-root runtime, SQLite integrity and container restart persistence. This is meaningful container evidence, but does not establish a persistent mount on the owner's intended long-lived host/device or disk-pressure recovery there.
- **Criterion 35:** `/health` and a container healthcheck are present and the container smoke test passed. HTTPS termination, certificate lifecycle and real host startup/failure behavior remain external.
- **Criterion 36:** authenticated Firebase WebSocket handshake, entitlement checks and periodic revalidation are implemented in source. No reverse-proxy deployment or actual browser/Android WSS end-to-end evidence was found in this audit.
- **Criteria 38–39:** no deployed self-hosted monitoring/alert infrastructure or actual alert-delivery/recovery exercise was found. Application status payloads and unit tests are not operational monitoring or alert proof.

### CI evidence for audited code HEAD

- Automated Tests #43596463914: **SUCCESS**, including frontend tests/build, secret scans, Android preflight test, backend tests, dependency audit, synthetic SQLite outbox benchmark, Docker image build, persistent-volume/restart/Redis-guard smoke test, and HIGH/CRITICAL Trivy gate.
- CodeQL #43596463973: **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit #43596463929: **SUCCESS**.

These CI results apply to code HEAD `37641c43b8ca6c10f5284d4680a654796f0a5380`; documentation changes after this audit will have their own CI runs. None of these results independently closes external criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 or 39. Stage 1 scoring therefore remains 30/40 criteria = 300/400 ticks = 75% provisional.


### Audit correction — criterion 39 scope (2026-11-14)

A deeper source review of `backend/app/alerts.py`, `backend/app/alert_store.py`, and the FastAPI route registration found that the current implementation provides alert-zone validation and durable SQLite storage only. It does **not** provide an active price-crossing evaluator, a local delivery adapter, a delivery worker/scheduler, or evidence of a delivered alert. Therefore do not describe alert storage as an implemented alert-delivery path. Criterion 39 remains externally open and also has an implementation gap to scope safely before claiming an end-to-end local alert path. No paid notification channel may be introduced.
