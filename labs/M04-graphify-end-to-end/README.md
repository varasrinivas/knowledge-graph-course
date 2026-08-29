# M04 Lab — Graphify End-to-End

**What you'll do**: run the real Graphify tool over orderflow, read all three artifacts, and query the graph. (Offline fallback: every step has a `kg_extract.py` equivalent.)
**Time**: 30–45 min · **Prerequisites**: `uv tool install graphifyy && graphify install` (or `pipx install graphifyy`).

## Step 1: Build the graph
```bash
cd labs/sample-project
graphify update .
```
Expected log shape (measured with graphify 0.9.40):
```
Re-extracting code files in . (no LLM needed)...
[graphify watch] Rebuilt: 70 nodes, 89 edges, 15 communities
[graphify watch] graph.json, graph.html and GRAPH_REPORT.md updated in graphify-out
```
Your counts will differ by graphify version and they will be **higher than the 36 nodes / 22 edges** that `shared_tools/kg_extract.py` reports on the same repo. That is not a contradiction: the course extractor emits functions, classes and modules joined by `calls` edges, while Graphify also indexes docstrings, doc headings, `imports_from` and `contains` edges. Two tools, two definitions of "node" — which is precisely why M05 argues you should never compare graph sizes across tools.
Note what did NOT happen: no LLM call, no API key, no tokens — the code pass is deterministic. Only docs/PDFs/images go through an LLM (`/graphify --update` in your assistant).

## Step 2: Read the three artifacts
- `graphify-out/graph.html` — open in a browser and look for the service split. **Expect a surprise:** Graphify reports ~15 communities, not three, and it names them after *files* (`app.py`, `db.py`, `worker.py`, `webhooks.py`, `orders.py`, `invoice.py`) plus separate communities for each document. The billing / orders / notifications split is still visible — those file communities line up with the services — but the tool does not hand it to you pre-labelled. On an 18-file corpus the clustering has too little call density to coarsen further; this is the small-repo tax the honesty rule warns about, seen from the inside.
- `graphify-out/GRAPH_REPORT.md` — the plain-language audit. Read its **God Nodes** section and compare it against what you assumed. It ranks `handle_payment_webhook()`, `AuthError`, `verify_token()` and `publish()` at 6 edges each, with `DatabasePool` down at 5. The persistence layer is *not* the hub. Then read **Suggested Questions**, where the tool names the real bridge itself: `publish()` — i.e. `shared/events.py` — with the highest betweenness (0.052), because it is the one module all three services touch. `shared/db.py` is reached by billing and orders only; notifications consumes events and never persists.
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
