# Work Cycle 2026-11-20 — Batch 62J-44 Gate 38 bounded metrics hardening

**Branch:** phase-2/market-data-foundation  
**Source commit:** 040c479bb01fd3d6d8f293aab7831164343ecac8  
**Regression-test commit:** a6acf605a44fe356602f92e8bc8e31d1f8e547b6  
**CI status at documentation time:** pending / not yet verified. The previous fully verified source/test checkpoint remains b576bbaa6e8b22af2f11e1e3f06565250ac193a1 (1,196 backend tests passed; six warnings; Automated Tests, CodeQL and Full Git History Secret Audit succeeded).

## Scope

This batch performs a source-level audit of Gate 38 observability metrics and hardens the boundedness of its in-memory accumulators. It does not change indicator calculations, chart rendering, WebSocket behavior, production configuration, deployment, or host logging.

## Findings already present before this batch

- Route/method series are bounded to 127 total, including the shared overflow series.
- Methods are allowlisted; status is reduced to a finite HTTP status class; malformed or overlong route labels collapse to unmatched.
- Request metrics are process-local and explicitly scoped process_local_since_start; they are not written to a metrics database.
- The internal metrics route is registered only when OBSERVABILITY_METRICS_TOKEN is configured.
- Authentication uses constant-time hmac.compare_digest against a Bearer token.
- Metrics responses use private no-store cache headers.
- Metrics, alert-delivery, and incident endpoints are excluded from request-metric self-observation; raw URL, query, path parameters, headers and client address are deliberately omitted from request logs.
- Snapshot results are detached from internal mutable state.
- Existing tests cover the 127-series cap, overflow accounting, invalid labels/durations, snapshot detachment, concurrency, authentication, query-string exclusion and token redaction.

## Defect corrected

Although series cardinality was bounded, individual integer counters and the accumulated floating-point duration had no explicit saturation ceiling. Over a sufficiently long process lifetime, counters could grow beyond exact JSON integer representation, and an accumulated floating-point sum had no explicit finite upper bound.

The implementation now uses:

- MAX_COUNTER = 2^53 - 1 for request counts, histogram counts and bucket counts.
- MAX_ACCUMULATED_MS = 86,400,000 × MAX_COUNTER for accumulated duration.

The duration ceiling is finite and derives from the existing one-day per-sample duration ceiling. This is a saturating telemetry policy: once a counter reaches its ceiling, later observations do not increase that value. It does not affect request handling or application decisions.

## Regression coverage added

A new test seeds a metric at each saturation boundary, records another sample, and asserts that request count, histogram count, bucket counts and accumulated duration remain capped. The test also checks that exported bucket counts remain integers within the JSON-safe ceiling.

## Verification boundary

- Source commit: 040c479bb01fd3d6d8f293aab7831164343ecac8.
- Test commit: a6acf605a44fe356602f92e8bc8e31d1f8e547b6.
- CI for the exact latest source/test commit has not yet been confirmed. Do not treat the new regression test as passed until the exact-head automated workflow and security workflows report success.
- No live host collector, log rotation, disk-retention, firewall, operator access or disk-pressure test was performed.

## Gate 38 disposition

**Gate 38 remains 🟧 OPEN.** Repository-level metric cardinality, input normalization, authentication, cache policy and accumulator bounds are now covered by source/tests. Remaining independent acceptance includes:

1. Owner-host firewall/reverse-proxy restriction for internal operations routes.
2. Actual operator-token injection, access review and rotation.
3. Bounded retention/rotation for host logs and any external collector.
4. Disk-pressure behavior and recovery on the intended host.
5. Credential redaction review across real process logs, crash reports and host monitoring.
6. Acceptance of the actual operator dashboard/collector access policy.

The application metrics snapshot itself is process-local and non-persistent; this is not a substitute for a host log retention policy.

## Project and indicator accounting

- Stage 1 remains **30/40 criteria = 300/400 ticks = 75% provisional**. No Stage 1 tick is added without a traceable acceptance-criterion mapping.
- Gate 10 remains **10/10 🟧 ORANGE / 0 formally closed**.
- WebSocket E remains complete for its defined automated CI failure-matrix scope; public WSS and production Redis acceptance remain external.
- SMA20, EMA20, RSI14, MACD12/26/9, Bollinger20,2 and Shared Indicator Hook remain 🟨 foundation.
- Footprint remains 🟧 SIMULATED and gated on owner reference image plus reviewed blueprint.
- Heatmap and Liquidation Maps remain 🟥.
- Stages 2–6, overall project percentage and aggregate indicator percentage remain unscored.
- ZERO COST maintained. No Vercel/Cloudflare deployment, paid provider, main modification, Termux or device operation.
