# DEZZTA CHART — Android / Termux readiness

Audit date: 2026-11-13  
Audited source branch: `phase-2/market-data-foundation`  
Source HEAD before this documentation checkpoint: `a3e920d6ab49967b073c40d5181d7033ee912d41`

## Executive status

**Termux support is not complete.** The repository currently contains a read-only Android host preflight and CI coverage for that script. This is an environment inventory, not an installation, runtime, deployment, or production-readiness certification.

The user's previously reported Termux environment showed OpenSSL 3.6.3 and a Python 3.13 environment where the backend encryption test module could not be collected because the `cryptography` package was unavailable. That result identifies an unresolved Python dependency/runtime compatibility gate; it does not establish that OpenSSL itself is broken.

## Corrected device evidence — 2026-11-13

The following later device results supersede the earlier incomplete preflight snapshot:

- Termux Python: **3.13.13**.
- Pytest: **9.2.0** was present in the latest reported device test session.
- SQLite backup-focused test suite: **15/15 passed**.
- Native SQLite backup/restore smoke: `INTEGRITY: ok`, `RESTORED_DATA: 6012.125`, `BACKUP_RESTORE_PASS`.
- Backup file permission check: `0o600`; backup exists and restored data check passed.
- `cryptography` remained unavailable to the Python interpreter in the reported preflight, and importing `app.backup_encryption` failed with `ModuleNotFoundError: No module named 'cryptography'`. Consequently, the encrypted-backup test module could not be collected. The successful SQLite-only tests do not test AES-GCM encryption.

### Verified Termux package integration path

The official `termux/termux-packages` repository's `packages/python-cryptography/build.sh` currently declares package version **50.0.2**, which satisfies this project's `cryptography>=50,<51` requirement. Its build recipe performs Termux-specific Rust target configuration, uses Termux's Python/OpenSSL paths, and adds the Termux Python shared library dependency to the Rust extension. This is materially different from a generic PyPI source build.

Therefore, the preferred compatibility path is the official Termux package-manager build of `python-cryptography`, not an unverified pip source compilation. This is a verified upstream packaging route, **not proof that version 50.0.2 is already available in the user's configured mirror or installed on the device**. After the package is present, the same Python interpreter used for the project must be able to import it. An isolated virtual environment will not automatically see a system package unless it is deliberately configured to expose system site-packages.



| Area | Evidence | Status |
|---|---|---|
| Android/Termux capability inventory | `scripts/android-host-preflight.sh` reports ABI, Android release, Termux markers, free storage, memory, command availability, OpenSSL headers/libraries, and selected Python module availability | Implemented; read-only |
| Preflight safety | Script explicitly installs nothing, starts no services, and avoids printing secrets/environment dumps | Implemented |
| Preflight automated test | `scripts/android-host-preflight.node-test.mjs` checks read-only behavior, no secret disclosure, and mocked Android/Termux metadata | Present; exact-HEAD CI step passed |
| Termux Python dependency readiness | Prior device run: Python 3.13 could not collect `test_backup_encryption.py` because `cryptography` was missing | Open |
| OpenSSL discovery | Prior device run reported OpenSSL 3.6.3; headers and linker flags were inspected | Partial; does not prove Python binding builds/imports |
| Backend runtime on Termux | No verified end-to-end backend startup, health check, SQLite persistence, Redis connection, or WebSocket session on the actual Android device | Not accepted |
| Restart and persistence | No verified Android process restart / persistent-data recovery drill | Not accepted |
| Network/TLS behavior | No verified real Android-device HTTPS/WSS and provider-independent backend smoke test | Not accepted |
| Production suitability | No production deployment, reliability, background-execution, or monitoring acceptance on Android | Not accepted |

## Important platform distinction

The backend container is based on `python:3.12-alpine3.24`; successful Docker CI is not evidence that the same backend runs natively in Termux. Termux uses Android/Bionic and a different package/build environment. A successful Linux CI build, Docker smoke test, or shell-script preflight cannot substitute for device-native validation.

The Python requirement currently includes `cryptography>=50,<51`. Compatibility must be demonstrated on the actual supported Termux Python version, including a successful import and execution of the backup-encryption tests. Do not lower or pin dependencies merely to silence an installation failure; first establish upstream wheel/source-build support and validate the security-sensitive encryption behavior.

## Acceptance gates before calling Termux complete

1. Record the actual supported Android release, ABI, Termux package source/version, Python version, OpenSSL version, and available compiler/build tools from the target device.
2. Resolve the `cryptography` dependency for the supported Termux Python version without weakening the declared security requirement or changing encryption semantics.
3. Run the backend test suite in the actual Termux environment, including backup encryption and SQLite persistence tests; capture exact pass/fail totals.
4. Start the backend natively on-device and verify health endpoint, graceful shutdown/restart, SQLite persistence, and configured Redis behavior (or explicitly document Redis as unavailable and the resulting feature limitations).
5. Verify frontend-to-backend connectivity and WebSocket behavior from the intended Android client/network path.
6. Verify Android background execution, process termination/restart recovery, storage permissions, and operational logging without exposing secrets.
7. Publish reproducible device test evidence and close each gate before declaring Termux support complete.

