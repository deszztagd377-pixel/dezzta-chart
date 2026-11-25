# DEZZTA CHART — Work Cycle 66: concurrent provider-demand release regression

Date: 25 November 2026  
Branch: `phase-2/market-data-foundation`  
Parent HEAD: `b062bf9229ebf21a0b47b7a082b15461cf95be24`  
Scope: offline provider-demand concurrency regression tests  
Cost: ZERO COST  
`main`: untouched • Vercel deployment: deferred • Live provider: not enabled

## 1. Problem addressed

The provider-demand coordinator already serialized acquire/release transitions and had explicit concurrent-acquire coverage. The focused test suite did not yet directly prove that simultaneous release attempts cannot stop one upstream more than once, nor that simultaneous final releases by multiple owners leave no residual lease state.

## 2. Changes

Added two tests to `backend/tests/test_provider_demand.py`:

1. **32 duplicate releases for one lease**
   - All release calls execute concurrently against the same immutable lease.
   - Exactly one call must return `True`; the other 31 must return `False`.
   - The adapter must record exactly one start and exactly one stop.
   - Active lease, subscriber, pending-release and active-key counts must all return to zero.

2. **16 owners release one shared upstream concurrently**
   - Sixteen distinct owners acquire the same canonical upstream key.
   - All sixteen releases execute concurrently.
   - Every distinct lease must be released successfully.
   - The shared upstream must have exactly one start and one final stop.
   - No active adapter key, lease, subscriber or pending release may remain.

No runtime source was modified. These tests exercise the existing asyncio-lock transition serialization rather than introducing a second ownership mechanism.

## 3. Acceptance mathematics

For one lease released N=32 times concurrently:
- successful releases = 1;
- idempotent no-op releases = N-1 = 31;
- upstream starts = 1;
- upstream stops = 1;
- final active leases = 0.

For M=16 distinct owners sharing one key:
- successful owner releases = M = 16;
- upstream starts = 1;
- upstream stops = 1 (only the 0→1 and 1→0 boundary transitions);
- final subscriber count = 0;
- final active keys = 0.

These are lifecycle invariants, not market-data throughput or latency claims.

## 4. Safety boundary

The tests prove only the in-process offline adapter/coordinator behavior. They do not prove:
- provider SDK dynamic subscribe/unsubscribe;
- provider-side acknowledgement;
- cancellation-safe external side effects;
- durable cross-process ownership or restart recovery;
- Gate 25 owner-host receipt/high-water ACK;
- Gate 36 public WSS/TLS or Firebase/Android production acceptance.

No external network call, provider credential, paid feed, deployment or destructive Redis operation was added.

## 5. CI and indicator accounting

This source/test commit requires exact-HEAD verification by Automated Tests, CodeQL, OCI ARM64 readiness and full Git-history secret audit. The run IDs and final conclusions must be recorded only after the workflows finish.

No indicator formula, calculation hook, chart component, renderer, UI or indicator test changed. No indicator completion credit is awarded. The full twelve-row indicator ledger and numerical contracts remain in `docs/INDICATOR_PROGRESS_LEDGER.md`.

## 6. Next ordered work

1. Verify exact-HEAD CI and inspect every job result.
2. Continue cross-process provider-demand ownership audit without confusing Redis replica-consumer leases with market-provider ownership.
3. Keep real-provider wiring blocked until recurring-$0 entitlement/redistribution rights and a verified adapter capability contract exist.
4. Continue Gate 25 and Gate 36 evidence work in their existing order.
5. Preserve Stage 4 indicator gate and user-reference requirements.

Target delivery remains approximately 24 December 2026. ZERO COST maintained. No `main` update or Vercel deployment.
