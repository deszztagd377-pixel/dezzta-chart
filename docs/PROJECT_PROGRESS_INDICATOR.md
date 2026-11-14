# DEZZTA CHART — Project Progress Indicator

Status: **operational project-tracking specification**  
Last audited: 2026-11-14  
Repository: https://github.com/deszztagd377-pixel/dezzta-chart  
Official working branch: `phase-2/market-data-foundation`  
Official current stage: **Stage 1 — Foundation, Security & Data Integrity**

> This document defines the **project-process progress indicator**. It is not an in-app technical indicator, chart overlay, or APK feature. Technical indicators such as SMA, EMA, RSI, MACD and Bollinger Bands are separate product work governed by Stage 4.

## Visual presentation standard — permanent through Stage 6

The project-process indicator uses the same six-card dashboard layout in every progress report and documentation snapshot. The visual reference is embedded below:

![DEZZTA CHART six-stage project progress dashboard](assets/project-progress-dashboard.svg)

### Fixed visual rules

- Always show all six official stages together, in the official order.
- Each stage keeps its own colored card and progress bar; do not redesign the layout between stages.
- Stage 1: emerald/green. Stage 2: cyan/blue. Stage 3: violet. Stage 4: amber. Stage 5: pink. Stage 6: slate.
- Status colors: green = verified/active; amber = in progress or provisional; red = blocked/failed; slate = not opened/not scored. Color is always accompanied by readable status text.
- Only show a numeric percentage and filled progress bar when that stage has an approved, evidence-backed scoring model. For stages not yet audited, show **NOT SCORED** and an empty/neutral bar, never a guessed 0% or an invented completion percentage.
- Show the active official stage prominently, and retain the same card geometry, typography hierarchy, spacing, and color mapping from Stage 1 through Stage 6.
- Keep the overall-project historical checkpoint in a separate footer/summary. It must never be confused with an individual stage percentage.
- This is a documentation/project-management visual. It must not be inserted into the APK or treated as an in-app technical indicator.

## 1. Six-stage dashboard

| Stage | Official scope | Current official state | Progress display |
|---:|---|---|---|
| 1 | Foundation, Security & Data Integrity | Active; 30/40 provisional criteria accepted; 10 external criteria open | **75% provisional** |
| 2 | Market Data Infrastructure | Not officially opened; preparatory code exists on the branch | Not scored |
| 3 | Chart Engine & Timeframe | Not officially opened | Not scored |
| 4 | Indicators & Analytics | Not officially opened; calculation groundwork exists | Not scored |
| 5 | Professional UI & Interactive Tools | Not officially opened; expansion gate applies | Not scored |
| 6 | Hardening, Validation & APK Release | Not officially opened | Not scored |

A stage is not opened until all preceding stage acceptance requirements are met and the transition is explicitly recorded. Branch names, code already present, documentation, or CI success cannot silently advance the official stage.

## 2. Stage 1 progress meter

The Stage 1 acceptance matrix contains 40 criteria. For the display meter, each fully accepted criterion earns 10 ticks.

| Metric | Value |
|---|---:|
| Total criteria | 40 |
| Ticks per criterion | 10 |
| Total available ticks | 400 |
| Provisionally accepted criteria | 30 |
| Earned ticks | 300 |
| Remaining criteria | 10 |
| Remaining ticks | 100 |
| Stage 1 meter | **300 / 400 = 75% provisional** |

Calculation:

`Stage 1 progress = (accepted criteria × 10) ÷ 400 × 100`

One tick represents 0.25 percentage points of Stage 1. A criterion earns all 10 ticks only when its complete acceptance boundary and evidence are satisfied. Otherwise it earns zero. No fractional credit is awarded.

**Important accounting distinction:** 75% is a provisional Stage 1 checklist meter, not production acceptance. Stage 1 is not production-accepted.

## 3. Ten open Stage 1 acceptance criteria

