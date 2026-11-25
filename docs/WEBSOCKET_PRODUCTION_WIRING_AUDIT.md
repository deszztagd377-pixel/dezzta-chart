## Batch 62J-134 — WebSocket close-reason accuracy fix (22 November 2026)

Source/test commit: `ecf7decb8e823effe09a6be8a9973bb98619ae92` on `phase-2/market-data-foundation`.

### Engineering change
Backend source uses WebSocket close code 4403 for both:
- Origin policy rejection: reason `Origin not allowed` before authentication.
- Canonical instrument/series entitlement denial: reason such as `Instrument access denied` or `Instrument access revoked`.

Previously the client supervisor mapped every 4403 to an entitlement failure. That produced a false diagnosis for a frontend Origin configuration error. The supervisor now classifies 4403 by the server-provided close reason:
- Origin rejection → “WebSocket Origin is not allowlisted” diagnostic.
- Other 4403 reasons → entitlement denial/revocation diagnostic.
Both remain terminal and do not trigger an automatic reconnect loop.

Regression tests cover both branches, verify the error and snapshot detail, and verify no retry. Files changed:
- `src/services/ohlcvStreamSupervisor.ts`
- `src/services/ohlcvStreamSupervisor.test.ts`

This is a diagnostic correctness fix only; it does not weaken authentication, authorization, Origin enforcement, or reconnect policy.

### Exact-commit CI status
- Automated Tests run [44991640588](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640588): **IN PROGRESS** at documentation time; frontend unit tests and frontend build passed, Redis TLS fixture passed, backend tests still running.
- CodeQL run [44991640593](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640593): **SUCCESS** (JavaScript/TypeScript and Python).
- Full Git History Secret Audit run [44991640577](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640577): **SUCCESS**.
- Zero-cost Android debug APK workflow [44991640574](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44991640574): **IN PROGRESS**; web build and Android wrapper setup passed, APK assembly still running.

Do not call the new regression tests accepted until Automated Tests completes successfully. No APK artifact is claimed until its workflow reports success.

### Remaining WebSocket acceptance
- Gate 25 OPEN: immutable snapshot installation digest/provenance receipt, owner-authenticated transfer and owner-host Redis acceptance.
- Gate 36 OPEN: public WSS/reverse proxy/certificate lifecycle, live Firebase project, production browser session and Android WebView foreground/background/process-death/network handover.
- Gate 38 OPEN: owner-host metrics persistence, disk pressure/restart/backup/retention and operator dashboard/alert/recovery.
- Redis TLS/AOF restart: isolated CI fixture PASS on the preceding exact-head docs baseline; owner-host failover/backup/restore remains untested.

### Indicator and project indicators
No indicator source or tests changed; indicator implementation status receives no credit:
- SMA20 🟨 foundation (first valid index 19).
- EMA20 🟨 SMA-seeded alpha 2/21 (first valid index 19).
- RSI14 Wilder 🟨 foundation (first valid index 14).
- MACD12/26/9 🟨 foundation (MACD index 25; signal/histogram index 33).
- Bollinger20,2 🟨 foundation (first valid index 19).
- Shared Indicator Hook 🟨 backend snapshot/alignment only; not chart-integrated.
- Footprint 🟧 synthetic educational accumulator only; wait for user visual reference and reviewed blueprint.
- Heatmap 🟥 not implemented; wait for user visual reference and reviewed blueprint.
- Liquidation Maps 🟥 not implemented.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 remain NOT SCORED; Gate 10 remains 0/10 external criteria formally closed. Overall project remains NOT SCORED until stage weights and acceptance denominator are approved.

IP3S for this batch is **PENDING** until exact-commit Automated Tests completes. This prevents unverified source changes from receiving CI-evidence credit. ZERO COST; no deployment, paid service, production credentials, device/Termux operations or `main` changes.

---

## Batch 62J-132 — exact-baseline CI acceptance and indicator reconciliation (22 November 2026)

**Source/test baseline:** `d549d99318abbeb156f716a4e2cf749eef226ca9` on `phase-2/market-data-foundation`. This is the commit tested by the three successful workflows; the documentation follow-up commit is a separate HEAD and must receive its own CI check.

- Automated Tests [44989988543](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988543): **SUCCESS**.
- CodeQL [44989988481](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988481): **SUCCESS** for JavaScript/TypeScript and Python.
- Full Git History Secret Audit [44989988510](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989988510): **SUCCESS**.
- Automated Tests include backend tests, real Redis TLS fixture, synthetic outbox/metrics benchmarks, backend dependency audit, backend container build, persistent-volume/shared-Redis-guard smoke test, image scan and frontend dependency audit enforcement.
- Trivy 0.76.2 scan of backend image digest `sha256:2943078f07ff217aedcdea4577b1edfed2c0355abbef37fa68d558110a71b643`: **0 OS vulnerabilities, 0 Python package vulnerabilities, 0 reported misconfigurations** in the exported CI report. Point-in-time CI image evidence only.
- Synthetic outbox: 1,000 bars; persist p95 4.155 ms / p99 5.943 ms; two replay readers p95 1.659 ms / p99 1.910 ms. Not a WebSocket or production SLO test.
- Synthetic metrics collector (899 logical series): four-process p95 flush 139.854 ms, p99 277.444 ms, 3 retries; 16-worker staggered-process p95 287.759 ms, p99 524.206 ms, 44 retries; 16-thread p95 594.880 ms, p99 844.445 ms, 213 retries. SQLite integrity remained `ok`; writer-lock contention is material at high fan-out. This is operational telemetry storage, not OHLCV WebSocket delivery.
- **Correction:** backend container persistent-volume smoke test does not prove Redis AOF durability/restart/failover. Those remain open.

### WebSocket acceptance
- Gate 25: **OPEN** — snapshot digest is not anchored in an immutable receipt; authenticated owner-host transfer/receipt custody and owner-host Redis persistence/restart/failover remain unproven. Proposed ADR: `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md`.
- Gate 36: **OPEN** — public hostname/reverse proxy/WSS certificate lifecycle, live Firebase, production browser and Android WebView/network-handover acceptance remain unproven. Series/Origin ticket binding remains a threat-model item.
- Real TLS fixture covers trusted CA, wrong CA, hostname mismatch, plaintext downgrade rejection and shared-guard ticket/lease operations; CI-only evidence.

### Technical indicator ledger — unchanged implementation status
SMA20 🟨 foundation (first index 19); EMA20 🟨 SMA-seeded alpha 2/21 (first index 19); RSI14 Wilder 🟨 (first index 14); MACD12/26/9 🟨 (MACD index 25, signal/histogram index 33); Bollinger20,2 🟨 (first index 19); Shared Indicator Hook 🟨 backend alignment only; Footprint 🟧 synthetic educational accumulator and reference-gated; Heatmap 🟥 not implemented; Liquidation Maps 🟥 not implemented. No indicator code/test changed, so no implementation credit.

Preserve warm-up nulls, candle alignment, no future-candle repaint, stale clearing on identity/timeframe changes and standard candle spacing while Footprint is OFF. Footprint/Heatmap visual work remains gated on user reference images and reviewed blueprint.

### Project progress and IP3S
- Stage 1: 30/40 = **75% provisional**. Stages 2–6 NOT SCORED. Gate 10 = 0/10 formally closed. Overall project = **NOT SCORED** because approved stage weights/denominator do not exist.
- **IP3S Batch 62J-132: 67/100** (cycle quality only): engineering delta 0/25; exact-baseline CI 20/20; blocker/evidence reduction 12/20; documentation 20/20; ZERO COST/scope integrity 15/15. Not overall completion.
- ZERO COST, docs/evidence only; no runtime/test source, no deployment, no paid services, no secrets, no device/Termux and no `main` changes.

## Batch 62J-131 — WebSocket replica recovery, exact-head CI and project progress (22 November 2026)

**Verified branch HEAD:** `5be3cff9c19064cbcc9ad686aaf359efb4e5c03d` on `phase-2/market-data-foundation`.

**Exact-head CI — all SUCCESS:**
- Automated Tests [44989326413](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326413)
- CodeQL [44989326466](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326466)
- Full Git History Secret Audit [44989326442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44989326442)

### New source-to-test acceptance evidence

- Publisher: 21 named tests cover deterministic cursor IDs, canonical payloads, ambiguous XADD/lost-reply recovery, conflict rejection, checkpoint fencing, retention and snapshot rebase. The publisher advances its durable checkpoint only after confirmed append or exact read-back.
- Consumer: 20 named tests cover SQLite apply-before-ACK, callback retry/idempotence, own-pending-first recovery, XAUTOCLAIM, independent gateway groups, multi-process broadcast, lease-loss-before-ACK, ACL separation and snapshot-generation convergence.
- Worker: 5 tests cover bounded retry/backoff, terminal resnapshot and ownership-loss behavior, and bounded shutdown.
- Replay: 11 tests cover global cursor scanning, fixed replica watermark, history gaps, retention/cursor-ahead, series validation and bounded all-or-resnapshot behavior.
- Stream hub: 10 tests cover atomic snapshot/live boundary, exact-series isolation, slow-consumer resnapshot and replay merge.
- Browser supervisor: 22 tests cover ticket/token retries, bounded reconnect, cursor replay, sequence-gap resnapshot, terminal auth/entitlement/policy rejection and close/stop races.
- A real TCP-path interruption test launches two ASGI gateway processes behind independent fault proxies, severs their Redis TCP paths, rejects reconnects during outage, restores connectivity, and verifies both clients receive the same cursor and both replica checkpoints converge. This is CI-local/ephemeral evidence, not public WSS or owner-host acceptance.

### Production boundary

Gate 25 remains OPEN: the installer is owner-supplied; its digest is format-checked and propagated but not anchored in the durable replica checkpoint. Authenticated owner-host snapshot transfer/receipts, Redis TLS/ACL/persistence/restart/failover remain unproven.

Gate 36 remains OPEN: ticket auth, series authorization, reconnect/replay and local TCP fault recovery are covered in repository tests. Public hostname/reverse proxy/TLS, live Firebase, real browser production session, Android WebView lifecycle and real public network handover remain unproven. Series/Origin ticket binding remains a threat-model decision, not an assumed defect.

### Indicator ledger

No indicator source/test changed; no implementation credit:
- SMA20 🟨 foundation, first valid index 19.
- EMA20 🟨 SMA-seeded, alpha 2/21, first valid index 19.
- RSI14 Wilder 🟨 foundation, first valid index 14.
- MACD12/26/9 🟨 foundation, MACD index 25; signal/histogram index 33.
- Bollinger20,2 🟨 foundation, first valid index 19.
- Shared Indicator Hook 🟨 backend snapshot/alignment foundation, not chart-integrated.
- Footprint 🟧 synthetic educational only; reference-image and reviewed-blueprint gate.
- Heatmap 🟥 not implemented.
- Liquidation Maps 🟥 not implemented.

Preserve warm-up nulls, candle-index alignment, no future-candle repaint, stale clearing on identity/timeframe changes and Footprint OFF normal candle spacing. Do not assign aggregate indicator percentage without approved weights/denominator.

### Project progress

Stage 1 = 30/40 = **75% provisional**. Stage 2–6 remain NOT SCORED/not officially opened. Gate 10 = **0/10 formally closed**. Overall project = **NOT SCORED** until six-stage weights and denominator are approved.

### IP3S — Indicator Proses Peningkatan Proyek Signifikan

Batch 62J-131 = **61/100** (cycle delivery quality only): engineering delta 0/25; exact-head CI 20/20; blocker reduction 8/20; canonical documentation 18/20; scope/cost integrity 15/15. This is not project completion.

**ZERO COST:** documentation-only; no runtime/test change, paid resource, deployment, credential, device/Termux work or main-branch change.

Full report: [WORK_CYCLE_2026-11-22_BATCH62J131_WEBSOCKET_REPLICA_ACCEPTANCE_IP3S.md](WORK_CYCLE_2026-11-22_BATCH62J131_WEBSOCKET_REPLICA_ACCEPTANCE_IP3S.md).

---

## Batch 62J-125 — WebSocket test-evidence mapping and production acceptance gap review (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Reviewed documentation/source baseline:** 4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d  
**CI on this baseline:** Automated Tests run [44986546422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546422), CodeQL [44986546414](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546414), and Full Git History Secret Audit [44986546413](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986546413) all SUCCESS on exact SHA `4cb91f518b14cff2b6d7ee1af3c53ed836dd6b5d`.

### New source/test evidence mapped

- Redis ticket issuance stores only a SHA-256 digest-keyed ticket record with account subject and purpose, 90-second TTL and create-only `SET NX`. Lua consume performs GET+DEL atomically. Tests cover digest-keying, subject binding, exact TTL, malformed/corrupt/wrong-purpose rejection, one-use consume, Redis TTL/consume integration, and a multi-process ticket+account-lease test.
- HTTPS ticket endpoint requires a verified principal and returns ticket, expiry and purpose. WebSocket handshake rejects disallowed non-empty Origin, consumes ticket before accepting its subject as principal, and applies separate exact-series/canonical-instrument entitlement authorization. Ticket does not itself bind the requested series or Origin; retain this as a threat-model review item.
- Firebase verifier tests require revoked-token checking and validate subject/claims using test doubles. These are not live Firebase-project credential, revocation, entitlement grant/revoke/renew E2E tests.
- Redis gateway tests verify snapshot installation precedes Redis client construction, installed source/generation/high-water cursor/hash match the durable local checkpoint, source mismatch fails before Redis construction, and production plaintext Redis is rejected. The callback is still owner-supplied; repository tests do not authenticate remote transfer receipts or prove independent gateway receipt custody.
- Replay tests verify global cursor advancement across unrelated series, missing cursor/history-gap fail-closed behavior, fixed checkpoint watermark, retention expiry/cursor-ahead rejection, and bounded scan/event limits with resnapshot response.
- Browser WebSocket tests cover ticket auth, exact-series subscribe, snapshot/update, durable cursor replay before live updates, renewal acknowledgement, heartbeat/error cleanup and reconnect supervisor recovery. These are simulated browser-socket tests, not public reverse-proxy or real browser/network deployment evidence.
- Server source checks Origin allowlist, performs periodic entitlement recheck and Redis lease renewal, and closes fail-closed on Redis/lease failure. Backend tests cover Redis outage and lease renewal failure. CI Redis is ephemeral.
- Android host preflight and immutable preview-publisher tests run in CI; they do not constitute Android device/WebView foreground-background, process-death, network handover or reconnect acceptance.

### Acceptance status — unchanged

Gate 25 remains OPEN pending owner-host snapshot transport authentication, independently authenticated per-gateway installation receipts, byte/hash custody and exact generation/high-water alignment under real Redis persistence/restart/failover.

Gate 36 remains OPEN pending verified public HTTPS/WSS endpoint, reverse proxy/TLS, real Firebase project, browser and Android WebView lifecycle tests, reconnect/replay/resnapshot and duplicate suppression across real network interruption, plus operator logs/alerts. Subject/purpose ticket binding and separate series authorization remain as implemented; adding series/Origin into ticket claims is a threat-model decision requiring explicit design review, not an assumed code change.

Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. CI/source tests do not close production owner-host gates.

### Indicator reconciliation — no implementation credit

No indicator implementation or test changed. Canonical statuses remain:
- SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2, and Shared Indicator Hook: 🟨 foundation, not fully chart-integrated.
- Footprint: 🟧 synthetic educational accumulator only; visual implementation waits for user reference image(s) and reviewed blueprint.
- Heatmap and Liquidation Maps: 🟥 not implemented.

Warm-up null semantics, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF normal candle spacing remain requirements. No aggregate percentage is assigned without approved weights/denominator.

### Cost and scope

ZERO COST. No source changes, external services, paid hosting, domains, deployment, cloud resource, account, production credentials, Android device action or Termux work. `main` untouched. This batch is documentation-only.

---

## Batch 62J-124 — exact-head CI, SQLite contention and WebSocket acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact source/test HEAD:** 332fd0dacdcd383a27744ea4b9f76d7cbe418cdc  
**Automated Tests #1962 [run 44986046696](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696): SUCCESS**; **CodeQL [run 44986046674](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046674): SUCCESS**; **Full Git History Secret Audit [run 44986046694](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046694): SUCCESS**. All three workflows target the same exact SHA.

