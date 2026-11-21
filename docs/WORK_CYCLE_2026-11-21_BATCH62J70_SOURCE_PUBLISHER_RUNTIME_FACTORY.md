# Work Cycle 62J-70 — Source publisher runtime factory and snapshot gate

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Scope:** source publisher construction and Gate 25 ACL precision. No production acceptance is claimed.

## Implemented

1. Added `backend/app/ohlcv_redis_runtime.py`, an opt-in source-role runtime factory. It uses a dedicated publisher URL rather than the shared security-guard `REDIS_URL`.
2. Production publisher URL validation requires `rediss://`, a dedicated ACL username/password and Redis database 0.
3. Redis client defaults are bounded: 3-second connect timeout, 5-second socket timeout and 15-second health-check interval. TLS certificate and hostname verification are required.
4. The factory refuses to create a Redis client unless a durable publisher checkpoint already exists and an owner-host snapshot verifier confirms exact source ID, stream key, snapshot generation and cursor across every required gateway installation receipt.
5. It never initializes or guesses a cursor. The default ASGI app remains disabled unless the owner explicitly injects the resulting runtime factory.
6. The documented publisher and gateway ACL allow-lists now include `+ping`, required by startup readiness checks. Other command permissions remain role-specific and narrowly scoped.
7. `backend/.env.example` documents the opt-in publisher variables without real credentials.

## Regression tests added

- Missing checkpoint fails before Redis client creation.
- Gateway snapshot receipt with a mismatched cursor fails before Redis client creation.
- Matching manifest and every gateway receipt permit construction of the dedicated TLS client.
- Production plaintext Redis is rejected.
- Environment factory remains opt-in.
- ACL tests assert the exact `+ping` permission for both roles.

## Production acceptance remains open

The snapshot-verifier callback is an interface contract, not a remote-host probe. Its owner-host implementation must read the authoritative global snapshot manifest and independently verified installation receipts. Live Redis TLS handshake, actual ACL enforcement, source/gateway host persistence, snapshot rotation/rollback, public WSS, browser and Android WebView acceptance still require owner-controlled host access. Gate 25 and Gate 36 remain 🟧 OPEN; source publisher activation remains 🟨🟩 HOST VERIFICATION PENDING.

## Indicator and project progress

No indicator formula, renderer or chart UI changed. SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint remains 🟧 SIMULATED / GATED; Heatmap and Liquidation Maps remain 🟥 NOT IMPLEMENTED. Full formulas, first-valid indices and outstanding renderer tasks remain in the current project dashboard. No indicator credit is awarded by this backend-only batch.

ZERO COST. No deployment, paid service, production credential, Termux/device operation, Vercel/Cloudflare operation or `main` modification.
