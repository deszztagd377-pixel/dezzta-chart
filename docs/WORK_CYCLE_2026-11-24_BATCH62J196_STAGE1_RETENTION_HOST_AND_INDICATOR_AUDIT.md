# Work cycle — 24 November 2026 — Batch 62J-196: Stage 1 retention, host, and indicator integration audit

**Branch:** `phase-2/market-data-foundation`  
**Audited starting HEAD:** `9f9260efe674886bf2232b896a726461b51614e5`  
**Scope:** read-only source/test/roadmap audit plus this report. No runtime code was changed.  
**ZERO COST:** preserved. No paid host, provider, Redis service, subscription, domain, or publication was added.  
**Protected scope:** `main` untouched.

## 1. Executive disposition

This batch closes an evidence gap, not a runtime feature. It deliberately does not award Stage 1 progress for synthetic tests or documentation alone.

| Workstream | Finding | Status |
|---|---|---|
| WebSocket sequence/replay | Deterministic replay, snapshot watermark, reconnect cursor and resnapshot protections exist and are covered by repository tests | 🟩 Repository regression coverage |
| Redis ACL | Dedicated publisher/gateway roles are exercised against CI Redis; database switching and out-of-scope key/command access are denied | 🟩 CI integration evidence |
| Redis stream retention/trim | No project-owned retention janitor or `XTRIM` path was found in the audited publisher/config/replay path; neither ACL role is authorized to trim | 🟥 Not implemented / not accepted |
| Real host WSS | Client/server code and synthetic/local proofs exist; no authenticated public owner-host WSS acceptance evidence is attached to this checkpoint | 🟥 Open |
| Android lifecycle | Repository preflight and lifecycle code exist; real phone network handover/background/force-stop/reboot acceptance is absent | 🟥 Open |
| Indicator calculations | Five standard studies and shared hook have numerical/data-trust tests | 🟨 Foundation |
| Indicator chart integration | Candlestick chart still creates only its candlestick series; it does not bind the shared indicator hook | 🟥 Not integrated; correctly parked for Stage 4 |
| Footprint | Synthetic educational accumulator only; no accepted exchange-native bid/ask contract or renderer | 🟧 Prototype |
| Heatmap | No accepted depth/liquidity renderer | 🟥 Not implemented |
| Liquidation Maps | No accepted runtime/renderer or defensible data-provenance contract | 🟥 Not implemented |

## 2. Redis retention/trim — verified gap and safety decision

### Source evidence

- `backend/app/ohlcv_redis_config.py` defines publisher commands as `+ping`, `+xadd`, and `+xrange`.
- The gateway role has read/group/ack and lease operations, but no `XTRIM` permission.
- `backend/app/ohlcv_redis_publisher.py` appends deterministic global cursor IDs using `XADD` and performs exact-ID read-back after ambiguous append outcomes. The audited appender does not perform stream trimming.
- `backend/app/ohlcv_redis_replay.py` requires every global cursor in the requested interval to be contiguous. Missing/trimmed entries produce `resnapshot_required`; partial replay events are not returned as success.
- `backend/tests/test_ohlcv_redis_acl_integration.py` exercises the publisher/gateway ACL roles against the configured CI Redis service. This is real Redis ACL integration in CI, not a real production Redis retention drill.

### Engineering decision

Do not grant `XTRIM` to the publisher or gateway as a shortcut. A safe retention controller needs a separately scoped identity and a durable ordering contract. At minimum, design and test:

1. Retention policy inputs: maximum stream age/length, minimum retained cursor, and the authoritative source checkpoint.
2. A monotonic retention-floor update that is durably committed before the corresponding trim can become visible to replay consumers.
3. A race-safe trim boundary that cannot remove entries newer than the committed floor or leave the checkpoint claiming history that Redis no longer contains.
4. Restart/retry behavior for crashes between floor publication and trim, including idempotent retries.
5. Replay during concurrent retention advancement: old cursors must resnapshot; cursors at/above the committed floor must remain contiguous.
6. Real Redis integration tests for trim boundaries, crash/restart, concurrent replay, and ACL least privilege.
7. A dedicated retention ACL role limited to the exact stream key and only the required commands; no publisher/gateway credential reuse.

Until that contract is implemented and tested, the safe behavior is to retain more history than desired rather than trim unsafely. The replay layer's fail-closed behavior is a safety net, not a retention implementation.

