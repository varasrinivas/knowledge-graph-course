# Knowledge Graphs for AI Agents — Course Repository

**"Knowledge Graphs for AI Agents: From RAG Limits to Self-Updating Codebase Brains"**

A 13-module, 6-track technical course with a hands-on capstone, teaching how AI coding agents stop wasting tokens re-deriving codebase structure — using structural graphs (tree-sitter/Graphify/CodeGraph/okf-rs), narrative knowledge (Google's Open Knowledge Format), and vector RAG as three complementary context layers.

Sibling course to [Building AI Agents with Claude](../claude-agent-course-final-adv) — same pedagogy, design system, and conventions.

## Repository Layout

```
knowledge-graph/
├── CLAUDE.md                 # Project rules — read first
├── prompts/                  # Course generation prompts (philosophy, template, design, content reference, depth rules)
├── .claude/commands/         # /generate-module, /review-module, /build-index
├── labs/                     # Hands-on lab repo (starter / solution / expected_output per lab)
│   └── sample-project/       # "orderflow" — the mock monorepo used by every lab
└── output/                   # The course: one self-contained HTML file per module + index.html
```

## Course Map

| Track | Modules |
|---|---|
| 0 — Overview | M00 The Context Problem & the Knowledge Lifecycle |
| 1 — Foundations | M01 Knowledge Graph Fundamentals · M02 The RAG Baseline and Where It Breaks |
| 2 — Structural Graphs | M03 Parsing Code with tree-sitter · M04 Graphify in Practice · M05 The Tool Landscape |
| 3 — Narrative Knowledge | M06 The OKF Specification · M07 OKF for Codebases · M08 The Enrichment Pipeline |
| 4 — Serving & Architecture | M09 Serving Graphs over MCP · M10 The Hybrid Context Stack |
| 5 — Production | M11 Drift, Staleness & Observability · M12 Structuring Projects for Agents + What's Next |
| Capstone | Build a Self-Updating Knowledge Graph Pipeline |

## Getting Started (learners)

Open `output/index.html` in a browser and start with M00. Labs live in `labs/` — see `labs/README.md` and `labs/SETUP.md`.

## Getting Started (authors)

Read `CLAUDE.md`, then use `/generate-module M06`, `/review-module M06`, `/build-index` from Claude Code.
