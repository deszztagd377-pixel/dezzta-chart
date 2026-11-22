# Batch 62J-128 — WebSocket snapshot acceptance and complete indicator progress reconciliation

**Date:** 22 November 2026  
**Branch:** \`phase-2/market-data-foundation\`  
**Audited baseline:** \`54f0d1c9908b19e3b3a04974e52c4e84500db57d\`  
**Scope:** source/test read-only audit plus this documentation record. No runtime implementation changes.

## 1. Exact-baseline CI disposition

All three workflows completed successfully on the exact audited SHA \`54f0d1c9908b19e3b3a04974e52c4e84500db57d\`:

- Automated Tests [run 44987898058](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987898058): **SUCCESS**.
- CodeQL [run 44987898130](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987898130): **SUCCESS**.
- Full Git History Secret Audit [run 44987898070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44987898070): **SUCCESS**.

The Automated Tests job reached and passed backend dependency installation, isolated Redis TLS CA/hostname fixture, backend tests, synthetic SQLite outbox and metrics benchmarks, backend container build, shared-Redis-guard/persistent-CI-volume smoke, Trivy scan/report and dependency-audit enforcement. These are CI-runner/fixture results, not owner-host or public-production acceptance. The run is now complete; no active CI job blocks a documentation-only commit.

## 2. Gate 25 — snapshot export, verification, gateway install and watermark alignment

### 2.1 Repository behavior verified

Reviewed source:
- \`backend/app/ohlcv_store.py\`
- \`backend/app/ohlcv_redis_runtime.py\`
- \`backend/app/ohlcv_redis_gateway_runtime.py\`
- \`backend/app/ohlcv_redis_publisher.py\`
- \`backend/app/ohlcv_redis_consumer.py\`
- \`backend/app/ohlcv_redis_replay.py\`
- \`backend/app/ohlcv_replica_bridge.py\`

Reviewed tests:
- \`backend/tests/test_ohlcv_store.py\`
- \`backend/tests/test_ohlcv_redis_runtime.py\`
- \`backend/tests/test_ohlcv_redis_gateway_runtime.py\`
- \`backend/tests/test_ohlcv_redis_publisher.py\`
- \`backend/tests/test_ohlcv_redis_replay.py\`
- \`backend/tests/test_ohlcv_replica_bridge.py\`

The source export path:
1. Opens one SQLite read transaction, pinning a consistent source read view while retained bars are streamed in bounded batches.
2. Exports every retained series into a temporary JSONL file and atomically publishes the completed file only after its manifest is flushed.
3. Records format/version, source ID, unique generation ID, retention floor and global \`high_water\`.
4. Calculates SHA-256 over the canonical header and bar records; the footer records row count and digest.
5. \`verify_global_snapshot\` checks envelope/version, source/generation fields, cursor and retention bounds, record ordering, row count, and recomputed SHA-256. It rejects trailing data after the manifest.

The replica installer writes the snapshot and its checkpoint as an atomic installation; tests cover successful install, wrong-source rejection, stale-cursor rejection, semantic-failure rollback, and no outbox echo. Query/hydration paths read bars and checkpoint from one SQLite read view. The bridge verifies that the exposed snapshot cursor/high-water agree before registering the stream hub, avoiding a split bars-versus-watermark boundary.

The publisher checkpoint is durable and fenced. It advances only one contiguous cursor after the corresponding Redis append is confirmed, checks deterministic Redis Stream IDs, and uses compare-and-swap against the expected prior cursor. Recovery from uncertain append outcome verifies the deterministic entry rather than blindly advancing. A retained-history gap requires a fresh snapshot rather than silently skipping cursors.

The source runtime requires an injected snapshot verifier before publisher activation. Its returned evidence must bind source ID, stream key, snapshot generation, cursor, SHA-256, the required gateway ID set, and one matching receipt per gateway. Each receipt is checked against the same source, stream, generation, cursor and digest before Redis client construction.

The gateway runtime requires an injected snapshot installer. It checks that the callback reports installation and that returned source/generation/high-water/digest metadata match the durable local replica checkpoint before constructing its Redis client and consumer. The consumer uses generation-scoped groups, contiguous cursor checks, apply-before-ACK, duplicate/conflict checks and resnapshot-required behavior for gaps or trimmed history.

### 2.2 What tests prove — and do not prove

Repository tests prove local snapshot consistency, SHA-256 integrity validation, source/generation/cursor/hash field matching, rejection of mismatched gateway receipt metadata, and fail-closed ordering before Redis client construction. Runtime tests use temporary local files, test doubles and synthetic receipt data. They do **not** establish that a remote gateway's receipt was cryptographically signed, that the callback authenticated the gateway identity, or that a production transfer channel delivered the exact file to the claimed gateway.

A matching SHA-256 proves byte equality against the supplied digest; it does not establish who supplied the digest or who issued a receipt. The host-supplied callbacks are therefore explicit trust boundaries. The owner/operator must independently authenticate the transfer, verify the exported file with \`SQLiteOhlcvStore.verify_global_snapshot()\`, authenticate each gateway receipt, and preserve evidence for each required gateway.

The source export documentation also notes that long-running WAL snapshot exports can grow the WAL. Owner-host disk-pressure and monitoring behavior remain operational acceptance work.

### 2.3 Gate 25 acceptance checklist — still OPEN

- [x] Repository snapshot export pins a consistent SQLite read view.
- [x] Snapshot manifest contains source/generation/watermark/retention metadata and SHA-256.
- [x] Local verification checks canonical contents, row count and digest.
- [x] Replica install and checkpoint are atomic; wrong source/stale cursor/semantic failure are rejected.
- [x] Publisher checkpoint is durable, fenced and contiguous.
- [x] Source activation validates matching evidence fields for every configured gateway.
- [x] Gateway activation checks installed metadata against its durable local checkpoint before Redis construction.
- [ ] Owner-host authenticated snapshot transport and gateway identity authentication.
- [ ] Independently authenticated installation receipt from every required gateway.
- [ ] Evidence custody proving each gateway installed the same source, generation, exact high-water cursor and SHA-256.
- [ ] Real Redis TLS CA/hostname and ACL validation on the owner host, including persistence, restart and failover.
- [ ] WAL/disk-pressure behavior and recovery validated on the intended persistent host.

**Disposition:** Gate 25 remains OPEN. The repository's shape/hash/checkpoint validation is substantial, but it is not a substitute for authenticated remote receipts and owner-host evidence.

## 3. Replay and client handoff boundaries

The replay implementation scans the global cursor interval, including events for unrelated series, while returning only the requested exact series. It uses the replica's durable applied cursor as a fixed upper watermark. Missing/trimmed history, invalid or expired client cursors, a cursor ahead of the replica, malformed entries, non-advancing pages or configured work caps result in a resnapshot-required response; the implementation does not silently jump over a cursor gap.

The replica bridge reads bars and checkpoint atomically and registers the matching hub watermark. Existing tests cover concurrent source writes during snapshot export, snapshot/checkpoint consistency, cursor gaps, missing first cursor, replay ending before the watermark, cursor expiry/ahead, unrelated-series global cursor advancement, and duplicate suppression at the bridge.

These are repository and simulated-test results. They do not prove public WSS reverse-proxy routing, trusted public TLS, real network handover, Android WebView process death/background recovery, or real-device duplicate suppression.

## 4. Gate 36 — WebSocket end-to-end acceptance

Previously reviewed client/server behavior remains:
- HTTPS ticket exchange uses a verified Firebase principal; the Firebase ID token is not placed in a WSS URL or raw WebSocket authentication frame.
- Tickets are short-lived and single-use; server checks Origin policy and exact-series/canonical-instrument entitlement separately.
- Browser tests cover ticket authentication, subscribe, snapshot/update, durable cursor replay, renewal acknowledgement, heartbeat/error cleanup and reconnect supervisor behavior.
- Client supervisor obtains a fresh Firebase ID token on reconnect, replays from the last validated cursor and requests snapshot recovery after sequence gaps.
- Chart lifecycle hooks online/offline and visibility changes, stopping the stream when hidden/offline and cleaning up on unmount.

The ticket binds subject and purpose; series authorization remains separate and the ticket does not itself bind series or Origin. This remains a threat-model review item, not an assumed defect or a change made by this batch.

Gate 36 remains OPEN pending verified public HTTPS/WSS endpoint, reverse proxy and TLS, live Firebase project validation, actual browser and Android WebView lifecycle tests, real network interruption/handover, replay/resnapshot and duplicate suppression, and operator-visible failure evidence.

## 5. Complete indicator progress status — 22 November 2026

**No indicator implementation progress was earned in this batch.** No indicator source, formula, test, hook, chart renderer, UI, toggle or workflow changed. CI success and documentation are not implementation progress.

| Indicator/component | Current status | Verified foundation | Remaining work / acceptance |
|---|---|---|---|
| SMA20 | 🟨 Foundation | 20-close simple moving average; first valid output at source index 19 | Full chart integration, visibility toggle, style/configuration, current value/legend, stale clearing and rendering/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/21; first valid output at index 19 | Full chart integration and UI/rendering/lifecycle acceptance |
| RSI14 Wilder | 🟨 Foundation | 14 close-to-close changes; first valid output at index 14; Wilder smoothing foundation | Full chart integration, bounded 0–100 display, levels/configuration, legend/current value and tests |
| MACD12/26/9 | 🟨 Foundation | MACD line first valid at index 25; signal and histogram first valid at index 33 | Full chart integration, three-series rendering, zero line, style/configuration, legend/current values and tests |
| Bollinger Bands 20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid output at index 19 | Full chart integration, upper/middle/lower rendering, fill/style/configuration, legend/current values and tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot and candle-index-aligned calculation output | Connect to chart lifecycle and study registry; ensure identity/timeframe reset, stale clearing, errors/loading and multi-study rendering |
| Footprint | 🟧 Synthetic educational accumulator | Synthetic accumulator foundation only; not a production market-by-price feed or finished chart study | User must provide Footprint visual reference image(s); create and review scoped blueprint before visual implementation; then real bid/ask data semantics, cluster layout, toggles, values, legends and tests |
| Heatmap | 🟥 Not implemented | No accepted visual/runtime implementation | User reference image and reviewed blueprint before implementation; define data semantics, rendering, lifecycle and acceptance tests |
| Liquidation Maps | 🟥 Not implemented | No accepted visual/runtime implementation | Define reliable liquidation data source and semantics, user-approved scope/blueprint, then rendering and acceptance tests |

### 5.1 Calculation and data-integrity invariants

These requirements remain mandatory for all applicable studies:

1. Warm-up periods return null/unavailable values, never fabricated zeroes.
2. Outputs remain aligned to original candle/source indices; no index shifting when warm-up values are absent.
3. No future-candle lookahead or repainting.
4. Candle identity, instrument, timeframe or source changes must clear stale indicator series before new values are shown.
5. Invalid, incomplete or stale market-data snapshots must not be presented as current indicator values.
6. Formula semantics and seed behavior must be deterministic and covered by unit tests.
7. Indicator OFF must remove its own visual output without corrupting the base chart or another study.

### 5.2 Footprint-specific chart behavior

- Footprint OFF must preserve the ordinary candlestick chart layout and normal candle spacing.
- Only an explicit user action turning Footprint ON may switch to the dedicated spaced-candle/cluster layout.
- The ON layout must allocate enough horizontal space for bid/ask or footprint cells to remain legible.
- Do not start Footprint visual implementation before the user supplies the relevant reference image(s) and the blueprint is reviewed.
- The same reference-first and reviewed-blueprint gate applies to Heatmap where the user's preferred reference is required.

### 5.3 Indicator completion criteria

A foundation label is not a completed study. A study is not accepted until its formula and warm-up behavior are tested, data alignment and stale-state behavior are verified, chart integration is complete, controls and legends/current values are present, visual behavior is reviewed against the approved scope/reference, and rendering/lifecycle tests pass. The Shared Indicator Hook is shared infrastructure, not a sixth completed visual indicator.

No aggregate indicator percentage is published: no approved study weights or denominator exist. Do not convert the count of foundation labels into a project completion percentage. Do not award progress for CI, benchmarks, documentation or unrelated backend/WebSocket work.

## 6. Overall project and stage disposition

- WebSocket Gate 10: **0/10 formally closed**.
- Stage 1: **30/40 = 75% provisional**, not formally exited.
- Stage 2: blocked pending formal Stage 1 exit review and required acceptance evidence.
- Gates 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open for their previously recorded owner-host/production evidence.
- CI ephemeral Redis, CI persistent-volume smoke, local fixtures and simulated browser tests do not close owner-host/public-production gates.
- No production hostname, Redis host, Firebase project, paid service, cloud resource or external account was created.

## 7. ZERO COST and change boundary

This batch is documentation-only. No runtime code, tests, workflows, deployment, paid hosting, domain, cloud resource, account, production credential, Android device action or Termux operation was changed or created. The active branch remains \`phase-2/market-data-foundation\`; \`main\` is untouched.

**Next safe engineering sequence:** retain the green exact-baseline CI record; specify a verifiable owner-controlled receipt format and transport acceptance contract without inventing a signing system; then separately review public WSS/reverse-proxy and real browser/Android acceptance requirements. Keep Gate 25 and Gate 36 open until evidence exists. Indicator implementation remains on hold until the relevant user reference images and reviewed blueprints are available.
