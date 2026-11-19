# LATEST CHECKPOINT — BATCH 62J-2 DURABLE REPLICA TO WEBSOCKET BRIDGE IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** \`phase-2/market-data-foundation\`  
**Parent code HEAD:** \`a3b43b0c8dbf8cecbaef8a17d508defbf287d1ec\`  
**Batch 62J-2:** \`backend/app/ohlcv_replica_bridge.py\` + consumer callback + hub cursor fence  
**Indicator ledger:** \`docs/INDICATOR_PROGRESS_LEDGER.md\`  
**Work report:** \`docs/WORK_CYCLE_2026-11-19_BATCH62J2_REPLICA_TO_WEBSOCKET_BRIDGE.md\`  
**Cost:** ZERO COST • CI only • no deploy • no paid services • no Termux • \`main\` untouched.

## Batch 62J-2 implementation

- Replica snapshot hydration into \`OhlcvPipeline\` from durable SQLite.
- Canonical Redis event reconstruction into \`OhlcvBar\`.
- Pipeline apply and local \`OhlcvStreamHub\` fan-out with source global cursor/event ID.
- Optional consumer callback executes after replica SQLite commit and before Redis ACK.
- Hub per-subscription global-cursor fence suppresses duplicate notification after ACK reply loss.
- Pipeline divergence raises an explicit error; it is never silently dropped.
- New bridge tests cover hydration, cursor restoration, event fan-out, duplicate suppression, snapshot replay and divergence.

**Important:** consumer/publisher startup remains unwired from \`main.py\`. This is a tested library bridge, not yet a running multi-instance backend deployment.

## Validation state

Exact-head CI has not yet completed for the new code. Do not claim this batch is verified until all three workflows pass.

## Project accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner evidence.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED; M1–M8 weights are unapproved.
- Indicator progress is unchanged by WebSocket work; see the full colored indicator ledger.
# LATEST CHECKPOINT — BATCH 62J PROCESS-LEVEL REDIS PARITY TESTS PASSED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Latest code HEAD:** `ad1b2815e5cbd2034851b57e735ac89124d29e75`  
**Publisher:** `backend/app/ohlcv_redis_publisher.py`  
**Consumer:** `backend/app/ohlcv_redis_consumer.py`  
**Integration tests:** `backend/tests/test_ohlcv_redis_publisher.py`, `backend/tests/test_ohlcv_redis_consumer.py`  
**Complete indicator ledger:** `docs/INDICATOR_PROGRESS_LEDGER.md`  
**Work report:** `docs/WORK_CYCLE_2026-11-19_BATCH62J_PROCESS_INTEGRATION.md`  
**Cost:** ZERO COST • GitHub Actions Redis 7 service only • no deployment • no Vercel/Cloudflare push • no paid service • no Termux • `main` untouched.

## Exact-head CI — all passed

At code HEAD `ad1b2815e5cbd2034851b57e735ac89124d29e75`:

- Backend: **1,090 passed in 38.01s**.
- Frontend: **236 passed / 28 test files**.
- Frontend production build and source/bundle secret scans: passed.
- Backend dependency audit: no known vulnerabilities reported.
- Backend container build and Redis/persistent-volume smoke: passed.
- CodeQL Python and JavaScript/TypeScript: passed.
- Full Git History Secret Audit: passed.
- Container vulnerability report: generated and uploaded.

Runs: Automated Tests `44545057500`, CodeQL `44545057428`, Secret Audit `44545057657`.

## Batch 62J-1 — separate worker processes

Added two real-Redis multiprocessing tests:
1. Two spawned gateway-consumer processes open two independent SQLite replica databases and consume the same stream event through independent Redis consumer groups. Both must apply cursor 1.
2. Two spawned publisher processes open the same authoritative SQLite source/checkpoint and race for the fenced lease. Exactly one publishes cursor 1; Redis contains one deterministic stream entry and the source checkpoint advances once.

This verifies cross-process worker coordination and independent-group broadcast semantics under the CI Redis 7 service.

**Scope limit:** these are separate Python worker processes, not two independently started ASGI backend servers, containers, machines, or production instances. The test does not prove public WSS, process supervision, startup lifecycle, or end-to-end browser fan-out.

## WebSocket relay status

- 62G-1 global snapshot export — implemented.
- 62G-2 isolated replica snapshot install — implemented.
- 62G-3 atomic incremental replica apply — implemented.
- 62H-1 durable publisher checkpoint and fenced lease — implemented.
- 62H-2 deterministic Redis append and publisher loop — implemented.
- 62H-3 real Redis append/retry tests — implemented.
- 62H-4 fenced retention snapshot rebase — implemented.
- 62I per-gateway consumer groups, XAUTOCLAIM and apply-before-ACK — implemented.
- 62J-1 separate publisher/consumer worker process tests — implemented and CI-validated.
- **62J-2:** wire durable replica apply into local in-memory pipeline and `OhlcvStreamHub`, with restart-safe hydration, cursor-aware dedupe and queue-overflow resnapshot tests.
- **62J-3:** separate backend process/container lifecycle, Redis outage/recovery, publisher/consumer restart and end-to-end cursor parity.
- 62K owner Gate 25/36 acceptance — still requires owner-controlled infrastructure evidence.

## Boundaries retained

- Publisher/consumer are not started by `main.py`.
- No `OhlcvStreamHub` forwarding is connected yet.
- No production Redis credentials, ACL changes, hosted service or stream trimming.
- No MAXLEN.
- No independent backend server, two-host, public WSS or browser/Android test.
- Redis Server 6.2+ is required for `XAUTOCLAIM`; CI uses Redis 7.

## Project accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner evidence.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights are unapproved.
- WebSocket work does not award indicator progress, Stage ticks or Gate closure.

# LATEST CHECKPOINT — BATCH 62J PROCESS-LEVEL REDIS PARITY TESTS PASSED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Latest code HEAD:** `ad1b2815e5cbd2034851b57e735ac89124d29e75`  
**Publisher:** `backend/app/ohlcv_redis_publisher.py`  
**Consumer:** `backend/app/ohlcv_redis_consumer.py`  
**Integration tests:** `backend/tests/test_ohlcv_redis_publisher.py`, `backend/tests/test_ohlcv_redis_consumer.py`  
**Complete indicator ledger:** `docs/INDICATOR_PROGRESS_LEDGER.md`  
**Work report:** `docs/WORK_CYCLE_2026-11-19_BATCH62J_PROCESS_INTEGRATION.md`  
**Cost:** ZERO COST • GitHub Actions Redis 7 service only • no deployment • no Vercel/Cloudflare push • no paid service • no Termux • `main` untouched.

## Exact-head CI — all passed

At code HEAD `ad1b2815e5cbd2034851b57e735ac89124d29e75`:

- Backend: **1,090 passed in 38.01s**.
- Frontend: **236 passed / 28 test files**.
- Frontend production build and source/bundle secret scans: passed.
- Backend dependency audit: no known vulnerabilities reported.
- Backend container build and Redis/persistent-volume smoke: passed.
- CodeQL Python and JavaScript/TypeScript: passed.
- Full Git History Secret Audit: passed.
- Container vulnerability report: generated and uploaded.

Runs: Automated Tests `44545057500`, CodeQL `44545057428`, Secret Audit `44545057657`.

## Batch 62J-1 — separate worker processes

Added two real-Redis multiprocessing tests:
1. Two spawned gateway-consumer processes open two independent SQLite replica databases and consume the same stream event through independent Redis consumer groups. Both must apply cursor 1.
2. Two spawned publisher processes open the same authoritative SQLite source/checkpoint and race for the fenced lease. Exactly one publishes cursor 1; Redis contains one deterministic stream entry and the source checkpoint advances once.

This verifies cross-process worker coordination and independent-group broadcast semantics under the CI Redis 7 service.

**Scope limit:** these are separate Python worker processes, not two independently started ASGI backend servers, containers, machines, or production instances. The test does not prove public WSS, process supervision, startup lifecycle, or end-to-end browser fan-out.

## WebSocket relay status

- 62G-1 global snapshot export — implemented.
- 62G-2 isolated replica snapshot install — implemented.
- 62G-3 atomic incremental replica apply — implemented.
- 62H-1 durable publisher checkpoint and fenced lease — implemented.
- 62H-2 deterministic Redis append and publisher loop — implemented.
- 62H-3 real Redis append/retry tests — implemented.
- 62H-4 fenced retention snapshot rebase — implemented.
- 62I per-gateway consumer groups, XAUTOCLAIM and apply-before-ACK — implemented.
- 62J-1 separate publisher/consumer worker process tests — implemented and CI-validated.
- **62J-2:** wire durable replica apply into local in-memory pipeline and `OhlcvStreamHub`, with restart-safe hydration, cursor-aware dedupe and queue-overflow resnapshot tests.
- **62J-3:** separate backend process/container lifecycle, Redis outage/recovery, publisher/consumer restart and end-to-end cursor parity.
- 62K owner Gate 25/36 acceptance — still requires owner-controlled infrastructure evidence.

## Boundaries retained

- Publisher/consumer are not started by `main.py`.
- No `OhlcvStreamHub` forwarding is connected yet.
- No production Redis credentials, ACL changes, hosted service or stream trimming.
- No MAXLEN.
- No independent backend server, two-host, public WSS or browser/Android test.
- Redis Server 6.2+ is required for `XAUTOCLAIM`; CI uses Redis 7.

## Project accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner evidence.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights are unapproved.
- WebSocket work does not award indicator progress, Stage ticks or Gate closure.

# HISTORICAL CHECKPOINT — BATCH 62I PER-GATEWAY REDIS CONSUMER IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Latest code HEAD:** `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`  
**Publisher recovery:** `backend/app/ohlcv_redis_publisher.py`  
**Redis consumer:** `backend/app/ohlcv_redis_consumer.py`  
**Publisher tests:** `backend/tests/test_ohlcv_redis_publisher.py`  
**Consumer tests:** `backend/tests/test_ohlcv_redis_consumer.py`  
**Complete indicator ledger:** `docs/INDICATOR_PROGRESS_LEDGER.md`  
**Work report:** `docs/WORK_CYCLE_2026-11-19_BATCH62H3_H4_62I_CONSUMER.md`  
**Cost:** ZERO COST • no paid service • no deployment • no Vercel/Cloudflare push • no Termux • `main` untouched.

## Exact-head CI — all passed

At code HEAD `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`:

- Backend: **1,088 passed in 32.15s**.
- Frontend: **236 passed / 28 test files**.
- Frontend build and source/bundle secret scans: passed.
- Backend dependency audit: no known vulnerabilities reported.
- Backend container build and Redis/persistent-volume smoke: passed.
- CodeQL Python and JavaScript/TypeScript: passed.
- Full Git History Secret Audit: passed.
- Container vulnerability report: generated and uploaded.

Runs: Automated Tests `44543198371`, CodeQL `44543198283`, Secret Audit `44543198433`.

## WebSocket relay implementation sequence

- **62G-1:** consistent bounded global snapshot export and manifest verification — implemented.
- **62G-2:** isolated replica identity and atomic snapshot install — implemented.
- **62G-3:** transactional incremental replica apply and bounded dedupe — implemented.
- **62H-1:** durable source-SQLite publisher checkpoint and fenced lease — implemented.
- **62H-2:** deterministic Redis XADD, exact-ID retry read-back, bounded publisher — implemented.
- **62H-3:** five real Redis integration tests — implemented and CI-validated.
- **62H-4:** explicit fenced publisher checkpoint rebase after retention snapshot — implemented and CI-validated.
- **62I:** per-gateway Redis consumer group, pending reclaim, durable apply-before-ACK, snapshot group reset — implemented and CI-validated.
- **62J:** actual two-process gateway parity, worker lifecycle, outage/recovery and failure matrix — next.
- **62K:** owner-side Gate 25/36 acceptance — requires real owner-controlled infrastructure evidence.

### 62H-3 real Redis coverage

Five tests run against the Redis 7 service already present in GitHub Actions:
1. Deterministic stream IDs and canonical payload fields.
2. Lost XADD reply after Redis committed the entry.
3. Conflicting existing deterministic ID rejected.
4. Uncertain read-back leaves checkpoint unchanged; later exact retry recovers.
5. New Redis client verifies an existing committed stream entry.

Exact-head CI at `95b00d0432aef2a680adf52d5566577689ca6db9`: 1,080 backend tests and 236 frontend tests passed; all three workflows passed.

### 62H-4 retention recovery

Added `SQLiteOhlcvPublisherCheckpoint.rebase_from_snapshot()`:
- Requires snapshot cursor inside the current authoritative retained window.
- Uses an expected-cursor compare-and-swap.
- Never moves the publisher cursor backward.
- Rejects a live publisher lease.
- Clears expired ownership and increments the fencing epoch.
- Sets the next deterministic stream boundary to `<snapshot_cursor>-0`.

This recovery method is explicit and must only be called after the matching global snapshot has been installed successfully on the affected replica(s). It is not wired to startup.

Exact-head CI at `3cd58f4a4172b5b36316233518ab5e1e0ddcfffd`: 1,083 backend tests and 236 frontend tests passed; all three workflows passed.

### 62I per-gateway consumer

Added `RedisOhlcvReplicaConsumer`:
- Stable consumer group derived from the persistent replica ID and source identity; each gateway has an independent broadcast group.
- Fresh group starts at the installed replica snapshot watermark.
- Existing group is preserved on process restart.
- Pending deliveries are reclaimed through Redis `XAUTOCLAIM`.
- Source ID, exact field set, canonical JSON, event ID and deterministic stream ID are validated before local apply.
- The replica's atomic SQLite apply completes before Redis `XACK`.
- `applied`, `duplicate` and `stale` are ACKable; cursor gaps, retention errors, malformed/conflicting events and deleted pending entries are not ACKed.
- An explicit group reset destroys/recreates the gateway group at the newly installed snapshot watermark. The consumer must be quiesced during this operation.
- One sequential worker is expected per gateway replica group. Multi-process orchestration and local WebSocket hub forwarding are not yet implemented.

Five real Redis tests cover durable apply/ACK, ACK failure and pending reclaim, gap/no-ACK, independent broadcast to two replica databases, and group reset after snapshot install.

## Explicitly not integrated

- Publisher and consumer are not started by `main.py`.
- No Redis ACL changes or production Redis endpoint are introduced.
- No MAXLEN trimming is used.
- No WebSocket hub forwarding or app startup worker lifecycle is enabled.
- The current CI tests two independent gateway replica databases and independent groups in one test process; they do not prove two separately deployed backend processes.
- Redis `XAUTOCLAIM` requires Redis Server 6.2 or newer; CI integration uses Redis 7.
- No deployment, paid service, or Termux work.

## Project accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner evidence.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights are unapproved.
- WebSocket batches do not award indicator progress, Stage ticks or Gate closure.

# LATEST CHECKPOINT — BATCH 62I PER-GATEWAY REDIS CONSUMER IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Latest code HEAD:** `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`  
**Publisher recovery:** `backend/app/ohlcv_redis_publisher.py`  
**Redis consumer:** `backend/app/ohlcv_redis_consumer.py`  
**Publisher tests:** `backend/tests/test_ohlcv_redis_publisher.py`  
**Consumer tests:** `backend/tests/test_ohlcv_redis_consumer.py`  
**Complete indicator ledger:** `docs/INDICATOR_PROGRESS_LEDGER.md`  
**Work report:** `docs/WORK_CYCLE_2026-11-19_BATCH62H3_H4_62I_CONSUMER.md`  
**Cost:** ZERO COST • no paid service • no deployment • no Vercel/Cloudflare push • no Termux • `main` untouched.

## Exact-head CI — all passed

At code HEAD `bb7ec0ebdd2565ca50d4020d3e99eec42292b062`:

- Backend: **1,088 passed in 32.15s**.
- Frontend: **236 passed / 28 test files**.
- Frontend build and source/bundle secret scans: passed.
- Backend dependency audit: no known vulnerabilities reported.
- Backend container build and Redis/persistent-volume smoke: passed.
- CodeQL Python and JavaScript/TypeScript: passed.
- Full Git History Secret Audit: passed.
- Container vulnerability report: generated and uploaded.

Runs: Automated Tests `44543198371`, CodeQL `44543198283`, Secret Audit `44543198433`.

## WebSocket relay implementation sequence

- **62G-1:** consistent bounded global snapshot export and manifest verification — implemented.
- **62G-2:** isolated replica identity and atomic snapshot install — implemented.
- **62G-3:** transactional incremental replica apply and bounded dedupe — implemented.
- **62H-1:** durable source-SQLite publisher checkpoint and fenced lease — implemented.
- **62H-2:** deterministic Redis XADD, exact-ID retry read-back, bounded publisher — implemented.
- **62H-3:** five real Redis integration tests — implemented and CI-validated.
- **62H-4:** explicit fenced publisher checkpoint rebase after retention snapshot — implemented and CI-validated.
- **62I:** per-gateway Redis consumer group, pending reclaim, durable apply-before-ACK, snapshot group reset — implemented and CI-validated.
- **62J:** actual two-process gateway parity, worker lifecycle, outage/recovery and failure matrix — next.
- **62K:** owner-side Gate 25/36 acceptance — requires real owner-controlled infrastructure evidence.

### 62H-3 real Redis coverage

Five tests run against the Redis 7 service already present in GitHub Actions:
1. Deterministic stream IDs and canonical payload fields.
2. Lost XADD reply after Redis committed the entry.
3. Conflicting existing deterministic ID rejected.
4. Uncertain read-back leaves checkpoint unchanged; later exact retry recovers.
5. New Redis client verifies an existing committed stream entry.

Exact-head CI at `95b00d0432aef2a680adf52d5566577689ca6db9`: 1,080 backend tests and 236 frontend tests passed; all three workflows passed.

### 62H-4 retention recovery

Added `SQLiteOhlcvPublisherCheckpoint.rebase_from_snapshot()`:
- Requires snapshot cursor inside the current authoritative retained window.
- Uses an expected-cursor compare-and-swap.
- Never moves the publisher cursor backward.
- Rejects a live publisher lease.
- Clears expired ownership and increments the fencing epoch.
- Sets the next deterministic stream boundary to `<snapshot_cursor>-0`.

This recovery method is explicit and must only be called after the matching global snapshot has been installed successfully on the affected replica(s). It is not wired to startup.

Exact-head CI at `3cd58f4a4172b5b36316233518ab5e1e0ddcfffd`: 1,083 backend tests and 236 frontend tests passed; all three workflows passed.

### 62I per-gateway consumer

Added `RedisOhlcvReplicaConsumer`:
- Stable consumer group derived from the persistent replica ID and source identity; each gateway has an independent broadcast group.
- Fresh group starts at the installed replica snapshot watermark.
- Existing group is preserved on process restart.
- Pending deliveries are reclaimed through Redis `XAUTOCLAIM`.
- Source ID, exact field set, canonical JSON, event ID and deterministic stream ID are validated before local apply.
- The replica's atomic SQLite apply completes before Redis `XACK`.
- `applied`, `duplicate` and `stale` are ACKable; cursor gaps, retention errors, malformed/conflicting events and deleted pending entries are not ACKed.
- An explicit group reset destroys/recreates the gateway group at the newly installed snapshot watermark. The consumer must be quiesced during this operation.
- One sequential worker is expected per gateway replica group. Multi-process orchestration and local WebSocket hub forwarding are not yet implemented.

Five real Redis tests cover durable apply/ACK, ACK failure and pending reclaim, gap/no-ACK, independent broadcast to two replica databases, and group reset after snapshot install.

## Explicitly not integrated

- Publisher and consumer are not started by `main.py`.
- No Redis ACL changes or production Redis endpoint are introduced.
- No MAXLEN trimming is used.
- No WebSocket hub forwarding or app startup worker lifecycle is enabled.
- The current CI tests two independent gateway replica databases and independent groups in one test process; they do not prove two separately deployed backend processes.
- Redis `XAUTOCLAIM` requires Redis Server 6.2 or newer; CI integration uses Redis 7.
- No deployment, paid service, or Termux work.

## Project accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner evidence.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights are unapproved.
- WebSocket batches do not award indicator progress, Stage ticks or Gate closure.

# HISTORICAL CHECKPOINT — BATCH 62H-2 DETERMINISTIC REDIS STREAMS PUBLISHER IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Exact validated HEAD:** `f1f998a8659d206c797bdfac14b110a3849d4d68`  
**Implementation:** `backend/app/ohlcv_redis_publisher.py`  
**Tests:** `backend/tests/test_ohlcv_redis_publisher.py`  
**Work report:** `docs/WORK_CYCLE_2026-11-19_BATCH62H2_REDIS_PUBLISHER.md`  
**Complete indicator ledger:** `docs/INDICATOR_PROGRESS_LEDGER.md`  
**Cost:** ZERO COST • no paid service • no deployment • no Termux • `main` untouched.

## Batch 62H-2 implementation

Added deterministic Redis Streams append/read-back and a bounded publisher loop on top of the 62H-1 source-SQLite checkpoint.

- Redis ID is exactly `<cursor>-0`.
- Event payload is canonical JSON with sorted keys and compact separators.
- Stream entry stores source ID, stable event ID and complete canonical payload.
- If XADD fails, publisher reads back only the exact deterministic ID.
- An existing entry is accepted only when source ID, event ID and canonical payload match byte-for-byte after UTF-8 decoding.
- A conflicting entry hard-fails; an unavailable read-back produces an uncertain outcome and does not advance the checkpoint.
- Lease is renewed before each event and the fencing epoch is checked.
- Checkpoint advances only after confirmed append/read-back and the source outbox event is revalidated.
- Bounded pages use global `read_outbox_batch()`.
- Source retention expiry requires a fresh global snapshot; no cursor skipping.
- No MAXLEN trimming, startup wiring, consumer group, ACL change or deployment.

### Exact-head CI — passed

At HEAD `f1f998a8659d206c797bdfac14b110a3849d4d68`:

- Backend: **1,075 passed**.
- Frontend: **236 passed / 28 test files**.
- Frontend build and secret scans: passed.
- Backend container build and Redis/persistent-volume smoke: passed.
- CodeQL Python + JavaScript/TypeScript: passed.
- Full Git History Secret Audit: passed.
- Container vulnerability report: generated and uploaded.

Runs: Automated Tests `44538993402`, CodeQL `44538993277`, Secret Audit `44538993352`.

The first 62H-2 CI attempt exposed one missing standard-library import. It was corrected in the validated HEAD; no production validation was weakened.

## Current WebSocket sequence

- 62G-1: global bounded snapshot export — implemented.
- 62G-2: isolated replica snapshot install — implemented.
- 62G-3: transactional incremental replica apply — implemented.
- 62H-1: durable source publisher checkpoint + fenced lease — implemented and CI-validated.
- 62H-2: deterministic Redis append, exact retry read-back and publisher loop — implemented and CI-validated.
- 62H-3: real Redis integration/restart tests — next.
- 62I: independent consumer groups, pending reclaim, apply-before-ACK — pending.
- 62J: two independent backend processes/read models and full failure matrix — pending.
- 62K: owner-side Gate 25/36 acceptance — pending real infrastructure evidence.

**Important:** publisher is deliberately not wired into `main.py`. No consumer exists yet, and no production cross-instance fan-out is claimed.

## Project accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria.
- Gate 10: **0/10 formally closed**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; M1–M8 weights are unapproved.
- Batch 62H-2 awards no Stage ticks, indicator completion or Gate closure.

# HISTORICAL CHECKPOINT — BATCH 62H-1 DURABLE PUBLISHER CHECKPOINT IMPLEMENTED

62H-1 implementation and test fixture repair are superseded by the latest 62H-2 checkpoint above. The exact-head 62H-1 repair commit `2b8e9012c2689977813d4a71e10366a674bd0f35` passed all three workflows: 1,068 backend tests, 236 frontend tests across 28 files, CodeQL and full-history secret audit. See the 62H-1 work report for details.

## Historical indicator summary — see complete ledger

| Indicator | Calculation foundation / first valid output | Remaining visible work | Status |
|---|---|---|---|
| SMA 20 | Rolling arithmetic mean; index 19; calculation + fixtures | Overlay, toggle, legend/current value, stale clearing, render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA, alpha 2/21; index 19; calculation + fixtures | Overlay, toggle, legend/current value, stale clearing, render tests | 🟨 Foundation |
| RSI 14 | Wilder-smoothed gains/losses; index 14; calculation + edge fixtures | 0–100 pane, 30/70 guides, toggle, lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | EMA12−EMA26; MACD index 25; signal/histogram index 33; warm-up fixtures | Pane, signal line, histogram, zero guide, render tests | 🟨 Foundation |
| Bollinger 20,2 | Mean ±2 population standard deviations; index 19; fixture | Three-line overlay, toggle, legend/current values, render tests | 🟨 Foundation |
| Shared indicator hook | Validated backend snapshot only; no DEMO fallback | Chart binding, loading/error, identity/timeframe stale clearing | 🟨 Foundation |
| Footprint | Deterministic educational accumulator; SIMULATED only | Reference image, reviewed blueprint, explicit-ON spaced cluster renderer/tests | 🟨 Gated |
| Heatmap | No implementation verified | Reference, blueprint, data contract, calculation, renderer, tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Reference, blueprint, data contract, calculation, renderer, tests | 🟥 Not implemented |

**Indicator invariants:** outputs stay aligned to candle indexes; warm-up values are null. Fixture coverage across 18 timeframe labels is not live-provider or visual-integration proof. Footprint OFF retains ordinary candle spacing; only explicit ON enables spaced clusters. Footprint/Heatmap/Liquidation visual work waits for owner reference images and reviewed scoped blueprints. Stage 4 visual work remains parked while Stage 1 is active.

## Project accounting and Gate 10

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN pending owner-side evidence.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights unapproved.
- Batch 62H-1 earns no Stage ticks and closes no owner gate. Exact-head CI and owner evidence remain distinct.
- ZERO COST; no Vercel/Cloudflare deployment; no Termux; `main` untouched.

---

# LATEST CHECKPOINT — BATCH 62G-3 INCREMENTAL REPLICA EVENT APPLY IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Baseline:** `35098bf07adb6a4b856dd8ce4c2034539e3e443f`  
**Code/test commits:** `bc54265784b16daaab50bc4da64e93306105ee87`, `8b60a6974210e9ba4d5999455205c543d0067740`, `92922b5c11cf640a0fb2c9512d2d09e0b56f5084`, `4dc6e8d397ae3c62850cae38c83ccb0f783d08ab`, `8c5d43d9487b3fd6e85a0a6bc1233933d1491b9a`, `a687a08293a29a31ea5190379e40ee4f5ab4455f`, `a59bfac3f3c6238a99439025d49f0ee1157ad624`, `0c2a6292728e819b2af062281817b71dbe100e70`  
**Cost:** ZERO COST • no deployment • no paid service • no Termux • `main` untouched.

## Batch 62G-3 — atomic incremental replica event apply

Added `SQLiteOhlcvReplicaStore.apply_replica_event()`.

- Requires an installed snapshot and matches the caller-supplied authoritative source ID against the durable replica checkpoint.
- Validates the exact outbox envelope, event type/version/operation, event ID, positive integer cursor, complete series identity and canonical bar schema.
- Cross-checks the full series identity against the bar payload.
- Preserves exact Decimal strings and integer nanosecond timestamps; rejects numeric decimal values, booleans in integer fields, non-canonical timestamps and malformed OHLCV.
- Accepts only the next contiguous cursor (E=C+1).
- Returns `duplicate` only when cursor, event ID and canonical payload digest all match a retained applied-event record.
- Returns `stale` for an older cursor whose deduplication record has aged out; never mutates bars or regresses checkpoint.
- Returns `resnapshot_required/cursor_gap` for (E>C+1); returns `resnapshot_required/retention_expired` when the observed source retention floor has overtaken the replica cursor.
- Reused event IDs/cursors with conflicting identity or payload are hard errors.
- Applies the bar, per-series retention pruning, bounded deduplication record and checkpoint cursor in one SQLite transaction.
- Mirrors the source's per-timeframe retention policy carried by snapshot format v2.
- Does not write to the replica outbox. The source-writer `apply()` and replica snapshot export remain blocked.
- Deduplication history is bounded to the latest 100,000 cursors, matching the source outbox retention window.
- Replica checkpoint schema/protocol version is 3; event replay fails closed when a checkpoint version is outdated and requires a current snapshot install.

### Regression coverage added

Five incremental-event test groups cover:
1. Contiguous event application, exact bar fidelity, durable cursor advance, duplicate replay and no outbox echo.
2. Cursor gap, source mismatch, malformed decimal payload, duplicate event, conflicting event ID and stale event after deduplication-history pruning.
3. Forced checkpoint-write failure after bar/ledger mutation; transaction rollback preserves previous bar, checkpoint and empty event ledger.
4. Per-series retention parity: after an additional event, replica and source retain the same five bars under a five-bar timeframe cap.
5. Outdated checkpoint protocol versions are rejected without advancing the cursor or mutating bars.

**Validation:** source and tests are committed. Exact-head CI is not confirmed; no runtime pass is claimed. Prior CI results apply only to their recorded SHAs.

## Integrated WebSocket status

- **62G-1:** consistent bounded global snapshot export and manifest verification.
- **62G-2:** isolated replica identity, format-v2 snapshot install, retention metadata and atomic checkpoint.
- **62G-3:** transactional incremental event apply and bounded idempotency ledger.
- **62H–62K:** Redis Streams, consumer recovery, two-process parity, failure matrix and owner Gate 25/36 acceptance remain pending.
- No Redis publisher/consumer is wired into app startup. No public deployment is performed.

## Project accounting — unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights are unapproved.
- This code batch earns no Stage ticks and closes no Gate before exact-head CI and owner-side evidence.

**Complete indicator ledger:** all existing formulas, first-valid indexes, calculation fixtures, visual integration gaps, and Footprint/Heatmap/Liquidation reference-image gates remain preserved below. No indicator implementation changed in this WebSocket cycle.

---

# LATEST CHECKPOINT — BATCH 62G-2 REPLICA SNAPSHOT INSTALL IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Baseline:** `35098bf07adb6a4b856dd8ce4c2034539e3e443f`  
**Code/test commits:** `fe1d05f214932268d25e2292079fe6752a32880f`, `307e6838fa3b2604f166cabff26bcc9affc1ac8a`, `ad8583a53cf68a89c368d01a8a9d51e959e83440`, `8e73cbc9c2e57bbf517dce024045dc59cac7749f`, `9c7217c3e9cf32ca7d53e1e07ec5a2b6607bc75c`, `608ccddc249a7f7183feb41ff05f15bc75601d35`, `0a5fe3b10e55f94de8ffdc0230be61de21e255d3`, `4885eb0be9261d6d5d35fe97d87bd40b03d151c0`, `29e40aa59310b03693eb710f1b4b07106f720b7b`, `7e1b3186e29999aef642982bc3e14aa552ffe323`, `13004e0d083c1ce0b466d22b5ed5aeefad6c4b47`, `40883b0e194d35f4e894f57862e5bc208104579c`, `e4dbe1f899aa382438a144fb59e9584ae8d969bc`, `09c0f5b8e82f710c18901cd4849bedce01d1ba1f`, `3987c9dc46bd11ade96742c8da4867b594147051`  
**Cost:** ZERO COST • no Vercel/Cloudflare deployment • no paid service • no Termux • `main` untouched.

## Batch 62G-2 — replica snapshot installation

Implemented `SQLiteOhlcvReplicaStore` in `backend/app/ohlcv_store.py` as a separate local read-model store.

- Stable `replica_id` is created once per gateway database and survives restart.
- Durable checkpoint records upstream `source_id`, replica ID, applied cursor, snapshot generation, retention floor, schema version and protocol version.
- `install_global_snapshot()` first preflights the snapshot, then re-reads and validates it while holding one target SQLite write transaction. This closes the file verify/use race.
- The target's existing bars are replaced inside that transaction. The global checkpoint is written only after every row and the final manifest validate; bars and checkpoint commit together or both roll back.
- Snapshot records must match the exact 23-field OHLCV schema. Decimal fields must be strings, integer/nanosecond fields must be actual integers (booleans rejected), and optional provider timestamp must be integer or null.
- Every row is reconstructed through `OhlcvBar` validation before insertion. Calendar identity, including CME session ID/version, is retained.
- Batch inserts are bounded to 1–5,000 records (default 500); no full-snapshot Python list is materialized.
- Replica `apply()` is explicitly disabled so callers cannot accidentally use the authoritative writer path and create source outbox echo.
- Replica `source_id()` is disabled; the authoritative identity is read from its upstream checkpoint, not confused with the replica database's local metadata.
- Snapshot envelope format is now version 2 and includes the complete per-timeframe bar-retention policy in addition to the outbox retention floor; the replica checkpoint stores that policy as JSON.
- A replica can only be initialized on a dedicated empty OHLCV read-model database. Existing authoritative bars/outbox state are detected and protected from replacement.
- Replica snapshot export is blocked, as is source-writer `apply()`, to prevent a read model from being mistaken for a new authority.

### Atomicity and recovery boundary

The target transaction starts before replacing bars. It streams rows in bounded batches, recomputes the complete header-plus-row SHA-256, validates the manifest, and writes the checkpoint before COMMIT. Any malformed row, duplicate primary key, changed file, I/O error or checkpoint failure rolls back the delete, inserted rows and checkpoint update together.

A replica already bound to another source is rejected. A snapshot whose high-water is below the current applied cursor is rejected. The source ID can also be pinned through `expected_source_id`.

### Regression coverage added

Five replica test groups now cover:
1. Successful full snapshot install across UTC and CME series; exact decimal and timestamp preservation; checkpoint contents; stable replica identity after restart; no outbox echo; source-writer apply blocked.
2. Wrong-source rejection and stale snapshot cursor rejection without mutation.
3. A semantically invalid but correctly checksummed snapshot fails after a prior batch is inserted; transaction rollback preserves the previous bars and checkpoint.
4. Numeric JSON decimal values are rejected even when the envelope checksum is valid, preventing lossy float-to-Decimal conversion.
5. An existing authoritative database cannot be reused as a replica target; source bars and outbox remain intact. Replica export is also blocked.

**Validation:** code and tests are committed, but exact-HEAD CI is not yet confirmed. No green test claim is made. The earlier 62F/62G-1 CI evidence applies only to its own exact commit SHA.

## Remaining integrated WebSocket cycle

1. **62G-3:** transactional event apply with source binding, event-ID/cursor validation, idempotency, duplicate/stale/gap handling and no outbox echo.
2. **62H:** deterministic Redis Streams publisher and independent consumer group per gateway.
3. **62I:** apply-before-ACK, pending reclaim, crash/restart and Redis outage recovery.
4. **62J:** two independent backend processes/read models, cursor parity and full failure matrix.
5. **62K:** owner-side Gate 25/36 evidence. No deployment is authorized just to manufacture evidence.

Redis relay is still not activated in application startup. No SQLite WAL is shared across hosts.

## Project accounting — unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights are unapproved.
- This replica-install slice earns no Stage ticks and closes no Gate until exact-head CI and owner acceptance requirements are satisfied.

**Complete indicator ledger:** all formula definitions, first valid indexes, fixture coverage, visual integration gaps, and Footprint/Heatmap/Liquidation reference-image gates are preserved in the sections below. Indicator implementation was not modified by this WebSocket batch.

---

# LATEST CHECKPOINT — BATCH 62G-1 GLOBAL SNAPSHOT EXPORT IMPLEMENTED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Previous approved blueprint:** `189ed4ba514dcf725ec38a9a0dc95f389017b304`  
**Code/test commits:** `a4ef6eca4ffe5dd15cb829f10090d54934216cf7`, `708532eb6b2edd4029176b2b95be822995305059`, `0cbc8b53afde575362050fbb88fdfe3dba8dedbf`, `498e644e1cc6037c02ea5c25935babc2e886a224`, `6463c968e25c86b6c07099dcc99c4415cd3c4b8d`  
**Cost:** ZERO COST • no deployment • no paid service • no Termux • `main` untouched.

## Batch 62G-1 — first executable slice of the approved eight-point cycle

Implemented in `backend/app/ohlcv_store.py`:
- Added a stable per-database `source_id` in an additive OHLCV-owned metadata table. It does not alter shared `PRAGMA user_version` or bump the OHLCV table schema version.
- Added `export_global_snapshot(destination_path, batch_size=500)`.
- Export pins one SQLite read transaction by reading outbox state first, then streams **all retained rows** from `ohlcv_bars` in deterministic primary-key order using `fetchmany()`.
- The export includes every bucket/calendar identity, including CME session rows; it does not reuse the chart query's default calendar filters.
- Header records source identity, generation ID, global high-water and retention floor. Footer records row count and SHA-256 over the canonical header plus every canonical bar record, protecting the source ID and watermark as well as payload rows.
- Output is written to a temporary file, flushed/fsynced, then atomically renamed only after successful export and source read-transaction completion.
- Added streaming `verify_global_snapshot()` to validate header constraints, record order, row count and a content digest covering the header plus all bar records without loading the whole file into memory.
- Added explicit destination protection and bounded batch-size validation.

### Consistency and resource notes

- The watermark and every exported bar come from the same pinned SQLite read view.
- Memory use is bounded by `batch_size`; default 500, maximum 5,000 rows per fetch.
- A long-lived WAL reader can delay WAL checkpoint/truncation and increase WAL disk usage while concurrent writes continue. Export duration and WAL growth must be benchmarked before production rollout.
- This is the **source export/verification half** of the snapshot protocol. Replica-side atomic installation, source/replica checkpoint, incremental replay and Redis Streams are not yet implemented or activated.
- The export file is an internal transfer artifact, not a public endpoint. No data is sent to a third party.

### Regression coverage added

Three tests added:
1. All retained bucket/calendar series exported, including CME identity, exact decimal strings, stable source ID, row count and manifest verification; tampering is rejected.
2. Concurrent source write after the snapshot watermark is pinned does not leak into the export; snapshot cursor and rows remain at the same committed view.
3. Invalid/boolean batch size, empty destination and source-database overwrite are rejected.

**Validation:** exact-head CI for the implementation commits is pending; do not mark tests green or award Stage/Gate progress until the exact final head passes. The prior Batch 62F CI 3/3 result remains evidence only for its own exact SHA.

## Next implementation work inside the same integrated cycle

1. Snapshot replica install contract: validate source identity, header/footer, all row identities and digest; stage rows into a separate local read model and swap atomically.
2. Replica identity/checkpoint schema and source binding.
3. Transactional idempotent event apply without outbox echo.
4. Duplicate/stale/gap/conflict/restart and exact-decimal tests.
5. Redis Streams append + independent consumer groups only after local replica correctness.
6. Two independent backend process parity and full recovery matrix.
7. Gate 25/36 owner acceptance only with real owner infrastructure and external evidence.

No partial relay is enabled at startup.

## Current project accounting

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks (unchanged).
- Gate 10: **0/10 formally closed** (unchanged).
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights are unapproved.
- This source-export slice earns no Stage ticks and closes no Gate.

**Complete indicator ledger:** retained in this document below, unchanged. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20, shared indicator hook, Footprint, Heatmap and Liquidation Maps retain their exact formulas, warm-up indexes, implementation boundaries and remaining work. Visual gates for Footprint/Heatmap/Liquidation remain in force.

---

# LATEST CHECKPOINT — BATCH 62G INTEGRATED WEBSOCKET BLUEPRINT APPROVED

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Baseline:** `1cb577c1de31e7a5c286075da5cf8f770b2c16e1` • **Blueprint commit:** `e25356ec66e49ab5b98918e602c746ce8b552fe3`  
**Owner decision:** APPROVED — combine all eight WebSocket architecture points into one dependency-ordered multi-work cycle.  
**Cost:** ZERO COST • no deployment • no paid service • no Termux • `main` untouched.

## Batch 62F exact-head CI — 3/3 SUCCESS

- Automated Tests + Build [44500814706](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44500814706): SUCCESS. Frontend tests/build, backend tests, bounded SQLite outbox benchmark, dependency audit, container build/smoke, image scan and report upload all completed.
- CodeQL [44500815399](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44500815399): Python and JavaScript/TypeScript SUCCESS.
- Full Git History Secret Audit [44500814616](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44500814616): SUCCESS.

CI is supporting repository evidence only; no owner-host Gate 10 acceptance is inferred.

## Batch 62G — integrated WebSocket blueprint

Created `docs/WORK_CYCLE_2026-11-19_BATCH62G_INTEGRATED_WEBSOCKET_BLUEPRINT.md`.

The eight approved points are consolidated into one work cycle:
1. Full retained read-model snapshot with all series/calendar identities and one consistent global watermark.
2. Stable source/replica identity and durable per-gateway checkpoint schema.
3. Atomic, idempotent replica apply without source-outbox echo.
4. Redis Streams publisher with deterministic retry identity and independent consumer groups per gateway.
5. Apply-before-ACK ordering, crash recovery, pending reclaim and safe local hub publication.
6. Two independent backend processes and read-model/watermark parity.
7. Failure matrix: duplicate, stale, out-of-order, gap, malformed/conflicting event, restart, Redis outage, retention expiry and interrupted snapshot.
8. Gate 25/36 owner acceptance: independent deployed instances, owner Redis, public WSS, browser/WebView and 330-second close attribution.

### Newly confirmed blocker — global snapshot semantics

The existing `query_snapshot()` is a correct scoped bars+watermark transaction, but it is not yet a complete global replica snapshot:
- Default filters omit calendar-qualified CME session series.
- Per-instrument snapshots cannot advance a global cursor.
- Independently paginated read transactions can represent different source moments.
- Unbounded in-memory materialization risks memory pressure.

**Resolution path:** implement a bounded immutable snapshot generation/manifest or equivalent stable snapshot transfer, covering every retained series identity and one global watermark. Only after every page and manifest validates may the replica atomically install the snapshot and set its global checkpoint. No partial relay activation.

### Replica cursor invariant

For durable replica cursor (C) and incoming cursor (E):
- (E=C+1): validate and apply transactionally.
- (E\le C): duplicate/stale path; never mutate or regress checkpoint.
- (E>C+1): integrity gap; stop and require resnapshot.

Bar apply + checkpoint update must share one SQLite transaction. Redis ACK must follow that commit. Replica apply must not append a source outbox event.

## Current project accounting

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights remain unapproved.
- Blueprint documentation earns no Stage ticks or Gate closures.

**Documentation work in this checkpoint:**
- `docs/WORK_CYCLE_2026-11-19_BATCH62G_INTEGRATED_WEBSOCKET_BLUEPRINT.md` — complete eight-point implementation sequence, cursor invariants, bounded snapshot requirements, failure matrix, Gate 10 packs and complete indicator ledger.
- `docs/ADR_WEBSOCKET_CROSS_INSTANCE_OUTBOX_RELAY.md` — architecture decision updated with the newly verified global snapshot constraint and no-partial-activation rule.

**Full indicator ledger and prior verified history are retained below unchanged.**

---

# LATEST VERIFIED CHECKPOINT — BATCH 62F OUTBOX CURSOR-INTEGRITY GUARD

**Date:** 19 November 2026 • **Branch:** `phase-2/market-data-foundation`  
**Baseline before this batch:** `bc1aff114f7dd040e6be4b5df949f7f4750eb63a`  
**Scope:** global outbox cursor-gap detection + regression tests + progress ledger.  
**Cost:** ZERO COST • no Vercel/Cloudflare deployment • no paid service • no Termux • `main` untouched.

## Batch 62F — implementation scope

- `SQLiteOhlcvStore.read_outbox_batch()` now validates contiguous cursor progression from the caller's checkpoint.
- It validates the look-ahead row, so a missing cursor immediately after a page boundary is detected before a relay can checkpoint past it.
- It validates the terminal cursor against the durable high-water mark, detecting a missing tail event or an unexpectedly empty page.
- Integrity gaps return `status=resnapshot_required`, `reason=cursor_gap`, and no partial events. The caller must not advance by treating a damaged page as healthy.
- Existing retention-expired and cursor-ahead behavior is preserved.
- Three regression scenarios cover a middle-page gap, a page-lookahead gap, and a missing tail cursor.

**Validation status:** source and test changes are committed only after static patch checks; exact-head CI is the authority for test/build validation. Do not claim this batch validated until all three exact-head workflows complete.

## WebSocket status

The local durable foundations remain: atomic bar+outbox writes, exact-decimal payloads, global cursor, retention floor, global outbox pagination, exact-revision lookup, and bars+watermark snapshot transactions. The new cursor-gap guard hardens relay input but does **not** implement replica apply, Redis Streams relay, cross-instance fan-out, or deployed WSS.

Next implementation sequence:
1. Replica identity/checkpoint schema and atomic apply without source-outbox re-emission.
2. Duplicate, stale, out-of-order, gap, exact-decimal, restart and watermark tests.
3. Redis Streams publisher/checkpoint and independent consumer groups per gateway.
4. Retry, crash, pending reclaim, Redis outage and retention-resnapshot tests.
5. Two independent backend processes with separate local read models.
6. Owner-side Gate 25/36 acceptance only after infrastructure and external evidence exist.

Do not share SQLite WAL across hosts. Do not activate partial relay at app startup.

## Gate 10 — all OPEN (0/10 formally closed)

| Gate | Required evidence | State |
|---:|---|---|
| 8 | Owner-host protected secret injection/mounts and runtime readback | 🟥 OPEN |
| 20 | Real Firebase valid/expired/revoked/wrong-project E2E | 🟥 OPEN |
| 25 | Owner Redis, independent instances, outage/recovery and operator evidence | 🟥 OPEN |
| 30 | Actual owner target-database restore | 🟥 OPEN |
| 31 | Zero-cost off-host backup, separate key custody, retention and restore | 🟥 OPEN |
| 34 | Persistent volume, restart and disk-pressure drill | 🟥 OPEN |
| 35 | Public HTTPS/WSS, certificate renewal and external scan | 🟥 OPEN |
| 36 | Snapshot-consistent fan-out, browser/WebView and 330-second attribution | 🟥 OPEN |
| 38 | Durable collector, retention and protected access | 🟥 OPEN |
| 39 | Named operator, escalation and acknowledgement/recovery drill | 🟥 OPEN |

CI is supporting evidence only; it cannot close owner-controlled gates.

## Complete indicator progress ledger

| Indicator | Exact calculation contract | First valid index | Current foundation | Remaining work | State |
|---|---|---:|---|---|---|
| SMA20 | Rolling arithmetic mean of close | 19 | Calculation + fixture tests | Visible overlay, toggle, legend/latest value, stale clearing, render tests | 🟨 |
| EMA20 | SMA-seeded EMA, alpha (2/21) | 19 | Calculation + fixture tests | Visible overlay, toggle, legend/latest value, stale clearing, render tests | 🟨 |
| RSI14 | Wilder-smoothed close-to-close gain/loss | 14 | Calculation + edge fixtures | Dedicated 0–100 pane, 30/70 guides, toggle, lifecycle/render tests | 🟨 |
| MACD12/26/9 | EMA12−EMA26; EMA9 signal | MACD 25; signal/histogram 33 | Calculation + warm-up fixtures | Pane, signal line, histogram, zero guide, render tests | 🟨 |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | Calculation + population-deviation fixture | Three-line overlay, toggle, legend/latest values, render tests | 🟨 |
| Shared indicator hook | Validated backend snapshot only; no DEMO fallback | Snapshot-dependent | Hook reads shared market-data store | Visible chart binding, loading/error handling, identity/timeframe stale clear | 🟨 |
| Footprint | Deterministic educational accumulator, explicitly SIMULATED | Not production order flow | Simulation only | Owner reference + reviewed blueprint + ON-only spaced cluster renderer | 🟨 GATED |
| Heatmap | Not implemented | — | None | Owner reference, blueprint, source data, calculation, renderer and tests | 🟥 |
| Liquidation Maps | Not implemented | — | None | Owner reference, blueprint, source data, calculation, renderer and tests | 🟥 |

**Indicator acceptance boundary:** the seven calculation test cases cover alignment/warm-up, RSI edge cases, MACD warm-up, Bollinger population deviation, shared calculation entry point, 18 timeframe labels and invalid inputs. They do not prove visible chart integration or live-provider correctness. Footprint OFF must preserve ordinary candle spacing; only explicit ON may enable spaced clusters. Footprint, Heatmap and Liquidation Maps visuals remain gated on owner reference images and reviewed blueprints. Stage 4 visible UI remains parked while Stage 1 is active.

## Project progress accounting

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — all ten remain OPEN.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** — M1–M8 weights remain unapproved.
- No stage ticks or Gate 10 closures are awarded for this batch before exact-head CI and owner evidence.

## Cost, branch and device controls

- ZERO COST. No paid Redis, hosting, data provider or subscription is introduced.
- No Vercel/Cloudflare deploy or promotion.
- No Termux required for this repository-side patch.
- Only `phase-2/market-data-foundation` is modified; `main` remains untouched.

**Detailed report:** [Batch 62F outbox cursor-integrity guard](WORK_CYCLE_2026-11-19_BATCH62F_OUTBOX_CURSOR_GAP_GUARD.md)

---

# CURRENT VERIFIED PROJECT STATUS — BATCH 62D (CI VERIFIED)

**Date:** 19 November 2026 • **Branch:** phase-2/market-data-foundation • **Verified source HEAD:** c2008868538cbf57fcff8f806e7c9b775785ef6e  
**Cost:** ZERO COST • no deployment • no Termux • main untouched.

## Batch 62D exact-head CI — 3/3 SUCCESS

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests + Build | [44495306834](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44495306834) | SUCCESS |
| CodeQL Python + JS/TS | [44495306746](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44495306746) | SUCCESS |
| Full Git History Secret Audit | [44495306805](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44495306805) | SUCCESS |

- Backend pytest: **1,048 passed in 32.45 seconds**.
- Frontend Vitest: **236 passed across 28 files**.
- Frontend npm audit: **0 vulnerabilities**.
- Backend dependency audit: **no known vulnerabilities**.
- Backend container build and smoke test: SUCCESS; shared Redis guard and persistent-volume checks completed.
- Trivy scanned 69 image/package targets: **0 vulnerabilities reported** in the table; report artifact uploaded.
- Batch 62D includes deterministic concurrent SQLite snapshot/watermark test and both Batch 62C snapshot tests.
- These remain CI/source results, not owner production acceptance.

## Gate 10 — 0/10 formally closed; all OPEN

| Gate | Remaining owner acceptance |
|---:|---|
| 8 | Owner-host secret injection, protected mounts and runtime readback |
| 20 | Real Firebase valid/expired/revoked/wrong-project E2E |
| 25 | Owner Redis, independent deployed app instances, outage/recovery and operator evidence |
| 30 | Actual owner target-database restore |
| 31 | Zero-cost off-host copy, separate key custody, retention and restore |
| 34 | Owner-host volume/restart/disk-pressure evidence |
| 35 | Public HTTPS/WSS ingress, certificate renewal and external scan |
| 36 | Snapshot-consistent cross-instance fan-out, browser/WebView and 330-second attribution |
| 38 | Durable cross-instance collector, retention and protected access |
| 39 | Named operator, escalation channel and acknowledgement drill |

## Complete indicator progress ledger

| Indicator | Formula / first valid index | Verified foundation | Remaining visible work | State |
|---|---|---|---|---|
| SMA20 | Rolling close mean / 19 | Fixture-tested calculation | Overlay, toggle, legend/value, stale clear, render tests | 🟨 |
| EMA20 | SMA seed, alpha 2/21 / 19 | Fixture-tested calculation | Overlay, toggle, legend/value, stale clear, render tests | 🟨 |
| RSI14 Wilder | Wilder smoothing / 14 | Fixture-tested calculation | 0–100 pane, 30/70 guides, toggle, lifecycle/render | 🟨 |
| MACD12/26/9 | EMA12−EMA26 / 25; signal/histogram / 33 | Fixture-tested calculation | Pane, signal, histogram, zero guide, render tests | 🟨 |
| Bollinger20,2 | Population stddev ×2 / 19 | Fixture-tested calculation | Three-line overlay, toggle, legend/value, render | 🟨 |
| useMarketIndicators() | Backend snapshot, aligned warm-up nulls | No demo fallback | Visible binding, loading/error, stale identity/timeframe clear | 🟨 |
| Footprint | Deterministic SIMULATED | Simulation only | Owner reference + reviewed blueprint + ON-only spaced cluster renderer | 🟨 gated |
| Heatmap | Not implemented | None | Reference, blueprint, source, calculation, renderer, tests | 🟥 |
| Liquidation Maps | Not implemented | None | Reference, blueprint, source, calculation, renderer, tests | 🟥 |

**Invariants:** warm-up nulls align to original candle indexes; 18-timeframe formula fixtures do not prove provider data quality or visible integration. Footprint OFF preserves ordinary candles; explicit ON alone enables spaced clusters. Footprint/Heatmap/Liquidation visual work waits for owner references and reviewed blueprint. Stage 1 active; Stage 4 visible UI parked.

## Progress accounting
- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks.
- Gate 10: **0/10 closed**.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED.
- ZERO COST; no deploy; no Termux; main untouched.

---

# CURRENT VERIFIED PROJECT STATUS — BATCH 62D

**Date:** 19 November 2026 • **Branch:** phase-2/market-data-foundation • **Pre-cycle HEAD:** b213824e8cee4402ab0b846feb05a45de98fe415  
**Cost:** ZERO COST • no deployment • no Termux • main untouched.

## Batch 62B exact-head CI — 3/3 SUCCESS
- Automated Tests [44494115133](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494115133): **1,045 backend passed in 35.10s**, **236 frontend tests / 28 files**, build, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy image scan/report upload all succeeded.
- CodeQL [44494114971](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494114971): Python + JavaScript/TypeScript SUCCESS.
- Full Git History Secret Audit [44494115057](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494115057): SUCCESS.
- Trivy scan completed and artifact uploaded (artifact ID 14514780896). Do not infer zero findings from scan success alone; inspect report for package-level results.

## Batch 62C validation
Exact HEAD `b213824e8cee4402ab0b846feb05a45de98fe415`:
- Automated Tests run [44494968794](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494968794): IN PROGRESS at last observation.
- CodeQL run [44494968708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494968708): IN PROGRESS at last observation.
- Secret Audit run [44494968711](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494968711): SUCCESS.
- Batch 62C added atomic SQLite snapshot/watermark and two tests. Do not claim its new tests pass until exact-head CI completes.

## Batch 62D source validation
Added a concurrency regression test to prove bars and outbox cursor remain on the same SQLite read transaction while another writer commits. New Batch 62D CI pending.

## Gate 10 — all OPEN (0/10 formally closed)
| Gate | Required owner evidence |
|---:|---|
| 8 | Owner-host secret injection, protected mounts, runtime readback |
| 20 | Real Firebase valid/expired/revoked/wrong-project E2E |
| 25 | Owner Redis, independent deployed app instances, outage/recovery and operator evidence |
| 30 | Actual owner target-database restore |
| 31 | Zero-cost off-host copy, separate key custody, retention and restore |
| 34 | Owner-host volume/restart/disk-pressure evidence |
| 35 | Public HTTPS/WSS ingress, certificate renewal and external scan |
| 36 | Snapshot-consistent cross-instance fan-out, browser/WebView and 330-second attribution |
| 38 | Durable cross-instance collector, retention and protected access |
| 39 | Named operator, escalation channel and acknowledgement drill |

## Complete indicator progress
| Indicator | Calculation / first valid index | Foundation | Remaining | State |
|---|---|---|---|---|
| SMA20 | Rolling close mean / 19 | Fixture tested | Overlay, toggle, legend/value, stale clear, render tests | 🟨 |
| EMA20 | SMA seed, alpha 2/21 / 19 | Fixture tested | Overlay, toggle, legend/value, stale clear, render tests | 🟨 |
| RSI14 Wilder | Wilder smoothing / 14 | Fixture tested | 0–100 pane, 30/70 guides, toggle, lifecycle/render | 🟨 |
| MACD12/26/9 | EMA12−EMA26 / 25; signal/hist 33 | Fixture tested | Pane, signal, histogram, zero guide, render tests | 🟨 |
| Bollinger20,2 | Population stddev ×2 / 19 | Fixture tested | Three-line overlay, toggle, legend/value, render | 🟨 |
| useMarketIndicators() | Backend snapshot, aligned warm-up nulls | No demo fallback | Visible binding, loading/error, stale identity/timeframe clear | 🟨 |
| Footprint | Deterministic SIMULATED | Simulation only | Owner reference + blueprint + ON-only spaced cluster renderer | 🟨 gated |
| Heatmap | Not implemented | None | Reference, blueprint, source, calculation, renderer, tests | 🟥 |
| Liquidation Maps | Not implemented | None | Reference, blueprint, source, calculation, renderer, tests | 🟥 |

**Invariants:** warm-up nulls align to source candle indexes; formula fixtures over 18 timeframes do not prove live data quality or visible integration. Footprint OFF preserves normal candles; explicit ON alone enables spaced clusters. Visual implementation waits for owner references and reviewed blueprint. Stage 1 active; Stage 4 UI parked.

## Progress
- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks.
- Gate 10: **0/10 closed**.
- Stages 2–6: NOT SCORED.
- Overall project: NOT ESTABLISHED.
- ZERO COST; no deploy; no Termux; main untouched.

---

# CURRENT VERIFIED PROJECT STATUS — BATCH 62C

**Date:** 19 November 2026 • **Branch:** phase-2/market-data-foundation • **Pre-cycle HEAD:** 7063e1c9708bc3228aedb44153ed4c4461553e28  
**Cost:** ZERO COST • no deploy • Termux not required • main untouched.

## Exact-head CI — Batch 62B
- Automated Tests run [44494115133](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494115133): still IN PROGRESS at last observation, specifically backend container build; backend tests, benchmark and backend dependency audit already succeeded.
- CodeQL run [44494114971](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494114971): SUCCESS for Python and JS/TS.
- Full Git History Secret Audit [44494115057](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44494115057): SUCCESS.
- Batch 62B backend test suite includes the new two-process Redis single-use-ticket + account-cap race. Its worker only attempts account lease after it has consumed the one-time ticket.
- Do not label Automated Tests 3/3 until the container build/smoke, image scan/report and final cleanup complete.

## Batch 62C source changes
- Added `SQLiteOhlcvStore.query_snapshot()`: exact query filters, bounded optional limit, selected bars, total count, durable outbox high-water and retention floor are read in one SQLite transaction.
- Added regression tests for snapshot contents/watermark progression and invalid limits.
- Tightened the cross-process Redis race test so ticket consumption and account lease winner are causally linked.
- Added the architecture decision and acceptance boundaries to the ADR.

## Gate 10 — all remain OPEN
| Gate | Remaining owner acceptance |
|---:|---|
| 8 | Owner-host secret injection, protected mounts and runtime readback |
| 20 | Real Firebase valid/expired/revoked/wrong-project E2E |
| 25 | Owner Redis, independent deployed app instances, outage/recovery and operator evidence |
| 30 | Actual owner target-database restore |
| 31 | Zero-cost off-host copy, separate key custody, retention and restore |
| 34 | Owner-host volume/restart/disk-pressure evidence |
| 35 | Public HTTPS/WSS ingress, certificate renewal and external scan |
| 36 | Snapshot-consistent cross-instance fan-out, browser/WebView and 330-second attribution |
| 38 | Durable cross-instance collector, retention and protected access |
| 39 | Named operator, escalation channel and acknowledgement drill |

**Formal closure: 0/10.** Source/CI evidence is not owner production acceptance.

## Complete indicator progress ledger
| Indicator | Formula / first valid index | Existing foundation | Remaining visible work | State |
|---|---|---|---|---|
| SMA20 | Rolling close mean; 19 | Fixture-tested calculation | Overlay, toggle, legend/value, stale clear, render tests | 🟨 |
| EMA20 | SMA seed; alpha 2/21; 19 | Fixture-tested calculation | Overlay, toggle, legend/value, stale clear, render tests | 🟨 |
| RSI14 Wilder | Wilder smoothing; 14 | Fixture-tested calculation | 0–100 pane, 30/70 guides, toggle, lifecycle/render | 🟨 |
| MACD12/26/9 | EMA12−EMA26; 25; signal/histogram 33 | Fixture-tested calculation | Pane, signal, histogram, zero guide, render tests | 🟨 |
| Bollinger20,2 | Population σ ×2; 19 | Fixture-tested calculation | Three-line overlay, toggle, legend/value, render | 🟨 |
| useMarketIndicators() | Backend snapshot, warm-up nulls aligned | No demo fallback | Visible binding, loading/error, stale identity/timeframe clear | 🟨 |
| Footprint | Deterministic SIMULATED data | Simulation only | Owner reference + reviewed blueprint + ON-only cluster renderer | 🟨 gated |
| Heatmap | No verified implementation | None | Reference, blueprint, source, calculations, renderer, tests | 🟥 |
| Liquidation Maps | No verified implementation | None | Reference, blueprint, source, calculations, renderer, tests | 🟥 |

**Indicator invariants:** warm-up nulls stay at original candle indexes; 18 timeframe formula fixtures do not prove live provider quality or visible integration. Footprint OFF retains standard candles; explicit ON alone enables spaced cluster layout. Footprint/Heatmap/Liquidation visual work awaits owner references and reviewed blueprint. Stage 1 active; Stage 4 visible indicator UI parked.

## Progress accounting
- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks.
- Gate 10: **0/10 closed**.
- Stages 2–6: NOT SCORED.
- Overall project: NOT ESTABLISHED.
- ZERO COST; no deployment; no Termux; main untouched.

---

# CURRENT VERIFIED PROJECT STATUS — BATCH 62B

**Date:** 19 November 2026 • **Branch:** phase-2/market-data-foundation • **Pre-cycle HEAD:** 97880bda671231a803d1abb06865fc849c16d686  
**Cost:** ZERO COST • no deploy • Termux not required • main untouched.

## Batch 62A exact-head CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests + Build | [44487591377](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44487591377) | SUCCESS |
| CodeQL JS/TS + Python | [44487591390](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44487591390) | SUCCESS |
| Full Git History Secret Audit | [44487591396](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44487591396) | SUCCESS |

Backend pytest **1,044 passed in 36.68s**; frontend Vitest **236 passed / 28 files**; npm audit **0 vulnerabilities**; pip-audit **no known vulnerabilities**. Container smoke passed Redis ACL/AOF restart, outage fail-closed/reconnect, non-root/volume ownership, SQLite integrity/restart and HTTP rate-limit checks. Synthetic outbox benchmark and Trivy report uploaded. These are CI results, not production acceptance.

## Gate 10 — all remain OPEN

| Gate | Remaining acceptance evidence |
|---:|---|
| 8 | Owner-host secret injection, protected mounts, runtime readback |
| 20 | Firebase valid/expired/revoked/wrong-project E2E |
| 25 | Owner Redis, independent app instances, outage/recovery and operator evidence |
| 30 | Actual owner target-database restore |
| 31 | Zero-cost off-host copy, separate key custody, retention and restore |
| 34 | Owner-host volume/restart/disk-pressure evidence |
| 35 | Public HTTPS/WSS ingress, certificate renewal and external scan |
| 36 | Snapshot-consistent cross-instance fan-out, browser/WebView and 330-second attribution |
| 38 | Durable cross-instance collector, retention and protected access |
| 39 | Named operator, escalation channel and acknowledgement drill |

**Formal closure: 0/10.** Gate 25 gains process-level CI evidence only if Batch 62B passes. Gate 36 is blocked by missing snapshot-consistent multi-instance data topology in addition to external runtime acceptance.

## Complete indicator progress ledger

| Indicator | Calculation foundation / first valid output | Remaining visible work | State |
|---|---|---|---|
| SMA 20 | Rolling close mean; index 19; fixture-tested | Overlay, toggle, legend/value, stale-series clearing, render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA, alpha 2/21; index 19; tested | Overlay, toggle, legend/value, stale-series clearing, render tests | 🟨 Foundation |
| RSI 14 Wilder | Wilder-smoothed gains/losses; index 14; tested | 0–100 pane, 30/70 guides, toggle, lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | EMA12−EMA26; MACD index 25, signal/histogram index 33; tested | Dedicated pane, signal, histogram, zero guide, render tests | 🟨 Foundation |
| Bollinger 20,2 | Population standard deviation, 2σ; index 19; tested | Upper/middle/lower overlay, toggle, legend/value, render tests | 🟨 Foundation |
| Shared useMarketIndicators() | Validated backend snapshot only; no demo fallback; warm-up nulls aligned | Visible binding, loading/error, immediate stale identity/timeframe clearing | 🟨 Foundation |
| Footprint | Deterministic simulation, explicitly SIMULATED | Owner reference, reviewed blueprint, explicit-ON spaced cluster renderer | 🟨 Gated |
| Heatmap | No verified implementation | Reference, blueprint, source contract, calculation, renderer, tests | 🟥 Not implemented |
| Liquidation Maps | No verified implementation | Reference, blueprint, source contract, calculation, renderer, tests | 🟥 Not implemented |

**Invariants:** warm-up outputs remain null and aligned to source candle indexes; fixture formula tests across 18 timeframes are not provider data-quality or visible-integration proof. Footprint OFF preserves standard candles; only explicit ON enables spaced cluster layout. Footprint/Heatmap/Liquidation visual work waits for owner references and reviewed blueprint. Stage 1 is active; Stage 4 visible indicator UI remains parked.

## Progress accounting

- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks.
- Gate 10: **0/10 closed**.
- Stages 2–6: NOT SCORED.
- Overall project: NOT ESTABLISHED; historical 20.9% is not current.
- ZERO COST; no deployment; no Termux; main untouched.

---

# BATCH 57 — Exact-head CI closure and indicator acceptance reconciliation

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Verified source HEAD:** `66c8a6741b1abe4d1e89ef0d5ad6ce0abb72a77d`  
**Cost:** ZERO COST • **Deployments:** none • **Termux:** not required • `main`: untouched

## 1. Exact-head CI evidence

All four push-triggered workflows associated with the exact source HEAD completed successfully:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44475945219](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945219) | SUCCESS |
| CodeQL Python + JavaScript/TypeScript | [44475945132](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945132) | SUCCESS |
| Full Git History Secret Audit | [44475945214](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945214) | SUCCESS |
| Android debug APK CI build | [44475945152](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44475945152) | SUCCESS |

Automated Tests job: all 32 steps succeeded. Frontend Vitest: **236 passed across 28 files**. Backend pytest: **1,040 passed in 34.00 seconds**. Frontend `npm audit --audit-level=high`: **0 vulnerabilities**. Backend dependency audit: **no known vulnerabilities**. Frontend source credential scan checked 78 files; bundle scan checked 5 files. Backend container smoke verified health, scoped Redis ACL authentication, Redis AOF persistence across restart, fail-closed behavior during Redis outage, reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection. Trivy scan/report completed and the report was uploaded; this does not substitute for production-host acceptance.

The Android workflow built the debug APK in CI. No APK was published or installed on the owner's device.

## 2. WebSocket Batch 56C — source and CI disposition

Verified changes at this HEAD:
- WebSocket principal is initialized before the authentication handshake wait; the finally path releases the global lease with a null subject when no principal was established.
- Missed periodic ticket renewal closes with transient code 1013, allowing a fresh ticket on reconnect; actual Firebase HTTP 401 remains terminal.
- Initial HTTPS ticket endpoint 401 stops the supervisor rather than retrying indefinitely.
- Frontend regression covers terminal initial-ticket 401; backend regression covers lease release when the initial auth frame times out.
- The supervisor retains bounded reconnect behavior and obtains a fresh Firebase ID token/ticket on each new connection attempt.

**Disposition:** source-level Batch 56C and exact-head automated CI are PASS. Gate 36 remains OPEN because public authenticated WSS, Firebase production valid/expired/revoked/wrong-project E2E, Android WebView foreground/background, 330-second attribution, and cross-instance fan-out have not been externally demonstrated. The synthetic POC remains synthetic-only.

## 3. Gate 10 — formal status unchanged

**0/10 formally closed; 10/10 remain OPEN.** CI success is supporting repository evidence, not owner-host acceptance.

| Gate | Internal evidence | Remaining acceptance blocker |
|---:|---|---|
| 8 | Repository/runtime configuration | Owner-host secret injection, protected mounts, runtime log/readback |
| 20 | HTTPS single-use ticket endpoint and WSS renewal | Real Firebase project valid/expired/revoked/wrong-project E2E |
| 25 | Redis atomic ticket consumption and scoped ACL | Independent owner Redis, multi-instance and outage drill |
| 30 | SQLite backup/restore implementation and CI tests | Actual owner target-database restore drill |
| 31 | Authenticated encryption and restore tests | Zero-cost off-host copy, separate key custody, retention and off-host restore |
| 34 | Container volume and restart smoke | Owner-host volume/restart/disk-pressure evidence |
| 35 | HTTPS/WSS configuration source | Public ingress, certificate renewal and external scan |
| 36 | Ticket protocol and lifecycle source tests | Browser/WebView, 330-second attribution and cross-instance fan-out |
| 38 | Local metrics/alert components | Durable cross-instance collector, retention and protected access |
| 39 | Local incident reporting components | Named operator, escalation channel and acknowledgement drill |

## 4. Technical indicator progress ledger

This is a capability ledger, not an invented completion percentage. Stage 1 remains the active official stage. Visible indicator controls, overlays and oscillator panes remain Stage 4 work; the existing UI blueprint is parked and implementation authorization is not granted during Stage 1.

| Indicator / component | Calculation or data foundation | Visible integration / acceptance | State |
|---|---|---|---|
| SMA 20 | Close-based rolling mean; first value at index 19; unit tests | Overlay, toggle, legend/current value, identity/timeframe clearing and render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; first value at index 19; unit tests | Overlay, toggle, legend/current value, identity/timeframe clearing and render tests | 🟨 Foundation |
| RSI 14 Wilder | Wilder-smoothed gains/losses; first value at index 14; flat/rising edge tests | Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | MACD starts index 25; signal/histogram start index 33; warm-up tests | Dedicated pane, MACD/signal lines, histogram, zero guide and render tests | 🟨 Foundation |
| Bollinger 20,2 | Population standard deviation; first value at index 19; unit tests | Upper/middle/lower overlay, toggle, legend/current value and render tests | 🟨 Foundation |
| Shared `useMarketIndicators()` | Exact validated backend snapshot only; DEMO/loading/unavailable/error produce null | Visible controls and immediate stale-series clearing on identity change | 🟨 Foundation |
| Footprint | Bounded deterministic simulation, explicitly labelled `SIMULATED` | Owner reference image, reviewed blueprint, ON-only spaced cluster renderer | 🟨 Gated |
| Heatmap | No implementation verified | Reference image, reviewed blueprint, source contract, calculations, rendering and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Reference image, reviewed blueprint, source contract, calculations, rendering and tests | 🟥 Not implemented |

### Calculation contract

- SMA 20 and EMA 20 use close values; EMA is seeded from the initial SMA window.
- RSI 14 uses Wilder smoothing. Its first output is at source index 14.
- MACD uses EMA 12 minus EMA 26; its first MACD value is at index 25 and signal/histogram first become available at index 33.
- Bollinger 20,2 uses population variance (division by period), with the first complete window at index 19.
- Warm-up values are null; outputs remain aligned to original candle indexes.
- The hook reads only non-empty validated backend bars in ready/degraded state; no demo fallback is allowed.
- Current unit tests exercise all five calculations across 18 timeframe labels. This proves formula execution against fixture bars, not provider-backed data quality or visible timeframe integration.

### Visual/data integrity constraints

- Footprint OFF preserves ordinary candlestick layout and spacing.
- Only explicit Footprint ON may enable the dedicated spaced-candle/cluster layout.
- Footprint, Heatmap and Liquidation Maps visual work remains blocked on the owner's relevant reference image(s) and a reviewed scoped blueprint.
- Do not add visible indicator UI during Stage 1; preserve the Stage 4 roadmap gate.
- No indicator percentage credit is awarded from general CI, calculation tests, or documentation alone.

## 5. Progress accounting

- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks; this is not a final certification.
- Gate 10: **0/10 formally closed**, 10 OPEN.
- Stage 2–6: NOT SCORED.
- Overall project: **NOT ESTABLISHED**. Historical 20.9% is not a current weighted score.
- CI: exact-head automated tests, CodeQL, secret-history audit, and Android debug build all PASS.
- Deployment: none. Billing: none. Termux: not required. Main branch: untouched.

## 6. Next work cycle

1. Preserve Batch 56C source and use its exact-head CI as the current baseline.
2. Advance Gate 20/25 only through controlled Firebase and independent Redis acceptance evidence; do not claim production readiness from mocks.
3. Continue Gate 36 external runtime acceptance without creating another deployment merely to generate logs.
4. Batch Gate 30/31/34 evidence work around backup, key custody, and persistence; do not assume a free off-host destination exists.
5. Keep indicator UI parked until the official Stage 4 authorization gate. Continue only source/data-contract audit and documentation during Stage 1.

# BATCH 56C — Authentication failure and lease lifecycle hardening

- Initialized the WebSocket principal before the handshake wait, so timeout, disconnect, malformed frame, and invalid-ticket exits all release the reserved global Redis lease with a null account subject when no principal exists.
- Missed periodic renewal now closes with transient 1013 rather than terminal 4401. The supervisor can reconnect and obtain a fresh ticket after a temporary background/network delay; actual Firebase 401 remains terminal.
- Initial HTTPS ticket endpoint 401 now stops the supervisor instead of retrying forever. Transient 429/5xx/network failures retain bounded exponential backoff.
- Added backend coverage for lease release when the initial auth frame times out and frontend coverage for terminal initial-ticket 401.

**Gate 10:** no gate closure awarded. Gate 20/25 code paths strengthened; external Firebase/host/browser acceptance remains open. Stage 1 stays 75% provisional, Gate 10 stays 0/10, overall project score NOT ESTABLISHED.

# BATCH 56B — Frontend ticket lifecycle, Redis ACL parity, and integration hardening

- Frontend supervisor now exchanges fresh Firebase ID tokens over HTTPS for each connection and renewal. WebSocket frames carry only opaque tickets.
- WebSocket client renews at 45 seconds, validates a 10-second acknowledgement deadline, and closes terminally on HTTP 401.
- CORS now permits POST for ticket issuance when optional alert-device storage is disabled.
- Global Redis connection lease is released when ticket authentication fails before a principal exists.
- Redis ACL grants SET/GET/DEL only within the existing guard key patterns; unrelated key access remains denied. CI smoke tests scoped SET and Lua GET/DEL.
- Added CORS preflight coverage, client renewal coverage, and Redis Lua single-use integration coverage.

**Timing:** ticket TTL 90 seconds; renewal 45 seconds; server authorization deadline 60 seconds; ACK timeout 10 seconds. Approximate ticket issuance: 60/45 = 1.33 requests/minute/active socket.

**Gate 10:** Gate 20/25 repository implementation strengthened; all external Firebase/host/browser evidence remains open. Gate 10 stays **0/10 formally closed**. Stage 1 remains 75% provisional. Overall project percentage remains NOT ESTABLISHED.

**Indicators:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9 and Bollinger20,2 have calculation foundations/tests but no visible integration; shared hook exists without controls/panes. Footprint remains offline simulation awaiting reference image; Heatmap and Liquidation Maps remain unimplemented. Footprint OFF preserves standard candle spacing.

# BATCH 56 — Redis-backed single-use WebSocket ticket backend

**Date:** 19 November 2026 (WIB) • **Branch:** `phase-2/market-data-foundation` • **Base:** `36c6e976a6199ce60784a457d1f87d42b1542ee7`  
**Cost:** ZERO COST • no deployment • no billing • no Termux • `main` untouched

## Backend implementation
- Added `backend/app/websocket_tickets.py`: 90-second single-use in-memory store for development/tests only.
- RedisSharedGuard issues 256-bit opaque tickets; Redis stores only SHA-256 digest-keyed records with verified subject/purpose, TTL 90 seconds, and atomic Lua GET+DEL consumption. Raw ticket is never stored in Redis.
- Added `POST /v1/auth/websocket-ticket`; Firebase Bearer verification includes revocation checking. Existing `/v1/` shared HTTP rate limit and no-store response headers apply.
- Production WSS now requires ticket auth; legacy token-in-frame remains only for non-production compatibility.
- Added subject-bound `auth.renew` frames. Server consumes each renewal ticket once, rechecks instrument entitlement, acknowledges, and advances the 60-second authorization deadline. Missing renewal closes 4401.

## Engineering calculations
| Parameter | Value | Rationale |
|---|---:|---|
| Ticket entropy | 256 bits | 32 random bytes |
| Ticket TTL | 90 s | Renewal margin |
| Renewal target | 45 s | 15 s slack before deadline |
| Server deadline | 60 s | Preserves prior revalidation cadence |
| Redis consume | One-key Lua GET+DEL | Atomic single-use across workers |
| Memory fallback | Non-production only | Local development without paid Redis |

The planned frontend performs 60/45 = 1.33 ticket exchanges/minute per active connection plus reconnects. Existing shared HTTP limits cover issuance. No production capacity claim is made.

## Tests added
- Redis fake-client digest/replay/purpose tests.
- Backend endpoint issue/replay/invalid-bearer tests and WSS renewal acknowledgement test.
- Frontend integration and final exact-head CI are the next acceptance slice.

## Gate 10
| Gate | Batch 56 impact | Remaining blocker | Status |
|---:|---|---|---|
| 8 | None | Host secret injection, protected mounts, runtime log/readback | OPEN |
| 20 | Ticket endpoint + WSS single-use renewal implemented | Real Firebase project valid/expired/revoked/wrong-project E2E | OPEN |
| 25 | Redis atomic ticket consumption integrated | Independent owner Redis, multi-instance/outage drill | OPEN |
| 30 | None | Actual owner database restore evidence | OPEN |
| 31 | None | Zero-cost off-host copy, separate key custody, retention/restore | OPEN |
| 34 | None | Owner-host volume/restart/disk-pressure evidence | OPEN |
| 35 | None | Public HTTPS/WSS ingress, cert renewal, external scan | OPEN |
| 36 | Protocol upgraded | Browser, Android WebView, 330-second attribution, cross-instance fanout | OPEN |
| 38 | None | Durable cross-instance collector, retention and protected access | OPEN |
| 39 | None | Named operator, escalation channel and acknowledgement drill | OPEN |

## Indicator inventory
| Indicator | Calculation foundation | Visible integration | State |
|---|---|---|---|
| SMA 20 | Implemented + tested | Not integrated | 🟨 |
| EMA 20 | Implemented + tested | Not integrated | 🟨 |
| RSI 14 Wilder | Implemented + tested | Not integrated | 🟨 |
| MACD 12/26/9 | Implemented + tested | Not integrated | 🟨 |
| Bollinger 20,2 | Implemented + tested | Not integrated | 🟨 |
| `useMarketIndicators()` | Shared validated snapshot hook | No controls/panes | 🟨 |
| Footprint | Offline deterministic simulation | Await reference visual | 🟨 |
| Heatmap | Not implemented | Not implemented | 🟥 |
| Liquidation Maps | Not implemented | Not implemented | 🟥 |

Seven calculation tests remain in frontend suite; 18 timeframe coverage is not visible integration. Footprint OFF preserves ordinary candle spacing. Footprint/Heatmap visuals remain blocked on reference images.

## Progress accounting
- Stage 1: 🟩 **75% provisional**, 30/40 criteria, 300/400 ticks.
- Gate 10: 🟥 **0/10 formally closed**. Gate 20/25 repository implementation improved; external evidence remains.
- Stage 2: 🟦 NOT SCORED • Stage 3: 🟪 NOT SCORED • Stage 4: 🟨 NOT SCORED.
- Stage 5: 🩷 NOT SCORED • Stage 6: ⬜ NOT SCORED.
- Overall: **NOT ESTABLISHED**; historical 20.9% is not a current weighted score.

# BATCH 55 — WebSocket authentication audit, ticket-exchange design, and final-head CI

**Date:** 19 November 2026 (WIB)  
**Active branch:** `phase-2/market-data-foundation`  
**Source baseline audited:** `baac62e150a8cd886b584095e825a43cdc839eee`  
**Final-head CI:** Automated Tests & Build [44471059444](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44471059444) — **SUCCESS, all 32 steps** • CodeQL [44471059411](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44471059411) — **SUCCESS, JavaScript/TypeScript + Python** • Full-history Secret Audit [44471059343](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44471059343) — **SUCCESS**  
**Cost:** ZERO COST • **Deployments:** none • **Termux:** not required • **main:** untouched

## 1. Final-head CI closure

The two previously pending workflows have now completed successfully. The Automated Tests & Build job reports every step completed with SUCCESS, including frontend dependency audit, frontend tests/build, source and bundle credential scans, Android preflight/publisher tests, backend tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy scan and artifact export. CodeQL completed both language jobs. The separate full-history secret audit also succeeded.

This confirms the final documentation baseline's automated checks. It does not convert CI fixtures into owner-host or production acceptance evidence.

## 2. WebSocket authentication — verified current behavior

Audited:
- `backend/app/main.py`
- `backend/app/identity.py`
- `backend/app/shared_guard.py`
- `backend/tests/test_shared_guard.py`
- `poc/vercel_ws/index.py`
- `backend/tests/test_vercel_ws_poc.py`
- `poc/vercel_ws/vercel.json`

Production market-data WSS currently:
1. Accepts the socket after the origin and global-capacity checks.
2. Requires an initial `{"type":"auth","token":"<Firebase ID token>"}` frame within five seconds.
3. Verifies the Firebase ID token server-side with revocation checking and issuer/audience/subject/auth-time validation.
4. Reserves the account-scoped Redis WebSocket lease using the verified principal subject.
5. Rechecks Firebase identity/revocation every 60 seconds and renews the Redis lease every one-third of its configured lease duration (default 45 seconds → 15 seconds).
6. Fails closed on identity-provider or shared-guard failures.

The isolated Vercel POC is a separate synthetic-only endpoint. Its 10-test suite covers health, browser probe headers, ping/pong, fresh sessions, message bounds, invalid frames, rate limiting and idle close. It does not authenticate production accounts or carry market data. Its deployment remains SSO-protected and project `live=false`.

## 3. Root cause boundary and WebSocket ticket-exchange design

**Confirmed design gap:** the production socket currently receives the Firebase ID token in its first WebSocket application frame. WSS encrypts transport, so this is not a plaintext-network leak; however, a short-lived, single-use, narrowly scoped ticket is a better boundary for the WebSocket handshake and avoids placing the long-lived Firebase bearer token in the socket protocol.

**Safe target protocol (design only; not yet implemented):**

1. Client obtains a current Firebase ID token using the existing Firebase Auth SDK.
2. Client calls a same-origin HTTPS ticket endpoint with that ID token in the HTTP Authorization header.
3. Backend verifies the Firebase token using the existing `FirebaseIdentityVerifier` with revocation checking. The account subject is always derived from verified claims.
4. Backend creates a cryptographically random opaque ticket (at least 256 bits). Redis stores only a digest-keyed, short-lived record containing the verified subject and narrowly defined purpose/audience metadata; the raw ticket is returned once to the client and never logged.
5. Client opens WSS and sends only the opaque ticket in the initial auth frame.
6. Backend atomically consumes the ticket with a Redis Lua operation (single-use, race-safe, TTL-enforced). Missing, expired, replayed, wrong-purpose, or malformed tickets fail closed. Ticket consumption and connection-lease acquisition must be ordered so failed capacity reservation cannot leave an authenticated unleased socket.
7. Preserve periodic revocation checks without storing the raw Firebase ID token in Redis: the client obtains a fresh ticket over HTTPS before the authorization deadline and sends a bounded re-auth frame; the server atomically consumes it, verifies that the subject is unchanged, and refreshes the authenticated session. If renewal is absent, invalid, replayed, or identity changes, close the socket. This preserves the current 60-second revocation/authorization boundary without persisting a Firebase bearer token in Redis.
8. Apply shared HTTP rate limits to ticket issuance and strict size/time limits to WSS auth/renewal frames. Ticket values, Firebase tokens, and raw subjects must never appear in logs, metrics labels, URLs, or Redis key names.

**Acceptance tests required before merge:** ticket expiry; single-use replay rejection; concurrent double-consume race; wrong purpose; malformed/oversized ticket; subject binding; account/global connection cap interaction; Redis unavailable fail-closed; ticket endpoint rate limit; token revoked between ticket issue and renewal; renewal timeout; reconnect obtains a fresh ticket; and no credential leakage in logs. Redis integration tests must exercise the actual Lua consume operation, not only a fake client.

**Why no speculative code patch was made:** this change spans the HTTP identity boundary, Redis atomic storage, WebSocket state machine, frontend token lifecycle and revocation semantics. A process-local ticket cache would fail across server instances; storing raw Firebase tokens in Redis would weaken credential custody; simply removing the 60-second revalidation would regress revocation handling. The design above resolves those hazards before implementation. The existing production authentication path remains unchanged and fail-closed.

## 4. Gate 10 — multi-gate evidence reconciliation

| Gate | Repository evidence / progress | Remaining acceptance blocker | Status |
|---:|---|---|---|
| 8 | Settings redaction, frontend source/bundle scans, reachable Git-history secret scan | Actual owner-host secret injection, protected file mounts and runtime log/readback proof | OPEN |
| 20 | Firebase client/server auth boundary; revocation/issuer/audience checks | Real owner Firebase valid/expired/revoked/wrong-project E2E; implement and test scoped WSS tickets | OPEN |
| 25 | Atomic Redis Lua HTTP limits and WS leases; TLS CA/hostname checks; ACL; fail-closed CI smoke | Independent owner-controlled Redis, network/TLS and multi-instance contention/outage drill | OPEN |
| 30 | Encrypted backup/decrypt/restore CI drill; committed fresh-connection readback | Restore the actual owner-controlled application database and verify recovery evidence | OPEN |
| 31 | Authenticated encryption and tamper/wrong-key tests | Zero-incremental-cost off-host copy, separate recovery-key custody, retention and restore drill | OPEN |
| 34 | CI mounted-volume ownership, SQLite integrity and restart persistence | Owner-host mounted volume, restart and disk-pressure evidence | OPEN |
| 35 | Exact HTTPS CORS validation and internal ASGI port boundary | Owner-controlled public HTTPS/WSS ingress, certificate renewal, HSTS/redirect and external TLS/WebView checks | OPEN |
| 36 | Isolated SSO-protected synthetic WSS POC; 10 local protocol tests | Authenticated owner-browser round-trip, Android WebView, 330-second close attribution, effective Fluid readback and cross-instance fanout | OPEN |
| 38 | Bounded 127-series process-local metrics, sanitization, locking and concurrency tests | Host collector, durable/cross-instance aggregation, retention and protected access | OPEN |
| 39 | Sanitized local transition/recovery reporter and deduplication tests | Host log collection, named operator, verified escalation channel and acknowledgement/recovery drill | OPEN |

No gate is closed by this source audit or CI alone. No external evidence was fabricated.

## 5. Technical indicator inventory — complete current state

| Indicator / layer | Calculation or data foundation | Visible chart integration | Current disposition |
|---|---|---|---|
| SMA 20 | Calculation + warm-up tests | Not integrated | Stage 4 parked |
| EMA 20 | Calculation + seeded-SMA warm-up tests | Not integrated | Stage 4 parked |
| RSI 14 (Wilder) | Calculation + index-14 warm-up tests | Not integrated | Stage 4 parked |
| MACD 12/26/9 | Calculation + line/signal warm-up tests (indices 25/33) | Not integrated | Stage 4 parked |
| Bollinger 20,2 | Calculation + population-deviation tests | Not integrated | Stage 4 parked |
| `useMarketIndicators()` | Shared hook consumes validated selected backend snapshot; DEMO/loading/unavailable/error suppression | No controls or panes | Stage 4 parked |
| Footprint | Deterministic offline simulated aggregation + fixtures | Visual not implemented; OFF must preserve ordinary candle spacing | Await owner visual reference |
| Heatmap | No implementation verified | Not implemented | Await owner visual reference |
| Liquidation Maps | No implementation verified | Not implemented | Await owner visual reference |

Seven calculation tests pass within the 234-test frontend suite and cover all 18 configured timeframes, warm-up alignment and invalid inputs. These calculations are groundwork, not finished visible features. Do not begin Footprint or Heatmap visual work before receiving the owner's corresponding reference images.

## 6. Colored progress accounting — unchanged, evidence-based

- **Stage 1:** 🟩 **75% provisional** — 30/40 criteria, 300/400 ticks.
- **Gate 10:** 🟥 **0/10 formally closed** — all ten criteria listed above remain open.
- **Stage 2:** 🟦 NOT SCORED.
- **Stage 3:** 🟪 NOT SCORED.
- **Stage 4:** 🟨 NOT SCORED (indicator calculation foundations only; visible UI parked).
- **Stage 5:** 🩷 NOT SCORED.
- **Stage 6:** ⬜ NOT SCORED.
- **Overall project:** **NOT ESTABLISHED**. Historical 20.9% is not a newly weighted project score; M1–M8 weights/criterion mapping remain unapproved.
- No stage ticks, gate closures, or overall percentage points are awarded for documentation, CI, or source-level evidence alone.

## 7. ZERO COST and operations

No deployment, Vercel/Cloudflare repeated push, billing activation, paid provider, paid Redis, paid monitoring, production promotion, or Termux operation was performed. No Termux action is currently required. The branch deployment guard remains the existing control; do not trigger a throwaway deployment to test WSS behavior.

**Next engineering sequence:** implement the Redis-backed single-use ticket primitives and HTTP issuance endpoint with focused backend tests; then integrate the WSS initial-ticket and re-auth renewal state machine; then update the frontend token/ticket lifecycle; finally run exact-head CI. Owner browser/Android and external host proofs remain separate acceptance steps. Major implementation stays behind the documented protocol review boundary.

---

# DEZZTA CHART — Project Progress Indicator (Current Snapshot)

**Audit:** 19 November 2026 — Batch 54  
**Active branch:** `phase-2/market-data-foundation` • **Audited HEAD:** `fba43a12017e314baeb9e2719a50b441274126c6`  
**Automated Tests:** [44470207284](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207284) — SUCCESS  
**CodeQL:** [44470207308](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207308) — SUCCESS  
**Full Git History Secret Audit:** [44470207366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207366) — SUCCESS  
**Tests:** Frontend 234/234 • Backend 1,032/1,032 • npm audit 0 vulnerabilities • Trivy report 0 vulnerabilities  
**ZERO COST:** no deploy / paid services / billing activation • **Termux:** not required • **main:** untouched

![Six-stage colored project dashboard](assets/project-progress-dashboard-current.svg)

## Batch 54 verified results

- Parsed exact-head Trivy JSON artifact: **0 vulnerabilities** reported in CI backend image.
- Parsed synthetic outbox benchmark: 1,000 bars/events persisted and replayed; persist p95 10.20 ms; concurrent replay page p95 1.62 ms. One-process synthetic benchmark only, not a production SLO.
- Gate 8/20/25/35 source and configuration audit completed. Source-level controls exist; production host, identity provider, Redis and TLS acceptance remain external.
- WSS preview remains SSO-protected and synthetic-only; no new deployment, SSO bypass or fabricated browser round-trip.
- Full report: [WORK_CYCLE_2026-11-19_BATCH54_CI_ARTIFACT_FORENSICS_GATE8_20_25_35.md](WORK_CYCLE_2026-11-19_BATCH54_CI_ARTIFACT_FORENSICS_GATE8_20_25_35.md).

## Indicator tracker

| Indicator | Calculation/data foundation | Visible chart |
|---|---|---|
| SMA 20 | Implemented + tested | Not integrated; Stage 4 parked |
| EMA 20 | Implemented + tested | Not integrated; Stage 4 parked |
| RSI 14 Wilder | Implemented + tested | Not integrated; Stage 4 parked |
| MACD 12/26/9 | Implemented + tested | Not integrated; Stage 4 parked |
| Bollinger 20,2 | Implemented + tested | Not integrated; Stage 4 parked |
| Shared indicator hook | Implemented; validated selected backend snapshot only | No controls/panes |
| Footprint | Offline deterministic simulation + fixtures | Wait for owner reference; OFF preserves standard spacing |
| Heatmap | Not implemented/verified | Wait for owner reference |
| Liquidation Maps | Not implemented/verified | Wait for owner reference |

Seven calculation tests pass in the 234 frontend suite, including all 18 configured chart timeframes. No DEMO/loading/unavailable/error value is represented as live.

## Progress accounting

- Stage 1: **75% provisional — 300/400 ticks, 30/40 criteria**.
- Gate 10: **0/10 formally closed**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain OPEN.
- Stages 2–6: **NOT SCORED**.
- Overall project: **NOT ESTABLISHED**; historical 20.9% remains historical only.
- No ticks or points awarded for audit/documentation/CI alone.

# DEZZTA CHART — Project Progress Indicator (Current Snapshot)

**Audit timestamp:** 19 November 2026 — Batch 53 exact-head CI and Gate 10 evidence audit  
**Active branch:** `phase-2/market-data-foundation`  
**Exact-head CI commit:** `8f377cfb07b082ce237cf3ac9137efbfbcc4f5d8`  
**Automated Tests:** [44468970676](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970676) — SUCCESS, 32/32 steps  
**CodeQL:** [44468970595](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970595) — SUCCESS, both language jobs  
**Full Git History Secret Audit:** [44468970614](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970614) — SUCCESS  
**Test totals:** Frontend 234/234 across 28 files • Backend 1,032/1,032 • npm audit 0 vulnerabilities  
**Main:** untouched • **Cost:** ZERO COST • **Termux:** not required  
**Indicator:** documentation/dashboard only; NOT inside APK.

![Six-stage colored project dashboard](assets/project-progress-dashboard-current.svg)

## Latest work cycle — Batch 53 (exact-head CI + Gate 10 evidence)

- The exact Batch 52 branch HEAD passed all 32 Automated Tests & Build steps, CodeQL Python + JS/TS, and full Git-history secret audit.
- Backend CI verified container build, Redis ACL/AOF, fail-closed outage behavior, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and Trivy HIGH/CRITICAL scan/report.
- Gate 30 integrated encrypted application restore drill is CI-verified but still lacks an owner target-host recovery.
- Gate 31 encryption and tamper/wrong-key coverage pass; no off-host artifact or separate key custody is verified.
- Gate 34 mounted-volume smoke passes in CI only; actual host volume and disk-pressure evidence remain absent.
- The WSS POC preview remains READY and SSO-protected with project `live=false`. No runtime logs/errors appeared in the queried windows; this is not a successful WSS round-trip. Effective Fluid Compute setting is not exposed by the current project-details read-back.
- No new deployment, SSO bypass, production promotion, paid resource, or Termux operation.

### Technical indicator tracker

| Indicator / layer | Calculation/data foundation | Visible chart status |
|---|---|---|
| SMA 20 | Implemented + tested | Not integrated; Stage 4 parked |
| EMA 20 | Implemented + tested | Not integrated; Stage 4 parked |
| RSI 14 Wilder | Implemented + tested | Not integrated; Stage 4 parked |
| MACD 12/26/9 | Implemented + tested | Not integrated; Stage 4 parked |
| Bollinger 20,2 | Implemented + tested | Not integrated; Stage 4 parked |
| Shared indicator hook | Implemented; exact validated backend snapshot only | No controls/panes |
| Footprint | Offline deterministic simulation + fixtures | Wait for owner visual reference; OFF keeps standard candle spacing |
| Heatmap | No implementation verified | Wait for owner visual reference |
| Liquidation Maps | No implementation verified | Wait for owner visual reference |

Indicator test coverage: 7 calculation tests pass within the 234 frontend tests, including all 18 configured timeframes and warm-up/edge validation. These are not visible feature-completion credit.

### Progress accounting

- Stage 1: **75% provisional (300/400 ticks; 30/40 criteria)**.
- Gate 10: **0/10 formally closed**; 8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain open.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; historical 20.9% retained without fresh recalculation.
- No Stage 1 tick or overall point awarded for CI/audit/documentation work alone.

Detailed report: [WORK_CYCLE_2026-11-19_BATCH53_CI_GATE10_WSS_INDICATOR_AUDIT.md](WORK_CYCLE_2026-11-19_BATCH53_CI_GATE10_WSS_INDICATOR_AUDIT.md).

---

# DEZZTA CHART — Project Progress Indicator (Current Snapshot)

**Audit timestamp:** 19 November 2026 — Batch 50 exact-head CI completed successfully  
**Active branch:** `phase-2/market-data-foundation`  
**Latest source SHA validated by CI:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`  
**Batch 50 exact-head CI:** SUCCESS — frontend 234/234 across 28 files; backend 1,032/1,032; frontend dependency audit (0 vulnerabilities), production build, source/bundle credential scans, Android preflight/publisher tests, backend dependency audit, backend container build, Redis/persistent-volume smoke, Trivy scan/report, Android APK, CodeQL, and Git-history secret audit all passed  
**Main:** untouched • **Cost:** ZERO COST  
**Indicator:** project documentation/dashboard only; NOT inside APK.

