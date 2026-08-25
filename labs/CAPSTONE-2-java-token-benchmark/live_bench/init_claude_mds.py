"""init arm prep: write a CLAUDE.md into every module subfolder (headless init).

Usage: python init_claude_mds.py <repo_root> [--prefix spring-]
Cost: roughly $0.05-0.15 per module at sonnet; resumable (skips existing files).
Remove them afterwards with: python init_claude_mds.py <repo_root> --remove
"""
import json
import sys
import shutil
import subprocess
import time
from pathlib import Path

CLAUDE = shutil.which("claude")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    print(__doc__); raise SystemExit(2)
REPO = Path(args[0]).resolve()
PREFIX = sys.argv[sys.argv.index("--prefix") + 1] if "--prefix" in sys.argv else ""
if "--remove" in sys.argv:
    removed = 0
    for f in REPO.rglob("CLAUDE.md"):
        f.unlink(); removed += 1
    print(f"removed {removed} CLAUDE.md files"); raise SystemExit(0)
PROMPT = ("Analyze this module and write a CLAUDE.md file for it (the standard Claude Code "
          "init artifact). Include: module purpose (2-3 sentences), key packages and their "
          "roles, the most important classes/entry points with one-line descriptions, and "
          "which sibling spring-* modules it depends on. Keep it under 60 lines. Inspect "
          "with Glob/Read/Grep as needed, then Write CLAUDE.md in this directory.")

total_cost = 0.0
mods = sorted(d for d in REPO.iterdir() if d.is_dir() and d.name.startswith(PREFIX) and not d.name.startswith("."))
for mod in mods:
    if (mod / "CLAUDE.md").exists():
        print(f"{mod.name}: already done, skipping", flush=True)
        continue
    t0 = time.time()
    proc = subprocess.run([CLAUDE, "-p", PROMPT, "--output-format", "json", "--model", "sonnet",
                           "--allowedTools", "Write", "Read", "Glob", "Grep"],
                          cwd=mod, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=900)
    try:
        d = json.loads(proc.stdout)
        cost = d.get("total_cost_usd") or 0
        total_cost += cost
        ok = (mod / "CLAUDE.md").exists()
        print(f"{mod.name}: {'OK' if ok else 'NO FILE'} turns={d.get('num_turns')} "
              f"${cost:.2f} ({time.time()-t0:.0f}s)", flush=True)
    except Exception:
        print(f"{mod.name}: PARSE FAIL rc={proc.returncode} stderr={proc.stderr[:150]!r}", flush=True)

done = sum(1 for m in mods if (m / "CLAUDE.md").exists())
print(f"\n{done}/{len(mods)} modules have CLAUDE.md; init cost this run ~${total_cost:.2f}")
