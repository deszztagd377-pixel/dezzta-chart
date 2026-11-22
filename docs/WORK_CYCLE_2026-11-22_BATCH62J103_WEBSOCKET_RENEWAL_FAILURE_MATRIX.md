# DEZZTA CHART — Work Cycle 62J-103
## WebSocket ticket renewal failure matrix + Redis ticket contract

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Final source/test HEAD:** `a18e963d4cd067fe22ec8d03c653418e003c7fde`  
**ZERO COST:** no deployment, paid service, Termux, device operation or production credential.

## Scope and changes

This cycle deliberately changed tests only. Production WebSocket, Redis, Firebase identity, market-data and indicator implementation files were not modified.

### `backend/tests/test_api.py`

Two new end-to-end FastAPI/WebSocket failure-path tests:

1. **Invalid/expired renewal ticket:** after a valid ticket handshake and OHLCV subscription, an invalid renewal ticket is rejected and the connection closes with code 4401.
2. **Ticket-store outage during renewal:** after a valid ticket handshake and subscription, the ticket store begins raising a simulated Redis connection error. The connection closes with 1013; internal exception/credential text is not sent to the client.

The audit also confirmed that existing tests already cover renewal-ticket subject mismatch (4401) and renewal after instrument-entitlement revocation (4403). Two duplicate candidate tests were removed; the final diff contains no redundant copies of those existing cases.

### `backend/tests/test_shared_guard.py`

Three new ticket-contract tests:

1. **Ticket storage contract:** asserts the Redis key contains only the SHA-256 ticket digest, the write uses exact TTL 90 seconds, and Redis SET uses NX create-only semantics. It also verifies the stored JSON purpose and subject.
2. **Corrupt stored payload:** malformed JSON is rejected and the consumed key is deleted; no unverified subject is returned.
3. **In-memory concurrent consume:** two simultaneous consumers race for one ticket; exactly one receives the bound subject and exactly one receives `None`.

An existing real-Redis single-use integration test was strengthened with a live `PTTL` assertion: the remaining ticket TTL must be positive and no greater than 90,000 ms.

## Final source/test diff

Compared with the prior docs checkpoint `d45290b8b95e5bbe73e2a993cd3fdaf497a8afc3`:

- `backend/tests/test_api.py`: +86 lines, 0 deletions.
- `backend/tests/test_shared_guard.py`: +47 lines, 0 deletions.
- Total: **+133 lines, 0 deletions, 5 new tests**, plus the real-Redis PTTL assertion in an existing integration test.

Final source/test HEAD: `a18e963d4cd067fe22ec8d03c653418e003c7fde`.

## Validation and acceptance boundary

The active branch was read back after the test changes. The source/test change set is nine commits ahead of the prior documentation checkpoint and zero commits behind it. `main` remains `e3841681bc69b73619058deaf939df82ae5116a1`.

**CI acceptance is not verified for this exact HEAD.** The available GitHub combined-status lookup returned an empty status list, including for the previously documented green source HEAD. Therefore this cycle does not claim that Automated Tests, CodeQL or full-history secret audit passed. The five new tests and the PTTL assertion must not be counted as CI-accepted until exact-head workflow results are independently visible.

## Gate 10 mapping

- **Gate 20 — 🟧 integration/acceptance open:** adds invalid/expired renewal-ticket and ticket-store outage handling. Existing tests cover cross-subject renewal rejection and revoked entitlement. Still needs Firebase-signed-token E2E in the actual owner environment and final threat-model review.
- **Gate 25 — 🟧 integration/acceptance open:** adds digest-key/NX/exact TTL/corrupt-payload tests and a real Redis PTTL check. Still needs owner-host Redis TLS/ACL, authenticated snapshot transfer receipt, persistence and failover acceptance.
- **Gate 36 — 🟧 integration/acceptance open:** adds renewal-path failure closure evidence. Still needs public HTTPS/WSS, reverse proxy, live Redis, browser and Android WebView acceptance.
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