![Six-stage colored project dashboard](assets/project-progress-dashboard-current.svg)





## Latest work cycle — Batch 50 (socket already CLOSED before native close event)

**Source SHA:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`  
**Parent:** `a483d6627a1d406aa93feced856392fa4792369b`  
**Exact-head CI:** [Automated Tests 44422985332](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332).

### Defect and fix
- Batch 48/49 synthetic close notification covered a platform `socket.close()` exception.
- Batch 50 adds the adjacent terminal case: the socket already reports native `CLOSED` before its close event reaches the transport.
- The `fail()` path now sends the idempotent synthetic terminal notification in either case; a later native event cannot duplicate it.
- The regression test sets the fake socket to CLOSED, injects a protocol failure, and verifies one `onClose(1011, "OHLCV stream ended before close event")` notification.
- The fake supervisor socket was corrected to model browser semantics: when a close event is deferred, `readyState` remains CLOSING (2) until the deferred native event is delivered. This preserves the invariant that a replacement connection must not start while the old socket is still closing.

### CI correction trail
- First Batch 50 CI attempt `44422763320` failed in two places: the test insertion had a syntax error, and the supervisor fake incorrectly reported CLOSED before its intentionally deferred close event. The latter made the new fallback correctly trigger early, exposing an unrealistic test fixture.
- Corrected in commit `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`: fixed test syntax and made the fake's lifecycle match browser CLOSING → CLOSED ordering.
- Corrected exact-head run [44422985332](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332): **SUCCESS**, no failed steps.
- Frontend Vitest: **234 passed across 28 files**; backend pytest: **1,032 passed in 30.94 seconds**.
- Frontend npm audit: **PASS — 0 vulnerabilities**. Frontend production build, 77-file source/bundle credential scans, Android preflight/publisher tests, backend dependency audit, backend container build, shared Redis ACL + persistent-volume smoke, and Trivy image scan/report: PASS.
- Trivy report artifact [14482732766](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332/artifacts/14482732766); synthetic-only SQLite outbox benchmark [14482428443](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985332/artifacts/14482428443).
- Android APK [44422985353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985353): SUCCESS; artifact [14482822189](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985353/artifacts/14482822189). No preview release published.
- CodeQL [44422985334](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985334): SUCCESS.
- Full Git History Secret Audit [44422985415](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44422985415): SUCCESS.
- No dependency downgrade, override, advisory suppression, lockfile manipulation, or audit threshold weakening.

### Gate/progress accounting
- Gate 36 remains OPEN pending public WSS roundtrip, Android WebView lifecycle, effective host configuration, owner-observed 330-second session/close attribution and cross-instance fan-out.
- Gate 10 remains **0/10** formally closed; open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional (300/400 ticks; 30/40 criteria)**. No progress tick is awarded for source/test/doc work alone.
- Stages 2–6 NOT SCORED; overall project percentage NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST; no deployment; no Termux; `main` untouched.

---

## Latest work cycle — Batch 49 (explicit WebSocket close observer fallback)

**Source commit:** `a8589e816b349d72db3d9093fd4b71eb01288813`  
**Parent:** `33f988dddb2cb55291299d63884d069648555b6a`  
**Exact-head CI:** [Automated Tests 44421919543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919543) — **SUCCESS**.

### 1. Defect found
Batch 48 covered a failed close request inside the transport's protocol/error failure path. A separate public shutdown path remained: `connection.close()` caught a platform exception and set local state to `closed`, but did not notify `onClose`. A consumer waiting on the close callback could therefore remain unaware that the close request had failed. The same path also did not synthesize a notification if the socket was already in native CLOSED state but the close event had not yet been delivered.

### 2. Implementation
- The explicit `connection.close()` path now records whether the platform's `socket.close()` request threw.
- Local state is set to `closed` before any fallback notification.
- If the close request throws, or the socket is already CLOSED, the transport sends one synthetic abnormal-close notification: code `1006`, with a sanitized reason.
- The existing idempotent `notifyClose()` guard prevents duplicate delivery if a native close event arrives later.
- If the platform accepts the close request and the socket remains CLOSING, the implementation continues to wait for the native close event; no early synthetic event is emitted.
- No server protocol, authentication, entitlement, cursor, sequence, heartbeat cadence, retry formula, hosting, or market-data behavior changed.

### 3. Regression coverage
- Added a regression that forces the platform close request to throw during an explicit client close.
- It asserts the API does not throw, local state becomes `closed`, and the observer receives exactly one `(1006, "Client close request failed")` notification.
- Existing close-observer exception and failed-close reconnect regressions remain in place.

### 4. Exact-head validation
For source SHA `a8589e816b349d72db3d9093fd4b71eb01288813`:
- Automated Tests [44421919543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919543): **SUCCESS**, no failed steps.
- Frontend Vitest: **234 passed across 28 files**.
- Backend pytest: **1,032 passed in 31.09 seconds**.
- Frontend npm audit: **PASS — 0 vulnerabilities**.
- Frontend production build and 77-file source/bundle credential scans: PASS.
- Android preflight/publisher tests: PASS.
- Backend dependency audit, backend container build, shared Redis ACL + persistent-volume smoke, and Trivy image scan/report: PASS.
- Trivy report artifact [14483195008](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919543/artifacts/14483195008); synthetic-only benchmark [14482701506](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919543/artifacts/14482701506).
- Android APK [44421919500](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919500): SUCCESS; artifact [14481438680](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919500/artifacts/14481438680). No preview release published.
- CodeQL [44421919553](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919553): SUCCESS.
- Full Git History Secret Audit [44421919501](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44421919501): SUCCESS. Do not infer them from Batch 48.

### 5. Gate and progress disposition
- Gate 36 remains OPEN: public WSS roundtrip, Android WebView transport/lifecycle, effective host configuration, owner-observed 330-second session/close attribution, and cross-instance fan-out still require external acceptance evidence.
- Gate 10 remains **0/10** formally closed; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. No tick is awarded for this source/test/documentation batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST maintained. No deployment, paid service, or Termux use. `main` untouched.

---

## Latest work cycle — Batch 48 (WebSocket failed-close recovery)

**Implementation commit:** `8eef475b2562506a0afd69f64c1ec19f860ec295`  
**Lifecycle-order correction commit / exact-head CI SHA:** `0b0e710e7e5f9565157e4051bae0619bb4c48123`  
**Parent:** `b458cc38fbf87fa9e738ee33f01af522d55e1b25`.

### 1. Defect found
A deeper failure-path audit found that transport `fail()` could set its local state to `closed` after `socket.close()` threw, but the supervisor still depended on the platform's native `close` event to receive `onClose` and schedule a reconnect. If the close request itself failed, that native event was not guaranteed. The UI could remain `reconnecting` without a retry timer.

### 2. Implementation
- Added an idempotent `notifyClose(code, reason)` guard so consumer close observers are invoked at most once, even if a synthetic failure notification is followed by a late native event.
- When `fail()` calls `socket.close(1011, ...)` and that call throws, transport now reaches its local `closed` state and sends a synthetic terminal `onClose(1011, "OHLCV stream failure")`. The supervisor can then schedule its bounded reconnect.
- When `socket.close()` succeeds, the transport preserves the existing native close-event ordering; it does **not** notify early. This is important because the supervisor must continue waiting for the actual close event on the normal path.
- The native close listener now sets transport state to `closed` before delivering the idempotent close notification.
- No wire protocol, backend, authentication, entitlement, replay cursor, sequence rules, heartbeat cadence, retry formula, hosting, or deployment configuration changed.

### 3. Regression tests and correction trail
- Transport regression: force `socket.close()` to throw during a protocol failure; verify terminal state, one synthetic 1011 close notification, and no duplicate notification when a late native close event arrives.
- Supervisor regression: force a transport error and then make the fake platform `socket.close()` throw; verify the supervisor schedules and opens a second connection after the deterministic 50 ms jittered delay.
- First CI attempt on `8eef475b...` correctly caught a behavior regression: the first implementation notified `onClose` even when `socket.close()` succeeded, violating the existing test that requires waiting for the native close event. Corrected in `0b0e710e...`: synthetic notification is now limited to the actual close-request-exception path. The corrected exact-head run is authoritative.

### 4. Exact-head CI evidence
Corrected source SHA: `0b0e710e7e5f9565157e4051bae0619bb4c48123`.

- Automated Tests [44419292784](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292784): **SUCCESS**.
- Frontend Vitest: **234 passed across 28 files**.
- Backend pytest: **1,032 passed in 40.49 seconds**.
- Frontend dependency audit: **PASS**. The previous `GHSA-fc5q-39xc-vjpf` advisory was withdrawn on 18 November 2026; the exact-head npm audit step now passes. No package downgrade, speculative override, suppression, lockfile manipulation, or threshold weakening was used. Upstream advisory record: [GitHub Advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf); maintainer discussion: [picomatch PR #235](https://github.com/micromatch/picomatch/pull/235).
- Frontend production build and source/bundle credential scans: PASS (77 source files and 5 bundle files scanned).
- Android preflight and immutable publisher tests: PASS.
- Backend dependency audit: PASS.
- Backend container build and shared Redis ACL + persistent-volume smoke: PASS. Smoke covered backend health, persisted Redis ACL authentication, AOF data across restart, fail-closed API outage behavior, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection.
- Trivy image scan/report: completed successfully; report artifact [14482290116](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292784/artifacts/14482290116). This is a CI image scan, not external production-host acceptance.
- Synthetic SQLite outbox benchmark artifact [14481880886](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292784/artifacts/14481880886): synthetic-only; it is not production market-data performance evidence.
- CodeQL [44419292719](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292719): SUCCESS.
- Full Git History Secret Audit [44419292875](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292875): SUCCESS.
- Android debug APK [44419292989](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292989): SUCCESS; artifact [14480328998](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44419292989/artifacts/14480328998). Preview release was skipped; no release was published.

### 5. Gate and progress disposition
- Gate 36 remains OPEN: public WSS roundtrip, Android WebView transport/lifecycle, effective host configuration, owner-observed 330-second session/close attribution, and cross-instance fan-out still require external acceptance evidence.
- Gate 10 remains **0/10** formally closed; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. No tick is awarded for this source/test/documentation batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST maintained. No deployment, paid service, or Termux use. `main` untouched.

## Latest work cycle — Batch 47 (WebSocket supervisor observer isolation)

**Implementation source SHA:** `bec43c87a2b8022c2cd8bf83e1aad884158ab271`  
**Test-timing correction commit:** `6b82a3dd4ac20d0b6ee4e1b2b43b7f211de7f4dc`  
**Parent of implementation:** `44450dbcc087e92ed5119732a475a0d4e926066e`.

### Defect and correction
- The transport callbacks are now guarded (Batch 46), but the supervisor still directly invoked its own consumer-provided `onStatus` and `onError` callbacks.
- A throwing `onStatus` could interrupt `scheduleReconnect()` before its timer was installed. A throwing `onError` could interrupt error handling or terminal authentication/entitlement reporting.
- Supervisor status updates now commit local status first and isolate consumer observer exceptions.
- All supervisor error notifications now go through a best-effort `reportError()`; callback failure cannot interrupt reconnect, stop, or terminal error handling.
- Added regression test: both consumer observers deliberately throw; after a validated stream is established and transport fails, the supervisor must still schedule and open the next socket using the bounded retry delay.
- First CI attempt on implementation SHA `bec43c87...` exposed a test expectation error: the test waited 99 ms before asserting no reconnect, but deterministic jitter with min delay 100 ms and random=0 correctly schedules at 50 ms. This was a test timing mistake, not a product-code regression. Corrected the assertion to 49 ms + 1 ms in commit `6b82a3dd...`, matching the existing jitter calculation and neighboring tests. The corrected exact-head run is the authoritative result.
- No wire protocol, backend, auth, entitlement, replay, sequence, heartbeat, retry formula, or deployment setting changed.

### Exact-head CI snapshot
- Corrected source SHA: `6b82a3dd4ac20d0b6ee4e1b2b43b7f211de7f4dc`.
- Automated Tests [44336190424](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190424): **FAILURE only at final step 27, Enforce frontend dependency audit result**. Frontend Vitest: **232 passed across 28 files**. Backend pytest: **1,032 passed in 30.84 seconds**. Frontend production build, source/bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark/report, backend dependency audit, backend container build, shared Redis guard + persistent-volume smoke, and Trivy scan/report all passed.
- Trivy: **0 vulnerabilities** for Alpine 3.24.4 and all scanned Python package targets. Report artifact [14440834494](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190424/artifacts/14440834494) uploaded successfully. Synthetic outbox benchmark artifact [14440569027](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190424/artifacts/14440569027) uploaded; it is synthetic-only, not production market-data performance evidence.
- Sole failure is frontend `npm audit --audit-level=high`: **five High findings** for GHSA-fc5q-39xc-vjpf in `picomatch`. The advisory remains unresolved; no dependency downgrade, override, suppression, lockfile manipulation, or threshold weakening was applied.
- Full Git History Secret Audit [44336190330](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190330): SUCCESS.
- CodeQL [44336190195](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190195): SUCCESS for JavaScript/TypeScript and Python.
- Android APK [44336190344](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190344): SUCCESS; debug APK checksum verified and uploaded as artifact [14441103214](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44336190344/artifacts/14441103214). Preview release was skipped; no release was published.
- The corrected Batch 47 exact-head source is `6b82a3dd...`. Its npm audit failure was subsequently superseded: GitHub withdrew GHSA-fc5q-39xc-vjpf on 18 November 2026, and the Batch 48 exact-head npm audit passed without suppressions or dependency changes. See Batch 48 below. The earlier run on `bec43c87...` failed one newly added test because its 99 ms assertion was inconsistent with the actual 50 ms jittered retry; the test was corrected to 49 ms + 1 ms and passed on the authoritative corrected SHA. This was a test timing correction, not a production-code rollback.
- **Final CI conclusion:** Automated Tests is **FAILURE only because the fail-closed frontend dependency audit remains unresolved**. All functional tests, builds, backend/container/Redis checks, Trivy, APK, CodeQL, and secret-history checks passed. Do not call CI all-green.
- No deployment, paid service, or Termux use.

### Gate and progress disposition
- Gate 36 remains OPEN pending external public WSS, Android WebView, host configuration, owner-observed long session, and cross-instance fan-out evidence.
- Gate 10 remains **0/10** formally closed; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. No tick is awarded for this code/test/documentation batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST maintained. `main` untouched.

## Latest work cycle — Batch 46 (WebSocket lifecycle observer and socket failure hardening)

**Implementation source SHA:** `4f746496b23cc9208804023bbb554a4e07c6480b`  
**Parent source SHA:** `8fecf72ece008455c82221ffbabd59ea0b945cfd`.

### Defects and correction
- Batch 45 isolated exceptions from `onError`, but the remaining lifecycle callbacks could still throw into native WebSocket event dispatch.
- `onStatus` is now best-effort and cannot interrupt the transport state transition.
- `onClose` is now best-effort and cannot prevent the connection from entering its terminal `closed` state.
- Authentication-frame `socket.send()` exceptions are converted into a controlled terminal transport failure and reported through the isolated error observer.
- Explicit `connection.close()` now reaches local `closed` state even if the platform's `socket.close()` throws.
- Added three regression tests covering throwing status observers, authentication send exceptions, and close observer/platform close exceptions.
- Existing `onError` isolation remains intact. Snapshot/update/cursor callback failures still fail the stream closed rather than silently dropping data.
- No wire protocol, server route, heartbeat cadence, replay cursor, sequence semantics, authentication policy, entitlement, retry schedule, or deployment setting changed.

### Exact-head CI status
- Source SHA: `4f746496b23cc9208804023bbb554a4e07c6480b`.
- CodeQL [44334598939](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598939): SUCCESS for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44334598934](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598934): SUCCESS.
- Automated Tests [44334598973](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973): **FAILURE only at final step 27, Enforce frontend dependency audit result**. Frontend Vitest: **231 passed across 28 files**. Backend pytest: **1,032 passed in 30.78 seconds**. Frontend production build, source/bundle credential scans (77 source files), Android preflight/publisher tests, synthetic SQLite outbox benchmark/report, backend dependency audit, backend container build, shared Redis guard + persistent-volume smoke, and Trivy scan/report all passed.
- Trivy: **0 vulnerabilities** reported for the Alpine 3.24.4 base and each scanned Python package target. Report artifact [14439909868](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973/artifacts/14439909868) uploaded successfully. Synthetic outbox benchmark artifact [14440682369](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334598973/artifacts/14440682369) uploaded; it is synthetic-only, not production market-data performance evidence.
- The sole failed step is frontend `npm audit --audit-level=high`: **five High findings** for GHSA-fc5q-39xc-vjpf in `picomatch` through Vite/fdir and Vitest/tinyglobby. npm proposes `npm audit fix --force`, which would install `vitest@3.1.4` as a breaking change. No downgrade, override, suppression, lockfile manipulation, or threshold weakening was applied.
- Android APK [44334599093](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334599093): SUCCESS; debug APK assembled, checksum verified, and uploaded as artifact [14441570921](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44334599093/artifacts/14441570921). Preview release was skipped; no release was published.
- The preceding source batch's frontend dependency audit remains blocked by five High picomatch findings (GHSA-fc5q-39xc-vjpf). No patched release was found in the previous upstream recheck. Do not downgrade dependencies, add speculative overrides, suppress the advisory, alter the lockfile without an upstream fix, or weaken the audit threshold.
- No deployment, preview release, paid service, or Termux use.

### Gate and progress disposition
- Gate 36 remains OPEN: public WSS roundtrip, Android WebView transport/lifecycle, host effective configuration, owner-observed 330-second session/close attribution, and cross-instance fan-out still require external acceptance evidence.
- Gate 10 remains **0/10** formally closed; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. No progress tick is awarded for this source/test batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and criterion mapping are approved.
- ZERO COST maintained. `main` untouched.

## Latest work cycle — Batch 45 (WebSocket error-observer isolation)

**Implementation source SHA:** `b1311ae469c546a60a5db3d6f744709e5586ea30`  
**Parent source SHA:** `c7e198508bdfbf4e13b727b748427baaab135147`.

### Defect and correction
- The transport's terminal `fail(error)` path invoked the caller-provided `onError` callback before closing the socket and setting terminal state.
- If application-level error reporting itself threw, that exception escaped the transport handler and could interrupt socket cleanup. This is an observer failure, not a network/protocol failure, and must not strand transport resources.
- Error notification is now isolated in a guarded best-effort call. Cleanup continues even if the observer throws.
- Socket close is also guarded so a platform implementation throwing during teardown cannot prevent local terminal-state transition.
- Added regression coverage: a deliberately throwing consumer error observer is triggered by an unexpected protocol message; the test requires no uncaught throw, exactly one error callback, terminal `closed` state, and a 1011 close request.
- No protocol message, server behavior, heartbeat interval, replay cursor, sequence semantics, auth, entitlement, retry policy, or hosting setting changed.

### Exact-head CI snapshot
- Source SHA: `b1311ae469c546a60a5db3d6f744709e5586ea30`.
- Frontend Vitest exact result: **228 passed across 28 files**; backend pytest exact result: **1,032 passed in 38.68 seconds**.
- Automated Tests [44333017089](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44333017089): **FAILURE only at final step 27, Enforce frontend dependency audit result**. Frontend Vitest: **228 tests across 28 files passed**. Backend pytest: **1,032 passed in 38.68 seconds**. Frontend production build, source/bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark/report, backend dependency audit, backend container build, shared Redis guard + persistent-volume smoke, and Trivy scan/report all passed.
- Trivy report: **0 HIGH/CRITICAL vulnerabilities** across the Alpine 3.24.4 base and scanned Python packages. Container report artifact [14441345073](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44333017089/artifacts/14441345073) uploaded successfully. Synthetic outbox benchmark artifact [14440566343](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44333017089/artifacts/14440566343) uploaded; synthetic only, not production market-data performance evidence.
- The only failed step is frontend `npm audit --audit-level=high`: **five High findings** for GHSA-fc5q-39xc-vjpf in `picomatch` via Vite/fdir and Vitest/tinyglobby. The package is dev-only per the passing dependency-boundary test, but this does not satisfy audit enforcement. No downgrade, override, suppression, lockfile manipulation, or threshold weakening was applied.
- CodeQL [44333017068](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44333017068): SUCCESS for both Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44333017053](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44333017053): SUCCESS.
- Android APK [44333017051](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44333017051): SUCCESS; Android debug APK assembled, checksum verified, and short-lived artifact uploaded (artifact ID 14439198660). Preview release step was skipped; no release was published.
- **Final CI conclusion:** Automated Tests is **FAILURE only because the fail-closed frontend dependency audit remains unresolved**. Functional tests, builds, container/Redis smoke, Trivy, APK, CodeQL, and secret-history checks passed. Do not call CI all-green.
- No deployment, preview release, billing action, paid provider, or Termux use.

### Dependency blocker recheck
- npm registry still lists picomatch 4.0.7 as latest; GitHub Advisory and OSV still list versions through 4.0.7 as affected with no fixed version published. [npm versions](https://www.npmjs.com/package/picomatch?activeTab=versions) • [GitHub Advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) • [OSV](https://osv.dev/vulnerability/GHSA-fc5q-39xc-vjpf).
- No compatible upstream patch is available. Do not use `npm audit fix --force`, downgrade Vite/Vitest, invent an override, suppress the advisory, or lower the audit threshold. The dependency remains development-only per the existing dependency-boundary test, but that does not make CI audit green.

### Gate and progress disposition
- Gate 36 remains OPEN: public WSS transport, Android WebView lifecycle, host effective configuration, owner-observed session duration/close attribution, and cross-instance fan-out still require external acceptance evidence.
- Gate 10 remains **0/10** formally closed; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. No tick is awarded for this code/test/documentation batch.
- Stages 2–6 remain NOT SCORED; overall project percentage remains NOT ESTABLISHED until M1–M8 weights and mapping are approved.
- ZERO COST maintained. `main` untouched.

## Latest work cycle — Batch 44 (reset retry backoff after cursor-replay recovery)

**Implementation source SHA:** `a1af6824d3b7b83d6c4e9af7cb81d9cde1892dc2`  
**Parent source SHA:** `689e90af890c7fe54023189bd631bff64f3ac0c3`.

### Defect and correction
- The supervisor reset its exponential reconnect-attempt counter when a fresh snapshot arrived, but not when a reconnect recovered through the cursor-replay path.
- The transport emits the same `subscribed` state after a validated replay-complete message. Before this batch, that healthy recovery left the previous failure streak intact; a later unrelated outage could therefore wait at a larger backoff interval than intended.
- The supervisor now resets `attempt` whenever the transport reports `subscribed`. This covers both validated snapshot acceptance and validated replay completion; it does not reset on mere socket-open/authentication or an unvalidated message.
- Added a deterministic regression test: initial snapshot with cursor, transport interruption, zero-event replay completion, second interruption, and assertion that the next retry uses the minimum delay rather than the doubled delay. It also verifies a fresh ID token is requested for the third connection.
- No heartbeat cadence, cursor semantics, replay count/watermark checks, sequence guard, authentication, entitlement, or server behavior changed.

### Exact-head validation
- Exact-head source SHA: `a1af6824d3b7b83d6c4e9af7cb81d9cde1892dc2`.
- GitHub Actions Automated Tests run [44329450510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44329450510): **FAILURE only at final step 27, Enforce frontend dependency audit result**. Frontend Vitest: **227 tests across 28 files passed**. Backend pytest: **1,032 passed in 37.27 seconds**. Frontend production build, frontend source/bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark/report upload, backend dependency audit, backend container build, shared Redis guard + persistent-volume smoke, Trivy scan and report export/upload all passed.
- Trivy report: **0 vulnerabilities** in Alpine 3.24.4 and each scanned Python package target. Report artifact [14437399510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44329450510/artifacts/14437399510) uploaded successfully. The Redis smoke also verified persistent-volume owner `10001:10001`.
- The sole failure is frontend `npm audit --audit-level=high`: **five High findings** for GHSA-fc5q-39xc-vjpf through `picomatch`, pulled by Vite/fdir and Vitest/tinyglobby. This run's npm output proposes `npm audit fix --force` that would install `vite@6.2.7`, explicitly described as a breaking change. Do not apply it. No suppression, downgrade, speculative override, lockfile manipulation, or threshold weakening was made. The dedicated dependency-boundary test passed and confirms the affected package remains development-only; this does not make the audit green.
- Full Git History Secret Audit [44329450526](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44329450526): SUCCESS.
- Android APK [44329450397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44329450397): SUCCESS; verified artifact uploaded (artifact ID 14439470186, SHA-256 `09d51847dab2e239fda1a19846cf80c027be8742477fc76989f7da61660fe27b`). Immutable preview release step was skipped; no release was published.
- CodeQL [44329450525](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44329450525): SUCCESS for JavaScript/TypeScript and Python.
- **Final CI conclusion:** Automated Tests is **FAILURE only because the fail-closed frontend dependency audit remains unresolved**. All listed functional, build, backend, container, Redis, Trivy, APK, CodeQL, and secret-history checks passed. Do not call CI all-green.

### WebSocket / Gate 36 disposition
- This closes the identified client retry-backoff consistency defect at source level; exact-head CI completed with the frontend regression suite passing. Gate 36 still requires external acceptance evidence.
- Gate 36 remains OPEN. Still required: real public WSS Upgrade and ping/pong; Android WebView foreground/background acceptance; owner-observed platform close attribution around the documented function lifetime; effective host configuration read-back; and cross-instance fan-out. Repository tests cannot substitute for those external observations.
- No Vercel deployment, Cloudflare deployment/resource, production promotion, paid provider, billing action, or external credential operation was performed. No Termux required for this repository change or CI.
- No Stage 1 tick or Gate 10 closure is awarded for this source/test change.

### Progress accounting
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10 remains **0/10 formally closed**.
- Open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6 remain **NOT SCORED**.
- Overall project percentage remains **NOT ESTABLISHED** until M1–M8 weights and criterion mapping are approved; 20.9% is historical only.
- ZERO COST maintained. `main` untouched.

## Latest work cycle — Batch 43 (upstream dependency advisory recheck)

**Recheck date:** 18 November 2026 • **Source SHA under validation:** `09dd096580b30bce5789d12ab09f9ee41ac4234d`.

- npm registry still lists `picomatch@4.0.7` as `latest`; its version history shows no later published release. [npm package registry](https://www.npmjs.com/package/picomatch?activeTab=versions).
- The advisory record continues to affect versions through 4.0.7 and does not list a patched version. [GitHub Advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) • [OSV record](https://osv.dev/vulnerability/GHSA-fc5q-39xc-vjpf).
- A same-day independent maintainer issue reports the same state: no patched release and the dependency is development-only. [Independent same-day report](https://github.com/modelcontextprotocol/servers/issues/5594).
- Upstream discussion remains disputed; no authoritative patched release was identified. Do not interpret a disputed advisory as permission to suppress CI.
- **Decision:** no source or lockfile change. Keep Vite/Vitest versions stable, preserve npm audit fail-closed, and retain the existing dev-only exposure test. Recheck when a real upstream release outside the affected range is published.
- This is a blocker status update, not a Gate closure or progress tick.

## Previous work cycle — Batch 42 (exact-head CI closure and dependency blocker triage)

**Validated source SHA:** `09dd096580b30bce5789d12ab09f9ee41ac4234d`  
**Documentation base:** `497e1344d936241dd23b7404acaebb60954f2d24`.

- **Frontend tests:** 226 tests across 28 files passed.
- **Backend tests:** 1,032 passed.
- **Frontend production build:** passed (Vite 6.4.5).
- **Credential controls:** frontend source/bundle scan passed; 77 source files checked.
- **Backend runtime checks:** backend dependencies audit passed; backend container build passed; shared Redis guard + persistent-volume smoke passed; Trivy container scan and vulnerability report export/upload passed.
- **Synthetic outbox benchmark:** passed with 1,000 inserted/replayed synthetic bars and two concurrent replay readers; explicitly not market-data performance evidence.
- **Android debug APK:** build passed.
- **CodeQL:** passed.
- **Full reachable Git-history secret audit:** passed.
- **Only CI failure:** final frontend `npm audit --audit-level=high` enforcement. It reports five High findings from the same `picomatch` advisory GHSA-fc5q-39xc-vjpf through Vite/fdir and Vitest/tinyglobby. npm proposes `--force` would install Vitest 3.1.4 (breaking downgrade). That is not accepted as a safe remediation. The advisory-bearing package is still development-only (the dedicated dependency-boundary test passed), but this does not make the audit green. No suppression, downgrade, override, lockfile manipulation, or threshold weakening was applied.
- **Result:** functional/security/build checks listed above passed, but Automated Tests workflow conclusion is **FAILURE** by design because dependency enforcement remains fail-closed. Do not call CI all-green.
- **Run references:** Automated Tests [44327851319](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851319); APK [44327851485](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851485); CodeQL [44327851364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851364); secret audit [44327851417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851417).
- **Stage/Gate accounting unchanged:** Stage 1 75% provisional; Gate 10 0/10; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39; Stages 2–6 unscored; overall project percentage not established. CI passing is engineering evidence, not external gate acceptance.
- **No deployment or paid resources:** no Vercel/Cloudflare deployment/resource, billing, paid provider, or Termux action.

**Batch 42 conclusion:** Batch 41 WebSocket credential-state fix has passed all frontend/backend functional tests and the APK build; CI's remaining red status is isolated to the unresolved High-severity development dependency advisory. The next dependency action is to re-check upstream fixed-release availability and assess a compatible upgrade only when a real patched release exists. Do not weaken enforcement to obtain a green badge.

## Previous work cycle — Batch 41 (empty-token retry-loop prevention)

**Implementation base:** `53d166037f4d2f7f43be74da184dce57a9a4f85d`  
**Implementation commits:** `ec226b6a97d42d6bd0af19011f1043ed133775b7`, followed by regression-test correction `09dd096580b30bce5789d12ab09f9ee41ac4234d`.

- **Defect identified:** the supervisor treated an empty/whitespace Firebase ID token as a transient connection failure. It retried with exponential backoff even though the credential was still unusable, creating a pointless identity-provider retry loop.
- **Fix:** empty or whitespace ID tokens now stop the current supervisor, mark the matching market-data snapshot unavailable with a sign-in-specific reason, report one explicit error, and wait for a new authenticated session/supervisor. Transient token-provider rejections remain retryable.
- **Regression coverage:** added parameterized tests for empty and whitespace-only token values; removed the obsolete test that expected an empty token to be retried. Existing transient-token-failure retry test remains.
- **CI correction:** first exact-head run exposed the obsolete expectation (not a production-code failure); the test was corrected in a follow-up commit. The latest exact-head run is now testing the corrected state.
- **Latest SHA:** `09dd096580b30bce5789d12ab09f9ee41ac4234d`.
- **CI at documentation update:** frontend unit tests and frontend production build passed; frontend source/bundle credential scans passed; full reachable-history secret audit passed. Backend dependency installation and tests, container/Redis smoke, APK build, and CodeQL were still in progress. Do not call CI fully green until all exact-head runs complete.
- **Previous intermediate SHA:** `ec226b6a97d42d6bd0af19011f1043ed133775b7` failed because an older test still asserted that empty credentials should reconnect. That contradictory test was removed in the follow-up; no production behavior was rolled back.
- **No dependency files changed:** picomatch advisory remains unresolved; CI audit stays fail-closed.
- **Progress accounting unchanged:** Stage 1 75% provisional; Gate 10 0/10; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39; Stages 2–6 unscored; overall percentage not established.
- **Cost/operations:** no Vercel deploy, Cloudflare resource, paid service, billing action, or Termux operation.

**Batch 41 conclusion:** a credential-state retry loop has been eliminated without weakening retries for transient identity-provider failures. Final acceptance is contingent on corrected exact-head CI.

## Previous work cycle — Batch 40 (cross-gate source audit and dependency blocker reassessment)

**Audit base:** `2096356c4034dc2233f6c48a04a4d7579271ff52`  
**Scope:** Gates 8, 20, 25, 30–31, 34–36, 38–39 plus the frontend dependency-audit blocker.

- **Dependency blocker reassessment:** npm registry still lists `picomatch@4.0.7` as latest; GHSA-fc5q-39xc-vjpf covers versions through 4.0.7 and publishes no patched version. The upstream fix discussion is disputed and its proposed fix was not merged. The current lockfile resolves the package only through development tooling (Vite/fdir and Vitest/tinyglobby); the project has already added a test that asserts the advisory-bearing package is development-only. No safe patched release or compatible non-breaking resolution was identified. Do not downgrade Vitest, pin an affected older release, add a speculative override, suppress the audit, or weaken the fail-closed CI policy.
- **Gate 8 source review:** backend runtime secrets are loaded from backend environment/protected files; secret-bearing Settings fields are excluded from `repr()/str()`. Alert-device key loading requires an absolute regular file, canonical base64 encoding of exactly 32 bytes, and POSIX permissions denying group/other access. Tests cover malformed keys, wrong lengths, permissive file modes, missing key files, and secret redaction. Still missing: real owner-host secret injection, bundle/log/runtime leakage evidence from the actual deployed host, and independent operator acceptance.
- **Gate 20 source review:** Firebase Admin verification calls `verify_id_token(..., check_revoked=True)`, validates project issuer/audience, identity subject, and auth_time, and normalizes SDK failures without leaking provider details. Entitlements are durable, account-scoped, canonical-instrument-scoped, default-deny, and revocable. Tests cover claim rejection, revocation-check invocation, wrong project, malformed tokens, grant isolation, revoke/regrant, and persistence. Still missing: real signed-token E2E against the approved Firebase project for valid, expired, revoked, and wrong-project tokens, plus real account/session acceptance. Mock verifier tests do not close Gate 20.
- **Gate 25:** production configuration requires TLS Redis (`rediss://`) with ACL username/password; settings diagnostics redact the URL. CI Redis/persistent-volume smoke passed. Still missing: owner-controlled production ACL/TLS verification, restart/failure recovery, and host acceptance.
- **Gates 30–31:** source and synthetic tests cover encrypted backup/restore and integrity checks (see existing backup/restore work-cycle records). Still missing: owner-target restore, separately controlled off-host backup/key custody, retention, and an independent recovery drill.
- **Gates 34–35:** source configuration enforces production HTTPS CORS origins and TLS Redis. No real host mount/ownership/disk-pressure/restart-durability or deployed HTTPS/certificate/runtime-secret-source evidence is available.
- **Gate 36:** Batch 38/39 prove browser online/visibility lifecycle policy and React effect cleanup in jsdom. They do not prove Android WebView, deployed WSS, 330-second platform lifetime, Fluid Compute read-back, or cross-instance fan-out.
- **Gates 38–39:** process-local metrics and sanitized local alert events are implemented/documented, but no actual protected host collector, bounded retention/rotation, protected dashboard, named adult operator, verified no-cost escalation channel, or isolated live recovery/acknowledgement drill exists. The runbook correctly leaves both gates open.
- **Progress accounting:** unchanged. Stage 1 remains 75% provisional (300/400 ticks; 30/40 criteria); Gate 10 remains 0/10 formally closed; open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38, 39; Stages 2–6 are unscored; overall percentage remains not established. No test, source audit, or documentation change awards a tick or closes a gate.
- **Cost and operations:** no Vercel deployment, Cloudflare resource, billing action, paid service, or Termux operation. No branch other than `phase-2/market-data-foundation` was changed; `main` remains untouched.

