# Batch 62J-38 — WebSocket ticket request deadline and Android update-readiness audit

**Date:** 20 November 2026  
**Branch:** phase-2/market-data-foundation  
**Source/test HEAD:** 734cd20d7525e9d67f6a045dc13a98410e26cdd0  
**Scope:** bounded WebSocket ticket renewal request, regression tests, Android distribution/update readiness audit, and complete progress reconciliation. ZERO COST. No deployment or preview publication.

## 1. WebSocket ticket renewal hard deadline

### Finding

The frontend requested short-lived WebSocket authentication tickets over HTTPS but did not impose a deadline on the fetch. A stalled response could leave the renewal callback awaiting indefinitely. The WebSocket stream's own acknowledgement timer begins only after a ticket is returned and sent, so it does not bound the preceding HTTPS request.

### Change

Updated `src/services/ohlcvWebSocketTicket.ts`:

- Added a fixed 10,000 ms request deadline.
- Uses `AbortController` and passes its signal to fetch.
- Keeps the same deadline active through response-body JSON parsing, not just until response headers arrive.
- Clears the timer on every success/error path.
- Preserves HTTP 401 as a typed status-bearing error so the reconnect/authentication supervisor can distinguish revoked/expired authentication.
- Keeps existing request protections: POST, Bearer token in the HTTPS header only, no-store, credentials omitted, redirects rejected, endpoint path normalized, and strict response validation.
- Does not log or place identity tokens in a URL or WebSocket frame.

Added `src/services/ohlcvWebSocketTicket.test.ts` with six tests covering normalized endpoint and request policy, 401 propagation, timeout before response headers, timeout while parsing the response body, malformed payload rejection, and invalid credential/URL rejection.

### Exact-head validation

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests & Build | [44717816608](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44717816608) | SUCCESS |
| CodeQL JavaScript/TypeScript + Python | [44717816621](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44717816621) | SUCCESS |
| Full Git History Secret Audit | [44717816577](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44717816577) | SUCCESS |
| Android debug APK build | [44717816593](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44717816593) | SUCCESS |

- Frontend: **242 tests passed across 29 test files**.
- Backend: **1,172 passed, 6 warnings in 62.95 seconds**.
- Frontend production build and bundle secret scan: SUCCESS.
- Backend container image build: SUCCESS.
- Shared Redis guard + persistent-volume container smoke test: SUCCESS.
- Container image scan and vulnerability report export: SUCCESS.
- Android debug APK assembled, SHA-256 calculated and CI artifact uploaded; no release was published.

The first CI attempt exposed a test-harness issue: the two timeout tests attached rejection assertions only after advancing fake timers, so Vitest observed late unhandled rejections despite all test assertions eventually passing. The assertions were moved before timer advancement, and the full exact-head workflow then passed. No user device operation or manual code execution was required.

## 2. WebSocket work disposition

The defined automated WebSocket E failure matrix remains complete, including:
- Two live ASGI gateways recovering after both Redis TCP paths are severed and restored without restarting either gateway.
- Two independent replicas installing the same verified snapshot watermark and applying the next cursor with converged checkpoints.

This is repository/CI acceptance, not production public-WSS acceptance. Still open:
- Owner-controlled Redis TLS/ACL, credential rotation and snapshot/relay contract (Gate 25).
- Public authenticated WSS reverse proxy, certificate/hostname validation, browser and Android WebView reconnect/replay tests, proxy restart (Gate 36).
- Retention/old-group cleanup governance and owner-host recovery runbook.

Do not describe production WebSocket as ready until these external acceptance steps pass.

## 3. Android patch/update readiness — important current limitation

The repository is public and the current Android workflow uses zero-cost GitHub Actions to build a Capacitor debug APK. The workflow:
- Uses `assembleDebug`, not a release-signing configuration.
- Uploads a short-lived CI artifact with a SHA-256 sidecar.
- Allows a versioned GitHub preview release only through explicit manual dispatch input; publication is opt-in and was skipped in this batch.
- Does not implement an in-app update checker or automatic APK installation.

A debug APK built on an ephemeral CI runner must **not** be treated as an update-compatible production package. The debug signing identity is not a durable owner-controlled release key. Android package updates require the same signing identity (or a supported signing-key lineage) and a compatible package/version path. Until a stable release key and custody plan exist, repeated CI debug APKs are previews, not a dependable in-place patch channel.

### Zero-cost target design — proposal, not activated

1. Keep the package ID stable and define a release versionCode/versionName policy.
2. Generate a dedicated release signing key under owner control, never commit it, and keep encrypted offline backups with a separately stored recovery procedure.
3. Inject the key and passwords only through protected GitHub Actions secrets at release-build time. Never put signing material in frontend assets, source control, logs, or artifacts.
4. Sign each release APK and publish an immutable GitHub Release containing the APK, SHA-256, version metadata, minimum supported app/data schema, and signed release manifest.
5. Pin the update-manifest verification public key in the app. Verify manifest signature, package ID, version monotonicity and APK hash before offering an update.
6. Use an in-app update notice/download flow, then hand off to Android's package installer. A normal Android application cannot silently install a sideloaded APK without privileged device-owner/system permissions; user confirmation remains part of the flow.
7. Keep prior signed releases and a forward-fix/rollback procedure. Database migrations must be versioned, backed up before destructive changes, and tested for recovery. Android generally blocks downgrades to lower versionCode through the ordinary installer; rollback should normally be a higher-version corrective release, not an assumed downgrade.
8. Add release-channel separation (stable/preview), dependency update review, reproducible build metadata, SBOM, security patch cadence, schema migration tests and exportable user data.