| Criterion | Required evidence / blocker | Safe handling |
|---:|---|---|
| 8 | Owner-controlled no-billing host secret injection and secret absence checks | Repository scans help but cannot prove host configuration |
| 20 | Firebase sign-in, expiry/revocation, entitlement denial and browser/Android flows | Keep production integration disabled unless no-billing configuration is verified |
| 25 | Self-hosted Redis TLS, ACL, private binding, persistence and failure behavior | Requires existing owner-controlled hardware; no paid Redis |
| 30 | Restore a production-like backup into a fresh database and verify application records | CI restore regression is supporting evidence, not the target-environment drill |
| 31 | Encrypted off-host backup, separately stored key, retention/access policy and recovery drill | Keep blocked while compatible authenticated encryption tooling is unresolved |
| 34 | Persistent volume mount, ownership, permissions, restart durability and disk-pressure recovery | Requires target host/device evidence |
| 35 | HTTPS health checks, startup failure and backend-only secrets | Local/LAN is acceptable while public exposure would create cost |
| 36 | Authenticated WSS from supported web and Android clients through reverse proxy | Requires target environment/client evidence |
| 38 | Self-hosted metrics/logs, bounded retention, dashboard and access control | Defer rather than introduce paid observability |
| 39 | No-incremental-cost alert route and documented incident ownership/escalation/recovery | Do not assume email/SMS/push is free |

These are external or target-environment acceptance gates. A repository-only change cannot close them.

## 4. Overall project percentage — separate meter

Historical checkpoints preserved from the owner-approved conversation:

- 20.3% first.
- 20.9% later and most recent owner-confirmed historical checkpoint.
- 19.60% is an older formally recorded estimate, not evidence of regression.
- 19.9% has no reproducible calculation located.

**Fresh overall percentage: not established.**

The proposed M1–M8 weighted ledger totals 100%, but remains unapproved and unscored criterion-by-criterion. Therefore no new overall percentage may be published until:
1. The owner approves or revises the eight milestone weights.
2. Every deliverable is mapped to one primary milestone.
3. Each acceptance criterion is classified using verified evidence.
4. Partial completion is justified and duplicate credit is excluded.
5. The arithmetic is independently checked and recorded against an exact branch HEAD.

Formula after approval:

`Overall progress = Σ (milestone weight × verified completion fraction)`

Do not substitute Stage 1's 75% for overall project progress. Do not award progress merely for commits, file count, code volume, documentation, or unrelated green CI.

## 5. Milestone mapping and anti-double-counting

The proposed ledger groups are:

| ID | Group | Proposed weight | Scoring state |
|---|---|---:|---|
| M1 | Application shell and core chart rendering | 15% | Pending owner approval and audit |
| M2 | Data contracts, validation and persistence foundation | 20% | Pending owner approval and audit |
| M3 | Authentication and application security foundation | 10% | Pending owner approval and audit |
| M4 | Chart interaction and educational drawing/measurement tools | 15% | Pending owner approval and audit |
| M5 | Educational indicator and mathematical visualization layer | 15% | Pending owner approval and audit |
| M6 | Responsive UX, accessibility and visual design | 10% | Pending owner approval and audit |
| M7 | Watchlist, settings and user preference persistence | 5% | Pending owner approval and audit |
| M8 | Quality engineering, reproducible builds and release readiness | 10% | Pending owner approval and audit |
| | **Total** | **100%** | **Not yet an approved scoring model** |

One capability receives one primary milestone credit. Tests validate that capability; they are not a second feature. A calculation helper is not counted as visible indicator UI. A design document is not counted as implemented functionality. DEMO data is never counted as live provider delivery.

## 6. Work-cycle status vocabulary

Every cycle uses these states consistently:

- **Verified complete:** acceptance boundary passed with reproducible evidence.
- **Implemented, not fully verified:** code exists but acceptance evidence is incomplete.
- **In progress:** an active task with a defined next validation.
- **Blocked — internal:** repository-side issue that can be resolved without owner-side access; remediation should be performed in the same work cycle where safe.
- **Blocked — external:** requires owner-controlled host/device, provider, credentials, or owner decision. State the exact dependency and safe alternatives.
- **Deferred by zero-cost/security constraint:** no paid service, trial that may bill, insecure bypass, or weakened security is permitted.
- **Not started / not scored:** future stage or unapproved scope.

A blocker report must state: finding, impact, evidence, remediation attempted/applied, remaining dependency, and the acceptance test that will close it. Do not repeatedly describe the same blocker without taking an available remediation step.

## 7. Per-cycle mandatory report

Each project work cycle must record:

