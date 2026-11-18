# DEZZTA CHART — Work Cycle 2026-11-18 Batch 41

## Empty identity-token retry-loop prevention

**Repository:** `deszztagd377-pixel/dezzta-chart`  
**Branch:** `phase-2/market-data-foundation`  
**Exact source SHA:** `09dd096580b30bce5789d12ab09f9ee41ac4234d`  
**Main:** untouched  
**Cost:** ZERO COST  
**Termux:** not required  
**Deployment:** none

### Defect and impact

The OHLCV supervisor retried when `getIdToken()` resolved to an empty or whitespace-only string. Unlike a temporary token-provider rejection, an empty credential is not a transport failure: retrying without a new authenticated session cannot produce a valid WebSocket auth frame. It could create repeated token-provider calls and useless reconnect timers.

### Corrective change

In `src/services/ohlcvStreamSupervisor.ts`, an empty/whitespace token now:
1. marks this supervisor instance terminal;
2. marks the selected market-data snapshot unavailable with a sign-in-specific message;
3. sets supervisor status to `stopped`;
4. reports one explicit error; and
5. does not schedule another connection attempt.

A new authenticated session must create a new supervisor. Transient rejected token-provider promises remain retryable, preserving recovery for temporary identity-provider/network failures.

### Regression tests

Updated `src/services/ohlcvStreamSupervisor.test.ts`:
- parameterized empty-string and whitespace-only token tests;
- verifies no socket is created;
- verifies no retry occurs after advancing fake timers;
- verifies the snapshot becomes unavailable and one error is reported;
- retains the separate transient token acquisition rejection/retry test.

The first implementation CI run correctly caught a stale test that still expected an empty token to retry. That contradictory test was removed in commit `09dd096580b30bce5789d12ab09f9ee41ac4234d`; no production code was reverted.

### Exact-head validation status

Latest run IDs for `09dd096580b30bce5789d12ab09f9ee41ac4234d`:
- Automated Tests: [44327851319](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851319) — frontend unit tests/build and frontend credential scans passed; backend dependency install/tests and remaining container checks were still running at snapshot time.
- Android APK: [44327851485](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851485) — in progress.
- CodeQL: [44327851364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851364) — in progress.
- Full Git History Secret Audit: [44327851417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44327851417) — success.

Earlier intermediate SHA `ec226b6a97d42d6bd0af19011f1043ed133775b7` failed on the stale test expectation; it is not the latest branch head. Do not report the latest SHA as fully green until its runs complete.

### Progress and open gates

- Stage 1: **75% provisional** — 300/400 ticks; 30/40 criteria.
- Gate 10: **0/10 formally closed**.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6: **NOT SCORED**.
- Overall percentage: **NOT ESTABLISHED**; approved M1–M8 weights/mapping are absent.
- No test or documentation update awards a progress tick or closes a gate.

### Constraints

No dependency downgrade/override/suppression was introduced. The picomatch advisory remains fail-closed. No Vercel deployment, Cloudflare resource, paid service, billing activation, or Termux operation was performed.

**Conclusion:** removes an avoidable empty-credential retry loop while preserving retries for transient identity-provider failures. Formal completion awaits exact-head CI.
