# Work Cycle 62J-84 — Gate 38 collector failure paths and SQLite benchmark

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Commit:** `92119a8dc05690e6492aab160662c9e36c839cad`  
**Scope:** Gate 38 repository-side failure-path coverage and initial 1/4/16-worker benchmark.  
**Cost:** zero; no deployment, no paid provider, no Termux/device work, no production credentials, no `main` modification.

## Source changes

1. Extended `backend/tests/test_metrics_collector.py`:
   - Four concurrent worker threads commit without losing aggregate deltas.
   - A held SQLite `BEGIN IMMEDIATE` lock causes a bounded failure; after releasing the lock, retry succeeds and the checkpoint/delta is not double-counted.
   - A corrupt SQLite file is rejected without being overwritten.
2. Added `backend/scripts/benchmark_metrics_collector.py`:
   - Synthetic local-only worker loads at 1, 4 and 16 concurrent Python threads.
   - 32 flushes per worker; monotonic cumulative snapshots.
   - Measures p50/p95/p99/max/mean flush latency, lock retry count, peak DB/WAL/SHM sizes and post-checkpoint sizes.
   - Verifies aggregate counts, active worker count and SQLite `integrity_check`.
3. Added `backend/tests/test_metrics_collector_benchmark.py` to verify all three worker scenarios.
4. Added CI execution and 14-day artifact upload for `synthetic-metrics-collector-benchmark`.

## Exact-head verification

- Automated Tests [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637): **SUCCESS**, 35/35 steps.
- Backend pytest: **1,265 passed in 36.46 seconds**.
- CodeQL [44900892567](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892567): **SUCCESS**.
- Full Git History Secret Audit [44900892606](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892606): **SUCCESS**.
- CI also completed backend dependency audit, container build, Redis ACL/persistent-volume smoke, Trivy scan and vulnerability report upload.

## Benchmark evidence

| Worker threads | Successful flushes | p50 ms | p95 ms | p99 ms | Peak DB bytes | Peak WAL bytes | Peak total DB+WAL+SHM |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 32 | 0.803282 | 0.888808 | 2.144816 | 49,152 | 0 | 81,920 |
| 4 | 128 | 0.324234 | 4.258792 | 19.107692 | 49,152 | 1,211,312 | 1,293,232 |
| 16 | 512 | 0.436627 | 19.058717 | 78.977826 | 57,344 | 4,194,192 | 4,284,304 |

- All scenarios: zero lock retries, correct aggregate counts, `integrity_check=ok`.
- Post `wal_checkpoint(TRUNCATE)`: WAL 0 bytes; total DB+SHM 81,920 / 81,920 / 90,112 bytes.
- **Important scope limit:** this initial benchmark uses only 12 logical metric series and Python threads, not all 899 series or separate OS processes. The observed file sizes are not a production host estimate and do not justify a byte ceiling.

## Gate 38 remaining work

- Full-cardinality (899 logical series) benchmark, process-level contention and representative long-running bucket/retention behavior.
- Disk-full and read-only failure tests; app-level proof that collector degradation cannot block HTTP/WebSocket traffic.
- Owner-host persistent volume, permission, restart, restore, disk-pressure and retention acceptance.
- Reverse-proxy/firewall/operator token access, acknowledgement/escalation and recovery drill.
- Multi-host aggregation remains unsupported.

## WebSocket and indicator invariants

- No WebSocket protocol, auth, replay, snapshot ordering, Redis guard or market-data payload behavior changed.
- SMA20 🟨; EMA20 🟨; RSI14 🟨; MACD12/26/9 🟨; Bollinger20,2 🟨; Shared Indicator Hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥.
- Warm-up values remain null, candle-index alignment is preserved, no future-candle repaint, and symbol/venue/dataset/chart/timeframe changes must clear stale series.
- Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced cluster layout. Visual work remains gated on user reference images and reviewed blueprints.

## Project indicators

- Gate 10: **0/10 formally closed**. Gate 38 remains 🟧; no host-only 🟨🟩 or completed green status is claimed.
- Stage 1: **30/40 criteria = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved weights/denominators.
- ZERO COST maintained. No deployment, paid services, Termux/device operations, production credentials or `main` modifications.
