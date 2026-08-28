# M08 Lab — The Diff-Scoped Enrichment Hook

**What you'll build**: a git post-commit hook that keeps the orderflow OKF bundle current — diff-scoped, linted, logged. This is the "self-updating" in self-updating knowledge graph.
**Time**: 45–60 min · **Prerequisites**: M06 and M07 labs (you need a bundle to update).

## The pipeline you're implementing
```
commit → diff-scoped scan → refresh affected concepts → append log.md → lint → (refuse to publish on lint failure)
```
The single most important property: **scope to the diff**. A full-repo rescan per commit is what makes teams turn the pipeline off.

## Step 1: Make sample-project a git repo (labs only)
```bash
cd labs/sample-project
git init -q && git add -A && git commit -qm "baseline"
```

## Step 2: Study `solution/refresh_concepts.py`
It maps changed files → owning service → concept file, regenerates the concept's `## Dependencies` section from `kg_extract` output, and appends a dated entry to `log.md`. Read the mapping table first — it is the part you'll adapt to any real repo.

## Step 3: Install the hook
```bash
cp ../M08-enrichment-hook/solution/post-commit .git/hooks/post-commit
# On macOS/Linux: chmod +x .git/hooks/post-commit
```
Note what the hook does NOT do: no `nohup` (silently absent on Git-for-Windows — M11 explains the postmortem), no silent skips — every failure prints and exits non-zero.

## Step 4: Trigger it
Edit `services/billing/webhooks.py` (add a comment), commit, and watch:
```
[enrich] changed: services/billing/webhooks.py -> concept billing-service
[enrich] refreshed Dependencies (4 edges) in knowledge/services/billing-service.md
[enrich] log.md updated
[enrich] lint: 5 concepts valid, 0 errors
```
✅ Checkpoint: `git log -1 --stat` shows only YOUR commit; the bundle refresh happened post-commit (commit the bundle separately or auto-amend — both strategies are discussed in the module).

## Step 5: Break it on purpose
Delete `type:` from a concept and commit any code change. The hook must FAIL LOUDLY (non-zero, message naming the file). If it passes, your lint gate is decorative.

## Troubleshooting
- Hook doesn't fire → file must be named exactly `post-commit`, be executable (macOS/Linux), and live in `.git/hooks/`.
- `python: command not found` inside the hook → hooks run with a minimal PATH; use an absolute interpreter path or `#!/usr/bin/env python3`.