## 3. WebSocket acceptance boundary

The repository regression suite covers deterministic protocol and lifecycle behavior, including:

- authenticated ticket protocol and strict URL construction;
- snapshot plus fixed watermark and cursor-contiguous replay;
- replay/live handoff and deduplication;
- server-directed resnapshot and stale resume-cursor clearing;
- malformed/non-monotonic cursor rejection;
- heartbeat, ticket renewal, close/failure cleanup and observer isolation;
- same-series subscriber isolation and queue saturation behavior.

These tests do not establish all production acceptance conditions. Remaining real-host evidence is:

- valid public HTTPS/WSS hostname and certificate chain;
- real Firebase identity/ticket issuance, expiry, renewal and revocation;
- authenticated browser connection to the deployed host;
- reconnect and replay after server instance replacement/restart;
- real shared Redis persistence/trim behavior under the exact least-privilege roles;
- cross-instance fan-out with more than one host instance;
- Android WebView certificate trust and mobile network handover.

Do not claim production WSS completion from a local test, a Vercel frontend preview, or a synthetic Worker proof.

## 4. Android lifecycle boundary

The current Android evidence is repository-side only. The APK workflow packages the frontend; it does not bundle or supervise the Python backend and Redis. The existing Termux package-signing/keyring blocker remains a hard stop for package-source changes.

No device acceptance is claimed for:

- offline → online transition and authenticated reconnect;
- background → foreground resnapshot;
- force-stop/relaunch recovery;
- process death/reboot recovery;
- Android WebView TLS hostname verification;
- sustained thermal/battery behavior while a stream is active.

No device command or package change is requested by this report. Do not bypass APT signature verification, weaken TLS, or substitute in-memory/plaintext Redis.

## 5. Complete indicator progress ledger

Calculation warm-up indices are zero-based source-candle indexes. Warm-up values remain null and must never be plotted as zero.

| Study | Formula/parameters | First valid output | Current status | Outstanding work |
|---|---|---:|---|---|
| SMA20 | Arithmetic mean of the latest 20 closes | 19 | 🟨 Foundation | Chart overlay, independent toggle, legend/latest value, identity clearing, render/performance acceptance |
| EMA20 | SMA-seeded EMA; multiplier \(2/(20+1)=2/21\) | 19 | 🟨 Foundation | Chart overlay, independent toggle, legend/latest value, identity clearing, render/performance acceptance |
| RSI14 Wilder | 14-change initial average, then Wilder-smoothed gain/loss recurrence | 14 | 🟨 Foundation | Dedicated 0–100 pane, 30/70 guides, toggle, legend/latest value, lifecycle/render acceptance |
| MACD12/26/9 | EMA12 − EMA26; EMA9 signal over MACD line; histogram = MACD − signal | MACD 25; signal/histogram 33 | 🟨 Foundation | Dedicated pane, two lines, histogram, zero guide, toggle, latest values, lifecycle/render acceptance |
| Bollinger20,2 | 20-close mean ± 2 population standard deviations | 19 | 🟨 Foundation | Upper/middle/lower overlays, toggle, latest values, identity clearing, render/performance acceptance |
| Shared Indicator Hook | `useMarketIndicators()`; one immutable, identity-bound backend OHLCV snapshot; cached calculations per snapshot | Per study warm-up | 🟨 Foundation | Bind to chart UI in Stage 4; verify stale clearing on every identity/timeframe transition; controls/legend/accessibility/performance |
| Footprint | Synthetic educational accumulator; not exchange-native bid/ask truth | N/A | 🟧 Prototype | Owner reference image(s), reviewed blueprint, verified bid/ask source contract, dedicated spaced cluster renderer and acceptance |
| Heatmap | No accepted depth/liquidity renderer | N/A | 🟥 Not implemented | Owner reference image(s), validated depth/liquidity contract, reviewed blueprint, renderer and acceptance |
| Liquidation Maps | No accepted runtime/renderer | N/A | 🟥 Not implemented | Defensible provenance/calculation contract, reviewed blueprint, renderer and acceptance |

### Verified calculation/test invariants

