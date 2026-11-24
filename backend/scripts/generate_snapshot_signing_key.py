"""Generate an owner-managed Ed25519 keypair for OHLCV snapshot signing.

The private key is written with owner-only permissions and is never printed.
Run this on the authoritative source host, not in the repository checkout.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def _write_exclusive(path: Path, content: bytes, mode: int) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    if os.name == "posix":
        os.chmod(path, mode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory",
        required=True,
        help="Absolute owner-only directory outside the repository and container build context.",
    )
    args = parser.parse_args()

    directory = Path(args.directory).expanduser()
    repository_root = Path(__file__).resolve().parents[2]
    if directory.resolve().is_relative_to(repository_root):
        raise ValueError("Signing keys must be stored outside the repository.")
    directory.mkdir(parents=True, exist_ok=True)
    private_key = Ed25519PrivateKey.generate()
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    key_id = hashlib.sha256(public_bytes).hexdigest()[:16]
    private_path = directory / f"{key_id}.private.pem"
    public_path = directory / f"{key_id}.public.b64"
    if private_path.exists() or public_path.exists():
        raise FileExistsError("Generated key output already exists; refusing to overwrite.")

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_b64 = base64.b64encode(public_bytes) + b"\n"
    _write_exclusive(private_path, private_pem, 0o600)
    try:
        _write_exclusive(public_path, public_b64, 0o644)
    except Exception:
        private_path.unlink(missing_ok=True)
        raise

    print(f"key_id={key_id}")
    print(f"public_key_base64={public_b64.decode('ascii').strip()}")
    print(f"private_key_file={private_path}")
    print(f"public_key_file={public_path}")
    print("Keep the private key on the authoritative source host; never commit or share it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
