# Canonical Instrument Identity Contract

## Purpose

DEZZTA CHART must support multiple asset classes without treating a ticker as a globally unique instrument. This contract introduces a provider-neutral identity model while leaving the existing futures catalog and market-data routes unchanged.

## Identity rules

- canonical_id is a registry-assigned UUID that must be persisted. It is not generated from a ticker, venue, provider ID, or expiry string.
- asset_class, instrument_type, symbol, and venue describe the app-level instrument.
- Provider identifiers remain in provider-scoped mappings. A provider ID is meaningful only in its documented provider, dataset, publisher, and validity scope.
- Two instruments with the same displayed symbol but different venues are distinct.
- Provider remapping or ticker changes must not silently change the canonical ID.

## Supported combinations in this schema

| Asset class | Instrument type |
| --- | --- |
| equity | stock |
| etf | etf |
| crypto | spot, perpetual |
| future | dated future |
| option | option |
| fx | fx_pair |
| index | index |

This is a metadata contract, not a claim that a live provider currently supplies every class or venue.

## Validation and precision

- UUID identity, non-empty symbol and venue, supported asset/type combinations, and asset-specific required fields are validated.
- Spot, perpetual, and FX instruments require distinct base and quote currency codes.
- Dated futures and options require an ISO calendar expiration date.
- Options additionally require call/put right, positive strike price, and a valid underlying canonical UUID distinct from the option's own ID.
- Tick size, quantity increment, strike, and contract multiplier are positive finite decimal strings. They are not converted to binary floating point in this identity layer.
- Session calendars and provider mappings are separate from chart timeframe and data-series identity.

## Important boundaries

This first implementation is an immutable schema and validation layer only. It does not yet provide:
- durable ID allocation or database persistence;
- provider discovery, entitlement checks, or licensing;
- symbol search/catalog APIs for every asset class;
- automatic futures roll or continuous-series construction;
- frontend catalog integration or multi-asset chart streaming.

The existing ES/NQ/GC futures path remains intact. Integration must be incremental and preserve exact provider/dataset/publisher/instrument/time identity for every market-data series.
