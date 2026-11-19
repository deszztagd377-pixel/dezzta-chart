# Batch 62J-10 — same-consumer pending retry ordering

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Failure mode

A callback can fail after replica SQLite has committed but before Redis ACK. The entry remains pending under the same consumer name. If the next consume_once() call waits for XAUTOCLAIM's min_idle_ms before retrying that worker's own pending entry, it can read a later new entry with XREADGROUP ">" first. That can advance the durable cursor and fan out a later event before the earlier callback is retried.

## Fix

RedisOhlcvReplicaConsumer.consume_once() now checks the current consumer's own pending list with XREADGROUP using ID "0" immediately after ensure_group(). If any own pending entries exist, it applies/retries and ACKs those entries before attempting XAUTOCLAIM for abandoned entries owned by other consumers or reading new entries.

This preserves:
- Retry of the same worker's callback-failed entry without waiting for the idle threshold.
- Strict cursor order before reading new entries.
- Existing XAUTOCLAIM recovery for entries abandoned by another process.
- Existing apply → callback → ACK ordering.
- Existing snapshot-generation group isolation and least-privilege ACL; XREADGROUP was already required by the gateway role.

## Regression test

The real Redis 7 test:
1. Delivers cursor 1 and forces its callback to fail after replica commit.
2. Keeps pending_idle_ms at 30 seconds.
3. Publishes cursor 2 before that idle threshold expires.
4. Calls consume_once() again and proves cursor 1 is retried/ACKed first.
5. Verifies cursor 2 is not applied until the following consume cycle.
6. Verifies callback order [1, 1, 2] and replica cursor order 1 then 2.

No idle threshold was weakened and no production assertion was removed.

## Gate 25 / cost

No additional Redis command permission is needed; XREADGROUP is already in the gateway ACL. No production ACL changes, credentials, deployments, paid services or Termux. Gate 25 remains open pending owner environment/TLS/ACL evidence.
