# DEZZTA CHART — Work Cycle 62J-98
## WebSocket + Gate 25 gateway runtime + Gate 38 telemetry + Gate 36 WSS reconciliation

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Verified source/test HEAD:** `b4325216d1293d3c747978fc45218bfe1fd1d79f`  
**Main branch:** untouched.  
**Cost:** ZERO COST. No deployment or paid service.

## 1. Execution scope — requested points 1–4

This cycle deliberately handles the four next workstreams as one bounded batch:
1. WebSocket source/transport audit and exact-head regression verification.
2. Gate 38 telemetry audit and full-cardinality concurrency benchmark read-back.
3. Gate 25 Redis gateway runtime gap: implementation of a fail-closed gateway runtime factory.
4. Gate 36 HTTPS/WSS production-client guard audit and CI verification.

No production endpoint, host, provider, credential, device or Termux state is fabricated.

## 2. New Gate 25 implementation

Added:
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- Gateway runtime environment placeholders and operational comments in `backend/.env.example`.

### Runtime contract

`build_gateway_replica_runtime_factory()` creates the exact mapping expected by `create_app(replica_runtime_factory=...)`:
- A durable `SQLiteOhlcvReplicaStore`.
- A `RedisOhlcvReplicaConsumer` bound to that exact store, Redis client and stream key.
- A dedicated Redis client.
- A sanitized snapshot evidence summary.

The owner must supply an authenticated snapshot installer callback. It must retrieve/authorize the actual snapshot and call `SQLiteOhlcvReplicaStore.install_global_snapshot()`. The factory then checks:
- Installer status is `installed`.
- The durable checkpoint exists.
- Source ID matches the configured authoritative source.
- Snapshot generation and high-water cursor match the installed checkpoint.
- SHA-256 is exactly 64 lowercase hexadecimal characters.

Only after these checks is the Redis client created. Production Redis requires `rediss://`; TLS certificate validation and hostname checking are explicitly enabled. Connect/socket timeouts are 3s/5s, and the consumer uses a bounded 1,000ms Redis block interval for managed shutdown.

The runtime remains opt-in. `gateway_replica_runtime_factory_from_environment()` returns `None` unless `OHLCV_REDIS_ENABLED` is explicitly true. The default application is not silently switched to gateway mode. This helper does not authenticate remote receipts itself; that trust remains the responsibility of the owner-supplied installer.

### Regression coverage

Six tests cover:
1. Real source snapshot export and replica install, then TLS client construction.
2. Source identity mismatch rejected before Redis client creation.
3. Missing/unverified installer evidence rejected before Redis client creation.
4. Plaintext production Redis rejected before snapshot install.
5. Redis client closed when consumer construction fails.
6. Environment activation remains opt-in and production TLS is enforced.

No publisher/gateway protocol, stream schema, ACK ordering, Redis ACL matrix or frontend wire protocol was changed.

## 3. WebSocket workstream

Repository-side automated WebSocket protocol/failure-matrix coverage remains complete for its defined CI scope. This cycle audited the source publisher/consumer runtime boundaries and the browser client:
- Source publisher runtime still verifies global snapshot source, generation, cursor and per-gateway SHA-256 installation receipts before activation.
- Gateway runtime now has a symmetric builder and validates the installed local snapshot against its durable SQLite checkpoint before creating the Redis client.
- Consumer still uses generation-scoped groups, exclusive Redis lease ownership, apply-before-ACK, replay and resnapshot-on-gap behavior.
- Browser client still requires HTTPS in production, derives WSS from the HTTPS base URL, authenticates with a short-lived ticket, and performs bounded heartbeat/replay/ticket renewal.
- No wire-protocol change or production host acceptance is claimed.

Production WSS remains blocked on a real owner-controlled endpoint, TLS/reverse-proxy configuration, live dedicated OHLCV Redis, actual installed gateway receipts, and browser plus Android WebView acceptance.

## 4. Gate 38 — exact benchmark artifact read-back

Exact-head Automated Tests [44916614912](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912) produced benchmark artifact [14712222307](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912). The JSON artifact was downloaded and parsed, not inferred from a green badge.

Full declared envelope: 899 logical series = 762 HTTP request series + 127 latency series + 10 WebSocket series. All benchmark profiles reported SQLite integrity `ok`.

| Profile | Flushes | p95 flush | p99 flush | Max flush | Retries |
|---|---:|---:|---:|---:|---:|
| 1 thread | 32/32 | 8.38 ms | 9.85 ms | 9.85 ms | 0 |
| 4 threads | 128/128 | 137.59 ms | 259.57 ms | 299.76 ms | 0 |
| 16 simultaneous threads | 512/512 | 376.08 ms | 796.15 ms | 1,406.30 ms | 78 |
| 4 OS processes | 128/128 | 40.43 ms | 239.10 ms | 371.84 ms | 1 |
| 16 startup-staggered threads | 512/512 | 18.34 ms | 88.57 ms | 259.74 ms | 0 |

