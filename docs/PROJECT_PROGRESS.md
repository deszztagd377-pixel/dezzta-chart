# DEZZTA CHART — Progress Record

Last verified snapshot: 2026-11-05  
Repository: https://github.com/deszztagd377-pixel/dezzta-chart  
Working branch: `phase-2/market-data-foundation`  
Snapshot HEAD before this progress-history correction: `89a1738e29ad4291299a4552e7056886e0e5c4bf`  
Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1`



## Owner correction — historical conversational checkpoints (2026-11-05)

The owner clarifies the sequence of previously communicated conversational progress checkpoints: **20.3% first, then 20.9%**. The 20.9% checkpoint was celebrated as having crossed 20%; it must not be erased or silently replaced by the older 19.60% figure.

Interpretation and accounting safeguards:
- **20.3% → 20.9%** is the owner's correction of the historical conversation sequence. Preserve both values and their order.
- **19.60%** remains the older value formally recorded in PROJECT_STATUS.md; it is not evidence that the project later regressed.
- **19.9%** has no verified calculation in the current repository record and must not be presented as a valid current percentage.
- The exact milestone formula behind the conversational 20.3% and 20.9% checkpoints has not yet been recovered. Therefore 20.9% is the latest owner-confirmed conversational checkpoint, while a newly recalculated weighted percentage remains pending a reproducible ledger.
- Do not lower, raise, or average these values to manufacture a current percentage. Reconcile the milestone weights and verified deliverables first, then document any correction transparently.

## Current percentage record

| Record | Value | Meaning |
|---|---:|---|
| Last formally weighted estimate in `PROJECT_STATUS.md` | **19.60%** | Historical formal estimate; last documented increment was +0.20 percentage points from 19.40% |
| Owner-confirmed conversational sequence | **20.3% → 20.9%** | Earlier then later checkpoint, clarified by the owner; formula/evidence ledger still needs reconstruction |
| Freshly reconciled overall percentage | **Not yet established** | Do not present either historical value as a newly recalculated current percentage |

The project percentage is a weighted milestone estimate toward the intended full application. It is **not** the percentage of files written, lines of code, commits, or CI jobs completed. A documentation-only commit or a passing CI run does not automatically increase overall project completion.

## Proposed weighted ledger

A proposed eight-group, 100%-total milestone model is now available in [PROJECT_MILESTONE_LEDGER.md](PROJECT_MILESTONE_LEDGER.md). It separates visible chart capability, data contracts/persistence, security, interaction tools, educational indicators, responsive UX, settings/watchlist, and release quality. The weights are a proposal only; criterion-level scoring and owner review are still required before calculating a new overall percentage.

## Why the discrepancy remains open

The repository now contains a proposed consolidated ledger, but it has not yet been approved or scored. A reproducible final calculation still requires:
1. Defines the complete project milestone groups and their total weights (100%).
2. Defines objective acceptance criteria for each milestone.
3. Assigns completion credit only to verified deliverables, avoiding duplicate credit for the same capability across commits.
4. Separates implemented code, automated tests, user-visible behavior, deployment verification, and owner-approved design.
5. Records evidence links and the calculation used for each percentage change.

Until the proposed ledger is reviewed and scored, **19.60% and 20.9% remain historical references**, not competing freshly verified measurements. Do not choose one by guesswork and do not increase the percentage merely because more commits exist.

## Verified evidence at this snapshot

- Working branch HEAD: `8ae99f5c5a11cdfb8b5d52acc1455a47259f194b`.
- Main HEAD: `e3841681bc69b73619058deaf939df82ae5116a1`; main was not modified by the audited work.
- GitHub Actions run [42053572558](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42053572558) completed successfully on the exact working-branch HEAD.
- The CI job passed frontend dependency installation, frontend unit tests, frontend production build, backend dependency installation, backend pytest, and backend container-image build.
- The repository has no root `package-lock.json`; the current CI uses `npm install`. Reproducible frontend dependency installation remains an open quality task.
- The latest verified code audit confirms code-level authenticated frontend stream integration. It does not establish deployed backend operation, live provider delivery, synchronized exchange time, or production performance.

## Product expansion gate — owner clarification (2026-11-05)

The owner has clarified that major UI reconstruction and broad feature expansion may begin at **40% overall project progress**, rather than 50%.

At the 40% gate:
1. Reconcile and publish the weighted milestone ledger.
2. Prepare a scoped UI/feature blueprint using the owner's visual preferences.
3. Review scope and priorities with the owner before large implementation.
4. Implement incrementally with tests and acceptance checks.

Before 40%, prioritize foundation quality, reliability, documentation, secure configuration, dependency hygiene, accessibility, responsive behavior, and regression coverage. The 40% gate is a planning checkpoint, not a promise that all planned features will be complete.

## Next progress-accounting work

- Rebuild the milestone weight model from the actual product scope.
- Map each verified implementation to exactly one primary milestone to prevent double counting.
- Separate completed, partial, blocked, planned, and unverified work.
- Reconcile the historical 19.60% and owner-recalled 20.9% values with evidence.
- Publish a new percentage only after the calculation is reproducible and the owner has reviewed the model.

---

## Verified checkpoint — CME session-calendar foundation (2026-11-07)

Working branch: `phase-2/market-data-foundation`  
Audited HEAD: `001299360b038b1b85fdbf8c9e2cdda47afe7b5c`  
CI run: [#42340030836](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42340030836) — **success**.

### Verified completed in this checkpoint

- Added `backend/app/session_calendar.py` with immutable calendar/session records, Chicago timezone-aware boundaries, explicit provenance metadata, calendar/product-family validation, and integer nanosecond conversion.
- Added fail-closed lookup semantics: missing schedule coverage is `unknown`, not an assumed regular session or holiday.
- Added Sunday reopen / adjacent trading-date resolution, DST-aware timezone handling, regular maintenance classification, and special/early-close handling.
- Added daily, weekly, monthly, and quarterly session-bucket-bound resolution. A period is returned only when every trading-date record in its full date range is explicitly covered; closed dates must also be represented.
- Added calendar tests in `backend/tests/test_session_calendar.py` for DST, reopen, maintenance, missing dates, explicit closures, special sessions, validation, and higher-timeframe bounds.

### CI evidence

The exact HEAD above passed all steps in the single GitHub Actions job: frontend dependency installation, frontend unit tests, frontend production build, Python setup, backend dependency installation, backend tests, and backend container-image build.

### Current integration boundary — not yet complete

- `backend/app/aggregation.py` still deliberately skips UTC-fixed child bars when deriving `1d`, `1w`, `1M`, and `3M`.
- `backend/app/ohlcv.py` currently supports only `UTC_LEGACY` and `UTC_FIXED_V1` bucket policies; `OhlcvBar` rejects calendar metadata under those policies.
- Therefore the new calendar primitives are **not yet connected to production aggregation**, and no CME session-aligned OHLCV should be claimed as active.
- No authoritative CME schedule release has been loaded. Tests use constructed fixtures only; they are not exchange-calendar data.
- The SQLite OHLCV store has already been audited: schema version 2 persists `bucket_policy`, `calendar_id`, and `calendar_version`, and all three participate in the bar primary key and series index. No SQLite migration is currently indicated for this integration.
- Next implementation must enable and validate the session bucket identity in `OhlcvBar`, preserve it through adapters and derived bars, and gate aggregation on a matching, fully covered calendar release. Existing UTC intraday behavior must remain unchanged.

### Progress accounting

The prior owner-confirmed conversational checkpoints remain **20.3% then 20.9%**. A newly reconciled weighted overall percentage is still **not established** because the proposed milestone ledger has not been approved and scored criterion-by-criterion. This calendar work is recorded as verified foundation work, not converted into an invented percentage increase.

SQLite is considered complete for the current foundation scope. No SQLite rework is scheduled unless a concrete regression or missing acceptance criterion is found.


### Follow-up persistence audit — 2026-11-07

A targeted audit of `backend/app/ohlcv_store.py` and `backend/tests/test_ohlcv_store.py` confirmed that OHLCV SQLite schema version 2 already persists calendar identity fields (`bucket_policy`, `calendar_id`, `calendar_version`) and includes them in the composite primary key and series index. Existing policy-isolation and legacy migration tests are present. **No SQLite schema change is currently required for the next calendar integration step.** The remaining enablement work is in the OHLCV model/adapter/aggregation contract; this is not a reason to reopen completed SQLite work.


## Indicator progress tracker — audited 2026-11-07

This tracker is intentionally separate from the CME calendar work so indicator progress is never omitted from a project checkpoint.

| Indicator / layer | Verified repository state | User-visible completion |
|---|---|---|
| SMA 20 | Calculation function and unit tests exist | Not integrated into visible chart UI |
| EMA 20 | Calculation function and unit tests exist | Not integrated into visible chart UI |
| RSI 14 (Wilder) | Calculation function and unit tests exist | Not integrated into visible chart UI |
| MACD | Calculation function and unit tests exist | Not integrated into visible chart UI |
| Bollinger Bands | Calculation function and unit tests exist | Not integrated into visible chart UI |
| Shared indicator hook | `useMarketIndicators()` consumes only validated backend data from the shared market-data store; DEMO/loading/unavailable/error states yield no values | Hook exists; no visible indicator controls/panes |
| Footprint | Offline deterministic simulated aggregation engine and fixtures exist; buy/sell/unknown are kept separate and duplicate event IDs are rejected | Not visually implemented; must remain clearly SIMULATED; wait for owner's Footprint reference image |
| Heatmap | No implementation verified in this audit | Pending owner reference image and later scoped implementation |
| Liquidation Maps | No implementation verified in this audit | Pending owner reference image and later scoped implementation |

### Indicator constraints and next gates

- Every indicator must use the exact validated chart series for the currently selected canonical instrument and timeframe; no separate price source or sample-candle substitution.
- Calculation helpers and tests are groundwork only. They are not counted as visible, usable indicator features.
- Do not begin Footprint visual layout before the owner supplies its reference image. Ordinary candles and spacing must remain unchanged when Footprint is OFF; only explicit Footprint ON may activate the dedicated spaced cluster layout.
- Heatmap and Liquidation Maps visual work likewise waits for their respective owner reference images.
- The project expansion gate is 40% overall. Before that gate, retain the calculation/data-integrity foundations and tests; prepare a scoped blueprint and obtain owner review at the gate before major UI implementation.
- No indicator may be presented as predictive or as buy/sell advice. Simulated Footprint data must retain a visible SIMULATED label and must never be confused with market observations.


### CME session identity contract — 2026-11-07

Implemented a bounded first integration slice on the active foundation branch:

- Added the explicit `CME_SESSION_V1` bucket-policy identity to the OHLCV contract.
- CME session bars are structurally limited to `1d`, `1w`, `1M`, and `3M`, and require both `calendar_id` and `calendar_version`.
- Session starts are no longer incorrectly forced onto UTC midnight/fixed-interval boundaries; the exchange calendar must validate the actual session bounds before production ingestion.
- UTC policies still reject calendar metadata and retain their existing UTC alignment checks.
- Aggregation explicitly skips CME-session-policy bars until a verified calendar-bound resolver is connected. This is a fail-closed guard, not active CME aggregation.
- Added OHLCV model tests and an aggregation regression test for the new contract.

Files changed in this slice:
- `backend/app/ohlcv.py`
- `backend/tests/test_ohlcv.py`
- `backend/app/aggregation.py`
- `backend/tests/test_aggregation.py`

The earlier run `42352853145` was subsequently cancelled during frontend dependency installation; the next run `42353072145` completed successfully across all listed frontend/backend test and build steps. The latter run's exact head-SHA association was not independently exposed by the connector, so it is not used as CI proof for later commits.

The remaining integration is still substantial: authoritative versioned calendar loading, calendar selection by canonical instrument/product family, adapter/API identity propagation, and exact session-bound aggregation with complete schedule coverage. No CME production bars are enabled by this change.

Indicator tracker remains unchanged: SMA/EMA/RSI/MACD/Bollinger calculations and tests exist but are not chart-integrated; Footprint remains simulated-only; Heatmap and Liquidation Maps remain unimplemented pending visual references.


### CME calendar registry and explicit product-family selection — 2026-11-07

Second integration slice completed on the active foundation branch:

- Added `calendar_id_for_product_family()`; only explicit ES/NQ/GC product-family values select a calendar. Raw contract symbols such as `ESZ6` are deliberately not parsed or guessed.
- Added `SessionCalendarRegistry` for explicit (calendar_id, version) registration and lookup.
- When multiple releases exist for one calendar, an unversioned lookup returns no result rather than guessing which release is current.
- Registry selection validates the product-family/calendar pairing; e.g. an ES calendar release cannot be silently reused for NQ or GC.
- Calendar record mappings are copied and made read-only at construction so callers cannot mutate a registered release through the original dictionary or the calendar object.
- Added tests for ES/NQ/GC selection, unknown roots, ambiguous versions, conflicting release keys, product-family mismatch, and immutable record mappings.

Files changed in this slice:
- `backend/app/session_calendar.py`
- `backend/tests/test_session_calendar.py`

This is a deterministic in-memory registry only. It does not fetch, parse, certify, or activate any official CME schedule release. The adapter is not yet wired to this registry, and CME OHLCV ingestion/aggregation remains disabled until canonical product-family metadata and verified calendar source loading are connected.

Indicator tracker unchanged: SMA/EMA/RSI/MACD/Bollinger calculations exist but are not chart-integrated; Footprint is simulated-only; Heatmap and Liquidation Maps remain pending their visual references.


### Targeted CI regression repair — 2026-11-07

The CI run for commit `5d5b049` exposed two failures in the new CME session-bar tests. Both had the same cause: `OhlcvBar.__post_init__` correctly bypassed UTC alignment inside the policy-specific branch, but a second unconditional UTC-alignment check remained later in the method.

Only that duplicate check was removed in commit `8f559e9`. The policy-specific validation remains authoritative:
- UTC policies still require UTC bucket alignment.
- CME session policy still requires an allowed session timeframe and both calendar identity fields.
- Actual CME session-bound validation remains pending the calendar-aware ingestion integration.

No unrelated test or SQLite code was changed for this repair. CI for the repair commit must complete before the change is marked verified.


### Versioned CME calendar artifact loader — 2026-11-07

Implemented the next isolated loader slice on the active branch:

- Added `backend/app/session_calendar_loader.py` with a strict canonical JSON schema (unknown/missing fields and duplicate JSON keys are rejected).
- Requires a separately supplied 64-character SHA-256 pin and verifies the exact raw UTF-8 artifact bytes before parsing.
- Requires explicit calendar ID, version, product family, effective date range, Chicago timezone, publication timestamp, source ID, and HTTPS source URL on the `cmegroup.com` domain.
- Rejects duplicate trading dates, missing effective-range dates, out-of-range records, unsupported schema versions, non-UTC publication timestamps, and malformed/ambiguous/nonexistent Chicago local times.
- Produces an immutable `SessionCalendar` carrying the computed `sha256:<digest>` value. The loader does not fetch remote files, register calendars, or enable ingestion.

Tests added in `backend/tests/test_session_calendar_loader.py` cover valid loading, digest mismatch, incomplete coverage, duplicate dates/JSON keys, inconsistent metadata, non-CME URLs, DST-invalid local times, and unknown schema fields.

Important trust boundary: a matching SHA-256 digest proves byte identity only against the independently supplied pin. It does not, by itself, authenticate the publisher or prove that a schedule is an official CME release. No official calendar artifact has been loaded; the test fixture is synthetic and must never be used as production market data.

Files changed:
- `backend/app/session_calendar_loader.py`
- `backend/tests/test_session_calendar_loader.py`

Branch comparison confirms the branch advanced exactly two commits beyond `aae7bd331a34033548be4974bfe5198f273e57dd`; latest code commit is `61815630ad4ffce04e0bba661e31ce8068bce748`. CI for these new commits has not yet been verified. The current combined commit status exposes Vercel as pending; the Actions run for this exact head is not yet available through the connected GitHub action surface.

No integration into the adapter, registry, OHLCV ingestion, or aggregation is claimed. The next slice is to harden loader edge cases, execute its dedicated and full backend tests in CI, then wire only validated instrument metadata to explicit calendar version selection. SQLite remains unchanged.

Progress accounting: the owner-confirmed historical checkpoint remains 20.9%; no new overall percentage is calculated or awarded from this code addition. The proposed weighted ledger remains unapproved and unscored.


### Loader hardening follow-up — 2026-11-07

The loader was tightened after static review:

- Rejects malformed URL ports instead of allowing URL parsing errors to escape the loader's domain exception.
- Requires an actual local datetime value (not a date-only string) for session boundaries.
- Caps a single artifact's effective date range at 10 years to bound memory/CPU use during completeness validation.
- Added regression tests for malformed ports, date-only session boundaries, and excessive effective ranges.

Latest branch comparison against the handoff checkpoint `aae7bd331a34033548be4974bfe5198f273e57dd` reports exactly six commits ahead and zero behind. Latest branch HEAD at this documentation update: `8f4fb0c8e701054ff757f089e380aee37be96dc7`. The connected status surface exposes Vercel as pending and no Actions check result for this HEAD; no successful CI claim is made. Run the full Actions workflow and inspect the backend test result before treating this loader slice as verified.

This follow-up does not change the project percentage. The loader remains a parser/validator only; no official CME calendar release is supplied, authenticated, registered, or activated.


### CI-verified calendar artifact loader and canonical instrument resolver — 2026-11-07

#### CI verification of the loader slice

GitHub Actions run [42353541813](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42353541813) completed successfully on exact HEAD `e0b8c42ae58af296a27278f8857a3ce41ae501a6`. Its single `Test and Build` job passed all reported steps: frontend dependency installation, frontend unit tests, frontend production build, backend dependency installation, backend tests, and backend container-image build. The prior run for `8f4fb0c` was cancelled; it is not the verification source for the loader.

#### Canonical instrument calendar resolution slice

The canonical instrument model already carries an explicit `session_calendar_id`. The OHLCV adapter currently resolves provider records to canonical mapping data, but does not yet apply a CME calendar. Rather than infer a calendar from raw provider symbols or add a guessed product-family mapping, the registry now exposes a narrow explicit resolver:

- `SessionCalendarRegistry.for_instrument(instrument, version=...)` accepts only a `CanonicalInstrument` future.
- It reads `session_calendar_id` from canonical instrument metadata.
- It requires a non-empty explicit release version and performs an exact (calendar ID, version) lookup.
- Missing/unsupported calendar IDs, non-futures, and unavailable versions return no calendar (fail closed).
- It does not inspect the canonical symbol, raw symbol, provider instrument ID, or publisher ID to infer the calendar.
- No adapter, ingestion, OHLCV timestamp validation, or aggregation path has been enabled by this method.

Added regression tests for successful explicit resolution, symbol-independence, missing/unsupported calendar metadata, non-futures, required version, and no version fallback.

Files changed in this resolver slice:
- `backend/app/session_calendar.py`
- `backend/tests/test_session_calendar.py`

The latest code change has triggered a new CI run; its result must be checked against the exact resulting HEAD before this resolver slice is marked verified. The earlier loader is CI-verified on `e0b8c42`; the newly added resolver is not yet CI-verified.

#### Current integration boundary

- Canonical instrument metadata can explicitly identify a session calendar.
- Versioned schedule loading and digest validation exist and passed CI on `e0b8c42`.
- The in-memory registry can resolve an exact calendar release from canonical metadata.
- No authoritative CME schedule artifact has been supplied or independently authenticated.
- No Databento adapter currently validates each bar timestamp against a resolved calendar.
- Session-aligned OHLCV aggregation remains disabled. UTC aggregation behavior remains unchanged.
- SQLite remains unchanged; its existing schema already persists the CME bucket identity fields needed for future integration.

Progress remains at the owner-confirmed historical conversational checkpoint of **20.9%** for continuity. This is not a newly recalculated weighted score. The new resolver does not receive percentage credit until its acceptance tests pass and the weighted ledger has been reconciled and approved.


### CME intraday bar/session validation boundary — 2026-11-07

Added a pure, fail-closed validation component for intraday OHLCV bars:

- `backend/app/session_bar_validation.py` validates the complete half-open bar interval `[ts_start_ns, ts_start_ns + timeframe)` against an explicitly versioned calendar release.
- Calendar selection is performed only through `SessionCalendarRegistry.for_instrument()` using the supplied `CanonicalInstrument.session_calendar_id`; it never parses canonical/raw symbols or guesses from provider identifiers.
- Only active futures and `UTC_FIXED_V1` intraday bars are accepted by this validator. Daily/session-aligned bars remain outside this contract.
- Regular and explicit special sessions (including early-close schedules) may pass. Maintenance, explicit closure, unknown calendar coverage, unavailable release versions, inactive/non-futures instruments, and intervals extending past session close are rejected with stable reason keys.
- Timestamp conversion refuses sub-microsecond precision rather than silently rounding. Current Databento OHLCV schemas in this repository are second/minute/hour granularity; no precision truncation is performed.

Added `backend/tests/test_session_bar_validation.py` with 11 deterministic tests covering regular sessions, special/early-close sessions, a bar crossing the early close, maintenance, explicit closure, missing coverage, canonical calendar identity, explicit version selection, inactive/non-futures instruments, unsupported bucket policy/timeframe, and timestamp precision.

**Important integration boundary:** the pure validator is now callable through a durable provider-identity resolver and an optional ingestion validation hook. The production application does **not** configure that hook yet because no authenticated official CME schedule release/version has been supplied. Therefore no claim is made that production Databento bars are currently session-validated.

No production CME calendar artifact has been supplied or authenticated. Test records are synthetic fixtures only. No session-aligned aggregation is enabled. Existing UTC ingestion/aggregation and SQLite schema are unchanged.

Files added:
- `backend/app/session_bar_validation.py`
- `backend/tests/test_session_bar_validation.py`

Progress remains at the owner-confirmed historical checkpoint **20.9%**; no weighted percentage increase is awarded for this isolated validation component before CI and the project milestone ledger are reconciled.




## Stage 1 audit snapshot — provisional criterion scoring (2026-11-07)
The owner requested a fresh Stage 1 calculation. Since the six-stage acceptance ledger has not yet been formally approved, this is a transparent **provisional Stage 1 index**, not a change to the overall project percentage.

Scoring method for this audit only:
- Ten Stage 1 acceptance groups are treated equally (10% of Stage 1 each).
- Complete = 1.0 credit; partial = 0.5; unverified/blocked = 0.
- Five groups are complete and five are partial: (5 × 1.0 + 5 × 0.5) / 10 = **75.00% provisional Stage 1 completion**.
- This method and criterion boundaries require owner approval before being used as the official stage score.

| Stage 1 acceptance group | Audit result | Evidence / remaining boundary |
|---|---|---|
| Frontend shell and production build | Complete | React/Vite/Lightweight Charts shell; latest observed frontend test/build steps passed |
| Backend bootstrap and health endpoint | Complete | FastAPI application and health endpoint have tests |
| API contracts and data validation | Partial | Versioned OHLCV contracts, request validation, and data guards exist; full deployed end-to-end validation remains unverified |
| Canonical instrument identity | Complete | Immutable canonical identities and point-in-time provider mappings have registry tests |
| SQLite persistence foundation | Complete | Persistence, schema migration, restart, and coverage tests exist; no SQLite rework is indicated |
| Firebase client/server authentication | Partial | Firebase client provider and Admin token verifier exist; actual deployment configuration and operational token flow are not verified |
| Account/instrument authorization | Complete | Server derives subject from verified principal and uses deny-by-default canonical-instrument entitlements; API and store tests exist |
| Secret/configuration/CORS hygiene | Partial | Backend-only provider secrets, redacted settings repr, and restricted CORS baseline exist; comprehensive security scanning/review remains open |
| Resilience and observability | Partial | Bounded ingestion, overflow gap tracking, retries, and status counters exist; production fault/monitoring verification remains open |
| CI reproducibility and deployment validation | Partial | CI #790 verified clean npm install, dependency audits, 26 frontend test files / 197 tests, production build, bundle-secret scan, 517 backend tests, container build, isolated Redis/persistent-volume smoke, and Trivy report; deployed Android/web smoke remains open |

This 75.00% Stage 1 index is not an overall-project percentage and does not imply Stage 1 is complete. Historical overall checkpoints 20.3% then 20.9% remain preserved. The overall baseline stays **20.9%** pending owner approval of a full weighted six-stage model and a reproducible cross-stage scoring ledger.


## CME provider-to-session validation integration seam — 2026-11-07

Added the next Stage 2 integration slice:

- `validate_provider_bar_session()` now resolves the provider mapping through `SQLiteInstrumentRegistry.resolve_provider_mapping()` using provider, dataset, publisher ID, instrument ID, and the bar event timestamp.
- The resulting canonical ID is used to load the canonical instrument. Calendar selection still comes only from explicit canonical `session_calendar_id` plus an explicit calendar version.
- Raw symbol is never used to select the instrument or calendar; it is checked only for consistency against the durable mapping. A mismatch is rejected.
- Missing/expired point-in-time mappings and registry lookup failures fail closed with stable rejection reasons.
- `OhlcvIngestionService` now accepts an optional `bar_validator` callback and invokes it after OHLCV parsing but before persistence, pipeline mutation, aggregation, or broadcast. Rejections are counted as `rejected_validation_<reason>`; a validation exception cannot stop the consumer.
- Added four durable-mapping/session tests and two ingestion-hook tests, including a proof that rejected bars never reach persistence/pipeline.

**Not enabled in the production app:** `main.py` intentionally does not supply a bar-validator callback yet. No authenticated official CME schedule artifact is present, and no approved calendar version is configured. The optional hook is an integration boundary, not a claim of active session validation. Existing UTC ingestion behavior is unchanged until a verified release is supplied and explicitly enabled. Session-aligned aggregation remains disabled.

CI for the latest code commit is pending. Do not mark these tests as passing until the exact-head workflow completes.



## Stage 1 security hardening — WebSocket Origin fail-closed (2026-11-07)

A focused Stage 1 security review found that the WebSocket Origin guard previously skipped enforcement when `cors_allowed_origins` was empty. That behavior treated an empty allowlist as unrestricted for browser-originated WebSocket connections.

Changed behavior:
- Any request carrying an `Origin` header is now rejected with close code `4403` unless the exact origin is explicitly present in `cors_allowed_origins`.
- An empty allowlist therefore rejects all browser-originated WebSocket connections.
- Clients without an Origin header remain supported (for example, native/non-browser clients); they must still pass the existing Firebase token verification and subscription entitlement checks.
- HTTP CORS configuration and the Firebase authentication flow were not weakened or bypassed.

Added API tests for an unlisted origin, an empty allowlist, and a non-browser client without an Origin header. CI must pass on the exact resulting HEAD before this security criterion is counted as verified. This change does not by itself complete Stage 1's full security or deployment acceptance criteria.



## Stage 1 async authentication hardening — 2026-11-07

The REST Bearer-auth dependency previously called Firebase Admin token verification directly inside an async FastAPI dependency. Firebase Admin verification includes revocation checking and may perform blocking SDK/network work, which could occupy the ASGI event-loop thread and delay unrelated requests.

Changed behavior:
- REST token verification now runs through `asyncio.to_thread`, matching the existing WebSocket verification approach.
- Existing response semantics remain unchanged: unavailable identity provider returns 503; invalid/expired token returns 401; only a verified principal is accepted.
- Added a focused API test that spies on the thread-offload boundary and verifies that the verifier is invoked through `asyncio.to_thread`.
- No token, Firebase credential, or client identity is logged or exposed.

This is a targeted resilience/performance improvement, not proof of deployed Firebase configuration or full Stage 1 completion. Count it as verified only after the exact-head backend tests and full CI pass.


## Stage 1 WebSocket authorization lifecycle hardening — 2026-11-07

The authenticated OHLCV WebSocket already rechecked instrument entitlement on a monotonic deadline, including while the stream was busy. Review found that the Firebase ID token itself was only verified during the initial handshake. A long-lived connection could therefore outlive the token's validity or remain connected after token revocation until the socket closed.

Changed behavior:
- The periodic deadline is now named `WEBSOCKET_AUTHORIZATION_RECHECK_SECONDS` because it covers both identity and instrument authorization.
- At each deadline, the server re-verifies the exact Firebase ID token originally supplied at handshake, using the verifier's revocation check.
- The refreshed verified principal must exactly match the principal established at handshake. Identity verification failure closes with `4401`; identity-provider unavailability closes with retryable `1013`.
- Only after identity revalidation succeeds does the server recheck the canonical instrument mapping, active status, and account entitlement. Missing/revoked entitlement still closes with `4403`.
- Revalidation runs on a monotonic deadline independent of market update frequency. The configured 60-second interval is the maximum intended periodic recheck cadence; this is not instantaneous revocation.

Added regression coverage for Firebase token rejection during an idle subscription, identity-provider outage during recheck, entitlement revocation during an idle subscription, and the existing continuous-update revocation case.

This hardening does not prove deployed Firebase credentials, production revocation latency, or end-to-end mobile behavior. Exact-head CI must pass before counting this acceptance criterion as verified.


## Stage 1 backend credential-representation hardening — 2026-11-07

A focused secret-handling review found that `Settings.__repr__` already hid the Databento API key and Firebase project identifier, but the backend WebSocket shared token was still a normal dataclass field and therefore appeared in the generated representation.

Changed:
- Marked `market_data_ws_token` as `repr=False`, matching the existing treatment of other backend-sensitive configuration values.
- Added `backend/tests/test_config_security.py` to assert that the WebSocket token, Databento key, and Firebase project identifier never appear in `repr(Settings)`, while non-sensitive environment metadata remains available for diagnostics.

Verification boundary:
- The change is implemented on `phase-2/market-data-foundation`.
- Exact-HEAD CI must pass before this control is counted as verified.
- This prevents accidental exposure through the dataclass representation; it does not replace deployment secret-manager controls, log review, credential rotation, or production smoke tests.

## Stage 1 dependency update monitoring — 2026-11-07

Added `.github/dependabot.yml` to request weekly dependency update pull requests for:
- npm dependencies at the repository root;
- pip dependencies under `/backend`;
- GitHub Actions dependencies under `/`.

All update pull requests target `phase-2/market-data-foundation`; Dependabot is configured with a maximum of five open update pull requests per ecosystem and a `dependencies` label.

Verification and security boundary:
- This configuration schedules dependency update pull requests; it is not a vulnerability scan and does not itself prove that Dependabot security alerts or security updates are enabled in repository settings.
- The repository still has no committed root `package-lock.json`; the current workflow still uses `npm install`, so frontend dependency resolution is not yet reproducible.
- Backend requirements still use version ranges and no backend lockfile was added.
- No dependency was upgraded, and no dependency audit or application test was run in this configuration-only slice.
- The workflow file `.github/workflows/ci.yml` remains unchanged. Exact-HEAD CI and validation of Dependabot PR creation remain pending.
- No overall or Stage 1 percentage credit is claimed for this monitoring configuration alone.


## Stage 1 CI backend dependency audit — 2026-11-07

Extended the existing GitHub Actions test/build workflow with a backend dependency vulnerability audit:
- Installs `pip-audit` in the CI runner after backend test dependencies are installed.
- Runs `pip-audit -r backend/requirements-dev.txt`, covering the backend runtime requirements included by that file and its development/test requirements.
- A reported known vulnerability or audit execution failure will fail the CI job instead of being silently ignored.

Scope and limitations:
- This checks resolved Python dependency versions against the vulnerability data available to pip-audit at run time; it does not pin dependencies or make resolution reproducible.
- Frontend dependency auditing is now wired into CI with `npm audit --audit-level=high` after `npm install`. Because no `package-lock.json` is committed, the audit checks the dependency graph resolved during that workflow run; it does not make frontend dependency resolution reproducible.
- Immutable SHA pinning for the three GitHub Actions used by this workflow is implemented and passed CI on commit `d41f8cdee9be31172ce8440b239cb53764a57251`. Secret scanning, container image scanning, and repository-level Dependabot security-alert settings remain outstanding.
- The backend `pip-audit` step passed on commit `d41f8cdee9be31172ce8440b239cb53764a57251`. The newly added frontend audit must pass on its own exact HEAD before it is considered verified. No security-clean claim is made from a dependency audit alone.
- Overall progress remains unchanged pending exact-HEAD CI evidence and acceptance-ledger review.


## Stage 1 CI supply-chain hardening — immutable GitHub Actions references (2026-11-07)

Updated the three external GitHub Actions used by `.github/workflows/ci.yml` from movable major-version tags to immutable commit references:

- `actions/checkout` → `11bd71901bbe5b1630ceea73d27597364c9af683` (tag `v4.2.2`)
- `actions/setup-node` → `49933ea5288caeca8642d1e84afbd3f7d6820020` (tag `v4.4.0`)
- `actions/setup-python` → `a26af69be951a213d495a4c3e4e4022e16d87065` (tag `v5.6.0`)

Each SHA was resolved from the corresponding action repository's Git tag reference before being written to the workflow. The version comment is for human readability; GitHub Actions executes the immutable SHA.

Verification boundary:
- This removes automatic tag movement for these three action dependencies; future action updates must deliberately verify and change the commit SHA.
- This does not pin dependencies installed by npm/pip, does not add lockfiles, and does not replace action-code review or a broader supply-chain policy.
- The updated workflow must pass on its resulting exact HEAD before this CI hardening is counted as verified. No overall or Stage 1 percentage increase is claimed from the edit alone.


## Stage 1 frontend dependency vulnerability gate (2026-11-07)

Added an `npm audit --audit-level=high` CI step immediately after frontend dependency installation. The gate fails the workflow when npm reports a high- or critical-severity advisory (or when the audit command itself fails).

Verification and limitations:
- The repository does not currently contain a committed `package-lock.json`; the GitHub API returned 404 for that path. CI's preceding `npm install` resolves dependencies in the runner, and npm audit checks that run's generated dependency graph.
- This improves vulnerability visibility but does not provide reproducible dependency resolution. A committed lockfile plus `npm ci` remains a separate requirement.
- The new audit has not yet run on the resulting commit at the time of this documentation change. Do not claim it passed until exact-HEAD CI finishes.
- No overall or Stage 1 progress increase is claimed from adding a gate alone.


## Frontend dependency audit remediation (2026-11-07)

The first exact-HEAD run of the new frontend `npm audit --audit-level=high` gate failed and reported 8 findings (1 moderate, 5 high, 2 critical). The affected dependency groups in the audit output were:

- `@grpc/grpc-js`, reached transitively through Firebase/Firestore. The Firebase Firestore dependency range held the gRPC client on a vulnerable release line. A root npm override now selects `@grpc/grpc-js ^1.14.7`, which is beyond the patched `1.14.5` release identified in the upstream advisory.
- `vite` / `esbuild`. Vite is raised from the 4.x line to `^6.4.4`, the patched Vite 6 release for the advisory reported by CI.
- `vitest` / `tinypool`. Vitest is raised from 0.34.x to `^4.1.12`, whose dependency line includes patched Tinypool 2.1.2 or later.

Compatibility intent: Vite 6.4.4 remains within the Vite 6 major line supported by the existing React plugin 4; Vitest 4.1 requires Node 20 or newer, matching the workflow's Node 20 setup. The repository's test suite and production build must still pass on the resulting exact HEAD before these upgrades are accepted.

No lockfile was hand-authored. The repository still lacks a committed `package-lock.json`, so dependency resolution is not yet reproducible. The remediation is pending exact-HEAD CI, including a clean high/critical npm audit result, frontend tests/build, backend tests/audit, and container build. No overall or Stage 1 progress increase is claimed at this point.



## Frontend dependency audit remediation — exact-HEAD CI verified (2026-11-07)

The dependency remediation documented above is now verified by GitHub Actions run #638 on exact HEAD `82e43bed39297256b5caa2e6cb3fad59350e1718`:

- Frontend install completed and npm reported **0 vulnerabilities**; the explicit `npm audit --audit-level=high` gate also reported **0 vulnerabilities**.
- Frontend tests: **22 test files passed, 158 tests passed**.
- Frontend production build completed using Vite **6.4.5** (the compatible range selected by the manifest).
- Backend tests: **437 passed, 1 warning**.
- Backend `pip-audit`: **No known vulnerabilities found**.
- Backend Docker image build completed successfully.
- Every step in the single CI job completed successfully; workflow conclusion: **success**.

This closes the exact-HEAD verification gap for the dependency remediation and confirms the Vite/Vitest/gRPC override combination passes the current CI test/build pipeline. It does **not** make dependency resolution reproducible: no committed root `package-lock.json` exists, and CI still uses `npm install` rather than `npm ci`. Python dependency resolution also remains range-based rather than lockfile-pinned.

Non-blocking build observation: Vite emitted its existing warning that the minified JavaScript chunk exceeds 500 kB (reported bundle approximately 534.15 kB, gzip approximately 151.28 kB). This did not fail the build, but should be evaluated in a separately scoped bundle/code-splitting performance task; no speculative code splitting was introduced during this security remediation.

The backend test warning was present in the successful run and has not yet been attributed to a specific warning source in this checkpoint. Do not treat the test suite as warning-free.

Evidence:
- Workflow run: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42358624621
- Exact tested commit: `82e43bed39297256b5caa2e6cb3fad59350e1718`

No overall percentage increase is claimed in this note. The project-wide acceptance ledger and stage weighting have not been formally approved, and passing CI is verification evidence rather than a standalone measure of total project completion.


## Follow-up verification and warning attribution (2026-11-07)

The documentation-only HEAD `b8bd556826df52bef4152021669d0348e42513bb` was itself verified by GitHub Actions run #639:

- Workflow conclusion: **success** on the exact HEAD.
- Frontend: npm audit found **0 vulnerabilities**; **22 test files / 158 tests passed**; Vite 6.4.5 production build passed.
- Backend: **437 tests passed**; pip-audit reported **No known vulnerabilities found**.
- Backend Docker image build passed.

The single pytest warning is now attributed from the captured test output, rather than left unexplained: `StarletteDeprecationWarning` originates from `fastapi/testclient.py` and states that using `httpx` with `starlette.testclient` is deprecated, recommending `httpx2`. This is a test-client dependency compatibility warning, not a failed assertion. It remains open for a controlled compatibility review; no dependency substitution or warning suppression was made because the current suite passes and a blind switch could change test-client behavior.

Additional workflow-level warnings observed in the same job:
- GitHub reports the pinned checkout/setup-node/setup-python actions are being forced onto Node.js 24 because Node.js 20 action runtime is deprecated.
- The pinned actions have not yet been upgraded in this checkpoint. This is a CI-maintenance item; action SHA changes must be checked against official release tags and compatibility before editing.
- The container build emits expected environment/user notices (pip running as root and UID 10001 above the distro's SYS_UID_MAX); the image build still succeeds.

Dependency reproducibility remains unresolved. Root `package-lock.json` is absent and CI runs `npm install`. Do not hand-author integrity hashes or convert to `npm ci` until a lockfile is generated by npm itself and checked against the manifest/overrides. Python requirements also remain version ranges, so `pip-audit` passing does not establish a fully locked/reproducible environment.

Evidence:
- Exact-HEAD run #639: https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42358903533
- Exact tested commit: `b8bd556826df52bef4152021669d0348e42513bb`

No overall or stage percentage increase is claimed. This checkpoint adds verification and accurately attributes an existing warning; it does not satisfy a new end-to-end acceptance criterion.


## Stage 1 CI runtime maintenance — immutable Node.js 24-compatible actions (2026-11-07)

After the previous exact-HEAD CI run completed successfully, the workflow's three pinned GitHub Actions were reviewed against their upstream release references. The old pinned releases generated GitHub's Node.js 20 action-runtime deprecation warning.

Updated `.github/workflows/ci.yml` to use immutable commit SHAs for the upstream Node.js 24-compatible releases:
- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1)
- `actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1` (v7.1.0)
- `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (v7.1.0)

