# Batch 62J-131 — WebSocket publisher/replica recovery acceptance and project indicators

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Audited source/test HEAD:** `5be3cff9c19064cbcc9ad686aaf359efb4e5c03d`  
**Scope:** exact-head CI verification; read-only publisher, consumer, worker, replay, stream-hub and browser supervisor audit; full indicator/project/IP3S reconciliation.  
**Change boundary:** documentation only. No runtime or test source modified.

## 1. Exact-head verification

Branch HEAD was independently read from the Git ref and equals `5be3cff9c19064cbcc9ad686aaf359efb4e5c03d`. All three CI workflows target this exact SHA and completed successfully:

- Automated Tests: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326413 — SUCCESS
- CodeQL: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326466 — SUCCESS
- Full Git History Secret Audit: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326442 — SUCCESS

Automated Tests completed all reported job steps successfully, including frontend dependency audit/tests/build, backend tests, Redis TLS CA/hostname integration, backend container build, persistent-volume/shared-Redis-guard smoke, container scan/report and dependency-audit enforcement. This is repository CI evidence, not owner-host production acceptance.

## 2. New WebSocket acceptance evidence — publisher to replica

### Source publisher

Reviewed `backend/app/ohlcv_redis_publisher.py` and its tests. The publisher uses a deterministic Redis Stream ID derived from the durable outbox cursor (`<cursor>-0`) and canonical JSON payload. On an ambiguous XADD reply, it reads back that exact ID and accepts it only when source ID, event ID and payload match. A conflicting entry fails closed; an unconfirmed append does not advance the durable publisher checkpoint. Checkpoint advancement is contiguous and fenced by the current unexpired lease epoch. If source retention overtakes the publisher cursor, the publisher requires a fresh global snapshot.

Test inventory: 21 named publisher tests in `backend/tests/test_ohlcv_redis_publisher.py`, including real-Redis lost-reply recovery, crash-after-append recovery, conflicting deterministic IDs, outage behavior, lease fencing and snapshot rebase.

### Gateway replica consumer

Reviewed `backend/app/ohlcv_redis_consumer.py`. The durable local SQLite apply occurs before the fan-out callback; Redis XACK occurs only after both succeed. Duplicate events repeat the callback to recover from a callback failure after local apply, relying on the stream hub durable-cursor fence for idempotence. The consumer retries its own pending entries before reading newer entries, then uses XAUTOCLAIM for abandoned pending entries. Deleted pending IDs, history gaps and invalid apply state require a new snapshot rather than silent skipping. Each gateway has an independent consumer group.

Test inventory: 20 named consumer tests in `backend/tests/test_ohlcv_redis_consumer.py`, including multi-process/two-gateway broadcast, callback failure and ACK-reply-loss recovery, lease-loss-before-ACK, pending-first ordering, ACL separation, snapshot-generation convergence and replay/live handoff.

### Worker, replay and stream boundary

- Worker: 5 named tests in `backend/tests/test_ohlcv_redis_worker.py`; bounded exponential retry for transient failures, terminal ownership-lost and resnapshot-required states, and bounded shutdown.
- Replay: 11 named tests in `backend/tests/test_ohlcv_redis_replay.py`; global cursor scanning, fixed replica watermark, retention expiry, cursor-ahead, history gaps, series identity validation, scan/event caps and all-or-resnapshot behavior.
- Stream hub: 10 named tests in `backend/tests/test_ohlcv_stream.py`; atomic snapshot/live boundary, exact-series isolation, slow-consumer resnapshot, replay boundary merge and overflow rejection.
- Browser supervisor: 22 named tests in `src/services/ohlcvStreamSupervisor.test.ts`; fresh-token/ticket retry, bounded reconnect, cursor resume, replay, resnapshot after sequence gaps, terminal auth/entitlement/policy rejection, observer failure isolation, close-event races and explicit stop behavior.

### Real TCP interruption test — scope correction

`test_two_asgi_gateways_recover_after_real_redis_tcp_path_interruption` launches two separate ASGI gateway processes, each behind its own TCP fault proxy to the test Redis service. It confirms active Redis TCP connections, severs both paths, rejects reconnect attempts during the outage, restores the paths, publishes a new event, and verifies both WebSocket clients receive cursor 1 and both replica checkpoints converge.

This is stronger than a purely mocked socket test: it is a real TCP-path interruption/recovery test within the CI environment. Its boundary remains local loopback WebSocket clients, ephemeral CI Redis, test certificates/configuration and controlled proxies. It does not prove public internet WSS, production reverse-proxy/TLS, a live Firebase project, Android WebView lifecycle, or owner-host Redis durability/failover. Documentation must preserve this distinction.

## 3. Remaining WebSocket acceptance blockers

### Gate 25 — snapshot and Redis

- Source snapshot exporter/verifier computes and checks canonical SHA-256.
- Gateway installer callback is owner-supplied; runtime validates returned source, generation, high-water cursor and digest format before constructing the Redis client.
- Durable replica checkpoint stores source, replica, applied cursor, snapshot generation, retention floor, bar-retention metadata and schema/protocol versions, but does not persist an anchored snapshot SHA-256. The installer digest is therefore evidence propagated by the runtime, not a digest compared with a digest column in the checkpoint.
- No authenticated owner-host snapshot transfer and independently authenticated per-gateway receipt custody have been evidenced.
- Owner-host Redis TLS/CA/hostname/ACL, AOF/persistence, restart, failover, retention and disk-pressure acceptance remain open.