Staggered versus simultaneous 16-thread profile:
- p95 reduction: **95.12%**.
- p99 reduction: **88.88%**.
- Maximum flush-latency reduction: **81.53%**.
- Lock retries: **78 → 0**.
- 16/16 workers, 512/512 successful flushes and 899/899 logical series verified.

Staggered startup phases were 0–14 seconds, matching the production worker UUID-prefix modulo-15 phase. The logical cadence remains 15 seconds, with CI wall-clock scaling 0.01. This is a deterministic synthetic concurrency model, not a 7.5-minute real-time soak.

16-thread simultaneous peak DB+WAL+SHM was 5,777,912 bytes; staggered peak was 5,341,192 bytes. Both post-checkpoint totals were 1,126,400 bytes. Snapshot payload was 105,586/262,144 bytes = 40.28%. These are GitHub CI runner observations, not production storage sizing or SLA guarantees.

Gate 38 remains 🟧 OPEN: actual host persistent volume, backup/retention, cross-host aggregation, operator dashboard/access and recovery acceptance are still required. Process-local telemetry and a same-host SQLite collector are not represented as a multi-host monitoring system.

## 5. Gate 36 — HTTPS/WSS source guard

Existing production guard verified:
- Ticket exchange refuses non-HTTPS production backend URLs before fetch.
- WebSocket client refuses plaintext production transport before socket creation.
- HTTPS base URL is converted to WSS.
- Ticket request uses bearer authorization, no-store, omitted credentials, redirect rejection and a hard timeout.
- Renewal requires server acknowledgement and closes on renewal failure.

Frontend tests passed at this exact head. Gate 36 remains 🟧 OPEN until a real public HTTPS/WSS endpoint, certificate/hostname/renewal and real browser/Android WebView flow are accepted.

## 6. Exact-head CI and security acceptance

Verified on exact source/test HEAD `b4325216d1293d3c747978fc45218bfe1fd1d79f`:
- Automated Tests [44916614912](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912): **SUCCESS**.
- CodeQL [44916614959](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614959): **SUCCESS**.
- Full Git History Secret Audit [44916614967](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614967): **SUCCESS**.
- Frontend: **255 passed**, 29 test files.
- Backend: **1,277 passed in 42.72 seconds**.
- Android host preflight and immutable preview-publisher tests: SUCCESS.
- Backend container build and shared Redis ACL/AOF persistent-volume smoke: SUCCESS.
- Trivy artifact [14711468367](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44916614912) downloaded and parsed: **0 vulnerabilities** in Alpine OS and Python package targets at HIGH/CRITICAL scan severity.

### CI correction record

The first source candidate `7bf14593ddfa5d776245bb632896a8277635f9e0` failed backend test collection due to one unmatched trailing brace in the newly added module. The failure was read from the GitHub Actions log. The syntax defect was removed in `b4325216d1293d3c747978fc45218bfe1fd1d79f`, and the complete exact-head workflow then passed. The failed candidate is not accepted or reported as green.

## 7. Gate 10 and project accounting

Gate 10 remains **0/10 formally closed**:
- 🟨🟩 Host/operator verification only: Gates 8, 30, 34, 35, 39.
- 🟧 Additional integration/acceptance: Gates 20, 25, 31, 36, 38.

The new gateway factory advances repository-side Gate 25 readiness but does not close Gate 25. Gate 36 and Gate 38 remain host-bound. No acceptance tick is awarded by CI-only evidence.

Stage 1 remains **30/40 = 75% provisional**. Stages 2–6 and overall project percentage remain unscored without approved denominators and weights.

## 8. Full indicator progress — unchanged

No indicator formula, calculation module, shared hook, renderer, chart UI or indicator test changed in this backend/runtime batch. No indicator progress credit is awarded.

| Indicator / subsystem | Status | Formula / first valid candle index | Remaining work |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Chart overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, renderer/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 price changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, stale clearing, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend, stale clearing, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ±2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated candle-index-aligned snapshot | Chart identity/timeframe binding, loading/error lifecycle, stale clearing, series isolation |
| Footprint | 🟧 Simulated / gated | Educational accumulator, not exchange-native bid/ask truth | User reference image, reviewed blueprint, ON-only spaced clusters, bid/ask cells, performance acceptance |
| Heatmap | 🟥 Not implemented | No validated zero-cost data contract | User reference image, free-source feasibility, validated data contract, blueprint and renderer |
| Liquidation Maps | 🟥 Not implemented | No validated source/formula contract | Zero-cost source feasibility, validated calculation/data contract, reference/blueprint and renderer |

Invariants: warm-up slots remain null, not zero; outputs stay candle-index aligned; no future-candle repaint; symbol/venue/dataset/chart/timeframe changes clear stale series. Footprint OFF preserves ordinary candle spacing; only explicit ON activates spaced clusters. Footprint and Heatmap visual implementation remains gated on user references and reviewed blueprints.

## 9. Cost and device boundary

ZERO COST. No paid provider, deployment, Vercel/Cloudflare operation, production credential, Termux/device operation or `main` modification. No user-side code or document action is required for this repository batch.
