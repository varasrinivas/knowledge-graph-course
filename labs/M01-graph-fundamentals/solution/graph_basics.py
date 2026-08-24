"""M01 solution — graph queries over orderflow."""
import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]


def load_graph() -> dict:
    out = Path(__file__).parent / "graph.json"
    result = subprocess.run(
        [sys.executable, str(LABS / "shared_tools" / "kg_extract.py"),
         str(LABS / "sample-project"), "--out", str(out)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"extractor failed:\n{result.stderr}")
    return json.loads(out.read_text(encoding="utf-8"))


def short(node_id: str) -> str:
    return node_id.rsplit(".", 1)[-1]


def build_reverse_index(graph: dict) -> dict[str, list[dict]]:
    reverse: dict[str, list[dict]] = defaultdict(list)
    for edge in graph["edges"]:
        if edge["type"] == "calls":
            reverse[edge["target"]].append(edge)
    return reverse


def callers(graph: dict, name: str, reverse: dict) -> list[str]:
    targets = [n["id"] for n in graph["nodes"] if short(n["id"]) == name]
    found = []
    for t in targets:
        for edge in reverse.get(t, []):
            found.append(short(edge["source"]))
    return sorted(set(found))


def blast_radius(graph: dict, name: str, reverse: dict,
                 min_confidence: str | None = None) -> list[str]:
    seeds = [n["id"] for n in graph["nodes"] if short(n["id"]) == name]
    queue = deque(seeds)
    visited: set[str] = set(seeds)
    impacted: set[str] = set()
    while queue:
        node = queue.popleft()
        for edge in reverse.get(node, []):
            if min_confidence == "EXTRACTED" and edge["provenance"] != "EXTRACTED":
                continue
            src = edge["source"]
            if src not in visited:
                visited.add(src)
                impacted.add(short(src))
                queue.append(src)
    return sorted(impacted)


def main() -> None:
    graph = load_graph()
    print(f"{len(graph['nodes'])} nodes, {len(graph['edges'])} edges loaded")

    if "--check" not in sys.argv:
        return

    reverse = build_reverse_index(graph)
    checks = [
        ("callers(decode_jwt)", callers(graph, "decode_jwt", reverse), ["verify_token"]),
        ("blast_radius(decode_jwt) contains post_invoice",
         "post_invoice" in blast_radius(graph, "decode_jwt", reverse), True),
        ("EXTRACTED-only radius is smaller or equal",
         len(blast_radius(graph, "execute", reverse, "EXTRACTED"))
         <= len(blast_radius(graph, "execute", reverse)), True),
    ]
    ok = True
    for label, got, want in checks:
        status = "PASS" if got == want else f"FAIL (got {got!r}, want {want!r})"
        ok &= got == want
        print(f"  [{status}] {label}")
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")


if __name__ == "__main__":
    main()
