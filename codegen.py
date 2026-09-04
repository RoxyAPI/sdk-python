#!/usr/bin/env python3
"""
Generate factory.py from OpenAPI spec.

Reads specs/openapi.json and auto-generates src/roxy_sdk/factory.py with all
domain namespace classes, Roxy aggregate, and create_roxy() factory.

The OpenAPI spec is the only source of truth for *which* tags exist and what
endpoints belong to each. This file only configures how tag names map to
public SDK namespaces:

  1. Most tags derive their snake_case attribute and PascalCase class name
     automatically, e.g. "Vedic Astrology" -> vedic_astrology / VedicAstrologyDomain,
     "Numerology" -> numerology / NumerologyDomain, "Languages" -> languages /
     LanguagesDomain. New tags need NO change here.
  2. A handful of tags use a curated short-form for branding: the public SDK
     exposes ``roxy.astrology``, not ``roxy.western_astrology``. Those overrides
     live in NAMESPACE_ALIASES below.

Adding a brand-new tag with a non-default short-form (e.g. "Crystals and Healing
Stones" -> ``crystals``) is the only reason to touch this file. Otherwise
codegen handles it.

Run: python codegen.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SPEC_PATH = Path("specs/openapi.json")
OUTPUT_PATH = Path("src/roxy_sdk/factory.py")

# Curated short-form namespaces for product branding. Keys are exact tag names
# from the OpenAPI spec; values are the desired snake_case attribute name on
# the Roxy aggregate. The class name is derived from the attribute name (see
# tag_to_class). Any tag not listed here uses snake_case(tag_name) automatically.
NAMESPACE_ALIASES: dict[str, str] = {
    "Western Astrology": "astrology",
    "Crystals and Healing Stones": "crystals",
    "Location and Timezone": "location",
    "I-Ching": "iching",
}


def _snake_case(name: str) -> str:
    """Split on non-alphanumerics, lowercase, join with underscores."""
    parts = [p for p in re.split(r"[^a-zA-Z0-9]+", str(name)) if p]
    if not parts:
        return str(name).lower()
    return "_".join(p.lower() for p in parts)


def tag_to_attr(name: str) -> str:
    """Return the snake_case attribute name on the Roxy aggregate for a tag."""
    return NAMESPACE_ALIASES.get(name, _snake_case(name))


def tag_to_class(name: str) -> str:
    """Return the PascalCase domain class name for a tag, suffixed with Domain."""
    attr = tag_to_attr(name)
    pascal = attr.title().replace("_", "")
    return f"{pascal}Domain"


def tag_summary(tag: dict[str, Any]) -> str:
    """Extract a short, dev-facing summary from the spec's tag object.

    Prefers ``x-sdk-summary`` if present (forward-compat for when the server adds
    explicit SDK summaries per tag). Otherwise takes the first sentence of
    ``description``, capped at ~120 chars.
    """
    sdk_summary = tag.get("x-sdk-summary")
    if isinstance(sdk_summary, str) and sdk_summary.strip():
        return sdk_summary.strip()
    desc = (tag.get("description") or "").strip()
    if not desc:
        return str(tag.get("name") or "")
    first_sentence = re.split(r"\.\s+", desc, maxsplit=1)[0].strip()
    flat = re.sub(r"\s+", " ", first_sentence)
    return flat[:117].rstrip() + "..." if len(flat) > 120 else flat


def load_spec() -> dict[str, Any]:
    """Read the spec written by generate.py's fetch_spec (honors ROXYAPI_SPEC_FILE upstream)."""
    return json.loads(SPEC_PATH.read_text())


