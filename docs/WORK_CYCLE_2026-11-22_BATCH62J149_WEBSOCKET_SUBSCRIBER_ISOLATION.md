# Work Cycle 62J-149 — WebSocket same-series subscriber isolation

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Base HEAD: `0f71a3e4b32dd7b7184f468c83874526b0a678a8`  
Test commit: `ed7f22a00b71223d0dd7ed280aadddd8a30cf6e1`  
Cost: ZERO COST. `main`: untouched.

## Objective

Strengthen evidence for the WebSocket invariant that one downstream client disconnecting must not interrupt another client subscribed to the same exact market-data series.

## Source inspection

Reviewed `backend/app/ohlcv_stream.py` and `backend/tests/test_ohlcv_stream.py`. `OhlcvStreamHub` stores a separate subscription object and bounded queue per client stream ID, and publishes validated bars to active subscriptions whose exact series identity matches.

## Added regression

New test: `test_same_series_subscribers_are_isolated_when_one_disconnects`.

Sequence:
1. Create one pipeline and apply initial bar.
2. Register two subscribers to the same dataset/publisher/instrument/symbol/timeframe identity.
3. Verify subscriber count is 2.
4. Publish first update; both queues receive one event.
5. Unsubscribe first stream; verify subscriber count becomes 1.
6. Publish second update; first subscription remains closed and empty, while second receives the update.
7. Unsubscribe second stream; verify subscriber count becomes 0.

This adds deterministic regression coverage for downstream isolation and last downstream subscriber cleanup.

## Explicit limitation

This test does not prove upstream market-data provider pooling, dynamic provider subscribe/unsubscribe, or on-demand market subscription. The provider manager still starts from application lifecycle/configuration and the current Databento adapter remains fixed-symbol. Do not promote Stage 2 based on this test.

## Project and indicator status

- Stage 1: 30/40 = 75% provisional 🟨.
- Stage 2: not officially opened/scored ⬜; on-demand provider coordination remains open.
- Gate 10: 0/10 external criteria formally closed.
- Overall project: NOT SCORED; stage weights/denominator not approved.
- Indicators remain: SMA20 🟨, EMA20 🟨, RSI14 Wilder 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- The complete indicator ledger and detailed mathematical/rendering acceptance criteria remain in `docs/INDICATOR_PROGRESS_LEDGER.md` and `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

## CI

New commit triggers exact-HEAD Automated Tests, CodeQL, secret audit and OCI ARM64 workflows. Previous HEAD CI is not a substitute; verify the exact latest branch SHA before acceptance.

## Cost and integrity

No paid provider, cloud account, credential, deployment, payment method, device/Termux action or `main` branch change. Only backend test and progress documentation changes were made.
