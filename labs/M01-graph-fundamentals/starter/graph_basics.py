"""M01 starter — build graph queries over orderflow. Fill in the TODOs."""
import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]


def load_graph() -> dict:
    """Run the course extractor over sample-project and load graph.json."""
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
    """'function:shared.auth.decode_jwt' -> 'decode_jwt'"""
    return node_id.rsplit(".", 1)[-1]


def build_reverse_index(graph: dict) -> dict[str, list[dict]]:
    """TODO 1: return {target_id: [edge, ...]} for all 'calls' edges."""
    reverse: dict[str, list[dict]] = defaultdict(list)
    # TODO: loop over graph["edges"], append each edge under its target
    raise NotImplementedError("TODO 1")


def callers(graph: dict, name: str, reverse: dict) -> list[str]:
    """Direct callers (short names) of the first node whose short name == name."""
    targets = [n["id"] for n in graph["nodes"] if short(n["id"]) == name]
    found = []
    for t in targets:
        for edge in reverse.get(t, []):
            found.append(short(edge["source"]))
    return sorted(set(found))


def blast_radius(graph: dict, name: str, reverse: dict,
                 min_confidence: str | None = None) -> list[str]:
    """TODO 2 + 3: every function transitively depending on `name`.

    BFS over the REVERSE index. If min_confidence == "EXTRACTED", skip
    INFERRED/AMBIGUOUS edges (TODO 3).
    """
    # TODO: seed a deque with all node ids whose short name == name,
    #       walk reverse edges, collect visited callers.
    raise NotImplementedError("TODO 2")


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
