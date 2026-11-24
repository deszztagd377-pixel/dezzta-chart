# DEZZTA CHART — Batch 62J-217: Temporary Dependency Audit Fail-Closed Regression Coverage

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Implementation HEAD:** `f8997b59ae5f644a3680cdd9001cdc2b24a98803`  
**Cost:** ZERO COST  
**Vercel:** no deployment or Vercel commit  
**Main:** untouched

## 1. Scope and source audit

Batch 62J-216 retained an explicit post-install `npm audit --json` gate after suppressing the redundant install-time audit summary with `--no-audit`. The reporter already rejected reported HIGH/CRITICAL findings and npm audit errors. This batch hardens the diagnostic boundary against internally inconsistent or incomplete JSON and incomplete dependency-tree output.

No application chart, market-data, WebSocket, indicator, credential, provider, hosting, or deployment code was changed.

## 2. Changes

1. Added `scripts/report-npm-audit.node-test.mjs` with isolated child-process fixtures.
2. Reporter validates the audit JSON object, vulnerability map, severity summary, non-negative integer severity counts, and total-to-severity consistency.
3. HIGH/CRITICAL findings are checked against both the metadata summary and individual vulnerability entries; an inconsistent zero summary cannot hide a HIGH/CRITICAL package finding.
4. Missing summaries, malformed findings, npm audit registry/transport errors, and incomplete dependency-tree output fail closed.
5. The npm dependency tree rejects reported `npm ls` problems and malformed/missing root dependencies.
6. The new regression suite is run directly by the required Automated Tests workflow.

## 3. Regression coverage

Eight focused cases are included:
- clean complete audit and nested Undici path reporting;
- HIGH advisory despite inconsistent zero metadata;
- CRITICAL advisory rejection;
- LOW-only advisory acceptance;
- incomplete `npm ls` tree rejection;
- npm audit registry/transport error rejection;
- missing audit summary rejection;
- malformed dependency-tree JSON rejection.

An isolated local reproduction of the reporter/test logic passed **8/8** cases, and Node syntax checks passed. This is local diagnostic evidence, not a substitute for the repository's exact-HEAD CI run.

## 4. Commit record

- `0b4bc924f4848fb3f2af5993e259d1d905874506` — add regression tests.
- `c03926945f835d7ffe78ea4d66156686edcc12cc` — fail-closed audit summary validation.
- `f28e8839cec75119ed6c63068b7d0678732385be` — execute regression tests in CI.
- `c026b01a3d3f4ca0aa22c5c4f93eccc97c41c403` — correct stderr assertion.
- `5622bedd57e80277bf3503ae61dba5f59eff9058` — reject incomplete dependency trees.
- `f8997b59ae5f644a3680cdd9001cdc2b24a98803` — add LOW-only and dependency-tree failure cases.

## 5. Exact-head CI evidence

The previous Batch 62J-216 report records five successful workflows on its base implementation HEAD `ebb64137442a14b185a7c4483bcd424267dfd482`. That evidence is not transferred to this batch.

For implementation HEAD `f8997b59ae5f644a3680cdd9001cdc2b24a98803`, the combined commit-status endpoint returned an empty status list. The available workflow-run helper returned no runs because it only exposes pull-request-triggered runs. Therefore exact-head CI is **UNVERIFIED** by the available read-back; it is not marked SUCCESS, FAILED, or assumed complete. The newly added regression suite must complete in the branch's Automated Tests workflow before this batch receives CI acceptance.

## 6. Project progress carry-forward

- Stage 1: 30/40 = 75% provisional; not independently re-audited in this batch.
- Stage 2: active; WebSocket/Gate 25 external acceptance remains open.
- Gate 25: repository foundation includes immutable per-generation receipts, atomic installation and Ed25519 verification; owner-host key custody, real signed transfer, remote gateway receipt custody and multi-gateway acknowledgements remain external blockers.
- Redis destructive retention: blocked; no `XTRIM`, `XDEL`, or consumer-group destruction enabled.
- Indicators: no source change; calculation/shared-hook foundations remain blue, Footprint remains gated prototype, Volume Profile/Heatmap/Liquidation Maps remain open. Visible chart integration is not credited.
- Overall project and aggregate indicator completion: NOT SCORED; approved denominators are unavailable.
- ZERO COST; `main` untouched; Vercel deployment remains deferred.
- Planning target remains approximately 24 December 2026, not a guarantee.

## 7. Next work order

1. Read back exact-head Automated Tests, CodeQL, OCI ARM64 and Full Git History Secret Audit results; do not transfer previous green checks.
2. If any exact-head workflow fails, inspect the failing job and logs, fix only the responsible issue on this branch, and repeat verification.
3. Continue Gate 25 remote receipt authentication/custody and owner-host acceptance without enabling destructive Redis retention.
4. Keep owner-host WSS/TLS, Firebase production E2E, Android real-device lifecycle, monitoring/recovery and cross-instance evidence tracked independently.
5. Preserve the Stage 4 gate and complete indicator inventory only with owner-approved decisions and reviewed blueprints.
