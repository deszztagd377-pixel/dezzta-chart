# DEZZTA CHART — Work Cycle 71
## Gate 10 / official stage boundary reconciliation and Gate 25 transport blueprint

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent HEAD: `19de41d3dc613a11a0441e65a075f7a1ed5cc685`  
Scope: reconcile Stage 1 vs Stage 2 accounting; close documentation drift; prepare the missing owner-controlled Gate 25 transport contract for review.  
Cost: ZERO COST.  
Runtime/source changes: none.  
Stage/indicator credit: none.

## 1. Exact-head CI closure on Batch 70

All four workflows completed successfully on the exact parent HEAD `19de41d3dc613a11a0441e65a075f7a1ed5cc685`:

| Workflow | Run | Result |
|---|---:|---|
| Automated Tests | 45595701779 | 🟩 SUCCESS — 41/41 steps |
| CodeQL Security Analysis | 45595699924 | 🟩 SUCCESS — Python 8/8; JavaScript/TypeScript 8/8 |
| OCI ARM64 Image Readiness | 45595699845 | 🟩 SUCCESS — 7/7 |
| Full Git History Secret Audit | 45595699982 | 🟩 SUCCESS — 6/6 |

Automated Tests backend summary: **1,426 passed, 1 skipped, 6 warnings in 63.60 seconds**. All four run records reference the same exact parent SHA. This is repository/CI evidence only; it does not prove owner-host, public WSS, Firebase production, Android device, or live-provider acceptance.

## 2. Official stage boundary — definitive interpretation

The official six-stage roadmap explicitly names **Stage 1 — Foundation, Security & Data Integrity** as the current official stage. The Stage 2 branch/workstream name is technical naming, not a stage transition.

- Stage 1 has 40 acceptance criteria; 30 have repository implementation/test or approved design evidence.
- The remaining ten external acceptance criteria are 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39.
- The provisional Stage 1 meter remains 30/40 = 75%.
- Stage 2 market-data code and design work exists as early/preparatory foundation work on the technical branch. This is permitted as parallel groundwork where it does not waive or falsify Stage 1 acceptance.
- Stage 2 is **not the official active stage yet**. The official stage transition waits for Stage 1 acceptance.
- Stages 3–6 remain unscored/not officially opened. Stage 4 indicator UI remains gated.
- The 40% overall-project threshold is a separate permission to prepare broader UI/feature blueprints and review them. It does not override the six-stage order, Stage 1 exit criteria, or Stage 4 indicator gate.

### Gate 10 is not a bucket of work transferred to Stage 2

Gate 10 is the roll-up of the ten outstanding Stage 1 acceptance criteria. It is not a separate phase that moves as a whole into Stage 2. Some implementation work can be shared or provide prerequisites for later stages, but the acceptance evidence remains attached to the criterion that requires it.

| Stage 1 criterion | Required external acceptance | Status |
|---:|---|---|
| 8 | Actual owner-host secret injection, ownership/mode, runtime exposure and rotation proof | 🟨 Host proof pending |
| 20 | No-billing Firebase sign-in, expiry/revocation, entitlement denial, ticket exchange and client reconnect | 🟥 Open |
| 25 (Stage 1 checklist) | Owner-hardware Redis TLS, ACL, private binding, persistence and failure/restart recovery | 🟥 Open |
| 30 | Actual application database restore to a fresh target and application-level readback | 🟨 Owner-target drill pending |
| 31 | Encrypted off-host backup, independent key custody and recovery restore | 🟥 Open |
| 34 | Actual persistent-volume mount, permissions, restart durability and disk-pressure recovery | 🟨 Host proof pending |
| 35 | Backend runtime/health/secret injection on existing owner hardware | 🟨 Host proof pending |
| 36 | Authenticated HTTPS/WSS through owner-controlled ingress from real browser and Android clients | 🟥 Open |
| 38 | Durable owner-host metrics, retention, backup/restore, dashboard and independent alert/ACK/recovery | 🟧 Open |
| 39 | Zero-cost local alert route and incident escalation/acknowledgement/recovery drill | 🟨 Operator drill pending |

No Gate 10 criterion is formally closed: **0/10**. Yellow/orange means repository readiness or partial preparation, not acceptance. A CI pass, document, synthetic fixture or code path cannot substitute for real owner-host/device evidence.

### Critical naming distinction: two different “25” items

1. **Stage 1 criterion #25** is owner-host Redis TLS/ACL/private-binding/persistence/restart acceptance.
2. **Project Gate 25** is the Ed25519 signed-snapshot installation, authenticated receipt custody and per-gateway high-water acknowledgement path.

They are separate work items. Both remain open. Project Gate 25 contributes to the broader WebSocket/data-integrity workstream; it does not replace Stage 1 criterion #25.

## 3. Gate 25 latest verified state

Repository-side foundations already present:
- Ed25519 source manifest signing and owner-pinned gateway public-key allow-list.
- Signature binding for source, generation, high-water cursor, retention floor, bar-retention policy, row count, format and canonical SHA-256 digest.
- Gateway startup re-verifies the persisted receipt before Redis client construction.
- Source-side validation requires one authenticated, owner-signature-verified receipt per configured gateway, unique durable replica IDs, signer identity, stream/generation/cursor and digest binding.
- Local snapshot install/checkpoint and local receipt persistence have repository regression coverage.

