# DEZZTA CHART — Work Cycle 62J-66 / 62J-67
## Gate 8 secret handling, key-file validation and Docker build-context hardening

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Current branch HEAD:** `8636e2a1f0b1a2ff5c1d803e00516a7570e5289d`  
**Policy:** ZERO COST; never modify `main`.

## Executive result

This cycle closed two repository-side gaps without changing production runtime behavior:
1. Explicit regression coverage for redacting the alert-device encryption key and for validating the protected key file.
2. Docker build-context exclusions so local secrets and runtime state are not transmitted to the backend image builder, plus complete optional environment examples.

All exact-head CI checks passed on the current branch HEAD. Gate 8 remains open because no owner-host secret-injection path or live process environment was available for verification. No Stage 1 acceptance tick is awarded.

## Batch 62J-66 — test coverage

### Commit 1
`0951a8cdfb75a083d48247321d7020d15c60f101`

- Added an explicit `Settings.__repr__` / `Settings.__str__` regression for `alert_device_encryption_key`.
- No runtime code changed.

### Commit 2
`58f0e721a197d95424395d08ecce2143ddcd4926`

- Added 9 key-file loader test cases in `backend/tests/test_config.py`.
- Valid canonical Base64 encoding of exactly 32 bytes with restrictive file mode is accepted.
- Group/other-readable permission modes are rejected.
- Malformed Base64 and 31-/33-byte decoded key material are rejected.
- Relative and missing paths are rejected.
- No runtime code changed.

Exact-head CI for `58f0e72`:
- Automated Tests [44860466353](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44860466353): **SUCCESS** — backend 1,235 passed; frontend 247/247 across 29 files; 33/33 steps.
- CodeQL [44860466368](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44860466368): **SUCCESS**.
- Full Git History Secret Audit [44860466365](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44860466365): **SUCCESS**.

The earlier Automated Tests run for `0951a8c` was cancelled automatically when the newer branch commit superseded it. It is not counted as a failed test run; the complete superseding exact-head CI passed.

## Batch 62J-67 — Docker build-context and configuration documentation

### Commit
`8636e2a1f0b1a2ff5c1d803e00516a7570e5289d`

Changed files:
- `backend/.dockerignore` — excludes `.env` files, key/certificate material, SSH private-key names, runtime databases/backups, and Python caches/virtual environments from the Docker build context.
- `backend/.env.example` — documents optional alert-device encrypted-store configuration, the disabled-by-default delivery worker, Redis URL and operator incident token. No real secret is included.

Why the build-context change matters: a Docker build context is sent to the builder even if the Dockerfile does not COPY a file into the final image. The backend Dockerfile explicitly copies only `requirements.txt` and `app/`; the new ignore file prevents local credential files from entering the build context at all.

Exact-head CI for `8636e2a`:
- Automated Tests [44861035493](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44861035493): **SUCCESS** — frontend **247/247 tests across 29 files**; backend **1,235 passed in 49.78s**; all **33/33 workflow steps** passed.
- CodeQL [44861035537](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44861035537): **SUCCESS**.
- Full Git History Secret Audit [44861035482](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44861035482): **SUCCESS**.
- Frontend dependency audit: **0 vulnerabilities**.
- Backend dependency audit: **no known vulnerabilities**.
- Trivy: **0 vulnerabilities** for scanned Alpine and Python package targets.
- Backend container build, Redis ACL/AOF + persistent-volume smoke, health check, non-root execution, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection: **SUCCESS**.

## Gate 8 disposition

**Repository-side status: improved and exact-head CI-verified. Production/host gate: OPEN.**

Verified in repository/CI:
- Settings repr/str redaction includes alert-device encryption key.
- Key-file loader requires an absolute path to a regular file, denies group/other permission bits, bounds file size, accepts canonical Base64 only, and requires exactly 32 decoded bytes.
- Backend build context excludes local credentials and runtime state.
- Frontend source/bundle secret scans and full reachable Git-history secret audit pass.

Still required on the actual owner-controlled runtime:
- Identify the actual host secret-injection mechanism and source path.
- Verify owner/group/mode and process readability. The backend container runs as UID/GID 10001; the mounted key file must be readable by that process while group/other permission bits remain zero.
- Verify the secret is absent from process arguments, logs, crash reports, build output and host diagnostics.
- Verify rotation/replacement behavior without exposing key material.
- Never paste production secrets or key contents into chat.

