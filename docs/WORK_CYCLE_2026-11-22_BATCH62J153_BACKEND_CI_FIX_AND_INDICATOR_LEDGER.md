# WORK CYCLE 62J-153 — Backend CI fixture correction and exact-series test isolation

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## Trigger and root cause

The previous Automated Tests run completed with:
- frontend unit tests: passed;
- frontend production build: passed;
- backend tests: 1 failed, 1,298 passed, 1 skipped;
- CodeQL: passed;
- OCI ARM64 image build and smoke test: passed;
- Secret Audit: passed.

The single backend failure was in:
`test_stream_hub_rejects_updates_when_any_series_identity_dimension_differs`.

Root cause was a malformed negative-test fixture, not a WebSocket routing defect. The test changed a one-second fixture's timeframe to `5s` while retaining a timestamp offset by one second. `OhlcvBar` correctly rejects a bar whose start timestamp is not aligned to its declared timeframe. Because object construction failed before `hub.publish()`, that case never tested routing isolation.

## Correction applied

Updated `backend/tests/test_ohlcv_stream.py`:
- timeframe mismatch now uses `make_bar(5)` before changing timeframe to `5s`, preserving valid five-second alignment;
- instrument ID mismatch now changes only `instrument_id`, leaving raw symbol unchanged, so the instrument dimension is independently tested;
- all ten exact-series identity dimensions remain covered;
- the test still verifies zero queued mismatched updates, zero watermark advancement, and clean unsubscribe.

No production runtime code changed. No dependency, provider key, account, paid service, cloud resource, or network feed was added.

## Commit

Test correction commit: `b2bf9627359f9b9d5e4aacbccd1469bcd7f05983`

Changed file:
- `backend/tests/test_ohlcv_stream.py`

The fix is a test-fixture correction only. It must not be reported as a production WebSocket feature or upstream provider-demand implementation.

## Acceptance and CI

The prior run's failure is explained by the invalid fixture above. The correction must be accepted by a fresh Automated Tests run against the corrected code commit. CodeQL, Secret Audit, and OCI ARM64 should also be checked on the resulting branch HEAD. Until the new runs finish successfully, CI status is pending and this correction is not CI-verified.

The previous run evidence:
- Automated Tests run `45020354350`: failed only at the malformed timeframe fixture; 1,298 passed, 1 skipped.
- CodeQL run `45020388466`: success.
- OCI ARM64 run `45020388457`: success.
- Secret Audit run `45020388519`: success.

OCI evidence is CI image build/smoke evidence only. It is not an OCI VM deployment, public endpoint, or installed production environment.

## WebSocket engineering status

Verified existing foundation:
- authenticated WebSocket ticket flow;
- per-client bounded queues;
- exact-series fan-out identity;
- provider and series-type isolation;
- bucket-policy and calendar identity isolation;
- same-series multi-subscriber disconnect isolation;
- replay/live boundary handling;
- overflow fail-closed behavior and resnapshot requirement.

Still open:
1. frontend singleton supervisor ownership versus multiple simultaneous chart panels;
2. backend provider ingestion lifecycle remains process/configuration scoped rather than chart-demand scoped;
3. upstream adapter dynamic add/remove semantics have not been verified against an exact pinned SDK version;
4. actual shared upstream provider refcounting and reconnect reconciliation are not implemented/verified;
5. no recurring-$0 CME source with the required exact instrument coverage and app display/redistribution rights has been approved;
6. public hostname, reverse proxy, WSS certificate, live Firebase, Android foreground/background/process-death/network-handover, and public-network acceptance remain external gates.

Do not add a disconnected reference counter or claim on-demand upstream control without a real provider lifecycle API behind it. Unsupported live series remain explicitly unavailable/demo. No scraping or repurposing personal-use quote data.

## Full indicator progress ledger

No indicator formula, hook, renderer, or indicator-specific test changed in this work cycle. Therefore indicator implementation credit for this cycle is zero.

