# DEZZTA CHART — Project Progress Indicator (Current Snapshot)

**Audit timestamp:** 18 November 2026, 18:58 WIB  
**Active branch:** `phase-2/market-data-foundation`  
**Verification target:** `9873a5fd1c52a0cbab94683c0c309732407212e8`  
**Main:** untouched • **Cost:** ZERO COST  
**Indicator:** project documentation/dashboard only; NOT inside APK.

![Six-stage colored project dashboard](assets/project-progress-dashboard-batch19.svg)

## Latest verified update — Batch 23

- Audited application-code parent: `60d2c182bf8b4600f138b020eef39c321ffb83e3`; latest branch documentation commit: `9873a5fd1c52a0cbab94683c0c309732407212e8`.
- Batch 22 WebSocket binary-frame regression: **PASS** in backend pytest job from CI run [44295544184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544184). Binary input receives the invalid-message response and close code `1003`.
- Automated Tests run [44295544184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544184): **FAILURE only at final frontend dependency-audit enforcement**. Frontend tests/build, credential scans, Android tests, backend pytest, backend audit, container build, Redis/persistent-volume smoke test, and Trivy scan/report passed.
- CodeQL run [44295544205](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544205): JavaScript/TypeScript and Python analyses **PASS**. Full Git History Secret Audit run [44295544181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544181): **PASS**.
- Exact WSS preview deployment [`dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg`](https://vercel.com/deszztagd377-pixel/dezzta-chart-ws-poc/4mPXXnj2XLLoNZYe5JkdQ1M7r5tg): **READY** on commit `9873a5f` (preview only, `target=null`). Protected `/health` returned HTTP 200 with `synthetic-only` and `production_data_connected=false`; root page returned HTTP 200 with Connect, Disconnect, synthetic ping and bounded 330-second probe controls.
- Frontend deployment for the same commit was **CANCELED by the Ignored Build Step** after it returned exit code 0. Its previous READY deployment remains on `bd6356d`; compare evidence confirms the intervening changes touched only WebSocket POC, backend test and documentation paths, not frontend application files.
- Deployment filtering is now evidenced in Vercel build logs. The WSS build ran because the previous successful WSS deployment was still `bd6356d`, and the commit range contained pending changes under `poc/vercel_ws/`; the build brought those WebSocket changes into a READY preview. The frontend build was correctly skipped. Both Vercel status contexts on `9873a5f` are **SUCCESS** (frontend skip counts as success; WSS deployment is READY).
- Upstream advisory review refreshed on 18 Nov 2026: GitHub advisory GHSA-fc5q-39xc-vjpf remains published; relevant upstream PRs including #237, #238, #257, #262, #264, #267 and #268 remain open/unmerged. PR #260 also has unresolved performance/compatibility review findings. No official patched npm release is verified; keep dependency-audit enforcement fail-closed.
- No actual public WebSocket Upgrade/ping-pong, Android WebView test, foreground 330-second observation, effective Fluid Compute read-back, or cross-instance fan-out is claimed. Gate 36 remains OPEN.

## Six-stage progress

| Stage | Scope | Status | Progress |
|---:|---|---|---:|
| 1 | Foundation, Security & Data Integrity | Active; provisional | **75% — 300/400 ticks; 30/40 criteria** |
| 2 | Market Data Infrastructure | Not opened; not scored | — |
| 3 | Core Chart Engine | Not opened; not scored | — |
| 4 | Indicators & Analytics | Not opened; not scored | — |
| 5 | Advanced Tools | Not opened; not scored | — |
| 6 | Release & Operations | Not opened; not scored | — |

**Gate 10: 0/10 formally closed.** Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No overall-project percentage is asserted.

## Gate 10 — evidence and remaining blockers

| Gate | Current repository evidence | Remaining external acceptance |
|---:|---|---|
| 8 | Frontend source/bundle credential scans and full Git history secret audit pass | Owner-controlled zero-billing runtime secret injection; prove absence from logs, build outputs and runtime artifacts |
| 20 | Firebase token/revocation/entitlement and WebSocket authorization code/tests | Verified no-billing Firebase setup; real sign-in, expiry/revocation, entitlement denial, browser + Android reconnect; otherwise production identity stays disabled |
| 25 | CI Redis ACL/TLS + persistent-volume smoke test passes in test environment | Existing owner-controlled Redis host, validated TLS, least-privilege ACL, private bind, persistence/restart/failure proof |
| 30 | CI encrypted snapshot/decrypt/full-restore integration test | Owner-target restore to fresh DB; unchanged source; integrity, FK, domain records and post-restore write/read/cleanup |
| 31 | Encrypted snapshot/recovery code and tests | Off-host artifact, separately controlled recovery key, retention/access policy and successful restore; zero-cost only |
| 34 | CI persistent-volume smoke test passes | Existing-host mount identity, restrictive permissions, disk-pressure and restart durability/recovery evidence |
| 35 | Backend container build and health-related tests pass | Existing-host HTTPS/certificate chain, fail-closed startup and redacted runtime-secret source evidence |
| 36 | Synthetic WSS POC and ASGI lifecycle/protocol tests; binary-frame rejection regression PASS in CI run `44295544184`; earlier READY previews are on `bd6356d`, not current code HEAD | Public WSS upgrade, foreground 330s observation, platform close attribution, effective Fluid setting read-back, native Android WebView WSS, cross-instance fan-out and owner cost acceptance |
| 38 | Concurrent metrics regression and input-hardening tests | Durable aggregation, bounded retention, host access controls, self-hosted dashboard and owner acceptance |
| 39 | Sanitized local alert/recovery tests and zero-cost runbook | Persistent alert evidence, named escalation owner and completed recovery drill |

## Historical CI checkpoint (prior commit) — run 44278716234

<badge color="danger">Overall workflow: FAILURE</badge> The single failing step is the final **Enforce frontend dependency audit result**. This is an intentional security gate, not a test/build crash.

- Backend pytest: **1,014 passed in 30.07s**.
- Frontend unit tests and production build: PASS.
- Frontend source and built-bundle credential scans: PASS.
- Android host preflight and immutable preview publisher tests: PASS.
- Synthetic SQLite outbox benchmark and artifact upload: PASS.
- Backend dependency audit: PASS.
- Backend container build: PASS.
- Redis/persistent-volume smoke test: PASS.
- Trivy image scan/report steps: PASS.
- CodeQL [44278716261](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716261): PASS.
- Full Git History Secret Audit [44278716240](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716240): PASS.

### Active npm audit blocker

Job log confirms **five High findings** through development-only `picomatch@4.0.7`, advisory **GHSA-fc5q-39xc-vjpf**. The new dependency-exposure regression passes, proving affected glob tooling remains dev-only and absent from direct runtime dependencies. This is exposure reduction, **not remediation**. Keep final enforcement active. Do not force upgrades/downgrades, suppress, waive, or mislabel the finding as fixed.

## Historical Vercel read-back (older commit)

Both protected previews are **READY** for source `4256c5e3ccab82255d115beaf961afd4794a3a42`:
- WSS POC [preview](https://dezzta-chart-ws-4eo7d8j18-deszztagd377-pixel.vercel.app) — `dpl_AtEV8yH6S5MwGApGaHQ8HagJTJsK`.
- Frontend [preview](https://dezzta-chart-bevptgcvw-deszztagd377-pixel.vercel.app) — `dpl_2Jc2So3HmvEQ6yeESjrXbMLorivz`.

Preview READY is not production acceptance. No production promotion.

## WebSocket status — strict interpretation

Implemented and CI-tested: correct CONNECTING/OPEN/close lifecycle, actual close event as the disconnected authority, opt-in synthetic heartbeat every 10 seconds, 25-second idle timeout, bounded 330-second browser probe, monotonic elapsed measurement, close details, and hidden-page invalidation.

Not yet evidenced: owner-observed foreground 330-second run, Vercel-originated maximum-duration close, effective Fluid Compute runtime read-back, native Android WebView WSS, cross-instance production fan-out, zero-cost operational acceptance. A client-side close at 330 seconds is not proof of platform termination. POC is synthetic-only; no production market data, credentials, identity, Redis or production worker.

## Roadmap beyond Stage 1

- Stage 2: market-data infrastructure, provider adapters, entitlement-aware ingestion, replay and durable sequencing.
- Stage 3: chart engine, timeframes, history, viewport, pan/zoom and rendering correctness.
- Stage 4: indicators and analytics; Footprint/Heatmap visuals must wait for the owner's reference images.
- Stage 5: advanced chart tools, alerts, layouts and drawing workflows.
- Stage 6: release hardening, Android packaging, performance, reliability, security and operations.

Stages 2–6 remain NOT SCORED.

## Zero-cost and owner-device controls

No paid hosting, managed Redis, market-data subscription, monitoring, storage, billing activation, paid plan upgrade, production promotion or SSO weakening. No Google Play publication unless explicitly approved. **No Termux required** for this CI/documentation cycle. If a gate requires paid infrastructure, it stays constrained/deferred. No code/document repair is delegated to the owner.

## Next engineering order

1. Keep npm audit enforcement active; accept only a reviewed, reproducible remediation.
2. Perform the owner-controlled foreground WSS observation against the exact READY protected preview; record the actual event evidence before closing any sub-check.
3. Continue existing-host Redis, restore, secrets, volume, metrics and alert acceptance only where already available at zero incremental cost.
4. Award no Stage 1 ticks until each external criterion has its required evidence and acceptance.

**Current accounting:** Stage 1 **75% provisional**; Gate 10 **0/10 closed**; Stages 2–6 **not scored**.


## Batch 15 — upstream dependency remediation review — 18 Nov 2026

The five High npm audit findings are still enforced. A fresh upstream review was performed before considering any patch:

- GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) remains published and identifies CVE-2026-112366. Its current page marks the record **Unreviewed** and does not list a patched version. OSV still carries the advisory record.
- Upstream issue [#247](https://github.com/micromatch/picomatch/issues/247) remains OPEN. Discussion indicates the Snyk-specific advisory was revoked, but that does not remove the GitHub advisory or the current npm audit finding.
- Upstream PR [#238](https://github.com/micromatch/picomatch/pull/238) remains OPEN. Review measurements reproduce exponential behavior for `+(*)`, `*(*)`, and `+(a*)`; a separate review also reports `+(*)` still timing out. It does not fully resolve the published advisory.
- Upstream PR [#237](https://github.com/micromatch/picomatch/pull/237) remains OPEN. Review discussion identifies uncovered multi-branch patterns (including `+(*a|*b)`) and semantic edge cases involving quoted stars and bracket classes. A single approval is not a maintainer release or comprehensive security validation.
- Upstream PR [#246](https://github.com/micromatch/picomatch/pull/246) targets the v2 branch and is not a release for this project's picomatch 4.x dependency path. Its own description scopes the fix and validation to selected patterns, not all ReDoS cases.
- Upstream PR [#235](https://github.com/micromatch/picomatch/pull/235) is CLOSED; maintainer comments dispute the vulnerability's practical exposure and recommend not allowing untrusted users to define glob/regex patterns. That disagreement does not change the active GitHub advisory or justify silently waiving npm audit.

**Decision:** do not vendor or override any of these unmerged patches. Do not claim the advisory is revoked globally. Keep the exact npm audit enforcement active and keep the vulnerable packages development-only. Reassess after a maintainer-reviewed release and independent regression validation against all relevant cases.

This upstream research does not alter Stage 1 scoring or Gate 10 closure.


## Batch 16 — exact-head CI + protected WSS HTTP read-back — 18 Nov 2026

**Branch head audited:** `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.

### Exact-head automated evidence

- Automated Tests [44280286764](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286764): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed in 31.94s**. Alert recovery, concurrent observability metrics, dependency-exposure, WebSocket protocol, bounded-probe contract and all other backend tests passed.
- Frontend unit tests/build, source and built-bundle credential scans, Android preflight/publisher tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke test, and Trivy scan/report steps passed.
- CodeQL [44280286768](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286768): **SUCCESS**.
- Full Git History Secret Audit [44280286699](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286699): **SUCCESS**.
- The only failing enforcement is still five High npm audit findings through dev-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. Do not suppress, waive, force-downgrade or call this fixed.

### WebSocket POC — protected preview read-back

- Last READY WSS preview: `dpl_C9bGENGcUpmgTFaxyyPNjg1Ehapv`, source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`.
- Protected `/health` request returned **HTTP 200** with `status=ok`, `service=dezzta-ws-poc`, `mode=synthetic-only`, `production_data_connected=false`.
- Protected root page returned **HTTP 200** and contains the 330-second probe control and 10-second heartbeat configuration.
- This proves HTTP health and page delivery only. No actual WebSocket upgrade/round-trip, owner-visible foreground 330-second observation, platform-originated 300-second close, effective Fluid Compute read-back, native Android WebView WSS or cross-instance fan-out is claimed. Gate 36 remains OPEN.

### Vercel build-rate restriction

- Exact-head Vercel commit status for `a5e90f75329c937a4ef11d560bab3b434e7f24e8`: both WSS and frontend contexts **FAILURE** with the platform `build-rate-limit` link.
- Filtered deployment lookup for exact SHA returned **zero deployment records** for both projects. Do not label this commit READY.
- Previous known READY previews remain on `72a959f375f7c1e999be25e73e5fd00fdc24abb0`. Existing READY previews were not changed; no redeploy retry loop, paid upgrade, billing activation or SSO weakening was performed.
- Team usage counters and exact reset time were not exposed by the available read-back; no quota remainder or reset estimate is invented.

### Stage 1 accounting — unchanged

- Stage 1: **300/400 ticks = 75% provisional; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- No score awarded for a passing test suite, documentation, or HTTP-only WSS checks without the external acceptance evidence.


## Batch 17 — branch-head and provider-blocker reconciliation — 18 Nov 2026

**Audited branch head:** `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a` (commit message: `docs: consolidate Batch 16 CI and WebSocket evidence`).
**Parent:** `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.
**Audit method:** GitHub branch ref, exact commit status/check-runs, workflow job logs, and Vercel deployment records filtered by exact SHA.
**Cost:** ZERO COST. No Termux, no paid plan, no billing change, no production promotion, no SSO weakening.

### Exact branch-head evidence

- GitHub Actions run [44281595750](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595750) — Test and Build: **FAILURE at final frontend dependency-audit enforcement**.
- The job reached and completed all earlier test/build/security/container steps. The final step reports `AUDIT_OUTCOME=failure` and exits 1 by design.
- CodeQL run [44281595873](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595873): both Python and JavaScript/TypeScript analysis jobs **SUCCESS**.
- Full reachable Git history scan run [44281595869](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595869): **SUCCESS**.
- The exact-head GitHub status has two Vercel contexts, both FAILURE with the provider message: **“Deployment rate limited — retry in 24 hours.”**
- Exact-SHA deployment queries returned **zero deployment records** for both WSS POC and frontend projects. Therefore `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a` is **not deployed**.

### Vercel blocker — isolated and contained

This is a provider-side deployment/build-rate restriction, not an application compile error. No retry loop was started. No paid upgrade, billing activation, or SSO bypass was attempted. The latest previously observed READY previews are tied to source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`, not the audited branch head. Those preview records do not certify the branch head.

No exact usage counter or reset timestamp was available. The provider status string says retry in 24 hours; no more precise remaining-time estimate is asserted.

### Dependency audit blocker — enforcement retained

The workflow's final enforcement is the sole Test and Build failure. The audit outcome is still failure for the five High findings through development-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. The development-only boundary regression is mitigation, not a fix. No unmerged patch, forced downgrade, override, suppression, waiver, or production-only audit substitution was applied.

### WebSocket acceptance — honest boundary

The latest previously recorded protected preview returned HTTP 200 for health and page delivery in synthetic-only mode. This is HTTP verification only. It is not a WebSocket upgrade, echo/round-trip, 330-second foreground observation, platform-originated duration close, Android WebView test, effective Fluid Compute read-back, or cross-instance fan-out proof. Gate 36 remains OPEN.

### Gate 10 action register

| Criterion | Immediate zero-cost work possible | Evidence still required |
|---:|---|---|
| 8 | Keep source/bundle/history scans and secret boundary tests enforced | Owner-controlled secret injection and runtime/log/artifact leakage proof |
| 20 | Preserve authorization/revocation regression tests | Real identity/revocation/entitlement acceptance on approved zero-cost setup |
| 25 | Keep Redis ACL/TLS and persistence CI tests | Owner-controlled existing Redis endpoint and real restart/failure proof |
| 30 | Keep encrypted snapshot/decrypt/restore integration tests | Restore drill against a fresh owner target and post-restore integrity/write checks |
| 31 | Keep encrypted backup/recovery controls | Off-host copy, separately controlled key, retention policy and restore drill |
| 34 | Keep persistent-volume smoke test | Existing-host mount, permissions, disk-pressure and restart durability proof |
| 35 | Keep container/health/fail-closed checks | Existing-host HTTPS/certificate and runtime secret-source evidence |
| 36 | Keep synthetic lifecycle/probe contract tests; no false duration claims | Foreground 330s run, platform close attribution, Fluid setting, Android WebView, fan-out |
| 38 | Keep concurrency/input-hardening tests | Durable aggregation, retention, host access controls and dashboard acceptance |
| 39 | Keep sanitized alert/recovery tests and runbook | Persistent alert, named escalation owner and completed recovery drill |

**Scoring unchanged:** Stage 1 **300/400 ticks = 75% provisional; 30/40 criteria**. Gate 10 **0/10 closed**. Open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 **NOT SCORED**. No progress credit for documentation-only work or provider-blocked deployments.


## Batch 18 — exact-head CI, WSS HTTP verification, and overall-progress accounting — 18 Nov 2026

**Audited source head:** `64f348cebccbfb3fad2b9efe5a066d28962970f6` (Batch 17 documentation reconciliation). **Branch:** `phase-2/market-data-foundation`. **Main:** untouched. **Cost:** zero. No Termux, no billing, no paid services, no production promotion.

### Exact-head CI outcome

- Automated Tests run [44287587066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587066): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed**. Frontend unit tests/build, source and built-bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke test and Trivy scan/report all **PASS**.
- The final enforcement step fails because npm audit outcome is failure: **five High findings through development-only `picomatch@4.0.7`**. The failure is intentional and no vulnerability was suppressed.
- CodeQL run [44287587070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587070): Python and JavaScript/TypeScript jobs **SUCCESS**.
- Full history scan run [44287587073](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587073) was requested in the prior read-back but its run ID was not valid; therefore this batch does **not** claim a new history-audit result. Earlier passing history scans remain historical evidence only.

### Vercel exact-head deployment

Both projects have READY deployments for this exact source SHA:
- WSS POC deployment `dpl_8iPQZm1Z2QJ4Dc8hjUPgSsPanPYb`, URL [protected preview](https://dezzta-chart-ws-arfnel7l9-deszztagd377-pixel.vercel.app).
- Frontend deployment `dpl_FqhfGebn7fU6f7udkPFmByyG1WTY`, URL [protected preview](https://dezzta-chart-ekpqshhr4-deszztagd377-pixel.vercel.app).

The previously observed build-rate-limit blocker is therefore no longer active for this commit. No paid upgrade, billing activation, SSO weakening, or production promotion occurred.

### WebSocket POC — verified scope

Protected WSS preview `/health` returned **HTTP 200** with `status=ok`, `service=dezzta-ws-poc`, `mode=synthetic-only`, and `production_data_connected=false`. The protected root page returned **HTTP 200** and serves the browser WebSocket client, including its explicit Connect, Disconnect, synthetic ping, and bounded 330-second probe controls.

This is HTTP health and page-delivery evidence only. The available HTTP fetch interface cannot perform or observe a real WebSocket protocol upgrade, so this batch does not claim a WSS handshake, ping/pong round-trip, foreground 330-second run, Vercel-originated duration close, Android WebView result, effective Fluid Compute read-back, or cross-instance fan-out. Gate 36 remains OPEN.

### Overall-project progress — corrected accounting

The approved progress specification explicitly says the M1–M8 weighted ledger is **not approved and not scored criterion-by-criterion**. Therefore a fresh overall-project percentage cannot be calculated without inventing weights or credit. The most recent owner-confirmed historical overall checkpoint is **20.9%**, and it must be labeled **HISTORICAL — NOT RECOMPUTED**. Do not present 20.9% as a current verified percentage.

The six official stages remain:
- Stage 1: **75% provisional** (300/400 ticks; 30/40 criteria); Gate 10 **0/10 formally closed**.
- Stages 2–6: **NOT SCORED**. Preparatory code does not count as officially opened stage progress.
- Overall project: **CURRENT % NOT ESTABLISHED**; historical reference **20.9%** only.

Formula remains pending owner-approved M1–M8 weights and criterion-to-deliverable mapping: `overall = Σ(weight × verified completion fraction)`. Duplicate credit is prohibited.

### Gate 10 status

Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No new external acceptance evidence in this cycle closes any of these criteria. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed.


## Batch 18.1 — deployment status labeling correction — 18 Nov 2026

The Batch 18 READY deployment records are for audited source `64f348cebccbfb3fad2b9efe5a066d28962970f6`, not the later documentation-only branch head. After Batch 18 documentation commit `ef453a1af9310d2c19fad8ae7afc1262530216cc`, GitHub reports WSS deployment **PENDING** and frontend deployment **FAILURE: Deployment rate limited — retry in 24 hours**. The dashboard now labels these separately to avoid presenting prior READY previews as current-head deployments. The Batch 18 technical CI/HTTP results remain scoped to source `64f348c`. No retry loop, paid upgrade, billing, SSO change or production promotion.

Overall project remains **CURRENT % NOT ESTABLISHED**; **20.9% HISTORICAL ONLY**. Stage 1 remains 75% provisional; Gate 10 0/10 closed.


## Batch 19 — executable WebSocket protocol contract and corrected progress accounting — 18 Nov 2026

### WebSocket protocol regression coverage added

Added `backend/tests/test_vercel_ws_protocol.py`. It imports the isolated synthetic POC application by its repository path and uses FastAPI/Starlette TestClient to exercise the ASGI WebSocket protocol, not just source-text patterns. Coverage includes:

1. WebSocket handshake, ready message and ping/pong round-trip with matching session ID and sequence.
2. Invalid-message error followed by close code 1003.
3. Oversized-message error followed by close code 1009.
4. Twelve-message/ten-second rate boundary and rate-limited close code 1013 on the next message.
5. HTTP health response explicitly declaring `synthetic-only` and `production_data_connected=false`.

**Evidence boundary:** these are executable in-process ASGI protocol tests. They do not prove public Vercel WSS upgrade, browser behavior, 330-second platform lifetime, Android WebView, Fluid Compute effective settings, or multi-instance fan-out. Gate 36 remains OPEN until those external observations exist.

### CI checkpoint before Batch 19 commit

- Latest branch CI run [44288721128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721128) was still running at read-back; frontend tests/build, source and bundle credential scans, Android preflight/publisher tests, backend pytest (PASS), synthetic outbox benchmark, backend dependency audit had passed; backend image build was in progress. Do not claim this run complete.
- CodeQL run [44288721099](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721099): SUCCESS.
- Full Git History Secret Audit run [44288721127](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721127): SUCCESS.
- Vercel commit status for `362ff6e`: both WSS POC and frontend report **Deployment rate limited — retry in 24 hours**. No retry loops, plan upgrade, billing or SSO change.

### Dependency blocker — confirmed path and safe decision

The root lockfile contains `picomatch@4.0.7` as `dev: true`, with transitive parents `tinyglobby@0.2.17`, `vite@6.4.5`, and `vitest@4.1.12`, all also development-only. The GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) still reports High severity, affected through 4.0.7, and no patched version. Upstream issue [#247](https://github.com/micromatch/picomatch/issues/247) remains open in the latest read. No reviewed/released fix is available to justify a lockfile override. Do not downgrade to 4.0.4: that release addressed a different earlier advisory, not this later single-branch extglob finding. Keep npm audit enforcement fail-closed; dev-only status is exposure reduction, not remediation.

### Progress accounting

- Stage 1: **75% provisional**, 300/400 ticks, 30/40 provisional criteria.
- Gate 10: **0/10 formally closed**; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: **NOT SCORED**.
- Overall current project percentage: **NOT ESTABLISHED** because M1–M8 weights and criterion mapping are not approved/scored. Historical 20.9% is retained only as a historical checkpoint, not presented as current.

No Gate 10 closure or Stage 1 tick increase is awarded from adding tests alone. No Termux required. Zero-cost constraints maintained. `main` untouched.


## Batch 23 — WebSocket CI reconciliation, Vercel build filtering, and advisory re-audit — 18 Nov 2026

### WebSocket verification

The Batch 22 binary-frame regression is no longer pending. Backend pytest in run [44295544184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544184) passed. The regression verifies a binary frame is rejected through the protocol error response and close code 1003. This is synthetic ASGI protocol evidence only; Gate 36 remains open.

The same workflow completed with overall FAILURE because its final frontend dependency-audit enforcement step failed. Earlier test, build, credential-scan, backend, container, Redis/persistent-volume, and Trivy steps passed. Do not label the workflow green.

### Vercel deployment filtering

Both Git-linked Vercel projects were configured with project-level Ignored Build Step commands:

- Frontend `dezzta-chart`: skip only when all changed paths are confined to `poc/vercel_ws/`, `backend/`, `docs/`, and `.github/`.
- WebSocket POC `dezzta-chart-ws-poc`: skip unless a file under `poc/vercel_ws/` changed.

The commands use `VERCEL_GIT_PREVIOUS_SHA` and `VERCEL_GIT_COMMIT_SHA`. The `git diff --quiet` pathspec behavior was verified in an isolated temporary Git repository:
- docs-only change → frontend skip, WSS skip;
- frontend-only change → frontend build, WSS skip;
- WSS-only change → WSS build, frontend skip.

The commands use `|| exit 1`, so missing refs or a Git diff error do not silently skip a needed build; they fall through to a build. Project settings updates were accepted by Vercel. The available project read-back preserves existing domains, SSO protection and latest READY preview records, but does not return the ignored-build command field itself. The settings update itself did not trigger a deployment. The subsequent Git push produced a needed WSS catch-up deployment and skipped the frontend build; no preview was deleted or promoted.

This filtering is intended to reduce duplicate/irrelevant builds; it does not remove account-level build limits. First Git-triggered validation: frontend skip confirmed; WSS build ran only because WebSocket code changes had accumulated since the last successful WSS deployment. The WSS preview is now READY on the latest branch commit. The next documentation-only push should skip both projects, but that post-catch-up case has not yet been separately observed.

### Dependency advisory re-audit

GitHub issue [micromatch/picomatch#234](https://github.com/micromatch/picomatch/issues/234) remains open and was updated on 18 Nov 2026. Related upstream fix PRs [#237](https://github.com/micromatch/picomatch/pull/237), [#238](https://github.com/micromatch/picomatch/pull/238), [#257](https://github.com/micromatch/picomatch/pull/257), [#262](https://github.com/micromatch/picomatch/pull/262), [#264](https://github.com/micromatch/picomatch/pull/264), [#267](https://github.com/micromatch/picomatch/pull/267), and [#268](https://github.com/micromatch/picomatch/pull/268) were still open/unmerged at audit time. PR [#260](https://github.com/micromatch/picomatch/pull/260) contains further reported performance counterexamples and compatibility tradeoffs. These PRs are not official published releases. No unmerged patch or Git override is accepted as a production dependency remediation. Keep npm audit enforcement fail-closed until a maintainer-reviewed, published version and project-specific regression verification exist.

### Progress and cost accounting

- Stage 1: **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall current project percentage: **NOT ESTABLISHED**. Historical 20.9% remains historical only; M1–M8 weights and criterion mapping are not approved.
- Cost: **ZERO COST policy retained**. No billing changes, paid services, deployments, promotions, or SSO weakening.
- Termux: **not required**.
- `main`: untouched.

No Stage 1 ticks or Gate 10 closures are awarded for this configuration/documentation work.


## Batch 24 — branch-scoped Vercel preview containment and WebSocket evidence — 18 Nov 2026

### Deployment policy decision and implementation

- Team plan read-back: **Hobby**. Project Deployment Policy API rejected the attempted preview-only source allowlist with HTTP 403 `pro_plan_required`; no paid upgrade was attempted.
- The shared repository-root `vercel.json` applies to both Git-linked projects and contains `git.deploymentEnabled.main=true` plus `git.deploymentEnabled.phase-2/market-data-foundation=false`. This blocks automatic Git deployments from the active working branch while preserving the configured `main` production branch; it does not disable other deployment sources or globally disable Preview.
- Build logs show the WSS project's Vercel build entrypoint is `.` (repository root), while Python dependencies are discovered under `poc/vercel_ws/`. Therefore `poc/vercel_ws/vercel.json` is not the authoritative project-root config for this deployment. Batch 26 corrects this by putting `fluid: true` in the shared repository-root config. The frontend is a static Vite project with no serverless function in this deployment, so the Fluid setting has no active function workload there.
- A project-level `resourceConfig.fluid=true` update was also accepted by the Vercel API, but the available project read-back does not expose the effective field; no field-level confirmation is claimed.
- This commit is intentionally the single planned branch update for both projects. Vercel deployment creation must be checked against the exact resulting SHA. The config is documented by Vercel as suppressing Git deployments for matching branches before a deployment is created; Ignored Build Step remains only a secondary build filter.
- No Vercel API deployment policy was enabled (Hobby restriction); no project was paused, no preview was deleted, no SSO setting changed, and no production promotion occurred.

### WebSocket acceptance checkpoint

- WSS preview `dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg` remains READY on `9873a5f`; protected `/health` and root page both returned HTTP 200 on 18 Nov 2026. Health payload remains `synthetic-only`, `production_data_connected=false`.
- Backend ASGI tests cover handshake, synthetic ping/pong, invalid JSON/type, binary rejection (1003), oversized frame (1009), rate limit (1013), and idle timeout. These do not prove the deployed Vercel WebSocket Upgrade or browser-to-server round-trip.
- Still unverified: public WSS Upgrade/ping-pong, foreground 330-second run and close attribution, Android WebView, effective Fluid Compute read-back, and cross-instance fan-out. Gate 36 remains OPEN.

### CI/security and progress accounting

- Latest fully inspected CI run remains [44295544184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544184): frontend/backend tests and builds, secret scans, Android checks, backend audit, container/Redis/Trivy checks passed; final frontend dependency audit enforcement failed on five High findings through dev-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. Enforcement remains fail-closed.
- CodeQL [44295544205](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544205) and full Git history secret audit [44295544181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544181) passed.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 remain **NOT SCORED**. Overall current percentage remains **NOT ESTABLISHED**; 20.9% is historical only.
- Zero-cost maintained. No Termux, billing, paid services, production deployment, or `main` modification.


## Batch 25 — serialize WebSocket recovery after transport errors — 18 Nov 2026

### Root cause and correction

- The authenticated OHLCV client reports a transport/protocol error and then closes the underlying socket. The supervisor previously scheduled a reconnect immediately from `onError`, while also scheduling from the authoritative `onClose` event.
- The timer guard prevented duplicate timers, but a delayed browser close event could arrive after the reconnect delay and allow a replacement socket to open while the previous socket was still closing.
- Changed the supervisor so `onError` reports the error and sets the visible state to `reconnecting`, but does **not** start the retry timer. The authoritative `onClose` event now owns transport retry scheduling. Token-provider failures still use the existing catch/finally retry path.
- Added a deferred-close regression test: after an error, advancing timers by 1,000 ms must not create a second socket until the original close event is delivered; after close, the bounded 50 ms test delay creates exactly one replacement with a fresh token.

### Verification and boundaries

- Source-level replacement and test insertion were validated against the exact active-branch file contents before commit. Full TypeScript/Vitest execution is pending the branch CI run; no test pass is claimed until CI reports it.
- Existing cursor-resume, snapshot/replay, fresh-token, bounded-backoff, terminal authentication/entitlement close, and stop-cancellation tests are preserved.
- This is a client lifecycle reliability fix. It does not prove public Vercel WebSocket Upgrade, platform 300-second lifetime behavior, Android WebView, or cross-instance fan-out. Gate 36 remains OPEN.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No score increase is awarded for this code/test addition alone.
- Zero-cost maintained; no Termux, billing, paid service, deployment, or `main` change.


## Batch 26 — Vercel root configuration correction and Fluid Compute declaration — 18 Nov 2026

### Root-directory evidence and correction

- Read the WSS preview build events for `dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg`. Vercel reports build `entrypoint: "."`, clones the repository root, and resolves Python from `poc/vercel_ws/.python-version` and dependencies from `poc/vercel_ws/requirements.txt`. This confirms the WSS project's build root is the repository root; the nested `poc/vercel_ws/vercel.json` is not the authoritative project-root configuration for that deployment.
- Updated the shared root `vercel.json` to include `"fluid": true`, preserving the branch-scoped `git.deploymentEnabled` rules. This makes Fluid Compute explicit for the WSS Python function while keeping the active working branch's Git preview deployment disabled and `main` enabled.
- The frontend project uses Vite and serves static output; no frontend serverless function is present in this deployment. The shared Fluid flag therefore has no active frontend function workload.
- Vercel documents Fluid Compute as enabled by default for projects created after 23 April 2025, and the WSS project was created on 17 November 2026. The explicit root setting removes reliance on that default. Hobby's documented maximum function duration remains 300 seconds; Fluid Compute does not make a 330-second invocation permissible on Hobby.
- The Vercel API accepted a WSS project-level `resourceConfig.fluid=true` update, but read-back does not expose the effective field. The root `vercel.json` is the authoritative, version-controlled configuration; effective deployment behavior still requires a future permitted deployment and runtime verification.

### Validation and progress

- Root JSON parsed successfully before commit. Branch guard values remain `main=true` and `phase-2/market-data-foundation=false`.
- No Vercel deployment was created by the settings update. The branch remains protected from Git-triggered preview creation by the root config; exact-SHA deployment records and status contexts must still be checked after the commit.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 remain **NOT SCORED**. Overall current percentage remains **NOT ESTABLISHED**; 20.9% remains historical only.
- Zero-cost maintained. No Termux, billing changes, paid service, production promotion, or `main` modification.


## Batch 27 — make Gate 30 post-restore write verification durable — 18 Nov 2026

### Defect found

- The existing restore drill's post-restore probe created a table, inserted a row, read it back, dropped the table, and committed all within one SQLite connection/transaction.
- That proved transaction-local read-your-writes, but did **not** prove the inserted probe survived a commit and a fresh connection. The report label `post_restore_write_read_cleanup=passed` therefore overstated the durability property being exercised.

### Correction

- The probe now creates and inserts its unique drill-owned record, commits it, closes the writer, and reads the exact record through a separate read-only connection.
- Only after successful committed readback does it drop the probe table in a new write transaction, commit cleanup, and verify absence through another read-only connection.
- If committed readback fails, a best-effort cleanup removes only the drill-owned probe table while preserving the original failure. A pre-existing table with the same name is still rejected and is never removed.
- Added two regression tests: (1) proves the probe row exists through the fresh read-only connection and is absent after cleanup; (2) injects a readback failure and proves the committed probe table is cleaned up.

### Scope and evidence boundary

- This strengthens repository-level restore verification. It does not prove the owner's actual Android database path, target-device execution, recovery time on the owner's device, or off-host disaster recovery.
- Gate 30 remains **OPEN** until a timestamped drill runs against the actual application database on the owner-controlled target. Gate 31 remains **OPEN** for off-host destination, separate key custody, retention, and recovery.
- Exact-head CI has not yet executed for this commit; the new tests are implemented, not yet claimed PASS.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No ticks are awarded for this source-level correction.
- ZERO COST maintained. No Vercel deployment, paid service, billing change, production data access, or `main` modification. The actual phone-only execution may require Termux/Python; no Termux installation or command has been requested or performed in this batch.
