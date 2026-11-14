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

### Next safe device action — SUPERSEDED; DO NOT FOLLOW

The initial mirror-switch proposal below was invalid for the owner's Google Play Termux build and is retained only as historical audit context. **Do not run `termux-change-repo` and do not switch this installation to `packages.termux.dev`.** The exact device evidence and corrected safe decision are recorded in the later section titled `Owner-reported Google Play Termux repository/keyring resolution — 2026-11-13`.

The original proposal was to switch Main from `termux.net` to `packages.termux.dev` and re-check `python-cryptography`. That proposal was superseded after the owner demonstrated that `termux-change-repo` is absent and the upstream repository is rejected by APT with `NO_PUBKEY 5A897D96E57CF20C`. It must not be presented as an actionable instruction.

Current safe state: retain the working Google Play source; do not bypass signature checks, install 48.0.1, lower `cryptography>=50,<51`, or modify the encryption design. The encryption gate remains open until a compatible authenticated package path is available and the encrypted-backup acceptance tests pass.

## Owner-reported Google Play Termux repository/keyring resolution — 2026-11-13

This section supersedes the earlier instruction in this document to use `termux-change-repo` and switch the Google Play installation to the upstream Main repository.

Exact device evidence reported by the owner:

- Termux build: `googleplay.2026.10.09`.
- Android: 15; ABI: `aarch64`; device: Infinix X6871.
- `termux-tools`: 3.0.9; `termux-keyring`: 3.15.
- `termux-change-repo` is absent from the installed `termux-tools` package.
- The installed keyring file `$PREFIX/share/termux-keyring/termux-packages.gpg` is 219 bytes and is symlinked into `$PREFIX/etc/apt/trusted.gpg.d/`.
- The Google Play build's original configured source was `https://termux.net`; `pkg update` succeeds against it.
- Its package index offers `python-cryptography 48.0.1-1`, which does not satisfy `cryptography>=50,<51`.
- Manually changing the source to `https://packages.termux.dev/apt/termux-main` produced `NO_PUBKEY 5A897D96E57CF20C`; APT correctly rejected the repository metadata. The owner restored the original `https://termux.net` source from a saved backup, and `pkg update` again succeeded.
- The saved original source configuration is outside APT's source directory at `$HOME/termux.sources.original-backup`.

A matching public report in `termux-play-store/termux-issues#1642` describes the same Google Play build, Android 15, aarch64, `termux-tools 3.0.9`, `termux-keyring 3.15`, 219-byte keyring, and missing key ID. The report explains that the Play Store keyring contains the Play repository signing key but not the upstream `termux-autobuilds` key required by `packages.termux.dev`. This is a build/repository signing-key mismatch, not evidence that the owner's keyring file is corrupt.

### Corrected decision

- Keep the currently working Google Play Termux installation and its original `https://termux.net` source for now.
- Do not run `termux-change-repo`; it is absent in this installation.
- Do not switch this build to `packages.termux.dev` unless a compatible signed keyring/update is officially provided for this Play build.
- Never bypass APT signature checks, import an unverified key, or install packages from an unauthenticated source.
- Do not install `python-cryptography 48.0.1-1` and do not lower `backend/requirements.txt` or alter the AES-GCM/PBKDF2 design.
- The native encrypted-backup test gate remains blocked. SQLite-only backup tests remain passed evidence but are not encryption acceptance.
- Any migration to a different Termux distribution would require a separately reviewed, verified backup/restore plan. No migration, uninstall, app-data clearing, or project deletion is authorized by this checkpoint.

## Owner product constraint — ZERO COST

The owner requires a ZERO COST direction for DEZZTA CHART. Prefer free/open-source tooling and a build/install/use workflow that does not depend on paid hosting, paid market-data subscriptions, paid APIs, or Play Store publication fees. Do not introduce paid infrastructure or services without explicit owner approval. The immediate product target is an installable APK on the owner's phone; Google Play publication is deferred until the owner explicitly decides to pursue it. Clearly disclose any unavoidable cost and investigate a genuinely free alternative before proposing a paid dependency.


## Follow-up verification — Google Play signing-key issue remains open (2026-11-14)

The matching upstream Google Play issue tracker was checked again through the GitHub repository API:
- [Issue #1642](https://github.com/termux-play-store/termux-issues/issues/1642) — still open; last updated 2026-11-10.
- [Issue #1648](https://github.com/termux-play-store/termux-issues/issues/1648) — still open; last updated 2026-10-15.
- The reported missing key `5A897D96E57CF20C` is the upstream `termux-autobuilds` signing key. The Play Store build's installed keyring does not contain it.

**Decision unchanged:** keep the working Google Play repository configuration; do not switch to `packages.termux.dev`, import an unverified key, bypass APT signature verification, or install the incompatible `python-cryptography 48.0.1-1`. Do not reduce `cryptography>=50,<51` or modify AES-GCM/PBKDF2. No Termux action is required from the owner in this checkpoint. Revisit only when the Play build provides an officially compatible signed keyring/repository path.