CI, a protected-file fixture, or a Docker smoke test is not a substitute for actual host verification. Gate 8 remains OPEN.

## WebSocket status

The defined automated WebSocket failure matrix remains complete: two independent ASGI processes, separate replicas/consumer groups, authenticated live delivery, replay reconnect boundary, process restart continuity, Redis read-failure recovery, independent Redis TCP interruption/recovery, and coordinated snapshot-generation replacement.

External work remains: production snapshot distribution/rotation/rollback, production Redis TLS/ACL/credential lifecycle and failover, public HTTPS/WSS, and browser/Android acceptance. Do not repeat the passing automated failure matrix.

## Gate 10 / Stage 1 accounting

| Gate | State | Outstanding external evidence |
|---:|---|---|
| 8 | 🟧 OPEN | Owner-host secret injection, ownership/mode, process exposure and runtime review |
| 20 | 🟧 OPEN | No-billing real Firebase auth/revocation/entitlement plus browser/Android acceptance |
| 25 | 🟧 OPEN | Production Redis TLS/ACL/credential lifecycle/persistence/failover |
| 30 | 🟧 OPEN | Restore drill on actual live database path |
| 31 | 🟧 OPEN | Off-host copy and independent key custody/recovery |
| 34 | 🟧 OPEN | Real persistent volume mount/restart/disk-pressure evidence |
| 35 | 🟧 OPEN | Real HTTPS endpoint and certificate/renewal |
| 36 | 🟧 OPEN | Public WSS proxy and browser/Android acceptance |
| 38 | 🟧 OPEN | Collector/dashboard/retention/access/disk-pressure |
| 39 | 🟧 OPEN | Real operator alert, acknowledgement/escalation and recovery drill |

**Gate 10:** 0/10 formally closed.  
**Stage 1:** 30/40 = 300/400 = **75% provisional**.  
**Overall project:** NOT SCORED; M1–M8 weights and denominator remain unapproved.  
**Indicator progress:** unchanged; no indicator completion credit.

## Complete indicator ledger

| Indicator / component | Status | Formula / first valid index | Remaining implementation |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded EMA; alpha = 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing over 14 close changes; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Pane, lines, histogram, zero guide, toggle, legend |
| Bollinger20,2 | 🟨 Foundation | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot; no DEMO fallback; candle-index aligned | Identity/timeframe binding, loading/error, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / gated | Educational simulated accumulator; not exchange-native bid/ask truth | Owner reference image, approved blueprint, explicit-ON spaced clusters, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | Data source/calculation contract not approved | Reference image, source feasibility, validated data contract, blueprint, renderer |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/calculation contract | Zero-cost source feasibility, validated calculation, blueprint/reference, renderer |

Correctness invariants:
- Warm-up values are null, never fabricated zeroes; all outputs align to candle indexes.
- Appending future candles cannot alter earlier indicator outputs (prefix causality).
- Symbol, venue, dataset, chart identity and timeframe changes invalidate stale values and isolate series.
- Footprint OFF preserves standard candlestick spacing; only explicit ON activates the spaced-cluster layout.
- Footprint and Heatmap visual implementation waits for the user's reference images and reviewed blueprint.
- No aggregate indicator percentage is assigned without approved weights/acceptance denominator.

## ZERO COST / device boundary

- No deployment or Vercel/Cloudflare operation.
- No paid service, trial, provider, billing activation or production credential.
- No Termux command was required for these remote repository changes.
- No second device, PC or laptop is assumed.
- `main` was not modified.

## Next execution order

1. Gate 8: owner-side secret injection and runtime ownership/mode review, if/when an authorized host environment is available.
2. Gate 30: consolidate the approved phone-only/local SQLite restore acceptance without confusing it with off-host disaster recovery.
3. Gate 38/39: continue repository-side checks only where a concrete defect is established; external host/operator acceptance remains separate.
4. Gate 20/25/34/35/36/31: remain constrained until no-cost resources and the required external evidence are genuinely available.
5. Indicators: preserve the calculation contracts; do not start Footprint/Heatmap visual work before the user's reference images and approved blueprint. Do not invent liquidation data.