### Exact-head CI and artifact evidence
- Automated Tests job completed successfully: frontend dependency audit/tests/build and bundle secret scans; Android host preflight and preview publisher tests; backend dependency installation and tests; isolated Redis TLS CA/hostname fixture; synthetic SQLite outbox and metrics benchmarks; backend container build; shared-Redis-guard/persistent-CI-volume smoke; Trivy scan/report; dependency audit enforcement. All 30 main job steps completed successfully.
- Synthetic metrics artifact [14739229002](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739229002) was downloaded and independently inspected. Full 899 logical-series envelope; 1 worker: 32/32 flushes, 0 retries, p95 flush 8.19 ms, SQLite integrity ok; 4 threads: 128/128, 2 retries, p95 flush 110.61 ms, p95 writer-lock wait 79.22 ms; 16 simultaneous threads: 512/512, 82 retries, p95 flush 371.19 ms, p95 writer-lock wait 314.04 ms; 4 independent processes: 128/128, 2 retries, p95 flush 84.23 ms, integrity ok. All synthetic flushes succeeded and integrity was ok. The 16-thread case still shows material lock contention; jitter improved the exact benchmark compared with the immediately preceding run's 187 retries / 627.74 ms p95 flush, but the runs are CI-runner-specific and not a controlled performance comparison or production SLO.
- Metrics artifact records synthetic operational counters only, not market data. It explicitly excludes production persistent-volume and multi-host claims. Do not infer production capacity or supported worker count from it.
- Trivy artifact [14739587046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739587046) was inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, linux/amd64, digest sha256:274264c0115b75b9c538a9c383140f393c9c8545eb73b4b1d48269384ab240ff, size 571,353,088 bytes. The report lists zero vulnerabilities and zero misconfigurations in the scanned Alpine OS and Python package result groups. This is point-in-time scanner evidence for this exact amd64 image/database only; it is not an ongoing guarantee or ARM64 evidence.
- Synthetic outbox artifact [14739104428](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986046696/artifacts/14739104428) was generated by CI but is not used here to make additional performance claims.

### Source change and scope boundary
Commit 332fd0dacdcd383a27744ea4b9f76d7cbe418cdc changes exactly backend/app/metrics_collector.py and backend/tests/test_metrics_collector.py. It raises bounded BEGIN-lock retry attempts to 16 and adds randomized backoff to desynchronize concurrent SQLite writers. The exact-head backend tests and synthetic benchmark passed. This is a metrics-collector resilience change only: no WebSocket transport, Firebase authentication, ticket, Redis market-data publisher/consumer, snapshot/replay, cursor, browser client, Android client, indicator formula, hook, renderer or indicator test was changed.

### WebSocket acceptance — repository evidence versus production evidence
- The source publisher and gateway replica runtime factories remain separate injected ASGI roles. The source publisher checkpoint/outbox and gateway replica consumer remain repository-side components; the gateway worker uses an ownership lease, sequential consumption, bounded retry on callback errors, and terminal resnapshot-required/ownership-lost states.
- The gateway snapshot installer is an owner-supplied authenticated transfer callback. The code validates installed metadata against its durable local checkpoint before Redis consumer construction; this does not independently authenticate remote snapshot bytes or receipts. The source activation verifier similarly remains an owner-supplied trust boundary.
- WebSocket tickets are short-lived (90 seconds) and single-use in the reviewed ticket path. Firebase ID-token exchange is over HTTPS; the Firebase token is not placed in a WSS URL or raw authentication frame. The ticket currently binds account subject and purpose; canonical series and Origin are not embedded in the ticket itself. Series authorization is performed separately. Retain series/Origin binding as an explicit threat-model and owner-review item before production exposure, not as a claim that this commit fixed it.
- Production gates remain unclosed: owner-host secret injection/rotation and redaction; real Firebase project token and entitlement E2E; owner-host Redis TLS/CA/hostname/ACL/persistence/failover and authenticated snapshot installation receipts; live database backup/restore; encrypted off-host backup/key custody; persistent volume ownership/restart/disk-pressure; verified public hostname/TLS; public HTTPS ticket exchange and WSS reverse proxy with real browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression evidence; real dashboards/retention/alerts and human acknowledgement.
- **Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional.** CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. No stage transition is authorized.

### Indicator progress reconciliation — no credit
No indicator source or tests changed in this commit. Keep the canonical matrix unchanged:
- SMA20 — 🟨 foundation; 20-close mean, first valid index 19.
- EMA20 — 🟨 foundation; SMA-seeded EMA, alpha 2/21, first valid index 19.
- RSI14 Wilder — 🟨 foundation; 14 close changes, first valid index 14.
- MACD12/26/9 — 🟨 foundation; MACD first valid index 25; signal/histogram index 33.
- Bollinger20,2 — 🟨 foundation; 20-close mean ±2 population standard deviations, first valid index 19.
- Shared Indicator Hook — 🟨 foundation; validated backend snapshot and candle-index-aligned calculation output, not chart-integrated.
- Footprint — 🟧 synthetic educational accumulator only; visual work remains blocked on user reference image(s) and reviewed blueprint.
- Heatmap — 🟥 not implemented.
- Liquidation Maps — 🟥 not implemented.

Warm-up values remain null, never zero; outputs align to source candle indices; no future-candle repaint; identity/timeframe changes clear stale series. Footprint OFF must preserve standard candlestick spacing; only explicit ON uses spaced cluster layout. No aggregate indicator percentage without approved weights and denominator. CI, benchmarks and documentation award zero indicator implementation progress.

### Cost and change boundary
ZERO COST maintained: no paid service, hosting, deployment, domain, cloud resource, account, production credential, device/Termux operation or external endpoint was created. No main-branch change. This batch is documentation-only after the already-tested source commit.

**Next safe sequence:** preserve this green exact-head CI; continue the read-only WebSocket owner-evidence audit and ARM64 build feasibility review without provisioning; keep all owner-host production gates open until real evidence and authorized adult account-owner review exist. Do not respond to remaining SQLite contention by blindly increasing retry limits; a single-writer/queue design would require a separate scoped architecture decision and measured acceptance criteria.

---

# WebSocket production wiring audit — Batch 62J-123

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
## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).

## Batch 62J-119 — WebSocket acceptance and indicator ledger exact-head reconciliation (22 November 2026)

**Verified parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750` on `phase-2/market-data-foundation`. This checkpoint was created only after all three workflows for that exact SHA completed successfully.

**Exact-head CI:**
- Automated Tests #1954 — [run 44982930281](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281): **SUCCESS**. Frontend unit tests/build, backend tests, isolated Redis TLS/CA/hostname enforcement fixture, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke test using shared Redis guard and persistent volume, Trivy image scan/report export/upload, and dependency-audit enforcement all completed successfully.
- CodeQL [run 44982930379](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930379): **SUCCESS**.
- Full Git History Secret Audit [run 44982930324](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930324): **SUCCESS**.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281/artifacts/14739265202). The workflow completed the configured HIGH/CRITICAL scan and uploaded the JSON report. Do not infer a zero-vulnerability result without reviewing the artifact contents.

These results verify the repository workflow and its CI service topology only. The CI Redis instance, ephemeral runner volume, and container smoke are not the intended OCI host or production Redis service.

**WebSocket repository evidence:** source-side publisher and gateway runtime factories, durable SQLite outbox, atomic snapshot/watermark primitives, Redis Streams publisher/consumer, per-gateway consumer groups, replica snapshot installation checks, fail-closed runtime construction, ticket authentication/renewal, reconnect/replay and client failure-matrix tests are present in the audited source. The latest CI validates the covered repository paths. The default FastAPI app intentionally does not invent owner-specific publisher/replica factories or trust snapshot receipts; those must be injected from a verified owner-controlled host setup.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS endpoint, production Firebase token/entitlement evidence, owner-host Redis TLS/ACL/persistence/rotation/failover, authenticated global snapshot manifest and per-gateway installation receipts, or real browser + Android WebView lifecycle evidence has been supplied. A successful CI container smoke cannot close those host/client gates.

**ZERO COST boundary:** no OCI account or resource was created, no deployment or public endpoint was started, no paid resource or trial-credit dependency was introduced, no credentials were requested, no device/Termux operation occurred, and `main` was not touched. OCI remains a conditional candidate subject to actual Always Free eligibility and adult account-owner approval.

**Indicator disposition — no source change and no progress credit:** the source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains the calculation baseline. The comparison through parent HEAD `6d5a05d611615972d5826002442a65e74c179750` is documentation-only; no indicator formula, hook, chart renderer, UI, or indicator test source changed. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formula definitions, warm-up indices, numerical safeguards, data identity, stale-series invariants, UI acceptance and reference prerequisites remain in the canonical audit and ledger. Aggregate indicator percentage remains unscored without approved weights and denominator.

**Project accounting:** Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI or documentation-only checkpoint. No progress is awarded from CI alone.

**Next zero-cost sequence:** preserve the green exact-head CI; finish ARM64 build/configuration readiness without provisioning; have the adult account owner verify OCI eligibility, capacity and all possible charges; only then, with explicit authorization, consider an Always Free-only host. Collect actual host and client evidence for Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Close Gate 10 only after evidence review and operator sign-off.

---

## Batch 62J-117 — exact-head CI verification (22 November 2026)

At exact branch HEAD e76b6cd6c8f7380e5a10a7d4707028fa7da78a02, Automated Tests [run #1952](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844), CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808), and Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851) all completed **SUCCESS**. The Automated Tests workflow reports all 61 steps successful, including frontend/backend tests, backend container build, isolated Redis TLS/CA/hostname fixture, persistent-volume Redis restart smoke, container scan/report and dependency audits. This verifies repository CI only; it does not close external production gates.

The repository-side client matrix remains 17 WebSocket transport tests, 7 HTTPS ticket-exchange tests and 21 stream-supervisor tests. Real Firebase token/entitlement cases (Gate 20), owner-host Redis TLS/ACL/persistence/recovery and snapshot installation receipts (Gate 25), and public HTTPS/WSS reverse-proxy plus real browser/Android WebView lifecycle tests (Gate 36) remain open. No public host or endpoint is verified. Keep ZERO COST; no OCI provisioning, deployment, production credentials or main-branch changes.

The indicator audit is unchanged because the comparison from its source/test baseline to this HEAD contains documentation-only changes. No indicator credit is awarded by this WebSocket CI pass. See the indicator audit and Batch 62J-117 reconciliation.

---

## Batch 62J-116 — current WebSocket acceptance evidence (22 November 2026)

At baseline `a3febdb3f7d3dd233f1cfeb8e482e986e56348e1`, exact-head CI is green: Automated Tests [44981340874](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340874), CodeQL [44981340863](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340863), and Full Git History Secret Audit [44981341220](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981341220). Frontend 29 test files passed; backend 1,294 passed and 1 skipped; all 36 automated workflow steps completed, including container and CI Redis persistence smoke.

The client suite includes 17 transport tests, 7 ticket-exchange tests, and 21 supervisor/reconnect tests. These prove the covered repository scenarios only. They do not prove public WSS, real Firebase project, owner-host Redis, global snapshot receipts, or browser/Android WebView acceptance. The current external evidence checklist is in [Batch 62J-116](WORK_CYCLE_2026-11-22_BATCH62J116_WEBSOCKET_ACCEPTANCE_RECONCILIATION.md).

---

## Batch 62J-94–96 — WebSocket data path unchanged (21 November 2026)

Gate 38 SQLite tail-latency instrumentation, benchmark analysis and the rejected/reverted retry-jitter experiment did not modify WebSocket transport, authentication, ticket exchange, snapshot/replay, cursor ordering, publisher/replica lifecycle, Redis ACL behavior or market-data payloads.

Exact source/test HEAD `2eb3181b21b7f2aa3a53c8c293ab6d27ec959b75` passed Automated Tests [44913778296](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778296), CodeQL [44913778266](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778266) and Full Git History Secret Audit [44913778270](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778270).

WebSocket repository-side automated failure-matrix scope remains previously implemented and CI-verified. Production acceptance remains open pending verified global snapshot bytes and authenticated installation receipts for every required gateway; owner-host Redis TLS/ACL credentials, secret rotation, persistence/failover/retention; public HTTPS/WSS proxy and certificate renewal; and real browser plus Android WebView acceptance. No public production endpoint or production Redis host is available in this checkpoint.

---

## Batch 62J-87 — Gate 38 writer-lock correction; WebSocket unchanged (21 November 2026)

The 16-worker SQLite benchmark exposed lock contention at `BEGIN IMMEDIATE`. Gate 38 now retries bounded writer-lock acquisition and records retry counts. No WebSocket transport, authentication, snapshot/replay, cursor, gateway or Redis code changed. Production WSS acceptance remains pending real owner-host and client evidence.

---

## Batch 62J-86 — telemetry bootstrap contention fix; WebSocket data path unchanged (21 November 2026)

The Gate 38 benchmark exposed SQLite schema-initialization contention while separate collector instances opened the same local database. The collector now serializes schema initialization within each instance and retries bounded SQLite lock failures; the benchmark models separate collector instances per worker. The new exact-head CI is pending.

No WebSocket publisher, gateway consumer, auth, replay, snapshot, cursor or market-data payload code changed. The WebSocket repository-side automated failure matrix remains previously verified for its defined scope; production acceptance still requires owner-host snapshot/Redis/TLS/proxy/browser/Android evidence.

---

## Batch 62J-85 — Gate 38 benchmark expansion; WebSocket scope unchanged (21 November 2026)

The latest Gate 38 work expands the synthetic SQLite metrics benchmark from 12 to the full 899 declared logical series and adds a transaction write-rejection rollback/retry test. It does not modify WebSocket publisher, gateway consumer, replay, snapshot, authentication, cursor or payload code. Exact-head CI is pending; no pass is claimed yet.

**WebSocket repository status:** the defined automated protocol/failure matrix remains implemented and previously CI-verified. **Production acceptance remains open** until the exact global snapshot bytes are SHA-256 verified and authenticated installation receipts are confirmed for every required gateway; owner-host dedicated Redis TLS/ACL, persistence/failover/retention and secret lifecycle are verified; public HTTPS/WSS proxy/certificate/renewal are operational; and real browser plus Android WebView acceptance is recorded. The default ASGI app remains opt-in for publisher/replica roles. No production host or endpoint is present in this checkpoint.

---

## Batch 62J-84 — Gate 38 SQLite failure-path and worker-load evidence (21 November 2026)

- Exact source/test HEAD `92119a8dc05690e6492aab160662c9e36c839cad`: Automated Tests [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637) SUCCESS (35/35 steps; 1,265 backend tests), CodeQL [44900892567](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892567) SUCCESS, Full Git History Secret Audit [44900892606](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892606) SUCCESS.
- Added tests for concurrent collector workers, busy-lock rollback/recovery and corrupt-database rejection. Added a local-only synthetic benchmark for 1/4/16 Python worker threads; CI artifact records latency and database/WAL/SHM size.
- Initial low-cardinality benchmark used 12 logical series. At 16 workers/512 flushes, p99 was 78.978ms, retry count zero and peak total DB+WAL+SHM was 4,284,304 bytes. This is not full 899-series capacity evidence or an owner-host byte budget.
- No WebSocket protocol, auth, replay, snapshot, market-data payload or Redis guard behavior changed. No public WSS or production acceptance is claimed.
- Gate 38 remains 🟧 OPEN pending full-cardinality/process-level benchmark, disk-full/read-only/app-isolation tests and owner-host acceptance. Gate 10 remains 0/10 formally closed.
- Indicator implementation is unchanged; no indicator progress credit is awarded. ZERO COST; no deploy, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-83 — Gate 38 telemetry hardening (21 November 2026)

- Pre-change exact HEAD `b1e21f552182a720400cd9a2d276705834a41358`: Automated Tests 44898947136 SUCCESS (33/33 steps); CodeQL 44898947150 SUCCESS; Full Git History Secret Audit 44898947186 SUCCESS.
- Collector hardening adds bounded stale-worker checkpoint eviction, seven-day retired-worker tombstones (4096 maximum) to reject a resumed evicted worker ID, seven-day read-side bucket filtering, explicit aggregate-row eviction counters, and worker timestamp monotonicity checks.
- Added regression coverage for worker-generation saturation, tombstone rejection, 16-worker live limit, retention filtering, and timestamp regression. Exact-head CI for source commit `e98bf7acda841ae4045d258b6d3b2fe774205239` passed: Automated Tests 44899788672, CodeQL 44899788812 and Full Git History Secret Audit 44899788701. Host acceptance remains open.
- WebSocket lifecycle accounting and transport semantics remain unchanged. The metrics collector is best-effort same-host telemetry only; production WSS remains unaccepted pending actual host/proxy/Redis/browser/Android evidence.
- No deployment, paid provider, Termux, production credential or `main` operation.

---



## Batch 62J-82 — exact-head CI and capacity-model correction (21 November 2026)

- Exact HEAD `c3577d7174ce5873502ebd8df7a57f27447a296b`: Automated Tests 44897164887 SUCCESS; CodeQL 44897164916 SUCCESS; Full Git History Secret Audit 44897164908 SUCCESS.
- Automated Tests completed backend container build, Redis persistent-volume smoke, Trivy scan and vulnerability report export/upload, in addition to frontend/backend tests, SQLite outbox benchmark and dependency audits.
- Gate 38 blueprint now explicitly states the nominal crash-loss window of up to one 15-second flush interval plus scheduler delay. Transactional checkpoints prevent replay of committed deltas but cannot recover unflushed in-memory increments. This is telemetry, not financial accounting.
- Series capacity is bounded from source contracts: 127 method/route pairs × 6 status classes = 762 request series; 127 latency series; conservative total planning ceiling 900 series per 15-minute bucket. 672 buckets represent seven days. Aggregate planning bound 604,800 rows; 16 workers × 900 checkpoints = 14,400; plus 16 heartbeats. Initial logical-row ceiling: 650,000. SQLite byte cap remains benchmark-derived.
- The 1,500x operation estimate is explicitly a comparison with hypothetical per-request persistence, not a measured improvement over current in-memory counters.
- No runtime source changed. Gate 38 remains 🟧 OPEN pending explicit blueprint approval, implementation, exact-head CI, measured byte budget and owner-host/operator acceptance.
- WebSocket send-confirmed lifecycle accounting remains unchanged and CI-verified. Production WSS acceptance still requires host-side snapshot/Redis/TLS/proxy/browser/Android evidence.
- ZERO COST; no deployment, production credentials, Redis ACL change, Termux, main modification or paid provider.

---
## Batch 62J-81 — Gate 38 zero-cost collector design (21 November 2026)

- Exact-head baseline 3eadda21f795abe5af195eedf0c81727d31f6436 rechecked: Automated Tests run 44895224507 SUCCESS; CodeQL run 44895224465 SUCCESS for JS/TS and Python; full Git-history secret audit run 44895224498 SUCCESS.
- Current source still has bounded process-local request and WebSocket metrics. The protected endpoint remains token-gated; the WebSocket middleware records lifecycle metadata only.
- The existing Redis client is coupled to shared security guards. It is not reused for telemetry because doing so couples monitoring availability to auth/rate-limit operations and could exceed its ACL scope.
- The existing SQLite incident journal is not a time-series collector. The market-data registry database is not used for high-frequency metrics writes.
- Added GATE38_METRICS_COLLECTOR_BLUEPRINT.md: same-host multi-worker aggregation using a dedicated SQLite metrics DB on a supported local persistent volume; 15-second snapshots; transactional deltas; 15-minute buckets; 90-second worker-heartbeat expiry; 7-day bounded retention; hard worker/cardinality/payload/row/disk limits.
- Load estimate at 100 requests/s: 8,640,000 request-level write opportunities/day/worker versus 5,760 periodic flushes/day/worker, a 1,500x operation-count reduction. This is an estimate, not a benchmark.
- This is a documentation/design checkpoint only. Source implementation requires explicit blueprint review under the project's major-implementation rule.
- Gate 38 remains 🟧 OPEN pending implementation, tests, exact-head CI, host volume/access/retention/disk-pressure evidence and independent operator notification/recovery acceptance.
- No indicator code changed and no indicator progress is awarded. Complete formulas, warm-up indices, remaining renderer work, and Footprint/Heatmap visual gates remain in INDICATOR_PROGRESS_LEDGER.md.
- ZERO COST; no deployment, production credentials, Redis ACL change, main modification, Termux or device operation.

---

## Batch 62J-80 — send-confirmed WebSocket lifecycle metrics

**Reviewed branch:** phase-2/market-data-foundation  
**Change scope:** backend/app/observability.py and backend/tests/test_observability.py

The observer now updates accepted-handshake and close-code metrics only after the downstream ASGI send call returns successfully. A failed send no longer produces false-positive acceptance/close telemetry. The middleware finally block still finalizes the connection, decrements the active count and records completion even when the application/transport raises.

Regression cases cover failure at the accept frame and failure at the close frame after a successful accept. These cases assert active=0 and completed=1, with accepted and close-class counters reflecting only successful downstream sends.

No WebSocket payload/protocol/auth/replay/snapshot behavior changed. Gate 38 remains 🟧 OPEN: metrics are process-local, not centrally aggregated or durably retained. The production acceptance boundary described below remains unchanged.

---

# WebSocket Production Wiring Audit

**Audit date:** 21 November 2026  
**Active branch:** `phase-2/market-data-foundation`  
**Source checkpoint reviewed:** `da9b2ad025ac5c49f75c95dbdd5f516573107f87`  
**Scope:** source SQLite outbox -> Redis Streams -> gateway replica -> authenticated WebSocket

## Executive result

The initial audit found that the repository contained substantial publisher and consumer primitives but lacked a source publisher lifecycle hook. Batch 62J-69 has since implemented that lifecycle hook and exact runtime-binding checks. The production data path is still not activated by the module-level default ASGI app and is not host-accepted; do not deploy this checkpoint as proof of live fan-out.

The initial audit found two independent integration gaps:

1. **Initial finding — source publisher lifecycle absent (superseded by Batch 62J-69).** `backend/app/ohlcv_redis_publisher.py` implements `SQLiteOhlcvPublisherCheckpoint`, `RedisOhlcvStreamAppender`, and `RedisOhlcvPublisher.publish_available()`. The publisher class explicitly documents that it is not connected to FastAPI startup. `backend/app/main.py` imports the gateway consumer worker but not the source publisher. Its `publish_persisted_bar()` reads the durable outbox event and calls only `stream_hub.publish()`; it does not append that event to Redis Streams.
2. **Gateway runtime remains injection-only.** `create_app()` accepts an optional `replica_runtime_factory`; the module-level `app = create_app()` supplies none. Therefore the default ASGI entry point starts the provider/local-SQLite path, not the replica consumer path. A gateway host needs an explicit, verified factory and a preinstalled replica snapshot.

These gaps are separate: wiring the source publisher does not automatically provision gateway snapshots or activate the replica runtime.

## Existing verified components

- Durable source OHLCV outbox with contiguous global cursors.
- SQLite publisher checkpoint with lease owner/epoch fencing and compare-and-swap cursor advancement.
- Redis appender with deterministic stream IDs (`<cursor>-0`) and exact-ID read-back after ambiguous XADD replies.
- Bounded publisher batches and explicit fresh-snapshot requirement when source outbox retention overtakes the publisher cursor.
- Atomic global snapshot export/verification and replica snapshot installation.
- Independent per-gateway Redis consumer groups, apply-before-ACK, durable local SQLite replica checkpoint, replay, ownership lease and resnapshot-required handling.
- Replica hydration and atomic snapshot-to-live subscription bridge.
- FastAPI gateway worker startup validates snapshot hydration, ownership lease and Redis consumer-group readiness before accepting traffic.

## Required implementation sequence

### WS-PUB — remaining host-side activation

The FastAPI lifecycle hook is implemented and CI-verified. Remaining activation requirements are owner-host tasks:

- Inject a source-only `publisher_runtime_factory`; the default module-level app deliberately remains disabled.
- Build the publisher against the exact `SQLiteOhlcvStore` instance supplied by FastAPI. Runtime startup rejects a different store, checkpoint, source ID, Redis client or stream key.
- Require a pre-existing checkpoint or initialize it only from the exact global snapshot watermark already installed on every target gateway. Never infer or invent the cursor.
- Use a dedicated least-privilege publisher ACL client and finite connect/socket timeouts; production must use `rediss://`.
- Verify the owner-host durable volume, Redis ACL and snapshot generation before enabling the feature.
- The sanitized lifecycle state is held in application state; it is not a public status route and does not expose credentials or exception messages.

