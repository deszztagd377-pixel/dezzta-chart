# Work Cycle 2026-11-20 — Batch 62J-47 cross-account WebSocket renewal regression

**Branch:** `phase-2/market-data-foundation`  
**Starting documentation/source checkpoint:** `b4b213866f59666ddebed8fc8b9ea1a3c5846b18`  
**Source/test commit:** `826bae749f48e844f5fddb82dfec396bb3f9baa7`  
**Scope:** Gate 20 WebSocket ticket subject-binding regression coverage. ZERO COST.

## Gap identified

The backend already compares the subject attached to a consumed renewal ticket with the subject authenticated on the existing WebSocket. A mismatch closes the connection with code `4401`. Existing API tests proved that a same-subject renewal succeeds, but did not directly prove that a different verified account's valid ticket is rejected on that connection.

## Change

Added one backend API regression test:

- `test_websocket_ticket_renewal_rejects_ticket_for_different_subject`

The test installs a deterministic verifier with two distinct verified account subjects, obtains one ticket for each account, authenticates the socket as the owner account, subscribes to an entitled canonical instrument, and then attempts renewal using the other account's ticket. It asserts that the server disconnects with code `4401`.

This is a test-only change. No production runtime code, ticket format, TTL, auth protocol, entitlement policy, dependency, or deployment configuration changed.

## Exact-head CI evidence

All workflows completed **SUCCESS** on exact source/test HEAD `826bae749f48e844f5fddb82dfec396bb3f9baa7`:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests & Build | [44751619536](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44751619536) | **SUCCESS** |
| CodeQL (JavaScript/TypeScript + Python) | [44751619516](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44751619516) | **SUCCESS** |
| Full Git History Secret Audit | [44751619621](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44751619621) | **SUCCESS** |

Verified test/audit results:

- Frontend: **245 passed across 29 test files**.
- Backend: **1,198 passed, 6 warnings, 41.58 seconds**.
- Frontend dependency audit: **0 vulnerabilities**.
- Backend dependency audit: **no known vulnerabilities reported**.
- Frontend source/bundle secret scans and full Git-history secret audit: passed.
- Backend container build, Redis ACL/AOF + mounted persistent-volume smoke test, and Trivy HIGH/CRITICAL scan/report export: passed.
- The Trivy report was exported as artifact `14635407508`; this report records scan completion but does not claim a zero-vulnerability count.
- Synthetic outbox benchmark artifact: `14635297409`; synthetic only, not a production capacity/SLO claim.

## Security and acceptance boundary

- The test confirms account-subject binding at the renewal boundary and verifies rejection code `4401`.
- The test does not establish real Firebase project behavior, production Redis deployment, public WSS, browser/Android end-to-end operation, or owner-host acceptance.
- Gate 20 remains **OPEN** pending real Firebase identity verification, session expiry/revocation and client reconnect acceptance.
- Gate 25/36 and the remaining owner-host gates are unchanged.
- Gate 10 remains **10/10 ORANGE / 0 formally closed**.
- Stage 1 remains **30/40 criteria = 300/400 ticks = 75% provisional**. No progress tick is awarded for this regression test alone.
- Stages 2–6 and overall project percentage remain unscored.

## Change boundary

Changed source/test file:
- `backend/tests/test_api.py`

Documentation added:
- `docs/WORK_CYCLE_2026-11-20_BATCH62J47_CROSS_ACCOUNT_WEBSOCKET_RENEWAL.md`

No deployment, paid service, Termux package operation, provider credential, production host operation, or `main` branch modification occurred.