**Batch 40 conclusion:** source controls are materially present for Gates 8 and 20, but their external acceptance evidence remains the critical blocker. The picomatch CI blocker has no upstream patched release at this audit; therefore the safe response is containment and monitoring, not an unsafe dependency mutation.

## Previous work cycle — Batch 39 (WebSocket lifecycle integration acceptance tests; exact-head CI completed)

- Parent exact branch HEAD: `09a81b455fb12b15515899d366bb9b2f1318fb54`; lifecycle integration source/test commit: `9c36ab295d3488500f97c20887d3e7e2ed305db3`; current exact-head CI target: `b389070bea42e84e4efba7c778a2026c51ef5545` (shared chart-layout fixture follow-up).
- Added a jsdom React integration test with mocked chart renderer and transport boundary. It verifies initial online/visible mount, offline stop, online recreation, background stop, foreground recreation, unmount cleanup, and initially offline/hidden mounts waiting until the matching event.
- Exact-head frontend tests: **225/225 passed across 28 files**. Exact-head backend tests: **1,032 passed in 52.01 seconds**. Frontend production build, source/bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy scan/report all completed successfully before final dependency enforcement.
- Exact-head Automated Tests [44324423988](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324423988): **FAILURE only at step 27**, final frontend dependency-audit enforcement. The audit reports five High findings rooted in `picomatch@4.0.7`; a dedicated backend test confirms the advisory-bearing package remains development-only. This is not permission to suppress the advisory: no patched upstream release is listed, and no downgrade, speculative override, package patch, waiver, or audit weakening was applied.
- Exact-head Android APK [44324423899](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324423899): **SUCCESS**. CodeQL [44324424075](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324424075): **SUCCESS**. Full Git History Secret Audit [44324424084](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44324424084): **SUCCESS**.
- The React/jsdom tests prove component effect ownership and event cleanup only. They do not prove Android WebView, deployed WSS, platform close attribution, Fluid Compute read-back, or cross-instance fan-out. Gate 36 remains OPEN pending external acceptance.
- No Vercel deploy, Cloudflare resource, billing action, paid service, or Termux operation. No Stage 1 ticks or Gate 10 closures are awarded for tests alone.

