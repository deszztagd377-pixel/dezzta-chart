# Gate 25 — Ed25519 Snapshot Authentication and Key Custody

**Batch:** 62J-213  
**Date:** 24 November 2026  
**Branch:** `phase-2/market-data-foundation`  
**Design:** owner-pinned Ed25519 public-key allow-list  
**Cost:** ZERO COST

## Trust model

- The authoritative source host owns one Ed25519 private key. It is stored in an owner-only PEM file (0600), outside the repository and container build context.
- The source signs a canonical payload after the snapshot content SHA-256 is computed.
- Every gateway receives only the matching public key through `OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON`.
- The signature binds source ID, generation ID, high-water cursor, retention floor, bar-retention policy, row count, snapshot format version, and canonical SHA-256 digest.
- A production gateway must have a non-empty valid trust allow-list. It rejects missing signatures, unknown key IDs, altered payloads, and invalid signatures before receipt commit and Redis client construction.
- The persisted immutable receipt stores the verified source identity, key ID, signature envelope, digest, replica ID, generation ID, cursor, retention floor, and bar-retention policy. Gateway startup re-verifies the persisted signature before creating Redis.

## Key provisioning

Run `backend/scripts/generate_snapshot_signing_key.py` on the authoritative source host with an explicit directory outside the repository. The script:
- generates an Ed25519 keypair using the already-installed `cryptography` dependency;
- writes the private PEM using exclusive creation and mode 0600;
- writes the public raw key as base64;
- derives a stable key ID from the public key fingerprint;
- refuses to overwrite existing output;
- never prints the private key.

Source-host configuration:
- `OHLCV_SNAPSHOT_SIGNING_KEY_FILE`
- `OHLCV_SNAPSHOT_SIGNING_KEY_ID`

The source snapshot callback calls `load_snapshot_signing_key_from_environment()` and passes the returned key and key ID to `SQLiteOhlcvStore.export_global_snapshot()`.

Gateway configuration:
- `OHLCV_SNAPSHOT_TRUSTED_KEYS_JSON`: JSON object mapping key IDs to base64 raw Ed25519 public keys.

No private key, generated keypair, production credential, or public deployment secret is stored in Git. CI tests use ephemeral in-memory keys only.

## Key rotation and revocation

1. Generate a new keypair on the authoritative source host.
2. Add the new public key to every gateway trust allow-list while retaining the old public key.
3. Confirm all required gateways have the new key.
4. Switch the source signer to the new key and install a newly generated signed snapshot.
5. Verify each gateway receipt reports the new key ID.
6. Remove the old key from active trust after all required gateways have converged; retain the old public key in owner-controlled audit storage for historical receipt verification.

If a private key is suspected compromised, remove its public key from active trust immediately and require a new snapshot signed by a replacement key. Do not silently re-sign an existing generation with different content or provenance.

## Compatibility and migration

- Existing content-only receipt rows are preserved and remain `CONTENT_ONLY_UNAUTHENTICATED`; migration does not fabricate signatures or authenticated source identity.
- Receipt schema migration is additive/rebuild-safe and preserves prior receipt fields and timestamps.
- Same source/replica/generation plus different digest, trust state, key ID, signature, retention floor, or retention policy is a conflict.
- Same identity and exact signed evidence is idempotent.
- Receipt UPDATE and DELETE remain prohibited.
- Snapshot rows, mutable checkpoint, and immutable receipt are committed or rolled back together.

## Remaining acceptance

The repository implementation can verify signatures and enforce production fail-closed behavior, but CI cannot provision the actual owner-host private key or prove its custody. Gate 25 remains OPEN until:
- source-host key is generated and protected outside Git/container artifacts;
- owner snapshot callback signs using the configured source key;
- every gateway has the correct public-key allow-list;
- real signed snapshot transfer succeeds and its persisted receipt is reverified after restart;
- multi-gateway receipt custody and high-water acknowledgements are accepted;
- Firebase E2E, owner-host WSS/TLS, Android lifecycle, and monitoring/recovery gates are separately accepted.

Redis `XTRIM`, `XDEL`, and consumer-group destruction remain blocked until all retention prerequisites are accepted. No Vercel deployment is performed by this work.
