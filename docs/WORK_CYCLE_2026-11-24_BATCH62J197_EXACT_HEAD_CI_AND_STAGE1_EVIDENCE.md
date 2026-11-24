# Work Cycle — 24 November 2026 — Batch 62J-197: Exact-HEAD CI closure and Stage 1 evidence reconciliation

**Repository:** deszztagd377-pixel/dezzta-chart  
**Branch:** phase-2/market-data-foundation  
**Audited commit:** 9037281341b28d3e28981c4a2d236e32891730b8  
**Protected branch:** main untouched  
**Cost posture:** ZERO COST; no paid hosting, market data, Redis, domain, observability, subscription, or publication was introduced.  
**Scope:** CI evidence reconciliation and project/indicator status documentation. No runtime source or dependency was changed.

## 1. Exact-head CI disposition

All four configured workflows ran against the exact audited SHA 9037281341b28d3e28981c4a2d236e32891730b8 and reached terminal SUCCESS:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45309250535](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45309250535) | 🟩 SUCCESS |
| CodeQL Security Analysis | [45309250548](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45309250548) | 🟩 SUCCESS — Python and JavaScript/TypeScript |
| OCI ARM64 Image Readiness | [45309250637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45309250637) | 🟩 SUCCESS |
| Full Git History Secret Audit | [45309250683](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45309250683) | 🟩 SUCCESS |

No failed workflow or failed step was reported for this exact SHA.

## 2. Automated Tests — extracted results

- Backend pytest: **1,359 passed, 1 skipped, 6 warnings** in 58.30 seconds.
- The general backend pytest invocation reports one skip for tests/test_shared_guard_tls_integration.py:22 because its TLS environment variables are intentionally scoped to a preceding dedicated workflow step. That dedicated step **did execute the same test successfully** (1 passed in 0.10s) against a TLS-only Redis listener, validating trusted CA + DNS hostname, wrong-hostname rejection, untrusted-CA rejection, plaintext downgrade rejection, ACL operations, and AOF/ACL survival across container restart. Therefore Redis TLS integration is covered by the dedicated CI fixture; the later generic-suite skip is expected and is not an unresolved TLS gap.
- Frontend unit tests: **320 passed across 34 test files**.
- Cloudflare synthetic Durable Object runtime proof: **11 passed**.
- Frontend dependency audit: **0 vulnerabilities**.
- Backend pip-audit: **No known vulnerabilities found**.
- Frontend source/bundle credential scans: pass (88 source files and 5 built output files).
- Frontend production build: pass.
- Android host preflight and immutable preview publisher tests: pass.
- Backend container build: pass.
- Trivy scan: workflow completed successfully with HIGH/CRITICAL severity enforcement (exit-code 1, ignore-unfixed false). No HIGH/CRITICAL finding caused a failure. JSON vulnerability report artifact ID: 14881874776 (19,044 bytes).
- Synthetic outbox benchmark and synthetic SQLite metrics collector benchmark: executed and uploaded. They are synthetic/local benchmark evidence only, not production provider or public WebSocket load tests.

### Backend container and Redis smoke acceptance

The Automated Tests job verified the following CI-only checks:

1. Backend container health endpoint returns status=ok, service=dezzta-chart-backend.
2. Redis ACL rejects unauthenticated access, incorrect password, and unrelated key/command access.
3. Persisted Redis ACL file survives Redis container restart.
4. AOF data survives Redis restart.
5. Backend rate-protection endpoint fails closed while Redis is unavailable.
6. Backend reconnects after Redis restart.
7. Backend runs with non-root UID/GID and mounted-volume ownership checks pass.
8. SQLite integrity and restart persistence checks pass.
9. HTTP rate-limit rejection check passes.

This is reproducible CI container evidence. It does **not** close owner-host Gate 25, Gate 34, Gate 35, or Gate 38; the CI service is not the user's persistent owner-controlled host.

## 3. Stage 1 criteria — authoritative status

