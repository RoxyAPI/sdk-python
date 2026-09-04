#!/usr/bin/env python3
"""
Regenerate the spec-derived docs in README.md and AGENTS.md:
  - The domain table (`<!-- BEGIN:DOMAINS -->` markers): one row per spec tag, in spec
    tag order, showing the `roxy.<accessor>` namespace and its method count.
  - The multi-language note (`<!-- BEGIN:LANGS -->` markers): the `lang` enum values and
    which domains take a `lang` query param, replacing hand-typed language lists.

Run with: python sync_docs.py (also runs automatically at the end of generate.py)

The OpenAPI spec is the single source of truth. Adding a new API domain requires NO
manual doc edit. Reuses codegen.py's spec loading and tag/operation walk rather than
parsing the spec a second time. Fails loudly only if:
  - README.md / AGENTS.md is missing its BEGIN/END markers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codegen import (
    group_by_tag,
    load_spec,
    ordered_tags_for,
    tag_index,
    tag_summary,
    tag_to_attr,
)

README_PATH = Path("README.md")
AGENTS_PATH = Path("AGENTS.md")

DOMAINS_BEGIN = "<!-- BEGIN:DOMAINS -->"
DOMAINS_END = "<!-- END:DOMAINS -->"
LANGS_BEGIN = "<!-- BEGIN:LANGS -->"
LANGS_END = "<!-- END:LANGS -->"

# Curated display titles for the README domain table's human-facing "Domain" column,
# for the same tags NAMESPACE_ALIASES shortens in codegen.py for branding. A brand-new
# tag needs no entry here; it falls back to its own spec tag name.
DOMAIN_TITLES: dict[str, str] = {
    "Crystals and Healing Stones": "Crystals",
    "Location and Timezone": "Location",
    "I-Ching": "I Ching",
}


def fail(msg: str) -> None:
    raise SystemExit(f"\n✗ sync_docs: {msg}\n")


def replace_region(path: Path, begin: str, end: str, block: str) -> bool:
    src = path.read_text()
    begin_idx = src.find(begin)
    end_idx = src.find(end)
    if begin_idx == -1 or end_idx == -1 or end_idx < begin_idx:
        fail(f"{path} is missing {begin} / {end} markers")
    next_src = src[:begin_idx] + block + src[end_idx + len(end) :]
    if next_src == src:
        return False
    path.write_text(next_src)
    return True


def render_domains_table(
    tags: list[str],
    domains: dict[str, list[dict[str, Any]]],
    tag_objects: dict[str, dict[str, Any]],
    *,
    with_title: bool,
) -> str:
    """Render the domain table for either file: README carries an extra human-facing
    "Domain" title column ahead of the namespace; AGENTS starts at the namespace."""
    if with_title:
        header = ["Domain", "Property", "Methods", "What it covers"]
        sep = ["--------", "----------", "---------", "----------------"]
    else:
        header = ["Namespace", "Methods", "What it covers"]
        sep = ["-----------", "---------", "----------------"]
    rows = [f"| {' | '.join(header)} |", f"|{'|'.join(sep)}|"]
    for tag in tags:
        ns = f"`roxy.{tag_to_attr(tag)}`"
        methods = str(len(domains.get(tag, [])))
        summary = tag_summary(tag_objects.get(tag, {"name": tag}))
        cells = [ns, methods, summary]
        if with_title:
            cells.insert(0, DOMAIN_TITLES.get(tag, tag))
        rows.append(f"| {' | '.join(cells)} |")
    return "\n".join([DOMAINS_BEGIN, *rows, DOMAINS_END])


def lang_facts(
    domains: dict[str, list[dict[str, Any]]], tags: list[str]
) -> tuple[list[str], str | None, list[str], list[str]]:
    """Derive the `lang` enum, its default, and which domains take it, from the
    operations already grouped by codegen.group_by_tag."""
    codes: list[str] = []
    default: str | None = None
    supports_lang: set[str] = set()
    for tag, ops in domains.items():
        for op in ops:
            lang_param = next(
                (p for p in op["parameters"] if p.get("name") == "lang" and p.get("in") == "query"),
                None,
            )
            if not lang_param:
                continue
            supports_lang.add(tag)
            schema = lang_param.get("schema", {})
            if not codes and schema.get("enum"):
                codes = list(schema["enum"])
            if default is None and schema.get("default") is not None:
                default = str(schema["default"])
    supported = [tag_to_attr(t) for t in tags if t in supports_lang]
    english_only = [tag_to_attr(t) for t in tags if t not in supports_lang]
    return codes, default, supported, english_only


def render_langs_block(
    domains: dict[str, list[dict[str, Any]]], tags: list[str], *, terse: bool
) -> str:
    """README gets a fuller sentence for a human reader; AGENTS keeps its existing
    terser register. Both derive the same three spec facts: the code list, the default,
    and the supported/English-only split."""
    codes, default, supported, english_only = lang_facts(domains, tags)
    code_list = ", ".join(f"`{c}`" for c in codes)
    supported_list = ", ".join(f"`{d}`" for d in supported)
    english_only_list = ", ".join(f"`{d}`" for d in english_only)
    default_clause = f" Defaults to `{default}`." if default else ""
    if terse:
        note = (
            f"{len(codes)} languages: {code_list}.{default_clause} "
            f"Supported: {supported_list}. English-only: {english_only_list}."
        )
    else:
        note = (
            f"Interpretations and editorial text are available in {len(codes)} languages: "
            f"{code_list}. Pass `lang` as a keyword argument on any supported method."
            f"{default_clause} Supported: {supported_list}. English-only: {english_only_list}. "
            "Languages without translations yet fall back to English."
        )
    return f"{LANGS_BEGIN}\n{note}\n{LANGS_END}"


def sync_file(
    path: Path,
    tags: list[str],
    domains: dict[str, list[dict[str, Any]]],
    tag_objects: dict[str, dict[str, Any]],
    *,
    with_title: bool,
    terse_langs: bool,
) -> bool:
    table_changed = replace_region(
        path,
        DOMAINS_BEGIN,
        DOMAINS_END,
        render_domains_table(tags, domains, tag_objects, with_title=with_title),
    )
    langs_changed = replace_region(
        path,
        LANGS_BEGIN,
        LANGS_END,
        render_langs_block(domains, tags, terse=terse_langs),
    )
    return table_changed or langs_changed


def main() -> None:
    spec = load_spec()
    tag_objects = tag_index(spec)
    domains = group_by_tag(spec)
    tags = ordered_tags_for(spec, domains)

    readme_changed = sync_file(
        README_PATH, tags, domains, tag_objects, with_title=True, terse_langs=False
    )
    agents_changed = sync_file(
        AGENTS_PATH, tags, domains, tag_objects, with_title=False, terse_langs=True
    )

    total_endpoints = sum(len(ops) for ops in domains.values())
    print(
        f"✓ sync_docs: {len(tags)} tags, {total_endpoints} endpoints. "
        f"README {'updated' if readme_changed else 'unchanged'}, "
        f"AGENTS {'updated' if agents_changed else 'unchanged'}."
    )


if __name__ == "__main__":
    main()
