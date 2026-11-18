# DEZZTA CHART — Batch 32: Gate 36 / 38 / 39 and dependency disposition

**Date:** 18 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Audited HEAD:** `b9f81a9ca25a6ebdf390c40671a4429241c4c5d2`  
**Source baseline:** `e6db77210dd28bd82196b2b7bf7d8d7e7256fc37`  
**Scope:** exact-head CI, WebSocket acceptance boundary, operational metrics/alerts, npm advisory, progress indicator  
**Cost:** ZERO COST  
**Deployment:** none  
**Main:** untouched

## 1. Exact-head CI — confirmed terminal results

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | [44306971092](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306971092) | FAILURE only at final dependency-audit enforcement |
| CodeQL JS/TS + Python | [44306971049](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306971049) | SUCCESS |
| Full Git History Secret Audit | [44306971204](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44306971204) | SUCCESS |

The Automated Tests job completed all functional/security/build/container checks before the final audit enforcement:
- Frontend: 26 test files, 212 tests passed.
- Backend: 1,030 tests passed in 33.74 seconds.
- Frontend production build: 1,526 modules transformed.
- Frontend source and built-bundle credential scans: passed.
- Android host preflight and immutable publisher tests: passed.
- Synthetic SQLite outbox benchmark: passed.
- Backend dependency audit: passed.
- Backend container build, Redis ACL/persistent-volume smoke, Trivy scan and report export: passed.
- Step 27, `Enforce frontend dependency audit result`: failed, intentionally fail-closed.

This is not a green workflow. Do not label the whole Automated Tests workflow successful.

## 2. Dependency blocker — latest upstream/registry review

The exact run reports five High dependency paths through `picomatch@4.0.7`, reached by development tooling through Vite/Vitest, `fdir`, and `tinyglobby`. npm's suggested `npm audit fix --force` downgrades Vite to 6.2.7, a breaking change.

