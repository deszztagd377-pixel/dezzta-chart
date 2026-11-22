# DEZZTA CHART — Work Cycle 62J-141
## WebSocket supervisor ownership, delayed-close regression and OCI ARM64 readiness

Date: 22 November 2026  
Branch: `phase-2/market-data-foundation`  
Documentation parent/source-test baseline: `f0c55e37998c2c32c3ba0aeab743bbe02e0c72d7`  
ZERO COST: no cloud account/resource, deployment, paid service, production credential, payment method, device operation or `main` change.

## 1. WebSocket supervisor ownership correction

The shared `marketDataStore` is a singleton. A chart-selection replacement must therefore not leave two supervisors capable of publishing into that store.

The supervisor now enforces a single active owner:
- Starting a replacement supervisor stops the previous owner first.
- The previous owner cannot clear or overwrite the replacement selection's snapshot during late cleanup.
- A superseded supervisor's queued messages are ignored by its stopped-state guards.
- The new selection starts with its own loading snapshot and publishes only its validated series.

Runtime file: `src/services/ohlcvStreamSupervisor.ts`.

## 2. Regression coverage

`src/services/ohlcvStreamSupervisor.test.ts` now covers:
1. Replacement while the previous Firebase ID-token request is still pending. The old request is cancelled; its late resolution cannot create a socket.
2. Timeframe replacement while the old browser WebSocket remains in CLOSING. The new 1m supervisor publishes its own snapshot; a late old message and delayed native close cannot damage that snapshot.

A first CI attempt exposed a test assertion mismatch: the assertion compared the raw protocol bar with the normalized candle object stored by the application. The runtime path was not the failing component. The assertion was corrected to compare the normalized candle representation. The full Automated Tests workflow subsequently passed on the exact source/test baseline below.

## 3. Exact-source-commit CI

Source/test and workflow baseline: `f0c55e37998c2c32c3ba0aeab743bbe02e0c72d7`.

- Automated Tests [45000228409](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000228409): **SUCCESS**.
- CodeQL [45000228422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000228422): **SUCCESS**.
- Full Git History Secret Audit [45000228438](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000228438): **SUCCESS**.

Automated Tests include frontend unit tests/build and secret checks, backend tests, Redis TLS CA/hostname fixture, bounded SQLite outbox and metrics checks, backend dependency audit, backend container build, shared-Redis/persistent-volume smoke test, and image scan/report.

These checks establish repository CI only. They do not establish public WSS, production Firebase, a provisioned OCI host, or real Android WebView/network-handover acceptance.

## 4. OCI ARM64 readiness — native build lane

The repository already contains the OCI Always Free due-diligence record in `docs/WORK_CYCLE_2026-11-22_BATCH62J118_OCI_ALWAYS_FREE_AND_WEBSOCKET_GATE10_READINESS.md`.

New workflow: `.github/workflows/oci-arm64-readiness.yml`.

It uses GitHub's native `ubuntu-24.04-arm` runner and is intended to:
- prove the runner and built backend image are ARM64;
- start the backend and verify `/health`;
- verify the application runs as UID 10001;
- verify the application user can write to the mounted data volume;
- restart the container and verify the volume data remains available.

The corrected native ARM64 workflow [45000816460](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45000816460) completed **SUCCESS** on exact HEAD `0372d488e1fd803343a06234105295b9675a3e0b`. It verified the native ARM64 runner, built the backend image as `arm64`, confirmed the backend health endpoint, verified PID 1 runs as UID 10001, proved that UID 10001 can write to the mounted persistent volume, restarted the container, and confirmed the probe file remained available. This is ARM64 image/runtime smoke evidence on GitHub-hosted CI; it is not an OCI account, VM, public WSS endpoint or production deployment.

GitHub documents standard ARM64 hosted runners as free and unlimited for public repositories:
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://github.blog/changelog/2025-01-16-linux-arm64-hosted-runners-now-available-for-free-in-public-repositories-public-preview/

This is a zero-cost CI architecture check, not OCI provisioning or deployment.

## 5. OCI account and resource boundary

OCI means Oracle Cloud Infrastructure. Its Always Free resources remain conditional on current tenancy eligibility, home-region capacity, resource quotas and terms. No account or cloud resource was created in this work cycle.

Because the project operator is a minor, any OCI account eligibility, signup, identity/card verification, billing controls and resource ownership must be handled by a parent/guardian as the lawful account owner, with their consent. Do not share credentials, payment information, private keys or account recovery material in chat. No Pay As You Go upgrade, trial-credit dependency, paid domain, paid DNS, paid load balancer or paid managed service is permitted under ZERO COST.

The repository-only work can prepare and verify an ARM64 image; it cannot install an OCI server without the account owner's separately authorized provisioning.

## 6. WebSocket gates and production boundary

- Gate 25: **OPEN** — authenticated immutable snapshot-installation receipt, receipt custody, owner-host Redis TLS/ACL, persistence and restart/failover remain unaccepted.
- Gate 36: **OPEN** — public hostname, trusted WSS/reverse-proxy path, live Firebase identity/entitlement and real browser/Android WebView lifecycle/network handover remain unaccepted.
- Gate 38: **OPEN** — owner-host durable metrics, retention, dashboards, alert delivery and recovery drill remain unaccepted.
- Other open Stage 1 tracks: Gates 8, 20, 30, 31, 34, 35 and 39.
- Gate 10: **0/10 external criteria formally closed**.

