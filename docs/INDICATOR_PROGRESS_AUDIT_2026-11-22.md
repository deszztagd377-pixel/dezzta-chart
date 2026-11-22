## Batch 62J-123 — exact-head CI and indicator reconciliation (22 November 2026) — exact-head WebSocket CI, artifact and runtime-boundary audit (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Audited exact HEAD:** 4c3e9f9f4cd8317c5cd03357b51aae06d289a804  
**Automated Tests [run 44984396895](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895): SUCCESS**; **CodeQL [run 44984396918](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396918): SUCCESS**; **Full Git History Secret Audit [run 44984396926](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396926): SUCCESS**. All three runs target the exact audited HEAD.

### CI evidence and limitations
- Frontend: 29 Vitest files, 255 tests passed.
- Backend: 1,294 passed, 1 skipped. The skipped test was the real Redis TLS/shared-guard integration test because REDIS_TEST_URL was not configured. The workflow's separate container smoke did exercise a CI Redis instance; this does not turn the skipped integration case into a pass.
- Container smoke passed: health endpoint, Redis ACL authentication, AOF data surviving Redis restart, fail-closed API behavior during Redis outage, backend reconnection, non-root UID/GID 10001, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection.
- Trivy report artifact [14739352623](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739352623) was independently inspected. Exact image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, image digest sha256:28fc78838f596968e3825ac2f46ffd3a1c7b688e029c62b53fcad2cd8bc09f85, reported **0 vulnerabilities** in Alpine OS and Python package result groups. Image size: 571,350,016 bytes (~571 MB). This is point-in-time scanner output for this exact amd64 image and database, not a permanent guarantee and not ARM64 evidence.
- Synthetic outbox artifact [14738863888](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14738863888): 1,000 synthetic bars/events; persist p95 2.655 ms; concurrent replay-page p95 1.305 ms with two reader threads. Local single-process SQLite microbenchmark only, not a real provider or WebSocket load/SLO test.
- Synthetic metrics collector artifact [14739436712](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739436712): 899 logical series; one thread 32/32 flushes, 0 retries, p95 flush 8.10 ms; four threads 128/128, 2 retries, p95 flush 112.97 ms and writer-lock p95 105.38 ms; 16 threads 512/512, 65 retries, p95 flush 350.53 ms and writer-lock p95 315.97 ms; four independent processes 128/128, 1 retry, p95 flush 60.23 ms; staggered 16-worker case 512/512, 0 retries. SQLite integrity was ok in all reported cases. This demonstrates contention in concurrent same-host SQLite workloads, but is not a production host or multi-host benchmark. Do not infer multi-worker capacity or SLO from it.

### WebSocket runtime boundary audit
- Source and gateway runtime factories remain explicitly injected into separate ASGI app roles. The app rejects simultaneously injecting both roles into one instance.
- Production settings require Redis TLS URL and Firebase project ID; the shared guard is mandatory in production. The non-production in-memory ticket store is not production acceptance.
- Source publisher activation requires a host-supplied snapshot verifier callback. Its evidence must bind source ID, stream key, generation, cursor, SHA-256 and one matching installation receipt per required gateway. The callback remains a trust boundary: the owner must independently verify snapshot bytes and authenticate each receipt; repository shape validation cannot probe remote gateways.
- Gateway activation requires an owner-supplied snapshot installer and validates its returned metadata against the durable local replica checkpoint before creating the Redis client/consumer. This does not independently establish remote source authenticity; owner transport and evidence custody remain external.
- Replica worker obtains a generation-scoped lease before group access, ensures group readiness before serving, and runs one sequential consumer per replica identity. Existing lease and consumer code fail closed on unverifiable/lost ownership, apply-before-ACK, reclaim pending messages, and require resnapshot on history gaps.
- No source change was made in this batch. These are source-review findings, not new runtime acceptance tests.

### Production disposition
Public hostname/TLS/reverse proxy, real Firebase signed-token and entitlement E2E, owner-host Redis ACL/secret rotation/persistence/failover, authenticated global snapshot receipts, public browser WSS and Android WebView lifecycle evidence remain absent. Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. CI container Redis and ephemeral volume evidence does not close owner-host gates.

### Indicator ledger reconciliation
Compare from indicator implementation baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 through 4c3e9f9f4cd8317c5cd03357b51aae06d289a804 contains documentation paths only; no indicator calculation, hook, renderer, UI, formula or indicator test implementation changed. Therefore this batch awards **zero indicator implementation progress**. Keep SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook at 🟨 foundation; Footprint 🟧 simulated/reference-gated; Heatmap and Liquidation Maps 🟥 not implemented. No aggregate percentage without approved weights/denominator. Footprint/Heatmap visual work remains blocked on user references and reviewed blueprint; Footprint OFF preserves ordinary candle spacing.

### Cost and change boundary
Documentation-only update. No deployment, host, resource, provider, paid service, account or credential was created or used. No main-branch changes, no device/Termux work, and no runtime or test files modified. ZERO COST maintained.

**Next safe sequence:** finish exact-head evidence review; design a zero-cost ARM64 build/smoke verification separately from amd64; retain the SQLite concurrency warning; and keep production gates open until owner-controlled evidence exists.
---
## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).

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

# DEZZTA CHART — Indicator Progress Audit and Acceptance Register

**Audit date:** 22 November 2026  
**Audited source/test baseline:** `0074f1d0b0e421f32800294742f92d9bc9c8a2c6`  
**Branch:** `phase-2/market-data-foundation`

## Batch 62J-117 — exact-head CI and indicator ledger reconciliation (22 November 2026)

