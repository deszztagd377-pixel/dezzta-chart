# Work Cycle Batch 15 — Upstream dependency remediation review

**Date:** 18 November 2026  
**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Cost:** ZERO COST

## Purpose

Investigate whether the High `picomatch@4.0.7` finding has a safe upstream patch that can be applied without bypassing CI or introducing unreviewed behavior.

## Findings

- GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) remains published for CVE-2026-112366; current GitHub page marks it Unreviewed and lists no patched version. OSV continues to carry the record.
- Upstream issue [#247](https://github.com/micromatch/picomatch/issues/247) remains open. Discussion notes that the Snyk-specific advisory was revoked, but the GitHub advisory remains.
- PR [#238](https://github.com/micromatch/picomatch/pull/238) remains open. Review measurements show residual exponential cases including `+(*)`, `*(*)`, and `+(a*)`; this does not fully close the reported behavior.
- PR [#237](https://github.com/micromatch/picomatch/pull/237) remains open. Review discussion reports uncovered multi-branch patterns and edge cases involving quoted stars and bracket classes.
- PR [#246](https://github.com/micromatch/picomatch/pull/246) targets the 2.x branch, not this project's 4.x dependency path; its description is scoped to selected shapes.
- PR [#235](https://github.com/micromatch/picomatch/pull/235) is closed and contains maintainer disagreement about threat model. It does not withdraw the GitHub advisory.

## Engineering decision

**No patch was applied.** All candidate fixes are unmerged and have known gaps or are for a different major version. Keep the final npm audit enforcement active, preserve the development-only dependency boundary, and reassess after a maintainer-reviewed release plus independent regression testing.

## Accounting

- Stage 1: **75% provisional** (300/400 ticks; 30/40 criteria).
- Gate 10: **0/10 closed**.
- Open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- No score change for research alone.