Remaining blocker:
- The source/gateway runtime factories require injected callbacks.
- Default `app = create_app()` and the Docker ASGI entrypoint do not supply owner-controlled source/gateway transport callbacks.
- No actual authenticated owner-host snapshot transfer or remote persisted-receipt retrieval is proven.
- Local gateway `applied_cursor` and Redis `XACK` do not constitute a source-side durable per-gateway high-water ACK ledger.

No fake callback, synthetic remote receipt, guessed endpoint, or local-only adapter is to be represented as production wiring.

## 4. Gate 25 transport contract — design for owner review only

This is a contract-level blueprint, not an endpoint choice or authorization to implement runtime changes.

### 4.1 Roles and trust boundaries

- **Authoritative source host:** holds the Ed25519 private key outside Git and container artifacts; exports a signed snapshot manifest and canonical snapshot bytes.
- **Gateway replica:** authenticates the source, downloads/installs the exact generation, commits bars/checkpoint/immutable receipt atomically, and exposes the persisted receipt only to an authenticated owner/source identity.
- **Source-side owner coordinator:** has a fixed owner-controlled gateway inventory; retrieves each gateway's persisted receipt, verifies it, and records a durable per-gateway acknowledgement.
- **Redis:** carries the stream only after source/gateway startup prerequisites pass. Redis consumer-group ACK is not the owner retention-floor ACK.

### 4.2 Required abstract operations

The transport must provide these operations without trusting caller-supplied gateway identity:

1. `fetch_snapshot(gateway_identity, source_id, generation_id)` — authenticated gateway fetches the signed manifest and bounded snapshot stream from the authoritative source.
2. `install_snapshot(source_identity, manifest, content_stream)` — gateway validates source identity, Ed25519 signature, canonical digest, schema and monotonic generation before atomic installation.
3. `read_persisted_receipt(source_identity, source_id, generation_id)` — owner/source retrieves the immutable receipt from the actual gateway after installation and after gateway restart.
4. `record_gateway_ack(gateway_id, replica_id, generation_id, high_water, digest, receipt_identity)` — source persists an independently verified ACK under a fenced owner epoch.
5. `read_ack_ledger(source_id)` — retention controller reads the complete durable gateway ACK set; missing, stale, conflicting or unknown gateway entries fail closed.

The actual HTTP/TCP/SSH/private-network protocol, endpoint addresses and authentication mechanism are intentionally **not selected** by this document. They must match infrastructure that already exists and can be operated at zero incremental cost.

### 4.3 Mandatory transport security

- Mutual authentication or an equivalent owner-controlled cryptographic channel with pinned peer identity; TLS certificate and hostname verification cannot be disabled.
- Gateway identity is derived from authenticated peer credentials/certificate mapping, never accepted from a request body alone.
- No public unauthenticated endpoint; no redirect to an untrusted host; no arbitrary URL or path supplied by clients.
- Bounded connect/read/write/overall deadlines, bounded payload size, streaming transfer, and bounded retry with jitter only where deterministic idempotency is preserved.
- Snapshot bytes are hashed while streaming and checked against the signed manifest before commit.
- Temporary files use private permissions and safe no-follow creation; incomplete transfers are discarded on restart.
- Generation monotonicity and same-generation/different-digest conflict rules remain fail closed.
- Receipt retrieval happens after durable commit and must still succeed after gateway process restart.
- Secrets and private keys never appear in logs, error messages, test fixtures committed to Git, client bundles or receipts.

### 4.4 Durable acknowledgement ledger

The source-side ledger must be independent of Redis `XACK` and persist at least:
- source ID and authenticated gateway ID;
- durable replica ID;
- installed generation ID;
- high-water cursor;
- canonical snapshot digest;
- receipt identity and owner-signature verification result;
- owner fencing epoch / generation;
- acknowledgement timestamp and schema version.

Updates must be transactional and monotonic. A stale owner epoch cannot overwrite a newer ACK. Duplicate identical ACKs are idempotent. A lower cursor, changed digest for the same generation, unknown gateway, missing receipt, or stale epoch is rejected. The ledger must survive source process restart and be reconciled against the configured gateway inventory before any retention decision.

### 4.5 Redis retention safety

Keep `XTRIM`, `XDEL` and consumer-group destruction disabled. They remain prohibited until:
- all required gateways are inventoried and retirement is explicitly reconciled;
- every required gateway has a persisted, re-verified receipt;
- every gateway has a durable source-side ACK at or beyond the proposed retention floor;
- pending-entry and consumer-group state are reconciled;
- a separate retention authority applies the floor under a fenced owner epoch;
- crash/restart tests prove no trim can occur from a partial ACK set.

### 4.6 Zero-cost transport selection — unresolved owner input

Only an already-owned host/network path with no incremental billing can be considered. A new domain, VPS, paid tunnel, managed Redis, hosted queue, paid market-data service or trial that can bill is out of scope. A free tier is not presumed permanent or suitable without current terms and limits being verified.

