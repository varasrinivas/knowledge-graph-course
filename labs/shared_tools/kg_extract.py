"""kg_extract — pure-Python structural graph extractor (offline fallback).

Builds a Graphify-style graph.json from a Python codebase using only the
standard library `ast` module. Deterministic: identical source -> identical
output (nodes and edges are sorted, no timestamps).

Every edge carries a provenance tag:
  EXTRACTED  — the call target is defined in the scanned codebase and the
               name resolves unambiguously.
  INFERRED   — the name matches exactly one definition but was resolved by
               bare-name matching (no import following), so it is a guess.
  AMBIGUOUS  — the name matches multiple definitions; all candidates emitted.

Usage:
    python kg_extract.py <repo_root> [--out graph.json]
"""
from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "graphify-out"}


def find_python_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*.py")):
        if not any(part in SKIP_DIRS for part in path.parts):
            files.append(path)
    return files


def module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def extract(root: Path) -> dict:
    nodes: dict[str, dict] = {}
    raw_calls: list[tuple[str, str]] = []  # (caller_id, callee_bare_name)
    defs_by_name: dict[str, dict[str, None]] = defaultdict(dict)  # name -> {node_id: None} (ordered set)

    for path in find_python_files(root):
        mod = module_name(root, path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            print(f"[kg_extract] skipping {path}: {exc}", file=sys.stderr)
            continue

        mod_id = f"module:{mod}"
        nodes[mod_id] = {"id": mod_id, "kind": "module", "name": mod,
                         "file": str(path.relative_to(root)).replace("\\", "/")}

        for item in ast.walk(tree):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_id = f"function:{mod}.{item.name}"
                nodes[fn_id] = {"id": fn_id, "kind": "function", "name": item.name,
                                "file": nodes[mod_id]["file"], "line": item.lineno}
                defs_by_name[item.name][fn_id] = None
                for call in ast.walk(item):
                    if isinstance(call, ast.Call):
                        callee = _call_name(call.func)
                        if callee:
                            raw_calls.append((fn_id, callee))
            elif isinstance(item, ast.ClassDef):
                cls_id = f"class:{mod}.{item.name}"
                nodes[cls_id] = {"id": cls_id, "kind": "class", "name": item.name,
                                 "file": nodes[mod_id]["file"], "line": item.lineno}
                defs_by_name[item.name][cls_id] = None

    edges = []
    for caller, callee_name in raw_calls:
        candidates = list(defs_by_name.get(callee_name, {}))
        if len(candidates) == 1:
            def owning_module(node_id: str) -> str:
                return node_id.split(":", 1)[1].rsplit(".", 1)[0]
            same_mod = owning_module(candidates[0]) == owning_module(caller)
            edges.append({"source": caller, "target": candidates[0], "type": "calls",
                          "provenance": "EXTRACTED" if same_mod else "INFERRED"})
        elif len(candidates) > 1:
            for cand in candidates:
                edges.append({"source": caller, "target": cand, "type": "calls",
                              "provenance": "AMBIGUOUS"})
        # names with zero candidates are external (stdlib / third-party): skipped

    edges.sort(key=lambda e: (e["source"], e["target"], e["provenance"]))
    return {"nodes": sorted(nodes.values(), key=lambda n: n["id"]), "edges": edges}


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else Path("graph.json")

    graph = extract(root)
    # --out graphify-out/graph.json is the documented shape (M11, capstone), so
    # create the directory rather than dying with a bare FileNotFoundError.
    if out.parent != Path("") and not out.parent.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    kinds = defaultdict(int)
    for n in graph["nodes"]:
        kinds[n["kind"]] += 1
    prov = defaultdict(int)
    for e in graph["edges"]:
        prov[e["provenance"]] += 1
    print(f"Rebuilt: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges -> {out}")
    print(f"  nodes: {dict(sorted(kinds.items()))}")
    print(f"  edges: {dict(sorted(prov.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
