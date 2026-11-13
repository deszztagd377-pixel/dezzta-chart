# DEZZTA CHART — Android / Termux readiness

Audit date: 2026-11-13  
Audited source branch: `phase-2/market-data-foundation`  
Source HEAD before this documentation checkpoint: `a3e920d6ab49967b073c40d5181d7033ee912d41`

## Executive status

**Termux support is not complete.** The repository currently contains a read-only Android host preflight and CI coverage for that script. This is an environment inventory, not an installation, runtime, deployment, or production-readiness certification.

The user's previously reported Termux environment showed OpenSSL 3.6.3 and a Python 3.13 environment where the backend encryption test module could not be collected because the `cryptography` package was unavailable. That result identifies an unresolved Python dependency/runtime compatibility gate; it does not establish that OpenSSL itself is broken.

## Evidence already present

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
