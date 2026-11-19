# Work Cycle 62H-2 — deterministic Redis Streams publisher

**Date:** 19 November 2026  
**Branch:** \`phase-2/market-data-foundation\`  
**Implementation commit:** \`9072632abd6658caacb82be233b23d00f34fadcf\`  
**Regression-test commit:** \`1b9b1c4bce4fc23abe69bb4cb58abaf6c5fdae56\`  
**Import-fix commit:** \`f1f998a8659d206c797bdfac14b110a3849d4d68\`  
**Exact-head CI:** Automated Tests run \`44538993402\`; CodeQL run \`44538993277\`; Full Git History Secret Audit run \`44538993352\`.  
**Cost:** ZERO COST. No paid service, no deployment, no Vercel/Cloudflare push, no Termux. \`main\` untouched.

## Objective

Implement the transport boundary between the authoritative global SQLite OHLCV outbox and Redis Streams without wiring it into FastAPI startup. Preserve the approved contract: deterministic cursor IDs, exact retry verification, fenced publisher ownership, no checkpoint advancement before append confirmation, and explicit resnapshot on source retention expiry.

## Code delivered

File: \`backend/app/ohlcv_redis_publisher.py\`

Added:

- \`RedisOhlcvStreamAppender\`: synchronous Redis Streams adapter; accepts an injected Redis client and does not create a new paid service or alter the existing Redis security guard.
- \`RedisStreamConflict\`: hard-fails when an existing deterministic ID contains a different source ID, event ID, or canonical payload.
- \`RedisAppendUnconfirmed\`: reports an uncertain append outcome when Redis cannot be queried to establish whether an append committed. The checkpoint remains unchanged.
- \`RedisOhlcvPublisher\`: bounded publisher loop using the existing global \`read_outbox_batch()\`, durable SQLite checkpoint, lease renewal and fencing epoch.

### Append and retry protocol

1. Read the current durable publisher cursor and a bounded global outbox page.
2. Renew the source-local SQLite lease and confirm the fencing epoch before each event.
3. Serialize the complete event as canonical JSON: sorted keys, compact separators, UTF-8, and non-finite JSON values rejected.
4. Append with Redis Stream ID exactly \`<cursor>-0\`. Fields include \`source_id\`, \`event_id\`, and canonical \`payload\`.
5. If XADD raises, read back only the exact deterministic Stream ID. Accept it only if all three stored fields exactly match. A mismatch is a hard conflict. If read-back is unavailable, report an uncertain outcome and do not advance SQLite.
6. Call \`record_confirmed_append()\` only after XADD success or exact read-back confirmation. The checkpoint enforces contiguous cursor, authoritative source-event equality, lease epoch, expiry and compare-and-swap.
7. If the source retention floor has overtaken the checkpoint, stop and require a fresh global snapshot. No silent cursor skip.
8. Do not use MAXLEN trimming.

The delivery guarantee is at-least-once with deterministic, verifiable replay. A crash after XADD and before checkpoint commit is recovered by retrying the same Stream ID and validating the existing entry.

## Regression tests

File: \`backend/tests/test_ohlcv_redis_publisher.py\`

Seven new publisher tests cover:

1. Ordered multi-event append and checkpoint advancement.
2. Redis committed XADD but the client lost the reply.
3. Process crash after append but before checkpoint, followed by exact-ID recovery.
4. Existing deterministic ID with conflicting source/event/payload.
5. Redis outage and uncertain append outcome without checkpoint advancement.
6. Source retention overtaking the publisher cursor, requiring a new snapshot.
7. Another publisher holding the lease; no event is appended.

The fake Redis implementation is local and deterministic. No production Redis credentials or paid infrastructure are used.

## CI failure and immediate correction

The first 62H-2 backend run exposed one shared implementation omission: the new canonical serializer used Python's \`json\` module without importing it. Five tests failed at that same line; the other 1,070 tests passed. Added the missing standard-library import in \`f1f998a8659d206c797bdfac14b110a3849d4d68\`. No algorithm or validation was weakened.

## Exact-head verification

At commit \`f1f998a8659d206c797bdfac14b110a3849d4d68\`:

- Backend: **1,075 passed**.
- Frontend: **236 passed across 28 test files**.
- Frontend production build and source/bundle secret scans: passed.
- Backend container build: passed.
- Container smoke: passed, including Redis ACL authentication, Redis AOF persistence across restart, API fail-closed outage behavior, backend reconnection, non-root execution, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit rejection.
- CodeQL Python and JavaScript/TypeScript: passed.
- Full Git History Secret Audit: passed.
- Container vulnerability report: generated and uploaded as workflow artifact. Do not infer an owner-host security acceptance gate from this CI artifact.

Workflow: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44538993402

## Explicit non-deliverables / safety boundaries

- No publisher is started by \`main.py\`; no startup integration.
- No consumer group, pending reclaim, ACK, multi-process fan-out or local hub forwarding in this batch.
- No Redis ACL changes for the OHLCV stream.
- No stream trimming / MAXLEN.
- No production Redis endpoint, secret, or credential is introduced.
- The existing RedisSharedGuard remains a separate HTTP/WebSocket security component.
- No deployment, hosting change, Vercel/Cloudflare push, Termux work, or paid service.

## Next dependency-ordered work

- **62H-3:** real Redis integration tests for deterministic IDs, duplicate ID read-back, wrong payload conflict, Redis unavailable, restart and no checkpoint advancement. Use the repository's existing CI Redis service only.
- **62I:** independent consumer group per gateway, pending reclaim, apply-before-ACK, dedupe and crash recovery.
- **62J:** two independent backend processes and local replica databases; verify cursor parity, outage/recovery and no loss/duplication.
- **62K:** owner-side Gate 25/36 acceptance only with actual owner-managed Redis ACL/TLS, independently deployed instances and external WSS/browser evidence.

No Stage ticks or Gate closures are awarded by this implementation or CI.

