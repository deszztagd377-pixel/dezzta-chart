# Batch 62G-4 — exact-head CI failure diagnosis and fixture repair

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Triggering commit:** `f093061f144120257fcb6d1eda44d51f966376ae`  
**Repair commit:** `eeaf1586886a1c3aec2be1a32e6c182a6085ea81`

## CI evidence and root cause

The push-triggered workflow `DEZZTA CHART - Automated Tests` for the triggering commit completed with failure. Its backend test step collected 1,062 tests: **1,061 passed and 1 failed**. Frontend unit tests and frontend build passed; CodeQL completed successfully.

The only failing test was:

`tests/test_ohlcv_store.py::test_replica_snapshot_rejects_numeric_decimal_fields_even_with_valid_digest`

The test constructed its forged JSONL snapshot with escaped backslash-n text (`"\\n"` / `b"\\n"`) rather than actual newline delimiters (`"\n"` / `b"\n"`). Consequently the entire fixture was parsed as one invalid header and verification stopped before exercising the intended semantic Decimal-type rejection. This was a test-fixture defect, not evidence that production snapshot validation accepted numeric Decimal fields.

## Repair

Only the target test function in `backend/tests/test_ohlcv_store.py` was changed. Its digest input now uses actual JSONL newline delimiters consistently for the header and bar record, and the written file uses the same exact byte sequence. The test continues to forge a valid checksum around a numeric Decimal field and expects replica installation to reject it with the canonical exact-decimal validation error.

No production source code, acceptance gate, deployment configuration, or application runtime was changed.

## Validation boundary

The repair commit triggers the repository's existing push CI. Its result must be read from the exact repair SHA before this defect can be marked closed. No test pass is claimed in this report. If the same test fails again, inspect the new exact-head log before any further edit.

## Cost and project controls

ZERO COST preserved. No Vercel or Cloudflare deployment, no paid Redis, no new dependency, no Termux action, and `main` untouched. Batch 62H publisher implementation remains blocked until the 62G replica foundation has green exact-head tests.

## Indicator ledger

No indicator implementation changed. The canonical detailed ledger remains in `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`. SMA20, EMA20, RSI14, MACD12/26/9 and Bollinger20,2 retain calculation/fixture foundations but still need visible chart integration and lifecycle/render evidence. Shared indicator hook still needs chart binding/loading/error/stale clearing. Footprint remains SIMULATED and gated on owner reference + reviewed blueprint; Heatmap and Liquidation Maps remain not implemented and gated on references/data/blueprints. Footprint OFF preserves normal candle spacing; only explicit ON enables spaced clusters.

## Accounting

Stage 1 remains 75% provisional (30/40 criteria; 300/400 ticks). Gate 10 remains 0/10 formally closed. Stages 2–6 remain NOT SCORED. Overall project percentage remains NOT ESTABLISHED because M1–M8 weights are unapproved. This test repair awards no ticks and closes no owner acceptance gate.
