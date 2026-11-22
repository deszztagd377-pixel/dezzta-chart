# Batch 62J-132 — WebSocket CI acceptance closure and operational benchmark review
Date: 22 November 2026
Branch: `phase-2/market-data-foundation`
Source/test baseline: `d549d99318abbeb156f716a4e2cf749eef226ca9`
The documentation follow-up commit is separate from this tested source baseline and must receive its own CI check.

## 1. Exact-baseline CI result

All three workflows completed successfully on exact source/test baseline `d549d99318abbeb156f716a4e2cf749eef226ca9`:

- [Automated Tests — run 44989988543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988543): SUCCESS.
- [CodeQL — run 44989988481](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988481): SUCCESS for JavaScript/TypeScript and Python.
- [Full Git History Secret Audit — run 44989988510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988510): SUCCESS.

Automated Tests completed frontend unit tests/build and credential scans; backend tests; real Redis TLS fixture; synthetic SQLite outbox and metrics benchmarks; backend dependency audit; backend container build; container smoke test with shared Redis guard and persistent volume; container image scan; vulnerability report export; and frontend dependency audit enforcement.

## 2. Redis TLS evidence

The real TLS-only Redis fixture test `test_real_redis_tls_ca_hostname_acl_and_shared_guard_operations` passed. It exercises a trusted CA connection and shared-guard HTTP allowance, WebSocket ticket issue/consume, and connection lease acquire/renew/release. Negative cases reject an untrusted CA, a hostname mismatch, and plaintext downgrade. This is CI fixture evidence, not proof of owner-host production Redis configuration.

## 3. Container vulnerability scan

Trivy 0.76.2 scanned image `dezzta-chart-backend:ci`, digest `sha256:2943078f07ff217aedcdea4577b1edfed2c0355abbef37fa68d558110a71b643`, Alpine 3.24.4 and Python package results. The exported report contains **0 OS vulnerabilities, 0 Python package vulnerabilities, and 0 reported misconfigurations** in the two scan result targets. This is a point-in-time scan of the CI image, not a permanent guarantee or a production-host scan.

Artifact: `container-vulnerability-reports`, workflow artifact 14741547043. Benchmark artifacts: 14741373555 and 14741019750.

## 4. Synthetic performance evidence and limitation

### SQLite OHLCV outbox
- 1,000 synthetic bars persisted; high-water cursor 1,000.
- Persist latency: p50 2.911 ms, p95 4.155 ms, p99 5.943 ms (1,000 samples).
- Two concurrent replay reader threads, 4,581 page samples: p50 0.517 ms, p95 1.659 ms, p99 1.910 ms.
- This is a single-process synthetic local microbenchmark, not a provider, WebSocket reconnect-storm, multi-host or production SLO benchmark.

### SQLite operational metrics collector
- Full declared envelope: 899 logical series (762 request, 127 latency, 10 WebSocket); limit 900.
- Four independent OS processes / 128 flushes: p95 flush 139.854 ms, p99 277.444 ms; p95 writer-lock wait 128.714 ms, p99 263.448 ms; 3 retries; SQLite integrity `ok`.
- Sixteen-worker staggered process case / 512 flushes: p95 flush 287.759 ms, p99 524.206 ms; p95 lock wait 271.832 ms, p99 508.022 ms; 44 retries; integrity `ok`.
- Sixteen-thread high-concurrency case / 512 flushes: p95 flush 594.880 ms, p99 844.445 ms; 213 bounded lock retries; integrity `ok`.

Interpretation: SQLite preserves correctness in these synthetic cases, but writer-lock contention becomes material at higher fan-out. This is operational telemetry storage, not the OHLCV WebSocket delivery path. Do not infer WebSocket latency or production capacity from these numbers. Keep this as a bounded operational-performance follow-up; do not change the database architecture from one CI benchmark alone.

## 5. WebSocket acceptance gates

