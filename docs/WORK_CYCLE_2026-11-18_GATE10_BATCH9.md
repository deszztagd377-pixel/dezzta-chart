# DEZZTA CHART — Gate 10 Work Cycle Batch 9
Date: 2026-11-18
Branch: `phase-2/market-data-foundation`
Policy: ZERO COST; `main` untouched.

## Objective
Continue the WebSocket POC correction, improve Gate 38/39 repository regression coverage, and update the colored project-process progress documentation without claiming external acceptance or unverified test results.

## Findings and remediations

### Gate 36 — WebSocket POC connection-state defects
A source audit found three related UI-state risks:
1. Connect was available during CONNECTING, permitting repeated attempts to replace the page's in-flight socket reference.
2. Disconnect was disabled during CONNECTING, preventing cancellation of a slow handshake.
3. The browser `error` event was treated as proof the socket had closed. A WebSocket error event does not guarantee the socket is already CLOSED, so this could briefly re-enable Connect while the previous socket was still in flight.

Remediation:
- Disable Connect during CONNECTING and OPEN.
- Enable Disconnect during CONNECTING and OPEN.
- Keep the connecting/error state until the actual `close` event is received; error handler only logs a sanitized transport message and updates status text.
- Add source-contract assertions for these behaviors.

Source commit: `60c3a2123112c88d840ca57f9da9db7dc0a7f023`.
Regression-contract commits: `be0849ab54ca77b9acd3827abb60a56597cb9cdd`, `f1c60ff07bf55d11581900f948efe28c86cbf426`, `0f2061cf53a625fa07573f510546028d40df45ac`, `254dc09e04bd3647b78d6499eb2d3703cfe34c7f`.

### Gate 38 — concurrent metrics accounting
Added a deterministic concurrency test using 8 threads × 125 observations = 1,000 expected observations. It checks request counts, histogram totals, and cumulative bucket ordering. This improves regression coverage for the existing thread-locked collector; it does not provide cross-process aggregation, durable retention, a protected host dashboard, or operational acceptance.

Commit: `2146f5931eed4d134183011f5009420d9f9a2881`.

### Gate 39 — sanitized alert recovery transition
Added a test for worker-error → healthy-batch recovery. It verifies the expected state transition and confirms that the exception message is not included in local operational log records. It does not prove persistent log retention, an incident escalation recipient, or an exercised recovery procedure.

Commit: `265ca1948777c7ef02076c3381b597080cbcb65d`.

## Files changed
- `poc/vercel_ws/index.py` — connection lifecycle state handling.
- `backend/tests/test_vercel_ws_probe_contract.py` — duplicate-connect, cancellation and error/close-state contracts.
- `backend/tests/test_observability.py` — concurrent request-metrics accounting test.
- `backend/tests/test_alert_operations.py` — sanitized error-recovery transition test.
- `docs/PROJECT_PROGRESS_INDICATOR.md` — detailed progress and work-cycle update.
- `docs/STAGE_1_ACCEPTANCE_MATRIX.md` — current verification boundary and gate accounting.
- `docs/WORK_CYCLE_2026-11-18_GATE10_BATCH9.md` — this report.

Documentation commits:
- Progress indicator: `dc6d6862b371deb6024d14fcc5b7d3605fdbfe91`.
- Acceptance matrix: `697ec2ff17c3e27965a6d6aaed40c39b06400c2d`.

## Verification boundary
- The latest test additions are committed but were **not executed** in a verified exact-head GitHub Actions run. Do not report them as passing.
- Earlier 1,008-test backend success belongs to the previously documented exact commit, not this new head.
- The available GitHub workflow-run connector path only exposes PR-triggered runs; no exact-head push-run result was available through this route.
- No Vercel build was triggered for the latest POC changes. The last READY WSS deployment is an older source revision. New POC behavior is not yet deployment-verified.
- The Vercel Hobby build-rate restriction remains a real constraint. No upgrade, billing activation, repeated retry, SSO weakening, or production promotion occurred.
- No Termux installation or command was required.

## Progress accounting — deliberately unchanged
- Stage 1: **300/400 ticks = 75% provisional** (30/40 provisional criteria).
- Gate 10: **0/10 external criteria formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall project percentage: no fresh score asserted; 20.90% remains a historical checkpoint only.
- No Stage 1 ticks awarded for source/test/documentation changes without the required acceptance evidence.

## Remaining blockers and next action
- **CI/dependency:** High `picomatch@4.0.7` advisory remains unresolved. The Batch 8 workflow adjustment is designed to let independent diagnostics run before mandatory final audit enforcement; its exact-head outcome still needs read-back.
- **Gate 36:** deploy the updated POC only when the free build quota safely permits one intentional build; then observe the bounded 330-second test, verify effective Fluid Compute settings, and complete supported Android WebView and target-host fan-out/cost acceptance.
- **Gate 38:** process-local collector is not durable; still requires a zero-cost host log/metrics sink, bounded retention, access control and accepted dashboard on existing owner-controlled hardware.
- **Gate 39:** local sanitized logging is implemented; persistent retention, escalation ownership and recovery drill remain external.
- **Gates 8, 20, 25, 30, 31, 34, 35:** require owner-controlled target environment evidence and remain open. Do not buy a managed service or weaken security to force closure.

No broken code or document is being handed to the owner for repair.

## Final documentation cross-links
- Final project progress indicator link commit: `de66dac4e5d58b363d24cbc757c61421482c133e`.
- Acceptance matrix Batch 9 report link commit: `1df00662de2f96721f2c807831dcb69e26ac9932`.
- Progress dashboard remains intentionally at Stage 1 **75% provisional** and Gate 10 **0/10**; no external acceptance evidence was created by documentation updates.
