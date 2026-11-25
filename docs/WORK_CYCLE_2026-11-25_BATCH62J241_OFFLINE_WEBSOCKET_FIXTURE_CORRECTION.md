# Offline WebSocket fixture correction — Batch 62J-241

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent: `d7581d72bfa9b34856c58e9cc807cc5d6ee84c2a`  
Cost: ZERO COST

## Root cause

Automated Tests failed in `test_offline_websocket_demand_is_shared_and_released_on_disconnect` before opening the WebSocket. The fixture passed `session_calendar_id=""` to `CanonicalInstrument`. The canonical identity model treats a supplied empty string as invalid and raised `InvalidCanonicalInstrument: session_calendar_id is required.`

## Minimal correction

The fixture now supplies `session_calendar_id="SYNTHETIC_24X7"`. The WebSocket request remains on `UTC_FIXED_V1` with no calendar ID/version, so the fixture does not bind to a production session-calendar release. Validation rules in production code are unchanged.

## Exact evidence from parent CI

- Automated Tests run: 45532735359 — failure at backend test step.
- Backend pytest: 1 failed, 1,410 passed, 1 skipped, 6 warnings.
- Sole failure: canonical instrument test fixture with empty session calendar ID.
- CodeQL run 45532735397 — success.
- OCI ARM64 Readiness run 45532735559 — success.
- Full Git History Secret Audit run 45532735370 — success.

The correction must be tested on its own exact commit SHA. Parent CI is not carried forward.

## Preserved behavior

- The offline fixture remains the only path that acquires the in-memory provider-demand coordinator.
- Lease acquisition follows mapping, active-instrument, calendar and entitlement validation.
- Route cleanup unsubscribes the stream and releases the lease on disconnect/return paths.
- The route regression continues to check two subscribers sharing one start and the last disconnect causing one stop.
- No live data source, provider SDK, remote adapter or recurring feed is connected.

## Indicator status

No indicator source changed. Current verified foundations remain SMA20, EMA20, RSI14 Wilder, MACD12/26/9 and Bollinger20,2; their chart rendering/integration remains unaccepted. Shared hook integration remains open. Footprint remains synthetic/offline foundation with renderer gated. Volume Profile variants, Heatmap and Liquidation Maps remain open. No aggregate completion percentage is invented.

Numerical invariants remain: SMA/EMA/Bollinger first valid index 19; RSI14 index 14; MACD line index 25 and signal/histogram index 33 under first-valid-MACD seeding; warm-up null; prefix-causal output; timestamps aligned; clear stale series on instrument/timeframe changes.

## Status and constraints

Synthetic route integration: 🟨 pending exact-HEAD CI. External provider lifecycle and provider ACK: 🟥 open. Cross-process demand ownership: 🟨 local-only. Public WSS/client E2E: 🟥 open. Gate 25 snapshot receipts/high-water ACK: 🟥 open. Redis destructive retention: 🟧 blocked.

No Vercel deployment, no main branch update, no paid service, no live-market connection, no destructive Redis retention. Target: around 24 December 2026 (planning target).