### WS-SNAP — snapshot generation coordination

Do not initialize the publisher checkpoint from an arbitrary current cursor. The checkpoint watermark must match the exact global snapshot generation installed on every target gateway. Snapshot export, integrity verification, distribution, installation, generation activation, publisher checkpoint initialization/rebase and rollback need an explicit ordered operator workflow.

### WS-GW — gateway runtime configuration

Provide a host-injected gateway runtime factory that:
- Opens a dedicated least-privilege Redis client.
- Opens the persistent local replica SQLite path.
- Requires a verified snapshot before constructing the consumer.
- Uses the generation-scoped group and owner lease.
- Closes resources safely on every startup-failure and shutdown path.

Keep source publisher and gateway consumer as separate application roles unless a reviewed architecture explicitly proves a combined role safe.

## Acceptance matrix

| Test | Required evidence |
|---|---|
| Publisher bootstrap | Missing checkpoint fails closed; valid snapshot checkpoint starts |
| Event relay | Source outbox cursor N becomes exactly Redis Stream ID N-0 |
| Ambiguous XADD | Lost reply is resolved by exact-ID read-back without double append |
| Redis outage | Source commit remains durable; publisher retries without advancing cursor |
| Retention gap | Publisher enters resnapshot-required; no cursor is skipped |
| Wake-up and backlog | New bars wake relay; process restart drains retained backlog |
| Shutdown | Publisher task stops and dedicated Redis client closes |
| Snapshot alignment | Publisher cursor equals the installed gateway snapshot watermark |
| Two gateways | Both independent replica groups receive the same ordered source events |
| Replay continuity | Restart/reconnect resumes from durable cursors without gaps or duplicate client delivery |
| Host acceptance | Real TLS/ACL, persistent volumes, public WSS, browser and Android WebView verified |

## Safety and cost constraints

- No Vercel or Cloudflare deployment is required for repository-side implementation or CI.
- No paid Redis service is assumed. Use only an already available, owner-controlled Redis endpoint; otherwise keep the relay disabled.
- No production credentials, snapshot files or encryption keys belong in Git or chat.
- Do not run a production host migration or alter persistent data as part of a code-only change.
- Do not modify `main`.
- Do not mark host-only gates green based on source tests or CI.

## Current project accounting

- Gate 10: 0/10 formally closed.
- Gate 8: yellow host-verification-only; all other Gate 10 entries remain open.
- Stage 1: 30/40 criteria = 300/400 ticks = 75% provisional.
- Overall project and aggregate indicator percentages: unscored pending approved weights and denominators.
- Indicator formulas/foundations remain unchanged by this audit. Existing indicator implementation status remains as documented in `PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

## Audit disposition

**WebSocket repository primitives:** substantially implemented and CI-verified for the defined automated failure matrix.  
**Source-to-Redis publisher lifecycle hook:** implemented and exact-head CI-verified; source runtime factory, snapshot watermark alignment, dedicated Redis ACL and host activation remain 🟨🟩 pending.  
**Redis-to-gateway replica integration:** opt-in factory exists; default ASGI entry point is not wired.  
**Production acceptance:** open; public WSS, production Redis TLS/ACL topology, snapshot distribution/rotation/rollback, browser and Android WebView acceptance remain unverified.  
**Initial audit code changes:** none. Batch 62J-69 adds the subsequent FastAPI publisher lifecycle and runtime-binding validation.


## Batch 62J-69 — source publisher lifecycle integration (21 November 2026)

**Source change:** FastAPI now accepts a dedicated, owner-injected `publisher_runtime_factory` for the source application role. Lifespan validates that the publisher, dedicated Redis client and exact stream key agree; performs Redis PING before provider ingestion starts; runs bounded synchronous publisher batches through `asyncio.to_thread`; wakes on persisted-bar callbacks; and polls once per second to recover retained backlog after restart. Transient failures use bounded 1–30 second exponential backoff. A typed retention-gap exception transitions the worker to terminal `resnapshot_required` without advancing the checkpoint. Shutdown waits up to 15 seconds and closes the dedicated client only after the publisher task has stopped.

**Role isolation:** one FastAPI app cannot be configured with both source publisher and gateway replica runtime factories. The module-level default app remains publisher-disabled unless its owner explicitly injects a source runtime factory. No Redis URL, credentials, snapshot cursor or snapshot artifact is inferred by application code.

**Host gate:** the source runtime factory must construct `SQLiteOhlcvPublisherCheckpoint` against the durable source database, require an existing checkpoint or initialize it only from the exact global snapshot watermark already installed on every target gateway, and use a dedicated publisher ACL client with finite socket/connect timeouts. The code cannot prove remote snapshot installation; this remains an owner-host prerequisite. Publisher lifecycle wiring is therefore **🟨🟩 HOST-FACTORY / SNAPSHOT VERIFICATION PENDING**, not production-green. Do not enable the source publisher until snapshot and ACL preconditions are satisfied.

**Verification boundary:** lifecycle contract tests cover Redis readiness, task startup, graceful client close, source/gateway role separation and runtime binding mismatch. The runtime also rejects a publisher bound to a different SQLite store or checkpoint/source ID. Exact-head CI on `6f49951c253a7e7b995b4bdd52eba8153edaef77` passed: Automated Tests [44866818528], CodeQL [44866818498] and Full Git History Secret Audit [44866818495] all SUCCESS; frontend 247/247, backend 1,241 passed, and all 33 workflow steps succeeded. Backend container build, Redis ACL/AOF + persistent-volume smoke, container scan and vulnerability-report export also succeeded. No deployment, live Redis connection, production host, Termux command, paid service, or `main` change was performed.



## Batch 62J-70/71 — dedicated source runtime and production transport enforcement

### Source publisher runtime (62J-70)

Added `backend/app/ohlcv_redis_runtime.py`:
- Separate dedicated publisher ACL URL; does not reuse the shared HTTP/WebSocket guard URL.
- Production validation requires `rediss://`, dedicated ACL username/password and database 0.
- Redis client uses 3-second connect timeout, 5-second socket timeout, 15-second health-check interval, TLS certificate-chain verification and hostname verification.
- The durable publisher checkpoint must already exist. The factory never creates an arbitrary cursor.
- Before creating a Redis client, an owner-injected snapshot verifier must prove exact source ID, stream key, generation and cursor equality between the global manifest and one installation receipt per required gateway.
- Missing gateway receipts, duplicate/empty gateway identities, or any generation/cursor/source/stream mismatch fail closed.
- Environment helper remains opt-in; default module-level ASGI app is not silently enabled.

The publisher and gateway ACL command matrices now include `+ping` for their readiness checks. Other command permissions remain separated by role. Tests assert the exact allow-lists.

### Production HTTPS/WSS enforcement (62J-71)

- Production frontend builds reject a plaintext HTTP ticket endpoint before issuing the Firebase bearer request.
- Production frontend builds reject a plaintext `ws://` market-data endpoint before creating the WebSocket.
- HTTPS maps to WSS. Development mode retains its prior HTTP/WS behavior for local work.
- Added frontend regressions for both rejected production plaintext paths.

### Exact-head verification

Source/test HEAD: `5575f5d820dd26d16a7170cb2c55e9c707c2afc1`.

- Automated Tests [44868539276] — SUCCESS; frontend **249/249 across 29 files**, backend **1,246 passed**, all **33/33 workflow steps**.
- CodeQL [44868539309] — SUCCESS.
- Full Git History Secret Audit [44868539423] — SUCCESS.
- Android APK Build (zero-cost CI) [44868539288] — SUCCESS. This confirms build output only, not installation or runtime acceptance on a physical Android device.
- Frontend/backend dependency audits, backend container build, Redis shared-guard/persistent-volume smoke, container scan, vulnerability-report export and artifact upload — SUCCESS.

### Production acceptance boundary

Repository-side source publisher runtime construction and production transport guards are implemented and CI-verified. **Production WebSocket acceptance is not yet complete.** The remaining evidence requires owner-controlled runtime access:
- Actual snapshot manifest and signed/controlled installation receipts for every target gateway.
- Durable source SQLite path, checkpoint watermark and actual gateway replica volumes.
- Live Redis TLS handshake, ACL enforcement, persistence, failover and private network restrictions.
- Owner-host secret injection, rotation and rollback.
- Gateway runtime factory configured on the target host.
- Public HTTPS/WSS reverse proxy, hostname/certificate/renewal.
- Browser end-to-end and actual Android WebView/device acceptance.

