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
