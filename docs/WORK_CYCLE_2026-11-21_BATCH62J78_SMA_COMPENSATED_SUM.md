# DEZZTA CHART — Batch 62J-78
## Compensated SMA cancellation accuracy

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Latest source/test HEAD:** `f70f0bcfe2208b4fbfb37440fe8dc3b740e8fbcc`

### Defect found
Batch 62J-77 prevented avoidable intermediate overflow by normalizing each SMA window. A further adversarial ordering showed that a tiny normalized residual could still be rounded away by ordinary summation:

- Inputs: `[Number.MAX_VALUE, 1, -Number.MAX_VALUE]`
- Exact arithmetic mean: (1/3)
- Plain normalized reduction: loses the (1/Number.MAX_VALUE) residual and returns zero.

### Correction
- Added an error-free floating-point expansion sum for normalized window terms. The expansion is invoked only when normalized terms substantially cancel; ordinary positive-price windows stay on a fast linear summation path. Bollinger middle-band means reuse the same stable mean helper.
- Retained scale normalization, finite-result guard, warm-up nulls and source-index alignment.
- Added regression tests for both `[MAX_VALUE, 1, -MAX_VALUE]` and `[MAX_VALUE, -MAX_VALUE, 1]`, plus the Bollinger middle-band equivalent.

### Complexity and scope
- Time complexity remains O(N × P); expansion storage is O(P) for each window.
- For SMA20, each window contains 20 values. No arbitrary-period controls are introduced.
- EMA20, RSI14 and MACD12/26/9 calculations are unchanged. Bollinger middle-band mean now shares the stable mean helper; normalized population variance and bands are unchanged. WebSocket code, chart UI and renderer are unchanged.
- This is numerical correctness work only; SMA20 remains 🟨 foundation.

### Verification
Initial exact-head Automated Tests run 44893124624 caught a missing normalized vector still required by Bollinger variance calculation (7 tests failed from the same ReferenceError; 248 passed). The vector has been restored without reverting the compensated middle-band mean. On corrected HEAD f70f0bcfe2208b4fbfb37440fe8dc3b740e8fbcc, frontend tests/build, CodeQL and full Git-history secret audit passed; backend tests and APK build remain in progress.

### Project and Gate 10 accounting
- Stage 1: 30/40 criteria = 75% provisional.
- Gate 10: 0/10 formally closed.
- 🟨🟩 host/owner verification only: Gates 8, 30, 34, 35, 39.
- 🟧 additional integration: Gates 20, 25, 31, 36, 38.
- Stages 2–6 and overall project percentage remain unscored.
- ZERO COST; no deployment, paid infrastructure, production credential, Termux/device command or `main` modification.


### Performance and shared-mean follow-up

- A local Node.js microbenchmark over 99,981 SMA20 windows from 100,000 ordinary positive-price samples measured the initial always-expansion implementation at approximately 200 ms versus approximately 26 ms for the previous normalized reducer.
- The implementation was optimized before acceptance: the normal path now uses a simple normalized sum, while the more expensive expansion is restricted to windows whose absolute normalized sum is less than half their total normalized magnitude.
- The same stable mean helper now calculates the Bollinger middle band, preventing the identical cancellation-order defect there.
- Re-running the same local microbenchmark measured approximately 25 ms for the optimized path. This is a local microbenchmark, not a CI performance guarantee; exact-head CI remains the acceptance gate.
