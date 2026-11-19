# Batch 62J-12 — dedicated OHLCV Redis relay configuration

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Configuration contract

Added OhlcvRedisRelayConfig, intentionally separate from the existing Settings.redis_url used by shared HTTP/WebSocket security guards.

Environment variables:
- OHLCV_REDIS_ENABLED — opt-in; defaults false.
- OHLCV_REDIS_STREAM_KEY — exact stream key; defaults to dezzta:market-data:ohlcv:v1.
- OHLCV_REDIS_PUBLISH_URL — dedicated publisher ACL URL.
- OHLCV_REDIS_GATEWAY_URL — dedicated gateway ACL URL.

Validation:
- Publisher and gateway URLs require distinct ACL usernames and distinct passwords.
- Both URLs require ACL credentials.
- Production requires rediss:// TLS.
- Only Redis database 0 is accepted to avoid SELECT permission.
- Stream key must be exact, non-empty, and contain no whitespace or Redis glob characters.
- URL query/fragment components are rejected.
- URL fields are repr-hidden to reduce accidental secret exposure.
- Relay remains disabled by default.

Least-privilege command contract:
- Publisher: XADD, XRANGE.
- Gateway: XGROUP CREATE, XAUTOCLAIM, XREADGROUP, XACK, XRANGE.
- No XGROUP DESTROY, XDEL, XTRIM, CONFIG, ACL or broad command categories for runtime identities.

## Tests

Unit tests cover disabled default, required URLs, TLS enforcement, distinct credentials, exact stream-key restrictions, database 0, ambiguous enable flag, command allowlists and repr secret redaction.

## Integration boundary

This configuration is not wired into main.py or FastAPI lifespan. No Redis client was created and no owner secrets were accessed. Production startup remains gated on snapshot delivery, owner ACL/TLS provisioning, worker shutdown supervision and multi-ASGI E2E.

## Cost and progress

No paid service, deployment or Termux. Gate 25 remains OPEN; Stage 1 and indicator statuses are unchanged.
