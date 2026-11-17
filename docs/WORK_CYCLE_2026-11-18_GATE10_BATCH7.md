# DEZZTA CHART — Gate 10 Batch 7: WebSocket Lifetime and Vercel Hobby Limits

Date: 2026-11-18  
Working branch: `phase-2/market-data-foundation`  
Scope: Gate 36 — isolated synthetic WebSocket POC  
Cost policy: ZERO COST; no plan upgrade, paid service, or billing activation.

## Executive result

The Vercel WebSocket platform blocker is now narrowed to a documented runtime-lifetime constraint, not an inability to deploy or an unsupported transport.

- The dedicated FastAPI WebSocket POC deployment is **READY** and remains protected by SSO for all deployment targets.
- The main Vite frontend deployment is also **READY**.
- Vercel WebSocket support is generally available as of 2026-10-20.
- Vercel documents that a WebSocket connection is pinned to the Function instance and closes when the Function reaches its maximum duration. Clients must reconnect; durable shared state cannot rely on one Function instance's memory.
- The Vercel team plan remains Hobby. With Fluid Compute, the documented Hobby default and maximum function duration are both **300 seconds (5 minutes)**. Hobby cannot raise this maximum.
- The source POC explicitly requests Fluid Compute using `poc/vercel_ws/vercel.json` with `"fluid": true`. The project settings API read-back still does not expose an independently verifiable effective Fluid Compute flag.

**Gate 36 remains OPEN.** The browser HTTP health, WebSocket handshake, ping/pong, manual reconnect with a fresh session, and idle timeout have already been owner-observed and recorded in the prior report. This batch does not claim a platform maximum-duration close, independent runtime setting read-back, Android Capacitor WebView acceptance, or production cross-instance fan-out.

## Verified repository and deployment state

- Exact active branch head at audit time: `de90b32a87111458f9225cc5151a59420f1fe8fb`.
- The branch is `phase-2/market-data-foundation`; `main` was not modified.
- Dedicated WSS POC: `dpl_5soNcXQGktR397joj26jcwe7Voas`, **READY**, source commit `cfc56b7ba050201823952ea1b67dd38182dc9bfb`.
- Main Vite frontend: `dpl_BzAaDUru7yhSX2pEWRt8EGxLLpdk`, **READY**, source commit `545334d9a594b58c19168df1b059f44ed520949c`.
- POC deployment protection: SSO enabled for **all** deployment targets.
- Frontend deployment protection: SSO enabled for all targets except custom domains.
- Both projects are non-production preview projects (`live=false`); no production alias was promoted in this audit.

The latest POC deployment is from the last source/test commit, not the latest docs-only commit. The frontend deployment is also an earlier known-good build. READY confirms those specific deployments; it does not prove remaining account quota or guarantee that a future build cannot encounter a rate limit.

## WebSocket lifetime calculation

| Item | Hobby / POC value | Meaning |
|---|---:|---|
| Fluid Compute default function duration | 300 s | Default maximum request/function lifetime |
| Fluid Compute Hobby maximum | 300 s | No Hobby headroom to increase it |
| Equivalent time | 5 min | Expected upper bound for a single function invocation |
| POC application idle timeout | 25 s | Current POC closes an idle socket well before the platform limit |
| Gap between idle close and platform cap | 275 s | A quiet connection cannot currently reach the platform cap |

The POC's existing 25-second idle timeout means that simply leaving the browser tab open will **not** test Vercel's 300-second maximum. A valid maximum-duration probe must keep the synthetic connection active at intervals shorter than 25 seconds, record connection-open time, and capture the close event. The probe must remain synthetic-only and protected by SSO.

## Safe bounded test design

The next platform-lifetime probe must be isolated to the disposable POC and must not connect production market data.

1. Keep the current 25-second server idle timeout unchanged unless a test-specific configuration explicitly requires otherwise.
2. Use a test-only client heartbeat interval with a comfortable margin below 25 seconds (for example, 10 seconds) so the server does not close the connection for idleness.
3. Record the browser-side monotonic connection start time, each synthetic pong, and the final WebSocket close code/reason. Do not log credentials, tokens, owner IDs, or private account data.
4. Prefer a temporary, lower `maxDuration` override on the POC preview (for example, 60 seconds) to prove the platform-triggered close with a bounded observation window. This tests the platform close mechanism but **does not** independently prove the full 300-second Hobby ceiling.
5. If the 60-second cap is not independently confirmed in the build/runtime configuration, do not claim a platform close test. Use a single controlled 300-second maximum-duration observation only after confirming the current Hobby usage allowance and ensuring no paid billing is activated.
6. Keep SSO enabled for every deployment target. Do not create a protection-bypass URL, public test route, custom domain, or production alias.
7. After a platform close, the production client design must reconnect with bounded exponential backoff, resubscribe to the exact stream, resume from a durable cursor, deduplicate replay/live overlap, and resnapshot if replay is unavailable.

