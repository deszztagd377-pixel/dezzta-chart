# Batch 62J-9 — Redis 7 relay ACL integration proof

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Purpose

Prove the minimum command and key permissions for the OHLCV relay using temporary Redis 7 ACL users in GitHub Actions. This does not provision or modify a production Redis account.

## Test topology

- Publisher ACL user: exact stream key only; XADD and XRANGE.
- Gateway ACL user: exact stream key only; XGROUP CREATE, XAUTOCLAIM, XREADGROUP, XACK and XRANGE.
- The source publisher writes one canonical event to Redis.
- The gateway consumer durably applies the event to its independent SQLite replica and ACKs it.
- The gateway replay reader reads the same event through XRANGE using only the gateway ACL identity.

## Negative authorization assertions

The integration test also verifies:
- Publisher cannot create consumer groups.
- Gateway cannot append events.
- Gateway cannot destroy a consumer group.
- Publisher cannot append to another key.
- Gateway cannot read another key.

The test generates ephemeral random ACL passwords and removes both temporary ACL users and test stream keys in a finally block. Credentials are not logged or persisted.

## Permission outcome

The steady-state command matrix is now supported by an executable Redis 7 integration test:
- Publisher: XADD, XRANGE.
- Gateway: XGROUP CREATE, XAUTOCLAIM, XREADGROUP, XACK, XRANGE.
- No runtime XGROUP DESTROY.
- Both users are scoped to the exact stream key.

## Remaining Gate 25 requirements

This CI proof does not close Gate 25. Still required:
- A defined production stream-key configuration contract.
- Separate owner-controlled publisher and gateway Redis URLs/ACL credentials.
- Production TLS endpoint and certificate validation.
- Owner environment provisioning and secret injection.
- Independent gateway instance/race and lease tests against the target Redis.
- Redis outage, recovery, stale pending and stream-retention drills.
- Safe maintenance procedure for retiring old snapshot-generation groups.

No production ACL users, secrets, Redis configuration or deployments were changed.


## Batch 62J-10 — pending-order guarantee

The consumer now retries entries pending under its own consumer name with XREADGROUP ID 0 before attempting XAUTOCLAIM or reading new entries. This closes a callback-failure ordering gap without waiting for the pending idle threshold. XREADGROUP was already included in the restricted gateway ACL, so no permission expansion is needed. The real Redis 7 regression test proves callback order [1, 1, 2] with a 30-second pending idle threshold.