The GitHub API resolved each immutable SHA from its named upstream tag, and the corresponding commit metadata reported verified signatures. The workflow's application runtime remains Node.js 20; this update concerns the JavaScript runtime used internally by the GitHub Actions themselves, not the Node version used to run the project.

Verification boundary:
- Previous workflow run #640 completed successfully on exact pre-change HEAD `b183968b0f76c0c682f4d9e0a843a665b277e5bc`, including frontend audit/tests/build, backend tests/audit, and Docker image build.
- The action upgrade is a new workflow change and is **not yet verified** until CI completes on the resulting exact HEAD.
- No application dependency, backend runtime, or application feature was changed in this slice.
- Root `package-lock.json` is still absent and frontend dependency resolution remains non-reproducible; backend requirements remain range-based.
- Vercel's separate build-rate-limit check is not the same as GitHub Actions CI and remains an external deployment limitation.

No overall or Stage 1 percentage increase is claimed from the workflow edit alone.

## Stage 1 static application security analysis — CodeQL workflow (2026-11-07)

Added `.github/workflows/codeql.yml` to run GitHub CodeQL analysis for both supported source-language groups:
- `javascript-typescript` for the React/Vite frontend.
- `python` for the FastAPI backend.

Workflow behavior:
- Runs on pushes to `main` and `phase-2/market-data-foundation`, pull requests targeting `main`, a weekly scheduled scan, and manual dispatch.
- Uses the interpreted-language `build-mode: none` for both language jobs; it does not run or execute application code as part of a build.
- Grants only the workflow permissions needed to read source/actions and upload code-scanning SARIF results (`security-events: write`).
- Pins CodeQL init/analyze to immutable commit `c793b717bc78562f491db7b0e93a3a178b099162` (release tag v4.32.5). The tag resolves to this commit; the commit metadata reports a valid verified signature. Checkout remains pinned to the previously verified immutable v7.0.1 SHA.

Verification boundary:
- The workflow file was committed to the project branch. A successful CodeQL run on this exact revision is still required before treating the scanner as operational.
- This workflow does not prove that repository-level secret scanning, push protection, Dependabot security alerts, or security configuration settings are enabled.
- CodeQL findings, if any, must be triaged; adding the workflow is not equivalent to a clean security audit.
- No application runtime behavior, market-data path, or SQLite schema was changed.
- No overall or Stage 1 percentage increase is claimed until the workflow has completed successfully and the security-analysis acceptance criterion is reviewed.


## CodeQL first successful run — exact HEAD verification (2026-11-07)

The new CodeQL workflow completed successfully on exact branch HEAD `f5a3a931e4bbaf70c53454f91811a915f13dc198`:
- Workflow run #2: `42363114204`
- JavaScript/TypeScript analysis job: success.
- Python analysis job: success.
- Both jobs completed initialization and analysis steps successfully.

This confirms the workflow is operational for both configured language groups on this revision. It does **not** establish that the repository has zero code-scanning findings; alert triage and repository security-setting verification remain separate tasks. No percentage increase is claimed from the successful workflow run alone.


## Frontend dependency lockfile and deterministic CI install — 2026-11-07

A root npm lockfile has now been generated by npm on the GitHub-hosted Node.js 20 runner (not hand-authored) and committed to the active foundation branch:
- `package-lock.json` uses lockfile format version 3 and contains 3,343 lines.
- The generated lock records registry tarball URLs and integrity hashes for resolved packages. Its root manifest records the current project dependencies and development dependencies, including Vite `^6.4.4`, Vitest `^4.1.12`, and the Firebase dependency.
- The lockfile-generation workflow completed successfully and ran `npm ls --package-lock-only --depth=0` to validate the root dependency tree before committing.

CI was then changed from `npm install` to `npm ci`, making the frontend CI install consume the committed lockfile without rewriting dependency resolution. The temporary workflow used to create the lockfile was removed after the lockfile commit landed.

Verification boundary at documentation time:
- Lockfile generation run [42363564698](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42363564698) succeeded on parent commit `e073ebac939d2a8b625dbc450b61b873971f0928` and committed the lockfile as `e872453bd7bd00a8c780e55b5243cc000f389288`.
- The CI run on the parent commit also succeeded, but it ran before `npm ci` was selected; it is not evidence that the new deterministic install has passed.
- CI run [42363908698](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42363908698) was started on the new `npm ci` workflow revision and was still in progress at this note. Its exact tested SHA is `bb1ddcac3ec694b6a54244bef4e5849b75111271`.
- CodeQL run [42363908709](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42363908709) was also in progress on that exact SHA.
- The temporary lockfile generator is no longer part of the branch. The `GITHUB_TOKEN`-pushed lockfile commit did not itself trigger CI, so a normal branch commit was used to trigger validation.

No overall or Stage 1 percentage increase is claimed by this dependency-hygiene task alone. The acceptance criterion for reproducible frontend dependency installation remains pending until `npm ci` and all downstream CI stages pass on the final branch HEAD. Python dependency ranges remain unlocked.


## Verified deterministic frontend install and security-doc reconciliation — 2026-11-07

The frontend dependency lockfile task is now verified on branch HEAD `033ec5f6865f2cae121ddab362674336d0e4649c`:
- CI run [42363936097](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42363936097) completed successfully on that exact SHA. The job completed the `npm ci` install, `npm audit --audit-level=high`, frontend unit tests, frontend build, Python dependency install, backend tests, `pip-audit`, and backend Docker image build.
- CodeQL run [42363936028](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42363936028) completed successfully on the same SHA for both JavaScript/TypeScript and Python analysis.
- Lockfile structural validation found 237 non-root package entries, each with a resolved registry location and integrity hash; root dependency declarations matched `package.json` without mismatch.

A stale security-baseline document was corrected so it no longer claims that the lockfile is absent or that dependency audits and CodeQL are missing. The documentation now distinguishes implemented CI checks from remaining repository secret scanning, container-image scanning, and runtime controls. This documentation correction does not itself increase the project progress score.

Verification scope: successful CI and CodeQL runs prove those configured jobs passed on the exact SHA above; they do not prove deployed Firebase configuration, production security, zero CodeQL alerts, or completion of all Stage 1 acceptance criteria.


## Strict environment CORS validation — 2026-11-07

A configuration-hardening slice was added on `phase-2/market-data-foundation`:
- Environment-loaded CORS values now accept only exact bare HTTP(S) origins. Wildcards, whitespace, URL paths, credentials, query strings, fragments, and malformed ports/URLs fail startup configuration parsing rather than being silently accepted.
- When `APP_ENV=production`, every configured CORS origin must use HTTPS. Exact local HTTP origins remain valid in development.
- Added focused tests for local development origin acceptance, wildcard rejection, path rejection, production HTTP rejection, and production HTTPS acceptance.

