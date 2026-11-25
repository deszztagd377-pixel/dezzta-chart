# DEZZTA CHART — Batch 62J-237: exact-head CI closure and engineering reconciliation

**Date:** 25 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent:** `fa83c322df377b2c852ffac1fb499898db3b891e`  
**Scope:** documentation reconciliation only; no runtime code/dependency/schema changes  
**ZERO COST:** preserved

## 1. Exact-head CI closure

All four workflows completed successfully against the exact parent SHA:
- Automated Tests `45527447791`: 41/41 steps; 1,394 passed, 1 skipped, 6 warnings in 64.34 seconds.
- CodeQL `45527447840`: Python 8/8 and JavaScript/TypeScript 8/8.
- OCI ARM64 `45527447819`: 7/7.
- Full Git History Secret Audit `45527447878`: 6/6.

No failed steps and no active workflow remains for the parent SHA. The one pytest skip is the isolated Redis TLS integration fixture; it is not owner-host acceptance. Container smoke verified Redis ACL denial paths, AOF/ACL persistence after restart, backend fail-closed behavior during Redis outage and recovery, non-root UID/GID 10001, SQLite volume ownership/integrity/restart persistence and HTTP rate limiting. Backend dependency audit reported no known vulnerabilities. Trivy image scan completed and artifact `14983702058` was uploaded; no clean-image claim is made without inspecting the report.

## 2. Current WebSocket integration boundary

The backend validates exact canonical series identity and entitlement before it registers a downstream `OhlcvStreamHub` subscription. The cleanup path removes that downstream subscription. The missing repository-side feature is an upstream provider-demand coordinator with acquire/release semantics, reference counting, serialized source mutation and gateway/adapter state reconciliation.

Do not conflate:
- client panel lease registry;
- authenticated backend downstream fan-out;
- provider upstream demand ownership.

They are separate layers. The coordinator must acquire only after canonical identity and entitlement validation, and release in guaranteed cleanup. One user's disconnect or entitlement revocation must not stop another user's shared upstream demand.

**Implementation gate:** provider-demand implementation remains gated on a reviewed, provider-neutral blueprint and deterministic fake/offline adapter contract. No provider SDK version change, live feed, API key, billing, or external provider request was made. Under ZERO COST, a live market-data source is not presumed available or approved.

## 3. Stage 1 blocker answer

Stage 1 remains 30/40 = 75% provisional. The ten unaccepted criteria are:
8 secret injection/rotation proof on owner host;
20 Firebase no-billing auth/entitlement E2E on real clients;
25 owner-host Redis TLS/ACL/private binding/persistence/recovery;
30 actual DB restore into fresh target;
31 encrypted off-host backup and independent key recovery;
34 real persistent-volume mount/ownership/restart/disk recovery;
35 backend runtime/health on owner hardware;
36 public authenticated WSS/TLS and real browser/Android lifecycle/cross-instance;
38 durable owner-host metrics and operational recovery;
39 zero-cost local alert and incident drill.

Repository CI cannot close these without real owner-host/device evidence. Do not weaken acceptance criteria or inflate Stage 1 percentage with documentation or synthetic tests. The single-device constraint and ZERO COST may defer several external criteria until an already-existing free environment is available.

Stage 1 criterion #25 (Redis) is not Project Gate 25 (Ed25519 snapshot receipt/high-water ACK). Both remain open.

## 4. Indicator status

28 named tests remain the verified source inventory (21 calculation + 7 shared hook), not a completion percentage. SMA20, EMA20, RSI14 Wilder, MACD12/26/9 and Bollinger20,2 are calculation foundations only. Shared hook is not integrated into CandlestickChart. Footprint is synthetic/offline and gated; VP variants, Heatmap and Liquidation Maps remain incomplete/not integrated. Indicator aggregate is NOT SCORED.

## 5. Dashboard and controls

- Stage 1: 🟨 30/40 = 75% provisional.
- Stage 2: 🟦 active / NOT SCORED.
- Stage 3: ⬜ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5: ⬜ NOT SCORED.
- Stage 6: ⬜ NOT SCORED.
- Gate 10: 🟥 0/10 closed.
- Overall: ⚪ NOT SCORED.
- Significant progress / IP3S: ⚪ NOT SCORED.
- Indicators: ⚪ aggregate NOT SCORED.

ZERO COST, no Vercel deployment, no `main` changes, no destructive Redis operations. Delivery planning target: approximately 24 December 2026.

**Batch outcome:** CI 4/4 exact-parent success; automated tests 1,394 passed / 1 skipped; provider-demand integration boundary clarified; Stage 1 and indicator ledger reconciled; external owner-host/device acceptance remains open.
