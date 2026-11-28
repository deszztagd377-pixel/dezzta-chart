# VERIFIED CURRENT CHECKPOINT — 28 November 2026

**Validated code/test HEAD:** `9f49d1affc7f784904bb99dc1c5b3393dc87a6a9` on `work/batch95-websocket-ack-protocol`.  
**PR #13:** OPEN, unmerged; base `phase-2/market-data-foundation`.  
**Repository safety:** `main` remains `e3841681bc69b73619058deaf939df82ae5116a1`; no merge, deployment, paid service, billing change, or new Cloudflare resource.

## Exact-head CI — 4/4 SUCCESS

- Automated Tests — [run 46104901664](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46104901664): **SUCCESS**, 41/41 steps; frontend 338/338 tests; backend 1,437 passed, 1 skipped; Worker runtime 26/26.
- CodeQL — [run 46104901668](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46104901668): **SUCCESS**.
- OCI ARM64 Image Readiness — [run 46104901656](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46104901656): **SUCCESS**.
- Full Git History Secret Audit — [run 46104901671](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46104901671): **SUCCESS**.

The Automated Tests workflow completed all 41 steps. It includes the pinned workerd/Miniflare proof, Durable Object runtime suite, frontend tests/build, Redis TLS fixture, backend suite, SQLite benchmarks, dependency audit, container build/smoke test, and image scan. Test totals from the run: Worker runtime 26/26; frontend 338/338 across 35 files; backend 1,437 passed and 1 skipped. All four workflow runs are terminal; none remains in progress.

## Latest protocol change

The frontend OHLCV parser now enforces generation identity binding:
- Production stream events require `generationId === streamId`.
- Synthetic proof events require generation `synthetic-v1` and stream ID `synthetic:${seriesKey}`.
- Tests cover production binding, synthetic binding, mismatches, and the cursor/digest fixtures.

The first two CI attempts exposed stale fixtures; those fixtures were aligned with the intended contract. The final exact-head run above passed. This change does **not** activate production ACK.

## Stage control

**Stage 1: 30/40 = 75% provisional. Gate 10: 0/10 formally closed.** Stage 2 remains preparatory and is not authorized. The ten owner-controlled evidence criteria still open are **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39**. All are YELLOW pending real evidence; repository CI or synthetic proof cannot substitute for production acceptance.

**Production WebSocket boundary — YELLOW:** FastAPI still has no production ACK receive/receipt handler. The synthetic Worker ACK proof is code/test-only. The frontend checks digest syntax but does not yet cryptographically verify the event digest before applying it. Production Firebase-to-Worker session grants, stable reconnect receipt semantics, public WSS, browser/Android E2E, provider redistribution rights and account-level zero-cost certification remain open.

**Deadline:** 24 December 2026 — **26 calendar days remain** from 28 November.

**Controls:** ZERO COST; no paid services, billing changes, deployment, PR merge, or `main` modification. No autonomous background/10-minute coding is running; CI is monitored during the active session.

---

# VERIFIED CURRENT CHECKPOINT — 27 November 2026 (supersedes older snapshots below)

**Last validated code/test HEAD:** `0409c8690650eb9fa78d28e7f4a3bb64b28b634e`.  
**Documentation follow-ups:** subsequent commits in this branch update only these two status documents; no source/runtime files changed and no new CI run is claimed for documentation-only commits.  
**PR #13:** OPEN, unmerged, base `phase-2/market-data-foundation`.  
**Stage 1:** 30/40 = 75% provisional; Gate 10 = 0/10 formally closed. Stage 2 remains preparatory and is not authorized.

## WebSocket lease lifecycle — GREEN at synthetic code/test level only

The validated code/test HEAD `0409c8690650eb9fa78d28e7f4a3bb64b28b634e` has all four required GitHub Actions workflows terminal SUCCESS:
- Automated Tests — [46019484467](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46019484467), SUCCESS (41/41 job steps).
- CodeQL — [46019484655](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46019484655), SUCCESS.
- OCI ARM64 — [46019484485](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46019484485), SUCCESS.
- Full Git History Secret Audit — [46019484584](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46019484584), SUCCESS.

The six code/test checks recorded as GREEN are: atomic lease acquisition/collision-safe takeover; same-owner renewal and expiry; monotonic fencing on takeover; owner/fence/live-lease validation on ACK; per-socket lifecycle with ping/ACK renewal, close/error release, alarm expiry and stale-owner fan-out rejection; expiry-aware compaction. The Automated Tests job passed the pinned workerd/Miniflare proof, Durable Object runtime tests, frontend tests/build, backend tests, Redis TLS fixture, container build/smoke/scan and related checks.

**Production boundary remains YELLOW:** Firebase-verified session grant and real consumer identity; production event generation/sequence/digest contract and FastAPI ACK integration; public WSS/TLS and browser/Android E2E; lawful provider/redistribution rights and account-level zero-cost certification; owner-host backup/restore, monitoring and incident evidence. Synthetic tests do not close these gates or add Stage 1 ticks.

## Remaining Stage 1 evidence gates — YELLOW

Criteria **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39** remain pending owner-controlled production evidence. No gate is marked accepted from documentation or synthetic CI alone.

**Controls:** ZERO COST; no paid service, billing change, new Cloudflare resource, production deployment, PR merge or `main` modification. PR #13 stays open. No autonomous 10-minute AI execution is running; CI is checked during an active session only.

**Deadline:** 24 December 2026 — 27 calendar days remained at this checkpoint.

---

# OWNER CHECKPOINT — Batch 96C WebSocket lease lifecycle

**WebSocket implementation: 6/6 GREEN at code/test level on tested source commit `a9b7a126cefd87e87d11d52bd7d2016d7f71e363`.**
- Atomic lease acquisition and collision-safe takeover — verified.
- Lease renewal and expiry handling — verified.
- Monotonic fencing token increment on takeover — verified.
- ACK bound to current owner token, fence token and live lease — verified.
- Per-socket lifecycle, ping/ACK renewal, close/error release, alarm expiry and stale-owner fan-out rejection — verified.
- Expiry-aware compaction — verified.

**Exact test evidence on the tested source commit:**
- Automated Tests run [46018548453](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46018548453) — SUCCESS. Includes Miniflare/workerd WebSocket test, Durable Object runtime suite, frontend tests, backend tests, Redis TLS fixture, backend build/smoke test and image scan.
- CodeQL run [46018548662](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46018548662) — SUCCESS.
- OCI ARM64 run [46018548597](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46018548597) — SUCCESS.
- Full Git History Secret Audit [46018548415](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46018548415) — SUCCESS.

**Clean source commit:** `57dd158fe085207989cad19d47f15214805a7397` removes temporary diagnostic logging only; exact-head CI is being rerun before this clean commit is finally accepted. No feature behavior was intentionally changed by that cleanup.

**Stage 1 is NOT complete:** remains 30/40 = 75% provisional; Gate 10 = 0/10 formally closed. These six synthetic code-level items do not prove public production WSS or close external Stage 1 criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Stage 2 remains preparatory and requires Stage 1 40/40 plus explicit owner approval. Zero cost; no new infrastructure. Target: 24 December 2026.

---

# AUTHORITATIVE OWNER CHECKPOINT — 27 November 2026, Batch 96C implementation candidate

**Stage control:** Stage 1 remains 30/40 (75% provisional); Gate 10 remains 0/10 formally closed. Stage 2 is preparatory only and cannot begin until Stage 1 is accepted at 40/40 and the owner explicitly approves.

**Parallel implementation streams completed in this candidate:**
- Core lease primitives: atomic acquisition, same-owner renewal, active-owner collision rejection, expiry takeover with monotonically incremented fence, fenced release, and owner/fence/expiry-validated receipt commit.
- WebSocket lifecycle: unique owner token and consumer ID per socket, lease renewal on ping/ACK, alarm-driven expiry, fan-out expiry guard, close/error release, and re-subscribe release.
- Retention safety: compaction deactivates expired leases and only blocks on non-expired active consumers.
- Runtime tests: acquisition/collision/renewal/takeover, stale ACK/release rejection, expired-lease compaction, socket isolation/close release, and ping+ACK renewal.

**Verification is still pending.** One prior Automated Tests run failed at JavaScript syntax checking because an ACK callback containing `await` was not marked `async`; this was corrected in commit `bebd1c66ee262240e593409f9c7ddee78b544045`. Follow-up fixes for pending lease cleanup and replay alarm scheduling are in `247b22344b437f729d026f05bc80f8469a889e4c`. The latest exact-head CI must still reach terminal SUCCESS on all four required workflows. No WebSocket item is accepted or awarded a Stage 1 tick until that evidence and runtime edge-case review pass.

**Latest candidate source commit:** `247b22344b437f729d026f05bc80f8469a889e4c`. Runtime-test commit: `d2760d18c7194bdd19b88e71adccf2e681fe7a02`. Subsequent documentation-only commits may move PR HEAD without changing source/test content.

**Remaining external Stage 1 gates:** 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 still require real owner-host, Firebase, backup/key recovery, deployment, public WSS/device, monitoring or incident evidence. Synthetic CI cannot close them. ZERO COST; no paid services or new infrastructure. Target: 24 December 2026.

---

# AUTHORITATIVE OWNER CHECKPOINT — 27 November 2026, Batch 96C candidate

**Stage 1:** 30/40 = 75% provisional; Gate 10 = 0/10 formally closed. Stage 2 remains preparatory and requires Stage 1 100% plus explicit owner approval.

**Batch 96C source implementation:** atomic per-socket lease acquisition/takeover, same-owner renewal, fenced release, owner/fence/expiry ACK validation, lease renewal on ping/ACK, expiry-aware compaction, alarm expiry, and per-socket attachment binding have been added in `cloudflare/proof/worker.mjs`. Runtime tests have been added for acquisition/collision/renewal/takeover, stale ACK/release rejection, expired-lease compaction, socket isolation/close release, and ping+ACK renewal.

**Verification state:** implementation is a candidate, NOT green or accepted yet. Exact-head CI must reach terminal SUCCESS for Automated Tests, CodeQL, OCI ARM64 and Full Git History Secret Audit. Any failure must be fixed and rerun. Runtime eviction/race/expiry edge cases remain to be checked. Do not award Stage 1 ticks until evidence is accepted.

**Source commit:** `8afee18c54e49c97bed7549da89255944d053f58`. **Runtime-test commit:** `d2760d18c7194bdd19b88e71adccf2e681fe7a02`. The final candidate HEAD changes again as follow-up fixes land.

**Stage 1 external gates:** criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 still require owner-host/production/Firebase/backup/deployment/WSS/monitoring evidence. Synthetic WebSocket tests cannot close these external gates. Zero-cost constraint remains; no new resources or paid services. Target 24 December 2026.

---

**Official stage:** Stage 1 — Foundation, Security & Data Integrity. Stage 2 is preparatory only and cannot officially start until Stage 1 reaches 100% and the owner explicitly authorizes the transition.

**Stage 1 accounting:** 30/40 = 75% provisional. The ten remaining external acceptance criteria are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Gate 10 remains 0/10 formally closed. These are not ten missing source-code functions: each requires owner-host, real Firebase, backup/key custody, deployment, public WSS/device, monitoring or incident evidence. Repository CI cannot truthfully close them. No ticks are added by documentation or synthetic tests.

**Exact source/test HEAD:** `96cb3d505b7f70d70147f6773d879632d71e9a58`. PR #13 remains OPEN and unmerged; branch `work/batch95-websocket-ack-protocol`; `main` untouched. The exact source/test SHA has all four required workflows terminal SUCCESS:
- Automated Tests [46011891943](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011891943) — **41/41 steps SUCCESS**.
- CodeQL [46011891956](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011891956) — **SUCCESS**.
- OCI ARM64 [46011892089](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011892089) — **SUCCESS**.
- Full Git History Secret Audit [46011892151](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/46011892151) — **SUCCESS**.

Automated Tests passed Worker/DO runtime tests, frontend tests and build, Android read-only preflight, Redis TLS CA/hostname fixture, backend tests, SQLite outbox/metrics benchmarks, dependency audit, backend image build, persistent-volume/Redis-guard smoke test, image scan/report and audit enforcement. This is repository/synthetic evidence, not a production deployment or owner-host acceptance.

**Batch 96B change:** schema v5 migration now deactivates legacy consumer rows without valid owner/fence/lease metadata. Regression test added for v4-to-v5 migration. The change is included in the exact SHA above and therefore has full four-workflow CI success.

**Remaining WebSocket lifecycle work:** implement atomic lease acquisition/renewal/release; monotonic fencing on expired takeover; owner+fence+expiry validation on ACK; expiry-aware compaction; socket lifecycle integration; stale owner/duplicate owner/takeover/restart/eviction/concurrency tests. These are still open. Do not claim WebSocket lifecycle complete.

**Project status:** Stage 1 75% provisional; Stage 2 preparatory; Stage 3/5/6 unscored; Stage 4 gated; overall project percentage not scored. ZERO COST. No paid trials, new resources, deployments or billing changes. Delivery target 24 December 2026: 27 calendar days remain from 27 November. No autonomous background AI coding is claimed; the 10-minute relay runs preflight only.

---

# HISTORICAL SNAPSHOT — Batch 95 (superseded by checkpoint above)

# Current Stage 1 acceptance snapshot — Batch 95 (27 November 2026)

**Official active stage:** Stage 1 — Foundation, Security & Data Integrity.  
**Stage 1 meter:** 30/40 criteria = 75% provisional. **Gate 10:** 0/10 external criteria formally closed.  
**Stages 2–6:** Stage 2 remains preparatory; Stages 3, 5 and 6 are not scored; Stage 4 remains gated. Overall project percentage is not scored.

