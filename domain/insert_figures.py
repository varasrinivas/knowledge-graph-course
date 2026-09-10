# -*- coding: utf-8 -*-
"""Insert domain/figures.json into the module pages.

These pages are hand-authored HTML with no data array, so a figure is inserted
directly: a <section id="worked-example"> after the page's objectives section —
after the reader has been told what the module is for, before it starts
teaching — plus the matching sidebar link, because this course's own checklist
requires every section to be reachable from the nav.

Idempotent: a page already carrying id="worked-example" has its figure
replaced, not duplicated, so re-running after editing figures.json is safe.

Styling comes from ../shared/figure; run its build.py to inline the stylesheet.

Usage:
    python domain/insert_figures.py
    python domain/insert_figures.py --check
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

FIGURES = Path("domain/figures.json")
PAGES = Path("output")
SECTION_ID = "worked-example"
NAV_LABEL = "On the codebase"

# Where the figure goes, in order of preference. Every module page has
# `objectives`; the pipeline capstone opens with `brief` instead.
ANCHORS = ("objectives", "brief")


def section(fig: dict) -> str:
    return (
        f'<section class="section" id="{SECTION_ID}">\n'
        f'<div class="ue-fig">\n'
        f'<div class="ue-label">◫ On the codebase</div>\n'
        f'<div class="ue-title">{fig["title"]}</div>\n'
        f'<div class="ue-body">{fig["body"]}</div>\n'
        f'<div class="ue-cap">{fig["caption"]}</div>\n'
        f'</div>\n'
        f'</section>\n'
    )


def end_of_section(html: str, section_id: str) -> int | None:
    """Index just past the closing </section> of the named section."""
    m = re.search(r'<section[^>]*id="%s"' % re.escape(section_id), html)
    if not m:
        return None
    depth = 0
    for tag in re.finditer(r"</?section\b", html[m.start():]):
        depth += 1 if tag.group(0) == "<section" else -1
        if depth == 0:
            close = re.compile(r"</section\s*>").search(html, m.start() + tag.start())
            return close.end() if close else None
    return None


def apply(path: Path, fig: dict) -> str:
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    html = raw.replace("\r\n", "\n")

    # strip any previous figure so a rebuild replaces rather than stacks
    existing = re.search(r'<section[^>]*id="%s".*?</section>\s*' % SECTION_ID, html, re.S)
    if existing:
        html = html[:existing.start()] + html[existing.end():]

    at = None
    for anchor in ANCHORS:
        at = end_of_section(html, anchor)
        if at:
            break
    if not at:
        return f"SKIPPED — no {' or '.join(ANCHORS)} section"

    html = html[:at] + "\n\n" + section(fig) + html[at:]

    # and the sidebar entry, right after the anchor's own link
    if f'href="#{SECTION_ID}"' not in html:
        nav = re.search(r'(<a href="#(?:%s)">[^<]*</a>)' % "|".join(ANCHORS), html)
        if nav:
            html = (html[:nav.end()] + f'\n  <a href="#{SECTION_ID}">{NAV_LABEL}</a>'
                    + html[nav.end():])

    io.open(path, "w", encoding="utf-8", newline="").write(html.replace("\n", nl))
    return "replaced" if existing else "inserted"


def main() -> int:
    check = "--check" in sys.argv
    figures = {k: v for k, v in json.loads(FIGURES.read_text(encoding="utf-8")).items()
               if not k.startswith("_")}

    # Longest prefix wins, or the CAPSTONE key would also claim CAPSTONE-2's
    # page and overwrite its figure with the wrong one.
    def pages_for(key: str) -> list[Path]:
        out = []
        for path in sorted(PAGES.glob("*.html")):
            owner = max((k for k in figures if path.name.startswith(k + "-")),
                        key=len, default=None)
            if owner == key:
                out.append(path)
        return out

    done = 0
    for key, fig in sorted(figures.items()):
        hits = pages_for(key)
        if not hits:
            print(f"  ! {key}: no page matches {key}-*.html")
            continue
        for path in hits:
            if check:
                print(f"  would update {path}")
                done += 1
                continue
            result = apply(path, fig)
            print(f"  {result:9} {path}")
            if not result.startswith("SKIPPED"):
                done += 1

    print(f"{done} of {len(figures)} figure(s) placed")
    return 0 if done == len(figures) else 1


if __name__ == "__main__":
    sys.exit(main())
