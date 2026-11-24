# DEZZTA CHART — Batch 62J-218: Exact-HEAD CI Failure Triage and Scoped Undici Audit

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base implementation HEAD:** `e8fa80256d23bd19e18d84cab4320bf5c425a0f6`  
**Cost:** ZERO COST  
**Vercel:** no deployment or Vercel commit  
**Main:** untouched

## 1. Exact-head verification

The branch tip was independently read from Git refs and matched `e8fa80256d23bd19e18d84cab4320bf5c425a0f6`. The Actions API was queried by exact `head_sha`; all four push workflows were returned for that SHA.

- Automated Tests: FAILED — run [45404639097](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45404639097).
- CodeQL: SUCCESS — run [45404639140](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45404639140).
- OCI ARM64 Image Readiness: SUCCESS — run [45404639228](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45404639228).
- Full Git History Secret Audit: SUCCESS — run [45404639143](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45404639143).

All four runs report the exact same `head_sha`. Overall exact-head result is **3/4 SUCCESS, 1/4 FAILED**.

## 2. Root cause

The failing Automated Tests job completed the new eight-case audit reporter suite successfully (8/8). The failure occurred in the following temporary Miniflare dependency check:

`npm ls undici --all --json`

The output contained two resolved Undici instances at version `7.30.1`, including the nested Miniflare dependency. The reporter rejected the entire npm tree because `npm ls` also emitted dependency diagnostics. This check is specifically intended to establish Undici resolution, so failing on unrelated package diagnostics was over-broad; ignoring Undici-specific missing/invalid findings would be unsafe.

No Worker runtime test failure was observed in the captured log: the preceding Worker node suite passed 27/27. The step exited before the Miniflare worker runtime test because the scoped dependency reporter returned nonzero.

## 3. Batch 62J-218 remediation

- Reporter now distinguishes Undici-specific problems from unrelated `npm ls` diagnostics.
- Any problem mentioning Undici still fails closed.
- Malformed `problems` data, missing root dependency maps, malformed JSON, and zero resolved Undici instances still fail closed.
- Unrelated `npm ls` diagnostics are logged explicitly and do not invalidate the scoped Undici resolution check.
- Test fixture defaults now include a resolved Undici package.
- Regression cases now cover Undici-specific missing dependency rejection, unrelated package diagnostic tolerance with two resolved Undici instances, and missing Undici rejection.
- Existing audit severity, summary consistency, transport-error and malformed-data tests remain.

The revised reporter and tests were committed on the active branch. Their correctness is **pending exact-head CI**; no green result is inferred from source inspection alone.

## 4. Changed files

- `scripts/report-npm-audit.mjs`
- `scripts/report-npm-audit.node-test.mjs`

No dependencies, lockfiles, app code, WebSocket protocol, credentials, provider settings, Redis retention policy, hosting, or deployment settings were changed.

## 5. Next verification and WebSocket work

1. Verify exact-head Automated Tests, CodeQL, OCI ARM64 and Full Git History Secret Audit for the remediation head.
2. If CI fails, inspect the exact failing step and logs, make a narrow correction, and verify the new exact head. Never carry over previous green checks.
3. Once exact-head CI is green, continue WebSocket Gate 25: owner-host private-key custody and signed transfer; remote gateway receipt custody; authenticated multi-gateway acknowledgement; then externally controlled WSS/TLS, Firebase production E2E, Android real-device reconnect/lifecycle, and recovery acceptance.
4. Keep destructive Redis retention blocked until gateway inventory/retirement, authenticated snapshot receipts, per-gateway floor acknowledgements, PEL policy and crash-safe trim/reconcile semantics are proven.

## 6. Project and indicator accounting

- Stage 1 remains 30/40 criteria = 75% provisional; not re-audited by this batch.
- Stage 2 remains active.
- Gate 25 remains open for external owner-host and multi-gateway acceptance.
- Redis destructive retention remains blocked.
- Indicator implementation was not changed; no indicator completion credit is awarded.
- Overall project and aggregate indicator completion remain **NOT SCORED** because approved weighted denominators are unavailable.
- ZERO COST; `main` untouched; Vercel deployment deferred.
- Delivery planning target remains approximately 24 December 2026, not a guarantee.