The snapshot-verifier callback is a strict contract; the repository cannot probe the user's remote hosts. No host acceptance is inferred from CI. Gate 25 and Gate 36 remain 🟧 OPEN. Source publisher remains 🟨🟩 HOST VERIFICATION PENDING. Gate 8 remains 🟨 HOST VERIFICATION ONLY.

### Indicator and project accounting

No indicator formula, calculation, hook, renderer or chart UI changed. The complete indicator ledger remains in `PROJECT_PROGRESS_INDICATOR_CURRENT.md`:
- SMA20 🟨, first valid candle index 19.
- EMA20 🟨, SMA-seeded with alpha 2/21, first valid index 19.
- RSI14 🟨, Wilder smoothing, first valid index 14.
- MACD12/26/9 🟨, MACD index 25 and signal/histogram index 33.
- Bollinger20,2 🟨, population standard deviation, first valid index 19.
- Shared Indicator Hook 🟨.
- Footprint 🟧 SIMULATED / GATED.
- Heatmap 🟥 NOT IMPLEMENTED.
- Liquidation Maps 🟥 NOT IMPLEMENTED.

Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; Stages 2–6 and overall project percentage remain unscored. ZERO COST; no production deployment, paid service, Termux/device operation, Vercel/Cloudflare operation or `main` change.


## Batch 62J-72 — snapshot artifact digest binding

The source publisher runtime now requires the exact SHA-256 digest returned by the verified global snapshot manifest and requires every gateway installation receipt to bind to that same digest. The runtime rejects malformed/missing digests and any gateway receipt mismatch before creating the Redis client.

The digest contract is grounded in the existing snapshot exporter/verifier:
- `SQLiteOhlcvStore.export_global_snapshot()` writes a SHA-256 digest over the canonical header and every canonical bar record, and returns it with the snapshot generation, source ID and high-water cursor.
- `SQLiteOhlcvStore.verify_global_snapshot()` recomputes the digest from the artifact and validates the manifest digest and row count.
- The host verifier must invoke that verifier on the actual snapshot artifact and authenticate the installation receipt source. It then maps the export/verifier `generation_id`, `cursor`, and `sha256` into the runtime evidence contract (`snapshot_generation`, `snapshot_cursor`, `snapshot_sha256`); each receipt must contain the matching `snapshot_sha256`.

This is stronger artifact identity binding, not proof of remote installation or receipt authenticity. No receipt-signing format or storage backend is invented by this change. Host-side verification remains external.

Regression coverage now includes:
- Missing publisher checkpoint fails before Redis client creation.
- Gateway cursor mismatch fails before Redis client creation.
- Gateway snapshot digest mismatch fails before Redis client creation.
- Malformed manifest digest fails before Redis client creation.
- Matching source, stream, generation, cursor and digest can construct the dedicated TLS client with certificate and hostname verification.

**Gate status:** Gate 25 🟧 OPEN (live Redis TLS/ACL, persistence, failover and credential lifecycle remain unverified). Gate 36 🟧 OPEN (public HTTPS/WSS reverse proxy and browser/Android runtime acceptance remain unverified). Source publisher activation remains 🟨🟩 host-verification pending.


## Batch 62J-74 — exact-head CI acceptance and Redis ACL least-privilege correction

### Exact CI evidence

The Automated Tests workflow completed successfully on head `3e3428910e3226f3d4365808f3a36a3138674231` (run [44874341856](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341856)). Backend pytest reported **1,249 passed in 57.10 seconds**. The new Redis ACL integration test and the existing full publisher/consumer ACL integration test both passed. CodeQL (run [44874341916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341916)) and full Git-history secret audit (run [44874341885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341885)) also succeeded.

The existing CI Docker smoke additionally verified:
- Redis ACL rejects unauthenticated access, wrong passwords and unrelated SET operations.
- Redis AOF data and its ACL file survive a Redis container restart on a named volume.
- The backend returns the expected fail-closed 503 during Redis outage and recovers after Redis returns.
- Non-root application UID/GID, persistent-volume/database ownership, SQLite integrity and backend restart persistence.
- HTTP rate-limit enforcement.
- Backend container image scan and vulnerability-report export/upload succeeded.

This is repository/CI simulation evidence, not production-host acceptance. The Redis AOF/volume smoke is for the shared guard service and does not prove production persistence/failover of the dedicated OHLCV relay stream.

### Redis ACL correction — supersedes Batch 62J-73 SELECT claim

The earlier Batch 62J-73 note incorrectly stated that redis-py needs `+select` when connecting to database 0. The existing real-Redis end-to-end ACL test used a `/0` URL without `+select` and passed. Database 0 is the Redis default; the client does not need a SELECT command to use it.

Batch 62J-74 removes `+select` from both publisher and gateway command allow-lists. The new integration test explicitly verifies:
- Both clients connect through the DB-0 URL and PING successfully.
- Publisher/gateway allowed stream and lease operations work.
- Explicit `SELECT 1` is rejected for both roles.
- Publisher and gateway prohibited commands and out-of-scope key access remain rejected.

This tightens least privilege. URL parsing still rejects non-zero database paths.

### Production boundary and gates

WebSocket E is complete for the defined automated repository failure matrix. Production acceptance still requires owner-controlled evidence for actual global snapshot artifact distribution and authenticated per-gateway receipts, production Redis TLS/ACL topology and secret rotation, dedicated OHLCV stream persistence/failover/retention, public HTTPS/WSS reverse proxy, browser and Android WebView runtime acceptance.

Gate 8 remains 🟨🟩 host-verification-only. Gate 25 and Gate 36 remain 🟧 OPEN; Gates 20, 30, 31, 34, 35, 38 and 39 remain 🟧 OPEN. Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.

See `PROJECT_PROGRESS_INDICATOR_CURRENT.md` for the complete indicator ledger and current accounting. ZERO COST; no deployment, production credentials, Termux, Vercel/Cloudflare operation or `main` modification.


## Batch 62J-75 — exact-head CI confirmation and host/device acceptance boundary

Exact-head CI for `f3264c7ee0db573b4ff999c558506c4efe3e59d5` completed successfully:
- Automated Tests [44875028851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028851) — SUCCESS; 1,249 backend tests passed in 49.05 seconds.
- CodeQL [44875028870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028870) — SUCCESS.
- Full Git History Secret Audit [44875028765](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028765) — SUCCESS.
- Redis ACL integration verified DB-0 operation with no `+select`; explicit `SELECT 1` is denied for publisher and gateway roles.
- Backend container build, Redis shared-guard/AOF persistent-volume smoke, image vulnerability scan and report export/upload — SUCCESS.

The ACL correction supersedes the Batch 62J-73 diagnosis: database 0 is the default in the redis-py client path used by this repository; granting `+select` was unnecessary and has been removed. This is a least-privilege improvement.

### WebSocket acceptance disposition

The repository-side automated WebSocket E/failure matrix is complete for its defined CI scope. The real-host production acceptance cannot be completed because this project currently has GitHub + CI only and no owner-controlled backend server. The CI Redis service and Docker smoke are ephemeral and do not create a public WSS endpoint.

### Gate 10 host/device classification

- 🟨🟩 Host/owner verification only: Gate 8 (secret injection/runtime exposure), Gate 30 (restore on actual owner-controlled database path), Gate 34 (actual persistent volume/restart/disk pressure), Gate 35 (real HTTPS certificate/proxy/renewal), Gate 39 (live operator visibility, acknowledgement/escalation and recovery).
- 🟧 Additional integration still open: Gate 20 (real Firebase project and browser/Android auth/revocation), Gate 25 (owner-injected snapshot verifier/receipts and live dedicated Redis TLS/ACL topology), Gate 31 (off-host backup destination and independent key custody), Gate 36 (public WSS plus browser/Android WebView acceptance), Gate 38 (collector/dashboard/retention integration).

Yellow-green is not acceptance or closure. Gate 10 remains 0/10 formally closed; only complete external evidence can turn a gate bright green.

**Host verification is not an APK-only test.** It requires evidence from the actual server/provider/storage/operator environment. Opening the APK is a separate client acceptance step. For Gate 36, Android/browser testing should occur only after a real public HTTPS/WSS endpoint is available. No Termux or phone-side command is required at this stage.

No production host, endpoint, TLS certificate, backup destination, Firebase project or credentials were fabricated or requested. ZERO COST; no deployment, no paid service, no `main` modification.


## Batch 62J-76 — exact-head verification and adjacent Gate 31/38 boundaries

Source/test HEAD 57b918feafd1b259b008b5efe1272199a29facff passed Automated Tests [44876347017](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347017), CodeQL [44876347037](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347037), Full Git History Secret Audit [44876347101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347101), and Android debug APK build [44876347021](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347021). Frontend 252/252 tests across 29 files; backend 1,249 passed in 50.02 seconds. The Android artifact is a CI build only, not device acceptance.

WebSocket repository/CI failure-matrix status remains complete for its defined automated scope. Production acceptance remains unavailable because no active backend host or public HTTPS/WSS endpoint exists. Do not infer production acceptance from the CI Redis service or container smoke.

Gate 31 remains open: repository encryption is AES-256-GCM/PBKDF2-based, but there is no independently controlled off-host destination or separate recovery-key custody. Gate 38 remains open: HTTP metrics are bounded and process-local, incident records persist in local SQLite, but central collection/dashboard, cross-worker aggregation, metrics retention/rotation, WebSocket telemetry and independent operator notification remain absent. The new Gate 38 runbook documents these boundaries.

Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35 and 39 are host/owner-verification-only 🟨🟩; Gates 20, 25, 31, 36 and 38 remain 🟧. Stage 1 is 30/40 = 75% provisional; overall project remains unscored. ZERO COST; no host, credentials, deployment, Termux or device operation.


## Batch 62J-77 — exact-head WebSocket/indicator acceptance checkpoint

Source/test HEAD e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8 passed Automated Tests [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829), CodeQL [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826), Full Git History Secret Audit [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841), and Android debug APK build [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773). Frontend 253/253 tests across 29 files; backend 1,249 passed in 48.11 seconds. Backend container build, Redis shared-guard/persistent-volume smoke and Trivy scan/export all succeeded.

SMA raw rolling-sum intermediate overflow was corrected using normalized window means; tests cover finite MAX_VALUE means and large cancellation. Full details are in docs/WORK_CYCLE_2026-11-21_BATCH62J77_NORMALIZED_SMA_AND_ACCEPTANCE.md and docs/INDICATOR_PROGRESS_LEDGER.md.

Repository WebSocket automated scope remains complete. Production acceptance remains blocked by absent owner-controlled host/public HTTPS-WSS endpoint and missing real production Redis/snapshot receipts. Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36, 38 remain 🟧. Stage 1 is 75% provisional; overall project remains unscored. ZERO COST; no host, credentials, deployment, Termux or device operation.


## Batch 62J-79 — WebSocket lifecycle metrics extension (21 November 2026)

- `backend/app/observability.py` now includes `WebSocketMetrics` and `WebSocketMetricsMiddleware`, scoped only to `/ws/market-data`.
- Captured fields: started, active, completed, accepted, peer disconnect count, five fixed close-code classes and cumulative duration. No payload/header/user data is read.
- Existing bearer-protected `/internal/metrics` response now includes a `websocket` object alongside HTTP metrics. No new public route.
- Tests cover accepted/closed lifecycle, peer disconnect and route isolation.
- The new metrics are process-local and reset at process start. They are not central telemetry, durable retention or an operator dashboard. Gate 38 remains 🟧 OPEN.
- Source/test HEAD: `2274f9adc5ac9907ea508800a2d962d9a7c14a84`. Frontend/backend tests and CodeQL analyses passed in the current run; remaining Automated Tests workflow steps were still running at documentation time. Full Git History Secret Audit passed. Exact links: [Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262277), [CodeQL](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262276), [Secret Audit](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262301).
- No WebSocket protocol, auth, replay, snapshot or market-data payload contract was changed. No public WSS/production acceptance claim is made.


## Batch 62J-88 — exact-head CI reconciliation (21 November 2026)

Repository-side WebSocket failure-matrix scope remains complete. Exact-head Automated Tests at `8424e5eefeecbd06c6534bc34d166f4749ba4055` passed all 35 workflow steps, including 1,268 backend tests, backend container build, ephemeral Redis shared-guard/persistent-volume smoke and Trivy image scan/report export. CodeQL and Full Git History Secret Audit also passed. The process-level metrics and read-only collector additions do not alter WebSocket protocol, transport, auth, replay, cursor, gateway or Redis market-data path. Public WSS, production snapshot receipts, owner-host Redis TLS/ACL/persistence/failover and browser/Android WebView acceptance remain external host gates. Gate 36 remains 🟧 OPEN.


## Batch 62J-92 — WebSocket acceptance reconciliation

Exact HEAD `427e5952d2f209ae1f40405223d8d0a4c7d8408c` passed Automated Tests [44905839386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839386), CodeQL [44905839403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839403) and Full Git History Secret Audit [44905839442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839442). Backend container build, ephemeral Redis shared-guard/persistent-volume smoke and Trivy scan/report also passed. The Gate 38 app-level isolation test confirmed that a failing metrics collector does not block authenticated WebSocket status delivery. No WebSocket protocol, transport, auth, replay, cursor, gateway or Redis market-data data-path change was made.

This does not close Gate 36: public HTTPS/WSS reverse proxy, certificates, owner-host Redis TLS/ACL/persistence/failover, snapshot distribution/installation receipts and real browser/Android WebView acceptance remain host-gated.


## Batch 62J-93 — WebSocket/Gate 38 exact-head reconciliation (21 November 2026)

Exact source/test HEAD `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb` passed Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436), CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400) and Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397). Backend tests: 1,271 passed; frontend: 255/255. The new SQLite batch-read optimization affects only metrics aggregation. No WebSocket protocol, transport, authentication, replay, cursor, gateway, Redis market-data path or message payload changed. Gate 38 app-level isolation still proves the metrics collector can degrade without blocking authenticated WebSocket status.

Gate 36 remains 🟧 OPEN for owner-host public HTTPS/WSS reverse proxy/certificate, production Redis TLS/ACL/persistence/failover, snapshot installation receipts and real browser/Android WebView acceptance.

## Batch 62J-123 — exact-head SQLite concurrency fix, CI artifacts and acceptance reconciliation (22 November 2026)

**Branch:** phase-2/market-data-foundation  
**Exact tested source/test HEAD:** 589aceadd40b3b3e10e950566081101b2dd49003  
**Automated Tests [run 44985059074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074): SUCCESS**; **CodeQL [run 44985059102](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059102): SUCCESS**; **Full Git History Secret Audit [run 44985059070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059070): SUCCESS**. All three workflows target the exact tested HEAD. Automated Tests completed all 36 job steps with no failed steps.

### CI and artifact evidence
- Frontend unit tests/build, source and production-bundle credential scans, Android host preflight, backend dependency audit/tests, isolated Redis TLS CA/hostname fixture, synthetic SQLite outbox and metrics benchmarks, backend image build, shared-Redis/persistent-volume container smoke, Trivy scan/report export and dependency-audit enforcement all completed successfully.
- Synthetic metrics artifact [14739815366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739815366): full 899-series envelope. One worker: 32/32 flushes, 0 retries, p95 flush 14.34 ms. Four threads: 128/128, 4 retries, p95 flush 46.92 ms. Sixteen simultaneous threads: 512/512, 187 retries, p95 flush 627.74 ms and writer-lock p95 572.23 ms. Four independent processes: 128/128, 3 retries, p95 flush 141.71 ms. Startup-staggered 16-worker case: 512/512, 26 retries, p95 flush 266.53 ms and writer-lock p95 250.93 ms. SQLite integrity reported ok for every case.
- The benchmark confirms no lost flushes in these synthetic cases and exposes material same-file SQLite writer contention at higher concurrency. It is runner/filesystem-specific, uses synthetic operational counters, and is not production load, persistent-volume, multi-host or SLO evidence. Do not infer production capacity from it.
- Synthetic outbox artifact [14739423041](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739423041) is attached to this exact run; it remains local synthetic benchmark evidence, not live provider/WebSocket load acceptance.
- Trivy artifact [14739224531](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44985059074/artifacts/14739224531) was independently inspected. Image dezzta-chart-backend:ci, Alpine 3.24.4, architecture amd64, digest sha256:5240158d55f11863aa41a49fbf4d00705d437519fcbdb0659164efc435ee58c0, size 571,352,064 bytes (~571.35 MB). The report contains 0 vulnerabilities in the scanned Alpine OS and Python package result groups. This is a point-in-time result for this exact amd64 image and scanner database, not a permanent guarantee, not a scan of every possible target, and not ARM64 evidence.
- Backend and frontend exact-head CI success proves the repository's configured tests and CI service topology only. The CI Redis fixture and ephemeral runner volume do not constitute owner-host acceptance.

