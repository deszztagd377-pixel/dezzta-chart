# Worker/frontend replay contract alignment — 27 November 2026

**Branch:** `phase-2/market-data-foundation`  
**Base:** `27d77f472c0a24370fa46045e957e80f41575d4e`  
**State:** implementation and regression candidate; exact-head CI pending  
**Cost:** ZERO COST; no external service or deployment.

## Defect found

The Cloudflare proof Worker returned a page-shaped `market_data.ohlcv.replay` message. The existing frontend WebSocket client does not accept that shape; it implements `market_data.ohlcv.replay_started`, individual `market_data.ohlcv.update` messages, and `market_data.ohlcv.replay_complete`. Worker-only replay tests therefore did not prove end-to-end protocol compatibility.

The frontend replay guard also used the replay event count as its final numeric sequence watermark, while the synthetic proof sequence and opaque cursor are distinct fields.

## Changes

- Worker emits replay_started with count, cursor bounds and explicit numeric stream-sequence bounds; emits persisted update events individually; then emits replay_complete.
- Frontend accepts explicit fromSequence/throughSequence, validates that the sequence span equals count, initializes its guard from the supplied baseline, and verifies the terminal watermark against throughSequence.
- Legacy replay fixtures without explicit sequence metadata retain the existing compatibility baseline.
- Miniflare verifies real-workerd frame order and the concurrent replay/live handoff; frontend Vitest covers the synthetic sequence/cursor baseline.

## Acceptance

The change remains YELLOW until Automated Tests, CodeQL, Full Git History Secret Audit and OCI ARM64 are terminal SUCCESS on the exact source/test SHA. No public WSS, provider integration, production identity or Android E2E is claimed.


## CI correction — post-race sequence gap fixture

The first integration run exercised the replay frame contract and concurrent handoff through sequence 52. A later legacy gap assertion still attempted sequence 53, which is correctly accepted as the next contiguous event. Updated the negative gap case to sequence 54. No production sequence-validation rule changed. Fresh exact-head CI is required.


## Exact-head verification — 27 November 2026

The aligned Worker/frontend replay contract and race regression passed exact-head CI on source/test SHA `c6097506eade1162859adf4312ed6031e99effae`:
- Automated Tests [45921185878](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185878) — SUCCESS
- CodeQL [45921185890](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185890) — SUCCESS
- Full Git History Secret Audit [45921185892](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185892) — SUCCESS
- OCI ARM64 [45921185920](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45921185920) — SUCCESS

Runtime verification: Worker Node 38/38; Miniflare/workerd 1/1 including replay frame contract and concurrent replay/live race; Durable Object runtime 18/18; frontend Vitest 35 files / 332 tests; backend pytest 1,435 passed / 1 skipped / 6 warnings; dedicated Redis TLS fixture 1/1; frontend build, backend container smoke and vulnerability scan passed.

The debug Android APK was built successfully by zero-cost CI at `030fca35477e1f5e3fbc0b2bec2c298b027d4775` (run 45921041784). Subsequent changes through the exact tested SHA above were test/documentation-only. No release signing, public WSS, production deployment or Android device E2E is claimed.

Remaining YELLOW items: real-workerd seeded-KV bootstrap/eviction, multi-page replay and >10-page fallback, replay/compaction fault injection, authenticated ACK/receipt identity binding, public WSS and Android device E2E.
