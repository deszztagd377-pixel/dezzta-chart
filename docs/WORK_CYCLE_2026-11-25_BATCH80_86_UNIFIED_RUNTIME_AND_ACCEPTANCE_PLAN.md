# DEZZTA CHART — Batch 80–86 Unified Engineering Work Package
Date: 25 November 2026
Branch: `phase-2/market-data-foundation`
Starting HEAD: `fd756cee2bf3e427a628c3089c37d07d9f75ada7`
Source/test baseline: `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833`
Cost ceiling: ZERO COST
Delivery planning target: around 24 December 2026

## 0. Execution record and truth boundary

This package consolidates the next seven sequential work batches into one reviewed engineering plan. It is a documentation/design deliverable, not a claim that production runtime code, public WSS, owner-host acceptance, or mobile end-to-end verification has been completed. No runtime code, secrets, Cloudflare resources, production data, or deployment were modified in this package. No user command or unverified code is required.

The user explicitly requested work on Batches 80–86 in one response. That authorizes continuing the project work; the established major-change gate still requires the scoped runtime blueprint to be reviewed before committing the new production runtime composition. Therefore the design and acceptance contracts below are prepared now, while runtime implementation remains blocked at the review gate. This is intentional change control, not a skipped stage.

The previous Batch 79 audit identified the exact source-level gap:
- Docker starts `uvicorn app.main:app`.
- Module-level `app = create_app()` supplies neither `replica_runtime_factory` nor `publisher_runtime_factory`.
- The factories are intentionally mutually exclusive.
- Without a replica factory, the gateway consumer/lease/worker are not constructed.
- Without a publisher factory, the source publisher is not started.
- Without a replica store, WebSocket snapshot/replay uses the source-local store/in-memory path.

The components already present are not to be rewritten casually: SQLite source outbox, publisher checkpoint, Redis stream appender/publisher, SQLite replica store, signed snapshot attestation, replica consumer, generation-scoped consumer lease, callback dispatcher, gateway worker, Firebase identity verifier, Redis shared ticket guard and WebSocket route.

## 1. Batch 80 — strict role/runtime configuration

Status: DESIGN COMPLETE; CODE NOT STARTED.

Required contract:
- Explicit role values: `source` or `gateway`; no silent default to a production role.
- Production startup rejects missing, unknown, conflicting, or partial role configuration with sanitized errors.
- Source role requires a file-backed source DB path, Redis TLS URL, stream key, stable source identity, publisher owner identity, and signing-key file plus key ID.
- Gateway role requires a separate file-backed replica DB path, Redis TLS URL, stream key, expected source ID, stable gateway identity, and non-empty owner-pinned Ed25519 public-key map.
- Gateway must never load or receive the source private signing key.
- Source and gateway factories remain mutually exclusive. No shared SQLite DB path and no shared publisher/consumer identity.
- All paths are absolute in production; reject empty, `:memory:`, directory, symlink/private-key path violations, and accidental source/replica path equality.
- Secrets are never emitted in logs, reprs, metrics, error details, or status endpoints.
- Redis production TLS/ACL validation must reuse existing Settings checks rather than weaken them.
- Zero-cost provider policy remains unchanged; do not enable paid market-data access.

Validation matrix: valid source, valid gateway, missing role, unknown role, missing required value, source key pair partial, empty trust map, malformed trust key, invalid path, duplicate DB path, role/factory conflict, plaintext Redis in production, source private key supplied to gateway.

## 2. Batch 81 — source publisher factory

Status: DESIGN READY; IMPLEMENTATION BLOCKED BY BATCH 80 REVIEW.

