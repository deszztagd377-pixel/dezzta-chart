# Batch 62J-112 — TLS negative-test expectation correction

**Parent:** `59013f1d9a65e08aef6392f489aca3f3367da072`  
**Scope:** correct the integration test's plaintext-negative branch after real CI evidence.

## Evidence

The Redis 7 TLS-only container started successfully after the permission correction. The integration test then reported:

`ValueError: A custom Redis CA bundle requires a rediss:// URL.`

This is correct production configuration validation: a custom CA must never be accepted with a plaintext URL. The test had incorrectly expected a socket-level connection error even though the guard correctly stopped before connecting.

## Correction

The integration test now passes an empty CA for its network-level plaintext attempt. It must fail to connect because the fixture's Redis server has `--port 0` and only the TLS port enabled. Existing unit coverage continues to assert that supplying a custom CA with `redis://` is rejected immediately.

## Expected acceptance

- Valid CA + matching DNS SAN: successful TLS and guard operations.
- Wrong hostname: TLS verification rejection.
- Wrong CA: chain verification rejection.
- Plaintext URL without custom CA: connection failure against TLS-only listener.
- Plaintext URL with custom CA: configuration `ValueError` (covered by unit test).

No production runtime code changed. Exact-head CI must pass before acceptance. ZERO COST; no deployment, Termux, paid services, or `main` changes.
