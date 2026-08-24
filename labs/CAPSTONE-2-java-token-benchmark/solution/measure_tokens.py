"""measure_tokens — CAPSTONE-2 benchmark: exploration vs graph, in tokens.

For each structural question "who calls <symbol>?" it measures both arms:

  BASELINE (simulated agent exploration)
    grep for the CALL-SITE pattern `\bsymbol(` across the repo (what a
    competent agent actually greps — not the bare name, which over-matches
    comments and longer identifiers); the agent must open every matching
    file to confirm which hits are real call sites and who contains them.
    Cost charged: the full size of each matched file (files enter context
    whole), tokens ~= bytes / 4. Ops = files opened. This is the mechanical,
    model-independent floor of what a CORRECT exploration costs.

  GRAPH (one MCP tool call)
    The answer returned by graph_callers()/explore() over a pre-built
    graph.json, plus a one-time per-session orientation read (~700 tokens,
    the GRAPH_SUMMARY.md pattern) amortized across the question count.
    Ops = 1 tool call.

Symbols are auto-selected from the graph (deterministic): the most-CALLED
resolvable method names — structurally relevant questions a developer would
actually ask — NOT the most grep-expensive ones. Selecting by grep expense
would manufacture a ceiling case, which is exactly the benchmark sin the
course teaches you to spot. Override with --symbols name1,name2,...

Honesty notes printed with every run:
  - the baseline assumes an agent confirms EVERY grep hit; a lazy agent reads
    fewer files, saves tokens, and risks a wrong answer — that tradeoff is
    the point of the course, not a flaw in the measurement.
  - reductions scale with repo size (M05): expect modest numbers on small
    repos and large ones on monorepos.

Usage:
    python measure_tokens.py <repo_root> <graph.json> [--questions 8]
                             [--symbols a,b,c] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ORIENTATION_TOKENS = 700  # one-time architectural summary read, per session
SKIP_DIRS = {".git", "build", "target", "out", ".gradle", "node_modules", "graphify-out"}


def tokens(nbytes: int) -> int:
    return max(1, nbytes // 4)


def load_graph(path: Path) -> tuple[dict, dict, dict]:
    graph = json.loads(path.read_text(encoding="utf-8"))
    reverse: dict[str, list[dict]] = defaultdict(list)
    by_short: dict[str, list[str]] = defaultdict(list)
    for e in graph["edges"]:
        reverse[e["target"]].append(e)
    for n in graph["nodes"]:
        by_short[n["id"].rsplit(".", 1)[-1]].append(n["id"])
    return graph, reverse, by_short


def graph_answer(symbol: str, reverse: dict, by_short: dict) -> dict:
    node_ids = by_short.get(symbol, [])
    callers = sorted({e["source"].split(":", 1)[1]
                      for nid in node_ids for e in reverse.get(nid, [])})
    if not callers:
        return {"symbol": symbol, "error": "not resolvable in graph — fall back to grep"}
    return {"symbol": symbol, "callers": callers,
            "provenance": sorted({e["provenance"] for nid in node_ids
                                  for e in reverse.get(nid, [])})}


def source_files(repo: Path) -> list[Path]:
    return [p for p in repo.rglob("*.java")
            if not any(part in SKIP_DIRS for part in p.parts)]


def callsite_pattern(symbol: str):
    import re
    return re.compile(rb"\b" + re.escape(symbol.encode()) + rb"\s*\(")


def baseline_cost(symbol: str, files: list[Path],
                  contents: dict[Path, bytes]) -> tuple[int, int]:
    """(tokens, files_opened) to confirm every call-site grep hit for symbol."""
    pattern = callsite_pattern(symbol)
    total, opened = 0, 0
    for f in files:
        body = contents[f]
        if pattern.search(body):
            opened += 1
            total += tokens(len(body))
    return total, opened


def auto_select(by_short: dict, reverse: dict, files: list[Path],
                contents: dict[Path, bytes], k: int) -> list[str]:
    """Deterministically pick k measurable symbols by CALLER COUNT (structural
    relevance), requiring only that grep finds >= 3 call-site files. Name
    length > 4 skips get/add-style universals."""
    # rank by caller count FIRST, then grep only the top candidates —
    # grepping every name in a 9,000-file repo is O(names x files) and takes
    # forever (ask us how we know).
    ranked = []
    for short, node_ids in by_short.items():
        if len(short) <= 4 or not short[0].islower():
            continue
        caller_count = sum(len(reverse.get(nid, [])) for nid in node_ids)
        if caller_count >= 2:
            ranked.append((caller_count, short))
    ranked.sort(key=lambda t: (-t[0], t[1]))

    picked: list[str] = []
    for _count, short in ranked[: max(k * 10, 50)]:
        pattern = callsite_pattern(short)
        grep_hits = sum(1 for f in files if pattern.search(contents[f]))
        if grep_hits >= 3:
            picked.append(short)
            if len(picked) == k:
                break
    return picked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", type=Path)
    ap.add_argument("graph", type=Path)
    ap.add_argument("--questions", type=int, default=8)
    ap.add_argument("--symbols", default=None, help="comma-separated override")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not repo.is_dir() or not args.graph.exists():
        print("error: repo dir or graph.json missing", file=sys.stderr)
        return 2

    print(f"Loading graph {args.graph} ...")
    graph, reverse, by_short = load_graph(args.graph)
    print(f"  {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")

    print(f"Reading corpus {repo} ...")
    files = source_files(repo)
    contents = {f: f.read_bytes() for f in files}
    corpus_tokens = sum(tokens(len(b)) for b in contents.values())
    print(f"  {len(files)} Java files, ~{corpus_tokens:,} tokens total")

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = auto_select(by_short, reverse, files, contents, args.questions)
    if not symbols:
        print("error: no measurable symbols found", file=sys.stderr)
        return 1

    rows = []
    for sym in symbols:
        answer = graph_answer(sym, reverse, by_short)
        b_tokens, b_ops = baseline_cost(sym, files, contents)
        if "error" in answer:
            rows.append({"symbol": sym, "skipped": True})
            continue
        g_tokens = tokens(len(json.dumps(answer))) + ORIENTATION_TOKENS // len(symbols)
        rows.append({
            "symbol": sym, "skipped": False,
            "baseline_tokens": b_tokens, "baseline_ops": b_ops,
            "graph_tokens": g_tokens, "graph_ops": 1,
            "callers_found": len(answer["callers"]),
            "reduction_pct": round(100 * (1 - g_tokens / b_tokens), 1) if b_tokens else 0.0,
            "multiple": round(b_tokens / g_tokens, 1) if g_tokens else 0.0,
        })

    measured = [r for r in rows if not r["skipped"]]
    print()
    print(f"{'who calls ...?':<24} {'files':>5} {'baseline tok':>12} {'graph tok':>9} "
          f"{'reduction':>9} {'multiple':>8}")
    print("-" * 74)
    for r in rows:
        if r["skipped"]:
            print(f"{r['symbol']:<24} {'—':>5} {'(unresolvable: graph declines to guess)':>40}")
            continue
        print(f"{r['symbol']:<24} {r['baseline_ops']:>5} {r['baseline_tokens']:>12,} "
              f"{r['graph_tokens']:>9,} {r['reduction_pct']:>8.1f}% {r['multiple']:>7.1f}x")
    if measured:
        tb = sum(r["baseline_tokens"] for r in measured)
        tg = sum(r["graph_tokens"] for r in measured)
        ob = sum(r["baseline_ops"] for r in measured)
        print("-" * 74)
        print(f"{'AGGREGATE':<24} {ob:>5} {tb:>12,} {tg:>9,} "
              f"{100 * (1 - tg / tb):>8.1f}% {tb / tg:>7.1f}x")
        print()
        print("HOW TO READ THIS (the Honesty Rule):")
        print(f"  * These are PER-QUESTION multiples for pure structural lookups — the "
              f"same class of number as okf-rs's published ~400x per query.")
        print(f"  * SESSION-level savings are far lower (replications: 6.8x-49x; "
              f"CodeGraph task benchmarks: OkHttp 645 files -> 13%, Django ~3,000 -> 36%, "
              f"VS Code ~10,000 -> 78%) because sessions also spend tokens on reasoning, "
              f"edits, and non-structural reads that a graph cannot remove.")
        print(f"  * Repo size here: {len(files)} files. The exploration burden (files "
              f"opened per question: {ob / max(1, len(measured)):.0f} avg) grows with the "
              f"haystack — compare your runs across repo sizes.")
        print("  * Baseline assumes the agent confirms EVERY grep hit — the honest floor "
              "for a CORRECT answer, not what a lazy (and wrong) agent spends.")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps({
            "repo": str(repo), "files": len(files), "corpus_tokens": corpus_tokens,
            "rows": rows}, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