| Indicator / subsystem | Status | Verified foundation | Remaining work / acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid candle index 19 | Chart overlay, enable/disable control, legend/latest value, symbol/timeframe lifecycle, render and performance tests |
| EMA20 | 🟨 Foundation | SMA seed; alpha = 2/21; first valid index 19 | Chart overlay, enable/disable control, legend/latest value, lifecycle/render/performance tests |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; regression coverage for mixed gain/loss | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render tests |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal and histogram first valid index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, controls, legend and render tests |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ± 2 population standard deviations; first valid index 19 | Upper/middle/lower overlay, toggle, values, lifecycle/render tests |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot and candle-index-aligned calculation foundation | Hook unit tests, chart binding, stale-result clearing, renderer integration |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator only | User-provided visual reference, scoped blueprint and review, valid bid/ask provenance/rights contract, cluster layout and acceptance |
| Heatmap | 🟥 Not implemented | No accepted runtime depth/liquidity renderer | User-provided reference, validated depth/liquidity data contract, reviewed blueprint, renderer and lifecycle tests |
| Liquidation Maps | 🟥 Not implemented | No accepted provenance-backed calculation or renderer | Defensible data provenance, validated calculation contract, reviewed blueprint, visualization and tests |

### Indicator invariants — mandatory

- Warm-up periods return null; never substitute zero.
- Every output remains aligned to the source candle index.
- Prefix causality: adding future candles cannot change prior outputs.
- Invalid, non-finite, or gapped bars cannot silently become zero or valid observations.
- Clear stale outputs on contract, venue, dataset, chart, or timeframe changes.
- Standard candlestick spacing remains unchanged while Footprint is OFF.
- Only explicit Footprint ON may activate the dedicated spaced cluster layout.
- Footprint and Heatmap visual implementation remains blocked until the user's reference image(s) are supplied and a scoped blueprint is reviewed.
- Documentation, CI, and benchmark results do not count as indicator implementation progress.

## Project stage and gate dashboard

| Stage | Status | Evidence / accounting |
|---|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 30/40 = 75% provisional | Existing verified baseline; not re-scored by this test-only correction |
| Stage 2 — Market Data Infrastructure | ⬜ Not scored | Provider demand lifecycle, rights-cleared source, dynamic adapter capability and multi-chart ownership remain open |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored | No stage acceptance calculation approved |
| Stage 4 — Indicators & Analytics | ⬜ Not scored | Indicator rendering and integration remain incomplete |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored | No approved stage denominator |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored | External device/public endpoint/release acceptance remains open |

- Overall project: NOT SCORED. Approved project weights and denominator are not defined; no fabricated overall percentage.
- Gate 10: project work is in the Gate 10 workstream, but formal external acceptance remains 0/10 closed. The remaining checklist cannot be marked complete from CI alone.
- Open external gate groups include deployment/hostname/WSS, live Firebase, Android lifecycle and public-network acceptance, replica trust/owner/key lifecycle, and persistent metrics/backup/retention/recovery.

## Significant project progress

- Exact-series routing regression now independently covers ten identity dimensions with valid OHLCV fixtures.
- The malformed fixture discovered by CI was corrected at its source.
- The failure was isolated to test construction; production routing code was left untouched.
- Prior security and ARM64 CI checks remain successful, pending fresh confirmation against the corrected HEAD.
- ZERO COST boundary remains intact.
- Delivery target remains 24 December 2026; it is a target, not a promise that external data rights or infrastructure will become free/available.

## Next engineering sequence

1. Verify the corrected backend test and full Automated Tests run.
2. Continue safe frontend multi-chart supervisor ownership audit without changing the singleton contract blindly.
3. Define provider capability states (dynamic, multiplexed, restart-required, unsupported) from verified SDK evidence.
4. Only then implement idempotent demand coordination/refcounts wired to a real provider lifecycle.
5. Keep indicator renderer work behind its existing data-contract and visual-reference gates.