This closes a configuration-validation gap only. It does not prove the deployed allowlist is correct, does not add rate limiting, and does not replace live HTTPS/WSS, Origin, Firebase lifecycle, or abuse-control smoke tests. No overall or Stage 1 percentage is increased until CI verifies the new commit and the broader Stage 1 ledger is reconciled.


## Authenticated OHLCV request-boundary hardening — 2026-11-07

Added bounded query validation to `GET /v1/ohlcv`:
- Dataset, timeframe, raw symbol, provider, series type, bucket policy, calendar ID/version, and nanosecond query values now have explicit maximum lengths.
- Publisher and provider instrument identifiers are constrained to positive signed 32-bit values.
- Snapshot limit is constrained to 1–5,000 bars at the HTTP boundary. The effective server-side cap is also hard-limited to 5,000 even if the environment configuration is set higher; REST and WebSocket snapshots use the same effective cap.
- Added parameterized API tests for oversized strings, invalid identifier ranges, oversized nanosecond strings, and excessive response limits.

This does not implement per-account/IP rate limiting, proxy-aware abuse controls, HTTP body limits, or WebSocket frame-size configuration. CI on the resulting HEAD must pass before these changes are treated as verified acceptance evidence.


## WebSocket client-message and frame-boundary hardening — 2026-11-07

- Added a monotonic sliding-window guard for authenticated OHLCV WebSocket client pings: at most 20 pings per 10 seconds per connection; excess traffic closes with policy-violation code 1008.
- Unsupported post-subscription client messages now close with code 1008 instead of being silently ignored.
- The backend container starts Uvicorn with a 64 KiB WebSocket message-size cap and a 16-message inbound queue cap.
- Added unit tests for the ping-window limit and exact expiry boundary.

Scope limitation: these controls bound each connection's message behavior and frame/queue sizes. They do not provide a global per-IP/account connection limit or distributed HTTP rate limiting. Those require deployment-aware trusted-proxy and shared-state design; do not treat these per-connection controls as complete abuse protection. CI for the resulting HEAD is pending verification.


## WebSocket subscription identity bounds — 2026-11-07

- Audited the authenticated WebSocket subscription parser and added explicit maximum lengths before registry lookups: raw symbol 128 characters, timeframe 16 characters, canonical instrument ID 36 characters (UUID-width contract).
- Added parameterized API tests proving oversized raw-symbol, timeframe, and canonical-ID values close with protocol error 4400 before a subscription is established.
- Existing provider-mapping equality, canonical-instrument active-state, entitlement checks, Firebase revalidation, per-connection ping window, and bounded Uvicorn frame/queue settings remain in place.
- This is bounded input validation, not global HTTP rate limiting, per-IP/account connection limiting, or distributed abuse protection. Backend hosting provider/topology is not selected in the repository deployment guide, so a shared-state or edge rate limiter must not be guessed or represented as complete.
- Exact-HEAD CI and CodeQL verification are pending for the resulting commit.


## HTTP API response hardening — 2026-11-07

- Added response security headers to `/health` and `/v1/*`: content-type sniffing disabled, framing denied, restrictive referrer policy, and camera/microphone/geolocation disabled.
- Added explicit non-cache policy (`private, no-store, max-age=0`, `Pragma: no-cache`, `Expires: 0`) for API and health responses, including authentication failures and market-data responses.
- Added API tests for the full header set on health responses and no-store/security headers on unauthenticated API errors.
- These application headers do not provide TLS termination, frontend CSP, rate limiting, or deployment-edge protections. HSTS is intentionally not set here because TLS termination and trusted-proxy behavior are not yet confirmed for the backend deployment.
- CI and CodeQL verification are pending for the resulting HEAD.


## API cache-policy regression coverage — 2026-11-07

- Extended the successful authenticated OHLCV snapshot test to assert `Cache-Control: private, no-store, max-age=0`, `Pragma: no-cache`, and `X-Content-Type-Options: nosniff` on a real populated snapshot response.
- This complements the existing health-response and unauthenticated-auth-error header tests, covering both successful market-data payloads and authentication failures.
- Exact-HEAD CI/CodeQL verification is pending; no project progress percentage is changed by adding test coverage alone.


## OHLCV nanosecond timestamp range enforcement — 2026-11-07

- The authenticated REST snapshot parser now rejects `start_ns` or `end_ns` values above `9223372036854775807` (signed 64-bit maximum), before those values reach pipeline/storage query operations. This closes the gap where a 19-digit decimal value could be syntactically accepted while exceeding the signed integer range used by backend persistence.
- Added API regression coverage for overflow on both query fields and for acceptance of the exact maximum signed 64-bit value on both lower/upper query bounds.
- Updated the security configuration reference with the timestamp range contract.
- This is bounded input/data-integrity validation; it is not HTTP rate limiting or a substitute for deployment-aware abuse controls. Existing SQLite implementation was not changed.
- Prior HEAD `3709a18` had CI and CodeQL success. Exact-HEAD validation for this change is pending; no project progress percentage is changed until the new acceptance evidence is verified.

- CI on intermediate commit `9cfce47` exposed a pytest collection error: the existing oversized-query parametrization decorator was temporarily attached to the new overflow test during insertion. The decorator was restored to its original test; exact-HEAD CI is rerunning on the corrected test file.


## Verified CI and security configuration checkpoint — 2026-11-07

Working branch: `phase-2/market-data-foundation`  
Verified HEAD before this documentation checkpoint: `01301eca926124cc7091a1269fbe4ede8bb3055a`  
Main HEAD at audit: `e3841681bc69b73619058deaf939df82ae5116a1` (unchanged).

### Exact-HEAD automated evidence

- CI run [42365951828](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42365951828) completed successfully on the exact HEAD.
- Frontend: 22 test files passed; npm audit reported 0 vulnerabilities; production build passed.
- Backend: 463 tests passed, 1 Starlette deprecation warning; pip-audit reported no known vulnerabilities; Docker image build passed.
- CodeQL run [42365951887](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42365951887) completed successfully for JavaScript/TypeScript and Python, and uploaded both analyses. Workflow success is not evidence that the alert inventory is empty; alert counts were not available in this audit.

### Repository security setting boundary

- GitHub repository metadata confirms the repository is public and user-owned, created on 2026-10-30.
- GitHub documents secret scanning and push protection as enabled by default for new public repositories owned by personal accounts. Administrators can disable them; this audit could not read the current repository-level setting or alert inventory. Do not mark the control fully verified until the Settings > Code security and analysis page and Security alert views have been inspected.
- Container image vulnerability scanning is not currently part of CI. The image is built successfully, but its OS/package vulnerability inventory is not yet scanned. Do not treat the successful Docker build as a security scan.
- No new scan action was added in this checkpoint: the available candidate scanner/action's supply-chain posture requires a separate review before adding a third-party CI dependency.

### Remaining Stage 1 security work

- Verify repository secret scanning and push-protection settings plus alert inventory.
- Add a reviewed, pinned container-image scanner and define severity/fixability policy.
- Reconcile backend dependency ranges and a reproducible lock strategy.
- Complete deployment-specific Firebase, HTTPS/WSS, Origin, rate-limit, and monitoring checks.

This verification does not change the owner-confirmed overall progress percentage. Passing CI validates only the configured checks on this commit.


## Configured provider dataset status consistency — 2026-11-07

- Corrected `GET /v1/market-data/status` to report the configured `databento_dataset` instead of a hard-coded `GLBX.MDP3` label. This keeps the unauthenticated status metadata aligned with the provider configuration actually used by ingestion and historical-source adapters.
- Added an API regression test that configures a non-default dataset (`GLBX.TEST`) and asserts that the status endpoint reports that exact value.
- This does not enable provider connectivity, certify a dataset entitlement, or change the current historical/educational-only development boundary.
- Exact-HEAD CI and CodeQL validation are required before treating this fix as verified. No progress percentage is changed by the code edit alone.


## Container image vulnerability scanning added to CI — 2026-11-07

- Added a Trivy image scan immediately after the backend Docker build. It scans both OS packages and application libraries in the locally built `dezzta-chart-backend:ci` image.
- The scan reports HIGH and CRITICAL vulnerabilities and fails the CI job when any matching finding is present; unfixed findings are not silently ignored.
- The third-party action is pinned to immutable commit `ed142fd0673e97e23eac54620cfb913e5ce36c25` (release v0.36.0). GitHub's tag object for v0.36.0 reported a valid verified signature. Its nested setup-trivy and actions/cache dependencies are also pinned to immutable SHAs in the inspected action metadata.
- Trivy scanner version is explicitly pinned to v0.76.2 rather than relying on the action's older default.
- This adds a repeatable container vulnerability check to CI. It does not prove the current image is vulnerability-free until the new exact-HEAD CI run completes, and it does not replace runtime/deployment scanning or a vulnerability remediation process.
- No progress percentage is increased before the scanner has run successfully and any findings have been triaged.



## Correction — preserve strict container vulnerability gate — 2026-11-07

A follow-up CI policy experiment on commit `1e09c5d` changed the image scan to block only findings with a reported fix. That relaxation was not sufficiently justified by exploitability, runtime exposure, or compensating-control analysis and therefore did not meet this project's fail-closed security standard.

The experiment was reverted on commit `1034d9f`:
- The original Trivy policy is restored: scan OS and application libraries at HIGH/CRITICAL severity, include unfixed findings, and fail CI on any matching finding.
- The full pre-existing progress history was restored after the experiment accidentally replaced rather than appended to this document.
- The 49 HIGH / 0 CRITICAL finding inventory from run `42367103349` remains an unresolved image-security issue. No claim is made that these findings are harmless or fixed.
- Next remediation work must inspect the exact base-image digest, package origins, fixed-version metadata, Debian security update availability, and whether a supported newer base image removes the findings. Any exception requires explicit risk acceptance; the CI gate must not be weakened merely to obtain a green run.

This correction is an incident record, not a progress increase. The strict scan will continue to block CI until findings are remediated or a separately reviewed, evidence-backed policy is approved.


## Container vulnerability diagnostic artifacts and base-image comparison — 2026-11-07

- Preserved the required Trivy gate unchanged: the production candidate image is still scanned for OS and library HIGH/CRITICAL findings, including unfixed findings, and any match still fails the CI job.
- Added an always-run JSON export of the current image scan so the full package/CVE/fixed-version metadata remains available even when the strict table scan fails.
- Added a feature-branch-only diagnostic build using the same backend Dockerfile and build context, changing only the Python base tag from `python:3.12-slim` to `python:3.12-slim-bookworm`. This candidate is diagnostic only and is not selected for deployment or production.
- Added a JSON scan for that candidate and a Markdown comparison summary. Diagnostic build/scan steps are explicitly non-gating; they cannot turn a failed strict scan green.
- Uploaded the reports as a 14-day GitHub Actions artifact using the immutable `actions/upload-artifact` v4 commit SHA `ea165f8d65b6e75b540449e92b4886f43607fa02`. Trivy remains pinned to the already reviewed action SHA and scanner version.
- The comparison counts unique vulnerability/package/installed-version tuples and separates HIGH from CRITICAL. A missing report is explicitly represented as unavailable rather than as zero findings.
- This is an observability and evidence-gathering improvement, not a vulnerability fix. The Bookworm image must still be built, scanned, checked for package compatibility, and reviewed before any base-image change. The strict current-image scan remains the required CI gate.
- Exact-HEAD CI and artifact contents are pending. No progress percentage is changed by adding diagnostics alone.


## Container scan findings and missing-report summary correction — 2026-11-07

- Inspected the completed CI run `42368580190` and downloaded its `container-vulnerability-reports` artifact (artifact ID `13572766556`). Frontend unit tests/build, backend tests, dependency audits, and Docker build passed; the strict Trivy image gate failed as configured.
- Exact Trivy report inventory for the current Debian 13.7 (Trixie) image: 49 HIGH package/version finding tuples, 13 distinct CVE IDs, 19 affected package names, and zero CRITICAL findings. The 49 count is not 49 distinct CVEs.
- Diagnostic Debian 12.15 (Bookworm) candidate: 40 HIGH plus 2 CRITICAL tuples (42 total), 17 distinct CVE IDs, and 19 affected package names. The two CRITICAL findings include `CVE-2025-7458` in `libsqlite3-0` and `CVE-2023-45853` in `zlib1g`. Bookworm is rejected as a safer replacement candidate; no production base-image change was made.
- Debian Security Tracker evidence confirms examples of unresolved stable-suite findings: Trixie `util-linux` `2.41.5-0+deb13u1` is listed vulnerable for CVE-2026-76642, while the fixed version is in newer testing/unstable; Trixie `acl` `2.3.2-2` is listed vulnerable for CVE-2026-54369; and Trixie `ncurses` `6.5+20250216-2` is listed vulnerable for CVE-2025-69720. See https://security-tracker.debian.org/tracker/CVE-2026-76642, https://security-tracker.debian.org/tracker/CVE-2026-54369, and https://security-tracker.debian.org/tracker/CVE-2025-69720. These records do not justify importing packages from unstable into the stable runtime.
- Fixed a real diagnostic-summary bug: when a JSON report was missing, the workflow previously converted it to an empty findings dictionary and displayed zero, which could falsely imply a clean scan. The summary now preserves missing as `NOT AVAILABLE`, while a present report with an empty `Results` list correctly reports zero. Inline assertions cover both cases.
- The strict Trivy gate is unchanged: HIGH/CRITICAL findings, including unfixed findings, still fail CI. No ignore rule, severity downgrade, or vulnerability suppression was introduced.
- This is a CI reporting correctness fix and security investigation evidence, not a remediation of the 49 Trixie findings. Overall progress remains unchanged until a new acceptance criterion is actually satisfied.


## Trixie security-update candidate diagnostic — 2026-11-07

The exact-HEAD Trivy artifact from run [42369053094](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42369053094) confirms:
- Current `python:3.12-slim` candidate: 49 HIGH, 0 CRITICAL unique vulnerability/package/version tuples.
- Bookworm comparison: 40 HIGH, 2 CRITICAL (42 total); it remains rejected as a replacement candidate.
- The strict Trivy gate failed as intended; frontend tests/build, backend tests, dependency audits, Docker build, and CodeQL passed on the same commit.

A further **diagnostic-only** candidate has been added to CI: retain the current Trixie base, apply Debian repository updates with `apt-get update && apt-get upgrade`, then build, runtime-smoke-test `/health`, and scan it with Trivy. The comparison report now includes this third candidate. This experiment does not alter `backend/Dockerfile`, does not change the strict required scan, and does not make any production base-image decision. It must pass the runtime smoke test and demonstrate a materially improved scan before it can be considered for a separately reviewed remediation.

The diagnostic workflow addition is not a completed security remediation or a Stage 1 acceptance. The exact final-HEAD CI result and artifact are pending. Overall progress remains unchanged.


## Alpine container base diagnostic — 2026-11-07

- The exact-HEAD diagnostic artifact from run [42369443589](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42369443589) shows that a Trixie image rebuilt with `apt-get update && apt-get upgrade` retains the same **49 HIGH / 0 CRITICAL** unique vulnerability/package/version tuples as the current image. The update-only candidate is therefore not a remediation and must not be promoted.
- The Debian Bookworm comparison remains worse at **40 HIGH / 2 CRITICAL** and is rejected.
- The current run's Trixie+upgrade candidate passed its `/health` runtime smoke test, but its vulnerability count did not improve. The strict current-image Trivy gate still fails as designed.
- Added a feature-branch-only diagnostic for `python:3.12-alpine`: build the same backend Dockerfile against Alpine, run an isolated `/health` smoke test, and export a Trivy JSON report for comparison. The candidate is diagnostic only; no production Dockerfile or base-image change is made. Build/runtime incompatibility or a missing report must remain visible as unavailable, not be treated as zero findings.
- This diagnostic experiment is not a security fix or Stage 1 acceptance. A production base-image change requires successful full dependency installation, backend test coverage, runtime smoke testing, vulnerability review, and a separate explicit decision.
- Overall progress remains unchanged; no Stage 1 acceptance criterion is awarded by adding a comparison job.



## Alpine diagnostic matcher correction — 2026-11-07

- Audited completed CI run [42369911702](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42369911702) on HEAD `7078a0ab4d0f44da80917da9ab34833f2ea9d5b5`. Frontend dependency audit, frontend tests/build, backend tests, backend dependency audit, Docker build, CodeQL, and all Debian diagnostic build/smoke/report steps completed successfully. The required strict Trivy scan failed with 49 HIGH / 0 CRITICAL findings, as intended.
- The exact-HEAD comparison summary showed current Trixie: 49 HIGH / 0 CRITICAL; Trixie plus `apt-get upgrade`: 49 HIGH / 0 CRITICAL; Bookworm: 40 HIGH / 2 CRITICAL. Neither Debian comparison is accepted as a production remediation.
- The Alpine report was unavailable. Source inspection found its AWK base-image matcher used a double-escaped dot (`\\\\.`) while the working Debian matchers use a single escaped dot (`\\.`). In an AWK ERE this does not match the literal dot in `3.12`, so the replacement guard can fail before the Alpine build.
- Corrected only the Alpine diagnostic matcher in `.github/workflows/ci.yml` to use the same single-escaped version pattern. This is a CI diagnostic correction, not a vulnerability remediation and not a production base-image change.
- The strict Trivy gate, severity thresholds, unfixed-finding policy, and production `backend/Dockerfile` remain unchanged. The corrected Alpine candidate must still build, pass its runtime smoke test, and produce a valid scan report before its findings can be compared.
- Follow-up CI triggered by this correction is pending at the time of this record. No overall progress or Stage 1 credit is awarded for this workflow-only fix.


### Strict container Trivy investigation — 2026-11-07

Latest audited branch HEAD before this investigation: `76e2e06f9afedfaeb5728caa0ac405c9e6dd5833`. Automated Tests run [42371490050](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42371490050) completed with failure at the required strict backend-image Trivy scan; CodeQL run [42371490129](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42371490129) passed. Frontend dependency audit, frontend tests/build, backend tests, backend dependency audit, and container build all passed.