## Previous work cycle — Batch 38 (browser network and visibility lifecycle; exact-head CI completed)

- Parent exact branch HEAD: `0f9c5a1d291d2d601fd63a8bc2c36b95c9ae8d14`.
- Finding: `CandlestickChart` started the authenticated stream whenever a contract was selected and the chart was ready, without gating on browser online state or document visibility. Mobile background timer throttling could cause needless heartbeat/reconnect activity.
- Added `getOhlcvStreamLifecycle`: a live supervisor is permitted only when `navigator.onLine` is true and `document.visibilityState` is `visible`.
- Added `online`, `offline`, and `visibilitychange` listeners with cleanup. Offline/background transitions stop the previous supervisor, clear backend indicator eligibility and display a specific paused/unavailable reason. Returning online + visible creates a new supervisor and obtains a fresh token and snapshot.
- Added five deterministic lifecycle-policy tests. No polling timer or additional request is introduced while paused.
- Exact-head Automated Tests [44321645937](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645937): **FAILURE only at step 27, final frontend dependency-audit enforcement**. Frontend Vitest: **222/222 passed across 27 files**; backend pytest: **1,032 passed in 31.26s**. Frontend build, source/bundle secret scans, Android preflight/publisher tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy scan/report all passed.
- Exact-head Android debug APK [44321645986](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645986): **SUCCESS**; APK artifact checksum verified and uploaded. Immutable preview release step was skipped; no release was published.
- Exact-head CodeQL [44321646301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321646301): **SUCCESS** for JavaScript/TypeScript and Python. Full Git History Secret Audit [44321645942](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44321645942): **SUCCESS**.
- The sole failing enforcement is five High npm audit findings for `picomatch@4.0.7` through Vite/fdir and Vitest/tinyglobby. npm proposes `vitest@3.1.4` via `npm audit fix --force`, explicitly marked as a breaking change. No downgrade, override, suppression, waiver, or audit weakening was applied.
- Uploaded artifacts: `14436035035` (synthetic outbox benchmark) and `14434973310` (container vulnerability report). Trivy reported 0 vulnerabilities for Alpine 3.24.4 and each listed Python package. The first database mirror returned a missing-blob error; fallback GHCR retrieval completed successfully.
- Batch 37 exact-head CI [44319494393](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494393) failed only at final frontend npm audit enforcement; Android APK [44319494274](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494274), CodeQL [44319494237](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494237), and full-history secret audit [44319494266](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44319494266) succeeded.
- The container scan found zero vulnerabilities in the scanned Alpine OS and Python package targets; Trivy's mirror fallback succeeded and its report artifact was uploaded.
- Gate 36 remains OPEN pending deployed WSS, Android WebView, foreground platform-lifetime observation, Fluid Compute read-back, and cross-instance fan-out.
- No deployment, paid service, billing change, Cloudflare resource, or Termux operation. No Stage 1 ticks or Gate 10 closures are awarded.

