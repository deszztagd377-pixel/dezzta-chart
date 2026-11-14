# Termux Android host compatibility and safe recovery status

Audit date: 2026-11-14  
Project: DEZZTA CHART  
Owner environment: one Infinix GT20, Android 15; no second phone, PC or laptop.  
Cost rule: zero incremental cost.

## Observed local environment and blocker

The owner's previously reported environment is:

- Termux Google Play build: `googleplay.2026.10.09`.
- Android: 15; architecture: `aarch64`.
- Installed `termux-keyring`: 3.15.
- Owner-restored, working configured package repository: `https://termux.net` (the Google Play build's original source). A separate report in issue #1648 describes a stock `packages.termux.dev` source on another affected setup; do not conflate that report with the owner's restored active source.
- APT failure: `NO_PUBKEY 5A897D96E57CF20C`.
- The required backend dependency is `cryptography>=50,<51`; the previously observed repository candidate was `48.0.1-1`, which does not satisfy that range.

This is a package-repository signature trust failure, not evidence that the user's project code or Python environment is corrupt. Until package metadata is verifiably signed and current, package installation and dependency-candidate conclusions from that repository are not trusted.

## External issue evidence reviewed

- [Termux Play Store issue #1642](https://github.com/termux-play-store/termux-issues/issues/1642) reports the same Android 15, `googleplay.2026.10.09`, aarch64, keyring 3.15 and exact missing key. It remained open at the time of this audit.
- [Termux Play Store issue #1648](https://github.com/termux-play-store/termux-issues/issues/1648) reports the same missing key on the same Play Store app build. The discussion identifies a possible mismatch between the repository signing key and the keyring packaged in the Play build; this is community issue discussion, not a verified maintainer-issued recovery procedure.
- The [official Play Store build release page](https://github.com/termux-play-store/termux-apps/releases) lists `googleplay.2026.10.09` as the latest app release reviewed for this audit. Its release notes do not document a keyring recovery fix.

## Safe disposition

**Status: BLOCKED — WAIT FOR VERIFIED OFFICIAL REPOSITORY/KEYRING FIX OR MAINTAINER-CONFIRMED PROCEDURE.**

Do not:
- disable APT signature verification;
- use `trusted=yes`, `--allow-unauthenticated`, or equivalent bypasses;
- import a signing key from an unverified source;
- manually replace trusted keyring files based only on a forum comment;
- downgrade the project's `cryptography>=50,<51` requirement to fit an older candidate;
- install unsigned or unverified package files.

Switching from the Play Store build to another distribution may involve a different Android signing identity and uninstall/reinstall. With one phone and project data in Termux, that is a consequential migration and is **not** treated as the immediate fix. No migration is authorized by this document.

## DEZZTA CHART impact and workarounds

- Termux-based encrypted-backup verification requiring `cryptography>=50,<51` remains blocked on this device.
- Existing SQLite standard-library backup/restore checks can continue independently where the already-installed Python/SQLite environment supports them; this does not close encrypted offsite-backup acceptance.
- CI remains the trusted location for repository tests that do not require changing the phone's package trust configuration.
- No user command is required for this checkpoint. Reassess only after a signed Play Store update or a recovery procedure explicitly confirmed by Termux maintainers is available.
- The Termux issue does not justify changing DEZZTA CHART's encryption algorithm, weakening dependency constraints, or claiming external backup acceptance.

## Re-audit triggers

Recheck the official Play Store release notes, issue #1642/#1648 maintainer responses, repository signing metadata and the installed keyring compatibility before any package operation. Record the exact app build, keyring version, repository URL, signature result and package candidate. If any of these cannot be verified, keep the blocker open.



## External issue re-audit — 2026-11-14

- Termux Play Store issue [#1642](https://github.com/termux-play-store/termux-issues/issues/1642) remains **OPEN**; its last recorded update at this audit was 2026-11-10. It reports the same app build `googleplay.2026.10.09`, Android 15, aarch64, keyring 3.15 and missing key `5A897D96E57CF20C`.
- The issue discussion identifies that key as the upstream `termux-autobuilds` signing key, which is absent from the Play Store keyring 3.15. This is community analysis, not a maintainer-confirmed recovery procedure.
- Issue [#1648](https://github.com/termux-play-store/termux-issues/issues/1648) includes a report that the Play Store build's stock `termux.sources` points to `packages.termux.dev/apt/termux-main`, with the same missing-key mismatch. A community reply suggests a distribution migration, but it requires a different app signing identity and uninstall/reinstall; this is not selected for the one-device setup.
- The latest Play Store app release visible in the official release list at this audit remains `googleplay.2026.10.09` (2026-10-09). Its published notes do not mention a keyring/signing fix.
- No maintainer-authored, verified recovery procedure or newer signed Play Store keyring fix was found in the audited issue/release evidence.

**Current decision remains unchanged:** retain APT signature verification, do not import the missing key from an unverified source, do not clear app data, and do not migrate distributions. The blocker is upstream packaging/repository trust compatibility, not a DEZZTA CHART source-code failure. Re-audit after an official maintainer response or signed Play Store release that explicitly fixes the repository keyring.

References:
- https://github.com/termux-play-store/termux-issues/issues/1642
- https://github.com/termux-play-store/termux-issues/issues/1648
- https://github.com/termux-play-store/termux-apps/releases


## Owner-confirmed delivery scope — direct APK sideload, not Play Store (2026-11-14)

The current delivery target is an Android APK installable directly on the owner's Infinix GT20 by manual sideload. Google Play Store publication is deferred and excluded from current cost and acceptance planning.

The existing Android workflow builds a debug APK from a temporary Capacitor wrapper and packages the frontend only. It does not prove native Termux backend hosting, Redis availability, or a live market-data connection. Treat APK packaging, on-device install/launch, and full backend-connected functionality as three separate evidence items.
