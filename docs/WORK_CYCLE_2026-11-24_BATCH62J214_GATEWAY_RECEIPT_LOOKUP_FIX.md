# DEZZTA CHART — Batch 62J-214: Gateway Receipt Lookup Regression Fix

**Date:** 24 November 2026  
**Branch:** phase-2/market-data-foundation  
**Failed-test baseline:** b6f56e53b4d0c35bceb24c9e944cf9ee20e27afc  
**Cost:** ZERO COST  
**Vercel deployment:** deferred.

## Exact baseline CI findings

On baseline b6f56e5:
- CodeQL: SUCCESS.
- OCI ARM64: SUCCESS.
- Full Git History Secret Audit: SUCCESS.
- Automated Tests: FAILURE — 1,382 passed, 1 skipped, 2 failed, 6 non-failing warnings.

Both failures were gateway runtime regression assertions:
1. Configured source mismatch returned “immutable receipt is missing” because lookup used the expected source ID before comparing it with the installed source.
2. Forged checkpoint replica ID returned “immutable receipt is missing” because lookup used the mutable checkpoint replica ID before checking it against the store's durable replica identity.

The gateway still failed before Redis construction, but the diagnostic path masked the intended metadata mismatch check.

## Fix

Receipt lookup now uses the installer-reported source/generation and the replica store's durable replica ID. The runtime then verifies the receipt's authenticated source binding and checks the configured source ID and checkpoint replica ID in the normal consistency validation. This preserves fail-closed behavior while ensuring both corrupt/mismatched states reach the correct rejection path before Redis construction.

No signature-verification relaxation, schema weakening, or Redis retention change was made.

## Verification

The exact new HEAD must pass all four required workflows before acceptance. The source/test change is committed only after the baseline workflow set completed; the new exact-HEAD CI is pending.

No main-branch changes, paid dependencies, secrets, key material, deployment, or Vercel release.
