# Work Cycle Batch 62J-85 — full-cardinality Gate 38 benchmark (21 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Source changes:** full-cardinality synthetic benchmark, benchmark contract test, transactional storage-write-failure regression.  
**Base source checkpoint:** `c8fc6ac6ebbf9a27f69c2ea8a4852336bc575d0f`  
**Latest source checkpoint:** `de104f388a4dd5c214567e911933d4c341bff570`  
**CI status at documentation time:** pending exact-head run; no pass is claimed yet.

## Work completed

1. Replaced the previous 12-series benchmark fixture with the complete declared logical-series envelope:
   - HTTP request counters: 127 routes × 6 status classes = 762.
   - HTTP latency histograms: 127.
   - WebSocket counters/classes: 4 scalar counters + 1 duration accumulator + 5 close-code classes = 10.
   - Total: 762 + 127 + 10 = **899 logical series**.
2. Kept the 1, 4 and 16 concurrent Python-thread cases and 32 flushes per worker by default. Each case verifies worker count, aggregate count, exact 899-series presence and SQLite `integrity_check=ok`.
3. Added serialized snapshot-size reporting against the existing 256 KiB input limit. The benchmark fails closed if the fixture exceeds that contract.
4. Added a transactional write-rejection test: a temporary SQLite trigger aborts an aggregate write; the test verifies the operation raises, removes the injected failure, retries the same cumulative snapshot and confirms the committed aggregate is exactly 4 rather than losing or double-counting the delta.
5. Kept the benchmark local and synthetic. It does not claim separate OS-process contention, a production volume, a disk-byte ceiling, multi-host operation or market-data performance.

## Capacity arithmetic

- Retention horizon: 7 days × 24 hours × 4 fifteen-minute buckets/hour = **672 buckets**.
- Full planned aggregate envelope: 899 × 672 = **604,128 aggregate rows**.
- Aggregate row cap: 650,000.
- Nominal row headroom: 650,000 − 604,128 = **45,872 rows**, equal to 7.06% of the cap (7.59% relative to the planned aggregate rows).
- Worker checkpoints, retired-worker tombstones, indexes, SQLite page overhead, WAL growth and filesystem metadata are separate storage costs. Therefore this row arithmetic is not a byte budget and cannot justify a database byte cap.
- The collector currently permits up to 900 series as a hard ceiling; the benchmark exercises the exact 899 series represented by the current source dimensions, leaving one series of schema-level headroom.

## Remaining Gate 38 work

- Separate OS-process contention benchmark.
- Explicit read-only-volume and actual disk-full behavior tests; the injected SQLite trigger is a transaction rollback test, not a disk-full simulation.
- Application-level acceptance proving collector failures never delay or fail HTTP/WebSocket traffic.
- Owner-host persistent-volume ownership, restart persistence, backup/restore, retention and disk-pressure recovery.
- Reverse-proxy/firewall restriction, operator visibility/access, acknowledgement/escalation and recovery drill.
- Do not infer production readiness or a byte cap from the synthetic CI benchmark.

## WebSocket boundary

No WebSocket protocol, auth, snapshot, replay, cursor, Redis publisher/consumer or market-data payload code was changed. Repository-side protocol/failure-matrix tests remain CI evidence only. Production WSS still requires the exact global snapshot artifact and authenticated gateway receipts, owner-host Redis TLS/ACL and persistence/failover, public HTTPS/WSS reverse proxy and real browser/Android WebView acceptance.

## Indicator ledger

No indicator formula, hook, data contract, renderer, UI or indicator test changed. No indicator progress credit is awarded. The full status and calculation ledger is maintained in `INDICATOR_PROGRESS_LEDGER.md`.

## Project / Gate 10 accounting

- Gate 10: **0/10 formally closed**.
- Stage 1: **30/40 criteria = 75% provisional**.
- Stages 2–6: unscored.
- Overall project percentage: unscored; approved aggregate weights and denominators do not exist.
- ZERO COST. No deployment, Vercel/Cloudflare operation, paid service, production credential, Termux/device operation or `main` modification.