**Verified branch HEAD:** `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02` (`phase-2/market-data-foundation`). The source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains valid: GitHub comparison from that baseline to this HEAD contains documentation-only changes, with no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source changes.

**Exact-head workflows on `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02`:**
- Automated Tests [run #1952 / 44981803844](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844): **SUCCESS**; all 61 reported workflow steps completed successfully, including frontend tests/build, backend tests, Redis TLS CA/hostname fixture, backend container build, persistent-volume Redis smoke test, image scan/report and dependency audits.
- CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808): **SUCCESS**.
- Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851): **SUCCESS**.
- These are exact-head repository CI/security results. They do not constitute production Firebase, owner-host Redis, public WSS, browser or Android WebView acceptance.

**Indicator disposition — unchanged, zero progress credit:** SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 (synthetic/reference-gated), Heatmap 🟥, Liquidation Maps 🟥. The five calculation foundations and their first-valid indices remain as recorded in the canonical audit; none is accepted as a finished visible chart feature. The chart integration, controls, legends/current values, pane/overlay rendering, stale-series clearing and lifecycle/render acceptance remain outstanding as listed per study. Footprint OFF must preserve ordinary candle spacing; only explicit ON may switch to spaced clusters. Footprint, Heatmap and Liquidation Maps visual work remains gated by user-provided reference image(s) and reviewed blueprint.

**Accounting:** no indicator or project completion credit is awarded by WebSocket CI or this documentation reconciliation. Aggregate indicator percentage remains unscored without approved weights and denominator. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed. Gates 20, 25 and 36 remain open for real Firebase/entitlement evidence, owner-host Redis TLS/ACL/persistence/recovery and public HTTPS/WSS proxy plus browser/Android acceptance. No deployment or production readiness is claimed.

**Cost/scope:** ZERO COST. No paid hosting/provider, OCI provisioning, credentials, deployment, Termux/device action or `main` modification.


> **Current conclusion:** SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and the shared indicator hook have tested calculation/data foundations, but none is a completed user-facing chart feature. Footprint is an offline educational simulation only. Heatmap and Liquidation Maps are not implemented. Aggregate indicator percentage is unscored because approved weights and a completion denominator do not exist.

## 1. Status vocabulary

| Status | Meaning |
|---|---|
| 🟩 Accepted | Formula/data contract, user-facing behavior, lifecycle, tests and applicable acceptance evidence all meet the agreed scope |
| 🟨 Foundation | Calculation or shared-data foundation exists and has tests; user-facing integration or acceptance remains |
| 🟧 Gated / partial | Limited prototype or simulation exists, or implementation is blocked by explicit owner/reference/roadmap prerequisites |
| 🟥 Not implemented | No implementation is verified in the audited source tree |
| ⬜ Not assessed | Evidence is insufficient to assign a completion state |

No study in this audit is 🟩 Accepted as a finished chart feature. A passing unit test proves only the tested calculation or contract; it does not prove rendered UI, live data, mobile behavior or production acceptance.

## 2. Canonical indicator matrix

| Study / subsystem | Status | Existing implementation | First valid output / source | Remaining work |
|---|---|---|---|---|
| SMA 20 | 🟨 Foundation | Rolling arithmetic mean of 20 closes | Candle index 19 | Overlay, independent toggle, legend/latest value, identity transitions, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | EMA seeded by first 20-close SMA; alpha = 2/21 | Candle index 19 | Overlay, independent toggle, legend/latest value, identity transitions, render/lifecycle tests |
| RSI 14 Wilder | 🟨 Foundation | Close-to-close gains/losses; initial 14-change averages then Wilder smoothing | Candle index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, identity transitions, render/lifecycle tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal over valid MACD values; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, two lines, histogram, zero guide, toggle, legend/latest values, identity transitions, render tests |
| Bollinger 20,2 | 🟨 Foundation | 20-close mean ± 2 × population standard deviation | Candle index 19 | Upper/middle/lower overlay, toggle, displayed values, identity transitions, render tests |
| Shared market-indicator hook | 🟨 Foundation | Reads shared validated snapshot and calculates five studies | Only non-empty backend bars in ready/degraded state | Dedicated hook tests, chart binding, loading/error lifecycle, stale clearing, per-series isolation, renderer integration |
| Footprint | 🟧 Simulation only / gated | Offline bounded accumulator for synthetic events; provenance SIMULATED | Synthetic event-time bucket and integer price tick; not exchange data | Owner reference, reviewed blueprint, validated source contract if live data proposed, explicit toggle, ON-only spaced clusters, OFF-layout regression, interaction/performance/lifecycle tests |
| Heatmap | 🟥 Not implemented | No implementation found in audited source tree | No validated source or calculation | Owner reference, zero-cost source feasibility, validated data contract, reviewed blueprint, renderer, legend/scale, toggle and tests |
| Liquidation Maps | 🟥 Not implemented | No implementation found in audited source tree | No validated source or calculation | Zero-cost source feasibility, validated calculation/data contract, owner reference/blueprint, renderer, scale/legend, toggle and tests |

## 3. Formula and numerical contracts

All five calculations consume the `close` values of the exact selected OHLCV series. Result arrays retain source length and index alignment. Warm-up entries are `null`, not zero, and are never shifted left.

### SMA 20

[
SMA_{20}(t)=\frac{1}{20}\sum_{i=0}^{19}C_{t-i}
]

First valid result: index 19. The implementation uses normalized/stable mean arithmetic to reduce intermediate overflow and cancellation loss.

### EMA 20

The first EMA value is seeded with the arithmetic mean of the first 20 closes. Thereafter:

