# -*- coding: utf-8 -*-
"""Retire the hand-written .term-tooltip definitions in favour of the corpus.

The convention was right and its limit was structural: a tooltip defines a word
in the module that happens to carry it, and nowhere else. OKF was expanded in
M05 while M10 used it fifty-five times and defined it nowhere; six words were
defined two different ways in two different modules, free to drift.

domain/corpus.json now holds those definitions — 43 of them harvested from
these very tooltips, so the wording is unchanged — and the shared runtime links
the first use of each word in every page. This removes the duplicates.

Refuses to unwrap a tooltip whose term resolves nowhere in the corpus: that
would delete a definition rather than move it. Run --check first.

Usage:
    python domain/retire_tooltips.py --check
    python domain/retire_tooltips.py
"""
from __future__ import annotations

import html as htmlmod
import io
import json
import re
import sys
from pathlib import Path

CORPUS = Path("domain/corpus.json")
PAGES = Path("output")

# <span class="term-tooltip" …>TERM<span class="tooltip-content" …>DEF</span></span>
TOOLTIP = re.compile(
    r'<span[^>]*class="[^"]*\bterm-tooltip\b[^"]*"[^>]*>'
    r'(?P<term>(?:(?!<span)[\s\S])*?)'
    r'<span[^>]*class="[^"]*\btooltip-content\b[^"]*"[^>]*>'
    r'(?P<def>[\s\S]*?)</span>\s*</span>',
    re.I,
)


def plain(fragment: str) -> str:
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def load_forms() -> dict[str, str]:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    forms = {}
    for entry in corpus["glossary"]:
        for form in [entry["term"]] + list(entry.get("match") or []):
            forms[form.lower()] = entry["term"]
    return forms


def resolves(term: str, forms: dict[str, str]) -> str | None:
    key = term.lower()
    for candidate in (key, key.rstrip("s"), key + "s"):
        if candidate in forms:
            return forms[candidate]
    return None


def main() -> int:
    check = "--check" in sys.argv
    forms = load_forms()

    total = kept = removed = 0
    unresolved: list[tuple[str, str]] = []

    for path in sorted(PAGES.glob("*.html")):
        raw = io.open(path, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in raw else "\n"
        src = raw.replace("\r\n", "\n")
        n_before = len(TOOLTIP.findall(src))
        if not n_before:
            continue
        total += n_before

        def unwrap(m: re.Match) -> str:
            nonlocal kept, removed
            term = plain(m.group("term"))
            if not resolves(term, forms):
                unresolved.append((path.name, term))
                kept += 1
                return m.group(0)          # a definition that lives nowhere else stays
            removed += 1
            return m.group("term")         # keep the words, drop the wrapper

        out = TOOLTIP.sub(unwrap, src)
        if not check and out != src:
            io.open(path, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))
        print(f"  {path.name}: {n_before} tooltip(s)")

    print(f"\n{total} tooltip(s): {removed} retired, {kept} kept")
    for page, term in unresolved:
        print(f"  KEPT {term!r} in {page} — no corpus entry, so unwrapping would lose it")
    if check:
        print("--check: nothing written")
    return 1 if kept else 0


if __name__ == "__main__":
    sys.exit(main())
