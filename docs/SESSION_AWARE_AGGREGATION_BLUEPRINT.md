# Session-aware OHLCV timeframe aggregation — owner review blueprint

Status: **OWNER-APPROVED BASIS — STAGED IMPLEMENTATION AUTHORIZED (2026-11-10)**

Branch: `phase-2/market-data-foundation`

## 1. Purpose and non-goals

Define a safe route from the current fail-closed CME futures aggregation path to exchange-session-aligned derived OHLCV for every supported timeframe. This blueprint does not enable provider ingestion, invent market bars, alter licensing, or start Footprint/Heatmap UI work.

The implementation must preserve exact canonical series identity, provider-bar precedence, durable outbox semantics, and explicit completeness/provenance. Unknown calendar coverage must remain a hard stop, not a fallback to UTC.

## 2. Verified current state

- `backend/app/aggregation.py` skips derivation for every `CME_SESSION_V1` child bar. This is intentional protection against incorrect exchange-session bucket labels.
- `UTC_FIXED_V1` aggregation currently stops before `1d`, `1w`, `1M`, and `3M`.
- `backend/app/session_calendar.py` provides immutable, provenance-bearing calendar releases and `session_bucket_bounds` for `1d`, `1w`, `1M`, and `3M`. It requires explicit records for every calendar date in a requested period; a missing record is UNKNOWN, not a closed day.
- `SessionRecord` supports an immutable tuple of explicit `SessionSegment` intervals. Schema-v2 artifacts can represent multiple tradable segments and breaks; schema-v1 remains supported as a single open/close interval for compatibility. Segment boundaries are validated for Chicago timezone validity, ordering, non-overlap, and containment within the session envelope.
- `lookup_instant` classifies gaps between explicit tradable segments as `maintenance`, while retaining the owning trading-date/session envelope. The separate generic 16:00–17:00 maintenance classification remains conditional on explicit adjacent regular-session records; it is not a substitute for per-date segment data.
- Existing tests assert that CME-session bars remain unaggregated and that UTC-fixed aggregation does not derive daily+ bars.

## 3. Proposed architecture

### A. One bucket resolver contract

Introduce a pure resolver abstraction used by the aggregator, conceptually:

- Input: canonical instrument/calendar identity, calendar version, source bucket policy, timeframe, and child-bar timestamp.
- Output: exact `start_ns`, `end_ns`, calendar ID/version, trading-period identity, and a deterministic bucket key; or an explicit unresolved result.
- It must never infer calendar identity from a raw symbol. Resolve only from the canonical instrument registry and the exact pinned calendar release.
- Resolver output must be deterministic for the same immutable calendar version and input timestamp.

The aggregation engine should depend on this contract rather than embed exchange time arithmetic.

### B. Explicit intraday session segments

Before enabling intraday futures aggregation, extend the versioned calendar artifact model to represent the actual tradable segments and non-trading breaks for each trading date. A single open/close pair is insufficient to safely encode all session boundaries and breaks.

- Segment boundaries must be timezone-aware Chicago-local instants, converted to integer epoch nanoseconds without floating-point timestamps.
- Validate ordering, non-overlap, containment within the trading date's declared session, and exact calendar provenance.
- Early closes, delayed opens, special sessions, holidays, maintenance breaks, and DST transitions must be explicit source records.
- Do not hardcode a generic 16:00–17:00 break as a substitute for sourced per-date schedule data.
- For an intraday timeframe, generate bucket bounds only within a tradable segment. Never create a bucket spanning a break or merge two segments into one candle.
- Decide and document the alignment anchor (segment-open aligned versus exchange-defined clock grid) per calendar policy before coding. Do not silently change alignment between releases.

### C. Higher timeframes

Reuse `session_bucket_bounds` for `1d`, `1w`, `1M`, and `3M` only after integration tests prove the aggregator passes the exact calendar version and trading date.

- Daily bounds come from the explicit trading-date record.
- Weekly/monthly/quarterly bounds require complete explicit date coverage, including explicit closed dates.
- A missing date, invalid release, checksum/version mismatch, or unresolved instrument calendar must produce no derived bar and a measurable unresolved-coverage reason.
- Preserve provider-supplied parent bars as authoritative; derived bars must never overwrite them.

### D. Aggregation and revisions

- Partition children by complete canonical series identity and exact bucket key.
- Include only child bars whose timestamps fall inside the resolved tradable bucket.
- Recompute deterministically after legitimate late revisions or cancellations; prevent duplicate volume counting.
- Preserve existing completeness semantics. Missing expected child intervals must not be silently filled with synthetic OHLCV.
- Keep derived origin, source timestamps, calendar ID/version, bucket policy, and completeness attached to each persisted bar and outbox event.
- A calendar version change must not mutate the meaning of already-persisted bars in place. Require an explicit reprocessing/migration policy.

## 4. Required test matrix before enabling any timeframe

1. Regular overnight session and Sunday reopen/trading-date assignment.
2. Regular maintenance break and any additional explicitly sourced breaks.
3. DST spring-forward and fall-back transitions in America/Chicago.
4. Holiday and explicitly closed trading dates.
5. Early close, delayed open, and special session.
6. Calendar effective-range edges, missing date records, bad checksum, and unknown calendar version.
7. Every supported intraday interval: `5s, 15s, 30s, 45s, 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 4h`.
8. Daily, weekly, monthly, and quarterly boundaries.
9. Bars exactly at segment open, bucket boundary, segment close, and break start/end.
10. Gaps, duplicate bars, out-of-order arrival, late corrections, provider parent-bar precedence, and incomplete periods.
11. Multiple instruments and timeframes concurrently, with no cross-series contamination.
12. Persist/restart/replay round-trip proving the same bucket identity and payload survive the durable outbox.

Property-based tests should additionally prove that generated buckets are ordered, non-overlapping, contained within tradable segments, and stable for a pinned calendar release.

## 5. Rollout and fail-closed gates

1. Implement schema/parser validation and pure resolver functions behind tests; keep production derivation disabled.
2. Add unit/property tests and deterministic fixture calendars with explicit provenance.
3. Add integration tests through the real ingestion → aggregation → persistence → outbox path.
4. Run benchmarks for every timeframe and concurrent series; measure event-to-client latency and gap/completeness behavior.
5. Verify actual provider SDK callbacks, entitlements, symbol universe, and source schema separately.
6. Enable only calendar/timeframe combinations with complete evidence. Keep unsupported combinations rejected and visible in status/coverage diagnostics.

No all-pairs or all-timeframes LIVE claim is allowed until provider coverage and latency evidence exist for the configured instrument universe.

## 6. Owner decisions and implementation guardrails

- Owner approved this blueprint as the engineering basis for staged implementation on 2026-11-10.
- The approval does not authorize guessed exchange rules. The bucket alignment policy must be selected from authoritative exchange specifications and recorded with source evidence before the resolver is enabled.
- Calendar-version corrections must preserve immutable historical interpretation until an explicit migration/backfill policy is evidenced and reviewed.
- Rollout is approved only for verified calendar/timeframe combinations; all others remain fail-closed.

The CME-session aggregation skip must remain in place until the resolver, exact calendar provenance, integration tests, and per-timeframe evidence are complete. This approved workstream is part of Stage 1 acceptance, not a separate stage.


## Owner approval record — 2026-11-10

The project owner approved this blueprint as the basis for staged implementation and explicitly requested that session-aware aggregation be integrated into Stage 1 completion. Work must remain on `phase-2/market-data-foundation`; no change to `main` is authorized. Approval is not evidence that any calendar/timeframe is production-ready and does not waive tests or external provider verification.
