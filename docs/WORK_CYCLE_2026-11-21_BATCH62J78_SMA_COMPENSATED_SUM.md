# DEZZTA CHART — Batch 62J-78
## Compensated SMA cancellation accuracy

**Date:** 21 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Base source/test HEAD:** `e6fd0dcb8d27be85b4fa32bc6b82a1495403e8e8`

### Defect found
Batch 62J-77 prevented avoidable intermediate overflow by normalizing each SMA window. A further adversarial ordering showed that a tiny normalized residual could still be rounded away by ordinary summation:

- Inputs: `[Number.MAX_VALUE, 1, -Number.MAX_VALUE]`
- Exact arithmetic mean: (1/3)
- Plain normalized reduction: loses the (1/Number.MAX_VALUE) residual and returns zero.

### Correction
- Added an error-free floating-point expansion sum for normalized window terms.
- Retained scale normalization, finite-result guard, warm-up nulls and source-index alignment.
- Added regression tests for both `[MAX_VALUE, 1, -MAX_VALUE]` and `[MAX_VALUE, -MAX_VALUE, 1]`.

### Complexity and scope
- Time complexity remains O(N × P); expansion storage is O(P) for each window.
- For SMA20, each window contains 20 values. No arbitrary-period controls are introduced.
- EMA20, RSI14, MACD12/26/9, Bollinger20,2, WebSocket code, chart UI and renderer are unchanged.
- This is numerical correctness work only; SMA20 remains 🟨 foundation.

### Verification
Exact-head CI must pass before this batch is considered accepted. No test, build, security or artifact result is assumed in advance.

### Project and Gate 10 accounting
- Stage 1: 30/40 criteria = 75% provisional.
- Gate 10: 0/10 formally closed.
- 🟨🟩 host/owner verification only: Gates 8, 30, 34, 35, 39.
- 🟧 additional integration: Gates 20, 25, 31, 36, 38.
- Stages 2–6 and overall project percentage remain unscored.
- ZERO COST; no deployment, paid infrastructure, production credential, Termux/device command or `main` modification.