### SQLite corrective change and remaining risk
- Commit 529031d3a6ae0d07cfcd2f38a5d7e02fffd81063 adds bounded retry for lock-only errors while applying connection-local PRAGMA synchronous=NORMAL to fresh SQLite connections. Commit 589aceadd40b3b3e10e950566081101b2dd49003 adds a 16-independent-collector, eight-round repeated concurrent-flush regression test.
- Exact-head backend tests and full CI pass. The prior fatal database-is-locked failure at connection PRAGMA setup was not reproduced in this run.
- The benchmark still shows substantial contention at 16 simultaneous workers (187 retries). Keep the collector classified as bounded same-host best-effort telemetry; do not claim high-concurrency production readiness. A single-writer queue/aggregation redesign would be a separate scoped architecture change, not silently bundled into this fix.

### WebSocket production acceptance disposition
- Source/gateway separation, Redis Streams consumer/replay, generation-scoped leases, apply-before-ACK, pending reclaim, fail-closed ownership and snapshot/replay recovery remain repository implementation evidence. Owner-supplied source snapshot verification and gateway installation callbacks remain trust boundaries requiring independent authentication of snapshot bytes, SHA-256, generation, cursor and per-gateway receipts.
- Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI result.
- Still missing owner-controlled evidence: Gate 8 secret injection/permissions/rotation/log redaction; Gate 20 real Firebase signed-token and entitlement grant/revoke/renew E2E; Gate 25 owner-host Redis TLS/CA/hostname, ACL, persistence/restart/failover, secret rotation and authenticated global snapshot/receipt alignment; Gate 30 live DB backup/restore; Gate 31 encrypted off-host backup and independent recovery-key custody; Gate 34 persistent volume UID/GID 10001/restart/disk-pressure; Gate 35 public hostname/trusted TLS/renewal; Gate 36 public HTTPS ticket exchange/WSS proxy, browser and Android WebView lifecycle/replay/resnapshot/duplicate-suppression; Gate 38 real dashboards/retention/alerts/disk pressure; Gate 39 external alert delivery, human acknowledgement and escalation.
- No public HTTPS/WSS endpoint, production Firebase project, owner-host Redis or production storage has been provisioned or verified. CI must not be used to close these gates.

### Architecture and zero-cost constraints
- Current workflow uses plain docker build on GitHub-hosted ubuntu-latest; Dockerfile base is python:3.12-alpine3.24. Exact artifact metadata is linux/amd64. ARM64 build and runtime smoke remain unverified; no multi-platform claim is made.
- Keep Redis private with strict TLS CA/hostname verification and least-privilege ACLs. Keep HTTPS ticket exchange before WSS; Firebase ID tokens must not be put in WSS URLs or raw WebSocket auth frames. Preserve separate source publisher and gateway replica roles and exact global snapshot/watermark alignment.
- ZERO COST: no deployment, host, account, resource, paid service, trial-credit dependency, production credential, Vercel/Cloudflare operation or device/Termux action. main remains untouched.

---
## Batch 62J-121 — exact-head WebSocket CI completion and indicator reconciliation (22 November 2026)

**Verified branch:** `phase-2/market-data-foundation`  
**Exact tested HEAD before this documentation update:** `524e78ff032f759d4475f3d396a58aa60f17b40b`  
**Exact-head CI:** Automated Tests [run 44983903576](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576) — **SUCCESS** (Test and Build job and all reported steps completed successfully); CodeQL [run 44983903708](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903708) — **SUCCESS**; Full Git History Secret Audit [run 44983903634](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903634) — **SUCCESS**.

The Automated Tests job completed frontend dependency audit, frontend unit tests and build, production bundle secret scans, Android preview-host preflight, backend dependency audit and tests, isolated Redis TLS CA/hostname enforcement fixture, synthetic SQLite outbox and metrics collector benchmarks, backend container build, container smoke with shared Redis guard and persistent CI volume, Trivy scan/report export and upload, and final dependency-audit enforcement. Artifacts produced by this exact run: synthetic outbox benchmark [14739336684](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14739336684), synthetic metrics collector benchmark [14738972814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738972814), and container vulnerability report [14738408566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44983903576/artifacts/14738408566). The report was generated and uploaded; this note does not claim a zero-vulnerability result because the current artifact contents were not independently inspected in this batch.

**WebSocket source/test review:** the source-side publisher, per-gateway Redis Stream consumer, durable replica apply-before-ACK flow, snapshot/replay recovery and scoped single-use ticket/client transport remain present at the audited source baseline. The consumer design uses independent groups per gateway, pending-message reclaim, idempotent replica application and explicit resnapshot on stream-history gaps. The client rejects production non-HTTPS base URLs, uses WSS, exchanges Firebase credentials over HTTPS for a short-lived ticket, and validates snapshot watermarks and stream sequence. These are repository implementation facts; CI confirms covered automated paths, not production service behavior.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS hostname/certificate/reverse-proxy route; no real Firebase project token, revocation and entitlement evidence; no owner-host Redis TLS/ACL/rotation/persistence/failover evidence; no independently verified global snapshot digest and per-gateway installation receipts; and no real browser plus Android WebView lifecycle evidence. CI Redis and ephemeral runner volumes do not satisfy owner-host acceptance. Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition is authorized.