A 60-second preview cap is a proposed test configuration, not yet applied. No deployment or long-lived connection test was triggered in this batch.

## Architectural consequence and existing reconnect implementation

A Vercel Hobby WebSocket can be used for short-lived realtime sessions, but it must not be treated as a permanent socket or durable worker.

**The production frontend already implements the client reconnect state machine** in `src/services/ohlcvStreamSupervisor.ts`; this audit confirmed the code and existing regression tests. It already provides:

- bounded exponential retry with jitter;
- fresh Firebase ID-token acquisition on every connection attempt;
- resume from the last validated durable cursor;
- chart-state preservation while reconnecting;
- replay validation and sequence continuity before returning to live updates;
- fresh snapshot recovery after sequence gaps;
- terminal handling for authentication, authorization, and malformed-subscription close codes;
- cancellation of pending retries when the stream is explicitly stopped.

Existing supervisor tests cover transient transport interruption, token-provider failure, fresh-token retry, durable-cursor replay, sequence-gap recovery, terminal authorization rejection, error/close races, and explicit stop. The backend also already contains durable outbox/replay and exact-series subscription behavior.

**Still not proven externally:** deployed Vercel maximum-duration close, native Android Capacitor WebView behavior, independently read-back effective Fluid Compute, and production cross-instance state/lease/fan-out. A synthetic POC ping/pong does not prove production market-data delivery.

## Work completed in this batch

- Re-read the active branch head and confirmed it is still the expected docs checkpoint.
- Re-read the isolated POC implementation and its explicit Fluid Compute request.
- Re-read both Vercel project records and both latest deployment records.
- Confirmed the current Hobby duration ceiling from Vercel's published Fluid Compute documentation.
- Identified why the current 25-second idle timeout prevents a 300-second platform-lifetime test.
- Produced this bounded test plan without changing runtime code, Vercel settings, deployment state, billing, or the production application.

## Gate 10 and project progress accounting

No acceptance ticks are awarded in this batch.

- Stage 1: **300/400 ticks = 75% provisional**.
- Gate 10: **0/10 external criteria formally closed**.
- Still-open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Gate 36: browser transport sub-checks remain passed; platform maximum-duration close, effective Fluid Compute read-back, Android WebView acceptance, production cross-instance fan-out, and cost/operational acceptance remain open.
- Stages 2–6: **NOT SCORED**.
- Overall 20.90%: historical checkpoint only; not recalculated.
- ZERO COST preserved. No Termux use or installation is needed for this remote repository/configuration audit.

The six-stage colored dashboard and Stage 1 ten-gate dashboard remain the authoritative project-process progress visuals. This document is a supporting work-cycle report, not a replacement dashboard and not an in-APK indicator.

## Files changed

- `docs/WORK_CYCLE_2026-11-18_GATE10_BATCH7.md` — added.

## Verification boundary

This is a documentation-only commit. It does not claim that a new source test ran, a new Vercel deployment was created, the maximum-duration close was observed, or Gate 36 was closed.


## Vercel build-rate-limit status clarification — 2026-11-18

The GitHub combined status for source commit `cfc56b7ba050201823952ea1b67dd38182dc9bfb` still reports the main Vite preview context as **FAILURE** with Vercel's build-rate-limit target URL. The dedicated FastAPI WSS POC preview context is **SUCCESS**. Separately, Vercel project/deployment read-back shows the last existing main Vite deployment `dpl_BzAaDUru7yhSX2pEWRt8EGxLLpdk` is **READY** (built from `545334d9a594b58c19168df1b059f44ed520949c`). These statements refer to different objects: a failed attempt to create a new preview for the later source commit versus a previously completed READY deployment. No retry, plan upgrade, billing activation, or deployment was triggered to bypass the rate limit. The current Vite preview remains available at its known READY deployment, but a new preview for the latest branch HEAD is not verified.


## Batch 7 implementation addendum — bounded synthetic lifetime probe

The previously documented blocker (the POC's 25-second idle timeout closing before Vercel's 300-second Hobby Fluid Compute maximum) has now been addressed in repository code without changing the server idle timeout or exposing a new route.

### Runtime change

- `poc/vercel_ws/index.py` now includes an explicit owner-started **bounded 330-second synthetic lifetime probe** button.
- While active, it sends one synthetic ping every 10 seconds. This is below half the 25-second server idle timeout and far below the existing server message-rate cap of 12 messages per 10-second window.
- It records monotonic elapsed time, heartbeat interval, probe start/stop, WebSocket close code/reason, and whether the client-side 330-second limit ended the probe.
- The client stops the interval and deadline timer on socket close or manual disconnect. At 330 seconds it closes its own socket with a distinct normal-close reason.
- The probe remains opt-in, synthetic-only, bounded, and protected by the existing Vercel deployment SSO. No server timeout was lengthened; no production data, credential, account, Redis, or database path was added.
- A regression contract test was added at `backend/tests/test_vercel_ws_probe_contract.py`. It checks that the heartbeat remains at most half the server idle timeout, the client probe exceeds 300 seconds but is capped at 360 seconds, and timing/close instrumentation remains present.

