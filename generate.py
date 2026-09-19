#!/usr/bin/env python3
"""
Refresh specs/openapi.json, regenerate factory.py from it, then sync the docs.

The spec comes from the live API, or from the file named by ROXYAPI_SPEC_FILE when that is
set: CI and the git hooks point it at the committed spec so the check is offline and
byte-reproducible, and only the release workflow fetches.

Run with: python generate.py
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any

import codegen
import sync_docs

SPEC_URL = "https://roxyapi.com/api/v2/openapi.json"


def _fetch_with_retry(url: str, attempts: int = 5) -> bytes:
    """Retry with backoff: a transient upstream error (CDN 520) must not fail the release run."""
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url) as resp:
                body: bytes = resp.read()
                return body
        except Exception as err:
            if attempt == attempts:
                raise
            delay = 2**attempt
            print(f"Fetch attempt {attempt}/{attempts} failed ({err}), retrying in {delay}s")
            time.sleep(delay)
    raise RuntimeError("unreachable")


def _load_raw_spec() -> bytes:
    spec_file = os.environ.get("ROXYAPI_SPEC_FILE")
    if spec_file:
        print(f"Reading OpenAPI spec from {spec_file} (offline, ROXYAPI_SPEC_FILE)")
        with open(spec_file, "rb") as f:
            return f.read()
    print(f"Fetching OpenAPI spec from {SPEC_URL}")
    return _fetch_with_retry(SPEC_URL)


def fetch_spec() -> None:
    spec: dict[str, Any] = json.loads(_load_raw_spec())

    # Patch server URL to absolute prod URL
    if spec.get("servers") and spec["servers"][0].get("url") == "/api/v2":
        spec["servers"][0]["url"] = "https://roxyapi.com/api/v2"
        print("Patched server URL to https://roxyapi.com/api/v2")

    codegen.SPEC_PATH.parent.mkdir(exist_ok=True)
    codegen.SPEC_PATH.write_text(json.dumps(spec, indent=2))
    paths = spec.get("paths", {})
    endpoint_count = sum(len(methods) for methods in paths.values())
    print(f"Spec saved: {len(paths)} paths, {endpoint_count} endpoints")


def main() -> None:
    fetch_spec()
    codegen.main()
    sync_docs.main()
    print("\nDone. All generated code is up to date.")


if __name__ == "__main__":
    main()