## Previous work cycle — Batch 37 (terminal WebSocket policy-close handling; exact-head CI completed)

- Parent exact branch HEAD: `de59c0ede125d31d2cd2cfa95c47082e44385214`.
- Source audit found a deterministic retry-loop risk: backend explicitly closes with WebSocket code `1008` for unsupported client control frames and ping-rate-limit violations, while the supervisor treated every close except `4400/4401/4403` as transient and retried with unchanged client behavior.
- Corrected the supervisor so `1008` is terminal for the current stream instance. It marks the market-data snapshot unavailable, reports a protocol-policy error, and does not reconnect until the owning session/selection recreates the supervisor after a corrected policy/configuration.
- Added a regression test that triggers server close `1008`, advances all pending timers, and proves the socket factory was called exactly once.
- Updated `docs/OHLCV_WEBSOCKET_CLIENT.md` and `docs/OHLCV_STREAM_PROTOCOL.md` to document this close-code contract.
- No heartbeat cadence, pong deadline, authentication, entitlement, replay, cursor, or data-validation behavior changed.
- CI audit blocker: exact package graph is `vite@6.4.5 → fdir@6.5.0 → picomatch@4.0.7` and `vitest@4.1.12 → tinyglobby@0.2.17 → picomatch@4.0.7`. The workflow reports five High findings. npm's automatic fix proposes downgrading Vitest to `3.1.4` (a breaking change); no safe maintainer-reviewed patched dependency is present in the current lockfile. Keep the audit fail-closed; do not force the downgrade or add speculative overrides.
- Exact-parent CI for documentation SHA `de59c0ede125d31d2cd2cfa95c47082e44385214`: frontend tests/build, backend tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy scan/report passed; final frontend dependency enforcement failed. CodeQL and full-history secret audit passed. This is parent evidence only; Batch 37 requires its own exact-head CI.
- Gate 36 remains OPEN pending public WSS, Android WebView, 330-second platform lifecycle attribution, effective Fluid Compute read-back, and cross-instance fan-out.
- No Vercel deployment, Cloudflare resource, paid service, billing change, or publication action. Termux is not required.
- Progress accounting unchanged: Stage 1 **75% provisional (300/400 ticks; 30/40 criteria)**; Gate 10 **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**; Stages 2–6 **NOT SCORED**; overall project percentage **NOT ESTABLISHED**. No ticks or gate closures are awarded by this source-only change.

## Latest work cycle — Batch 36 (strict WebSocket heartbeat; exact-head CI completed)

- Current exact branch HEAD: `11d3ea4ba426b1da021bf0f9c79abdc0205b3c9d`; parent: `9c76726f031568fe126479f4aa3c34bf0d151e49`.
- Client correction: accept a heartbeat pong only while subscribed, only while a pong deadline is outstanding, and only with protocol `version: 1`. Unsolicited or unsupported-version pong frames fail closed. Two frontend regression tests were added.
- Exact-head Automated Tests [44317099110](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099110): **FAILURE only at step 27, final frontend dependency-audit enforcement**. Steps 1–26 passed, including frontend tests/build, backend tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke test, Trivy image scan and report export.
- Exact-head Android debug APK build [44317099094](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099094): **SUCCESS**. Exact-head CodeQL [44317099846](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099846): **SUCCESS**. Full Git History Secret Audit [44317099074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099074): **SUCCESS**.
- The final dependency enforcement remains blocked by the dev-only `picomatch@4.0.7` advisory path. Keep enforcement fail-closed; do not force a Vite downgrade, add a speculative override, patch package contents, suppress the finding, or waive the gate.
- Heartbeat calculation unchanged: client `1/20 = 0.05` ping/s; server ceiling `20/10 = 2` ping/s; utilization **2.5%**; pong deadline 10 seconds.
- Gate 36 remains OPEN: deployed public WSS, Android WebView runtime, owner-observed 330-second session/platform close attribution, effective Fluid Compute read-back, and cross-instance fan-out remain unverified.
- No Vercel deployment/retry, Cloudflare resource, paid service, billing change, or publication action. Termux is not required.
- Progress unchanged: Stage 1 **75% provisional (300/400 ticks; 30/40 criteria)**; Gate 10 **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**; Stages 2–6 **NOT SCORED**; overall project percentage **NOT ESTABLISHED**. No ticks or closures awarded from CI alone.

## Cross-gate source audit — Batch 36 (evidence boundaries; no gate closures)

- **Gate 25 — Redis shared guard:** source enforces production `rediss://` with non-empty ACL username/password, CA-chain and hostname verification, startup `PING`, atomic Lua HTTP counters and WebSocket leases, and fail-closed Redis error propagation. Exact-head CI passed backend tests and the Redis/persistent-volume smoke stage. Still missing: owner-controlled Redis ACL permission review, actual production TLS endpoint validation, restart/failure recovery evidence, and independent host acceptance.
- **Gates 30–31 — backup/restore:** source implements SQLite Online Backup API snapshots, integrity checks, atomic publication, no-overwrite restore, foreign-key checks, application-domain inventory/hash comparison, post-restore write/read/cleanup probe, and AES-256-GCM authenticated backup encryption with PBKDF2-HMAC-SHA256 (600,000 iterations). Tests exercise synthetic application data and cryptographic tamper/wrong-key paths. Still missing: restore on the intended owner host, separately controlled off-host copy, independent key custody, retention controls, and a real recovery drill.
- **Gate 8 — runtime secrets:** frontend source and production bundle credential scans passed exact-head CI; this does not prove that production secrets are injected from a protected host secret source or absent from runtime diagnostics.
- **Gate 20 — identity:** Firebase Admin verification checks revocation and validates issuer/audience/subject claims; subscription authorization checks canonical instrument mapping and entitlement. A real Firebase project signed-token acceptance test (valid, expired, revoked, wrong-project) remains outstanding.
- **Gates 34–35 — host durability and transport:** container/persistent-volume smoke passed in CI, but this does not prove the intended host's mount identity, ownership, disk-pressure behavior, restart durability, HTTPS certificate chain, or runtime secret-source configuration.
- **Gates 38–39 — operations:** process-local metrics and sanitized local alert reporting are documented and tested at source level. External log collection, retention/rotation, protected dashboard, no-cost alert receipt, named adult operator, and recovery exercise remain unaccepted.
- These are source-readiness findings only. They do not change Stage 1 ticks, Gate 10 formal closures, or the overall project percentage.

## Previous work cycle — Batch 35 (verified on its recorded parent)

- Parent exact-head Automated Tests [44310352740](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310352740): **FAILURE only at final frontend dependency-audit enforcement**. All functional, build, container, Redis/persistent-volume smoke, and Trivy/report steps before enforcement succeeded.
- Parent exact-head Android debug APK build [44310351406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351406): **SUCCESS**. The APK was built and verified as a CI artifact; no preview release was published.
- Parent exact-head CodeQL [44310351525](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351525): **SUCCESS**. Full Git History Secret Audit [44310351555](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351555): **SUCCESS**.
- Batch 35 adds backend route-level tests for the actual authenticated text-frame `ping` → JSON `market_data.pong` exchange and for fail-closed rejection of unsupported control frames. Candidate's own CI is pending until exact SHA runs finish.
- Heartbeat rate calculation: client 1 ping/20 s = 0.05/s; server ceiling 20/10 s = 2/s; client steady-state rate = **2.5%** of ceiling. Pong timeout = 10 s.
- Gate 36 remains OPEN: deployed public WSS, Android WebView, owner-observed 330-second session/platform close attribution, effective Fluid Compute read-back, and cross-instance fan-out remain unverified.
- Dependency blocker remains five High paths via dev-only `picomatch@4.0.7`. Keep enforcement fail-closed; no downgrade, speculative override, hand patch, suppression, or waiver.
- No Vercel deployment/retry, Cloudflare resource, paid service, database/host/storage provisioning, billing change, or publication action. Termux is not required for this batch.
- Progress remains conservative: Stage 1 **75% provisional (300/400 ticks; 30/40 criteria)**; Gate 10 **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**; Stages 2–6 **NOT SCORED**; overall project percentage **NOT ESTABLISHED**. Historical overall checkpoint **20.9%** is not recomputed. No ticks or gate closures are awarded by tests alone.

## Batch 34 verified CI outcome

- Automated Tests [44310352740](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310352740): final frontend dependency-audit enforcement failed; all preceding functional/build/container/security scan steps succeeded.
- Android debug APK Build [44310351406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351406): SUCCESS.
- CodeQL [44310351525](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351525): SUCCESS.
- Full Git History Secret Audit [44310351555](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44310351555): SUCCESS.

## Batch 34 source correction

See [Batch 34 WebSocket heartbeat correction](WORK_CYCLE_2026-11-18_BATCH34_WEBSOCKET_HEARTBEAT.md). Client heartbeat uses the literal text `ping` every 20 seconds and expects `market_data.pong` within 10 seconds. The client tests cover send, acknowledgement, timeout, and cleanup.

## Batch 33 verified audit

See the Batch 33 historical audit notes below. Gate 30/31 backup/restore and Gate 36 authenticated WebSocket source reviews remain repository-level evidence only; owner-host acceptance is still required.

## Previous verified update — Batch 32