[
EMA_t=\alpha C_t+(1-\alpha)EMA_{t-1},\qquad \alpha=\frac{2}{21}
]

First valid result: index 19. Do not silently change this seed convention.

### RSI 14 — Wilder

Let (Delta_t=C_t-C_{t-1}), (G_t=\max(Delta_t,0)), and (L_t=\max(-Delta_t,0)). Initial average gain/loss uses the first 14 price changes. Subsequent values use Wilder smoothing:

[
AG_t=\frac{13AG_{t-1}+G_t}{14},\qquad
AL_t=\frac{13AL_{t-1}+L_t}{14}
]

[
RSI_t=100-\frac{100}{1+AG_t/AL_t}
]

First valid result: index 14 because 14 close-to-close changes require 15 closes. Explicit edge semantics: no loss with positive gain gives 100; no gain with positive loss gives 0; both zero (flat series) gives 50. The ratio is normalized for large finite magnitudes.

### MACD 12/26/9

[
MACD_t=EMA_{12}(C)_t-EMA_{26}(C)_t
]

MACD first exists at index 25, when EMA26 is first valid. The signal is EMA(9) seeded over the first nine valid MACD values. Signal and histogram first exist at index 33:

[
Histogram_t=MACD_t-Signal_t
]

MACD, signal and histogram have separate nullable fields; a valid MACD value does not imply the signal/histogram are ready.

### Bollinger Bands 20,2

The middle band is the 20-close mean. Deviation uses **population** variance (division by 20), not sample variance:

[
Upper_t=Mean_{20,t}+2\sigma_{population,t},\qquad
Lower_t=Mean_{20,t}-2\sigma_{population,t}
]

All three bands first exist at index 19. The implementation normalizes values before variance calculation and rejects non-finite results.

### Shared numerical safety

- Periods must be positive safe integers; MACD fast period must be smaller than slow period.
- Non-finite inputs and non-finite intermediate/output values are rejected.
- Bollinger deviation multiplier must be finite and non-negative.
- Warm-up is explicitly nullable.
- Extreme finite values, cancellation and representable-mean boundaries have regression tests.
- Prefix-causality tests compare each study on historical prefixes with the same prefix of a full-series calculation. Future candles must not alter earlier outputs.

## 4. Data lineage and lifecycle

Required lineage:

`validated instrument catalog + selected timeframe`
→ `authenticated backend snapshot/stream`
→ `protocol and exact-series validation`
→ `marketDataStore`
→ `CandlestickChart` and `useMarketIndicators()`
→ `indicator calculations`.

The audited store identity includes provider, series type, dataset, publisher ID, instrument ID, raw symbol, timeframe, bucket policy and calendar identity/version. The store validates chronological OHLCV boundaries, freezes published snapshots/bars, and refuses non-empty bars in demo/loading/unavailable/error states. The hook exposes identity, status, source, revision and calculated arrays. It returns no indicator arrays unless source is backend, status is ready/degraded and bars are non-empty.

**Integration distinction:** the hook exists, but `CandlestickChart.tsx` at the audited baseline does not import or call `useMarketIndicators()`. The chart creates one candlestick series. No indicator overlay, oscillator pane, toggle or legend is wired into current chart UI. This is a data/calculation foundation, not completed chart integration.

Required lifecycle behavior:
1. Consume only the exact validated backend snapshot for the selected canonical instrument/timeframe; never calculate from DEMO candles.
2. Clear plotted values immediately on instrument, provider/venue, dataset, timeframe, bucket-policy/calendar identity changes and loading/unavailable/error/empty states.
3. Preserve source candle index/timestamp alignment when filtering nullable warm-up points.
4. Preserve toggle preference across refresh only for the same valid identity; never retain plotted values across identity changes.
5. Snapshot replacement and historical corrections require an ordered full-series update; incremental updates only when revision/timestamp continuity is proven.
6. No future-candle repaint: value at index (t) may depend only on bars through (t).
7. Gaps, invalid bars and unavailable values must never be silently replaced with zero.

## 5. Visual acceptance scope

### Price pane — proposed default OFF
- SMA20: one overlay line.
- EMA20: one overlay line.
- Bollinger20,2: upper, middle and lower overlay lines.
- Each has an independent accessible toggle and legend/latest-value display.
- During warm-up, show a neutral waiting state rather than a fabricated value.

### Oscillator panes — proposed default OFF
- RSI14: separate 0–100 pane with 30 and 70 guides.
- MACD12/26/9: separate pane with MACD and signal lines, histogram and zero guide.
- Verify pane/series APIs against the exact installed Lightweight Charts v5 dependency and lockfile; do not guess method signatures.

### Cross-cutting acceptance
- Each toggle controls only its own series.
- Initial OFF state preserves the current candlestick-only experience.
- Toggling does not corrupt candle spacing, scale, viewport, crosshair, resize or cleanup.
- Narrow mobile layouts remain usable; labels remain readable.
- Controls are keyboard operable and expose accessible names/state.
- Instrument/timeframe change clears stale series before new validated bars arrive.
- Snapshot replacement, newest-bar update, historical correction, reconnect and empty/error transitions are covered by integration tests.
- Performance is measured on maximum retained history and a representative mobile viewport.
- No trading signals, order execution, broker integration or buy/sell recommendations are in scope.

## 6. Footprint / Heatmap / Liquidation Maps constraints

### Footprint

`src/education/simulatedFootprint.ts` is an offline educational accumulator. It groups synthetic events by event-time interval and integer price tick, separates buy/sell/unknown quantities, calculates delta only as buy volume minus sell volume, rejects duplicate IDs and invalid quantities/timestamps, and fails closed at bounded event-ledger capacity. Snapshots carry `dataOrigin: 'SIMULATED'`.

