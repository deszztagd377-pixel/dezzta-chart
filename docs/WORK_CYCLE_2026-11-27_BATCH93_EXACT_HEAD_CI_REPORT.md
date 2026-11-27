# DEZZTA CHART — Batch 93 exact-head replay/resume CI report

**Date:** 27 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test SHA:** `c6097506eade1162859adf4312ed6031e99effae`  
**State:** replay/retention core and frontend WebSocket replay contract GREEN for the tested synthetic-proof slice; edge integrations remain YELLOW  
**Cost/deployment:** ZERO COST; no production deployment or new paid resource.

## Exact-head CI — 4/4 terminal SUCCESS

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45921185878](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185878) | SUCCESS |
| CodeQL Security Analysis | [45921185890](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185890) | SUCCESS |
| Full Git History Secret Audit | [45921185892](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185892) | SUCCESS |
| OCI ARM64 Image Readiness | [45921185920](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185920) | SUCCESS |

All four required workflows completed on the same source/test SHA. No required workflow remains in progress or failed for this SHA.

## Runtime and build evidence

- Worker Node proof: **38/38 passed**
- Miniflare pinned workerd integration: **1/1 passed**, including auth, snapshot, live fan-out, durable replay frames, retention compaction/resnapshot and concurrent replay/live handoff
- Durable Object hibernation/alarms/per-series runtime: **18/18 passed**
- Frontend Vitest: **35 files / 332 tests passed**
- Backend pytest: **1,435 passed / 1 skipped / 6 warnings**
- Dedicated Redis TLS integration: **1 passed**
- Frontend production build and source/bundle secret scans: passed
- Backend container build, shared-Redis/persistent-volume smoke test and vulnerability scan: passed
- OCI ARM64 build/smoke, CodeQL Python and JavaScript/TypeScript, and full reachable-history secret audit: passed

The skipped pytest case is the optional Redis TLS integration case in the main backend suite; the dedicated TLS integration fixture passed separately. The six warnings are recorded, not suppressed.

## Correctness changes verified

1. Worker replay emits the frontend-supported `replay_started` → persisted `market_data.ohlcv.update` frames → `replay_complete` sequence.
2. Replay start/complete includes explicit numeric `fromSequence` / `throughSequence`, distinct from decimal-string cursors. The frontend sequence guard initializes from the explicit baseline and verifies the terminal watermark.
3. Replay remains cursor-exclusive and bounded to 100 events / 65,536 UTF-8 bytes per page, with at most 10 pages per subscribe. Over-budget backlogs request a new snapshot.
4. Retention compaction atomically deletes events and advances the retention floor.
5. The real-workerd race regression reconnects from cursor 50 while sequence 52 commits; it asserts exactly [51,52] in order, whether sequence 52 is replayed or arrives through live fan-out.

## Corrections made during validation

- First race-test run exposed a stale snapshot cursor assertion; high-water had correctly advanced to 52. The test expectation was corrected from 51 to 52.
- The next integration run confirmed the replay/race path but exposed a stale sequence-gap fixture; after event 52, sequence 53 is contiguous and valid. The negative gap case was corrected to sequence 54.
- Cross-file review found the original page-shaped replay message did not match the frontend's replay_started/update/replay_complete contract. Worker and frontend were aligned, with a dedicated Vitest case and real-workerd frame assertions.
- The corrected candidate passed all four required exact-head CI workflows.

## Remaining YELLOW exit criteria

- Real-workerd seeded legacy-KV bootstrap, interrupted initialization and DO eviction persistence.
- Real-workerd multi-page replay and >10-page snapshot fallback.
- Concurrent compaction/replay and injected rollback/corruption failures.
- ACK/consumer receipts: define authenticated stable consumer identity first; client-supplied consumerId alone is not production authentication.
- Public WSS, production identity/provider integration and Android device E2E.

## Android build

Zero-cost CI produced and verified a debug APK on source SHA `030fca35477e1f5e3fbc0b2bec2c298b027d4775`, run [45921041784](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921041784), SUCCESS. App source was unchanged by later test/documentation commits through the exact source/test SHA above. This is not release signing, publication or device E2E.

**Target:** approximately 24 December 2026. **main remains untouched.** Synthetic proof is not production market data.