1. Official stage and branch.
2. Exact starting and ending HEAD.
3. Stage meter and formula.
4. Overall historical checkpoint separately from any approved fresh calculation.
5. Acceptance criteria changed and their before/after states.
6. Problems found and concrete fixes applied.
7. Files created/changed and why.
8. Commands or scripts executed by the development environment, if any.
9. Test/build/security results tied to the exact commit.
10. CI run links and final conclusions; queued/running workflows must not be called passed.
11. New commit SHA.
12. Termux/device action only when a specific test requires it, with the reason and verified compatibility. Never hand over a known failing command or ask the owner to repair generated files.

## 8. Termux and zero-cost constraints

- Product direction remains zero incremental cost.
- Do not introduce paid hosting, market-data subscriptions, paid APIs, managed Redis, paid backups/monitoring, paid runners, or trials that can bill.
- Do not switch the owner's Google Play Termux installation to an incompatible repository or bypass APT signature verification.
- The documented Google Play Termux keyring/repository mismatch remains an open external tooling constraint for the encrypted-backup gate. Keep the working source intact; do not import unverified keys, bypass signatures, or weaken the cryptography requirement.
- No Termux command is required for this project-process indicator documentation.
- Google Play publication remains deferred; the target is an installable APK on the owner's device when Stage 6 acceptance is reached.

## 9. Stage gates and expansion rules

- Stage 1 must be accepted before official transition to Stage 2.
- Each subsequent stage must satisfy its own documented acceptance gate before moving forward.
- The 40% overall-project gate is for major UI/feature expansion planning. It requires a reconciled approved ledger, scoped blueprint, and owner review. It does not bypass stage order.
- Visible technical indicator controls and overlays belong to Stage 4, not the project-process progress meter.
- Footprint, Heatmap and Liquidation Maps remain gated by owner-provided visual references, a scoped blueprint and owner review. Footprint remains explicitly SIMULATED unless a separately validated real-data source is implemented.

## 10. Current evidence snapshot — 2026-11-14

