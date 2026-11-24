# DEZZTA CHART — Batch 62J-219: npm Extraneous Undici Override CI Correction

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Failed remediation HEAD:** `1130c53b5d9f95def9b455985b9a28445431c61b`  
**Cost:** ZERO COST  
**Vercel:** deployment deferred  
**Main:** untouched

## 1. Exact-head CI result for previous remediation

The four workflows for exact HEAD `1130c53b5d9f95def9b455985b9a28445431c61b` completed:

- Automated Tests: FAILED — run [45406076334](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406076334).
- CodeQL: SUCCESS — run [45406076364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406076364).
- OCI ARM64: SUCCESS — run [45406076872](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406076872).
- Full Git History Secret Audit: SUCCESS — run [45406076614](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406076614).

Automated Tests confirmed 10/10 reporter regression tests passed. The scoped tree reporter then identified the exact remaining failure: npm reports the root-level `undici@7.30.1` package as `extraneous`, because it is introduced by the temporary no-save install/override rather than as a direct project dependency. The nested Miniflare Undici and root override were both resolved at 7.30.1. The Worker runtime test was not reached because the reporter stopped first.

## 2. Batch 62J-219 correction

The reporter now:
- fails closed on Undici-specific `missing` or `invalid` diagnostics;
- tolerates npm's `extraneous: undici@...` diagnostic from the temporary no-save override, while still printing the complete resolved package paths and versions;
- logs all tolerated npm diagnostics for audit visibility;
- continues to reject malformed tree JSON, malformed `problems`, missing root dependencies, and zero resolved Undici instances;
- retains the separate npm audit HIGH/CRITICAL, summary-integrity, and transport-error checks.

Regression coverage now includes:
- missing Undici is rejected;
- unrelated package diagnostics are tolerated only when Undici is resolved;
- the expected extraneous root Undici override is tolerated when the nested and root copies are present;
- missing resolved Undici is rejected.

This is a narrow npm Arborist diagnostic correction; no vulnerability severity gate is disabled.

## 3. Changed files

- `scripts/report-npm-audit.mjs`
- `scripts/report-npm-audit.node-test.mjs`

No application/Worker/WebSocket code, dependency manifest, lockfile, credentials, provider configuration, Redis retention, hosting, or deployment was changed.

## 4. Verification state

The 10-test suite passed on the preceding exact HEAD, but the current Batch 62J-219 source/test commits have not yet received exact-head CI. All four required workflows must finish against the final documentation HEAD before acceptance. Do not infer success from the prior run.

## 5. WebSocket continuation

After this CI correction is green, continue Gate 25 and WebSocket acceptance in this order:
1. Verify owner-host source signer custody and real signed snapshot transfer.
2. Verify persisted immutable receipt after gateway restart.
3. Verify remote receipt custody and authenticated multi-gateway acknowledgements.
4. Complete owner-controlled public WSS/TLS/proxy acceptance.
5. Complete Firebase sign-in, revocation and entitlement E2E.
6. Complete Android/browser real-device lifecycle, reconnect and resnapshot acceptance.
7. Complete monitoring, backup/restore and recovery evidence.

Redis destructive retention remains blocked pending gateway inventory/retirement, per-gateway floor acknowledgements, PEL policy and crash-safe trim/reconcile proof.

## 6. Progress accounting

- Stage 1: 30/40 criteria = 75% provisional.
- Stage 2: active.
- Gate 25: OPEN; external owner-host and multi-gateway evidence outstanding.
- Indicators: no implementation changes; no completion credit.
- Overall project and aggregate indicator progress: NOT SCORED.
- ZERO COST; `main` untouched; Vercel deployment deferred.
- Planning target: approximately 24 December 2026, not a guarantee.
