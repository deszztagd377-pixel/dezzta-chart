# Work Cycle 62H-3 / 62H-4 / 62I — Redis integration, retention recovery and per-gateway consumer

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code HEAD:** `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`  
**Cost:** ZERO COST • GitHub Actions Redis 7 service only • no paid services • no deployment • no Vercel/Cloudflare push • no Termux • `main` untouched.

## Batch 62H-3 — real Redis integration

Added five tests to `backend/tests/test_ohlcv_redis_publisher.py`, using the existing `REDIS_TEST_URL` GitHub Actions service:

1. Real Redis deterministic IDs `1-0`, `2-0`, source/event identity and canonical payload.
2. Redis commits XADD but the client loses the reply; exact-ID read-back verifies it.
3. Existing deterministic ID with different source/event/payload fails closed.
4. If XADD outcome is uncertain and read-back is unavailable, SQLite checkpoint does not advance; a later publisher recovers the existing exact entry.
5. A newly created Redis client can verify the committed stream entry.

No fake production service, credentials or new infrastructure were added.

**Exact-head validation at `95b00d0432aef2a680adf52d5566577689ca6db9`:**
- Backend **1,080 passed**.
- Frontend **236 passed / 28 files**.
- Container build and Redis/persistent-volume smoke passed.
- CodeQL and full-history secret audit passed.
- Backend dependency audit reported no known vulnerabilities.
- Container vulnerability report was generated and uploaded.

Runs: [Automated Tests 44540975426](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44540975426), [CodeQL 44540975475](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44540975475), [Secret Audit 44540975627](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44540975627).

## Batch 62H-4 — publisher snapshot rebase blocker

Code review found that publisher correctly stopped when source outbox retention overtook its cursor, but the existing checkpoint API could only initialize once and had no safe recovery path after installing a fresh snapshot. That left a legitimate recovery dead-end.

Added `SQLiteOhlcvPublisherCheckpoint.rebase_from_snapshot()` and three tests.

Safety rules:
- Snapshot cursor must be within the current source retention floor/high-water window.
- Caller supplies the expected previous cursor; update is compare-and-swap protected.
- Snapshot cursor cannot move backward.
- A live publisher lease blocks the operation.
- Expired ownership is cleared and fencing epoch increments, invalidating stale workers.
- Checkpoint records the snapshot watermark and deterministic boundary `<cursor>-0`.
- Caller must install the matching snapshot on the affected replica(s) before invoking the rebase.

**Exact-head validation at `3cd58f4a4172b5b36316233518ab5e1e0ddcfffd`:**
- Backend **1,083 passed**.
- Frontend **236 passed / 28 files**.
- Container build/smoke, CodeQL and secret audit passed.

Runs: [Automated Tests 44542026867](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44542026867), [CodeQL 44542027029](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44542027029), [Secret Audit 44542026910](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44542026910).

## Batch 62I — per-gateway Redis Streams consumer

Added:
- `backend/app/ohlcv_redis_consumer.py`
- `backend/tests/test_ohlcv_redis_consumer.py`

Protocol:
1. Consumer requires an installed replica snapshot and binds to its source ID.
2. Consumer group name is deterministic from persistent `replica_id` plus source identity, so gateways have independent broadcast groups rather than load-balancing through one shared group.
3. A new group begins at the replica's applied snapshot cursor. Existing groups are preserved on restart.
4. Consumer first calls `XAUTOCLAIM` for abandoned pending entries, then reads new entries with `XREADGROUP`.
5. Each entry is checked for exact field schema, source ID, canonical JSON, event ID, cursor and deterministic Stream ID.
6. `SQLiteOhlcvReplicaStore.apply_replica_event()` commits the local bar, dedupe record and checkpoint atomically.
7. Only `applied`, `duplicate` and `stale` results are ACKed. A gap or retention error raises `ReplicaResnapshotRequired` and remains pending.
8. If a snapshot is installed, `reset_group_after_snapshot()` destroys/recreates that gateway's group at the new snapshot watermark. The worker must be quiesced during reset.
9. ACK failure after durable apply is safe: the message remains pending and replay is recognized as a duplicate before ACK.

Five real Redis tests cover:
- Durable local apply before ACK.
- Lost ACK reply, pending reclaim by a restarted consumer, duplicate apply and eventual ACK.
- Cursor gap remains pending and unacknowledged.
- Two separate replica databases each receive the same event through independent groups.
- Snapshot installation plus group reset discards obsolete pending delivery and resumes at the new watermark.

**Exact-head validation at `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`:**
- Backend **1,088 passed in 32.15s**.
- Frontend **236 passed / 28 files**.
- Frontend build and credential scans passed.
- Backend dependency audit reported no known vulnerabilities.
- Container build, Redis ACL/AOF and persistent-volume smoke passed.
- CodeQL Python and JavaScript/TypeScript passed.
- Full Git History Secret Audit passed.
- Container vulnerability report generated and uploaded.

Runs: [Automated Tests 44543198371](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44543198371), [CodeQL 44543198283](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44543198283), [Secret Audit 44543198433](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44543198433).

## Boundaries retained

- Publisher and consumer are deliberately not started by `main.py`.
- No production Redis URL, ACL, secret or hosted service is introduced.
- No MAXLEN stream trimming.
- No actual two-process or two-host gateway test yet. Two independent replica databases/groups are tested in one CI process.
- No forwarding from replica apply into `OhlcvStreamHub` yet.
- Redis Server must be at least 6.2 for `XAUTOCLAIM`; CI uses Redis 7.
- No deploy, paid service, Termux, or main-branch change.

## Next work — 62J

- Add worker lifecycle/supervision without starting it by default.
- Verify two independent backend processes with separate SQLite replica databases and independent Redis groups.
- Exercise Redis disconnect/reconnect, consumer restart, publisher restart, pending reclaim, snapshot rebase and cursor parity.
- Connect durable replica apply to local `OhlcvStreamHub` only after idempotency/order behavior is tested.
- Add end-to-end bounded fan-out and replay tests before any startup integration.

## Indicator and Gate 10 accounting

No indicator implementation changed in these batches. The complete colored ledger remains at `docs/INDICATOR_PROGRESS_LEDGER.md`; formulas, first-valid indexes, remaining UI work and Footprint/Heatmap/Liquidation gates are unchanged.

- Stage 1: **75% provisional** (30/40 criteria; 300/400 ticks).
- Gate 10: **0/10 formally closed**; all ten remain OPEN.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED; M1–M8 weights remain unapproved.

CI is repository evidence, not owner-side Gate 8/20/25/30/31/34/35/36/38/39 acceptance.