**Latest repository candidate:** PR [#13](https://github.com/deszztagd377-pixel/dezzta-chart/pull/13), branch `work/batch95-websocket-ack-protocol`, current PR HEAD `2bfe7b2e8732ee92ddf1f25e4c8ffe944e007ebe` (documentation-only). The latest source/test SHA is `7dcf148b772d37c4321122a1c45d49bae0e43868`; all four required workflows (Automated Tests, CodeQL, Full Git History Secret Audit and OCI ARM64) reached terminal SUCCESS on that exact source/test SHA. Batch 96A adds the v5 consumer lease schema and its runtime migration assertions; exact-head CI is in progress. PR #13 remains open and unmerged. This does not establish production WebSocket acceptance.

**Remaining Stage 1 external criteria — all YELLOW / evidence pending:**
- **8:** actual production secret injection, host permissions, runtime exposure and rotation.
- **20:** real Firebase sign-in/revocation/entitlement and browser/Android integration under verified no-billing terms.
- **25:** owner-host Redis TLS, ACL, persistence and failover.
- **30:** owner-environment database backup/restore drill with application-record verification.
- **31:** encrypted off-host backup and independent key-recovery evidence.
- **34:** real persistent-volume mount, permissions, restart durability and recovery.
- **35:** backend HTTPS deployment on an existing zero-incremental-cost host.
- **36:** public WSS/reverse-proxy and browser/Android E2E.
- **38:** external metrics/logging/dashboard, retention and access-control evidence.
- **39:** delivered alert, acknowledgement, escalation and incident-recovery drill.

Repository tests, synthetic proof, documentation and CI do not close these external gates. No Stage 1 ticks are awarded without the specified owner-host/device/production evidence. The current single-device/no-PC/no-second-phone and zero-cost constraints remain binding; no paid trial, billing upgrade, new hardware or production resource is assumed.

**Next code sequence on the existing PR branch:** Batch 96 — implement and test the synthetic required-consumer lease/fencing lifecycle before any production identity binding. Batch 96A adds additive v5 columns `owner_token`, `fence_token`, and `lease_expires_at_ms`, with migration assertions. Lease acquisition/renewal, expiry enforcement, stale-owner rejection, ACK/close fencing and safe deregistration remain unimplemented. Acceptance must cover additive migration, same-owner renewal, active-owner collision, expiry/reacquisition with incremented fence, stale ACK/close rejection, multiple sockets, compaction and eviction/restart. No Batch 96 source implementation is claimed at this checkpoint. The PR is not to be merged automatically.

**Historical record note:** sections below retain dated checkpoints. Where an older snapshot says Batch 92–93 ACK/replay work is absent, that statement is historical and superseded by the Batch 95 candidate evidence above.

---

# Stage 1 / project architecture reconciliation — Work Cycle 89 (25 November 2026)

**Selected architecture:** Cloudflare Native / Zero-Origin. Historical owner-host/Redis Batch 80–86 execution and the earlier Python Workers spike are superseded as active work.  
**Stage 1 meter:** 30/40 = 75% provisional 🟨; not whole-project completion.  
**Gate 10:** 0/10 formally closed 🟨. Remaining criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.  
**Stage 2:** 🟦 PREPARATORY. **Stage 3:** ⚪ NOT SCORED. **Stage 4:** 🟪 GATED. **Stage 5/6:** ⚪ NOT SCORED.  
**Overall project / IP3S:** ⚪ NOT SCORED; no approved reproducible weighted denominator.  
**Production WebSocket:** 🟨 OPEN; Worker remains synthetic-only proof and is not deployed evidence.  
**Project Gate 25:** 🟨 OPEN; durable signed snapshot/receipt/high-water acceptance not proven.  
**Gate 36:** 🟨 OPEN; public WSS/TLS/browser/Android E2E not proven.  
**Live market data:** 🟨 OPEN; lawful, compatible and genuinely zero-cost provider access not established.  
**CI:** documentation-only commits use `[skip ci]`; this is not a source/runtime test pass. Empty status/run results mean UNKNOWN / NOT VERIFIED.  
**Cost:** ZERO COST; no deployment, paid service, resource creation or `main` changes.

## Active execution order — authoritative

1. **Batch 89 — runtime gate:** `npm ci`, app tests, production build, Miniflare runtime tests, Durable Object runtime tests, and final working-tree hygiene. Capture versions/logs/exit codes/exact SHA; all four validation commands must pass.
2. **Batch 90 — SQLite schema/migration:** additive migration, v1 compatibility, local DO runtime proof.
3. **Batch 91 — provider-neutral API/envelope contract:** parallel contract preparation allowed; runtime acceptance follows schema gate.
4. **Batch 92 — durable event log:** atomic payload/digest/high-water, fan-out-after-commit, bounded contiguous replay.
5. **Batch 93 — ACK/receipt/RESUME:** authenticated consumer identity, digest/generation validation, durable monotonic receipts, retention-floor resnapshot and eviction recovery.
6. **Batch 94 — lawful zero-cost provider ingress:** no provider activation without evidence.
7. **Batch 95 — public WSS/TLS/browser/Android E2E, quota and restore acceptance:** after predecessor gates only.

Parallel preparation is limited to independent contract review and failure-injection test design. Serialize schema migrations and shared Worker/DO runtime changes. Never claim a batch complete from a design document alone.

## Current acceptance disposition

- Batch 89: 🟨 OPEN; runtime commands not executed in the current connector environment.
- Batches 90–91: 🟦 design/preparation; implementation acceptance open.
- Batches 92–93: 🟨 durable event log/replay and ACK/receipt/RESUME missing from inspected source.
- Batch 94: 🟨 lawful zero-cost provider gate not passed.
- Batch 95 / Gate 36: 🟨 public WSS/TLS/browser/Android E2E absent.
- Project Gate 25: 🟨 durable signed snapshot receipt/high-water acceptance open.
- Redis destructive retention: 🟨 BLOCKED; do not enable without durable receipt and retention-floor proof.

The repository connector does not provide a checkout/terminal. No current install/build/test/audit execution is claimed. Runtime code must not be committed without a supported execution path and captured acceptance evidence.

**Detailed source/test traceability:** `docs/WEBSOCKET_ACCEPTANCE_TRACEABILITY_2026-11-25.md`.  
**Source-level Batch 89–93 blockers:** `docs/BATCH89_93_SOURCE_AUDIT_2026-11-25.md`.


---

# Latest Stage 1 acceptance reconciliation — Work Cycle 87 (25 November 2026)

**Audited source/test HEAD:** `471eb4413a716922b20a5503fe5165607e77947f`.  
**Stage 1:** 30/40 = 75% provisional 🟨; this is not whole-project progress.  
**Gate 10:** 0/10 formally closed 🟨. Remaining criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.  
**Stage 2:** 🟦 PREPARATORY only. **Stage 4:** 🟪 GATED. Stages 3, 5 and 6 ⚪ NOT SCORED.  
**Project overall and IP3S:** ⚪ NOT SCORED; no approved denominator/formula.  
**WebSocket:** synthetic-only Worker proof exists in repository, but production deployment/public WSS is not evidenced. Project Gate 25 signed receipt/high-water ACK and Gate 36 public WSS/TLS/device E2E remain 🟨 OPEN. Redis destructive retention remains 🟨 BLOCKED.  
**CI:** latest source SHA status query returned no checks; available workflow-run query returned no PR-triggered runs. Current CI state is UNKNOWN / NOT VERIFIED, not SUCCESS.  
**ZERO COST:** maintained; no paid service, resource creation or deployment. `main` untouched.

Gate 10 criteria are still Stage 1 acceptance items. Stage 1 criterion #25 (owner-host Redis TLS/ACL/persistence) is distinct from Project Gate 25 (signed snapshot transfer/receipt/high-water ACK). Synthetic tests, documentation and CI cannot substitute for owner-host/device evidence.

Full Work Cycle 87 audit: `docs/WORK_CYCLE_2026-11-25_BATCH87_INDICATOR_AND_WEBSOCKET_RECONCILIATION.md`.

---

# Current Stage 1 / Gate 10 status — Batch 72 (25 November 2026)

**Audited source HEAD:** `6a6e9e82ed2de725bef94e8ed1fa7f28c60e0a49`; Batch 71 CI 4/4 terminal SUCCESS.  
**Official active stage:** Stage 1 — Foundation, Security & Data Integrity.  
**Stage 1:** 30/40 = 75% provisional 🟨. **Gate 10:** 0/10 formally closed 🟨.  
**Cloudflare acceptance evidence:** repository Worker/DO proof is synthetic-only and not deployed. The connected Cloudflare account inventory contains no Worker, Pages project, Tunnel, Durable Object namespace, Zone, or Worker domain. Therefore it does not close Stage 1 criteria 8/25/35/36/38/39 or Project Gate 25.  
**Zero-cost restriction:** Workers Free + SQLite DO may be used within free quotas; Cloudflare Containers require Workers Paid and are excluded. A Tunnel requires an existing owner-operated origin. No resources were created or deployed.  
**Gate 10 remains:** 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. No docs, synthetic tests, or CI pass substitutes for actual host/device/production evidence.  
**Important:** Stage 1 criterion #25 (owner-host Redis TLS/ACL/persistence) remains distinct from Project Gate 25 (signed snapshot/receipt/high-water ACK).  
**Stage 2:** preparatory only; no official transition. **Stage 4:** indicator UI gated.

---

# Current Stage 1 / Gate 10 status — Batch 71 (25 November 2026)

**Current branch HEAD at audit:** `19de41d3dc613a11a0441e65a075f7a1ed5cc685`; Batch 70 exact-HEAD CI 4/4 SUCCESS.  
**Official active stage:** Stage 1 — Foundation, Security & Data Integrity.  
**Stage 1 evidence meter:** 30/40 = 75% provisional 🟨.  
**Gate 10:** 0/10 formally closed 🟨.

Gate 10 comprises only these ten remaining Stage 1 criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39**. They do not migrate wholesale into Stage 2. Early Stage 2 market-data foundation work on `phase-2/market-data-foundation` is preparatory technical work, not official stage advancement.

- 🟨 Host/owner proof pending: 8, 30, 34, 35, 39.
- 🟨 Operational/owner proof partially prepared: 38.
- 🟨 External production/device acceptance open: 20, 25, 31, 36.
- **Important:** Stage 1 criterion #25 is Redis TLS/ACL/persistence on owner hardware. Project Gate 25 is Ed25519 signed snapshot transfer/receipt/high-water ACK. They are separate blockers.
- No criterion is formally closed by docs, synthetic tests or CI alone.
- ZERO COST; `main` untouched; no paid hosting/data/monitoring/backup; Vercel deferred; Redis destructive retention blocked.

---

# Verified Stage 1 blocker reconciliation — Batch 62J-236 (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Audited documentation HEAD:** `e03ada0cd1a21ebc76b2c9b5fce41c73db1e923c`  
**Exact-HEAD CI:** 4/4 terminal SUCCESS on this exact SHA:
- Automated Tests run `45525451961`: 41/41 steps, no failed steps.
- CodeQL run `45525451749`: Python 8/8 and JavaScript/TypeScript 8/8.
- OCI ARM64 run `45525451873`: 7/7 steps.
- Full Git History Secret Audit run `45525451791`: 6/6 steps.
All four runs completed against the exact same SHA. Earlier runs on superseded documentation commits were cancelled by newer commits; the final SHA has its own successful, terminal run set. No workflow remains running for this SHA.

## Why Stage 1 is not 100%

The Stage 1 matrix has 40 acceptance criteria. 30 have repository implementation/test evidence or approved design evidence; 10 still lack required real owner-host, owner-device, or production acceptance evidence. The provisional meter is therefore **30/40 = 75%**. The remaining 10 are not one generic code bug; most cannot be proven from GitHub CI alone.

| Criterion | Remaining proof required | Current blocker |
|---|---|---|
| 8 | Actual owner-host secret injection, owner/mode, UID 10001 readability, runtime exposure/rotation/log checks | 🟨 Host evidence absent |
| 20 | Real no-billing Firebase sign-in, expiry/revocation, entitlement denial, ticket exchange and web/Android reconnect | 🟨 Real project/device E2E absent; billing must remain disabled |
| 25 (Stage 1 checklist) | Self-hosted Redis TLS certificate validation, ACL, private binding/firewall, persistence, restart/failure/recovery on existing owner hardware | 🟨 Owner-host Redis acceptance absent; managed paid Redis prohibited |
| 30 | Restore the actual application DB into a fresh target-host destination and verify application records | 🟨 Owner-target restore drill absent |
| 31 | Encrypted off-host backup, separate key custody, retention/access policy and successful key-recovery restore | 🟨 No zero-cost off-host destination/key-custody evidence |
| 34 | Actual persistent volume mount/owner/permissions, restart durability, disk-pressure and recovery | 🟨 Owner-host volume proof absent |
| 35 | Backend on existing owner hardware, health/startup/secret injection; public route only if no incremental cost | 🟨 Host route/runtime proof absent; public route may be zero-cost constrained |
| 36 | Authenticated HTTPS/WSS through owner-controlled reverse proxy from real web and Android clients; reconnect/resnapshot/cross-instance | 🟨 Production WSS/device proof absent |
| 38 | Durable owner-host metrics, retention, backup/restore, disk pressure, firewall, token rotation, dashboard, independent alert/ACK/recovery | 🟨 Host observability/operations proof absent |
| 39 | Demonstrated zero-cost local alert route plus incident owner, escalation, acknowledgement and recovery drill | 🟨 Operator drill absent |

**Important naming distinction:** Stage 1 checklist criterion **#25** is the Redis TLS/ACL/persistence acceptance item above. The separately tracked project **Gate 25** is the Ed25519 signed-snapshot installation/receipt/high-water-ACK acceptance path. They are different work items and both remain open. Project Gate 25 still needs owner-host private-key custody, authenticated transfer to each gateway, persisted receipt retrieval after restart, re-verification, and durable per-gateway high-water ACK.

**Gate 10 accounting:** 0/10 formally closed. Repository CI success does not close any of these ten external acceptance criteria. No points are awarded for documentation-only work or synthetic CI substitutes.

## Work order without stage skipping

1. Project Gate 25: owner-host custody → authenticated snapshot transfer → persisted receipt per gateway → restart/reverify → durable per-gateway high-water ACK.
2. Stage 1 criterion #25: existing-hardware Redis TLS/ACL/private binding/persistence/restart/failure recovery.
3. Criterion 8: actual secret injection and runtime exposure/rotation proof.
4. Criteria 30/31/34: real restore, off-host key recovery and persistent-volume evidence, strictly zero incremental cost.
5. Criterion 35: owner-host backend runtime and health checks; public exposure only if existing path is free.
6. Criterion 36: public WSS/TLS/proxy and real browser/Android E2E, only when no-billing infrastructure is proven.
7. Criteria 38/39: durable operations metrics and local alert/incident drill.
8. Criterion 20: Firebase E2E only on a verified no-billing configuration.
9. Only after Stage 1 acceptance, progress the official stage transition. Early Stage 2 source foundations do not authorize skipping Stage 1.

**Safety / cost:** ZERO COST. No managed paid Redis, paid hosting, domain purchase, paid market data, paid monitoring, paid backup, or billing-plan upgrade. No Vercel deployment. `main` untouched. No destructive Redis retention. APK planning target remains approximately 24 December 2026.

---

# Latest exact-head reconciliation — Batch 62J-96 (21 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `2eb3181b21b7f2aa3a53c8c293ab6d27ec959b75`

- Automated Tests [44913778296](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778296): **SUCCESS**; frontend **255/255 tests across 29 files**; backend **1,271 passed in 46.68 seconds**.
- CodeQL [44913778266](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778266): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44913778270](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44913778270): **SUCCESS**.
- Backend dependency audit reported no known vulnerabilities. Container smoke verified Redis ACL/AOF persistence across restart, backend outage fail-closed/reconnect, non-root runtime, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit rejection.
- The 62J-94 diagnostic instrumentation remains in source: benchmark reports end-to-end flush, writer-lock wait and transaction-body/commit distributions for 1/4/16 threads and four OS processes.
- The 62J-95 retry-jitter experiment was rejected after measured regressions and reverted in this HEAD. Do not claim jitter improved tail latency. The restored 62J-94 implementation and tests passed the exact-head workflows above.
- Restored-source benchmark on the CI runner: 16-thread p95/p99 295.505/644.926 ms, writer-lock p99 613.413 ms, transaction p99 18.152 ms, 68 retries; four-process p95/p99 59.106/135.398 ms, writer-lock p99 128.640 ms, transaction p99 9.771 ms, 0 retries. These are synthetic stress results, not production-host measurements or an SLA. Phase percentiles are independently calculated and cannot be treated as the exact share of an individual flush.
- WebSocket protocol/auth/replay/snapshot/cursor/Redis paths were not changed by Batches 62J-94–96. Production WSS remains host/client gated.
- **Gate 10: 0/10 formally closed.** Gates **8, 30, 34, 35, 39** remain 🟨🟩 repository-ready / host-owner verification only. Gates **20, 25, 31, 36, 38** remain 🟨 externally open. Yellow-green is not closure; bright green requires complete acceptance evidence.
- **Stage 1: 30/40 = 300/400 = 75% provisional.** Stages 2–6 remain unscored. Overall project percentage remains unscored without approved weights/denominators.
- Indicators unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟨, Heatmap 🟨, Liquidation Maps 🟨.
- ZERO COST. No deployment, paid service, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.

---

# Latest exact-head reconciliation — Batch 62J-93 (21 November 2026)

**Branch:** `phase-2/market-data-foundation`  
**Source/test HEAD:** `a62e7423a5d36d3fdbc003e0e56d86c3a9e6ecbb`

- Automated Tests [44911391436](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391436): **SUCCESS**, 35/35 workflow steps.
- Frontend: **255/255 tests across 29 files**; backend: **1,271 passed in 55.86 seconds**.
- CodeQL [44911391400](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391400): **SUCCESS**; Full Git History Secret Audit [44911391397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44911391397): **SUCCESS**.
- Frontend npm audit: 0 vulnerabilities; backend dependency audit: no known vulnerabilities; Trivy scanned Alpine and Python package targets with 0 reported vulnerabilities.
- Gate 38 batch-read optimization passed exact-head CI. Full 899-series benchmark passed for 1/4/16 threads and four separate OS processes; read-only failure/recovery, SQLite `SQLITE_FULL` rollback/recovery and application-level HTTP/WebSocket failure isolation passed.
- WebSocket repository-side automated failure matrix remains complete. Production HTTPS/WSS, Redis owner-host topology, snapshot distribution and browser/Android owner acceptance remain external.
- **Gate 10: 0/10 formally closed.** Gates **8, 30, 34, 35, 39** are 🟨🟩 repository-ready / host-owner verification only. Gates **20, 25, 31, 36, 38** remain 🟨 externally open. Yellow-green is not closure; bright green requires full acceptance evidence.
- **Stage 1: 30/40 = 300/400 = 75% provisional**, unchanged; no gate tick awarded by this source optimization. Stages 2–6 remain unscored. Overall project percentage remains unscored without approved weights/denominators.
- Indicators unchanged: SMA20 🟨, EMA20 🟨, RSI14 🟨, MACD12/26/9 🟨, Bollinger20,2 🟨, Shared Hook 🟨, Footprint 🟨, Heatmap 🟨, Liquidation Maps 🟨.
- ZERO COST. No deployment, paid service, Vercel/Cloudflare operation, Termux/device action, production credentials or `main` modification.

---

## Batch 15 — upstream dependency remediation review — 2026-11-18

Fresh upstream review confirms there is no safe patch/release to integrate yet:

- GHSA-fc5q-39xc-vjpf remains published; current GitHub advisory page is marked Unreviewed and lists no patched version. OSV continues to carry the record.
- Issue [picomatch #247](https://github.com/micromatch/picomatch/issues/247) remains open. Snyk-specific revocation does not revoke the GitHub advisory.
- PR [#238](https://github.com/micromatch/picomatch/pull/238) remains open; reviews reproduce remaining exponential behavior for `+(*)`, `*(*)`, and `+(a*)`.
- PR [#237](https://github.com/micromatch/picomatch/pull/237) remains open; review comments report unhandled multi-branch and quoted/bracket semantic edge cases.
- PR [#246](https://github.com/micromatch/picomatch/pull/246) targets the v2 branch and is not applicable as a drop-in fix for this project's picomatch 4.x path.
- PR [#235](https://github.com/micromatch/picomatch/pull/235) is closed and contains maintainer disagreement about the vulnerability's threat model. This is not an official withdrawal of the GitHub advisory.

No upstream PR is merged/released as a validated fix. No patch or override was applied. The npm audit enforcement remains active. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed.


## Batch 14 — exact-head verification refresh — 2026-11-18

Verification target source commit: `4256c5e3ccab82255d115beaf961afd4794a3a42`.

- Automated Tests [44278716234](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716234): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed in 30.07s**. Frontend tests/build and credential scans, Android preflight/publisher tests, synthetic outbox benchmark, backend audit, container build, Redis/persistent-volume smoke test and Trivy report steps passed.
- CodeQL [44278716261](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716261): **SUCCESS**.
- Full Git History Secret Audit [44278716240](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44278716240): **SUCCESS**.
- Exact-source WSS preview `dpl_AtEV8yH6S5MwGApGaHQ8HagJTJsK` and frontend preview `dpl_2Jc2So3HmvEQ6yeESjrXbMLorivz`: **READY**.
- The audit log confirms five High paths through dev-only `picomatch@4.0.7` (GHSA-fc5q-39xc-vjpf). Exposure regression passes but does not remediate the advisory; enforcement remains active.
- Gate 36 remains OPEN: no owner-observed foreground 330-second platform-duration result, effective Fluid Compute read-back, native Android WebView WSS or cross-instance fan-out.
- Accounting unchanged: Stage 1 **300/400 = 75% provisional**, 30/40 criteria; Gate 10 **0/10 closed**; open **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 are not scored.

---

> **OWNER CONSTRAINT — ZERO MONEY (2026-11-10):** All Stage 1 acceptance work must comply with [ZERO_COST_POLICY.md](ZERO_COST_POLICY.md). Do not provision Fly.io, paid Redis, paid market-data APIs, paid backup/monitoring, paid email/SMS, paid runners, or any trial/plan that can create a charge. Earlier Fly.io deployment research is superseded and must not be executed. If a criterion cannot be satisfied at zero incremental cost, record it as constrained/deferred rather than purchasing a service.

# Stage 1 — Production Acceptance Matrix

Branch: `phase-2/market-data-foundation`


## Latest verified repository checkpoint — Batch 13 — 2026-11-18

- Exact source commit: `c3bcb0c6011f1f7228be17d16d227f325d7cbb29`.
- Automated Tests [44271321142](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44271321142): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,013 passed in 29.73s**. Frontend tests/build, frontend credential scans, Android preflight/publisher tests, backend audit, Docker build, persistent-volume/Redis ACL smoke test, and Trivy scan all passed.
- Trivy backend image report: **0 HIGH / 0 CRITICAL**.
- CodeQL [44271321171](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44271321171): **SUCCESS**.
- Full Git History Secret Audit [44271321225](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44271321225): **SUCCESS**.
- Exact commit Vercel previews: WSS `dpl_HYCzptpjB6ZkWGjmDhqAz1QkDozc` **READY**; frontend `dpl_2f6nmwUWNWC1iLBaMBn4AMeZwBwv` **READY**.
- Five High npm audit findings remain through dev-only `picomatch@4.0.7`. Upstream PR #238 is open/unmerged and has no successful check-runs recorded at this read-back. Do not suppress, waive, or mislabel it as fixed.
- A new regression test verifies the vulnerable transitive glob tooling remains development-only and absent from runtime dependencies. This is exposure reduction only; it does not close the npm audit.
- Stage 1 remains **300/400 = 75% provisional**, 30/40 provisional criteria; Gate 10 remains **0/10 closed**. Open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.

This matrix separates repository implementation from evidence that must come from a real deployment. A source-code check or a test file is **not** proof that the corresponding production control has passed. Do not mark an item complete without attaching reproducible evidence (CI run, deployment output, restore report, or monitoring test result).

## Status legend

- **Implemented / test present** — relevant code and/or regression coverage exists in this branch; execution on the current branch still needs recorded CI evidence.
- **External verification required** — requires a real provider, deployment, managed service, client, or operational exercise.
- **Approval / design required** — must not be implemented or enabled until the owner approves the scope and threat model.

## Latest verified repository checkpoint — 2026-11-17

- Exact source/test commit: `d32645019db6c93532666f691c43cfe87b9fa8d8`.
- Automated Tests & Build [44107801447](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801447): **SUCCESS**, 32/32 steps; backend pytest **1,008 passed in 26.26s**.
- CodeQL [44107801732](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801732): **SUCCESS**.
- Full Git History Secret Audit [44107801473](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44107801473): **SUCCESS**.
- Both Vercel preview status contexts completed successfully. Preview status is not production acceptance.
- Current accounting: **30/40 provisional = 300/400 = 75%**; **0/10 external gates closed**. Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Gate 38 metrics-input hardening is test-verified at repository level; Gate 39 local operator logging and zero-cost runbook are present. Neither external gate is closed.

## Forty-point acceptance checklist

### A. Configuration and secret handling

1. **Implemented / test present** — production startup requires a Redis URL.
2. **Implemented / test present** — production startup requires a Firebase project ID.
3. **Implemented / test present** — production Redis configuration requires the `rediss://` scheme.
4. **Implemented / test present** — production CORS origins must be exact HTTPS origins; wildcard origins are rejected.
5. **Implemented / test present** — shared HTTP/WebSocket limits reject booleans, non-integers, zero, and negative values.
6. **Implemented / test present** — Redis and provider credentials are excluded from settings representations.
7. **Implemented / test present** — safe provider defaults keep live and historical ingestion disabled.
8. **🟨🟩 Host verification only** — confirm production secrets use an owner-controlled, no-billing host secret-injection mechanism (for example OS-protected service credentials) and are absent from frontend bundles, logs, build output, and repository history. Do not introduce a paid secret manager.

### B. Identity and WebSocket authorization

9. **Implemented / test present** — Firebase Admin verifies signed ID tokens.
10. **Implemented / test present** — token verification requests revocation checking.
11. **Implemented / test present** — issuer, audience, subject, and authentication-time claims are validated.
12. **Implemented / test present** — conflicting Firebase `uid` and JWT `sub` claims are rejected.
13. **Implemented / test present** — malformed tokens, claims, SDK failures, and provider initialization errors fail closed with normalized messages.
14. **Implemented / test present** — browser WebSocket origins are checked against the exact allowlist before acceptance.
15. **Implemented / test present** — WebSocket authentication is required before authenticated subscriptions proceed.
16. **Implemented / test present** — instrument entitlement is checked against the verified principal, not a client-supplied account identity.
17. **Implemented / test present** — identity and authorization are periodically revalidated during a connection.
18. **Implemented / test present** — shared WebSocket admission enforces global and per-account connection limits.
19. **Implemented / test present** — expiring shared leases and release paths are implemented for WebSocket connections.
20. **External verification required / constrained by ZERO MONEY** — exercise real Firebase sign-in, token expiry/revocation, entitlement denial, reconnect, and browser plus Android WebSocket flows only if a no-billing configuration is verified. Otherwise keep production Firebase integration disabled and defer this gate; never enable Blaze.

### C. Shared guards and service resilience

21. **Implemented / test present** — Redis health is required during shared-guard startup.
22. **Implemented / test present** — HTTP rate limiting fails closed when Redis operations fail.
23. **Implemented / test present** — WebSocket admission and lease operations fail closed on Redis errors.
24. **Implemented / test present** — shared counters and leases use atomic Redis Lua scripts.
25. **External verification required / managed paid Redis prohibited** — validate TLS certificate checking, ACLs, private-network binding, persistence, restart and failure behavior for a self-hosted Redis instance on existing owner-controlled hardware. Do not purchase managed Redis.

### D. SQLite durability and backup

26. **Implemented / test present** — SQLite snapshots use the Online Backup API for transactionally consistent copies.
27. **Implemented / test present** — backup output is checked with `PRAGMA integrity_check`.
28. **Implemented / test present** — backup publication uses a temporary file and atomic replacement; POSIX snapshot data is flushed before publication and the parent directory is flushed after rename; pre-publication failures preserve the previous destination. Directory-flush failure is surfaced because rename durability is uncertain.
29. **Implemented / test present** — POSIX backup files are restricted to owner-only permissions, and failure to set permissions prevents publication.
30. **🟨🟩 Owner-device/host verification only** — perform and record a restore drill from the actual application database into a fresh destination into a fresh database, verifying application-level records as well as SQLite integrity. Batch 6 adds a CI integration test chaining encrypted snapshot recovery into the full application restore drill; this is repository evidence only and does not replace the target-host drill.
    - Batch 27 strengthens the repository probe: it now commits a unique test record, verifies it through a fresh read-only connection, then commits cleanup and verifies absence through another read-only connection. Two regression tests cover durable readback and cleanup after injected failure. This remains CI/repository evidence only; Gate 30 stays OPEN pending the actual owner-device database drill.
31. **External verification required** — encrypt backups before off-host transfer, store encryption keys separately, enforce retention/access policy, and prove a restore using the documented key-recovery procedure. Batch 6 adds an end-to-end CI regression for snapshot → AES-256-GCM artifact → authenticated decrypt → application restore; off-host storage, separate key custody, retention, and owner-target recovery remain unverified.

### E. Container and deployment

32. **Implemented / test present** — the backend container runs the application as UID/GID `10001:10001`.
33. **Implemented / test present** — the CI workflow contains a Docker smoke test for volume ownership, SQLite integrity, restart persistence, and rate-limit behavior.
34. **🟨🟩 Host verification only** — configure a persistent data volume on existing owner-controlled hardware and verify mount path, owner, permissions, restart durability, disk-pressure behavior, and recovery. Do not provision a paid provider volume.
35. **🟨🟩 Host verification only / zero-cost constrained** — run the backend on existing owner-controlled hardware and verify HTTPS health checks, startup failure behavior, and backend-only secret injection. Expose it publicly only if the existing network/domain path is verified to create no incremental charge; otherwise keep it local/LAN and defer public deployment.
36. **External verification required** — verify the WSS handshake and authenticated subscription flow from supported web and Android clients through a reverse proxy on the owner-controlled host. Do not purchase hosting, domain, or CDN to satisfy this gate.

### F. Operations and production acceptance

37. **Implemented / test present** — the market-data status endpoint exposes bounded application-level operational state; it is not external monitoring.
38. **🟨 External verification required / paid observability prohibited** — repository-side instrumentation now includes bounded HTTP/WebSocket process-local metrics and a same-host SQLite multi-worker collector (899 logical series, 15-minute buckets, 7-day retention, 650,000-row cap, up to 16 live workers). Exact-head CI verifies full-cardinality thread/process benchmarks, SQLite read-only and `SQLITE_FULL` recovery, and HTTP/WebSocket failure isolation. Batch 62J-93 reduces per-flush bucket reads to one SELECT (99.8888% fewer SELECT statements at 899 series) and records both improved and regressed latency percentiles. This remains CI evidence only. Actual owner-host persistent volume, permissions, restart, retention, disk pressure, backup/restore, firewall, operator token rotation, dashboard, independent notification and acknowledgement/recovery remain required.
39. **🟨🟩 Host/operator verification only / paid delivery prohibited** — demonstrate a no-incremental-cost local alert path and document incident ownership, escalation, and recovery steps. Do not assume email/SMS/push delivery is free.
40. **Owner-approved design — complete (2026-11-10)** — the owner explicitly approved the detailed replay cursor model, outbox retention policy, reconnect semantics, benchmark plan, and short-lived scoped WebSocket-ticket threat model in [WEBSOCKET_RELIABILITY_DESIGN.md](WEBSOCKET_RELIABILITY_DESIGN.md). This closes the owner-approval criterion. Durable outbox/replay implementation still requires incremental code review and regression evidence; ticket exchange additionally remains gated on an independent security review before ticket code is added.

## Evidence required before Stage 1 can be marked 100%

- A successful GitHub Actions run for the exact release candidate commit, including frontend tests/build/security scan, backend pytest, dependency audit, Docker build, persistent-volume restart smoke test, and Trivy scan.
- A successful production-like Firebase + Redis + HTTPS/WSS integration run.
- A documented persistent-volume restart check and encrypted off-site backup restore drill.
- Evidence of monitoring and alert delivery, plus an approved incident/recovery procedure.
- Owner approval of the scoped replay/benchmark/ticket blueprint (completed 2026-11-10); independent security review remains mandatory before implementing ticket exchange.

**Current disposition:** Stage 1 is not production-accepted. The branch contains substantial implementation and regression coverage, but external acceptance evidence listed above is still outstanding. A green frontend deployment check alone does not satisfy these gates.

## Recorded CI evidence

The following CI evidence is recorded for the current checkpoint:

- Commit: `fcfa7c9c59520d55cba4554a6d4a9f45ba3ed26d`
- Workflow run: [DEZZTA CHART — Automated Tests](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42801624127)
- Run conclusion: **success** (2026-11-10)
- Verified workflow steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume container smoke test, Trivy container scan, vulnerability-report export and upload.
- This is CI evidence for the listed repository checks only. It does **not** prove real Firebase project integration, managed Redis provider configuration, production volume provisioning, encrypted off-site backup/restore, deployed HTTPS/WSS, external monitoring/alert delivery, or owner approval of the remaining design scope.

The CI workflow succeeding does not change the external acceptance status above. Stage 1 remains **not production-accepted** until every required external gate and the owner-reviewed design decision have reproducible evidence.

## Latest verified checkpoint — 2026-11-10

- Release-candidate branch: `phase-2/market-data-foundation`
- Commit: `969e5c9868c79006a1efc632a307cf8873ef03ad`
- Automated Tests & Build: [run 42804110006](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42804110006) — **success**.
- Verified workflow steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume container smoke test, Trivy container scan, vulnerability-report export and upload.
- CodeQL Security Analysis: [run 42804110246](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42804110246) — **success** for both JavaScript/TypeScript and Python analysis jobs.
- The latest code change is documentation-only: it aligns the deployment guide's production startup example and hosting configuration with the already-required `FIREBASE_PROJECT_ID` setting. No runtime code was changed by this commit.
- These green workflows provide repository CI and static-analysis evidence for this exact commit. They do not satisfy the external deployment, managed Redis/Firebase integration, backup encryption/restore, production WSS, monitoring/alerting, or owner-approval gates listed above. Stage 1 therefore remains **not production-accepted**.


## Latest verified checkpoint — 2026-11-10 (commit 93d144c)

- Release-candidate branch: `phase-2/market-data-foundation`
- Exact tested commit: `93d144cc837be96ccb27a7bbb89d97be1b6035a3`
- Automated Tests & Build: [run 42805150877](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42805150877) — **success**.
- Verified steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume smoke test, Trivy image scan, vulnerability report export/upload.
- CodeQL Security Analysis: [run 42805150519](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42805150519) — **success** for JavaScript/TypeScript and Python.
- The owner approved the four design objectives on 2026-11-10. A scoped technical blueprint has been added in `docs/WEBSOCKET_RELIABILITY_DESIGN.md`; implementation remains gated on review of the detailed cursor/retention choices and ticket threat model.
- CI and CodeQL are repository evidence only. They do not prove production Firebase/managed Redis integration, provider entitlement/real-time market-data quality, production volume provisioning, encrypted off-site backup/restore, deployed HTTPS/WSS, monitoring/alert delivery, or market-data provider cost/availability.
- The design blueprint explicitly keeps live and historical provider ingestion disabled by default. No provider credentials, paid services, runtime behavior, or authentication flow were changed in this checkpoint.
- Stage 1 remains **not production-accepted** until all external gates and the scoped design review have reproducible evidence.


## Latest verified checkpoint — 2026-11-10 (commit bb60452)

- Branch: `phase-2/market-data-foundation`
- Commit: `bb604521d37262bdeb6745111c012a088429863a`
- Automated Tests & Build: [run 42807415946](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42807415946) — **success**.
- Verified: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret-scanner test and production-bundle credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume smoke test, Trivy image scan, vulnerability-report export/upload.
- Code change: corrected the WebSocket subscription identity type annotation to use the same 10-field canonical series identity returned by `identity_for`; runtime behavior was not changed.
- Owner approval: the detailed WebSocket reliability blueprint was explicitly approved on 2026-11-10. The separate security review remains required before ticket-exchange code.
- The green CI run is repository evidence only. It does not satisfy the external Firebase/managed Redis integration, real deployment volume, encrypted off-host backup/restore, deployed HTTPS/WSS, monitoring/alert delivery, or market-data licensing/provider gates.

**Current checklist accounting:** 30/40 criteria have repository implementation/test evidence or completed owner approval; 10/40 remain external production verification gates. This is a checklist count, not a production-readiness percentage. Stage 1 remains **not production-accepted**.


## Latest verified checkpoint — 2026-11-10 (commit 26a9ed8)

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `26a9ed840449cab9abeb573d5029b02d8fcbe998`
- Automated Tests & Build: [run 42810062870](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42810062870) — **success**.
- CodeQL Security Analysis: [run 42810062624](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42810062624) — **success** for JavaScript/TypeScript and Python.
- Verified steps: frontend dependency install/audit, frontend unit tests/build, frontend bundle secret scanner and production credential scan, backend dependency install/pytest/audit, Docker image build, Redis + persistent-volume smoke test, Trivy image scan, vulnerability-report export/upload.
- The backend test suite initially exposed one invalid test fixture (close=999 while high=103). The fixture was corrected to a valid but different close=102, preserving the intended exact-payload mismatch test. The rerun passed.
- Implementation: durable outbox cursor and persisted event ID now propagate into the WebSocket snapshot and live notification path. The callback resolves the exact stored event for each source/derived bar revision rather than assuming the global latest cursor belongs to that bar.
- Still outstanding: WebSocket reconnect cursor input and durable replay delivery, expired-cursor resnapshot protocol at the socket layer, replay authorization/pagination integration, and sustained throughput/reconnect benchmarks.
- Feed coverage is not all-pair by default: `DATABENTO_LIVE_SYMBOLS` defaults empty and the live source subscribes only to explicitly configured raw contract symbols. The current default allowed roots are ES, NQ, and GC. Real-time coverage requires lawful provider entitlement, credentials, and explicit configured symbols.
- This CI/CodeQL evidence does not satisfy real production Firebase/managed Redis integration, provisioned production volume, encrypted off-host backup/restore, deployed HTTPS/WSS, external monitoring/alert delivery, or market-data licensing/provider coverage.

**Checklist remains 30/40 with 10 external production gates outstanding.** The durable cursor bridge is a partial implementation increment and does not close the full reconnect/replay acceptance requirement. Stage 1 remains **not production-accepted**.


## Latest verified implementation checkpoint — durable WebSocket replay (2026-11-10)

- Branch: `phase-2/market-data-foundation`
- Exact code commit tested: `38174c9c4e6280669649cb4677426809c37d9cf5`
- Automated Tests & Build: [run 42812016639](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812016639) — **success**.
- CodeQL Security Analysis: [run 42812016650](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812016650) — **success** for JavaScript/TypeScript and Python.
- Verified: frontend dependency audit/unit tests/build/secret scans; backend pytest/dependency audit; Docker image build; Redis + persistent-volume smoke test; Trivy image scan; vulnerability report export/upload.
- Implementation now accepts an optional decimal-string reconnect cursor, authorizes the exact series before replay, performs bounded exact-series replay, and hands off to live updates with a new contiguous stream sequence. Expired/ahead cursors, replay storage errors, and excessive backlog explicitly fall back to a fresh snapshot.
- Frontend stream client and supervisor now preserve the last accepted durable cursor across transient socket reconnects, apply replay events through the existing validated update path, and retain the current chart while reconnecting. Cursor values remain strings to avoid JavaScript integer precision loss.
- Added backend and frontend regression coverage for replay ordering, exact series identity, cursor-ahead resnapshot, cursor precision, replay/live transition, and supervisor reconnect.
- This remains repository evidence, not production browser/Android WSS proof. Sustained throughput/reconnect benchmarks and real production provider latency/gap evidence remain outstanding.

**Checklist accounting remains 30/40, with 10 external production verification gates outstanding.** No external gate is marked complete by source-code changes or CI alone. Stage 1 remains **not production-accepted**.


## Latest verified checkpoint — reconnect cursor hardening (2026-11-10)

- Branch: `phase-2/market-data-foundation`
- Exact code commit: `9cb7a876bca9215b7792312aa908b3ad60e0b5a6`
- Automated Tests & Build: [run 42812627122](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812627122) — **success**.
- CodeQL Security Analysis: [run 42812627082](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42812627082) — **success** for JavaScript/TypeScript and Python.
- Latest regression hardening rejects non-ASCII digit cursor strings, decimal strings, and values outside signed SQLite 64-bit range; malformed cursors are rejected with the expected WebSocket close code.
- Verified workflow steps include frontend dependency audit/unit tests/build/secret scans, backend pytest/dependency audit, Docker image build, Redis + persistent-volume smoke test, Trivy scan, and vulnerability-report export/upload.
- These checks validate repository behavior only. They do not prove every market pair is configured or entitled, every timeframe has live provider coverage, or production Firebase/Redis/HTTPS/WSS, backup restore, monitoring, and alert delivery have passed.

**Checklist remains 30/40 with 10 external production verification gates outstanding.** The reconnect cursor hardening does not close any external gate. Stage 1 remains **not production-accepted**.


## Verified implementation — replay I/O event-loop isolation (2026-11-10)

- Candidate code commit: `dac22020bfe10e48cef58f5125ee3e6d341bc969` on `phase-2/market-data-foundation`.
- The SQLite durable replay page read is executed with `asyncio.to_thread`, preventing the bounded synchronous SQLite query from occupying the ASGI event-loop thread. Subscription-before-replay and queue handoff remain unchanged.
- Exact branch-head verification commit: `63469d9cb4d4557e4e3c992056ea2a732a1e5ea2`. This commit descends from the replay candidate and was tested as a whole.
- Automated Tests & Build: [run 42815030378](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030378) — **success**. Frontend unit tests/build/secret scans, backend pytest/dependency audit, Docker build, Redis + persistent-volume smoke test, Trivy scan and report export all passed.
- CodeQL Security Analysis: [run 42815030406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030406) — **success** for JavaScript/TypeScript and Python.
- No external production gate is closed by this code change or by repository CI alone.

## Market-data coverage and timeframe readiness — explicit acceptance blockers

This is an additional operational/functional acceptance track; it does not change the 40-point checklist count above.

- The live adapter currently requests the Databento `ohlcv-1s` schema and subscribes only to the explicit `DATABENTO_LIVE_SYMBOLS` raw-contract allowlist. The setting defaults to empty. Therefore the repository does not provide all-pair LIVE coverage by default.
- Supported timeframe identifiers include `1s, 5s, 15s, 30s, 45s, 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 4h, 1d, 1w, 1M, 3M`. Most are intended to be derived from accepted child bars; a timeframe being listed is not proof that a live series is currently produced.
- The aggregator deliberately fails closed for `CME_SESSION_V1` bars until verified session-aligned bucket bounds are available. In particular, it currently skips derivation for CME-session bars rather than risk assigning futures bars to incorrect UTC/session buckets. UTC-fixed derivation also stops before daily/weekly/monthly periods. This means the code must not be represented as delivering every timeframe for CME futures.
- `backend/app/databento_sources.py` explicitly labels its official SDK wrappers **UNVERIFIED**; the real SDK calls have not yet been exercised with valid provider credentials in CI or a production-like environment.
- Before claiming all-pair/all-timeframe LIVE readiness, require: (1) real SDK connection and callback verification for the pinned SDK version, (2) approved provider entitlements and a complete configured instrument universe, (3) exchange-calendar-aware intraday and higher-timeframe bucket derivation with DST/holiday/early-close tests, (4) per-instrument/per-timeframe gap and completeness checks, and (5) measured event-to-client latency and reconnect recovery across every supported timeframe.

**No source-code shortcut is accepted for these requirements.** Existing fail-closed behavior is intentional protection against fabricated or misaligned candles. Replay I/O event-loop isolation was verified on ancestor commit `63469d9cb4d4557e4e3c992056ea2a732a1e5ea2` by successful Automated Tests and CodeQL runs 42815030378 and 42815030406. The current calendar publication timestamp hardening is a separate change and remains pending its own exact-commit CI; neither change proves feed coverage or timeframe derivation.


## Latest verified branch-head checkpoint — 2026-11-10

- Branch: `phase-2/market-data-foundation`
- Exact branch head: `63469d9cb4d4557e4e3c992056ea2a732a1e5ea2`
- Automated Tests & Build: [run 42815030378](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030378) — **success**.
- CodeQL Security Analysis: [run 42815030406](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42815030406) — **success**.
- The exact branch head includes the replay I/O isolation candidate and its prior implementation history. Workflow jobs were inspected individually; every listed job and step completed successfully.
- Checklist accounting remains 30/40 with 10 external production verification gates outstanding. Market-data provider, symbol-universe, SDK, calendar-aware timeframe, and latency requirements remain additional functional acceptance blockers. Stage 1 remains **not production-accepted**.


## Stage 1 integrated functional workstream — session-aware timeframe derivation

This is an additional functional acceptance track **inside Stage 1**, not a separate stage and not a replacement for any of the 40 production checklist criteria. The owner approved the engineering blueprint on 2026-11-10 for staged implementation.

- Approved engineering basis: [SESSION_AWARE_AGGREGATION_BLUEPRINT.md](SESSION_AWARE_AGGREGATION_BLUEPRINT.md).
- Current CME-session aggregator remains fail-closed. The calendar artifact still needs explicit tradable segments and intraday breaks; bucket alignment must be grounded in authoritative exchange specifications.
- This workstream must be completed and tested before claiming supported futures timeframes. Approval alone does not mark it complete or production-ready.
- The 10 external production gates remain outstanding independently. The 40-point matrix will not be reduced or marked complete merely because this workstream is approved.



## Latest code hardening checkpoint — calendar publication timestamp (2026-11-10)

- Code commit: `088e91dc135e65adbb0ad176f89a5c32cfec6df4`.
- Test commit / current branch head: `1f52e8053fbd6ed50ce94b2cf93ac906ff75814e`.
- `SessionCalendar.published_at_utc` now rejects aware timestamps with non-zero UTC offsets and normalizes valid zero-offset timestamps to `timezone.utc`.
- Regression test covers conversion from America/Chicago to UTC and rejection of non-UTC offsets.
- Exact-commit Automated Tests run: [42816364225](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816364225) — queued at the latest inspection.
- Exact-commit CodeQL run: [42816364046](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816364046) — analysis in progress at the latest inspection.
- This hardening does not change the 30/40 checklist evidence count or close any production gate. Do not mark it CI-verified until both workflows finish successfully.


## Latest exact-commit verification — calendar UTC test repair (2026-11-10)

- Branch: `phase-2/market-data-foundation`.
- Exact tested commit: `cc2914e95aa6646a4b5dcba9f5c76dfd60992d59`.
- The production invariant is unchanged: `published_at_utc` must have a zero UTC offset and is normalized to canonical `timezone.utc`. The regression fixture was corrected to use a zero-offset timezone for the normalization case; a Chicago (UTC-6) timestamp remains explicitly rejected.
- Automated Tests & Build: [run 42816899715](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816899715) — **success**. Every step passed, including frontend audit/tests/build/secret scans, backend pytest/dependency audit, Docker build, Redis + persistent-volume smoke test, Trivy scan, and vulnerability report export/upload.
- CodeQL: [run 42816899668](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42816899668) — **success** for both Python and JavaScript/TypeScript jobs.
- This closes the pending CI verification for the UTC timestamp hardening only. It does not implement session-aware aggregation, verify the Databento SDK against a real account, or satisfy any external production gate.
- Checklist accounting remains **30/40** with **10 external production verification gates** outstanding. Stage 1 remains **not production-accepted**.


## Latest exact-commit CI verification — 2026-11-10

- Exact commit: 7b41c5a3ead82cb07f428b10474ba01267a45c60 on phase-2/market-data-foundation.
- Automated Tests & Build: [run 42817566167](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42817566167) — **success**. All steps completed successfully, including frontend dependency audit, unit tests, build, bundle-secret scans, backend pytest, backend dependency audit, Docker build, isolated Redis + persistent-volume restart smoke test, Trivy image scan, vulnerability report export, and artifact upload.
- CodeQL Security Analysis: [run 42817566002](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42817566002) — **success** for Python and JavaScript/TypeScript analysis.
- This exact-commit CI evidence supersedes the earlier pending/queued checkpoint notes above for the 7b41c5a commit. It verifies repository CI and an ephemeral CI volume/Redis test only; it does **not** prove a Fly deployment, managed Redis, production Firebase credentials, a production Fly Volume, encrypted off-host backup/restore, production WSS, or external monitoring/alert delivery.
- External production gates remain **10/40 outstanding**. Stage 1 remains **not production-accepted** and the checklist count is unchanged.


## Mandatory zero-cost acceptance overlay — owner decision 2026-11-10

- The owner has explicitly prohibited all project charges and unexpected future bills. This is a mandatory constraint across all 40 criteria, including hosting, identity, market data, backup, monitoring, alert delivery, CI, and operations.
- The Fly.io plan is superseded as an executable deployment target. Do not create an app, Machine, Volume, managed Redis instance, billing account, or trial.
- Databento live/historical access remains disabled; no paid market-data API or dataset may be used. A free source must be independently checked for lawful use, coverage, freshness, quotas, and no billing exposure before adoption.
- Firebase is permitted only if the exact selected authentication methods remain within a verified no-billing plan. Phone/SMS and billing upgrades are prohibited. If billing is required, defer the integration rather than upgrade.
- Any no-cost replacement for managed Redis or external operations tooling must preserve the existing security guarantees and be reviewed/tested before changing production requirements. No insecure in-memory fallback is allowed.
- A free tier or promotional credit alone is not evidence of zero cost. Payment methods, automatic upgrades, overages, trial conversion, and quota exhaustion behavior must be checked. Unknown billing behavior means do not enable the service.
- This overlay does not reduce the 40 criteria, does not close external gates, and does not change the current 30/40 evidence accounting. Stage 1 remains not production-accepted.


## Ten remaining external gates — zero-cost remediation register (2026-11-10)

The following ten criteria are audited individually. ZERO MONEY is binding, so none may be closed by purchasing a service, enabling billing, attaching a payment method, starting a trial, or accepting an overage. A repository test is not a substitute for the real-host evidence required by an external gate.

| Criterion | Current status | Zero-cost handling plan | Evidence still required |
|---|---|---|---|
| 8 — production secret storage | **Open — host not provisioned** | Use the operating system's protected secret/environment mechanism on an already-owned host; keep secrets out of Git, frontend bundles, logs, and chat. Do not buy a managed secret store. | Inspect the actual host's permissions and process environment; scan deployed artifacts/logs. |
| 20 — real Firebase identity flow | **Open — no real project verification** | Keep the integration disabled until a no-billing Firebase configuration and non-billable sign-in method are verified. Use emulator-based regression tests where possible without billing. Never enable phone/SMS or upgrade to a billing plan. | Real signed-token, expiry/revocation, entitlement-denial, reconnect and web/Android test against a verified no-billing project. If that cannot be guaranteed, defer production auth integration. |
| 25 — managed Redis TLS/access/failover | **Open — managed service prohibited** | Candidate alternative: self-host Redis on the same already-owned host, with TLS, authentication, private binding, persistence policy, and fail-closed application behavior. No in-memory fallback. | Owner-approved topology plus tests for TLS certificate validation, access restrictions, Redis outage, restart/persistence and recovery. A single local Redis instance does not prove managed failover or high availability. |
| 30 — production-like backup restore | **Open — external drill not recorded** | Run SQLite Online Backup API restore tests locally against a fresh database and verify known application-level records, not only SQLite integrity. Use existing storage only. | Dated restore report from the actual chosen host and backup location. |
| 31 — encrypted off-host backup/key recovery | **Open — no destination or key custody verified** | Candidate: client-side encryption with an open-source tool and key material held separately on storage already owned by the project owner. No paid cloud bucket, paid KMS, or new storage purchase. | Confirm existing off-host storage is available at zero incremental cost; prove encryption, access restriction, retention, key recovery, and a successful restore. If no suitable existing storage exists, keep this gate open. |
| 34 — production persistent volume | **Blocked by zero-cost decision — Fly.io superseded** | Do not create a Fly Volume. Candidate replacement is a persistent local disk/directory on an already-owned machine, with explicit permissions and a single-writer SQLite topology. | Owner confirms an existing host/storage resource; verify mount/path ownership, restart durability, replacement/recovery. No new hardware or hosting purchase. |
| 35 — production HTTPS deployment | **Blocked by zero-cost decision — Fly.io superseded** | Do not deploy to Fly or buy a domain/hosting. Candidate is a service on an already-owned host. Public HTTPS is only acceptable if an existing domain/network path and certificate can be used without charges; otherwise keep service local and mark public production deployment deferred. | Verify actual HTTPS endpoint, health/startup behavior, secret injection, and certificate renewal without creating a bill. |
| 36 — production WSS through reverse proxy | **Open — no deployed endpoint** | First run local reverse-proxy/WSS integration tests on existing hardware, preserving origin checks and authenticated subscription. No paid CDN, tunnel, proxy, or hosting. | Successful web and Android client handshake/subscription against the actual zero-cost deployment path. |
| 38 — external monitoring/logging | **Open — no external collector** | Prefer bounded local logs/metrics and a self-hosted dashboard on existing hardware. No paid observability service or usage-metered log retention. | Verify retention limits, access controls, dashboard availability, and that monitoring does not expose secrets. |
| 39 — alert delivery/incident response | **Open — delivery channel unverified** | Implement local alert records/logs and a documented manual response path first. Do not use paid SMS, email, paging, or trial services. | Demonstrate an alert reaches an already-available no-cost operator channel; test acknowledgement/escalation/recovery. Otherwise document manual-only operations and keep external delivery gate open. |

### Hard boundary before changing the architecture

- The candidate local/self-hosted alternatives are **design options**, not proof that the owner has suitable hardware, network access, backup media, a domain, or a free alert channel.
- Do not change production startup validation, weaken Redis fail-closed behavior, enable a provider, or publish a public endpoint until the zero-cost alternative has been reviewed and its security tests pass.
- The owner must not buy hardware, hosting, domains, storage, or subscriptions to close these gates. If existing resources are insufficient, the affected production capability remains deferred.
- The ten gates remain open. No percentage or checklist count is increased by this remediation register.



## Zero-cost disposition for all ten external gates — 2026-11-10

The owner-mandated ZERO MONEY policy is binding across Stage 1 and all later stages. The gate-by-gate resolution plan is documented in [STAGE_1_ZERO_COST_GATE_PLAN.md](STAGE_1_ZERO_COST_GATE_PLAN.md). It specifies no-billing candidate approaches, required evidence, and explicit defer conditions for criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39.

This plan is not production evidence and does not close any external criterion. No paid provider, hosting, managed Redis, Firebase billing upgrade, paid backup/KMS, paid monitoring/alerting, domain, trial, or paid runner is authorized. If an existing owner-controlled environment cannot meet a gate safely at zero incremental cost, keep that gate open/constrained rather than weakening controls or creating a payment obligation.


## Android debug APK — owner-reported smoke test (2026-11-13)

- The owner installed the generated debug APK on the Infinix GT20 and confirmed that the app launches and displays the chart screen.
- The owner opened Settings, cleared the app cache, relaunched the app, and reported that it remained operational without a visible issue.
- The screenshot shows the chart's explicit `DEMO DATA · SAMPLE OHLC` label. This is evidence of Android packaging and a limited UI launch/cache-relaunch smoke test only; it is **not** evidence of live CME data, Firebase authentication, backend connectivity, production WSS, notification delivery, or production readiness.
- This is owner-reported manual evidence, not an independently captured device test report. No Stage 1 criterion is closed or re-counted from this report.
- Push/local notification delivery is intentionally deferred to its planned later stage. Stage 1 must not claim notification delivery as implemented or verified.
- No app code was changed as part of recording this manual test. The existing APK build and CI evidence remain tied to their recorded commits and workflow runs.




## Latest verified checkpoint — SQLite backup durability on Android (2026-11-13)

- Branch: `phase-2/market-data-foundation`
- Exact tested branch-head commit: `58594459ee60113e75ea3c4d908e1d56ac3eec4b`
- Code changes:
  - `47c6c736` — flush the SQLite snapshot file before atomic publication; fail closed on flush failure.
  - `f2ba7bde` — flush the parent directory after atomic replacement; surface directory-flush failure instead of claiming confirmed durability.
  - `3ec67dcb` and `58594459` — regression tests for snapshot flush failure, parent-directory flush invocation, and post-replacement directory-flush failure semantics.
- Automated Tests & Build: [run 43407628746](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43407628746) — **success** for the exact branch-head commit. All 28 job steps completed successfully, including frontend unit tests/build, backend pytest, dependency audits, synthetic SQLite outbox benchmark, Docker build, Redis + persistent-volume container smoke test, Trivy image scan, and vulnerability-report export/upload.
- CodeQL Security Analysis: [run 43407628566](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43407628566) — **success** for the same commit.
- Owner-device smoke test: the owner pulled the exact branch head into Termux on Android and ran the SQLite backup helper. Observed `PRAGMA integrity_check = ok`, restored/read value `DEZZTA_OK`, and `ANDROID_BACKUP_TEST: SUCCESS`. This verifies the basic backup and directory-fsync path on that device/filesystem.
- Scope limitation: the Android smoke test used a temporary local source and backup file; it is not the production-like application restore drill in criterion 30, a power-loss test, or an off-host restore. Criteria 30 and 31 remain external verification gates.
- No paid service, provider credential, production deployment, or feature removal was introduced by this work.

**Checklist accounting remains 30/40, with 10 external production verification gates outstanding.** The new Android smoke test and green CI/CodeQL runs strengthen repository/device evidence but do not close external deployment gates. Stage 1 remains **not production-accepted**.


## Latest verified checkpoint — 2026-11-13 (commit 08bdf52)

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `08bdf52cb60b2c98216df2437b3f9363cd4e2d66`
- Automated Tests & Build: [run #1006](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43413442206) — **success**.
- CodeQL Security Analysis: [run #364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43413442133) — **success** for Python and JavaScript/TypeScript.
- Backend regression suite: **774 passed in 24.03s**. Frontend tests/build, backend dependency audit, synthetic SQLite outbox benchmark, Docker build, Redis + persistent-volume smoke test, Trivy image scan, and vulnerability-report export/upload also passed.
- CME daily aggregation now consumes only validated UTC 1-hour child bars, matching the accepted ADR. Finer bars continue through the normal UTC intraday hierarchy; each 1-hour interval is re-resolved against the pinned calendar and rejected if it crosses a tradable-segment boundary. Regression tests cover direct 1-hour input, 1-second cascade through an open 1-hour child, complete 1-minute-to-1-hour-to-daily derivation, and split-session rejection.
- The synthetic CME calendar fixtures are test-only. No authoritative production CME schedule is loaded, and no live provider entitlement or production client path is established by this CI.
- The synthetic outbox benchmark now exercises concurrent replay readers alongside the single SQLite writer; it remains a single-process benchmark, not a production or multi-process SLO.
- **Acceptance accounting remains 30/40, with 10 external production gates open:** 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39. No external gate is closed by this repository-only work. Stage 1 remains **not production-accepted**.


## Owner-confirmed one-phone/no-PC constraint — 2026-11-13

The owner has one Android device (Infinix GT20, Android 15) and no second phone, PC, or laptop. This constraint supersedes all candidate remediation text above that assumes an additional owner-controlled host or second device. Do not ask the owner for a second device again and do not propose purchasing hardware or enabling paid infrastructure.

The ten open production gates remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Their phone-only feasibility is classified in STAGE_1_ZERO_COST_GATE_PLAN.md, section **Owner-confirmed device constraint and phone-only disposition**.

- Criterion **30** is the nearest same-device candidate: the SQLite Online Backup API and restore-to-fresh-path flow can run using Python/SQLite standard-library support. Existing device evidence covers integrity/readback smoke, and CI includes application-record restore tests; one consolidated application-record restore report from the owner's device is still missing. This does not satisfy off-host disaster recovery.
- Criterion **31** remains blocked by lack of a second device/verified off-host destination and the unresolved Termux Play Store cryptography>=50,<51 package/keyring mismatch.
- Localhost, CI, APK, and local-storage tests can strengthen evidence for criteria 8, 20, 25, 34, 35, 36, 38, and 39, but do not prove production host, public endpoint, independent monitoring, or operator delivery.

No criterion is closed and the 30/40 provisional accounting is unchanged by this constraint record. Do not change the production acceptance definition or claim 40/40 without owner-approved scope revision and evidence.


## Criterion 8 repository-side audit update — 2026-11-13

Repository-side defense-in-depth now includes a pre-build scan of frontend JS/JSX/TS/TSX source, the existing post-build production-bundle scan, a TSX token-pattern regression test, and backend settings \`repr()\`/\`str()\` redaction tests. The exact-HEAD CI and CodeQL runs are recorded in \`docs/PROJECT_PROGRESS.md\`; their conclusions must be checked before acceptance.

This does **not** change criterion 8 from **External verification required**. The owner-controlled host's secret-injection mechanism, deployed runtime/build logs, GitHub secret-scanning settings/alerts, and reachable repository history remain unverified. No paid secret manager or billing-enabled infrastructure may be introduced.


## Criterion 8 repository-side audit update — 2026-11-13 (verified)

The full reachable Git-history scan is now implemented in CI using Gitleaks v8.30.1, a full-depth checkout, `--log-opts="--all"`, and a SHA-256-verified release archive. Dedicated run [#43451610210](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610210) scanned **1,133 commits (~2.57 MB)** and reported **no leaks**. Integrated CI [#43451610297](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610297) and CodeQL [#43451610192](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610192) both passed on commit `efdf9a9ecfa68647586cd89f819e76469e11d3df`.

This closes the repository-side reachable-history scan subtask only. Criterion 8 remains **External verification required** until the owner-controlled production host's secret-injection mechanism and deployed logs are inspected, and GitHub native secret-scanning/push-protection settings plus alert inventory are verified. The history scan does not prove the absence of secrets in unreachable Git objects or external clones.
## Stage 1 progress tick display — 2026-11-14

This is the project's progress indicator scale requested by the owner. It is **not** a technical indicator inside the APK and does not refer to market-price ticks.

### Scale

- 40 Stage 1 acceptance criteria × 10 display ticks each = **400 total ticks**.
- 1 accepted criterion = 10 ticks = 2.5% Stage 1 progress.
- 1 tick = 0.25 percentage points of Stage 1 progress.
- A criterion receives all 10 ticks only when its complete acceptance condition and required evidence are met. No inferred fractional/sub-tick credit.

### Current audited tally

| Item | Ticks | Stage 1 share |
|---|---:|---:|
| 30 provisionally accepted/implemented criteria | **300 / 400** | **75%** |
| 10 external verification criteria still open | **100 / 400 outstanding** | **25%** |
| Total | **400 / 400** | **100% scale** |

Open criteria (0/10 ticks each): **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stage 1 remains **not production-accepted**. “300 ticks” is the finer representation of the existing provisional 30/40 tally, not a new completion award.

### Tick change policy

A future tick change must cite the criterion number, its full acceptance boundary, exact evidence/report, and exact tested commit. Repository work toward an external gate is progress in remediation but does not earn that gate's ticks before its external evidence exists. CI/documentation/commit volume alone never changes the tally. The tick scale is separate from the overall weighted project percentage and from the in-app technical indicator tracker.


## Ten-gate work-cycle audit — 2026-11-14

See [STAGE_1_ZERO_COST_GATE_PLAN.md](STAGE_1_ZERO_COST_GATE_PLAN.md) for the per-gate disposition. Repository-side test expansion now covers a single restored application database across instrument registry, entitlements, alert zones, coverage intervals/gaps, OHLCV and durable outbox, including a post-restore write. The new shared-application-database restore test passed exact-commit CI on `e599b45d480c29f195d53047cf9b301182a74de0` (Automated Tests #43566762952).

This strengthens criterion 30's repository-side evidence only. It does not satisfy the required target-environment restore drill. Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 all remain **OPEN / external verification required**; no ticks are awarded by this test or its CI result alone.


## Criterion 20 implementation status correction — 2026-11-14

The source audit confirms the Firebase client prototype is already integrated and mounted; the previous statement that the frontend had not yet been connected is stale. Owner setup context records a registered Firebase Web App on the Spark/no-billing path with Google Sign-In and Email/Password methods enabled. The source includes email registration/sign-in, Google redirect, auth-state/ID-token observer, fresh token acquisition for WebSocket reconnect, backend Firebase Admin verification with `check_revoked=True`, entitlement enforcement and periodic WebSocket revalidation.

This is **repository implementation plus owner-configured provider setup**, not a completed real-provider integration drill. Live project billing state, actual frontend runtime configuration, backend Admin credential injection, real sign-in, revocation/expiry, entitlement denial and browser/Android WSS reconnect evidence remain required. Criterion 20 stays OPEN and receives no acceptance ticks.


## Exact-commit CI evidence — 2026-11-14 — `e599b45d480c29f195d53047cf9b301182a74de0`

- Automated Tests workflow #43566762952: **completed successfully**. Frontend dependency audit, unit tests, production build and bundle secret scans passed; backend tests passed including the expanded shared-application-database restore test; bounded SQLite outbox benchmark passed; backend dependency audit passed; container image build passed; Redis shared-guard + persistent-volume smoke test passed; Trivy image scan/report completed; workflow cleanup completed.
- CodeQL workflow #43566763073: **completed successfully** (Python and JavaScript/TypeScript).
- Full Git History Secret Audit #43566762971: **completed successfully**.
- Exact branch HEAD at this checkpoint: `e599b45d480c29f195d53047cf9b301182a74de0`.
- The restore regression now passes in CI. It strengthens criterion 30 repository-side evidence only; it does not substitute for an owner-device/production restore report.
- The Redis and persistent-volume CI smoke tests strengthen criteria 25 and 34 repository-side evidence only; they do not prove owner-host production network, TLS, ACL, mount or restart behavior.
- No external gate was closed and no Stage 1 ticks were awarded by CI alone. Stage 1 remains **300/400 = 75% provisional**.

Workflow evidence:
- Automated Tests: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43566762952
- CodeQL: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43566763073
- Gitleaks: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43566762971


## Criterion 30 — exact-HEAD CI passed; target-device evidence still required — 2026-11-14

The fresh-destination restore implementation in `backend/app/sqlite_backup.py` passed the exact-HEAD CI workflows on `13f489aebffa193affcb8eae619503e78e512b29`:
- Automated Tests #43569886961 — SUCCESS.
- CodeQL #43569886954 — SUCCESS.
- Full Git History Secret Audit #43569886911 — SUCCESS.

The helper verifies SQLite integrity and foreign-key consistency, refuses to overwrite a destination, publishes through an atomic same-directory hard link, applies owner-only POSIX permissions, flushes the restored file and parent directory, and cleans temporary files on failure.

This is repository implementation evidence only. Criterion 30 remains **OPEN** until an actual owner-device application database restore is completed into a fresh destination, with application-level readback of the durable domains and a post-restore write on the restored copy. The source database must remain untouched. No tick is awarded by CI alone.


## Gate 10 batch 2 — restore failure-path CI evidence — 2026-11-14

Exact source HEAD: `4e741f10d5c27dba7994742a45d08f2d1c590415`

The restore helper's failure behavior is now covered by three additional regression tests:

- `test_restore_fails_closed_when_owner_only_permissions_cannot_be_set`
- `test_restore_fails_closed_when_restored_file_cannot_be_flushed`
- `test_restore_fails_closed_when_atomic_publication_is_unavailable`

Together with the five baseline restore tests, the focused restore module contains eight tests. The new tests verify fail-closed publication behavior and temporary-file cleanup for permission, flush and atomic-publication failures.

Exact-HEAD CI:
- Automated Tests [#43570345495](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345495) — **SUCCESS**.
- CodeQL [#43570345625](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345625) — **SUCCESS**.
- Full Git History Secret Audit [#43570345516](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43570345516) — **SUCCESS**.

This closes the repository-side test/CI subtask only. Criterion 30 remains **OPEN** until the actual owner-device application database is restored to a fresh destination, integrity and foreign-key checks pass, durable application domains are read back, and a post-restore write is verified on the restored copy. The source database must remain untouched.

No criterion tick is awarded by this CI result. Stage 1 remains **300/400 = 75% provisional** with criteria **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39** open.


## Gate 10 batch 3 — criterion 30 restore-helper regression refinement — 2026-11-14

The full shared-application-database restore test now invokes `restore_consistent_sqlite_backup()` directly rather than manually copying the snapshot. It verifies integrity and foreign-key checks, reopens every durable application store, checks representative application records, and proves a post-restore write on the restored copy.

Two additional tests cover directory-flush failure after publication and a competing process creating the destination immediately before atomic publication. The intended guarantees are tested: durability uncertainty is surfaced without pretending publication was rolled back, and a destination created by another process is never overwritten.

Exact-HEAD CI is pending. Criterion 30 remains OPEN pending the actual owner-device restore report; no acceptance ticks are awarded by these repository tests alone.


## Criterion 30 — Gate 10 batch 3 evidence boundary — 2026-11-14

The shared-application-database restore regression now invokes `restore_consistent_sqlite_backup()` directly, validates SQLite integrity and foreign-key consistency, reopens durable application stores, checks representative records across registry, entitlement, alert-zone, coverage/gap, OHLCV and outbox/replay domains, and verifies a post-restore write on the restored copy. Directory-flush failure after publication and a competing destination race are also covered.

Exact-HEAD CI on `ba01807b043de1f446b0630002ff607ac48a069a` passed Automated Tests #43571145976, CodeQL #43571145954 and Full Git History Secret Audit #43571145944. This is repository-side evidence only. Criterion 30 remains OPEN until the actual owner-device application database is restored to a fresh destination and a secret-free report verifies all available durable domains and a post-restore write. Do not overwrite or delete the source DB; do not assume the repository's default DB path is the live Android path.


## Documentation HEAD CI completion — 2026-11-14

The documentation commit `cf7044922df3cac0d2e9a52679509ea0aa957a81` has now passed all exact-HEAD workflows: Automated Tests #43571570406, CodeQL #43571570477, and Full Git History Secret Audit #43571570418 — all **SUCCESS**. This validates the documentation revision and does not change the acceptance state of any criterion. Stage 1 remains **300/400 = 75% provisional**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain OPEN pending external evidence.


## Gate 10 batch 4 — exact-HEAD CI and database-path audit — 2026-11-14

**Audited branch HEAD:** `38309c377dc8ff9f800461a7890965ac7c46b958` (`phase-2/market-data-foundation`; `main` untouched).

All three workflows for this exact HEAD are now complete:
- Automated Tests [#43571964355](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43571964355) — **SUCCESS**.
- CodeQL [#43571964368](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43571964368) — **SUCCESS**.
- Full Git History Secret Audit [#43571964397](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43571964397) — **SUCCESS**.

The repository audit confirmed that the backend's shared SQLite path is configured by `INSTRUMENT_REGISTRY_DB_PATH`, defaulting to `./data/instrument_registry.sqlite3`. `create_app()` passes that same configured path to the instrument registry, price-alert store, entitlement store, OHLCV store, coverage tracker, and provider-definition synchronizer. This is the backend process's configured path, not proof of the resolved path of a running Android service.

The installable APK workflow generates a temporary Capacitor wrapper and packages the frontend. The repository has no checked-in Android host project that bundles or supervises the Python backend/Redis. Therefore, the APK installation does not by itself establish that this backend database exists on the phone. Criterion 30 still requires identifying the actual running backend process and its effective working directory/environment before any owner-device restore drill.

### Repository regression added in this batch

- `backend/tests/test_api.py`: verifies the five durable adapters exposed by `create_app()` share the exact configured SQLite path and that the database file is initialized.
- `backend/tests/test_config_security.py`: verifies `INSTRUMENT_REGISTRY_DB_PATH` is read from the backend environment.

These tests make the repository's path contract explicit. They do not prove a live Android database location and award no Stage 1 ticks by themselves.

### Acceptance and safety disposition

- Criterion 30: **OPEN** — target-device/live-backend restore report not yet available.
- Criterion 31: **OPEN / BLOCKED** — Termux Google Play repository signing-key mismatch and no verified off-host target/key-custody path.
- Termux: keep the existing working repository configuration; no package command, repository switch, key import, signature bypass, crypto downgrade, or app migration is authorized or required.
- Stage 1: **300/400 ticks = 75% provisional**; 30/40 criteria provisionally accepted; open criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stage 2–6: **NOT SCORED**. Overall project: historical owner-confirmed **20.90%** only; no newly approved weighted calculation.

No external acceptance gate is closed by this repository work or green CI alone.


## Gate 10 batch 5 — exact-HEAD CI and restore failure-path hardening (2026-11-14)

- Starting HEAD: `cabf637bf2e48cb54983a98bd854416975272df5`.
- Automated Tests & Build: [#43572423301](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43572423301) — **SUCCESS**.
- CodeQL: [#43572423236](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43572423236) — **SUCCESS**.
- Full Git History Secret Audit: [#43572423268](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43572423268) — **SUCCESS**.
- All three workflows completed against the same exact HEAD. Automated Tests completed frontend tests/build and secret scans, backend pytest, dependency audit, synthetic SQLite benchmark, backend container build, Redis/persistent-volume smoke test, and image vulnerability scanning.
- Added regression coverage for a corrupt/non-SQLite restore source. The restore must raise a database error, publish no destination, and clean its temporary file.
- This is repository-side failure-path coverage only. Criterion 30 still requires the actual owner-device application database path and a consolidated restore report. Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open; no external criterion or progress tick is awarded by this batch.
- Stage 1 remains 30/40 provisional (300/400 ticks, 75%) and not production-accepted.

## Gate 10 batch 6 — exact-HEAD CI reconciliation and documentation link repair (2026-11-14)

**Exact source/test HEAD:** `8a159274eaa35339b8f68a1948f0bab002bc998c` on `phase-2/market-data-foundation`.

All three workflows completed successfully against this exact commit:
- Automated Tests [#43582913692](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43582913692) — **SUCCESS**.
- CodeQL [#43582913713](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43582913713) — **SUCCESS**.
- Full Git History Secret Audit [#43582913733](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43582913733) — **SUCCESS**.

Automated Tests passed frontend tests/build and secret scanning, Android host preflight, backend tests (including corrupt SQLite restore rejection), synthetic outbox benchmark, dependency audits, backend container build, Redis/persistent-volume smoke test, backend image scan and vulnerability-report export. No workflow failure was reported.

Documentation repair: corrected the malformed CodeQL run URL in this batch's earlier Gate 10 references. This is a documentation integrity correction, not a change to application behavior.

Acceptance accounting is unchanged:
- Stage 1: **30/40 provisional criteria = 300/400 ticks = 75% provisional**.
- External criteria still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 are not closed by CI alone. Criterion 30 still needs an owner-device restore report; criterion 31 remains blocked by the unverified Termux-compatible encrypted off-host/key-custody path.
- Stages 2–6 remain **NOT SCORED** and officially unopened.
- Overall project remains the historical **20.90%** checkpoint; no new weighted score is approved.

Termux disposition: no action required in this batch. Keep the known-good Google Play repository and signature verification unchanged. No device command, repository switch, key import, or crypto downgrade is authorized or needed.


### Criterion 30 — owner-device drill tooling (2026-11-14)

A reusable report-producing procedure is implemented in backend/app/sqlite_restore_drill.py. It snapshots the actual source database through SQLite Online Backup, restores to a fresh path through restore_consistent_sqlite_backup, checks required shared-application tables, integrity and foreign keys, compares per-table counts, reopens registry/entitlement/alert/coverage/OHLCV adapters, validates outbox event identity uniqueness, and tests a write/read/cleanup operation on the restored copy only. Automated tests use a synthetic application database and are repository evidence only. Criterion 30 remains OPEN until the tool is executed against the actual owner-controlled Android backend database and a redacted report is reviewed.


### Criterion 30 — report integrity and latest repository evidence (2026-11-14)

The owner-device drill report now includes a generated drill ID and SHA-256 over canonical redacted JSON, plus passed/failed check metadata. Automated tests validate the report hash, domain counts, source immutability, and no-overwrite behavior. Exact HEAD 86cc42f passed all three CI workflows; the complete backend suite reported 819 passing tests. This does not close criterion 30: the actual owner-controlled Android database, live process path, and device restore report are still outstanding.
 
## Gate 10 batch 7 — secret-audit false-positive remediation and exact-HEAD CI (2026-11-14)

- Audited the full-history secret-scan failure rather than suppressing it blindly. The reported finding was the public commit SHA embedded in a historical project-status metadata line, classified by Gitleaks as `generic-api-key`; the report did not establish that a credential was present.
- Added a narrow line-and-file-scoped Gitleaks allowlist for that exact metadata line. Corrected a TOML quoting/newline issue after the first remediation attempt; the failing workflow log identified the configuration parse error, and the corrected configuration was re-run.
- Exact HEAD: `462bca4342d6cb585b6b389ae5996020c4c47dd3`.
- Automated Tests #1149: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614075.
- CodeQL #507: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614165.
- Full Git History Secret Audit #88: **SUCCESS** — https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43594614104.
- The automated workflow completed frontend tests/build and source/bundle secret checks, read-only Android preflight tests, backend pytest, synthetic SQLite outbox benchmark, dependency audits, backend container build, Redis/persistent-volume smoke test, and container vulnerability scanning/report export.
- No external criterion is closed by these repository checks. Criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain open pending their exact host/device/provider evidence. No Stage 1 tick is awarded by this batch.
- Stage 1 remains **30/40 provisional = 300/400 ticks = 75% provisional**. Stage 2–6 remain **NOT SCORED**. Overall 20.90% remains a historical checkpoint only.
- No Termux package, repository, keyring, crypto dependency, runtime, production secret, paid service, or APK release was changed.


## Gate 10 — consolidated evidence packet contract (2026-11-14)

This section makes the remaining external gates executable as evidence requests. It does not mark any gate complete and awards no ticks by itself. Every packet must be redacted, tied to a date and exact software/configuration revision, and reviewed against the pass conditions below.

| Criterion | Minimum evidence packet | Pass condition | Immediate fail/defer condition |
|---:|---|---|---|
| 8 | Host/service secret-injection method; redacted service configuration; frontend bundle scan; repository-history scan; log/build-output scan | Secret values are injected only at runtime, never shipped to clients or emitted in logs/build artifacts/history | Any secret in a client artifact/log/history, or no verified host-side injection mechanism |
| 20 | No-billing Firebase project settings; redacted sign-in results; valid, expired, revoked, wrong-project token cases; entitlement-denial case; browser and Android reconnect results | All identity and authorization cases behave as designed without enabling paid billing | Billing state is unclear, a negative case is accepted, or any paid plan is required |
| 25 | Redis version/config fingerprint; certificate-validation result; ACL identity/permission test; private-bind check; persistence/restart/failure test | TLS verification and least-privilege ACLs succeed; Redis is not publicly exposed; persisted state survives the defined restart drill | Plaintext transport, disabled certificate validation, broad ACL, public bind, or lost required state |
| 30 | Actual backend process identity; effective working directory and DB-path source; redacted restore-drill JSON; source-before/after hash; fresh restore integrity and application readback | Correct live DB is positively identified; source remains unchanged; fresh restore passes integrity, FK, domain readback, and post-restore write/read/cleanup | DB path is guessed, source changes, output overwrites an existing file, or any verification fails |
| 31 | Encrypted artifact hash/format; separate key-custody location description (never the key); retention/access policy; successful restore result from encrypted artifact | Authenticated decryption and database restore succeed using a separately controlled recovery key, with no incremental cost | Key is stored beside the artifact, key is lost/unrecoverable, destination is not independently controlled, or paid storage is needed |
| 34 | Volume/mount identity; ownership and mode; write/read marker; restart result; disk-pressure/recovery result | Correct persistent volume remains mounted with restrictive permissions and data survives the required restart/recovery cases | Data resides only in ephemeral container storage, permissions are broad, or restart loses required data |
| 35 | Backend startup/health output; HTTPS certificate-chain result; failure-injection result; redacted runtime-secret source | Health check succeeds over verified HTTPS; startup fails closed when required config is absent; secrets remain backend-only | HTTP-only production exposure, invalid TLS, secrets in frontend, or paid public exposure required |
| 36 | Reverse-proxy config (redacted); WSS handshake; Firebase-authenticated subscription; unauthorized/expired-token rejection; web and Android client results | Both supported clients establish verified WSS and only authorized subscriptions succeed | Insecure transport outside local development, token in URL/logs, auth bypass, or only mocked client evidence |
| 38 | Self-hosted metrics/log config; retention limits; access-control test; disk/resource budget; sample redacted incident trace | Operational data is locally collected, bounded, access-controlled, and sustainable on existing hardware | Unbounded logs, exposed sensitive data, resource exhaustion, or paid observability dependency |
| 39 | Local alert route test; failure-to-alert and alert-delivery timestamps; incident owner/escalation/recovery runbook; recovery exercise | A no-cost alert is actually received and the documented recovery drill succeeds | Alert route is merely configured but untested, depends on paid delivery, or has no accountable recovery procedure |

### Gate evidence review rules

1. Keep raw secrets, Firebase tokens, Redis credentials, encryption passphrases, private keys, personal account data, and absolute private-storage paths out of chat, commits, screenshots, and reports.
2. A report must identify the tested environment and revision without disclosing secret values. Screenshots alone are insufficient where a machine-readable redacted result is available.
3. CI evidence may support a gate but cannot replace device/host/provider evidence explicitly required above.
4. A failed or unavailable check leaves the criterion OPEN; it does not earn partial ticks. Fix a safe repository-side defect before asking for any owner-device action.
5. No criterion may be closed by an assumed free tier, trial, local mock, synthetic fixture, or unverified network path.


## Gate 10 technical audit — source and CI reconciliation (2026-11-14)

Audited the active branch source and the successful CI run for exact HEAD `37641c43b8ca6c10f5284d4680a654796f0a5380`.

- **Criterion 8:** backend settings redact credential-bearing fields; frontend bundle scanning and full reachable Git-history scanning are in CI. This still does not prove owner-host secret injection or inspect a live host's logs/process environment. External host evidence remains required.
- **Criterion 20:** Firebase frontend observer/sign-in lifecycle and backend Admin token verification are present. Backend verification uses revocation checking and validates issuer, audience, subject and auth time; tests exercise mocked SDK boundaries. Actual project billing state, real sign-in, revocation/expiry, entitlement denial and supported-client integration remain external.
- **Criterion 25:** production config rejects non-TLS Redis and missing ACL credentials; the Redis client explicitly requires CA-chain and hostname validation. A regression test checks these client options. CI's Redis integration is not a substitute for the owner's actual private TLS Redis endpoint, ACL, persistence and restart/failure drill.
- **Criterion 30:** the restore-drill implementation checks required application tables, integrity, foreign keys, schema, row content hashes, domain readback, post-restore write/read and cleanup while preserving the source. CI tests exercise a synthetic fixture only. The actual Android application DB path and owner-device drill remain outstanding.
- **Criterion 31:** versioned AES-256-GCM backup encryption, PBKDF2-HMAC-SHA256 derivation, atomic publication and tamper/wrong-key rejection tests are present. Separate owner-controlled key custody, independent no-cost destination, retention/access controls and recovery drill are not proven by repository code.
- **Criterion 34:** CI's container smoke test passed volume ownership, non-root runtime, SQLite integrity and container restart persistence. This is meaningful container evidence, but does not establish a persistent mount on the owner's intended long-lived host/device or disk-pressure recovery there.
- **Criterion 35:** `/health` and a container healthcheck are present and the container smoke test passed. HTTPS termination, certificate lifecycle and real host startup/failure behavior remain external.
- **Criterion 36:** authenticated Firebase WebSocket handshake, entitlement checks and periodic revalidation are implemented in source. No reverse-proxy deployment or actual browser/Android WSS end-to-end evidence was found in this audit.
- **Criteria 38–39:** no deployed self-hosted monitoring/alert infrastructure or actual alert-delivery/recovery exercise was found. Application status payloads and unit tests are not operational monitoring or alert proof.

### CI evidence for audited code HEAD

- Automated Tests #43596463914: **SUCCESS**, including frontend tests/build, secret scans, Android preflight test, backend tests, dependency audit, synthetic SQLite outbox benchmark, Docker image build, persistent-volume/restart/Redis-guard smoke test, and HIGH/CRITICAL Trivy gate.
- CodeQL #43596463973: **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit #43596463929: **SUCCESS**.

These CI results apply to code HEAD `37641c43b8ca6c10f5284d4680a654796f0a5380`; documentation changes after this audit will have their own CI runs. None of these results independently closes external criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 or 39. Stage 1 scoring therefore remains 30/40 criteria = 300/400 ticks = 75% provisional.


### Audit correction — criterion 39 scope (2026-11-14)

A deeper source review of `backend/app/alerts.py`, `backend/app/alert_store.py`, and the FastAPI route registration found that the current implementation provides alert-zone validation and durable SQLite storage only. It does **not** provide an active price-crossing evaluator, a local delivery adapter, a delivery worker/scheduler, or evidence of a delivered alert. Therefore do not describe alert storage as an implemented alert-delivery path. Criterion 39 remains externally open and also has an implementation gap to scope safely before claiming an end-to-end local alert path. No paid notification channel may be introduced.


### Criterion 39 implementation increment — durable entry evaluator (2026-11-14)

The alert repository now contains an internal, transaction-safe price-zone entry evaluator and durable pending trigger-event outbox.

- Evaluates a canonical instrument's finite decimal price against active/triggered/paused zone intervals.
- Requires an initial outside/inside observation baseline; the first sample never fabricates an entry.
- Emits one event on an observed outside-to-inside transition, suppresses duplicate provider event IDs, and re-arms only after an observed exit.
- Persists per-instrument source timestamp high-water marks and rejects stale, future-skewed, and out-of-order events.
- Tracks paused zones' boundary state without triggering while paused.
- Persists trigger payload fields and `pending` delivery status for later delivery processing.
- Adds regression coverage for entry, no-repeat while inside, exit/re-entry, restart durability, duplicate IDs, stale/future/out-of-order rejection, paused behavior, instrument isolation, and invalid prices.

**Not yet complete:** the evaluator is not wired to a verified live tick/event source; no worker claims and delivers pending events; no FCM device registration, permission, sender, retry/dead-letter handling, Android background/closed-app evidence, or operational alert/recovery exercise exists. The method is internal and is not exposed through an API. Its caller must establish provider provenance and canonical identity before invoking it. Therefore criterion 39 remains open and receives no Stage 1 ticks.


### Criterion 39 implementation increment — leased delivery outbox foundation (2026-11-14)

The durable trigger outbox now supports worker-safe leasing and controlled retry state:

- Atomic batch claims use SQLite `BEGIN IMMEDIATE`; an active lease prevents a second worker from claiming the same event.
- Lease expiry permits recovery after a worker interruption; attempt counts persist across claims.
- A stale worker cannot acknowledge an event after another worker has acquired a replacement lease.
- A worker can acknowledge delivery, schedule a retry for a future nanosecond timestamp, or mark a terminal failure.
- Stored failure information is constrained to a short lowercase machine-readable error code. Raw exception text, credentials, provider response bodies and personal data are not accepted.
- Additive column migration preserves existing trigger-event rows when opening databases created before lease/retry fields existed.

**Not yet complete:** no delivery worker is scheduled or running, no local Android notification/WebSocket delivery adapter exists, and no verified live tick source is connected. The lease/retry API is a backend reliability primitive only. Criterion 39 remains open and receives no Stage 1 ticks until actual end-to-end delivery and recovery evidence exists.

### Outbox concurrency and input-boundary hardening (2026-11-14)

- Concurrent worker claims are covered by an eight-worker regression test proving a single pending event is leased to only one worker.
- Retry timestamps are bounded to SQLite's signed 64-bit integer range.
- Persisted error codes are restricted to ASCII lowercase machine-safe characters, excluding free-form Unicode text and raw exception content.
- This strengthens the internal outbox only; it does not establish a running delivery worker or delivered notification. Criterion 39 remains open.

### Criterion 39 — lease-expiry acknowledgement correction (2026-11-14)

A review of the delivery lease lifecycle found that a worker holding an expired lease could still acknowledge or reschedule an event if no replacement worker had claimed it yet. The acknowledgement and reschedule operations now require the caller's current timestamp and update only rows whose lease expiry is strictly later than that timestamp. Regression coverage checks the expiry boundary both before and after lease reclamation. This closes a stale-worker state-transition gap in the outbox primitive only; it does not provide a delivery worker or end-to-end notification. Criterion 39 remains open.


### Gate 10 audit update — CI reconciliation and backup runtime constraint (2026-11-14)

Exact audited code HEAD: `1b1db514f8250d4d833a4cd913d1f3abe4b227ee` on `phase-2/market-data-foundation`.

- Automated Tests run [43599398919](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43599398919): **IN PROGRESS** at the time of this correction; frontend/backend tests, secret scans, Android preflight, dependency audits, SQLite outbox benchmark, container build, Redis/shared-guard and persistent-volume restart smoke test, and image scan had completed; vulnerability-report export and final cleanup were still pending. Do not claim SUCCESS until the run concludes.
- CodeQL [43599398902](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43599398902): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [43599398944](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43599398944): **SUCCESS**.

**Criterion 31 correction/clarification:** source and tests confirm AES-256-GCM + PBKDF2-HMAC-SHA256 backup encryption and authenticated recovery behavior; the recovery guide already requires offline separate passphrase custody. The outstanding requirements are real owner-controlled key custody, independent zero-cost off-host destination, retention/access enforcement, and an actual restore exercise. The tested Termux Python environment lacks `cryptography`; available package candidate 48.0.1 conflicts with the declared `cryptography>=50,<51` requirement. Do not downgrade, bypass signature verification, or alter package repositories/keyrings. Device encryption acceptance remains blocked until a compatible and verifiable runtime is available.

The CI results are repository evidence only and do not close any external criterion. Stage 1 remains 30/40 criteria = 300/400 ticks = 75% provisional; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 remain OPEN. Gate 10 remains 0/10 officially closed. Stage 2–6 remain NOT SCORED; overall 20.90% remains historical only. ZERO COST remains mandatory.


### Evidence correction — latest documentation HEAD (2026-11-14)

The Automated Tests workflow referenced above was still running when inspected; the prior statement that it had completed successfully was premature and is superseded by the status recorded here. CodeQL and Full Git History Secret Audit completed successfully. The Vercel combined status is a separate account build-rate-limit failure; no paid upgrade is permitted. These statuses do not close external acceptance criteria.


### Vercel build-rate-limit investigation (2026-11-14)

GitHub combined status reports Vercel `failure` with target `upgradeToPro=build-rate-limit`. The target is not a detailed error log, so the account's exact quota counter/error code is not proven. Vercel's official limits page lists 32 Hobby deployments per hour, 100 per day, one concurrent Hobby build, and a 45-minute per-build timeout; these are separate limits (https://vercel.com/docs/limits, https://vercel.com/docs/builds/build-queues). A community report documents the same target URL alongside `api-deployments-paid-per-hour`, but that is corroboration rather than account-specific proof (https://community.vercel.com/t/check-on-github-pr-not-updating-after-build-rate-limit-failure/28030).

Most likely explanation: Vercel rejected a deployment creation because of a deployment-rate limit, not because the app source failed compilation. Exact account usage and reset window remain unknown without Vercel deployment logs/usage dashboard. No paid upgrade or hosting integration change is authorized. GitHub Actions CI remains independent. This failure does not close or reopen any Stage 1 acceptance criterion by itself.


### Gate 39 implementation increment — local operator alert reporting (2026-11-17)

A local-only operational alert reporter is now integrated into the existing opt-in alert-delivery worker.

- `backend/app/alert_operations.py` emits sanitized transition-based JSON logs for retry scheduling, terminal failure, lease loss, worker exceptions, and recovery.
- `backend/tests/test_alert_operations.py` covers deduplication, recovery, exception-message redaction, and strict counter validation.
- `backend/app/main.py` invokes the reporter from the worker loop. It uses the application logger only; no new HTTP endpoint or external notification service is added.
- Reporter output excludes owner identifiers, installation identifiers, FCM tokens, provider/event payloads, raw exception messages, and credentials.
- Automated Tests & Build on code commit `5a0c106d388b78ebb2c7821893d918879c5415da` completed **SUCCESS** (32/32 steps); backend pytest collected 1,006 tests and all passed in 28.39s. CodeQL and full-history secret audit also passed. Both Vercel preview status contexts completed successfully. These results do not replace the target-host operational acceptance evidence.
- **Repository-level local operator logging is implemented; external criterion 39 remains OPEN.** Actual host log collection, incident ownership/escalation, and a recovery exercise remain required. This does not implement end-user alert delivery; FCM remains opt-in/disabled by default and no live tick source is connected.
- No Stage 1 ticks are awarded. The complete criterion 39 acceptance boundary remains unfulfilled. Stage 1 remains 75% provisional and Gate 10 remains 0/10 formally closed.
- ZERO COST maintained: no service, subscription, provider, credential, billing change, or Termux modification.


### Gate 38 repository input-hardening increment — 2026-11-17

- `backend/app/observability.py` safely normalizes unhashable method labels, rejects boolean status codes and boolean/string/non-finite durations, handles integer-to-float overflow, and clamps finite samples to 86,400,000 ms.
- `backend/tests/test_observability.py` adds regression coverage for NaN, ±infinity, booleans, strings, unhashable labels, boolean status codes and extreme finite durations.
- The 127-series cardinality cap and existing metrics schema are unchanged.
- **External Gate 38 remains OPEN** because process-local metrics are not durable or aggregated across instances; bounded retention, self-hosted dashboard, host access controls and operational evidence remain outstanding.
- No Stage 1 ticks awarded. Gate 10 remains 0/10; Stage 1 remains 300/400 (75% provisional).


### Gate 38–39 zero-cost operations runbook — 2026-11-17

- Added [OPERATIONS_RUNBOOK_ZERO_COST.md](OPERATIONS_RUNBOOK_ZERO_COST.md) documenting the existing protected process-local metrics routes, token requirements, privacy boundaries, 127-series limit, alert event meanings, adult operator responsibilities, escalation and recovery evidence.
- The runbook explicitly says process-local metrics reset on restart and do not aggregate across instances; unit tests do not prove host collection or alert receipt.
- The current one-phone environment has no independent host or second device. No operational acceptance is claimed; Gates 38 and 39 remain OPEN.

- Exact-head verification for source commit `d32645019db6c93532666f691c43cfe87b9fa8d8`: Automated Tests & Build **32/32 steps SUCCESS**, backend **1,008 passed in 26.26s**; CodeQL and Full Git History Secret Audit **SUCCESS**; both Vercel preview status contexts **SUCCESS**. This remains repository evidence only; external Gate 38 remains OPEN.


### Batch 4 authoritative count reconciliation — 2026-11-17

The acceptance matrix is the source of truth for Gate 10 accounting. It currently lists **ten**, not four, external acceptance criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. Gate 10 remains 0/10 formally closed. Stage 1 remains 300/400 ticks = 75% provisional. No partial or repository-only ticks are awarded.


### Gate 36 deployment-context sub-check — 2026-11-17

- Latest observed isolated FastAPI POC deployment `dpl_39dRJ6Ki9gU1PrXcN8YU4kQ7zCzW` is **READY** on the Hobby team; SSO protection is enabled for all deployment targets.
- Actual build log confirms Python 3.12 from `poc/vercel_ws/.python-version` and dependency installation from `poc/vercel_ws/requirements.txt`. The expected subdirectory build context is verified.
- Project read-back omits the effective `resourceConfig.fluid` value. Although source `poc/vercel_ws/vercel.json` requests `fluid: true`, effective Fluid Compute remains unverified.
- No Gate 36 closure or Stage 1 ticks are awarded. Remaining items: maximum-duration behavior, effective Fluid Compute read-back, Android Capacitor WebView WSS, production cross-instance fan-out, and cost/operational acceptance.


### Batch 6 repository regression — 2026-11-17

A new test in `backend/tests/test_sqlite_restore_drill.py` exercises the full encrypted application backup and restore sequence using existing production-code helpers and an isolated synthetic application database. It checks exact domain counts, schema and row content, integrity, post-restore write/read/cleanup, source immutability, privacy redaction and temporary-file cleanup. Exact-head CI passed: Automated Tests & Build **32/32**, backend **1,009 passed in 36.34s**, CodeQL **SUCCESS**, and Full Git History Secret Audit **SUCCESS**. Criteria 30 and 31 remain externally OPEN.


### Batch 6 exact-head evidence — 2026-11-17

- Source commit `cfc56b7ba050201823952ea1b67dd38182dc9bfb`: Automated Tests & Build **SUCCESS (32/32)**; backend **1,009 passed in 36.34s**; CodeQL and Full Git History Secret Audit **SUCCESS**.
- FastAPI WSS POC Vercel preview status passed. Main Vite preview status was blocked by Vercel build-rate limit; no paid upgrade or repeated build attempt was made.
- This CI regression does not replace target-host backup restore or off-host key-custody acceptance. Gate 30 and 31 remain OPEN; Stage 1 remains 75% provisional.


### Batch 7 WebSocket platform-lifetime finding — 2026-11-18

Vercel documents a 300-second default and maximum Function duration on Hobby with Fluid Compute. WebSocket sessions are bound to the Function invocation and close when its maximum duration is reached. The isolated POC's own 25-second idle timeout currently prevents a passive session from reaching that platform boundary. A bounded POC-only maximum-duration test design is documented in `docs/WORK_CYCLE_2026-11-18_GATE10_BATCH7.md`; the temporary 60-second cap has not been applied. This is an architectural/test-plan clarification, not platform-close evidence. Criterion 36 remains OPEN and earns no ticks. Stage 1 remains 300/400 (75% provisional); Gate 10 remains 0/10 formally closed.


### Gate 36 — bounded synthetic lifetime probe implementation (2026-11-18)

The isolated Vercel POC now has an opt-in 330-second synthetic heartbeat probe: 10-second heartbeat cadence against the 25-second server idle timeout, with monotonic elapsed-time and WebSocket close-event logging. A regression contract test verifies the timing bounds and instrumentation. This addresses the POC's prior idle-timeout design obstacle at source level. It does not yet prove the deployed Function maximum-duration close. Gate 36 remains OPEN pending new protected deployment observation, effective Fluid Compute read-back, Android WebView acceptance, and production cross-instance fan-out/cost evidence.


Gate 36 deployment note (2026-11-18): the bounded synthetic lifetime probe now has a protected Vercel preview deployment in READY state (`dpl_EV3ScKYRdCA2X4seYFktuuoQgDx6`, source commit `08263d49ab12fd2195515d673b9e84588dcbac57`). This confirms deployment of the test harness only. The actual platform-close observation, effective Fluid Compute read-back, Android WebView acceptance and production fan-out remain open.


### CI dependency audit blocker — 2026-11-18

The current exact-HEAD Automated Tests run failed before tests/build at `npm audit` due five High findings in the dev-only transitive dependency `picomatch@4.0.7` (via `fdir`, `tinyglobby`, Vite and Vitest), GHSA-fc5q-39xc-vjpf / CVE-2026-112366. No patched picomatch version is published; upstream PR #235 closed unmerged and PR #238 remains open with a narrower scope. Do not force-downgrade Vitest, pin another known-affected picomatch version, or suppress the finding. CI remains blocked until a verified upstream release or a separately reviewed safe dependency replacement is available. This does not award ticks or close an external gate.


### CI diagnostic continuity correction — Batch 8 — 2026-11-18

The fail-fast behavior at the frontend dependency audit has been corrected without weakening the security requirement:

- `Audit frontend dependencies` has a stable step ID and `continue-on-error: true` so independent tests, build, backend checks, and image diagnostics can run even while npm reports the unresolved High advisory.
- A final `if: always()` enforcement step reads the audit step's actual outcome and exits non-zero unless the audit succeeded. The overall workflow therefore remains failed while the advisory exists.
- `backend/tests/test_ci_dependency_audit_order.py` protects this ordering and mandatory final enforcement, and asserts frontend unit tests, frontend build, backend tests, and backend image scanning are placed between the audit and final enforcement.
- The advisory itself remains open; this is not a dependency remediation. The next exact-head CI run must prove that the diagnostics now execute and that the final audit gate still fails honestly. Until that run is read back, no new CI pass is claimed and Stage 1 accounting remains unchanged.


### Vercel READY preview read-back — 2026-11-18

The Hobby plan remains active. The latest listed READY previews at read-back are WSS POC deployment `dpl_7HQmpEAPpxnvcSQFz8umK7u1kf71` from source commit `001e142d3981cea99bed5da957d266af6261b2dc` and Vite deployment `dpl_Ejcq4EaG2dWnFoeDLza8s8wqeUcB` from `9e654a842f4e320d775fd8cb3489af65eb700376`. Build logs confirm both builds completed. These are not proof of deployment of the newest Batch 8 commits and are not production releases. No extra deployment was triggered. Gate 36 remains OPEN pending actual platform lifetime, Android, fan-out, and operational acceptance.


## Follow-on repository audit — 2026-11-18

Detailed evidence: [Gate 10 Batch 9 work-cycle report](WORK_CYCLE_2026-11-18_GATE10_BATCH9.md).

The active branch received additional repository-side work after the earlier verified checkpoint:
- Gate 36 POC: Connect is locked during CONNECTING; Disconnect can cancel a pending handshake; a browser transport error no longer falsely marks the socket closed before the actual close event.
- Gate 36 regression contract: assertions cover the connecting/cancellation/error-state transitions.
- Gate 38 regression contract: added an 8-thread × 125-sample concurrency accounting test (1,000 total expected samples) and cumulative histogram bucket ordering.
- Gate 39 regression contract: added a worker-error → healthy-batch recovery transition test and verifies exception messages are not logged.

Relevant commits:
- `60c3a2123112c88d840ca57f9da9db7dc0a7f023` — WebSocket source correction.
- `254dc09e04bd3647b78d6499eb2d3703cfe34c7f` — WebSocket regression contract.
- `2146f5931eed4d134183011f5009420d9f9a2881` — metrics concurrency test.
- `265ca1948777c7ef02076c3381b597080cbcb65d` — alert recovery test.

**Execution status:** these latest regression additions have not yet been executed in a verified exact-head GitHub Actions run. Treat them as implemented/test-present, not test-passed. The prior 1,008-test result belongs to the older exact commit documented above. No latest-source WSS deployment has been confirmed.

**Gate status remains unchanged:** criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39 are OPEN; Gate 10 is 0/10 closed; Stage 1 is 300/400 = 75% provisional. Repository tests do not satisfy the external host/device/operations requirements. ZERO COST maintained; no Termux action required.


## Gate 10 Batch 11 — exact-head CI diagnosis and correction (2026-11-18)

Exact audited parent commit: `90e7c479651a415a8d68ed1c0808291dc2baffe0`.

Automated Tests run [44269828285](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44269828285) completed **FAILURE**:
- Frontend tests, build, source/bundle secret scans, Android preflight and immutable preview publisher tests passed.
- Backend pytest: **1,011 passed, 1 failed** (1,012 total).
- Failure: `tests/test_observability.py::test_request_metrics_concurrent_recording_preserves_all_samples`.
- Root cause: the test asserted cumulative histogram bucket counts in descending order. The collector correctly increments every bucket whose upper bound contains the sample, so cumulative counts must be non-decreasing.
- Batch 11 changes only the test assertion from `left >= right` to `left <= right`; no production metrics code change is required for this failure.
- The same run's frontend dependency audit reports five High findings via `picomatch@4.0.7` (GHSA-fc5q-39xc-vjpf). The final audit-enforcement step correctly failed. This is a separate outstanding dependency blocker and is not suppressed.
- Backend container build, persistent-volume smoke test and Trivy scan were not reached after pytest failed.
- Full Git History Secret Audit run [44269828220](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44269828220) was pending at last read-back.

Both Vercel previews for commit `90e7c479...` were independently read back as **READY**. This does not make CI green or close external gates.

No Gate 10 criterion is closed and no Stage 1 ticks are awarded for the correction until exact-head CI evidence passes. Stage 1 remains 300/400 = 75% provisional; Gate 10 remains 0/10 formally closed.


## Exact-head verification read-back — Batch 12 — 18 November 2026

Commit under verification: 9feb6cca8a51f563cae199eb33a6f57402eb3237.

Automated Tests run [44270272294](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272294) completed FAILURE, with the failure isolated to the required frontend dependency audit enforcement. Diagnostic continuity worked: independent checks completed rather than being skipped.

Verified successful steps:
- Frontend unit tests, production build, source and built-bundle credential scans.
- Android host preflight and immutable preview publisher contract tests.
- Backend pytest completed successfully, including the corrected cumulative histogram test and WebSocket POC tests.
- Synthetic SQLite outbox benchmark completed and its artifact was uploaded.
- Backend dependency audit passed.
- Backend Docker image build passed.
- Persistent-volume / Redis ACL smoke test passed, including restart persistence, fail-closed outage response, non-root identity, and SQLite integrity.
- Trivy container scan completed. Its uploaded JSON report contains zero HIGH and zero CRITICAL vulnerabilities across the Alpine OS and Python package targets.
- CodeQL run [44270272422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272422) passed.
- Full Git History Secret Audit run [44270272360](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44270272360) passed.

Remaining CI blocker:
- Frontend npm audit reports five High findings through dev-only transitive picomatch@4.0.7, GHSA-fc5q-39xc-vjpf / CVE-2026-112366, reached through fdir, tinyglobby, Vite and Vitest.
- The current npm registry still lists picomatch@4.0.7 as latest, while the advisory affects versions through 4.0.7 and has no published fixed version. A forced downgrade to Vite 6.2.7 would be a breaking dependency change and is not a verified patch for picomatch. No downgrade, suppression, override, or audit waiver is applied.
- The final audit-enforcement step correctly fails the workflow. Do not call the overall CI green.

Vercel preview read-back for the same source commit:
- WSS POC deployment dpl_EFLLSev63hRMKu9FEbrVTCUtR8Vg: READY.
- Frontend deployment dpl_9vazakEetH3VW4Qht3T5ymknWFdo: READY.
- WSS vercel.json explicitly sets fluid: true. This is source configuration evidence, not proof of effective runtime entitlement or a 330-second platform observation.
- The actual bounded 330-second WebSocket run and native Android WebView WSS remain unverified. Gate 36 stays OPEN.

Accounting unchanged:
- Stage 1: 300/400 ticks = 75% provisional; 30/40 provisional criteria.
- Gate 10: 0/10 formally closed.
- Open criteria: 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: NOT SCORED.
- No Stage 1 ticks or Gate closures are awarded for CI diagnostics alone.

## Batch 16 — exact-head CI + protected WSS HTTP read-back — 18 Nov 2026

**Branch head audited:** `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.

### Exact-head automated evidence

- Automated Tests [44280286764](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286764): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed in 31.94s**. Alert recovery, concurrent observability metrics, dependency-exposure, WebSocket protocol, bounded-probe contract and all other backend tests passed.
- Frontend unit tests/build, source and built-bundle credential scans, Android preflight/publisher tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke test, and Trivy scan/report steps passed.
- CodeQL [44280286768](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286768): **SUCCESS**.
- Full Git History Secret Audit [44280286699](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44280286699): **SUCCESS**.
- The only failing enforcement is still five High npm audit findings through dev-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. Do not suppress, waive, force-downgrade or call this fixed.

### WebSocket POC — protected preview read-back

- Last READY WSS preview: `dpl_C9bGENGcUpmgTFaxyyPNjg1Ehapv`, source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`.
- Protected `/health` request returned **HTTP 200** with `status=ok`, `service=dezzta-ws-poc`, `mode=synthetic-only`, `production_data_connected=false`.
- Protected root page returned **HTTP 200** and contains the 330-second probe control and 10-second heartbeat configuration.
- This proves HTTP health and page delivery only. No actual WebSocket upgrade/round-trip, owner-visible foreground 330-second observation, platform-originated 300-second close, effective Fluid Compute read-back, native Android WebView WSS or cross-instance fan-out is claimed. Gate 36 remains OPEN.

### Vercel build-rate restriction

- Exact-head Vercel commit status for `a5e90f75329c937a4ef11d560bab3b434e7f24e8`: both WSS and frontend contexts **FAILURE** with the platform `build-rate-limit` link.
- Filtered deployment lookup for exact SHA returned **zero deployment records** for both projects. Do not label this commit READY.
- Previous known READY previews remain on `72a959f375f7c1e999be25e73e5fd00fdc24abb0`. Existing READY previews were not changed; no redeploy retry loop, paid upgrade, billing activation or SSO weakening was performed.
- Team usage counters and exact reset time were not exposed by the available read-back; no quota remainder or reset estimate is invented.

### Stage 1 accounting — unchanged

- Stage 1: **300/400 ticks = 75% provisional; 30/40 criteria**.
- Gate 10: **0/10 formally closed**.
- Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- No score awarded for a passing test suite, documentation, or HTTP-only WSS checks without the external acceptance evidence.


## Batch 17 — branch-head and provider-blocker reconciliation — 18 Nov 2026

**Audited branch head:** `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a` (commit message: `docs: consolidate Batch 16 CI and WebSocket evidence`).
**Parent:** `a5e90f75329c937a4ef11d560bab3b434e7f24e8`.
**Audit method:** GitHub branch ref, exact commit status/check-runs, workflow job logs, and Vercel deployment records filtered by exact SHA.
**Cost:** ZERO COST. No Termux, no paid plan, no billing change, no production promotion, no SSO weakening.

### Exact branch-head evidence

- GitHub Actions run [44281595750](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595750) — Test and Build: **FAILURE at final frontend dependency-audit enforcement**.
- The job reached and completed all earlier test/build/security/container steps. The final step reports `AUDIT_OUTCOME=failure` and exits 1 by design.
- CodeQL run [44281595873](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595873): both Python and JavaScript/TypeScript analysis jobs **SUCCESS**.
- Full reachable Git history scan run [44281595869](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44281595869): **SUCCESS**.
- The exact-head GitHub status has two Vercel contexts, both FAILURE with the provider message: **“Deployment rate limited — retry in 24 hours.”**
- Exact-SHA deployment queries returned **zero deployment records** for both WSS POC and frontend projects. Therefore `fabf2c63fa8df13dc42da3afdbc6ed45682a4a3a` is **not deployed**.

### Vercel blocker — isolated and contained

This is a provider-side deployment/build-rate restriction, not an application compile error. No retry loop was started. No paid upgrade, billing activation, or SSO bypass was attempted. The latest previously observed READY previews are tied to source `72a959f375f7c1e999be25e73e5fd00fdc24abb0`, not the audited branch head. Those preview records do not certify the branch head.

No exact usage counter or reset timestamp was available. The provider status string says retry in 24 hours; no more precise remaining-time estimate is asserted.

### Dependency audit blocker — enforcement retained

The workflow's final enforcement is the sole Test and Build failure. The audit outcome is still failure for the five High findings through development-only `picomatch@4.0.7` / GHSA-fc5q-39xc-vjpf. The development-only boundary regression is mitigation, not a fix. No unmerged patch, forced downgrade, override, suppression, waiver, or production-only audit substitution was applied.

### WebSocket acceptance — honest boundary

The latest previously recorded protected preview returned HTTP 200 for health and page delivery in synthetic-only mode. This is HTTP verification only. It is not a WebSocket upgrade, echo/round-trip, 330-second foreground observation, platform-originated duration close, Android WebView test, effective Fluid Compute read-back, or cross-instance fan-out proof. Gate 36 remains OPEN.

### Gate 10 action register

| Criterion | Immediate zero-cost work possible | Evidence still required |
|---:|---|---|
| 8 | Keep source/bundle/history scans and secret boundary tests enforced | Owner-controlled secret injection and runtime/log/artifact leakage proof |
| 20 | Preserve authorization/revocation regression tests | Real identity/revocation/entitlement acceptance on approved zero-cost setup |
| 25 | Keep Redis ACL/TLS and persistence CI tests | Owner-controlled existing Redis endpoint and real restart/failure proof |
| 30 | Keep encrypted snapshot/decrypt/restore integration tests | Restore drill against a fresh owner target and post-restore integrity/write checks |
| 31 | Keep encrypted backup/recovery controls | Off-host copy, separately controlled key, retention policy and restore drill |
| 34 | Keep persistent-volume smoke test | Existing-host mount, permissions, disk-pressure and restart durability proof |
| 35 | Keep container/health/fail-closed checks | Existing-host HTTPS/certificate and runtime secret-source evidence |
| 36 | Keep synthetic lifecycle/probe contract tests; no false duration claims | Foreground 330s run, platform close attribution, Fluid setting, Android WebView, fan-out |
| 38 | Keep concurrency/input-hardening tests | Durable aggregation, retention, host access controls and dashboard acceptance |
| 39 | Keep sanitized alert/recovery tests and runbook | Persistent alert, named escalation owner and completed recovery drill |

**Scoring unchanged:** Stage 1 **300/400 ticks = 75% provisional; 30/40 criteria**. Gate 10 **0/10 closed**. Open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 **NOT SCORED**. No progress credit for documentation-only work or provider-blocked deployments.


## Batch 18 — exact-head CI, WSS HTTP verification, and overall-progress accounting — 18 Nov 2026

**Audited source head:** `64f348cebccbfb3fad2b9efe5a066d28962970f6` (Batch 17 documentation reconciliation). **Branch:** `phase-2/market-data-foundation`. **Main:** untouched. **Cost:** zero. No Termux, no billing, no paid services, no production promotion.

### Exact-head CI outcome

- Automated Tests run [44287587066](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587066): **FAILURE only at final frontend dependency-audit enforcement**.
- Backend pytest: **1,014 passed**. Frontend unit tests/build, source and built-bundle credential scans, Android preflight/publisher tests, synthetic SQLite outbox benchmark, backend dependency audit, backend container build, Redis/persistent-volume smoke test and Trivy scan/report all **PASS**.
- The final enforcement step fails because npm audit outcome is failure: **five High findings through development-only `picomatch@4.0.7`**. The failure is intentional and no vulnerability was suppressed.
- CodeQL run [44287587070](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587070): Python and JavaScript/TypeScript jobs **SUCCESS**.
- Full history scan run [44287587073](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44287587073) was requested in the prior read-back but its run ID was not valid; therefore this batch does **not** claim a new history-audit result. Earlier passing history scans remain historical evidence only.

### Vercel exact-head deployment

Both projects have READY deployments for this exact source SHA:
- WSS POC deployment `dpl_8iPQZm1Z2QJ4Dc8hjUPgSsPanPYb`, URL [protected preview](https://dezzta-chart-ws-arfnel7l9-deszztagd377-pixel.vercel.app).
- Frontend deployment `dpl_FqhfGebn7fU6f7udkPFmByyG1WTY`, URL [protected preview](https://dezzta-chart-ekpqshhr4-deszztagd377-pixel.vercel.app).

The previously observed build-rate-limit blocker is therefore no longer active for this commit. No paid upgrade, billing activation, SSO weakening, or production promotion occurred.

### WebSocket POC — verified scope

Protected WSS preview `/health` returned **HTTP 200** with `status=ok`, `service=dezzta-ws-poc`, `mode=synthetic-only`, and `production_data_connected=false`. The protected root page returned **HTTP 200** and serves the browser WebSocket client, including its explicit Connect, Disconnect, synthetic ping, and bounded 330-second probe controls.

This is HTTP health and page-delivery evidence only. The available HTTP fetch interface cannot perform or observe a real WebSocket protocol upgrade, so this batch does not claim a WSS handshake, ping/pong round-trip, foreground 330-second run, Vercel-originated duration close, Android WebView result, effective Fluid Compute read-back, or cross-instance fan-out. Gate 36 remains OPEN.

### Overall-project progress — corrected accounting

The approved progress specification explicitly says the M1–M8 weighted ledger is **not approved and not scored criterion-by-criterion**. Therefore a fresh overall-project percentage cannot be calculated without inventing weights or credit. The most recent owner-confirmed historical overall checkpoint is **20.9%**, and it must be labeled **HISTORICAL — NOT RECOMPUTED**. Do not present 20.9% as a current verified percentage.

The six official stages remain:
- Stage 1: **75% provisional** (300/400 ticks; 30/40 criteria); Gate 10 **0/10 formally closed**.
- Stages 2–6: **NOT SCORED**. Preparatory code does not count as officially opened stage progress.
- Overall project: **CURRENT % NOT ESTABLISHED**; historical reference **20.9%** only.

Formula remains pending owner-approved M1–M8 weights and criterion-to-deliverable mapping: `overall = Σ(weight × verified completion fraction)`. Duplicate credit is prohibited.

### Gate 10 status

Still open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. No new external acceptance evidence in this cycle closes any of these criteria. Stage 1 remains 75% provisional; Gate 10 remains 0/10 closed.


## Batch 19 — executable WebSocket protocol contract and corrected progress accounting — 18 Nov 2026

### WebSocket protocol regression coverage added

Added `backend/tests/test_vercel_ws_protocol.py`. It imports the isolated synthetic POC application by its repository path and uses FastAPI/Starlette TestClient to exercise the ASGI WebSocket protocol, not just source-text patterns. Coverage includes:

1. WebSocket handshake, ready message and ping/pong round-trip with matching session ID and sequence.
2. Invalid-message error followed by close code 1003.
3. Oversized-message error followed by close code 1009.
4. Twelve-message/ten-second rate boundary and rate-limited close code 1013 on the next message.
5. HTTP health response explicitly declaring `synthetic-only` and `production_data_connected=false`.

**Evidence boundary:** these are executable in-process ASGI protocol tests. They do not prove public Vercel WSS upgrade, browser behavior, 330-second platform lifetime, Android WebView, Fluid Compute effective settings, or multi-instance fan-out. Gate 36 remains OPEN until those external observations exist.

### CI checkpoint before Batch 19 commit

- Latest branch CI run [44288721128](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721128) was still running at read-back; frontend tests/build, source and bundle credential scans, Android preflight/publisher tests, backend pytest (PASS), synthetic outbox benchmark, backend dependency audit had passed; backend image build was in progress. Do not claim this run complete.
- CodeQL run [44288721099](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721099): SUCCESS.
- Full Git History Secret Audit run [44288721127](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44288721127): SUCCESS.
- Vercel commit status for `362ff6e`: both WSS POC and frontend report **Deployment rate limited — retry in 24 hours**. No retry loops, plan upgrade, billing or SSO change.

### Dependency blocker — confirmed path and safe decision

The root lockfile contains `picomatch@4.0.7` as `dev: true`, with transitive parents `tinyglobby@0.2.17`, `vite@6.4.5`, and `vitest@4.1.12`, all also development-only. The GitHub Advisory [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) still reports High severity, affected through 4.0.7, and no patched version. Upstream issue [#247](https://github.com/micromatch/picomatch/issues/247) remains open in the latest read. No reviewed/released fix is available to justify a lockfile override. Do not downgrade to 4.0.4: that release addressed a different earlier advisory, not this later single-branch extglob finding. Keep npm audit enforcement fail-closed; dev-only status is exposure reduction, not remediation.

### Progress accounting

- Stage 1: **75% provisional**, 300/400 ticks, 30/40 provisional criteria.
- Gate 10: **0/10 formally closed**; open criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stages 2–6: **NOT SCORED**.
- Overall current project percentage: **NOT ESTABLISHED** because M1–M8 weights and criterion mapping are not approved/scored. Historical 20.9% is retained only as a historical checkpoint, not presented as current.

No Gate 10 closure or Stage 1 tick increase is awarded from adding tests alone. No Termux required. Zero-cost constraints maintained. `main` untouched.


## Batch 62J-14 — 2026-11-19 exact-head WebSocket handoff update

- Exact source HEAD before this batch: 1246ec19585faabb6754f83e59d14fc8a4361a56. Automated Tests, CodeQL and Full Git History Secret Audit all SUCCESS (runs 44562762820, 44562762581, 44562762579).
- Main source-SQLite WebSocket reconnect route now delegates queue merge/resequence to the separately tested OhlcvStreamHub.merge_replay_boundary() helper.
- The route sends replay_complete only after successful handoff; failure emits sanitized resnapshot_required and closes with 1013.
- This is a source-route correctness improvement, not replica-backed Redis startup integration or public WSS acceptance.
- Gate 10 remains 0/10 formally closed; Stage 1 remains 75% provisional (30/40 criteria; 300/400 ticks). No score increase.


## Verified repository checkpoint — 2026-11-20 — Batch 62J-14

- Exact branch HEAD: `407d2b38882e92cdf6db5b7df6c44350b6cd746d`.
- Automated Tests [44564212673](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44564212673): **SUCCESS**; backend **1,153 passed in 27.93s**, frontend **236 passed / 28 test files**, build, frontend secret scans, Android preflight/publisher tests, backend dependency audit, synthetic outbox benchmark, backend container build, Redis/persistent-volume smoke, Trivy report and frontend dependency-audit enforcement all passed.
- CodeQL [44564212707](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44564212707): **SUCCESS** for Python and JavaScript/TypeScript.
- Full Git History Secret Audit [44564212714](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44564212714): **SUCCESS**.
- Batch 62J-14 source-SQLite WebSocket reconnect path uses the tested `merge_replay_boundary()`; replay completion is emitted only after merge success, and handoff failure fails closed with `resnapshot_required` / close 1013.
- Redis replica runtime remains intentionally not startup-wired. Gate 25 still requires owner-controlled credentials, TLS, target multi-instance behavior and operational recovery proof. CI is not a substitute for those external checks.
- No deployment, paid service, production secret/ACL mutation or Termux operation.
- Accounting: Stage 1 **300/400 = 75% provisional** (30/40 criteria); Gate 10 **0/10 formally closed**; open **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**. Stages 2–6 unscored; overall weighted project percentage unestablished.


## Batch 62J-44 — criterion 38 source hardening update (2026-11-20)

The repository collector's per-series scalar accumulators now have explicit saturation limits in addition to the existing 127-series cardinality limit. Request counters, histogram counts and bucket counts saturate at 2^53−1, preserving exact JSON integer representation. Accumulated duration saturates at 86,400,000 × (2^53−1) milliseconds, derived from the existing one-day per-sample duration ceiling. A regression test exercises the saturation boundary. Source commit: 040c479bb01fd3d6d8f293aab7831164343ecac8. Test commit/latest source-test HEAD: a6acf605a44fe356602f92e8bc8e31d1f8e547b6. Exact-head CI is pending; no test-pass claim is made.

This does not change criterion 38's external status: host-side collection, bounded log retention/rotation, dashboard access, disk-pressure recovery and real secret-redaction evidence remain required. No Stage 1 tick is awarded. Stage 1 remains 30/40 = 75% provisional; open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. ZERO COST maintained; no deployment, paid service, Termux or device operation.
\n\n## Batch 62J-45 — Gate 30 owner-host drill preparation — 2026-11-20\n\n- Added `docs/GATE30_OWNER_HOST_RESTORE_DRILL_RUNBOOK.md`.\n- Audited the existing restore drill, SQLite Online Backup helper, runtime database-path configuration and its 12 named regression tests. The drill already checks source read-only behavior, fresh-path no-overwrite publication, SQLite integrity, foreign keys, required application tables, typed per-table row hashes, schema hashes, domain-store readback, outbox identity/cursor uniqueness and committed write/fresh-read/cleanup.\n- Runtime database selection is `INSTRUMENT_REGISTRY_DB_PATH`, falling back to `./data/instrument_registry.sqlite3` relative to the backend process working directory. Repository source cannot prove the live injected path or host.\n- Runbook capacity threshold: `3 × S + max(64 MiB, 10% of 3 × S)` additional free space, where S is the source DB file size.\n- Owner-host execution is not performed. Termux on a client phone is not a substitute if the backend database resides on a separate host.\n- **Gate 30 remains OPEN; no Stage 1 tick is awarded.**\n

## Batch 72 exact-head CI closure — 25 November 2026

**Audited commit:** `a342a2abe8f70315445343e123e661ea37c52050` on `phase-2/market-data-foundation`. All four required workflows are now terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45599485761 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45599485734 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45599485776 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45599485759 | 🟢 SUCCESS | 6/6 |

Automated Tests log confirms **1,426 passed, 1 skipped, 6 warnings in 59.44 seconds**. The skipped test is the isolated Redis TLS integration fixture because it is not configured. Therefore this is not owner-host Redis TLS acceptance. Container smoke checks passed for health, Redis ACL/AOF persistence across restart, fail-closed API response during Redis outage, backend reconnect, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection. OCI ARM64, CodeQL and full-history secret audit passed. No failure was recorded.

**Evidence boundary:** these are GitHub CI results only. They do not prove a live Cloudflare deployment, public WSS, Firebase identity, real market-data provider, owner-host Redis TLS, Android/browser production lifecycle, or production snapshot transfer/ACK. The CI success does not change Stage 1 30/40 provisional or Gate 10 0/10. Indicator implementation status and completion credit are unchanged.


## Batch 73 exact-head CI closure and dedicated Redis TLS acceptance — 25 November 2026

**Audited commit:** `c3effcd4f48f03ef9cbe28edf59787ed74f4bc88` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45601263082 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45601263013 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45601262998 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45601263240 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 48.77 seconds**. In addition, the dedicated TLS step generated an ephemeral test CA, trusted server certificate for DNS:localhost, wrong CA and a TLS-only Redis listener; it ran `tests/test_shared_guard_tls_integration.py` separately and the result was **1 passed in 0.07s**. That test verified successful CA/hostname validation and ACL-backed shared-guard operations, rejection of wrong hostname, untrusted CA and plaintext downgrade. The same TLS listener then proved AOF data, TLS-only listener and ACL survived a real container restart. The later general pytest run reports the TLS test skipped because its short-lived fixture variables are intentionally scoped to the preceding dedicated step; this does not negate the dedicated 1/1 pass.

The same run also passed frontend tests/build and secret scanning, Cloudflare synthetic proof tests, Durable Object runtime tests, backend dependency audit, synthetic SQLite outbox and metrics benchmarks, backend container build, container smoke tests and container vulnerability scan. CodeQL, native ARM64 and full reachable-history secret audit passed. No CI failure was recorded.

**Evidence boundary remains:** isolated CI Redis TLS acceptance is not owner-host Redis TLS deployment acceptance. CI still does not prove production Cloudflare deployment, public WSS, Firebase identity/entitlement, live provider rights/data, production snapshot transfer/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10 formally closed. Indicator completion credit unchanged.


## Batch 74 exact-head CI closure — 25 November 2026

**Audited commit:** `9671ce0b9c1c54b1127fe55a03e5008611c6fc2e` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45602155645 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45602155744 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45602155670 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45602155558 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 48.66 seconds**. Dedicated Redis TLS integration: **1 passed in 0.07 seconds** using an ephemeral CA, DNS:localhost certificate, wrong CA and TLS-only Redis listener. Wrong-hostname, untrusted-CA and plaintext downgrade cases were rejected; authenticated shared-guard operations succeeded. Redis AOF data, TLS-only listener and ACL survived an actual container restart. The later general suite's one skip is expected because the temporary TLS fixture variables are scoped to the dedicated preceding step. Container health, fail-closed Redis outage/reconnect, non-root UID/GID, mounted-volume ownership, SQLite integrity/restart persistence and HTTP rate-limit smoke checks passed. Frontend tests/build/secret scan, Cloudflare synthetic Worker/DO runtime tests, backend dependency audit, synthetic SQLite benchmarks, backend container build and vulnerability scan passed.

This CI success does not prove owner-host TLS, production Cloudflare deployment/public WSS, Firebase identity, live provider rights/data, production snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator status and completion credit are unchanged.


## Batch 75 exact-head CI closure — 25 November 2026

**Audited commit:** `fd200b617a87d04693a08d04be26ad4991a0f978` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45603007729 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45603007940 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45603007601 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45603008057 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 71.47 seconds**. Dedicated Redis TLS integration: **1 passed in 0.11 seconds**. Ephemeral CA/server certificate/TLS-only Redis fixture verified trusted CA + DNS hostname, ACL-backed shared-guard operations, rejection of wrong hostname, untrusted CA and plaintext downgrade; AOF data, TLS-only listener and ACL survived an actual container restart. The later general pytest invocation skips the TLS test because fixture environment variables are intentionally scoped to the preceding dedicated step. Backend container health/outage/reconnect, non-root runtime, persistent volume, SQLite integrity/restart and rate-limit smoke checks passed. Frontend tests/build/secret scan, Cloudflare synthetic Worker/DO tests, dependency audit, synthetic SQLite benchmarks, image build/scan, CodeQL, ARM64 and full-history secret audit passed.

Evidence remains CI-only: not owner-host TLS acceptance, production Cloudflare deployment/public WSS, Firebase identity, live provider rights/data, production snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator completion credit unchanged.


## Batch 76 exact-head CI closure — 25 November 2026

**Audited source commit:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` on `phase-2/market-data-foundation`. All four workflows are terminal SUCCESS on this exact SHA:

| Workflow | Run | Result | Job steps |
|---|---:|---|---:|
| Automated Tests | 45604020771 | 🟢 SUCCESS | 41/41 |
| CodeQL Security Analysis | 45604020613 | 🟢 SUCCESS | Python 8/8 + JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45604020280 | 🟢 SUCCESS | 7/7 |
| Full Git History Secret Audit | 45604020286 | 🟢 SUCCESS | 6/6 |

Automated suite: **1,426 passed, 1 skipped, 6 warnings in 57.78 seconds**. Dedicated Redis TLS integration: **1 passed in 0.08 seconds**. It used an ephemeral CA, DNS:localhost certificate and TLS-only Redis listener; trusted CA/hostname and ACL-backed shared-guard operations passed; wrong hostname, untrusted CA and plaintext downgrade were rejected. AOF data, TLS-only listener and ACL survived a real Redis container restart. The general pytest suite's one skip is expected because fixture variables are scoped to the dedicated preceding step. Backend container smoke tests, frontend build/tests/secret scan, Cloudflare synthetic Worker/DO tests, backend dependency audit, synthetic SQLite benchmarks, container vulnerability scan, CodeQL, ARM64 and full-history secret audit all passed.

This is CI evidence only. It does not prove owner-host TLS, production Cloudflare deployment/public WSS, Firebase identity/entitlement, live provider rights/data, production signed snapshot/receipt ACK, or Android/browser production lifecycle. Stage 1 remains 30/40 provisional; Gate 10 remains 0/10. Indicator completion credit unchanged.

The following documentation-only reconciliation commit does not change runtime/source files; CI is not rerun for that documentation-only commit because the exact source tree above already passed all four workflows.


---

## STAGE 1 ACCEPTANCE MATRIX — Batch 78 reconciliation (25 November 2026)

**Active branch:** `phase-2/market-data-foundation`  
**Documentation HEAD before Batch 78:** `fb4fb9843535b0dae1cc733d65df9de653dd88ba`  
**Last source/test SHA:** `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`  
**Batch 78 report:** [Recovery, monitoring and five-batch reconciliation](WORK_CYCLE_2026-11-25_BATCH78_RECOVERY_MONITORING_RECONCILIATION.md)

Batches 74–77 already existed and are reconciled; they are not reimplemented. Exact-source CI recorded by Batch 77: Automated Tests 41/41 (1,426 passed, 1 skipped, 6 warnings), CodeQL 16/16, OCI ARM64 7/7, Secret Audit 6/6; dedicated Redis TLS integration 1 passed. The subsequent branch commits are documentation-only and marked `[skip ci]`; no new source CI run is claimed for them.

**Stage dashboard:** Stage 1 official active, 30/40 = 75% provisional 🟨; Gate 10 = 0/10 formally closed 🟨 (criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39). Stage 2 🟦 preparatory only; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project, aggregate indicator completion and IP3S remain ⚪ NOT SCORED because no approved weighted denominator exists.

**WebSocket/Gate 25:** production WSS, Firebase identity/entitlement, lawful zero-cost provider provenance, production ticket issuance, signed snapshot transfer, authenticated persisted receipt retrieval, durable per-gateway high-water ACK/fencing/restart reconciliation and public browser/Android E2E remain OPEN. Redis `XTRIM`, `XDEL` and consumer-group destruction remain BLOCKED until durable gateway ACK acceptance. Cloudflare Worker/DO remains synthetic-only; no production resources were created. The connected account inventory is empty, while the user has separately stated the project server is on Cloudflare; do not infer that the connected account is the hosting account or create duplicate infrastructure.

**Recovery/monitoring:** CI verifies container-scope health, Redis ACL/AOF restart, outage fail-closed/reconnect, non-root execution, volume ownership smoke, SQLite integrity/restart, rate limiting and isolated TLS. Owner-host secret/volume/DB restore/off-host encrypted backup, independent alert/incident drill, production WSS and device recovery remain unaccepted.

**Indicators:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 FOUNDATION; Footprint PRO 2GD 🟨 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟨 OPEN. Focused declarations remain 28 (21 calculation + 7 hook), not completion. No indicator source/UI change and no completion credit in Batch 78. `CandlestickChart.tsx` integration remains absent. Preserve warm-up nulls, prefix causality, no lookahead/repaint, exact timestamp alignment and Footprint OFF normal candle spacing.

**Controls:** ZERO COST; `main` untouched; Vercel deferred; no paid data/hosting/monitoring/backup; no production deployment; delivery target around 24 December 2026.


---

## Batch 80–86 unified runtime and acceptance work package (25 November 2026)

Authoritative work package: [WORK_CYCLE_2026-11-25_BATCH80_86_UNIFIED_RUNTIME_AND_ACCEPTANCE_PLAN.md](WORK_CYCLE_2026-11-25_BATCH80_86_UNIFIED_RUNTIME_AND_ACCEPTANCE_PLAN.md). Starting HEAD: `fd756cee2bf3e427a628c3089c37d07d9f75ada7`; source/test baseline: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`.

**Scope/accuracy:** this package is the detailed engineering blueprint and acceptance matrix for Batches 80–86. It does not claim runtime implementation, production deployment, public WSS, owner-host verification, or indicator completion. No source code, secrets, production data, Cloudflare resources, or deployments were changed. The major runtime composition review gate remains in force; implementation is sequenced after the scoped blueprint review. This preserves the user's no-broken-code requirement.

**Batch sequence:** 80 strict source/gateway role config and fail-closed validation; 81 source publisher factory and signed snapshot/checkpoint startup; 82 gateway replica factory with owner-pinned Ed25519 verification and install-before-Redis; 83 real Redis two-gateway process/restart/fault tests; 84 immutable per-gateway durable receipt and monotonic high-water ACK; 85 existing Cloudflare route/origin mapping and public WSS/browser/Android acceptance; 86 zero-cost recovery, monitoring, backup/restore and incident acceptance. Full test matrices, security boundaries, startup/shutdown rules, Redis ACL boundaries, and acceptance gates are in the linked package.

**Critical safeguards:** source and gateway remain separate app roles; no shared DB; gateway never receives source private key; Redis destructive `XTRIM`, `XDEL`, and consumer-group destruction remain blocked until every required gateway has an owner-accepted durable high-water ACK and restart reconciliation proof. XACK/local applied cursor are not owner acceptance. Do not create duplicate Cloudflare resources or introduce paid providers.

**Engineering parameter review:** current defaults observed in source are publisher lease 30,000 ms, publisher batch 100, consumer pending-idle 30,000 ms, consumer batch 100, gateway lease 15,000 ms with 5,000 ms default renewal, WebSocket ticket TTL 90 seconds, entitlement recheck 60 seconds. These are existing defaults, not production SLOs; validate against measured p99 latency, host scheduling and Redis RTT before acceptance.

**CI:** source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has prior exact-source evidence: Automated Tests 41/41, 1,426 passed, 1 skipped, 6 warnings; CodeQL 16/16; OCI ARM64 7/7; Secret Audit 6/6; dedicated Redis TLS 1 passed. Current documentation HEAD `fd756cee2bf3e427a628c3089c37d07d9f75ada7` is 12 commits ahead, zero behind, documentation-only by compare; no new source CI is claimed. The documentation commit uses `[skip ci]` and has no run/status. Previously recorded source jobs are terminal success; no running jobs left.

**Progress unchanged:** Stage 1 30/40 = 75% provisional 🟨; Gate 10 0/10 closed 🔴 (8, 20, 25, 30, 31, 34, 35, 36, 38, 39); Stage 2 🟦 preparatory; Stage 3 ⚪ not scored; Stage 4 🟪 gated; Stages 5–6 ⚪ not scored. Overall project/IP3S ⚪ NOT SCORED. WebSocket runtime, Gate 25 durable ACK, public Cloudflare WSS/device E2E and owner-host recovery remain 🔴 OPEN.

**Indicator ledger unchanged:** SMA20, EMA20, RSI14 Wilder, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook 🟨 FOUNDATION; Footprint PRO 2GD 🟨 GATED; Volume Profile, Complete Volume Profile, Movable-range VP, Heatmap and Liquidation Maps 🔴 OPEN. 28 focused declarations (21 calculation + 7 hook) are not a completion percentage. No indicator source/UI changes. Keep warm-up nulls, prefix causality, no lookahead/repaint, timestamp alignment, stale-output clearing and no calculations on unavailable/demo/error/empty snapshots. Footprint OFF remains normal spacing; Footprint ON alone uses spaced clusters. Footprint references are available; Heatmap reference is still required before visual work.

Controls: ZERO COST; `main` untouched; Vercel deferred; no new/duplicate Cloudflare resources; no paid data/hosting/monitoring/backup; delivery target around 24 December 2026.


---

## Batch 80 — strict runtime role and fail-closed app binding (25 November 2026)

**Status: IMPLEMENTED + VERIFIED 🟩.** This is a bounded Batch 80 completion, not a claim that the complete source/gateway production relay is deployed.

### Implemented controls

- OHLCV_REDIS_ROLE must explicitly be source or gateway whenever OHLCV_REDIS_ENABLED=true; missing, unknown, or mismatched roles fail closed.
- create_app() validates that the declared role has its matching injected factory: source requires publisher_runtime_factory; gateway requires replica_runtime_factory. A crossed factory or enabled relay with no injected factory is rejected before application startup.
- Source and gateway factories remain mutually exclusive.
- Source and replica SQLite database targets must be absolute file paths; relative paths, symbolic-link targets, and directory targets are rejected.
- backend/.env.example now documents the role selector. Relay remains disabled by default.
- Added focused tests for missing/invalid/mismatched roles, factory-role binding, fail-closed app creation, absolute database paths, directories and symlinks.

### Changed files

- backend/app/ohlcv_redis_config.py
- backend/app/ohlcv_redis_runtime.py
- backend/app/ohlcv_redis_gateway_runtime.py
- backend/app/main.py
- backend/tests/test_ohlcv_redis_config.py
- backend/tests/test_ohlcv_redis_runtime.py
- backend/tests/test_ohlcv_redis_gateway_runtime.py
- backend/tests/test_ohlcv_redis_publisher_lifecycle.py
- backend/.env.example

### Exact verification — final source commit

Commit: 66d4c6a812d5ce2570345e1108e813b5067f5248

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [2457](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188191) | 🟩 41/41 steps; 1,433 passed, 1 skipped, 6 warnings |
| CodeQL Python | [1814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | 🟩 8/8 |
| CodeQL JavaScript/TypeScript | [1814](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188170) | 🟩 8/8 |
| Full Git History Secret Audit | [1396](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188184) | 🟩 6/6 |
| OCI ARM64 Image Readiness | [443](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45612188277) | 🟩 7/7 |

Automated Tests also completed the Redis TLS fixture step, backend dependency audit, backend container build, container smoke test with shared Redis guard/persistent volume, and container scan. All four workflows are terminal success; no CI job remains running. An earlier run exposed one legacy gateway fixture missing the new role; that fixture was corrected before the final successful run.

### Boundary — what is still not complete

The module-level production ASGI app does not invent owner-specific snapshot callbacks. Source publisher activation still requires an owner-provided snapshot_verifier that verifies the exact snapshot and every required gateway's durable installation receipt. Gateway activation still requires an authenticated snapshot_installer and owner-pinned Ed25519 trust keys. These callbacks are not guessed or fabricated. Therefore production publisher/gateway runtime wiring, Gate 25 owner-accepted durable high-water ACK, public Cloudflare WSS, browser/Android E2E and owner-host recovery remain 🔴 OPEN. No production deployment or Cloudflare resource was changed.

### Next ordered work

1. **Batch 81:** source publisher runtime integration, contingent on the authoritative owner snapshot-verifier and durable gateway-receipt source.
2. **Batch 82:** gateway replica runtime integration, contingent on the authenticated snapshot-transfer/install callback and owner-pinned key configuration.
3. **Batch 83:** two-gateway Redis process/restart/fencing/fault acceptance.
4. **Batch 84:** durable owner-accepted high-water ACK and restart reconciliation.
5. **Batch 85:** existing Cloudflare route/origin plus public WSS/browser/Android acceptance.
6. **Batch 86:** owner-host backup/restore, local observability and incident drills.

Do not trim/delete Redis stream entries or destroy consumer groups until every required gateway has a durable owner-accepted high-water ACK and restart reconciliation proof.

### Project and indicator progress — no percentage inflation

- Stage 1: **30/40 = 75% provisional 🟨** (unchanged; Batch 80 does not auto-close Stage 1 criteria).
- Gate 10: **0/10 formally closed 🔴**; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 2: 🟦 preparatory, not officially entered/scored.
- Stage 3: ⚪ not scored.
- Stage 4: 🟪 gated.
- Stages 5–6: ⚪ not scored.
- Overall project: ⚪ NOT SCORED; approved weighted denominator is still absent.
- Significant project index/IP3S: ⚪ NOT SCORED for the same reason.

### Complete indicator ledger — source/UI unchanged in Batch 80

| Indicator | Status | Current implementation/evidence | Mathematical/acceptance boundary |
|---|---|---|---|
| SMA20 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; arithmetic mean of 20 closes |
| EMA20 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; alpha 2/21; recursive seed contract tested |
| RSI14 Wilder | 🟨 FOUNDATION | Calculation foundation only | First valid index 14; Wilder smoothing; no divide-by-zero NaN leak |
| MACD12/26/9 | 🟨 FOUNDATION | Calculation foundation only | MACD line first valid index 25; signal and histogram index 33 |
| Bollinger20,2 | 🟨 FOUNDATION | Calculation foundation only | First valid index 19; population standard deviation per current contract |
| Shared Indicator Hook | 🟨 FOUNDATION | 7 focused declarations | Chart integration into CandlestickChart.tsx remains open |
| Footprint PRO 2GD | 🟨 GATED | Synthetic/offline accumulator only | Visual work must match both saved Footprint references; OFF keeps normal candle spacing, ON alone enables spaced clusters |
| Volume Profile | 🟨 OPEN | Not accepted | Price-bin volume conservation, range semantics and timestamp boundaries |
| Complete Volume Profile | 🟨 OPEN | Not accepted | Full-session completeness, POC/VA derivation and conservation |
| Movable-range Volume Profile | 🟨 OPEN | Not accepted | User-selected range bounds and deterministic recomputation |
| Heatmap | 🟨 OPEN | Visual implementation not started | Must wait for the user's Heatmap reference image |
| Liquidation Maps | 🟨 OPEN | Not accepted | Data provenance and methodology remain unapproved |

Focused declaration inventory remains **28 total = 21 calculation + 7 shared-hook declarations**. This is not an indicator completion percentage or count of accepted indicators. Batch 80 changed no indicator calculation or chart UI; indicator progress credit is therefore unchanged.

Cross-indicator acceptance remains mandatory: warm-up values null until mathematically valid; prefix causality; no future-candle lookahead/repaint; exact timestamp/series identity alignment; stale-output clearing on identity change; deterministic repeated results; bounded computation; no mutation of source candle data; no calculations for demo/loading/unavailable/error/empty snapshots.

**Controls:** ZERO COST; active branch only phase-2/market-data-foundation; main untouched; no Vercel; no paid market data, hosting, monitoring, backup, subscription or publication; no duplicate Cloudflare infrastructure. Planning target remains around **24 December 2026**.

---

# Work Cycle 89–93 Zero-Origin blueprint status — 25 November 2026

Blueprint: `docs/WORK_CYCLE_2026-11-25_BATCH89_93_ZERO_ORIGIN_BLUEPRINT.md`. This is a design draft, not implementation or production acceptance.

| Batch | Current status | Acceptance still required |
|---:|---|---|
| 89 | 🟨 Dependency inspection recorded; runtime unverified | Isolated Python Worker project and exact runtime compatibility tests |
| 90 | 🟦 DO SQLite schema/migration design drafted | Owner review, DDL implementation, migration and digest/restore tests |
| 91 | 🟦 Provider-neutral API contract drafted | Existing frontend contract reconciliation, implementation and route tests |
| 92 | 🟦 Series DO/event/replay design drafted | Durable implementation and concurrency/restart/gap/idempotency tests |
| 93 | 🟦 WebSocket/receipt design drafted | Authenticated ticket, hibernation, reconnect, durable receipt and restart tests |
| 94 | 🟨 Provider gate blocked | Lawful zero-cost source and runtime/transport compatibility evidence |
| 95 | 🟨 Public acceptance blocked | Explicit deployment authorization, public WSS/TLS, browser/Android E2E, quota and restore drill |

Production WebSocket: 🟨 OPEN. Project Gate 25: 🟨 OPEN. Gate 36: 🟨 OPEN. No production Worker/API is claimed deployed. No deployment or Cloudflare resource creation occurred. Zero Cost and main-branch isolation preserved.


---

# Owner-approved execution update — 25 November 2026

The owner approved the Batch 89–93 Zero-Origin blueprint. Approval authorizes scoped implementation planning/work; it does not authorize deployment, Cloudflare resource creation, paid services or bypassing test evidence.

## Newly confirmed WebSocket production gaps

- Current synthetic proof stores sequence watermark but not durable event payload.
- Fan-out occurs after sequence commit, creating a crash window with no replay source.
- WebSocket protocol currently handles auth and ping only; ACK/RESUME are absent.
- No durable consumer receipt ledger or restart receipt reconciliation exists.

Therefore production WebSocket remains 🟨 OPEN. Correct order: DO SQLite atomic event+cursor → bounded replay → durable ACK receipt → reconnect/resnapshot → public WSS/browser/Android E2E. Gate 25 and Gate 36 remain open.

## Execution status

| Batch | Status | Evidence |
|---:|---|---|
| 89 | 🟨 platform feasibility / 🟨 runtime unverified | FastAPI ASGI path documented; no exact repository runtime execution |
| 90 | 🟦 design | DO SQLite schema and migration invariants |
| 91 | 🟦 design | provider-neutral API and fail-closed response contract |
| 92 | 🟦 design | durable series event/cursor/replay contract |
| 93 | 🟦 design | ticket, ACK receipt, hibernation and reconnect contract |
| 94 | 🟨 blocked | no provider passed zero-cost lawful compatibility gate |
| 95 | 🟨 blocked | no production WSS/device E2E/restore evidence |

No code was committed without a runnable test environment. GitHub connector currently exposes file operations only, and local container could not resolve github.com. This limitation is recorded rather than disguising untested source as successful.

Stage 1 acceleration will parallelize independent design and evidence tracks but retain implementation dependency order. No gate closure is inferred from documentation completion.


---

# Stage 1 execution checkpoint — 25 November 2026 source re-audit

This audit confirms that the current synthetic Worker remains proof-only. The sequence cursor is persisted without a durable event payload/digest; fan-out occurs after the cursor transaction; authenticated WebSocket messages support ping/pong but not ACK/RESUME; no durable consumer receipt ledger is present. Therefore the event-log, replay, ACK receipt and reconnect portions of Stage 1 remain unaccepted.

| Acceptance item | Status | Evidence required to close |
|---|---|---|
| Python Worker dependency compatibility (Batch 89) | 🟨 OPEN | Exact isolated runtime probes, package versions and terminal test output |
| DO SQLite schema/migration (Batch 90) | 🟦 DESIGN | Tested DDL, repeatable migration, rollback and legacy digest parity |
| Provider-neutral API (Batch 91) | 🟦 DESIGN | Frontend contract reconciliation, route tests and fail-closed status semantics |
| Durable event log/replay (Batch 92) | 🟨 OPEN | Atomic event+digest+high-water, bounded replay, gap/duplicate/eviction tests |
| WebSocket ACK/receipt/reconnect (Batch 93) | 🟨 OPEN | Bound ACK validation, durable monotonic receipts, RESUME/resnapshot and race/restart tests |
| Provider ingress (Batch 94) | 🟨 BLOCKED | Lawful terms, technical compatibility and zero-cost proof |
| Public WSS/device E2E (Batch 95) | 🟨 BLOCKED | Explicit deployment authorization, TLS, browser/Android reconnect, quota and restore proof |

The current session has no checked-out repository command runner. No runtime tests, build, lint or Cloudflare simulator suite were executed. The GitHub status endpoint returned no status entries and the available workflow endpoint is PR-filtered; neither is evidence of a successful CI run. No code was committed without runnable tests.

No Stage 1 gate is closed by this documentation audit. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed; Gate 25 and Gate 36 remain open. Zero-cost and branch-isolation constraints remain mandatory.


---

# WebSocket test evidence inventory — 25 November 2026

Source inventory: **43 test declarations** (31 Node proof, 11 Durable Object runtime, 1 Miniflare/workerd integration). These are declarations only; no execution is claimed.

The current suites cover synthetic proof request validation, ticket lifecycle/race, sequence continuity, exact-series authenticated fan-out, socket attachment restoration and alarm behavior. Production acceptance remains open for:
- atomic event payload + digest + high-water commit and rollback;
- digest-aware idempotency/conflict detection;
- durable event replay after DO eviction;
- fan-out crash-window proof;
- authenticated ACK and durable monotonic receipt;
- bounded RESUME, retention-floor resnapshot and generation mismatch;
- ACK receipt race and durable cursor restoration;
- Android/browser process-death and network-handover E2E.

Existing ticket-consumption race tests and socket-attachment restoration tests are only adjacent coverage; they do not satisfy ACK receipt race or event replay requirements. No Gate 25/36 status is changed by this inventory.


---

# Coordinated durable-delivery acceptance addendum — 25 November 2026

The detailed cross-batch contract is maintained in [BATCH90_95_DURABLE_WEBSOCKET_DELIVERY_SPEC.md](BATCH90_95_DURABLE_WEBSOCKET_DELIVERY_SPEC.md), commit `327cac59c17894859d0deb6ac99644cdd3aa101f`.

New combined acceptance groups: (1) compatible additive DO SQLite schema; (2) atomic event payload+digest+high-water; (3) duplicate idempotency/conflict and gap rollback; (4) fan-out-after-commit; (5) bounded contiguous replay and retention-floor resnapshot; (6) authenticated ACK and durable monotonic receipts; (7) RESUME/hibernation/eviction recovery; (8) provider legal/free/runtime gate; (9) public WSS/browser/Android/restore E2E. All remain 🟨 OPEN until executable evidence is attached to the exact commit.

No acceptance gate closes from this design document. Stage 1 remains 30/40 = 75% provisional; Gate 10 remains 0/10 formally closed; Gate 25 and Gate 36 remain OPEN. No runtime code or Cloudflare resources were changed.


---

# Batch 89–93 source-audit evidence — 25 November 2026

Detailed evidence and blob SHAs: [BATCH89_93_SOURCE_AUDIT_2026-11-25.md](BATCH89_93_SOURCE_AUDIT_2026-11-25.md).

Static test inventory: 31 Node proof + 11 Durable Object Vitest + 1 Miniflare declarations = 43, all NOT RUN. Static lockfile root metadata matches package.json; no runtime compatibility or installation claim follows from this check.

Batch 92 source blocker: sequence cursor only is committed; event payload/digest replay storage is absent. Batch 93 source blocker: ACK, durable consumer receipt, RESUME and replay recovery are absent. Existing socket attachment restore tests do not close these gates. All Batch 89–93 runtime acceptance conditions remain OPEN pending exact-SHA execution evidence.


**Batch 96A CI:** exact source/test HEAD `7dcf148b772d37c4321122a1c45d49bae0e43868`. Automated Tests run 46010599247, CodeQL 46010599101 and OCI ARM64 46010599133 were still running at last poll; Full Git History Secret Audit run 46010599070 reached SUCCESS. Do not treat Batch 96A as accepted until all required workflows are terminal SUCCESS.