**Indicator exact-head reconciliation:** GitHub compare from indicator implementation baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` to `524e78ff032f759d4475f3d396a58aa60f17b40b` reports six commits and only documentation paths changed (13 documentation files; no indicator implementation, calculation, hook, renderer, chart UI or indicator-test source). Therefore this CI/documentation batch awards **zero indicator progress**. Current statuses remain: SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook — 🟨 foundation; Footprint — 🟧 simulated/reference-gated; Heatmap and Liquidation Maps — 🟥 not implemented. Keep the formula/warm-up definitions, candle identity and alignment rules, stale-series clearing, renderer/UI acceptance, and Footprint OFF standard-candle-spacing invariant unchanged. Footprint and Heatmap visual work remains blocked until user-provided reference images and a reviewed blueprint exist. No aggregate indicator percentage is assigned without an approved denominator and weights.

**ZERO COST and scope:** documentation-only reconciliation. No runtime source, tests, workflows, formulas, renderer, UI or deployment configuration changed. No host, account, resource, endpoint or paid service was created; no credentials were requested; no device/Termux work occurred; `main` was not touched. No trial-credit or paid-service dependency is introduced.

**Next sequence:** (1) preserve the green exact-head CI; (2) keep Gate 8/20/25/30/31/34/35/36/38/39 open until the listed owner-host/operator evidence is supplied; (3) pursue only zero-cost, non-provisioning checks until adult account-owner review and explicit authorization exist; (4) continue indicator implementation only within its existing approved scope and reference gates. Do not count CI, documentation or synthetic benchmarks as production acceptance.

---

## Batch 62J-120 — exact-head CI and artifact inspection (22 November 2026)

**Tested HEAD:** `c6cd331c5f9293093418bda31f93960f5aed1600`. Automated Tests #1954, CodeQL and Full Git History Secret Audit all completed SUCCESS. The Trivy JSON artifact was inspected: zero reported vulnerabilities in the scanned Alpine OS and Python package groups for the `linux/amd64` CI image. Synthetic outbox replay passed; the 899-series metrics collector benchmark exposed increasing SQLite writer-lock retries under higher concurrency. These are CI-only measurements, not production SLOs. ARM64 remains unverified; public WSS, production Redis/Firebase and browser/Android E2E remain open. No indicator source or test changed; indicator statuses and Stage 1 accounting remain unchanged. Full evidence and limitations: [Batch 62J-120](WORK_CYCLE_2026-11-22_BATCH62J120_EXACT_HEAD_CI_ARTIFACT_AND_ACCEPTANCE_AUDIT.md).

## Batch 62J-119 — WebSocket acceptance and indicator ledger exact-head reconciliation (22 November 2026)

**Verified parent HEAD:** `6d5a05d611615972d5826002442a65e74c179750` on `phase-2/market-data-foundation`. This checkpoint was created only after all three workflows for that exact SHA completed successfully.

**Exact-head CI:**
- Automated Tests #1954 — [run 44982930281](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281): **SUCCESS**. Frontend unit tests/build, backend tests, isolated Redis TLS/CA/hostname enforcement fixture, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke test using shared Redis guard and persistent volume, Trivy image scan/report export/upload, and dependency-audit enforcement all completed successfully.
- CodeQL [run 44982930379](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930379): **SUCCESS**.
- Full Git History Secret Audit [run 44982930324](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930324): **SUCCESS**.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44982930281/artifacts/14739265202). The workflow completed the configured HIGH/CRITICAL scan and uploaded the JSON report. Do not infer a zero-vulnerability result without reviewing the artifact contents.

These results verify the repository workflow and its CI service topology only. The CI Redis instance, ephemeral runner volume, and container smoke are not the intended OCI host or production Redis service.

**WebSocket repository evidence:** source-side publisher and gateway runtime factories, durable SQLite outbox, atomic snapshot/watermark primitives, Redis Streams publisher/consumer, per-gateway consumer groups, replica snapshot installation checks, fail-closed runtime construction, ticket authentication/renewal, reconnect/replay and client failure-matrix tests are present in the audited source. The latest CI validates the covered repository paths. The default FastAPI app intentionally does not invent owner-specific publisher/replica factories or trust snapshot receipts; those must be injected from a verified owner-controlled host setup.

**Production acceptance remains OPEN:** no verified public HTTPS/WSS endpoint, production Firebase token/entitlement evidence, owner-host Redis TLS/ACL/persistence/rotation/failover, authenticated global snapshot manifest and per-gateway installation receipts, or real browser + Android WebView lifecycle evidence has been supplied. A successful CI container smoke cannot close those host/client gates.

**ZERO COST boundary:** no OCI account or resource was created, no deployment or public endpoint was started, no paid resource or trial-credit dependency was introduced, no credentials were requested, no device/Termux operation occurred, and `main` was not touched. OCI remains a conditional candidate subject to actual Always Free eligibility and adult account-owner approval.

**Indicator disposition — no source change and no progress credit:** the source-backed indicator audit baseline `0074f1d0b0e421f32800294742f92d9bc9c8a2c6` remains the calculation baseline. The comparison through parent HEAD `6d5a05d611615972d5826002442a65e74c179750` is documentation-only; no indicator formula, hook, chart renderer, UI, or indicator test source changed. SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 not implemented. Formula definitions, warm-up indices, numerical safeguards, data identity, stale-series invariants, UI acceptance and reference prerequisites remain in the canonical audit and ledger. Aggregate indicator percentage remains unscored without approved weights and denominator.

**Project accounting:** Gate 10 remains **0/10 formally closed**. Stage 1 remains **30/40 = 75% provisional**. No stage transition or Stage 2 entry is authorized by this CI or documentation-only checkpoint. No progress is awarded from CI alone.

**Next zero-cost sequence:** preserve the green exact-head CI; finish ARM64 build/configuration readiness without provisioning; have the adult account owner verify OCI eligibility, capacity and all possible charges; only then, with explicit authorization, consider an Always Free-only host. Collect actual host and client evidence for Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Close Gate 10 only after evidence review and operator sign-off.

---

## Batch 62J-117 — exact-head CI verification (22 November 2026)

At exact branch HEAD e76b6cd6c8f7380e5a10a7d4707028fa7da78a02, Automated Tests [run #1952](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803844), CodeQL [44981803808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803808), and Full Git History Secret Audit [44981803851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981803851) all completed **SUCCESS**. The Automated Tests workflow reports all 61 steps successful, including frontend/backend tests, backend container build, isolated Redis TLS/CA/hostname fixture, persistent-volume Redis restart smoke, container scan/report and dependency audits. This verifies repository CI only; it does not close external production gates.

The repository-side client matrix remains 17 WebSocket transport tests, 7 HTTPS ticket-exchange tests and 21 stream-supervisor tests. Real Firebase token/entitlement cases (Gate 20), owner-host Redis TLS/ACL/persistence/recovery and snapshot installation receipts (Gate 25), and public HTTPS/WSS reverse-proxy plus real browser/Android WebView lifecycle tests (Gate 36) remain open. No public host or endpoint is verified. Keep ZERO COST; no OCI provisioning, deployment, production credentials or main-branch changes.

The indicator audit is unchanged because the comparison from its source/test baseline to this HEAD contains documentation-only changes. No indicator credit is awarded by this WebSocket CI pass. See the indicator audit and Batch 62J-117 reconciliation.

---

## Batch 62J-116 — current WebSocket acceptance evidence (22 November 2026)

At baseline `a3febdb3f7d3dd233f1cfeb8e482e986e56348e1`, exact-head CI is green: Automated Tests [44981340874](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340874), CodeQL [44981340863](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981340863), and Full Git History Secret Audit [44981341220](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44981341220). Frontend 29 test files passed; backend 1,294 passed and 1 skipped; all 36 automated workflow steps completed, including container and CI Redis persistence smoke.

The client suite includes 17 transport tests, 7 ticket-exchange tests, and 21 supervisor/reconnect tests. These prove the covered repository scenarios only. They do not prove public WSS, real Firebase project, owner-host Redis, global snapshot receipts, or browser/Android WebView acceptance. The current external evidence checklist is in [Batch 62J-116](WORK_CYCLE_2026-11-22_BATCH62J116_WEBSOCKET_ACCEPTANCE_RECONCILIATION.md).

---

## Batch 62J-94–96 — WebSocket data path unchanged (21 November 2026)

Gate 38 SQLite tail-latency instrumentation, benchmark analysis and the rejected/reverted retry-jitter experiment did not modify WebSocket transport, authentication, ticket exchange, snapshot/replay, cursor ordering, publisher/replica lifecycle, Redis ACL behavior or market-data payloads.

Exact source/test HEAD `2eb3181b21b7f2aa3a53c8c293ab6d27ec959b75` passed Automated Tests [44913778296](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778296), CodeQL [44913778266](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778266) and Full Git History Secret Audit [44913778270](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778270).

WebSocket repository-side automated failure-matrix scope remains previously implemented and CI-verified. Production acceptance remains open pending verified global snapshot bytes and authenticated installation receipts for every required gateway; owner-host Redis TLS/ACL credentials, secret rotation, persistence/failover/retention; public HTTPS/WSS proxy and certificate renewal; and real browser plus Android WebView acceptance. No public production endpoint or production Redis host is available in this checkpoint.

---

## Batch 62J-87 — Gate 38 writer-lock correction; WebSocket unchanged (21 November 2026)

The 16-worker SQLite benchmark exposed lock contention at `BEGIN IMMEDIATE`. Gate 38 now retries bounded writer-lock acquisition and records retry counts. No WebSocket transport, authentication, snapshot/replay, cursor, gateway or Redis code changed. Production WSS acceptance remains pending real owner-host and client evidence.

---

## Batch 62J-86 — telemetry bootstrap contention fix; WebSocket data path unchanged (21 November 2026)

The Gate 38 benchmark exposed SQLite schema-initialization contention while separate collector instances opened the same local database. The collector now serializes schema initialization within each instance and retries bounded SQLite lock failures; the benchmark models separate collector instances per worker. The new exact-head CI is pending.

No WebSocket publisher, gateway consumer, auth, replay, snapshot, cursor or market-data payload code changed. The WebSocket repository-side automated failure matrix remains previously verified for its defined scope; production acceptance still requires owner-host snapshot/Redis/TLS/proxy/browser/Android evidence.

---

## Batch 62J-85 — Gate 38 benchmark expansion; WebSocket scope unchanged (21 November 2026)

The latest Gate 38 work expands the synthetic SQLite metrics benchmark from 12 to the full 899 declared logical series and adds a transaction write-rejection rollback/retry test. It does not modify WebSocket publisher, gateway consumer, replay, snapshot, authentication, cursor or payload code. Exact-head CI is pending; no pass is claimed yet.

**WebSocket repository status:** the defined automated protocol/failure matrix remains implemented and previously CI-verified. **Production acceptance remains open** until the exact global snapshot bytes are SHA-256 verified and authenticated installation receipts are confirmed for every required gateway; owner-host dedicated Redis TLS/ACL, persistence/failover/retention and secret lifecycle are verified; public HTTPS/WSS proxy/certificate/renewal are operational; and real browser plus Android WebView acceptance is recorded. The default ASGI app remains opt-in for publisher/replica roles. No production host or endpoint is present in this checkpoint.

---

## Batch 62J-84 — Gate 38 SQLite failure-path and worker-load evidence (21 November 2026)

- Exact source/test HEAD `92119a8dc05690e6492aab160662c9e36c839cad`: Automated Tests [44900892637](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892637) SUCCESS (35/35 steps; 1,265 backend tests), CodeQL [44900892567](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892567) SUCCESS, Full Git History Secret Audit [44900892606](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44900892606) SUCCESS.
- Added tests for concurrent collector workers, busy-lock rollback/recovery and corrupt-database rejection. Added a local-only synthetic benchmark for 1/4/16 Python worker threads; CI artifact records latency and database/WAL/SHM size.
- Initial low-cardinality benchmark used 12 logical series. At 16 workers/512 flushes, p99 was 78.978ms, retry count zero and peak total DB+WAL+SHM was 4,284,304 bytes. This is not full 899-series capacity evidence or an owner-host byte budget.
- No WebSocket protocol, auth, replay, snapshot, market-data payload or Redis guard behavior changed. No public WSS or production acceptance is claimed.
- Gate 38 remains 🟧 OPEN pending full-cardinality/process-level benchmark, disk-full/read-only/app-isolation tests and owner-host acceptance. Gate 10 remains 0/10 formally closed.
- Indicator implementation is unchanged; no indicator progress credit is awarded. ZERO COST; no deploy, production credentials, Termux/device operation or `main` modification.

---

## Batch 62J-83 — Gate 38 telemetry hardening (21 November 2026)

- Pre-change exact HEAD `b1e21f552182a720400cd9a2d276705834a41358`: Automated Tests 44898947136 SUCCESS (33/33 steps); CodeQL 44898947150 SUCCESS; Full Git History Secret Audit 44898947186 SUCCESS.
- Collector hardening adds bounded stale-worker checkpoint eviction, seven-day retired-worker tombstones (4096 maximum) to reject a resumed evicted worker ID, seven-day read-side bucket filtering, explicit aggregate-row eviction counters, and worker timestamp monotonicity checks.
- Added regression coverage for worker-generation saturation, tombstone rejection, 16-worker live limit, retention filtering, and timestamp regression. Exact-head CI for source commit `e98bf7acda841ae4045d258b6d3b2fe774205239` passed: Automated Tests 44899788672, CodeQL 44899788812 and Full Git History Secret Audit 44899788701. Host acceptance remains open.
- WebSocket lifecycle accounting and transport semantics remain unchanged. The metrics collector is best-effort same-host telemetry only; production WSS remains unaccepted pending actual host/proxy/Redis/browser/Android evidence.
- No deployment, paid provider, Termux, production credential or `main` operation.

---



## Batch 62J-82 — exact-head CI and capacity-model correction (21 November 2026)

- Exact HEAD `c3577d7174ce5873502ebd8df7a57f27447a296b`: Automated Tests 44897164887 SUCCESS; CodeQL 44897164916 SUCCESS; Full Git History Secret Audit 44897164908 SUCCESS.
- Automated Tests completed backend container build, Redis persistent-volume smoke, Trivy scan and vulnerability report export/upload, in addition to frontend/backend tests, SQLite outbox benchmark and dependency audits.
- Gate 38 blueprint now explicitly states the nominal crash-loss window of up to one 15-second flush interval plus scheduler delay. Transactional checkpoints prevent replay of committed deltas but cannot recover unflushed in-memory increments. This is telemetry, not financial accounting.
- Series capacity is bounded from source contracts: 127 method/route pairs × 6 status classes = 762 request series; 127 latency series; conservative total planning ceiling 900 series per 15-minute bucket. 672 buckets represent seven days. Aggregate planning bound 604,800 rows; 16 workers × 900 checkpoints = 14,400; plus 16 heartbeats. Initial logical-row ceiling: 650,000. SQLite byte cap remains benchmark-derived.
- The 1,500x operation estimate is explicitly a comparison with hypothetical per-request persistence, not a measured improvement over current in-memory counters.
- No runtime source changed. Gate 38 remains 🟧 OPEN pending explicit blueprint approval, implementation, exact-head CI, measured byte budget and owner-host/operator acceptance.
- WebSocket send-confirmed lifecycle accounting remains unchanged and CI-verified. Production WSS acceptance still requires host-side snapshot/Redis/TLS/proxy/browser/Android evidence.
- ZERO COST; no deployment, production credentials, Redis ACL change, Termux, main modification or paid provider.

---
## Batch 62J-81 — Gate 38 zero-cost collector design (21 November 2026)

- Exact-head baseline 3eadda21f795abe5af195eedf0c81727d31f6436 rechecked: Automated Tests run 44895224507 SUCCESS; CodeQL run 44895224465 SUCCESS for JS/TS and Python; full Git-history secret audit run 44895224498 SUCCESS.
- Current source still has bounded process-local request and WebSocket metrics. The protected endpoint remains token-gated; the WebSocket middleware records lifecycle metadata only.
- The existing Redis client is coupled to shared security guards. It is not reused for telemetry because doing so couples monitoring availability to auth/rate-limit operations and could exceed its ACL scope.
- The existing SQLite incident journal is not a time-series collector. The market-data registry database is not used for high-frequency metrics writes.
- Added GATE38_METRICS_COLLECTOR_BLUEPRINT.md: same-host multi-worker aggregation using a dedicated SQLite metrics DB on a supported local persistent volume; 15-second snapshots; transactional deltas; 15-minute buckets; 90-second worker-heartbeat expiry; 7-day bounded retention; hard worker/cardinality/payload/row/disk limits.
- Load estimate at 100 requests/s: 8,640,000 request-level write opportunities/day/worker versus 5,760 periodic flushes/day/worker, a 1,500x operation-count reduction. This is an estimate, not a benchmark.
- This is a documentation/design checkpoint only. Source implementation requires explicit blueprint review under the project's major-implementation rule.
- Gate 38 remains 🟧 OPEN pending implementation, tests, exact-head CI, host volume/access/retention/disk-pressure evidence and independent operator notification/recovery acceptance.
- No indicator code changed and no indicator progress is awarded. Complete formulas, warm-up indices, remaining renderer work, and Footprint/Heatmap visual gates remain in INDICATOR_PROGRESS_LEDGER.md.
- ZERO COST; no deployment, production credentials, Redis ACL change, main modification, Termux or device operation.

---

## Batch 62J-80 — send-confirmed WebSocket lifecycle metrics

**Reviewed branch:** phase-2/market-data-foundation  
**Change scope:** backend/app/observability.py and backend/tests/test_observability.py

The observer now updates accepted-handshake and close-code metrics only after the downstream ASGI send call returns successfully. A failed send no longer produces false-positive acceptance/close telemetry. The middleware finally block still finalizes the connection, decrements the active count and records completion even when the application/transport raises.

Regression cases cover failure at the accept frame and failure at the close frame after a successful accept. These cases assert active=0 and completed=1, with accepted and close-class counters reflecting only successful downstream sends.

No WebSocket payload/protocol/auth/replay/snapshot behavior changed. Gate 38 remains 🟧 OPEN: metrics are process-local, not centrally aggregated or durably retained. The production acceptance boundary described below remains unchanged.

---

# WebSocket Production Wiring Audit

**Audit date:** 21 November 2026  
**Active branch:** `phase-2/market-data-foundation`  
**Source checkpoint reviewed:** `da9b2ad025ac5c49f75c95dbdd5f516573107f87`  
**Scope:** source SQLite outbox -> Redis Streams -> gateway replica -> authenticated WebSocket

## Executive result

The initial audit found that the repository contained substantial publisher and consumer primitives but lacked a source publisher lifecycle hook. Batch 62J-69 has since implemented that lifecycle hook and exact runtime-binding checks. The production data path is still not activated by the module-level default ASGI app and is not host-accepted; do not deploy this checkpoint as proof of live fan-out.

The initial audit found two independent integration gaps:

1. **Initial finding — source publisher lifecycle absent (superseded by Batch 62J-69).** `backend/app/ohlcv_redis_publisher.py` implements `SQLiteOhlcvPublisherCheckpoint`, `RedisOhlcvStreamAppender`, and `RedisOhlcvPublisher.publish_available()`. The publisher class explicitly documents that it is not connected to FastAPI startup. `backend/app/main.py` imports the gateway consumer worker but not the source publisher. Its `publish_persisted_bar()` reads the durable outbox event and calls only `stream_hub.publish()`; it does not append that event to Redis Streams.
2. **Gateway runtime remains injection-only.** `create_app()` accepts an optional `replica_runtime_factory`; the module-level `app = create_app()` supplies none. Therefore the default ASGI entry point starts the provider/local-SQLite path, not the replica consumer path. A gateway host needs an explicit, verified factory and a preinstalled replica snapshot.

These gaps are separate: wiring the source publisher does not automatically provision gateway snapshots or activate the replica runtime.

## Existing verified components

- Durable source OHLCV outbox with contiguous global cursors.
- SQLite publisher checkpoint with lease owner/epoch fencing and compare-and-swap cursor advancement.
- Redis appender with deterministic stream IDs (`<cursor>-0`) and exact-ID read-back after ambiguous XADD replies.
- Bounded publisher batches and explicit fresh-snapshot requirement when source outbox retention overtakes the publisher cursor.
- Atomic global snapshot export/verification and replica snapshot installation.
- Independent per-gateway Redis consumer groups, apply-before-ACK, durable local SQLite replica checkpoint, replay, ownership lease and resnapshot-required handling.
- Replica hydration and atomic snapshot-to-live subscription bridge.
- FastAPI gateway worker startup validates snapshot hydration, ownership lease and Redis consumer-group readiness before accepting traffic.

## Required implementation sequence

### WS-PUB — remaining host-side activation

The FastAPI lifecycle hook is implemented and CI-verified. Remaining activation requirements are owner-host tasks:

- Inject a source-only `publisher_runtime_factory`; the default module-level app deliberately remains disabled.
- Build the publisher against the exact `SQLiteOhlcvStore` instance supplied by FastAPI. Runtime startup rejects a different store, checkpoint, source ID, Redis client or stream key.
- Require a pre-existing checkpoint or initialize it only from the exact global snapshot watermark already installed on every target gateway. Never infer or invent the cursor.
- Use a dedicated least-privilege publisher ACL client and finite connect/socket timeouts; production must use `rediss://`.
- Verify the owner-host durable volume, Redis ACL and snapshot generation before enabling the feature.
- The sanitized lifecycle state is held in application state; it is not a public status route and does not expose credentials or exception messages.

### WS-SNAP — snapshot generation coordination

Do not initialize the publisher checkpoint from an arbitrary current cursor. The checkpoint watermark must match the exact global snapshot generation installed on every target gateway. Snapshot export, integrity verification, distribution, installation, generation activation, publisher checkpoint initialization/rebase and rollback need an explicit ordered operator workflow.

### WS-GW — gateway runtime configuration

Provide a host-injected gateway runtime factory that:
- Opens a dedicated least-privilege Redis client.
- Opens the persistent local replica SQLite path.
- Requires a verified snapshot before constructing the consumer.
- Uses the generation-scoped group and owner lease.
- Closes resources safely on every startup-failure and shutdown path.

Keep source publisher and gateway consumer as separate application roles unless a reviewed architecture explicitly proves a combined role safe.

## Acceptance matrix

| Test | Required evidence |
|---|---|
| Publisher bootstrap | Missing checkpoint fails closed; valid snapshot checkpoint starts |
| Event relay | Source outbox cursor N becomes exactly Redis Stream ID N-0 |
| Ambiguous XADD | Lost reply is resolved by exact-ID read-back without double append |
| Redis outage | Source commit remains durable; publisher retries without advancing cursor |
| Retention gap | Publisher enters resnapshot-required; no cursor is skipped |
| Wake-up and backlog | New bars wake relay; process restart drains retained backlog |
| Shutdown | Publisher task stops and dedicated Redis client closes |
| Snapshot alignment | Publisher cursor equals the installed gateway snapshot watermark |
| Two gateways | Both independent replica groups receive the same ordered source events |
| Replay continuity | Restart/reconnect resumes from durable cursors without gaps or duplicate client delivery |
| Host acceptance | Real TLS/ACL, persistent volumes, public WSS, browser and Android WebView verified |

## Safety and cost constraints

- No Vercel or Cloudflare deployment is required for repository-side implementation or CI.
- No paid Redis service is assumed. Use only an already available, owner-controlled Redis endpoint; otherwise keep the relay disabled.
- No production credentials, snapshot files or encryption keys belong in Git or chat.
- Do not run a production host migration or alter persistent data as part of a code-only change.
- Do not modify `main`.
- Do not mark host-only gates green based on source tests or CI.

## Current project accounting

- Gate 10: 0/10 formally closed.
- Gate 8: yellow host-verification-only; all other Gate 10 entries remain open.
- Stage 1: 30/40 criteria = 300/400 ticks = 75% provisional.
- Overall project and aggregate indicator percentages: unscored pending approved weights and denominators.
- Indicator formulas/foundations remain unchanged by this audit. Existing indicator implementation status remains as documented in `PROJECT_PROGRESS_INDICATOR_CURRENT.md`.

## Audit disposition

**WebSocket repository primitives:** substantially implemented and CI-verified for the defined automated failure matrix.  
**Source-to-Redis publisher lifecycle hook:** implemented and exact-head CI-verified; source runtime factory, snapshot watermark alignment, dedicated Redis ACL and host activation remain 🟨🟩 pending.  
**Redis-to-gateway replica integration:** opt-in factory exists; default ASGI entry point is not wired.  
**Production acceptance:** open; public WSS, production Redis TLS/ACL topology, snapshot distribution/rotation/rollback, browser and Android WebView acceptance remain unverified.  
**Initial audit code changes:** none. Batch 62J-69 adds the subsequent FastAPI publisher lifecycle and runtime-binding validation.


## Batch 62J-69 — source publisher lifecycle integration (21 November 2026)

**Source change:** FastAPI now accepts a dedicated, owner-injected `publisher_runtime_factory` for the source application role. Lifespan validates that the publisher, dedicated Redis client and exact stream key agree; performs Redis PING before provider ingestion starts; runs bounded synchronous publisher batches through `asyncio.to_thread`; wakes on persisted-bar callbacks; and polls once per second to recover retained backlog after restart. Transient failures use bounded 1–30 second exponential backoff. A typed retention-gap exception transitions the worker to terminal `resnapshot_required` without advancing the checkpoint. Shutdown waits up to 15 seconds and closes the dedicated client only after the publisher task has stopped.

**Role isolation:** one FastAPI app cannot be configured with both source publisher and gateway replica runtime factories. The module-level default app remains publisher-disabled unless its owner explicitly injects a source runtime factory. No Redis URL, credentials, snapshot cursor or snapshot artifact is inferred by application code.

**Host gate:** the source runtime factory must construct `SQLiteOhlcvPublisherCheckpoint` against the durable source database, require an existing checkpoint or initialize it only from the exact global snapshot watermark already installed on every target gateway, and use a dedicated publisher ACL client with finite socket/connect timeouts. The code cannot prove remote snapshot installation; this remains an owner-host prerequisite. Publisher lifecycle wiring is therefore **🟨🟩 HOST-FACTORY / SNAPSHOT VERIFICATION PENDING**, not production-green. Do not enable the source publisher until snapshot and ACL preconditions are satisfied.

**Verification boundary:** lifecycle contract tests cover Redis readiness, task startup, graceful client close, source/gateway role separation and runtime binding mismatch. The runtime also rejects a publisher bound to a different SQLite store or checkpoint/source ID. Exact-head CI on `6f49951c253a7e7b995b4bdd52eba8153edaef77` passed: Automated Tests [44866818528], CodeQL [44866818498] and Full Git History Secret Audit [44866818495] all SUCCESS; frontend 247/247, backend 1,241 passed, and all 33 workflow steps succeeded. Backend container build, Redis ACL/AOF + persistent-volume smoke, container scan and vulnerability-report export also succeeded. No deployment, live Redis connection, production host, Termux command, paid service, or `main` change was performed.