### Gate 25 — snapshot provenance and replica installation: OPEN
Confirmed: snapshot verification and transactional install checks are present; runtime compares source, generation and high-water cursor against the durable replica checkpoint; SHA-256 is format-checked and propagated as evidence. The durable checkpoint still does not anchor the snapshot digest in an immutable installation receipt. Owner-authenticated transfer, independent receipt custody, owner-host Redis CA/ACL, Redis persistence policy, restart/failover and retention acceptance remain open.

Design direction is recorded in `ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`: immutable receipt separated from the mutable replication cursor checkpoint. Digest integrity alone does not authenticate origin.

### Gate 36 — authenticated WebSocket edge and client lifecycle: OPEN
Confirmed CI covers ticket and entitlement test paths, bounded reconnect/replay, local TCP-path fault recovery, and Redis TLS fixture behavior. Public hostname, reverse proxy, public WSS certificate lifecycle, live Firebase project, production browser session, Android WebView foreground/background/process-death/network-handover and public-network acceptance remain unproven. Series/Origin ticket binding remains a threat-model decision, not an assumed defect.

### Explicit correction to avoid overclaim
The passing backend-container persistent-volume smoke test does **not** establish Redis AOF durability, Redis restart recovery or failover. Those remain separate owner-host/Redis acceptance items unless a dedicated Redis persistence test is independently evidenced.

## 6. Technical indicator ledger

No indicator implementation or test source changed in this batch; therefore no calculation or visual implementation credit is awarded.

- SMA20: 🟨 calculation foundation; first valid index 19.
- EMA20: 🟨 SMA-seeded EMA, alpha 2/21; first valid index 19.
- RSI14 Wilder: 🟨 foundation; first valid index 14.
- MACD12/26/9: 🟨 foundation; MACD first valid index 25, signal/histogram index 33.
- Bollinger20,2: 🟨 foundation; first valid index 19.
- Shared Indicator Hook: 🟨 backend snapshot/alignment foundation, not chart-integrated.
- Footprint: 🟧 synthetic educational accumulator only; visual implementation awaits user reference image and reviewed blueprint.
- Heatmap: 🟥 not implemented; awaits reference image and reviewed blueprint.
- Liquidation Maps: 🟥 not implemented.

Invariants: warm-up nulls, candle-index alignment, no future-candle repaint, no silent conversion of invalid/gapped bars to zero, stale output cleared on symbol/venue/dataset/chart/timeframe changes. Footprint OFF preserves standard candle spacing; explicit ON switches to spaced cluster layout.

## 7. Project indicators

- Stage 1: 30/40 criteria = 75% provisional.
- Stages 2–6: NOT SCORED / not officially opened.
- Gate 10: 0/10 external criteria formally closed.
- Overall project: NOT SCORED; no approved six-stage weighting/denominator exists.
- Do not reuse the historical 20.9% as current project completion.

### IP3S — Indicator Proses Peningkatan Proyek Signifikan

Batch 62J-132 = **67/100**, cycle delivery quality only:
- Verified engineering delta: 0/25 (no runtime/test source change).
- Exact-baseline CI evidence: 20/20.
- Blocker reduction/evidence closure: 12/20.
- Canonical documentation and benchmark interpretation: 20/20.
- Scope and ZERO COST integrity: 15/15.

IP3S is not project completion and cannot be added to the overall project percentage.

## 8. Scope and next sequence

This batch is documentation, CI evidence reconciliation and artifact analysis only. No runtime/test source edits, paid hosting, paid APIs, deployment, production credentials, device/Termux actions or `main` changes.

Next sequence:
1. Implement and test the snapshot installation receipt only after ADR review and migration/test design.
2. Finish owner-host Redis persistence/restart/failover acceptance as a separate gate.
3. Review ticket series/Origin binding threat model.
4. Define a measured concurrency acceptance threshold for metrics collector writer-lock wait before considering any optimization.
5. Run public WSS/browser/Android lifecycle acceptance only when a genuinely controlled, authorized environment exists; do not invent one or incur cost.
