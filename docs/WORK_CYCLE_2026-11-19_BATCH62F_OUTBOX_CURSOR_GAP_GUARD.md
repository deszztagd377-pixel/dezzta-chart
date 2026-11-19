# Batch 62F — outbox cursor-integrity guard

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent:** `bc1aff114f7dd040e6be4b5df949f7f4750eb63a`  
**Cost:** ZERO COST • no deployment • no paid service • no Termux • `main` untouched

## Objective

Prevent a global WebSocket relay from advancing its durable checkpoint across a missing retained outbox cursor.

## Source change

File: `backend/app/ohlcv_store.py`

`SQLiteOhlcvStore.read_outbox_batch()` now enforces three conditions before returning a healthy page:

1. Every returned row, including the one-row look-ahead, must equal the next expected global cursor.
2. If the page is terminal (`has_more=False`), its final cursor (or the caller's cursor for an empty page) must equal the durable high-water mark.
3. Any mismatch returns `resnapshot_required` with `reason=cursor_gap`, an empty event list and the current high-water/retention metadata.

The look-ahead validation is important: it detects a missing cursor immediately after the selected page before a relay acknowledges/checkpoints the previous page. Gaps farther into the stream are detected by the subsequent page before that page is allowed to advance.

Existing cursor-expired and cursor-ahead responses are preserved. This change does not rewrite event payloads, cursor allocation, retention, SQLite schema or source writes.

## Regression tests

File: `backend/tests/test_ohlcv_store.py`

Added `test_global_outbox_batch_requires_resnapshot_on_missing_cursor`, covering:

- A missing cursor inside a page.
- A missing cursor in the look-ahead position at a page boundary.
- A missing terminal cursor while durable high-water remains ahead.

Each case confirms that no partial events are returned and the caller is explicitly told to resnapshot.

## Safety and compatibility review

- No schema migration.
- No new dependency.
- No Redis configuration change.
- No app startup/lifespan change.
- No new public endpoint.
- No source-outbox re-emission path.
- Existing retention-floor and cursor-ahead semantics retained.
- No SQLite WAL sharing across hosts.
- No relay activation or deployment.

## Validation

Static patch review confirms the function replacement is isolated to `read_outbox_batch()`, the regression test is added adjacent to the existing global-outbox tests, and the current progress ledger is updated. Runtime validation is pending the three GitHub Actions workflows on the new exact commit. This report must not be interpreted as a passing CI result until those workflows finish.

## Remaining WebSocket implementation

This is a cursor-integrity guard, not a complete multi-instance WebSocket solution. Remaining work is:

1. Replica identity and durable checkpoint schema.
2. Atomic idempotent apply of source events into independent local read models, without creating a new source outbox event.
3. Duplicate, stale, out-of-order, cursor-gap, exact-decimal, restart and watermark tests.
4. Redis Streams append/checkpoint and independent consumer groups per gateway.
5. Retry, crash, pending reclaim, outage and retention-expiry/resnapshot tests.
6. Two independent backend processes and owner-side Gate 25/36 acceptance.

Redis must not become a second source of truth. A Redis outage must not roll back committed source bars/outbox events.

## Gate 10 and indicator ledger

Gate 10 remains **0/10 formally closed** pending owner evidence. Stage 1 remains **75% provisional**; Stages 2–6 are not scored; overall project percentage is not established because M1–M8 weights are not approved.

The complete indicator ledger is maintained at the top of `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`. Calculation foundations for SMA20, EMA20, Wilder RSI14, MACD12/26/9 and Bollinger20,2 are fixture-tested but not yet visible chart controls/overlays/panes. Footprint remains simulated and gated on owner references; Heatmap and Liquidation Maps remain unimplemented and gated on references/blueprints.

## Cost and release

ZERO COST. No Vercel/Cloudflare deployment, no paid service, no Termux, and no change to `main`.
