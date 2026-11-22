# DEZZTA CHART — Batch 62J-110
## Real Redis TLS integration acceptance in zero-cost CI

**Date:** 22 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Baseline:** `ec8566a2d34e693283b0fa18421aaf3d4d01ef45`  
**Scope:** replace the Redis TLS configuration-only assertion with an actual Redis TLS handshake and negative verification tests.  
**Cost:** ZERO COST. CI-only ephemeral resources; no production host, paid service, deployment, secret, Termux action, Vercel/Cloudflare operation, or `main` change.

## 1. Verified baseline and concrete gap

At the baseline, exact-head CI was green (Automated Tests run 44978512376, CodeQL 44978512421, Full Git History Secret Audit 44978512369). Existing Redis container smoke covered ACL rejection, AOF/ACL persistence across restart, fail-closed backend behavior during Redis outage, recovery, and SQLite volume integrity.

However, CI's Redis service listened on plaintext port 6379. The existing `test_shared_guard_tls.py` only inspected arguments passed to a mocked `Redis.from_url`; it did not establish a TLS session or prove certificate/hostname rejection.

## 2. Changes in this batch

1. `.github/workflows/ci.yml`
   - Adds an isolated Redis 7 TLS-only container on loopback port 6380.
   - Generates an ephemeral test CA, a server certificate with only `DNS:localhost` SAN, and a separate untrusted CA.
   - Disables the plaintext listener (`--port 0`), disables client-certificate authentication for this server-auth-only fixture, and uses a disposable ACL user with only the shared-guard commands/key prefixes.
   - Runs the real TLS integration test before the existing backend suite.
   - Removes the fixture container with a shell EXIT trap.
2. `backend/tests/test_shared_guard_tls_integration.py`
   - Connects using the real redis-py client and `RedisSharedGuard`.
   - Validates the trusted CA + matching hostname handshake.
   - Exercises HTTP rate-limit Lua, one-time WebSocket ticket, connection lease, renewal and release operations through TLS + ACL.
   - Requires rejection for an untrusted CA, a trusted certificate presented under the wrong hostname, and plaintext protocol access to the TLS-only port.
   - Skips in ordinary local pytest runs when the isolated CI fixture variables are absent; the dedicated workflow step supplies all three values and therefore cannot silently skip.
3. `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md`
   - Appends this checkpoint and preserves the existing complete indicator ledger.

## 3. Acceptance matrix

| Test | Expected | Evidence produced by this batch |
|---|---|---|
| Trusted CA + DNS SAN match | Connect | Real Redis TLS handshake + PING |
| Shared-guard HTTP Lua | Pass | Actual INCR/EXPIRE/TTL via Redis ACL |
| WebSocket ticket issue/consume | Pass | Actual SET/GET/DEL Lua via Redis ACL |
| WebSocket lease acquire/renew/release | Pass | Actual sorted-set Lua operations via Redis ACL |
| Trusted CA + wrong hostname | Reject | Hostname verification failure |
| Wrong CA + correct hostname | Reject | Certificate-chain verification failure |
| Plaintext to TLS-only listener | Reject | No plaintext port is configured |
| Redis ACL scope | Enforced | Test identity is limited to guard key prefixes and required commands |

The CI fixture is server-authenticated TLS with client authentication disabled. Production mutual TLS is not claimed or required by the current architecture.

## 4. Security and lifecycle constraints

- Test CA private keys, server keys, passwords and ACL file are generated per workflow run and are never committed.
- The Redis listener is published only on runner loopback.
- Redis plaintext port is disabled.
- The test fixture is ephemeral and does not represent an OCI/production host.
- Production `ssl_cert_reqs="required"` and `ssl_check_hostname=True` remain unchanged.
- No production source/configuration behavior is modified by this test-only batch.

## 5. Gate 10 disposition