Internal CI, synthetic tests, an ARM64 build, and documentation do not close external host/production gates.

## 7. Complete technical indicator ledger

No indicator formula, hook, renderer, UI or indicator test source changed in this work cycle. No indicator implementation credit is awarded.

| Indicator/component | Status | Verified foundation and remaining work |
|---|---|---|
| SMA20 | 🟨 Foundation | 20-close arithmetic mean; first valid index 19; chart integration and edge-case acceptance remain |
| EMA20 | 🟨 Foundation | SMA-seeded EMA, alpha 2/21; first valid index 19; chart integration and edge-case acceptance remain |
| RSI14 Wilder | 🟨 Foundation | Wilder smoothing; first valid index 14; numerical edge cases and chart integration remain |
| MACD12/26/9 | 🟨 Foundation | MACD first valid index 25; signal/histogram first valid index 33; chart integration remains |
| Bollinger20,2 | 🟨 Foundation | 20-close mean ±2 population standard deviations; first valid index 19; chart integration remains |
| Shared Indicator Hook | 🟨 Foundation | Backend snapshot/aligned calculation output; full chart integration remains |
| Footprint | 🟧 Prototype only | Synthetic educational accumulator, not exchange-native bid/ask truth; reference image(s) and reviewed blueprint required before visuals |
| Heatmap | 🟥 Not implemented | Reference image(s), validated data contract and reviewed blueprint required before visuals |
| Liquidation Maps | 🟥 Not implemented | No implementation evidence; data contract and renderer remain |

Mandatory invariants:
- Warm-up values remain null, not zero.
- Outputs stay aligned to originating candle indices.
- Prefix causality: adding future candles cannot alter earlier indicator values.
- Invalid/missing/gapped bars are never silently converted to zero.
- Stale output clears on symbol, venue, dataset, chart and timeframe identity changes.
- Calculation, chart rendering, interaction, lifecycle and performance are separate acceptance dimensions.
- Footprint OFF preserves standard candle spacing; only explicit ON enables the dedicated spaced-cluster layout.
- Footprint and Heatmap visuals remain blocked until the user supplies reference image(s) and reviews the scoped blueprint.
- Aggregate indicator completion remains NOT SCORED because indicator weights and denominator are not approved.

## 8. Project-wide progress indicator

Legend: 🟩 accepted; 🟨 partial/provisional; 🟧 prototype; 🟥 not implemented; ⬜ not scored/not opened.

| Official stage | Current progress | Status |
|---|---:|---|
| 1. Foundation, Security & Data Integrity | 30/40 criteria = 75% provisional | 🟨 |
| 2. Market Data Infrastructure | Not scored / not officially opened | ⬜ |
| 3. Chart Engine & Timeframe | Not scored / not officially opened | ⬜ |
| 4. Indicators & Analytics | Not scored / not officially opened | ⬜ |
| 5. Professional UI & Interactive Tools | Not scored / not officially opened | ⬜ |
| 6. Hardening, Validation & APK Release | Not scored / not officially opened | ⬜ |

Overall project: **NOT SCORED**. The six-stage weights and overall acceptance denominator have not been approved. Stage 1's 75% must not be presented as the whole-project percentage.

## 9. IPS35 — Indicator Proses Peningkatan Proyek Signifikan

IPS35 measures verified cycle delivery quality, not overall project completion. The ARM64 readiness workflow is now accepted by its native CI smoke test. The final numeric score remains **PENDING** until this documentation commit receives exact-HEAD Automated Tests, CodeQL and Secret Audit. No points are awarded in advance for a pending workflow.

Scoring dimensions:
- Engineering delta: 25 points.
- Exact-commit automated/security CI: 20 points.
- Blocker isolation/reduction: 20 points.
- Complete canonical documentation: 20 points.
- ZERO COST, branch and scope integrity: 15 points.

## 10. Integrity and next acceptance sequence

- Active branch remains `phase-2/market-data-foundation`.
- `main` remains untouched.
- No new dependency or database/schema migration.
- No production credentials or secrets added.
- No paid service, cloud resource, account or deployment.
- No device or Termux operation.

Next:
1. Verify the corrected native ARM64 readiness workflow on the final documentation HEAD.
2. Continue WebSocket stale-callback and lifecycle acceptance without changing the authenticated ticket contract.
3. Keep Gate 25 receipt schema/trust implementation approval-gated.
4. Complete real owner-host and public WSS acceptance only through a separately authorized adult-owned zero-cost environment.

**Final status:** supervisor ownership and delayed-close regression coverage are implemented; exact-source CI passed; ARM64 image build passed but its first smoke test failed and the corrected smoke rerun remains pending; WebSocket production gates remain open; Stage 1 remains 75% provisional; Gate 10 remains 0/10; overall project and aggregate indicator completion remain not scored.
