# DEZZTA CHART — Work Cycle 2026-11-18 — Gate 10 Batch 13

## Purpose

Handle several connected issues in one controlled cycle: read back the exact-head CI result, verify both exact-source previews, inspect the upstream picomatch remediation proposal, add a regression guard for the production dependency boundary, and replace stale progress reporting with one authoritative current dashboard.

## Exact source and deployments

- Active branch: `phase-2/market-data-foundation`
- Source commit entering this cycle: `c3bcb0c6011f1f7228be17d16d227f325d7cbb29`
- WSS preview: `dpl_HYCzptpjB6ZkWGjmDhqAz1QkDozc` — READY
- Frontend preview: `dpl_2f6nmwUWNWC1iLBaMBn4AMeZwBwv` — READY
- Main branch untouched; no production promotion.

## CI findings

Automated Tests run [44271321142](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44271321142) completed FAILURE only at final frontend dependency-audit enforcement.

Successful exact-head checks:
- Backend pytest: 1,013 passed in 29.73 seconds.
- Frontend tests and production build.
- Frontend source and built-bundle credential scans.
- Android host preflight and immutable preview publisher tests.
- Synthetic SQLite outbox benchmark and report upload.
- Backend dependency audit.
- Backend container build.
- Persistent-volume / Redis ACL smoke test.
- Trivy scan: zero HIGH and zero CRITICAL.
- CodeQL [44271321171](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44271321171).
- Full Git History Secret Audit [44271321225](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44271321225).

## Frontend dependency blocker

The audit reports five High paths through `picomatch@4.0.7`, GHSA-fc5q-39xc-vjpf / CVE-2026-112366, via `fdir`, `tinyglobby`, Vite and Vitest. The lockfile marks each as dev-only; the root runtime dependency list does not include them.

Upstream PR [#238](https://github.com/micromatch/picomatch/pull/238) proposes a narrowly scoped parser mitigation, but remains open/unmerged. Its commit has no recorded successful check-runs in the read-back. It is not an official package release. No unsafe vendoring, fabricated package version, npm audit suppression, or forced Vite downgrade was made.

Added `backend/tests/test_frontend_dependency_exposure.py` to assert the affected tooling remains dev-only and absent from production runtime dependencies. This is a regression guard and exposure reduction; the audit remains enforced and the five High findings remain unresolved.

## WebSocket status

The exact WSS preview is READY. CI passed all 1,013 backend tests, including protocol close-code assertions and the bounded 330-second probe contract. The page-hidden guard prevents a background-tab interval from being counted as valid duration evidence.

Still unverified: actual foreground 330-second observation, effective Fluid Compute runtime read-back, native Android WebView WSS, and cross-instance fan-out. The POC remains synthetic-only.

## Progress accounting

- Stage 1: **300/400 ticks = 75% provisional**, 30/40 criteria.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- No gate or score increase awarded for tests/docs/deployments without external acceptance evidence.

## Zero-cost and owner controls

- No paid plan, billing, paid hosting, managed Redis, market-data subscription, paid monitoring, or Play publication.
- No Termux required.
- No user-directed code/document repair.
- No secrets, production market data, or production worker connected to the WebSocket POC.
