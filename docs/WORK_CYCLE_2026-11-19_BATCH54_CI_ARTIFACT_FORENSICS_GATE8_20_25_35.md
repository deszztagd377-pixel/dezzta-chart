# WORK CYCLE BATCH 54 — CI artifact forensics and Gate 8/20/25/35 acceptance audit

**Date:** 19 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Audited HEAD:** `fba43a12017e314baeb9e2719a50b441274126c6`  
**Cost:** ZERO COST • **Deployments:** none • **Termux:** not required • **main:** untouched

## 1. Exact-head CI fully completed

Automated Tests & Build [run 44470207284](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207284) completed with **SUCCESS** on the exact audited HEAD. CodeQL [run 44470207308](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207308) and Full Git History Secret Audit [run 44470207366](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207366) also completed successfully on the same SHA.

- Frontend Vitest: **234/234 passed**, 28 test files.
- Backend pytest: **1,032/1,032 passed**.
- Frontend dependency audit: **0 vulnerabilities**.
- Backend dependency audit: no known vulnerabilities reported.
- Production frontend build and source/bundle credential checks passed.
- Backend container build passed.
- Redis ACL/AOF, fail-closed outage behavior, non-root runtime, persistent-volume ownership, SQLite integrity and restart persistence smoke tests passed.
- Trivy HIGH/CRITICAL scan completed and report was exported.
- The CI job completed successfully; no pending cleanup step remains.

## 2. Container vulnerability report — artifact inspected, not inferred

Downloaded and parsed the exact workflow artifact:
[container-vulnerability-reports — artifact 14503114420](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207284/artifacts/14503114420)

- Artifact contains `trivy-current.json`.
- Scanned image: `dezzta-chart-backend:ci`.
- Image digest: `sha256:51c3bcf50e62d8e875028debf81d98204697a87e1ef2ed7035c27768b676d27e`.
- Image OS: Alpine 3.24.4.
- Parsed Trivy JSON: **0 reported vulnerabilities across all results**, including HIGH and CRITICAL.
- This is a scan of the CI image built for this commit; it is not a deployed-host image or a permanent guarantee against newly disclosed CVEs.

The frontend npm audit and backend dependency audit are separate checks; none is substituted for the container scan.

## 3. Synthetic SQLite/outbox benchmark — measured and bounded

Inspected [synthetic-outbox-benchmark artifact 14503597322](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44470207284/artifacts/14503597322), which identifies the exact audited commit.

| Measurement | Result |
|---|---:|
| Synthetic bars inserted | 1,000 |
| Outbox high-water mark | 1,000 |
| Events replayed | 1,000 |
| Replay readers | 2 threads, same process |
| Persist p50 / p95 / p99 | 2.60 / 10.20 / 26.99 ms |
| Concurrent replay page p50 / p95 / p99 | 0.36 / 1.62 / 8.86 ms |
| Replay batch size | 250 |

**Strict limitation:** this is a local SQLite microbenchmark on one GitHub runner, one process, one writer and concurrent reader threads. It is synthetic-only, not market data. It does not measure provider latency, WebSocket fanout, reconnect storms, multi-process contention, production host performance, or any production SLO. Do not convert these values into a capacity promise.

## 4. Gate 8 — secret injection and runtime isolation

Repository evidence re-audited:
- Sensitive settings are marked non-repr and tests assert that Redis credentials, Firebase project identifiers, provider credentials, legacy token and calendar digest do not appear in Settings repr/str.
- Frontend source and built bundle credential scans pass.
- Full reachable Git-history secret audit passes.
- Firebase Admin credentials are expected only from server-side Application Default Credentials or a protected runtime secret source; Firebase client config in `VITE_*` is public configuration, not an Admin secret.
- Alert-device encryption key loader requires an absolute regular file, restrictive POSIX permissions, canonical base64 and exactly 32 decoded bytes.

**Still OPEN:** there is no accepted read-back proving that an actual production host injects the correct secret values, protects file mounts, and keeps credentials out of process diagnostics/logs. No secret values were requested or copied into this audit.

## 5. Gate 20 — Firebase authentication boundary

Source/test evidence:
- Client AuthProvider uses Firebase Auth email/password and Google redirect flows; auth observer lifecycle and error sanitization have unit/DOM tests.
- Backend FirebaseIdentityVerifier requests `check_revoked=True`, validates subject, issuer, audience and auth_time, and returns a provider-neutral VerifiedPrincipal.
- HTTP and WebSocket subscription authorization derive account identity from the verified principal, not request-supplied owner IDs.
- Instrument mapping and explicit entitlement checks remain separate from authentication.
- Production settings require `FIREBASE_PROJECT_ID`; Admin credentials remain server-side.
- Firebase client config is public browser configuration. Phone/SMS authentication is not part of the zero-cost plan and must not be enabled.