- **Audited branch HEAD:** `b9f81a9ca25a6ebdf390c40671a4429241c4c5d2` on `phase-2/market-data-foundation`. Source baseline remains `e6db77210dd28bd82196b2b7bf7d8d7e7256fc37`; Batch 31 changed only progress documentation. This Batch 32 bundle also changes documentation and the colored SVG only.
- Exact-HEAD Automated Tests [44306971092](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306971092): **FAILURE only at step 27, final frontend dependency-audit enforcement**. Frontend Vitest **212/212 PASS across 26 files**; backend pytest **1,030 PASS in 33.74s**; frontend build (1,526 modules), source/bundle credential scans, Android preflight and immutable publisher tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy scan/report export all PASS.
- Exact-HEAD CodeQL [44306971049](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306971049): **SUCCESS**, JavaScript/TypeScript and Python. Full Git History Secret Audit [44306971204](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306971204): **SUCCESS**.
- The final dependency audit still reports five High paths through `picomatch@4.0.7` under Vite/Vitest development tooling. npm proposes a forced Vite downgrade to 6.2.7, which is breaking. Official npm registry still lists 4.0.7 as latest; GitHub/OSV advisory still affects versions through 4.0.7 and states no patched version. Upstream PR #194 is OPEN and addresses a different extglob parsing behavior; it is not a published security fix. No override, unreviewed patch, downgrade, suppression, or waiver is accepted.
- **Gate 38 source audit:** request metrics are process-local, bounded to 127 route/method series including overflow, protected by an optional operator bearer token, and served with private/no-store headers. Unit tests cover cardinality, normalization, detached snapshots, invalid durations and concurrent recording. The remaining criterion is operational: host collection, bounded retention/rotation, disk-pressure proof, protected dashboard access, and a redacted incident trace. Process-local metrics reset on restart and do not aggregate across instances.
- **Gate 39 source audit:** the opt-in worker emits sanitized local JSON transitions for degraded delivery, worker errors and recovery; tests cover deduplication, counter validation, recovery and redaction. The worker is disabled by default. This is local logging, not a guaranteed operator notification. Actual host log collection, accountable adult operator/escalation, no-cost alert receipt and isolated recovery exercise remain unproven.
- **Gate 36:** the source and CI WebSocket regression suites pass, but the POC remains synthetic. No new Vercel deployment was created; no exact-head WSS Upgrade/ping-pong, Android WebView, 330-second owner-observed run, platform close attribution, effective Fluid Compute read-back, or cross-instance fan-out evidence exists.
- **Gate 30/31:** repository restore/encryption tests remain useful evidence but do not replace owner-target restore, off-host artifact, separately controlled recovery key, retention/access policy, and external recovery.
- Exact-head Vercel lookup on `b9f81a9ca25a6ebdf390c40671a4429241c4c5d2` returned zero deployments for both frontend and WSS projects. Root `vercel.json` keeps branch deployments disabled and `main` enabled. No deployment/retry, paid service, billing change, or Cloudflare resource.
- **Termux:** not required for this remote repository/CI audit. Any later device-specific requirement will be explained before requesting action. No Stage 1 ticks or Gate 10 closures are awarded from this documentation/source audit.

## Previous verified update — Batch 31

- **Audited exact HEAD:** `0c12dc54bce9fb5694b57e13928d995ff258ecef` on `phase-2/market-data-foundation`. This commit is documentation-only relative to source baseline `e6db77210dd28bd82196b2b7bf7d8d7e7256fc37`; no application source changed.
- Exact-HEAD Automated Tests run [44306105968](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306105968): **FAILURE only at the final frontend dependency-audit enforcement**. Frontend Vitest **212/212 PASS** (26 files); backend pytest **1,030 PASS in 26.29s**; frontend production build, source/bundle credential scans, Android preflight and immutable publisher tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke, Trivy image scan and vulnerability-report export all PASS.
- Exact-HEAD CodeQL run [44306106124](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306106124): **SUCCESS** for JavaScript/TypeScript and Python. Full Git History Secret Audit [44306106134](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306106134): **SUCCESS**.
- The only failing enforcement remains **five High findings** through development-only `picomatch` / `GHSA-fc5q-39xc-vjpf`. The exact run's npm output says `npm audit fix --force` would install `vitest@3.1.4`, a breaking change. No force downgrade, dependency override, suppression, or waiver was applied. Keep audit enforcement fail-closed.
- **WebSocket source evidence:** frontend client/protocol/supervisor suites passed in the 212 tests; backend stream, authenticated API WebSocket, synthetic POC protocol and bounded-probe contracts are included in the 1,030 passing backend tests. This does not prove deployed public WSS Upgrade/ping-pong, Android WebView, 330-second foreground observation, platform close attribution, effective Fluid Compute read-back, or fan-out.
- Existing WSS preview remains preview-only and synthetic. Its prior protected `/health` HTTP 200 response explicitly reported `production_data_connected=false`; HTTP health is not a WebSocket transport acceptance.
- **Gate 30 source audit:** `backend/app/sqlite_restore_drill.py` now commits the drill-owned probe record, reads it from a fresh read-only connection, commits cleanup, and verifies absence through another connection. The latest 1,030-test backend run passed. This is repository/CI evidence only; no owner-target application database restore has been run.
- **Gate 31 source boundary:** `backend/app/sqlite_backup.py` provides consistent local SQLite snapshot/restore, integrity and foreign-key checks, owner-only POSIX permissions, atomic publication and fsync handling. Its own module contract explicitly does not encrypt or upload snapshots. Existing CI encrypted-snapshot integration evidence does not create an off-host artifact, separately controlled recovery key, retention/access policy, or owner-target recovery. Gate 31 stays OPEN.
- Exact-SHA Vercel deployment lookups for audited HEAD `0c12dc54bce9...` returned zero deployment records for both projects. Root `vercel.json` keeps `main=true` and `phase-2/market-data-foundation=false`. No deployment, retry, production promotion, billing change, paid service, or SSO change.
- **No Termux required for this remote GitHub/source/CI audit.** Actual owner-device restore and Android-native WSS acceptance are separate target-device activities; no installation or command is being requested in this batch.
- No Stage 1 ticks or Gate 10 closures are awarded from CI/source evidence where owner-target acceptance is still missing. ZERO COST maintained; `main` untouched.

## Six-stage progress

| Stage | Scope | Status | Progress |
|---:|---|---|---:|
| 1 | Foundation, Security & Data Integrity | Active; provisional | **75% — 300/400 ticks; 30/40 criteria** |
| 2 | Market Data Infrastructure | Not opened; not scored | — |
| 3 | Core Chart Engine | Not opened; not scored | — |
| 4 | Indicators & Analytics | Not opened; not scored | — |
| 5 | Advanced Tools | Not opened; not scored | — |
| 6 | Release & Operations | Not opened; not scored | — |

**Gate 10: 0/10 formally closed.** Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No overall-project percentage is asserted.

## Gate 10 — evidence and remaining blockers

| Gate | Current repository evidence | Remaining external acceptance |
|---:|---|---|
| 8 | Frontend source/bundle credential scans and full Git history secret audit pass | Owner-controlled zero-billing runtime secret injection; prove absence from logs, build outputs and runtime artifacts |
| 20 | Firebase token/revocation/entitlement and WebSocket authorization code/tests | Verified no-billing Firebase setup; real sign-in, expiry/revocation, entitlement denial, browser + Android reconnect; otherwise production identity stays disabled |
| 25 | CI Redis ACL/TLS + persistent-volume smoke test passes in test environment | Existing owner-controlled Redis host, validated TLS, least-privilege ACL, private bind, persistence/restart/failure proof |
| 30 | CI encrypted snapshot/decrypt/full-restore integration test | Owner-target restore to fresh DB; unchanged source; integrity, FK, domain records and post-restore write/read/cleanup |
| 31 | Encrypted snapshot/recovery code and tests | Off-host artifact, separately controlled recovery key, retention/access policy and successful restore; zero-cost only |
| 34 | CI persistent-volume smoke test passes | Existing-host mount identity, restrictive permissions, disk-pressure and restart durability/recovery evidence |
| 35 | Backend container build and health-related tests pass | Existing-host HTTPS/certificate chain, fail-closed startup and redacted runtime-secret source evidence |
| 36 | Synthetic WSS POC and ASGI lifecycle/protocol tests; binary-frame rejection regression PASS in CI run `44295544184`; earlier READY previews are on `bd6356d`, not current code HEAD | Public WSS upgrade, foreground 330s observation, platform close attribution, effective Fluid setting read-back, native Android WebView WSS, cross-instance fan-out and owner cost acceptance |
| 38 | Concurrent metrics regression and input-hardening tests | Durable aggregation, bounded retention, host access controls, self-hosted dashboard and owner acceptance |
| 39 | Sanitized local alert/recovery tests and zero-cost runbook | Persistent alert evidence, named escalation owner and completed recovery drill |

## Historical CI checkpoint (prior commit) — run 44278716234

<badge color="danger">Overall workflow: FAILURE</badge> The single failing step is the final **Enforce frontend dependency audit result**. This is an intentional security gate, not a test/build crash.

- Backend pytest: **1,014 passed in 30.07s**.
- Frontend unit tests and production build: PASS.
- Frontend source and built-bundle credential scans: PASS.
- Android host preflight and immutable preview publisher tests: PASS.
- Synthetic SQLite outbox benchmark and artifact upload: PASS.
- Backend dependency audit: PASS.
- Backend container build: PASS.
- Redis/persistent-volume smoke test: PASS.
- Trivy image scan/report steps: PASS.
- CodeQL [44278716261](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716261): PASS.
- Full Git History Secret Audit [44278716240](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716240): PASS.

### Active npm audit blocker

Job log confirms **five High findings** through development-only `picomatch@4.0.7`, advisory **GHSA-fc5q-39xc-vjpf**. The new dependency-exposure regression passes, proving affected glob tooling remains dev-only and absent from direct runtime dependencies. This is exposure reduction, **not remediation**. Keep final enforcement active. Do not force upgrades/downgrades, suppress, waive, or mislabel the finding as fixed.

## Historical Vercel read-back (older commit)

