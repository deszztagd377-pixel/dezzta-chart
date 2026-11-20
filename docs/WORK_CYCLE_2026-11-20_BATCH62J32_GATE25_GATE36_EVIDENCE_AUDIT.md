# Batch 62J-32 — Gate 25/36 source and CI evidence audit

**Date:** 20 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/test evidence HEAD:** `cf6219a1f0fbea5a0daf8378ef47af386f8446fa`  
**Current documentation parent:** `080dde95c342605af34daee79f83477af64bc7ee`  
**Scope:** inspect existing Redis security configuration, Redis CI smoke, relay enablement boundary and WebSocket deployment/client acceptance. No runtime code or deployment changed.

## 1. Exact-head verification

The source/test checkpoint `cf6219a1f0fbea5a0daf8378ef47af386f8446fa` passed:
- Automated Tests [44708222353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222353) — SUCCESS.
- CodeQL [44708222403](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222403) — SUCCESS.
- Full Git History Secret Audit [44708222417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708222417) — SUCCESS.

The current documentation parent `080dde95c342605af34daee79f83477af64bc7ee` also passed all three workflows:
- Automated Tests [44708949484](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708949484) — SUCCESS.
- CodeQL [44708949469](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708949469) — SUCCESS.
- Full Git History Secret Audit [44708949472](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44708949472) — SUCCESS.

## 2. Gate 25 — precise Redis evidence

### 2.1 Production shared-guard TLS

Source inspection confirms:
- `Settings.__post_init__` requires `REDIS_URL` in production.
- Production URL must use `rediss://` and include username/password.
- `RedisSharedGuard` passes `ssl_cert_reqs="required"` and `ssl_check_hostname=True` to redis-py for `rediss://`.
- `backend/tests/test_shared_guard_tls.py` asserts both options and verifies plaintext `redis://` does not silently receive TLS options.

This proves TLS client configuration intent and option selection. It does **not** prove a successful live TLS handshake, certificate chain or hostname against the owner-controlled Redis endpoint.

### 2.2 Redis 7 disposable CI smoke

The CI workflow creates an isolated Redis 7 container and private Docker network:
- default ACL user disabled;
- ephemeral randomly generated test password;
- exact `dezzta:{guard-http}:*` and `dezzta:{guard-ws}:*` key patterns;
- restricted command list;
- AOF `appendonly yes`, `appendfsync always`;
- ACL file and AOF data on a temporary named volume.

The smoke test:
1. Rejects unauthenticated access.
2. Rejects an incorrect ACL password.
3. Rejects unrelated `SET` commands.
4. Starts the backend and validates health plus shared guard behavior.
5. Stops Redis and verifies the backend returns fail-closed HTTP 503 with Retry-After.
6. Recreates Redis over the same test volume.
7. Verifies the AOF canary and ACL restrictions persist.
8. Restarts the backend and verifies it recovers, while rate-limit behavior remains enforced.

This is strong repository-level persistence/ACL/outage/recovery evidence. It is not a production host drill or TLS test; the smoke network uses a disposable plaintext Redis URL.

### 2.3 OHLCV relay activation boundary

`backend/app/ohlcv_redis_config.py` validates:
- separate publisher and gateway Redis ACL usernames/passwords;
- exact stream key (no glob/wildcard);
- Redis database 0;
- production `rediss://` scheme.

However, its module documentation explicitly says the config is not wired into application startup until snapshot transport and owner-controlled ACL credentials are ready. The relay is not silently activated by environment flags. This is intentional fail-safe behavior, not an implementation failure to bypass.

### 2.4 Gate 25 remaining external acceptance

- Owner-controlled Redis TLS endpoint and certificate identity.
- Owner-host ACL creation and least-privilege permission verification.
- Publisher/gateway secret injection, rotation and rollback.
- Host firewall/private-network restriction.
- Approved snapshot distribution/rotation contract and relay startup integration.
- Target-host recovery and operator evidence.

**Disposition: Gate 25 remains 🟧 OPEN.** CI and source evidence are recorded; no production Redis, secrets or deployment were changed.

## 3. Gate 36 — WSS and client boundary

- Backend `/ws/market-data` route exists.
- It accepts Firebase ID-token authentication in the first JSON auth message and revalidates identity/series entitlement during the connection.
- Deployment documentation explicitly states source existence is not proof of deployed WSS availability.
- No owner-host reverse proxy, public WSS handshake, browser end-to-end, Android WebView, deployed cross-instance fan-out or platform connection-lifetime evidence was found.
- A separate short-lived scoped WebSocket ticket exchange is not implemented.

**Disposition: Gate 36 remains 🟧 OPEN.** No public endpoint was deployed and no client acceptance was fabricated.

## 4. Indicator and project progress

No indicator implementation or UI code changed. The complete indicator dashboard remains:
- SMA20 🟨, first valid index 19.
- EMA20 🟨, first valid index 19.
- RSI14 🟨, first valid index 14.
- MACD12/26/9 🟨, MACD index 25; signal/histogram index 33.
- Bollinger20,2 🟨, first valid index 19.
- Shared Indicator Hook 🟨.
- Footprint 🟧, deterministic SIMULATED data only; owner visual reference and reviewed blueprint required.
- Heatmap 🟥, not implemented.
- Liquidation Maps 🟥, no validated data/calculation contract.

Stage 1 remains 30/40 = 75% provisional. Stages 2–6 are unscored. Overall project percentage remains unestablished. Gate 10 remains 10/10 ORANGE, 0/10 closed.

## 5. Documentation consistency repair

The ledger contained an older Batch 62J-29 sentence claiming TCP interruption and dual-replica snapshot replacement were still untested. That statement was accurate at that historical checkpoint but was not labeled as superseded. It is now explicitly marked historical and superseded by Batch 62J-31, whose tests passed exact-head CI.

## 6. Controls

- ZERO COST maintained.
- No paid service, hosting, market-data provider or billing change.
- No Vercel/Cloudflare deployment.
- No Termux action or requirement.
- No production Redis relay activation.
- No `main` branch change.
