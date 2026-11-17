# DEZZTA CHART — Gate 38 observability hardening work cycle

Date: 2026-11-17  
Branch: `phase-2/market-data-foundation`  
Base head: `30389f7fc1dc6627a1e13e03fd8daffeed0e1f7a`  
Protected `main`: untouched

## Objective
Harden the existing bounded, process-local HTTP metrics collector against malformed and pathological duration/label inputs. This is repository-level reliability work for Gate 38, not external production acceptance.

## Changes
- `backend/app/observability.py`: type-check method labels before membership lookup; reject boolean status codes; normalize boolean, string, NaN, ±infinity and unconvertibly large integer duration samples; clamp finite durations to 86,400,000 ms so one pathological sample cannot inject infinity into the accumulated sum or break JSON serialization.
- `backend/tests/test_observability.py`: add regression coverage for NaN, infinities, booleans, strings, unhashable method labels, boolean status codes and extreme finite durations.
- Preserve the 127-series hard cap, overflow series, route sanitization, status classes, lock protection, detached snapshots and histogram schema.

## Verification boundary
Exact-head CI is triggered by this source commit. No test pass is claimed until the workflow completes successfully. No production collector, durable metrics store, retention policy, dashboard host, or external access-control acceptance is claimed.

## Gate disposition
**Gate 38 repository input-hardening increment: implemented. External Gate 38: OPEN.** Metrics remain process-local and reset on process restart; durable/multi-instance aggregation, bounded on-disk retention, self-hosted dashboard and host access-control evidence remain open.

**Gate 39: OPEN.** The existing local operator reporter remains in place, but host log collection, incident owner/escalation and recovery exercise are unverified.

## Stage 1 / cost
- Gate 10: **0/10 formally closed**.
- Stage 1: **300/400 ticks = 75% provisional**; no ticks awarded for repository-only hardening.
- Open criteria: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.
- Stages 2–6 NOT SCORED; overall 20.90% historical only.
- ZERO COST maintained: no service, provider, subscription, billing change, credential or Termux modification.
- `main` untouched.
