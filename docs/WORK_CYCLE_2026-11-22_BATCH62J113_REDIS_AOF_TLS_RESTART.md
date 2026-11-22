# Work cycle — Redis AOF persistence across TLS restart (22 November 2026)

- Branch: `phase-2/market-data-foundation`; parent HEAD: `5b165e5efbcf1fe2ff32592161f4cbc660aedee5`.
- Scope: strengthen the isolated CI Redis TLS fixture; no production Redis configuration or application runtime changes.
- The fixture now mounts a dedicated ephemeral Docker volume at `/data`, enables Redis AOF with `appendfsync always`, and removes the volume during CI cleanup.
- After the TLS/CA/hostname/plaintext integration suite, CI writes a canary under the permitted ACL keyspace, restarts the actual Redis container, reconnects using the trusted CA and ACL identity, and verifies the canary value survived.
- This is a repository-level restart/persistence integration test only. It does not prove OCI block-volume durability, host reboot recovery, encrypted off-host backup, production failover, or public WSS.
- Test-only password and CA remain ephemeral; no production secrets are added. Redis remains TLS-only and no public Redis port is exposed.
- Exact-head CI is pending. Do not mark the batch accepted until Automated Tests, CodeQL, and Full Git History Secret Audit all complete successfully.
- ZERO COST; no cloud resource, paid service, deployment, Termux/device operation, or `main` modification.