def tag_index(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map tag name -> tag object, for description/summary lookups."""
    return {t["name"]: t for t in spec.get("tags", []) if isinstance(t, dict) and "name" in t}


def spec_tag_order(spec: dict[str, Any]) -> list[str]:
    """Tag names in the order the spec declares them (the canonical domain order)."""
    return [t["name"] for t in spec.get("tags", []) if isinstance(t, dict) and "name" in t]


def group_by_tag(spec: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Bucket every operation by its first tag, walked once and shared by every consumer."""
    domains: dict[str, list[dict[str, Any]]] = {}
    for path, path_item in spec.get("paths", {}).items():
        for http_method in ("get", "post"):
            operation = path_item.get(http_method)
            if not operation:
                continue
            tags = operation.get("tags", ["Other"])
            tag = tags[0]
            oid = operation.get("operationId", "")
            if not oid:
                continue

            body_props, body_req = extract_body(spec, operation)

            domains.setdefault(tag, []).append(
                {
                    "operationId": oid,
                    "method": http_method,
                    "path": path,
                    "summary": operation.get("summary", ""),
                    "parameters": operation.get("parameters", []),
                    "body_properties": body_props,
                    "body_required_fields": body_req,
                }
            )
    return domains


def ordered_tags_for(spec: dict[str, Any], domains: dict[str, list[Any]]) -> list[str]:
    """Tags with operations, in spec order; brand-new tags not yet in the spec's own
    tags[] array sort alphabetically after, so they still get a deterministic position."""
    order = spec_tag_order(spec)
    ordered = [t for t in order if t in domains]
    ordered += sorted(t for t in domains if t not in order)
    return ordered


def camel_to_snake(name: str) -> str:
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1).lower()


def json_type_to_python(schema: dict) -> str:
    t = schema.get("type", "string")
    if t == "integer":
        return "int"
    if t == "number":
        return "float"
    if t == "boolean":
        return "bool"
    if t == "array":
        inner = json_type_to_python(schema.get("items", {}))
        return f"list[{inner}]"
    if t == "object":
        return "dict[str, Any]"
    return "str"


def resolve_ref(spec: dict, ref: str) -> dict:
    parts = ref.lstrip("#/").split("/")
    obj = spec
    for part in parts:
        obj = obj[part]
    return obj


def extract_body(spec: dict, operation: dict) -> tuple[dict, list[str]]:
    """Extract request body properties and required fields."""
    rb = operation.get("requestBody", {})
    if not rb:
        return {}, []
    content = rb.get("content", {}).get("application/json", {})
    schema = content.get("schema", {})
    if "$ref" in schema:
        schema = resolve_ref(spec, schema["$ref"])
    props = {}
    for name, prop in schema.get("properties", {}).items():
        if "$ref" in prop:
            prop = resolve_ref(spec, prop["$ref"])
        props[name] = prop
    return props, schema.get("required", [])


def build_method(op: dict) -> str:
    """Generate sync + async wrapper methods for one endpoint."""
    func = camel_to_snake(op["operationId"])
    http = op["method"]
    path = op["path"]
    summary = (op.get("summary") or func).replace("'", "").replace('"', "")

    path_params = [p["name"] for p in op.get("parameters", []) if p.get("in") == "path"]
    query_params = [p for p in op.get("parameters", []) if p.get("in") == "query"]

    # Build method signature params
    sig_parts: list[str] = []
    for p in path_params:
        sig_parts.append(f"{camel_to_snake(p)}: str")

    body_props = op.get("body_properties", {})
    body_required = op.get("body_required_fields", [])
    if body_props:
        for prop_name, prop_info in body_props.items():
            py_name = camel_to_snake(prop_name)
            py_type = json_type_to_python(prop_info)
            if prop_name in body_required:
                sig_parts.append(f"{py_name}: {py_type}")
            else:
                sig_parts.append(f"{py_name}: {py_type} | None = None")

    # Query params (skip lang, add at end)
    for qp in query_params:
        if qp["name"] == "lang":
            continue
        py_name = camel_to_snake(qp["name"])
        py_type = json_type_to_python(qp.get("schema", {}))
        sig_parts.append(f"{py_name}: {py_type} | None = None")

    has_lang = any(qp["name"] == "lang" for qp in query_params)
    if has_lang:
        sig_parts.append("lang: str | None = None")

    sig = ", ".join(["self", "*"] + sig_parts) if sig_parts else "self"

    # Build f-string path
    fpath = path
    for p in path_params:
        fpath = fpath.replace(f"{{{p}}}", f"{{{camel_to_snake(p)}}}")

    # Build method body
    body_lines: list[str] = []

    if http == "get":
        if query_params:
            body_lines.append("        params: dict[str, Any] = {}")
            for qp in query_params:
                py_name = camel_to_snake(qp["name"])
                body_lines.append(f"        if {py_name} is not None:")
                body_lines.append(f'            params["{qp["name"]}"] = {py_name}')
            body_lines.append(f'        return self._get(f"{fpath}", params=params or None)')
        else:
            body_lines.append(f'        return self._get(f"{fpath}")')
    else:  # POST
        if body_props:
            body_lines.append("        body: dict[str, Any] = {}")
            for prop_name in body_props:
                py_name = camel_to_snake(prop_name)
                if prop_name in body_required:
                    body_lines.append(f'        body["{prop_name}"] = {py_name}')
                else:
                    body_lines.append(f"        if {py_name} is not None:")
                    body_lines.append(f'            body["{prop_name}"] = {py_name}')
        else:
            body_lines.append("        body: dict[str, Any] = {}")

        if has_lang:
            body_lines.append("        params: dict[str, Any] = {}")
            body_lines.append("        if lang is not None:")
            body_lines.append('            params["lang"] = lang')
            body_lines.append(f'        return self._post(f"{fpath}", body, params=params or None)')
        else:
            body_lines.append(f'        return self._post(f"{fpath}", body)')

    body_code = "\n".join(body_lines)
    async_body = body_code.replace("self._get(", "await self._get_async(").replace(
        "self._post(", "await self._post_async("
    )

    return f"""    def {func}({sig}) -> Any:
        \"\"\"{summary}\"\"\"
{body_code}

    async def {func}_async({sig}) -> Any:
        \"\"\"{summary} (async)\"\"\"
{async_body}
"""