**No paid hosting is required for a public GitHub Release distribution path.** This does not imply a free Android Play Store listing; Play publication remains deferred and may have fees and account requirements.

### Longevity claim boundary

No engineering team can guarantee that an app will operate for 100 years. The realistic goal is long-term maintainability: documented interfaces, portable data formats, explicit schema migrations, pinned/reviewed dependencies, automated security and compatibility tests, signed releases, key backups/rotation policy, and the ability to build from archived source without depending on one vendor. The application must not claim autonomous updates are enabled until the signed release and user-confirmed installation flow are implemented and tested.

### Termux / device boundary

Termux was **not required** for this batch. A later phone-only release-signing setup may require a local key-generation utility if no desktop environment is available. Before any such operation, the owner will be told exactly why it is needed and asked to approve the key-custody procedure. No signing key was generated, exported or requested in this batch.

## 4. Gate 10 and indicator dashboard

Gate 10 remains **10/10 🟧 ORANGE / 0 CLOSED**. Repository CI does not close owner-host acceptance gates.

| Gate | Status | Remaining external acceptance |
|---:|---|---|
| 8 | 🟧 | Owner-host secret injection, file ownership/mode, process exposure, log/crash redaction |
| 20 | 🟧 | Real Firebase sign-in, expiry/revocation, entitlement denial and browser/Android acceptance |
| 25 | 🟧 | Owner-host Redis TLS, ACL, credential rotation, persistence/recovery and snapshot/relay contract |
| 30 | 🟧 | Actual Android DB path, fresh-path restore report, application-domain readback and recovery timing |
| 31 | 🟧 | Encrypted off-host artifact, separate recovery-key custody, independent restore and retention/deletion |
| 34 | 🟧 | Actual persistent mount/path, UID/GID permissions, restart persistence and disk-pressure recovery |
| 35 | 🟧 | Owner-controlled HTTPS backend, certificate/hostname verification, health/startup/secret injection |
| 36 | 🟧 | Authenticated public WSS proxy, browser/Android acceptance, reconnect/replay and proxy restart |
| 38 | 🟧 | Bounded metrics/log retention, dashboard access control, disk pressure and credential redaction |
| 39 | 🟧 | Bounded FCM worker design/implementation, induced-failure alert, operator acknowledgement/escalation and tested recovery |

### Full indicator status — no indicator completion credit in this batch

| Indicator | State | Verified foundation | Remaining work |
|---|---|---|---|
| SMA 20 | 🟨 | Rolling mean; first valid index 19 | Overlay, toggle, legend/value, stale clearing and render tests |
| EMA 20 | 🟨 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/value, stale clearing and render tests |
| RSI 14 Wilder | 🟨 | Wilder smoothing; first valid index 14 | 0–100 pane, 30/70 guides, toggle, legend and render tests |
| MACD 12/26/9 | 🟨 | MACD index 25; signal/histogram index 33 | Dedicated pane, lines, histogram, zero guide and render tests |
| Bollinger 20,2 | 🟨 | Population standard deviation; first valid index 19 | Three-line overlay, toggle, legend/value and render tests |
| Shared Indicator Hook | 🟨 | Validated backend snapshot only; no DEMO fallback | Active chart binding, loading/error and cross-series isolation |
| Footprint | 🟧 | Synthetic educational accumulator; SIMULATED only | Owner reference image, reviewed blueprint, ON-only spaced cluster layout |
| Heatmap | 🟥 | No implementation verified | Owner reference, blueprint, validated data/calculation contract and renderer |
| Liquidation Maps | 🟥 | No validated data/calculation contract | Source feasibility, reference, calculations and renderer |

Indicator formulas and warm-up alignment remain unchanged:
- SMA20 / EMA20: index 19.
- RSI14: index 14.
- MACD12/26/9: MACD index 25; signal/histogram index 33.
- Bollinger20,2: index 19.

No Footprint/Heatmap visual work is authorized without the required owner references and reviewed blueprint. Stage 4 remains parked while Stage 1 is active.

## 5. Project accounting and change boundary

- Stage 1: **30/40 = 75% provisional**.
- Stages 2–6: unscored.
- Overall project percentage: not established; M1–M8 weights remain unapproved.
- Indicator aggregate percentage: not established; no approved weighted denominator.
- Gate 10: 10/10 ORANGE / 0 closed.
- ZERO COST: GitHub Actions and public GitHub repository only; no paid service, deployment, preview release or provider activation.
- No Termux operation.
- No main branch modification.

## 6. Changed files

- `src/services/ohlcvWebSocketTicket.ts` — fixed 10-second abortable ticket request deadline, including body parsing.
- `src/services/ohlcvWebSocketTicket.test.ts` — six request/timeout/authentication validation tests.
- `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` — current dashboard and gate/update-readiness reconciliation.
- `docs/INDICATOR_PROGRESS_LEDGER.md` — complete indicator state and explicit no-credit update.
- `docs/WORK_CYCLE_2026-11-20_BATCH62J38_WEBSOCKET_TICKET_DEADLINE_ANDROID_UPDATE_READINESS.md` — this report.