It is **not** a provider adapter, exchange-native bid/ask feed, aggressor-side classifier or production order-flow engine. Never label synthetic cells as live market truth.

Mandatory layout:
- Footprint OFF: ordinary chart layout and candle spacing remain unchanged.
- Only explicit Footprint ON may switch to a dedicated spaced-candle/cluster layout.
- ON layout reserves enough horizontal space for readable bid/ask cells; OFF must not inherit cluster spacing.
- Obtain the owner's preferred Footprint reference image and approve a scoped blueprint before visual implementation.

### Heatmap

No implementation is verified. Before work: owner reference, zero-cost source feasibility, explicit data definition/provenance, calculation contract, scoped blueprint, then renderer/legend/scale/toggle and tests. Do not fabricate liquidity, order-book depth or heat values.

### Liquidation Maps

No implementation is verified. Before work: zero-cost source feasibility, explicit validated calculation/data contract and provenance, owner reference/blueprint, then renderer/scale/legend/toggle and tests. Do not fabricate liquidation prices, leverage clusters or exchange liquidation events.

## 7. Roadmap and authorization gates

- Official roadmap has six stages. Project remains **Stage 1 — Foundation, Security & Data Integrity**; branch name does not change official stage.
- Visible indicator controls, overlays and oscillator panes belong to **Stage 4 — Indicators & Analytics**. Do not implement them during Stage 1.
- The separate 40% overall-project milestone permits scoped blueprint preparation/review; it does not authorize skipping stages or starting Stage 4 early.
- Footprint and Heatmap visuals remain reference-gated. Liquidation Maps require validated source/formula and reviewed reference/blueprint.
- Stage 1 is 30/40 = 75% provisional. This is not indicator progress and does not authorize Stage 4.
- No aggregate indicator percentage until owner-approved per-study weights and completion denominator exist. Counting formulas, tests, UI checkboxes or commits as equal units misrepresents completion.

## 8. Verified source and test evidence

Audited files:
- `src/indicators/indicatorCalculations.ts`
- `src/indicators/indicatorCalculations.test.ts`
- `src/indicators/useMarketIndicators.ts`
- `src/services/marketDataStore.ts`
- `src/services/useMarketDataSnapshot.ts`
- `src/components/CandlestickChart.tsx`
- `src/components/CandlestickChart.lifecycle.test.tsx`
- `src/education/simulatedFootprint.ts`
- `docs/INDICATOR_DATA_ARCHITECTURE.md`
- `docs/INDICATOR_UI_BLUEPRINT.md`

Evidence at baseline:
- Calculation test file contains **15 test cases**: alignment/warm-up, RSI edge cases, MACD warm-up, population deviation, common entry point, timeframe fixtures, invalid inputs, prefix causality, period-one/falling RSI, extreme numeric values, stable RSI ratios, overflow-safe SMA means, Bollinger extremes and cancellation residuals.
- Frontend CI: **255/255 tests across 29 files**. These are not 255 indicator tests.
- Backend CI: **1,294 passed, 1 skipped**. Backend tests do not close chart indicator acceptance.
- Automated Tests [44980548455](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548455): SUCCESS.
- CodeQL [44980548587](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548587): SUCCESS.
- Full Git History Secret Audit [44980548469](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548469): SUCCESS.
- Container build, Redis TLS/AOF and persistent-volume smoke, container scan/report export and dependency audits passed. These are infrastructure checks, not indicator visual acceptance.
- No dedicated `useMarketIndicators` test file was found.
- Chart lifecycle tests cover browser online/offline/visibility/cleanup, not indicator rendering/toggles.
- Timeframe fixture loops do not prove live/provider-backed availability for every interval.

## 9. Next work, in correct order

1. Keep this audit and ledger synchronized whenever indicator source, data contract, renderer, tests or roadmap gates change.
2. While Stage 1 remains active, do not start Stage 4 visual implementation. At a permitted design-review gate, obtain owner approval before implementation.
3. Once Stage 4 is authorized, add dedicated hook/identity/status transition tests; then implement SMA/EMA/Bollinger overlays and RSI/MACD panes in separately reviewable slices.
4. Verify exact installed Lightweight Charts v5 APIs before writing chart-series/pane code.
5. Implement independent controls, accessible legends/current values, stale-series clearing and mobile layout; run exact-head CI and visual/browser acceptance.
6. Keep Footprint, Heatmap and Liquidation Maps as separate reference/data-contract projects; do not bundle them into the basic indicator rollout.

## 10. Explicit non-claims

This audit does not claim live exchange data, validated support for every timeframe, visible indicator UI, mobile-device visual acceptance, trading accuracy, production deployment, or completion of any indicator. This is documentation-only and awards **zero implementation progress credit**.

**Cost boundary:** Rp0. No paid provider, hosting, domain, deployment, credentials, device action or `main` modification.

## Batch 62J-123 — exact-head SQLite concurrency fix, CI artifacts and acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact tested source/test HEAD:** 589aceadd40b3b3e10e950566081101b2dd49003  
**Automated Tests [run 44985059074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074): SUCCESS**; **CodeQL [run 44985059102](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059102): SUCCESS**; **Full Git History Secret Audit [run 44985059070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059070): SUCCESS**. All three workflows target the exact tested HEAD. Automated Tests completed all 36 job steps with no failed steps.

