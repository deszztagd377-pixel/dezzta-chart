# DEZZTA CHART — Vercel Preview Security & Build Audit

Audit date: 2026-11-17  
Repository: `deszztagd377-pixel/dezzta-chart`  
Branch: `phase-2/market-data-foundation`  
Exact audited HEAD: `3003226c982c2a51b52d6a4f5f64b1794c625ff0`  
Vercel project: `dezzta-chart` (`prj_fQDJUEVZbQPdNsbfk7erQVo8Ek8V`)  
Plan: Hobby

## Scope

Read-only inspection of GitHub visibility, exact branch HEAD, GitHub Actions, Vercel project metadata, deployment metadata and build events. No Vercel settings, domains, environment variables, deployment protections, source files or workflows were changed or retriggered.

## Repository visibility

GitHub reports `private: false`: the repository is **public**. Source code, commit history and tracked documentation are publicly readable. Vercel deployment protection does not make GitHub source private. Do not store credentials, tokens, production secrets or private operational notes in tracked files. The full-history secret audit passed, but that does not make publishing secrets safe.

## Vercel protection

| Control | Observed state |
|---|---|
| SSO protection | Enabled |
| SSO scope | `all_except_custom_domains` |
| Password protection | Disabled |
| Trusted IP restrictions | Disabled |
| Plan | Hobby |
| Framework | Vite |
| Linked repo | `deszztagd377-pixel/dezzta-chart` |

No protection setting was changed. The explicit custom-domain exception means custom-domain protection must be checked separately; do not assume it inherits this SSO scope. No temporary bypass/share URL was generated.

## Exact deployment

| Field | Value |
|---|---|
| Deployment | `dpl_5LXiSDH7jKh3dnvxfCywaRjfYbJs` |
| State | **READY** |
| Target | Preview (`target: null`), not proven production |
| Commit | `3003226c982c2a51b52d6a4f5f64b1794c625ff0` |
| Branch | `phase-2/market-data-foundation` |
| URL | `https://dezzta-chart-1gjh7czan-deszztagd377-pixel.vercel.app` |

This is a Vite frontend preview, not proof of deployed FastAPI, authenticated WSS, Firebase, Redis, durable storage or live market data. The repository has no root Python `api/` entrypoint or root `vercel.json`. The project-read response did not expose Root Directory or Fluid Compute settings; both remain unverified for this Vite project.

## Build findings

- Vite 6.4.5; 1,526 modules transformed.
- Build completed successfully in approximately 6 seconds.
- Main JS chunk: 537.43 kB minified (approximately 152.06 kB gzip), above the 500 kB warning threshold.
- npm emitted an unknown `cache-dir` configuration warning.
- npm reported install scripts not covered by its allowlist for `@firebase/util`, `esbuild`, and `protobufjs`.

These warnings were non-fatal; deployment reached READY. No warning was hidden by increasing the threshold and no install script was automatically approved. Investigate package/runtime impact before changing dependencies or script permissions.

## Visual QA boundary

The available Vercel connection returned project/deployment metadata and build events, not an authenticated rendered-browser screenshot or interactive browser session. Assistant visual inspection is **not claimed**. A screenshot supplied in this chat can be inspected without making the deployment public.

## Next safe sequence

1. Preserve the current Vite project and protection settings.
2. Put a synthetic-only FastAPI/WebSocket proof of concept in a dedicated repository subdirectory and a separate Hobby Vercel project.
3. Configure SSO protection before the POC's first deployment; do not create public bypass links.
4. Verify Fluid Compute, HTTP health, WebSocket upgrade, connection lifetime, disconnect, reconnect and replay.
5. Do not attach production Firebase, Redis credentials, provider data, SQLite records or notification workers.
6. Stop if the free Hobby allowance is insufficient; do not upgrade or enable a paid trial.

## Gate accounting

This audit adds evidence but closes no Gate and earns no Stage 1 tick:
- Stage 1: **300/400 = 75% provisional**.
- Gate 10: **0/10 formally closed**; ten external acceptance criteria remain open.
- Stages 2–6: **NOT SCORED**.
- Overall: **20.90% historical checkpoint only**; no fresh weighted calculation.
- Termux: not required for this remote audit.
- Zero-cost: preserved.

## 2026-11-17 follow-up — exact commit `ce079f8402a08b2d3bcdf64c3c80f41b8230fffd`

- Vercel main Vite preview `dpl_3NqxWPshEa9cNVKjmFiYtrs23gjJ`: **READY**.
- Vercel FastAPI POC preview `dpl_Ns63oEgDLBVYaSBrjcFefiNGXKY3`: **READY**; protected by project SSO for all deployment targets.
- Vercel FastAPI POC staging deployment `dpl_EJgJNiLxZxupJYSGo4M2SH14oYTF`: **READY**.
- No custom domain or temporary protection-bypass URL was created for the POC.
- The available Vercel runtime-log query returned no records for the POC deployment during the last 50-minute window. This means no live HTTP/WSS test request has yet been observed; it is not a failed test.
- Project update explicitly requested Root Directory `poc/vercel_ws`, Fluid Compute enabled, and 60-second default function timeout. Build logs prove Python 3.12 and requirements were read from the POC subdirectory. The project read-back omits the Fluid Compute flag, so it remains **not independently verified**.
- Main Vite bundle split is described in the project progress documentation. No security settings on the main Vite project were changed.
- Exact commit CI: Automated Tests & Build run `44063590646` SUCCESS; CodeQL `44063590667` SUCCESS; Full Git History Secret Audit `44063590758` SUCCESS; Android debug APK build `44063590583` SUCCESS.
- The Android APK artifact is a temporary CI artifact, not a public Play Store release. It expires 2026-11-24. SHA-256 of the extracted APK: `4db7a2898cd028154f6e282a9d514e83732ec89f4aebdf9d821f27da73c0a16e`.

No Stage 1 ticks are awarded from deployment readiness or APK generation. Gate 36 remains open until a protected live HTTP/WSS request, ping/pong and reconnect test are observed.
