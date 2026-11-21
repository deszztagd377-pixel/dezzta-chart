# Work Cycle Batch 62J-87 — bounded SQLite writer-lock acquisition

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test commit:** `c95a9a19091a5881136144491937073ba7fcb767`  
**CI:** exact-head results pending after documentation commit.

## Failure evidence

Automated Tests run [44902861326](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44902861326) failed on the 16-worker full-cardinality benchmark at `db.execute("BEGIN IMMEDIATE")` with `sqlite3.OperationalError: database is locked`. Schema initialization had already completed; this was the separate single-writer transaction lock.

## Correction

- Add up to eight bounded retries around `BEGIN IMMEDIATE`, retrying only SQLite lock errors.
- Retain the 250 ms busy timeout; apply bounded exponential backoff between retry attempts.
- Expose `lock_retries` in each successful flush result and aggregate the count in benchmark evidence.
- Add a regression test that holds a writer lock for 350 ms, then releases it; assert successful flush, a recorded retry, and exactly-once aggregate delta.

## Acceptance limits

- Previous exact-head Automated Tests failed; CodeQL and secret-history audit passed only on predecessor SHA `73a19e5db54b44d1d07caa038ec567d31d19a0a8`.
- New source/test SHA `c95a9a19091a5881136144491937073ba7fcb767`; documentation commit follows. Exact-head CI pending.
- 899 logical series; 1/4/16 Python threads; 32 flushes per worker. Separate OS processes are not covered.
- Gate 38 remains 🟧 OPEN pending exact-head CI, process-level contention, physical read-only/disk-full tests, app-level HTTP/WebSocket isolation, and owner-host retention/backup/operator acceptance.
- WebSocket data path unchanged; production WSS remains host-gated.
- Indicators unchanged; no credit. Gate 10 remains 0/10 formally closed; Stage 1 30/40 = 75% provisional; overall project remains unscored.

ZERO COST. No deployment, Vercel/Cloudflare operation, paid provider, production credentials, Termux/device operation or `main` modification.