The official matrix docs/STAGE_1_ACCEPTANCE_MATRIX.md contains 40 criteria. At this checkpoint, the documented provisional score remains:

- **30/40 criteria = 75% provisional**
- **300/400 ticks = 75% provisional**
- Gate 10: **0/10 formally closed**
- Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**

CI green does not close an external acceptance criterion. The remaining gates require owner-host, owner-device, production-like, encrypted off-host recovery, operational alert, or public WSS/Firebase evidence that CI cannot manufacture.

| Criterion | Remaining evidence | Status |
|---:|---|---|
| 8 | Owner-controlled no-billing secret injection; prove secrets absent from bundles, logs, build output and repository history | 🟨 External host verification |
| 20 | Real Firebase sign-in, expiry/revocation, entitlement denial and browser/Android WSS, only with verified no-billing configuration | 🟥 External / zero-cost constrained |
| 25 | Owner-controlled Redis TLS/ACL/private network/persistence/restart/failure behavior | 🟥 Owner-host verification |
| 30 | Restore drill against actual application database and fresh destination on target host/device | 🟨 Owner-host verification |
| 31 | Encrypted off-host backup, separate key custody, retention/access policy and key-recovery restore | 🟥 External verification |
| 34 | Persistent owner-controlled volume, mount/ownership/permissions/restart/disk-pressure/recovery | 🟨 Owner-host verification |
| 35 | Backend on existing owner hardware, health/startup/secret injection; public route only if no incremental charge | 🟨 Owner-host / zero-cost constrained |
| 36 | Authenticated WSS from web and Android through owner-controlled reverse proxy | 🟥 External verification |
| 38 | Owner-host metrics persistence, retention, backup/restore, disk pressure, dashboard, independent alert/acknowledgement/recovery | 🟧 External operations |
| 39 | No-incremental-cost local alert path, incident ownership/escalation and recovery procedure | 🟨 Owner/operator verification |

No criterion above is closed by this batch. No progress tick is awarded for documentation or CI repetition.

## 4. Full indicator progress ledger

The indicator aggregate is **NOT SCORED**. The calculation foundation and user-facing completion are separate deliverables.

| Indicator | Formula / parameters | First valid output (zero-based candle index) | Status | Remaining acceptance |
|---|---|---:|---|---|
| SMA20 | Arithmetic mean of the latest 20 closes | 19 | 🟨 Foundation | Chart overlay, independent toggle, legend/latest value, identity clearing, render/performance acceptance |
| EMA20 | SMA-seeded EMA; multiplier 2/21 | 19 | 🟨 Foundation | Chart overlay, independent toggle, legend/latest value, identity clearing, render/performance acceptance |
| RSI14 Wilder | Initial 14-change average; then Wilder smoothing | 14 | 🟨 Foundation | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, render/lifecycle acceptance |
| MACD12/26/9 | EMA12 − EMA26; EMA9 signal; histogram = MACD − signal | MACD 25; signal/histogram 33 | 🟨 Foundation | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, latest values, render/lifecycle acceptance |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | 🟨 Foundation | Upper/middle/lower overlays, toggle, latest values, identity clearing, render/performance acceptance |
| Shared Indicator Hook | useMarketIndicators(), shared immutable OHLCV snapshot, trust-state suppression and cached calculations | Per study warm-up | 🟨 Foundation | Stage 4 chart binding, stale clearing on identity/timeframe transitions, controls/legend/accessibility/performance |
| Footprint | Synthetic educational accumulator only | N/A | 🟧 Prototype | User visual reference, reviewed blueprint, verified bid/ask data contract, dedicated spaced-cluster renderer |
| Heatmap | No accepted depth/liquidity renderer | N/A | 🟥 Not implemented | User visual reference, reviewed blueprint, validated depth contract, renderer and acceptance |
| Liquidation Maps | No accepted calculation/renderer | N/A | 🟥 Not implemented | Defensible provenance/calculation contract, reviewed blueprint, renderer and acceptance |

