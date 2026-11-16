# Zero-Cost Market-Data Source Policy

Status: design policy; no new provider is enabled by this document.
Last reviewed: 2026-11-16.
Applies to DEZZTA CHART provider onboarding and automated refresh.

## 1. Non-negotiable zero-cost rule

A source is eligible for the zero-cost baseline only when ordinary recurring use can remain at $0 without depending on expiring trial credits, a paid tier, a paid market-data entitlement, paid hosting, or an assumed future subsidy.

A free account is not automatically a free data licence. Every provider must be checked for:
- recurring quota and rate limits;
- asset, venue, feed and instrument coverage;
- real-time, delayed or end-of-day freshness;
- historical lookback and retention;
- personal-use versus display/redistribution rights;
- attribution, caching and derived-data restrictions;
- account, key, geographic and eligibility requirements;
- whether exceeding a quota silently bills, hard-fails, or requires an upgrade.

Do not add a source to the production allowlist until these fields have an evidence-backed record. No hidden fallback to a paid endpoint is permitted. The application must not request or store payment details for data access.

## 2. Publicly documented source candidates (not yet approved for production)

| Candidate | What official documentation says | Zero-cost assessment | Important boundary |
|---|---|---|---|
| Alpaca Market Data Basic | Free equities plan covers US stocks/ETFs with IEX real-time feed, up to 30 websocket symbols, 200 historical API calls/minute, and historical data limited to the latest 15 minutes. | Potential recurring $0 source for a narrowly labelled IEX feed, subject to account and data-use terms. | IEX is not the full consolidated US market. Never label it as all-US-exchange coverage or silently combine it with another feed. |
| Alpha Vantage free API | Most datasets are available at 25 requests/day. US real-time and 15-minute delayed stock data are premium-only. | Potential low-volume historical/EOD enrichment, subject to current terms and quota. | Not a free real-time US stock source; 25 requests/day is a strict design constraint. |
| Databento | New accounts receive $125 in credits; historical usage is metered by data volume; live data requires a paid subscription plan. | Trial credit only; not a sustainable zero-cost baseline. | Existing integration must remain disabled unless the owner explicitly configures a paid budget. Do not mistake credits for a free recurring entitlement. |
| Direct public exchange endpoints | Some venues publish public market endpoints without API credentials; exact endpoints, limits and licences vary by venue. | Candidate-by-candidate review only. | Public access does not grant redistribution rights, uptime guarantees, or permission to aggregate venues as one consolidated feed. |

Official references:
- Alpaca market-data plan matrix: https://docs.alpaca.markets/us/docs/about-market-data-api
- Alpha Vantage quotas and real-time entitlement: https://www.alphavantage.co/support/api-key/
- Alpha Vantage data freshness/entitlement documentation: https://www.alphavantage.co/documentation/
- Databento pricing and credits: https://databento.com/pricing/
- Databento usage-based billing explanation: https://databento.com/docs/faqs/usage-pricing-and-data-credits

These are source-evaluation notes, not a claim that the listed providers are currently configured, licensed for redistribution, or available to every user. Re-check official terms before enabling any connector. The broader candidate matrix, including exchange-specific public feeds, FX reference, macro and country indicators, is maintained in [MARKET_DATA_SOURCE_INVENTORY_ZERO_COST.md](MARKET_DATA_SOURCE_INVENTORY_ZERO_COST.md).

## 3. Data families must stay distinct

The provider registry must identify the exact data family rather than calling everything "market data":

1. Trades: individual executions, with venue and event timestamp.
2. Quotes: bid/ask prices and sizes, with feed scope and quote condition.
3. Order book: depth level and venue; L1, L2 and L3 are not interchangeable.
4. OHLCV bars: timeframe, bucket policy, session calendar, adjustment policy and completeness.
5. Instrument definitions: contract identity, expiry, strike, multiplier, tick size, lot size and effective time.
6. Corporate actions/fundamentals: source attribution, publication time, effective date and adjustment lineage.
7. FX/reference rates and indices: source methodology, timestamp and whether values are indicative or executable.

