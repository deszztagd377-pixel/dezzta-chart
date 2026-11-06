# CME Session Calendar Design (ADR)

Status: Accepted design; implementation not started  
Target branch: `phase-2/market-data-foundation`  
Decision date: 2026-11-05

## 1. Purpose and non-goals

Define a versioned, exchange-session-aware time model for CME equity-index futures ES/NQ and COMEX Gold futures GC. The design must prevent UTC calendar buckets from being confused with exchange trading-session buckets while preserving all previously stored UTC data.

This document is a design contract, not evidence of a working calendar, a live market feed, or production readiness.

Non-goals:
- Brokerage, order routing, execution, or trade recommendations.
- Inferring market state from the arrival or absence of OHLCV trades.
- Generating synthetic candles for intervals with no source records.
- Treating Databento `ohlcv-1s` as raw tick-by-tick or MBO data.

## 2. Product calendar mapping

| Instrument family | Calendar ID | Calendar source |
|---|---|---|
| ES, NQ | `CME_EQUITY_INDEX` | CME Group Equity Index futures schedule |
| GC | `COMEX_GOLD` | CME Group COMEX Gold schedule |

The regular Globex template currently documented by CME for these product families is Sunday through Friday, 17:00–16:00 America/Chicago, with a daily maintenance interval from 16:00–17:00 CT. This is only the regular template. It must not be treated as a complete holiday or exceptional-session calendar.

Authoritative references:
- Equity Index futures hours: https://www.cmegroup.com/markets/equities/sp-500-and-nasdaq-100-futures.html
- COMEX Gold product hours: https://www.cmegroup.com/markets/metals/precious/gold.timeAndSales.html
- CME holiday and trading-hours schedules: https://www.cmegroup.com/trading-hours.html

The calendar implementation must verify the exact product family and effective date against the official CME schedule before enabling a session. A generic exchange-wide schedule is not sufficient to infer every product's special hours.

## 3. Time and identity policies

Four distinct bucket policies are required:

- `UTC_LEGACY`: existing persisted bars. Preserve their current UTC interpretation and identity.
- `UTC_FIXED_V1`: newly accepted intraday bars from 1s through 4h. Fixed intervals remain UTC-aligned as currently specified.
- `UTC_PROVIDER_DAILY_V1`: provider-sourced 1D bars whose source defines a UTC calendar-day bucket. Preserve the vendor's UTC day semantics; never relabel these as CME sessions.
- `CME_SESSION_V1`: newly derived 1D, 1W, 1M, and 3M bars assigned using the applicable versioned CME trading calendar. This policy is not valid for an unverified provider UTC daily bar.

Every persisted bar and API representation using the new model must carry enough identity to distinguish `bucket_policy`, `calendar_id`, and `calendar_version`. The calendar fields are null for all UTC policies and required for `CME_SESSION_V1`.

The durable bar key must include all three policy fields. A calendar-version change must never silently overwrite bars generated under a prior version. Existing rows must be assigned `UTC_LEGACY` only; no history deletion, silent relabeling as CME, or mixed-policy aggregation is allowed. Provider daily bars accepted after rollout must be explicitly assigned `UTC_PROVIDER_DAILY_V1` when their source contract confirms UTC calendar-day semantics.

## 4. Trading-session semantics

Timezone: IANA `America/Chicago`, resolved with a timezone database (not a hard-coded UTC offset).

Regular session template:
- Session opens at 17:00 CT on the preceding civil day.
- Session closes at 16:00 CT on the trading-date civil day.
- The 16:00–17:00 CT interval is closed maintenance time.
- Sunday 17:00 CT opens the Monday trading session; its trading date is Monday.
- A scheduled holiday closure or special schedule overrides the regular template.

Represent session boundaries as timezone-aware instants and persist their UTC nanosecond values. Resolve DST using the IANA timezone database. Never calculate a session by adding a fixed 24-hour duration to its open instant.

A session lookup must return an explicit result such as open, maintenance, closed, or special-session, together with the schedule provenance. Unknown schedule data must fail closed for session labeling: do not guess a session boundary.

## 5. Higher-timeframe bucket rules

- `1D`: one CME trading session, from its actual 17:00 CT open to its actual 16:00 CT close on the trading date. Derive from session-contained 1H child bars, not 4H bars.
- `1W`: group the trading dates assigned to one CME trading week. Its boundaries must be obtained from the versioned calendar, not the host machine's Monday/UTC week.
- `1M`: group CME trading dates by Chicago-local trading month.
- `3M`: group CME trading dates by Chicago-local trading quarter (Jan–Mar, Apr–Jun, Jul–Sep, Oct–Dec).

For weekly/monthly/quarterly bars, store an explicit half-open UTC bucket interval and its trading-date range. Calendar periods with no source records must not create synthetic candles. The precise weekly period boundary and period-label convention must be represented in tests and API metadata before code rollout.

