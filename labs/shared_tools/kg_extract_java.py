"""kg_extract_java — structural graph extractor for Java codebases.

Java sibling of kg_extract.py: same graph.json schema (nodes/edges with
EXTRACTED / INFERRED / AMBIGUOUS provenance), built on tree-sitter-java —
the same parser family the course teaches in M03. Deterministic: identical
source -> identical output (sorted nodes/edges, no timestamps).

Node kinds: class, interface, method, module (one per .java file)
Edge types:  calls (method_invocation), extends, implements

Provenance:
  EXTRACTED — callee defined in the same file (unambiguous local resolution)
  INFERRED  — exactly one definition of that bare name in the whole corpus
  AMBIGUOUS — 2..AMBIG_CAP definitions (Java overloads make this common;
              every candidate is emitted, honestly labeled)
  unresolved — names with more than AMBIG_CAP definitions are NOT turned into
              edges (a call to a name defined 150 times carries no structural
              signal — emitting it would be quadratic noise, not honesty).
              They are counted and reported instead. Real tools solve this
              with type resolution (M03's LSP ladder); this fallback declines
              to guess.

Usage:
    python kg_extract_java.py <repo_root> [--out graph.json] [--quiet]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import tree_sitter_java
from tree_sitter import Language, Parser

SKIP_DIRS = {".git", "build", "target", "out", ".gradle", "node_modules", "graphify-out"}
AMBIG_CAP = 8  # max candidates before a bare-name call is declared unresolved
JAVA = Language(tree_sitter_java.language())
UNRESOLVED: dict[str, int] = defaultdict(int)  # name -> dropped call count


def find_java_files(root: Path) -> list[Path]:
    return [p for p in sorted(root.rglob("*.java"))
            if not any(part in SKIP_DIRS for part in p.parts)]


def node_text(src: bytes, node) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def child_by_field(node, field: str):
    return node.child_by_field_name(field)


def extract_file(src: bytes, tree, rel: str, mod: str, nodes: dict,
                 defs_by_name: dict, raw_calls: list, raw_hier: list) -> None:
    """Walk one file's AST collecting type/method defs, calls, and hierarchy."""
    mod_id = f"module:{mod}"
    nodes[mod_id] = {"id": mod_id, "kind": "module", "name": mod, "file": rel}

    def walk(node, owner_id: str | None, owner_name: str | None):
        for child in node.children:
            kind = child.type
            if kind in ("class_declaration", "interface_declaration",
                        "enum_declaration", "record_declaration"):
                name_node = child_by_field(child, "name")
                if name_node is None:
                    continue
                name = node_text(src, name_node)
                nkind = "interface" if kind == "interface_declaration" else "class"
                tid = f"{nkind}:{mod}.{name}"
                nodes[tid] = {"id": tid, "kind": nkind, "name": name,
                              "file": rel, "line": child.start_point[0] + 1}
                defs_by_name[name][tid] = None
                sup = child_by_field(child, "superclass")
                if sup is not None:
                    for t in _type_names(src, sup):
                        raw_hier.append((tid, t, "extends"))
                ifaces = child_by_field(child, "interfaces")
                if ifaces is not None:
                    for t in _type_names(src, ifaces):
                        raw_hier.append((tid, t, "implements"))
                body = child_by_field(child, "body")
                if body is not None:
                    walk(body, tid, name)
            elif kind in ("method_declaration", "constructor_declaration"):
                name_node = child_by_field(child, "name")
                if name_node is None:
                    continue
                name = node_text(src, name_node)
                scope = f"{owner_name}." if owner_name else ""
                mid = f"method:{mod}.{scope}{name}"
                if mid not in nodes:  # overloads collapse to one node
                    nodes[mid] = {"id": mid, "kind": "method", "name": name,
                                  "file": rel, "line": child.start_point[0] + 1}
                defs_by_name[name][mid] = None
                _collect_calls(src, child, mid, raw_calls)
            else:
                walk(child, owner_id, owner_name)

    walk(tree.root_node, None, None)


def _type_names(src: bytes, node) -> list[str]:
    """Pull simple type identifiers out of a superclass/interfaces clause."""
    names = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type == "type_identifier":
            names.append(node_text(src, n))
        stack.extend(n.children)
    return names