Composition contract:
1. Open the authoritative `SQLiteOhlcvStore` at the configured persistent path.
2. Load Ed25519 private key and key ID together using existing `load_snapshot_signing_key_from_environment` / key-loader behavior; production source role must fail closed if absent.
3. Export a globally consistent snapshot and sign its canonical manifest.
4. Initialize publisher checkpoint from the exact verified snapshot source ID, generation, high-water cursor and stream identity.
5. Construct one dedicated Redis TLS client with source least-privilege ACL.
6. Construct the existing stream appender and `RedisOhlcvPublisher` with explicit bounded owner/lease/batch configuration.
7. Inject the factory through `create_app(publisher_runtime_factory=...)`.
8. Ensure partial startup failure closes every resource already opened; shutdown waits for publisher task and closes Redis only after task termination.

Publisher invariants:
- SQLite outbox remains authoritative if Redis is unavailable.
- Deterministic Stream IDs and exact read-back verification remain intact.
- Checkpoint cursor advances only after append confirmation.
- Lease fencing is mandatory before each append.
- Source ACL must not grant `XTRIM`, `XDEL`, `XGROUP DESTROY`, or gateway consumer permissions.

## 3. Batch 82 — gateway replica factory

Status: DESIGN READY; IMPLEMENTATION BLOCKED BY BATCH 80 REVIEW.

Startup order is security-critical:
1. Validate gateway role config and absolute paths.
2. Load/validate owner-pinned Ed25519 public keys; do not load a private key.
3. Verify snapshot attestation and expected source identity before accepting Redis events.
4. Install the snapshot atomically into a dedicated replica SQLite DB with `require_authenticated_snapshots=True`.
5. Confirm the durable receipt, source ID, generation, digest and high-water cursor.
6. Only then create the Redis TLS client and gateway consumer.
7. Ensure generation-scoped consumer group and acquire the existing token-fenced ownership lease.
8. Hydrate the in-memory pipeline from the installed replica snapshot.
9. Construct the callback dispatcher and `RedisOhlcvGatewayWorker`.
10. Inject through `create_app(replica_runtime_factory=...)`; do not start source provider ingestion in gateway role.

Gateway ACL must be read/consume-only for the configured stream and lease keys; no publish, trim, delete, or group-destroy rights. A snapshot source mismatch, missing signature, unknown key, stale generation, missing checkpoint, Redis TLS failure, or lease contention must fail closed.

## 4. Batch 83 — multi-gateway integration and recovery

Status: ACCEPTANCE MATRIX READY; SOURCE CI NOT YET RUN.

Minimum test topology:
- One source SQLite DB and one source publisher.
- One Redis service with isolated source/gateway ACL users.
- Two independent gateway processes.
- Two distinct replica SQLite files, two stable replica IDs, two generation-scoped consumer groups and two ownership leases.
- One WebSocket client per gateway.

Acceptance scenarios:
1. Source publishes cursor N; both gateway replicas independently apply N and fan out N.
2. Duplicate delivery and ACK reply loss do not duplicate durable state or fan-out.
3. Callback failure occurs before XACK; pending entry is retried and callback is safely repeated.
4. Gateway A outage does not block gateway B.
5. Redis TCP interruption, restart and reconnect preserve applied cursors and recover without gaps.
6. Gateway process restart reuses its durable replica DB and reconciles the correct consumer group.
7. Lease loss/fencing prevents the old owner from applying or ACKing.
8. Pending reclaim, event gap, deleted pending entry and retention-floor breach require resnapshot rather than cursor skipping.
9. Snapshot generation switch creates a new generation-scoped group; old groups remain until separately authorized cleanup.
10. Startup/shutdown failures close resources and never report a clean worker stop when the worker is still alive.

Test matrix must run against real Redis in CI; mocks alone are insufficient for Stream/consumer-group semantics.

## 5. Batch 84 — Gate 25 durable receipt and high-water ACK

Status: DESIGN READY; GATE OPEN.

Keep four progress notions separate:
- Source publisher checkpoint: highest source outbox cursor confirmed appended to Redis.
- Replica SQLite applied cursor: highest event committed to this gateway's durable local read model.
- Redis consumer-group ACK: Redis pending-entry acknowledgement for delivery bookkeeping.
- Owner-accepted durable gateway receipt/high-water ACK: externally auditable statement that a particular gateway has durably accepted a particular signed snapshot generation and cursor.

