# Market-data source inventory — zero-cost and provenance review

Review date: 2026-11-16  
Scope: candidate data ports for DEZZTA CHART; no feed is activated by this inventory.  
Decision rule: **a free API request is not automatically a free, redistributable market-data licence.**

## Executive decision

The internet contains many public data endpoints, but they are not interchangeable. Some expose only one venue, some provide delayed or reference values, some require a key/account, and some have a free quota while restricting display or redistribution.

The inventory separates three independent questions:

1. **Cost:** Is ordinary recurring API use genuinely $0, rather than a trial, expiring credit or paid-tier teaser?
2. **Data fit:** Does the feed provide the exact asset, venue, event type, timestamp precision and freshness the chart claims to show?
3. **Rights:** Do the source terms permit this application's intended display, caching, derived values and redistribution?

A candidate may pass cost and still be blocked by data fit or rights. No candidate below is approved for production distribution as of this review.

## Candidate matrix

| Source | Data families / scope | Cost and limits documented | Freshness / data fit | Rights and decision |
|---|---|---|---|---|
| Alpaca Basic | US equities/ETFs; IEX feed; indicative options feed | $0 Basic; up to 30 websocket symbols; 200 historical calls/min; historical access limited to latest 15 minutes | Real-time IEX only; not consolidated all-US-venue coverage | Rights for this app's display/redistribution not approved. **Conditional candidate only** |
| Alpha Vantage Free | Selected equity, FX, crypto and reference datasets | 25 requests/day free quota | US real-time and 15-minute delayed stock data are premium; not a free real-time US stock feed | Rights/redistribution still require review. **Low-volume reference candidate only** |
| Twelve Data Basic | Selected US equities, FX and crypto | 8 API credits shown; 800 calls/day; websocket access is trial-limited | Mixed and plan-dependent | Basic pricing page describes internal non-display usage. **Do not use for user-facing chart display until written rights are clear** |
| CoinGecko Demo | Aggregated crypto prices, market cap, volume and metadata | $0 Demo; 10,000 credits/month; 100 calls/min | Freshness from 60 seconds; not an exchange's complete order book or venue-specific trades | Attribution required; commercial redistribution not established. **Prototype/personal evaluation only until terms approved** |
| Binance public market-data-only endpoints | Exchange-specific spot trades, ticker, depth, klines and public streams | Market-data-only REST/WebSocket endpoints do not require an API key; request-weight/IP limits apply | Venue-specific exchange data; public endpoints do not mean consolidated market coverage | Display/redistribution rights for this app remain unreviewed. **Technical candidate only** |
| Kraken public market-data endpoints | Exchange-specific ticker, depth and trades; public endpoints | Public market-data endpoints do not require an account; REST limits vary by endpoint/IP/pair | Venue-specific live and historical market observations | Display/redistribution rights for this app remain unreviewed. **Technical candidate only** |
| FRED | US macroeconomic time series, release history and vintages | Free API with registered API key; documented 120 requests/min before 429 response | Periodic macro data, not live market prices | Attribution, third-party series ownership and API terms apply; intended use is restricted. **Macro/reference only** |
| Frankfurter | FX and currency reference rates | Free public API, no key; open-source project | Reference rates update when source institutions publish, generally once or a few times daily; not executable live quotes | Terms for redistribution in this application still need review. **FX reference candidate only** |
| World Bank Indicators API | Country/economic indicators | Public API, no API key; nearly 16,000 indicators documented | Periodic macro/economic series, not live prices | Dataset-specific attribution/reuse review remains required. **Macro/reference only** |
| Databento | Exchange market data, including trades/quotes/depth/OHLCV/definitions | Introductory credit is finite; historical use is metered; live requires subscription | Broad, dataset-dependent market data | **Not recurring free; excluded from the $0 baseline** |

## Official documentation used

### Equities and multi-asset APIs

- Alpaca market-data plan matrix: https://docs.alpaca.markets/us/docs/about-market-data-api
- Alpaca explanation of IEX versus SIP feeds: https://alpaca.markets/support/data-provider-alpaca
- Alpha Vantage API key and free quota: https://www.alphavantage.co/support/api-key/
- Alpha Vantage endpoint/entitlement documentation: https://www.alphavantage.co/documentation/
- Twelve Data pricing and Basic plan limits: https://twelvedata.com/pricing
- CoinGecko API pricing, Demo quota and freshness: https://www.coingecko.com/en/api/pricing

### Venue-specific public market-data APIs

- Binance official market-data-only endpoint documentation: https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md
- Binance official REST rate-limit documentation: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
- Kraken official public endpoint examples: https://support.kraken.com/in/articles/360000919986-public-endpoint-examples-you-can-try-them-directly-in-a-web-browser-
- Kraken official public REST rate-limit notes: https://support.kraken.com/au/articles/206548367-what-are-the-api-rate-limits-

### Macro and reference data

- FRED API terms: https://fred.stlouisfed.org/docs/api/terms_of_use.html
- FRED API rate-limit/error documentation: https://fred.stlouisfed.org/docs/api/fred/errors.html
- Frankfurter official API documentation: https://frankfurter.dev/
- World Bank Indicators API documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- World Bank open-data usage overview: https://data.worldbank.org/about/get-started

