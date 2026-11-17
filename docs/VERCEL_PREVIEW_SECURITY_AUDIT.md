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
