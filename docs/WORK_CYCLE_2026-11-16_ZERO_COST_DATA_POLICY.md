# DEZZTA CHART — Work-cycle report: zero-cost data sources and longevity

Date: 2026-11-16  
Active branch: `phase-2/market-data-foundation`  
Protected branch: `main` (untouched)

## Executive result

This cycle converts the owner's requirement — authentic source data, durable evolution, automatic refresh where supported, and zero recurring cost — into a documented provider-onboarding policy. It deliberately does not activate a new data feed or claim global real-time coverage.

The existing provider pipeline is currently Databento-specific. A new provider must fit the existing normalization and persistence contracts rather than weakening them or relabelling a limited feed as complete market coverage.

## Work completed

### 1. Zero-cost market-data source policy

Added `docs/FREE_MARKET_DATA_SOURCE_POLICY.md`.

The policy:
- separates recurring free sources from free trials/credits and paid entitlements;
- records official constraints for Alpaca Basic, Alpha Vantage free, and Databento credits/subscriptions;
- distinguishes trades, quotes, order-book depth, OHLCV, instrument definitions, corporate actions/fundamentals, FX and index/reference data;
- requires provenance, venue/feed scope, freshness, quota, licensing, attribution, retention and schema-version metadata;
- prohibits paid fallback when a free quota is exhausted;
- requires compatible feed scope before failover; incompatible sources must not be blended;
- specifies bounded retries, rate limiting, circuit breaking, idempotent ingestion, gap recovery, stale-data visibility and source acceptance tests.

Official source references are embedded in the policy document. A source listed there is a candidate only; it is not automatically approved, licensed for redistribution, configured, or live.

### 2. Colored project dashboard refreshed

Updated `docs/assets/project-progress-dashboard.svg` to reflect:
- the schema migration foundation;
- the zero-cost data-source policy;
- the fact that provider-neutral integration is still pending;
- current verification boundary (Vercel pending on the latest observed dashboard revision; GitHub Actions runs unavailable).

The dashboard remains documentation-only and is not part of the APK.

### 3. Repository review findings

Inspected the current `provider.py`, `instrument_registry.py`, `ohlcv_store.py`, `instrument_identity.py`, and `instrument_metadata.py` implementation.

Confirmed existing foundation:
- provider-neutral `LiveSource` and `HistoricalSource` protocols exist, but the manager's current runtime is explicitly Databento-oriented;
- canonical instrument identities and time-bounded provider mappings already exist;
- the OHLCV store preserves exact decimal values and integer nanosecond timestamps;
- the ingestion pipeline already has bounded historical backfill, coverage tracking, definition synchronization, reconnect handling and freshness state;
- the schema migration ledger and deterministic schema fingerprint helper exist, but are not yet adopted by the current stores.

A mistaken first attempt to fetch two guessed filenames returned 404; no repository files were changed by that failed read. The actual filenames were then obtained from the branch directory listing before review.

## Verified source constraints

- Alpaca Basic is documented as free for a limited US equities feed (IEX), with up to 30 websocket symbols and a historical-data limit of the latest 15 minutes. It must not be described as full consolidated US market coverage.
- Alpha Vantage documents 25 free requests per day; US real-time and 15-minute delayed stock data are premium-only.
- Databento's $125 is introductory credit; historical data is metered and live data requires a subscription. It is therefore not a recurring zero-cost baseline.

No new API key, credential, paid service, paid hosting, subscription, or data source was added.

## Next implementation sequence

1. Add a typed provider capability/entitlement manifest (asset class, venue/feed scope, data families, granularity, freshness, quota, terms and redistribution state).
2. Add one recurring-$0 source adapter only after its official terms fit the intended display use.
3. Normalize the source into existing canonical IDs, provider mappings and OHLCV ingestion.
4. Expose provenance and freshness so users can see source, venue/feed scope, event time and stale/degraded state.
5. Enforce hard quota budgets and compatible-only failover; no paid endpoint may be selected automatically.
6. Add exact-source CI and adapter-specific integration tests before enabling the source.

## Progress accounting — unchanged

- Stage 1: **30/40 provisional criteria; 300/400 ticks; 75% provisional**.
- Gate 10: **0/10 officially closed**.
- Open Stage 1 criteria/gates: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall: **20.90% historical owner-confirmed checkpoint only**; not recalculated by this cycle.
- No ticks or criteria awarded for code, docs, tests, CI or dashboard changes alone.

## Verification, safety and cost

- Source policy commit: `caf54b58a104e420deda626f7d27db58f757ff0c`.
- Dashboard commit: `5d7667f0970b9f7c5b78230c5c2f869681b0ffef`.
- At the dashboard verification snapshot, Vercel reported **PENDING** and no GitHub Actions workflow runs were returned. The final report commit itself still requires a fresh status check. No test pass is claimed.
- No Termux command or device-side action was required.
- No APK artifact or official download link was produced or verified.
- No production feed was enabled.
- ZERO COST maintained; no paid dependency or service added.
- `main` was not touched.

## Project links

- [Zero-cost market-data source policy](FREE_MARKET_DATA_SOURCE_POLICY.md)
- [Colored six-stage dashboard](assets/project-progress-dashboard.svg)
- [Project progress indicator](PROJECT_PROGRESS_INDICATOR.md)
- [Longevity and data evolution contract](FOUNDATION_LONGEVITY_AND_DATA_EVOLUTION.md)
