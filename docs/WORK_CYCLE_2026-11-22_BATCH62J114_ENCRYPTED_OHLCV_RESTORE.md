# Work cycle — authenticated encrypted restore of real OHLCV/outbox (22 November 2026)

- Branch: `phase-2/market-data-foundation`; parent: `7939184360775ec80b14ce07cf3c7d62975b191a`.
- Scope: test-only integration of the existing SQLite Online Backup API, AES-256-GCM encrypted artifact, authenticated decryption, and fresh-path SQLite restore using the actual `SQLiteOhlcvStore`.
- The test creates a real OHLCV bar and durable replay-outbox event, snapshots the database, encrypts the snapshot, decrypts only after GCM authentication, validates and restores the SQLite file, then verifies exact Decimal values, outbox cursor/event ID and replay page.
- It also writes a second bar after recovery and checks the durable cursor advances monotonically from 1 to 2.
- Existing wrong-passphrase and ciphertext-tamper tests continue to verify that unauthenticated plaintext is not published.
- No production encryption or SQLite runtime behavior changes. The test uses only an ephemeral test passphrase.
- This is CI/repository evidence, not proof of an off-host backup destination, offline key custody, OCI volume durability, host recovery, or operator key-recovery drill.
- Exact-head Automated Tests, CodeQL and Full Git History Secret Audit must all pass before acceptance.
- ZERO COST; no deployment, cloud provisioning, paid service, production credential, Termux/device operation, or `main` modification.
