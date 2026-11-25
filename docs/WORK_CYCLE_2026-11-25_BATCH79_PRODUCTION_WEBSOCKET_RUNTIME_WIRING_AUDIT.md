# DEZZTA CHART — Batch 79: Production WebSocket Runtime Wiring Source Audit
Date: 25 November 2026
Branch: `phase-2/market-data-foundation`
Audited documentation HEAD: `114d8464e085977aba2d95b3581ee49a95990c18`
Audited source baseline: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`
Cost policy: ZERO COST
Scope: inspect the actual FastAPI app entrypoint, Docker command, runtime factories, signed snapshot support, WebSocket route selection, and CI evidence. This is a read-only source audit and documentation update; no runtime code, secret, Cloudflare resource, or deployment was changed.

## 1. Exact-source findings

### 1.1 Default container entrypoint does not inject the replica/publisher runtime

Verified source facts:
- `backend/Dockerfile` starts `uvicorn app.main:app`.
- The bottom of `backend/app/main.py` declares `app = create_app()`.
- `create_app()` defaults both `replica_runtime_factory=None` and `publisher_runtime_factory=None`.
- The function rejects simultaneous source-publisher and gateway-replica factories, explicitly requiring separate source and gateway app roles.
- When `replica_runtime_factory` is absent, lifespan starts the provider manager instead of constructing the Redis replica store, consumer, ownership lease, callback dispatcher and gateway worker.
- When `publisher_runtime_factory` is absent, the source Redis publisher is not constructed or started.
- The WebSocket route selects replica-backed snapshots/replay only when `application.state.ohlcv_replica_store` is non-null. Otherwise it uses the local source SQLite store and in-memory pipeline.
- Production Settings forbid Databento API credentials/provider switches under the ZERO MONEY policy. Thus the stock Docker entrypoint can start the HTTP/auth surface with Redis/Firebase configuration while the OHLCV publisher/replica relay remains unconfigured and the feed remains disconnected.

Conclusion: the production relay is opt-in and structurally supported, but the repository's stock Docker entrypoint does not provide a default production runtime composition. This is the concrete code-level WSS blocker; it is not a Cloudflare DNS-only problem.

### 1.2 Gate 25 primitives exist, but the default app does not assemble them

Verified source facts:
- `SQLiteOhlcvReplicaStore` accepts `trusted_snapshot_keys` and `require_authenticated_snapshots`.
- It exposes `install_global_snapshot(snapshot_path, expected_source_id=...)`, which verifies the manifest/attestation and atomically installs bars plus checkpoint/receipt state.
- `snapshot_attestation.py` provides owner-key loading, canonical Ed25519 signing and trusted-public-key verification.
- `backend/app/config.py` does not expose a standard production replica runtime configuration object for snapshot path, expected source ID, trusted-key map, replica DB path, stream key and consumer identity.
- The opt-in runtime factory must currently assemble these values and ensure the signed snapshot is installed before consumer construction.
- The FastAPI lifespan validates the injected store, consumer, Redis client, stream key, group, lease, hydration and worker, but it does not create the runtime itself.

Conclusion: signed snapshot verification and replica install are implemented as primitives; production owner-host key custody, transfer, install and default startup wiring are not accepted.

### 1.3 WebSocket auth and per-series entitlement are already guarded

Verified source facts:
- Production identity uses Firebase Admin token verification with revocation checks.
- The HTTPS ticket endpoint derives the subject from the verified principal.
- The ticket is purpose-bound, short-lived (90 seconds) and single-use.
- Production requires Redis-backed shared guard/ticket storage when `APP_ENV=production` requires `REDIS_URL`; the in-memory ticket store is the non-Redis development fallback.
- The WebSocket handler enforces Origin policy, ticket consumption, canonical instrument mapping, active instrument state and explicit per-account instrument entitlement.
- Ticket-authenticated sessions require periodic ticket renewal; entitlement is rechecked on a monotonic 60-second deadline.
- Replica-backed snapshot/replay is selected only after a verified replica runtime has been injected.

These are code-level protections; real Firebase project credentials, production Redis ACL/TLS and public WSS/device acceptance remain external acceptance evidence.

### 1.4 Lifecycle and worker safeguards already present

The replica lifespan validates factory output before traffic, hydrates the pipeline, acquires a generation-scoped token-fenced Redis lease, verifies consumer group readiness, creates an event-loop callback dispatcher, then starts the managed worker. Shutdown waits for the worker before releasing the lease and closing the Redis client; on timeout it deliberately leaves the client open and logs the failure. Publisher shutdown has a separate bounded wait.

Do not weaken these safeguards to make startup appear green.

## 2. Root-cause statement

The main blocker is **missing production runtime composition and verified deployment topology**, not absence of the individual Redis/replica/Ed25519/WebSocket components.

A safe production composition needs two explicit roles:
1. Authoritative source role: source SQLite/outbox, signed snapshot export, publisher checkpoint/lease and Redis appender.
2. Gateway role: owner-pinned trusted public keys, verified snapshot artifact/transfer, dedicated replica SQLite DB, replica consumer, generation-scoped consumer group and ownership lease.

The current `create_app` contract intentionally prevents both roles from sharing one app process. The implementation must preserve this separation and must not run source and gateway roles against the same SQLite database or consumer group.

## 3. Work items and acceptance tests

### W1 — Runtime contract/configuration (source-only, zero cost)
- Define strict role selection and reject ambiguous/unknown role values.
- Parse only the required environment values; never log secret contents.
- Validate absolute file-backed database/snapshot paths, source identity, trusted Ed25519 key map, stream key and consumer identity.
- Require authenticated snapshots in the production gateway role.
- Keep publisher and gateway runtime factories mutually exclusive.
- Missing or invalid production role configuration must fail closed with a sanitized startup error, not silently claim a connected feed.

### W2 — Source role factory
- Reuse the existing source store, signed snapshot export and publisher checkpoint/lease/appender classes.
- Require the configured signing key and key ID together in production.
- Verify publisher checkpoint source ID/stream identity before the publisher loop starts.
- Use a dedicated Redis client and least-privilege source publisher ACL.
- Never grant source publisher permissions to trim/delete streams or destroy consumer groups.

### W3 — Gateway role factory
- Load trusted public keys; do not load the source private key on a gateway.
- Verify the signed snapshot before Redis client creation and install into a dedicated empty/file-backed replica DB.
- Verify expected source identity and generation; refuse source mismatch, rollback, unsigned snapshot or untrusted key.
- Create the generation-scoped consumer and lease using a dedicated gateway Redis ACL.
- Keep destructive Redis retention permissions absent.

### W4 — Exact acceptance matrix
- Unit tests: invalid role, missing required env, malformed key map, invalid paths, source/gateway role conflict, wrong source ID and unsigned snapshot.
- Integration: source signs and exports; gateway installs and verifies; source appends; two independent gateway replicas consume independently.
- Recovery: process restart, Redis restart, lease loss, duplicate delivery, pending reclaim, event gap, retention floor and snapshot-generation switch.
- Security: gateway cannot publish or destroy groups; source cannot trim/delete; invalid signature rejected before Redis is initialized.
- Lifecycle: startup failure closes partially created resources; worker timeout never reports a clean stop.
- End-to-end: real public WSS, browser reconnect/resnapshot and Android WebView foreground/background/process-death/network handover.

### W5 — Gate 25 durable acknowledgement boundary
- Distinguish local SQLite applied cursor, Redis consumer-group XACK, immutable signed snapshot receipt and owner-accepted per-gateway durable high-water ACK.
- Require a durable per-gateway ACK/receipt record with source ID, replica ID, snapshot generation, cursor, digest, receipt verification state and monotonic update rules.
- Reject stale generation, cursor regression, receipt mismatch and stale gateway ownership.
- Prove restart reconciliation from durable receipt/ACK state before any stream retention advancement.
- Keep `XTRIM`, `XDEL` and consumer-group destruction disabled until all required gateways have accepted durable high-water state.

## 4. Exact CI evidence boundary

The last source/test SHA is `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`. The recorded exact-source CI results are:
- Automated Tests: 41/41 workflow steps; 1,426 passed, 1 skipped, 6 warnings.
- CodeQL: 16/16 (Python 8/8; JavaScript/TypeScript 8/8).
- OCI ARM64: 7/7.
- Full-history Secret Audit: 6/6.
- Dedicated Redis TLS integration: 1 passed.

The documentation HEAD `114d8464e085977aba2d95b3581ee49a95990c18` is six documentation-only commits ahead of that source/test SHA, with no source/runtime changes in the compare. Its commit uses `[skip ci]`; it has no associated workflow runs or status checks. No current HEAD CI success is claimed, and no source code was changed in this audit.

## 5. Project and indicator accounting

- Stage 1 remains the official active stage: 30/40 = 75% provisional 🟨.
- Gate 10 remains 0/10 formally closed 🟥: criteria 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.
- Stage 2 remains 🟦 PREPARATORY, not an official transition.
- Stage 3 ⚪ NOT SCORED; Stage 4 🟪 GATED; Stages 5–6 ⚪ NOT SCORED.
- Overall project and IP3S remain ⚪ NOT SCORED because the approved weighted denominator is absent.
- WebSocket production wiring/Gate 25/Gate 36 remain 🟥 OPEN.
- Indicator calculations and Shared Hook remain 🟨 FOUNDATION; Footprint PRO 2GD 🟧 GATED; Volume Profile, Complete Volume Profile, Movable-range Volume Profile, Heatmap and Liquidation Maps 🟥 OPEN.
- Focused indicator declarations: 21 calculation + 7 hook = 28; this is not implementation completion. No indicator source or UI changed.

## 6. Controls

ZERO COST. Keep `main` untouched. Keep Vercel deferred. Do not deploy to an empty/mismatched Cloudflare account or create duplicate resources. The user has stated the project server is on Cloudflare; the connected account inventory previously returned empty, so resolve the existing project/account mapping by inspecting the actual existing Cloudflare deployment rather than assuming a new account or hostname. Do not claim owner-host, live provider, public WSS or Android acceptance from CI. Planning target remains around 24 December 2026.
