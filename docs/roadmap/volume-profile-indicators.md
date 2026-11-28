# Volume Profile Indicators — Product Requirements

Status: queued for implementation after the current Stage 1 market-data foundation work.
Target application branch: `phase-2/market-data-foundation`.
This document records requirements only; it does not add indicator UI or alter chart rendering.

## 1. Separate indicator tiers

### Exclusive Indicator — right-docked profile
- The profile is placed at the right edge of the chart and remains docked there while enabled.
- It must lay out automatically without covering candle bodies or blocking chart interaction.
- Its visual treatment should use the supplied reference as direction for horizontal price-level bars and volume distribution.
- The white arrow and white oval in the reference are annotations only; they are not product UI.

### Mid Tier Indicator — movable profile
- This is a separate indicator implementation, not a movable mode of the Exclusive indicator.
- The user can reposition it within the chart workspace.
- Its visual design and interaction polish are deferred until after the Exclusive indicator and the current Stage 1 foundation work.

## 2. Data and update requirements
- Both tiers must use the application's validated market-data pipeline and support every timeframe for which valid source data exists.
- Live updates must follow incoming market-data events; the profile must not animate fabricated values or use hard-coded volume.
- Revisions to the active candle must update the current profile deterministically. Historical corrections or snapshot replacements must trigger a consistent rebuild.
- The UI must expose the data provenance and distinguish verified volume from estimated or unavailable volume.

## 3. Volume fidelity constraint
- Standard OHLCV candles provide total volume per candle, not the traded volume at every individual price level inside that candle.
- A true price-level Volume Profile requires trade prints or provider-supplied volume-at-price / footprint data.
- If only candle OHLCV is available, any price-level allocation is an approximation and must be explicitly labelled as estimated. It must never be presented as exchange-verified volume-at-price.
- Bid/ask delta or footprint cells require suitable bid/ask-classified trade data; they cannot be inferred reliably from candle OHLCV alone.
- Do not add a paid data dependency. First inspect the existing provider/backend contracts and determine whether they already expose the required granularity.

## 4. Acceptance criteria
- Exclusive profile docks to the right edge when enabled and remains aligned during resize, timeframe changes, and chart updates.
- Mid Tier profile can be moved by the user and retains its position according to the product's workspace-state rules.
- Both tiers use the same canonical instrument identity and validated data source as the chart.
- All supported timeframes are handled without claiming unsupported granularities.
- No synthetic volume, decorative arrow, or reference-image annotation is rendered as indicator functionality.
- Unit tests cover price-bin aggregation, candle revisions, empty/unavailable data, timeframe changes, and deterministic rebuilds.
- Integration tests verify live update handling and that chart interaction remains usable.
- Visual implementation is scheduled after Stage 1; this document alone does not mark either indicator complete.
