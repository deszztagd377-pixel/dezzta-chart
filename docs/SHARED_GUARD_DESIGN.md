# Redis shared security guard

## Production requirements
- `REDIS_URL` is mandatory for `APP_ENV=production`; production URLs require
  `rediss://` TLS.
- Redis is pinged before serving traffic. Startup fails if unavailable.
- Redis errors during HTTP checks return 503; rate-limit rejections return 429.
- Redis errors or exhausted WebSocket capacity close with code 1013.
- No process-local fallback is used when Redis is configured.

## Atomic operations
- One Lua script increments hashed-client and global HTTP minute buckets.
- WebSocket sorted-set leases reserve global capacity before accept, then
  per-account capacity only after Firebase verifies identity.
- Account subjects are SHA-256 hashed in Redis keys.
- Leases expire after worker failure and active sockets renew every one-third
  of the lease duration. Disconnects explicitly release leases.

## Initial defaults
| Control | Default |
| --- | ---: |
| HTTP requests per client per minute | 120 |
| Global HTTP requests per minute | 6,000 |
| Concurrent WebSockets globally | 500 |
| Concurrent WebSockets per account | 5 |
| WebSocket lease duration | 45 seconds |

These are initial guardrails, not load-tested capacity guarantees.

## Environment
Set `REDIS_URL` as a backend secret, never in frontend variables or source
control. Managed Redis should provide a TLS URL. Development/test may omit
Redis; then shared protection is inactive and must not be described as
production-protected.

Optional limits: `HTTP_RATE_LIMIT_PER_CLIENT`, `HTTP_RATE_LIMIT_GLOBAL`,
`WEBSOCKET_CONNECTION_LIMIT_GLOBAL`,
`WEBSOCKET_CONNECTION_LIMIT_PER_ACCOUNT`, `WEBSOCKET_LEASE_SECONDS`.

No Firebase token or raw account subject is stored in Redis. Arbitrary
`X-Forwarded-For` headers are not trusted; the ASGI peer address is used until
trusted-proxy configuration is explicitly reviewed.
