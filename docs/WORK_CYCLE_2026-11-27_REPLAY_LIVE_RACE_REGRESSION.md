# Replay-to-live race regression — 27 November 2026

**Branch:** `phase-2/market-data-foundation`  
**Base:** `d952d04b377641e9404330013dd9f400ac1c57db`  
**State:** candidate test added; exact-head CI pending  
**Cost:** ZERO COST; local workerd/Miniflare only.

A real-workerd regression reconnects with cursor 50 while event 52 is committed concurrently. It accepts only exactly ordered delivery [51, 52]: both in replay, or event 51 in replay followed by event 52 via live fan-out. Missing, duplicate or reordered events fail the assertion.

The test does not claim the entire production WebSocket stack is accepted. Multi-page >10 fallback, failure injection, ACK/receipts/RESUME protocol, public WSS and Android E2E remain YELLOW.

Prior replay/retention exact-head CI remains valid only for source/test SHA `17857c948cb932d5465eaca1e46dae15ce6c0344`; this candidate requires fresh exact-head CI.