- SMA20, EMA20 and Bollinger20 first produce values at index 19.
- Wilder RSI14 first produces a value at index 14.
- MACD line first produces a value at index 25; signal and histogram first produce values at index 33.
- Calculation outputs preserve source-array length and candle-index alignment.
- Prefix-causality regression tests confirm that appending future candles does not rewrite prior outputs.
- Invalid/non-finite closes fail closed; extreme finite values have numerical stability regressions.
- The shared hook accepts non-empty backend `ready`/`degraded` snapshots and suppresses demo/error/loading/unavailable states.
- Immutable snapshot revisions recalculate results; same-snapshot panels share a frozen calculation result.
- No visible indicator controls, overlays, oscillator panes or chart-series binding are implemented yet.

### Indicator design gate

`docs/INDICATOR_UI_BLUEPRINT.md` remains **PARKED**. Its scope is Stage 4, not Stage 1. No indicator UI work is authorized by this batch. Footprint OFF must continue to preserve ordinary candlestick spacing; only explicit Footprint ON may use the dedicated spaced-candle/cluster layout. Footprint and Heatmap visuals remain blocked on the owner's reference image(s) and scoped blueprint review.

**Aggregate indicator percentage: NOT SCORED.** A weighted denominator and approved acceptance model do not exist. Calculation readiness must not be presented as complete user-facing indicators.

## 6. Stage map and evidence-based progress

The official roadmap contains six stages. The active official stage remains Stage 1; the branch name is not a stage transition.

| Official stage | Current accounting | Color/status |
|---|---:|---|
| Stage 1 — Foundation, Security & Data Integrity | 30/40 = 75% provisional | 🟨 Active; 10 criteria remain open |
| Stage 2 — Market Data Infrastructure | Not scored | ⬜ Not officially opened |
| Stage 3 — Chart Engine & Timeframe | Not scored | ⬜ Not officially opened |
| Stage 4 — Indicators & Analytics | Not scored | ⬜ Not officially opened |
| Stage 5 — Professional UI & Interactive Tools | Not scored | ⬜ Not officially opened |
| Stage 6 — Hardening, Validation & APK Release | Not scored | ⬜ Not officially opened |

**Gate 10:** 0/10 formally closed. The open criterion IDs remain 8, 20, 25, 30, 31, 34, 35, 36, 38 and 39. This report does not infer their exact criterion descriptions or award ticks.

**Overall project:** NOT SCORED. No approved weighted denominator exists. The Stage 1 75% is not the overall project percentage.  
**Significant verified progress:** replay cursor safety and CI regression coverage are green at repository level; real Redis retention, production WSS and physical Android acceptance remain red.  
**Delivery target:** 24 December 2026 (planning target, not guarantee).  
**Cost:** ZERO COST.

## 7. Multi-cycle execution order from this checkpoint

1. Define and implement the separate Redis retention-controller contract, including atomic floor/trim ordering and a dedicated least-privilege role. Add real Redis integration tests before enabling any trim.
2. Build a production-host WSS acceptance proof using only an already-available zero-cost plan. If the plan cannot provide durable shared state and the required runtime behavior at zero cost, record a no-go rather than silently introducing billing.
3. Reconcile cross-instance publisher/gateway lifecycle and restart behavior against the exact Redis retention contract.
4. Run Android acceptance only after a secure backend endpoint and certificate chain exist; keep the Termux package-signature blocker untouched.
5. Reconcile the ten open Stage 1 criteria against source, CI and owner-device evidence. Change 30/40 only when a specific criterion has all required evidence.
6. At Stage 4 entry, review and approve the parked indicator blueprint before chart UI integration. Do not start Footprint/Heatmap visuals without the required reference images.

## 8. Files inspected

- `backend/app/ohlcv_redis_config.py`
- `backend/app/ohlcv_redis_publisher.py`
- `backend/app/ohlcv_redis_replay.py`
- `backend/app/ohlcv_redis_gateway_runtime.py`
- `backend/tests/test_ohlcv_redis_acl_integration.py`
- `backend/tests/test_ohlcv_redis_replay.py`
- `src/indicators/indicatorCalculations.ts`
- `src/indicators/indicatorCalculations.test.ts`
- `src/indicators/useMarketIndicators.ts`
- `src/indicators/useMarketIndicators.test.ts`
- `src/components/CandlestickChart.tsx`
- `src/services/ohlcvWebSocketClient.ts`
- `docs/INDICATOR_UI_BLUEPRINT.md`
- `docs/ANDROID_BACKEND_HOST_AUDIT.md`

No source behavior, dependency, credential, deployment setting, provider setting, or owner device was modified.
