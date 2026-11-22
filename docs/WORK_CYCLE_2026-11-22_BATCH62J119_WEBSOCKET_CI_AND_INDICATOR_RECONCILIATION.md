# DEZZTA CHART — Batch 62J-119
## WebSocket acceptance CI closure and indicator progress reconciliation

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750`  
**Scope:** exact-head CI, WebSocket production acceptance boundary, zero-cost constraints, full indicator ledger reconciliation  
**Change type:** documentation only; no runtime code changed.

## Batch 62J-119 — WebSocket acceptance and indicator ledger exact-head reconciliation (22 November 2026)

**Verified parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750` on `phase-2/market-data-foundation`. This checkpoint was created only after all three workflows for that exact SHA completed successfully.

**Exact-head CI:**
- Automated Tests #1954 — [run 44982930281](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281): **SUCCESS**. Frontend unit tests/build, backend tests, isolated Redis TLS/CA/hostname enforcement fixture, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke test using shared Redis guard and persistent volume, Trivy image scan/report export/upload, and dependency-audit enforcement all completed successfully.
- CodeQL [run 44982930379](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930379): **SUCCESS**.
- Full Git History Secret Audit [run 44982930324](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930324): **SUCCESS**.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281/artifacts/14739265202). The workflow completed the configured HIGH/CRITICAL scan and uploaded the JSON report. Do not infer a zero-vulnerability result without reviewing the artifact contents.

These results verify the repository workflow and its CI service topology only. The CI Redis instance, ephemeral runner volume, and container smoke are not the intended OCI host or production Redis service.

**WebSocket repository evidence:** source-side publisher and gateway runtime factories, durable SQLite outbox, atomic snapshot/watermark primitives, Redis Streams publisher/consumer, per-gateway consumer groups, replica snapshot installation checks, fail-closed runtime construction, ticket authentication/renewal, reconnect/replay and client failure-matrix tests are present in the audited source. The latest CI validates the covered repository paths. The default FastAPI app intentionally does not invent owner-specific publisher/replica factories or trust snapshot receipts; those must be injected from a verified owner-controlled host setup.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS endpoint, production Firebase token/entitlement evidence, owner-host Redis TLS/ACL/persistence/rotation/failover, authenticated global snapshot manifest and per-gateway installation receipts, or real browser + Android WebView lifecycle evidence has been supplied. A successful CI container smoke cannot close those host/client gates.

**ZERO COST boundary:** no OCI account or resource was created, no deployment or public endpoint was started, no paid resource or trial-credit dependency was introduced, no credentials were requested, no device/Termux operation occurred, and `main` was not touched. OCI remains a conditional candidate subject to actual Always Free eligibility and adult account-owner approval.

**Indicator disposition — no source change and no progress credit:** the source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains the calculation baseline. The comparison through parent HEAD `6d5a05d611615972d5826002442a65e74c179750` is documentation-only; no indicator formula, hook, chart renderer, UI, or indicator test source changed. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formula definitions, warm-up indices, numerical safeguards, data identity, stale-series invariants, UI acceptance and reference prerequisites remain in the canonical audit and ledger. Aggregate indicator percentage remains unscored without approved weights and denominator.

**Project accounting:** Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI or documentation-only checkpoint. No progress is awarded from CI alone.

**Next zero-cost sequence:** preserve the green exact-head CI; finish ARM64 build/configuration readiness without provisioning; have the adult account owner verify OCI eligibility, capacity and all possible charges; only then, with explicit authorization, consider an Always Free-only host. Collect actual host and client evidence for Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Close Gate 10 only after evidence review and operator sign-off.

---


## WebSocket acceptance — detailed evidence boundary

### Verified in repository and CI
- HTTPS ticket exchange and short-lived, single-use WebSocket tickets; Firebase ID tokens are not put in WSS URLs or raw auth frames.
- Ticket expiry, replay protection, cross-account renewal rejection, entitlement rechecks and fail-closed behavior.
- WebSocket transport, heartbeat/pong timeout, close behavior, reconnect supervisor and stream replay/snapshot continuity tests.
- SQLite authoritative OHLCV outbox with monotonic cursor and atomic snapshot/high-water read.
- Source publisher checkpoint fencing and deterministic Redis Stream append/read-back.
- Gateway replica store, generation-scoped consumer groups, pending-message reclaim, durable apply-before-ACK and explicit resnapshot on retention gaps.
- Runtime factories validate owner-provided snapshot evidence and Redis configuration; the normal module-level app does not activate publisher/replica roles automatically.
- CI built and smoke-tested the backend container against a temporary Redis service and persistent CI volume; configured Trivy scan/report and dependency audit completed.

