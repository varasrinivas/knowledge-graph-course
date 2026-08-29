# M09 Lab — Serve the Graph over MCP

**What you'll build**: an MCP server exposing `graph_callers`, `graph_callees`, and a composite `explore` over orderflow's graph.json — so any MCP-aware agent answers structural questions in ONE tool call instead of N file reads.
**Time**: 60–75 min · **Prerequisites**: M01 lab; `pip install mcp`.

## Why this matters (the arithmetic)
Answering "who calls `decode_jwt`?" by reading `shared/auth.py` costs the file's full size in tokens, every session, every re-read after compaction. `graph_callers` returns one line.

On orderflow that is a modest win and you should see it as modest: `shared/auth.py` is 45 lines, about **375 tokens** (chars/4) against roughly **15** for the graph answer. The ratio only becomes decisive at real file sizes — a 700-line service module runs to ~6,000 tokens for the same one-line answer — and the ratio is not the whole story anyway: the parse cost was paid ONCE at extract time, so the saving repeats on every session and every re-read after compaction, while the cost does not.

## Step 1: Generate the graph
```bash
cd labs/M09-mcp-graph-server/starter
python -c "import server; server.load_graph()" && echo graph ok
```

## Step 2: Implement the three tools (TODOs in starter/server.py)
- `graph_callers(symbol)` — reverse-index lookup (you wrote this logic in M01; reuse it).
- `graph_callees(symbol)` — forward lookup.
- `explore(symbol)` — composite: kind, file:line, callers, callees, blast-radius size. One call, whole picture — token budget goes to reasoning, not tool-call overhead.
Every tool must handle unknown symbols with a helpful message (the agent needs a graceful miss so it can fall back to grep), never a stack trace.

## Step 3: Smoke-test without an agent
```bash
python server.py --selftest
```
Expected: see `expected_output/sample_output.txt`.

## Step 4: Register with Claude Code
```bash
claude mcp add orderflow-graph -- python /absolute/path/to/labs/M09-mcp-graph-server/solution/server.py
```
Then ask: "Using orderflow-graph, who calls decode_jwt and what's its blast radius?" and watch it answer with a single tool call.

## The trap to remember (M11 preview)
This server loads graph.json AT STARTUP. Regenerate the graph and the running server still serves the old one. Restart it after every rebuild — or you have a fresh graph on disk and a stale graph in the agent's memory.

## Troubleshooting
- `ImportError: mcp` → `pip install mcp` in the venv.
- Tool calls hang → never print to stdout in an MCP stdio server except protocol frames; use stderr for logs.
