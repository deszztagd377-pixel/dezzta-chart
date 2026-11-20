# Work Cycle 2026-11-20 — Batch 62J-48 exact-head WebSocket CI and indicator reconciliation

**Branch:** `phase-2/market-data-foundation`  
**Parent source/test HEAD:** `0d548aa398cf3efb7952b65e2fb9723e330ddeb6`  
**Scope:** finish repository-side WebSocket ticket regression verification; reconcile Gate 10 and indicator progress; zero-cost only.

## 1. Exact-head CI result

All three workflows completed successfully on the same exact HEAD:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests & Build | [44755071944](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44755071944) | **SUCCESS** |
| CodeQL (JavaScript/TypeScript + Python) | [44755071870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44755071870) | **SUCCESS** |
| Full Git History Secret Audit | [44755071865](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44755071865) | **SUCCESS** |

Verified from the completed CI job log:

- Frontend: **245 tests passed across 29 test files**.
- Backend: **1,202 passed, 6 warnings in 44.40 seconds**.
- Frontend dependency audit: **0 vulnerabilities**.
- Backend dependency audit: **No known vulnerabilities found**.
- Frontend source/bundle secret scan: passed.
- Backend container build and Redis ACL/AOF + mounted persistent-volume smoke test: passed.
- Trivy container scan and vulnerability-report export: completed successfully. The report was uploaded as artifact `14636689364`; this cycle does not claim a zero-vulnerability count because the JSON report was not parsed here.
- Android host preflight and immutable preview publisher tests ran in CI and passed. This is CI-host evidence, not a test on the owner's Android device.

## 2. WebSocket ticket regression work now verified

The two test-only commits after the prior checkpoint are:

