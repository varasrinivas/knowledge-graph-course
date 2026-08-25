"""Aggregate live-bench runs into a median comparison table.

Usage: python aggregate.py <runs-dir> [--json out.json]
Reads run-*.json produced by run_live_bench.py; reports per-cell medians
(min-max), per-arm totals by question kind, and flags errors/contamination.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def tot(r): return (r.get("input_tokens") or 0) + (r.get("cache_read") or 0) + \
                   (r.get("cache_creation") or 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs_dir", type=Path)
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    runs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(args.runs_dir.glob("run-*.json"))]
    good = [r for r in runs if "error" not in r]
    bad = [r for r in runs if "error" in r]
    if bad:
        print(f"WARNING: {len(bad)} errored runs excluded:")
        for r in bad[:5]:
            print(f"  {r['qid']}/{r['arm']}/r{r['rep']}: {r['error'][:100]}")

    contaminated = [r for r in good if r["arm"] == "baseline" and r.get("repo_claude_md_count")]
    if contaminated:
        print(f"WARNING: {len(contaminated)} baseline runs had CLAUDE.md files present — "
              "not a clean control.")

    arms = sorted({r["arm"] for r in good},
                  key=lambda a: ["baseline", "init", "available", "forced"].index(a)
                  if a in ["baseline", "init", "available", "forced"] else 99)
    qids = sorted({r["qid"] for r in good})

    def cell(qid, arm):
        rs = [r for r in good if r["qid"] == qid and r["arm"] == arm]
        if not rs:
            return None
        toks = sorted(tot(r) for r in rs)
        return {"n": len(rs), "med": statistics.median(toks), "min": toks[0], "max": toks[-1],
                "turns": statistics.median(r["num_turns"] for r in rs),
                "cost": statistics.median(r["cost_usd"] for r in rs)}

    header = f"{'Q':<5}" + "".join(f"{a:<34}" for a in arms)
    print("\n" + header)
    print("-" * len(header))
    for qid in qids:
        row = f"{qid:<5}"
        for arm in arms:
            c = cell(qid, arm)
            row += (f"{c['med']:>8,.0f} ({c['min']:,}-{c['max']:,}) {c['turns']:.0f}t".ljust(34)
                    if c else " " * 34)
        print(row)
    print("-" * len(header))

    kinds = sorted({r["kind"] for r in good})
    for kind in kinds + ["ALL"]:
        row = f"{kind:<11}"
        for arm in arms:
            cells = [cell(q, arm) for q in qids
                     if any(r["qid"] == q and (kind == "ALL" or r["kind"] == kind) for r in good)]
            cells = [c for c in cells if c]
            row += (f"{sum(c['med'] for c in cells):>10,.0f} tok  ${sum(c['cost'] for c in cells):.2f}"
                    .ljust(34) if cells else " " * 34)
        print(row)

    print("\nRead per the Honesty Rule: medians of independent fresh sessions; "
          "tokens include cache reads (cheaper per token — check costs too); "
          "session variance up to 2x is normal; only your stack's numbers describe your stack.")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(good, indent=2), encoding="utf-8")
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