### CI and artifact evidence
- Frontend unit tests/build, source and production-bundle credential scans, Android host preflight, backend dependency audit/tests, isolated Redis TLS CA/hostname fixture, synthetic SQLite outbox and metrics benchmarks, backend image build, shared-Redis/persistent-volume container smoke, Trivy scan/report export and dependency-audit enforcement all completed successfully.
- Synthetic metrics artifact [14739815366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739815366): full 899-series envelope. One worker: 32/32 flushes, 0 retries, p95 flush 14.34 ms. Four threads: 128/128, 4 retries, p95 flush 46.92 ms. Sixteen simultaneous threads: 512/512, 187 retries, p95 flush 627.74 ms and writer-lock p95 572.23 ms. Four independent processes: 128/128, 3 retries, p95 flush 141.71 ms. Startup-staggered 16-worker case: 512/512, 26 retries, p95 flush 266.53 ms and writer-lock p95 250.93 ms. SQLite integrity reported ok for every case.
- The benchmark confirms no lost flushes in these synthetic cases and exposes material same-file SQLite writer contention at higher concurrency. It is runner/filesystem-specific, uses synthetic operational counters, and is not production load, persistent-volume, multi-host or SLO evidence. Do not infer production capacity from it.
- Synthetic outbox artifact [14739423041](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739423041) is attached to this exact run; it remains local synthetic benchmark evidence, not live provider/WebSocket load acceptance.
- Trivy artifact [14739224531](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739224531) was independently inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, architecture amd64, digest sha256:5240158d55f11863aa41a49fbf4d00705d437519fcbdb0659164efc435ee58c0, size 571,352,064 bytes (~571.35 MB). The report contains 0 vulnerabilities in the scanned Alpine OS and Python package result groups. This is a point-in-time result for this exact amd64 image and scanner database, not a permanent guarantee, not a scan of every possible target, and not ARM64 evidence.
- Backend and frontend exact-head CI success proves the repository's configured tests and CI service topology only. The CI Redis fixture and ephemeral runner volume do not constitute owner-host acceptance.

### SQLite corrective change and remaining risk
- Commit 529031d3a6ae0d07cfcd2f38a5d7e02fffd81063 adds bounded retry for lock-only errors while applying connection-local PRAGMA synchronous=NORMAL to fresh SQLite connections. Commit 589aceadd40b3b3e10e950566081101b2dd49003 adds a 16-independent-collector, eight-round repeated concurrent-flush regression test.
- Exact-head backend tests and full CI pass. The prior fatal database-is-locked failure at connection PRAGMA setup was not reproduced in this run.
- The benchmark still shows substantial contention at 16 simultaneous workers (187 retries). Keep the collector classified as bounded same-host best-effort telemetry; do not claim high-concurrency production readiness. A single-writer queue/aggregation redesign would be a separate scoped architecture change, not silently bundled into this fix.

### WebSocket production acceptance disposition
- Source/gateway separation, Redis Streams consumer/replay, generation-scoped leases, apply-before-ACK, pending reclaim, fail-closed ownership and snapshot/replay recovery remain repository implementation evidence. Owner-supplied source snapshot verification and gateway installation callbacks remain trust boundaries requiring independent authentication of snapshot bytes, SHA-256, generation, cursor and per-gateway receipts.
- Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI result.
- Still missing owner-controlled evidence: Gate 8 secret injection/permissions/rotation/log redaction; Gate 20 real Firebase signed-token and entitlement grant/revoke/renew E2E; Gate 25 owner-host Redis TLS/CA/hostname, ACL, persistence/restart/failover, secret rotation and authenticated global snapshot/receipt alignment; Gate 30 live DB backup/restore; Gate 31 encrypted off-host backup and independent recovery-key custody; Gate 34 persistent volume UID/GID 10001/restart/disk-pressure; Gate 35 public hostname/trusted TLS/renewal; Gate 36 public HTTPS ticket exchange/WSS proxy, browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression; Gate 38 real dashboards/retention/alerts/disk pressure; Gate 39 external alert delivery, human acknowledgement and escalation.
- No public HTTPS/WSS endpoint, production Firebase project, owner-host Redis or production storage has been provisioned or verified. CI must not be used to close these gates.

### Architecture and zero-cost constraints
- Current workflow uses plain docker build on GitHub-hosted ubuntu-latest; Dockerfile base is python:3.12-alpine3.24. Exact artifact metadata is linux/amd64. ARM64 build and runtime smoke remain unverified; no multi-platform claim is made.
- Keep Redis private with strict TLS CA/hostname verification and least-privilege ACLs. Keep HTTPS ticket exchange before WSS; Firebase ID tokens must not be put in WSS URLs or raw WebSocket auth frames. Preserve separate source publisher and gateway replica roles and exact global snapshot/watermark alignment.
- ZERO COST: no deployment, host, account, resource, paid service, trial-credit dependency, production credential, Vercel/Cloudflare operation or device/Termux action. main remains untouched.

### Indicator disposition — no implementation progress credited
Git compare from indicator implementation baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 to exact tested HEAD 589aceadd40b3b3e10e950566081101b2dd49003 shows 10 commits and 17 changed paths, of which indicator-related paths are documentation only. The only source/test changes are backend/app/metrics_collector.py and backend/tests/test_metrics_collector.py; no indicator calculation, data contract, hook, renderer, chart UI, Footprint/Heatmap implementation or indicator test changed. Therefore **zero indicator implementation progress** is awarded.

SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 simulated/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formulas, first-valid indices, candle alignment, warm-up nulls, no-future-repaint and stale-series clearing remain unchanged. Footprint OFF must preserve normal candle spacing; only explicit ON may use spaced clusters. Footprint/Heatmap visual work still requires user-provided reference images and a reviewed blueprint. No aggregate indicator percentage is assigned without approved weights and denominator.