The uploaded scan artifact was inspected (artifact `13573724056`):
- Current `python:3.12-slim` / Debian 13.7 image: **49 HIGH, 0 CRITICAL**, representing 13 distinct CVE IDs across OS packages. The report lists no fixed version for these findings; the dominant packages are util-linux family, acl, ncurses, SQLite, systemd, perl-base, and zlib.
- Debian Bookworm comparison: **40 HIGH, 2 CRITICAL**; therefore it is not an acceptable replacement.
- Trixie plus `apt-get upgrade`: **49 HIGH, 0 CRITICAL`; package versions/findings remained effectively unchanged.
- Alpine comparison did not produce a report because its diagnostic build failed: the Debian-specific `useradd` command is unavailable in Alpine (exit 127). The prior “Alpine not available” row was not a clean scan and must not be interpreted as zero findings.

No severity threshold was weakened, no Trivy ignore was added, and the production base image was not changed. This checkpoint updates only the Alpine *diagnostic candidate* to use Alpine's `addgroup`/`adduser` equivalents, preserving UID/GID 10001 and ownership, so CI can build, runtime-smoke-test, and scan that candidate. The result must be reviewed before any production base-image migration. If Alpine has no usable compatible build or still reports HIGH/CRITICAL findings, investigate a smaller hardened Debian-derived runtime image or other evidence-backed mitigation; do not hide findings.

Strict Trivy remains an active release blocker until the required scan passes without suppressing HIGH/CRITICAL findings. No overall progress credit is claimed for diagnostics or documentation.


## Strict Trivy remediation checkpoint (2026-11-07)

- Audited branch HEAD: `ae0d5f7db9bfd8b3dacba6abfce9724c17d43b11` on `phase-2/market-data-foundation`; `main` was not changed.
- Latest Automated Tests run `42372282172` completed with failure at the required production-image Strict Trivy scan. Frontend tests/build, backend tests, backend dependency audit, and production Docker build passed; CodeQL run `42372282139` passed.
- Downloaded and inspected the run's `container-vulnerability-reports` artifact. The current Debian-based production candidate had 49 HIGH and 0 CRITICAL findings. Debian Bookworm comparison had 40 HIGH and 2 CRITICAL; Trixie with apt upgrade still had 49 HIGH.
- The Alpine comparison image (Alpine 3.24.4) had 0 HIGH/CRITICAL findings across Trivy OS and Python library package results, and its runtime `/health` smoke test passed. This is a candidate backed by the exact CI artifact, not yet a production remediation claim.
- Applying the tested Alpine base and matching non-root user setup to the production Dockerfile. Removing obsolete Debian/Alpine comparison-image CI scaffolding so the required production scan remains the single authoritative gate; retaining the current-image JSON artifact.
- **Strict production Trivy status remains pending** until a new CI run builds the actual production Dockerfile, passes runtime checks, and passes the unchanged HIGH/CRITICAL scan with `ignore-unfixed: false` and `exit-code: 1`.
- No progress percentage is increased by this diagnostic or configuration change. Stage 1 remains provisional at 75%; overall checkpoint remains 20.90% pending verified acceptance-criteria reconciliation.


## Strict production Trivy remediation — verified (2026-11-07)

- Production remediation commit: `040cd7f6f905519255c8bfa7fc6f5fe85e2e2b14` (`security: switch backend image to verified Alpine base`).
- Exact-HEAD Automated Tests run [#42373092999](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42373092999) completed with **success**. Its required `Scan backend container image` step completed with **success**; the JSON export and artifact upload also succeeded.
- Exact-HEAD CodeQL run [#42373092954](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42373092954) completed with **success**.
- Downloaded and inspected artifact `container-vulnerability-reports` (artifact ID `13574522197`, SHA-256 `e876ff509d0ea312158bbcca44eb7702e67f183c469067f2eafd14a493d0bdfc`). Its Trivy JSON identifies Alpine `3.24.4`, image digest `sha256:2e6ffaf4681fc3e99deed9f2bc9efb4f08ef35e82cc1ac0c34fd0949460fbcc5`, and two result classes: Alpine OS packages and Python packages. Both report zero vulnerabilities; total HIGH/CRITICAL findings in the exported report: **0**.
- The required scan configuration remains unchanged: Trivy `v0.76.2`, vulnerability types `os,library`, severity `HIGH,CRITICAL`, `ignore-unfixed: false`, and `exit-code: 1`. No severity threshold was weakened and no findings were ignored.
- The production Dockerfile now uses `python:3.12-alpine3.24`; the image runs as UID/GID `10001:10001` and retains the `/health` Docker healthcheck. Frontend tests/build, backend tests, frontend/backend dependency audits, Docker build, strict Trivy scan, and CodeQL all passed on the remediation commit.
- **Disposition:** the Strict Trivy HIGH/CRITICAL vulnerability blocker is resolved for this exact image digest and CI run. This does not imply zero security risk, a complete security audit, or production release readiness. Future base-image/dependency changes must continue to pass the same strict gate.
- The next calendar task is an integration audit, not a new loader implementation: `backend/app/session_calendar_loader.py` and `backend/tests/test_session_calendar_loader.py` already exist. The loader validates schema, trusted SHA-256 pin, CME-domain HTTPS provenance, timezone, explicit effective-date coverage, duplicate/missing records, and ambiguous/nonexistent Chicago local times. Next inspect whether validated releases are connected to canonical instrument metadata and per-bar timestamp validation; do not duplicate the loader or claim any constructed fixture is an official CME schedule.
- No overall percentage or Stage 1 completion credit is assigned solely for clearing this CI blocker. The owner-confirmed overall checkpoint remains 20.90%; Stage 1 remains provisional at 75% pending a complete acceptance-criteria review.


## Calendar ingestion integration audit — 2026-11-07

### Verified current implementation
- `backend/app/session_calendar_loader.py` parses pinned versioned calendar artifacts and rejects digest mismatch, malformed/duplicate JSON keys, unknown schema fields, invalid CME provenance URL, timezone mismatch, incomplete effective-date coverage, duplicate dates, and ambiguous/nonexistent Chicago local timestamps.
- `SessionCalendarRegistry.for_instrument()` selects only the explicit `session_calendar_id` from `CanonicalInstrument` and requires an explicit release version.
- `backend/app/session_bar_validation.py` provides intraday session validation and a provider-bar entry point that resolves the point-in-time durable provider mapping before canonical instrument lookup. It checks raw symbol only after provider-ID mapping as a consistency assertion.
- `OhlcvIngestionService` already supports an optional `bar_validator` callback and calls it before persistence and in-memory pipeline mutation. Its rejection counters are observable.
- `Aggregator` deliberately skips deriving CME-session bars into higher timeframes until exact session bucket bounds are supplied. Existing tests cover this fail-closed behavior.
- Existing tests in `backend/tests/test_session_bar_validation.py` cover regular session, early close, maintenance, explicit closed date, missing coverage, metadata mismatch, required version, inactive/non-futures, unsupported policy/timeframe, sub-microsecond precision, point-in-time mapping, and symbol mismatch.

### Integration gap confirmed
- `backend/app/main.py` constructs `OhlcvIngestionService` with persistence and stream callback but does not pass `bar_validator`.
- `backend/app/config.py` currently has no trusted calendar artifact path, pinned SHA-256, calendar release version, or calendar-registry configuration.
- Therefore the validator exists and its isolated tests pass, but the application composition root does not yet activate it. Do not claim live application ingestion is session-validated.
- Do not wire a made-up calendar fixture or untrusted environment-only digest as an official schedule. A trusted release-manifest/pin and a verified calendar artifact are prerequisites for production activation. Until then, the integration must remain explicitly unavailable/fail-closed for any path that claims CME session validation.
- No session-aligned daily/weekly/monthly/quarterly aggregation was enabled. The current aggregator's CME skip is correct and must remain until the calendar resolver is integrated with exact session bucket bounds.

### Next implementation unit
Design the application-level calendar release source contract (trusted manifest/pin, immutable artifact bytes, explicit version) and dependency injection into `create_app()`; then wire `validate_provider_bar_session` into ingestion only when a complete trusted release is loaded. Add composition-root tests proving: no release means no CME session validation is claimed; a valid pinned release validates before persistence/pipeline mutation; mapping/calendar errors reject without mutating state. Keep synthetic test calendars labeled test fixtures only.

### Verification
- Latest exact-HEAD CI before this audit: Automated Tests [#42373445229](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42373445229) SUCCESS; CodeQL [#42373445285](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42373445285) SUCCESS.
- This audit changes no runtime behavior and earns no progress credit by itself.

## 2026-11-07 — Session calendar runtime ingestion integration

- Added explicit backend settings for a calendar artifact path, trusted SHA-256 pin, and exact release version. No calendar URL fetching or default/fabricated schedule is introduced.
- Added runtime loading that verifies the configured artifact through the existing strict loader, enforces a 16 MiB artifact size limit, and exposes only a sanitized availability state. Missing, partial, mismatched, or invalid configuration leaves an empty registry.
- Wired a provider-bar validator into the application composition root and exposed the ingestion service/runtime calendar state for operational inspection.
- The validator resolves provider identity through the durable point-in-time mapping first; it does not infer a canonical instrument from raw symbols. Active non-futures retain their non-CME path. Futures require an explicit loaded calendar version and session validation before persistence or pipeline mutation.
- Added composition/runtime tests for unconfigured fail-closed behavior, digest mismatch, release-version mismatch, successful pinned-fixture acceptance, and rejection before both persistence and pipeline writes.
- Test fixture source metadata is deliberately labelled test-only; it is not an official CME release and must not be configured in deployment.
- CME session-aligned higher-timeframe aggregation remains disabled pending an independently trusted, complete release with exact bucket-boundary semantics.
- This checkpoint records implementation scope only; progress credit remains pending until CI passes and the acceptance criteria are reviewed.


## 2026-11-07 — Calendar integration CI regression triage

- Automated Tests run [#42374317485](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42374317485) failed on commit `a9c8d035827af6b7b81d02fa58d7d49ecde86d05`: 458 passed, 11 failed. Frontend tests/build and CodeQL passed; backend dependency audit, container build, and Trivy were skipped because pytest failed.
- Root cause identified: existing API test helpers register ESZ6 as a futures canonical instrument but do not configure a matching pinned calendar release. The new application-level validator correctly fails closed, so those tests no longer ingest their fixture bars. Test harness now uses a clearly labelled, pinned test-only calendar artifact; it must never be deployed as an official CME schedule.
- A separate new runtime test incorrectly expected exactly one persisted row although the existing aggregator also writes derived intraday rows. Its assertion now verifies that the provider-sourced 1m bar was persisted; it does not enable CME session-aligned daily/weekly/monthly aggregation.
- No production calendar, synthetic market prices, or session schedule is added to runtime configuration. Progress remains unchanged pending a green exact-HEAD CI run.


## Stage 1 — Redis shared guard and container runtime verification (2026-11-08)

### Branch and CI checkpoint before this work
- Active branch: `phase-2/market-data-foundation`; HEAD before this unit: `c103cf98e4c8e1328415687f81e2dacadbe1a643`. Branch `main` was read for comparison only and was not modified.
- Automated Tests [#42377723802](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42377723802) and CodeQL [#42377723806](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42377723806) completed successfully on exact HEAD `c103cf9`.
- The backend test log reports 489 passed and one Starlette/httpx deprecation warning. Dependency audit, Docker build, and strict Trivy scan completed successfully; the exported image report showed zero HIGH/CRITICAL findings for that exact image digest. This is scoped scan evidence, not a claim of zero overall security risk.

### Verified Redis shared-guard implementation
- Added `backend/app/shared_guard.py` with atomic Redis Lua fixed-window HTTP limits and leased WebSocket connection caps shared across backend instances.
- Production configuration requires `REDIS_URL` with `rediss://`; the application pings Redis during lifespan startup and refuses to serve when the shared store is unavailable. HTTP Redis failures fail closed with 503; rejected limits return 429; WebSocket guard failures/capacity rejection close the connection.
- Redis key hash tags keep each multi-key Lua operation within a single Redis Cluster hash slot. Account subjects are SHA-256 digested before use in keys.
- Added Redis 7 as a CI service and real Lua integration tests. Exact-HEAD CI above exercised the scripts against Redis, rather than relying only on mocks.

### Runtime smoke-test gap and remediation
- The previous workflow built and scanned the backend image but did not start the image. The old local production smoke-test command in `docs/BACKEND_DEPLOYMENT.md` also omitted the now-mandatory Redis secret and would therefore fail startup.
- This change adds a container runtime smoke step using the CI Redis service, checks `/health`, then sends two requests through the Redis-protected `/v1/market-data/status` path with a one-request client limit and verifies 200 followed by 429. The test uses an unencrypted loopback Redis URL only inside the isolated CI network; production still requires managed Redis TLS.
- Updated deployment guidance to require a backend-only managed Redis secret, verify the `rediss://` scheme, and explain fail-closed startup. No provider credentials or real Redis credentials are added to source.

### Remaining boundaries
- No managed Redis provider or backend hosting platform has been selected or provisioned. Production DNS, TLS certificate validation, private networking, persistence/failover, and deployed smoke tests remain unverified.
- Proxy-aware client identity remains intentionally disabled; arbitrary `X-Forwarded-For` values are not trusted. Before public deployment, confirm the backend proxy topology and configure a narrowly trusted proxy policy if needed.
- Initial rate/connection defaults are not load-tested capacity guarantees. Redis Cluster client routing has not been verified; the key scheme is slot-compatible but the configured client is the standard Redis async client.
- Historical overall checkpoint remains **20.90%**; Stage 1 remains **75% provisional**. This CI/deployment-preparation work does not independently change the owner-confirmed overall percentage or establish Stage 1 completion.

### Files changed in this unit
- `.github/workflows/ci.yml`: start the built image and verify health plus real Redis-backed HTTP rate limiting.
- `docs/BACKEND_DEPLOYMENT.md`: correct production Redis requirements and remove the broken no-Redis production smoke command.
- `docs/PROJECT_PROGRESS.md`: record exact prior evidence, this validation scope, and remaining production boundaries.

