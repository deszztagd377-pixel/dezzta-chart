# Batch 62J-53 — Redis replica consumer ownership guard

**Branch:** `phase-2/market-data-foundation`  
**Scope:** one token-fenced Redis lease per generation-scoped replica consumer group.

## Implementation

- Startup acquires a unique lease using `SET NX PX` before group initialization or worker start.
- Lease keys are derived from the exact generation-scoped group name and use the dedicated `dezzta:ohlcv:gateway-lease:` namespace.
- Renewal, ownership checks, and release use token-comparison Lua scripts. A former owner cannot renew or release a successor's lease.
- A heartbeat renews at one-third of the TTL. A transient Redis transport error pauses consumption and retries verification without ACK; if the original token remains valid it renews and resumes. If the lease expired and another owner acquired it, token mismatch marks ownership lost. If the key is absent, the former owner may reacquire only with SET NX, so it cannot overwrite a successor.
- The consumer checks ownership before applying each event and again immediately before ACK. The worker fails closed when ownership cannot be proven.
- Shutdown releases only after the worker thread has stopped. If shutdown times out, the lease and Redis client are deliberately left intact.
- Snapshot generations naturally receive different lease keys, so a new generation is not blocked by an old-generation lease.

## ACL impact

The gateway ACL now additionally requires `SET`, `EVAL`, `GET`, `PEXPIRE`, and `DEL`, restricted to the lease-key namespace. Publisher permissions are unchanged. Lua scripts perform token-checked renewal and release; no `XGROUP DESTROY` permission is added.

## Validation

**Exact-head CI on `56317eff2b71886040acb998bf692814622feedf`:** Automated Tests [44774049019](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774049019) **SUCCESS** (frontend 245/245 across 29 files; backend 1,218 passed, 6 warnings, 35.76s); CodeQL [44774050265](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774050265) **SUCCESS**; Full Git History Secret Audit [44774048914](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44774048914) **SUCCESS**. Backend container build, Redis ACL/AOF + persistent-volume smoke test, bounded synthetic outbox benchmark, dependency audit and vulnerability scan/report export also passed. No skipped tests were reported in the backend pytest summary.


The Redis 7 test suite covers competing processes, independent replica groups, TTL takeover, stale-owner fencing, lease-loss detection, and generation separation. This is a CI-level ownership guard, not proof of protection against arbitrary host compromise or every possible process pause/Redis partition. During an outage the consumer does not apply or ACK new events until ownership can be verified again. Event application remains idempotent and ACK is guarded by a fresh ownership check, but the ownership check and subsequent ACK are separate Redis operations; the design does not claim a transaction spanning local SQLite, WebSocket fan-out, and Redis ACK.

## Operational boundary

No production Redis users, credentials, deployments, or paid services are modified by this batch. Gate 25 remains open pending owner-controlled TLS/ACL, persistence, outage and recovery drills.
