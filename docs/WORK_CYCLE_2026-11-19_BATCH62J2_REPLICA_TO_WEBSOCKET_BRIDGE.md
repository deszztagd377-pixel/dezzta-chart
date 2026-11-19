# Work Cycle 62J-2 — durable replica to local WebSocket bridge

**Date:** 19 November 2026  
**Branch:** \`phase-2/market-data-foundation\`  
**Parent code HEAD:** \`a3b43b0c8dbf8cecbaef8a17d508defbf287d1ec\`  
**Scope:** local library and callback integration only. This batch does not start Redis workers from \`main.py\`.

## Problem addressed

Before this batch, Redis consumer events committed to the gateway's replica SQLite database, but the local \`OhlcvPipeline\` and \`OhlcvStreamHub\` were not updated from those durable events. A process restart could therefore leave the in-memory WebSocket read model empty even though the replica database was current.

## Implementation

### 1. Durable hydration

New \`backend/app/ohlcv_replica_bridge.py\` provides \`hydrate_replica_pipeline()\`:
- Requires an installed, verified replica checkpoint.
- Loads all retained bars from the replica read model.
- Atomically replaces the in-memory pipeline snapshot.
- Returns retained bar count, applied global cursor and retention floor.
- Does not invent bars or read from a provider.

### 2. Durable event fan-out

\`forward_replica_event()\` reconstructs a validated \`OhlcvBar\` from the canonical event envelope, applies it to the in-memory pipeline and publishes it to the local \`OhlcvStreamHub\` with the source event's global cursor and event ID.

A pipeline conflict/stale/expired result raises an explicit divergence error. It is not silently discarded.

### 3. ACK ordering and idempotency

\`RedisOhlcvReplicaConsumer\` accepts an optional synchronous \`on_event_applied\` callback. For \`applied\` and \`duplicate\` events, it calls the callback after the durable SQLite transaction and before Redis ACK.

The hub now suppresses a durable cursor already observed by a subscription. This closes the retry case where:
1. SQLite replica commit succeeds.
2. Local pipeline/hub callback succeeds.
3. Redis ACK reply is lost.
4. Redis redelivers the pending event.

The pipeline returns \`duplicate\`, the hub sees that the subscription cursor has already advanced, and no second WebSocket message is queued. If callback fails before fan-out, the event remains pending; restart hydration restores the committed replica snapshot.

### 4. Tests

New \`backend/tests/test_ohlcv_replica_bridge.py\` covers:
- Snapshot hydration and cursor restoration.
- First live event fan-out with durable cursor/event ID.
- Duplicate event retry suppression.
- Old pending event suppression after snapshot hydration.
- Explicit pipeline divergence instead of silent drop.

## Safety boundary

- No Redis consumer/publisher startup wiring in \`main.py\`.
- No production Redis endpoint or credentials.
- No Vercel/Cloudflare deployment.
- No stream trimming or MAXLEN.
- No claim of two-host, public WSS, Android WebView or owner Gate 25/36 acceptance.
- No Termux work.
- \`main\` untouched.

## Validation

CI is pending for the exact commit. Do not treat this report as passed until Automated Tests, CodeQL and Full Git History Secret Audit complete successfully.

## Next

62J-3 should add end-to-end tests that exercise callback ordering through the real Redis consumer, including ACK-reply loss, callback failure/no-ACK, restart hydration, and multiple subscriber cursors. Only after those pass should a separate startup/lifecycle blueprint be reviewed; no production worker should be enabled by this batch.
