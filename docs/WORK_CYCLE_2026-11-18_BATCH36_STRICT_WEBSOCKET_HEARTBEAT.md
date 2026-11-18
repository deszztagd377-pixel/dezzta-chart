# DEZZTA CHART — Batch 36: strict WebSocket heartbeat acknowledgement

**Date:** 18 November 2026 (WIB)  
**Branch:** `phase-2/market-data-foundation`  
**Parent exact HEAD:** `9c76726f031568fe126479f4aa3c34bf0d151e49`  
**Resulting exact HEAD:** `11d3ea4ba426b1da021bf0f9c79abdc0205b3c9d`  
**Scope:** fail-closed client validation for unsolicited and unsupported-version heartbeat pong frames  
**Cost:** ZERO COST  
**Deployment:** none  
**Main:** untouched

## 1. Audit finding

The prior client cleared its pong deadline for any JSON object whose `type` was `market_data.pong`. It did not require protocol version 1, a subscribed stream, or an outstanding ping. That allowed an unsolicited or malformed pong to satisfy the heartbeat acknowledgement path.

## 2. Source correction

The client now accepts a pong only when all three conditions hold:

1. The stream state is `subscribed`.
2. A heartbeat pong deadline is currently outstanding.
3. The pong envelope declares `version: 1`.

Any violation fails the stream closed through the existing error path. A valid pong clears only its own outstanding timeout. No server route, heartbeat cadence, timeout, authentication, reconnect, or data-delivery behavior was changed.

## 3. Regression coverage

Added frontend tests for:
- unsolicited version-1 pong before any heartbeat ping;
- unsupported pong protocol version after a ping has been sent.

Existing tests continue to cover text ping cadence, valid version-1 acknowledgement, timeout, timer cleanup, snapshot/replay, and sequence-gap behavior.

### Exact-head CI outcome

For exact SHA `11d3ea4ba426b1da021bf0f9c79abdc0205b3c9d`:
- Automated Tests [run 44317099110](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099110): failed only at step 27, final frontend dependency-audit enforcement. Steps 1–26 passed, including frontend unit tests and production build, backend tests, synthetic outbox benchmark, backend dependency audit, container build, Redis/persistent-volume smoke, Trivy scan and vulnerability-report export.
- Android debug APK build [run 44317099094](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099094): success.
- CodeQL [run 44317099846](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099846): success.
- Full Git History Secret Audit [run 44317099074](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/44317099074): success.

The final dependency enforcement is still blocked by the existing development-tooling `picomatch@4.0.7` advisory. Do not weaken or bypass the audit. This exact-head CI result validates the WebSocket regression tests and build, but does not establish deployed public WSS or Android runtime acceptance.

## 4. Engineering calculation

- Client cadence: (1/20 = 0.05) ping/s.
- Server rolling ceiling: (20/10 = 2) ping/s.
- Utilization: (0.05/2 = 0.025 = 2.5\%).
- Pong deadline: 10 s, equal to 50% of the 20 s cadence.
- Strict acknowledgement condition: 3/3 predicates must hold; otherwise fail closed.

## 5. Gate 36 boundary

This is a client protocol correctness improvement, not public transport acceptance. Gate 36 remains OPEN until public WSS Upgrade/ping-pong, Android WebView behavior, owner-observed 330-second session and platform close attribution, effective Fluid Compute read-back, and cross-instance fan-out are evidenced on an already authorized host. No new deployment is justified by this source-only correction.

## 6. Cost and device boundary

No Vercel deployment, Cloudflare resource, paid service, host/database/storage provisioning, billing change, or publication action. Termux is not required for this remote source/CI correction.

## 7. Progress accounting

No Stage 1 ticks or Gate 10 closures are awarded by source edits or CI results alone. Stage 1 remains 75% provisional (300/400 ticks; 30/40 criteria); Gate 10 remains 0/10 formally closed; open criteria remain 8, 20, 25, 30, 31, 34, 35, 36, 38, 39. Stages 2–6 remain unscored and overall project progress remains not established.
