# Batch 94 — Zero-Cost Provider Gate Audit

**Date:** 27 November 2026  
**Base branch:** `phase-2/market-data-foundation`  
**Audit branch:** `audit/batch94-zero-cost-provider-gate`  
**Scope:** provider eligibility only; no provider adapter, credential, production endpoint, or deployment is introduced.  
**Decision:** **YELLOW — no provider approved for public redistribution at this checkpoint.**

## 1. Acceptance criteria

A source may be approved for integration only when evidence establishes all of the following:

1. Official API/WebSocket documentation and stable protocol semantics.
2. The exact required data classes are available (OHLCV, trades, and, if needed, order-book updates).
3. Free-tier limits, connection limits, rate limits, retention, attribution, and expiry are documented.
4. Terms explicitly permit the intended display/redistribution to DEZZTA CHART users, or written permission/license is obtained.
5. No payment card, paid trial conversion, recurring fee, or paid upgrade is required for the accepted scope.
6. Runtime compatibility, reconnect behavior, timestamps, sequence semantics, and provenance can be validated.
7. Data is not scraped, relayed from an unauthorized account, or mislabeled as live.

A public unauthenticated endpoint proves connectivity availability only. It does **not** prove redistribution rights.

## 2. Official-source findings

### Binance public market data

Official documentation describes public REST market-data endpoints and a public market-data WebSocket endpoint that do not require API-key authentication:

- https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md
- https://developers.binance.me/en/docs/products/caas/market-data-streams

**Verified:** public endpoint documentation exists; Spot REST includes aggregate trades, depth, klines and recent trades; public WebSocket streams are documented.

**Not established by this audit:** permission to redistribute or publicly display the resulting data through a third-party multi-user application; applicable regional/exchange terms for the intended deployment; a complete free-tier/SLA guarantee for this product. No legal permission is inferred from endpoint accessibility.

**Decision:** candidate for technical evaluation only; not approved for public production integration.

### Coinbase public market data

Official documentation describes a public Exchange WebSocket feed for market-data updates:

- https://help.coinbase.com/en/developer-platform/websocket-feeds/exchange
- https://docs.cdp.coinbase.com/exchange/docs/websocket-overview

**Verified:** public WebSocket market-data documentation exists.

**Not established by this audit:** a no-cost redistribution/display license for DEZZTA CHART, and all commercial/public application conditions for the intended use.

**Decision:** candidate for technical evaluation only; not approved for public production integration.

### Kraken public market data

Official support documentation confirms unauthenticated public WebSocket market-data feeds:

- https://support.kraken.com/articles/360022326871-kraken-websocket-api-frequently-asked-questions

**Verified:** public WebSocket market-data access is documented.

**Not established by this audit:** explicit rights for redistribution/public display in DEZZTA CHART, nor all free-tier and production capacity constraints.

**Decision:** candidate for technical evaluation only; not approved for public production integration.

### Market Data personal plans

The provider's current documentation explicitly says self-service/personal plans do not permit redistribution, including embedding live or recent data in a product available to other users:

- https://www.marketdata.app/docs/account/data-policies/data-redistribution/
- https://www.marketdata.app/docs/api/cors/
- https://www.marketdata.app/terms/

**Verified:** personal/self-service access is not sufficient for a public multi-user chart application.

**Decision:** excluded from public DEZZTA CHART provider selection unless an appropriate redistribution license is obtained. This audit does not recommend a paid plan because the project has a zero-cost constraint.

## 3. Technical implications

- Do not add a provider adapter or credentials based solely on public endpoint availability.
- Keep synthetic proof mode explicitly synthetic.
- Keep production provider status disabled until terms and runtime gates are accepted.
- Do not use scraped web pages, personal-account relays, or another user's credentials.
- Keep source provenance, event timestamps, sequence/gap detection, reconnect policy, and rate-limit handling mandatory in any later adapter.
- Footprint/order-flow must not be populated from OHLCV alone. A future implementation requires a validated trade-level feed and documented aggressor-side semantics. No footprint feature is promoted to live-data status by this provider audit.

## 4. Batch 94 decision matrix

| Gate | Result | Evidence / exit condition |
|---|---|---|
| Official API documentation | YELLOW | Candidate docs exist; protocol implementation review remains |
| Public unauthenticated connectivity | YELLOW | Documented for candidates; runtime probe not performed |
| Free-tier/limits/expiry | YELLOW | Exact product-level limits need a scoped written audit |
| Public redistribution/display rights | YELLOW | No candidate has sufficient evidence in this audit |
| Runtime compatibility | YELLOW | No provider adapter or live connection tested |
| Timestamp/sequence/provenance | YELLOW | Must be verified against selected protocol before implementation |
| Zero-cost production eligibility | YELLOW | No candidate currently passes all criteria |

No gate is RED in the active project dashboard; unresolved evidence remains YELLOW and blocks promotion. This is a status convention, not a claim that acceptance criteria have passed.

## 5. Explicit non-actions

- No provider selected or enabled.
- No API key or secret created, read, or changed.
- No production data connection started.
- No Worker/Pages/Cloudflare resource created or deployed.
- No paid service or trial started.
- No changes to `main`.
- No change to the cancelled 10-minute interval decision.

## 6. Next dependency order

1. Complete Batch 94 evidence only if a provider supplies explicit rights and a verified zero-cost scope.
2. Otherwise keep provider gate YELLOW and continue provider-independent durability, replay, receipt, and recovery tests.
3. Do not begin Batch 95 public WSS/device acceptance with an unapproved live provider.
4. Return to Footprint PRO after the backend/provider dependency is ready. Its visual reference and per-cell tap/detail interaction remain a recorded product requirement; the existing PR is not a backend priority.

**Delivery target:** approximately 24 December 2026.  
**Cost:** zero.  
**Overall project completion:** not inferred from this gate audit.
