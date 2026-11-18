# DEZZTA CHART — Batch 33: Gate 30 / 31 / 36 deep audit

**Date:** 18 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Audited exact HEAD:** `2cdbae52711ed87e9f3acad5f94c15096196a57f`  
**Scope:** exact-head CI, SQLite backup/restore, authenticated WebSocket lifecycle, npm advisory, progress-reference correction  
**Cost:** ZERO COST  
**Deployment:** none  
**Main:** untouched

## 1. Exact-head CI

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44307814857](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44307814857) | **FAILURE** only at final frontend dependency-audit enforcement |
| CodeQL Python + JS/TS | [44307814928](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44307814928) | **SUCCESS** |
| Full Git History Secret Audit | [44307814948](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44307814948) | **SUCCESS** |

The Automated Tests job completed every step before step 27 successfully: frontend dependency audit reporting, frontend unit tests, production build, source and bundle credential scans, Android preflight and immutable publisher tests, backend tests, synthetic outbox benchmark, backend dependency audit, backend container build, Redis guard/persistent-volume smoke, Trivy scan and vulnerability-report export. The only failing step is `Enforce frontend dependency audit result`. This is intentionally fail-closed; do not describe the workflow as green. Test totals from this exact run were not independently extracted, so this report records step conclusions rather than copying previous-run counts.

## 2. Gate 30 — SQLite backup / restore audit

### Verified source behavior

- `backend/app/sqlite_backup.py` creates snapshots using SQLite's Online Backup API, not a raw live-file copy.
- Snapshot destination is written to a temporary file in the destination directory and checked with `PRAGMA integrity_check`.
- POSIX snapshots are changed to owner-only permissions and flushed before publication.
- Default backup replacement behavior is explicit; the no-overwrite path uses an atomic hard link and fails closed when the destination exists or the filesystem does not support the operation.
- Restore opens the source backup read-only, copies through SQLite's Online Backup API, checks full integrity and foreign keys, uses owner-only permissions on POSIX, and publishes with a no-overwrite atomic hard link.
- File and directory flush failures are surfaced rather than reported as durable success. Tests verify cleanup and the special case where publication already happened but the final directory flush fails.
- `backend/app/sqlite_restore_drill.py` checks required application tables, integrity, foreign keys, table row counts, per-row SHA-256 hashes, schema SHA-256, application-domain readback, and a committed write/read/cleanup probe through independent connections.
- Drill outputs are new paths; the source is opened read-only and must remain unchanged. Failed verification removes only outputs created by that drill invocation.
- CI test `test_encrypted_application_backup_round_trip_feeds_full_restore_drill` covers SQLite snapshot → authenticated encryption → decrypt → full restore drill.

### Security details verified

- `backend/app/backup_encryption.py` uses versioned `DZCBK01` format.
- Key derivation: PBKDF2-HMAC-SHA256, 600,000 iterations, 32-byte key.
- Encryption: AES-256-GCM, 16-byte salt, 12-byte nonce, 16-byte authentication tag; header is authenticated as additional data.
- Input/output is streamed in 1 MiB chunks.
- Decryption writes to a private temporary file and only publishes after GCM finalization authenticates successfully. Wrong passphrase or tampered ciphertext cannot publish plaintext.
- Atomic no-clobber publication prevents overwriting an existing backup/restore destination. POSIX files are owner-only and parent directory flush is attempted.

### Gate 30 remains OPEN

The source and CI prove local backup/restore behavior in test fixtures. They do **not** prove a restore on the owner's actual database/host. External acceptance still needs a fresh destination on the intended target, source preservation, application-level readback and an owner-observed recovery result. No production database was accessed.

## 3. Gate 31 — encrypted recovery and custody

### Verified

The code provides authenticated encryption/decryption and CI integration into the full SQLite restore drill. It does not upload the encrypted file or choose a storage destination.

### Still missing

- An actual off-host encrypted artifact.
- Recovery key stored and controlled separately from that artifact.
- Retention and access-control policy for both artifact and key.
- Successful recovery from the off-host copy on the intended target.
- A zero-cost storage location already owned/available and verified as suitable.

No cloud bucket, paid storage, managed database, or external provider was provisioned. Gate 31 remains OPEN.

## 4. Gate 36 — WebSocket source and acceptance boundary

### Verified source path

The authenticated `/ws/market-data` route:

1. Checks the request origin and shared connection capacity before accepting.
2. Requires a bounded-time authentication message and verifies the Firebase identity.
3. Applies account-level connection capacity and validates exact provider/series identity.
4. Re-checks active instrument mapping and entitlement before subscription.
5. Captures the durable outbox high-water cursor and takes the snapshot/registers the stream without an intervening await.
6. Supports bounded durable replay, with explicit resnapshot fallback for invalid/unavailable/oversized replay.
7. Closes slow consumers on queue overflow so updates are not silently skipped.
8. Re-verifies the supplied identity token and entitlement on a monotonic deadline, and renews the shared connection lease.
9. Cancels pending tasks and unsubscribes the stream on disconnect; releases the shared lease in the outer cleanup.

### Architectural boundary

The `OhlcvStreamHub` subscriber queues are process-local. A shared Redis guard protects connection capacity/leases, but that is not evidence of cross-instance market-data fan-out. The isolated Vercel POC is explicitly synthetic-only; HTTP health is not a WebSocket handshake test.

### Gate 36 remains OPEN

No exact-head public deployment was made. Therefore no live WSS Upgrade/ping-pong, Android WebView compatibility, 330-second foreground owner observation, Vercel platform-close attribution, effective Fluid Compute read-back, or cross-instance fan-out is claimed. A code-only change cannot prove these host/device properties. No safe source defect was demonstrated in this audit; no speculative broker or paid service is introduced.

## 5. Dependency audit blocker

The current official [npm version listing](https://www.npmjs.com/package/picomatch?activeTab=versions) still reports `4.0.7` as latest. The [GitHub advisory GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) and [OSV record](https://osv.dev/vulnerability/GHSA-fc5q-39xc-vjpf) still identify versions through 4.0.7 as affected and state no patched version. Keep the final audit fail-closed. No force downgrade, override, fork, hand-patch, suppression or waiver.

## 6. Deployment, zero-cost and device controls

- No Vercel deployment/retry or production promotion.
- No Cloudflare resource, paid service, subscription, billing/plan change, or publication fee.
- `main` untouched; active branch remains `phase-2/market-data-foundation`.
- No Termux required for this remote source/CI audit. Any future device-side prerequisite will be explained before asking the owner to install or run anything.

## 7. Progress accounting

| Indicator | Verified state |
|---|---|
| Stage 1 | **75% provisional — 300/400 ticks; 30/40 criteria** |
| Gate 10 | **0/10 formally closed** |
| Open criteria | **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** |
| Stages 2–6 | **NOT SCORED** |
| Overall project | **NOT ESTABLISHED**; M1–M8 weights and criterion mapping not approved |
| Historical overall checkpoint | 20.9%, historical only |
| Cost | ZERO COST |
| Main | untouched |

No stage tick or gate closure is awarded for source-only, CI-only, documentation-only or synthetic evidence where owner-host/device acceptance is required.

**Engineering disposition:** the code-level SQLite and WebSocket paths have been inspected more deeply. Gate 30/31 and Gate 36 remain externally blocked, not because a known safe source defect is being ignored, but because the remaining acceptance evidence must come from the actual target host/device and custody arrangement. Do not manufacture that evidence or spend money to bypass it.
