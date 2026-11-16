# DEZZTA CHART — Work cycle: expanded zero-cost data-source audit and fail-closed catalog

Date: 2026-11-16  
Branch: `phase-2/market-data-foundation`  
Protected branch: `main` — untouched

## Executive result

The previous source review was only a small initial subset. This cycle expanded the inventory to ten data-source candidates spanning equities, exchange-specific spot market data, aggregated crypto reference data, FX reference rates, macroeconomic series and country indicators.

A machine-readable, fail-closed provider candidate catalog and focused tests were added. No new provider is activated. This is deliberate: recurring $0 API access is only one part of the requirement; intended-use display/redistribution rights, exact data scope, quota, hosting cost and freshness must also be proven.

## Files added or updated

### Runtime foundation
- `backend/app/provider_catalog.py` — immutable provider candidate inventory with explicit cost class, rights status, freshness class, asset classes, data families, authentication mode, documented quota/limits, official documentation URL and caveat.
- The catalog helper does not call the internet, create clients, store keys, enable providers or alter the existing Databento runtime.
- A source is eligible only when recurring cost is classified as free, intended-use rights are explicitly approved, official HTTPS documentation exists, a quota/limit is recorded, and asset/data-family scope is complete.
- Unknown provider IDs and incomplete evidence fail closed.
- Trial credits are a distinct cost class and can never qualify as recurring free.

### Regression tests
- `backend/tests/test_provider_catalog.py` — eleven tests authored for unique provider IDs, unknown-provider rejection, rights gating, trial-credit exclusion, source-family classification, venue-scope distinctions, and incomplete-evidence rejection.
- Tests have not been run or verified by CI on the final commit. No test pass is claimed.

### Documentation
- `docs/MARKET_DATA_SOURCE_INVENTORY_ZERO_COST.md` — expanded source-by-source review, data-family distinctions, cost verdicts, official documentation references and activation checklist.
- `docs/FREE_MARKET_DATA_SOURCE_POLICY.md` — links to the expanded inventory.
- `docs/PROJECT_PROGRESS_INDICATOR.md` — full work-cycle record added; test count corrected to eleven.
- `docs/assets/project-progress-dashboard.svg` — six-stage colored dashboard refreshed.
- `docs/WORK_CYCLE_2026-11-16_ZERO_COST_DATA_AUDIT.md` — this report.

## Ten source candidates reviewed

| Candidate | Cost classification | Data fit | Rights status for this app |
|---|---|---|---|
| Alpaca Basic | Recurring $0 tier | US equities IEX feed; limited websocket and historical window | Unknown; not consolidated all-US coverage |
| Alpha Vantage Free | Recurring $0 tier | 25 requests/day; US real-time/delayed stock data premium | Unknown; not a free live US stock feed |
| Twelve Data Basic | Recurring $0 tier | 8 API credits, 800/day shown; websocket allowance trial-limited | Unknown; Basic labels internal non-display usage |
| CoinGecko Demo | Recurring $0 Demo tier | 10,000 credits/month, 100/min, freshness from 60 seconds | Unknown; attribution required, commercial redistribution not assumed |
| Public exchange-specific market-data endpoints | Public market-data calls have no API key requirement | Trades, ticker, depth, candles/streams within each venue's scope | Unknown; no assumption of redistribution rights |
| FRED | Recurring $0 API | Macro time series, not live prices; API key required | Restricted by terms/third-party series conditions |
| Frankfurter | Recurring $0 public API | FX reference rates, not executable bid/ask quotes | Unknown for this application's redistribution |
| World Bank Indicators | Public API, no key | Country/macro indicators, not live prices | Unknown at app/dataset-specific level |
| Databento | Trial/credit only, then metered/paid | Broad exchange market data | Excluded from recurring-$0 baseline |

The inventory includes official documentation links for all entries. It is not claimed to be exhaustive of every public data source on the internet.

## Important distinction: $0 endpoint versus $0 production use

A free endpoint can still fail the project requirement if:
- the free quota is too small for the planned chart refresh;
- the source is delayed or cached while the UI labels it real-time;
- the free plan permits internal non-display use only;
- the terms do not grant display or redistribution rights;
- hosting, storage, bandwidth, logs, monitoring or egress introduce a charge;
- a quota overrun triggers an upgrade or paid fallback.

Therefore the catalog currently has **no production-approved provider**. This is not a lack of work; it prevents accidentally enabling a data source that violates the owner's zero-money requirement or misrepresents the data.

## Technical boundaries preserved

- Existing canonical instrument IDs and time-bounded provider symbol mappings are unchanged.
- Existing exact-decimal OHLCV storage and ingestion contracts are unchanged.
- Existing Databento-oriented provider manager remains unchanged and is not silently switched.
- No market-data credentials were requested, created, copied or stored.
- No source feed was activated and no synthetic data was passed off as real.
- No paid fallback, auto-upgrade, subscription, hosting or monitoring service was added.
- No APK was built or claimed ready.
- No Termux work was needed.

## Progress accounting — unchanged

- Stage 1: **30/40 provisional criteria; 300/400 ticks; 75% provisional**.
- Gate 10: **0/10 officially closed**.
- Open Stage 1 criteria/gates: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall: **20.90% historical owner-confirmed checkpoint only**, not recalculated.
- No ticks or criteria were awarded for research, code, tests, docs or dashboard changes alone.

## Verification and repository state

- All changes are on `phase-2/market-data-foundation`.
- `main` was not touched.
- Source catalog and tests are committed; tests remain unexecuted/unverified.
- No GitHub Actions run is available from the current commit-status lookup. Vercel status is separate and is not backend test evidence.
- No Termux command or user-side code/document action is required.

## Next work sequence

1. Choose exactly one source and one data family after reviewing terms for the actual app audience.
2. Confirm that all source, hosting, storage and bandwidth costs remain $0 at the expected refresh volume.
3. Implement a provider adapter against the existing interfaces without altering canonical identity or OHLCV persistence.
4. Add hard quota enforcement, provenance, freshness and stale-state behavior.
5. Test duplicate/out-of-order events, reconnect, gap recovery, schema drift and quota exhaustion.
6. Keep the adapter disabled until exact-commit CI, rights review and controlled live verification pass.

The target remains broad and TradingView-like in chart capability, but coverage claims must be earned feed by feed, not inferred from a long provider list.
