# DEZZTA CHART — Project Progress Indicator (Current Snapshot)
 
**Audit date:** 18 November 2026  
**Repository:** https://github.com/deszztagd377-pixel/dezzta-chart  
**Working branch:** `phase-2/market-data-foundation`  
**Main branch:** untouched  
**Cost policy:** ZERO COST  
**Indicator type:** project-process dashboard; not an in-app chart indicator or APK feature.

![Six-stage DEZZTA CHART progress dashboard](assets/project-progress-dashboard-batch10.svg)

## Authoritative progress

| Stage | Scope | Status | Progress |
|---:|---|---|---:|
| 1 | Foundation, Security & Data Integrity | Active; provisional scoring only | **75% — 300/400 ticks** |
| 2 | Market Data Infrastructure | Not opened / not scored | — |
| 3 | Core Chart Engine | Not opened / not scored | — |
| 4 | Indicators & Analytics | Not opened / not scored | — |
| 5 | Advanced Tools | Not opened / not scored | — |
| 6 | Release & Operations | Not opened / not scored | — |

Stage 1 has **30/40 provisional criteria** and **10 external acceptance criteria still open**. Gate 10 is **0/10 formally closed**. No percentage is assigned to Stages 2–6. No fresh overall-project percentage is asserted.

## Gate 10 — remaining external acceptance criteria

| Criterion | Status | Evidence still required |
|---:|---|---|
| 8 | OPEN | Exact target-environment acceptance evidence recorded in the Stage 1 matrix |
| 20 | OPEN | Owner-controlled target verification |
| 25 | OPEN | Zero-cost managed Redis alternative with required ACL/TLS and owner acceptance, or equivalent accepted architecture |
| 30 | OPEN | Actual recovery drill against owner-selected restore target |
| 31 | OPEN | Off-host snapshot retention and separate key custody demonstrated |
| 34 | OPEN | Target-environment evidence per acceptance matrix |
| 35 | OPEN | Target-environment evidence per acceptance matrix |
| 36 | OPEN | Maximum-duration observation, effective Fluid Compute read-back, Android WebView WSS, fan-out and cost/operational acceptance |
| 38 | OPEN | Durable aggregation, retention, host access controls and dashboard acceptance |
| 39 | OPEN | Persistent alert retention, escalation ownership and recovery drill |

Do not close an external criterion on the basis of repository code or documentation alone.

## Batch 10 — WebSocket lifecycle correction

- `poc/vercel_ws/index.py`: after receiving `idle_timeout`, the browser now displays **“Idle timeout — waiting for close”**. The authoritative WebSocket `close` event remains responsible for transitioning controls to disconnected.
- `backend/tests/test_vercel_ws_probe_contract.py`: added a contract assertion that the idle-timeout message handler does not prematurely mark the socket closed.
- Source commit: `8e43e8f0975130a96f4858df69d4d487a5bf97d8`.
- Regression-test follow-up commits: `b804a23147316483589883d66d6cd2c1c13c7274`, `84d30fdb81e13dc16083b60346b8cdba83d2956e`, `21e76a2a2c45e0462a9c6e99d3c1c42b17b5eed7`.
- The final test source was read back from the active branch. **Execution is not yet evidenced**; do not claim pytest passed.
- No Vercel deployment of these new commits is confirmed. The latest READY WSS and frontend previews are older commits; this is not a production release.

## Verification boundary

- Previous browser-level health/reconnect/idle-timeout observations remain valid only for the older deployed POC version and do not validate this Batch 10 source change.
- The 330-second probe is implemented but has not been observed end-to-end.
- The current frontend dependency audit still has unresolved High `picomatch@4.0.7` findings; no suppression, forced upgrade, or risky override was introduced.
- The exact-head GitHub Actions result is not available through the currently exposed workflow-run connector route.
- No Stage 1 ticks are added for this code/test change until required verification and acceptance evidence exists.

## Zero-cost and safety controls

- No paid plan, paid host, paid data provider, or billing activation.
- No deployment retry was triggered during this source-only correction.
- No production promotion or SSO weakening.
- No Termux installation or command required.
- No changes to `main`.
- No code/document repair is delegated to the project owner.