## Batch 62J-70/71 — dedicated source runtime and production transport enforcement

### Source publisher runtime (62J-70)

Added `backend/app/ohlcv_redis_runtime.py`:
- Separate dedicated publisher ACL URL; does not reuse the shared HTTP/WebSocket guard URL.
- Production validation requires `rediss://`, dedicated ACL username/password and database 0.
- Redis client uses 3-second connect timeout, 5-second socket timeout, 15-second health-check interval, TLS certificate-chain verification and hostname verification.
- The durable publisher checkpoint must already exist. The factory never creates an arbitrary cursor.
- Before creating a Redis client, an owner-injected snapshot verifier must prove exact source ID, stream key, generation and cursor equality between the global manifest and one installation receipt per required gateway.
- Missing gateway receipts, duplicate/empty gateway identities, or any generation/cursor/source/stream mismatch fail closed.
- Environment helper remains opt-in; default module-level ASGI app is not silently enabled.

The publisher and gateway ACL command matrices now include `+ping` for their readiness checks. Other command permissions remain separated by role. Tests assert the exact allow-lists.

### Production HTTPS/WSS enforcement (62J-71)

- Production frontend builds reject a plaintext HTTP ticket endpoint before issuing the Firebase bearer request.
- Production frontend builds reject a plaintext `ws://` market-data endpoint before creating the WebSocket.
- HTTPS maps to WSS. Development mode retains its prior HTTP/WS behavior for local work.
- Added frontend regressions for both rejected production plaintext paths.

### Exact-head verification

Source/test HEAD: `5575f5d820dd26d16a7170cb2c55e9c707c2afc1`.

- Automated Tests [44868539276] — SUCCESS; frontend **249/249 across 29 files**, backend **1,246 passed**, all **33/33 workflow steps**.
- CodeQL [44868539309] — SUCCESS.
- Full Git History Secret Audit [44868539423] — SUCCESS.
- Android APK Build (zero-cost CI) [44868539288] — SUCCESS. This confirms build output only, not installation or runtime acceptance on a physical Android device.
- Frontend/backend dependency audits, backend container build, Redis shared-guard/persistent-volume smoke, container scan, vulnerability-report export and artifact upload — SUCCESS.

### Production acceptance boundary

Repository-side source publisher runtime construction and production transport guards are implemented and CI-verified. **Production WebSocket acceptance is not yet complete.** The remaining evidence requires owner-controlled runtime access:
- Actual snapshot manifest and signed/controlled installation receipts for every target gateway.
- Durable source SQLite path, checkpoint watermark and actual gateway replica volumes.
- Live Redis TLS handshake, ACL enforcement, persistence, failover and private network restrictions.
- Owner-host secret injection, rotation and rollback.
- Gateway runtime factory configured on the target host.
- Public HTTPS/WSS reverse proxy, hostname/certificate/renewal.
- Browser end-to-end and actual Android WebView/device acceptance.

The snapshot-verifier callback is a strict contract; the repository cannot probe the user's remote hosts. No host acceptance is inferred from CI. Gate 25 and Gate 36 remain 🟧 OPEN. Source publisher remains 🟨🟩 HOST VERIFICATION PENDING. Gate 8 remains 🟨 HOST VERIFICATION ONLY.

### Indicator and project accounting

No indicator formula, calculation, hook, renderer or chart UI changed. The complete indicator ledger remains in `PROJECT_PROGRESS_INDICATOR_CURRENT.md`:
- SMA20 🟨, first valid candle index 19.
- EMA20 🟨, SMA-seeded with alpha 2/21, first valid index 19.
- RSI14 🟨, Wilder smoothing, first valid index 14.
- MACD12/26/9 🟨, MACD index 25 and signal/histogram index 33.
- Bollinger20,2 🟨, population standard deviation, first valid index 19.
- Shared Indicator Hook 🟨.
- Footprint 🟧 SIMULATED / GATED.
- Heatmap 🟥 NOT IMPLEMENTED.
- Liquidation Maps 🟥 NOT IMPLEMENTED.

Gate 10 remains 0/10 formally closed; Stage 1 remains 30/40 = 75% provisional; Stages 2–6 and overall project percentage remain unscored. ZERO COST; no production deployment, paid service, Termux/device operation, Vercel/Cloudflare operation or `main` change.


## Batch 62J-72 — snapshot artifact digest binding

The source publisher runtime now requires the exact SHA-256 digest returned by the verified global snapshot manifest and requires every gateway installation receipt to bind to that same digest. The runtime rejects malformed/missing digests and any gateway receipt mismatch before creating the Redis client.

The digest contract is grounded in the existing snapshot exporter/verifier:
- `SQLiteOhlcvStore.export_global_snapshot()` writes a SHA-256 digest over the canonical header and every canonical bar record, and returns it with the snapshot generation, source ID and high-water cursor.
- `SQLiteOhlcvStore.verify_global_snapshot()` recomputes the digest from the artifact and validates the manifest digest and row count.
- The host verifier must invoke that verifier on the actual snapshot artifact and authenticate the installation receipt source. It then maps the export/verifier `generation_id`, `cursor`, and `sha256` into the runtime evidence contract (`snapshot_generation`, `snapshot_cursor`, `snapshot_sha256`); each receipt must contain the matching `snapshot_sha256`.

This is stronger artifact identity binding, not proof of remote installation or receipt authenticity. No receipt-signing format or storage backend is invented by this change. Host-side verification remains external.

Regression coverage now includes:
- Missing publisher checkpoint fails before Redis client creation.
- Gateway cursor mismatch fails before Redis client creation.
- Gateway snapshot digest mismatch fails before Redis client creation.
- Malformed manifest digest fails before Redis client creation.
- Matching source, stream, generation, cursor and digest can construct the dedicated TLS client with certificate and hostname verification.

**Gate status:** Gate 25 🟧 OPEN (live Redis TLS/ACL, persistence, failover and credential lifecycle remain unverified). Gate 36 🟧 OPEN (public HTTPS/WSS reverse proxy and browser/Android runtime acceptance remain unverified). Source publisher activation remains 🟨🟩 host-verification pending.


## Batch 62J-74 — exact-head CI acceptance and Redis ACL least-privilege correction

### Exact CI evidence

The Automated Tests workflow completed successfully on head `3e3428910e3226f3d4365808f3a36a3138674231` (run [44874341856](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341856)). Backend pytest reported **1,249 passed in 57.10 seconds**. The new Redis ACL integration test and the existing full publisher/consumer ACL integration test both passed. CodeQL (run [44874341916](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341916)) and full Git-history secret audit (run [44874341885](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44874341885)) also succeeded.

The existing CI Docker smoke additionally verified:
- Redis ACL rejects unauthenticated access, wrong passwords and unrelated SET operations.
- Redis AOF data and its ACL file survive a Redis container restart on a named volume.
- The backend returns the expected fail-closed 503 during Redis outage and recovers after Redis returns.
- Non-root application UID/GID, persistent-volume/database ownership, SQLite integrity and backend restart persistence.
- HTTP rate-limit enforcement.
- Backend container image scan and vulnerability-report export/upload succeeded.

This is repository/CI simulation evidence, not production-host acceptance. The Redis AOF/volume smoke is for the shared guard service and does not prove production persistence/failover of the dedicated OHLCV relay stream.

### Redis ACL correction — supersedes Batch 62J-73 SELECT claim

The earlier Batch 62J-73 note incorrectly stated that redis-py needs `+select` when connecting to database 0. The existing real-Redis end-to-end ACL test used a `/0` URL without `+select` and passed. Database 0 is the Redis default; the client does not need a SELECT command to use it.

Batch 62J-74 removes `+select` from both publisher and gateway command allow-lists. The new integration test explicitly verifies:
- Both clients connect through the DB-0 URL and PING successfully.
- Publisher/gateway allowed stream and lease operations work.
- Explicit `SELECT 1` is rejected for both roles.
- Publisher and gateway prohibited commands and out-of-scope key access remain rejected.

This tightens least privilege. URL parsing still rejects non-zero database paths.

### Production boundary and gates

WebSocket E is complete for the defined automated repository failure matrix. Production acceptance still requires owner-controlled evidence for actual global snapshot artifact distribution and authenticated per-gateway receipts, production Redis TLS/ACL topology and secret rotation, dedicated OHLCV stream persistence/failover/retention, public HTTPS/WSS reverse proxy, browser and Android WebView runtime acceptance.

Gate 8 remains 🟨🟩 host-verification-only. Gate 25 and Gate 36 remain 🟧 OPEN; Gates 20, 30, 31, 34, 35, 38 and 39 remain 🟧 OPEN. Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional; overall project percentage remains unscored.

See `PROJECT_PROGRESS_INDICATOR_CURRENT.md` for the complete indicator ledger and current accounting. ZERO COST; no deployment, production credentials, Termux, Vercel/Cloudflare operation or `main` modification.


## Batch 62J-75 — exact-head CI confirmation and host/device acceptance boundary

Exact-head CI for `f3264c7ee0db573b4ff999c558506c4efe3e59d5` completed successfully:
- Automated Tests [44875028851](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028851) — SUCCESS; 1,249 backend tests passed in 49.05 seconds.
- CodeQL [44875028870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028870) — SUCCESS.
- Full Git History Secret Audit [44875028765](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44875028765) — SUCCESS.
- Redis ACL integration verified DB-0 operation with no `+select`; explicit `SELECT 1` is denied for publisher and gateway roles.
- Backend container build, Redis shared-guard/AOF persistent-volume smoke, image vulnerability scan and report export/upload — SUCCESS.

The ACL correction supersedes the Batch 62J-73 diagnosis: database 0 is the default in the redis-py client path used by this repository; granting `+select` was unnecessary and has been removed. This is a least-privilege improvement.

### WebSocket acceptance disposition

The repository-side automated WebSocket E/failure matrix is complete for its defined CI scope. The real-host production acceptance cannot be completed because this project currently has GitHub + CI only and no owner-controlled backend server. The CI Redis service and Docker smoke are ephemeral and do not create a public WSS endpoint.

### Gate 10 host/device classification

- 🟨🟩 Host/owner verification only: Gate 8 (secret injection/runtime exposure), Gate 30 (restore on actual owner-controlled database path), Gate 34 (actual persistent volume/restart/disk pressure), Gate 35 (real HTTPS certificate/proxy/renewal), Gate 39 (live operator visibility, acknowledgement/escalation and recovery).
- 🟧 Additional integration still open: Gate 20 (real Firebase project and browser/Android auth/revocation), Gate 25 (owner-injected snapshot verifier/receipts and live dedicated Redis TLS/ACL topology), Gate 31 (off-host backup destination and independent key custody), Gate 36 (public WSS plus browser/Android WebView acceptance), Gate 38 (collector/dashboard/retention integration).

Yellow-green is not acceptance or closure. Gate 10 remains 0/10 formally closed; only complete external evidence can turn a gate bright green.

**Host verification is not an APK-only test.** It requires evidence from the actual server/provider/storage/operator environment. Opening the APK is a separate client acceptance step. For Gate 36, Android/browser testing should occur only after a real public HTTPS/WSS endpoint is available. No Termux or phone-side command is required at this stage.

No production host, endpoint, TLS certificate, backup destination, Firebase project or credentials were fabricated or requested. ZERO COST; no deployment, no paid service, no `main` modification.


## Batch 62J-76 — exact-head verification and adjacent Gate 31/38 boundaries

Source/test HEAD 57b918feafd1b259b008b5efe1272199a29facff passed Automated Tests [44876347017](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347017), CodeQL [44876347037](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347037), Full Git History Secret Audit [44876347101](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347101), and Android debug APK build [44876347021](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44876347021). Frontend 252/252 tests across 29 files; backend 1,249 passed in 50.02 seconds. The Android artifact is a CI build only, not device acceptance.

WebSocket repository/CI failure-matrix status remains complete for its defined automated scope. Production acceptance remains unavailable because no active backend host or public HTTPS/WSS endpoint exists. Do not infer production acceptance from the CI Redis service or container smoke.

Gate 31 remains open: repository encryption is AES-256-GCM/PBKDF2-based, but there is no independently controlled off-host destination or separate recovery-key custody. Gate 38 remains open: HTTP metrics are bounded and process-local, incident records persist in local SQLite, but central collection/dashboard, cross-worker aggregation, metrics retention/rotation, WebSocket telemetry and independent operator notification remain absent. The new Gate 38 runbook documents these boundaries.

Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35 and 39 are host/owner-verification-only 🟨🟩; Gates 20, 25, 31, 36 and 38 remain 🟧. Stage 1 is 30/40 = 75% provisional; overall project remains unscored. ZERO COST; no host, credentials, deployment, Termux or device operation.


## Batch 62J-77 — exact-head WebSocket/indicator acceptance checkpoint

Source/test HEAD e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8 passed Automated Tests [44877470829](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470829), CodeQL [44877470826](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470826), Full Git History Secret Audit [44877470841](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470841), and Android debug APK build [44877470773](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44877470773). Frontend 253/253 tests across 29 files; backend 1,249 passed in 48.11 seconds. Backend container build, Redis shared-guard/persistent-volume smoke and Trivy scan/export all succeeded.

SMA raw rolling-sum intermediate overflow was corrected using normalized window means; tests cover finite MAX_VALUE means and large cancellation. Full details are in docs/WORK_CYCLE_2026-11-21_BATCH62J77_NORMALIZED_SMA_AND_ACCEPTANCE.md and docs/INDICATOR_PROGRESS_LEDGER.md.

Repository WebSocket automated scope remains complete. Production acceptance remains blocked by absent owner-controlled host/public HTTPS-WSS endpoint and missing real production Redis/snapshot receipts. Gate 10 remains 0/10 formally closed. Gates 8, 30, 34, 35, 39 are 🟨🟩 host/owner-verification-only; Gates 20, 25, 31, 36, 38 remain 🟧. Stage 1 is 75% provisional; overall project remains unscored. ZERO COST; no host, credentials, deployment, Termux or device operation.


## Batch 62J-79 — WebSocket lifecycle metrics extension (21 November 2026)

- `backend/app/observability.py` now includes `WebSocketMetrics` and `WebSocketMetricsMiddleware`, scoped only to `/ws/market-data`.
- Captured fields: started, active, completed, accepted, peer disconnect count, five fixed close-code classes and cumulative duration. No payload/header/user data is read.
- Existing bearer-protected `/internal/metrics` response now includes a `websocket` object alongside HTTP metrics. No new public route.
- Tests cover accepted/closed lifecycle, peer disconnect and route isolation.
- The new metrics are process-local and reset at process start. They are not central telemetry, durable retention or an operator dashboard. Gate 38 remains 🟧 OPEN.
- Source/test HEAD: `2274f9adc5ac9907ea508800a2d962d9a7c14a84`. Frontend/backend tests and CodeQL analyses passed in the current run; remaining Automated Tests workflow steps were still running at documentation time. Full Git History Secret Audit passed. Exact links: [Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262277), [CodeQL](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262276), [Secret Audit](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44894262301).
- No WebSocket protocol, auth, replay, snapshot or market-data payload contract was changed. No public WSS/production acceptance claim is made.


## Batch 62J-88 — exact-head CI reconciliation (21 November 2026)

Repository-side WebSocket failure-matrix scope remains complete. Exact-head Automated Tests at `8424e5eefeecbd06c6534bc34d166f4749ba4055` passed all 35 workflow steps, including 1,268 backend tests, backend container build, ephemeral Redis shared-guard/persistent-volume smoke and Trivy image scan/report export. CodeQL and Full Git History Secret Audit also passed. The process-level metrics and read-only collector additions do not alter WebSocket protocol, transport, auth, replay, cursor, gateway or Redis market-data path. Public WSS, production snapshot receipts, owner-host Redis TLS/ACL/persistence/failover and browser/Android WebView acceptance remain external host gates. Gate 36 remains 🟧 OPEN.


## Batch 62J-92 — WebSocket acceptance reconciliation

Exact HEAD `427e5952d2f209ae1f40405223d8d0a4c7d8408c` passed Automated Tests [44905839386](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839386), CodeQL [44905839403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839403) and Full Git History Secret Audit [44905839442](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44905839442). Backend container build, ephemeral Redis shared-guard/persistent-volume smoke and Trivy scan/report also passed. The Gate 38 app-level isolation test confirmed that a failing metrics collector does not block authenticated WebSocket status delivery. No WebSocket protocol, transport, auth, replay, cursor, gateway or Redis market-data data-path change was made.

