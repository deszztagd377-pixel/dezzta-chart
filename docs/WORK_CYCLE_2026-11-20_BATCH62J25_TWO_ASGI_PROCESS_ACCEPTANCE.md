# Work Cycle 62J-25 — two independent ASGI gateway process acceptance

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Parent code:** 0057bb2baf37628430aea04803b50d9bbb69a449  
**Scope:** real two-process ASGI + Redis 7 + independent SQLite replicas + actual WebSocket route.

## Test topology

- One source SQLite store and one empty global snapshot fixture.
- Two independently spawned operating-system processes, each running its own Uvicorn/FastAPI server.
- Two separate replica SQLite files and separate instrument-registry databases.
- Two separate Redis clients and consumer identities using the same Redis 7 stream.
- Each gateway authenticates a client and subscribes through /ws/market-data before the source event is appended.
- One source event is appended once; both WebSocket clients must receive the same durable cursor and both replica checkpoints must advance.

## Acceptance assertions

1. Both ASGI health endpoints become ready only after their replica snapshot hydration and Redis group bootstrap.
2. Both WebSocket handshakes authenticate and return the expected status.
3. Both subscriptions receive a replica-backed snapshot at cursor 0.
4. One source event is appended to the shared Redis stream.
5. Both actual WebSocket routes emit market_data.ohlcv.update at cursor 1.
6. Both independent SQLite replica checkpoints equal 1 after delivery.
7. Processes, WebSockets and Redis resources are cleaned up in a bounded finally block.

## Cost and safety

Uses the existing CI Redis 7 service and temporary local SQLite files only. No Vercel/Cloudflare deployment, paid service, public WSS, main branch change or Termux operation.

CI must pass on the exact resulting commit before this acceptance is marked verified. Indicator progress is unchanged.
