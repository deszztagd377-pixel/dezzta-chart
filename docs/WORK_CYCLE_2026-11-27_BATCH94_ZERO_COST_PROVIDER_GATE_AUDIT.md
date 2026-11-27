# Batch 94 — Zero-Cost Provider Gate Audit

**Date:** 27 November 2026  
**Base branch:** `phase-2/market-data-foundation`  
**Audit branch:** `audit/batch94-zero-cost-provider-gate`  
**Scope:** eligibility and acceptance gate only; no provider adapter, credentials, production endpoint, or deployment is introduced.  
**Decision:** **YELLOW — provider eligibility is not accepted at this checkpoint.**

## 1. Acceptance criteria

A data source may be approved for a later engineering evaluation only when the project has evidence for all of the following:

1. Official API/WebSocket documentation and stable protocol semantics.
2. Exact required data classes and their definitions (OHLCV, trade-level events, and order-book updates where applicable).
3. Free-tier limits, connection limits, rate limits, retention, attribution, and expiry.
4. Written terms that clearly permit the intended display/redistribution, or written permission/license for that exact use.
5. No payment card, paid trial conversion, recurring fee, or paid upgrade for the accepted scope.
6. Runtime compatibility, reconnect behavior, timestamp semantics, sequence/gap behavior, and provenance.
7. No scraping, personal-account relay, credential sharing, or mislabeling of synthetic data as live.

Public endpoint availability is not proof of redistribution rights. A technically reachable feed is not automatically eligible for a multi-user application.

## 2. Audit finding

The current evidence does not establish one source that passes every required criterion for the intended DEZZTA CHART scope. In particular, public access and documented endpoints alone do not settle public display/redistribution permission, product-level free limits, expiry, attribution, or runtime acceptance.

No legal conclusion is made by this engineering audit. Any unclear license or redistribution condition remains an open acceptance item and requires authoritative written clarification before integration.

## 3. Technical implications

- Do not add a live provider adapter or credentials until the acceptance criteria are evidenced.
- Keep the existing Worker proof explicitly synthetic-only.
- Keep production provider status disabled.
- Do not use scraped pages, personal-account relays, or another person's credentials.
- Keep source provenance, event timestamps, sequence/gap detection, reconnect policy, and rate-limit handling mandatory in any later adapter.
- Footprint/order-flow must not be populated from OHLCV alone. A later implementation requires a validated trade-level source and documented aggressor-side semantics.
- No synthetic fixture may be presented as a live market feed.

## 4. Batch 94 decision matrix

| Gate | Result | Exit evidence |
|---|---|---|
| Official API documentation | YELLOW | A selected source and exact supported protocol must be reviewed |
| Required data classes | YELLOW | Trade/order-book semantics must be confirmed for the intended scope |
| Free-tier/limits/expiry | YELLOW | Written limits and expiry evidence required |
| Public display/redistribution rights | YELLOW | Explicit license or written permission required |
| Runtime compatibility | YELLOW | Pinned local runtime probe and reconnect tests required |
| Timestamp/sequence/provenance | YELLOW | Contract mapping and integrity tests required |
| Zero-cost eligibility | YELLOW | All above must pass without paid service or trial dependency |

No active item is marked RED in the project dashboard. YELLOW denotes an unresolved acceptance gate; it does not mean the gate has passed.

## 5. Explicit non-actions

- No provider selected or enabled.
- No provider credentials or secrets created, read, or changed.
- No production data connection started.
- No Worker/Pages/Cloudflare resource created or deployed.
- No paid service or trial started.
- No changes to `main`.
- No change to the cancelled 10-minute interval decision.

## 6. Next dependency order

1. Keep Batch 94 YELLOW until a source meets every documented eligibility condition.
2. Continue provider-independent durability, replay, receipt, and recovery testing.
3. Do not begin public WSS/device acceptance against an unapproved live source.
4. Return to Footprint PRO after backend and data-source dependencies are ready. Its visual reference and per-cell tap/detail interaction remain a deferred product requirement; the existing feature PR is not the current backend priority.

**Delivery target:** approximately 24 December 2026.  
**Cost:** zero.  
**Overall project completion:** not inferred from this gate audit.


## 7. Official-source legal screening — 27 November 2026

This screening is an engineering eligibility check, not legal advice or a final interpretation of any provider agreement.

| Candidate/source | Official evidence reviewed | Engineering decision |
|---|---|---|
| Coinbase Exchange market data | [Market Data Terms of Use](https://www.coinbase.com/legal/market_data) restrict redistribution, display, or dissemination of Market Data and Derived Works to third parties absent prior express written consent. | YELLOW — do not use for a multi-user display until the exact intended use is expressly authorized in writing. |
| Kraken public API data | [Kraken API introduction](https://docs-legacy.kraken.com/api/docs/guides/global-intro/) says prior permission is required for certain uses, including non-personal commercial use of public endpoint data. | YELLOW — intended application use and permission boundary need authoritative confirmation; public endpoint access is not acceptance. |
| Binance public Spot streams | [Official Binance API documentation](https://developers.binance.com/en/docs/introduction) and [official Spot API documentation repository](https://github.com/binance/binance-spot-api-docs) establish documented public market-data interfaces. This establishes technical documentation, not by itself a redistribution license. | YELLOW — stream-specific terms and rights for the intended multi-user display remain to be confirmed. |
| Binance Vision historical datasets | [Binance Vision Dataset Terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md), last updated 26 August 2026, state a CC BY-NC-SA 4.0 non-commercial grant and prohibit hosting or commercial exploitation of derivative real-time or historical feeds. These dataset terms must not be assumed to govern every live Spot stream. | YELLOW — not accepted as a general-purpose multi-user feed; obtain a written interpretation for any proposed use. |

### 7.1 Gate conclusion

No candidate is promoted to APPROVED. Coinbase has an explicit third-party redistribution/display restriction absent written consent. Kraken's documentation identifies a prior-permission boundary for certain non-personal commercial uses. Binance's public stream documentation confirms technical availability, while the separately published Vision dataset terms impose non-commercial and redistribution constraints on those datasets. None of these findings establishes every required item in the Batch 94 acceptance matrix: exact data classes, current rate/connection limits, retention, attribution, expiry, runtime behavior, and permission for DEZZTA CHART's exact distribution model.

The provider gate therefore remains YELLOW. Do not add credentials, provider adapters, live endpoints, or data claims on the basis of endpoint reachability alone. Recheck the controlling terms immediately before any later provider decision because terms and product scope can change.

