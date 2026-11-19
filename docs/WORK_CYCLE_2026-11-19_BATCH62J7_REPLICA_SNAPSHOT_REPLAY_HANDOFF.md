# Batch 62J-7 — replica-consistent snapshot and bounded reconnect replay

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation  
**Scope:** Bind the replica SQLite read model to WebSocket subscription registration and provide a bounded replay operation through the replica's fixed applied cursor. No production startup wiring.

## Root cause discovered

The Redis consumer commits an event to replica SQLite before invoking the event-loop callback that updates the in-memory pipeline and WebSocket hub. A reconnect handler that reads the replica checkpoint but takes its bars from the in-memory pipeline can therefore pair a newer cursor with older bars.

The failure window is:
1. Consumer commits bar and advances replica checkpoint.
2. Consumer callback has not yet run on the asyncio loop.
3. WebSocket handler reads the new checkpoint but queries the stale in-memory pipeline.
4. Snapshot cursor claims the event is included, while snapshot bars do not include it.

## Fix

- Added OhlcvStreamHub.subscribe_snapshot_bars(): registers a subscription from bars supplied by an external durable read transaction, validating the exact ten-field series identity.
- Added subscribe_replica_snapshot(): calls SQLiteOhlcvReplicaStore.query_snapshot(), which reads bars and checkpoint in one SQLite read transaction, then registers the hub subscription synchronously using that exact cursor.
- The delayed callback for an event already represented by the snapshot is still allowed to update the in-memory pipeline, while the subscription cursor fence suppresses duplicate client delivery.
- A later event with a cursor above the snapshot checkpoint is delivered as a live update.
- Added strict bridge validation that the event's top-level series identity exactly matches its bar payload.
- Added a high-water equality check so a malformed replica read model cannot register a subscription with inconsistent cursor metadata.

## Bounded replay operation

Added replay_replica_history():
- Uses the replica checkpoint's source_id, applied_cursor, and retention_floor.
- Fixes the replay upper watermark to applied_cursor; events appended after that checkpoint are delivered through the live subscription.
- Rejects client cursors below retention floor or ahead of the replica checkpoint.
- Uses bounded pages and exact global cursor continuity while filtering one exact series.
- Caps matching replay events at 10,000 and global scanned entries at 50,000 by default.
- If Redis history is trimmed/gapped/corrupt or a work cap is exceeded, returns an all-or-resnapshot result with no partial events.
- Validates Redis client, stream key and exact series identity even when the requested interval is empty.

## Tests

- Fixed one test fixture whose timestamp was not aligned to its declared 1-minute timeframe. Production validation was preserved.
- Replica snapshot test simulates durable SQLite commit before callback, proves the returned snapshot includes the event at cursor 1, proves delayed callback updates the in-memory pipeline without duplicate queue delivery, then proves cursor 2 arrives as live.
- Mixed-series snapshot bars are rejected.
- Top-level event series/bar identity mismatch is rejected.
- Replay tests cover fixed watermark, unrelated global events, cursor expiry/ahead, matching-event cap, global scan cap and empty-interval input validation.
- Previous CI run on the pre-fix head reported 1,123 passed and one failed test due solely to the misaligned test fixture. The fix is in this batch; exact-head CI must pass before this batch is marked green.

## Remaining integration boundary

- The helpers are not yet wired into main.py.
- The caller must perform the replica snapshot read and hub registration synchronously on the owning event loop with no intervening await.
- Redis replay may run in a worker thread after subscription registration; live updates accumulate in the bounded queue while replay is sent.
- The caller must preserve the existing replay sequence merge behavior and close/resnapshot if the live queue overflows.
- Worker startup/shutdown, relay ACL, snapshot generation/group reset lifecycle, multi-ASGI WebSocket E2E and owner-side public WSS acceptance remain open.

## Gate 25 — preliminary Redis ACL command matrix

Derived from current relay code; this is a policy draft only, not a live ACL mutation:

| Principal | Required Redis commands | Purpose |
|---|---|---|
| Publisher | XADD, XRANGE | Append deterministic cursor ID and exact-ID read-back |
| Gateway consumer/replay | XGROUP CREATE, XAUTOCLAIM, XREADGROUP, XACK, XRANGE | Generation-scoped per-gateway delivery, pending recovery, ACK and reconnect replay |
| Snapshot maintenance | No runtime group-reset command required | Old generation groups are retired from use and cleaned separately under owner-controlled maintenance |

Important restrictions:
- Publisher and gateway credentials should be separate; scope each identity to the exact configured OHLCV stream key, not all keys.
- The stream key is injected into publisher/consumer constructors and is not yet a production configuration contract. Do not invent a key pattern or issue ACL commands until that contract is established.
- Do not grant all-command access, CONFIG, ACL, FLUSHALL, XDEL or XTRIM to runtime identities.
- Consumer groups now include a hash of the installed snapshot generation. After a snapshot replacement, the consumer switches to a new group at the new applied cursor; it does not destroy the previous group or its pending list. Runtime ACL therefore needs XGROUP CREATE but not XGROUP DESTROY.
- Previous generation groups remain in Redis until a separately authorized cleanup procedure verifies that no worker uses them. Do not grant runtime credentials XGROUP DESTROY merely to avoid this bounded maintenance task.
- Production transport must use TLS (rediss://) and owner-controlled credentials. Existing REDIS_URL belongs to shared HTTP/WebSocket guards and must not be broadened to serve the OHLCV relay.
- No ACL users, passwords, key names or remote Redis configuration were created or changed in this batch.

Gate 25 remains OPEN until owner-controlled Redis ACL/TLS, independent instances, lease/race behavior and outage/recovery are demonstrated in the target environment.

## Cost and project accounting

No paid services, Vercel/Cloudflare deployment, production secret changes or Termux work. No change to main. Indicator calculations and visual acceptance are unchanged; WebSocket infrastructure does not earn indicator progress or Gate closure.


## Batch 62J-8 — snapshot-generation consumer groups

The consumer group name now includes a stable hash of the replica snapshot generation. Reinstalling a snapshot moves the gateway to a new group starting at that snapshot's applied cursor. The old group's pending entries remain isolated and are not acknowledged or destroyed by the runtime consumer. The real-Redis test proves the new group has zero pending entries, the old group's pending entry remains intact, and the consumer continues from the next global cursor without invoking XGROUP DESTROY.

This reduces the steady-state gateway ACL surface by one destructive command. Stale group cleanup remains a separately authorized maintenance operation and must be bounded/observed before production rollout.