### Trial/credit exclusion

- Databento pricing: https://databento.com/pricing/
- Databento usage pricing and credits: https://databento.com/docs/faqs/usage-pricing-and-data-credits

## Cost verdicts — keep the meanings separate

- **Recurring-free API:** documentation shows a $0 recurring tier or public endpoint. This does not by itself prove that the application can redistribute the data.
- **Free trial/credit:** not accepted as zero-cost infrastructure. It can expire or turn into paid usage.
- **Free account/key:** the account may be free, but the data licence may still limit display or redistribution.
- **No-key public endpoint:** avoids account/key costs, but does not automatically grant redistribution rights, unlimited use or service guarantees.
- **Self-hosted/open-source:** software may have no licence fee, but compute, storage, electricity, bandwidth, maintenance and source-data rights still matter.

## Data-family fit — don't combine unlike feeds

1. **Trades:** execution events from a named venue/feed. Preserve event time, venue and sequence where provided.
2. **Quotes:** bid/ask observations. A last-trade ticker is not a quote.
3. **Order book:** preserve venue, depth level and snapshot/update semantics. A level-1 quote is not L2/L3 depth.
4. **OHLCV:** preserve timeframe, session calendar, adjustment policy, bucket boundaries and completeness.
5. **Instrument definitions:** preserve contract identity, expiry, multiplier, tick size, lot size and effective timestamps.
6. **Macro/fundamental series:** preserve publication time, observation period, revision/vintage and source.
7. **FX reference rates:** label as reference rates and their publication date, never as executable bid/ask prices.

A feed must not be relabelled as "global", "all exchanges", "real-time", "live order book" or "consolidated" unless its official dataset scope proves that claim.

## Zero-cost activation gate

A source may move from candidate to enabled only after all conditions below are evidenced:

- Recurring API/data price is $0 for the intended usage; no trial, expiring credit, paid fallback or auto-upgrade.
- Hosting, persistence, egress, secrets and monitoring needed for the connector remain within the approved zero-cost plan.
- Intended display, caching, derivative calculation and redistribution rights are documented for the actual app audience.
- Exact asset class, venue, feed scope, event families, historical lookback and freshness are declared.
- Quotas are encoded as hard local budgets; reaching a quota pauses/degrades the feed rather than selecting a paid endpoint.
- Instrument mapping and decimal/timestamp parsing are tested.
- Duplicate, out-of-order, reconnect, gap, stale-state and provider-schema-change tests pass.
- Provider attribution is displayed where required.
- A successful CI run and controlled live verification exist for the exact adapter commit.

## Provider-neutral application contract

The accompanying `backend/app/provider_catalog.py` is a descriptive inventory and fail-closed policy helper only. It does not call any provider, hold credentials, activate a feed, or change the existing Databento manager.

Its safety property is deliberate:
- unknown provider ID => blocked;
- free trial/credit => blocked from the recurring-$0 baseline;
- recurring free but display rights unknown/restricted => blocked;
- only recurring-free AND rights-approved candidates can be considered eligible;
- no current candidate is pre-approved.

Do not bypass this gate by changing a status flag without a dated, evidence-backed terms review. Do not treat a source's API availability as proof of a licence.

## Current implementation boundary and next steps

Existing DEZZTA CHART foundations include canonical instrument identities, provider-symbol mappings, exact decimal OHLCV storage, ingestion, coverage tracking, definition synchronization and source freshness. The active runtime remains Databento-oriented.

Next implementation order:
1. Review the provider catalog and rights evidence.
2. Choose one data family and one venue/feed scope first; do not attempt every asset class simultaneously.
3. Build one adapter against existing provider-neutral interfaces.
4. Validate payloads and map instruments without changing canonical IDs.
5. Enforce hard quota budgets and source-aware freshness/provenance.
6. Keep the adapter disabled until tests, CI, rights review and live source verification pass.

This inventory is intentionally broad but not exhaustive. New sources can be added only after the same cost/data/rights review. "Many endpoints exist on the internet" is not a reason to trust them or make them part of the application.


## Multi-provider connection design

The companion [Multi-provider WebSocket pool design](MULTI_PROVIDER_WEBSOCKET_POOL_DESIGN.md) defines how multiple approved sources can be multiplexed and isolated without opening a socket per pair. It specifies bounded sessions, per-provider quota budgets, backpressure, stale/gap handling, reconnect policy and measured capacity acceptance. It is a design specification only: no WebSocket pool or new provider has been activated.


## Complementary pair coverage

The [Pair Coverage Federation design](PAIR_COVERAGE_FEDERATION_ZERO_COST.md) documents the intended model: independent free providers may cover different subsets of the target instruments, and DEZZTA CHART can combine the union of eligible mappings. It explicitly does not assume that one provider covers every pair, nor that each pair needs its own socket. Provider/venue identity, licensing, quota and freshness remain mandatory per mapping. This is architecture only; no provider-specific pair claim is approved and no feed is active.
