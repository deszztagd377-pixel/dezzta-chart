# CME Session Calendar Engine

Status: **pinned calendar runtime, provider-session validation, and CME 1D/1W/1M/3M aggregation are implemented; an authoritative production schedule release is not configured.**
Last verified: 2026-11-13
Working branch: `phase-2/market-data-foundation`

## Purpose

Daily and higher OHLCV bars for CME futures must follow exchange trading sessions, not UTC midnight boundaries. The initial product families are CME equity index futures (ES, NQ) and COMEX Gold (GC). The calendar layer distinguishes regular sessions, special sessions, early closes, delayed opens, explicit closures, maintenance intervals, and unknown schedule coverage.

This is a data-integrity boundary for historical/educational chart data. It does not submit orders, connect to a live trading venue, or manufacture market observations.

## Implemented components

- `backend/app/session_calendar.py` defines immutable calendar releases, session records, explicit tradable segments, session lookup results, and session-aligned bucket bounds.
- Session boundaries use timezone-aware `America/Chicago` datetimes. UTC epoch-nanosecond conversion uses integer arithmetic; nonexistent and ambiguous Chicago wall-clock boundaries are rejected.
- Calendar mapping recognizes `CME_EQUITY_INDEX` for ES/NQ and `COMEX_GOLD` for GC. Instrument resolution uses the canonical instrument's explicit `session_calendar_id`; it never infers a calendar from a raw symbol.
- `backend/app/session_calendar_loader.py` validates versioned JSON artifacts, duplicate keys/dates, explicit coverage for every effective date, Chicago DST boundaries, CME-domain HTTPS provenance, and a SHA-256 digest supplied as a trusted external pin. Schema v2 supports explicit non-overlapping tradable segments.
- `backend/app/session_calendar_runtime.py` loads one explicitly pinned release per calendar ID atomically. A bad or incomplete release leaves the runtime registry unavailable; the loader does not fetch remote schedules.
- Provider bars are resolved through the durable point-in-time provider mapping and validated against the exact canonical instrument calendar and pinned release before persistence.
- CME daily bars use only complete UTC 1-hour child intervals that are fully contained in an explicit tradable segment, matching the accepted design. Smaller validated UTC intervals, including 1-second input, cascade through the normal intraday hierarchy to 1-hour; each complete hour is re-resolved against the same pinned calendar release before daily aggregation.
- CME weekly/monthly/quarterly bars are derived from session-aligned daily/monthly bars using explicit calendar bounds. Period bounds are withheld unless every civil date in the period, including closed dates, is represented in the release.
- CME bars carry `CME_SESSION_V1`, `calendar_id`, and `calendar_version` in their series identity. The SQLite OHLCV store persists these identity fields; UTC legacy/fixed identities remain separate.
- REST and WebSocket snapshots require an exact loaded calendar ID/version for CME-session series. A wrong calendar or unavailable release is rejected.

## Important integration boundaries

1. **No authoritative production schedule is loaded.** Current calendar artifacts in tests are synthetic test fixtures only. They are not official CME holiday/special-session data and must never be enabled as production releases.
2. **Production remains fail-closed without a trusted release.** Missing, stale, malformed, partial, or incorrectly pinned calendar data must not be interpreted as a regular session or a closure.
3. **Daily child resolution follows the accepted design.** CME 1D aggregation consumes only validated 1-hour children. One-second and smaller intraday inputs may contribute through the ordinary UTC intraday aggregation hierarchy, but a partial minute or hour can never bypass the 1-hour session boundary check.
4. **Completeness is separate from observed trades.** Live OHLCV observations do not prove continuous coverage because quiet intervals may contain no trades. A derived session bar is marked complete only when the coverage tracker has an accepted coverage basis; otherwise it remains partial.
5. **Provider semantics remain limited.** Databento `ohlcv-1s` is vendor-aggregated one-second OHLCV, not raw tick-by-tick or MBO data. Provider entitlements, schedule quality, latency, and all-contract coverage are not established by local tests.
6. **No paid infrastructure is authorized.** Do not buy market-data access, hosting, Redis, storage, domains, monitoring, or notification delivery to satisfy these remaining conditions.

## Required next engineering batch

1. Exercise the accepted 1-hour daily child-resolution path against authoritative session schedules, including early closes, delayed opens, and split tradable segments.
2. Obtain a genuine, authoritative CME schedule release for the supported product families. Record its exact source, publication/version, effective date range, and checksum; obtain the expected digest through an independently trusted channel.
3. Validate the release's holiday, early-close, delayed-open, and exceptional-session coverage. Do not replace missing schedule dates with guessed regular hours.
4. Exercise the selected pinned release through the complete ingestion, REST, WebSocket, browser, and Android paths in a zero-cost owner-controlled environment.
5. Keep production calendar acceptance open until the actual release and deployment evidence exist. Synthetic fixtures and green CI are repository evidence, not proof of official schedule correctness.

## Verification record

- Code and regression-test commit: `08bdf52cb60b2c98216df2437b3f9363cd4e2d66` (core aggregation change introduced in `a32ffe0dbf7eda05a1c69dfc41415b1da0274f79`).
- Automated Tests & Build: [run #1006](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43413442206) — **success**; backend suite **774 passed in 24.03s**. Frontend tests/build, dependency audits, synthetic outbox benchmark, Docker build, Redis + persistent-volume smoke test, Trivy scan, and vulnerability-report export/upload also succeeded.
- CodeQL Security Analysis: [run #364](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43413442133) — **success** for Python and JavaScript/TypeScript.
- Regression coverage includes the 1-second-to-1-minute path, 1-minute-to-1-hour-to-CME-daily derivation, direct validated 1-hour inputs, open/partial completeness semantics, rejection of an hourly child crossing a tradable-segment end, exact calendar identity in REST/WebSocket snapshots, and rejection of an unknown release.
- These checks do not prove an authoritative production schedule is loaded, live provider entitlement, production HTTPS/WSS, or production deployment readiness.