def _collect_calls(src: bytes, method_node, caller_id: str, raw_calls: list) -> None:
    stack = list(method_node.children)
    while stack:
        n = stack.pop()
        if n.type == "method_invocation":
            name_node = child_by_field(n, "name")
            if name_node is not None:
                raw_calls.append((caller_id, node_text(src, name_node)))
        elif n.type == "object_creation_expression":
            t = child_by_field(n, "type")
            if t is not None:
                names = _type_names(src, t)
                if names:
                    raw_calls.append((caller_id, names[0]))
        stack.extend(n.children)


def owning_module(node_id: str) -> str:
    body = node_id.split(":", 1)[1]
    parts = body.split(".")
    # module path is everything before the def name (and optional Class scope)
    return ".".join(parts[:-1])


def resolve_edges(raw: list[tuple[str, str]], defs_by_name: dict,
                  edge_type: str, same_file_of: dict) -> list[dict]:
    edges = []
    for src_id, name in raw:
        candidates = list(defs_by_name.get(name, {}))
        if not candidates:
            continue  # external symbol (JDK / dependency): skipped, honestly
        if len(candidates) == 1:
            same = same_file_of.get(candidates[0]) == same_file_of.get(src_id)
            edges.append({"source": src_id, "target": candidates[0], "type": edge_type,
                          "provenance": "EXTRACTED" if same else "INFERRED"})
        elif len(candidates) <= AMBIG_CAP:
            for cand in candidates:
                edges.append({"source": src_id, "target": cand, "type": edge_type,
                              "provenance": "AMBIGUOUS"})
        else:
            UNRESOLVED[name] += 1  # too many candidates: no signal, don't guess
    return edges


def extract(root: Path, quiet: bool = False) -> dict:
    parser = Parser(JAVA)
    nodes: dict[str, dict] = {}
    defs_by_name: dict[str, dict[str, None]] = defaultdict(dict)
    raw_calls: list[tuple[str, str]] = []
    raw_hier: list[tuple[str, str, str]] = []

    files = find_java_files(root)
    for i, path in enumerate(files):
        rel = str(path.relative_to(root)).replace("\\", "/")
        mod = rel[:-len(".java")].replace("/", ".")
        try:
            src = path.read_bytes()
            tree = parser.parse(src)
        except Exception as exc:  # noqa: BLE001 - skip unreadable files loudly
            print(f"[kg_extract_java] skipping {rel}: {exc}", file=sys.stderr)
            continue
        extract_file(src, tree, rel, mod, nodes, defs_by_name, raw_calls, raw_hier)
        if not quiet and (i + 1) % 500 == 0:
            print(f"  parsed {i + 1}/{len(files)} files...", file=sys.stderr)

    same_file_of = {nid: n["file"] for nid, n in nodes.items()}
    edges = resolve_edges(raw_calls, defs_by_name, "calls", same_file_of)
    hier_raw = [(s, t) for s, t, _k in raw_hier]
    for (s, name, kind) in raw_hier:
        for e in resolve_edges([(s, name)], defs_by_name, kind, same_file_of):
            edges.append(e)
    _ = hier_raw

    # dedupe + deterministic order
    seen = set()
    unique = []
    for e in sorted(edges, key=lambda e: (e["source"], e["target"], e["type"], e["provenance"])):
        key = (e["source"], e["target"], e["type"], e["provenance"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return {"nodes": sorted(nodes.values(), key=lambda n: n["id"]), "edges": unique}


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    root = Path(args[0]).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    out = Path(args[args.index("--out") + 1]) if "--out" in args else Path("graph.json")
    quiet = "--quiet" in args

    graph = extract(root, quiet=quiet)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    kinds: dict[str, int] = defaultdict(int)
    for n in graph["nodes"]:
        kinds[n["kind"]] += 1
    prov: dict[str, int] = defaultdict(int)
    for e in graph["edges"]:
        prov[e["provenance"]] += 1
    print(f"Rebuilt: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges -> {out}")
    print(f"  nodes: {dict(sorted(kinds.items()))}")
    print(f"  edges: {dict(sorted(prov.items()))}")
    if UNRESOLVED:
        dropped = sum(UNRESOLVED.values())
        top = sorted(UNRESOLVED.items(), key=lambda kv: -kv[1])[:5]
        print(f"  unresolved: {dropped} calls to {len(UNRESOLVED)} over-ambiguous names "
              f"(> {AMBIG_CAP} candidates) dropped, e.g. {[n for n, _ in top]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
