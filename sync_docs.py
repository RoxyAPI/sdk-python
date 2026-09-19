#!/usr/bin/env python3
"""
Regenerate the spec-derived docs in README.md and AGENTS.md:
  - The domain table (`<!-- BEGIN:DOMAINS -->` markers): one row per spec tag, in spec
    tag order, showing the `roxy.<namespace>` property and its method count.
  - The multi-language note (`<!-- BEGIN:LANGS -->` markers): the `lang` enum values and
    which domains take a `lang` query param, replacing hand-typed language lists.

Run with: python sync_docs.py (also runs automatically at the end of generate.py)

The OpenAPI spec is the single source of truth. Adding a new API domain requires NO
manual doc edit: the domain walk is codegen.domains(), the same one the generator uses,
and the README title column is the tag name of the spec. Fails loudly only if:
  - README.md / AGENTS.md is missing its BEGIN/END markers.
  - The `lang` parameter is declared with different enums or defaults across operations.
"""

from __future__ import annotations

from pathlib import Path

from codegen import ROOT, Domain, domains, fail, load_spec

README_PATH = ROOT / "README.md"
AGENTS_PATH = ROOT / "AGENTS.md"

DOMAINS_BEGIN = "<!-- BEGIN:DOMAINS -->"
DOMAINS_END = "<!-- END:DOMAINS -->"
LANGS_BEGIN = "<!-- BEGIN:LANGS -->"
LANGS_END = "<!-- END:LANGS -->"


def replace_region(path: Path, begin: str, end: str, block: str) -> bool:
    src = path.read_text()
    begin_idx = src.find(begin)
    end_idx = src.find(end)
    if begin_idx == -1 or end_idx == -1 or end_idx < begin_idx:
        fail(f"sync_docs: {path.relative_to(ROOT)} is missing {begin} / {end} markers")
    next_src = src[:begin_idx] + block + src[end_idx + len(end) :]
    if next_src == src:
        return False
    path.write_text(next_src)
    return True


def render_domains_table(all_domains: list[Domain], *, with_title: bool) -> str:
    """Render the domain table for either file: README carries the spec tag name as a
    human-facing "Domain" column ahead of the property; AGENTS starts at the namespace."""
    if with_title:
        header = ["Domain", "Property", "Methods", "What it covers"]
        sep = ["--------", "----------", "---------", "----------------"]
    else:
        header = ["Namespace", "Methods", "What it covers"]
        sep = ["-----------", "---------", "----------------"]
    rows = [f"| {' | '.join(header)} |", f"|{'|'.join(sep)}|"]
    for domain in all_domains:
        cells = [f"`roxy.{domain.attr}`", str(len(domain.operations)), domain.summary]
        if with_title:
            cells.insert(0, domain.tag)
        rows.append(f"| {' | '.join(cells)} |")
    return "\n".join([DOMAINS_BEGIN, *rows, DOMAINS_END])


def lang_facts(all_domains: list[Domain]) -> tuple[list[str], str | None, list[str], list[str]]:
    """The `lang` enum, its default, and which domains take it. The spec declares the
    parameter once per operation, so every declaration must agree."""
    enums: set[tuple[str, ...]] = set()
    defaults: set[str] = set()
    supports_lang: set[str] = set()
    for domain in all_domains:
        for op in domain.operations:
            for p in op["parameters"]:
                if p.get("name") != "lang" or p.get("in") != "query":
                    continue
                supports_lang.add(domain.attr)
                schema = p.get("schema", {})
                enums.add(tuple(schema.get("enum", [])))
                if schema.get("default") is not None:
                    defaults.add(str(schema["default"]))
    if len(enums) != 1 or len(defaults) > 1:
        fail(f"sync_docs: lang declared inconsistently: {sorted(enums)} / {sorted(defaults)}")
    supported = [d.attr for d in all_domains if d.attr in supports_lang]
    english_only = [d.attr for d in all_domains if d.attr not in supports_lang]
    return list(enums.pop()), next(iter(defaults), None), supported, english_only


def render_langs_block(all_domains: list[Domain], *, terse: bool) -> str:
    """README gets a fuller sentence for a human reader; AGENTS keeps its existing
    terser register. Both derive the same three spec facts: the code list, the default,
    and the supported/English-only split."""
    codes, default, supported, english_only = lang_facts(all_domains)
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
    path: Path, all_domains: list[Domain], *, with_title: bool, terse_langs: bool
) -> bool:
    table_changed = replace_region(
        path, DOMAINS_BEGIN, DOMAINS_END, render_domains_table(all_domains, with_title=with_title)
    )
    langs_changed = replace_region(
        path, LANGS_BEGIN, LANGS_END, render_langs_block(all_domains, terse=terse_langs)
    )
    return table_changed or langs_changed


def main() -> None:
    all_domains = domains(load_spec())

    readme_changed = sync_file(README_PATH, all_domains, with_title=True, terse_langs=False)
    agents_changed = sync_file(AGENTS_PATH, all_domains, with_title=False, terse_langs=True)

    total_endpoints = sum(len(d.operations) for d in all_domains)
    print(
        f"✓ sync_docs: {len(all_domains)} tags, {total_endpoints} endpoints. "
        f"README {'updated' if readme_changed else 'unchanged'}, "
        f"AGENTS {'updated' if agents_changed else 'unchanged'}."
    )


if __name__ == "__main__":
    main()