def main() -> None:
    spec = load_spec()
    tag_objects = tag_index(spec)
    domains = group_by_tag(spec)

    # Warn on stale NAMESPACE_ALIASES: aliases pointing at tags no longer in
    # the spec. New tags are fine; they auto-derive via tag_to_attr / tag_to_class.
    spec_tag_names = set(tag_objects) | set(domains)
    for alias_tag in NAMESPACE_ALIASES:
        if alias_tag not in spec_tag_names:
            print(
                f"WARNING: NAMESPACE_ALIASES entry '{alias_tag}' is stale: "
                "no such tag in the OpenAPI spec. Remove it from codegen.py."
            )

    # Write output
    out: list[str] = [
        '"""',
        "AUTO-GENERATED by codegen.py from OpenAPI spec. Do not edit manually.",
        "Regenerate with: python generate.py",
        '"""',
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "import httpx",
        "",
        "from roxy_sdk.version import VERSION",
        "",
        "",
        '_BASE_URL = "https://roxyapi.com/api/v2"',
        "",
        "",
        "class RoxyAPIError(Exception):",
        '    """Error returned by the RoxyAPI."""',
        "",
        "    def __init__(self, error: str, code: str, status_code: int) -> None:",
        "        self.error = error",
        "        self.code = code",
        "        self.status_code = status_code",
        '        super().__init__(f"[{status_code}] {code}: {error}")',
        "",
        "    def __repr__(self) -> str:",
        '        return f"RoxyAPIError(error={self.error!r}, code={self.code!r}, status_code={self.status_code})"',
        "",
        "",
        "def _default_headers(api_key: str) -> dict[str, str]:",
        "    return {",
        '        "X-API-Key": api_key,',
        '        "X-SDK-Client": f"roxy-sdk-python/{VERSION}",',
        '        "Accept": "application/json",',
        "    }",
        "",
        "",
        "def _handle_response(resp: httpx.Response) -> Any:",
        '    """Parse response, raising RoxyAPIError on 4xx/5xx."""',
        "    if resp.status_code >= 400:",
        "        try:",
        "            body = resp.json()",
        "        except Exception:",
        "            body = {}",
        "        raise RoxyAPIError(",
        '            error=body.get("error", resp.text or "Unknown error"),',
        '            code=body.get("code", "unknown"),',
        "            status_code=resp.status_code,",
        "        )",
        "    return resp.json()",
        "",
        "",
        "class _BaseDomain:",
        '    """Base class for all domain namespaces."""',
        "",
        "    def __init__(self, client: httpx.Client, async_client: httpx.AsyncClient) -> None:",
        "        self._client = client",
        "        self._async_client = async_client",
        "",
        "    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:",
        "        return _handle_response(self._client.get(path, params=params))",
        "",
        "    async def _get_async(self, path: str, params: dict[str, Any] | None = None) -> Any:",
        "        return _handle_response(await self._async_client.get(path, params=params))",
        "",
        "    def _post(self, path: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:",
        "        return _handle_response(self._client.post(path, json=body, params=params))",
        "",
        "    async def _post_async(self, path: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:",
        "        return _handle_response(await self._async_client.post(path, json=body, params=params))",
        "",
    ]

    # Domain classes. Emit in spec tag order when available; fall back to
    # alphabetical so brand-new endpoints get a deterministic position.
    ordered_tags = ordered_tags_for(spec, domains)

    domain_classes: list[tuple[str, str]] = []
    for tag in ordered_tags:
        class_name = tag_to_class(tag)
        attr_name = tag_to_attr(tag)
        summary = tag_summary(tag_objects.get(tag, {"name": tag}))
        docstring = summary or f"{tag} endpoints."
        domain_classes.append((class_name, attr_name))
        out.append("")
        out.append(f"class {class_name}(_BaseDomain):")
        out.append(f'    """{docstring}"""')
        out.append("")
        for op in sorted(domains[tag], key=lambda x: x["operationId"]):
            out.append(build_method(op))

    # Roxy class
    out.append("")
    out.append("class Roxy:")
    out.append('    """')
    out.append("    RoxyAPI Python SDK.")
    out.append("    Reuses HTTP connections. Supports context manager.")
    out.append("")
    out.append("    Usage::")
    out.append("        from roxy_sdk import create_roxy")
    out.append('        roxy = create_roxy("your-api-key")')
    out.append('        horoscope = roxy.astrology.get_daily_horoscope(sign="aries")')
    out.append('    """')
    out.append("")
    out.append(
        "    def __init__(self, api_key: str, base_url: str = _BASE_URL, timeout: float = 30.0) -> None:"
    )
    out.append("        if not api_key:")
    out.append(
        '            raise ValueError("API key is required. Get one at https://roxyapi.com/pricing")'
    )
    out.append("        headers = _default_headers(api_key)")
    out.append(
        "        self._client = httpx.Client(base_url=base_url, headers=headers, timeout=timeout)"
    )
    out.append(
        "        self._async_client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout)"
    )
    for cn, an in domain_classes:
        out.append(f"        self.{an} = {cn}(self._client, self._async_client)")
    out.append("")
    out.append("    def close(self) -> None:")
    out.append('        """Close sync HTTP connections."""')
    out.append("        self._client.close()")
    out.append("")
    out.append("    async def aclose(self) -> None:")
    out.append('        """Close all HTTP connections (sync + async)."""')
    out.append("        self._client.close()")
    out.append("        await self._async_client.aclose()")
    out.append("")
    out.append("    def __enter__(self) -> Roxy:")
    out.append("        return self")
    out.append("")
    out.append("    def __exit__(self, *args: Any) -> None:")
    out.append("        self.close()")
    out.append("")
    out.append("    async def __aenter__(self) -> Roxy:")
    out.append("        return self")
    out.append("")
    out.append("    async def __aexit__(self, *args: Any) -> None:")
    out.append("        await self.aclose()")
    out.append("")
    out.append("    def __repr__(self) -> str:")
    out.append('        return f"Roxy(base_url={self._client.base_url!r})"')
    out.append("")
    out.append("")

    # create_roxy
    out.append(
        "def create_roxy(api_key: str, base_url: str = _BASE_URL, timeout: float = 30.0) -> Roxy:"
    )
    out.append('    """')
    out.append("    Create a configured Roxy instance.")
    out.append("")
    out.append("    Args:")
    out.append("        api_key: Your RoxyAPI key. Get one at https://roxyapi.com/pricing")
    out.append(
        "        base_url: Override the default API base URL. Default: https://roxyapi.com/api/v2"
    )
    out.append("        timeout: Request timeout in seconds. Default: 30.")
    out.append('    """')
    out.append("    return Roxy(api_key=api_key, base_url=base_url, timeout=timeout)")
    out.append("")

    OUTPUT_PATH.write_text("\n".join(out))
    print(f"Generated {OUTPUT_PATH} ({len(out)} lines)")


if __name__ == "__main__":
    main()
