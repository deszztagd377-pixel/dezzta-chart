# Batch 62J-11 — managed Redis gateway worker lifecycle

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Implementation

Added RedisOhlcvGatewayWorker:
- Owns one sequential consumer thread.
- Installs EventLoopCallbackDispatcher.dispatch as the consumer's on_event_applied callback.
- Runs synchronous Redis operations off the asyncio event-loop thread.
- Uses bounded exponential backoff for Redis/callback errors.
- Retries through the consumer's own-pending-first path after callback failures.
- Treats ReplicaResnapshotRequired as terminal and exposes state resnapshot_required; it cannot restart until a new worker is constructed against a verified snapshot.
- Exposes only state, error class name and result status; exception messages/Redis URLs/passwords are never exposed.
- Provides stop() and stop_async(); async shutdown joins the worker using asyncio.to_thread.
- Limits blocking XREADGROUP to at most 1 second so normal shutdown is bounded.
- Does not close the injected Redis client; application owner closes it after worker shutdown.

## Tests

- Unit tests cover start/run/stop, transient Redis outage recovery, terminal resnapshot state, safe callback installation, bounded blocking configuration and backoff validation.
- Real Redis 7 integration test verifies a worker thread consumes a stream event, dispatches fan-out onto the owning asyncio loop, the subscription receives cursor 1, Redis ACK completes, and shutdown leaves no pending entry.

## Deployment boundary

This worker is not wired into main.py/FastAPI lifespan. Before production integration, the application must:
1. Install/verify the global snapshot and replica checkpoint.
2. Hydrate all retained bars into the pipeline before worker start.
3. Construct the dispatcher on the app's owning event loop.
4. Use the dedicated gateway ACL identity and exact stream key.
5. Start one sequential worker per replica group.
6. On shutdown, await stop_async() and confirm success before closing Redis.
7. Surface resnapshot_required and require a new verified snapshot before restart.

The worker does not solve cross-host snapshot delivery, production configuration, owner ACL/TLS provisioning or multi-ASGI WebSocket E2E.

## Cost and progress

No production startup wiring, deployment, paid service, or Termux. Indicator calculations and visuals remain unchanged. Gate 25 remains open pending owner environment evidence.