**Gate 25 remains OPEN.** Do not add a digest schema field until immutable installation provenance versus mutable replica state, migration, rollback and backward compatibility are designed.

### Gate 36 — public WSS and clients

- Ticket is single-use, 90-second TTL, subject- and `market-data`-purpose-bound. Production rejects raw Firebase token fallback in the WebSocket auth frame.
- Origin allowlist and exact canonical-series entitlement checks are separate; entitlement is rechecked during the session.
- Whether series and/or Origin should be embedded in ticket claims remains a threat-model decision, not an assumed defect.
- No verified public hostname, reverse proxy, production TLS certificate/renewal, live Firebase project or production browser session is present.
- Real Android WebView foreground/background, process-death, network handover, reconnect and replay acceptance remains outstanding.

**Gate 36 remains OPEN.** The local TCP fault-proxy test is recorded as CI resilience evidence only.

## 4. Technical indicator progress — complete current ledger

No indicator source, calculation, hook, renderer, UI or test changed in this batch; therefore no technical-indicator implementation credit is awarded.

| Indicator | Verified current state | First valid output | Remaining acceptance |
|---|---|---:|---|
| SMA20 | 🟨 Calculation foundation; arithmetic mean of 20 closes | Candle index 19 | Visible overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 SMA-seeded EMA; alpha 2/21 | Candle index 19 | Visible overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 Wilder | 🟨 Wilder-smoothed gains/losses across 14 close changes | Candle index 14 | 0–100 pane, 30/70 guides, toggle, legend/current value, stale clearing and renderer tests |
| MACD 12/26/9 | 🟨 EMA12 minus EMA26; signal and histogram use 9-period signal | MACD index 25; signal/histogram index 33 | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle, values and lifecycle/render tests |
| Bollinger20,2 | 🟨 20-close mean ±2 population standard deviations | Candle index 19 | Upper/middle/lower overlay, toggle, displayed values, stale clearing and renderer tests |
| Shared Indicator Hook | 🟨 Validated backend snapshot and candle-index-aligned output | Depends on input study | Bind chart identity/timeframe, loading/error lifecycle, stale clearing, per-series isolation and renderer integration |
| Footprint | 🟧 Synthetic educational accumulator only; not exchange-native bid/ask truth | Not a production data acceptance | User reference image and reviewed blueprint first; then validated data contract, cluster renderer, toggle and performance/lifecycle tests |
| Heatmap | 🟥 Not implemented | N/A | Zero-cost source feasibility, user reference image, validated data contract, reviewed blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | N/A | Zero-cost data feasibility and calculation contract; never fabricate unavailable liquidation levels |

Shared invariants: warm-up values are null, never zero; outputs remain aligned to source candle indices; no future-candle repaint; invalid/gapped bars are not silently converted to zero; stale outputs clear when symbol, venue, dataset, chart or timeframe changes. Footprint OFF preserves ordinary candlestick spacing; only explicit ON switches to spaced cluster layout. Footprint and Heatmap visual work remains gated on user-provided reference image(s) and a reviewed blueprint. Stage 4 remains unopened; no aggregate indicator percentage is assigned without approved weights and denominator.

## 5. Overall project progress indicator

| Stage | Scope | Current state |
|---|---|---|
| 1 | Foundation, Security & Data Integrity | 30/40 criteria; **75% provisional** |
| 2 | Market Data Infrastructure | Not officially opened; **NOT SCORED** |
| 3 | Chart Engine & Timeframe | Not officially opened; **NOT SCORED** |
| 4 | Indicators & Analytics | Not officially opened; calculation groundwork exists; **NOT SCORED** |
| 5 | Professional UI & Interactive Tools | Not officially opened; **NOT SCORED** |
| 6 | Hardening, Validation & APK Release | Not officially opened; **NOT SCORED** |

**Overall project: NOT SCORED.** The six-stage weighting/acceptance denominator has not been approved. Do not invent an overall percentage or reuse historical 20.9%.

**Gate 10:** 0/10 formally closed. Open external acceptance gates: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. CI success does not close owner-host gates or authorize a stage transition.

## 6. IP3S — Indicator Proses Peningkatan Proyek Signifikan

IP3S measures delivery quality for this work cycle only; it is not overall project completion.

| Dimension | Weight | Batch 62J-131 | Basis |
|---|---:|---:|---|
| Verified engineering delta | 25 | 0 | No runtime/test source changed |
| Test/CI evidence | 20 | 20 | All three exact-HEAD CI workflows SUCCESS |
| Blocker reduction | 20 | 8 | Clarified and bounded recovery/production evidence gaps; no production gate closed |
| Canonical documentation | 20 | 18 | New source-to-test acceptance mapping and reconciled project/indicator ledgers |
| Scope/cost integrity | 15 | 15 | ZERO COST; main untouched; no credentials, deployment or paid resources |
| **Total** | **100** | **61/100** | Documentation and evidence quality only |

Do not interpret 61/100 as 61% project completion or as a closed acceptance gate.

## 7. Exact scope and next actions

- No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed.
- No hosting, domain, paid service, cloud resource, account or production credential was created or used.
- No device/Termux operation occurred. `main` untouched.
- Keep the exact-head CI green; any later documentation commit must receive its own exact-head CI check.
- Next zero-cost work: design the snapshot-digest provenance ADR; map owner-host receipt requirements; complete the ticket series/Origin threat-model decision record; retain real Android/public WSS as external acceptance.