The fourth item is the Gate 25 acceptance boundary. It must not be inferred from the first three.

Proposed immutable receipt fields:
- protocol/schema version;
- source ID;
- gateway/replica ID;
- snapshot generation;
- snapshot SHA-256 digest;
- signed-manifest key ID and verification state;
- installed snapshot high-water cursor;
- current durable applied high-water cursor;
- receipt creation/update timestamps;
- monotonic sequence/version and owner acceptance state.

Required monotonicity:
- source ID cannot silently change;
- replica ID is stable for the DB identity;
- snapshot generation cannot roll backward;
- applied cursor cannot decrease within a generation;
- a new generation must be authenticated and explicitly reconciled;
- receipt digest and source/generation identity must match installed DB checkpoint;
- stale lease owner cannot update the accepted high-water ACK.

Restart proof must reconstruct the accepted receipt from durable state and compare it with the SQLite checkpoint and Redis stream/group state. Receipt storage must be durable and independent of transient process memory. Do not equate XACK with an owner acceptance record.

Retention policy:
- `XTRIM`, `XDEL`, and consumer-group destruction remain blocked.
- No retention floor may advance beyond the minimum owner-accepted high-water ACK across every required gateway.
- Missing/stale gateway receipt means retention cannot advance.
- Cleanup requires an explicit future migration and acceptance gate.

## 6. Batch 85 — Cloudflare WSS and device acceptance

Status: BLOCKED ON BATCHES 80–84 AND EXISTING-HOST MAPPING.

No new Cloudflare Worker, Pages, Durable Object, domain, tunnel, paid service, or duplicate infrastructure is authorized by this work package.

The user has stated that the project server is on Cloudflare. The connected Cloudflare account inventory previously returned no relevant resources. This is an account/visibility mismatch, not proof that the project has no Cloudflare deployment. Resolve the existing production mapping from the actual owner-controlled deployment record; do not guess a hostname, route, account, or create replacements.

Acceptance sequence:
1. Confirm existing Cloudflare account, zone/route, Worker or reverse-proxy topology, origin and owner-host identity.
2. Confirm existing origin process role and persistent storage path.
3. Confirm TLS termination and origin TLS mode; no insecure downgrade.
4. Confirm public WSS handshake and Origin allowlist.
5. Confirm Firebase-issued principal, 90-second single-use ticket and 60-second entitlement recheck.
6. Verify snapshot/replay/live event path from source through Redis to the gateway.
7. Verify reconnect, backoff, resnapshot, stale cursor, unauthorized instrument and expired/reused ticket rejection.
8. Browser tests: foreground/background, tab suspension, reconnect and network handover.
9. Android tests: foreground/background, process death, reconnect, network handover and stale local state.
10. Verify no secret appears in client bundle, logs, URLs or telemetry.

A successful CI loopback WebSocket test is not public Cloudflare WSS acceptance.

## 7. Batch 86 — recovery, observability and owner-host operations

Status: CONTRACT READY; OWNER-HOST ACCEPTANCE OPEN.

Zero-cost observability should use existing local metrics/incident primitives and operator logs; do not introduce paid monitoring or external alert SaaS.

Metric families:
- WSS: active sessions, auth failures, ticket replay/expiry, origin rejection, reconnects, close codes, per-account limit hits.
- Publisher: outbox lag, published cursor, last successful batch, lease conflicts/loss, append mismatch, resnapshot-required.
- Replica: applied cursor, source-to-replica lag, pending count, reclaim count, duplicate/stale count, callback failures, resnapshot count.
- Redis: TLS/connectivity, command failures, group lag, pending age, lease renewal/loss, restart/reconnect.
- Snapshot/receipt: signature failures, untrusted key, source mismatch, digest mismatch, generation, installed cursor, receipt age, accepted high-water cursor.
- Host: process restarts, disk free bytes, SQLite integrity result, DB/WAL size, backup age and restore drill result.

