# CLAUDE.md — Knowledge Graphs for AI Agents Course

## Project Identity
This project generates the course **"Knowledge Graphs for AI Agents: From RAG Limits to Self-Updating Codebase Brains"** — a 13-module, 6-track technical course with a hands-on capstone project. It is the sibling course to "Building AI Agents with Claude" (`../claude-agent-course-final-adv`) and follows the same pedagogy, visual design system, and file conventions.

The course teaches how AI coding agents stop wasting tokens re-deriving codebase structure by using three complementary context layers:
1. **Structural graphs** — deterministic AST-derived code graphs (tree-sitter, Graphify, CodeGraph, okf-rs)
2. **Narrative knowledge** — curated Markdown+YAML bundles (Google's Open Knowledge Format, OKF v0.1)
3. **Vector RAG** — semantic search over the unstructured long tail

**M00 is the gateway module** — a code-free overview showing the context problem (an agent reading 147 files to fix a 3-line bug), the three context layers, and the knowledge lifecycle (extract → curate → serve → maintain). Every learner starts here.

**The CAPSTONE is a BUILD module** — the student builds a self-updating knowledge graph pipeline over a provided mock repository: Graphify structural graph + OKF bundle + git-hook enrichment + MCP serving + CI freshness gate. 80% lab, 20% concept.

**CAPSTONE-2 is an optional bonus BUILD module** — the student graphs a real large Java codebase (commons-lang, spring-framework, or a deterministic synthetic fallback) with `labs/shared_tools/kg_extract_java.py` (tree-sitter-java) and produces their own measured benchmark table with `measure_tokens.py`. It stays outside the 14-part numbering (badge: "Capstone 2 · Bonus").

## Course Map (13 Modules + M02B bridge + 2 Capstones, 6 Tracks)
B-suffix modules are ADDITIVE (sibling-course convention): inserted between numbered modules, badge "Module 2B · Bridge", the numbered spine keeps "Module N of 14".
- Track 0 — OVERVIEW: M00 The Context Problem & the Knowledge Lifecycle
- Track 1 — FOUNDATIONS (M01–M02 + M02B): Knowledge Graph Fundamentals; The RAG Baseline and Where It Breaks; The Context Engineering Frame (bridge to the sibling course's M03B — maps its four levers add/compress/retrieve/offload onto this course's machinery)
- Track 2 — STRUCTURAL GRAPHS (M03–M05): Parsing Code into Graphs with tree-sitter; Graphify in Practice; The Tool Landscape (CodeGraph, okf-rs, and Friends)
- Track 3 — NARRATIVE KNOWLEDGE (M06–M08): The OKF Specification; OKF for Codebases; The Enrichment Pipeline (Self-Updating Graphs)
- Track 4 — SERVING & ARCHITECTURE (M09–M10): Serving Graphs to Agents over MCP; The Hybrid Context Stack
- Track 5 — PRODUCTION (M11–M12): Drift, Staleness & Observability; Structuring Projects So Agents Don't Get Lost + What's Next
- CAPSTONE: Build a Self-Updating Knowledge Graph Pipeline

## Output Format
- Every module = ONE self-contained .html file in `output/`
- All CSS and JS MUST be inline (no external files in production output)
- Target file size: 80–150KB per module; depth wins over the target when the weight is prose and markup
- Import only: Google Fonts (Bricolage Grotesque, Source Sans 3, JetBrains Mono); no other external assets

## File Conventions
- Module files: `output/M{XX}-{slug}.html` (e.g., `output/M06-okf-specification.html`)
- Capstone file: `output/CAPSTONE-knowledge-pipeline.html`
- Course landing page: `output/index.html`
- Prompt files: `prompts/` — read these BEFORE generating any content
- Labs: `labs/M{XX}-{slug}/` with `README.md`, `starter/`, `solution/`, `expected_output/`
- Walkthroughs: `walkthroughs/*.json` — interactive step-throughs embedded in modules. See `../shared/walkthrough/README.md`. Mount at the END of the section they belong to under `<h3>Walk it, step by step</h3>` + one bespoke bridge sentence + `<div data-wt="id" data-wt-theme="dark"></div>`, with `<!-- WT:BUNDLE -->` once before `</body>`. Rebuild with `python ../shared/walkthrough/build.py --scenarios walkthroughs/X.json --root . --target output/M{XX}-*.html` (idempotent). Every scenario declares provenance; a `measured` citation that does not resolve **fails the build** — that is the Honesty Rule made mechanical.

## Key Design Rules (always apply)
1. Every technical term gets a tooltip definition on FIRST use
2. Every concept gets: analogy → technical definition → animated visual → "why it matters"
3. Code examples must be COMPLETE and RUNNABLE — never pseudocode
4. Language policy: Python is the primary lab language. Where an API example exists in both ecosystems, ship Python AND Node.js tabs. CLI, YAML, and Markdown examples are single blocks (no tabs needed)
5. Error handling in ALL code examples — no happy-path-only code
6. Accessibility: `prefers-reduced-motion` media query, ARIA labels, keyboard nav
7. Interactive quiz (5 questions minimum) at end of every module
8. Progress indicator showing module position in the 14-part curriculum (M00–M12 + CAPSTONE)
9. Responsive layout — must work on tablet (768px) and desktop (1440px)
10. DEPTH RULES (read `prompts/07-depth-rules.md` before generating ANY content):
    - Analogies: minimum 3 sentences (BEFORE → PAIN → MAPPING)
    - Tech definitions: teach with plain English, define every sub-term
    - Code blocks: annotate in 3–5 chunks with WHAT/WHY/GOTCHA before each chunk
    - "Why It Matters": use concrete numbers and real scenarios, never abstract
    - Add conceptual bridges between major sections
    - Add "What Just Happened?" checkpoints after code blocks
    - Common Misconceptions callout for every major new concept
11. HONESTY RULE (specific to this course): always pair marketing numbers with replicated numbers. The 71.5x token-reduction claim is a ceiling case; independent replications land at 6.8x–49x (7.3x on a from-scratch Python codebase). Below ~500 files the tooling tax exceeds the savings. Teach the honest range.
12. All tool commands must match the real tools: `uv tool install graphifyy && graphify install`, `/graphify .`, `okf init / hook install / search / lint`, `okf-rs generate / validate / watch`, `codegraph init -i`, `claude mcp add`.

## Domain Anchor (for labs and capstone)
All labs use one running example: **"orderflow"** — a small B2B order-tracking monorepo (FastAPI Python backend + a worker service + docs) provided as mock code in `labs/sample-project/`. Concepts map to it consistently: `billing-service`, `orders_fact`, `weekly_active_users`, auth middleware, payment webhooks. This mirrors Domain B of the sibling course so learners moving between courses see familiar territory.

## Slash Commands
| Command | Description |
|---|---|
| `/generate-module M06` | Generate a complete module HTML file |
| `/review-module M06` | Review a module against quality standards |
| `/build-index` | Regenerate course landing page from completed modules |

## Quality Checklist (applied by /generate-module and /review-module)
- [ ] All CSS/JS inline (external only: Google Fonts)
- [ ] Every H2/H3 has an `id` for sidebar navigation
- [ ] Sticky sidebar navigation present
- [ ] Progress bar shows correct position (e.g., "Module 6 of 14")
- [ ] All technical terms have tooltip definitions on first use
- [ ] At least 3 animated visualizations with play/pause/restart controls
- [ ] `prefers-reduced-motion` media query present
- [ ] All code blocks have copy buttons
- [ ] Quiz section: 5+ questions with immediate feedback
- [ ] Previous/Next module navigation links
- [ ] No hardcoded API keys
- [ ] ARIA labels on interactive elements
- [ ] Depth rules applied (analogies unpacked, code annotated, bridges present)
- [ ] Honesty rule applied (benchmark claims paired with replicated ranges)