### Calculation correctness constraints

- SMA20, EMA20 and Bollinger20 first produce values at index 19.
- Wilder RSI14 first produces a value at index 14.
- MACD line first produces a value at index 25; signal and histogram first produce values at index 33.
- Warm-up output remains null; it must never be fabricated as zero.
- Every output remains aligned to the original candle index/timestamp.
- Prefix causality: appending future bars must not rewrite historical outputs.
- Invalid/non-finite prices and untrusted market-data states must not produce chart values.
- Instrument/timeframe identity changes must clear stale values.
- Calculation tests do not equal chart rendering, control interaction, accessibility, or mobile performance acceptance.

### Visual implementation gates

- docs/INDICATOR_UI_BLUEPRINT.md remains **PARKED — Stage 4 preparation only**; implementation authorization is not granted during Stage 1.
- CandlestickChart still does not bind useMarketIndicators; standard indicator overlays/panes remain not integrated.
- All indicators should initially be OFF at Stage 4 unless owner review approves a different default.
- Footprint OFF must preserve ordinary candlestick spacing. Only explicit Footprint ON may switch to the dedicated spaced-candle/cluster layout.
- Footprint and Heatmap visual implementation remains blocked until the owner supplies reference image(s) and approves the scoped blueprint.
- No formula or indicator visual behavior was changed in this batch.

## 5. Official six-stage map

| Stage | Name | Status |
|---:|---|---|
| 1 | Foundation, Security & Data Integrity | 🟨 30/40 = 75% provisional; 10 external criteria open |
| 2 | Market Data Infrastructure | ⬜ NOT SCORED |
| 3 | Chart Engine & Timeframe | ⬜ NOT SCORED |
| 4 | Indicators & Analytics | ⬜ NOT SCORED |
| 5 | Professional UI & Interactive Tools | ⬜ NOT SCORED |
| 6 | Hardening, Validation & APK Release | ⬜ NOT SCORED |

**Overall project progress:** NOT SCORED. No approved weighted denominator or criterion-to-deliverable mapping supports a defensible current aggregate percentage.  
**Significant progress:** exact-head CI is now 4/4 green, backend 1,359 tests passed, frontend 320 tests passed, synthetic Worker 11 tests passed, CI container/Redis restart and fail-closed smoke passed.  
**Still materially red:** real owner-host Redis/TLS/retention, authenticated public WSS, owner-device Android lifecycle, actual backup restore and operational alert/acknowledgement.  
**Target delivery:** 24 December 2026, planning target only.  
**Cost:** ZERO COST.

## 6. Next work sequence

1. Define the Redis stream retention-floor and trim protocol as a separate least-privilege controller. Do not give XTRIM to publisher or gateway identities. Add crash/retry, concurrent replay and real Redis trim-boundary tests before enabling trim.
2. Keep the dedicated Redis TLS fixture and its separate test invocation intact. The general-suite skip is expected because the TLS variables are scoped to the dedicated step; retain this distinction in future CI reports.
3. Produce a production-host WSS acceptance path only if the existing zero-cost hosting/network plan supports durable shared state, certificates and required runtime behavior without new charges. Otherwise keep production integrations disabled and record a no-go.
4. Reconcile owner-host criteria 8, 25, 30, 31, 34, 35, 38 and 39 with actual target-host evidence; do not substitute CI for owner hardware.
5. Complete public authenticated WSS/Firebase/Android acceptance for criteria 20 and 36 only after the zero-cost configuration is verified.
6. Keep the indicator blueprint parked until Stage 4; then obtain owner approval before chart integration. Do not implement Footprint/Heatmap visuals before references arrive.

## 7. Change record

- Added only this engineering/evidence document.
- No runtime source, test source, package manifest, lockfile, credentials, deployment settings, market-data provider, hosting plan, or owner device was changed.
- main remains untouched.
