# DEZZTA CHART — Work Cycle Batch 62J-73
## Zero-cost Redis ACL host simulation (superseded ACL note corrected in Batch 62J-74)

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Scope:** dedicated Redis publisher/gateway role startup and least-privilege ACL verification

## Context

The project currently has GitHub repository + CI but no active owner-controlled backend host. A production endpoint cannot be accepted without a real host. Rather than asking the user to purchase hosting or provide credentials, this batch uses the existing CI Redis 7 service as a disposable, zero-cost host simulation.

The existing automated workflow already provisions Redis and sets `REDIS_TEST_URL` for backend pytest. No additional workflow, paid integration, deployment, or service was introduced.

## Engineering finding

The dedicated publisher and gateway Redis URLs are constrained to database 0. Redis clients initialized from a URL select the configured database during connection setup. The prior role command allow-lists omitted `+select`, creating a potential authentication/startup rejection before the runtime could PING or access the stream.

## Changes

Updated:
- `backend/app/ohlcv_redis_config.py`
- `backend/tests/test_ohlcv_redis_config.py`

Added:
- `backend/tests/test_ohlcv_redis_acl_integration.py`

Both role command matrices now include `+select`. Database 0 remains mandatory. The role-specific stream/lease key patterns and all other least-privilege restrictions remain unchanged.

## Real Redis integration test design

The new test runs against `REDIS_TEST_URL` and:
1. Creates two disposable Redis ACL identities with cryptographically random, runtime-only passwords.
2. Configures the publisher user for its exact stream key and publisher command allow-list.
3. Configures the gateway user for its exact stream and lease keys and gateway command allow-list.
4. Connects both clients through the configured Redis URL/database path and validates PING.
5. Proves publisher XADD/XRANGE works and consumer/lease operations are denied.
6. Proves gateway XGROUP CREATE, XREADGROUP, XAUTOCLAIM, XACK, XRANGE and lease Lua operations work.
7. Proves gateway XADD and out-of-scope key access are denied.
8. Removes temporary keys and ACL users in a `finally` cleanup path.

No generated secret is committed or printed. When `REDIS_TEST_URL` is absent, the test skips locally; the current CI backend test job already sets it, so the integration test is included automatically in that job.

## Verification status

**Source/test checkpoint:** `7e7d17144c178c8167c22520ce9efc8bcef52b07`. The exact-head CI result must be inspected before any pass claim. No green status is inferred from earlier CI runs.

## What this achieves

- A genuine Redis ACL integration check in an isolated ephemeral environment.
- Verification of the exact database-selection and role-command behavior.
- No need for the user to create a hosting account, supply credentials, run Termux, or manually execute code.

## What remains outside the simulation

- Public Redis TLS certificate and hostname validation against a real provider.
- Owner-host secret injection, rotation and rollback.
- Production Redis persistence/failover and private network controls.
- Actual source/gateway host volumes and multi-host snapshot distribution/installation.
- Public HTTPS/WSS reverse proxy, browser acceptance and Android WebView/device acceptance.
- Real backup destination, recovery and monitoring host evidence.

The CI Redis instance is ephemeral and must never be represented as a production host.

## Gate 10 and project accounting

- Gate 8 — 🟨🟩 host-verification-only.
- Gate 25 — 🟧 OPEN: live Redis TLS/ACL, persistence/failover and secret lifecycle remain host-bound.
- Gate 36 — 🟧 OPEN: public HTTPS/WSS and browser/Android runtime acceptance remain host-bound.
- Gate 10 — 0/10 formally closed.
- Stage 1 — 30/40 = 75% provisional.
- Stages 2–6 and overall project percentage remain unscored pending approved denominators/weights.

## Complete indicator ledger (unchanged by this batch)

- SMA20 — 🟨 foundation; arithmetic mean of 20 closes; first valid index 19.
- EMA20 — 🟨 foundation; SMA-seeded, alpha 2/21; first valid index 19.
- RSI14 — 🟨 foundation; Wilder smoothing; first valid index 14.
- MACD 12/26/9 — 🟨 foundation; MACD first index 25; signal/histogram first index 33.
- Bollinger20,2 — 🟨 foundation; mean ± 2 × population standard deviation; first valid index 19.
- Shared Indicator Hook — 🟨 foundation; validated, candle-index-aligned snapshot.
- Footprint — 🟧 simulated/gated; awaits user visual reference and approved blueprint.
- Heatmap — 🟥 not implemented; awaits user visual reference, free-source feasibility and approved data contract.
- Liquidation Maps — 🟥 not implemented; awaits free-source feasibility and validated data/calculation contract.

Invariants: warm-up values are null, never zero; series align to candle indices; no future-candle repaint; identity/timeframe changes clear stale series. Footprint OFF preserves normal candle spacing; explicit ON alone enables spaced clusters. Full renderer work remains in the project dashboard.

## Batch 62J-74 correction and CI result\n\nThe prior `+select` permission was unnecessary for database 0 and has been removed from both roles. The ACL integration test now proves that each role can operate on its DB-0 URL while explicit `SELECT 1` is denied. Exact-head CI passed with 1,249 backend tests; the full CI run, container smoke, CodeQL and history secret audit succeeded. See the current dashboard and WebSocket audit for exact run references and the remaining production-host boundary.\n\n## Cost and device boundary

ZERO COST. No deployment, paid hosting, production credentials, Vercel/Cloudflare operation, Termux/device action or `main` modification.
