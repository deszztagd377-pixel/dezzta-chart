# Work Cycle Batch 62J-89 — test-harness correction

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Parent:** `002517f778bed20bcb9e7fe7eed7946893c9763f`

## Failure analysis

Automated Tests [44904630244](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630244) failed one test after frontend 255/255 passed and backend 1,268 passed / 1 failed.

Failing test: `test_concurrent_workers_commit_without_losing_deltas`.

The exact source showed:
```python
barrier.wait(timeout=5)
collector.flush(worker_id, request, websocket, now=900)
raise AssertionError("bounded SQLite retry loop exhausted")
```

The assertion was a leftover from the previous retry-loop implementation and had become unconditional after the retry loop was removed. The collector flush had completed; the test then raised its own assertion. This is a test-harness defect, not proof of SQLite lock retry exhaustion.

## Correction

- Remove only the unconditional assertion.
- Keep the direct collector flush call; do not restore outer retries.
- No production code, WebSocket data path, or retry policy is changed.

## Evidence from the same CI attempt

- Read-only storage failure/recovery test: PASSED.
- Benchmark contract test with four spawned OS processes and 899 logical series: PASSED.
- CodeQL [44904630257](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630257): SUCCESS.
- Full Git History Secret Audit [44904630302](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904630302): SUCCESS.
- Full Automated Tests run remains FAILED because of the stray assertion; rerun on corrected exact HEAD is required.

## Acceptance state

Gate 38 remains 🟧 OPEN pending corrected exact-head CI, genuine disk-full/storage-exhaustion testing, app-level HTTP/WebSocket isolation proof, and owner-host persistence/retention/backup/operator acceptance. The process benchmark is synthetic same-host evidence only; it does not support multi-host SQLite.

Indicators unchanged. Gate 10 remains 0/10 formally closed. Stage 1 remains 30/40 = 75% provisional. Overall project percentage remains unscored.

ZERO COST. No deployment, Termux/device action, paid service, production credentials or `main` modification.


## Batch 62J-90 — exact-head acceptance for the prior correction

The corrected thread regression test is accepted on exact HEAD `2650c70e977b22a4c70a5e0e292dcc3a8a59082c`: Automated Tests [44904944196](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944196) SUCCESS (35/35 steps; frontend 255/255 across 29 files; backend 1,269 passed in 53.67 seconds), CodeQL [44904944207](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944207) SUCCESS, Full Git History Secret Audit [44904944202](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44904944202) SUCCESS. The separate-process benchmark and read-only recovery test are therefore CI-accepted for this exact HEAD.