### Still required outside CI
1. Real Firebase project: valid, expired, revoked, wrong-project tokens and entitlement grant/revoke (Gate 20).
2. Owner-controlled Redis: TLS CA + hostname verification, dedicated least-privilege role ACLs, secret rotation, persistence, restart/failover and recovery (Gate 25).
3. Exact global snapshot artifact: independently verified SHA-256 manifest and authenticated matching install receipt for every required gateway; generation/source/cursor consistency before publisher activation (Gate 25/36).
4. Public HTTPS/WSS: stable no-cost hostname, trusted certificate, renewal, reverse-proxy Upgrade headers/timeouts and no Redis/public worker exposure (Gate 35/36).
5. Real browser and Android WebView: foreground/background, network interruption, fresh-token reconnect, replay/resnapshot, renewal beyond ticket TTL, duplicate suppression and teardown (Gate 36).
6. Durable monitoring, alert routing/acknowledgement, disk-pressure, retention and recovery evidence (Gate 38/39).

A source callback or environment variable is not evidence that a trusted remote snapshot was installed. Do not activate a publisher until its verifier can authenticate the exact source snapshot and every required gateway receipt. Do not enable replica mode until its installer verifies the artifact and durable local checkpoint. Keep the default single-process source-mode hub when these prerequisites are absent.

### Zero-cost deployment policy
- No paid hosting, managed Redis, paid domain, paid DNS, paid mail, paid monitoring, paid backup or trial-credit resource.
- No Pay As You Go upgrade.
- OCI is only a conditional candidate; actual Always Free label, home-region capacity, storage, public-IP/DNS/TLS path and billing state must be verified by the adult account owner before any resource creation.
- If any required public ingress or hostname component cannot be verified as zero-cost, defer public WSS rather than silently introduce a charge.
- Do not ask for or transmit secrets in chat. No account/resource provisioning occurred in this batch.

## Indicator progress — complete current disposition

The canonical source-backed audit remains `docs/INDICATOR_PROGRESS_AUDIT_2026-11-22.md`; the detailed historical and current-state ledger remains `docs/INDICATOR_PROGRESS_LEDGER.md`.

| Study / subsystem | Current status | Verified foundation | Remaining acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close rolling arithmetic mean; first valid candle index 19 | Chart overlay, toggle, legend/latest value, identity transitions, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | First 20-close SMA seed; alpha 2/21; first valid index 19 | Same visible overlay and lifecycle acceptance |
| RSI14 Wilder | 🟨 Foundation | 14 close changes; initial gain/loss averages then Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle, values and lifecycle tests |
| MACD12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | MACD/signal lines, histogram, zero guide, pane, toggle and lifecycle tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values and lifecycle tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and aligned calculation output | Dedicated hook tests, chart binding, loading/error handling, stale clearing, per-series isolation and renderer integration |
| Footprint | 🟧 Synthetic / gated | Offline educational accumulator only; not exchange-native bid/ask truth | User reference image and reviewed blueprint first; validated source contract; ON-only spaced cluster renderer; OFF normal candle-spacing regression |
| Heatmap | 🟥 Not implemented | No verified implementation | User reference, zero-cost source feasibility, validated contract, reviewed blueprint, renderer/legend/scale/toggle/tests |
| Liquidation Maps | 🟥 Not implemented | No verified implementation | Zero-cost source feasibility, validated calculation/data contract, reference/blueprint, renderer/scale/tests |

### Invariants and scope controls
- All five calculations consume closes from the exact selected OHLCV series and preserve source-array length/index alignment.
- Warm-up entries are null, not zero; first valid indices remain 19, 19, 14, 25/33 and 19 respectively.
- No future-candle repaint; series identity includes provider/dataset/instrument/timeframe/bucket policy/calendar where applicable.
- Symbol, venue, dataset, chart or timeframe changes must clear stale series before replacement data is accepted.
- Footprint OFF must preserve ordinary candlestick spacing. Only explicit Footprint ON may switch to spaced candle clusters.
- Do not start Footprint or Heatmap visual implementation before the relevant user-provided reference image(s) and a reviewed blueprint.
- The five calculation foundations do not constitute completed visible chart features. Aggregate indicator percentage remains unscored until weights and a completion denominator are approved.
- Indicator work remains in its planned roadmap stage; this documentation and WebSocket CI do not authorize skipping stages.

## Stage and gate accounting

- Gate 10: **0/10 formally closed**.
- Stage 1: **30/40 = 75% provisional**.
- Host/operator tracks still require real evidence: Gates 8, 30, 34, 35, 39.
- Integration/acceptance tracks still require real evidence: Gates 20, 25, 31, 36, 38.
- Stage 2 remains blocked until every Stage 1 exit criterion is accepted and documented.
- No indicator or project progress credit is awarded by this documentation-only batch.

**Final result:** exact-head repository CI is green at parent HEAD; WebSocket production acceptance remains open; OCI remains conditional under ZERO COST; indicator status is fully reconciled without artificial progress; Stage 1 remains provisional and Stage 2 is not started.