## Current decision

- **Preflight script:** implemented and its CI test passed on the audited source HEAD.
- **Native Termux backend:** not yet validated.
- **Termux Python cryptography dependency:** unresolved based on the last reported device test.
- **Termux support overall:** **INCOMPLETE / NOT ACCEPTED**.

No user device command is required for this documentation checkpoint. No package installation, production secret, paid provider, or production infrastructure was changed.

## Updated decision after native-device evidence

- SQLite backup/restore core on the user's Termux device: **15/15 focused tests passed**; native integrity/data/permission smoke passed.
- Python 3.13.13 and pytest 9.2.0 were available in the latest reported session.
- Encrypted backup remains blocked specifically by the missing `cryptography` import; encryption tests were not collected and must not be counted as passing.
- Upstream official Termux packaging now provides a concrete, version-compatible route: `python-cryptography` recipe version 50.0.2 satisfies `cryptography>=50,<51`. The device's configured repository availability and successful import remain to be confirmed.
- Next validation is narrowly scoped: confirm the package-manager-provided module is visible to the exact project interpreter, then run the encrypted-backup tests and verify AES-GCM round-trip, wrong-passphrase/tamper rejection, and private permissions on-device. No encryption fallback or weakened dependency range is accepted.
- Full native backend startup, Redis/WebSocket, client connectivity, and Android background/restart behavior remain open.


## Termux package-index observation — 2026-11-13 (latest device output)

The owner queried the configured Termux APT package metadata and reported:

- `pkg show python-cryptography` resolves to package version **48.0.1-1**.
- The project interpreter still reports `ModuleNotFoundError` for `cryptography`.
- The declared backend dependency is `cryptography>=50,<51`.
- Therefore the package version currently advertised by the configured repository is **not compatible with the declared project dependency**, and the package is not installed/visible to the interpreter.

This narrows the blocker: it is not an OpenSSL header/linker discovery issue and it is not a SQLite backup failure. The configured APT package index currently exposes an older package than the official Termux build recipe's 50.0.2 version.

### Corrective decision

- Do **not** install 48.0.1 as a workaround; it does not satisfy the declared `>=50,<51` dependency.
- Do **not** weaken `backend/requirements.txt`, change AES-GCM/PBKDF2 behavior, or substitute a different crypto implementation merely to make the import pass.
- First refresh the configured Termux package indexes and re-check the candidate version. If the refreshed configured mirror still exposes only 48.0.1, the mirror/repository source is stale relative to the current official Termux package recipe; resolve that repository mismatch before installing.
- The official Termux package recipe at `termux/termux-packages/packages/python-cryptography/build.sh` declares **50.0.2** and includes Termux-specific Rust/PyO3/Python shared-library integration. A generic PyPI source build is not treated as equivalent.
- After a compatible package is available, validate import using the exact interpreter/environment that runs the project, then run `backend/tests/test_backup_encryption.py`. Only a passing AES-GCM round-trip, wrong-passphrase rejection, ciphertext-tamper rejection, atomic-publication behavior, and private-permission checks close this dependency gate.

No source code, dependency constraint, encryption format, or device package was changed by this observation. Termux native backend support remains **INCOMPLETE / NOT ACCEPTED**.

## Confirmed repository-source mismatch — 2026-11-13 (after package-index refresh)

The owner ran `pkg update` successfully and then queried the package metadata again. The output still showed:

- Active APT source: `https://termux.net stable`.
- Package candidate: `python-cryptography 48.0.1-1`.
- APT reported all packages up to date.

This is stronger evidence than the earlier stale-index hypothesis: the configured source itself is the legacy `termux.net` endpoint, while the current official Termux package mirror documentation lists `https://packages.termux.dev/apt/termux-main stable main` as the primary Main repository. The same documentation recommends using `termux-change-repo` to select a current Main mirror. See:
- https://github.com/termux/termux-packages/wiki/Mirrors
- https://github.com/termux/termux-packages/wiki/Package-Management

### Next safe device action

Use the interactive `termux-change-repo` utility to change **Main repository only** from the legacy `termux.net` source to the current official primary host `packages.termux.dev` (or a mirror explicitly listed by the official Termux Mirrors page). Do not manually guess or paste an unverified mirror URL. After selecting the source, refresh metadata and re-check the package candidate before installing anything.

Do not run a broad package upgrade as part of this diagnostic step. First confirm that the candidate for `python-cryptography` is in the project's required range `>=50,<51`. If the candidate remains incompatible, stop and capture the exact repository/source output for further diagnosis. Never install 48.0.1, lower the project requirement, or change the encryption implementation as a workaround.

No device package was installed and no application source/dependency was changed by this diagnosis. The encryption gate remains open until the exact project interpreter imports a compatible package and all encrypted-backup acceptance tests pass.
