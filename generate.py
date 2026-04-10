#!/usr/bin/env python3
"""
Fetch the latest OpenAPI spec from RoxyAPI, run openapi-python-client to generate
typed client code, then run codegen to produce the factory.py wrapper.

Run with: python generate.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

SPEC_URL = "https://roxyapi.com/api/v2/openapi.json"
SPEC_PATH = Path("specs/openapi.json")
GENERATED_DIR = Path("src/roxy_sdk/_generated")


def fetch_spec() -> dict:
    import urllib.request

    print(f"Fetching OpenAPI spec from {SPEC_URL}")
    with urllib.request.urlopen(SPEC_URL) as resp:
        spec = json.loads(resp.read())

    # Patch server URL to absolute prod URL
    if spec.get("servers") and spec["servers"][0].get("url") == "/api/v2":
        spec["servers"][0]["url"] = "https://roxyapi.com/api/v2"
        print("Patched server URL to https://roxyapi.com/api/v2")

    SPEC_PATH.parent.mkdir(exist_ok=True)
    SPEC_PATH.write_text(json.dumps(spec, indent=2))
    print(f"Spec saved to {SPEC_PATH}")

    # Count endpoints for verification
    paths = spec.get("paths", {})
    endpoint_count = sum(len(methods) for methods in paths.values())
    print(f"Spec contains {len(paths)} paths, {endpoint_count} endpoints")

    return spec


def run_openapi_python_client() -> None:
    """Run openapi-python-client to generate typed client code into _generated/."""
    # Clean existing generated directory
    if GENERATED_DIR.exists():
        shutil.rmtree(GENERATED_DIR)
        print(f"Cleaned {GENERATED_DIR}")

    # Find the openapi-python-client binary
    # Try .venv first, then system PATH
    venv_bin = Path(".venv/bin/openapi-python-client")
    if venv_bin.exists():
        opc_cmd = str(venv_bin)
    else:
        opc_cmd = "openapi-python-client"

    cmd = [
        opc_cmd,
        "generate",
        "--path",
        str(SPEC_PATH),
        "--meta",
        "none",
        "--output-path",
        str(GENERATED_DIR),
    ]

    # Note: openapi-python-client.toml is not used with --meta none

    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")

    if result.returncode != 0:
        print(result.stderr, end="", file=sys.stderr)
        sys.exit(result.returncode)

    # Count generated files
    api_dir = GENERATED_DIR / "api"
    model_dir = GENERATED_DIR / "models"
    api_files = list(api_dir.rglob("*.py")) if api_dir.exists() else []
    model_files = list(model_dir.rglob("*.py")) if model_dir.exists() else []
    print(f"Generated {len(api_files)} API files, {len(model_files)} model files")


def run_codegen() -> None:
    """Run codegen.py to produce the factory.py wrapper."""
    print("\nRunning codegen...")
    result = subprocess.run(
        [sys.executable, "codegen.py"],
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="", file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    # 1. Fetch spec from production API
    fetch_spec()

    # 2. Generate factory.py from spec (domain classes, methods, Roxy aggregate)
    run_codegen()

    # Optional: run openapi-python-client for typed models (not used by factory.py yet)
    # Uncomment when wiring typed return types:
    # run_openapi_python_client()

    print("\nDone. All generated code is up to date.")


if __name__ == "__main__":
    main()
