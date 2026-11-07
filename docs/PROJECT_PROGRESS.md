# DEZZTA CHART — Progress Record

Last verified snapshot: 2026-11-05  
Repository: https://github.com/deszztagd377-pixel/dezzta-chart  
Working branch: `phase-2/market-data-foundation`  
Snapshot HEAD before this progress-history correction: `89a1738e29ad4291299a4552e7056886e0e5c4bf`  
Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1`



## Owner correction — historical conversational checkpoints (2026-11-05)

The owner clarifies the sequence of previously communicated conversational progress checkpoints: **20.3% first, then 20.9%**. The 20.9% checkpoint was celebrated as having crossed 20%; it must not be erased or silently replaced by the older 19.60% figure.

Interpretation and accounting safeguards:
- **20.3% → 20.9%** is the owner's correction of the historical conversation sequence. Preserve both values and their order.
- **19.60%** remains the older value formally recorded in PROJECT_STATUS.md; it is not evidence that the project later regressed.
- **19.9%** has no verified calculation in the current repository record and must not be presented as a valid current percentage.
- The exact milestone formula behind the conversational 20.3% and 20.9% checkpoints has not yet been recovered. Therefore 20.9% is the latest owner-confirmed conversational checkpoint, while a newly recalculated weighted percentage remains pending a reproducible ledger.
- Do not lower, raise, or average these values to manufacture a current percentage. Reconcile the milestone weights and verified deliverables first, then document any correction transparently.

## Current percentage record

| Record | Value | Meaning |
|---|---:|---|
| Last formally weighted estimate in `PROJECT_STATUS.md` | **19.60%** | Historical formal estimate; last documented increment was +0.20 percentage points from 19.40% |
| Owner-confirmed conversational sequence | **20.3% → 20.9%** | Earlier then later checkpoint, clarified by the owner; formula/evidence ledger still needs reconstruction |
| Freshly reconciled overall percentage | **Not yet established** | Do not present either historical value as a newly recalculated current percentage |

The project percentage is a weighted milestone estimate toward the intended full application. It is **not** the percentage of files written, lines of code, commits, or CI jobs completed. A documentation-only commit or a passing CI run does not automatically increase overall project completion.

## Proposed weighted ledger

A proposed eight-group, 100%-total milestone model is now available in [PROJECT_MILESTONE_LEDGER.md](PROJECT_MILESTONE_LEDGER.md). It separates visible chart capability, data contracts/persistence, security, interaction tools, educational indicators, responsive UX, settings/watchlist, and release quality. The weights are a proposal only; criterion-level scoring and owner review are still required before calculating a new overall percentage.

## Why the discrepancy remains open

The repository now contains a proposed consolidated ledger, but it has not yet been approved or scored. A reproducible final calculation still requires:
1. Defines the complete project milestone groups and their total weights (100%).
2. Defines objective acceptance criteria for each milestone.
3. Assigns completion credit only to verified deliverables, avoiding duplicate credit for the same capability across commits.
4. Separates implemented code, automated tests, user-visible behavior, deployment verification, and owner-approved design.
5. Records evidence links and the calculation used for each percentage change.

Until the proposed ledger is reviewed and scored, **19.60% and 20.9% remain historical references**, not competing freshly verified measurements. Do not choose one by guesswork and do not increase the percentage merely because more commits exist.

## Verified evidence at this snapshot

- Working branch HEAD: `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`.
- Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1`; main was not modified by the audited work.
- GitHub Actions run [42053572558](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42053572558) completed successfully on the exact working-branch HEAD.
- The CI job passed frontend dependency installation, frontend unit tests, frontend production build, backend dependency installation, backend pytest, and backend container-image build.
- The repository has no root `package-lock.json`; the current CI uses `npm install`. Reproducible frontend dependency installation remains an open quality task.
- The latest verified code audit confirms code-level authenticated frontend stream integration. It does not establish deployed backend operation, live provider delivery, synchronized exchange time, or production performance.

## Product expansion gate — owner clarification (2026-11-05)

The owner has clarified that major UI reconstruction and broad feature expansion may begin at **40% overall project progress**, rather than 50%.

At the 40% gate:
1. Reconcile and publish the weighted milestone ledger.
2. Prepare a scoped UI/feature blueprint using the owner's visual preferences.
3. Review scope and priorities with the owner before large implementation.
4. Implement incrementally with tests and acceptance checks.

Before 40%, prioritize foundation quality, reliability, documentation, secure configuration, dependency hygiene, accessibility, responsive behavior, and regression coverage. The 40% gate is a planning checkpoint, not a promise that all planned features will be complete.

## Next progress-accounting work

- Rebuild the milestone weight model from the actual product scope.
- Map each verified implementation to exactly one primary milestone to prevent double counting.
- Separate completed, partial, blocked, planned, and unverified work.
- Reconcile the historical 19.60% and owner-recalled 20.9% values with evidence.
- Publish a new percentage only after the calculation is reproducible and the owner has reviewed the model.

---

## Verified checkpoint — CME session-calendar foundation (2026-11-07)

