import json
from pathlib import Path


def test_picomatch_advisory_dependency_remains_dev_only():
    """Keep the known advisory out of the production dependency graph."""
    root = Path(__file__).resolve().parents[2]
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((root / "package-lock.json").read_text(encoding="utf-8"))

    runtime_dependencies = package.get("dependencies", {})
    development_dependencies = package.get("devDependencies", {})
    lock_packages = lock.get("packages", {})

    # The frontend runtime must not acquire build/test-only glob tooling.
    for name in ("picomatch", "fdir", "tinyglobby", "vite", "vitest"):
        assert name not in runtime_dependencies

    assert "vite" in development_dependencies
    assert "vitest" in development_dependencies

    # npm lockfile's dev flag means these packages are reachable only from
    # development dependencies. This is exposure reduction, not an audit waiver.
    for name in ("picomatch", "fdir", "tinyglobby", "vite", "vitest"):
        entry = lock_packages.get(f"node_modules/{name}")
        assert entry is not None
        assert entry.get("dev") is True
