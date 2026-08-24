"""M11 solution — CI freshness gate for the structural graph.

Checks, mechanically:
  1. graph.json exists
  2. graph.json is not older than HEAD by more than --max-age-commits commits
  3. (--cross-check) node/edge counts match a fresh extraction

Exit 0 = fresh; exit 1 = stale/desynced (block the pipeline); exit 2 = usage.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]


def sh(args: list[str], cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def commits_since(repo: Path, epoch: int) -> int:
    out = sh(["git", "rev-list", "--count", f"--since={epoch}", "HEAD"], cwd=repo)
    return int(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", type=Path)
    ap.add_argument("--graph", default="graphify-out/graph.json")
    ap.add_argument("--max-age-commits", type=int, default=0,
                    help="how many commits the graph may lag HEAD (default 0)")
    ap.add_argument("--cross-check", action="store_true",
                    help="verify stored counts against a fresh extraction")
    args = ap.parse_args()

    repo = args.repo.resolve()
    graph_path = repo / args.graph
    if not graph_path.exists():
        print(f"STALE: {graph_path} does not exist — run the extractor")
        return 1

    graph_mtime = int(graph_path.stat().st_mtime)
    head_time = int(sh(["git", "log", "-1", "--format=%ct"], cwd=repo))

    if graph_mtime >= head_time:
        print("FRESH: graph.json generated at/after HEAD commit")
        lag = 0
    else:
        lag = commits_since(repo, graph_mtime)
        if lag > args.max_age_commits:
            print(f"STALE: graph.json predates HEAD by {lag} commit(s)")
            print(f"  fix: python {LABS / 'shared_tools' / 'kg_extract.py'} {repo} "
                  f"--out {graph_path}  (then restart any MCP server holding the old graph)")
            return 1
        print(f"FRESH ENOUGH: lags HEAD by {lag} commit(s), within --max-age-commits={args.max_age_commits}")

    if args.cross_check:
        stored = json.loads(graph_path.read_text(encoding="utf-8"))
        fresh_out = graph_path.with_suffix(".freshcheck.json")
        try:
            sh([sys.executable, str(LABS / "shared_tools" / "kg_extract.py"),
                str(repo), "--out", str(fresh_out)], cwd=repo)
            fresh = json.loads(fresh_out.read_text(encoding="utf-8"))
        finally:
            fresh_out.unlink(missing_ok=True)
        if (len(stored["nodes"]), len(stored["edges"])) != (len(fresh["nodes"]), len(fresh["edges"])):
            print(f"DESYNC: stored graph has {len(stored['nodes'])}n/{len(stored['edges'])}e, "
                  f"fresh extraction has {len(fresh['nodes'])}n/{len(fresh['edges'])}e")
            return 1
        print("CROSS-CHECK OK: stored counts match a fresh extraction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