This does not close Gate 36: public HTTPS/WSS reverse proxy, certificates, owner-host Redis TLS/ACL/persistence/failover, snapshot distribution/installation receipts and real browser/Android WebView acceptance remain host-gated.


## Batch 62J-93 — WebSocket/Gate 38 exact-head reconciliation (21 November 2026)

Exact source/test HEAD `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb` passed Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436), CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400) and Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397). Backend tests: 1,271 passed; frontend: 255/255. The new SQLite batch-read optimization affects only metrics aggregation. No WebSocket protocol, transport, authentication, replay, cursor, gateway, Redis market-data path or message payload changed. Gate 38 app-level isolation still proves the metrics collector can degrade without blocking authenticated WebSocket status.

Gate 36 remains 🟧 OPEN for owner-host public HTTPS/WSS reverse proxy/certificate, production Redis TLS/ACL/persistence/failover, snapshot installation receipts and real browser/Android WebView acceptance.


## Batch 62J-126 — owner-host acceptance evidence boundary audit (22 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Parent HEAD:** `5b0cc02be04efbef3971aa313836eb171e877117`  
**Exact-parent CI:** Automated Tests [44986957808](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986957808) SUCCESS; CodeQL [44986957788](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986957788) SUCCESS; Full Git History Secret Audit [44986957739](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44986957739) SUCCESS. The first two were polled to completed jobs; all three target `5b0cc02be04efbef3971aa313836eb171e877117`.

### Additional owner-host evidence review

- **Gate 30 — live backup/restore:** repository implementation includes SQLite Online Backup API, integrity and foreign-key checks, encrypted backup with ciphertext-integrity authentication, restore to a new database path rather than overwriting the active database, and hash/schema/row-count/domain validation. The restore drill can validate registry, entitlement, alert, coverage, OHLCV and outbox records. This is repository/test evidence only; no owner-host backup artifact or live production restore/readback has been supplied.
- **Gate 31 — off-host backup/key custody:** encryption and fresh-path restore checks do not prove an independently controlled off-host destination, separate recovery-key custody, or successful recovery using that separately held key. Gate remains open.
- **Gate 38 — observability:** current metrics are process-local and measured since process start. No evidence of a central retained dashboard, external notification route, or operator-facing disk-pressure dashboard was found in the reviewed implementation. Same-process counters and synthetic benchmarks do not establish cross-restart retention or production monitoring.
- **Gate 39 — alert delivery:** observed operational alert sink is local logging. No evidence of remote delivery, named human acknowledgement, escalation receipt or a completed operator recovery drill. Keep lifecycle/logging tests separate from real notification acceptance.
- **Android acceptance:** CI exercises host-side preflight and immutable preview-publisher contracts only. It does not launch an Android device/WebView or prove foreground/background, process death, network handover, reconnect/replay or duplicate suppression on a real device.
- **Architecture build coverage:** the reviewed backend container workflow builds `linux/amd64`. No multi-platform Buildx manifest or ARM64 build/smoke evidence was established. ARM64 remains unverified; do not claim support based on the amd64 Trivy report.

### WebSocket gate disposition

These findings do not close any production gate. Gate 25 remains open for authenticated owner-host snapshot transfer, independently authenticated gateway receipts, byte/hash custody and exact generation/high-water alignment under real Redis persistence/restart/failover. Gate 36 remains open for verified public HTTPS/WSS, trusted TLS/reverse proxy, real Firebase and entitlement E2E, real browser/Android lifecycle tests, network-interruption recovery, replay/resnapshot/duplicate suppression and production operator evidence. Gate 38 and Gate 39 remain open for real retained dashboards/alerting and externally delivered, acknowledged/escalated alerts.

**Gate 10: 0/10 formally closed. Stage 1: 30/40 = 75% provisional.** No Stage 2 transition. CI green is not owner-host production acceptance.

### Safe next sequence

1. Continue source/test audit of backup key lifecycle and alert/event boundaries; do not request or expose secrets.
2. Define a zero-cost, local-only acceptance harness for restore and monitoring contracts if it can run entirely in CI without new external accounts or services.
3. Keep real off-host recovery, public WSS, Firebase project and device acceptance as owner-operated gates; do not provision a host or create accounts.
4. Review ARM64 feasibility from workflow and dependency constraints before changing CI. Do not add paid runners or services.

### Indicator reconciliation

No indicator source, tests, formulas, hook, renderer or chart UI changed. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint remains 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps remain 🟥 unimplemented. No indicator progress credit or aggregate percentage is assigned. Preserve warm-up nulls, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF standard candle spacing.

### Cost and change boundary

ZERO COST. Documentation-only; no runtime source, tests, workflows, deployment, cloud resource, domain, account, production credential, Android device action or Termux work. `main` untouched.

## Batch 62J-127 — operator escalation and notification-boundary audit (22 November 2026)

**Parent:** b7d0482ff8fa5906c006460583ad3b175f4c282c  
**Exact-parent CI:** Automated Tests [44987388625](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388625) SUCCESS; CodeQL [44987388511](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388511) SUCCESS; Full Git History Secret Audit [44987388505](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987388505) SUCCESS.

### Corrected notification and operator-response boundary

- **User price-alert push is implemented as a distinct path:** owner-scoped FCM registration and fan-out use the durable price-alert trigger outbox. Device tokens are encrypted at rest with AES-256-GCM and owner/installation associated data; startup requires an owner-injected 32-byte key from a protected absolute-path regular file with group/other permissions denied. Production sender initialization uses Firebase Admin Application Default Credentials (ADC). Delivery is at-least-once, not exactly-once; Android event-ID deduplication remains required. These are code-path/test findings, not proof of successful delivery to the owner's live Firebase project or real devices.
- **Operational incident response is separate:** LocalAlertReporter writes sanitized local logs and an optional persistent SQLite incident journal. The journal deduplicates active fingerprints, retains resolved rows for 30 days, bounds capacity, and supports open/acknowledged/resolved state. Acknowledgement currently records the generic actor "operator", not a verified individual operator identity.
- **Escalation exists but is not notification delivery:** the application runs an escalation loop every 15 seconds and escalate_due advances up to three levels; the loop emits a local structured log event. It does not send an email, SMS, FCM operator push, webhook or paging event. Thus no external receipt, human acknowledgement or escalation chain is proven.
- **Internal operator endpoints exist:** incident list/acknowledge/resolve routes are gated by an injected bearer token. Their presence does not constitute an operator dashboard, authenticated individual attribution, remote alert delivery or an on-call response drill.
- **Metrics nuance:** /internal/metrics exposes process-local HTTP/WebSocket counters and can additionally include a same-host SQLite collector aggregation. The collector is bounded, uses 15-minute buckets and 7-day retention, and is best-effort local telemetry. There is no verified central dashboard, independent off-host metrics retention, external alert sink or operator paging integration. The separate alert-delivery status endpoint explicitly reports process-local-since-start scope.

### Acceptance implications

- Gate 20 still requires real Firebase project token validation/revocation and entitlement grant/revoke/renew E2E. The code's ADC initialization and test doubles do not close it.
- Gate 38 remains open for owner-host operational visibility, retained dashboard, disk-pressure behavior and monitoring across restart/failure.
- Gate 39 remains open for a real externally delivered operator alert, verified recipient, human acknowledgement, escalation receipt and documented response drill. Local escalation log entries are not external alerts.
- Gate 8 remains open for owner-host secret injection, permissions, rotation and log-redaction acceptance, including the FCM key and runtime ADC identity. A protected file loader is a source control, not owner-host evidence.
- Gate 10 remains **0/10 formally closed**; Stage 1 remains **30/40 = 75% provisional**. No Stage 2 transition.

### Scope and indicator reconciliation

No WebSocket runtime code, FCM runtime code, operator routes, tests or workflows changed. No indicator implementation, formula, hook, renderer, UI or tests changed. SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation; Footprint 🟧 synthetic/reference-gated; Heatmap and Liquidation Maps 🟥 unimplemented. No indicator progress credit or aggregate percentage. Preserve warm-up nulls, source-index alignment, no future-candle repaint, stale-series clearing and Footprint OFF standard candle spacing.

ZERO COST; documentation-only; main untouched.


## Batch 62J-129 — Gate 25 checkpoint digest precision correction (22 November 2026)

Read-only review of `backend/app/ohlcv_redis_gateway_runtime.py`, `backend/app/ohlcv_store.py` and `backend/tests/test_ohlcv_redis_gateway_runtime.py` found that the durable replica checkpoint stores source ID, replica ID, applied cursor, snapshot generation, retention floor and schema/protocol versions, but **does not store snapshot SHA-256**. The gateway runtime compares source/generation/cursor with that checkpoint and returns the installer-provided digest after checking its lowercase-hex shape. The unit test compares that returned digest with the source export metadata, but does not show digest persistence in the checkpoint. Therefore earlier wording that the gateway compares the digest against its durable checkpoint is inaccurate and is corrected by Batch 62J-129.

The verified installer callback still calls the store's snapshot verifier/installer; this is a trust boundary. No exploit is asserted. Persisting a digest would require a design decision covering checkpoint schema migration and the meaning/lifecycle of a snapshot-only digest after stream updates. Gate 25 remains OPEN pending this design decision plus authenticated owner-host transfer, independent gateway receipts and owner-host Redis operational evidence.

Batch 62J-129 also introduced IP3S, a per-cycle delivery-quality score. Its 58/100 is not project completion and grants no indicator implementation credit. See `WORK_CYCLE_2026-11-22_BATCH62J129_GATE25_GATE36_IP3S.md` for the exact scoring rubric and Gate 36 evidence matrix.


## Batch 62J-130 — Gateway snapshot digest anchoring and overall project progress (22 November 2026)

The durable `ohlcv_replica_checkpoint` schema stores source ID, replica ID, applied cursor, snapshot generation, retention floor, bar-retention metadata and schema/protocol versions. It does **not** store snapshot SHA-256. The gateway installer return value is checked for 64-character lowercase-hex format and propagated; source/generation/cursor are compared with the durable checkpoint. Do not describe the installer digest as being compared with a digest in that checkpoint. The canonical snapshot exporter/verifier independently computes and validates SHA-256 over snapshot contents. Any persistent digest field requires an explicit decision about immutable installation provenance, stream-update lifecycle, schema migration and compatibility. No source edit was made.

Overall project progress remains **NOT SCORED** because there is no approved six-stage weighting/denominator. Stage 1 is **30/40 = 75% provisional**, Gate 10 is **0/10 formally closed**, and Stages 2–6 are NOT SCORED. Batch IP3S is separate from project completion. Gate 25 and Gate 36 remain OPEN. See `WORK_CYCLE_2026-11-22_BATCH62J130_OVERALL_PROGRESS_WEBSOCKET_ACCEPTANCE.md`.


## Batch 62J-145 — real TLS/WSS and multi-user disconnect integration (22 November 2026)

Source/test HEAD: f8e41ad68656e82a82d30cf40f720f3ec98ac337.

A new backend integration test starts a real Uvicorn loopback server with an ephemeral X.509 CA/server certificate, connects using the websockets client over wss://, verifies TLS and the HTTP Upgrade, accepts the configured HTTPS Origin, rejects a disallowed Origin with HTTP 403, and rejects a client that does not trust the test CA. It authenticates using the non-production test-token path, subscribes to an exact canonical OHLCV series, receives a four-bar snapshot, and completes the application text ping/pong exchange.

The same TLS listener also tests two distinct identities with separately granted entitlement. Both subscriptions become active; after User B disconnects, the test waits for ASGI final cleanup, verifies the subscription count returns from two to one, and confirms User A still receives pong. The separate TestClient multi-user regression remains.

Important limitation: this test uses the backend's test-only legacy token authentication path. It does not yet exercise the production HTTPS Firebase ID-token to one-time ticket endpoint to ticket-authenticated WSS handshake/renewal over the same TLS listener. That is the next implementation target.

Exact-HEAD CI on f8e41ad:
- Automated Tests 45005536779: SUCCESS; 1,297 passed, 1 skipped, 6 warnings.
- CodeQL 45005536789: SUCCESS.
- Full Git History Secret Audit 45005537134: SUCCESS.
- OCI ARM64 readiness 45005536741: SUCCESS.

The Automated Tests workflow also passed frontend tests/build, Redis TLS CA/hostname/ACL/AOF fixture, synthetic SQLite outbox and metrics benchmarks, backend dependency audit, backend image build, shared Redis/persistent-volume smoke, and Trivy HIGH/CRITICAL image scan. The Trivy report showed zero findings for scanned Alpine 3.24.4 OS and Python package targets. Container smoke verified UID/GID 10001, persistent volume ownership, SQLite integrity/restart, Redis AOF/ACL recovery, and fail-closed API behavior during Redis outage.

This remains repository CI/local synthetic integration evidence, not a public WSS endpoint, production Firebase project, OCI deployment, owner-host Redis acceptance or Android WebView acceptance. Gate 10 remains 0/10 formally closed; Gates 25, 36 and 38 remain OPEN. ZERO COST; main untouched; no deployment or production credentials. See WORK_CYCLE_2026-11-22_BATCH62J145_REAL_TLS_MULTI_USER_WEBSOCKET.md.


---

## Batch 79 — Production WebSocket runtime wiring audit (25 November 2026)

Source audit report: [Batch 79 production runtime wiring and Gate 25 composition](WORK_CYCLE_2026-11-25_BATCH79_PRODUCTION_WEBSOCKET_RUNTIME_WIRING_AUDIT.md). Audited documentation HEAD before this report: `114d8464e085977aba2d95b3581ee49a95990c18`; last source/test SHA: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`.

**Newly isolated root cause:** the individual publisher, Redis replica consumer, SQLite replica store, Ed25519 snapshot attestation, Firebase identity, single-use ticket and WebSocket route primitives exist. However, the stock Docker command starts `uvicorn app.main:app`, and module-level `app = create_app()` supplies neither `replica_runtime_factory` nor `publisher_runtime_factory`. With no replica factory, lifespan starts the provider manager instead of the replica consumer/worker; with no publisher factory, the source relay is not started. The WebSocket handler falls back to the local source SQLite/in-memory pipeline when no replica store is injected. This is the concrete production runtime-composition gap. Source and gateway factories are intentionally mutually exclusive and must remain separate roles.

**Gate 25:** Ed25519 signed snapshot verification and atomic replica installation primitives exist, but the default app does not assemble owner-pinned trusted keys, expected source identity, signed snapshot transfer/install, dedicated gateway DB, consumer, lease and runtime lifecycle. The production runtime contract and owner-host evidence remain OPEN. Local replica cursor and Redis XACK must not be mislabeled as the owner-accepted per-gateway durable high-water receipt/ACK.

**CI boundary:** exact source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has recorded Automated Tests 41/41 (1,426 passed, 1 skipped, 6 warnings), CodeQL 16/16, OCI ARM64 7/7, Secret Audit 6/6 and dedicated Redis TLS 1 passed. Documentation HEAD `114d8464e085977aba2d95b3581ee49a95990c18` has six documentation-only commits ahead of that source SHA and no source/runtime diff; the docs-only commit has no CI runs/status because of `[skip ci]`. No new source CI is claimed.

**Progress:** Stage 1 30/40 = 75% provisional 🟨; Gate 10 0/10 formally closed 🟥 (8, 20, 25, 30, 31, 34, 35, 36, 38, 39). Stage 2 🟦 preparatory only; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project and IP3S ⚪ NOT SCORED. Indicator inventory unchanged: SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Hook 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟥 OPEN. Focused declarations 28 (21 calculation + 7 hook), not completion. No indicator source/UI changes.

**Next order:** define strict source/gateway role configuration; implement source factory; implement gateway factory with signed snapshot install before Redis initialization; add multi-process source-to-two-gateway integration and restart/fencing tests; prove per-gateway durable receipt/high-water ACK; then public Cloudflare WSS/browser/Android E2E; then owner-host backup/restore/monitoring acceptance. Keep Redis destructive retention blocked until ACK acceptance.

Controls unchanged: ZERO COST, `main` untouched, Vercel deferred, no duplicate Cloudflare resources, no paid data/hosting/monitoring/backup, planning target around 24 December 2026.
