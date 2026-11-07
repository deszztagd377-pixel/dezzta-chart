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
| CI reproducibility and deployment validation | Partial | CI runs frontend/backend tests and container build; dependency lockfile and deployed Android/web smoke verification remain open |

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
- Snapshot limit is constrained to 1–5,000 bars at the HTTP boundary, in addition to the configured server-side cap.
- Added parameterized API tests for oversized strings, invalid identifier ranges, oversized nanosecond strings, and excessive response limits.

This does not implement per-account/IP rate limiting, proxy-aware abuse controls, HTTP body limits, or WebSocket frame-size configuration. CI on the resulting HEAD must pass before these changes are treated as verified acceptance evidence.