Operational controls:
- sanitized structured logs; never log secrets or full credential-bearing Redis URLs;
- bounded metric cardinality and retention;
- SQLite WAL checkpoint and integrity check;
- encrypted off-host backup only where a genuinely zero-cost owner-controlled destination exists; otherwise disclose backup gap, do not silently rely on local disk;
- restore drill into a separate path and verify DB integrity, source identity, replica receipt, cursor and service startup;
- incident drill for Redis loss, host restart, bad snapshot, expired key, disk-full and gateway lease takeover;
- no false healthy state while workers are degraded, disconnected, resnapshot-required or shutdown-timed-out.

## 8. Mathematical/operational parameter review

Existing source defaults observed in the current code:
- Publisher default lease TTL: 30,000 ms; bounded publisher batch default: 100.
- Gateway consumer default pending-idle threshold: 30,000 ms; bounded batch default: 100; block interval is optional and bounded.
- Gateway lease default TTL: 15,000 ms; default renewal interval is TTL/3 = 5,000 ms.
- WebSocket ticket TTL: 90 seconds; entitlement recheck: 60 seconds.
- These are existing code defaults, not measured production SLOs.

Reasoning:
- Gateway lease heartbeat at 5 seconds provides three renewal opportunities per 15-second TTL. This is an engineering default only; real host scheduling and Redis RTT must be measured before declaring it safe.
- 30-second pending idle threshold must be greater than expected normal processing latency; tune only from observed p99 processing/transport latency and recovery tests, never guess from average.
- 100-event batches bound work but do not prove throughput. Measure event size and processing time; enforce bounded queue/memory and backpressure.
- 90-second ticket TTL with 60-second entitlement recheck leaves a nominal 30-second interval between checks and ticket expiry; ticket renewal must remain explicit and single-use.
- No stream retention calculation is valid until every required gateway has a durable accepted high-water ACK. Current safe retention advancement = zero destructive trimming.

No production SLO or throughput number is claimed from these defaults.

## 9. Indicator documentation and current acceptance

No indicator code or UI was changed in Batches 80–86 planning. Therefore indicator completion credit remains zero.

| Indicator | Current state | Mathematical acceptance |
|---|---|---|
| SMA20 | FOUNDATION 🟨 | First valid index 19; arithmetic mean of 20 closes |
| EMA20 | FOUNDATION 🟨 | First valid index 19; alpha 2/21; recursive seed contract fixed by tests |
| RSI14 Wilder | FOUNDATION 🟨 | First valid index 14; Wilder smoothing; no divide-by-zero NaN leak |
| MACD12/26/9 | FOUNDATION 🟨 | MACD line first valid index 25; signal/histogram index 33 |
| Bollinger20,2 | FOUNDATION 🟨 | First valid index 19; population standard deviation per current contract |
| Shared Indicator Hook | FOUNDATION 🟨 | 7 focused declarations; integration into chart still open |
| Footprint PRO 2GD | GATED 🟧 | Synthetic/offline accumulator only; visual implementation must match both supplied references |
| Volume Profile | OPEN 🟥 | Price-bin volume conservation, range semantics and timestamp boundaries |
| Complete Volume Profile | OPEN 🟥 | Full-session completeness, POC/VA derivation and conservation |
| Movable-range Volume Profile | OPEN 🟥 | User-selected range bounds and deterministic recomputation |
| Heatmap | OPEN 🟥 | Visual work waits for user reference image; no invented visual spec |
| Liquidation Maps | OPEN 🟥 | Data provenance and methodology not yet accepted |

