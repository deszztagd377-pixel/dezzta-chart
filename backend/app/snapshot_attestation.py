"""Ed25519 attestation helpers for authoritative OHLCV snapshots.

Public keys are configured on each replica; private signing keys stay on the
authoritative source host and are never serialized into snapshots or receipts.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import re
import stat
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

_KEY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate_trusted_public_keys(
    trusted_public_keys: Mapping[str, str] | None,
) -> dict[str, bytes]:
    """Validate a key-id -> base64(raw Ed25519 public key) trust map."""
    if trusted_public_keys is None:
        return {}
    if not isinstance(trusted_public_keys, Mapping):
        raise ValueError("trusted_snapshot_keys must be a mapping.")
    normalized: dict[str, bytes] = {}
    for key_id, encoded in trusted_public_keys.items():
        if not isinstance(key_id, str) or not _KEY_ID.fullmatch(key_id):
            raise ValueError("Snapshot signing key IDs must be stable identifiers.")
        if not isinstance(encoded, str) or not encoded:
            raise ValueError("Snapshot trusted public keys must be base64 strings.")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Snapshot trusted public key is not valid base64.") from exc
        if len(raw) != 32:
            raise ValueError("Ed25519 public keys must contain exactly 32 raw bytes.")
        normalized[key_id] = raw
    return normalized


def canonical_snapshot_attestation_payload(metadata: Mapping[str, Any]) -> bytes:
    """Return deterministic bytes binding snapshot identity and content."""
    if not isinstance(metadata, Mapping):
        raise ValueError("Snapshot attestation metadata must be a mapping.")
    source_id = metadata.get("source_id")
    generation_id = metadata.get("generation_id")
    high_water = metadata.get("high_water")
    retention_floor = metadata.get("retention_floor")
    bar_retention = metadata.get("bar_retention")
    row_count = metadata.get("row_count")
    digest = metadata.get("sha256")
    format_version = metadata.get("format_version")
    if (
        not isinstance(source_id, str) or not source_id or len(source_id) > 128
        or not isinstance(generation_id, str) or not generation_id or len(generation_id) > 128
        or type(high_water) is not int or high_water < 0
        or type(retention_floor) is not int or not 0 <= retention_floor <= high_water
        or not isinstance(bar_retention, Mapping)
        or any(
            not isinstance(key, str) or type(value) is not int or value < 1
            for key, value in bar_retention.items()
        )
        or type(row_count) is not int or row_count < 0
        or not isinstance(digest, str) or not _SHA256.fullmatch(digest)
        or type(format_version) is not int or format_version < 1
    ):
        raise ValueError("Snapshot attestation metadata is incomplete or invalid.")
    payload = {
        "schema": "dezzta.ohlcv.snapshot-attestation",
        "schema_version": 1,
        "source_id": source_id,
        "generation_id": generation_id,
        "high_water": high_water,
        "retention_floor": retention_floor,
        "bar_retention": dict(sorted(bar_retention.items())),
        "row_count": row_count,
        "sha256": digest,
        "format_version": format_version,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_snapshot_attestation(
    metadata: Mapping[str, Any],
    *,
    key_id: str | None,
    private_key: object | None,
) -> dict[str, str] | None:
    """Sign snapshot identity/content metadata with an owner-held Ed25519 key."""
    if private_key is None and key_id is None:
        return None
    if not isinstance(key_id, str) or not _KEY_ID.fullmatch(key_id):
        raise ValueError("A valid snapshot signing key ID is required.")
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Snapshot signing key must be an Ed25519 private key.")
    signature = private_key.sign(canonical_snapshot_attestation_payload(metadata))
    return {
        "algorithm": "Ed25519",
        "key_id": key_id,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def verify_snapshot_attestation(
    metadata: Mapping[str, Any],
    attestation: Mapping[str, Any] | None,
    trusted_public_keys: Mapping[str, str] | None,
) -> str:
    """Verify an attestation against the configured owner-pinned public keys."""
    keys = validate_trusted_public_keys(trusted_public_keys)
    if not isinstance(attestation, Mapping) or set(attestation) != {
        "algorithm", "key_id", "signature"
    }:
        raise ValueError("Snapshot is missing a valid Ed25519 attestation envelope.")
    if attestation.get("algorithm") != "Ed25519":
        raise ValueError("Snapshot attestation algorithm is unsupported.")
    key_id = attestation.get("key_id")
    signature_text = attestation.get("signature")
    if not isinstance(key_id, str) or not _KEY_ID.fullmatch(key_id):
        raise ValueError("Snapshot attestation key ID is invalid.")
    public_key_bytes = keys.get(key_id)
    if public_key_bytes is None:
        raise ValueError("Snapshot attestation key ID is not trusted.")
    if not isinstance(signature_text, str) or not signature_text:
        raise ValueError("Snapshot attestation signature is missing.")
    try:
        signature = base64.b64decode(signature_text, validate=True)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature, canonical_snapshot_attestation_payload(metadata))
    except (binascii.Error, ValueError, InvalidSignature) as exc:
        raise ValueError("Snapshot Ed25519 attestation verification failed.") from exc
    return key_id


def load_ed25519_private_key(path: str) -> Ed25519PrivateKey:
    """Load a bounded PEM key through a no-follow, verified file descriptor."""
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Snapshot signing key path is required.")
    key_path = Path(path).expanduser()
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if os.name == "posix":
        no_follow = getattr(os, "O_NOFOLLOW", None)
        if no_follow is None:
            raise ValueError(
                "Snapshot private key loading requires no-follow file support."
            )
        flags |= no_follow
        # Avoid blocking on FIFOs/devices before fstat rejects non-regular files.
        flags |= getattr(os, "O_NONBLOCK", 0)

    try:
        descriptor = os.open(key_path, flags)
    except OSError as exc:
        raise ValueError(
            "Snapshot private key file cannot be opened safely."
        ) from exc

    pem_bytes = b""
    try:
        file_info = os.fstat(descriptor)
        if not stat.S_ISREG(file_info.st_mode):
            raise ValueError("Snapshot private key path must reference a regular file.")
        if os.name == "posix":
            if file_info.st_uid != os.geteuid():
                raise ValueError("Snapshot private key file must be owned by the service user.")
            if stat.S_IMODE(file_info.st_mode) & 0o077:
                raise ValueError(
                    "Snapshot private key file must be owner-only with no group/world access."
                )
        with os.fdopen(descriptor, "rb") as key_file:
            descriptor = -1
            pem_bytes = key_file.read(65_537)
        if len(pem_bytes) > 65_536:
            raise ValueError("Snapshot private key file exceeds the 64 KiB size limit.")
    finally:
        if descriptor >= 0:
            os.close(descriptor)

    key = serialization.load_pem_private_key(pem_bytes, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Snapshot signing key file must contain an Ed25519 private key.")
    return key


def load_snapshot_signing_key_from_environment(
    environ: Mapping[str, str] | None = None,
) -> tuple[Ed25519PrivateKey | None, str | None]:
    """Load optional source-host signing material without exposing private bytes."""
    source = os.environ if environ is None else environ
    key_path = source.get("OHLCV_SNAPSHOT_SIGNING_KEY_FILE", "").strip()
    key_id = source.get("OHLCV_SNAPSHOT_SIGNING_KEY_ID", "").strip()
    if not key_path and not key_id:
        return None, None
    if not key_path or not key_id:
        raise ValueError(
            "OHLCV_SNAPSHOT_SIGNING_KEY_FILE and OHLCV_SNAPSHOT_SIGNING_KEY_ID must be configured together."
        )
    if not _KEY_ID.fullmatch(key_id):
        raise ValueError("OHLCV_SNAPSHOT_SIGNING_KEY_ID is invalid.")
    return load_ed25519_private_key(key_path), key_id


def export_raw_public_key(private_key: Ed25519PrivateKey) -> str:
    """Return the base64 raw public key suitable for the replica trust map."""
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("private_key must be an Ed25519 private key.")
    raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode("ascii")
