# Work Cycle 62J-1 — process-level publisher and gateway parity tests

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Code HEAD:** `ad1b2815e5cbd2034851b57e735ac89124d29e75`  
**Cost:** ZERO COST • existing GitHub Actions Redis 7 service • no deployment • no paid service • no Termux • `main` untouched.

## Scope

Extend 62I's real Redis consumer integration from a single test process to independent Python worker processes. The tests use the existing CI Redis service and temporary SQLite files; no external Redis host or credentials are introduced.

## Added tests

File: `backend/tests/test_ohlcv_redis_consumer.py`.

### 1. Two independent gateway consumer processes

- Parent creates one authoritative source and a verified global snapshot.
- Two separate replica SQLite databases are installed from the same snapshot.
- One canonical event is appended to one Redis Stream.
- Two spawned Python processes open their own replica database and Redis client.
- Each process creates its own stable replica-derived consumer group and consumes the same event.
- Both must return one applied event and durable applied cursor 1.

This proves Redis broadcast semantics across separate processes and independent local databases. It is not a full backend server/container/host deployment test.

### 2. Two independent publisher processes sharing one source lease

- Parent creates the authoritative source database, source checkpoint and one outbox event.
- Two spawned publisher processes open the same source/checkpoint database and separate Redis clients.
- A multiprocessing barrier starts both publisher attempts together.
- The SQLite fenced lease serializes publication.
- Exactly one process may advance cursor 1; the other may observe a busy lease or an already-empty page.
- Redis must contain exactly one deterministic entry, `1-0`, and the durable source checkpoint must equal 1.

This validates the lease/CAS protocol across independent processes, not merely two publisher objects in one event loop.

## Exact-head CI

At `ad1b2815e5cbd2034851b57e735ac89124d29e75`:

- Backend: **1,090 passed in 38.01s**.
- Frontend: **236 passed / 28 test files**.
- Frontend build and source/bundle secret scans passed.
- Backend dependency audit: no known vulnerabilities reported.
- Backend container build and Redis/persistent-volume smoke passed.
- CodeQL Python and JavaScript/TypeScript passed.
- Full Git History Secret Audit passed.
- Container vulnerability report generated and uploaded.

Runs: [Automated Tests 44545057500](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44545057500), [CodeQL 44545057428](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44545057428), [Secret Audit 44545057657](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44545057657).

## Remaining integration boundaries

- These tests do not start two ASGI backend servers or containers.
- The consumer is not wired to `main.py` or a worker supervisor.
- Durable replica apply is not yet forwarded into the gateway's `OhlcvPipeline` and `OhlcvStreamHub`.
- No public WSS, browser, Android WebView, two-host network or owner-operated Redis acceptance is claimed.
- No stream trimming, deployment, paid infrastructure or Termux work.

## Next batch — 62J-2 / 62J-3

1. Hydrate the gateway's in-memory pipeline from the durable replica SQLite read model after restart.
2. Forward each committed event into the local `OhlcvStreamHub` with durable cursor/event identity.
3. Ensure replay/duplicate forwarding cannot double-notify subscribers; queue overflow must require a fresh snapshot rather than silently dropping events.
4. Test snapshot-to-live handoff, local hub cursor continuity, restart hydration, Redis outage/recovery and two separate ASGI processes before considering startup integration.

## Project and indicator accounting

No indicator implementation changed. The full colored formula/status ledger remains in `docs/INDICATOR_PROGRESS_LEDGER.md`.

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED; M1–M8 weights are unapproved.

Worker-level CI evidence does not close owner-side Gate 25 or Gate 36.