Both protected previews are **READY** for source `4256c5e3ccab82255d115beaf961afd4794a3a42`:
- WSS POC [preview](https://dezzta-chart-ws-4eo7d8j18-deszztagd377-pixel.vercel.app) — `dpl_AtEV8yH6S5MwGApGaHQ8HagJTJsK`.
- Frontend [preview](https://dezzta-chart-bevptgcvw-deszztagd377-pixel.vercel.app) — `dpl_2Jc2So3HmvEQ6yeESjrXbMLorivz`.

Preview READY is not production acceptance. No production promotion.

## WebSocket status — strict interpretation

Implemented and CI-tested: correct CONNECTING/OPEN/close lifecycle, actual close event as the disconnected authority, opt-in synthetic heartbeat every 10 seconds, 25-second idle timeout, bounded 330-second browser probe, monotonic elapsed measurement, close details, and hidden-page invalidation.

Not yet evidenced: owner-observed foreground 330-second run, Vercel-originated maximum-duration close, effective Fluid Compute runtime read-back, native Android WebView WSS, cross-instance production fan-out, zero-cost operational acceptance. A client-side close at 330 seconds is not proof of platform termination. POC is synthetic-only; no production market data, credentials, identity, Redis or production worker.

## Roadmap beyond Stage 1

- Stage 2: market-data infrastructure, provider adapters, entitlement-aware ingestion, replay and durable sequencing.
- Stage 3: chart engine, timeframes, history, viewport, pan/zoom and rendering correctness.
- Stage 4: indicators and analytics; Footprint/Heatmap visuals must wait for the owner's reference images.
- Stage 5: advanced chart tools, alerts, layouts and drawing workflows.
- Stage 6: release hardening, Android packaging, performance, reliability, security and operations.

Stages 2–6 remain NOT SCORED.

## Zero-cost and owner-device controls

No paid hosting, managed Redis, market-data subscription, monitoring, storage, billing activation, paid plan upgrade, production promotion or SSO weakening. No Google Play publication unless explicitly approved. **No Termux required** for this CI/documentation cycle. If a gate requires paid infrastructure, it stays constrained/deferred. No code/document repair is delegated to the owner.

## Next engineering order

1. Keep npm audit enforcement active; accept only a reviewed, reproducible remediation.
2. Perform the owner-controlled foreground WSS observation against the exact READY protected preview; record the actual event evidence before closing any sub-check.
3. Continue existing-host Redis, restore, secrets, volume, metrics and alert acceptance only where already available at zero incremental cost.
4. Award no Stage 1 ticks until each external criterion has its required evidence and acceptance.

**Current accounting:** Stage 1 **75% provisional**; Gate 10 **0/10 closed**; Stages 2–6 **not scored**.


## Batch 15 — upstream dependency remediation review — 18 Nov 2026

The five High npm audit findings are still enforced. A fresh upstream review was performed before considering any patch:

- GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) remains published and identifies CVE-2026-112366. Its current page marks the record **Unreviewed** and does not list a patched version. OSV still carries the advisory record.
- Upstream issue [#247](https://github.com/micromatch/picomatch/issues/247) remains OPEN. Discussion indicates the Snyk-specific advisory was revoked, but that does not remove the GitHub advisory or the current npm audit finding.
- Upstream PR [#238](https://github.com/micromatch/picomatch/pull/238) remains OPEN. Review measurements reproduce exponential behavior for `+(*)`, `*(*)`, and `+(a*)`; a separate review also reports `+(*)` still timing out. It does not fully resolve the published advisory.
- Upstream PR [#237](https://github.com/micromatch/picomatch/pull/237) remains OPEN. Review discussion identifies uncovered multi-branch patterns (including `+(*a|*b)`) and semantic edge cases involving quoted stars and bracket classes. A single approval is not a maintainer release or comprehensive security validation.
- Upstream PR [#246](https://github.com/micromatch/picomatch/pull/246) targets the v2 branch and is not a release for this project's picomatch 4.x dependency path. Its own description scopes the fix and validation to selected patterns, not all ReDoS cases.
- Upstream PR [#235](https://github.com/micromatch/picomatch/pull/235) is CLOSED; maintainer comments dispute the vulnerability's practical exposure and recommend not allowing untrusted users to define glob/regex patterns. That disagreement does not change the active GitHub advisory or justify silently waiving npm audit.

**Decision:** do not vendor or override any of these unmerged patches. Do not claim the advisory is revoked globally. Keep the exact npm audit enforcement active and keep the vulnerable packages development-only. Reassess after a maintainer-reviewed release and independent regression validation against all relevant cases.

This upstream research does not alter Stage 1 scoring or Gate 10 closure.


## Batch 16 — exact-head CI + protected WSS HTTP read-back — 18 Nov 2026

**Branch head audited:** `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.

### Exact-head automated evidence

- Automated Tests [44280286764](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286764): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed in 31.94s**. Alert recovery, concurrent observability metrics, dependency-exposure, WebSocket protocol, bounded-probe contract and all other backend tests passed.
- Frontend unit tests/build, source and built-bundle credential scans, Android preflight/publisher tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke test, and Trivy scan/report steps passed.
- CodeQL [44280286768](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286768): **SUCCESS**.
- Full Git History Secret Audit [44280286699](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286699): **SUCCESS**.
- The only failing enforcement is still five High npm audit findings through dev-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. Do not suppress, waive, force-downgrade or call this fixed.

### WebSocket POC — protected preview read-back

- Last READY WSS preview: `dpl_C9bGENGcUpmgTFaxyyPNjg1Ehapv`, source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`.
- Protected `/health` request returned **HTTP 200** with `status=ok`, `service=dezzta-ws-poc`, `mode=synthetic-only`, `production_data_connected=false`.
- Protected root page returned **HTTP 200** and contains the 330-second probe control and 10-second heartbeat configuration.
- This proves HTTP health and page delivery only. No actual WebSocket upgrade/round-trip, owner-visible foreground 330-second observation, platform-originated 300-second close, effective Fluid Compute read-back, native Android WebView WSS or cross-instance fan-out is claimed. Gate 36 remains OPEN.

### Vercel build-rate restriction

- Exact-head Vercel commit status for `a5e90f75329c937a4ef11d560bab3b434e7f24e8`: both WSS and frontend contexts **FAILURE** with the platform `build-rate-limit` link.
- Filtered deployment lookup for exact SHA returned **zero deployment records** for both projects. Do not label this commit READY.
- Previous known READY previews remain on `72a959f375f7c1e999be25e73e5fd00fdc24abb0`. Existing READY previews were not changed; no redeploy retry loop, paid upgrade, billing activation or SSO weakening was performed.
- Team usage counters and exact reset time were not exposed by the available read-back; no quota remainder or reset estimate is invented.

### Stage 1 accounting — unchanged

- Stage 1: **300/400 ticks = 75% provisional; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- No score awarded for a passing test suite, documentation, or HTTP-only WSS checks without the external acceptance evidence.


## Batch 17 — branch-head and provider-blocker reconciliation — 18 Nov 2026

**Audited branch head:** `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a` (commit message: `docs: consolidate Batch 16 CI and WebSocket evidence`).
**Parent:** `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.
**Audit method:** GitHub branch ref, exact commit status/check-runs, workflow job logs, and Vercel deployment records filtered by exact SHA.
**Cost:** ZERO COST. No Termux, no paid plan, no billing change, no production promotion, no SSO weakening.

### Exact branch-head evidence

- GitHub Actions run [44281595750](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595750) — Test and Build: **FAILURE at final frontend dependency-audit enforcement**.
- The job reached and completed all earlier test/build/security/container steps. The final step reports `AUDIT_OUTCOME=failure` and exits 1 by design.
- CodeQL run [44281595873](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595873): both Python and JavaScript/TypeScript analysis jobs **SUCCESS**.
- Full reachable Git history scan run [44281595869](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595869): **SUCCESS**.
- The exact-head GitHub status has two Vercel contexts, both FAILURE with the provider message: **“Deployment rate limited — retry in 24 hours.”**
- Exact-SHA deployment queries returned **zero deployment records** for both WSS POC and frontend projects. Therefore `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a` is **not deployed**.

### Vercel blocker — isolated and contained

This is a provider-side deployment/build-rate restriction, not an application compile error. No retry loop was started. No paid upgrade, billing activation, or SSO bypass was attempted. The latest previously observed READY previews are tied to source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`, not the audited branch head. Those preview records do not certify the branch head.

No exact usage counter or reset timestamp was available. The provider status string says retry in 24 hours; no more precise remaining-time estimate is asserted.

### Dependency audit blocker — enforcement retained

The workflow's final enforcement is the sole Test and Build failure. The audit outcome is still failure for the five High findings through development-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. The development-only boundary regression is mitigation, not a fix. No unmerged patch, forced downgrade, override, suppression, waiver, or production-only audit substitution was applied.

### WebSocket acceptance — honest boundary

The latest previously recorded protected preview returned HTTP 200 for health and page delivery in synthetic-only mode. This is HTTP verification only. It is not a WebSocket upgrade, echo/round-trip, 330-second foreground observation, platform-originated duration close, Android WebView test, effective Fluid Compute read-back, or cross-instance fan-out proof. Gate 36 remains OPEN.

### Gate 10 action register

| Criterion | Immediate zero-cost work possible | Evidence still required |
|---:|---|---|
| 8 | Keep source/bundle/history scans and secret boundary tests enforced | Owner-controlled secret injection and runtime/log/artifact leakage proof |
| 20 | Preserve authorization/revocation regression tests | Real identity/revocation/entitlement acceptance on approved zero-cost setup |
| 25 | Keep Redis ACL/TLS and persistence CI tests | Owner-controlled existing Redis endpoint and real restart/failure proof |
| 30 | Keep encrypted snapshot/decrypt/restore integration tests | Restore drill against a fresh owner target and post-restore integrity/write checks |
| 31 | Keep encrypted backup/recovery controls | Off-host copy, separately controlled key, retention policy and restore drill |
| 34 | Keep persistent-volume smoke test | Existing-host mount, permissions, disk-pressure and restart durability proof |
| 35 | Keep container/health/fail-closed checks | Existing-host HTTPS/certificate and runtime secret-source evidence |
| 36 | Keep synthetic lifecycle/probe contract tests; no false duration claims | Foreground 330s run, platform close attribution, Fluid setting, Android WebView, fan-out |
| 38 | Keep concurrency/input-hardening tests | Durable aggregation, retention, host access controls and dashboard acceptance |
| 39 | Keep sanitized alert/recovery tests and runbook | Persistent alert, named escalation owner and completed recovery drill |

**Scoring unchanged:** Stage 1 **300/400 ticks = 75% provisional; 30/40 criteria**. Gate 10 **0/10 closed**. Open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 **NOT SCORED**. No progress credit for documentation-only work or provider-blocked deployments.


## Batch 18 — exact-head CI, WSS HTTP verification, and overall-progress accounting — 18 Nov 2026

**Audited source head:** `64f348cebccbfb3fad2b9efe5a066d28962970f6` (Batch 17 documentation reconciliation). **Branch:** `phase-2/market-data-foundation`. **Main:** untouched. **Cost:** zero. No Termux, no billing, no paid services, no production promotion.

### Exact-head CI outcome

- Automated Tests run [44287587066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587066): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed**. Frontend unit tests/build, source and built-bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke test and Trivy scan/report all **PASS**.
- The final enforcement step fails because npm audit outcome is failure: **five High findings through development-only `picomatch@4.0.7`**. The failure is intentional and no vulnerability was suppressed.
- CodeQL run [44287587070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587070): Python and JavaScript/TypeScript jobs **SUCCESS**.
- Full history scan run [44287587073](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587073) was requested in the prior read-back but its run ID was not valid; therefore this batch does **not** claim a new history-audit result. Earlier passing history scans remain historical evidence only.

### Vercel exact-head deployment

Both projects have READY deployments for this exact source SHA:
- WSS POC deployment `dpl_8iPQZm1Z2QJ4Dc8hjUPgSsPanPYb`, URL [protected preview](https://dezzta-chart-ws-arfnel7l9-deszztagd377-pixel.vercel.app).
- Frontend deployment `dpl_FqhfGebn7fU6f7udkPFmByyG1WTY`, URL [protected preview](https://dezzta-chart-ekpqshhr4-deszztagd377-pixel.vercel.app).

The previously observed build-rate-limit blocker is therefore no longer active for this commit. No paid upgrade, billing activation, SSO weakening, or production promotion occurred.

### WebSocket POC — verified scope

Protected WSS preview `/health` returned **HTTP 200** with `status=ok`, `service=dezzta-ws-poc`, `mode=synthetic-only`, and `production_data_connected=false`. The protected root page returned **HTTP 200** and serves the browser WebSocket client, including its explicit Connect, Disconnect, synthetic ping, and bounded 330-second probe controls.

This is HTTP health and page-delivery evidence only. The available HTTP fetch interface cannot perform or observe a real WebSocket protocol upgrade, so this batch does not claim a WSS handshake, ping/pong round-trip, foreground 330-second run, Vercel-originated duration close, Android WebView result, effective Fluid Compute read-back, or cross-instance fan-out. Gate 36 remains OPEN.

### Overall-project progress — corrected accounting

The approved progress specification explicitly says the M1–M8 weighted ledger is **not approved and not scored criterion-by-criterion**. Therefore a fresh overall-project percentage cannot be calculated without inventing weights or credit. The most recent owner-confirmed historical overall checkpoint is **20.9%**, and it must be labeled **HISTORICAL — NOT RECOMPUTED**. Do not present 20.9% as a current verified percentage.

The six official stages remain:
- Stage 1: **75% provisional** (300/400 ticks; 30/40 criteria); Gate 10 **0/10 formally closed**.
- Stages 2–6: **NOT SCORED**. Preparatory code does not count as officially opened stage progress.
- Overall project: **CURRENT % NOT ESTABLISHED**; historical reference **20.9%** only.

Formula remains pending owner-approved M1–M8 weights and criterion-to-deliverable mapping: `overall = Σ(weight × verified completion fraction)`. Duplicate credit is prohibited.

### Gate 10 status

Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No new external acceptance evidence in this cycle closes any of these criteria. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed.


## Batch 18.1 — deployment status labeling correction — 18 Nov 2026

The Batch 18 READY deployment records are for audited source `64f348cebccbfb3fad2b9efe5a066d28962970f6`, not the later documentation-only branch head. After Batch 18 documentation commit `ef453a1af9310d2c19fad8ae7afc1262530216cc`, GitHub reports WSS deployment **PENDING** and frontend deployment **FAILURE: Deployment rate limited — retry in 24 hours**. The dashboard now labels these separately to avoid presenting prior READY previews as current-head deployments. The Batch 18 technical CI/HTTP results remain scoped to source `64f348c`. No retry loop, paid upgrade, billing, SSO change or production promotion.

Overall project remains **CURRENT % NOT ESTABLISHED**; **20.9% HISTORICAL ONLY**. Stage 1 remains 75% provisional; Gate 10 0/10 closed.


## Batch 19 — executable WebSocket protocol contract and corrected progress accounting — 18 Nov 2026

### WebSocket protocol regression coverage added

Added `backend/tests/test_vercel_ws_protocol.py`. It imports the isolated synthetic POC application by its repository path and uses FastAPI/Starlette TestClient to exercise the ASGI WebSocket protocol, not just source-text patterns. Coverage includes:

1. WebSocket handshake, ready message and ping/pong round-trip with matching session ID and sequence.
2. Invalid-message error followed by close code 1003.
3. Oversized-message error followed by close code 1009.
4. Twelve-message/ten-second rate boundary and rate-limited close code 1013 on the next message.
5. HTTP health response explicitly declaring `synthetic-only` and `production_data_connected=false`.

**Evidence boundary:** these are executable in-process ASGI protocol tests. They do not prove public Vercel WSS upgrade, browser behavior, 330-second platform lifetime, Android WebView, Fluid Compute effective settings, or multi-instance fan-out. Gate 36 remains OPEN until those external observations exist.

### CI checkpoint before Batch 19 commit

- Latest branch CI run [44288721128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721128) was still running at read-back; frontend tests/build, source and bundle credential scans, Android preflight/publisher tests, backend pytest (PASS), synthetic outbox benchmark, backend dependency audit had passed; backend image build was in progress. Do not claim this run complete.
- CodeQL run [44288721099](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721099): SUCCESS.
- Full Git History Secret Audit run [44288721127](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721127): SUCCESS.
- Vercel commit status for `362ff6e`: both WSS POC and frontend report **Deployment rate limited — retry in 24 hours**. No retry loops, plan upgrade, billing or SSO change.

### Dependency blocker — confirmed path and safe decision

The root lockfile contains `picomatch@4.0.7` as `dev: true`, with transitive parents `tinyglobby@0.2.17`, `vite@6.4.5`, and `vitest@4.1.12`, all also development-only. The GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) still reports High severity, affected through 4.0.7, and no patched version. Upstream issue [#247](https://github.com/micromatch/picomatch/issues/247) remains open in the latest read. No reviewed/released fix is available to justify a lockfile override. Do not downgrade to 4.0.4: that release addressed a different earlier advisory, not this later single-branch extglob finding. Keep npm audit enforcement fail-closed; dev-only status is exposure reduction, not remediation.

### Progress accounting

- Stage 1: **75% provisional**, 300/400 ticks, 30/40 provisional criteria.
- Gate 10: **0/10 formally closed**; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: **NOT SCORED**.
- Overall current project percentage: **NOT ESTABLISHED** because M1–M8 weights and criterion mapping are not approved/scored. Historical 20.9% is retained only as a historical checkpoint, not presented as current.

No Gate 10 closure or Stage 1 tick increase is awarded from adding tests alone. No Termux required. Zero-cost constraints maintained. `main` untouched.


## Batch 23 — WebSocket CI reconciliation, Vercel build filtering, and advisory re-audit — 18 Nov 2026

### WebSocket verification

The Batch 22 binary-frame regression is no longer pending. Backend pytest in run [44295544184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544184) passed. The regression verifies a binary frame is rejected through the protocol error response and close code 1003. This is synthetic ASGI protocol evidence only; Gate 36 remains open.

The same workflow completed with overall FAILURE because its final frontend dependency-audit enforcement step failed. Earlier test, build, credential-scan, backend, container, Redis/persistent-volume, and Trivy steps passed. Do not label the workflow green.

### Vercel deployment filtering

Both Git-linked Vercel projects were configured with project-level Ignored Build Step commands:

- Frontend `dezzta-chart`: skip only when all changed paths are confined to `poc/vercel_ws/`, `backend/`, `docs/`, and `.github/`.
- WebSocket POC `dezzta-chart-ws-poc`: skip unless a file under `poc/vercel_ws/` changed.

The commands use `VERCEL_GIT_PREVIOUS_SHA` and `VERCEL_GIT_COMMIT_SHA`. The `git diff --quiet` pathspec behavior was verified in an isolated temporary Git repository:
- docs-only change → frontend skip, WSS skip;
- frontend-only change → frontend build, WSS skip;
- WSS-only change → WSS build, frontend skip.

The commands use `|| exit 1`, so missing refs or a Git diff error do not silently skip a needed build; they fall through to a build. Project settings updates were accepted by Vercel. The available project read-back preserves existing domains, SSO protection and latest READY preview records, but does not return the ignored-build command field itself. The settings update itself did not trigger a deployment. The subsequent Git push produced a needed WSS catch-up deployment and skipped the frontend build; no preview was deleted or promoted.

This filtering is intended to reduce duplicate/irrelevant builds; it does not remove account-level build limits. First Git-triggered validation: frontend skip confirmed; WSS build ran only because WebSocket code changes had accumulated since the last successful WSS deployment. The WSS preview is now READY on the latest branch commit. The next documentation-only push should skip both projects, but that post-catch-up case has not yet been separately observed.

### Dependency advisory re-audit

GitHub issue [micromatch/picomatch#234](https://github.com/micromatch/picomatch/issues/234) remains open and was updated on 18 Nov 2026. Related upstream fix PRs [#237](https://github.com/micromatch/picomatch/pull/237), [#238](https://github.com/micromatch/picomatch/pull/238), [#257](https://github.com/micromatch/picomatch/pull/257), [#262](https://github.com/micromatch/picomatch/pull/262), [#264](https://github.com/micromatch/picomatch/pull/264), [#267](https://github.com/micromatch/picomatch/pull/267), and [#268](https://github.com/micromatch/picomatch/pull/268) were still open/unmerged at audit time. PR [#260](https://github.com/micromatch/picomatch/pull/260) contains further reported performance counterexamples and compatibility tradeoffs. These PRs are not official published releases. No unmerged patch or Git override is accepted as a production dependency remediation. Keep npm audit enforcement fail-closed until a maintainer-reviewed, published version and project-specific regression verification exist.

### Progress and cost accounting

- Stage 1: **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall current project percentage: **NOT ESTABLISHED**. Historical 20.9% remains historical only; M1–M8 weights and criterion mapping are not approved.
- Cost: **ZERO COST policy retained**. No billing changes, paid services, deployments, promotions, or SSO weakening.
- Termux: **not required**.
- `main`: untouched.

No Stage 1 ticks or Gate 10 closures are awarded for this configuration/documentation work.


## Batch 24 — branch-scoped Vercel preview containment and WebSocket evidence — 18 Nov 2026

### Deployment policy decision and implementation

- Team plan read-back: **Hobby**. Project Deployment Policy API rejected the attempted preview-only source allowlist with HTTP 403 `pro_plan_required`; no paid upgrade was attempted.
- The shared repository-root `vercel.json` applies to both Git-linked projects and contains `git.deploymentEnabled.main=true` plus `git.deploymentEnabled.phase-2/market-data-foundation=false`. This blocks automatic Git deployments from the active working branch while preserving the configured `main` production branch; it does not disable other deployment sources or globally disable Preview.
- Build logs show the WSS project's Vercel build entrypoint is `.` (repository root), while Python dependencies are discovered under `poc/vercel_ws/`. Therefore `poc/vercel_ws/vercel.json` is not the authoritative project-root config for this deployment. Batch 26 corrects this by putting `fluid: true` in the shared repository-root config. The frontend is a static Vite project with no serverless function in this deployment, so the Fluid setting has no active function workload there.
- A project-level `resourceConfig.fluid=true` update was also accepted by the Vercel API, but the available project read-back does not expose the effective field; no field-level confirmation is claimed.
- This commit is intentionally the single planned branch update for both projects. Vercel deployment creation must be checked against the exact resulting SHA. The config is documented by Vercel as suppressing Git deployments for matching branches before a deployment is created; Ignored Build Step remains only a secondary build filter.
- No Vercel API deployment policy was enabled (Hobby restriction); no project was paused, no preview was deleted, no SSO setting changed, and no production promotion occurred.

### WebSocket acceptance checkpoint

- WSS preview `dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg` remains READY on `9873a5f`; protected `/health` and root page both returned HTTP 200 on 18 Nov 2026. Health payload remains `synthetic-only`, `production_data_connected=false`.
- Backend ASGI tests cover handshake, synthetic ping/pong, invalid JSON/type, binary rejection (1003), oversized frame (1009), rate limit (1013), and idle timeout. These do not prove the deployed Vercel WebSocket Upgrade or browser-to-server round-trip.
- Still unverified: public WSS Upgrade/ping-pong, foreground 330-second run and close attribution, Android WebView, effective Fluid Compute read-back, and cross-instance fan-out. Gate 36 remains OPEN.

### CI/security and progress accounting

- Latest fully inspected CI run remains [44295544184](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544184): frontend/backend tests and builds, secret scans, Android checks, backend audit, container/Redis/Trivy checks passed; final frontend dependency audit enforcement failed on five High findings through dev-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. Enforcement remains fail-closed.
- CodeQL [44295544205](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544205) and full Git history secret audit [44295544181](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44295544181) passed.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 remain **NOT SCORED**. Overall current percentage remains **NOT ESTABLISHED**; 20.9% is historical only.
- Zero-cost maintained. No Termux, billing, paid services, production deployment, or `main` modification.


## Batch 25 — serialize WebSocket recovery after transport errors — 18 Nov 2026

### Root cause and correction

- The authenticated OHLCV client reports a transport/protocol error and then closes the underlying socket. The supervisor previously scheduled a reconnect immediately from `onError`, while also scheduling from the authoritative `onClose` event.
- The timer guard prevented duplicate timers, but a delayed browser close event could arrive after the reconnect delay and allow a replacement socket to open while the previous socket was still closing.
- Changed the supervisor so `onError` reports the error and sets the visible state to `reconnecting`, but does **not** start the retry timer. The authoritative `onClose` event now owns transport retry scheduling. Token-provider failures still use the existing catch/finally retry path.
- Added a deferred-close regression test: after an error, advancing timers by 1,000 ms must not create a second socket until the original close event is delivered; after close, the bounded 50 ms test delay creates exactly one replacement with a fresh token.

### Verification and boundaries

- Source-level replacement and test insertion were validated against the exact active-branch file contents before commit. Full TypeScript/Vitest execution is pending the branch CI run; no test pass is claimed until CI reports it.
- Existing cursor-resume, snapshot/replay, fresh-token, bounded-backoff, terminal authentication/entitlement close, and stop-cancellation tests are preserved.
- This is a client lifecycle reliability fix. It does not prove public Vercel WebSocket Upgrade, platform 300-second lifetime behavior, Android WebView, or cross-instance fan-out. Gate 36 remains OPEN.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No score increase is awarded for this code/test addition alone.
- Zero-cost maintained; no Termux, billing, paid service, deployment, or `main` change.


## Batch 26 — Vercel root configuration correction and Fluid Compute declaration — 18 Nov 2026

### Root-directory evidence and correction

- Read the WSS preview build events for `dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg`. Vercel reports build `entrypoint: "."`, clones the repository root, and resolves Python from `poc/vercel_ws/.python-version` and dependencies from `poc/vercel_ws/requirements.txt`. This confirms the WSS project's build root is the repository root; the nested `poc/vercel_ws/vercel.json` is not the authoritative project-root configuration for that deployment.
- Updated the shared root `vercel.json` to include `"fluid": true`, preserving the branch-scoped `git.deploymentEnabled` rules. This makes Fluid Compute explicit for the WSS Python function while keeping the active working branch's Git preview deployment disabled and `main` enabled.
- The frontend project uses Vite and serves static output; no frontend serverless function is present in this deployment. The shared Fluid flag therefore has no active frontend function workload.
- Vercel documents Fluid Compute as enabled by default for projects created after 23 April 2025, and the WSS project was created on 17 November 2026. The explicit root setting removes reliance on that default. Hobby's documented maximum function duration remains 300 seconds; Fluid Compute does not make a 330-second invocation permissible on Hobby.
- The Vercel API accepted a WSS project-level `resourceConfig.fluid=true` update, but read-back does not expose the effective field. The root `vercel.json` is the authoritative, version-controlled configuration; effective deployment behavior still requires a future permitted deployment and runtime verification.

### Validation and progress

- Root JSON parsed successfully before commit. Branch guard values remain `main=true` and `phase-2/market-data-foundation=false`.
- No Vercel deployment was created by the settings update. The branch remains protected from Git-triggered preview creation by the root config; exact-SHA deployment records and status contexts must still be checked after the commit.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 remain **NOT SCORED**. Overall current percentage remains **NOT ESTABLISHED**; 20.9% remains historical only.
- Zero-cost maintained. No Termux, billing changes, paid service, production promotion, or `main` modification.


## Batch 27 — make Gate 30 post-restore write verification durable — 18 Nov 2026

### Defect found

- The existing restore drill's post-restore probe created a table, inserted a row, read it back, dropped the table, and committed all within one SQLite connection/transaction.
- That proved transaction-local read-your-writes, but did **not** prove the inserted probe survived a commit and a fresh connection. The report label `post_restore_write_read_cleanup=passed` therefore overstated the durability property being exercised.

### Correction

- The probe now creates and inserts its unique drill-owned record, commits it, closes the writer, and reads the exact record through a separate read-only connection.
- Only after successful committed readback does it drop the probe table in a new write transaction, commit cleanup, and verify absence through another read-only connection.
- If committed readback fails, a best-effort cleanup removes only the drill-owned probe table while preserving the original failure. A pre-existing table with the same name is still rejected and is never removed.
- Added two regression tests: (1) proves the probe row exists through the fresh read-only connection and is absent after cleanup; (2) injects a readback failure and proves the committed probe table is cleaned up.

### Scope and evidence boundary

- This strengthens repository-level restore verification. It does not prove the owner's actual Android database path, target-device execution, recovery time on the owner's device, or off-host disaster recovery.
- Gate 30 remains **OPEN** until a timestamped drill runs against the actual application database on the owner-controlled target. Gate 31 remains **OPEN** for off-host destination, separate key custody, retention, and recovery.
- Exact-head CI has not yet executed for this commit; the new tests are implemented, not yet claimed PASS.
- Stage 1 remains **75% provisional — 300/400 ticks; 30/40 criteria**. Gate 10 remains **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No ticks are awarded for this source-level correction.
- ZERO COST maintained. No Vercel deployment, paid service, billing change, production data access, or `main` modification. The actual phone-only execution may require Termux/Python; no Termux installation or command has been requested or performed in this batch.

## Batch 28 — exact-head WebSocket and Gate 30/31 reconciliation — 18 Nov 2026

### Exact branch and CI evidence

- Active branch resolves to `e6db77210dd28bd82196b2b7bf7d8d7e7256fc37`; this is the current audited head.
- GitHub combined commit status for that exact SHA returned an empty status list. The available workflow-run lookup is PR-triggered only, so this is **not evidence that push-triggered CI passed or failed**. No test result is inferred from missing status contexts.
- Exact-SHA Vercel deployment lookup returned zero records for both linked projects. No deployment was created or retried in this audit.
- `main` remains untouched. No deployment, production promotion, billing change, paid service, or Termux command was performed.

### WebSocket client lifecycle audit

- Re-read `ohlcvStreamSupervisor.ts`, `ohlcvStreamSupervisor.test.ts`, `ohlcvWebSocketClient.ts`, and `ohlcvWebSocketClient.test.ts` at the exact branch head.
- The supervisor waits for the transport `onClose` event before scheduling a replacement socket after a transport error. Token acquisition failures retain their separate bounded retry path.
- Existing regression coverage includes delayed close, duplicate close notification, stop-before-retry, stop-during-token-acquisition, cursor resume/replay, snapshot/update sequencing, sequence-gap rejection, and clean explicit close.
- This is source/test-presence verification only. Vitest was not run in this audit and no new CI run is confirmed. Public WSS Upgrade, deployed ping/pong, Android WebView, 330-second platform close attribution, and multi-instance fan-out remain unverified; Gate 36 stays OPEN.

### Gate 30/31 reconciliation

- Batch 27's SQLite probe commits the drill-owned record, verifies it over a fresh read-only connection, commits cleanup, and verifies absence through another connection.
- Two regression tests are present for committed readback and cleanup after injected readback failure. They are **implemented, not confirmed passing** until exact-head pytest/CI evidence is available.
- Gate 30 remains OPEN pending a timestamped restore drill against the actual owner-controlled application database.
- Gate 31 remains OPEN pending an actual zero-cost off-host artifact, separately controlled recovery key, retention/access policy, and successful recovery drill. No storage provider is assumed or provisioned.

### Documentation reconciliation

- The top-level audit target and latest-update heading are synchronized to the current branch head and Batch 28. Older historical batch records remain preserved below.
- Stage and gate accounting is unchanged: Stage 1 **75% provisional (300/400 ticks; 30/40 criteria)**; Gate 10 **0/10 formally closed**; open criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**; Stages 2–6 **NOT SCORED**; overall current percentage **NOT ESTABLISHED**; 20.9% is historical only.
- No Stage 1 ticks or Gate 10 closures are awarded for documentation reconciliation or source/test additions without acceptance evidence.
- ZERO COST maintained. No Termux installation or command requested or performed.


## Batch 30 — exact-head CI, WSS preview and deployment-filter reconciliation — 18 November 2026

### Exact repository and automated verification

- Branch: `phase-2/market-data-foundation`; exact HEAD: `0126c847b015f08645b8b64cdb37ad458bc2fd43`. Main was not modified.
- Automated Tests run [44304765032](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44304765032) completed with FAILURE only at the final Enforce frontend dependency audit result step.
- Frontend Vitest: **26 test files, 212 tests passed**. WebSocket-specific frontend suites: client **6/6**, protocol **14/14**, supervisor **14/14**.
- Backend pytest: **1,030 passed in 35.88 seconds**, including backend OHLCV stream hub, authenticated API WebSocket, Vercel POC protocol, and bounded probe contract tests.
- Frontend production build, frontend source/bundle credential scans, Android host preflight, immutable Android preview publisher tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis ACL/persistent-volume smoke test, Trivy image scan/report steps all passed.
- CodeQL [44304764936](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44304764936) and Full Git History Secret Audit [44304764965](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44304764965) completed SUCCESS.

### Dependency blocker — exact cause and safe disposition

- Exact-head npm audit reports five High findings through picomatch, pulled by fdir / tinyglobby through development dependencies Vite and Vitest.
- The audit's suggested npm audit fix --force would install vite@6.2.7, a breaking downgrade from the current Vite 6.4.5 toolchain. This is not an acceptable automatic remediation.
- GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) and OSV [record](https://osv.dev/vulnerability/GHSA-fc5q-39xc-vjpf) were checked on 18 Nov 2026; they still identify the affected range through 4.0.7 and do not publish a patched version.
- Keep the final audit enforcement active. Keep the existing dependency-exposure regression. Do not downgrade, vendor an unmerged upstream patch, suppress, waive, or mark the advisory fixed. This remains the sole failing CI enforcement step.

### WebSocket — source tests vs deployed transport

- Frontend WebSocket client/protocol/supervisor regression suites all passed in the exact-head CI run. Backend pytest also passed all stream and synthetic POC protocol contracts.
- Existing WSS POC deployment dpl_4mPXXnj2XLLoNZYe5JkdQ1M7r5tg is READY on source 9873a5fd1c52a0cbab94683c0c309732407212e8, with target=null (preview, not production).
- Protected /health read-back returned HTTP 200 and the exact payload status=ok, service=dezzta-ws-poc, mode=synthetic-only, production_data_connected=false.
- The WSS preview is isolated synthetic POC. HTTP health does not prove a public WebSocket Upgrade, browser ping/pong, authentication of a real market-data session, Android WebView, or cross-instance fan-out.
- Vercel's official Fluid Compute documentation lists Hobby's maximum function duration as 300 seconds. The 330-second browser probe intentionally runs beyond that boundary to observe a platform-originated close; no foreground observation or close attribution has yet been collected. The 330-second client timer itself is not evidence of a 330-second server lifetime.
- Gate 36 remains OPEN. No production market-data connection or production promotion.

### Vercel cost and deployment controls

- Exact-SHA deployment lookups for HEAD 0126c847... returned zero deployment records for frontend and WSS.
- The existing frontend deployment dpl_tYw6Y4dbeSzwR6t7shtkKpT7nxBc was canceled by its configured Ignored Build Step. Build log states the command returned exit code 0 because the changed paths did not require a frontend build; this is intentional skip behavior, not a failed Vite build.
- The existing WSS preview remains READY; no new build or deployment was started during this audit.
- Root vercel.json retains main=true and phase-2/market-data-foundation=false. No retry loop, paid upgrade, billing activation, SSO weakening, or production promotion.

### Gate 10 and progress accounting

- Stage 1: **75% provisional — 300/400 ticks; 30/40 criteria**. No increase awarded in this batch.
- Gate 10: **0/10 formally closed**. Open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall current project percentage: **NOT ESTABLISHED** until M1–M8 weights and criterion mapping are approved. Historical 20.9% remains historical only.
- No Termux required for CI, GitHub, or protected HTTP checks. Any future owner-device restore or Android-native verification requiring Termux must be raised before asking the owner to install or run anything.
- ZERO COST maintained; no deployment, paid service, billing change, production promotion, or main-branch modification.


## Batch 31 — multi-gate engineering reconciliation — 18 November 2026

### Exact-head CI and security disposition

The audited source baseline remains `e6db77210dd28bd82196b2b7bf7d8d7e7256fc37`; Batch 30 HEAD `0c12dc54bce9fb5694b57e13928d995ff258ecef` changed documentation only. Exact-head run [44306105968](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306105968) reports frontend 212/212 and backend 1,030/1,030 passing, plus production build, credential scans, Android preflight/publisher tests, outbox benchmark, backend audit, container build, Redis/persistent-volume smoke and Trivy report steps passing. The workflow is still red solely because npm audit enforcement found five High dev-transitive picomatch findings. The exact audit log recommends a breaking Vitest downgrade; it was rejected. CodeQL [44306106124](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306106124) and Full Git History Secret Audit [44306106134](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306106134) both succeeded.

### Gate 30 — local restore correctness vs owner-target proof

Source review confirms the restore drill compares integrity, foreign keys, required application tables, row counts, row hashes, schema hash, domain-level records and outbox identity. The post-restore probe now commits before a fresh read-only read and commits cleanup before a separate absence check. CI passed the relevant backend suite. The remaining acceptance item is a timestamped drill against the actual owner-controlled application database; CI fixtures cannot substitute for that.

### Gate 31 — encryption and off-host boundary

The local SQLite helper is intentionally not an encryption or transfer layer. Existing repository evidence for encrypted snapshot/decrypt/restore is not equivalent to off-host retention. Still required: a genuinely zero-incremental-cost off-host destination, separately controlled recovery-key custody, explicit retention/access policy and successful recovery from that destination. No provider was provisioned or assumed.

### Gate 36 — WebSocket boundary

Frontend and backend WebSocket regression tests pass at the audited source baseline. The deployed POC evidence remains synthetic-only HTTP health. The external checks still missing are real public Upgrade and ping/pong, owner-observed foreground probe with platform close attribution, Android WebView, effective Fluid Compute configuration and cross-instance fan-out. No Vercel deployment was initiated because the branch guard disables branch deployments and the current goal is audit, not an unnecessary build.

### Stage and Gate 10 indicator

- Stage 1: **75% provisional — 300/400 ticks; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** pending an approved M1–M8 weighting ledger and criterion mapping. Historical 20.9% remains historical only.
- No stage ticks are awarded for documentation, CI alone, or source-level checks that do not meet the external acceptance condition.

**Disposition:** no safe repository-only change can honestly close the remaining external gates or remediate the currently unpatched dependency advisory. Keep fail-closed controls; do not trade security or zero-cost constraints for a superficially green status.


# BATCH 58 — Post-commit exact-head CI closure and Gate 10/indicator reconciliation

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Verified parent HEAD:** `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`  
**Cost:** ZERO COST • **Deployments:** none • **Termux:** not required • `main`: untouched

## 1. Exact-head CI completion for Batch 57 documentation commit

The push-triggered workflows for exact HEAD `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d` have now completed:

| Workflow | Run | Final result |
|---|---:|---|
| Automated Tests + Build | [44482698128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44482698128) | SUCCESS |
| CodeQL Security Analysis | [44482698127](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44482698127) | SUCCESS |
| Full Git History Secret Audit | [44482698387](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44482698387) | SUCCESS |

Automated test job completed successfully. Frontend Vitest reports **28 test files passed**; backend pytest reports **1,040 passed in 34.00 seconds**. Frontend npm audit reports **0 vulnerabilities**; backend dependency audit reports **no known vulnerabilities**. The exact-head workflow completed successfully, including the configured backend/container and build checks. CodeQL and full-history secret audit are successful at the same SHA.

**Scope correction:** Android debug APK CI success documented for source HEAD `66c8a6741b1abe4d1e89ef0d5ad6ce0abb72a77d` is parent-baseline evidence, not an Android build run for documentation-only HEAD `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`. Do not report it as a fourth workflow on `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`.

## 2. WebSocket Batch 56C disposition

The source-level lifecycle hardening remains validated by frontend/backend regression coverage and exact-head CI on the source baseline. No newly confirmed repository-only blocker was found in this review. Do not make speculative changes to the stable close/reconnect state machine.

Gate 36 remains OPEN until independently observed public authenticated WSS upgrade, real Firebase project token-state E2E, Android WebView foreground/background behavior, 330-second session attribution, and cross-instance fan-out are recorded. The synthetic POC is not production acceptance. No deployment was initiated to manufacture evidence.

## 3. Gate 10 acceptance register — unchanged

**Formal closure: 0/10. Open: 10/10.**

| Gate | Internal repository evidence | External/owner acceptance still required |
|---:|---|---|
| 8 | Configuration and runtime code | Owner-host secret injection, protected mounts, runtime log/readback |
| 20 | Single-use HTTPS ticket endpoint and WSS renewal | Real Firebase valid/expired/revoked/wrong-project E2E |
| 25 | Atomic Redis ticket consumption and ACL tests | Independent owner Redis, multi-instance and outage drill |
| 30 | SQLite backup/restore implementation and CI smoke | Restore against actual owner-controlled database |
| 31 | Local encryption/snapshot/restore helpers | Zero-cost off-host copy, separate key custody, retention and off-host restore |
| 34 | Container persistent-volume and restart smoke | Owner-host volume, restart and disk-pressure evidence |
| 35 | HTTPS/WSS configuration source | Public ingress, certificate renewal and external scan |
| 36 | Ticket protocol and lifecycle regression suite | Public WSS, Android WebView, 330-second attribution, cross-instance fan-out |
| 38 | Local observability components | Durable cross-instance collector, retention and protected access |
| 39 | Local alert/incident components | Named operator, escalation route and acknowledgement drill |

## 4. Indicator progress — full technical ledger

The five calculation foundations are implemented and unit-tested. This does not mean the user-facing indicators are complete. No visual indicator UI was added in this batch because Stage 1 remains active and Stage 4 implementation is gated by the approved roadmap.

| Indicator | Formula/data contract | Calculation readiness | Visible UI / acceptance |
|---|---|---|---|
| SMA 20 | Rolling arithmetic mean of 20 closes; first valid index 19 | 🟢 Foundation + tests | 🟡 Overlay, toggle, legend, latest value and render/lifecycle tests pending |
| EMA 20 | SMA-seeded EMA; first valid index 19 | 🟢 Foundation + tests | 🟡 Overlay, toggle, legend, latest value and render/lifecycle tests pending |
| RSI 14 Wilder | Wilder-smoothed average gain/loss; first valid index 14 | 🟢 Foundation + tests | 🟡 Dedicated 0–100 pane, 30/70 guides, toggle and lifecycle tests pending |
| MACD 12/26/9 | EMA12−EMA26; MACD first valid index 25; signal/histogram index 33 | 🟢 Foundation + tests | 🟡 Dedicated pane, signal line, histogram, zero guide and lifecycle tests pending |
| Bollinger 20,2 | 20-close mean ± 2 population standard deviations; first valid index 19 | 🟢 Foundation + tests | 🟡 Three-line overlay, fill, toggle, legend and lifecycle tests pending |
| Shared `useMarketIndicators()` | Validated non-empty backend snapshot; no DEMO fallback | 🟡 Hook foundation | 🟡 Visible controls and stale-series clearing on symbol/timeframe changes pending |
| Footprint | Bounded deterministic offline simulation only | 🟡 Simulated foundation | 🟡 Reference image + approved blueprint + dedicated ON-only cluster layout required |
| Heatmap | No verified implementation | 🔴 Not implemented | 🔴 Reference image + approved blueprint + data/render/test implementation required |
| Liquidation Maps | No verified implementation | 🔴 Not implemented | 🔴 Reference image + approved blueprint + data/render/test implementation required |

### Formula and integrity checks

- SMA 20: arithmetic mean over exactly 20 valid closes; warm-up slots remain null.
- EMA 20: initial SMA seed followed by α = 2/(20+1); warm-up slots remain null.
- RSI 14: Wilder smoothing, aligned to source candle indexes; flat-series handling must remain deterministic.
- MACD 12/26/9: EMA12 minus EMA26; signal EMA9 begins only after nine valid MACD values; histogram is MACD minus signal.
- Bollinger 20,2: population standard deviation, divisor 20; upper/lower bands are mean ± 2σ.
- Every output must preserve candle-index alignment and use null during warm-up; no fabricated values or demo fallback.
- The existing unit-test coverage validates formula behavior against fixtures, not live provider data quality or visible chart integration.

### Visual constraints and feature gate

- Footprint OFF must preserve ordinary candlestick layout and normal spacing.
- Only explicit Footprint ON may switch to the dedicated spaced-candle/cluster layout.
- Footprint and Heatmap reference images must be supplied by the owner before visual implementation; Liquidation Maps also require an approved scoped visual/data blueprint.
- Do not begin Stage 4 UI expansion during Stage 1. Keep the existing roadmap gate and require blueprint review before major implementation.

## 5. Project progress accounting

- Stage 1: **75% provisional — 30/40 criteria; 300/400 ticks**. No increase awarded by this CI/documentation batch.
- Gate 10: **0/10 formally closed; 10 OPEN**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED** pending approved M1–M8 weights and criterion mapping. Historical 20.9% remains historical only.
- CI exact HEAD `d61a0d815a58469f0e0f8acc6590c7ecee1eed4d`: **3/3 workflows PASS** (Automated Tests, CodeQL, Full Git History Secret Audit).
- ZERO COST maintained; no Vercel/Cloudflare deployment, no paid service, no billing change, no production promotion, no Termux action, and no `main` modification.

## 6. Next multi-gate work sequence

1. Gate 20/25: prepare owner-controlled Firebase/Redis acceptance evidence matrix; no mock is accepted as production proof.
2. Gate 36: retain stable source; run public WSS and WebView acceptance only when existing deployment/runtime access permits without creating a paid or quota-consuming deployment.
3. Gate 30/31/34: consolidate restore, key custody, off-host retention and volume acceptance into one evidence pack. Do not assume an off-host free destination exists.
4. Gate 8/35: verify existing host configuration/readback before considering any deployment.
5. Gate 38/39: specify durable collector retention, protected access and incident acknowledgement evidence.
6. Keep indicator UI parked; preserve calculations and the full readiness ledger until Stage 4 authorization.

**Batch 58 disposition:** exact-head CI closed successfully. No source-code change was justified by the inspected evidence; no gate was falsely closed. Documentation/dashboard are refreshed to reflect final CI state.


# BATCH 59 — Exact-head CI finalization (19 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD:** `5099033ed76fbf4d40d9b4a7e2f3250904145d75`  
**Cost:** ZERO • **Deployments:** none • **Termux:** not required • `main`: untouched

## Exact-head CI results

All three workflows for the exact Batch 58 HEAD completed successfully:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests + Build | [44483259055](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44483259055) | SUCCESS |
| CodeQL Security Analysis | [44483258942](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44483258942) | SUCCESS |
| Full Git History Secret Audit | [44483258991](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44483258991) | SUCCESS |

Automated Tests + Build evidence from run 44483259055:

- Frontend: **28 test files passed**.
- Backend: **1,040 tests passed in 29.42 seconds**.
- Frontend npm audit: **0 vulnerabilities** (both audit invocations reported zero).
- Backend dependency audit: **no known vulnerabilities found**.
- Frontend production build and credential scanning completed successfully.
- Android host preflight and immutable preview publisher tests completed successfully; these are test checks, not a device-side release.
- Synthetic SQLite outbox benchmark completed and its report was uploaded. It is synthetic benchmark evidence only, not owner production-load acceptance.
- Backend container image built; shared Redis guard + persistent-volume smoke test completed; Trivy HIGH/CRITICAL image scan and vulnerability-report export/upload completed. This record confirms the scan ran successfully; it does not assert zero image findings because the verified log excerpt does not establish a zero-finding count.

CodeQL JavaScript/TypeScript and Python jobs both succeeded. Full reachable Git-history secret audit succeeded.

## WebSocket / Gate 10 disposition

No new WebSocket source defect was demonstrated by this CI cycle. Existing client regression suite covers ticket authentication/renewal, heartbeat and pong timeout, replay cursor, sequence-gap rejection, observer isolation, transport close fallback, and terminal state. Do not destabilize the state machine without a reproducible defect. Gate 36 remains OPEN for real public authenticated WSS, Android WebView foreground/background, 330-second attribution and cross-instance fan-out evidence.

Formal Gate 10 closure remains **0/10**. Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain OPEN pending the owner-host, Firebase, Redis, off-host backup, public ingress, device, collector and operator evidence specified in Batch 58. CI success is not substituted for those acceptance drills.

## Indicator ledger and project score

No indicator implementation state changed in this CI-only batch. Preserve the full per-indicator formula/readiness ledger in this document and Batch 58. SMA20, EMA20, RSI14, MACD12/26/9 and Bollinger20,2 calculation foundations remain unit-tested; user-facing chart overlays/panes remain pending. Shared hook remains backend-snapshot-only. Footprint remains simulation-only and gated by owner reference + approved blueprint. Heatmap and Liquidation Maps remain not implemented. Footprint OFF retains standard candles; only explicit ON may activate spaced cluster layout.

- Stage 1: **75% provisional; 30/40 criteria; 300/400 ticks** — unchanged.
- Gate 10: **0/10 formally closed** — unchanged.
- Stages 2–6: **NOT SCORED**.
- Overall project score: **NOT ESTABLISHED** pending approved M1–M8 weights and criterion mapping.

**Batch 59 conclusion:** all exact-head CI workflows passed; no source edit was warranted; no external gate is falsely marked closed. No Vercel/Cloudflare deployment, no paid service, no Termux action and no `main` change.



# BATCH 60 — Gate 10 zero-cost acceptance matrix and evidence quality controls (19 November 2026)

**Branch:** `phase-2/market-data-foundation`
**Parent:** `ade070ab04fcefd8f4b49103afe191224996bccf`
**Scope:** documentation/evidence planning only; no production credentials, external service mutation, or source behavior change.
**Cost:** ZERO • **Deployment:** none • **Termux:** not required • `main`: untouched.

## 1. CI state and correction of evidence labels

Batch 58 source HEAD `5099033ed76fbf4d40d9b4a7e2f3250904145d75` has 3/3 CI workflows SUCCESS: Automated Tests + Build (run 44483259055), CodeQL (44483258942), and Full Git History Secret Audit (44483258991). Its evidence includes 28 frontend test files, 1,040 backend tests, frontend dependency audit with zero vulnerabilities, backend dependency audit with no known vulnerabilities, backend container build, Redis/persistent-volume smoke, and completion of Trivy HIGH/CRITICAL scan/report export. No zero-finding Trivy claim is made.

Batch 59 documentation commit `ade070ab04fcefd8f4b49103afe191224996bccf` triggered a separate CI set: Automated Tests + Build run 44483765684, CodeQL run 44483765691, and Full Git History Secret Audit run 44483766211. At the latest verified read-back for this batch, CodeQL and Secret Audit were SUCCESS; Automated Tests was still executing the backend container image scan/report workflow. Do not label the Batch 59 commit 3/3 PASS until run 44483765684 reaches completed/success. The dashboard distinguishes source-head CI from docs-commit CI.

## 2. Gate 10 — evidence acceptance matrix

All ten formal gates remain OPEN. The plan consolidates work into five evidence packs to reduce repeated setup while preserving each gate's independent acceptance decision.

| Pack | Gates | Zero-cost work already evidenced | Required owner-side acceptance artifact | Pass condition / blocker |
|---|---|---|---|---|
| A — identity + shared guard | 20, 25 | Firebase verifier source checks issuer/audience/subject/auth_time and revocation; Redis guard tests atomic limits, ticket consume, lease lifecycle, TLS/ACL policy; CI Redis smoke | Redacted real-project matrix for valid, expired, revoked, wrong-project tokens; independent Redis ACL/TLS identity; two-instance consume/renew/release; Redis outage + recovery trace | All identity cases reject/accept correctly; ticket single-use across instances; no over-limit lease; fail-closed outage and bounded recovery. Missing real Firebase project and owner Redis endpoint. |
| B — WSS runtime | 36 | Frontend/backend protocol tests for auth, ticket renewal, heartbeat/pong, cursor replay, sequence gaps, observer isolation and close fallback | Existing public HTTPS/WSS endpoint; real Upgrade + authenticated session; foreground/background browser and Android WebView; timed 330-second run with platform close attribution; two-instance fan-out trace | Real authenticated WSS round-trip, correct renewal/reconnect and fan-out, bounded/attributed close. Must not create a new deployment solely to obtain evidence. |
| C — recovery + persistence | 30, 31, 34 | SQLite online backup/restore integrity and readback tests; AES-GCM encrypted backup tests; container persistent-volume smoke | Actual owner target-database restore record; encrypted artifact copied to an already-available zero-cost off-host destination; separately controlled recovery-key custody; retention/access record; owner-host mount/restart/disk-pressure trace | Restore passes integrity, FK, schema/domain checks and post-restore write/read; off-host recovery works without co-located key; data survives host restart and disk-pressure handling. Off-host destination/key custody currently unproven. |
| D — runtime boundary + ingress | 8, 35 | Source/bundle/history secret scans, production configuration validation, container/health checks | Owner-host masked secret injection and protected mount readback; public HTTPS/WSS certificate chain, renewal observation and external ingress scan; sanitized runtime logs | No secret in source/bundle/logs; only intended runtime identity can read mounts; public TLS and renewal pass. Never capture secret values in evidence. |
| E — telemetry + incident response | 38, 39 | Bounded/sanitized metrics and local incident reporter tests; local recovery/dedup logic | Durable cross-instance collector, retention/rotation, protected dashboard access; named responsible operator, escalation route, alert receipt and acknowledgement/recovery drill | Metrics survive process restart and aggregate across instances; alert is actually received and acknowledged by an accountable operator. Local JSON log alone is insufficient. |

## 3. Common evidence schema — required for every pack

Each accepted drill must preserve: (1) unique evidence ID and gate IDs; (2) UTC start/end timestamps; (3) tested environment/service identifier with secrets and personal data redacted; (4) operator role (no credentials); (5) exact scenario and expected result; (6) observed result and pass/fail; (7) redacted logs/trace and cryptographic digest of the retained artifact; (8) recovery/cleanup outcome; (9) cost delta = zero; and (10) independent reviewer/owner acknowledgement. No bearer tokens, private keys, passwords, raw customer identifiers, or secret environment values may enter the report.

A test fixture, fake Firebase project, local Redis, synthetic WSS endpoint, CI container, or documentation statement is supporting engineering evidence only. It cannot be promoted to owner production acceptance. If a prerequisite does not exist at zero incremental cost, record BLOCKED with the exact missing dependency; do not provision paid infrastructure or burn deployment quota to force a green state.

## 4. Execution order and dependency logic

1. Pack A first: Gate 20 identity correctness and Gate 25 shared ticket/lease atomicity are prerequisites for trusting public WSS authentication.
2. Pack B second: Gate 36 only after A passes; reuse the existing owner-approved endpoint and devices. The 330-second observation must capture actual platform close attribution, not infer it from a timer.
3. Pack C in one controlled maintenance window: combine Gate 30 restore, Gate 31 off-host/key separation and Gate 34 persistence/restart evidence. Keep recovery-key custody separate from the backup artifact.
4. Pack D: verify runtime secret injection and ingress/certificate chain on the existing host without deployment or secret disclosure.
5. Pack E: test durable telemetry and a real human acknowledgement after collector/retention/access controls exist.

No gate closes automatically when another pack passes. Each gate requires its own evidence review. Formal closure count remains **0/10** until all its acceptance criteria are met.

## 5. Indicator progress — complete ledger retained, no false completion credit

The complete per-indicator ledger and formula contract in this file remain authoritative and unchanged by this documentation cycle:

| Indicator | Current calculation/data foundation | Remaining visible/acceptance work | Status |
|---|---|---|---|
| SMA 20 | Rolling close mean; first valid index 19; tested | Chart overlay, toggle, legend/current value, identity/timeframe clearing, render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; first valid index 19; tested | Chart overlay and lifecycle/render acceptance | 🟨 Foundation |
| RSI 14 | Wilder smoothing; first valid index 14; tested | 0–100 pane, 30/70 guides, toggle and render/lifecycle tests | 🟨 Foundation |
| MACD 12/26/9 | MACD first index 25; signal/histogram first index 33; tested | Dedicated pane, two lines, histogram, zero guide and lifecycle/render tests | 🟨 Foundation |
| Bollinger 20,2 | Population standard deviation; first valid index 19; tested | Three-line/band overlay, toggle, legend and render tests | 🟨 Foundation |
| Shared indicator hook | Validated backend snapshot only; null for demo/loading/unavailable/error | Visible binding and stale-data clearing on instrument/timeframe changes | 🟨 Foundation |
| Footprint | Deterministic bounded SIMULATED data only | Owner visual reference + reviewed blueprint + ON-only spaced cluster renderer | 🟨 Gated |
| Heatmap | No implementation verified | Owner reference + blueprint + source contract, calculations, renderer and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Owner reference + blueprint + source contract, calculations, renderer and tests | 🟥 Not implemented |

Calculation details remain: SMA20 rolling mean; EMA20 SMA-seeded with alpha 2/21; RSI14 Wilder; MACD EMA12−EMA26 with EMA9 signal; Bollinger20,2 using population standard deviation. Warm-up outputs remain null and index-aligned. Tests across 18 timeframe labels are fixture formula evidence, not provider data-quality or visible integration proof. No per-indicator percentage is invented.

Visual invariants remain mandatory: Footprint OFF keeps ordinary candlestick layout and spacing; only explicit ON enables spaced cluster layout. Footprint/Heatmap/Liquidation Maps visual implementation requires the relevant owner reference image(s) and scoped blueprint review. Stage 1 remains active, so visible Stage 4 indicator work stays parked.

## 6. Progress and release accounting

- Stage 1: **75% provisional; 30/40 criteria; 300/400 ticks** — unchanged.
- Gate 10: **0/10 formally closed; all ten OPEN**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; historical 20.9% is not a current weighted score.
- ZERO COST maintained. No Vercel/Cloudflare deployment, paid resource, production promotion, Termux operation, or `main` change.
- Documentation-only evidence planning awards no stage/gate completion ticks.

**Batch 60 disposition:** the work packages, evidence schema, dependency order and indicator ledger are documented. External acceptance blockers are explicitly isolated rather than hidden by CI or mock results.


# BATCH 61 — Cross-client Redis atomicity regression and scan-report review

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Parent baseline:** `1253d592a490247c081d326118a331da8e156592`  
**Scope:** Gate 25 local integration coverage + exact-head evidence reconciliation. No production deployment, no paid service, no Termux, and no `main` modification.

## 1. Newly added Redis integration regression

The existing real-Redis ticket test exercised single-use consumption sequentially through one guard/client. Batch 61 adds a separate integration case using **two independent Redis client connections** to the same CI Redis service:

- Issue one single-use ticket through client A; concurrently consume through A and B; exactly one consumer must receive the verified subject and the other must receive `None`.
- Acquire an account-scoped WebSocket lease through A; B must be denied a second lease for that same account.
- B can acquire a lease for a different account while global capacity remains; a third connection must be rejected at the global cap.
- B must be able to renew and release A's lease; A can then acquire the freed capacity.

This is real Redis Lua/Redis state integration in CI, not a FakeRedis-only test. It proves atomic shared-state behavior across independent client connections. It does **not** prove two separately deployed owner application instances, independent owner Redis, production ACL configuration, or an outage drill; Gate 25 remains OPEN until owner acceptance.

## 2. Container vulnerability report review

Batch 60's uploaded Trivy JSON report for image `dezzta-chart-backend:ci` was downloaded and inspected. The report contains two scan result groups (Alpine OS packages and Python packages) and **zero HIGH/CRITICAL vulnerability entries** under the workflow's configured severity filter. This is scoped to that exact CI image digest and scan timestamp; it is not a guarantee of zero vulnerabilities at other severities or in later images.

## 3. Gate 10 status and dependency disposition

- Gate 20: OPEN — real Firebase project valid/expired/revoked/wrong-project E2E still needs owner project credentials and controlled execution.
- Gate 25: OPEN — Batch 61 adds cross-client Redis atomicity regression; owner-managed independent Redis + separately deployed instances + outage/recovery evidence still missing.
- Gate 36: OPEN — public authenticated WSS, Android WebView foreground/background, 330-second close attribution and deployed cross-instance fan-out remain external acceptance.
- Gates 8/30/31/34/35/38/39: OPEN — owner-host secrets/ingress, actual restore/off-host key custody/persistence, durable telemetry and operator acknowledgement remain unproven.

No gate closure or Stage 1 ticks are awarded from this local test addition.

## 4. Indicator progress ledger — unchanged, explicitly complete as a status record

| Indicator / component | Verified foundation | Remaining work | State |
|---|---|---|---|
| SMA 20 | Rolling close mean; first valid index 19; tested | Visible overlay, toggle, legend/value, stale-series lifecycle and render tests | 🟨 Foundation |
| EMA 20 | SMA-seeded EMA; first valid index 19; tested | Visible overlay, toggle, legend/value, stale-series lifecycle and render tests | 🟨 Foundation |
| RSI 14 Wilder | Wilder smoothing; first valid index 14; tested | Dedicated 0–100 pane, 30/70 guides, toggle and render/lifecycle tests | 🟨 Foundation |
| MACD 12/26/9 | MACD first index 25; signal/histogram first index 33; tested | Dedicated pane, signal line, histogram, zero guide and render tests | 🟨 Foundation |
| Bollinger 20,2 | Population standard deviation; first valid index 19; tested | Upper/middle/lower overlay, toggle, legend/value and render tests | 🟨 Foundation |
| Shared indicator hook | Validated backend snapshot only; null in demo/loading/unavailable/error states | Visible binding and immediate clearing on identity/timeframe changes | 🟨 Foundation |
| Footprint | Bounded deterministic `SIMULATED` data | Owner reference image, reviewed blueprint, explicit-ON spaced cluster renderer | 🟨 Gated |
| Heatmap | No implementation verified | Owner reference, blueprint, source/data contract, calculation, renderer and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Owner reference, blueprint, source/data contract, calculation, renderer and tests | 🟥 Not implemented |

Calculation contract remains: SMA20 rolling mean; EMA20 SMA-seeded (`alpha = 2/21`); RSI14 Wilder; MACD EMA12−EMA26 with EMA9 signal; Bollinger20,2 population standard deviation. Warm-up values are null and outputs remain aligned to source candle indexes. Existing tests across 18 timeframe labels are fixture formula evidence, not provider data-quality or visible chart acceptance.

**Visual invariants:** Footprint OFF must retain ordinary candle layout/spacing; only explicit Footprint ON may enable spaced cluster layout. Footprint/Heatmap/Liquidation Maps visuals require the owner's reference image(s) and a reviewed scoped blueprint. Stage 1 is active, so Stage 4 visible UI remains parked.

## 5. Current progress accounting

- Stage 1: **75% provisional** — 30/40 criteria, 300/400 ticks; unchanged.
- Gate 10: **0/10 formally closed**, all ten OPEN.
- Stages 2–6: **NOT SCORED**.
- Overall project: **NOT ESTABLISHED**; no invented weighted percentage.
- CI baseline entering Batch 61: Batch 60 exact HEAD had Automated Tests, CodeQL, and Full Git History Secret Audit all SUCCESS (3/3). Batch 61's own commit must receive its own exact-HEAD CI result before it can be called green.
- ZERO COST; no Vercel/Cloudflare deployment; Termux not required; `main` untouched.


# BATCH 62 — Global outbox relay foundation and indicator ledger reconciliation

**Date:** 19 November 2026 • **Parent:** `45a887ae65e556d4457602467c4963f8d195d270` • **Branch:** `phase-2/market-data-foundation`  
**Scope:** global outbox scan API + regression tests + architecture decision; no distributed relay or production acceptance claimed.

## Confirmed architecture facts

- `SQLiteOhlcvStore.apply()` commits accepted candle revisions and outbox events atomically.
- The durable outbox contains stable event IDs, monotonic global cursors, exact series identity, and a bounded 100,000-event retention window.
- `replay_outbox()` is exact-series scoped for authenticated client replay; it is not suitable as a global relay scan.
- `OhlcvStreamHub` is process-local. Local fan-out is implemented, but it does not broadcast to another app process.
- The SQLite database uses a local filesystem path and WAL; it must not be treated as a safe multi-host shared network database.

## Batch 62A implementation

Added `SQLiteOhlcvStore.read_outbox_batch()` for a future relay worker. It returns bounded global pages in cursor order, with high-water and retention floor from the same SQLite read snapshot. Expired/ahead cursors return explicit `resnapshot_required`.

Added tests for mixed-series ordering, pagination, cursor/high-water progression, retention expiry, ahead cursors, and argument validation. This is source/test groundwork only; no Redis relay or cross-instance delivery is claimed.

## Durable relay decision

Preserve SQLite as source of truth. Future relay delivery is at-least-once. Use deterministic cursor identity, verify duplicate append on retry, and deduplicate before local hub publication. Every app instance needs its own consumer group; one shared group distributes events instead of broadcasting. Pending entries must be reclaimable. Retention exhaustion must trigger explicit resnapshot, never silent skip. See `docs/ADR_WEBSOCKET_CROSS_INSTANCE_OUTBOX_RELAY.md`.

## Gate 10 status

Gate 25 and Gate 36 remain OPEN. The global outbox reader enables a safe relay implementation path, but owner-managed Redis, deployed app instances, outage/recovery and Android WebView/330-second evidence are not present. Gates 8,20,30,31,34,35,38,39 remain OPEN pending their acceptance packs. No Gate closure or Stage 1 ticks are awarded.

## Complete indicator ledger — capability state unchanged

| Indicator | Calculation/data foundation | Formula / first valid index | Visible integration still required | State |
|---|---|---|---|---|
| SMA 20 | Implemented + fixture-tested | Rolling close mean; index 19 | Overlay, toggle, legend/current value, identity/timeframe clearing and render tests | 🟨 Foundation |
| EMA 20 | Implemented + fixture-tested | SMA seed; alpha = 2/21; index 19 | Overlay, toggle, legend/current value, lifecycle/render tests | 🟨 Foundation |
| RSI 14 | Implemented + fixture-tested | Wilder smoothing; index 14 | 0–100 pane, 30/70 guides, toggle and lifecycle/render tests | 🟨 Foundation |
| MACD 12/26/9 | Implemented + fixture-tested | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Dedicated pane, signal line, histogram, zero guide and render tests | 🟨 Foundation |
| Bollinger 20,2 | Implemented + fixture-tested | Population standard deviation; index 19 | Upper/middle/lower overlay, toggle, legend and render tests | 🟨 Foundation |
| Shared `useMarketIndicators()` | Validated backend snapshot only | No DEMO/loading/unavailable/error fallback | Visible binding and stale-series clearing on identity/timeframe changes | 🟨 Foundation |
| Footprint | Bounded deterministic simulation only | Explicit `SIMULATED`; not real exchange bid/ask | Owner reference image, reviewed blueprint, explicit-ON spaced cluster renderer | 🟨 Gated |
| Heatmap | No implementation verified | Not available | Reference, blueprint, source contract, calculations, renderer and tests | 🟥 Not implemented |
| Liquidation Maps | No implementation verified | Not available | Reference, blueprint, source contract, calculations, renderer and tests | 🟥 Not implemented |

**Calculation contract:** warm-up outputs remain null and aligned to original candle indexes. Fixture coverage across 18 timeframe labels is not provider data-quality proof or visible integration. No per-indicator completion percentage is invented.

**Visual invariants:** Footprint OFF preserves ordinary candle layout/spacing; only explicit ON enables spaced cluster layout. Footprint/Heatmap/Liquidation Maps visuals require the owner's relevant reference images and reviewed scoped blueprint. Stage 1 is active; visible Stage 4 work remains parked.

## Current project accounting

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed**; all ten remain OPEN.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED.
- Batch 62 exact-head CI: pending until this commit's workflows finish.
- ZERO COST; no Vercel/Cloudflare deployment; no Termux; `main` untouched.


# BATCH 62H-0 — Redis publisher contract audit (19 November 2026)

**Branch:** `phase-2/market-data-foundation` • **Parent:** `3bccf107ff88a2bc7330afa1015e85b20708c773` • **Scope:** documentation-only architecture audit; no executable code changed.

Confirmed separation: RedisSharedGuard is a security primitive, not the OHLCV relay. The current OHLCV path persists bars/outbox in SQLite and fans out to the process-local OhlcvStreamHub. `read_outbox_batch()` is the existing bounded global cursor reader suitable for a future publisher.

The 62H publisher contract now requires deterministic Redis Stream IDs (`cursor-0`), a source-SQLite publisher checkpoint, exact duplicate read-back verification after the XADD/checkpoint crash window, single-writer serialization/fencing, no unsafe MAXLEN trimming, explicit snapshot rebuild when source retention overtakes the publisher cursor, and source-write independence during Redis outage. Every gateway must have its own consumer group; ACK follows durable local replica apply only.

**Next:** 62H-1 checkpoint schema/API, but only after exact-head validation of 62G. No startup wiring, Redis provision, deployment, or Termux is authorized by this documentation batch.

## Indicator ledger — complete status retained

This audit made no indicator code or formula changes. The full detailed ledger above remains canonical; the summary is reproduced in `docs/WORK_CYCLE_2026-11-19_BATCH62H0_REDIS_PUBLISHER_CONTRACT.md`. Status remains:
- 🟨 SMA20: rolling mean, first index 19; calculation/fixtures present; overlay/toggle/legend/stale clearing/render tests pending.
- 🟨 EMA20: SMA-seeded, alpha 2/21, first index 19; calculation/fixtures present; visible overlay lifecycle pending.
- 🟨 RSI14: Wilder smoothing, first index 14; calculation/edge fixtures present; dedicated pane/30–70 guides/lifecycle pending.
- 🟨 MACD12/26/9: EMA12−EMA26, MACD index 25, signal/histogram index 33; calculation fixtures present; pane/line/histogram/zero guide pending.
- 🟨 Bollinger20,2: population standard deviation, first index 19; calculation fixture present; three-line overlay/lifecycle pending.
- 🟨 Shared indicator hook: validated backend snapshot only; chart binding/loading/error/stale-identity clearing pending.
- 🟨 Footprint: deterministic SIMULATED accumulator only; reference image + reviewed blueprint + ON-only spaced cluster renderer required.
- 🟥 Heatmap: no implementation verified; reference/data/calculation/renderer/tests pending.
- 🟥 Liquidation Maps: no implementation verified; reference/data/calculation/renderer/tests pending.

Footprint OFF must preserve normal candle spacing. Do not begin Footprint/Heatmap/Liquidation visual implementation before receiving the corresponding owner reference images and reviewing the scoped blueprint. Stage 4 visible UI remains parked while Stage 1 is active.

**Accounting unchanged:** Stage 1 75% provisional (30/40; 300/400); Gate 10 0/10 closed (all OPEN); Stages 2–6 NOT SCORED; overall percentage NOT ESTABLISHED because M1–M8 weights are not approved. No ticks or gate closure from this audit. ZERO COST; no deployment; no Termux; `main` untouched.


# BATCH 62G-4 — exact-head CI regression repair (19 November 2026)

The Automated Tests workflow for `f093061f144120257fcb6d1eda44d51f966376ae` reported **1,061 passed / 1 failed**. Frontend unit tests/build passed and CodeQL succeeded. The sole failure was `test_replica_snapshot_rejects_numeric_decimal_fields_even_with_valid_digest`: the test fixture wrote literal backslash-n sequences instead of actual JSONL newlines, so parsing failed at the header before the intended Decimal type assertion.

The test fixture in `backend/tests/test_ohlcv_store.py` was corrected to hash and write actual newline-delimited records. Production snapshot validation was not weakened or changed. Repair commit: `eeaf1586886a1c3aec2be1a32e6c182a6085ea81`. Exact-head CI for the repair commit remains pending; do not mark the test green until its run completes.

**Indicator status unchanged:** SMA20, EMA20, RSI14, MACD12/26/9 and Bollinger20,2 have calculation/fixture foundations but visible integration remains pending; shared hook needs chart binding/loading/error/stale clearing; Footprint remains SIMULATED and reference/blueprint-gated; Heatmap and Liquidation Maps remain unimplemented. Footprint OFF retains normal candle spacing; explicit ON alone enables spaced clusters. The complete formula, warm-up, tests and remaining-work ledger above remains canonical.

**Accounting unchanged:** Stage 1 75% provisional (30/40; 300/400); Gate 10 0/10 closed; Stages 2–6 NOT SCORED; overall project percentage NOT ESTABLISHED. No ticks or gates are awarded by this repair. ZERO COST; no deploy; no Termux; `main` untouched.


## 62H-1 CI repair note

Run `44537009483` exposed one test-fixture error: the CAS test supplied cursor 2 while its expected cursor remained 0, triggering the correct contiguous-cursor guard before CAS. Fixed the test to replay the already-confirmed cursor-1 event with stale expected cursor 0, which directly exercises the intended compare-and-swap rejection. No production logic was changed for this repair. Repair commit `e37f7ecda67b80e1c9d6aff593c8cb342304ead8` is awaiting exact-head CI.


## Complete indicator ledger

See `docs/INDICATOR_PROGRESS_LEDGER.md` for formula definitions, first-valid indexes, current implementation state, remaining chart UI/lifecycle acceptance, Footprint/Heatmap/Liquidation gates, and project accounting. The table above is a concise snapshot; the separate ledger is the canonical detailed record.


# LIVE AUDIT CHECKPOINT — 19 NOVEMBER 2026 (WIB)

## Exact-head CI reconciliation — Batch 62J-2 repair commit

- Code commit: `9eb936778f75caa4b0c5aaa512f8e3091be8ad1b`.
- Automated Tests run `44548655650`: SUCCESS; all 55 reported steps completed successfully, including frontend tests/build, backend tests, dependency audit, backend container build, Redis/persistent-volume smoke and image scan/report steps.
- CodeQL run `44548655582`: SUCCESS for Python and JavaScript/TypeScript.
- Full Git History Secret Audit run `44548655649`: SUCCESS.
- The previous three bridge-test failures were test-fixture/API misuse: `outbox_event_for_bar()` returns cursor/eventId metadata, not a canonical event envelope. Tests now obtain the canonical event from `read_outbox_batch()`. Production assertions were not weakened.
- Backend/frontend exact test totals were not exposed by the job summary retrieved in this audit; no numeric totals are asserted here.

## Vercel live account audit — read-only

- Team: `deszztagd377-pixel`; projects found: `dezzta-chart` and `dezzta-chart-ws-poc`.
- Latest listed WebSocket POC deployment: `dpl_5VXGuNtmkxzWTDQkcGZgBrrL7WrK`, state `READY`, commit `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`.
- Latest listed main-project deployment: `dpl_tYw6Y4dbeSzwR6t7shtkKpT7nxBc`, state `CANCELED`; Vercel reports the Ignored Build Step documentation as its error link. This is not evidence of a usage-limit block.
- Earlier main-project deployment `dpl_3hNjT1oQFn6h22BTY2b3Qh2RXKFS` is `READY`.
- Team API response did not expose plan/quota counters. Billing charges endpoint returned `404 costs_not_found`. Therefore remaining quota, spend-to-date, and hard/soft limit status are **NOT VERIFIED**. READY proves deployment capability for that deployment, not remaining quota.
- No deployment, promotion, configuration change, billing change, or service provisioning was performed during this audit.

## WebSocket next engineering boundary

62J-2 bridge code is exact-head CI-green, but it is still a library integration and is not started from `main.py`. The next safe batch must cover real-Redis callback ordering (durable apply before ACK), callback failure/no-ACK, ACK-loss redelivery, restart hydration, partial multi-subscriber fan-out, and then the replica snapshot/replay read model plus event-loop-safe worker dispatch. Dedicated `OHLCV_REDIS_URL` ACL separation must be derived from actual Redis commands and CI configuration; do not broaden the existing shared-guard ACL. Do not wire startup or deploy until these tests and lifecycle proofs pass.

## Accounting unchanged

- Stage 1: **75% provisional** — 30/40 criteria; 300/400 ticks.
- Gate 10: **0/10 formally closed** — Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain OPEN pending owner evidence.
- Stages 2–6: NOT SCORED.
- Overall weighted project percentage: NOT ESTABLISHED; M1–M8 weights remain unapproved.
- ZERO COST maintained; no Vercel/Cloudflare deployment, no paid service, no Termux, and `main` untouched.


## 62J-3 / 62J-4 engineering checkpoint — 19 November 2026

- Callback recovery test additions were committed at `4b7cd9771a9997330c01f8e42a1331ae27e2fb0e`: callback exception leaves the Redis delivery pending; ACK-reply-loss recovery reclaims and re-invokes the callback on duplicate apply. **CI result for this commit is not yet available from the connected workflow-run/status endpoints; do not mark it passed.**
- Replica snapshot read-model implementation: `SQLiteOhlcvReplicaStore.query_snapshot()` now reads retained bars and replica checkpoint (`source_id`, `applied_cursor`, `retention_floor`) within one SQLite read transaction. It overrides the inherited source-store implementation, which depended on source outbox state and was not valid for replica watermark semantics.
- Tests added for checkpoint-aligned snapshot result, bounded filtering, and fail-closed behavior before snapshot installation. Code commit: `3b19a483d3a3d93dea34181dd343595f265b2e82`; tests finalized at `146ab7861266e9b32b548059fa1a4391f530855c`.
- This closes one read-model prerequisite only. Redis replay pagination/retention semantics, snapshot-to-live handoff on replica, event-loop-safe callback dispatch, dedicated relay ACL, ASGI lifecycle and multi-process WebSocket E2E remain open. No `main.py` startup wiring.
- No new Vercel/Cloudflare deployment, paid service, or Termux requirement. `main` remains untouched.


## Batch 62J-5 — 19 November 2026

- Added `backend/app/ohlcv_redis_replay.py`: bounded `XRANGE` replay through a fixed watermark, global cursor pagination across unrelated series, exact series filtering, canonical envelope/source/stream-ID validation, series-vs-bar identity validation, and fail-closed resnapshot on missing/trimmed cursor history.
- Added `backend/tests/test_ohlcv_redis_replay.py` for bounded pages, unrelated-series cursor advancement, missing cursor, truncated history, malformed series identity and empty interval.
- Added a real Redis 7 integration test in `backend/tests/test_ohlcv_redis_consumer.py` for multi-page replay, exact-series filtering and deleted-entry gap detection.
- Documentation: `docs/WORK_CYCLE_2026-11-19_BATCH62J5_REDIS_REPLAY_READ_MODEL.md`.
- Latest code/test commits: `cdfbe6c4adea61da0f8c95a495d28845b98a3c7e`, `d76a8241d23336bae679923fc4d5be632abf07cf`, `fe9f93cb8938bf46eee404bcd6c9117067d8e06b`, `31a7bd7da63d26aff77d65c50d4624baccb6740e`, `2c983704ce1846716aed224bc16967a90ec53ee4`. Documentation commit: `2ed424b2139b96f06892697f1cfaa228c3af17d3`.
- CI for the final batch head is not yet verified. No WebSocket endpoint wiring, worker startup, Vercel/Cloudflare deployment, paid service, or Termux requirement.
- Indicator statuses are unchanged. Stage 1 remains 75% provisional (30/40 criteria; 300/400 ticks); Gate 10 remains 0/10 closed; Stages 2–6 unscored; overall weighted project percentage not established.
