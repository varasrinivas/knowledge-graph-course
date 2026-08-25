"""Live benchmark runner — measure what a REAL agent spends, per arm.

Four arms (pick with --arms):
  baseline   Read/Glob/Grep only — the honest control
  init       identical config to baseline, but you run it AFTER writing
             CLAUDE.md files into the repo's modules (see init_claude_mds.py)
             — measures the ADD lever (M12's layered-CLAUDE.md pattern)
  available  file tools PLUS the graph MCP tools, prompt says "prefer the graph"
  forced     graph MCP tools ONLY — the Graphify-style forced integration
             (structural questions only unless --forced-logic; it has no file
             access, so logic answers come from edge-walking + prior knowledge)

Methodology (learned the hard way — see the module's live-run section):
  * every `claude -p` invocation is a fresh session; repeat each cell
    --reps times (default 3) and report MEDIANS, never single runs
  * every run records the repo's CLAUDE.md count — if a "baseline" run sees
    nonzero, your arms are contaminated and the record says so
  * single-line prompts only (the Windows .cmd shim truncates argv at newlines)
  * resumable: existing run-*.json files are skipped; delete to re-run
  * the forced arm doubles as a CANARY: if the MCP server is broken, forced
    sessions fail loudly instead of silently falling back to file tools

Usage:
  python run_live_bench.py <repo> --arms baseline,available,forced
                           [--mcp-config mcp.json] [--questions questions.json]
                           [--reps 3] [--model sonnet] [--out-dir runs]
Then:  python aggregate.py <out-dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

# Windows: which("claude") can resolve to the extension-less bash shim, which
# CreateProcess cannot execute — prefer the .cmd/.exe launchers explicitly.
CLAUDE = (shutil.which("claude.cmd") or shutil.which("claude.exe")
          or shutil.which("claude") or "claude")

HINT_AVAILABLE = ("You have MCP tools (springgraph: graph_callers, graph_callees, explore) over a "
                  "pre-built structural graph of this codebase. Prefer them over file exploration "
                  "for caller/callee questions; fall back to Read/Grep only when the graph cannot answer. ")
HINT_FORCED = ("You have MCP tools (springgraph: graph_callers, graph_callees, explore) over a "
               "pre-built structural graph of this codebase. They are your ONLY tools — you have "
               "no file access. Answer exclusively from the graph tools; note honestly in your "
               "answer if the graph's provenance tags (AMBIGUOUS) make parts uncertain. ")
EFFORT = "Work efficiently: use at most ~10 tool calls, then give your best answer. Be concise. "

FILE_TOOLS = ["Read", "Glob", "Grep"]
MCP_TOOLS = ["mcp__springgraph__graph_callers", "mcp__springgraph__graph_callees",
             "mcp__springgraph__explore"]

ARMS = {
    "baseline":  {"hint": "", "tools": FILE_TOOLS, "mcp": False},
    "init":      {"hint": "", "tools": FILE_TOOLS, "mcp": False},
    "available": {"hint": HINT_AVAILABLE, "tools": FILE_TOOLS + MCP_TOOLS, "mcp": True},
    "forced":    {"hint": HINT_FORCED, "tools": MCP_TOOLS, "mcp": True},
}


def claude_md_count(repo: Path) -> int:
    return sum(1 for _ in repo.rglob("CLAUDE.md"))


def run_one(repo: Path, out_dir: Path, q: dict, arm: str, rep: int,
            model: str, mcp_config: Path | None) -> dict:
    out_file = out_dir / f"run-{q['id']}-{arm}-r{rep}.json"
    if out_file.exists():
        return json.loads(out_file.read_text(encoding="utf-8"))

    cfg = ARMS[arm]
    prompt = cfg["hint"] + EFFORT + "Question: " + q["text"]  # single line!
    cmd = [CLAUDE, "-p", prompt, "--output-format", "json", "--model", model,
           "--allowedTools"] + cfg["tools"]
    if cfg["mcp"]:
        if not mcp_config:
            raise SystemExit(f"arm {arm!r} needs --mcp-config")
        cmd += ["--mcp-config", str(mcp_config.resolve())]

    t0 = time.time()
    proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=900)
    record = {"qid": q["id"], "kind": q["kind"], "arm": arm, "rep": rep,
              "model": model, "repo_claude_md_count": claude_md_count(repo),
              "elapsed_s": round(time.time() - t0, 1), "returncode": proc.returncode}
    try:
        data = json.loads(proc.stdout)
        u = data.get("usage", {})
        record.update({
            "num_turns": data.get("num_turns"), "cost_usd": data.get("total_cost_usd"),
            "input_tokens": u.get("input_tokens"), "cache_read": u.get("cache_read_input_tokens"),
            "cache_creation": u.get("cache_creation_input_tokens"),
            "output_tokens": u.get("output_tokens"),
            "answer": (data.get("result") or "")[:4000],
        })
    except Exception as exc:  # noqa: BLE001 - keep stderr: silent failures lie
        record["error"] = (f"{exc}; stdout[:300]={proc.stdout[:300]!r}; "
                           f"stderr[:300]={proc.stderr[:300]!r}")
    out_file.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", type=Path)
    ap.add_argument("--arms", default="baseline", help="comma list of: baseline,init,available,forced")
    ap.add_argument("--mcp-config", type=Path, default=None)
    ap.add_argument("--questions", type=Path, default=Path(__file__).parent / "questions.json")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).parent / "runs")
    ap.add_argument("--forced-logic", action="store_true",
                    help="also run logic questions on the forced arm")
    args = ap.parse_args()

    repo = args.repo.resolve()
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in arms if a not in ARMS]
    if unknown:
        raise SystemExit(f"unknown arms: {unknown}; choose from {list(ARMS)}")
    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)

    md_count = claude_md_count(repo)
    print(f"repo: {repo} ({md_count} CLAUDE.md files present)")
    if "baseline" in arms and md_count:
        print("WARNING: baseline arm with CLAUDE.md files present — arms are "
              "contaminated; run baseline before init_claude_mds.py, or remove them.")
    if "init" in arms and not md_count:
        print("WARNING: init arm but no CLAUDE.md files — run init_claude_mds.py first.")

    for rep in range(args.reps):
        for q in questions:
            for arm in arms:
                if arm == "forced" and q["kind"] == "logic" and not args.forced_logic:
                    continue
                print(f"[{time.strftime('%H:%M:%S')}] rep{rep} {q['id']} ({q['kind']}) / {arm} ...",
                      flush=True)
                rec = run_one(repo, args.out_dir, q, arm, rep, args.model, args.mcp_config)
                tok = (rec.get("input_tokens") or 0) + (rec.get("cache_read") or 0) + \
                      (rec.get("cache_creation") or 0)
                err = "ERROR: " + rec["error"][:100] if "error" in rec else ""
                print(f"    -> turns={rec.get('num_turns')} cost=${rec.get('cost_usd')} "
                      f"in-tokens~{tok:,} ({rec['elapsed_s']}s) {err}", flush=True)
    print("DONE — aggregate with: python aggregate.py", args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
