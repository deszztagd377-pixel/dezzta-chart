# Work Cycle 62J-68 — Gate 8 no-follow secret loader hardening

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Source/config/test HEAD:** `da9b2ad025ac5c49f75c95dbdd5f516573107f87`  
**Parent:** `4afdc4e7651856f1847aeda658b3e9a3f76dbadf`

## Objective and defect

Gate 8 already covered key length, canonical Base64, absolute paths, group/other permission denial and Settings repr/str redaction. A source audit found that the loader used `Path.is_file()`, `Path.stat()` and `Path.read_bytes()` separately. These operations followed a final-component symbolic link and performed validation and reading through separate path lookups. This left a symlink/TOCTOU gap in a secret-loading boundary.

## Implementation

Changed:
- `backend/app/config.py`
- `backend/tests/test_config.py`

The loader now:
1. Requires an absolute configured path and a platform with `O_NOFOLLOW`; it fails closed if no-follow opening is unavailable.
2. Opens the file once with `O_NOFOLLOW`, plus `O_CLOEXEC` and `O_NONBLOCK` where available.
3. Uses `fstat()` on that descriptor, not a second path lookup.
4. Accepts only a regular file with no group/other permission bits.
5. Enforces the 1–128 byte bound from metadata and reads at most 129 bytes to detect growth beyond the bound.
6. Preserves canonical Base64 validation and the exact 32-byte decoded-key requirement.
7. Returns sanitized deterministic errors for missing files, symlink/unavailable files and non-ASCII data.

New regression coverage rejects a final-component symbolic link, a directory/non-regular file and non-ASCII key-file contents. Existing coverage retains permission-mode, malformed Base64, wrong key length and absolute/missing path checks.

## Verification history — transparent CI reconciliation

The first candidate commit `4afdc4e` passed CodeQL and Full Git History Secret Audit, but Automated Tests exposed one compatibility regression: a missing file now returned the generic unavailable error instead of the existing explicit “regular file” validation message. Result: 1 failed, 1,237 passed. This was one assertion/contract mismatch, not a runtime security bypass.

Fixed by mapping `FileNotFoundError` to the existing explicit missing-regular-file validation message in commit `da9b2ad025ac5c49f75c95dbdd5f516573107f87`.

Final exact-HEAD CI:
- Automated Tests [44863517983](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517983) — **SUCCESS**; frontend 247/247; backend 1,238 passed in 49.89s; 32/32 workflow steps.
- CodeQL [44863518025](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863518025) — **SUCCESS**.
- Full Git History Secret Audit [44863517962](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44863517962) — **SUCCESS**.
- Backend image build, Redis ACL/AOF + persistent-volume smoke, Trivy scan and report export — **SUCCESS**.
- Trivy: 0 vulnerabilities in scanned Alpine and Python package targets.
- Backend dependency audit: no known vulnerabilities.

## Gate 10 status

**Gate 8 — 🟨 HOST VERIFICATION ONLY; still OPEN.**

Repository-side work is complete. Only actual owner-host verification remains:
- Secret source/injection path and ownership.
- File mode and read access for backend UID/GID 10001.
- Process environment/arguments exposure.
- Rotation and log/crash exposure.
- Runtime loading with the real host-provided secret, without sharing the secret in chat.

Gate 8 is not green/closed until this evidence is reviewed. The other nine gates remain 🟧 OPEN. Gate 10 remains 0/10 formally closed, 1/10 host-verification-only, 9/10 externally open.

## Stage and project accounting

- Stage 1: 30/40 criteria = 300/400 ticks = **75% provisional**.
- No Stage 1 tick is awarded by this source-side hardening or CI.
- Overall project percentage remains **NOT SCORED** because M1–M8 weights and denominator are not approved.
- Stages 2–6 remain NOT SCORED.
- No indicator implementation or indicator test changed in this cycle.

## Complete indicator ledger

| Indicator | Status | Formula / first valid index | Remaining |
|---|---|---|---|
| SMA20 | 🟨 Foundation | Mean of 20 closes; index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| EMA20 | 🟨 Foundation | SMA-seeded; alpha 2/21; index 19 | Overlay, toggle, legend/current value, stale clearing, render/lifecycle tests |
| RSI14 | 🟨 Foundation | Wilder smoothing; index 14 | 0–100 pane, 30/70 guides, toggle, legend, renderer tests |
| MACD 12/26/9 | 🟨 Foundation | EMA12−EMA26; MACD index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero guide, toggle, legend, renderer tests |
| Bollinger20,2 | 🟨 Foundation | Mean ± 2 × population SD; index 19 | Three-line overlay, toggle, values, stale clearing, renderer tests |
| Shared Indicator Hook | 🟨 Foundation | Validated backend snapshot only; no DEMO fallback | Chart/symbol/timeframe identity, loading/error, stale clearing, series isolation |
| Footprint | 🟧 SIMULATED / gated | Educational simulated accumulator | Owner reference image, reviewed blueprint, explicit-ON spaced clusters, bid/ask cells, performance tests |
| Heatmap | 🟥 Not implemented | Data source/calculation contract unapproved | Owner reference image, source feasibility, validated contract, reviewed blueprint, renderer |
| Liquidation Maps | 🟥 Not implemented | No validated liquidation dataset/contract | Zero-cost source feasibility, validated calculation, reviewed blueprint/reference, renderer |

Correctness constraints remain: candle-index alignment; warm-up values null; prefix causality; stale-value invalidation on symbol/venue/dataset/timeframe changes; Footprint OFF preserves standard candle spacing; Footprint ON alone activates spaced clusters. Footprint and Heatmap visuals remain gated on the user's reference images and reviewed blueprint. No aggregate indicator percentage is invented.

## ZERO COST and operational disposition

No deployment, paid service, Vercel/Cloudflare operation, production credential, Termux command, device change, or `main` modification. No user action or Termux step is required in this cycle.
