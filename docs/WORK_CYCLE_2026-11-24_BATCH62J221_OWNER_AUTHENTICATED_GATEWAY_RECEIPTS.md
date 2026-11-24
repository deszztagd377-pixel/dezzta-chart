# DEZZTA CHART — Batch 62J-221: Owner-Authenticated Multi-Gateway Receipt Binding

**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Verified CI base HEAD:** `0fa0b17b7f436e5c41e87599ae8f993da8b67a7a`  
**Cost:** ZERO COST  
**Main:** untouched • **Vercel:** deployment deferred

## 1. Previous CI acceptance

Batch 62J-220 final documentation HEAD `0fa0b17b7f436e5c41e87599ae8f993da8b67a7a` completed all four required workflows successfully:

- Automated Tests: SUCCESS — [45406917673](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406917673).
- CodeQL: SUCCESS — [45406917414](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406917414).
- OCI ARM64: SUCCESS — [45406917429](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406917429).
- Full Git History Secret Audit: SUCCESS — [45406917428](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45406917428).

Every workflow reports the same exact `head_sha`.

## 2. Source audit finding

The source publisher runtime already required a receipt mapping for every configured gateway and matched source ID, stream key, generation, cursor, and snapshot SHA-256. However, it did not require the receipt to carry the gateway's persisted owner-authentication state, authenticated source binding, signer key ID, or durable replica ID. A callback could therefore accidentally pass a content-only receipt or map one durable replica under multiple gateway IDs while satisfying the existing digest/cursor checks.

The gateway runtime already re-verifies the persisted Ed25519 receipt before Redis client construction. Its returned `snapshot_evidence` did not include the explicit `authenticated_source_id` field needed by the source-side receipt contract.

## 3. Batch 62J-221 implementation

- Gateway runtime now exports `authenticated_source_id` alongside source, generation, cursor, digest, replica ID, verification state, and key ID.
- Source runtime requires each configured gateway receipt to report:
  - `source_id` and `authenticated_source_id` matching the authoritative source;
  - `verification_state == OWNER_SIGNATURE_VERIFIED`;
  - a non-empty durable `replica_id`;
  - a valid bounded ASCII signer key ID;
  - the exact configured stream, generation, high-water cursor, and canonical digest.
- Replica IDs must be unique across distinct configured gateway IDs.
- All gateways must report the same owner snapshot signer key ID for the installed generation.
- Validation remains before source Redis client construction; failures do not start the publisher.

This strengthens the source-side contract but does not pretend the callback itself has become a remote transport. The owner-host callback must still authenticate the remote gateway connection and retrieve the persisted receipt from the actual gateway. Repository tests cannot prove real host custody or network authentication.

## 4. Changed files

- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/app/ohlcv_redis_runtime.py`
- `backend/tests/test_ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_redis_runtime.py`

Regression coverage includes content-only receipt rejection, wrong authenticated source, missing replica/key identity, duplicate replica identity, mixed signer key IDs, and preservation of fail-before-Redis behavior.

## 5. Next acceptance sequence

1. Run all four workflows against the final Batch 62J-221 documentation HEAD; fix any exact-head failure.
2. Wire the owner-controlled source callback to fetch each gateway's persisted immutable receipt over an authenticated owner-managed channel and return the exact evidence contract.
3. Verify the real owner-host private key is outside Git/container artifacts and protected by owner-only permissions.
4. Run real signed snapshot transfer and restart verification on every gateway.
5. Verify multi-gateway receipt persistence, per-gateway high-water acknowledgement, and signer key rotation/revocation.
6. Continue external WSS/TLS, Firebase E2E, Android/browser lifecycle, monitoring, backup/restore and recovery acceptance.

Redis `XTRIM`, `XDEL`, and consumer-group destruction remain prohibited until gateway inventory/retirement, PEL handling, per-gateway floor acknowledgements and crash-safe trim/reconcile are independently proven.

## 6. Progress accounting

- Stage 1: 30/40 criteria = 75% provisional.
- Stage 2: active.
- Gate 25: improved source-side receipt contract; real owner-host transport/custody remains OPEN.
- Redis destructive retention: BLOCKED.
- Indicators: no implementation change or completion credit.
- Overall project and aggregate indicator progress: NOT SCORED.
- ZERO COST; `main` untouched; Vercel deployment deferred.
- Planning target remains approximately 24 December 2026.
