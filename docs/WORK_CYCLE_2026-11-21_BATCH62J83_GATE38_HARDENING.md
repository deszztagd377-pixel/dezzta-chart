# Work Cycle 62J-83 — Gate 38 collector hardening
**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base HEAD:** `b1e21f552182a720400cd9a2d276705834a41358`  
**Scope:** harden worker checkpoint capacity, retention visibility, and regression tests.  
**Cost:** zero; no deploy, no paid provider, no Termux, no `main` changes.

## Baseline verification
- Automated Tests run 44898947136: SUCCESS, 33/33 steps.
- CodeQL run 44898947150: SUCCESS.
- Full Git History Secret Audit run 44898947186: SUCCESS.

## Findings and changes
1. The original 256 worker-generation ceiling could block a replacement process if all saved checkpoints were younger than seven days, even though most were no longer live.
2. Under checkpoint-capacity pressure, the collector now evicts only the oldest stale checkpoints. It records their worker IDs in a separate seven-day tombstone table, preventing an evicted process ID from returning and replaying cumulative counters.
3. Tombstones are bounded at 4,096 rows. If no stale checkpoint can be safely evicted, or the tombstone ceiling is reached, the new worker is rejected. The collector degrades visibly; market-data paths remain independent.
4. Snapshot reads filter data older than seven days even if no new flush has run.
5. Aggregate-row capacity evictions are counted in a fixed metadata row and exposed through `capacity_evicted_rows_total`, alongside oldest bucket and effective retention.
6. Worker timestamps must be monotonic for a worker ID; timestamp regression is rejected transactionally.
7. Regression tests added for generation-cap eviction/tombstones, 16-live-worker enforcement, retention filtering without a subsequent flush, and timestamp regression.

## Capacity arithmetic
- Route series: 127 × 6 status classes = 762 request series.
- Latency series: 127.
- WebSocket lifecycle history: at most 10 scalar series.
- Conservative series ceiling: 900.
- Seven days at 15-minute resolution: 7 × 24 × 4 = 672 buckets.
- Aggregate planning bound: 900 × 672 = 604,800 rows.
- Aggregate table hard ceiling: 650,000 rows; headroom = 45,200 rows, approximately 7.47%.
- Worker checkpoint rows: at most 256, each stores a JSON snapshot.
- Retired-worker tombstones: at most 4,096, seven-day expiry.
- Metadata rows: one fixed row.
- Combined logical table-row ceiling at aggregate saturation: 650,000 + 256 + 4,096 + 1 = 654,353, excluding SQLite indexes and WAL pages.
- Serialized snapshot limit: 256 KiB. Live worker limit: 16. Stale threshold: 90 seconds.

The row ceiling is not a byte budget. Database/WAL byte limits remain benchmark-derived and host-specific.

## Gate 38 acceptance still outstanding
- Exact-head Automated Tests, CodeQL and full-history secret audit for this hardening commit.
- SQLite/WAL byte benchmark under 1/4/16 worker loads.
- Disk-full, read-only, corruption and lock-contention failure tests.
- Actual owner-host persistent-volume permissions, restart persistence, restore and retention evidence.
- Reverse-proxy/firewall restriction, operator token injection/rotation, acknowledgement/escalation and recovery drill.
- Multi-host aggregation remains unsupported.

## WebSocket and indicators
- No WebSocket wire protocol, auth, replay, snapshot, market-data payload or Redis guard behavior changed.
- Collector remains best-effort same-host telemetry. Unflushed in-memory increments can be lost on abrupt process termination; this is not financial accounting.
- No indicator formula, hook, data contract, renderer, UI or indicator test changed. No indicator progress credit.

## Project status
- Gate 38: 🟧 OPEN; repository implementation hardened, exact-head CI and owner-host acceptance pending.
- Gate 10: 0/10 formally closed.
- Stage 1: 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored.
- Indicator statuses remain unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
