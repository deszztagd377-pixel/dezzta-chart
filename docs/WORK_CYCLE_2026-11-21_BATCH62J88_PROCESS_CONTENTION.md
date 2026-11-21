# Work Cycle Batch 62J-88 — exact-head 899-series benchmark and process contention

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline source/test HEAD:** `8424e5eefeecbd06c6534bc34d166f4749ba4055`

## Exact-head CI acceptance
- Automated Tests [44903581963](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581963): **SUCCESS**, all 35 workflow steps.
- Frontend: **255/255 tests across 29 files**.
- Backend: **1,268 passed in 46.21 seconds**.
- Backend container build, ephemeral Redis shared-guard/persistent-volume smoke, Trivy image scan and report export: SUCCESS.
- CodeQL [44903581995](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581995): **SUCCESS**, JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44903581971](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44903581971): **SUCCESS**.
- Exact tested HEAD: `8424e5eefeecbd06c6534bc34d166f4749ba4055`.

## 899-series benchmark evidence
Artifact `synthetic-metrics-collector-benchmark`, ID `14707346273`.

| Threads | Flushes | p50 ms | p95 ms | p99 ms | Retries | Peak DB+WAL+SHM |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 32 | 11.301871 | 12.130371 | 16.124758 | 0 | 323,584 B |
| 4 | 128 | 10.259108 | 239.199409 | 291.808640 | 4 | 4,953,536 B |
| 16 | 512 | 56.776010 | 562.425669 | 982.128261 | 196 | 7,277,592 B |

All cases verified 899/899 logical series (762 request + 127 latency + 10 WebSocket) and `integrity_check=ok`. Total 672 successful flushes and 200 retries (0.298 retry/flush). The 16-thread p95/p99 show significant writer contention; do not infer production readiness.

Payload size: 105,586 / 262,144 bytes = 40.30%; headroom 156,558 bytes = 59.70%.

## Batch 62J-88 changes
1. Remove benchmark-only outer retries so measurements represent only the collector's own bounded `flush()` retry.
2. Remove redundant outer retry from the concurrent-thread regression test.
3. Add four spawned OS processes sharing one SQLite WAL database; verify 899 series, worker count, exact aggregation, integrity and latency.
4. Add a read-only connection failure/recovery regression test proving failed writes do not advance checkpoint or aggregate, then recover without double counting.
5. No WebSocket protocol, transport, auth, replay, cursor, gateway or Redis market-data-path changes.

Exact-head CI for these additions is pending; they are not accepted until green.

## Capacity arithmetic
- 7 days × 24 hours × 4 fifteen-minute buckets/hour = **672 buckets**.
- 899 × 672 = **604,128 aggregate rows**.
- Configured aggregate-row limit = **650,000**.
- Nominal headroom = **45,872 rows**, or **7.06%** of limit.
- Combined logical table-row ceiling = 650,000 + 256 checkpoints + 4,096 tombstones + 1 metadata row = **654,353 rows**, excluding indexes, freelist, WAL and SQLite page overhead.
- This is a row-count calculation, not a disk-byte estimate.

## Remaining Gate 38 acceptance
- Process-level benchmark and read-only test: pending exact-head CI.
- Genuine disk-full/storage-exhaustion test remains.
- App-level proof that collector failures cannot block HTTP/WebSocket traffic remains.
- Owner-host persistent volume, permissions, restart persistence, backup/restore, disk-pressure recovery and retention remain unverified.
- Reverse-proxy/firewall, operator access, acknowledgement/escalation and recovery drill remain host acceptance.
- Multi-host aggregation remains unsupported.

## Project status
- Repository-side WebSocket failure-matrix scope complete. Production acceptance still requires real snapshot distribution/installation receipts, owner-host Redis TLS/ACL/persistence/failover, public HTTPS/WSS and browser/Android WebView acceptance.
- Gate 10: **0/10 formally closed**. Gates 8, 30, 34, 35, 39 🟨🟩; Gates 20, 25, 31, 36, 38 🟧 OPEN.
- Stage 1: **30/40 = 75% provisional**. Stages 2–6 and overall project percentage unscored due missing approved weights/denominators.
- Indicators unchanged: SMA20 🟨 (index 19); EMA20 🟨 (SMA-seeded, alpha 2/21, index 19); RSI14 🟨 (Wilder, index 14); MACD12/26/9 🟨 (MACD 25, signal/histogram 33); Bollinger20,2 🟨 (population SD, index 19); Shared Hook 🟨; Footprint 🟧; Heatmap 🟥; Liquidation Maps 🟥.
- Warm-up null, candle-index aligned, no future-candle repaint, stale clearing on identity/timeframe change. Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters. Footprint/Heatmap visuals require user references and reviewed blueprints.
- ZERO COST: no paid services, deployment, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.


## Batch 62J-89 — remove stray assertion from thread regression (21 November 2026)

- Initial CI for commit `002517f778bed20bcb9e7fe7eed7946893c9763f`: Automated Tests [44904630244](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630244) failed one test; frontend 255/255 passed, backend 1,268 passed and one failed.
- Root cause was a test-edit residue: after the intended single `collector.flush(...)` call, the thread test still contained an unconditional `raise AssertionError("bounded SQLite retry loop exhausted")`. The flush completed; the test then deliberately failed. This was not evidence of collector retry exhaustion.
- In the same run, the new read-only recovery test passed, and the benchmark contract test—including the four spawned OS-process/899-series case—passed.
- CodeQL [44904630257](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630257) SUCCESS; Full Git History Secret Audit [44904630302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630302) SUCCESS.
- Correction removes only the stray assertion. It does not restore benchmark/test outer retries and does not change production collector code.
- Exact-head CI must rerun before the process/read-only additions are accepted. Gate 38 remains 🟧 OPEN.
- Indicator state unchanged; Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; overall project remains unscored.
- ZERO COST; no deployment, Termux/device action, or `main` modification.
