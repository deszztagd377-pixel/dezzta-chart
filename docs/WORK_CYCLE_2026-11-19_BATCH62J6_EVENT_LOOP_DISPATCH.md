# Batch 62J-6 — event-loop-safe replica callback dispatch

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Scope:** Provide a synchronous worker-to-asyncio callback adapter. No production startup wiring.

## Problem

The Redis replica consumer is synchronous, while `OhlcvPipeline` and `OhlcvStreamHub` are event-loop confined. Calling the bridge directly from a Redis worker thread would violate the hub's ownership model. ACK must wait until the loop-owned callback completes.

## Implementation

Added `backend/app/ohlcv_event_loop.py` with `EventLoopCallbackDispatcher`:

- Captures the owning running asyncio loop and a callback.
- Schedules callback execution using `asyncio.run_coroutine_threadsafe`.
- Supports synchronous and awaitable callbacks.
- Blocks the Redis worker until callback completion, preserving apply → callback/fan-out → ACK order.
- Propagates callback exceptions so consumer ACK is not reached.
- Rejects calls from the owner loop thread to prevent self-deadlock.
- Rejects closed/stopped loops and validates a finite positive timeout.
- On timeout, cancels the scheduled future and raises; caller must not ACK. A callback that has already begun may complete after timeout, so retry idempotency via the durable cursor fence remains mandatory.

## Tests

- Callback runs on the owner event-loop thread even when invoked from a worker thread.
- Async callback is awaited before dispatch returns.
- Callback exceptions propagate to the synchronous caller.
- Same-loop synchronous invocation is rejected.
- Closed-loop construction is rejected.
- Real Redis 7 integration test connects the dispatcher to `forward_replica_event`, proving consumer processing waits for local hub fan-out before ACK.

## Integration boundary

The dispatcher is not wired into `main.py` or a production worker lifecycle. Before startup wiring, add explicit shutdown/drain semantics, worker thread lifecycle, Redis ACL isolation, replica replay integration and multi-ASGI end-to-end tests. A timeout cannot forcibly stop a synchronous callback already executing on the event loop; durable idempotency is required.

## Cost and indicator accounting

No paid service, deployment, Cloudflare/Vercel action, or Termux requirement. No indicator formula or chart UI changed. Indicator statuses remain unchanged; WebSocket transport tests do not award indicator progress or Gate 10 acceptance.
