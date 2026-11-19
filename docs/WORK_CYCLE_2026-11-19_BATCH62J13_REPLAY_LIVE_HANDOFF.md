# Batch 62J-13 — snapshot/replay/live handoff

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Change

Added OhlcvStreamHub.merge_replay_boundary():
- Validates that the subscription is active and has not overflowed.
- Validates replay event cursors are strictly increasing, within the fixed replay boundary, and match the subscription's exact ten-field series identity.
- Drains queued live messages that arrived while replay was read/sent.
- Discards live messages at or below the replay boundary because those events are already represented in replay.
- Resequences only live messages above the boundary after the replay event count.
- Preserves the latest durable cursor and updates the subscription watermark.
- Fails closed and requires resnapshot for queue overflow, malformed durable cursor or out-of-order live messages.

## Real Redis 7 integration proof

The new integration test:
1. Publishes cursor 1 to Redis and installs a global replica snapshot at cursor 1.
2. Hydrates the in-memory pipeline and registers a hub subscription from the atomic replica snapshot.
3. Publishes cursor 2 after the snapshot.
4. Reads replay through the fixed cursor-1 replica checkpoint while the gateway worker consumes cursor 2.
5. Verifies replay contains only cursor 1.
6. Verifies cursor 2 is queued live, then merge_replay_boundary resequences it to sequence 2.
7. Verifies final replica cursor 2 and no pending Redis entries after ACK.

Unit tests additionally verify stale queued messages are discarded, newer messages are resequenced, wrong-series replay is rejected, and queue overflow requires resnapshot.

## Integration boundary

The helper is not wired into main.py yet. The WebSocket handler must send replay events, call merge_replay_boundary synchronously on the event loop, then resume live queue delivery. Any overflow or validation error requires a fresh snapshot. No production startup or public WSS activation.

## Gate and cost

This strengthens Gate 25 transport correctness evidence but does not close it. Owner TLS/ACL provisioning, multi-ASGI target test, outage recovery, and external public WSS remain open. No deployment, paid service or Termux.