See [Batch 10 work-cycle report](WORK_CYCLE_2026-11-18_GATE10_BATCH10.md) and [Stage 1 acceptance addendum](STAGE_1_GATE10_BATCH10_ACCEPTANCE_ADDENDUM.md).


## Exact-head CI and deployment read-back — 18 November 2026 (Batch 10)

Commit: `90e7c479651a415a8d68ed1c0808291dc2baffe0`

- Vercel WSS POC preview: **READY** for this exact commit.
- Vercel frontend preview: **READY** for this exact commit.
- Frontend unit tests/build and source/bundle credential checks: **SUCCESS**.
- Backend pytest: **1,012 total; 1,011 passed; 1 failed**. The failure is the newly added concurrent histogram test's assertion direction: cumulative bucket counts are non-decreasing as the bucket upper bound increases. Batch 11 corrects the test from `left >= right` to `left <= right`. This was a test assertion defect; no evidence indicates metric sample loss.
- Frontend `npm audit --audit-level=high`: **FAILED** due to five High findings through `picomatch@4.0.7` (GHSA-fc5q-39xc-vjpf). The workflow's final audit enforcement correctly fails. No suppression or forced downgrade is permitted.
- Docker/container scan steps did not run to completion because the backend test job failed before image build. Artifact upload warnings for absent benchmark/image reports are expected downstream effects, not separate source defects.
- Full Git History Secret Audit for this exact commit was pending at the last read-back; no result claimed.

**Accounting unchanged:** Stage 1 = 300/400 ticks = 75% provisional; 30/40 criteria. Gate 10 = 0/10 formally closed. Open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38, 39. Stages 2–6 are NOT SCORED.


## Exact-head verification read-back — Batch 12 — 18 November 2026

Commit under verification: 9feb6cca8a51f563cae199eb33a6f57402eb3237.

Automated Tests run [44270272294](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272294) completed FAILURE, with the failure isolated to the required frontend dependency audit enforcement. Diagnostic continuity worked: independent checks completed rather than being skipped.

Verified successful steps:
- Frontend unit tests, production build, source and built-bundle credential scans.
- Android host preflight and immutable preview publisher contract tests.
- Backend pytest completed successfully, including the corrected cumulative histogram test and WebSocket POC tests.
- Synthetic SQLite outbox benchmark completed and its artifact was uploaded.
- Backend dependency audit passed.
- Backend Docker image build passed.
- Persistent-volume / Redis ACL smoke test passed, including restart persistence, fail-closed outage response, non-root identity, and SQLite integrity.
- Trivy container scan completed. Its uploaded JSON report contains zero HIGH and zero CRITICAL vulnerabilities across the Alpine OS and Python package targets.
- CodeQL run [44270272422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272422) passed.
- Full Git History Secret Audit run [44270272360](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272360) passed.

Remaining CI blocker:
- Frontend npm audit reports five High findings through dev-only transitive picomatch@4.0.7, GHSA-fc5q-39xc-vjpf / CVE-2026-112366, reached through fdir, tinyglobby, Vite and Vitest.
- The current npm registry still lists picomatch@4.0.7 as latest, while the advisory affects versions through 4.0.7 and has no published fixed version. A forced downgrade to Vite 6.2.7 would be a breaking dependency change and is not a verified patch for picomatch. No downgrade, suppression, override, or audit waiver is applied.
- The final audit-enforcement step correctly fails the workflow. Do not call the overall CI green.

Vercel preview read-back for the same source commit:
- WSS POC deployment dpl_EFLLSev63hRMKu9FEbrVTCUtR8Vg: READY.
- Frontend deployment dpl_9vazakEetH3VW4Qht3T5ymknWFdo: READY.
- WSS vercel.json explicitly sets fluid: true. This is source configuration evidence, not proof of effective runtime entitlement or a 330-second platform observation.
- The actual bounded 330-second WebSocket run and native Android WebView WSS remain unverified. Gate 36 stays OPEN.

Accounting unchanged:
- Stage 1: 300/400 ticks = 75% provisional; 30/40 provisional criteria.
- Gate 10: 0/10 formally closed.
- Open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: NOT SCORED.
- No Stage 1 ticks or Gate closures are awarded for CI diagnostics alone.