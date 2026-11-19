# WORK CYCLE BATCH 53 — Exact-head CI, WSS runtime boundary, Gate 10 and indicator audit

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Starting HEAD:** `8f377cfb07b082ce237cf3ac9137efbfbcc4f5d8`  
**Scope:** exact-head CI completion; isolated WSS deployment/runtime evidence; Gate 30/31/34 evidence review; technical-indicator implementation audit and progress reconciliation.  
**Cost:** ZERO COST  
**Deployment:** none  
**Termux:** not required  
**Main:** untouched

## 1. Exact-head automated verification

The Batch 52 documentation checkpoint received completed CI verification on the exact branch HEAD `8f377cfb07b082ce237cf3ac9137efbfbcc4f5d8`.

| Check | Run | Result |
|---|---:|---|
| Automated Tests & Build | [44468970676](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970676) | **SUCCESS — 32/32 steps** |
| CodeQL Python + JavaScript/TypeScript | [44468970595](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970595) | **SUCCESS — both language jobs** |
| Full Git History Secret Audit | [44468970614](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970614) | **SUCCESS** |

Exact workflow log evidence:
- Frontend Vitest: **234 passed across 28 test files**.
- Backend pytest: **1,032 passed in 40.72 seconds**.
- Frontend npm audit: **0 vulnerabilities**; audit enforcement succeeded.
- Frontend production build and 77-file source/bundle credential scan: **PASS**.
- Android read-only preflight and immutable preview publisher tests: **PASS**; no APK publication was performed in this batch.
- Backend dependency audit and backend container image build: **PASS**.
- Redis ACL/AOF persistence, fail-closed API behavior, backend reconnection, non-root UID/GID, mounted-volume ownership, SQLite integrity and restart persistence, and HTTP rate-limit smoke: **PASS**.
- Trivy HIGH/CRITICAL image scan and JSON vulnerability report export: **PASS**. Report artifact: [14502883681](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44468970676/artifacts/14502883681).
- The CI log's conditional failure message was not executed: `AUDIT_OUTCOME=success`, and the enforcement step completed successfully. No audit suppression or threshold weakening occurred.

This verifies the repository and ephemeral CI runner. It does not certify a separate production host, device, persistent volume, or external recovery destination.

## 2. Isolated WebSocket preview — current verified boundary