Working branch: `phase-2/market-data-foundation`  
Audited HEAD: `001299360b038b1b85fdbf8c9e2cdda47afe7b5c`  
CI run: [#42340030836](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42340030836) — **success**.

### Verified completed in this checkpoint

- Added `backend/app/session_calendar.py` with immutable calendar/session records, Chicago timezone-aware boundaries, explicit provenance metadata, calendar/product-family validation, and integer nanosecond conversion.
- Added fail-closed lookup semantics: missing schedule coverage is `unknown`, not an assumed regular session or holiday.
- Added Sunday reopen / adjacent trading-date resolution, DST-aware timezone handling, regular maintenance classification, and special/early-close handling.
- Added daily, weekly, monthly, and quarterly session-bucket-bound resolution. A period is returned only when every trading-date record in its full date range is explicitly covered; closed dates must also be represented.
- Added calendar tests in `backend/tests/test_session_calendar.py` for DST, reopen, maintenance, missing dates, explicit closures, special sessions, validation, and higher-timeframe bounds.

### CI evidence

The exact HEAD above passed all steps in the single GitHub Actions job: frontend dependency installation, frontend unit tests, frontend production build, Python setup, backend dependency installation, backend tests, and backend container-image build.

### Current integration boundary — not yet complete

- `backend/app/aggregation.py` still deliberately skips UTC-fixed child bars when deriving `1d`, `1w`, `1M`, and `3M`.
- `backend/app/ohlcv.py` currently supports only `UTC_LEGACY` and `UTC_FIXED_V1` bucket policies; `OhlcvBar` rejects calendar metadata under those policies.
- Therefore the new calendar primitives are **not yet connected to production aggregation**, and no CME session-aligned OHLCV should be claimed as active.
- No authoritative CME schedule release has been loaded. Tests use constructed fixtures only; they are not exchange-calendar data.
- The SQLite OHLCV store has already been audited: schema version 2 persists `bucket_policy`, `calendar_id`, and `calendar_version`, and all three participate in the bar primary key and series index. No SQLite migration is currently indicated for this integration.
- Next implementation must enable and validate the session bucket identity in `OhlcvBar`, preserve it through adapters and derived bars, and gate aggregation on a matching, fully covered calendar release. Existing UTC intraday behavior must remain unchanged.

### Progress accounting

The prior owner-confirmed conversational checkpoints remain **20.3% then 20.9%**. A newly reconciled weighted overall percentage is still **not established** because the proposed milestone ledger has not been approved and scored criterion-by-criterion. This calendar work is recorded as verified foundation work, not converted into an invented percentage increase.

SQLite is considered complete for the current foundation scope. No SQLite rework is scheduled unless a concrete regression or missing acceptance criterion is found.


### Follow-up persistence audit — 2026-11-07

A targeted audit of `backend/app/ohlcv_store.py` and `backend/tests/test_ohlcv_store.py` confirmed that OHLCV SQLite schema version 2 already persists calendar identity fields (`bucket_policy`, `calendar_id`, `calendar_version`) and includes them in the composite primary key and series index. Existing policy-isolation and legacy migration tests are present. **No SQLite schema change is currently required for the next calendar integration step.** The remaining enablement work is in the OHLCV model/adapter/aggregation contract; this is not a reason to reopen completed SQLite work.


## Indicator progress tracker — audited 2026-11-07

This tracker is intentionally separate from the CME calendar work so indicator progress is never omitted from a project checkpoint.

| Indicator / layer | Verified repository state | User-visible completion |
|---|---|---|
| SMA 20 | Calculation function and unit tests exist | Not integrated into visible chart UI |
| EMA 20 | Calculation function and unit tests exist | Not integrated into visible chart UI |
| RSI 14 (Wilder) | Calculation function and unit tests exist | Not integrated into visible chart UI |
| MACD | Calculation function and unit tests exist | Not integrated into visible chart UI |
| Bollinger Bands | Calculation function and unit tests exist | Not integrated into visible chart UI |
| Shared indicator hook | `useMarketIndicators()` consumes only validated backend data from the shared market-data store; DEMO/loading/unavailable/error states yield no values | Hook exists; no visible indicator controls/panes |
| Footprint | Offline deterministic simulated aggregation engine and fixtures exist; buy/sell/unknown are kept separate and duplicate event IDs are rejected | Not visually implemented; must remain clearly SIMULATED; wait for owner's Footprint reference image |
| Heatmap | No implementation verified in this audit | Pending owner reference image and later scoped implementation |
| Liquidation Maps | No implementation verified in this audit | Pending owner reference image and later scoped implementation |

### Indicator constraints and next gates

- Every indicator must use the exact validated chart series for the currently selected canonical instrument and timeframe; no separate price source or sample-candle substitution.
- Calculation helpers and tests are groundwork only. They are not counted as visible, usable indicator features.
- Do not begin Footprint visual layout before the owner supplies its reference image. Ordinary candles and spacing must remain unchanged when Footprint is OFF; only explicit Footprint ON may activate the dedicated spaced cluster layout.
- Heatmap and Liquidation Maps visual work likewise waits for their respective owner reference images.
- The project expansion gate is 40% overall. Before that gate, retain the calculation/data-integrity foundations and tests; prepare a scoped blueprint and obtain owner review at the gate before major UI implementation.
- No indicator may be presented as predictive or as buy/sell advice. Simulated Footprint data must retain a visible SIMULATED label and must never be confused with market observations.
