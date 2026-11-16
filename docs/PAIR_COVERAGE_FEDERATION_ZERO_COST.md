# Pair coverage federation — multi-provider WebSocket strategy

Date: 2026-11-16  
Stage: 1 — Foundation, Security & Data Integrity  
Gate: 10 — market-data source and ingestion foundations  
Status: design specification; no provider has been activated by this document.

## Correct interpretation

The target is **many free providers with complementary pair coverage**. Provider A may support only a subset of instruments, Provider B a different subset, Provider C another subset, and so on. DEZZTA CHART can combine their coverage so that the union of approved provider/instrument mappings covers the desired watchlist.

This does not mean one socket per pair, nor does it require every provider to carry every pair. A provider session can carry its own supported pair subscriptions; multiple providers can coexist because each contributes a different part of the coverage map.

Example only (fictional; not actual provider claims):

| Source | Supported instruments | Connection model |
|---|---|---|
| Provider A | PAIR-1, PAIR-2 | One multiplexed session |
| Provider B | PAIR-3, PAIR-4 | One multiplexed session |
| Provider C | PAIR-5 | One session |
| Provider D | PAIR-1, PAIR-5 | Optional secondary/backup feed, clearly labelled |

The desired coverage is the union of eligible mappings, not the intersection. If an instrument is available from only one eligible provider, that is still useful coverage. If it is available from several, the app must preserve source identity and must not silently blend incompatible venue prices.

## Coverage registry

Represent availability as a reviewed mapping, not a guess:

- canonical instrument ID;
- provider ID and provider-native symbol;
- venue/market identifier;
- asset class and quote/base currency;
- supported event families (trade, quote, candle, depth);
- supported intervals and history limits;
- feed freshness (real-time, delayed, cached, daily reference);
- connection/session scope and multiplexing support;
- subscription, message, REST and monthly quotas;
- recurring price and expiry/trial status;
- display, caching and redistribution rights status;
- last successful verification date and evidence reference.

An absent mapping means unsupported. Do not infer that a provider supports a pair because the pair appears in a search result, website UI, or a similarly named symbol.

## Routing and fallback

1. Resolve the requested canonical instrument to all reviewed provider mappings.
2. Filter out providers that fail recurring-$0, terms/rights, freshness, asset/venue or quota requirements.
3. Select a primary source according to the user's selected market/venue and the feed's declared quality—not simply whichever responds first.
4. Keep other eligible sources as explicit alternatives or backups.
5. If primary disconnects, switch only under a declared fallback policy. Display the source/venue change and mark any continuity break.
6. Never merge trades, quotes, OHLCV or order-book levels from distinct venues into one apparently continuous feed without a separately designed consolidation policy.
7. If no eligible source remains, show unavailable/stale status. Never silently switch to a paid endpoint or an unreviewed source.

A backup is not automatically equivalent to the primary. It may have different trading hours, symbol conventions, quote currency, aggregation, delay, historical depth or licensing terms.

## Socket layout for complementary coverage

Use one connection pool per provider endpoint and credential scope. Each provider adapter owns its own session lifecycle and subscription set. If a provider permits multiple symbols on one session, subscribe to the assigned set on that session. If it only permits one symbol per connection, isolate that provider behind its documented connection cap and evaluate whether the free tier can cover the required set at all.

The total socket count is therefore determined by provider rules and the number of selected providers—not by the number of chart pairs. A target of 5–10 providers is an architectural possibility, not a fixed requirement or a promise that ten free feeds exist for every asset class.

## Pair coverage and capacity calculation

For a target watchlist W and approved provider mappings M, define:

- coverage(p) = instruments in W supported by provider p after all eligibility filters;
- unionCoverage = union of coverage(p) for all approved providers;
- uncovered = W minus unionCoverage;
- redundant = instruments mapped by more than one approved provider.

Before enabling a source, calculate:
- number of required subscriptions per provider;
- sessions required under the provider's documented multiplexing/connection limits;
- expected messages per second and peak burst;
- REST backfill budget and historical lookback;
- monthly and daily quota headroom;
- expected bandwidth and storage;
- total non-API operating costs (compute, egress, persistence, backup, monitoring).

Do not estimate capacity using only pair count. High-volume instruments and depth feeds can generate substantially more events than quiet ticker streams.

## Zero-cost and anti-surprise-billing policy

Every provider must be classified as one of:
- recurring $0 with documented quota and acceptable rights;
- free trial/credit (not eligible for permanent baseline);
- paid/metered (blocked);
- unknown (blocked).

The exact workload must remain within free quotas with a safety margin. Quota exhaustion must stop or degrade that provider; it must not trigger an upgrade, paid fallback, metered endpoint, or automatic billing. Hosting, egress, storage, backups and monitoring also require a zero-cost proof. No API key or provider credential may be placed in the Android APK or source control.

Free API access is not proof of free redistribution. Terms must explicitly cover the intended in-app display, caching and user audience. If rights are unknown, the mapping is not eligible.

## Reliability requirements

- Per-provider bounded queue and backpressure.
- Provider-scoped exponential reconnect with jitter.
- Heartbeat and independent data-freshness monitoring.
- Duplicate and out-of-order detection.
- Sequence-gap recovery for order books using a valid snapshot; invalidate book until resynchronized.
- Timestamp normalization while retaining source event time and receive time.
- Stale status when no recent valid event arrives within a feed-specific threshold.
- Provider fault isolation; one provider's reconnect loop cannot starve other feeds.
- Explicit source/venue label and feed quality indicator in downstream data.
- Bounded metrics for session count, subscriptions, event rate, queue age, lag, dropped/coalesced events and quota consumption.

## Rollout

1. Define the actual target watchlist and asset classes.
2. Review official provider documentation and terms for each candidate.
3. Build the coverage matrix using only evidence-backed mappings.
4. Select one eligible provider and a narrow instrument subset.
5. Implement and test its adapter against the existing provider-neutral contract.
6. Verify source identity, exact instrument mapping, freshness, reconnect, quota-stop and stale-state behavior.
7. Add a second provider with disjoint or complementary coverage.
8. Validate fallback and source-change semantics.
9. Expand toward 5–10 providers only when each additional source increases useful, licensed coverage and remains inside the zero-cost budget.
10. Measure target-host/device latency, CPU, memory, network and queue behavior before declaring capacity.

## Current project boundary

The existing provider catalog is a descriptive candidate inventory and remains fail-closed. The existing runtime remains Databento-oriented. This document does not activate any provider, create sockets, add credentials, change OHLCV contracts, or claim any specific free provider covers any specific pair.

The provider inventory remains intentionally non-exhaustive. We will add candidates only after official evidence is reviewed. No dark-web/deep-web scraping or untrusted endpoint is needed: only documented, auditable sources can enter the product.

No Termux step is required for this design work. No paid service is introduced. No Stage 1 ticks are awarded for documentation alone.