Deployment: [dezzta-chart-ws-n3mvfjv0n-deszztagd377-pixel.vercel.app](https://dezzta-chart-ws-n3mvfjv0n-deszztagd377-pixel.vercel.app)  
Deployment ID: `dpl_5VXGuNtmkxzWTDQkcGZgBrrL7WrK`  
Source SHA: `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`

Read-only Vercel inspection confirmed:
- Deployment state **READY**.
- Project `live=false`; no production promotion.
- Vercel Authentication / SSO protection enabled for **all** deployment targets.
- Deployment type is a Vercel Lambda deployment.
- The project-details read endpoint did not expose the effective `resourceConfig.fluid` value. Therefore the checked-in `fluid: true` plus its unit test remain configuration-source evidence, not independent effective-runtime read-back.
- Runtime log query for the deployment over the available 30-minute window returned no logs; runtime error query over one hour returned no errors. The initial 60-minute runtime-log request exceeded the Hobby retention window and was corrected to 30 minutes. “No logs” is not evidence that a WebSocket request succeeded.
- No authenticated browser WSS round-trip, Android WebView test, 330-second foreground session, or cross-instance fan-out was performed in this cycle.

**WSS disposition:** no source defect was demonstrated by the repository audit or current runtime-log evidence. The POC remains synthetic-only and Gate 36 remains OPEN. Do not create another deployment just to generate logs, do not weaken SSO, and do not expose a temporary public share link to automate around protection.

## 3. Gate 30 — production-like SQLite restore

Repository/CI evidence confirmed:
- SQLite Online Backup API is used for consistent snapshots.
- Backup and restore publication use private temporary files and atomic no-overwrite behavior.
- Restore checks SQLite integrity, foreign keys, required application tables, row counts, row hashes, schema hash, application-domain readback, and a committed write/read/cleanup probe.
- The integrated regression chains an application-domain snapshot through AES-256-GCM encryption, authenticated decryption, and the full fresh-path restore drill.
- Exact-head backend tests include the backup/restore coverage and all 1,032 tests passed.

**Still OPEN:** the owner-device/target-host drill has not been run. Required evidence remains a fresh destination on the intended target, source preservation, representative application-level reads and recovery timing. Same-device recovery is useful local recovery evidence but is not off-host disaster recovery.

## 4. Gate 31 — encrypted off-host backup and key custody

Repository evidence confirms versioned authenticated encryption using AES-256-GCM, PBKDF2-HMAC-SHA256 (600,000 iterations), random salt/nonce, authenticated header, 1 MiB streaming chunks, private temporary files, and no-overwrite publication. Wrong-key and tampered-ciphertext paths fail closed; automated tests cover cleanup and destination preservation.

**Still OPEN:** no verified off-host encrypted artifact, separate recovery-key custody, retention/access-control test, or restore from the off-host copy exists. The owner environment is one Android phone; do not assume a second device or a secure free external destination. No paid bucket, KMS, or cloud storage was enabled.

## 5. Gate 34 — persistent volume

Exact-head CI's container smoke test passed:
- The backend container ran as non-root UID/GID `10001:10001`.
- The mounted data directory/database ownership was checked.
- SQLite integrity was checked against the mounted database.
- The test verified persistence across container restart and Redis AOF data across service restart.
- The API failed closed during Redis outage and recovered after Redis returned.

**Still OPEN:** this is a GitHub-hosted ephemeral CI runner and test volume, not the owner's production host. No real host mount, filesystem capacity/disk-full behavior, process replacement, or host recovery evidence exists. Keep the gate open; do not equate a CI named volume with production persistent storage.

## 6. Remaining Gate 10 disposition

| Criterion | Repository / CI status | External acceptance status |
|---:|---|---|
| 8 — production secrets | source, bundle and Git-history scans pass | OPEN — actual host secret injection not verified |
| 20 — Firebase auth/revocation | emulator/unit groundwork only | OPEN — real no-billing provider and deployed client path not accepted |
| 25 — Redis shared guard | Redis ACL/AOF/fail-closed CI smoke passes | OPEN — no independently operated production Redis host |
| 30 — backup restore | integrated encrypted application restore test passes | OPEN — owner target-host restore absent |
| 31 — encrypted off-host backup | encryption and local recovery tests pass | OPEN — off-host artifact and separate key custody absent |
| 34 — persistent volume | mounted-volume ownership/integrity/restart CI smoke passes | OPEN — actual host volume absent |
| 35 — HTTPS backend | repository configuration and CI build evidence only | OPEN — no accepted owner-host HTTPS deployment |
| 36 — WSS proxy | isolated synthetic preview READY, SSO protected | OPEN — browser/Android/330-second/effective Fluid/cross-instance proof absent |
| 38 — observability | bounded process-local metrics tests pass | OPEN — host collector, retention and protected dashboard absent |
| 39 — incident response | sanitized local alert reporter tests pass | OPEN — responsible adult operator, escalation and observed drill absent |

Gate 10 remains **0/10 formally closed**. CI improvements strengthen repository evidence but do not waive external acceptance.

## 7. Technical indicator progress — complete inventory

The following are calculation/data foundations, not finished user-visible chart indicators:

| Indicator / layer | Verified implementation | User-visible chart status |
|---|---|---|
| SMA 20 | Calculation + unit tests | Not integrated |
| EMA 20 | Calculation + unit tests | Not integrated |
| RSI 14 (Wilder) | Calculation + unit tests | Not integrated |
| MACD 12/26/9 | Calculation + unit tests | Not integrated |
| Bollinger Bands 20,2 | Calculation + unit tests | Not integrated |
| Shared `useMarketIndicators()` hook | Uses exact validated shared backend snapshot; suppresses DEMO/loading/unavailable/error values | Hook exists; no controls/panes |
| Footprint | Deterministic offline simulated aggregation + fixtures | Visual work waits for owner reference; OFF must preserve ordinary candle spacing |
| Heatmap | No implementation verified | Wait for owner reference and approved scoped blueprint |
| Liquidation Maps | No implementation verified | Wait for owner reference and approved scoped blueprint |

The exact-head frontend suite includes **7 indicator calculation tests** within the 234 passing tests. The calculation tests exercise all 18 configured chart timeframes, warm-up alignment, Wilder RSI, MACD signal warm-up, Bollinger population deviation, and invalid-input rejection.

**Roadmap guard:** Stage 1 remains active. Visible indicator controls/panes belong to Stage 4 and remain parked. Do not start chart UI implementation early. Footprint, Heatmap and Liquidation Maps additionally require their owner-supplied visual references. No indicator value may be fabricated from DEMO data or presented as live.

## 8. Progress and cost accounting

- Stage 1: **30/40 criteria; 300/400 ticks; 75% provisional**.
- Gate 10: **0/10 formally closed**; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**. Historical 20.9% remains historical until M1–M8 weights and criteria are approved and scored.
- No Stage 1 ticks or overall points are awarded for this CI/audit/documentation cycle.
- No Vercel deployment, Cloudflare deployment, production promotion, paid provider, billing activation, paid storage, or notification provider.
- No Termux command, package, repository, or keyring change.
- Protected `main` remains untouched.

## 9. Next evidence-driven sequence

1. Preserve the current passing exact-head CI as the repository baseline.
2. Keep WSS preview isolated; obtain owner-authenticated browser and Android WebView observations only through the existing SSO-protected deployment. Do not create a new deployment or bypass SSO.
3. If an independently readable Vercel project setting endpoint becomes available, read back effective Fluid Compute without changing project settings.
4. Prepare a phone-only Gate 30 restore drill only when the owner explicitly wants to run the existing reviewed procedure; never ask for secrets or paste recovery material into chat.
5. Keep Gate 31, 34, 38 and 39 externally constrained while the owner has one Android device and no separate production host/operator.
6. Maintain the technical indicator foundations and keep Stage 4 visual implementation parked until the official roadmap gate and owner references are satisfied.

**Final engineering disposition:** Batch 53 closes the outstanding CI-verification uncertainty for Batch 52 and strengthens the Gate 30/31/34 evidence map. It does not falsely close any external gate or claim a live WSS round-trip. ZERO COST, SSO preserved, production untouched, `main` protected.