- Gate 10: **0/10 formally closed**; no gate closure is awarded from CI simulation.
- Gate 25: 🟧 OPEN. Repository-side Redis TLS handshake/CA/hostname/ACL behavior is now targeted by a real TLS fixture; owner-host Redis TLS/ACL topology, secret lifecycle, durable OHLCV relay persistence/failover, snapshot distribution and installation receipts remain external.
- Gate 36: 🟧 OPEN. Public HTTPS/WSS hostname, certificate, reverse proxy, browser and Android WebView acceptance remain host/device-bound.
- Gate 8: 🟨🟩 owner-host verification only.
- Gates 20, 30, 31, 34, 35, 38 and 39 retain their existing external Firebase, restore/backup, volume, proxy, observability and operator-recovery requirements.
- Stage 1 remains 30/40 = 75% provisional. Stages 2–6 and overall project percentage remain unscored; no approved global denominator/weights exist.

## 6. Full indicator progress ledger

No indicator source, calculation, data contract, renderer or UI changed in this batch; no indicator progress credit is awarded.

| Indicator | Formula / first valid index | Current state | Remaining work |
|---|---|---|---|
| SMA20 | Mean of 20 closes; index 19 | 🟨 Foundation | Chart overlay, independent toggle, legend/current value, stale-series and renderer lifecycle tests |
| EMA20 | SMA-seeded EMA; alpha 2/21; index 19 | 🟨 Foundation | Chart overlay, toggle, legend/current value, stale clearing and renderer tests |
| RSI14 | Wilder smoothing over 14 close changes; index 14 | 🟨 Foundation | Dedicated 0–100 pane, 30/70 guides, toggle, legend/current value and renderer tests |
| MACD 12/26/9 | EMA12 − EMA26; index 25; signal/histogram index 33 | 🟨 Foundation | Dedicated pane, MACD/signal lines, histogram, zero guide, toggle and renderer tests |
| Bollinger20,2 | Mean ± 2 × population SD; index 19 | 🟨 Foundation | Upper/middle/lower overlay, toggle, values and renderer lifecycle tests |
| Shared Indicator Hook | Validated candle-index-aligned snapshot | 🟨 Foundation | Chart identity/timeframe binding, loading/error lifecycle, stale clearing and renderer integration |
| Footprint | Educational accumulator is simulated, not exchange-native bid/ask truth | 🟧 Reference-gated | User visual reference + reviewed blueprint, validated source contract, cluster renderer and lifecycle/performance tests; OFF keeps normal spacing, explicit ON enables spaced clusters |
| Heatmap | Not implemented; no validated zero-cost source contract | 🟥 Not implemented | User reference, zero-cost source feasibility, validated data contract, reviewed blueprint, renderer/legend/scale/toggle |
| Liquidation Maps | Not implemented; no fabricated liquidation levels | 🟥 Not implemented | Zero-cost source feasibility, validated data/calculation contract, reference/blueprint, renderer and scale/legend |

**Shared indicator invariants:** warm-up values are `null`, never zero; arrays align to candle indices; no future-candle repaint; stale series clear on symbol/venue/dataset/chart/timeframe changes; invalid bars/gaps are not silently converted to zero. Footprint OFF preserves ordinary candle spacing; only explicit ON selects the spaced cluster layout. Footprint and Heatmap visual work remains gated on user reference images and reviewed blueprints.

## 7. CI verification required

This commit is a candidate until all exact-head workflows finish. Required:
- Automated Tests: dedicated real Redis TLS integration step, full backend/frontend tests, container smoke, audits and build.
- CodeQL.
- Full Git History Secret Audit.

A failed check must be diagnosed from its log and corrected before acceptance is reported. CI success remains repository evidence only; it does not create a public WSS endpoint or prove owner-host deployment.

**Disposition:** Real TLS acceptance has been added to the CI design. Exact-head workflow results determine whether this batch passes. Production WebSocket acceptance and Gate 10 remain open.
