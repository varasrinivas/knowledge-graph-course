"""M09 solution — MCP server over a structural graph.

Default: extracts and serves orderflow (labs/sample-project).
Any other codebase: pass --graph <path/to/graph.json> to serve a pre-built
graph (e.g. one produced by kg_extract_java.py for CAPSTONE-2's Java repos).

Run under an MCP client (stdio), or `python server.py --selftest` standalone.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]
_graph: dict | None = None
_reverse: dict[str, list[dict]] = {}
_forward: dict[str, list[dict]] = {}


def load_graph(graph_path: Path | None = None) -> dict:
    """Index a graph. Default: extract sample-project; else load graph_path.

    NOTE (M11): this runs ONCE at startup. If the graph.json on disk is
    regenerated later, this server keeps serving the old one until restarted.
    """
    global _graph, _reverse, _forward
    if graph_path is None:
        out = Path(__file__).parent / "graph.json"
        result = subprocess.run(
            [sys.executable, str(LABS / "shared_tools" / "kg_extract.py"),
             str(LABS / "sample-project"), "--out", str(out)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"extractor failed:\n{result.stderr}")
        graph_path = out
    _graph = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    _reverse, _forward = defaultdict(list), defaultdict(list)
    for edge in _graph["edges"]:
        _reverse[edge["target"]].append(edge)
        _forward[edge["source"]].append(edge)
    return _graph


def _resolve(symbol: str) -> list[dict]:
    assert _graph is not None
    return [n for n in _graph["nodes"]
            if n["id"].rsplit(".", 1)[-1] == symbol or n["id"] == symbol]


def _short(node_id: str) -> str:
    return node_id.split(":", 1)[1]


def graph_callers(symbol: str) -> dict:
    nodes = _resolve(symbol)
    if not nodes:
        return {"error": f"symbol {symbol!r} not in graph — it may be external; try grep"}
    callers = sorted({_short(e["source"]) for n in nodes for e in _reverse.get(n["id"], [])})
    return {"symbol": symbol, "callers": callers}


def graph_callees(symbol: str) -> dict:
    nodes = _resolve(symbol)
    if not nodes:
        return {"error": f"symbol {symbol!r} not in graph — it may be external; try grep"}
    callees = sorted({_short(e["target"]) for n in nodes for e in _forward.get(n["id"], [])})
    return {"symbol": symbol, "callees": callees}


def explore(symbol: str) -> dict:
    """Composite: whole structural picture in one call."""
    nodes = _resolve(symbol)
    if not nodes:
        return {"error": f"symbol {symbol!r} not in graph — it may be external; try grep"}
    node = nodes[0]
    seen: set[str] = {n["id"] for n in nodes}
    queue = deque(seen)
    while queue:  # transitive blast radius over the reverse index
        for edge in _reverse.get(queue.popleft(), []):
            if edge["source"] not in seen:
                seen.add(edge["source"])
                queue.append(edge["source"])
    return {
        "symbol": symbol,
        "kind": node["kind"],
        "location": f"{node['file']}:{node.get('line', '?')}",
        "callers": graph_callers(symbol).get("callers", []),
        "callees": graph_callees(symbol).get("callees", []),
        "blast_radius": len(seen) - len(nodes),
        "ambiguous": len(nodes) > 1,
    }


def selftest() -> int:
    load_graph()
    for call, expect in [
        (graph_callers("decode_jwt"), {"callers": ["shared.auth.verify_token"]}),
        (graph_callees("handle_payment_webhook"), None),
        (explore("decode_jwt"), None),
        (graph_callers("not_a_symbol"), None),
    ]:
        print(json.dumps(call, indent=2))
        if expect and not all(call.get(k) == v for k, v in expect.items()):
            print("SELFTEST FAILED", file=sys.stderr)
            return 1
    print("SELFTEST PASSED")
    return 0


def serve(graph_path: Path | None = None) -> None:
    # MCP SDK 2.x renamed FastMCP; support both generations so the lab
    # doesn't silently break on a fresh `pip install mcp` (ask us how we know:
    # a crashed server under an MCP client looks like "tools not available",
    # not like an error — the M11 silent-failure lesson, again).
    try:
        from mcp.server import MCPServer as ServerClass  # SDK 2.x
    except ImportError:
        from mcp.server.fastmcp import FastMCP as ServerClass  # SDK 1.x

    name = "orderflow-graph" if graph_path is None else f"graph:{graph_path.stem}"
    mcp = ServerClass(name)
    mcp.tool()(graph_callers)
    mcp.tool()(graph_callees)
    mcp.tool()(explore)
    load_graph(graph_path)
    print(f"{name}: serving over stdio "
          f"({len(_graph['nodes'])} nodes, {len(_graph['edges'])} edges)", file=sys.stderr)
    mcp.run()  # stdio transport


if __name__ == "__main__":
    graph_arg = None
    if "--graph" in sys.argv:
        graph_arg = Path(sys.argv[sys.argv.index("--graph") + 1]).resolve()
        if not graph_arg.exists():
            print(f"error: {graph_arg} not found — build it first", file=sys.stderr)
            raise SystemExit(2)
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    serve(graph_arg)
