# Lab Setup

## Requirements
- Python 3.10+ (3.11 recommended)
- git 2.25+
- Optional: Node.js 18+ (for the Node tabs in modules)
- Optional: `uv` or `pipx` (for installing Graphify in M04)

## Install

```bash
cd labs
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Only the LLM-enrichment steps (M08 optional pass 2, capstone extension) need `ANTHROPIC_API_KEY` in `.env`. Everything structural runs offline — that is the point of deterministic extraction.

## Where to run commands from

Every lab README states its working directory, and the relative paths in its commands (`../shared_tools/...`, `../M06-okf-authoring/solution/...`) only resolve from there. Rule of thumb:

- Lab exercises: run from inside that lab's folder (`labs/M01-graph-fundamentals/starter`, `labs/M02B-context-levers/solution`, ...)
- Anything that operates ON the sample repo (M04 graphify, M07 bundle authoring, M08 hook, M11 gate, Capstone 1): run from `labs/sample-project`
- Capstone 2: run from `labs/CAPSTONE-2-java-token-benchmark`

If a command fails with `No such file or directory` on a `../` path, you are in the wrong directory — `cd` to the one named at the top of the lab's README before debugging anything else.

## Tool installs used by specific labs

| Lab | Tool | Install |
|---|---|---|
| M04 | Graphify | `uv tool install graphifyy && graphify install` (or `pipx install graphifyy`) |
| M07 | okf CLI (optional) | see github.com/superops-team/okf releases |
| M09 | MCP SDK | included in requirements.txt (`mcp`) |

If a third-party tool is unavailable in your environment, every lab has an offline path using the provided pure-Python fallbacks (`shared_tools/kg_extract.py`).

## Troubleshooting
- `ModuleNotFoundError: No module named 'tree_sitter'` → `pip install -r requirements.txt` inside the activated venv.
- `graphify: command not found` → ensure the uv/pipx bin directory is on PATH; restart the shell.
- Windows git hooks not firing → check `.git/hooks/post-commit` exists and has no `.sample` suffix; Git Bash executes hooks with `sh`, so keep hooks POSIX-compatible (no `nohup` — see M11 for why).
- `AuthenticationError` in enrichment labs → `ANTHROPIC_API_KEY` missing from `.env`.
