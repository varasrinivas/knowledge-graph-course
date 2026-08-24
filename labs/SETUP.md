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
