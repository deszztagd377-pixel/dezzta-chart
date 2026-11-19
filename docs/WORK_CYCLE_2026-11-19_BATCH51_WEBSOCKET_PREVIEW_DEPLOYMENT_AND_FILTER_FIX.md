# Batch 51 — WebSocket preview deployment and Vercel ignored-build recovery

**Date:** 19 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Deployed source SHA:** `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`  
**Latest application source/test SHA included:** `b30ce94ca278e527731d86e40ddf06c6dbd16b5b`  
**Deployment:** `dpl_5VXGuNtmkxzWTDQkcGZgBrrL7WrK`  
**Preview URL:** https://dezzta-chart-ws-n3mvfjv0n-deszztagd377-pixel.vercel.app

## Objective

Deploy the verified Batch 50 WebSocket lifecycle correction to the isolated FastAPI POC preview, while avoiding an unnecessary Vite frontend deployment and preventing the POC's ignored-build filter from treating missing Git history as a changed source directory.

## Pre-deployment checks

- Active branch confirmed as `phase-2/market-data-foundation`.
- Exact current branch HEAD before this work was `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`.
- The WSS POC had no deployment for that SHA.
- Existing WSS POC was READY but deployed from older source `9873a5fd1c52a0cbab94683c0c309732407212e8`; it did not contain Batch 50.
- The frontend project was not selected for redeployment.

## Deployment result

- Created exactly one deployment, scoped to the isolated `dezzta-chart-ws-poc` project and the preview environment.
- Vercel read-back: **READY**.
- Deployment source SHA: `9961471f1d72e3d35b4bf3f4314171d7b5fe2b1a`.
- Python 3.12 was selected from `poc/vercel_ws/.python-version`.
- Dependencies were installed from `poc/vercel_ws/requirements.txt`.
- Build completed in approximately 4 seconds; deployment completed successfully.
- Project remains `live=false`; SSO protection remains enabled for all deployment targets.
- No production alias/promotion was performed.

## Ignored Build Step blocker and correction

### Observed

The previous ignored-build command attempted:

```sh
git diff --quiet "$VERCEL_GIT_PREVIOUS_SHA" "$VERCEL_GIT_COMMIT_SHA" -- ":(top)poc/vercel_ws/**" || exit 1
```

Vercel's shallow clone did not contain the previous commit object. The build log showed:

```text
fatal: bad object 9873a5fd1c52a0cbab94683c0c309732407212e8
```

This did not fail the deployment: the command returned the build-required path and Vercel proceeded. It did mean the POC path filter could not distinguish a documentation-only commit from a POC source change when the previous object was absent.

### Corrective project setting

Updated only the `dezzta-chart-ws-poc` project's `commandForIgnoringBuildStep` to:

```sh
git cat-file -e "$VERCEL_GIT_PREVIOUS_SHA^{commit}" 2>/dev/null || git fetch --no-tags --depth=1 origin "$VERCEL_GIT_PREVIOUS_SHA" >/dev/null 2>&1 || exit 1; git diff --quiet "$VERCEL_GIT_PREVIOUS_SHA" "$VERCEL_GIT_COMMIT_SHA" -- ':(top)poc/vercel_ws/**'
```

- Command length: **254/256 characters**.
- If the previous commit is already present, compare it directly.
- If absent, attempt one shallow fetch of that exact commit before comparing.
- If the fetch or comparison cannot be completed, exit non-zero so Vercel safely performs the build instead of incorrectly skipping it.
- If the POC directory has no changes and the comparison succeeds, exit zero and allow Vercel to skip the build.
- This is a settings-only correction; it does not alter application code, credentials, deployment protection, or billing.
- The currently READY deployment ran before this setting change took effect; a future eligible deployment is needed to verify the new filter behavior end-to-end. Do not trigger a second deployment just to test the filter.

## Post-deployment observations

- Deployment status read-back: **READY**.
- Runtime warning/error/fatal log query for the new deployment over the most recent 30-minute window: **no matching records**. This means no matching runtime logs were returned; it does not prove the endpoints were invoked or that the WebSocket transport was exercised.
- No owner-device authenticated browser WSS round-trip, Android WebView WSS, 330-second foreground lifetime test, effective Fluid Compute runtime read-back, or production fan-out test was performed in this cycle.
- The preview remains synthetic POC infrastructure, not a production market-data service.

## Progress and gate disposition

- Stage 1: **30/40 criteria; 300/400 ticks; 75% provisional**. No ticks awarded for deployment or documentation.
- Gate 10: **0/10 formally closed**.
- Open external criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Gate 36 remains OPEN; deployment readiness is only one sub-check and is not live transport acceptance.
- Stages 2–6: NOT SCORED.
- Overall project percentage: NOT ESTABLISHED; 20.9% remains historical only pending approved M1–M8 scoring.
- ZERO COST maintained. No paid plan, billing activation, paid provider, production credential, or Termux operation.
- Protected `main` untouched.

## Next engineering work

1. Use the READY SSO-protected preview for an owner-observed WSS lifecycle trace; do not weaken SSO or publish a bypass.
2. Keep the maximum-duration, native Android WebView, independent Fluid Compute, and cross-instance checks separate from the synthetic CI proof.
3. Validate the revised ignored-build filter naturally on a future relevant push; do not create a throwaway deployment.
4. Continue Gate 10 blockers in dependency order, without awarding progress for deployment-only evidence.
