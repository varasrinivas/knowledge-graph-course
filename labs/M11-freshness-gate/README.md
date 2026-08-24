# M11 Lab — The Freshness Gate

**What you'll build**: the CI check that answers the course's defining question — *"How would you detect a stale graph within 24 hours?"* — in specific, mechanical terms.
**Time**: 30–45 min · **Prerequisites**: M08 lab (a repo with a bundle + graph that update on commit).

## The failure you're defending against
A graph rebuild hook can fail with a green exit code four documented ways (missing `nohup` on Windows, drifted extension allowlists, silent resource-gating skips, MCP startup caches). The graph then lies confidently. The ONLY defense is treating freshness as an **observable property**: compare artifact timestamps against `git log -1`, mechanically, in CI.

## Step 1: Run the gate on a fresh repo
```bash
cd labs/sample-project     # after the M08 lab setup
python ../M11-freshness-gate/solution/freshness_gate.py . --max-age-commits 0
```
Expected: `FRESH: graph.json generated at/after HEAD commit` and exit 0.

## Step 2: Make it stale on purpose
```bash
git commit --allow-empty -qm "commit without rebuilding the graph"
python ../M11-freshness-gate/solution/freshness_gate.py . --max-age-commits 0
```
Expected: `STALE: graph.json predates HEAD by 1 commit(s)` + actionable fix command + exit 1. This is the moment most "production" setups never test.

## Step 3: Cross-check the artifacts
Run with `--cross-check`: the gate verifies graph.json's node/edge counts match what a fresh extraction reports. Artifacts that disagree with each other are the second silent failure class (graph.json vs GRAPH_REPORT.md desync).

## Step 4: Wire it into CI
Add to your pipeline before any agent-consuming step:
```yaml
- run: python labs/M11-freshness-gate/solution/freshness_gate.py . --max-age-commits 0 --cross-check
```

## The rule this lab encodes
Never trust hook exit codes. Log rebuilds with timestamps, compare against HEAD, alert past a threshold, and restart MCP servers after every regeneration. If your setup can't fail this lab's Step 2, it isn't a production setup — it's a demo that hasn't failed yet.
