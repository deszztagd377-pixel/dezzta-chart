# DEZZTA CHART — Batch 95 WebSocket ACK protocol proof

**Date:** 27 November 2026  
**Branch:** `work/batch95-websocket-ack-protocol`  
**Pull request:** [#13](https://github.com/deszztagd377-pixel/dezzta-chart/pull/13)  
**Base:** `phase-2/market-data-foundation`  
**Scope:** synthetic Cloudflare Durable Object proof only; no production activation.

## 1. Verified implementation boundary

The repository already contains a Python `FirebaseIdentityVerifier` in `backend/app/identity.py`. Its production verification path calls Firebase Admin `verify_id_token(..., check_revoked=True)`, then validates the expected Firebase issuer, project audience, non-empty subject, authentication time, and consistency of `uid` and `sub`. The backend's WebSocket-ticket design therefore remains the identity boundary; a second Firebase verifier inside the synthetic Worker would duplicate trust logic and introduce an unnecessary credential/configuration surface.

The Cloudflare proof Worker remains explicitly `PROOF_MODE=synthetic-only`. Its one-time ticket subject is the fixed synthetic proof principal, not a Firebase user. This PR does not convert that proof route into a production authentication endpoint.

## 2. Batch 95 code change

The synthetic Durable Object now accepts a versioned WebSocket message:

```json
{
  "type": "market_data.ack",
  "version": 1,
  "sequence": 52,
  "eventDigest": "<64 lowercase hexadecimal characters>"
}
```

The consumer identity is not accepted from the ACK payload. It is attached server-side to the authenticated synthetic proof socket. Before subscription is enabled, the Durable Object registers that required consumer in the existing SQLite registry.

The ACK handler enforces:
- the socket is authenticated and subscribed;
- the sequence is an integer greater than the snapshot watermark;
- the sequence does not exceed the highest event delivered to that socket;
- the digest is syntactically valid and exactly matches the retained event;
- the existing receipt transaction accepts only monotonic, generation-bound ACKs.

The per-socket delivered watermark advances only after a successful live frame send. A replay subscription sets it to the replay boundary only after the replay batch is emitted. An ACK beyond the delivered boundary returns `market_data.ack_rejected`; an accepted ACK returns `market_data.acknowledged` with the durable receipt cursor and version.

## 3. Test coverage added

`cloudflare/proof/worker.miniflare-test.mjs` adds a real workerd/Miniflare WebSocket integration case:
1. Send an ACK one sequence beyond the delivered watermark; expect rejection.
2. ACK the exact sequence and digest delivered over the WebSocket; expect an accepted durable receipt at cursor 52, receipt version 1.

The existing HTTP proof ACK tests remain in place for receipt duplicate, regression, digest mismatch, and compaction-boundary behavior. The new WebSocket case exercises the protocol path rather than replacing those lower-level tests.

## 4. Known limitations — remain YELLOW

- Consumer ID is a fixed synthetic proof identity scoped to the per-series Durable Object. It is not a production device/install identity.
- The required-consumer registry still has no lease, expiry, fencing, or safe deregistration lifecycle. A stale registered consumer can block compaction indefinitely; this is fail-closed but can cause unbounded retention growth.
- The synthetic ticket is not Firebase-authenticated and must not be exposed as a production route.
- Public WSS, Cloudflare Durable Object deployment, real Firebase project E2E, browser/Android E2E, provider rights, and zero-cost billing certification remain unverified.
- The WebSocket ACK proof does not by itself close production Gate 10 or Stage 1.

## 5. Next engineering sequence

1. Define consumer ownership from the backend's verified Firebase principal plus a separately validated installation identity.
2. Add lease renewal, expiry, fencing tokens, and explicit safe deregistration semantics. Compaction must include only consumers whose lease/lifecycle state is authoritative; expiry must be designed so an offline but valid consumer is not silently skipped.
3. Bind the backend-issued short-lived ticket to the exact series and a signed/opaque consumer grant that the Worker can validate without exposing Firebase Admin credentials.
4. Add reconnect/replay/ACK races, expired-lease fencing, duplicate registration, consumer replacement, and compaction-vs-expiry concurrency tests.
5. Only after those tests pass, connect the real backend ticket path to a deployed public WSS endpoint and run browser/Android E2E.

## 6. Source references

- Firebase Admin token verification: https://firebase.google.com/docs/auth/admin/verify-id-tokens
- Firebase session revocation checks: https://firebase.google.com/docs/auth/admin/manage-sessions
- Cloudflare Durable Object WebSocket hibernation: https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- Cloudflare Durable Object WebSocket state API: https://developers.cloudflare.com/durable-objects/api/state/
- Cloudflare Workers WebSocket API: https://developers.cloudflare.com/workers/runtime-apis/websockets/

## 7. Validation record

The PR's exact-head GitHub Actions result is the acceptance authority. Do not infer success from a preview deployment, an earlier commit, or a different branch. Update this section only after every required workflow on the final head reaches a terminal result.