### Calculation and expected interpretation

- Server idle timeout: 25 seconds.
- Heartbeat interval: 10 seconds (15-second nominal safety margin; 2.5× faster than the idle timeout).
- Vercel Hobby Fluid Compute documented maximum: 300 seconds.
- Client-side bounded probe: 330 seconds (30-second observation margin beyond the documented platform maximum).
- Server message rate cap: 12 messages per 10 seconds; probe emits approximately 1 message per 10 seconds, leaving substantial margin.

A close near 300 seconds with a platform-originated close signature would support the maximum-duration finding. A close at 25 seconds indicates heartbeat delivery/idle handling failed. A client close at 330 seconds is only the probe's own safety bound and is **not** evidence that Vercel closed the connection. The probe has been implemented but has **not yet been executed against a new deployment**. No Gate 36 ticks are awarded yet.

### Verification boundary

- The new Python regression test is committed but its CI execution is pending at this report checkpoint.
- No Vercel deployment, 330-second observation, production connection, billing action, or plan upgrade was initiated by this code change.
- The existing main Vite preview build-rate-limit status remains separate from the dedicated WSS POC preview status.
- Gate 36 remains OPEN pending deployed observation, effective Fluid Compute read-back, native Android WebView test, and production cross-instance fan-out/cost acceptance.


## Protected POC preview deployment result — 2026-11-18

The isolated POC source and regression contract test were deployed by the repository's existing Vercel Git integration:

- Deployment: `dpl_EV3ScKYRdCA2X4seYFktuuoQgDx6`
- State: **READY**
- Source commit: `08263d49ab12fd2195515d673b9e84588dcbac57`
- Preview URL: `https://dezzta-chart-ws-qywwkeiui-deszztagd377-pixel.vercel.app`
- Alias: `https://dezzta-chart-ws-poc-git-phase-2-marke-513321-deszztagd377-pixel.vercel.app`
- No production alias was promoted. This is the isolated synthetic POC preview only.

This confirms the updated POC has a READY deployment. It does **not** mean the 330-second probe has been run or that a Vercel 300-second platform close has been observed. Deployment SSO remains the existing access boundary; do not weaken or bypass it. The main Vite preview context on the same source was canceled from the Vercel Dashboard; the previously known frontend READY deployment remains distinct from this WSS POC deployment.


## CI dependency-audit blocker — 2026-11-18

The final exact-HEAD Automated Tests run `44203187496` on branch head `94f2580b63176e1d871fcb2bb7175ca4f26285c2` failed at **Audit frontend dependencies** before frontend unit tests or backend tests could run. The log identifies five High findings in the dependency tree, all through `picomatch@4.0.7` (transitively used by dev-only `fdir`, `tinyglobby`, Vite `6.4.5`, and Vitest `4.1.12`). The lockfile marks these dependencies as `dev: true`; they are not declared production dependencies.

The relevant current GitHub Advisory is GHSA-fc5q-39xc-vjpf / CVE-2026-112366, a reported ReDoS in repeated single-branch extglob patterns. The advisory lists no patched version. The public npm registry currently lists `picomatch@4.0.7` as latest. Upstream remediation PR #235 was closed without merge; PR #238 remains open and its own description documents a narrower fix with known limitations. The advisory and upstream state are recorded here:

- [GitHub Advisory GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf)
- [picomatch issue #247 — release/remediation guidance](https://github.com/micromatch/picomatch/issues/247)
- [picomatch PR #238 — narrow single-branch guard](https://github.com/micromatch/picomatch/pull/238)
- [npm picomatch package and current published version](https://www.npmjs.com/package/picomatch)

**Remediation decision:** no `npm audit fix --force`, no Vitest downgrade, no guessed override to an affected version, no suppression of the High finding, and no production-audit weakening. There is no verified patched release to install. The dependency audit therefore remains honestly blocked by upstream package remediation. The dependency is currently dev-only and the application does not expose a user-supplied glob-pattern API; this reduces application runtime exposure but does not make the advisory disappear or justify marking the audit PASS.

The CI run stopped at npm audit, so frontend tests/build and backend tests were skipped in that run. Gitleaks history scan passed. The separate Git-history secret audit run `44203187501` passed. CodeQL was still pending at last read-back. Do not describe this source head as fully CI-green.

No Stage 1 ticks are awarded for this batch. Gate 10 remains 0/10 formally closed; Stage 1 remains 300/400 = 75% provisional. This is a newly surfaced internal dependency-security blocker that must be revisited when upstream publishes a verified fix or when a thoroughly tested alternative glob stack is approved.
