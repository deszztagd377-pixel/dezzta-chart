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

1. Client ACK is now capability-gated: the browser coalesces ACKs only when the server advertises protocol v1 and events contain a generation ID plus SHA-256 digest. The synthetic Worker advertises this capability. The production FastAPI stream does not yet do so and remains unchanged.
2. Resolve the production event-envelope mismatch: add a canonical per-series generation/sequence/digest contract or define a separately safe global-cursor receipt contract. Do not send the synthetic ACK schema to the current FastAPI path.
3. Implement the lease/fencing lifecycle and bounded retention policy from the ADR, with no per-heartbeat alarm writes.
4. Bind a backend-issued, one-time Firebase-verified session grant to the exact series and Worker session identity.
5. After exact-head tests pass, connect the real ticket path to a deployed WSS endpoint and run browser/Android E2E.

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

**Validated source/test head:** `a428c7901ae3ddd398897cbc5a7d78a378e180d3`

All four required workflows reached terminal **SUCCESS** on this exact head:

- Automated Tests — run [45982338038](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45982338038): **SUCCESS**. All 40 job steps completed, including Worker syntax/unit tests, pinned workerd/Miniflare integration, Durable Object hibernation/alarm/isolation tests, frontend tests/build, backend tests, Redis TLS integration, benchmarks, backend image build/smoke test and image scan.
- CodeQL Security Analysis — run [45982338137](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45982338137): **SUCCESS** (JavaScript/TypeScript and Python).
- Full Git History Secret Audit — run [45982338192](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45982338192): **SUCCESS**.
- OCI ARM64 Image Readiness — run [45982337953](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45982337953): **SUCCESS**.

### Failure and correction history

The preceding source head `880ae0f8e7fe787015b41b5a63e86a8689377266` had an Automated Tests failure in run [45982180407](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45982180407). The failing unit test was `fan-out is withheld until a durable SQLite commit succeeds`: three mock socket fixtures still used the pre-ACK attachment shape. The production guard correctly rejected those stale fixtures. The fixtures were updated to include the synthetic consumer ID and delivered-sequence watermark, then the final head `a428c790` passed the full workflow.

The intermediate CI attempts on older heads were cancelled by GitHub's branch concurrency policy; they are not counted as successful validation. The final four runs listed above are terminal and green.

**Repository safety:** PR #13 remains open and unmerged. `main` was verified unchanged at `e3841681bc69b73619058deaf939df82ae5116a`. No Cloudflare deployment/resource, secret, paid service, or recurring automation was changed.

This is repository-level synthetic proof acceptance only. It does not establish Firebase-to-Worker production identity, consumer lease/fencing/deregistration, public WSS, provider rights, billing zero-cost certification, or browser/Android production acceptance. Overall Batch 95 and production Gate 10 remain **YELLOW**.



## 8. Frontend ACK and cost audit — 2026-11-27

The frontend transport now supports the synthetic ACK protocol only when the server advertises `consumerAckProtocolVersion: 1`. It validates ACK responses, fails closed on rejection/timeout, and coalesces contiguous applied updates into a 10-second batch. The synthetic Worker advertises the capability. The current FastAPI production path does not advertise it, so the client sends no ACK there.

Audit evidence from the existing client: application text ping every 20 seconds, pong timeout 10 seconds, ticket renewal every 45 seconds. The current chart series store and resume cursor are in memory; a page reload starts with a fresh snapshot rather than a durable browser checkpoint.

Production compatibility gap: FastAPI stream events have per-subscription sequence plus global outbox cursor, but do not currently carry the Cloudflare proof's generation ID and digest. The backend WebSocket handler also does not implement the proof ACK response contract. This is an explicit integration gate, not a reason to send incompatible ACK messages.

Zero-cost review: Cloudflare Durable Objects Free currently lists 100,000 requests/day, 100,000 SQLite row writes/day, 5 million row reads/day, 5 GB SQLite storage, and 13,000 GB-s/day. Incoming WebSocket messages use a 20:1 request billing ratio; outgoing messages are not charged as requests. The current proof's two writes per event make a sustained 1 Hz stream exceed the row-write allowance before ACKs. High-frequency zero-cost production is therefore not certified. See the [official Durable Objects pricing page](https://developers.cloudflare.com/durable-objects/platform/pricing/).

The frontend ACK implementation and Worker capability advertisement are a repository candidate only. Production Firebase identity, per-session lease/fencing, canonical production event digest, public WSS, provider rights, and device E2E remain YELLOW.


## 9. Exact-head validation closeout — 2026-11-27

**Validated HEAD:** `fb25f4eb29536473610b206542f7a356fa6c2c02`

All four required GitHub Actions workflows reached terminal **SUCCESS** on this exact commit:

- Automated Tests — [run 45989797712](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45989797712): **SUCCESS**, 41/41 job steps completed.
- CodeQL Security Analysis — [run 45989797796](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45989797796): **SUCCESS**.
- Full Git History Secret Audit — [run 45989797647](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45989797647): **SUCCESS**.
- OCI ARM64 Image Readiness — [run 45989797592](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/45989797592): **SUCCESS**.

### Test correction history

The preceding candidate head `2e5f5230e3f7fab6529ba1b929f18be802ce0232` had one frontend test failure in `coalesces durable ACKs and confirms the highest contiguous applied event`. The second synthetic candle fixture had a close above its high, violating the existing OHLCV invariant. The fixture was corrected by setting the high to the same valid upper boundary; the final head above passed the complete Automated Tests workflow. The ACK protocol implementation itself was not changed for this fixture correction.

### Repository closeout

- PR #13 remains open and unmerged; target branch is `phase-2/market-data-foundation`.
- `main` remains unchanged at `e3841681bc69b73619058deaf939df82ae5116a1`.
- No queued or in-progress workflows remained in either `dezzta-chart` or `dezzta-chart-runner` at closeout.
- No Cloudflare resources or deployments, secrets, paid services, or recurring automations were changed or created.
- Production Firebase grant, consumer lease/fencing implementation, canonical FastAPI event digest/sequence contract, public WSS, provider rights, account-level zero-cost certification, and browser/Android E2E remain **YELLOW**.

This closeout proves repository CI only. It does not mark the production WebSocket path as accepted.
