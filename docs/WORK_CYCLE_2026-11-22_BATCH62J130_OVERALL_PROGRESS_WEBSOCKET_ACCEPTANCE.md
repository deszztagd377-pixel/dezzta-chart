# Batch 62J-130 — Overall project progress dashboard and WebSocket acceptance reconciliation

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited HEAD:** `3468489152bf2b6432b4e2296fa74d64081a1035`  
**Scope:** read-only WebSocket source audit, exact-head CI status check, overall project progress accounting and documentation correction. No runtime source or test changes.

## 1. Overall DEZZTA CHART project progress indicator

The official six-stage project dashboard is:

| Stage | Official scope | State | Progress |
|---|---|---|---:|
| 1 | Foundation, Security & Data Integrity | Active; 30/40 provisional criteria accepted; 10 external acceptance criteria remain open | **75% provisional** |
| 2 | Market Data Infrastructure | Not officially opened; preparatory implementation exists | **NOT SCORED** |
| 3 | Chart Engine & Timeframe | Not officially opened | **NOT SCORED** |
| 4 | Indicators & Analytics | Not officially opened; calculation groundwork exists | **NOT SCORED** |
| 5 | Professional UI & Interactive Tools | Not officially opened; expansion gate applies | **NOT SCORED** |
| 6 | Hardening, Validation & APK Release | Not officially opened | **NOT SCORED** |

**OVERALL PROJECT: NOT SCORED.** This is the correct official overall indicator, not a missing number. The project has no approved weighted M1–M8 denominator for aggregating the six stages. A historical 20.9% figure is not a current weighted result and must not be reused.

### Stage 1 meter

- 40 criteria × 10 ticks = 400 total ticks.
- 30 provisionally accepted criteria × 10 = 300 ticks.
- 300/400 = **75% provisional**.
- 10/10 Gate 10 external criteria formally closed: **0/10**.
- Stage 1 is not production-accepted. No stage transition is authorized.

### Separate indicators (never conflate)

- **Overall project progress:** NOT SCORED pending approved six-stage denominator and weights.
- **Stage 1 progress:** 75% provisional.
- **Gate 10 closure:** 0/10 formally closed.
- **IP3S (per-work-cycle delivery quality):** Batch 62J-129 = 58/100. This is not project completion.
- **Technical indicator implementation:** six foundations/shared hook 🟨; Footprint 🟧; Heatmap and Liquidation Maps 🟥. No aggregate indicator percentage is approved.

## 2. WebSocket Gate 25 — checkpoint digest correction confirmed

Read-only source review of `backend/app/ohlcv_store.py` confirms the `ohlcv_replica_checkpoint` schema stores source ID, replica ID, applied cursor, snapshot generation, retention floor, bar-retention metadata and schema/protocol versions. It does **not** persist the snapshot SHA-256. The checkpoint read path likewise does not return a snapshot digest.

`backend/app/ohlcv_redis_gateway_runtime.py` validates the installer-returned digest as 64 lowercase hexadecimal characters and compares source ID, generation and cursor against the durable checkpoint. The digest is propagated in runtime evidence, but is not compared with a digest anchored in that checkpoint.

The global snapshot exporter/verifier does compute and verify SHA-256 over canonical snapshot content. The installer callback is owner-supplied and must invoke the verified store installer. The exact missing element is durable checkpoint anchoring of the snapshot digest, not the source snapshot hash computation itself.

**Design decision before any source edit:** determine whether a snapshot-only digest should remain as immutable installation provenance after live stream updates, or whether the checkpoint should distinguish installed-snapshot digest from current replica state. Define migration for existing replica databases, rollback compatibility, and integrity semantics first. No schema patch is justified without this decision.

Gate 25 remains OPEN pending the design decision and real owner-host authenticated transfer/receipt, Redis TLS/ACL/persistence/restart/failover evidence.

## 3. WebSocket Gate 36 — acceptance status

Source review confirms:
- HTTPS ticket endpoint requires a verified Firebase principal.
- Ticket is single-use, 90-second TTL, bound to subject and `market-data` purpose.
- Production rejects raw Firebase-token WebSocket auth fallback.
- Handshake rejects a non-empty disallowed Origin; missing Origin is allowed for native clients and must not be treated as authentication.
- Exact-series/canonical-instrument entitlement is separately checked before snapshot and rechecked during active subscription.
- Client obtains a fresh Firebase ID token for HTTPS ticket exchange and sends the short-lived ticket in the WebSocket auth frame.

Open threat-model decision: whether series and/or Origin should also be bound into ticket claims. This is not an assumed defect; current separate series authorization and Origin defense-in-depth must remain accurately described.

No reverse-proxy configuration or verified public hostname/certificate is present in the repository. No live Firebase project, public HTTPS/WSS, actual browser production session, Android WebView lifecycle, real network handover/replay/resnapshot or duplicate suppression acceptance has been evidenced.

**Gate 36 remains OPEN.** CI tests do not prove deployed WSS or real-device behavior.

## 4. Exact-head CI

All runs below target `3468489152bf2b6432b4e2296fa74d64081a1035`:
- Automated Tests [44989033922](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989033922): **IN PROGRESS** at latest check.
- CodeQL [44989033909](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989033909): **SUCCESS**.
- Full Git History Secret Audit [44989033898](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989033898): **SUCCESS**.

Do not label the exact-head test workflow green until its run concludes successfully.

## 5. ZERO COST and scope

No runtime code/tests changed. No paid hosting, domain, deployment, cloud resource, account, production credential, Android device/Termux action or external service was created. `main` remains untouched. Working branch remains `phase-2/market-data-foundation`.

## 6. Next acceptance work

1. Complete exact-head Automated Tests run.
2. Write a short ADR for immutable snapshot digest provenance versus mutable replica checkpoint state; include schema migration and backward-compatibility tests before any implementation.
3. Continue Gate 36 ticket threat-model review, then create a deployment-neutral WSS reverse-proxy acceptance checklist only; do not invent hostname or proxy config.
4. Keep Stage 1 at 75% provisional and overall project NOT SCORED until formal denominator/weight approval.
5. Keep indicator implementation stages and image-reference gates unchanged.
