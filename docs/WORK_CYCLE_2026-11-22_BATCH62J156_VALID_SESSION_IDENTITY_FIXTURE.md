# WORK CYCLE 62J-156 — Valid session-calendar identity fixtures

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Code commit: `c2cab415506906ad5a45df8c9c925612a6a069cd`  
Delivery target: 24 December 2026  
Cost boundary: ZERO COST  
`main`: untouched

## CI finding

Automated Tests run `45021071051` completed with:
- frontend unit tests: passed;
- frontend production build: passed;
- backend tests: 1 failed, 1,298 passed, 1 skipped.

The sole failure remained in:
`test_stream_hub_rejects_updates_when_any_series_identity_dimension_differs`.

The first fixture correction fixed timeframe alignment, but the next CI run exposed an independent invalid fixture: calendar ID/version mismatches were created by changing calendar metadata on a UTC bucket policy. The OHLCV model correctly rejects exchange calendar metadata unless the bucket policy is `CME_SESSION_V1` and timeframe is session-based.

## Root cause and correction

Production validation is correct and was not weakened.

Updated `backend/tests/test_ohlcv_stream.py`:
- calendar ID mismatch fixture now uses a valid `1d` `CME_SESSION_V1` bar with `calendar_id=CME`, `calendar_version=2026a`;
- calendar version mismatch fixture uses the same valid session identity but `calendar_version=2026b`;
- the other eight identity-dimension fixtures remain independently varied;
- no invalid bar is constructed before publish;
- subscriber queue, watermark, and unsubscribe assertions remain.

The test now checks all ten exact series identity dimensions using model-valid bars:
1. dataset
2. publisher ID
3. instrument ID
4. raw symbol
5. timeframe
6. provider
7. series type
8. bucket policy
9. calendar ID
10. calendar version

This is a test-only correction. No production runtime logic, dependencies, provider credentials, paid data source, or infrastructure changed.

## Commit and verification boundary

Correction commit: `c2cab415506906ad5a45df8c9c925612a6a069cd`

A fresh Automated Tests run is required against this commit. Until it completes successfully, this correction is pending CI acceptance. Re-check CodeQL, OCI ARM64 and Secret Audit for the exact latest HEAD as well. Do not treat earlier successful runs on the parent SHA as proof for this commit.

## WebSocket progress

Verified foundations remain:
- authenticated ticket flow and exact-series subscription;
- bounded per-client queues and exact identity fan-out;
- ten-dimensional exact-series mismatch rejection regression test;
- replay/live boundary and watermark behavior;
- independent subscriber cleanup.

Open:
- frontend singleton supervisor/store prevents independent concurrent multi-chart ownership;
- backend provider lifecycle remains process/configuration scoped, not chart-demand scoped;
- dynamic upstream subscribe/unsubscribe behavior is not verified against an exact pinned SDK;
- shared upstream demand refcounting and reconnect reconciliation remain unimplemented;
- ZERO COST CME feed with app display/redistribution rights remains unverified/unavailable.

No disconnected refcount is to be implemented as a substitute for actual provider lifecycle control.

## Full indicator progress ledger

No indicator calculation, hook, renderer, or indicator-specific test changed in this work cycle. Indicator progress credit: zero.

| Indicator / subsystem | Status | Verified foundation | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 | 20-close arithmetic mean; first valid index 19; warm-up nulls and prefix causality | Calendar-aware gap handling, chart overlay, toggle, legend/latest value, lifecycle/render/performance tests |
| EMA20 | 🟨 | SMA seed; alpha 2/21; first valid index 19 | Gap handling, overlay, toggle, legend, lifecycle/render tests |
| RSI14 Wilder | 🟨 | Wilder smoothing; first valid index 14; edge-case regression tests | Gap handling, 0–100 pane, 30/70 guides, toggle, legend/render |
| MACD12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Gap handling, dedicated pane, lines/histogram/zero guide, controls |
| Bollinger20,2 | 🟨 | 20-close mean ± 2 population SD; first valid index 19 | Gap handling, three-line overlay, toggle/value display/render |
| Shared Indicator Hook | 🟨 | Backend snapshot gating and aligned calculation foundation | Per-series store, gap-aware contract, hook tests, chart binding, stale clearing |
| Footprint | 🟧 | Synthetic educational accumulator only | User visual reference, reviewed blueprint, valid bid/ask provenance and rights, renderer/acceptance |
| Heatmap | 🟥 | No accepted depth/liquidity renderer | User reference, validated data contract, reviewed blueprint, renderer |
| Liquidation Maps | 🟥 | No accepted provenance-backed calculation/renderer | Valid provenance and calculation contract, reviewed blueprint, renderer |

### Mandatory indicator invariants

- Warm-up values remain null, not zero.
- Output stays aligned to source candle indices.
- Prefix causality remains mandatory.
- Non-finite and invalid bars must not become valid observations.
- Calendar-aware gap detection must distinguish missing in-session bars from overnight, weekend, holiday and scheduled breaks.
- No guessed fixed-seconds threshold; no synthetic zero-price bars.
- Stale indicator outputs must clear on series/timeframe/calendar changes.
- Footprint OFF preserves standard candle spacing; explicit ON enables its dedicated spaced cluster layout.
- Footprint and Heatmap visual implementation remains gated on user-provided references and a reviewed scoped blueprint.

## Stage and gate dashboard

| Stage | Status |
|---|---|
| Stage 1 — Foundation, Security & Data Integrity | 🟨 30/40 = 75% provisional |
| Stage 2 — Market Data Infrastructure | ⬜ Not scored |
| Stage 3 — Chart Engine & Timeframe | ⬜ Not scored |
| Stage 4 — Indicators & Analytics | ⬜ Not scored |
| Stage 5 — Professional UI & Interactive Tools | ⬜ Not scored |
| Stage 6 — Hardening, Validation & APK Release | ⬜ Not scored |

Overall project: NOT SCORED; no approved stage weights/denominator.  
Gate 10: 0/10 external acceptance criteria formally closed. CI does not prove a public deployment, Android lifecycle acceptance, or external data rights.

## Next sequence

1. Wait for and inspect the new Automated Tests run on commit `c2cab415`.
2. If backend tests fail, inspect the exact failure and correct the invalid assumption without weakening production validation.
3. Verify all required CI workflows on the latest exact HEAD.
4. Continue the multi-chart keyed-store design and tests in a separate scoped implementation after the current CI result.
5. Keep provider demand control blocked until a real, verified provider lifecycle capability exists.

Delivery target remains 24 December 2026. No paid services or resources were introduced.
