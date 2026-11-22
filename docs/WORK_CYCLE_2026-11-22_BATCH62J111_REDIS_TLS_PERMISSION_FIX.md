# Batch 62J-111 — Redis TLS CI fixture permission correction

**Parent:** `fc13d6ed302c8eccd1fc4cf18102b2c50b66fd5c`  
**Scope:** fix the exact CI fixture failure without changing production behavior.

## Observed failure

The first real TLS integration attempt generated the certificates successfully and started the Redis container. Redis 7.4.12 then aborted with:

`Error loading ACLs, opening file '/tls/users.acl': Permission denied`

The read-only bind mount preserved runner ownership and mode 0600, while Redis ran as its unprivileged image user. The fixture therefore failed before a TLS handshake was attempted. This is a test-fixture permission failure, not evidence for or against the application TLS verification logic.

## Correction

The workflow now queries the UID/GID of the `redis` account from the exact `redis:7-alpine` image used by the fixture. It assigns only `server.key` and `users.acl` to that account, retains mode 0600, and makes the public CA/server certificates readable. The CA private key and untrusted-CA private key remain mode 0600 and are not needed by the Redis process. The mount remains read-only and the listener remains TLS-only.

## Security boundaries

- No private production key, password, CA or deployment credential is introduced.
- Test-only private keys and ACL credentials are generated per CI run.
- Redis remains loopback-bound, with plaintext port disabled.
- No production code, public service, OCI resource, Termux command, paid service or `main` branch is changed.

## Acceptance

This patch is not considered accepted until a new exact-head CI run completes:
1. Redis TLS fixture starts with the ACL file loaded.
2. Trusted CA and matching hostname succeed.
3. Wrong CA, wrong hostname and plaintext access fail.
4. Real RedisSharedGuard HTTP and WebSocket operations succeed over TLS.
5. Full existing backend/frontend/build/security workflows pass.

Gate 10 remains open; production WSS remains unprovisioned and unverified.