Current independent evidence:
- GitHub Advisory: [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) lists affected versions through 4.0.7 and no patched version.
- OSV record: [GHSA-fc5q-39xc-vjpf](https://osv.dev/vulnerability/GHSA-fc5q-39xc-vjpf), updated 17 November, retains the High advisory.
- npm registry: [picomatch versions](https://www.npmjs.com/package/picomatch?activeTab=versions) still lists 4.0.7 as latest at audit time.
- Upstream [PR #194](https://github.com/micromatch/picomatch/pull/194) is OPEN and addresses leading question-mark parsing in extglob bodies. It is not a merged/released advisory fix. Do not mistake this PR for the ReDoS remediation.
- A third-party record mentions 4.0.8, but the official npm registry does not list that release and the official advisory does not identify it as patched. It is not acceptable evidence for an override.

**Disposition:** no safe published fix is available in the verified package registry/advisory evidence. Do not force downgrade, hand-patch node_modules, use an unmerged fork, add an unreviewed override, suppress the advisory, or lower audit severity. Keep CI red at the final fail-closed enforcement while preserving all other diagnostics.

## 3. Gate 36 — WebSocket

### Repository evidence
- Frontend client, protocol and supervisor tests passed in the 212 frontend tests.
- Backend authenticated API WebSocket, replay, stream, synthetic POC protocol and bounded-probe tests passed within 1,030 backend tests.
- Transport errors wait for authoritative close before reconnect scheduling; reconnect obtains a fresh token and preserves the durable cursor.
- Synthetic POC validates text-only messages, message bounds, rate bounds, ping/idle behavior and browser-side probe lifecycle.

### Acceptance still missing
- Real public WSS Upgrade and ping/pong.
- Foreground 330-second owner-observed session with actual close code/reason and elapsed duration.
- Android WebView compatibility.
- Effective Fluid Compute setting read-back.
- Cross-instance fan-out under a verified runtime.
- Production data/provider entitlement and owner cost acceptance.

The existing POC is synthetic-only. HTTP `/health` success does not prove WebSocket upgrade. No new Vercel deployment was made because the branch deployment guard is disabled and a new build would not produce the missing owner-device evidence.

## 4. Gate 38 — metrics / monitoring

### Verified implementation
- `backend/app/observability.py` provides process-local request counters and latency histograms.
- Series cardinality is capped at 127 including the overflow series.
- Method, route, status and duration inputs are normalized; extreme/non-finite durations are bounded.
- Snapshot is detached from internal state and concurrent recording is lock-protected.
- `/internal/metrics` is registered only when an operator token is configured; it requires Bearer authentication and returns private/no-store headers.
- Unit tests cover cardinality, normalization, detached snapshots, invalid values and concurrent recording.

### External acceptance still missing
- Host-level collection and durable/aggregated data.
- Bounded log/metric retention and rotation.
- Disk-pressure behavior and resource budget.
- Dashboard/collector access-control proof.
- Redacted incident trace and operator review.

The scope is explicitly `process_local_since_start`: metrics reset on restart and do not aggregate across instances. A local endpoint and passing tests are not a production monitoring system.

## 5. Gate 39 — operational alerts

### Verified implementation
- `LocalAlertReporter` emits transition-based sanitized JSON logs for degraded delivery, worker errors and recovery.
- Tests cover duplicate-state suppression, recovery transitions, strict counter validation and exception-message redaction.
- The opt-in worker calls the reporter from its delivery loop.
- Raw exception text, owner identifiers, installation identifiers, FCM tokens, provider payloads and credentials are excluded from reporter records.
- Worker remains disabled by default; this is not end-user notification delivery and not an out-of-band operator alert.

### External acceptance still missing
- Actual host log collection and bounded retention.
- A designated responsible adult operator and escalation ownership.
- A verified no-cost, privacy-reviewed alert channel (none is assumed configured).
- Isolated failure/acknowledgement/recovery exercise with sanitized timestamps and evidence.

Do not enable a production worker or send notifications merely to make a gate look complete. Keep the current safe disabled default.

## 6. Gate 30 / 31 carry-forward

- Gate 30: CI restore drill validates source preservation, integrity, foreign keys, schema, row hashes, domain readback, committed post-restore write/read and cleanup. An owner-target application database restore is still required.
- Gate 31: AES-256-GCM/PBKDF2 recovery code and CI round trip exist. Off-host artifact, separate key custody, retention/access policy and recovery from that destination remain absent. No storage provider is provisioned.

## 7. Deployment / cost / device controls

- Exact-SHA Vercel lookup for both projects at `b9f81a9ca25a6ebdf390c40671a4429241c4c5d2`: zero deployments.
- Root `vercel.json`: `main=true`; `phase-2/market-data-foundation=false`; `fluid=true`.
- No Vercel deploy/retry, no Cloudflare resource, no billing/plan change, no paid service, no SSO change.
- No Termux required for this remote source/CI audit. Any future device-side prerequisite must be explained before action is requested.
- `main` untouched.

## 8. Progress accounting — unchanged

| Indicator | Verified state |
|---|---|
| Stage 1 | **75% provisional — 300/400 ticks; 30/40 criteria** |
| Gate 10 | **0/10 formally closed** |
| Open criteria | **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** |
| Stages 2–6 | **NOT SCORED** |
| Overall project | **NOT ESTABLISHED**; M1–M8 weighting and criterion mapping not approved |
| Historical overall checkpoint | 20.9%, historical only |
| Cost | ZERO COST |
| Main | untouched |

No stage ticks or gate closures are awarded for source-only, CI-only, documentation-only or synthetic evidence where the acceptance matrix requires owner-host/device proof.

**Engineering decision:** the current blocker set has no safe repository-only shortcut. Keep the npm audit fail-closed, preserve the synthetic WSS boundary, and do not manufacture host monitoring/alert evidence. This batch is a verified multi-gate audit and progress-dashboard refresh, not a claim of production acceptance.
