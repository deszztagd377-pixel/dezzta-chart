# DEZZTA CHART — Batch 62J-122
## Exact-head WebSocket CI, artifact and runtime-boundary audit

## Batch 62J-122 — exact-head WebSocket CI, artifact and runtime-boundary audit (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Audited exact HEAD:** 4c3e9f9f4cd8317c5cd03357b51aae06d289a804  
**Automated Tests [run 44984396895](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895): SUCCESS**; **CodeQL [run 44984396918](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396918): SUCCESS**; **Full Git History Secret Audit [run 44984396926](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396926): SUCCESS**. All three runs target the exact audited HEAD.

### CI evidence and limitations
- Frontend: 29 Vitest files, 255 tests passed.
- Backend: 1,294 passed, 1 skipped. The skipped test was the real Redis TLS/shared-guard integration test because REDIS_TEST_URL was not configured. The workflow's separate container smoke did exercise a CI Redis instance; this does not turn the skipped integration case into a pass.
- Container smoke passed: health endpoint, Redis ACL authentication, AOF data surviving Redis restart, fail-closed API behavior during Redis outage, backend reconnection, non-root UID/GID 10001, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit rejection.
- Trivy report artifact [14739352623](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739352623) was independently inspected. Exact image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, image digest sha256:28fc78838f596968e3825ac2f46ffd3a1c7b688e029c62b53fcad2cd8bc09f85, reported **0 vulnerabilities** in Alpine OS and Python package result groups. Image size: 571,350,016 bytes (~571 MB). This is point-in-time scanner output for this exact amd64 image and database, not a permanent guarantee and not ARM64 evidence.
- Synthetic outbox artifact [14738863888](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14738863888): 1,000 synthetic bars/events; persist p95 2.655 ms; concurrent replay-page p95 1.305 ms with two reader threads. Local single-process SQLite microbenchmark only, not a real provider or WebSocket load/SLO test.
- Synthetic metrics collector artifact [14739436712](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44984396895/artifacts/14739436712): 899 logical series; one thread 32/32 flushes, 0 retries, p95 flush 8.10 ms; four threads 128/128, 2 retries, p95 flush 112.97 ms and writer-lock p95 105.38 ms; 16 threads 512/512, 65 retries, p95 flush 350.53 ms and writer-lock p95 315.97 ms; four independent processes 128/128, 1 retry, p95 flush 60.23 ms; staggered 16-worker case 512/512, 0 retries. SQLite integrity was ok in all reported cases. This demonstrates contention in concurrent same-host SQLite workloads, but is not a production host or multi-host benchmark. Do not infer multi-worker capacity or SLO from it.

### WebSocket runtime boundary audit
- Source and gateway runtime factories remain explicitly injected into separate ASGI app roles. The app rejects simultaneously injecting both roles into one instance.
- Production settings require Redis TLS URL and Firebase project ID; the shared guard is mandatory in production. The non-production in-memory ticket store is not production acceptance.
- Source publisher activation requires a host-supplied snapshot verifier callback. Its evidence must bind source ID, stream key, generation, cursor, SHA-256 and one matching installation receipt per required gateway. The callback remains a trust boundary: the owner must independently verify snapshot bytes and authenticate each receipt; repository shape validation cannot probe remote gateways.
- Gateway activation requires an owner-supplied snapshot installer and validates its returned metadata against the durable local replica checkpoint before creating the Redis client/consumer. This does not independently establish remote source authenticity; owner transport and evidence custody remain external.
- Replica worker obtains a generation-scoped lease before group access, ensures group readiness before serving, and runs one sequential consumer per replica identity. Existing lease and consumer code fail closed on unverifiable/lost ownership, apply-before-ACK, reclaim pending messages, and require resnapshot on history gaps.
- No source change was made in this batch. These are source-review findings, not new runtime acceptance tests.

### Production disposition
Public hostname/TLS/reverse proxy, real Firebase signed-token and entitlement E2E, owner-host Redis ACL/secret rotation/persistence/failover, authenticated global snapshot receipts, public browser WSS and Android WebView lifecycle evidence remain absent. Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. CI container Redis and ephemeral volume evidence does not close owner-host gates.

### Indicator ledger reconciliation
Compare from indicator implementation baseline 0074f1d0b0e421f32800294742f92d9bc9c8a2c6 through 4c3e9f9f4cd8317c5cd03357b51aae06d289a804 contains documentation paths only; no indicator calculation, hook, renderer, UI, formula or indicator test implementation changed. Therefore this batch awards **zero indicator implementation progress**. Keep SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook at 🟨 foundation; Footprint 🟧 simulated/reference-gated; Heatmap and Liquidation Maps 🟥 not implemented. No aggregate percentage without approved weights/denominator. Footprint/Heatmap visual work remains blocked on user references and reviewed blueprint; Footprint OFF preserves ordinary candle spacing.

### Cost and change boundary
Documentation-only update. No deployment, host, resource, provider, paid service, account or credential was created or used. No main-branch changes, no device/Termux work, and no runtime or test files modified. ZERO COST maintained.

**Next safe sequence:** finish exact-head evidence review; design a zero-cost ARM64 build/smoke verification separately from amd64; retain the SQLite concurrency warning; and keep production gates open until owner-controlled evidence exists.
---