Cross-indicator acceptance:
- prefix causality: appending future candles cannot alter prior outputs;
- no lookahead or future-candle repaint;
- exact timestamp/series identity alignment;
- warm-up values remain null until mathematically valid;
- stale output clears when series identity changes;
- no calculation for demo/loading/unavailable/error/empty snapshots;
- deterministic results for repeated identical input;
- bounded computation and no mutation of source candle data.
- Footprint OFF preserves standard candlestick spacing. Only explicit Footprint ON activates the spaced-cluster layout.
- Footprint/Heatmap visual implementation cannot start without the relevant user reference; Footprint references are already available, Heatmap reference remains outstanding.

Focused declaration inventory remains 28 (21 calculation + 7 shared hook). This is not a percentage or accepted indicator count. Chart integration remains open.

## 10. Progress ledger — no percentage inflation

- Stage 1: 30/40 = 75% provisional 🟨.
- Gate 10: 0/10 formally closed 🔴; criteria 8, 20, 25, 30, 31, 34, 35, 36, 38, 39.
- Stage 2: 🟦 PREPARATORY, not officially entered/scored.
- Stage 3: ⚪ NOT SCORED.
- Stage 4: 🟪 GATED.
- Stage 5: ⚪ NOT SCORED.
- Stage 6: ⚪ NOT SCORED.
- Overall project: ⚪ NOT SCORED (approved weighted denominator absent).
- IP3S/significant project index: ⚪ NOT SCORED (same reason).
- WebSocket production runtime: 🔴 OPEN.
- Gate 25 durable receipt/high-water ACK: 🔴 OPEN.
- Public Cloudflare WSS/device E2E: 🔴 OPEN.
- Owner-host backup/restore/monitoring: 🔴 OPEN.

Do not convert design completion into implementation completion. Do not award progress to indicator code for this package.

## 11. Exact CI and repository boundary

Source/test SHA `a2d2e7a03e2afee89429bb9d22c4641fd5b8a833` has previously recorded:
- Automated Tests: 41/41 workflow steps; 1,426 passed, 1 skipped, 6 warnings.
- CodeQL: 16/16 (Python 8/8; JavaScript/TypeScript 8/8).
- OCI ARM64: 7/7.
- Full-history Secret Audit: 6/6.
- Dedicated Redis TLS integration: 1 passed.

The current documentation checkpoint `fd756cee2bf3e427a628c3089c37d07d9f75ada7` is 12 commits ahead of that source/test SHA, zero behind, and the compare reports documentation files only. The current documentation HEAD uses `[skip ci]`, has no associated workflow runs/status checks, and is not represented as a new source CI success. Previously recorded source workflow jobs were rechecked as terminal success; no running jobs were left.

## 12. Ordered execution and exit gates

1. User review of this source/gateway runtime blueprint (change-control gate).
2. Batch 80: implement strict role config and unit tests; run full backend suite and security checks.
3. Batch 81: source factory and publisher integration tests; run full CI.
4. Batch 82: gateway factory and authenticated snapshot startup tests; run full CI.
5. Batch 83: real Redis multi-process/two-gateway/restart/fault tests; run full CI.
6. Batch 84: durable receipt/high-water ACK schema, migration, monotonicity and restart tests; review migration/rollback before applying anywhere.
7. Batch 85: existing Cloudflare route/origin mapping, public WSS and browser/Android E2E; no new infra.
8. Batch 86: owner-host backup/restore/monitoring/incident acceptance.
9. Re-run Stage 1 matrix and close only criteria with exact evidence.

No stage skip. No destructive retention. No production deploy. No paid service. Never leave CI running without checking it to terminal state. If CI fails, diagnose and fix on this branch before proceeding.

## 13. Controls

- Active branch only: `phase-2/market-data-foundation`.
- Never modify `main`.
- ZERO COST; no Vercel; no paid data, hosting, monitoring, backups, subscriptions or publication.
- No duplicate Cloudflare infrastructure; existing hosting topology must be verified.
- Preserve working features and exact source contracts.
- Do not ask the user to run unverified code or commands.
- Target planning date remains around 24 December 2026.
