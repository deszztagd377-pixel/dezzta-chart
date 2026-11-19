# Batch 62J-5 — bounded Redis replay read model

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Scope:** Add a reusable, bounded Redis Streams replay reader. This batch does not wire it into `main.py` or change deployment configuration.

## Problem

The current WebSocket reconnect path reads `SQLiteOhlcvStore.replay_outbox()`. That is correct for the authoritative source process, but a gateway backed by an independent replica cannot query the source SQLite outbox. The gateway needs a Redis replay reader that preserves the source's global cursor semantics.

## Implementation

Added `backend/app/ohlcv_redis_replay.py`:

- Reads a bounded page using Redis `XRANGE`, with deterministic stream IDs `<cursor>-0`.
- Validates source identity, canonical JSON encoding, event envelope, event ID, stream ID/cursor agreement and series/bar identity agreement.
- Scans the global stream, not just one symbol. Unrelated series still advance `next_cursor`, preventing pagination from stalling when the stream contains other instruments.
- Filters returned events against the exact ten-field canonical series identity.
- Requires contiguous global cursors. Missing, trimmed, malformed or mismatched entries fail closed with `RedisReplayResnapshotRequired`; the caller must require a fresh snapshot instead of silently skipping history.
- Uses a fixed `through_cursor` watermark supplied by the caller so replay cannot chase a moving stream indefinitely.
- Empty intervals return without touching Redis.

## Tests added

- Fake-Redis unit tests cover multi-page global cursor advancement, unrelated-series filtering, missing first cursor, stream ending before the requested watermark, series/bar identity mismatch and empty interval.
- Real Redis 7 integration test covers bounded paging, exact-series filtering across unrelated instruments, and a deleted stream entry causing a fail-closed cursor-gap result.

## Explicit limits

- The reader is not yet called by the WebSocket endpoint.
- It does not establish the snapshot-to-live handoff by itself.
- It does not decide whether a client cursor predates the replica snapshot; caller must compare requested cursor, snapshot cursor and retention floor before replay.
- It does not replace Redis ACL setup or consumer event-loop dispatch.
- No worker startup integration, public WSS, Vercel/Cloudflare deployment, paid service or Termux use.

## Required next integration checks

1. Compare reconnect cursor with replica checkpoint cursor and retention floor; require resnapshot when expired or ahead.
2. Read bounded pages until the fixed replica watermark; enforce the existing maximum replay-event cap.
3. Register live subscription against the same in-memory replica watermark before yielding control to the event loop.
4. Drop queued live notifications at or below the replay completion cursor; preserve and resequence only newer events.
5. Verify queue overflow, Redis outage and retention gap all produce an explicit resnapshot path.
6. Add multi-ASGI integration tests before enabling startup.

## Verification

Source and test files were committed to the active feature branch. Exact-head CI is not yet confirmed by a successful workflow result in this checkpoint; do not treat this batch as CI-green until Automated Tests, CodeQL and the full-history secret audit report success for the final head.

## Indicator ledger impact

No indicator formula, provider data, chart rendering or indicator lifecycle changed. SMA20, EMA20, RSI14, MACD12/26/9 and Bollinger20,2 remain 🟨 Foundation; Shared Indicator Hook remains 🟨 Foundation; Footprint remains 🟧 Gated; Heatmap and Liquidation Maps remain 🟥 Not implemented. WebSocket replay work does not increase indicator progress.