---
## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).

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

# DEZZTA CHART — Indicator Progress Audit and Acceptance Register

**Audit date:** 22 November 2026  
**Audited source/test baseline:** `0074f1d0b0e421f32800294742f92d9bc9c8a2c6`  
**Branch:** `phase-2/market-data-foundation`

## Batch 62J-117 — exact-head CI and indicator ledger reconciliation (22 November 2026)

**Verified branch HEAD:** `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02` (`phase-2/market-data-foundation`). The source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains valid: GitHub comparison from that baseline to this HEAD contains documentation-only changes, with no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source changes.

**Exact-head workflows on `e76b6cd6c8f7380e5a10a7d4707028fa7da78a02`:**
- Automated Tests [run #1952 / 44981803844](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844): **SUCCESS**; all 61 reported workflow steps completed successfully, including frontend tests/build, backend tests, Redis TLS CA/hostname fixture, backend container build, persistent-volume Redis smoke test, image scan/report and dependency audits.
- CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808): **SUCCESS**.
- Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851): **SUCCESS**.
- These are exact-head repository CI/security results. They do not constitute production Firebase, owner-host Redis, public WSS, browser or Android WebView acceptance.

**Indicator disposition — unchanged, zero progress credit:** SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧 (synthetic/reference-gated), Heatmap 🟥, Liquidation Maps 🟥. The five calculation foundations and their first-valid indices remain as recorded in the canonical audit; none is accepted as a finished visible chart feature. The chart integration, controls, legends/current values, pane/overlay rendering, stale-series clearing and lifecycle/render acceptance remain outstanding as listed per study. Footprint OFF must preserve ordinary candle spacing; only explicit ON may switch to spaced clusters. Footprint, Heatmap and Liquidation Maps visual work remains gated by user-provided reference image(s) and reviewed blueprint.

**Accounting:** no indicator or project completion credit is awarded by WebSocket CI or this documentation reconciliation. Aggregate indicator percentage remains unscored without approved weights and denominator. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed. Gates 20, 25 and 36 remain open for real Firebase/entitlement evidence, owner-host Redis TLS/ACL/persistence/recovery and public HTTPS/WSS proxy plus browser/Android acceptance. No deployment or production readiness is claimed.

**Cost/scope:** ZERO COST. No paid hosting/provider, OCI provisioning, credentials, deployment, Termux/device action or `main` modification.


> **Current conclusion:** SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and the shared indicator hook have tested calculation/data foundations, but none is a completed user-facing chart feature. Footprint is an offline educational simulation only. Heatmap and Liquidation Maps are not implemented. Aggregate indicator percentage is unscored because approved weights and a completion denominator do not exist.

## 1. Status vocabulary

| Status | Meaning |
|---|---|
| 🟩 Accepted | Formula/data contract, user-facing behavior, lifecycle, tests and applicable acceptance evidence all meet the agreed scope |
| 🟨 Foundation | Calculation or shared-data foundation exists and has tests; user-facing integration or acceptance remains |
| 🟧 Gated / partial | Limited prototype or simulation exists, or implementation is blocked by explicit owner/reference/roadmap prerequisites |
| 🟥 Not implemented | No implementation is verified in the audited source tree |
| ⬜ Not assessed | Evidence is insufficient to assign a completion state |

No study in this audit is 🟩 Accepted as a finished chart feature. A passing unit test proves only the tested calculation or contract; it does not prove rendered UI, live data, mobile behavior or production acceptance.

## 2. Canonical indicator matrix

| Study / subsystem | Status | Existing implementation | First valid output / source | Remaining work |
|---|---|---|---|---|
| SMA 20 | 🟨 Foundation | Rolling arithmetic mean of 20 closes | Candle index 19 | Overlay, independent toggle, legend/latest value, identity transitions, render/lifecycle tests |
| EMA 20 | 🟨 Foundation | EMA seeded by first 20-close SMA; alpha = 2/21 | Candle index 19 | Overlay, independent toggle, legend/latest value, identity transitions, render/lifecycle tests |
| RSI 14 Wilder | 🟨 Foundation | Close-to-close gains/losses; initial 14-change averages then Wilder smoothing | Candle index 14 | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, identity transitions, render/lifecycle tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12 − EMA26; EMA9 signal over valid MACD values; histogram = MACD − signal | MACD index 25; signal/histogram index 33 | Dedicated pane, two lines, histogram, zero guide, toggle, legend/latest values, identity transitions, render tests |
| Bollinger 20,2 | 🟨 Foundation | 20-close mean ± 2 × population standard deviation | Candle index 19 | Upper/middle/lower overlay, toggle, displayed values, identity transitions, render tests |
| Shared market-indicator hook | 🟨 Foundation | Reads shared validated snapshot and calculates five studies | Only non-empty backend bars in ready/degraded state | Dedicated hook tests, chart binding, loading/error lifecycle, stale clearing, per-series isolation, renderer integration |
| Footprint | 🟧 Simulation only / gated | Offline bounded accumulator for synthetic events; provenance SIMULATED | Synthetic event-time bucket and integer price tick; not exchange data | Owner reference, reviewed blueprint, validated source contract if live data proposed, explicit toggle, ON-only spaced clusters, OFF-layout regression, interaction/performance/lifecycle tests |
| Heatmap | 🟥 Not implemented | No implementation found in audited source tree | No validated source or calculation | Owner reference, zero-cost source feasibility, validated data contract, reviewed blueprint, renderer, legend/scale, toggle and tests |
| Liquidation Maps | 🟥 Not implemented | No implementation found in audited source tree | No validated source or calculation | Zero-cost source feasibility, validated calculation/data contract, owner reference/blueprint, renderer, scale/legend, toggle and tests |

