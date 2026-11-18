# DEZZTA CHART — Batch 30 Engineering Audit

**Date:** 18 November 2026  
**Branch:** phase-2/market-data-foundation  
**Exact HEAD:** 0126c847b015f08645b8b64cdb37ad458bc2fd43  
**Application source baseline:** e6db77210dd28bd82196b2b7bf7d8d7e7256fc37  
**Cost policy:** ZERO COST  
**Main:** untouched

## Executive result

- Frontend unit tests: **212/212 PASS** (26 files).
- Backend pytest: **1,030 PASS in 35.88s**.
- Frontend production build and source/bundle credential scans: PASS.
- Android preflight and immutable preview publisher tests: PASS.
- Synthetic SQLite outbox benchmark: PASS.
- Backend dependency audit, container build, Redis ACL/persistent-volume smoke test, Trivy scan/report: PASS.
- CodeQL: PASS. Full Git History Secret Audit: PASS.
- Automated Tests workflow remains FAILURE **only** at final frontend dependency audit enforcement: five High picomatch findings.

Exact runs:
- [Automated Tests #44304765032](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44304765032)
- [CodeQL #44304764936](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44304764936)
- [Full Git History Secret Audit #44304764965](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44304764965)

## WebSocket verification

### Verified

- Frontend ohlcvWebSocketClient tests: 6 passing tests.
- Frontend ohlcvStreamProtocol tests: 14 passing tests.
- Frontend ohlcvStreamSupervisor tests: 14 passing tests.
- All backend stream, authenticated API WebSocket, synthetic POC protocol and probe contract tests are included in 1,030 passing backend tests.
- Existing WSS POC preview dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg is READY, source 9873a5fd1c52a0cbab94683c0c309732407212e8, preview target only.
- Protected /health returned HTTP 200 with mode=synthetic-only and production_data_connected=false.

### Not verified; Gate 36 stays OPEN

- Public WebSocket Upgrade and real browser ping/pong on deployed Vercel.
- Foreground 330-second probe and platform-originated close attribution.
- Effective deployed Fluid Compute read-back.
- Native Android WebView WSS.
- Cross-instance fan-out and production data integration.

Vercel's [Fluid Compute documentation](https://vercel.com/docs/fluid-compute) and [function duration documentation](https://vercel.com/docs/functions/configuring-functions/duration) list Hobby maximum duration as 300 seconds. The 330-second client probe is an observation window beyond that limit, not evidence that a serverless invocation can remain alive for 330 seconds. No owner-observed run is claimed.

## Vercel deployment controls

- Exact-SHA deployment lookups for branch HEAD 0126c847... returned zero deployments for both linked projects.
- Existing frontend deployment dpl_tYw6Y4dbeSzwR6t7shtkKpT7nxBc was canceled by Ignored Build Step with exit code 0. Log indicates the changed paths did not require a frontend build; this is an intentional skip, not a compile failure.
- Existing WSS preview remains READY; no new deployment was triggered or retried.
- Root vercel.json retains main=true and phase-2/market-data-foundation=false.

## Dependency audit blocker

Exact-head npm audit reports five High findings through picomatch in development tooling (fdir, tinyglobby, Vite and Vitest). Its npm audit fix --force recommendation would downgrade Vite to 6.2.7, a breaking change. GitHub's [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) and [OSV record](https://osv.dev/vulnerability/GHSA-fc5q-39xc-vjpf) still list affected versions through 4.0.7 without a published patched version. No downgrade, unmerged patch, suppression, waiver, or speculative override is accepted. CI remains fail-closed.

## Gate 10 accounting

| Gate | Status | Evidence still required |
|---|---|---|
| 8 | OPEN | Owner-controlled no-cost runtime secret injection and leakage proof |
| 20 | OPEN | Real identity, revocation, entitlement and reconnect acceptance |
| 25 | OPEN | Owner-controlled existing Redis endpoint, TLS, ACL and restart/failure proof |
| 30 | OPEN | Actual owner-target database restore drill and post-restore validation |
| 31 | OPEN | Zero-cost off-host artifact, separate key custody, retention/access policy, external restore |
| 34 | OPEN | Existing-host volume identity, permissions, disk-pressure and durability |
| 35 | OPEN | Existing-host HTTPS/certificate and runtime secret-source evidence |
| 36 | OPEN | Deployed WSS Upgrade, 330s observation, platform close, Android WebView, fan-out |
| 38 | OPEN | Durable metrics, bounded retention, access controls and dashboard acceptance |
| 39 | OPEN | Persistent alert, escalation owner and completed recovery drill |

## Progress indicator

- Stage 1: **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** pending approved M1–M8 weighting and criterion mapping. Historical 20.9% is not current progress.

No score is awarded for CI success alone where owner-target or external acceptance remains required. No Termux is required for this audit. If future owner-device restore work requires it, the need will be explained before any installation or command request.