- Repository: `deszztagd377-pixel/dezzta-chart`
- Working branch: `phase-2/market-data-foundation`
- Source HEAD audited before the project-meter documentation commit: `10046851065e41fa73bdcf757eb87b02e5a12b6d`
- Automated Tests: [run #43567126816](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43567126816) — success on that exact source HEAD.
- CodeQL: [run #43567126843](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43567126843) — success on that exact source HEAD.
- Full Git History Secret Audit: [run #43567126815](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43567126815) — success on that exact source HEAD.
- The project-meter documentation commit is separate from the tested source commit. Its own Automated Tests workflow was still running at the time of this snapshot; do not treat it as passed until its exact-HEAD run concludes successfully.
- CI success does not close external criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 or 39.
- Stage 1 remains 300/400 ticks = 75% provisional and not production-accepted.
- No fresh overall percentage is calculated.

## 11. Change log

| Date | Change |
|---|---|
| 2026-11-14 | Added explicit project-process progress indicator specification, six-stage dashboard, Stage 1 tick calculation, external blocker register, overall-percentage safeguards, work-cycle reporting contract and Termux/zero-cost constraints. |


## Latest work-cycle evidence update — 2026-11-14

### Criterion 30 — repository-side restore coverage audited

The existing test `backend/tests/test_sqlite_backup.py::test_full_application_database_restore_preserves_all_shared_sqlite_domains` already exercises a full shared-application SQLite snapshot and fresh-path restore. It reopens and verifies representative instrument-registry, entitlement, price-alert, coverage, OHLCV, and durable outbox/replay records, then confirms a post-restore write advances the outbox sequence.

This is meaningful repository/CI evidence and identifies the correct next phone-only restore-report target. It does **not** close criterion 30: the matrix still requires a timestamped owner-device restore report and application-level verification on the actual owner environment. No tick is added; Stage 1 remains 300/400 = 75% provisional.

### Latest exact-HEAD CI update

At HEAD `21eabf46bf51f076f074e8fc6c2eb55723111956`:
- Full Git History Secret Audit — success.
- CodeQL — success.
- Automated Tests — still running; frontend tests/build, backend tests, bounded synthetic SQLite outbox benchmark, dependency audit, backend image build, and shared-Redis/persistent-volume container smoke test had completed successfully. Backend container image scan was still running at the last check.

Do not mark the complete workflow successful until the image scan, report export/upload, and final job conclusion are complete.

### Termux dependency gate

A fresh check of the matching Google Play Termux issue tracker found the signing-key mismatch reports still open, including issues [#1642](https://github.com/termux-play-store/termux-issues/issues/1642) and [#1648](https://github.com/termux-play-store/termux-issues/issues/1648). The missing key is the upstream `termux-autobuilds` signing key, which is not included in the Play build's installed keyring. This confirms that the previously documented refusal to switch repositories or bypass signature checks remains correct.

No Termux command is required for this cycle. Preserve the original working repository configuration and the `cryptography>=50,<51` security requirement.


### CI completion reconciliation — 2026-11-14

The prior Automated Tests run `43568430935` later reached a **cancelled** workflow conclusion. Its recorded frontend checks, backend tests, synthetic outbox benchmark, dependency audit, container build, Redis/persistent-volume smoke test, Trivy image scan, vulnerability report export, and artifact upload steps all show success; however, the enclosing job/run conclusion is cancelled, so it is not counted as a fully green workflow.

The documentation-only follow-up HEAD `c63560ebf16bd16ab3de482df35c35b381fa009e` has fresh Automated Tests and CodeQL runs in progress and Full Git History Secret Audit pending. Their final conclusions must be checked on the exact latest HEAD before reporting full CI acceptance.


## Authoritative exact-HEAD CI and external-gate entry — 2026-11-14

This section supersedes earlier pending/in-progress CI snapshots above.

- Audited branch: `phase-2/market-data-foundation`.
- Exact HEAD: `d64ad3fa1620f75b363b4f32e3df01b06a62c2d2`.
- Automated Tests #43568751544: **SUCCESS** on this exact HEAD. The completed workflow includes frontend tests/build and bundle-secret checks, backend tests, dependency audits, bounded SQLite outbox benchmark, backend container build, Redis/shared-guard and persistent-volume smoke test, Trivy image scan, report export/upload, and cleanup.
- CodeQL #43568751559: **SUCCESS** on this exact HEAD for JavaScript/TypeScript and Python.
- Full Git History Secret Audit #43568751546: **SUCCESS** on this exact HEAD.
- Earlier cancelled runs on superseded commits are not treated as failures of this HEAD and are not used as proof.

### Entry decision: ten external gates

Repository/CI prerequisites for beginning the external-gate work are now green. Work may proceed against the ten open criteria without changing the official stage. **Stage 1 remains 300/400 ticks = 75% provisional; none of the ten external criteria has been awarded a tick.**

The first viable phone-only evidence target is criterion 30 (fresh SQLite restore and application-record verification). Its local restore path uses Python/SQLite standard-library functionality and does not require the blocked `cryptography` package. The successful CI restore regression is supporting evidence only; the owner-device report remains outstanding.

Criteria 8, 20, 25, 31, 34, 35, 36, 38 and 39 retain their distinct owner-host, provider, storage, operator or no-billing dependencies. Local/CI subtests must not be mislabeled as production acceptance.

### Current dashboard snapshot

- Stage 1 — emerald: **75% provisional**, 300/400 ticks, 30/40 criteria; 10 external gates open.
- Stage 2 — cyan: **NOT SCORED**.
- Stage 3 — violet: **NOT SCORED**.
- Stage 4 — amber: **NOT SCORED**.
- Stage 5 — pink: **NOT SCORED**.
- Stage 6 — slate: **NOT SCORED**.
- Overall project: **20.9% historical owner-confirmed checkpoint**; fresh weighted total remains unestablished.


## Gate 10 authorization and execution checkpoint — 2026-11-14

The owner explicitly authorized opening the ten external acceptance gates. This is an execution authorization, not an acceptance waiver and not a stage transition.

- Official stage remains Stage 1.
- Stage 1 remains 300/400 ticks = 75% provisional.
- The ten external criteria remain open until their individual evidence packages are reviewed.
- First active workstream: criterion 30, fresh SQLite restore and application-level verification.
- The restore helper now has a no-overwrite publication design, integrity and foreign-key checks, private POSIX permissions, and failure-cleanup tests. It is still repository implementation until the exact-HEAD CI passes and the owner-device restore report is produced.
- The process indicator is documentation-only; it is not an APK technical indicator.

### Current exact HEAD before this implementation batch

`a6fa0d68691bdf943101e71c5be70df0ba30d591` — all three workflows passed on this exact HEAD:
- Automated Tests #43569290818 — success.
- CodeQL #43569290707 — success.
- Full Git History Secret Audit #43569290886 — success.

The next implementation commit must receive its own fresh CI results before any code acceptance is claimed.
