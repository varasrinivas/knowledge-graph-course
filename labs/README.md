# Knowledge Graphs for AI Agents — Lab Repository

Hands-on labs for the course. Each lab folder contains starter code with TODOs, a complete solution, and expected output for verification.

## Quick Start

```bash
# 1. Enter the labs directory
cd labs

# 2. Set up environment
cp .env.example .env          # add your Anthropic API key (only needed for LLM-enrichment labs)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start with the sample project tour
cd sample-project
cat README.md
```

See [SETUP.md](SETUP.md) for detailed installation and troubleshooting.

## The Running Example: orderflow

Every lab works against `sample-project/` — **orderflow**, a small B2B order-tracking monorepo:

```
sample-project/
├── services/
│   ├── billing/        # subscription billing, invoicing, payment webhooks
│   ├── orders/         # order lifecycle, orders_fact, weekly_active_users metric
│   └── notifications/  # consumes billing events
├── shared/             # auth (verify_token → decode_jwt), db pool
└── docs/               # runbook, architecture doc, ADR-001
```

It is deliberately small (~15 files) so you can verify every graph edge by hand — and deliberately below the ~500-file threshold where graph tooling pays off, which is itself one of the course's lessons (M04, M11).

## Lab Structure

```
M06-okf-authoring/
├── README.md              # Step-by-step instructions
├── starter/               # Skeleton with TODOs (start here)
├── solution/              # Complete working code (peek if stuck)
└── expected_output/       # What success looks like
```

**Rule**: config, mock data, and helper files are complete. You only build the knowledge-graph logic.

## Labs by Module

| Lab | Title | Difficulty | Key Skill |
|-----|-------|-----------|-----------|
| M01 | Graph fundamentals in pure Python | Beginner | Build an adjacency-list code graph; BFS callers; blast radius |
| M02 | Watch RAG shred context | Beginner | Chunk orderflow docs; observe a stale-definition retrieval |
| M02B | Context levers: fix the poisoned transcript | Beginner+ | Retrieve and offload levers over a rotted session; four-arm token comparison |
| M03 | tree-sitter extraction | Intermediate | Parse a file to an AST; extract call edges with provenance tags |
| M04 | Graphify end-to-end | Intermediate | `/graphify` orderflow; read the three artifacts; query paths |
| M06 | OKF authoring | Beginner | Write valid concept files; frontmatter validation |
| M07 | The orderflow bundle | Intermediate | index.md + cross-linked concepts; lint them |
| M08 | Enrichment hook | Intermediate | Diff-scoped git hook that refreshes concepts + log.md |
| M09 | MCP graph server | Advanced | Serve graph_callers/graph_callees/explore over stdio |
| M11 | Freshness gate | Intermediate | CI script that catches a stale graph within one commit |
| CAPSTONE | Self-updating pipeline | ★★★★☆ | All layers wired together, end-to-end |
| CAPSTONE-2 | Large Java codebase: measure the token reduction | ★★★☆☆ | tree-sitter-java extraction of commons-lang / spring-framework; your own benchmark table |

Modules without a lab folder (M00, M05, M10, M12) have their exercises embedded in the module HTML.
