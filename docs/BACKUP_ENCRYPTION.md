# Encrypted backup artifacts

## Scope

`app.backup_encryption` provides authenticated file encryption for an existing
SQLite backup artifact. It does not upload files, manage keys, configure
retention, or prove that an owner-controlled host is recoverable.

Format version 1 uses:

- AES-256-GCM authenticated encryption;
- PBKDF2-HMAC-SHA256 with a random 16-byte salt and 600,000 iterations;
- a random 12-byte GCM nonce;
- authenticated versioned header data;
- 1 MiB streaming chunks;
- private temporary files and atomic publication;
- GCM authentication before a decrypted file is published.

A wrong passphrase or modified ciphertext fails authentication. The previous
destination is preserved and temporary plaintext is removed. On POSIX systems,
published encrypted and restored files are mode `0600`.

## Local use

Create a consistent SQLite snapshot first with
`app.sqlite_backup.create_consistent_sqlite_backup`. Then encrypt it. Run the
following from the `backend/` directory on the owner-controlled machine:

```python
from getpass import getpass
from app.backup_encryption import encrypt_backup_file, decrypt_backup_file

# Enter the passphrase interactively; do not put it in source or shell history.
key = getpass("Backup encryption passphrase: ").encode("utf-8")
encrypt_backup_file(
    "./data/market.sqlite3",
    "./backup/market.sqlite3.enc",
    key,
)

# On a restore exercise, enter the same separately stored passphrase.
restore_key = getpass("Backup decryption passphrase: ").encode("utf-8")
decrypt_backup_file(
    "./backup/market.sqlite3.enc",
    "./restore/market.sqlite3",
    restore_key,
)
```

Use a unique, high-entropy passphrase of at least 16 bytes; a randomly
generated 32-byte secret is recommended. Store the passphrase in a separate
owner-controlled offline location, not beside the backup, database, repository,
container image, or application logs. Losing it makes the encrypted backup
unrecoverable. Do not send it through chat or commit it to Git.

## Acceptance and limitations

Automated tests cover round-trip recovery, wrong-key rejection, ciphertext
tampering, invalid headers, temporary-file cleanup, destination preservation,
and owner-only POSIX permissions.

This implementation is repository-level encryption support, not proof of
production key management. Stage 1 point 31 remains externally unverified until
the owner demonstrates separate key storage, retention/access controls, and a
successful restore on the intended host using the documented recovery process.
Likewise, a local encrypted file is not an off-host backup until it is copied
to a separately controlled destination with no incremental cost and verified
there.

Do not enable a paid object store, KMS, backup service, or trial to complete
this criterion. If a secure no-cost off-host destination is unavailable, record
the limitation and retain local-only backup status rather than weakening
encryption or claiming disaster recovery.