A chart may display more than one family, but must never silently imply that unlike feeds are equivalent.

## 4. Canonical source record

Every enabled source/feed should have a versioned configuration record containing at least:

- provider and dataset identifiers;
- asset class, venue, feed scope and instrument mapping namespace;
- supported data families and granularities;
- real-time/delayed/EOD classification;
- documented quota, current local usage counter and reset window;
- authentication mode and secret reference (never the secret itself);
- licence/terms URL, terms review date, attribution and redistribution status;
- retention/lookback limits;
- source schema version and normalizer version;
- last successful fetch/stream time, last event time, freshness state and health;
- explicit zero-cost eligibility and reason.

Do not place credentials in the APK, source repository, logs, public API responses or progress dashboard.

## 5. Safe automatic refresh and failover

- Use WebSocket streaming only where the provider documents it; otherwise use bounded polling with a source-specific interval.
- Apply per-provider rate limiting, request budgets, exponential backoff with jitter, bounded retries and a circuit breaker.
- Enforce a hard zero-cost budget: do not automatically switch to a paid endpoint, paid dataset or paid cloud service when a free quota is exhausted.
- Persist source event time and local receive time separately. Track stale data, gaps, duplicate events, out-of-order events and provider outages.
- Use idempotent ingestion keys and durable checkpoints. Backfill only explicitly covered missing intervals and within the source's documented historical limits.
- Failover is allowed only to a source with compatible asset, venue, feed scope, adjustment policy and licence. Otherwise mark the chart degraded or unavailable; do not blend incompatible prices.
- Preserve the source/provider identity on every persisted observation so the displayed chart can explain provenance.
- Treat provider schema/API changes as versioned adapter changes. Validate new payloads before accepting them; quarantine unknown shapes instead of guessing fields.

## 6. Data integrity rules

- Canonical instrument IDs are stable and independent of provider symbols.
- Provider symbol aliases are time-bounded mappings; a reused ticker must not rewrite historical identity.
- Prices, sizes and volume retain exact decimal representation; timestamps retain documented units and timezone.
- Never invent missing candles, fill unknown values with zero, or claim a stale last price is live.
- Record corrections as traceable revisions; do not silently overwrite source history.
- Display source, venue/feed scope, freshness and timestamp wherever users could mistake delayed or partial data for complete real-time data.

## 7. Acceptance tests before a source is enabled

1. Terms and recurring cost review is recorded.
2. Instrument mapping tests prove venue and contract identity.
3. Payload schema and timestamp/decimal validation reject malformed data.
4. Quota/rate-limit tests prove no paid fallback and bounded retries.
5. Duplicate, out-of-order, gap and reconnect tests pass.
6. Freshness and stale-state reporting is correct.
7. Historical backfill respects documented limits and does not fabricate coverage.
8. Licence/redistribution and attribution constraints are enforced.
9. Provider outage leaves existing durable data readable and the UI clearly degraded.
10. CI passes on the exact source commit; live credentials and production feed verification are separately recorded.

## 8. Current DEZZTA CHART integration boundary

The existing provider manager is Databento-specific and its settings/credentials gate whether it starts. The current pipeline already has ingestion, durable OHLCV, canonical instrument mapping, definition synchronization, bounded historical recovery, coverage tracking and provider connection/freshness state. This is a useful adapter foundation, not yet a multi-provider zero-cost router.

The next safe implementation sequence is:
1. Add a provider-neutral capability/entitlement manifest and validation model.
2. Add one separately tested adapter for a recurring-$0 feed whose terms fit the intended display use.
3. Normalize it into the existing canonical identity and OHLCV ingestion contracts.
4. Add source-aware freshness and provenance to chart/API responses.
5. Add budget enforcement and compatibility-checked failover.
6. Only then consider additional asset classes or venues.

Do not replace or weaken the current Databento normalizer to make a free source fit. Do not enable an unverified source, and do not claim broad worldwide coverage until each venue/feed is evidenced.
