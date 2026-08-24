# M04 Lab — Graphify End-to-End

**What you'll do**: run the real Graphify tool over orderflow, read all three artifacts, and query the graph. (Offline fallback: every step has a `kg_extract.py` equivalent.)
**Time**: 30–45 min · **Prerequisites**: `uv tool install graphifyy && graphify install` (or `pipx install graphifyy`).

## Step 1: Build the graph
```bash
cd labs/sample-project
graphify update .
```
Expected log shape:
```
Re-extracting code files in . (no LLM needed)...
[graphify watch] Rebuilt: ~36 nodes, ~2x edges, ~3 communities
[graphify watch] graph.json, graph.html and GRAPH_REPORT.md updated in graphify-out
```
Note what did NOT happen: no LLM call, no API key, no tokens — the code pass is deterministic. Only docs/PDFs/images go through an LLM (`/graphify --update` in your assistant).

## Step 2: Read the three artifacts
- `graphify-out/graph.html` — open in a browser; find the three communities (billing / orders / notifications) and the god node (`shared/db.py`).
- `graphify-out/GRAPH_REPORT.md` — the plain-language audit; check it names the same communities.
- `graphify-out/graph.json` — the machine layer; this is what M09's MCP server consumes.

## Step 3: Query
```bash
graphify path "post_invoice" "decode_jwt"
graphify query "What components depend on DatabasePool?"
```
Verify both answers against the ground-truth list in `sample-project/README.md` — on a 15-file repo you CAN check the graph by hand; that is the point of this repo.

## Step 4: The honest measurement
orderflow is far below the ~500-file threshold where graph tooling pays for itself. Ask your assistant a structural question with and without `/graphify .` and record actual token counts. Expect a small multiple, not 71.5x — the vendor's ceiling case came from a 52-file corpus with a favorable query. Write down your measured number; you'll reuse it in the capstone.

## Troubleshooting
- `graphify: command not found` → uv/pipx bin dir not on PATH.
- graph.html missing → very large codebases skip it (logged); not applicable here, so check the run log for errors.
- `.graphifyignore` exists to exclude junk dirs if you add any.
