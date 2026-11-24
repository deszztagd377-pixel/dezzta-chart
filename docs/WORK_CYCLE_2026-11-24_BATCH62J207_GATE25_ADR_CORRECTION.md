# DEZZTA CHART — Batch 62J-207: Gate 25 ADR Correction and Exact-Head Verification

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Pre-batch HEAD:** `cc79e292c84fb10261dc4b8bd1fc5c91786144ce`  
**Scope:** correct stale Gate 25 ADR wording; reconcile current progress indicator  
**Cost:** ZERO COST

## Source evidence

The current source/test checkpoint remains `b71bf86c31fadd2895a2b4f18991b6742847e1a1`. The current branch's SQLite replica checkpoint has a nullable `snapshot_sha256` column; snapshot installation recomputes and validates the digest while installing rows and writes it with the mutable checkpoint in the same transaction. Gateway runtime compares installer metadata with the durable checkpoint digest before constructing the Redis client.

This is not an immutable receipt history. The current checkpoint is mutable and advances with newer snapshot generations. Callback receipt-map validation does not, by itself, prove authenticated owner-host retrieval or durable custody of immutable per-generation receipts.

## Changes

1. Corrected the opening Context paragraph in `docs/ADR_WEBSOCKET_SNAPSHOT_INSTALLATION_RECEIPT.md` so it no longer states that the mutable checkpoint lacks a digest.
2. Preserved the proposed design direction for a separate immutable receipt and owner-controlled trust/key provenance.
3. Updated `docs/PROJECT_PROGRESS_INDICATOR_CURRENT.md` with Batch 62J-207 evidence and exact-head verification requirements.
4. No application source, tests, dependencies, credentials, provider configuration, hosting, or deployment changed.
5. `main` was not modified.

## Remaining Gate 25 acceptance gap

- append-only immutable receipt per source/replica/generation;
- authenticated owner-host receipt retrieval/custody;
- trusted signer/key identity and key lifecycle;
- atomic receipt persistence with snapshot installation;
- conflict, migration, rollback, crash-recovery and retention acceptance tests.

Gate 25 remains OPEN. No schema/runtime implementation is authorized by this documentation correction. Redis Stream trimming remains prohibited until the separately defined retention prerequisites are proven.

## Progress accounting

- Stage 1: 30/40 criteria = 300/400 ticks = 75% provisional (unchanged).
- Gate 10: 0/10 formally closed (unchanged).
- Overall project: NOT SCORED.
- Aggregate indicator progress: NOT SCORED.
- Footprint owner-reference prerequisite: cleared by Batch 62J-206; visual implementation remains parked until Stage 4 and scoped blueprint review.
- ZERO COST; `main` untouched.

## Verification

The previous documentation HEAD `cc79e292c84fb10261dc4b8bd1fc5c91786144ce` had all four configured workflows SUCCESS. The new documentation HEAD must independently complete Automated Tests, CodeQL, OCI ARM64 readiness and Full Git History Secret Audit. Exact-head terminal conclusions are required; no pending workflow is treated as success.
