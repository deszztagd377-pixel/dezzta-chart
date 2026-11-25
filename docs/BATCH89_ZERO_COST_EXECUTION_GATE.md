# Batch 89 — Zero-Cost Runtime Execution Gate

**Date:** 25 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Architecture:** Cloudflare Native / Zero-Origin  
**Purpose:** Make the next Batch 89 execution deterministic without deploying resources, introducing paid services, or changing application runtime code.

## 1. Repository evidence inspected

- Root `package.json` declares:
  - `test`: `vitest run`
  - `test:cloudflare-runtime`: installs pinned Miniflare `4.20260730.0`, performs a temporary dependency audit, then runs `node --test cloudflare/proof/worker.miniflare-test.mjs`.
  - `test:cloudflare-durable-objects`: installs pinned `@cloudflare/vitest-plugin@1.9.0`, then runs Vitest with `vitest.cloudflare.config.mts`.
- `vitest.cloudflare.config.mts` points Wrangler at `cloudflare/wrangler.jsonc`, binds a synthetic proof token for tests, includes only `cloudflare/proof/worker.durable-object.runtime.mjs`, sets test/hook timeouts to 15 seconds, and disables file parallelism.
- `cloudflare/wrangler.jsonc` explicitly sets `PROOF_MODE=synthetic-only`, `workers_dev=false`, `preview_urls=false`, localhost-only proof origins, and SQLite migration `v1` for `SeriesCoordinatorDO`.
- `scripts/report-npm-audit.mjs` fails closed for malformed/missing audit metadata, npm audit errors, and HIGH/CRITICAL advisories. It also checks the Undici dependency tree.

## 2. Execution environment gate

The project scripts are defined, but their execution has **not** been verified in the current work cycle. The GitHub connector used for this audit exposes repository contents and limited commit/PR status, not a repository checkout or command runner. No test result is inferred from the existence of scripts.

A valid zero-cost execution environment must provide:
1. A disposable checkout of this branch at the exact commit under test.
2. A supported Node.js/npm runtime compatible with the repository lockfile and Vitest version.
3. Outbound package-registry access for the pinned test-only packages (or an already-populated compatible cache).
4. No paid compute, hosted database, paid market-data feed, Cloudflare deployment, or Cloudflare resource creation.
5. Captured exit code and complete logs for every command; a missing log or interrupted run is NOT PASS.

Downloading public open-source packages may be zero monetary cost, but it is still a network/dependency prerequisite. Do not claim an offline run unless all dependencies are already present.

## 3. Ordered Batch 89 command matrix

Run from the repository root, after checkout and dependency installation are available. The six rows include setup and final hygiene checks; rows 2–5 are the four validation commands:

| Order | Command | Required evidence |
|---:|---|---|
| 1 | `npm ci` | Lockfile-resolved install exits 0; no lockfile mutation |
| 2 | `npm test -- --reporter=verbose` | Full app test output and exit code |
| 3 | `npm run build` | Production build output and exit code |
| 4 | `npm run test:cloudflare-runtime` | Audit gate and Miniflare integration test output |
| 5 | `npm run test:cloudflare-durable-objects` | workerd/Miniflare Durable Object test output |
| 6 | `git status --short` | No unintended tracked-file or lockfile modifications |

The repository's own scripts install their test-only Cloudflare dependencies. Before invoking them, record Node/npm versions and inspect lockfile consistency. Do not run multiple package-manager installs concurrently in the same checkout.

## 4. Batch 89 acceptance criteria

Batch 89 can be marked complete only when:
- all four validation commands (app tests, production build, Miniflare runtime tests, and Durable Object tests) have captured terminal results;
- each validation command exits 0;
- no unexpected lockfile or tracked-file changes remain;
- dependency audit does not report blocking HIGH/CRITICAL findings;
- the Worker test runtime actually loads the project's Wrangler configuration;
- Durable Object SQLite migration and test bindings initialize in the local test runtime;
- results are attached to the exact tested commit SHA.

A failed command must be diagnosed and rerun after a scoped fix. A test skipped, not run, timed out, or lacking logs remains OPEN. Do not substitute historical CI results or test declaration counts for current execution.

## 5. Downstream dependency order

After Batch 89 acceptance:
1. Batch 90 — implement and test SQLite schema/migration.
2. Batch 91 — implement provider-neutral API shell and contract tests.
3. Batch 92 — atomic durable event payload + digest + sequence/high-water, then bounded replay.
4. Batch 93 — authenticated ACK, durable monotonic receipts, RESUME/reconnect/resnapshot and eviction recovery.
5. Batch 94 — provider ingress only after lawful, compatible, genuinely zero-cost evidence.
6. Batch 95 — public WSS/TLS/browser/Android E2E and restore acceptance.

Do not advance downstream implementation past its dependency gates.

## 6. Safety and scope invariants

- Never modify `main`.
- Never deploy or create Cloudflare resources as part of this gate.
- Never add paid services, subscriptions, paid sandboxes, or paid market-data sources.
- Keep synthetic fixtures explicitly separate from live-data provenance.
- Do not represent a local proof Worker as production service.
- Preserve existing application behavior and indicator implementations.
- Batch 89 is runtime/toolchain validation; it earns no indicator implementation credit.

## 7. Current status

**🟨 Gate specification documented. 🟥 Runtime execution pending.**  
The exact current test/build results remain UNKNOWN / NOT VERIFIED. This document does not claim a test pass.
