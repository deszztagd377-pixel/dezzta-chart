# Stage 1 — Gate 10 Acceptance Addendum (Batch 10)
 
**Date:** 18 November 2026  
**Branch:** `phase-2/market-data-foundation`

## New source-level correction

The isolated synthetic WebSocket POC now treats the server's `idle_timeout` message as a notification that closure is imminent, not proof that the browser socket is already closed. The UI reports **“Idle timeout — waiting for close”** and waits for the browser's `close` event before transitioning controls to the disconnected state.

This prevents the UI from getting ahead of the actual WebSocket lifecycle and complements the earlier transport-error correction.

### Changed files

- `poc/vercel_ws/index.py`
- `backend/tests/test_vercel_ws_probe_contract.py`

### Commit chain

- Source correction: `8e43e8f0975130a96f4858df69d4d487a5bf97d8`
- Test assertion added: `b804a23147316483589883d66d6cd2c1c13c7274`
- Test assertion made deterministic: `84d30fdb81e13dc16083b60346b8cdba83d2956e`
- Test block-boundary correction: `21e76a2a2c45e0462a9c6e99d3c1c42b17b5eed7`

### Verification status

- Source and test files read back from the active branch after the final commit.
- Test execution: **NOT VERIFIED**.
- New Vercel deployment: **NOT VERIFIED / NOT TRIGGERED**.
- No Gate 36 closure or Stage 1 score increase is claimed.

## Gate 10 ledger — unchanged

| Criterion | Status |
|---:|---|
| 8 | OPEN |
| 20 | OPEN |
| 25 | OPEN |
| 30 | OPEN |
| 31 | OPEN |
| 34 | OPEN |
| 35 | OPEN |
| 36 | OPEN |
| 38 | OPEN |
| 39 | OPEN |

**Gate 10: 0/10 formally closed.**  
**Stage 1: 300/400 ticks = 75% provisional.**  
**Stages 2–6: NOT SCORED.**

The next Gate 36 proof requires a controlled 330-second observation, effective Fluid Compute configuration read-back, Android WebView compatibility, cross-instance fan-out, and cost/operational acceptance. A client-side 330-second timer alone is not evidence that the platform allowed the connection to run for that duration.
