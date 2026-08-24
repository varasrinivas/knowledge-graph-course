"""M09 starter — MCP server over orderflow's structural graph. Fill in the TODOs."""
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


def load_graph() -> dict:
    """Build graph.json from sample-project and index it. Called once at startup."""
    global _graph, _reverse, _forward
    out = Path(__file__).parent / "graph.json"
    result = subprocess.run(
        [sys.executable, str(LABS / "shared_tools" / "kg_extract.py"),
         str(LABS / "sample-project"), "--out", str(out)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"extractor failed:\n{result.stderr}")
    _graph = json.loads(out.read_text(encoding="utf-8"))
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
    """TODO 1: resolve symbol; on miss return {'error': '... try grep'};
    otherwise {'symbol': symbol, 'callers': sorted unique short names}."""
    raise NotImplementedError("TODO 1")


def graph_callees(symbol: str) -> dict:
    """TODO 2: same shape as graph_callers, using the FORWARD index."""
    raise NotImplementedError("TODO 2")


def explore(symbol: str) -> dict:
    """TODO 3: composite answer — kind, file:line, callers, callees,
    transitive blast_radius (BFS over _reverse), ambiguous flag."""
    raise NotImplementedError("TODO 3")


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


def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("orderflow-graph")
    mcp.tool()(graph_callers)
    mcp.tool()(graph_callees)
    mcp.tool()(explore)
    load_graph()
    print("orderflow-graph: serving graph.json over stdio", file=sys.stderr)
    mcp.run()  # stdio transport


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    serve()