**Review decision required before runtime implementation:** identify the existing authoritative source host and gateway reachability/authentication path, or explicitly state that no such always-on owner-controlled environment exists. If none exists, Gate 25 remains externally blocked; do not fabricate an implementation to make the dashboard green.

## 5. Indicator progress — no change and no completion credit

| Indicator / subsystem | Calculation/data foundation | Visible chart acceptance | Status |
|---|---|---|---|
| SMA20 | 20-close arithmetic mean; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 FOUNDATION |
| EMA20 | SMA-seeded EMA; alpha 2/21; first valid index 19 | Overlay, toggle, legend/latest value and lifecycle absent | 🟨 FOUNDATION |
| RSI14 Wilder | 14-change seed + Wilder recurrence; first valid index 14 | 0–100 pane, 30/70 guides and lifecycle absent | 🟨 FOUNDATION |
| MACD12/26/9 | MACD first index 25; signal/histogram first index 33 | Dedicated pane, lines, histogram and zero guide absent | 🟨 FOUNDATION |
| Bollinger20,2 | 20-close mean ± 2 population SD; first valid index 19 | Upper/middle/lower overlays, fill and lifecycle absent | 🟨 FOUNDATION |
| Shared Indicator Hook | Keyed immutable backend snapshot/cache/trust gate; 7 hook test declarations | Not integrated into `CandlestickChart.tsx` | 🟨 FOUNDATION |
| Footprint PRO 2GD | Synthetic/offline accumulator only; not exchange-native bid/ask truth | Stage 4 gated; two supplied visual references remain authoritative | 🟧 GATED |
| Volume Profile | Full binning/value-area behavior not accepted | Not integrated | 🟥 OPEN |
| Complete Volume Profile | Session/range/POC/VAH/VAL methodology not accepted | Not integrated | 🟥 OPEN |
| Movable-range Volume Profile | Range selection/recalculation lifecycle not accepted | Not integrated | 🟥 OPEN |
| Heatmap | Lawful depth source, aggregation and decay not accepted | Not integrated; visual reference gate remains | 🟥 OPEN |
| Liquidation Maps | Provenance, estimation methodology and confidence limits not accepted | Not integrated | 🟥 OPEN |

Focused declaration inventory: **21 calculation + 7 shared-hook = 28 declarations**. This is not a pass count or completion percentage. Mathematical invariants remain warm-up nulls, prefix causality, no future-candle lookahead, exact timestamp/series alignment, stale-output clearing on identity change, and no output from demo/loading/unavailable/error snapshots. Footprint OFF preserves normal candle spacing; only explicit ON uses spaced candle clusters.

Aggregate indicator completion: ⚪ NOT SCORED. No indicator source/test/UI changes in this cycle.

## 6. Reconciled project dashboard

| Meter | Verified state | Status |
|---|---:|---|
| Stage 1 — official active stage | 30/40 = 75% provisional | 🟨 |
| Stage 2 — early technical foundation only | No approved denominator; not official stage transition | 🟦 PREPARATORY |
| Stage 3 | Not officially scored/opened | ⬜ |
| Stage 4 — Indicators & Analytics | Stage gate + scoped blueprint/review required | 🟪 GATED |
| Stage 5 | Not officially scored/opened | ⬜ |
| Stage 6 | Not officially scored/opened | ⬜ |
| Gate 10 | 0/10 formally closed | 🟥 |
| Project Gate 25 | Owner transport, receipt retrieval and durable ACK absent | 🟥 |
| Gate 36 public WSS/TLS/Firebase/device | Production acceptance absent | 🟥 |
| Redis destructive retention | Safety prerequisites not met | 🟧 BLOCKED |
| Overall project | No approved weighted six-stage denominator | ⚪ NOT SCORED |
| Aggregate indicators | No approved weighted indicator denominator | ⚪ NOT SCORED |
| Significant progress / IP3S | No approved reproducible formula applied | ⚪ NOT SCORED |

No progress ticks are awarded by documentation or Batch 70 CI alone.

## 7. Ordered next work — sequence preserved

1. Owner review of the Gate 25 transport contract and identification of the existing zero-cost owner-host/gateway path.
2. Only after review: implement the owner-host callback composition with pinned peer identity, bounded transfer and fail-closed startup.
3. Add durable per-gateway high-water ACK ledger with fencing, restart and stale-owner regression tests.
4. Prove real signed snapshot transfer and receipt re-verification after gateway restart.
5. Complete Stage 1 criterion #25 Redis owner-host TLS/ACL/private-binding/persistence/restart acceptance.
6. Continue remaining Stage 1 host/device evidence in the documented order; no gate is waived by CI.
7. Complete Gate 36 public WSS/TLS/Firebase and browser/Android acceptance only through an existing zero-cost environment.
8. Keep destructive Redis retention blocked until every independent safety prerequisite passes.
9. Keep major indicator UI behind the official Stage 4 gate and scoped blueprint/review.

Target remains approximately **24 December 2026**, not month-end. ZERO COST, `main` untouched, Vercel deferred, no production credentials or destructive Redis action.