1. [e89501b](https://github.com/deszztagd377-pixel/dezzta-chart/commit/e89501b98af7082e170abfc4859e5db4aaa0d62c) — three in-memory ticket-store tests:
   - single-use consumption and subject binding;
   - expiry at the exact TTL boundary;
   - wrong-purpose ticket is consumed and cannot later be reused.
2. [0d548aa](https://github.com/deszztagd377-pixel/dezzta-chart/commit/0d548aa398cf3efb7952b65e2fb9723e330ddeb6) — one API regression test:
   - authenticated WebSocket receives a renewal ticket;
   - canonical-instrument entitlement is revoked before renewal;
   - renewal is denied and the socket closes with **4403**.

Prior repository coverage at Batch 62J-47 also verifies that a ticket issued to account B cannot renew account A's connection; the server rejects it with **4401**.

### Security properties covered by repository evidence

- Ticket TTL is 90 seconds in the production contract.
- Ticket is random, single-use, subject-bound and purpose-bound.
- Ticket material is stored as a digest rather than the raw ticket in the in-memory store.
- Renewal requires the same verified account subject.
- Instrument entitlement is rechecked on renewal.
- The in-memory store is development/test only; production uses the shared Redis guard.

### Remaining Gate 20 acceptance — cannot be closed by more mocked tests

1. Real Firebase project: valid signed ID token and correct issuer/audience/project.
2. Expired and revoked Firebase session behavior through the real Firebase Admin verifier.
3. Real entitlement-denial flow for an account without the selected canonical instrument entitlement.
4. Browser client: HTTPS ticket exchange, WSS authentication, renewal and reconnect.
5. Android client: same authenticated flow on the actual target device.
6. No-billing configuration must be verified before enabling any Firebase project integration. Do not enable billing/Blaze or introduce a paid dependency.

**Decision:** repository-side ticket regression work is complete for this batch. Gate 20 remains **OPEN** until real identity/client acceptance is performed. No further test-only commits should be added without a newly identified untested boundary.

## 3. WebSocket boundary and blocker classification

- Automated WebSocket failure-matrix scope E remains complete as previously documented.
- Gate 20 is distinct from WebSocket transport reliability: identity/session and client acceptance are still outstanding.
- Gate 25/36 still require owner-controlled Redis TLS/ACL/persistence and public WSS/browser/Android acceptance.
- Public cross-network operation remains blocked by the absence of a demonstrated zero-cost, owner-controlled always-on host and reachable network path. APK sideloading does not provide a backend.
- Do not deploy to Vercel/Cloudflare, use tunnels as a substitute for production hosting, or purchase hosting/data services to bypass the blocker.

## 4. Complete indicator progress — unchanged

| Indicator / subsystem | State | Verified foundation | First valid output | Remaining work |
|---|---|---|---:|---|
| SMA 20 | 🟨 Foundation | Rolling arithmetic mean of 20 closes | Index 19 | Chart overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21 | Index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI 14 (Wilder) | 🟨 Foundation | Wilder-smoothed gains/losses | Index 14 | 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing, render tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; EMA9 signal; histogram difference | MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, render tests |
| Bollinger Bands 20,2 | 🟨 Foundation | SMA20 ± 2 population standard deviations | Index 19 | Upper/middle/lower overlay, toggle, legend/current values, stale clearing, render tests |
| Shared indicator hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Snapshot-dependent | Active chart identity/timeframe binding, loading/error states, stale-result clearing, cross-series isolation |
| Footprint | 🟧 Gated | Deterministic educational accumulator; explicitly SIMULATED | Candle/price-level dependent | Owner reference image, reviewed blueprint, ON-only spaced cluster renderer, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | No verified implementation/data contract | N/A | Owner reference image, reviewed blueprint, source/calculation contract, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No validated data/calculation contract | N/A | Data-source feasibility, owner reference/blueprint, calculations, renderer and tests |

### Indicator correctness contracts

- **SMA20:** first valid output at candle index 19; 20-close rolling arithmetic mean.
- **EMA20:** α = 2/21, seeded from the initial 20-period SMA; first valid output index 19.
- **RSI14:** 14 close-to-close changes initialize average gain/loss; Wilder smoothing thereafter; first valid output index 14.
- **MACD12/26/9:** MACD first valid index 25; signal and histogram first valid index 33.
- **Bollinger20,2:** middle = SMA20; upper/lower = middle ± 2 × population standard deviation; first valid output index 19.
- Warm-up positions must remain null/unavailable, not zero.
- Indicator arrays must remain aligned to candle indexes.
- Symbol, venue, dataset, timeframe and chart identity changes must invalidate stale results.
- Footprint OFF must preserve ordinary candle layout and spacing; only explicit ON may activate the spaced cluster layout.
- Footprint/Heatmap visual work remains gated on the user's reference images and a reviewed scoped blueprint.

No indicator formula, calculation, chart renderer, control or runtime source changed in this work cycle. The WebSocket CI result does not award indicator progress.

## 5. Project progress and gate dashboard

**Color legend:** 🟩 accepted/verified for stated scope • 🟨 foundation/partial • 🟧 open/gated • 🟥 not implemented • ⬜ unscored.

| Measure | Current state | Evidence/accounting |
|---|---|---|
| Official stage | 🟧 Stage 1 — Foundation, Security & Data Integrity | Stage 2 is not active; branch name does not change official stage |
| Stage 1 | 🟨 75% provisional | 30/40 criteria = 300/400 ticks; no new tick |
| Gate 10 | 🟧 0/10 closed | All ten external gates remain open |
| Gate 8 | 🟧 OPEN | Owner-host secret injection/permissions/rotation evidence |
| Gate 20 | 🟧 OPEN | Real Firebase session + browser/Android reconnect acceptance |
| Gate 25 | 🟧 OPEN | Owner-controlled Redis TLS/ACL/persistence/outage recovery |
| Gate 30 | 🟧 OPEN | Restore drill on intended owner-controlled host |
| Gate 31 | 🟧 OPEN | Off-host encrypted artifact and separate recovery-key custody |
| Gate 34 | 🟧 OPEN | Actual host volume, restart and disk-pressure evidence |
| Gate 35 | 🟧 OPEN | Owner-host HTTPS endpoint and certificate validation |
| Gate 36 | 🟧 OPEN | Public WSS/browser/Android, platform lifetime and cross-instance evidence |
| Gate 38 | 🟧 OPEN | Protected host collector/dashboard, retention and disk-pressure evidence |
| Gate 39 | 🟧 OPEN | Operator acknowledgement/escalation and observed recovery drill |
| Stages 2–6 | ⬜ Unscored | Prior stage acceptance not complete |
| Overall project | ⬜ Not established | M1–M8 weights/denominator not approved |
| Indicator aggregate | ⬜ Not established | No approved indicator weights/denominator |

## 6. Next work-cycle order — avoid circular WebSocket churn

1. Keep Gate 20 at repository-complete / external-acceptance-open; do not add redundant tests without a new uncovered condition.
2. Audit Gate 8/38/39 source and test boundaries together; prioritize safe, testable code-side gaps that do not require external credentials or host access.
3. Reconcile Gate 30/31/34 owner-host runbooks and identify exactly which proof can be produced on existing hardware without cost.
4. Keep Gate 25/35/36 external network/host requirements blocked until a genuine zero-cost owner-controlled route is demonstrated.
5. Maintain the indicator ledger; do not start Stage 4 UI implementation during Stage 1 and do not fabricate indicator percentages.

## 7. Change boundary

This batch is documentation-only. Runtime source and test files are unchanged. No package install, Termux command, Firebase credential, provider feed, deployment, tunnel, paid service, Vercel/Cloudflare action, or `main` modification occurred.

