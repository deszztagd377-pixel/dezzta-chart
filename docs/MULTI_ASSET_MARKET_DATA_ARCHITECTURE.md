# DEZZTA CHART — Multi-asset market-data architecture

Status: approved product direction; architecture specification, not an assertion of live coverage.
Date: 2026-11-02
Working branch: `phase-2/market-data-foundation`

## Product direction

DEZZTA CHART is intended to become a multi-asset charting application. Target asset classes:
- Equities and ETFs.
- Listed futures and futures spreads where explicitly supported and identified.
- Crypto spot pairs and, as a separately modeled product type, crypto derivatives.
- FX pairs.
- Spot and calculated indices where the source provides licensed, clearly identified data.
- Additional classes only after a source, data contract, licensing, and instrument model are verified.

"All pairs" means broad, expandable catalog coverage across supported providers and licensed venues. It does not mean every global symbol is automatically available from one provider. A symbol is selectable as a real-data instrument only when a verified provider definition, entitlement, and supported data schema exist. Never fabricate a symbol, expiry, venue, price, or availability state.

## Provider strategy

Use a provider-neutral application contract with provider-specific adapters. Databento remains the first market-data provider candidate for its verified supported datasets and schemas. Its catalog spans multiple asset classes and venues, but coverage and licensing are dataset-specific. Do not assume that it provides every crypto spot exchange, every FX venue, or every global equity listing.

A later provider may be added for a missing class or venue. Routing must be explicit and observable:
- A canonical instrument can map to one or more provider-specific instrument records.
- Each mapping records provider, dataset, venue/publisher, provider instrument ID, raw symbol, validity interval, schema, and entitlement requirements.
- Provider failover is allowed only where the alternate source is contractually permitted and semantically compatible. Do not silently splice incompatible feeds or claim one feed is a continuation of another.
- Store provenance and timestamps so the UI can show the actual source and whether data is live, delayed, historical, demo, degraded, or unavailable.

## Canonical instrument identity

Do not use a ticker string as a globally unique identifier. Introduce a stable internal canonical ID and model at least:

| Field | Purpose |
|---|---|
| canonical_id | Stable application identity, independent of provider symbol changes |
| asset_class | equities, etf, futures, crypto_spot, crypto_derivative, fx, index, etc. |
| instrument_type | spot, outright future, option, perpetual, dated derivative, index, etc. |
| base_asset / quote_asset | Required where the product is a pair; null otherwise |
| display_symbol | Human-readable selector label, never used alone as a primary key |
| venue | Exchange/market venue; explicit, not inferred from ticker |
| quote_currency | Currency used for displayed prices |
| price_scale / tick_size | Exact decimal representation and valid price increment |
| quantity_step | Valid quantity precision where applicable |
| contract_multiplier | Futures/derivative contract economics where supplied by verified definitions |
| expiration / settlement | Required for dated contracts when supplied |
| trading_calendar / session_timezone | Venue-specific session and time interpretation |
| status and valid_from/to | Listing lifecycle and point-in-time identity |
| source mappings | Provider/dataset/publisher/instrument IDs and mapping validity |

Keep provider IDs scoped by provider and dataset. They are not global identifiers and may change over time. Use exact decimal strings or integer fixed-point values at API boundaries; avoid floating-point identity or price arithmetic where precision matters.

Asset-specific fields must be optional and typed, not forced into a futures-only schema. Do not invent values for unavailable metadata.

## Data pipeline and shared indicator contract

Every selected chart series follows one path:

`Canonical instrument + provider mapping + timeframe`
→ entitlement and source selection
→ provider adapter
→ normalized event/bar validation
→ sequence and gap handling
→ shared market-data store
→ chart and indicators.

The currently implemented shared store identity is futures-oriented (dataset, publisher, instrument ID, raw symbol, timeframe). It must be evolved deliberately to include canonical instrument ID, asset class, venue, provider mapping, and schema/version without weakening the existing exact-series validation. Migrate with compatibility tests; do not simply remove existing identity checks.

All indicators consume the exact same selected series identity and validated bars as the chart. Changing symbol, venue, contract, provider mapping, or timeframe must clear old indicator inputs before accepting the new series. A chart cannot show one instrument while an indicator silently calculates another.

Not every indicator is valid for every data type. For example, bid/ask footprint requires suitable trade/quote or order-book source data; OHLCV-only bars cannot be used to fabricate bid/ask volume. The UI must explain unsupported source requirements rather than show made-up values.

## Accuracy, freshness, and recovery

- Preserve source event time and server receive time separately; record display time separately.
- Keep source provenance, schema, sequence/revision, and quality flags.
- Detect gaps, duplicates, out-of-order events, stale feed, invalid prices, session transitions, and symbol-definition changes.
- Recover with a provider-supported snapshot/replay or historical backfill. If continuity cannot be established, expose degraded/unavailable status; never silently bridge a gap.
- Handle market calendars, daylight-saving changes, overnight sessions, holidays, halts, and asset-specific trading hours using venue calendars, not one global UTC bucket rule.
- Corporate actions and symbol changes for equities must be represented explicitly; historical adjustments must be labeled and reproducible.
- Crypto markets are venue-specific and operate continuously, but a pair on one venue is not automatically interchangeable with the same pair on another.
- Futures expirations and roll rules must be explicit. A continuous series is a derived analytical series, not the same thing as an expiry-specific contract.
- Persist required definitions, entitlements, and data according to provider license. Durable storage, backups, restore tests, monitoring, and replay are required before long-term production claims.

## Coverage and licensing gate

Before a product is enabled:
1. Verify the provider dataset and exact instrument definition.
2. Verify real-time and historical availability separately.
3. Verify exchange/vendor licensing and redistribution/display rights for the intended user model.
4. Verify schema and timeframe support.
5. Verify session/calendar and precision metadata.
6. Add tests for symbol resolution, identity, provider mapping validity, gap/recovery, and indicator compatibility.
7. Expose source, delay status, and quality state in the UI.

A successful API connection does not prove a user has rights to display every instrument. User identity and market-data entitlement are separate authorization layers.

## Phased delivery

1. Preserve and complete the current futures OHLCV foundation.
2. Select and implement canonical multi-asset instrument identity with backward-compatible migration tests.
3. Add a verified instrument catalog endpoint and catalog UI driven only by provider definitions.
4. Add provider adapter interfaces and one asset-class adapter at a time.
5. Add durable storage, historical recovery, and operational monitoring.
6. Add authenticated user sessions and server-side per-instrument data entitlements.
7. Integrate the frontend stream through the shared store.
8. Add asset-specific indicator source contracts and UI only after the underlying data exists.
9. Expand venues/providers based on verified coverage, licensing, cost, and operational reliability.

No step may mark a market live merely because a selector entry exists. No broker execution or order placement is part of this market-data foundation.

## Current limitations

- No real provider credentials/session or production market feed is configured.
- Current catalog and symbol resolver are in-memory and futures-focused.
- Current configured roots are ES, NQ, and GC.
- The frontend WebSocket client is not integrated.
- The shared market-data store uses the existing futures-oriented exact identity and needs a tested canonical-identity migration.
- Durable persistence, replay, and production deployment remain incomplete.
- No all-market coverage or all-pairs availability is claimed.