## 3. Formula and numerical contracts

All five calculations consume the `close` values of the exact selected OHLCV series. Result arrays retain source length and index alignment. Warm-up entries are `null`, not zero, and are never shifted left.

### SMA 20

[
SMA_{20}(t)=\frac{1}{20}\sum_{i=0}^{19}C_{t-i}
]

First valid result: index 19. The implementation uses normalized/stable mean arithmetic to reduce intermediate overflow and cancellation loss.

### EMA 20

The first EMA value is seeded with the arithmetic mean of the first 20 closes. Thereafter:

[
EMA_t=\alpha C_t+(1-\alpha)EMA_{t-1},\qquad \alpha=\frac{2}{21}
]

First valid result: index 19. Do not silently change this seed convention.

### RSI 14 — Wilder

Let (Delta_t=C_t-C_{t-1}), (G_t=\max(Delta_t,0)), and (L_t=\max(-Delta_t,0)). Initial average gain/loss uses the first 14 price changes. Subsequent values use Wilder smoothing:

[
AG_t=\frac{13AG_{t-1}+G_t}{14},\qquad
AL_t=\frac{13AL_{t-1}+L_t}{14}
]

[
RSI_t=100-\frac{100}{1+AG_t/AL_t}
]

First valid result: index 14 because 14 close-to-close changes require 15 closes. Explicit edge semantics: no loss with positive gain gives 100; no gain with positive loss gives 0; both zero (flat series) gives 50. The ratio is normalized for large finite magnitudes.

### MACD 12/26/9

[
MACD_t=EMA_{12}(C)_t-EMA_{26}(C)_t
]

MACD first exists at index 25, when EMA26 is first valid. The signal is EMA(9) seeded over the first nine valid MACD values. Signal and histogram first exist at index 33:

[
Histogram_t=MACD_t-Signal_t
]

MACD, signal and histogram have separate nullable fields; a valid MACD value does not imply the signal/histogram are ready.

### Bollinger Bands 20,2

The middle band is the 20-close mean. Deviation uses **population** variance (division by 20), not sample variance:

[
Upper_t=Mean_{20,t}+2\sigma_{population,t},\qquad
Lower_t=Mean_{20,t}-2\sigma_{population,t}
]

All three bands first exist at index 19. The implementation normalizes values before variance calculation and rejects non-finite results.

### Shared numerical safety

- Periods must be positive safe integers; MACD fast period must be smaller than slow period.
- Non-finite inputs and non-finite intermediate/output values are rejected.
- Bollinger deviation multiplier must be finite and non-negative.
- Warm-up is explicitly nullable.
- Extreme finite values, cancellation and representable-mean boundaries have regression tests.
- Prefix-causality tests compare each study on historical prefixes with the same prefix of a full-series calculation. Future candles must not alter earlier outputs.

## 4. Data lineage and lifecycle

Required lineage:

`validated instrument catalog + selected timeframe`
→ `authenticated backend snapshot/stream`
→ `protocol and exact-series validation`
→ `marketDataStore`
→ `CandlestickChart` and `useMarketIndicators()`
→ `indicator calculations`.

The audited store identity includes provider, series type, dataset, publisher ID, instrument ID, raw symbol, timeframe, bucket policy and calendar identity/version. The store validates chronological OHLCV boundaries, freezes published snapshots/bars, and refuses non-empty bars in demo/loading/unavailable/error states. The hook exposes identity, status, source, revision and calculated arrays. It returns no indicator arrays unless source is backend, status is ready/degraded and bars are non-empty.

**Integration distinction:** the hook exists, but `CandlestickChart.tsx` at the audited baseline does not import or call `useMarketIndicators()`. The chart creates one candlestick series. No indicator overlay, oscillator pane, toggle or legend is wired into current chart UI. This is a data/calculation foundation, not completed chart integration.

Required lifecycle behavior:
1. Consume only the exact validated backend snapshot for the selected canonical instrument/timeframe; never calculate from DEMO candles.
2. Clear plotted values immediately on instrument, provider/venue, dataset, timeframe, bucket-policy/calendar identity changes and loading/unavailable/error/empty states.
3. Preserve source candle index/timestamp alignment when filtering nullable warm-up points.
4. Preserve toggle preference across refresh only for the same valid identity; never retain plotted values across identity changes.
5. Snapshot replacement and historical corrections require an ordered full-series update; incremental updates only when revision/timestamp continuity is proven.
6. No future-candle repaint: value at index (t) may depend only on bars through (t).
7. Gaps, invalid bars and unavailable values must never be silently replaced with zero.

## 5. Visual acceptance scope

### Price pane — proposed default OFF
- SMA20: one overlay line.
- EMA20: one overlay line.
- Bollinger20,2: upper, middle and lower overlay lines.
- Each has an independent accessible toggle and legend/latest-value display.
- During warm-up, show a neutral waiting state rather than a fabricated value.

### Oscillator panes — proposed default OFF
- RSI14: separate 0–100 pane with 30 and 70 guides.
- MACD12/26/9: separate pane with MACD and signal lines, histogram and zero guide.
- Verify pane/series APIs against the exact installed Lightweight Charts v5 dependency and lockfile; do not guess method signatures.

