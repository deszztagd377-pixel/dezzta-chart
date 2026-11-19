# Batch 62J-8 — generation-scoped Redis consumer groups

**Date:** 19 November 2026  
**Branch:** phase-2/market-data-foundation

## Security issue

The prior snapshot reset destroyed the existing Redis consumer group to clear its pending list. This required XGROUP DESTROY in the gateway runtime ACL, a destructive permission that is not necessary for normal event consumption.

## Change

- Consumer group names now include a deterministic hash of the replica's snapshot_generation, in addition to stable replica and source identifiers.
- A snapshot replacement changes the generation. reset_group_after_snapshot() refreshes the checkpoint generation and creates the new group at the installed applied_cursor.
- ensure_group() also refreshes generation, so a restarted worker cannot remain attached to an obsolete group after a snapshot replacement.
- Old groups and pending entries are retained and isolated; the new group starts with an empty pending list.
- Runtime consumer code no longer calls XGROUP DESTROY. The steady-state ACL command matrix is reduced to XGROUP CREATE, XAUTOCLAIM, XREADGROUP, XACK and XRANGE.
- Cleanup of old generation groups is intentionally separated into owner-authorized maintenance. Do not grant destructive group permissions to runtime identities.

## Verification

The real Redis test creates a pending entry in the old group, installs a newer snapshot, switches generation, asserts the old pending entry remains in the old group, asserts the new group has no pending entries, and confirms the consumer applies the next cursor. The test replaces the Redis client's xgroup_destroy method with a guard that raises if runtime reset tries to call it.

Exact-head CI is required before marking this batch verified. No production ACL or credentials are changed.

## Gate 25

This narrows the runtime permission set but does not close Gate 25. The exact stream key, separate publisher/gateway URLs, TLS endpoint, ACL user provisioning, multi-instance target test, lease/race and outage recovery still require owner-controlled environment evidence.

## Cost and indicator status

Zero-cost source and GitHub Actions tests only. No Vercel/Cloudflare deployment, paid service, Termux, or main branch change. Indicator status unchanged.
