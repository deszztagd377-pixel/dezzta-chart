# Batch 62J-14 — production WebSocket route uses tested replay/live handoff

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Main route integration

The existing source-SQLite WebSocket reconnect path now uses OhlcvStreamHub.merge_replay_boundary() instead of maintaining a second inline queue-drain/resequence implementation.

Changes:
- Replay payloads are copied before adding streamId, sequence, emittedAtNs, cursor string and replayed flag. Canonical replay event objects retain their integer cursor for boundary validation.
- After replay messages are sent, the route synchronously merges the queued live events against replay_end_cursor.
- replay_complete is sent only after the handoff merge succeeds.
- On queue overflow, malformed cursor or series mismatch, the route sends resnapshot_required with a sanitized reason, closes with code 1013, and does not claim replay_complete.
- The endpoint's existing cleanup path still releases subscription and shared WebSocket lease.

## Tests

- Existing real endpoint regression test forces a live publish after the replay read and verifies replay sequences 1–4, replay_complete, then live sequence 5.
- New endpoint regression test forces handoff failure and verifies a sanitized resnapshot_required message followed by close code 1013; internal exception text is not exposed.
- The lower-level hub tests cover exact series identity, replay boundary filtering, live resequencing and queue overflow.

## Boundary

This integrates the tested helper into the current source-SQLite endpoint. The replica-backed Redis reader/snapshot helpers are still not wired into main.py because production snapshot transport, dedicated Redis URLs/ACL credentials and single-worker ownership are not yet established. No startup/deployment changes.

## CI and project status

Exact-head CI for this commit is required. No Vercel/Cloudflare deployment, paid service, or Termux. Stage 1 and Gate 10 accounting remain unchanged.