### Cross-cutting acceptance
- Each toggle controls only its own series.
- Initial OFF state preserves the current candlestick-only experience.
- Toggling does not corrupt candle spacing, scale, viewport, crosshair, resize or cleanup.
- Narrow mobile layouts remain usable; labels remain readable.
- Controls are keyboard operable and expose accessible names/state.
- Instrument/timeframe change clears stale series before new validated bars arrive.
- Snapshot replacement, newest-bar update, historical correction, reconnect and empty/error transitions are covered by integration tests.
- Performance is measured on maximum retained history and a representative mobile viewport.
- No trading signals, order execution, broker integration or buy/sell recommendations are in scope.

## 6. Footprint / Heatmap / Liquidation Maps constraints

### Footprint

`src/education/simulatedFootprint.ts` is an offline educational accumulator. It groups synthetic events by event-time interval and integer price tick, separates buy/sell/unknown quantities, calculates delta only as buy volume minus sell volume, rejects duplicate IDs and invalid quantities/timestamps, and fails closed at bounded event-ledger capacity. Snapshots carry `dataOrigin: 'SIMULATED'`.

It is **not** a provider adapter, exchange-native bid/ask feed, aggressor-side classifier or production order-flow engine. Never label synthetic cells as live market truth.

Mandatory layout:
- Footprint OFF: ordinary chart layout and candle spacing remain unchanged.
- Only explicit Footprint ON may switch to a dedicated spaced-candle/cluster layout.
- ON layout reserves enough horizontal space for readable bid/ask cells; OFF must not inherit cluster spacing.
- Obtain the owner's preferred Footprint reference image and approve a scoped blueprint before visual implementation.

### Heatmap

No implementation is verified. Before work: owner reference, zero-cost source feasibility, explicit data definition/provenance, calculation contract, scoped blueprint, then renderer/legend/scale/toggle and tests. Do not fabricate liquidity, order-book depth or heat values.

### Liquidation Maps

No implementation is verified. Before work: zero-cost source feasibility, explicit validated calculation/data contract and provenance, owner reference/blueprint, then renderer/scale/legend/toggle and tests. Do not fabricate liquidation prices, leverage clusters or exchange liquidation events.

## 7. Roadmap and authorization gates

- Official roadmap has six stages. Project remains **Stage 1 — Foundation, Security & Data Integrity**; branch name does not change official stage.
- Visible indicator controls, overlays and oscillator panes belong to **Stage 4 — Indicators & Analytics**. Do not implement them during Stage 1.
- The separate 40% overall-project milestone permits scoped blueprint preparation/review; it does not authorize skipping stages or starting Stage 4 early.
- Footprint and Heatmap visuals remain reference-gated. Liquidation Maps require validated source/formula and reviewed reference/blueprint.
- Stage 1 is 30/40 = 75% provisional. This is not indicator progress and does not authorize Stage 4.
- No aggregate indicator percentage until owner-approved per-study weights and completion denominator exist. Counting formulas, tests, UI checkboxes or commits as equal units misrepresents completion.

## 8. Verified source and test evidence

Audited files:
- `src/indicators/indicatorCalculations.ts`
- `src/indicators/indicatorCalculations.test.ts`
- `src/indicators/useMarketIndicators.ts`
- `src/services/marketDataStore.ts`
- `src/services/useMarketDataSnapshot.ts`
- `src/components/CandlestickChart.tsx`
- `src/components/CandlestickChart.lifecycle.test.tsx`
- `src/education/simulatedFootprint.ts`
- `docs/INDICATOR_DATA_ARCHITECTURE.md`
- `docs/INDICATOR_UI_BLUEPRINT.md`

Evidence at baseline:
- Calculation test file contains **15 test cases**: alignment/warm-up, RSI edge cases, MACD warm-up, population deviation, common entry point, timeframe fixtures, invalid inputs, prefix causality, period-one/falling RSI, extreme numeric values, stable RSI ratios, overflow-safe SMA means, Bollinger extremes and cancellation residuals.
- Frontend CI: **255/255 tests across 29 files**. These are not 255 indicator tests.
- Backend CI: **1,294 passed, 1 skipped**. Backend tests do not close chart indicator acceptance.
- Automated Tests [44980548455](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548455): SUCCESS.
- CodeQL [44980548587](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548587): SUCCESS.
- Full Git History Secret Audit [44980548469](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44980548469): SUCCESS.
- Container build, Redis TLS/AOF and persistent-volume smoke, container scan/report export and dependency audits passed. These are infrastructure checks, not indicator visual acceptance.
- No dedicated `useMarketIndicators` test file was found.
- Chart lifecycle tests cover browser online/offline/visibility/cleanup, not indicator rendering/toggles.
- Timeframe fixture loops do not prove live/provider-backed availability for every interval.

## 9. Next work, in correct order

1. Keep this audit and ledger synchronized whenever indicator source, data contract, renderer, tests or roadmap gates change.
2. While Stage 1 remains active, do not start Stage 4 visual implementation. At a permitted design-review gate, obtain owner approval before implementation.
3. Once Stage 4 is authorized, add dedicated hook/identity/status transition tests; then implement SMA/EMA/Bollinger overlays and RSI/MACD panes in separately reviewable slices.
4. Verify exact installed Lightweight Charts v5 APIs before writing chart-series/pane code.
5. Implement independent controls, accessible legends/current values, stale-series clearing and mobile layout; run exact-head CI and visual/browser acceptance.
6. Keep Footprint, Heatmap and Liquidation Maps as separate reference/data-contract projects; do not bundle them into the basic indicator rollout.

## 10. Explicit non-claims

This audit does not claim live exchange data, validated support for every timeframe, visible indicator UI, mobile-device visual acceptance, trading accuracy, production deployment, or completion of any indicator. This is documentation-only and awards **zero implementation progress credit**.

**Cost boundary:** Rp0. No paid provider, hosting, domain, deployment, credentials, device action or `main` modification.
