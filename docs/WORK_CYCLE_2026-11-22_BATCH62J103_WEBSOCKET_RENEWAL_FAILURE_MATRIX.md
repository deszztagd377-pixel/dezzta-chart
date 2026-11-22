# DEZZTA CHART — Work Cycle 62J-103
## WebSocket ticket renewal failure matrix + Redis ticket contract

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `7ff83f6e31ac869e43e1ce36ec1e00b693837fcc`  
**Documentation commits:** `bc772d3deb9ef54a05e5566a87c5a7d20f14f2d6`, `94725764404acc392300531879eb983f5a1705f2`  
**ZERO COST:** no deployment, paid service, Termux, device operation or production credential.

## Scope and changes

This cycle deliberately changed tests only. Production WebSocket, Redis, Firebase identity, market-data and indicator implementation files were not modified.

### `backend/tests/test_api.py`

Three new end-to-end FastAPI/WebSocket failure-path tests:

1. **Renewal subject mismatch:** a valid initial account ticket establishes the connection; a renewal ticket bound to another account is rejected with close code 4401 and remains single-use.
2. **Ticket-store outage during renewal:** after a valid ticket handshake and subscription, the ticket store begins raising a simulated Redis connection error. The connection closes with 1013; internal exception/credential text is not sent to the client.
3. **Revoked instrument entitlement:** a matching-subject renewal ticket is presented after the subscribed instrument entitlement is revoked. Renewal cannot restore access; the connection closes with 4403.

The file also receives the required top-level `asyncio` import for the test helper calls.

### `backend/tests/test_shared_guard.py`

Three additional contract tests:

1. **Ticket storage contract:** asserts the Redis key contains only the SHA-256 ticket digest, the write uses exact TTL 90 seconds, and Redis SET uses NX create-only semantics. It also verifies the stored JSON purpose and subject.
2. **Corrupt stored payload:** malformed JSON is rejected and the consumed key is deleted; no unverified subject is returned.
3. **In-memory concurrent consume:** two simultaneous consumers race for one ticket; exactly one receives the bound subject and exactly one receives `None`.

No existing test was removed. Final source/test delta relative to the prior docs checkpoint:
- `backend/tests/test_api.py`: +132 lines, 0 deletions.
- `backend/tests/test_shared_guard.py`: +44 lines, 0 deletions.
- Total: **+176 lines, 0 deletions, 6 new tests**.

## Validation and acceptance boundary

Final source/test HEAD: `7ff83f6e31ac869e43e1ce36ec1e00b693837fcc`.

The branch head was read back and compared with the prior checkpoint. The active branch is four commits ahead of `d45290b8b95e5bbe73e2a993cd3fdaf497a8afc3`, with zero commits behind. `main` remains `e3841681bc69b73619058deaf939df82ae5116a1`.

**CI status is not verified for this exact HEAD.** The available combined-status lookup returned an empty status list for both the new HEAD and the previously documented green source HEAD. Therefore this work cycle does not claim that Automated Tests, CodeQL or full-history secret audit passed. The six new tests must not be counted as CI-accepted until exact-head workflow results are independently visible. This is an evidence-access limitation, not a test failure or a pass.

## Gate 10 mapping

- **Gate 20 — 🟧 integration/acceptance open:** adds direct evidence for renewal subject binding, unavailable ticket store, entitlement revocation and sanitized failure handling. Still needs Firebase-signed-token E2E in the actual owner environment and final threat-model review.
- **Gate 25 — 🟧 integration/acceptance open:** adds exact Redis ticket TTL/NX/digest-key and corrupt-payload evidence. Still needs owner-host Redis TLS/ACL, authenticated snapshot transfer receipt, persistence and failover acceptance.
- **Gate 36 — 🟧 integration/acceptance open:** adds renewal-path connection failure and entitlement enforcement tests. Still needs public HTTPS/WSS, reverse proxy, live Redis, browser and Android WebView acceptance.
- **Gate 31 — 🟧 integration/acceptance open:** independent off-host encrypted backup, offline key custody and key-recovery restore remain.
- **Gate 38 — 🟧 integration/acceptance open:** owner-host persistent volume, private perimeter, dashboard/notifications and recovery drill remain.
- **🟨🟩 host/operator-only verification:** Gates 8, 30, 34, 35 and 39.
- **Gate 10:** 0/10 formally closed. No gate is closed by this test-only cycle.

CI Redis container smoke is not owner-host acceptance. No live production host, Firebase project, Redis credentials, public endpoint or device was accessed.

## Project and indicator progress

- Stage 1: 30/40 = 75% provisional.
- Stages 2–6 and overall project percentage: unscored; approved weights/denominators do not exist.
- Indicator implementation: unchanged; **zero indicator progress credit**.
- Full formula, warm-up, rendering and remaining-work matrix is maintained in `docs/INDICATOR_PROGRESS_LEDGER.md`.
- SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Indicator Hook 🟨, Footprint 🟧, Heatmap 🟥, Liquidation Maps 🟥.
- Footprint/Heatmap visual implementation remains blocked on user reference image(s) and reviewed blueprint. Footprint OFF must keep normal candle spacing; explicit ON enables spaced clusters.

## Operational constraints

No deployment, no Vercel/Cloudflare operation, no paid service/provider, no production credentials, no Termux/device operation, and no `main` branch changes. No overall percentage was invented.