**Still OPEN:** real signed Firebase ID tokens from an owner-controlled project have not been tested end-to-end for valid, expired, revoked and wrong-project cases. A separate short-lived scoped WebSocket ticket exchange is not implemented; the current client sends the Firebase ID token in the initial WebSocket auth frame. The managed provider architecture direction is documented, but no real Firebase project deployment or billing activation was performed.

## 6. Gate 25 — shared Redis guard

Source and test evidence:
- Atomic Lua fixed-window HTTP counters and sorted-set WebSocket leases.
- Per-client and global HTTP limits; per-account and global WebSocket limits.
- Account subjects are SHA-256 hashed before Redis key construction.
- Lease renewal occurs every one-third of the configured lease duration; default lease is 45 seconds, so nominal renewal cadence is 15 seconds.
- Redis TLS uses required CA validation and hostname verification.
- Production configuration requires `rediss://`, non-empty ACL username/password, and startup health ping.
- Redis failure is fail-closed: HTTP security checks return 503; WebSocket capacity/store errors close with 1013. No process-local fallback is silently substituted.
- Exact-head CI smoke verifies Redis ACL/AOF and outage/recovery behavior.

**Still OPEN:** no separately operated production Redis endpoint, independent network/TLS validation, multi-process/instance contention test, or owner-host outage drill exists. The CI Redis service is not production evidence. Client IP attribution behind a reverse proxy also remains intentionally conservative: arbitrary `X-Forwarded-For` is not trusted without an explicit trusted-proxy boundary.

## 7. Gate 35 — HTTPS/WSS deployment acceptance

Repository configuration:
- Production CORS accepts exact HTTPS origins only; wildcard, path, query, fragment, credentials and malformed origin components are rejected.
- The WebSocket path enforces credentials and entitlement independently of Origin.
- The container exposes the ASGI service internally on port 8000; it does not itself terminate public TLS.
- HTTPS/WSS must be terminated by an owner-controlled ingress/platform with certificate renewal and trusted forwarding configuration.

**Still OPEN:** there is no accepted owner-controlled backend HTTPS endpoint, certificate/renewal test, HSTS/redirect policy evidence, external TLS scan, or Android WebView connection against that endpoint. The isolated Vercel WSS preview is synthetic-only and does not close Gate 35.

## 8. WSS POC — no unsafe workaround

The existing POC deployment remains READY and SSO-protected, with project `live=false`. The POC's unit tests cover synthetic ping/pong, fresh session sequence reset, input size/shape rejection, rate limit and idle timeout. No authenticated owner-browser WSS round-trip, Android WebView, 330-second foreground session, effective Fluid Compute read-back, or cross-instance fanout proof is available.

No deployment was created, SSO was not weakened, and no public share link was created. A missing runtime proof is not repaired by manufacturing a deployment or claiming that an empty log query proves a successful socket.

## 9. Gate 10 and progress disposition

| Criterion | Batch 54 finding | Formal status |
|---:|---|---|
| 8 | CI source/bundle/history scans pass; actual host injection absent | OPEN |
| 20 | Firebase client/server source tests pass; real project E2E absent | OPEN |
| 25 | Redis shared guard + TLS + CI outage smoke pass; production Redis absent | OPEN |
| 30 | Integrated encrypted restore CI proof remains; owner-host restore absent | OPEN |
| 31 | Encryption implementation/tests remain; off-host copy and separate key custody absent | OPEN |
| 34 | CI mounted-volume restart proof remains; production host volume absent | OPEN |
| 35 | HTTPS origin config validated; public owner backend TLS absent | OPEN |
| 36 | Synthetic WSS preview remains SSO-protected; real browser/device/runtime proof absent | OPEN |
| 38 | Bounded process-local metrics tests remain; host collector/retention absent | OPEN |
| 39 | Sanitized local reporter tests remain; owner/operator escalation drill absent | OPEN |

**Gate 10 remains 0/10 formally closed.** This cycle awards no Gate closure, Stage 1 ticks, or overall percentage points.

- Stage 1: **30/40 criteria; 300/400 ticks; 75% provisional**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: **NOT ESTABLISHED**; historical 20.9% remains historical until M1–M8 scoring is approved.
- Technical indicators remain exactly as Batch 53: five calculation foundations + shared hook, not visible chart integration; Footprint visuals wait for owner reference; Heatmap/Liquidation Maps unimplemented/unverified pending references and Stage 4 gate.

## 10. Cost and safety ledger

No Vercel/Cloudflare deployment, no production promotion, no paid provider, no billing activation, no cloud storage subscription, no Firebase phone/SMS auth, no FCM sender activation, and no Termux operation. Active branch only; `main` untouched.

**Engineering disposition:** Batch 54 closes the uncertainty about the exact-head CI run and inspects its raw container-scan and benchmark artifacts. It materially strengthens evidence for Gates 8/20/25/35 but cannot replace owner-host acceptance. ZERO COST, no speculative code edits, no blind deploy.
