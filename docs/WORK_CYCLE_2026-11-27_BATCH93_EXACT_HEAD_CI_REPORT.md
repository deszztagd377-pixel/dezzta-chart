# DEZZTA CHART — Batch 93 exact-head replay/resume/receipt CI report

**Date:** 27 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Exact source/test SHA:** `05dd055bbf54e551907e2b4195c169edb591bcac`  
**State:** replay, retention and synthetic consumer receipt persistence GREEN for tested proof scope; production identity and edge integrations remain YELLOW  
**Cost/deployment:** ZERO COST; no production deployment or new paid resource.

## Exact-head CI — 4/4 terminal SUCCESS

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [45922189465](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45922189465) | SUCCESS |
| CodeQL Security Analysis | [45922189575](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45922189575) | SUCCESS |
| Full Git History Secret Audit | [45922189550](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45922189550) | SUCCESS |
| OCI ARM64 Image Readiness | [45922189496](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45922189496) | SUCCESS |

All four required workflows completed on the same source/test SHA. No required workflow remains in progress or failed for this SHA.

## Runtime and build evidence

- Worker Node proof: **38/38 passed**
- Miniflare pinned workerd integration: **1/1 passed**, including auth, snapshot, live fan-out, replay frame contract, retention compaction/resnapshot, replay/live race and consumer receipt persistence checks
- Durable Object hibernation/alarms/per-series runtime: **18/18 passed**
- Frontend Vitest: **35 files / 332 tests passed**
- Backend pytest: **1,435 passed / 1 skipped / 6 warnings**
- Dedicated Redis TLS integration: **1 passed**
- Frontend production build and source/bundle secret scans: passed
- Backend container build, shared-Redis/persistent-volume smoke test and vulnerability scan: passed
- OCI ARM64 build/smoke, CodeQL Python and JavaScript/TypeScript, and full reachable-history secret audit: passed

The skipped pytest case is the optional Redis TLS integration case in the main backend suite; the dedicated TLS integration fixture passed separately. The six warnings are recorded, not suppressed.

## Correctness changes verified

1. Worker replay emits frontend-supported `replay_started` → persisted `market_data.ohlcv.update` frames → `replay_complete`.
2. Explicit numeric `fromSequence` / `throughSequence` bounds are separate from decimal-string cursors. Frontend guard initializes from the explicit baseline and verifies terminal watermark.
3. Replay is cursor-exclusive and bounded to 100 events / 65,536 UTF-8 bytes per page, with at most 10 pages per subscribe. Over-budget backlogs request a fresh snapshot.
4. Retention compaction atomically deletes events and advances retention floor.
5. Real-workerd race test reconnects from cursor 50 while sequence 52 commits; exact ordered delivery [51,52] is asserted with no missing or duplicate events.
6. Consumer receipt transaction validates the persisted event digest, generation, high-water and retention boundary. Identical retry is idempotent; regression and digest mismatch are rejected.

## Validation corrections

- Corrected stale snapshot cursor expectation after race advanced high-water to 52.
- Corrected stale gap fixture: after sequence 52, sequence 53 is contiguous; gap case uses 54.
- Replaced one-shot race-test message listeners with a persistent message queue because workerd can synchronously deliver all replay frames before the test awaits the next frame.
- Cross-file review aligned Worker replay frames with the frontend's established replay_started/update/replay_complete protocol.
- Corrected candidate passed all four exact-head workflows.

## Remaining YELLOW exit criteria

- Real-workerd seeded legacy-KV bootstrap, interrupted initialization and DO eviction persistence.
- Real-workerd multi-page replay and >10-page snapshot fallback.
- Concurrent replay/compaction and injected rollback/corruption failures.
- Owner-authenticated stable consumer identity; current proof ACK consumerId is caller-supplied and cannot be used as production identity.
- Production WebSocket ACK/RESUME, public WSS, provider integration and Android device E2E.

## Android build

Zero-cost CI produced and verified a debug APK on frontend source SHA `030fca35477e1f5e3fbc0b2bec2c298b027d4775`, run [45921041784](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921041784), SUCCESS. App source was unchanged by later commits through the exact source/test SHA above. This is not release signing, publication or device E2E.

**Target:** approximately 24 December 2026. **main remains untouched.** Synthetic proof is not production market data.