Provider-sourced daily data that uses a vendor's UTC calendar-day semantics must use `UTC_PROVIDER_DAILY_V1`. It must not be silently relabeled as `CME_SESSION_V1` or merged into a CME-session daily bar. If the provider's daily bucket semantics are unknown, reject or quarantine that bar from policy-aware aggregation rather than guessing.

## 6. Aggregation and completeness

Intraday 1s–4h aggregation remains under `UTC_FIXED_V1`. Higher timeframe session aggregation must use calendar-aware child selection:
- A 1D parent may include only child bars whose complete bucket interval is contained in that trading session.
- 1H children crossing a session boundary must be rejected for session aggregation.
- Weekly/monthly/quarterly aggregation may consume only child bars with matching calendar ID, version, policy, and trading-period membership.
- Existing provider-precedence, revision, duplicate, and eviction safeguards must remain intact.
- No bucket may be called complete merely because its observed OHLCV records span part of the session. Completeness requires an explicit successful coverage basis and calendar-aware expected-open intervals.
- A quiet interval with no trades is not, by itself, proof of a data gap. Feed health and trade observation freshness remain separate concepts.

## 7. Calendar data lifecycle

Calendar data must be versioned and auditable. Each schedule release or override must record:
- calendar ID and version;
- product family and applicable instruments;
- effective trading-date range;
- source URL or official source identifier;
- retrieval/publication timestamp;
- source checksum or immutable content identifier;
- explicit regular sessions, full closures, early closes, delayed opens, and exceptional sessions.

Do not hard-code a guessed list of future holidays. Do not treat an absent override as proof that the regular session applies unless the relevant official schedule version explicitly covers that date range.

If official schedule data is unavailable, malformed, stale beyond the configured policy, or contradictory, mark the calendar unavailable for the affected date range and do not emit a CME-session candle for it.

## 8. Migration sequence

1. Add a dedicated OHLCV schema-version table (for example `ohlcv_schema_meta`); do not change SQLite `PRAGMA user_version`, which is owned by the shared instrument registry.
2. Rebuild the OHLCV bar table transactionally where required to change its primary key; SQLite cannot add the required policy-aware primary-key columns with a simple `ALTER TABLE`.
3. Backfill every pre-existing row to `UTC_LEGACY` with null calendar fields; preserve all original timestamps, symbols, and OHLCV values exactly.
4. Add uniqueness constraints/indexes whose identity includes bucket policy, calendar ID, and calendar version. Ensure reads, writes, retention, revisions, and queries use the expanded identity consistently.
5. Add calendar data storage and validation without changing the active aggregation policy.
6. Add pure calendar boundary functions and DST/holiday tests.
7. Add calendar-aware 1D aggregation from session-contained 1H bars, initially behind a disabled feature flag.
8. Add 1W/1M/3M aggregation only after their trading-period boundaries and API semantics are tested.
9. Enable the policy only after migration, rollback, restart, legacy-data preservation, and full regression checks pass.

Each migration must be idempotent, transactional where SQLite permits, tested against a copy of a pre-migration database, and must preserve the shared instrument registry's `PRAGMA user_version` contract. A failed migration must leave the prior OHLCV table and all rows intact.

## 9. Required test matrix

- DST spring transition and fall transition in America/Chicago.
- Sunday reopen and Monday trading-date assignment.
- Daily 16:00–17:00 CT maintenance interval.
- Exact open/close boundary inclusivity and half-open interval behavior.
- Full holiday, early close, delayed open, and missing/unknown schedule data.
- ES/NQ mapping to the equity-index calendar and GC mapping to COMEX Gold.
- Daily 1H child selection, including rejection of any child crossing the session boundary.
- Weekly/monthly/quarterly trading-date membership and period boundary semantics.
- Vendor UTC daily isolation using `UTC_PROVIDER_DAILY_V1` from CME-session daily using `CME_SESSION_V1`.
- Reopening a shared database confirms the OHLCV migration does not alter the instrument registry's `PRAGMA user_version`.
- No synthetic bars for empty intervals.
- Coverage completeness with maintenance and scheduled closures excluded from expected-open time.
- SQLite migration, restart restoration, rollback, legacy row preservation, and policy-version coexistence.
- Existing UTC intraday 1s–4h tests and stream/API compatibility.

## 10. Release gates and claims

The calendar is not production-ready until official schedule ingestion, version pinning, product-specific exception handling, the complete test matrix, and migration rollback have passed.

A passing CI run proves only the configured tests for that commit. It does not prove live Databento delivery, real-time latency, provider SDK compatibility, or production deployment.

The current Databento source schema `ohlcv-1s` is vendor-aggregated one-second OHLCV. It is not raw tick-by-tick or MBO data. No claim of raw market-by-order fidelity may be made until a separately validated source and schema are implemented.