### Exact-HEAD verification completed (2026-11-08)
- Automated Tests [#42432195466](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42432195466) completed with conclusion **success** on exact HEAD `a603d1f91e52a46b2eb23f8cc68eb7676b8097ca`.
- Frontend: 22 test files and 158 tests passed; production build succeeded; frontend bundle secret scan checked 3 files and passed.
- Backend: 489 tests passed, with one Starlette/httpx deprecation warning. Backend dependency audit and Docker image build passed.
- The new container smoke test passed: backend container became healthy, first Redis-protected status request returned HTTP 200, and the next request returned HTTP 429 under the one-request test limit.
- Strict Trivy image scan completed successfully; its report showed 0 HIGH/CRITICAL vulnerabilities for the scanned Alpine OS and Python package targets. This is scoped to this image and severity filter, not a claim of zero security risk.
- Vulnerability report artifact [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42432195466/artifacts/13598435728) was uploaded successfully.
- CodeQL [#42432195494](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42432195494) completed successfully for both JavaScript/TypeScript and Python analysis jobs on the same exact HEAD.
- The CI smoke test validates container startup and shared Redis HTTP limiting in isolated CI only; it does not validate a managed production Redis endpoint, production proxy topology, persistent host volume, Firebase production identity, or deployed backend connectivity.
- The earlier “verification pending” note is superseded by this result. Overall progress remains **20.90%** and Stage 1 remains **75% provisional** because no new owner-approved acceptance-weight change or production deployment acceptance criterion was completed.


## 2026-11-08 — Stage 1 security configuration audit (five-work-package cycle)

### Baseline and branch safety
- Pre-change branch HEAD: `a4e391986ce28548546b386d35803d1396c9b04f` on `phase-2/market-data-foundation`.
- `main` was inspected and remained at `e3841681bc69b73619058deaf939df82ae5116a1`; no work was performed on `main`.
- Latest pre-change CodeQL run [#42433757134](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42433757134) completed successfully on the exact pre-change HEAD.
- Latest pre-change Automated Tests run [#42433757042](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42433757042) had frontend install/audit/tests/build/bundle-secret-scan and backend dependency installation/tests/dependency audit completed successfully; the Docker image build was still running at audit time. No final conclusion was available for that run.

### Five work packages handled
1. **Identity-path audit:** confirmed the backend verifies Firebase ID tokens with revocation checking and validates issuer, audience, subject, and authentication time. Real production Admin credentials and signed-token E2E behavior remain unverified.
2. **Production configuration audit:** found that production required TLS Redis but did not require `FIREBASE_PROJECT_ID`; the app could therefore start while authenticated routes had no project configured.
3. **Fail-fast configuration fix:** production settings now reject an empty Firebase project identifier. This is configuration validation only; it does not claim that Admin credentials are available.
4. **Deployment contract alignment:** documented `FIREBASE_PROJECT_ID` in the backend example environment and Fly template. The Fly template retains the selected `sin` region and a deliberate placeholder that must be replaced before deployment.
5. **Security/progress evidence:** updated deployment and security documentation, added a focused regression test for the missing-project rejection, and preserved all external production checks as open gates.

### Remaining Stage 1 / release gates
- Production Firebase Admin application credentials must be configured server-side and tested with valid, expired, revoked, and wrong-project tokens.
- Fly app name, actual Fly CLI validation, Machine/Volume provisioning, mounted-volume UID/GID permissions, SQLite restart persistence, and an application-consistent backup/restore drill remain unverified.
- Managed Redis TLS connectivity, Fly ingress client-IP trust policy, production CORS/HTTPS smoke tests, and deployment monitoring remain unverified.
- Public exposure of `/health`, `/v1/market-data/status`, and `/v1/instruments` still requires explicit owner approval.
- No resource was provisioned and no paid service was created.

### Progress accounting
- Historical owner-confirmed overall checkpoint remains **20.90%**; Stage 1 remains **75% provisional**.
- This work closes a code-level configuration gap but does not complete the external identity/deployment acceptance criteria. No progress increase is claimed pending exact-HEAD CI and criterion-level reconciliation.
- Indicator implementation state is unchanged: SMA/EMA/RSI/MACD/Bollinger calculation foundations and tests exist without visible chart integration; Footprint remains deterministic offline simulation; Heatmap and Liquidation Maps remain unverified and await owner visual references.


### CI regression follow-up — production configuration test isolation
- Exact-HEAD Automated Tests run [#42434126660](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42434126660) failed with **1 failed, 489 passed**; CodeQL [#42434126648](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42434126648) succeeded.
- Root cause: the existing TLS Redis negative test omitted the newly mandatory Firebase project identifier. It therefore failed earlier at the Firebase guard and never reached the Redis TLS assertion.
- Corrective change: the TLS-specific test now supplies a valid non-secret Firebase project ID, isolating the intended insecure-Redis condition. The dedicated missing-Firebase test continues to verify the new production requirement.
- No production validation was weakened; only the test fixture was corrected. Exact-HEAD CI must rerun before this correction is accepted.

## 2026-11-08 — Firebase Admin adapter verification tests

### Five-work-package cycle
1. Revalidated the active branch and exact HEAD before editing; the working branch was `phase-2/market-data-foundation` at `dc75cebe736d80ccb4a8ef2262b1ef4c43ca9093`. The `main` ref remained unchanged at `e3841681bc69b73619058deaf939df82ae5116a1`.
2. Confirmed both workflows on the exact baseline HEAD had completed successfully: Automated Tests [#42434289775](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42434289775) and CodeQL [#42434289748](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42434289748).
3. Audited `FirebaseIdentityVerifier` and found its Admin SDK adapter boundary had no direct tests for named-app reuse, initialization arguments, initialization failure normalization, or missing SDK behavior. Existing tests primarily exercised the injected verification callable.
4. Added focused tests with a fake Firebase Admin module to verify: the named project app is reused; a missing app is initialized with the configured project ID; every Admin verification call receives `check_revoked=True`; initialization exceptions are sanitized; and missing Admin SDK imports fail closed.
5. Recorded the new test scope and its production boundary here. These are deterministic adapter tests, **not** real signed-token tests and do not establish that production credentials, token expiry, revocation, or wrong-project behavior have been verified against Firebase.

### Files changed
- `backend/tests/test_identity.py`: Admin SDK adapter lifecycle and fail-closed regression tests.
- `docs/PROJECT_PROGRESS.md`: exact baseline, test scope, and remaining production validation boundary.

### Verification boundary and next actions
- The new tests have not yet run locally or in CI at the time of this record; accept them only after the exact-HEAD Automated Tests and CodeQL workflows complete successfully.
- Next, review whether the existing backend identity tests cover token claim mismatches, token expiry/revocation normalization, and route-level rejection consistently. Then strengthen frontend auth lifecycle tests without introducing a new test framework solely for superficial coverage.
- Production Firebase Admin credentials and real signed-token lifecycle remain an external deployment gate. No credentials or paid resources were created.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional**.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`
- Adding tests and documentation alone does not earn progress credit; the tests must pass and the milestone ledger must be reconciled before any percentage change.


## 2026-11-08 — Firebase Admin adapter tests: exact-HEAD CI reconciliation

- This entry supersedes the preceding note that said the new Admin SDK adapter tests were still awaiting CI. The branch remained `phase-2/market-data-foundation` at exact HEAD `6c8403464f5944b7b36b48cd33754fbb32166fbf` during this audit; the `main` ref remained `e3841681bc69b73619058deaf939df82ae5116a1` and was not modified.
- Automated Tests [#42434723776](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42434723776) completed successfully on that exact branch and SHA. The workflow log reports **22 frontend test files / 158 frontend tests passed**, **494 backend tests passed**, frontend production build passed, frontend bundle secret scan passed, backend dependency audit passed, Docker image build passed, and the Redis-backed container health/rate-limit smoke test passed. Pytest emitted one Starlette/httpx deprecation warning. The Trivy image scan and report-upload steps completed successfully; no broad claim of zero vulnerabilities or zero security risk is made here.
- CodeQL [#42434723800](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42434723800) completed successfully for both Python and JavaScript/TypeScript analysis jobs on the same exact SHA.
- The Firebase Admin adapter tests are therefore CI-verified. They validate named-app reuse, configured-project initialization, revocation-check argument enforcement, sanitized initialization failure, and missing-SDK fail-closed behavior. They are still mocked adapter tests, not real Firebase-signed-token production E2E tests.

### Frontend authentication lifecycle audit — five focused work packages
1. **Repository/CI integrity:** confirmed the active branch HEAD and exact-HEAD Automated Tests + CodeQL success; confirmed `main` was unchanged.
2. **Test harness:** inspected `package.json`, `package-lock.json`, and `vite.config.ts`. Vitest is configured through the `test` script, but no DOM renderer/test environment or React Testing Library package is installed in the lockfile.
3. **Existing frontend test quality:** current component tests use `renderToStaticMarkup`; this verifies static markup only and does not execute effects, event handlers, or Firebase observer callbacks.
4. **Auth implementation:** reviewed `AuthProvider.tsx`, `services/firebase.ts`, and `AuthPanel.tsx`. Firebase sign-in, registration, Google redirect, sign-out, auth-state observation, and ID-token retrieval are implemented. The auth provider lifecycle itself has no dedicated integration test file in the current source tree.
5. **Safe next implementation boundary:** do not pretend static rendering proves sign-in lifecycle. Add a real DOM-capable test harness and lockfile-consistent dependencies in a dedicated change, then cover initial observer state, signed-out/signed-in transitions, sign-in/register failures, token refresh, sign-out, and observer cleanup. Avoid hand-editing the lockfile or claiming lifecycle coverage before those tests run.

### Stage 1 acceptance boundary and progress accounting
- CI now verifies the repository-level frontend/backend test and build pipeline plus the isolated backend container/Redis smoke path. This closes the CI-pending note for commit `6c84034` but does not validate production Firebase Admin credentials, real valid/expired/revoked/wrong-project signed tokens, managed Redis TLS, Fly Machine/Volume permissions and restart persistence, off-host backup/restore, production ingress/CORS/HTTPS, or monitoring.
- Overall progress remains **20.90%**; Stage 1 remains **75% provisional**. No progress credit is assigned merely for CI completion or documentation reconciliation; a criterion-level weighting review and production-gate evidence are still required.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`


## 2026-11-08 — Firebase frontend configuration boundary and status semantics

### Five-work-package implementation cycle
1. **Exact branch/CI preflight:** started from branch HEAD `10a96951d18e71728e0d22128f174e2aa5170fd4`; `main` remained unchanged. CodeQL for this HEAD completed successfully; Automated Tests was still running when this unit began.
2. **Firebase app selection hardening:** `getFirebaseAuth()` now searches specifically for the Firebase default app rather than treating any named app as proof that a default app exists.
3. **Project-boundary enforcement:** a pre-existing default app is reused only when its API key, auth domain, project ID, and app ID exactly match the current `VITE_FIREBASE_*` configuration. A mismatch throws a sanitized configuration error before `getAuth()` is called; no credentials are logged.
4. **Service regression coverage:** added tests for incomplete environment configuration, default-app initialization and memoization, named-app-only initialization, reuse of a matching default app alongside named apps, wrong-project rejection, and Google account-selection parameters.
5. **Authentication status accuracy:** corrected `AuthPanel` so provider status `error` is displayed as `AUTH ERROR`, not the misleading `SIGNED OUT`; added static-render regression tests for error, unconfigured, and signed-in states.

### Files changed
- `src/services/firebase.ts`: select only the default Firebase app and enforce exact configured project/app identity before obtaining Auth.
- `src/services/firebase.test.ts`: focused Firebase configuration and app-selection tests.
- `src/components/AuthPanel.tsx`: accurately distinguish authentication errors from signed-out state.
- `src/components/AuthPanel.test.tsx`: static markup regressions for status presentation.
- `docs/PROJECT_PROGRESS.md`: record this security and test slice plus its verification boundary.

### Verification boundary
- These new tests are committed for CI execution; no local Vitest run is claimed from this GitHub-only editing session.
- The component tests use `renderToStaticMarkup`; they verify displayed status but do not execute browser events or React effects.
- Full `AuthProvider` lifecycle integration testing still requires a DOM-capable test environment and lockfile-consistent dependencies. The repository currently has neither jsdom/happy-dom nor React Testing Library in its package lock, so no dependency or lockfile was fabricated in this change.
- Production Firebase Admin credentials and real signed-token E2E (valid, expired, revoked, wrong-project) remain open external acceptance gates.

### Progress accounting
- Overall checkpoint remains **20.90%**; Stage 1 remains **75% provisional**.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`
- This implementation improves code-level Firebase app isolation and error-state accuracy; progress credit awaits exact-HEAD Automated Tests and CodeQL results plus the agreed acceptance ledger.


## 2026-11-08 — Firebase Auth initialization fails closed in React provider

### Five-work-package cycle
1. Rechecked active branch and exact HEAD before editing: `phase-2/market-data-foundation` at `faf171e5c0d53b90f96c17d475c3de365240afb3`; `main` remained unchanged.
2. Rechecked CI for that exact SHA: CodeQL completed successfully; Automated Tests had frontend tests/build, backend tests, and dependency audits successful while the backend image build was still running.
3. Reviewed the AuthProvider effect and action boundaries. `getFirebaseAuth()` could throw on a default-app/project mismatch before the provider installed its observer, and the same exception could escape a sign-in/register/sign-out action because initialization happened outside the action try/catch.
4. Added a single fail-closed resolution boundary. Initialization errors now become an explicit safe error state in the provider effect and user actions; they no longer escape as uncaught exceptions. Token retrieval also rejects with the sanitized provider-level message.
5. Added focused unit tests for successful resolution, initialization failure, and an unconfigured Firebase result.

### Files changed
- `src/auth/AuthProvider.tsx`: normalize Firebase initialization failures and prevent uncaught exceptions in effect/action boundaries.
- `src/auth/AuthProvider.test.tsx`: test the fail-closed resolver contract.
- `docs/PROJECT_PROGRESS.md`: record the implementation and exact verification boundary.

### Verification boundary
- This change is committed for exact-HEAD CI. No local test run is claimed.
- Resolver unit tests validate the initialization boundary but are not a full React DOM lifecycle test. Auth observer transitions, redirect completion, token refresh, and cleanup still need a DOM-capable integration harness.
- At the time of this edit, exact-HEAD Automated Tests was still in progress after frontend tests/build and backend tests had passed; backend image build and Redis smoke/security scan steps had not yet completed. CodeQL had completed successfully.
- No credentials, paid resources, Firebase production setup, or Fly resources were created.

### Progress accounting
- Overall checkpoint remains **20.90%**; Stage 1 remains **75% provisional**.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`
- This is a code-level fail-closed correction; no progress credit is assigned until exact-HEAD CI and criterion-level verification are complete.


## 2026-11-08 — Firebase Auth observer subscription boundary

### Five-work-package cycle
1. Rechecked the active branch HEAD (13526a0af359b8de060d10c767edc4295d7ef796) and current workflow state before editing. The branch remains phase-2/market-data-foundation; main remains untouched.
2. Confirmed exact-HEAD CodeQL success. Automated Tests had frontend tests/build, secret scans, backend tests, and dependency audits complete successfully; backend container image build was still in progress.
3. Identified a remaining exception boundary: observer registration itself was outside a try/catch. A synchronous SDK/setup failure could still escape the React effect. The observer error callback also left a potentially stale user in provider state.
4. Added subscribeToFirebaseAuth() as a narrow subscription boundary. It forwards signed-in/signed-out observer events, preserves the Firebase unsubscribe callback, forwards asynchronous observer errors, and converts synchronous registration failures into the provider's existing fail-closed error path. Observer errors now clear the user before setting error status.
5. Expanded AuthProvider unit coverage with three observer-contract tests: state-event forwarding and cleanup, asynchronous error forwarding, and synchronous registration failure handling.

### Files changed
- src/auth/AuthProvider.tsx: isolate observer registration, preserve cleanup, and clear stale user state on observer error.
- src/auth/AuthProvider.test.tsx: add observer contract and cleanup tests.
- docs/PROJECT_PROGRESS.md: record the change and verification limits.

### Verification boundary
- No local test run is claimed. The exact-HEAD CI run observed before this commit had not yet completed its backend container build, Redis smoke test, and image scan.
- The new tests exercise the observer subscription contract with mocked Firebase callbacks. They do not mount the React provider in a DOM, and do not prove real browser lifecycle, Firebase redirect completion, token refresh behavior, or production identity-token validation.
- A DOM-capable test harness remains a separate follow-up because the current dependency manifest/lockfile does not contain jsdom, happy-dom, or React Testing Library. No lockfile was hand-edited and no unverified dependency version was introduced.
- No production credentials or paid cloud resources were provisioned.

### Progress accounting
- Overall remains 20.90%; Stage 1 remains 75% provisional.
- Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.
- Code and mock-level test coverage improved, but exact-HEAD CI and end-to-end lifecycle acceptance remain outstanding.


## 2026-11-08 — Exact-HEAD CI closure and Stage 1 remaining-gates audit

### Five-work-package verification cycle
1. Revalidated the active branch ref and confirmed HEAD is `55eadd66d619accde6577b590f5f5b21b1d38270`; `main` remained at `e3841681bc69b73619058deaf939df82ae5116a1` and was not modified.
2. Re-polled the exact-HEAD Automated Tests workflow. Run [#42436063431](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42436063431) completed with conclusion **success**.
3. Inspected all job steps: frontend dependency install/audit, frontend unit tests, production build, frontend secret scans, backend dependency install/tests/audit, backend container build, Redis-backed container smoke test (health + 200 then 429 rate-limit behavior), Trivy HIGH/CRITICAL image scan, vulnerability report export/upload, and cleanup all completed successfully.
4. Confirmed exact-HEAD CodeQL run [#42436063369](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42436063369) completed with conclusion **success**.
5. Audited the remaining Stage 1 authentication and release evidence. Backend `FirebaseIdentityVerifier` has unit coverage for issuer/audience/subject/auth-time validation, revocation-check invocation, malformed/oversized tokens, SDK errors, project app initialization, and fail-closed behavior. HTTP and WebSocket authorization also check canonical instrument mapping and entitlement. The remaining gap is not the verifier unit layer: browser-level React AuthProvider lifecycle coverage and real deployment Firebase/Admin credential smoke tests remain outstanding.

### Verified status and boundaries
- Exact-HEAD Automated Tests and CodeQL are both green on `55eadd66d619accde6577b590f5f5b21b1d38270`.
- The CI Redis smoke test uses an ephemeral CI Redis service. It does not establish managed production Redis TLS, persistence, failover, or Fly network reachability.
- Trivy's CI step passed for the tested image at this commit; this is not a permanent guarantee against newly disclosed vulnerabilities after the scan.
- The AuthProvider tests remain mocked observer-contract tests. They do not mount/unmount the provider in a browser DOM or prove redirect completion, token refresh, or production session behavior.
- Production Firebase Admin credentials and signed-token E2E (valid, expired, revoked, wrong-project), Fly ingress trust, persistent-volume permissions, backup/restore, and deployed HTTPS/WSS smoke tests remain external release gates.
- No credentials, user data, paid cloud resources, or production services were provisioned.

### Next focused Stage 1 work
1. Add a DOM-capable frontend integration test environment with a dependency/lockfile update generated and verified consistently; do not hand-edit lockfile metadata.
2. Exercise AuthProvider mount, initial loading, signed-in/signed-out observer transitions, observer error, cleanup/unmount, sign-out, and token refresh behavior with controlled Firebase SDK mocks.
3. Re-run exact-HEAD frontend tests/build, full Automated Tests, and CodeQL.
4. Keep real Firebase Admin and deployment smoke checks explicitly external; do not mark them complete without real environment evidence.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional**.
- CI completion validates the current repository commit but does not by itself satisfy the outstanding browser lifecycle and production deployment acceptance criteria.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`



## 2026-11-08 — Auth lifecycle and release-gate evidence refresh (HEAD 70fdf42)

### Five-work-package audit
1. Re-read the active branch ref: `phase-2/market-data-foundation` is at `70fdf42e9cd9e6c79eae8d3a144a68f59d0ddd72`. `main` remains at `e3841681bc69b73619058deaf939df82ae5116a1`; no main ref was changed.
2. Verified the latest Automated Tests run `42436392709` and CodeQL run `42436392713` both target exact HEAD `70fdf42e9cd9e6c79eae8d3a144a68f59d0ddd72` and completed successfully. Vercel commit status is success.
3. Inspected `AuthProvider.tsx`, its tests, Firebase client initialization, Vite config, and the CI workflow. Firebase client initialization checks all required public config values and rejects a mismatched default Firebase app. The observer subscription boundary preserves unsubscribe and fails closed on synchronous or asynchronous observer errors.
4. Confirmed the frontend tests still only exercise the observer contract with mocked Firebase callbacks. There is no DOM environment in the dependency lockfile; actual provider mount/unmount, context transitions, and browser lifecycle are not yet tested. No dependency or lockfile change was attempted because a real package-manager environment to generate and verify the lockfile is not available through this repository connector.
5. Re-audited backend identity tests and deployment boundaries. Firebase Admin verifier tests use injected callables/fake SDK modules, not signed production Firebase tokens. Fly config remains a template; no production Fly Machine/Volume, managed Redis, credentials, encrypted off-host backup, or restore drill has been provisioned.

### Exact-HEAD CI evidence
- Automated Tests: [run 42436392709](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42436392709) — completed successfully; frontend tests/build, backend tests, image build, ephemeral Redis smoke test, and Trivy scan all succeeded.
- CodeQL: [run 42436392713](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42436392713) — JavaScript/TypeScript and Python analyses succeeded.
- Vercel commit status: success.
- The Redis service in CI is ephemeral; this is not evidence of production managed Redis TLS, persistence, failover, or Fly connectivity.
- Trivy success applies to the image scanned for this commit only.

### Corrections and remaining gates
- The preceding section's run evidence referred to commit `55eadd66d619accde6577b590f5f5b21b1d38270`, not the current documentation-only HEAD. This section records the separately verified exact-HEAD runs for `70fdf42`.
- Current AuthProvider integration gap: DOM mount/unmount and observable context lifecycle.
- Current identity integration gap: real signed-token checks for valid, expired, revoked, and wrong-project cases in an authorized test Firebase project.
- Current deployment gates: Fly UID/GID and volume permission/persistence checks, SQLite Online Backup API backup and restore drill, off-host encrypted backup/retention, trusted Fly proxy configuration, managed Redis network/reliability checks, deployed HTTPS/WSS smoke tests, and monitoring.
- Branch protection currently reports `protected: false`; changing repository governance settings requires explicit owner approval.
- No credentials, user data, or paid cloud resources were provisioned.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional**.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`
- This audit and documentation correction do not satisfy new implementation acceptance criteria and do not justify increasing the progress score.


## 2026-11-08 — Firebase ID-token observer coverage

### Authentication lifecycle hardening
- Switched the AuthProvider observer from `onAuthStateChanged` to Firebase `onIdTokenChanged`. The latter reports sign-in/sign-out state and ID-token refresh events, allowing the existing provider callback to receive updated Firebase User state after credential refresh.
- Retained the existing observer error handling and unsubscribe cleanup contract.
- Extended the mocked observer tests to assert that the subscription uses the ID-token observer and forwards an updated User instance for a same-account token refresh event.
- This is observer-contract coverage only. It does not replace the still-pending React DOM mount/unmount lifecycle test or a real Firebase signed-token E2E against an authorized test project.
- Exact-HEAD Automated Tests for parent commit `6c71eb3` were still running when this change was prepared; the new commit must receive its own full CI result before being considered validated.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional**.
- This implementation improves the authentication observer behavior, but acceptance criteria for actual browser lifecycle and production identity validation remain incomplete. Do not increase progress until the new tests pass and the broader criteria are met.


## 2026-11-08 — AuthProvider server-rendered context contract tests

### Verified repository test coverage added
- Added React server-rendered tests for the AuthProvider context boundary using the existing `react-dom/server` dependency; no new package or lockfile mutation was required.
- Tests cover the initial `loading` state when Firebase is configured, the explicit `unconfigured` state when Firebase configuration is absent, exposure of the expected auth action methods, and rejection of `useAuth` outside an AuthProvider.
- These tests intentionally do **not** claim browser DOM lifecycle coverage: server rendering does not run the provider effect, mount a browser DOM, exercise Firebase observer transitions, or verify unmount cleanup.
- The existing mocked observer tests remain responsible for the subscription callback, error forwarding, refresh callback, and unsubscribe contract.
- Exact-HEAD CI validation for this test addition is pending until the commit's Automated Tests and CodeQL runs complete.

### Remaining Stage 1 authentication gates
1. A DOM-capable test environment and real React mount/unmount lifecycle coverage.
2. Firebase Admin signed-token E2E for valid, expired, revoked, and wrong-project tokens against an authorized test Firebase project.
3. Production deployment and identity-boundary validation remain separate release gates.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional** pending exact-HEAD test results and outstanding integration/release acceptance criteria.
- Server-rendered context contract tests are additional unit coverage, not a substitute for DOM lifecycle or real signed-token E2E.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`


## 2026-11-08 — Firebase authentication error disclosure regression tests

### Security-focused test slice
- Exported the existing pure Firebase error-to-user-message mapper so it can be tested directly without mounting React or initializing Firebase.
- Added tests proving recognized Firebase error codes map to fixed Indonesian messages and unknown/provider-supplied error messages are not forwarded to the UI.
- Covered non-object/null error input and a synthetic sensitive-detail string to guard against accidental disclosure of provider internals or token-like text.
- This change does not alter authentication decisions, token verification, or Firebase SDK behavior; it makes the existing sanitization boundary directly regression-testable.

### Verification boundary
- Tests are committed for exact-HEAD CI execution; no local package-manager run is claimed.
- This is pure-function security regression coverage, not browser DOM lifecycle or signed-token E2E coverage.
- The existing DOM-capable React lifecycle and authorized Firebase signed-token E2E gates remain open.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional**.
- No progress credit is assigned until the exact-HEAD CI run passes and the Stage 1 acceptance ledger is reconciled.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`


## 2026-11-08 — Firebase Auth action contract regression coverage

### Implementation
- Expanded the existing Firebase SDK mocks so AuthProvider action methods can be asserted directly without changing production authentication behavior.
- Added six tests for email sign-in normalization, email registration normalization, Google redirect provider wiring, sign-out Auth-instance wiring, current-user ID-token retrieval, and rejection when no user is signed in.
- Tests obtain the AuthProvider context through React server rendering. They cover exposed action callbacks only; server rendering does not execute the provider effect, mount a browser DOM, or validate observer lifecycle/unmount cleanup.
- The lockfile does not contain installed package entries for jsdom, happy-dom, @testing-library/react, @testing-library/dom, or react-test-renderer. No dependency or lockfile changes were made.

### Verification boundary
- Exact-HEAD GitHub Actions validation is required for this test change; no local npm execution is claimed.
- Browser DOM lifecycle tests and real Firebase Admin signed-token E2E (valid, expired, revoked, wrong-project) remain open.
- Production Fly/Redis/backup/restore/deployed HTTPS-WSS gates remain external release requirements.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional**.
- The added tests cover AuthProvider action wiring but do not close browser lifecycle, real signed-token, or production deployment acceptance criteria.
- Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.


## 2026-11-08 — Firebase subject and UID consistency hardening

### Implementation
- Tightened the verified-principal claim boundary: when Firebase Admin returns both JWT `sub` and `uid`, the verifier now rejects a token payload if those identifiers disagree.
- Preserved the existing Firebase Admin signature, issuer, audience, expiry, and revocation verification path. This is an additional consistency check after SDK verification; it does not replace cryptographic token validation.
- Added a regression case to the invalid-claims matrix proving a mismatched `uid`/`sub` pair cannot produce a `VerifiedPrincipal`.
- Existing valid claim fixtures continue to represent matching identifiers. No SQLite, CME calendar, frontend behavior, dependency, or lockfile changes were made.

### Verification boundary
- The new regression test is committed for exact-HEAD CI execution; no local pytest run is claimed through the GitHub repository connector.
- This test exercises the decoded-claims validation boundary using the existing injected verifier seam. It is not a real Firebase signed-token E2E test.
- DOM lifecycle coverage and authorized Firebase signed-token E2E for valid, expired, revoked, and wrong-project cases remain open.

### Progress accounting
- Overall remains **20.90%**; Stage 1 remains **75% provisional** until exact-HEAD CI and the remaining integration/release acceptance criteria are satisfied.
- This targeted identity-consistency hardening does not by itself close the Stage 1 identity acceptance gate.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`


### Exact-HEAD CI verification — 2026-11-08

The Firebase subject/UID consistency hardening from commit `0e99dc039495a90abbea1649569e75eff7b864ee` is now verified by GitHub Actions on that exact HEAD:

- Workflow run [42439735705](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42439735705) completed with conclusion **success** for the push event on `phase-2/market-data-foundation`.
- The single `Test and Build` job passed all reported steps, including frontend dependency installation/audit, frontend unit tests and production build, frontend bundle secret scanning, backend dependency installation/tests/audit, container build, Redis-backed smoke test, and Trivy image scan.
- The combined commit status reports Vercel **success** for the same HEAD.
- The mismatched `uid`/`sub` regression case is therefore covered by the exact-HEAD backend test run. This remains a decoded-claims validation test using the injected verifier seam, not a real signed Firebase token E2E.

Remaining Stage 1 identity gates are unchanged: real Firebase signed-token E2E (valid, expired, revoked, wrong-project) and React DOM AuthProvider lifecycle coverage (mount/unmount, observer transitions/errors, token refresh, and cleanup). The existing frontend AuthProvider tests use helper-level mocks and server rendering; they do not execute browser effects.

Progress accounting remains unchanged: overall **20.90%**, Stage 1 **75% provisional**. Exact-HEAD CI verifies the targeted regression but does not close the outstanding lifecycle, signed-token, and production reliability acceptance criteria. No progress credit is inferred from CI completion alone.


### Auth observer lifecycle boundary hardening — 2026-11-08

Implemented a testable lifecycle boundary for the Firebase observer used by `AuthProvider`:

- Extracted the complete observer startup/state-transition path into `startFirebaseAuthObserver`; the React effect delegates to this boundary and returns its cleanup.
- Observer events are ignored after cleanup has deactivated the lifecycle, including callbacks already queued by the provider. Cleanup is idempotent and invokes the Firebase unsubscribe at most once.
- Initialization failure remains fail-closed; unconfigured Firebase does not manufacture a signed-out state; observer registration and asynchronous observer errors map to a sanitized error state.
- Added focused tests for signed-out/signed-in/error transitions, post-cleanup callback suppression, idempotent cleanup, initialization failure, unconfigured state, and synchronous registration failure.

Verification boundary: these tests exercise the complete extracted observer lifecycle boundary with Firebase observer mocks. They do **not** mount React into a browser DOM and do not replace the still-open React DOM mount/unmount integration test or authorized Firebase signed-token E2E. No dependency or lockfile was changed.


## 2026-11-08 — Firebase principal UID length validation

- Tightened the verified-principal boundary to reject a Firebase UID/subject longer than the documented 128-character maximum.
- Added regression coverage for an oversized matching `uid`/`sub` pair and for the supported `sub`-only fallback.
- Existing issuer, audience, auth-time, Firebase Admin signature verification, and revocation-check behavior are unchanged.
- Exact-HEAD verification completed on 2026-11-08 for commit `79ccd4c089f81be97dc831b4f86c9e64b37a84b3`: Automated Tests run #747 (`42441298097`) succeeded, including 25 frontend test files / 190 frontend tests, 497 backend tests, production build, Redis-backed container smoke test, dependency audits, and the Trivy HIGH/CRITICAL OS/library package scan. CodeQL run #105 (`42441298157`) also succeeded for JavaScript/TypeScript and Python, and the Vercel commit status was success. The Trivy report is scoped to HIGH/CRITICAL OS/library vulnerabilities; it is not a full secrets, misconfiguration, license, or all-severity audit. These CI results do not close the separate React DOM lifecycle, authorized Firebase signed-token E2E, or production infrastructure acceptance criteria.
- Overall progress remains **20.90%** and Stage 1 remains **75% provisional**; this targeted validation does not close the signed-token E2E or production release gates.



### WebSocket principal identity-drift regression — 2026-11-08

- Added a backend API regression test for a WebSocket session whose Firebase verifier initially returns one verified principal and returns a different principal at the scheduled authorization recheck.
- The test asserts the existing fail-closed behavior closes the socket with authentication failure (4401), rather than allowing the established subscription to continue under a changed account identity.
- This is test coverage for an existing identity revalidation branch; no production authentication behavior, Firebase configuration, token verification policy, SQLite schema, or market-data behavior was changed.
- Verification boundary: committed for exact-HEAD GitHub Actions execution. No local pytest run is claimed through the repository connector. This is not a real signed-token Firebase Admin E2E test.
- Overall remains **20.90%**; Stage 1 remains **75% provisional**. This additional regression test does not close the React DOM lifecycle, authorized Firebase signed-token E2E, or production reliability gates.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`

### Firebase principal claim-boundary regression coverage — 2026-11-08

- The first exact-HEAD CI run exposed two incorrect negative test expectations: the verifier intentionally accepts either a valid `uid` or, when `uid` is absent, a valid `sub`. Requiring each field independently contradicted the implemented fallback contract; this was a test defect, not a production verifier regression.
- Corrected the omission matrix to require the non-fallback claims (`iss`, `aud`, and `auth_time`) and added explicit positive coverage for both `sub`-only and `uid`-only principals, plus rejection when both subject identifiers are absent.
- Retained rejection of non-object claim payloads and existing issuer/audience mismatch, UID/subject drift, oversized identifiers, malformed/oversized tokens, SDK error normalization, named Firebase Admin app reuse/initialization, and `check_revoked=True` coverage.
- Verification boundary: correction is committed for exact-HEAD GitHub Actions validation; no local pytest run is claimed. These tests use an injected verifier/fake Admin SDK and are not real signed-token Firebase E2E coverage.
- Overall remains **20.90%** and Stage 1 remains **75% provisional**. This test correction does not close React DOM lifecycle, authorized Firebase signed-token E2E, or production reliability acceptance criteria.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`


### Exact-HEAD CI verification — Automated Tests #754 — 2026-11-08

- Workflow run [42446010425](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42446010425) completed with conclusion **success** for branch `phase-2/market-data-foundation` at exact HEAD `cf74d0eff49b1e642b226854468052f2506b565d`.
- The `Test and Build` job completed successfully, including frontend dependency installation and audit, frontend unit tests and production build, frontend bundle secret scanning, backend dependency installation and tests, backend dependency audit, backend container build, Redis-backed container smoke test, backend container Trivy scan, vulnerability report export, and report upload.
- The commit's combined status reports Vercel **success** for the same HEAD. CodeQL run [42446010422](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42446010422) was separately observed successful for JavaScript/TypeScript and Python.
- This confirms the repository's current automated CI and deployment status at this exact commit. It does not establish React DOM lifecycle coverage, real Firebase signed-token E2E, or production Fly Volume/backup/restore/Redis failover and deployed HTTPS/WSS acceptance.
- No source code or dependencies changed in this verification. Overall progress remains **20.90%** and Stage 1 remains **75% provisional**; CI success alone does not close the remaining Stage 1 integration and production reliability gates.
- `Perubahan progres: 0,00% — belum ada acceptance criteria baru yang terverifikasi.`


### Stage 1 evidence reconciliation — 2026-11-09

- The current working-branch tree at HEAD `d1e4a37169bf5c4f129db565bbf92a1a5eb0b72c` contains a root `package-lock.json` (lockfileVersion 3). The earlier Stage 1 audit text stating that no root lockfile exists is historical and must not be read as the current repository state.
- The exact-HEAD GitHub Actions workflow run [#784](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42618501125) succeeded at `d1e4a37169bf5c4f129db565bbf92a1a5eb0b72c`. Its job steps confirm `npm ci`, `npm audit --audit-level=high`, frontend tests, frontend production build, frontend bundle secret scanning, backend tests, backend dependency audit, container build, Redis/persistent-volume smoke test, and Trivy container scanning all completed successfully.
- This exact-HEAD CI evidence closes the automated clean-install/dependency-audit/CI portion of the CI reproducibility criterion. It does not close deployed Android/web smoke acceptance, Firebase signed-token E2E, Fly Volume production permissions/restart, off-host backup/restore drill, managed Redis TLS/failover/private networking, or production HTTPS/WSS and monitoring verification.
- React DOM lifecycle coverage remains unimplemented at this HEAD; no `jsdom` dependency or `src/auth/AuthProvider.dom.test.tsx` file is present in the audited tree.
- Stage 1 remains **75.00% provisional** under the historical equal-weight method. No percentage increase is awarded by this evidence reconciliation because the remaining partial acceptance groups are not fully closed and the scoring method remains unapproved. Do not describe Stage 1 as 100% complete.
- No production source, runtime configuration, or deployment resource was changed by this reconciliation.

### Exact-HEAD CI and Stage 1 reconciliation — 2026-11-09

Working branch: `phase-2/market-data-foundation`  
Audited HEAD: `f26c3d8421814796ed954b2a804eaeba5aeeca2c`

- Automated Tests [#787](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42628687958) completed successfully on this exact HEAD; all 25/25 job steps passed. The run verified `npm ci`, frontend dependency audit, frontend unit tests and production build, frontend bundle secret scanning, backend dependency installation/tests/audit, container build, Redis/persistent-volume smoke test, Trivy image scan/report export, and cleanup.
- CodeQL [#145](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42628687971) completed successfully on the same exact HEAD for Python and JavaScript/TypeScript. The combined commit status reported Vercel success.
- The root `package-lock.json` is present (lockfileVersion 3). Earlier statements in this file that describe a missing root lockfile are historical snapshots and must not be read as the current tree state.
- The frontend AuthProvider has a testable observer lifecycle boundary with helper-level tests for signed-in/signed-out/error transitions, callback suppression after cleanup, idempotent cleanup, initialization failure, unconfigured state, and synchronous observer-registration failure. It still lacks a React DOM mount/unmount integration test; no jsdom or equivalent DOM test dependency is present in the current package manifest.
- Firebase Admin verification code has unit coverage for issuer/audience, UID/subject consistency and length, malformed claims, and revocation checking via an injected verifier/fake SDK. Those tests are not real signed-token E2E using credentials and project configuration owned by the authorized production administrator.
- The SQLite backup helper creates an owner-restricted local consistent snapshot and checks SQLite integrity. It does not provide encryption, off-host transfer, retention, scheduling, or a restore drill.
- Production settings enforce Firebase project ID, TLS Redis URL, and HTTPS CORS constraints. Automated CI container smoke tests exercise Redis and a persistent volume, but they do not establish production Fly Volume permissions/restart behavior, managed Redis private networking/failover, deployed HTTPS/WSS, Android/web behavior, or production monitoring/recovery.
- Remaining Stage 1 acceptance gates therefore remain open: React DOM lifecycle test; real Firebase signed-token E2E; production Fly Volume verification; encrypted off-host backup/retention/restore; managed Redis TLS/private networking/failover; deployed HTTPS/WSS and Android/web smoke tests; production observability/fault recovery.
- Stage 1 remains **75.00% provisional** under the historical equal-weight ten-group model. No score increase is assigned from CI or documentation-only work. The scoring method and boundaries remain subject to owner approval.
- No application source, dependency manifest, lockfile, credentials, production configuration, or infrastructure was changed in this checkpoint.



### React DOM AuthProvider integration — 2026-11-09

- Added `jsdom@26.1.0` as a frontend development dependency and generated the root lockfile through the Node 20 CI runner. The generated `package-lock.json` was committed as `1826912f3e8b99ef242e19c8ac06dc5665a5f62a`; the final workflow is restored to clean `npm ci` with read-only repository permissions.
- Added `src/auth/AuthProvider.dom.test.tsx` with seven browser-DOM integration tests: initial mount/loading, signed-out and signed-in observer transitions, current-user rendering, safe observer error state, unmount unsubscribe and late-callback suppression, React StrictMode effect replay/cleanup, Firebase initialization failure, unconfigured state, and synchronous observer-registration failure.
- Initial run [#789](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42630725571) exposed one test-harness mistake: StrictMode wrapped only the child probe rather than the AuthProvider. The test was corrected so StrictMode wraps the provider itself; deprecated `react-dom/test-utils act` was replaced by `React.act`.
- Automated Tests [#790](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42631149393) completed successfully on source commit `55b7d4f8e86836500af0846ca7d89ab1f40cc3b8`. Frontend: 26 test files and 197 tests passed, including all seven DOM tests; npm audit reported zero vulnerabilities; production build and frontend bundle secret scan passed. Backend: all 517 tests passed; pip-audit reported no known vulnerabilities; container build, isolated Redis guard, non-root runtime, mounted-volume ownership, SQLite integrity/restart persistence, HTTP rate-limit rejection, Trivy scan, report export, and artifact upload passed.
- The same run generated the jsdom lockfile before `npm ci` and committed that generated file as the branch follow-up commit `1826912f3e8b99ef242e19c8ac06dc5665a5f62a`. The run therefore exercised the generated lockfile contents, although its checkout SHA was the parent source commit rather than the follow-up lockfile commit; the next clean workflow run is the exact-HEAD verification.
- CodeQL [#148](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42631149482) completed successfully for Python and JavaScript/TypeScript on source commit `55b7d4f8e86836500af0846ca7d89ab1f40cc3b8`; Vercel status was success for that commit.
- Trivy artifact [13681570393](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42631149393/artifacts/13681570393) was inspected. It covers the CI image `dezzta-chart-backend:ci`, digest `sha256:d0024931974be9799d5380f63d1a8a7394db5a43b7f34ca7ba7205d61dd9dab2`, Alpine 3.24.4 and Python package targets; it contains zero HIGH/CRITICAL findings in the configured OS/library scan. This is scoped to that CI image and scan configuration, not a production security certification.
- These changes close the React DOM lifecycle test sub-gate and remove the dependency-lockfile uncertainty. They do not close real Firebase signed-token E2E or any production deployment/backup/managed Redis/monitoring acceptance gate. Stage 1 remains **75.00% provisional** under the historical scoring method; no score increase is claimed until the remaining acceptance groups are fully closed and scoring criteria approved.
- Application runtime behavior, production credentials, database schema, and production infrastructure were not changed.


### Exact-HEAD validation after React DOM integration — 2026-11-09

- Working branch `phase-2/market-data-foundation` exact HEAD `0aaf2c7367aabc706e9b498eee1dafb95c81c986` passed Automated Tests [#791](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42632245788), all 25/25 workflow steps, after temporary lockfile-generation/push steps were removed and CI permissions returned to read-only.
- Frontend: `npm ci`, `npm audit --audit-level=high`, 26 test files / 197 tests, production build, bundle-secret scanner tests, and production bundle scan all passed.
- Backend: 517 pytest tests, pip-audit, Docker image build, isolated Redis shared-guard test, persistent-volume ownership/restart/SQLite integrity smoke test, Trivy scan, report export/upload, and cleanup all passed.
- CodeQL [#149](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42632245960) passed Python and JavaScript/TypeScript on the same exact HEAD; Vercel commit status was success.
- Manually inspected Trivy artifact [13682051497](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42632245788/artifacts/13682051497): CI image digest `sha256:54e829d9468ceef7349a124127e5f1529e445cef36a7b125e60784468c2d0963`, Alpine 3.24.4 and Python package targets, zero HIGH/CRITICAL findings in the configured OS/library scan. Scope limitations remain as documented above.
- Stage 1 remains **75.00% provisional**. Exact-HEAD CI and React DOM lifecycle gates are verified, but real Firebase signed-token E2E and production infrastructure acceptance remain open. No production resource or secret was modified.


### Stage 1 exact-HEAD validation and backup hardening — 2026-11-09

- Exact source HEAD validated: `7b6fa39ab0862e8ed8e436d95f64ff2207a78456` on `phase-2/market-data-foundation`.
- Hardened local SQLite backup publication: POSIX permission enforcement is now fail-closed when owner-only mode `0600` cannot be applied. Added regression tests for the mode and for preserving the previous destination on permission failure.
- Automated Tests [#794](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42636775435) passed on exact source HEAD. Frontend: 26 files / 197 tests. Backend: 519 tests. npm audit, pip-audit, production build, secret scanning, Docker build, isolated Redis and persistent-volume smoke tests, SQLite integrity/restart checks, Trivy scan, report export and upload all passed.
- Both new backup regression tests passed. CodeQL [#152](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42636775603) passed Python and JavaScript/TypeScript on the same source HEAD; Vercel status was success.
- Manually inspected Trivy artifact [13683362475](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42636775435/artifacts/13683362475). Alpine 3.24.4 OS and Python package targets each reported zero vulnerabilities in the configured scan. Scope is limited to the CI image and configured scanners.
- The React DOM AuthProvider integration gate is now closed by the seven committed DOM tests and exact-HEAD CI evidence. Do not carry forward older entries that say those tests are missing.
- Remaining Stage 1 production gates: authorized real Firebase signed-token E2E; actual Fly Volume permission/restart; encrypted off-host backup, retention and restore drill; managed Redis TLS/private networking/failover; deployed HTTPS/WSS and Android/web smoke; production monitoring/fault recovery.
- Stage 1 remains **75.00% provisional** under the historical equal-weight ten-group method. No percentage increase is assigned because the remaining production acceptance gates remain open and the scoring method still requires owner approval. No production resources or secrets were modified.


### 2026-11-09 follow-up — exact-HEAD CI #796 and authentication acceptance audit

- Active branch: `phase-2/market-data-foundation`; audited source HEAD: `855260b474c686e97b2ae2a744c77540a00c0f94`.
- CI [#796](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42637776798) is complete and successful on that exact HEAD; all job steps including cleanup passed. Frontend: 26 test files passed, clean install, npm audit, production build, and bundle secret checks passed. Backend: 519 tests passed and pip-audit found no known vulnerabilities. Docker, isolated Redis shared guard, non-root persistent-volume ownership, SQLite integrity/restart persistence, rate-limit smoke, Trivy scan and artifact export/upload passed.
- CodeQL [#154](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42637776819) passed Python and JavaScript/TypeScript; Vercel status passed.
- Inspected Trivy artifact [13682739863](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42637776798/artifacts/13682739863): configured OS (Alpine 3.24.4) and Python package targets reported zero vulnerabilities at HIGH/CRITICAL threshold. This is CI-image-only evidence.
- Auth integration review found `AuthPanel` exists but is not mounted in `src/App.tsx`; therefore the visible sign-in journey is not integrated into the app shell. The approved architecture direction calls for Firebase identity exchange into a short-lived, narrowly scoped WebSocket ticket, but issuance/signing-key lifecycle and real-provider E2E are not complete. Keep all of these within the open Firebase/auth production acceptance gate.
- Six production gates remain open: real Firebase signed-token and scoped-ticket E2E plus visible auth flow; actual Fly Volume permission/restart; encrypted off-host backup/retention/restore; managed Redis TLS/private networking/failover; deployed HTTPS/WSS and Android/web smoke; production monitoring/fault recovery.
- No Fly production app/Machine/volume, managed Redis, DNS, billing resource, production credential, or live provider feed was created or modified. These require authorized project-owner/admin access and secret-manager handling outside chat.
- Stage 1 remains **75.00% provisional**. No scoring change is justified by the CI run alone; production gates and scoring acceptance remain open. `main` was not changed.


### Stage 1 exact-HEAD follow-up — CI #799 and CodeQL #157 — 2026-11-09

- Exact branch HEAD: `7ce27502e1ef14ca65da79f366272778836ffe6d` on `phase-2/market-data-foundation`.
- Corrected `backend/README.md`: the WebSocket prototype authenticates using a Firebase Authentication ID token verified by Firebase Admin; it does not yet implement the separately approved short-lived, narrowly scoped WebSocket-ticket exchange. The documentation now explicitly blocks treating the prototype as the final production credential design.
- Automated Tests [#799](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42639532618) completed successfully on the exact HEAD. All 39 Test and Build job steps, including cleanup, completed successfully. Frontend clean install, audit, unit tests, production build and bundle-secret checks passed. Backend dependency install, 519 pytest tests, pip-audit, Docker build, Redis/persistent-volume smoke tests, Trivy scan/report export and upload passed.
- CodeQL [#157](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/42639533040) completed successfully for Python and JavaScript/TypeScript on the same exact HEAD. Vercel status was success.
- The open-PR/open-issue search returned no open pull requests or issues at the time of this audit.
- No runtime code, production credentials, production infrastructure, or deployment configuration changed. These CI results do not substitute for production acceptance.
- The six production gates remain open: authorized real Firebase signed-token E2E plus visible sign-in and scoped-ticket flow; actual Fly Volume permissions/restart; encrypted off-host backup/retention/restore; managed Redis TLS/private networking/failover; deployed HTTPS/WSS and Android/web smoke; production monitoring/fault recovery.
- Stage 1 remains **75.00% provisional**. No progress increase is justified by documentation-only changes or CI success alone. The scoring method remains subject to owner approval; `main` remains untouched.


---

## Indicator progress audit — 2026-11-13

Audit target before this documentation-only checkpoint: `600ff7ee7c5494ad894c762aa7e5644694de3175` on `phase-2/market-data-foundation`.
This section records repository evidence, not a claim that indicator features are complete or visible to users.

### Indicator status matrix

| Indicator / study | Verified implementation | Verified tests / safeguards | User-visible status |
|---|---|---|---|
| SMA 20 | `src/indicators/indicatorCalculations.ts`; rolling arithmetic mean of close values | Source-index alignment; null warm-up for first 19 bars; positive safe-integer period and finite input validation | Not integrated into chart controls or rendered overlay |
| EMA 20 | Same calculation module; SMA-seeded EMA with multiplier (2/(20+1)) | Source-index alignment; null warm-up for first 19 bars; invalid periods/non-finite values rejected | Not integrated into chart controls or rendered overlay |
| RSI 14 (Wilder) | Same module; average gains/losses use Wilder smoothing | First value appears at source index 14; flat-series edge case returns 50; rising-only edge case returns 100; finite input checks | Not integrated into a visible oscillator pane |
| MACD (12, 26, 9) | Same module; EMA(12) minus EMA(26), then EMA(9) signal and histogram | MACD line warm-up through index 24; signal warm-up through index 32; fast period must be smaller than slow | Not integrated into visible line/signal/histogram pane |
| Bollinger Bands (20, 2) | Same module; 20-close mean and population standard deviation × 2 | First complete band at index 19; non-negative finite deviation multiplier; finite values | Not integrated into visible chart overlay |
| Shared indicator hook | `src/indicators/useMarketIndicators.ts` | Reads `useMarketDataSnapshot()`; returns no indicator values unless source is backend, status is ready/degraded, and bars are non-empty; memoized by snapshot | Hook exists; no user-facing indicator selector or pane |
| Footprint (educational simulation only) | `src/education/simulatedFootprint.ts`; deterministic event-time bucketing into price cells | Buy/sell/unknown kept separate; delta = buy − sell; duplicate IDs rejected; invalid input and capacity overflow fail closed; bounded 10,000-event default ledger; reset and deterministic fixture tests | No chart rendering. Must display SIMULATED if later shown; not real trades/order flow |
| Heatmap | No implementation verified in source tree at this audit | No calculation/rendering test evidence found | Not implemented; await owner's reference image |
| Liquidation Maps | No implementation verified in source tree at this audit | No calculation/rendering test evidence found | Not implemented; await owner's reference image |

### Calculation and data-integrity details

- All five conventional indicators currently use the selected bar series' `close` values. They do not independently fetch market data.
- `calculateIndicators(bars)` returns arrays aligned one-to-one with the source bars. Warm-up entries are `null`, not synthetic or forward-filled values.
- The unit test file `src/indicators/indicatorCalculations.test.ts` covers SMA/EMA alignment and warm-up, RSI flat/rising cases, MACD line/signal warm-up, Bollinger population standard deviation, combined output lengths, invalid periods/non-finite values, and all 18 declared timeframe labels (`1s` through `3M`) using generated 40-bar test inputs.
- That timeframe test proves calculation helpers accept fixture bars labelled across those timeframe cases. It does **not** prove real backend data availability, timeframe selector enablement, exchange-session correctness, or deployed streaming support for every interval.
- The shared market-data architecture binds the hook to the exact validated backend snapshot identity and revision. DEMO/loading/unavailable/error states intentionally produce no indicator values.
- Footprint's fixture quantities are arbitrary simulation units. Unknown aggressor volume is never guessed into buy or sell. It has no provider/network adapter.

### UI and acceptance boundary

A source audit of `src/App.tsx` and `src/components/CandlestickChart.tsx` found the current app exposes chart, watchlist, settings, and timeframe navigation, but no indicator controls, indicator panes, or indicator overlay wiring. Therefore calculation foundations and tests are not equivalent to usable chart indicators.

No visual implementation is authorized by this audit. Keep the existing standard candlestick layout and spacing unchanged when Footprint is OFF. Only an explicitly enabled Footprint mode may later switch to the separately designed spaced-candle/cluster layout. Do not begin Footprint, Heatmap, or Liquidation Maps visual work until the owner supplies the relevant reference image(s) and the scoped blueprint is reviewed at the 40% project gate.

### Verification state and next actions

- Calculation and Footprint test files are present in the branch. Their presence is not a test-pass claim.
- At the time of this audit, Automated Tests run [43418208176](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43418208176) for `600ff7ee7c5494ad894c762aa7e5644694de3175` was pending with no jobs/results exposed yet.
- CodeQL run [43418208169](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43418208169) for the same SHA completed successfully.
- Next: obtain a completed exact-HEAD CI result; then add visible indicator controls/overlays/panes only under the approved scope, with interaction, timeframe-change, stale-series clearing, and rendering/performance tests.
- No overall project percentage is increased by this audit. Preserve the existing recorded progress accounting and the separate Stage 1 acceptance disposition.



---

## Android / Termux readiness audit — 2026-11-13

See [ANDROID_TERMUX_STATUS.md](./ANDROID_TERMUX_STATUS.md) for the full evidence matrix and acceptance gates.

- The read-only Android/Termux host preflight script exists and its automated CI test passed on the audited source HEAD.
- This only validates the inventory script and its safe behavior; it does not validate native backend execution on Android.
- The user's last reported Termux environment used Python 3.13; backend encryption test collection was blocked because `cryptography` was unavailable. OpenSSL 3.6.3 was reported, but that alone does not prove Python cryptography compatibility.
- Native Termux backend startup, complete backend tests on-device, SQLite restart persistence, Redis behavior, WebSocket/client connectivity, and Android background/recovery behavior remain unverified.
- **Termux support is incomplete and not accepted.** Docker CI on Python 3.12 Alpine is not a substitute for Android/Bionic validation.
- No percentage increase is awarded for this documentation audit. Stage 1 remains at its last recorded **75.00% provisional** and is not complete.


---

## Exact-HEAD verification follow-up — 2026-11-13

Audited documentation/source HEAD: `b4a9a742a2a34bcd621a5a1f87efea7bd3ab01cf` on `phase-2/market-data-foundation`.

- Automated Tests [#43419202810](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43419202810): **success** on this exact HEAD; all job steps and cleanup completed.
- Frontend: **26 test files / 211 tests passed**. The indicator calculation suite passed **7 tests**; simulated Footprint core passed **8 tests**, and Footprint fixture tests passed **4 tests**. These are calculation/simulation tests, not chart-rendering acceptance.
- Backend: **776 tests passed** on CI Python 3.12.16; backend dependency audit reported no known vulnerabilities; Docker image build, isolated Redis/shared-guard + persistent-volume smoke, container scan, and vulnerability-report export/upload all completed successfully.
- CodeQL [#43419202809](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43419202809): **success** on the same exact HEAD.
- No indicator UI was added by this verification. SMA/EMA/RSI/MACD/Bollinger calculations and Footprint simulation remain as recorded above; visible controls, overlays/panes, Heatmap, and Liquidation Maps remain incomplete.
- This exact-HEAD CI result closes the pending automated verification item for the recorded indicator calculation/simulation test files. It does not close live-data, UI, or visual acceptance.
- No progress percentage is increased from CI-only evidence. Stage 1 remains **75.00% provisional**; overall project progress remains at the last approved/historical **20.9%** checkpoint.

## Termux native test evidence update — 2026-11-13

The earlier Termux status entry is refined by later user-reported device results:

- Python 3.13.13 and pytest 9.2.0 were present in the latest reported test session.
- SQLite backup-focused tests passed **15/15**. Native backup/restore reported `INTEGRITY: ok`, `RESTORED_DATA: 6012.125`, `BACKUP_RESTORE_PASS`; file permission was `0o600`.
- The encrypted-backup tests remain blocked because the project interpreter cannot import `cryptography`. Do not describe SQLite-only backup tests as encryption tests.
- Official Termux package recipe `python-cryptography` version 50.0.2 satisfies the project's declared `cryptography>=50,<51` requirement and is the preferred native packaging route. Device repository availability and import under the project interpreter remain unverified.
- Native full backend startup, Redis/WebSocket, frontend connection, and Android process-restart/background validation remain open. Termux support is **not yet accepted**.
- No Stage 1 or overall percentage increase is assigned from these focused tests or documentation work.


## Exact-HEAD verification follow-up — 2026-11-13 (Termux documentation checkpoint)

Audited commit: `da7d000d789bdb445f0c551b7879beed89e5e7d4` on `phase-2/market-data-foundation`.

- Automated Tests [#43419736603](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43419736603): **success** on the exact audited SHA. Every step completed successfully, including frontend dependency install/audit, frontend unit tests/build, frontend bundle secret scanning, read-only Android host preflight test, backend dependency install/tests/audit, bounded synthetic SQLite outbox benchmark, backend container build, Redis shared-guard + persistent-volume smoke test, container scan, vulnerability report export/upload, and cleanup.
- CodeQL [#43419736562](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43419736562): **success** on the same exact SHA for JavaScript/TypeScript and Python.
- This closes the previously pending CI verification for the documentation checkpoint. It does not certify native Android/Bionic behavior or production deployment.
- Indicator calculation/simulation tests remain green on this exact HEAD through the full frontend test workflow. This confirms calculation/simulation regression coverage only; it does not add chart controls, overlays, oscillator panes, live Footprint data, Heatmap, or Liquidation Maps.
- Android host preflight remains a read-only inventory and its automated test passed. It does not install or prove `cryptography` on the user's Termux interpreter.
- No source code changed in this CI verification; no production infrastructure, credentials, or paid market-data provider was touched. `main` was not changed.
- Stage 1 remains **75.00% provisional** and overall project progress remains at the last historical **20.9%** checkpoint. CI success alone does not satisfy the outstanding production or native-device acceptance gates.


## Latest continuation checkpoint — 2026-11-13

Working branch: `phase-2/market-data-foundation` (do not modify `main`).

### Newly confirmed Termux blocker

The latest owner-reported Termux package query returns `python-cryptography` **48.0.1-1**, while `backend/requirements.txt` requires `cryptography>=50,<51`; the project interpreter still cannot import `cryptography`. This is a concrete repository-candidate mismatch, not an OpenSSL failure and not a SQLite backup failure. Installing 48.0.1 or lowering the dependency range is not accepted. The next safe action is to refresh package indexes and verify the configured mirror exposes a compatible 50.x package; if it does not, resolve the stale mirror/repository before installation. Full details and acceptance checks are recorded in `docs/ANDROID_TERMUX_STATUS.md`.

### Indicator progress documentation

`docs/INDICATOR_DATA_ARCHITECTURE.md` now contains the complete indicator acceptance matrix and latest available test evidence. The audited state remains:

- SMA 20, EMA 20, RSI 14 Wilder, MACD 12/26/9, and Bollinger Bands 20,2: calculation foundations implemented and unit-tested; visible chart controls/rendering/panes/legends/transition acceptance remain incomplete.
- Shared indicator hook: exact validated backend series only; no DEMO fallback; visible controls and rendering integration remain incomplete.
- Footprint: synthetic educational simulation only, marked SIMULATED; visual layout, owner reference image, approved blueprint, and live order-flow source remain unimplemented.
- Heatmap and Liquidation Maps: not implemented; owner reference images and reviewed blueprints remain prerequisites.

Latest inspected workflow evidence: frontend 26 files / 211 tests passed, including 7 indicator calculation tests, 8 Footprint core tests, and 4 Footprint fixture tests; backend 776 tests passed. These tests do not constitute visible indicator UI or Android-native acceptance.

### Progress percentages and release gate

- Stage 1 remains **75.00% provisional**, not complete, pending its remaining acceptance gates.
- Overall project progress remains the last owner-confirmed historical checkpoint **20.9%**; a freshly reconciled weighted percentage is still not established because the proposed milestone ledger has not been approved and scored criterion-by-criterion.
- No percentage increase is awarded for this documentation work, test-count totals, or commit count.
- The major UI expansion gate remains **40% overall**, with a scoped blueprint and owner review required before major implementation.

### Files updated in this continuation

- `docs/ANDROID_TERMUX_STATUS.md` — records the exact 48.0.1-1 package candidate and the safe corrective decision.
- `docs/INDICATOR_DATA_ARCHITECTURE.md` — records detailed acceptance states and latest inspected CI test totals.
- `docs/PROJECT_PROGRESS.md` — records the current blocker, indicator status, and unchanged progress accounting.

No source code, dependency constraints, encryption algorithm, production credentials, or production infrastructure were changed. `main` was not modified.

## Latest continuation checkpoint — 2026-11-13 (APK-first / ZERO COST)

Working branch: `phase-2/market-data-foundation`. Do not modify `main`.

### Owner's confirmed product direction

- Immediate delivery target is an Android APK installable and usable on the owner's Infinix GT20 (Android 15, aarch64).
- **ZERO COST** is a hard project constraint: prefer open-source/free tooling and avoid paid hosting, paid market-data subscriptions, paid APIs, paid build services, and paid publication. Disclose any unavoidable cost and seek a genuinely free alternative before proposing paid services.
- Google Play Store publication is explicitly deferred. Do not begin Play Store publishing, developer-account setup, or fee-related work unless the owner later asks.
- The owner is willing to consider a Termux distribution migration only if the project remains usable on the phone and a complete, verified backup/restore procedure exists. No uninstall, app-data clearing, or migration is authorized by this checkpoint.
- Preserve all existing features and do not trade away functionality to satisfy a zero-cost implementation. Clearly distinguish offline/demo behavior from real market data.

### Stage 1 and overall progress accounting

- Stage 1 remains **30/40 acceptance criteria = 75.00% provisional**. Ten external/operational acceptance gates remain open. This is the same 75% value recorded in earlier checkpoints, not a new increase.
- Overall project progress remains the latest owner-confirmed historical checkpoint **20.9%**. The newly proposed weighted ledger has not been approved/scored, so no freshly recalculated overall percentage is asserted.
- Do not increase either percentage for documentation commits, test counts, or APK workflow configuration alone.

### Android APK packaging audit

Verified workflow file: `.github/workflows/android-apk.yml`.

- Workflow supports manual dispatch and relevant source pushes on `phase-2/market-data-foundation`.
- Uses GitHub-hosted Ubuntu runner, Node 20, Java 21, Android SDK platform 35/build-tools 35.0.0, locked web dependency installation, Vite production build, and pinned Capacitor 7.4.3 tooling.
- Generates a temporary Android wrapper with application ID `com.dezzta.chart` and app name `DEZZTA CHART`.
- Runs Gradle `assembleDebug`, verifies the APK exists and is non-empty, calculates SHA-256, and uploads artifact `dezzta-chart-android-debug-apk` for seven days.
- This is a **zero-additional-build-fee CI route** using GitHub Actions; it does not establish a published APK artifact or successful installation on the owner's phone by itself.
- Current audit did not retrieve the exact successful Android APK workflow run, artifact ID, or APK SHA-256 for the APK previously downloaded by the owner. Do not invent or reuse an old APK download URL.
- **New owner-reported device evidence (2026-11-13):** the owner confirms that a trial DEZZTA CHART APK was successfully installed on the Infinix GT20. Record this as an owner-reported installation result, not as independently verified package identity or exact source-SHA provenance. The owner cannot resend the two previously seen images because of the app's upload limit; do not require them to proceed.
- Installation is now supported by owner report, but successful first launch, chart/navigation/touch behavior, persistence/restart, and correct offline/demo labelling remain unverified. The next APK acceptance step is to verify launch and core interactions on-device, then tie that result to a known APK artifact/checksum when available.
- The owner-reported installation result is not used to increase Stage 1's 30/40 provisional score because the historical acceptance ledger has not been reconciled to map this observation to a specific criterion and artifact.

### Indicator progress — complete tracker retained

The detailed acceptance matrix remains in `docs/INDICATOR_DATA_ARCHITECTURE.md` and the 2026-11-13 audit above. No indicator implementation status is upgraded by this checkpoint:

| Indicator / component | Verified calculation or engine | Visible feature status |
|---|---|---|
| SMA 20 | Implemented and covered by calculation tests; close-based, 20-bar warm-up | No chart toggle/overlay/legend integration |
| EMA 20 | Implemented and covered by calculation tests; SMA-seeded, 20-bar warm-up | No chart toggle/overlay/legend integration |
| RSI 14 Wilder | Implemented and covered by tests; first value at index 14 | No oscillator pane/scale/guides |
| MACD 12/26/9 | Implemented and covered by tests; line begins index 25, signal/histogram index 33 | No dedicated rendered pane |
| Bollinger Bands 20,2 | Implemented and covered by tests; population standard deviation, first band index 19 | No visible overlay/legend integration |
| Shared market-indicator hook | Exact validated backend snapshot only; no DEMO fallback | No user-facing controls/panes; stale-value transition acceptance remains |
| Footprint | Deterministic bounded synthetic educational simulation; buy/sell/unknown separated; SIMULATED provenance | No visual layout or live order-flow source; owner reference and reviewed blueprint required |
| Heatmap | No implementation verified | Not implemented; owner reference and reviewed blueprint required |
| Liquidation Maps | No implementation verified | Not implemented; owner reference and reviewed blueprint required |

Latest recorded CI evidence remains workflow #43420429575: frontend 26 files/211 tests, including 7 indicator calculation tests, 8 Footprint core tests, 4 Footprint fixture tests; backend 776 tests. This is regression evidence, not visible UI, live market-data, or Android acceptance. The normal candlestick layout and spacing must remain unchanged while Footprint is OFF; only explicit Footprint ON may activate the dedicated spaced-cluster layout. Do not begin Footprint/Heatmap/Liquidation Maps visual implementation before the respective owner reference image(s) and scoped blueprint review at the 40% overall gate.

### Termux blocker — corrected resolution

The authoritative current device evidence and corrected decision are in `docs/ANDROID_TERMUX_STATUS.md`. This supersedes older instructions elsewhere in this progress history that recommended switching to upstream `packages.termux.dev`:

- The owner's Termux is Google Play build `googleplay.2026.10.09`, `termux-tools 3.0.9`, `termux-keyring 3.15`, Android 15/aarch64.
- Its original `https://termux.net` source verifies successfully and offers only `python-cryptography 48.0.1-1`.
- Upstream `packages.termux.dev` requires a signing key absent from this Play build's keyring; APT rejected it with `NO_PUBKEY 5A897D96E57CF20C`. The original source was restored successfully.
- Keep the working Play build and its original source for now. Never bypass signature checks, install 48.0.1, weaken `cryptography>=50,<51`, or change AES-GCM/PBKDF2.
- SQLite backup tests previously passed 15/15, but encrypted-backup tests remain blocked until a compatible, authenticated package path is available. Any Termux migration requires a verified backup/restore plan and owner approval.

### Immediate next execution sequence

1. Reconcile and retrieve the exact APK workflow run/artifact the owner recalls, or dispatch a new workflow on the active branch if the connected GitHub Actions interface permits it. Do not claim an APK is ready until artifact and checksum are verified.
2. Verify the exact APK on the Infinix GT20; keep Google Play publication out of scope.
3. Continue closing Stage 1's remaining ten acceptance criteria with evidence, prioritizing no-cost paths and not claiming external production gates without owner-controlled credentials/resources.
4. Keep indicator progress documentation synchronized after each real implementation/test milestone.

No application source, dependency, encryption implementation, paid infrastructure, production credential, or `main` branch was changed by this documentation checkpoint.


## Latest continuation evidence — 2026-11-13 (APK owner report and exact-HEAD CI)

- Active branch HEAD verified as `f7728136a480925bca11feb51b56f3b59b67bbf6` on `phase-2/market-data-foundation`; `main` was not modified.
- Automated Tests run [#1029](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43441589186) completed successfully on that exact HEAD. Its `Test and Build` job completed successfully.
- CodeQL run [#387](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43441588920) completed successfully on the same exact HEAD. Vercel commit status is success.
- The CI artifacts on #1029 are the synthetic outbox benchmark and container vulnerability reports; **they are not Android APK artifacts**. No Android APK artifact/checksum was inferred from these CI results.
- Owner reports a trial APK was installed successfully on the Infinix GT20. This is useful device evidence, but exact APK workflow run, artifact identity, checksum, launch, and interaction evidence are not yet linked to it.
- Stage 1 remains `30/40 = 75.00% provisional`; overall progress remains the historical `20.9%`. No score uplift is assigned until the acceptance ledger maps the owner report to a specific criterion and the remaining operational gates are evidenced.
- Indicator status remains unchanged and is fully tracked in `docs/INDICATOR_DATA_ARCHITECTURE.md`: SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, and Bollinger Bands 20,2 have tested calculation foundations but no visible chart controls/panes/overlays; the shared hook has no user-facing integration; Footprint is SIMULATED only; Heatmap and Liquidation Maps are not implemented. Do not claim visible/live indicator completion from CI tests.
- No source code, dependency constraints, production credentials, paid infrastructure, encryption design, or `main` branch were changed.


## Verified Android APK build — 2026-11-13

A fresh Android debug APK build completed successfully on the active branch.

- Workflow run: [#43442780935](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43442780935)
- Source branch: `phase-2/market-data-foundation`
- Source commit: `ba05d72d87a6c228fd6fb242ea37507636d5081e`
- Workflow job: `Build installable Android debug APK` — completed successfully.
- All 14 substantive steps completed, including locked web dependency installation, web production build, pinned Capacitor Android wrapper generation, Gradle `assembleDebug`, APK non-empty verification, and artifact upload.
- Artifact: `dezzta-chart-android-debug-apk`, artifact ID `14046691238`, 3,874,510-byte ZIP, expires 2026-11-20 14:28:37 UTC.
- GitHub artifact ZIP SHA-256: `bdc373a056bb2d4fe7d0e228e851a0e15e85575b91d5685f17e546e8a3dd30d7`.
- Artifact was downloaded and inspected in the audit environment. It contains `app-debug.apk` (4,233,778 bytes); ZIP integrity test passed.
- Extracted APK SHA-256: `d1203014fc16bbfd0a823ceb2fdae2bab0f855f554bec3393fad44d2b0e1de49`.
- APK file signature/container inspection identifies it as an Android package; the APK archive integrity test passed.
- Workflow commit `ba05d72...` only adds a clarifying comment to the existing Android APK workflow. No app source, package manifest, dependency lock, encryption, or production configuration changed in that trigger commit.
- Vercel status on the workflow source commit is success.
- The owner's earlier trial APK installation on the Infinix GT20 remains owner-reported evidence. It is not yet proven to be this exact artifact. First launch, package identity on-device, chart interactions, persistence/restart, and offline/demo labelling remain unverified.

### Acceptance and progress accounting after APK build

- Android APK build/package artifact gate: **passed for this workflow run**.
- APK installation/launch on target GT20 for this exact artifact: **not yet verified**.
- This build does not by itself close the remaining Stage 1 external/operational gates.
- Stage 1 remains **30/40 = 75.00% provisional** pending criterion-by-criterion ledger reconciliation. Do not award additional percentage solely for a successful CI APK build.
- Overall project remains at historical **20.9%**; no new weighted ledger calculation is asserted.
- Indicator status is unchanged. Refer to `docs/INDICATOR_DATA_ARCHITECTURE.md` for the full calculation definitions, test evidence, visual acceptance matrix, owner-reference prerequisites, and mode constraints. An APK package build is not evidence that visible indicators are implemented or accepted.


## Owner confirmation — installation of the 4.23 MB APK (2026-11-13)

The owner confirms they installed the **4.23 MB `app-debug.apk`** on the Infinix GT20. This matches the extracted APK file size (4,233,778 bytes) from the sole APK contained in workflow run [#43442780935](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43442780935), artifact ID `14046691238`.

Evidence boundary:
- The workflow run contains exactly one artifact, `dezzta-chart-android-debug-apk`, and the ZIP contains exactly one APK, `app-debug.apk`.
- The owner-reported 4.23 MB installation therefore matches the only APK produced by that run by filename/size context.
- File size alone is not a cryptographic identity check. Do not claim that the installed device package has been matched to SHA-256 `d1203014fc16bbfd0a823ceb2fdae2bab0f855f554bec3393fad44d2b0e1de49` unless an on-device digest/package inspection is later available.
- Record installation on the target device as **owner-confirmed for the matching-size APK**. First launch, package identity, chart interaction, navigation, persistence/restart, and offline/demo provenance remain separate acceptance checks.

No Stage 1 percentage uplift is applied automatically. The historical provisional Stage 1 score remains 30/40 (75.00%) until the ten-group scoring ledger is reconciled criterion by criterion. Overall progress remains the historical 20.9%.


## APK static security review — 2026-11-13

The exact Android artifact from workflow run [#43442780935](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43442780935) was downloaded again and inspected in the audit environment.

### Artifact identity

- Workflow artifact ID: `14046691238`; ZIP contains exactly one file, `app-debug.apk`.
- APK size: **4,233,778 bytes**.
- APK SHA-256: `d1203014fc16bbfd0a823ceb2fdae2bab0f855f554bec3393fad44d2b0e1de49`.
- Package: `com.dezzta.chart`; version name `1.0`; version code `1`.
- Android manifest: min SDK 23; target SDK 35.
- The APK archive was readable and its ZIP integrity check passed.

### Manifest and signing observations

- Declared permissions observed: `android.permission.INTERNET` and the app-specific AndroidX dynamic-receiver permission `com.dezzta.chart.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`.
- No camera, microphone, contacts, SMS, or location permission was present in the decoded manifest.
- The application manifest has `android:debuggable=true` and `android:allowBackup=true`.
- The embedded signer certificate identifies itself as **Android Debug** (self-issued), RSA 2048-bit, SHA256withRSA. Certificate SHA-256 fingerprint: `1E:01:30:B0:59:CE:8C:DE:F8:42:FC:7A:D0:90:4B:43:6A:2F:FE:FC:09:54:1B:08:1E:40:BD:94:C1:7E:42:5B`.
- This matches the workflow's explicit `assembleDebug` output. A debug certificate and debuggable application are expected characteristics of a debug APK, but they are not suitable as the final public-release signing/configuration.

### Antivirus-warning interpretation and limits

The owner reports that the phone's antivirus still flags the installed APK, while a manual scan reports no virus. The debug signing identity and `debuggable=true` setting are plausible reasons for a generic sideload/debug-build warning. They do **not** establish that the warning is a false positive, and this static audit does **not** prove the APK malware-free.

No third-party scanner upload was performed. The exact antivirus product, detection name, and detection category have not been supplied, so the specific warning cannot yet be attributed. Do not upload the APK to public scanning services without the owner's informed consent.

### Release-hardening actions before any public/release APK

1. Build a dedicated release variant with debugging disabled.
2. Define explicit Android backup/data-extraction rules and review what app data may be backed up.
3. Use a dedicated release signing key with a documented offline backup; never commit the key or passwords.
4. Rebuild and verify the release APK's manifest, certificate fingerprint, permissions, package identity, and artifact checksum.
5. Compare the exact antivirus detection label against the release artifact before drawing a conclusion.

This audit does not change the installed APK on the owner's device and does not certify it as malware-free. The current artifact remains a **debug/test APK**, not a production release.

### Progress and indicator accounting

- No Stage 1 or overall project percentage is awarded for this static audit.
- Stage 1 remains **30/40 = 75.00% provisional**; the ten zero-cost-constrained external acceptance gates remain open until their actual operational evidence exists.
- Overall project progress remains the historical **20.9%**; no new weighted calculation is asserted.
- Indicator acceptance is unchanged. The full current matrix, calculation definitions, test evidence, user-visible gaps, SIMULATED Footprint restrictions, and owner-reference prerequisites remain in `docs/INDICATOR_DATA_ARCHITECTURE.md`. No indicator receives credit from APK signing or antivirus analysis.
- No application runtime source, dependency, production credential, provider setting, paid service, or `main` branch was changed by this documentation record.


## Stage 1 blocker audit — ten external gates (2026-11-13)

A criterion-by-criterion review of `docs/STAGE_1_ACCEPTANCE_MATRIX.md` confirms that the remaining ten open criteria are **8, 20, 25, 30, 31, 34, 35, 36, 38, and 39**. They are not ten missing unit tests; each requires reproducible evidence from an actual owner-controlled operational environment.

| Criterion | Required operational evidence | Current blocker |
|---:|---|---|
| 8 | Host-side secret injection and leakage review | No production host configuration inspected |
| 20 | Real Firebase sign-in, expiry/revocation, entitlement, browser and Android flows | No authorized real-project E2E on a verified no-billing configuration |
| 25 | Self-hosted Redis TLS/ACL/private binding/persistence/failure test | No operational Redis host tested |
| 30 | Production-like backup restore with application records | Prior SQLite helper/isolated smoke evidence is not a complete production-like drill |
| 31 | Encrypted off-host backup, separate key custody, recovery and retention test | Termux Google Play package/keyring mismatch blocks the required `cryptography>=50,<51` dependency on-device; no verified second-device recovery drill |
| 34 | Host persistent-volume ownership, restart and disk-pressure test | No operational host volume inspected |
| 35 | HTTPS backend deployment and secret injection | No existing owner-controlled deployment endpoint verified |
| 36 | Browser and Android WSS through a reverse proxy | Depends on the unverified host/proxy deployment |
| 38 | Protected metrics/logs, bounded retention and dashboard | No self-hosted operational monitoring instance verified |
| 39 | Observed alert, acknowledgement, escalation and recovery exercise | No operational alert path demonstrated |

### Constraint resolution

- ZERO MONEY remains mandatory. Do not create paid/trial infrastructure or enable billing to force completion.
- Do not substitute local CI for production deployment evidence, or weaken authentication, TLS, backup encryption, or monitoring controls.
- The Termux blocker remains safely contained: keep the original working repository source; do not bypass APT signature checks, install the incompatible 48.0.1 package, lower the backend dependency, or change the AES-GCM/PBKDF2 design.
- This audit does not close any of the ten gates and awards no progress percentage. Stage 1 remains **30/40 = 75.00% provisional**; overall project progress remains the historical **20.9%**, not a new weighted calculation.

### Indicator progress

No indicator code or acceptance evidence changed in this audit. The complete indicator matrix, formulas, warm-up/index alignment, test evidence, UI acceptance gaps, Footprint SIMULATED-only boundary, and Heatmap/Liquidation Maps owner-reference gates remain in `docs/INDICATOR_DATA_ARCHITECTURE.md`. No indicator progress is awarded for Stage 1 blocker analysis.


## Owner-confirmed one-phone constraint — Stage 1 execution adjustment (2026-11-13)

The owner has one Infinix GT20 (Android 15) and no second phone, PC, or laptop. This was already stated; do not ask again. All execution plans must be phone-only and ZERO COST.

The ten external gates remain 8, 20, 25, 30, 31, 34, 35, 36, 38, and 39. Their revised phone-only feasibility is documented in docs/STAGE_1_ZERO_COST_GATE_PLAN.md and the matching acceptance-matrix addendum.

**Immediate attainable target:** criterion 30's same-device SQLite restore-to-fresh-path drill. The project already has:
- A standard-library SQLite Online Backup API helper with integrity checking, owner-only POSIX permissions, file fsync, atomic replacement, and parent-directory fsync.
- Device smoke evidence of SQLite integrity ok and a restored/read-back value.
- CI coverage that creates a consistent backup, encrypts/decrypts it, restores it, and verifies application-like instruments and bars records.

The remaining evidence gap is a consolidated owner-device restore report that verifies representative application records on the phone. This can be advanced without the cryptography package by testing the unencrypted SQLite restore path separately; it does not close criterion 31 or prove off-host disaster recovery.

**Hard limit:** criterion 31 cannot be accepted as encrypted off-host recovery with one device and no verified external destination. The Termux Play Store package/keyring mismatch continues to block the required cryptography>=50,<51 import on-device. Do not bypass signatures, lower the dependency, or weaken AES-GCM/PBKDF2.

The other local/CI subtests may advance, but they do not replace actual production host, public HTTPS/WSS, mounted volume, independent monitoring, or external alert/operator evidence. Do not change the 40-item production acceptance definition to force 100%.

Progress remains **30/40 = 75.00% provisional** and overall remains the historical **20.9%**; this constraint analysis awards no progress. Full indicator status remains in docs/INDICATOR_DATA_ARCHITECTURE.md and is unchanged: five calculation foundations tested but visible controls/rendering incomplete; shared hook UI incomplete; Footprint SIMULATED-only with visual reference/blueprint gate; Heatmap and Liquidation Maps unimplemented.


## Criterion 8 — repository-side secret leakage controls (2026-11-13)

Working branch: \`phase-2/market-data-foundation\`  
Implementation HEAD at this checkpoint: \`733663c73669c10b695e6b455794d2f8f1d2c3b8\`

### Changes recorded

- Extended \`scripts/check-frontend-bundle-secrets.mjs\` to inspect JavaScript, JSX, TypeScript, and TSX files as well as generated bundle formats.
- Added a CI scan of \`src/\` before the production frontend build. The existing post-build scan of \`dist/\` remains in place.
- Added a TSX regression fixture for a high-confidence GitHub token pattern. Findings contain only a relative path and pattern category; matched credential text is never returned.
- Extended backend settings representation tests to cover both \`repr()\` and \`str()\` for WebSocket token, provider key, Firebase project field, Redis URL/password, and session-calendar hash fields.
- Updated \`docs/SECURITY_CONFIGURATION.md\` to distinguish automated source/bundle checks from the remaining operational checks.

### CI evidence status

- Previous baseline commit \`4d1a3c5a79f02e248bd54afb1acbe80e92815ca5\` passed Automated Tests run [#43447996526](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43447996526) and CodeQL run [#43447996417](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43447996417).
- New exact-HEAD Automated Tests run [#43449331315](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43449331315) and CodeQL run [#43449331425](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43449331425) were in progress when this record was prepared. Do not treat their results as passed until the final conclusion is checked.

### Explicitly still open

- No owner-controlled production host or runtime secret-injection mechanism has been inspected.
- No runtime production logs/build-host logs have been reviewed from a real deployment.
- GitHub secret-scanning/push-protection settings, alert inventory, and full reachable repository-history scan have not been independently verified.
- The regex scanner covers selected high-confidence patterns only; it cannot prove absence of every credential format or obfuscated secret.
- CI and settings-representation tests do not prove that production secrets are injected securely or never logged by a host/runtime.

**Criterion 8 remains open / external verification required.** This work strengthens repository-side defense in depth only. It does not close Stage 1 criterion 8 or award Stage 1/overall project progress. Keep Stage 1 at **30/40 = 75.00% provisional** and overall progress at the historical **20.9%**; no fresh weighted percentage is calculated.


### Criterion 8 — exact implementation CI result (2026-11-13 correction)

The implementation commit \`733663c73669c10b695e6b455794d2f8f1d2c3b8\` was re-run after an earlier concurrency cancellation. The final attempt completed successfully:

- Automated Tests & Build [run #43449331315, attempt 2](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43449331315): **success**.
- CodeQL [run #43449331425](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43449331425): **success** for JavaScript/TypeScript and Python.
- Frontend source scan: **74 files checked**, passed before bundling.
- Production bundle scan: **3 files checked**, passed after bundling.
- Frontend scanner regression tests and Android host preflight tests passed.
- Backend suite: **780 passed in 24.40s**, including the expanded sensitive-settings representation test.
- Frontend build, dependency audits, synthetic SQLite outbox benchmark, backend container build, Redis/persistent-volume smoke test, and HIGH/CRITICAL container vulnerability scan all passed.

The CI run was executed against the exact implementation/test/workflow commit above. Later commits in the same branch only appended acceptance/progress/indicator documentation; they did not alter the tested application or scanner source.

**Acceptance boundary unchanged:** green CI and CodeQL establish repository-side checks only. They do not verify production host secret injection, runtime/build logs from a deployed host, GitHub secret-scanning settings/alert inventory, or the full reachable Git history. Criterion 8 therefore remains **open / external verification required**. No Stage 1 or overall progress credit is awarded.


### CI build-output / workflow-log spot audit — 2026-11-13

After successful CI attempt 2, the complete available workflow-job log for job \`131968105353\` (308,410 characters) was checked for high-confidence private-key PEM, AWS access-key, GitHub token, Stripe live-secret, credential-bearing Redis URL, and service-account private-key patterns. **Zero matches** were found. This is a bounded audit of this CI job's output only; it is not a scan of deployed runtime logs or every possible secret format.


## Criterion 8 — full reachable Git history audit (2026-11-13)

Implementation/workflow commit: `efdf9a9ecfa68647586cd89f819e76469e11d3df`

- CI now checks out full Git history (`fetch-depth: 0`) and runs the standalone Gitleaks CLI against all fetched refs using `--log-opts="--all"`.
- Gitleaks version: `8.30.1`; the Linux x64 release archive is SHA-256 verified before execution.
- A narrowly scoped Gitleaks allowlist excludes only the exact synthetic GitHub-token fixture in `scripts/check-frontend-bundle-secrets.node-test.mjs`; it does not exclude the whole file, directory, or commit.
- Dedicated full-history audit [run #43451610210](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610210): **1,133 commits scanned**, approximately **2.57 MB**, result **no leaks found**.
- Integrated CI [run #43451610297](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610297): **success** on the implementation/workflow commit; the full-history scan, frontend scans, backend tests, dependency audits, container build, persistent-volume/Redis smoke test, and container vulnerability scan all passed.
- CodeQL [run #43451610192](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43451610192): **success** on the same commit.

### Remaining Criterion 8 acceptance gates

- No owner-controlled production host has been inspected; runtime secret injection remains unverified.
- Production runtime/build-host logs have not been reviewed.
- GitHub's native secret-scanning/push-protection settings and alert inventory remain unverified.
- The scan covers reachable Git refs fetched by CI; it cannot establish the state of unreachable Git objects, external clones, or secrets previously rotated outside this repository.
- The automated regex/source scans are defense-in-depth, not proof that every possible credential format is absent.

**Criterion 8 remains open / external verification required.** No Stage 1 or overall project progress credit is awarded by the repository-side scan.

Stage 1 remains **30/40 = 75.00% provisional**. Overall project progress remains **20.9% historical**.

## Exact branch-head checkpoint — 2026-11-14

- Working branch: `phase-2/market-data-foundation`
- Indicator documentation commit: `b1823004006aa58c332589563fa85c14bd7004ac`
- Indicator architecture record: `docs/INDICATOR_DATA_ARCHITECTURE.md` now contains the complete calculation foundation/acceptance ledger for SMA 20, EMA 20, Wilder RSI 14, MACD 12/26/9, Bollinger Bands 20/2, shared indicator hook, simulated Footprint, Heatmap and Liquidation Maps. It also records warm-up indices, data-source restrictions, visual acceptance requirements and the owner-reference/blueprint gate.
- Automated Tests & Build [run #43537645757](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43537645757): **success** on the exact documentation commit. Frontend: **26 test files / 211 tests passed**. Backend: **795 tests passed in 27.85s**.
- The same exact-HEAD run completed frontend source/bundle secret scans, frontend production build, Android host preflight, backend dependency audit, synthetic SQLite outbox benchmark, backend container build, isolated Redis + persistent-volume smoke test, and HIGH/CRITICAL Trivy image scan. Trivy reported **0 HIGH/CRITICAL findings** for the scanned image.
- CodeQL [run #43537645698](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43537645698): **success** for JavaScript/TypeScript and Python.
- Full reachable Git-history Gitleaks [run #43537645629](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43537645629): **success**; the job log explicitly reports `no leaks found`.
- The 795-test backend run includes the full Digest Authorization redaction regression. The frontend suite includes the indicator calculation and simulated Footprint regression tests. No indicator UI, live provider feed, or owner-device indicator rendering was introduced by these documentation/security changes.

### Acceptance and progress accounting

- Stage 1 remains **30/40 = 75.00% provisional**; external production/operational gates **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** remain open.
- Overall progress remains the **20.9% owner-confirmed historical checkpoint**, not a freshly recalculated weighted result. The proposed milestone ledger still requires reproducible scoring and owner review.
- No progress credit is awarded for documentation-only changes, green CI by itself, test-count growth, or security scans alone.
- Criterion 8 remains **open / external verification required**: production host secret injection, deployed runtime/build logs, and GitHub native secret-scanning/push-protection settings and alert inventory have not been independently verified.
- Criteria 30/31 remain distinct: CI and previous Android SQLite smoke evidence do not replace a consolidated owner-device application restore report (30), and do not establish encrypted off-host backup/key recovery (31).
- ZERO COST and one-phone/no-PC constraints remain binding. No Termux package/keyring workaround, billing activation, paid infrastructure, or extra hardware is authorized by this checkpoint.

## Criterion 25 repository-side Redis ACL hardening — 2026-11-14

- Working branch: `phase-2/market-data-foundation`
- Exact tested commit: `ed62578eafad89b0d27ec233c06e5503c9f00123`
- Production settings now fail closed unless `REDIS_URL` uses `rediss://` and contains both a non-empty ACL username and password. Development/test environments retain their existing local configuration flexibility.
- Redis TLS client configuration explicitly requires CA-chain validation and hostname verification. Redis URL credentials remain excluded from Settings `repr()` and `str()`.
- Added regression coverage for missing ACL username, missing ACL password, and missing both credentials. The exact tested run confirms all three rejection cases pass.
- Automated Tests & Build [run #43538598583](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43538598583): **success**. Frontend: **26 test files / 211 tests passed**. Backend: **798 tests passed in 26.48s**.
- CodeQL [run #43538598765](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43538598765): **success** for Python and JavaScript/TypeScript.
- Full reachable Git-history Gitleaks [run #43538598582](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43538598582): **success**; **1,150 commits / ~2.59 MB scanned**, with `no leaks found`.
- Trivy HIGH/CRITICAL scan in the same automated run reported **0 findings** for the backend CI image. The isolated Redis + persistent-volume container smoke test also passed.

### Criterion 25 acceptance boundary

This closes the missing **repository configuration guard** for production Redis ACL credentials; it does **not** close criterion 25. The actual production Redis host, private-interface binding, firewall restriction, least-privilege ACL permissions, persistence configuration, restart/recovery, failover, and production TLS endpoint have not been independently observed. Keep criterion 25 **OPEN / EXTERNAL VERIFICATION REQUIRED**.

### Progress accounting

- Stage 1 remains **30/40 = 75.00% provisional**; the ten external gates remain open.
- Overall project progress remains **20.9% historical**; no percentage is awarded for configuration hardening, tests, CI, or documentation alone.
- No paid Redis, hosting, billing activation, cloud trial, extra hardware, or Termux trust bypass was introduced.



## Exact branch-head verification — Redis ACL smoke-test correction — 2026-11-14

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `290dd2a812ef9068fce82b9dd78bbfdb2d990d1e`
- Automated Tests & Build [run #43542532632](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43542532632): **success**.
- Frontend: **26 test files / 211 tests passed**. Frontend dependency audit, source/bundle secret scans, production build, scanner regression tests, and Android host preflight passed.
- Backend: **803 tests passed in 19.85s**. The previously failing synthetic SQLite outbox benchmark concurrency test passed on this exact commit.
- Bounded synthetic outbox benchmark: **1,000 bars inserted and 1,000 events replayed**; two concurrent in-process reader threads each replayed 1,000 events. Report explicitly limits its scope: this is not a provider/WebSocket/reconnect-storm/production-host benchmark and is not a multi-process test.
- Backend dependency audit reported no known vulnerabilities.
- Redis ACL + persistent-volume container smoke test: **success** on this exact commit. The workflow now uses `redis-cli -e` for authentication-denial assertions and generates a random CI-only ACL password at runtime.
- CodeQL [run #43542532635](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43542532635): **success** for JavaScript/TypeScript and Python.
- Full reachable Git-history Gitleaks [run #43542532618](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43542532618): **success**; **1,158 commits / ~2.60 MB scanned**, with `no leaks found`.
- Container image vulnerability scan and report export completed successfully in the automated workflow. This checkpoint does not claim a zero-finding count unless the report is separately inspected.
- The run validates repository/CI behavior only. It does not establish production Redis hosting, production secrets, production volume, external backup, HTTPS/WSS, external monitoring, or operator alert delivery.

### Acceptance and progress accounting

- The ten external acceptance gates **8, 20, 25, 30, 31, 34, 35, 36, 38, 39 remain OPEN / EXTERNAL VERIFICATION REQUIRED**. This CI run improves repository evidence for gates 8, 25, 30 and 34 but does not substitute for owner-host/device/production evidence.
- Stage 1 remains **30/40 = 75.00% provisional**. Overall progress remains **20.9% owner-confirmed historical checkpoint**; neither percentage is recalculated or increased by this CI run.
- ZERO COST, no paid services, no billing activation, no new hardware, no weakening of TLS/ACL/security, and no Termux trust bypass remain binding.
- No user action or shell command is required for this repository CI result.
## Stage 1 project progress tick meter — owner clarification (2026-11-14)

The owner clarified that the requested “tick” value refers to the **project progress indicator**, not to technical indicators rendered inside the DEZZTA CHART application. This section defines a more granular, auditable display for Stage 1 only. It does not add or change any in-app chart feature.

### Fixed scale and formula

- Stage 1 contains 40 acceptance criteria.
- Each criterion is represented by exactly 10 progress ticks.
- Total Stage 1 scale: **400 ticks**.
- One tick represents 0.25 percentage points of Stage 1 completion.
- One fully accepted criterion contributes 10 ticks (2.5 percentage points of Stage 1).
- Formula: Stage 1 ticks = accepted criteria × 10; Stage 1 percentage = earned ticks ÷ 400 × 100.
- A criterion earns its 10 ticks only when its own acceptance condition and required evidence are satisfied. No fractional ticks are awarded merely for partial code, documentation, a passing unrelated CI job, or work-in-progress.
- If a criterion is split into smaller evidence checks in a future revision, those checks must be explicitly listed and owner-reviewed before fractional ticks are used. Do not infer sub-ticks.

### Current Stage 1 tick snapshot

| Measure | Value |
|---|---:|
| Accepted/provisionally implemented checklist criteria | 30 / 40 |
| Earned Stage 1 ticks | **300 / 400** |
| Outstanding external criteria | 10 / 40 |
| Outstanding Stage 1 ticks | **100 / 400** |
| Stage 1 completion | **75% (provisional)** |
| Production acceptance | **Not accepted** |

The ten outstanding criteria are **8, 20, 25, 30, 31, 34, 35, 36, 38, and 39**. Each currently contributes 0/10 ticks because its required external evidence has not been demonstrated. The other 30 criteria account for the provisional 300/400 checklist ticks; this does not mean Stage 1 is production-ready.

### Counting safeguards

1. The tick meter is a finer display of the existing 30/40 Stage 1 checklist; it does not create additional acceptance criteria or inflate the score.
2. Ten ticks per criterion are a display scale, **not ten assumed sub-tasks**. A criterion is either accepted for 10 ticks or remains at 0 until its acceptance boundary is met.
3. Repository-side remediation can improve evidence for an external criterion but cannot earn its ticks until the external acceptance requirement is proven.
4. CI success, documentation changes, commit count, APK size, or a local smoke test never automatically increase Stage 1 ticks.
5. A tick update must identify the changed criterion, exact evidence, tested commit, and calculation. Preserve previous snapshots rather than silently rewriting history.
6. Stage 1 ticks must never be converted into the overall project percentage. The proposed weighted project milestone ledger remains unapproved/unscored; 20.9% remains a historical owner-confirmed conversational checkpoint, not a newly recalculated overall score.

### Relationship to technical indicator progress

The Stage 1 tick meter is a **project-management progress display only**. It is not an SMA/EMA/RSI/MACD/Bollinger/Footprint/Heatmap/Liquidation Maps value, data tick, price tick, market-data update, or in-app indicator feature. The detailed technical indicator acceptance matrix remains separately maintained in docs/INDICATOR_DATA_ARCHITECTURE.md and is not awarded completion credit by this project tick scale.

### Current audit reference

- Working branch: phase-2/market-data-foundation.
- Baseline code checkpoint for this tick-accounting clarification: fa99fb7f4af1cfebfdc983124ddf7bc6ae3234b9.
- Exact-head follow-ups on commits `5a5f12dd33b1409f3072b0b396a82b273d456b5e` and `6ec37c2b75c017832c636aad6adb737469042cb5` are fully green: Automated Tests & Build, CodeQL, and Gitleaks all completed successfully. See the verified 2026-11-14 audit sections below.

## Exact branch-head CI verification — 2026-11-14

- Branch: `phase-2/market-data-foundation`
- Exact HEAD: `aa5d4ef70b234ae75ceb07909a61609e512211cb`
- Automated Tests & Build: [run #43543969282](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43543969282) — **success**.
- Frontend: 26 test files passed; build and production-bundle secret scan passed.
- Backend: **803 tests passed in 33.19s**.
- Backend dependency audit: **no known vulnerabilities found**.
- Gitleaks reachable-history scan: **no leaks found**.
- Redis ACL correction verified: the scoped ACL user now has the required `SELECT` permission for configured database 15. Smoke test confirms unauthenticated, wrong-password, and unrelated `SET` access are rejected; backend health, non-root runtime identity, persistent-volume ownership, SQLite integrity/restart persistence, and HTTP rate-limit rejection passed.
- CodeQL [run #43543969220](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43543969220) — **success**.
- Gitleaks [run #43543969222](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43543969222) — **success**.
- The earlier Trivy report was superseded by the inspected latest-HEAD scan documented below; do not infer findings for the earlier artifact from the later scan.
- This is repository/CI evidence only. It does not close any of the ten external production gates, and does not establish a production host, managed Redis failover, public HTTPS/WSS, real Firebase project flow, off-host encrypted backup, external monitoring, or alert delivery.
- Stage 1 accounting remains **30/40 criteria = 300/400 ticks = 75% provisional**; the ten external gates **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** remain open. No progress ticks are awarded from this CI pass alone.


## Exact latest-HEAD verification — 2026-11-14

- Branch: `phase-2/market-data-foundation`
- Exact tested commit: `5a5f12dd33b1409f3072b0b396a82b273d456b5e`
- Automated Tests & Build: [run #43544575936](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43544575936) — **success**.
- CodeQL Python and JavaScript/TypeScript: [run #43544576006](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43544576006) — **success**.
- Full reachable Git-history Gitleaks: [run #43544575920](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43544575920) — **success**, 1,166 commits / approximately 2.62 MB scanned, no leaks found.
- Frontend: 26 test files passed; dependency audit, source credential scan, production build, and production-bundle credential scan passed.
- Backend regression suite: **803 passed in 17.32s**.
- Backend dependency audit: **no known vulnerabilities found**.
- Synthetic SQLite outbox benchmark: 1,000 bars inserted and 1,000 events replayed; two in-process reader threads each replayed 1,000 events. This is a bounded, single-process synthetic benchmark, not a provider/WebSocket/reconnect-storm, multi-process, or production-host benchmark.
- Redis/container smoke test: **passed**. The scoped ACL user has the required `SELECT` permission for configured Redis database 15; unauthenticated, wrong-password, and unrelated `SET` access were rejected. Backend health, non-root UID/GID 10001, mounted-volume and SQLite ownership, SQLite integrity, restart persistence, and HTTP rate-limit rejection passed.
- Trivy report artifact: [container-vulnerability-reports](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43544575936/artifacts/14093542877). The downloaded JSON report for image digest `sha256:b398511affbe93b1a0cdd59daf9429ddd9bcf9b0e1fb973c5479f166c9069526` reports **0 OS-package vulnerabilities, 0 Python-package vulnerabilities, 0 secrets, and 0 misconfigurations** in the scanned image.
- These results are CI/repository evidence. They do not prove production deployment, a managed Redis service, live Firebase, public HTTPS/WSS, off-host encrypted backup, independent monitoring, or external alert delivery.
- Stage 1 accounting remains **30/40 criteria = 300/400 ticks = 75% provisional**. External criteria **8, 20, 25, 30, 31, 34, 35, 36, 38, 39** remain open. No ticks are awarded from CI/documentation success alone.


## Latest documentation-head validation — 2026-11-14

- Exact tested documentation HEAD: `6ec37c2b75c017832c636aad6adb737469042cb5`.
- Automated Tests & Build [run #43550752630](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43550752630): **success**.
- CodeQL [run #43550752411](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43550752411): **success**.
- Gitleaks [run #43550752447](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43550752447): **success**, 1,167 commits / approximately 2.63 MB scanned, no leaks found.
- Frontend: 26 test files passed; dependency audit, source scan, build, and production-bundle credential scan passed.
- Backend: **803 tests passed in 22.79s**; backend dependency audit reported no known vulnerabilities.
- Synthetic SQLite outbox benchmark: 1,000 synthetic bars inserted and 1,000 events replayed; two same-process reader threads each replayed 1,000 events. Not a provider/WebSocket, reconnect-storm, multi-process, or production-host benchmark.
- Redis/container smoke test passed: ACL authentication and scoped command rejection, health, non-root UID/GID 10001, mounted-volume and SQLite ownership, SQLite integrity, restart persistence, and HTTP rate-limit rejection.
- Latest Trivy report [artifact](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43550752630/artifacts/14096650758), for image digest `sha256:17579dc8eb2f5fc1677af5ca576b0420e7f1dd810dccd1391dc9196c8613bbe9`, was downloaded and inspected: **0 OS-package vulnerabilities, 0 Python-package vulnerabilities, 0 secrets, and 0 misconfigurations** in that scanned image.
- This is repository/CI evidence only; it does not close any external production gate or prove production deployment.
- Stage 1 remains **300/400 ticks (75% provisional)**. The ten external gates remain open: **8, 20, 25, 30, 31, 34, 35, 36, 38, 39**.


## Exact branch-head CI checkpoint — 2026-11-14 — `00ac447`

- Active branch: `phase-2/market-data-foundation`; exact tested HEAD: `00ac44791345f714f1a9f4a0f8d3dce75d99075e`.
- Automated Tests & Build [#43565730118](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43565730118): **success**. Frontend unit tests/build and dependency audit; frontend source and production-bundle credential scans; backend tests; bounded synthetic SQLite outbox benchmark; backend dependency audit; backend container build; Redis + persistent-volume smoke test; Trivy image scan and report export/upload all completed successfully.
- CodeQL [#43565730126](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43565730126): **success** for Python and JavaScript/TypeScript.
- Gitleaks [#43565730158](https://github.com/deszztagd377-pixel/dezzta-chart/actions/runs/43565730158): **success** for reachable Git history.
- The benchmark concurrency regression is now verified passing on this exact HEAD. This supersedes earlier interim notes that described verification as pending.
- This is repository/CI evidence only. It does not prove production Firebase, managed Redis, host volume, encrypted offsite backup, deployed HTTPS/WSS, monitoring or external alert delivery.
- Stage 1 remains **300/400 ticks = 75% provisional**. Open external criteria remain **8, 20, 25, 30, 31, 34, 35, 36, 38 and 39**. No tick is awarded by CI alone.
- Indicator status is unchanged: five calculation foundations (SMA20, EMA20, Wilder RSI14, MACD12/26/9, Bollinger20,2) remain tested but user-facing chart controls/rendering are incomplete; shared-hook UI integration remains incomplete; Footprint remains SIMULATED and visually gated; Heatmap and Liquidation Maps remain unimplemented. See `docs/INDICATOR_DATA_ARCHITECTURE.md` for the full acceptance ledger.
- No runtime or indicator source was changed in this checkpoint. `main` was not modified.


## Ten-gate remediation cycle — 2026-11-14 — source HEAD `4ab3579`

- Re-audited the complete 40-point Stage 1 acceptance matrix and the zero-cost/single-phone gate plan rather than treating the ten open items as a single generic blocker.
- Criterion 30 gap identified: existing fresh-database restore test covered OHLCV/outbox but not every durable adapter wired to the same `INSTRUMENT_REGISTRY_DB_PATH`.
- Added a regression test to restore one shared application database and reopen/verify instrument registry, entitlements, alert zones, coverage intervals and gaps, OHLCV, outbox cursor/event identity, SQLite integrity, and post-restore write continuity. Exact-commit CI is pending.
- Criterion 8: latest reachable-history Gitleaks scan passed on source HEAD; owner-host secret injection and GitHub native settings remain external.
- Criterion 25: repository TLS/ACL/fail-closed protections and CI Redis smoke tests are present; owner-host network/persistence/restart proof remains external.
- Criteria 20, 31, 34, 35, 36, 38 and 39 remain constrained by the verified single-phone/no-PC/no-second-device and ZERO MONEY conditions. No paid account, trial, host, storage, domain, notification provider, or hardware was introduced.
- No Stage 1 tick change: **300/400 = 75% provisional**; all ten criteria remain open pending their complete acceptance evidence.


## Criterion 20 source audit correction — 2026-11-14

- Corrected stale project notes: Firebase client integration is already mounted in `src/main.tsx`; email registration/sign-in, Google redirect, ID-token observer and token retrieval are implemented in `src/auth/AuthProvider.tsx`.
- The authenticated WebSocket supervisor requests a fresh token on each reconnect. Backend Firebase Admin verification requests revocation checking; API tests cover entitlement denial/revocation, token revalidation, identity drift and reconnect/resnapshot paths.
- Owner context records an existing registered Firebase Web App, Spark/no-billing choice, and enabled Google Sign-In + Email/Password methods. This is not a substitute for checking the live billing state or a real deployed end-to-end run.
- Criterion 20 remains OPEN until the actual project/runtime configuration, backend Admin credential injection, real sign-in, expired/revoked-token behavior, entitlement denial, and browser/Android WSS flows are exercised. No billing upgrade.
- Criterion 30 test fixture correction: CI run #43566514902 caught an invalid `OhlcvBar.series_type="instrument"`; the accepted contract values are `contract` and `continuous`. The fixture is corrected to `contract` in the next commit. The other 803 backend tests passed on the failed attempt; this is not a passing CI result.
