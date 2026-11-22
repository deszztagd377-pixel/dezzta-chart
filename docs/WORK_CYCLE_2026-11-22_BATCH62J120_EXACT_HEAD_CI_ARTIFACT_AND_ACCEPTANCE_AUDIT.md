# DEZZTA CHART — Batch 62J-120
## Exact-head CI closure, artifact inspection, WebSocket acceptance and indicator reconciliation

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact tested parent HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`  
**Change scope:** documentation only; no runtime source, CI workflow, indicator formula, chart renderer or UI modified.  
**ZERO COST:** no infrastructure provisioned, no paid services enabled, no trial-credit dependency, no credentials collected.

## 1. Exact-head CI closure

All three workflows for `c6cd331c5f9293093418bda31f93960f5aed1600` completed successfully:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests #1954 | [44983396146](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983396146) | SUCCESS |
| CodeQL | [44983396167](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983396167) | SUCCESS |
| Full Git History Secret Audit | [44983396142](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983396142) | SUCCESS |

The Automated Tests run completed frontend tests/build and bundle-secret scans, Android host preflight, backend tests, Redis TLS/CA/hostname fixture tests, synthetic SQLite outbox and metrics benchmarks, backend container build, shared-Redis-guard + persistent-volume container smoke test, backend dependency audit, Trivy image scan/report export, and teardown.

### Trivy report inspected

Artifact: [container-vulnerability-reports (14738792690)](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983396146/artifacts/14738792690)  
Artifact digest: `sha256:08148f95394262a6b984f29399623afdac5632d60eeefc4a0c0913b2bb8834ce`  
Scanned image: `dezzta-chart-backend:ci`  
Image digest: `sha256:200a7418ffdf6995497d9e248afb115e5cdf714996d6d181a5d9aa0032ee6dda`  
Image OS: Alpine 3.24.4  
Image architecture: **linux/amd64**

The downloaded JSON contained zero reported vulnerabilities in both scanned result groups: Alpine OS packages and Python packages. This is a point-in-time scan of this exact CI image and scanner database; it is not a permanent security guarantee, does not cover a future image, and does not establish ARM64 scan status.

## 2. WebSocket-related test evidence

The workflow verifies:
- Redis TLS-only fixture with a trusted CA and hostname verification, plus wrong-CA rejection tests.
- Redis ACL-restricted operations and AOF-backed persistence across a real test-container restart.
- Backend WebSocket/authentication and related backend test suite.
- Backend container build and a smoke test with shared Redis guard and persistent CI volume.
- Synthetic SQLite OHLCV outbox replay and concurrent reader behavior.

The outbox benchmark artifact [14738692836](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983396146/artifacts/14738692836) reports 1,000 synthetic bars/events, two concurrent reader threads, all 1,000 events replayed, p95 persist latency 4.472 ms and p95 concurrent replay-page latency 1.644 ms. The benchmark explicitly states that it is a single-process SQLite microbenchmark, not a provider, WebSocket, reconnect-storm, multi-process, production-host or SLO test.

### SQLite metrics collector stress findings

Artifact: [synthetic-metrics-collector-benchmark (14739270866)](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983396146/artifacts/14739270866)

The synthetic collector benchmark exercised the full 899 logical-series envelope. Results include:
- 1-thread case: 32 successful flushes, zero retries, SQLite integrity `ok`.
- 4-thread case: 128 successful flushes, 6 lock retries, SQLite integrity `ok`; p95 writer-lock wait 231.388 ms.
- 16-thread case: 512 successful flushes, 168 lock retries, SQLite integrity `ok`; p95 writer-lock wait 540.741 ms.
- Four separate OS-process writers: 128 successful flushes, 3 lock retries, SQLite integrity `ok`; p95 writer-lock wait 103.701 ms.
- 16-worker staggered-start case: 512 successful flushes, 33 retries, SQLite integrity `ok`; p95 writer-lock wait 266.800 ms.

These figures are local synthetic diagnostics on an ephemeral x86_64 GitHub runner. They are not production SLOs, host capacity guarantees or direct WebSocket throughput measurements. They expose real SQLite writer-lock contention under concurrency; do not claim that scaling worker count linearly improves the shared SQLite collector. Before any production multi-worker rollout, measure the intended host/storage and define a safe writer/process topology, retry budget and latency target. Do not use these CI numbers as a deployment sizing promise.

## 3. ARM64 and deployment readiness

The inspected Docker image metadata identifies `linux/amd64`. The existing CI workflow builds and smoke-tests one image on `ubuntu-latest`; it does not contain a native ARM64 build/test job or QEMU/buildx multi-platform validation. Therefore:
- OCI Ampere A1 / ARM64 compatibility remains **UNVERIFIED**.
- Alpine/Python source compatibility alone is not proof that every pinned dependency wheel/native extension and runtime behavior works on AArch64.
- No OCI host, public IP, DNS, TLS endpoint, Redis production instance or persistent volume was created.
- No public WSS endpoint or real browser/Android WebView E2E evidence exists yet.
- No resource may be provisioned until the adult account owner independently verifies Always Free eligibility, capacity and every possible charge, and explicitly authorizes it. If zero-cost ingress/hostname cannot be proven, defer public WSS.

## 4. Production acceptance status

Repository CI is green; production acceptance is still open. Required external evidence remains:
1. Gate 8: owner-host secret injection, permissions, rotation and log-redaction proof.
2. Gate 20: real Firebase project valid/expired/revoked/wrong-project token and entitlement lifecycle tests.
3. Gate 25: owner-host Redis TLS/CA/hostname, ACL, persistence, restart/failover and exact snapshot/watermark receipts.
4. Gate 30: live backend DB backup/restore and integrity readback.
5. Gate 31: encrypted off-host backup and independent recovery-key custody.
6. Gate 34: persistent volume UID/GID 10001, restart and disk-pressure validation.
7. Gate 35: verified public hostname, trusted TLS and renewal.
8. Gate 36: public WSS proxy, ticket exchange, browser/Android lifecycle, replay/resnapshot and duplicate suppression.
9. Gate 38: real dashboards, retention, alerting and disk-pressure behavior.
10. Gate 39: actual alert delivery, human acknowledgement and escalation.

Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. Stage 2 remains blocked pending formal Stage 1 exit review. Green CI does not close host/client gates.

## 5. Indicator progress reconciliation

No indicator source or test changed between the previous indicator baseline and tested parent `c6cd331c5f9293093418bda31f93960f5aed1600`. No progress is awarded from CI, security scans, benchmarks or this documentation-only update.

| Indicator/subsystem | Status | Current verified foundation | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close mean; first valid index 19 | Visible overlay, toggle, legend/current value, lifecycle and render tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha 2/21; first valid index 19 | Visible overlay and lifecycle acceptance |
| RSI14 Wilder | 🟨 Foundation | 14 close changes; first valid index 14 | Pane, 0–100 scale, 30/70 guides, toggle and lifecycle tests |
| MACD12/26/9 | 🟨 Foundation | MACD index 25; signal/histogram index 33 | Lines, histogram, zero guide, pane and lifecycle tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population SD; first valid index 19 | Three overlays, toggle, current values and lifecycle tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and aligned calculation output | Chart binding, loading/error states, stale clearing, isolation and renderer tests |
| Footprint | 🟧 Synthetic / gated | Educational synthetic accumulator only | User visual reference and reviewed blueprint before visual implementation |
| Heatmap | 🟥 Not implemented | No verified implementation | Reference, zero-cost data feasibility, blueprint, renderer and tests |
| Liquidation Maps | 🟥 Not implemented | No verified implementation | Data-source feasibility, calculation contract, blueprint, renderer and tests |

Invariants remain unchanged: exact selected OHLCV identity, index alignment, null warm-up values, no future-candle repaint, stale-series clearing on identity changes, and normal candle spacing whenever Footprint is OFF. Footprint/Heatmap visual work remains blocked on the user's reference image(s) and reviewed blueprint. No aggregate indicator percentage is assigned without approved weights and denominator.

## 6. Next zero-cost engineering sequence

1. Preserve the green exact-head baseline and reviewed scan/benchmark artifacts.
2. Prepare a separate ARM64 build + smoke-test plan; do not change CI until action pins, build method and runner constraints are inspected.
3. Design a bounded SQLite writer/process acceptance test on a representative host; define target p95/p99, retry ceiling and disk cap before changing runtime topology.
4. Collect owner-controlled production evidence only after adult owner approval and verified zero-cost eligibility.
5. Close gates individually with reproducible evidence and sign-off; do not promote stage or award indicator progress based on documentation.

**Final disposition:** CI 3/3 green at `c6cd331c5f9293093418bda31f93960f5aed1600`; Trivy report inspected with zero reported OS/Python package vulnerabilities in this amd64 image; synthetic benchmarks expose SQLite contention at higher concurrency; ARM64 and production WebSocket acceptance remain unverified; indicators remain at their previously audited foundation statuses; ZERO COST and stage boundaries preserved.
