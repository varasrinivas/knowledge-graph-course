# Module Content Reference — What Each Module Teaches

This file is the authoritative content distillation from the research corpus. Every module generator must cover the listed concepts with the listed concrete facts, numbers, and examples. Facts marked (vendor) are vendor-reported; pair them with replicated figures per the Honesty Rule.

---

## M00 — The Context Problem & the Knowledge Lifecycle (Track 0, Gold, code-free gateway)
**Hook story**: A developer asks Claude Code to fix a session-timeout bug in auth middleware. The fix is 3 lines. Claude reads 147 files first — the logging system, migration history, half the API endpoints, the Terraform configs — before the developer hits Escape. The problem is not the model; it is that the agent has no map.
**Concepts**:
- Exploration vs reasoning tokens: most tokens in agentic coding are spent FINDING code, not thinking about it. Every file read costs its full size in context tokens; re-reads after compaction cost it again.
- The context-assembly problem (Google's term): table schemas, metric definitions, JOIN paths, runbooks live scattered across catalogs, wikis, code comments, and the heads of senior engineers on vacation. Every new agent re-assembles the same context from scratch.
- Karpathy's LLM Wiki idea (April 2026): let the model build and maintain a living wiki; "models don't get bored maintaining cross-references the way people abandon their personal wikis."
- The 90-day timeline: Apr 1 Karpathy post → Apr 3 Graphify launch (YC S26) → Jun 1 58.3K stars → Jun 12 Google ships OKF v0.1 → Jul 1 Graphify↔OKF toolkit → Jul 5 scrutiny begins.
- The three context layers preview: structural (what the code IS — AST graphs), narrative (what engineers KNOW — OKF), semantic (the messy long tail — vector RAG).
- The knowledge lifecycle the course follows: EXTRACT (parse code into a graph) → CURATE (write narrative concepts) → SERVE (MCP, progressive disclosure) → MAINTAIN (hooks, lint, freshness gates).
**Animations**: LOST_AGENT (agent icon opening file after file, token meter climbing, vs map path); TIMELINE (90-day ecosystem timeline); THREE_LAYERS (three stacked context sources feeding one agent).
**Quiz themes**: exploration-vs-reasoning tokens; what each layer holds; lifecycle order; why bigger context windows don't solve it.

## M01 — Knowledge Graph Fundamentals (Track 1, Indigo)
**Concepts**:
- Node, edge, typed edge, directed graph — code is a social network, not a book: files/classes/functions are nodes; calls/imports/inherits are edges.
- Traversal vs search: answering "what calls verify_token?" by following edges (deterministic, O(edges followed)) vs by reading text (probabilistic, O(files read)).
- Multi-hop reasoning: "what breaks in the API layer if I alter db/migrations/04_users.sql?" requires linking facts across files that never co-occur in one text chunk.
- Communities: clusters of densely-connected nodes ≈ natural subsystems. Leiden algorithm (used by Graphify); modularity-based clustering (Clauset–Newman–Moore in okf-rs) splits what connected-components collapses into one blob.
- God nodes: high-centrality nodes everything depends on; betweenness centrality is O(V×E) — foreshadow the M11 scale wall (450K nodes × 690K edges ≈ 310 billion operations; a 96-core Xeon rebuild killed after 114 minutes).
- Blast radius / impact analysis: transitive-caller count as a risk score (okf-rs `impact` scores concepts by transitive callers, public-API membership, cycle participation).
- Provenance tags: EXTRACTED (parsed from source, ground truth) vs INFERRED (heuristic guess) vs AMBIGUOUS — the only honest graphs label which answers are facts and which are guesses.
**Animations**: GRAPH_BUILD (files morph into nodes, edges draw in); TRAVERSAL (query walks edges, hops light up, token counter stays flat); COMMUNITY_DETECT (nodes cluster into colored groups, god node pulses at the center).
**Code**: a tiny pure-Python adjacency-list graph of orderflow (build nodes/edges dict, BFS "who calls X", transitive blast radius) — no libraries, ~40 lines, both Python and Node tabs.
**Quiz themes**: typed edges; why traversal is deterministic; what a god node implies for refactoring; EXTRACTED vs INFERRED.

## M02 — The RAG Baseline and Where It Breaks (Track 1, Indigo)
**Concepts**:
- RAG recap in two phases (setup: chunk → embed → store; query: embed → nearest-neighbor → paste into prompt).
- What chunking destroys: "shredded context" — hierarchy, table structure, cross-references. "If cause and effect aren't co-located in the same 512-token chunk, your system has no idea they're connected" (Prism Labs). You cannot fix this with better embeddings; it is inherent to chunking.
- Probabilistic retrieval vs canonical truth: the churn-rate story — agent retrieves a 2023 PowerPoint, an old wiki, and a Slack argument; blends three conflicting definitions; ships a wrong dashboard nobody catches for 3 weeks. Nothing crashed; the agent "confidently retrieved the wrong version of the truth."
- Embedding drift & re-indexing cost; the permissions leak: copying content into a vector index frequently strips source-system ACLs — anyone who can query the index sees everything (Google's Knowledge Catalog preserves source permissions; that's the fix's origin story).
- Where RAG STILL wins: millions of genuinely unstructured, uncurated documents; exploratory/thematic queries ("common themes in churn interviews"). 72% of enterprise RAG deployments underdelivered in year one — but often due to bad chunking/embeddings, not missing graphs. "RAG first, graph when depth becomes a bottleneck" (Atlan).
- Semantic search's structural blind spot: it knows handleAuth() and validateToken() contain similar LANGUAGE, not that one CALLS the other. Leads vs answers.
**Animations**: SHREDDER (structured doc goes through chunker, table rows separate, links snap); COSINE_ROULETTE (query vector pulls 3 chunks: one right, one stale, one irrelevant — each run differs); LEADS_VS_ANSWERS (semantic search returns ranked hints requiring verification reads; graph query returns the edge directly).
**Code**: minimal RAG pipeline over orderflow docs (chunk + embed + query) that demonstrably returns a stale WAU definition; then the same question answered from a single curated file. Python + Node tabs.
**Quiz themes**: two phases of RAG; shredded context; probabilistic vs deterministic; ACL leak; when RAG is still the right tool.

## M03 — Parsing Code into Graphs with tree-sitter (Track 2, Violet)
**Concepts**:
- What an AST is (parse tree of code structure); tree-sitter: incremental parser built for Atom, now Neovim's syntax engine; fault-tolerant — produces partial ASTs even with syntax errors (real dev never happens in a compilable state); fast enough for tens of thousands of files.
- Extraction queries: language-specific patterns pull symbols (functions, classes, methods, interfaces) and edges (calls, imports, inheritance, implementations).
- Determinism: AST parsing needs zero LLM calls — no API key, no token cost, no hallucination risk in the structural pass. Identical source → identical graph (okf-rs guarantees byte-identical output: no timestamps, no unordered-map noise).
- Name resolution limits: dynamic languages ("types are merely suggestions"), dynamic dispatch invisible, ambiguous names. Solutions ladder: heuristics (INFERRED edges with confidence) → LSP-backed disambiguation (okf-rs `generate --lsp` asks rust-analyzer/pyright via textDocument/definition) → accept AMBIGUOUS labels.
- Visibility rules vary by language: explicit opt-in (Rust pub, Java public), opt-out (PHP/Kotlin), capitalization-based (Go), section-based (C++).
- Language coverage in practice: Graphify 36 grammars; okf-rs 11 languages; CodeGraph strongest in TS/Python/Rust/Go.
**Animations**: AST_GROW (source code text morphs into a tree, nodes labeled); EXTRACT_EDGES (tree-sitter query highlights call expressions, edges fly onto a graph panel); RESOLVE_LADDER (ambiguous call tries heuristic → LSP → tagged AMBIGUOUS).
**Code**: py-tree-sitter walkthrough — parse a small orderflow file, walk the tree, extract function defs + call edges into a dict; show the same in Node (tree-sitter npm). Include error-handling for parse failures.
**Quiz themes**: why fault tolerance matters; why the structural pass can't hallucinate; what LSP adds over heuristics; EXTRACTED/INFERRED/AMBIGUOUS assignment.

## M04 — Graphify in Practice (Track 2, Violet)
**Concepts**:
- What Graphify is: MIT/Apache-2.0, by Safi Shamsi (YC S26), PyPI package `graphifyy`, CLI `graphify`; turns any folder (code, docs, PDFs, images, video) into a graph. Code parsed structurally (free, no LLM); only docs/papers/images go through an LLM (only that pass can hallucinate).
- Install & run: `uv tool install graphifyy && graphify install` (or pipx/pip); registers `/graphify` skill in 17 assistants (Claude Code, Cursor, Codex, Gemini CLI, Aider…). `graphify update .` / `/graphify .`.
- The three artifacts in `graphify-out/`: `graph.json` (machine-readable, GraphRAG-ready), `graph.html` (interactive, self-contained), `GRAPH_REPORT.md` (plain-language audit). Plus `cache/` — only changed files re-run. `.graphifyignore` for exclusions. Note: very large codebases skip graph.html generation (logged).
- Sample log output: "Rebuilt: 87 nodes, 100 edges, 13 communities".
- Querying: `graphify path "UserService" "DatabasePool"`; `graphify query "What components depend on AuthTokenValidator?"`; MCP serving via `python -m graphify.serve graphify-out/graph.json`.
- Leiden community detection → subsystem discovery; god-node identification; use cases: onboarding, impact analysis ("the 14 hidden dependencies that say Yes"), security audits (trace unauthenticated request flow), architecture discovery ("microservices that are secretly a monolith in a trench coat").
- Honest benchmarks (HONESTY RULE — teach all of these): vendor 71.5x token reduction on a 52-file corpus (ceiling case: 123K tokens naive vs ~1.7K with graph); replications 6.8x (code review) to 49x (daily coding, 500+ file repos); 7.3x on a from-scratch real Python codebase; LongMemEval-S: graph retrieval 76% accuracy / 0.844 recall@10 vs dense RAG 76% / 0.848 — a tie on accuracy, slight loss on recall; LOCOMO: 45.3% at $1.40 ingest vs Supermemory 49.7% at $15.67 (11x cost). Graphify's real edge = ingest cost + zero-hallucination structure, NOT retrieval superiority. ~500-file floor where tooling tax exceeds savings.
- Limitations: noisy graphs on messy code (5000-line GodController = ball of yarn); dynamic-language guessing; big-graph query latency.
**Animations**: PIPELINE (folder → tree-sitter → graph → three artifact cards); COMMUNITY_MAP (orderflow graph clusters into billing/orders/notifications, god node glows); BENCHMARK_BARS (animated bars: 71.5x ceiling vs 7.3–49x replicated, with condition labels).
**Code**: full lab flow on orderflow: install → run → read GRAPH_REPORT.md excerpt → query paths → load graph.json in Python and compute top-degree nodes.
**Quiz themes**: which pass costs tokens; the three artifacts; what Leiden finds; interpreting the benchmark table honestly; when NOT to bother (<500 files).

## M05 — The Tool Landscape: CodeGraph, okf-rs, and Friends (Track 2, Violet)
**Concepts**:
- CodeGraph (MIT, 32.1K stars): tree-sitter → SQLite + FTS5 at `.codegraph/codegraph.db`; fully local (no cloud, no API key); installer auto-detects Claude Code/Cursor/Codex/OpenCode/Gemini CLI/Antigravity/Kiro; `codegraph init -i` (10+ min on 100K-file repos, one-time); answers "what calls this?" in ONE MCP tool call.
- CodeGraph benchmarks (7 projects, Claude Opus 4.7 headless, 4 runs, medians): VS Code 78% token cut; Excalidraw 90%; Tokio 86% (Rust module systems punish exploration); Django 36%; OkHttp only 13%; Gin 34%. Aggregate: 57% fewer tokens, 71% fewer tool calls, 46% faster, 35% cheaper. Pattern: bigger haystack → bigger savings; small repos → diminishing returns.
- Auto-sync three layers: (1) native OS file watchers (FSEvents/ReadDirectoryChangesW/inotify — no polling); (2) 2-second debounced batching; (3) staleness flags + reconnection reconciliation via (size, mtime) + content hash. "No rebuild-the-index step in anyone's workflow."
- Framework route recognition across 14 web frameworks (annotation: Spring/NestJS; decorator: Flask/FastAPI; DSL: Rails/Laravel; file-convention: Django/SvelteKit) — "which handler processes POST /api/users?" in one query.
- okf-rs (Rust, MIT/Apache-2.0, Jeremy Jeanne): outputs an OKF Markdown bundle instead of a database — git-diffable, greppable, renders on GitHub. `okf-rs init/generate/validate/watch`; content-hash incremental caching; `--enrich` optional LLM descriptions (never overwrites existing); deterministic architecture extraction (graph layers/domains/communities/patterns/features); `impact`/`review` PR automation with `--fail-on-risk` CI gating; exports HTML/PDF/GraphML/Obsidian/DITA.
- Cursor's built-in semantic indexing vs structural graphs: leads vs answers (recap); Sourcegraph (server-heavy, org-scale), Gemini Code Assist / Copilot indexing (cloud-bound — data sovereignty constraint).
- Comparison axes for ANY tool: storage substrate (DB vs Markdown), sync model (watchers vs hooks vs manual), provenance labeling, local vs cloud, query surface (CLI/MCP/slash), multimodal support.
- Positioning: enhancers, not replacements — they cut exploration cost; reasoning quality stays with the model.
**Animations**: TOOL_MATRIX (animated comparison grid filling in); SYNC_LAYERS (file save → watcher → debounce window collects changes → single batch sync; staleness flag path); BENCH_SCALE (savings % vs repo size curve rising).
**Code**: `codegraph init -i` flow; okf-rs generate/validate output; a sample generated concept file (`verify_token` with Calls link); registering okf-mcp: `claude mcp add okf-rs -- /path/to/okf-mcp /path/to/project`.
**Quiz themes**: SQLite vs Markdown substrate tradeoff; the three sync layers; why Tokio saved 86% but OkHttp 13%; which tools keep code local; enhancer-not-replacement.

## M06 — The Open Knowledge Format Specification (Track 3, Cyan)
**Concepts**:
- Lineage & release: published Jun 12–13 2026 by Google Cloud's Sam McVeety & Amir Hormati via GoogleCloudPlatform/knowledge-catalog, v0.1; formalizes Karpathy's LLM Wiki + the AGENTS.md convention + Obsidian-vault patterns. "OKF doesn't invent a new substrate; it standardizes the one that already won: Markdown, frontmatter, and Git."
- Format not platform: no database, no model, no service, no SDK. "If you can cat a file, you can read OKF; if you can git clone a repo, you can ship it." The USB-C analogy (Alphamatch): universal connector, no lock-in.
- Bundle anatomy: bundle = directory of Markdown files; concept = one file = one unit of knowledge; the file PATH is the identity (no separate ID system). Directory example: company_brain/ with engineering/, analytics/tables/, analytics/metrics/.
- Frontmatter: exactly ONE required field — `type` (producer-defined, unvalidated). Recommended optional: title, description, resource, tags, timestamp. Full canonical example: the Orders BigQuery-table concept (schema table + joins with relative links) and the WAU metric concept (computation rules excluding staging.internal_testers, [[analytics/tables/customers]] links).
- Reserved filenames: `index.md` (directory listing → progressive disclosure: agent walks hierarchy one level at a time — a token-budget control, not a convenience); `log.md` (chronological change history of what the bundle KNOWS — distinct from git log which records what the FILES did).
- Conformance leniency (three rules, one page): consumers MUST NOT reject bundles for missing optional fields, unknown types, unknown keys, or broken links. Leniency = adoptability AND silent-degradation risk (foreshadow M11).
- Reading it: `python-frontmatter` in ~3 lines (`frontmatter.load(...)`, `.metadata`, `.content`).
- Cross-links: ordinary relative Markdown links; semantics carried by surrounding prose; a folder of files becomes a deterministic knowledge graph. Cap: untyped/unenforced links limit formal reasoning vs RDF/OWL graphs.
- Determinism payoff: the agent retrieves the EXACT versioned file — no similarity threshold. "90% semantic similarity is a failure; 100% exactness is non-negotiable" for compliance docs, runbooks, API specs.
- Google's GA4 demo bundle: 17 markdown files (indexes, references, datasets, tables) — restraint scales to something real.
**Animations**: BUNDLE_TREE (directory tree draws in, index.md pulses as entry point); FRONTMATTER_ANATOMY (a concept file dissects: YAML block lifts and labels, body highlights, links glow into edges); PROGRESSIVE_DISCLOSURE (agent reads root index → one branch index → one concept; token meter barely moves; contrast: bundle-dump maxes the meter).
**Code**: author two orderflow concepts (WAU metric, orders table) with correct frontmatter; read them with python-frontmatter (Python) and gray-matter (Node); validate `type` presence with error handling.
**Quiz themes**: the single required field; path-as-identity; index.md vs log.md; leniency rules and their tradeoff; what OKF explicitly does NOT include (search/retrieval).

## M07 — OKF for Codebases (Track 3, Cyan)
**Concepts**:
- The pivot: Google's reference use case is BigQuery tables; the same shape maps to services/modules/APIs — swap `resource:` console URL → repo path; swap `# Schema` → `# Responsibilities` / `# Dependencies`.
- Full billing-service concept example (type: Service; Responsibilities owning Invoice/PaymentEvent; Dependencies → customer-service, notifications-service; Citations to runbook).
- Cross-links as a dependency graph richer than the filesystem tree: billing-service formally points at everything it calls and publishes to, independent of repo layout. NOT a substitute for static analysis — it is the curated summary; Graphify's graph is the verified one.
- Root index.md as the agent's pre-flight read (billing domain example) — replaces a full-repo scan or re-embed. "A pre-flight context load, not a search index you query mid-task."
- The okf CLI (Go, Apache-2.0, superops-team, independent of Google): `okf init` (scaffold .okf/knowledge), `okf hook install` (auto-update on commit), `okf search -q "billing"`, `okf lint` (13 built-in spec-compliance rules).
- Go primitives for orchestration: `okf.LoadBundle`, `bundle.Search`, `lint.LintBundle` — search is what an orchestrator calls before dispatching a sub-agent; lint is what CI calls before trusting a bundle.
- Body-structure consistency across concept files matters more for agent consumption than any single field.
- The "attested computation" concept type: a sanctioned, checkable way to COMPUTE a value (vs just documenting what it means) — for governed metrics needing a single source of truth.
- Type drift in multi-team bundles ("API Endpoint" vs "Endpoint" vs "Route") — no registry; only lint + conventions hold the line.
- Kiso: compiles a bundle to a static site (HTML + llms.txt + sitemap.xml) in CI on every merge.
**Animations**: SCHEMA_TO_SERVICE (BigQuery concept morphs field-by-field into a Service concept); LINK_GRAPH (concept files connect by their relative links into a dependency graph overlaying — and differing from — the folder tree); PREFLIGHT (agent reads index.md then exactly two concepts before touching the repo).
**Code**: build the orderflow bundle: index.md + 4 concepts (billing-service, customer-service, orders_fact, WAU) with cross-links; run okf lint mock output; a Python CI validator (frontmatter check + dangling-link check) with real error handling.
**Quiz themes**: what changes when OKF describes code; curated vs verified dependency graph; the 13-rule lint's role; attested computation; type drift.

## M08 — The Enrichment Pipeline: Self-Updating Graphs (Track 3, Cyan)
**Concepts**:
- The gap the spec leaves open: OKF has NO opinion on how bundles get generated or stay true. "Adopting OKF is trivial. The real engineering work is the enrichment-agent pipeline that keeps the graph accurate as code changes."
- Google's reference pattern = two-pass agent: pass 1 walks changed assets and DRAFTS a concept per asset from schema/interfaces; pass 2 adds CITATIONS by cross-referencing runbooks, ADRs, PRs. Skipping pass 2 → plausible-sounding but unverified descriptions.
- The pipeline: commit pushed → diff-scoped scan (which services changed?) → draft/update concepts → re-link cross-references (both sides: dependency AND dependents) → lint (hard gate) → publish (commit bundle / CI / catalog).
- DIFF-SCOPED, ALWAYS: full-repo rescans on every commit make the pipeline too expensive before the repo is big enough to need it. Diff-scoping is what makes per-commit runs affordable.
- End-to-end trace: dev adds fraud-check dependency to billing-service → hook fires → pass 1 rewrites # Dependencies → pass 2 cites the PR → cross-refs updated both directions → lint → publish → next day an unrelated agent loads ONE concept file and already knows the relationship.
- Graphify↔OKF integration (shipped Jul 1 2026): `graphify export --format okf --out docs/knowledge/` — structural graph exported into narrative catalog; bundles typically at docs/knowledge/ or .well-known/okf/.
- log.md maintenance as part of the pipeline; the LLM-as-librarian principle: "LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass."
- Adoption gate: skip it if nothing consumes the bundle yet — "you are maintaining a wiki nobody reads." Start with your most-changed service, not the whole repo; measure the token delta before full rollout. Claimed ~95% token reduction vs naive loading for stable domains is anecdotal — label it as such.
**Animations**: PIPELINE_FLOW (commit travels through the six stages, diff-scope filter shrinking the work); TWO_PASS (pass 1 drafts a file skeleton; pass 2 draws citation threads to runbook/PR nodes); BOTH_SIDES (a new dependency updates billing-service.md AND fraud-check.md dependents section).
**Code**: a working mini enrichment hook in Python: parse `git diff --name-only HEAD~1`, map changed files → services, regenerate the affected concept's # Dependencies from the Graphify graph.json, update log.md, run lint, fail loudly on error. Node tab equivalent.
**Quiz themes**: why two passes; why diff-scoping is the cost model; lint as CI gate; when NOT to adopt; what export --format okf bridges.

## M09 — Serving Graphs to Agents over MCP (Track 4, Orange)
**Concepts**:
- The last mile: a bundle on disk helps nobody until an agent can query it. Serving options: slash-command skill (Graphify), MCP server (okf-mcp, CodeGraph, graphify.serve), pre-flight file reads (index.md).
- okf-mcp tool surface: `search`, `graph_callers`, `graph_callees`, `graph_api`, `graph_cycles`, `graph_modules`, `graph_path`, and composite `explore` (signature + description + callers + callees + blast radius + API membership + cycles in ONE call — token budget for reasoning, not tool-call overhead).
- One-line registration: `claude mcp add okf-rs -- /path/to/okf-mcp /path/to/project`; plain MCP over stdio = vendor-neutral: same binary serves Claude Code, opencode, any MCP client.
- Token economics worked example: "who calls cmd_generate?" by hand = open a 672-line ~24KB file ≈ 6,000 tokens; graph_callers = one line ≈ 15 tokens (~400x for that query). Compounds per-query (parse cost paid once at generate time) and per-session (no re-opening files after context compaction — flat context use vs growing).
- Progressive disclosure as serving strategy: orchestrator reads index.md, routes sub-agents to specific concept files; MUST be designed into the orchestration layer — bolting OKF onto an agent that dumps directories gets maintenance cost without savings.
- The MCP cache trap (foreshadow M11): servers cache graph.json at startup with no hot-reload — fresh graph on disk, stale graph in the agent's memory; restart or hot-reload after regeneration.
- Honest expectations recap: per-query ratios are real; session-level savings depend on corpus topology and task mix (6.8x–49x range).
**Animations**: MCP_HANDSHAKE (client/server frames: tools/list then graph_callers call/response); TOKEN_SCALE (a 24KB file vs a one-line answer on a balance scale with token counts); ORCHESTRATOR_ROUTE (orchestrator reads index, dispatches two sub-agents each loading only their concept).
**Code**: minimal MCP server in Python over graph.json (list tools; implement graph_callers/graph_callees via reverse adjacency; stdio transport; error handling for unknown symbols) + registration; Node tab.
**Quiz themes**: why MCP beats file-dumping; the explore composite rationale; the 6000-vs-15 arithmetic; the startup-cache trap; what progressive disclosure requires of the orchestrator.

## M10 — The Hybrid Context Stack (Track 4, Orange)
**Concepts**:
- Three layers, not three competitors: Vector RAG (docs/tickets/Slack — the unstructured long tail), Graphify/structural (AST call graphs, hierarchies, imports), OKF/narrative (architecture, schemas, playbooks). "Graphify extracts what the code IS, OKF curates what engineers KNOW, RAG searches the unstructured remainder."
- Failure-mode-driven adoption (the decision framework): observe a concrete failure first. Trigger 1 multi-hop reasoning failure → add structural graph. Trigger 2 tribal-knowledge sprawl (valid code violating unwritten conventions) → add OKF. No observed failure → add nothing ("adding layers without a failure mode increases complexity without improving performance").
- The staged query pipeline: Stage 1 OKF progressive disclosure (~2K tokens narrative orientation) → Stage 2 Graphify structural traversal (zero LLM cost) → Stage 3 vector/sparse search for the unstructured remainder ("What breaks if I modify UserService.py?").
- The router pattern: canonical question ("SLA for Sev-1?") → deterministic OKF read; exploratory question ("themes in churn interviews?") → vector search.
- ERPNext case study: 1M+ LOC Python/JS, Claude Opus 4.8, 14-turn cap: baseline 70.8% key-fact coverage vs hybrid 82.0% (~140K tokens/session). An 11.2-point accuracy gain is a better production signal than any token-reduction multiple.
- Hallucination context: legal-domain RAG hallucinates in 17–33% of complex queries — retrieval alone fails multi-document logic.
- Decision matrix by codebase shape (monolith / microservices / monorepo) × failure mode; "RAG first, graph when depth becomes a bottleneck."
- MCP vs RAG vs OKF role separation: OKF = knowledge written in advance; MCP = live connection to systems; RAG = on-the-spot retrieval. WAU definition lives in OKF; the actual BigQuery query runs via MCP; OKF bundles can themselves be RAG targets ("RAG, pointed at something worth retrieving from").
**Animations**: THREE_LAYER_STACK (query hits router, routes animate by question type); STAGED_PIPELINE (one query descends three stages, token meter incrementing 2K → +0 → +search); DECISION_TREE (underperforming agent → symptom branch → tool trigger).
**Code**: a router agent skeleton: classify query (canonical/structural/exploratory) → dispatch to bundle read / graph query / vector search; Python + Node tabs with fallbacks and logging.
**Quiz themes**: which layer owns which context; the two failure triggers; stage order and why; ERPNext numbers; router classification.

## M11 — Production Operations: Drift, Staleness & Observability (Track 5, Green)
**Concepts**:
- The core insight: graphs don't self-heal. Graphify builds a STATIC index; without working hooks it silently drifts. "A stale structural graph is worse than no graph — it provides high-confidence wrong answers." Documented: GRAPH_SUMMARY.md two weeks stale on origin/main, still handed to agents as ground truth. "If you refactor a module and forget to rerun /graphify, your agent is navigating with a stale map."
- The failure mode is not "wrong once" — it's wrong with ZERO signal: update reports success, hook ran, nothing crashed, the map lies.
- Four documented silent-failure mechanisms (from real issue trackers): (1) Windows hooks use nohup, which Git-for-Windows' shell lacks — rebuild never happens, no error; (2) the hook's hardcoded CODE_EXTS allowlist drifted from detect.py — valid code commits don't trigger rebuilds; (3) resource gating (psutil CPU ≤50%, ≥2GB free) silently skips, "next commit retries" = unbounded staleness on quiet branches; (4) MCP servers cache graph.json at startup, no hot-reload — fresh on disk, stale in memory.
- Artifact desync: graph.json / graph.html / GRAPH_REPORT.md can tell different stories with no built-in cross-check.
- The scale wall: betweenness centrality O(V×E); 450K nodes × 690K edges ≈ 310 billion ops, single-threaded; 96-core Xeon killed at 114 min; M3 Pro ~10 min on a smaller repo — cost non-linear and hardware-unpredictable. "Incremental" means smaller-than-full, not fast (0.8s vs 10+s reported).
- Ops hygiene: gitignore graphify-out/ or every regen dirties the tree and blocks CI.
- The production checklist: (1) log rebuild success/failure with timestamps — never trust exit codes; (2) CI cross-check: artifacts agree with each other AND are recent vs `git log -1`; (3) restart/hot-reload MCP servers after regen; (4) resource-gating only WITH a scheduled catch-up job + staleness alert threshold; (5) verify you're above the ~500-file payoff floor.
- OKF-side governance: leniency lets bundles silently degrade (broken links, drifted types are all spec-conformant); lint as hard CI gate is "the only thing standing between technically conformant and actually useful."
- The definitional test: "Write down, concretely, how you would detect a stale graph within 24 hours. If you can't answer in specific mechanical terms, you have a demo that hasn't failed yet."
**Animations**: DRIFT_TIMELINE (code commits accumulate; graph timestamp freezes; divergence gap widens; agent confidently answers from the frozen side); SILENT_FAILURES (four doors: each hook failure path ends in a green "success" light over a red state); FRESHNESS_GATE (CI compares artifact timestamps vs HEAD; stale → pipeline blocks with alarm).
**Code**: a freshness-gate script (Python): compare graph.json mtime + embedded counts vs git log -1 timestamp; cross-check three artifacts agree; exit nonzero + alert on threshold breach; a staleness-alert cron pattern. Node tab.
**Quiz themes**: the four silent failure mechanisms; why "incremental ≠ fast"; the artifact cross-check; what the 24-hour test asks; resource gating done right.

## M12 — Structuring Projects So Agents Don't Get Lost + What's Next (Track 5, Green)
**Concepts** (the human-side complement — six patterns):
- Pattern 1 layered CLAUDE.md: root = repo-wide rules only (~40 lines); per-package files add stack-specifics; loads cwd→root. Before/after: 340-line root file → 147 file reads; layered → ~4 reads in main context.
- Pattern 2 skills for procedures: facts every session → CLAUDE.md; procedures/references → .claude/skills/ loaded on demand (api-testing SKILL.md example).
- Pattern 3 subagents for isolated exploration: 40 file reads stay in the subagent's context; main gets a 200-word summary; caveat — summaries lose detail (line numbers may need re-reads).
- Pattern 4 permission deny rules: block reads of generated/vendored code (dist/, *.generated.*, vendor/) — caveat: also blocks your own explicit read requests.
- Pattern 5 sparse worktrees: worktree.sparsePaths → only needed packages checked out (git 2.25+).
- Pattern 6 code-intelligence plugins: LSP answers "where is refreshAuthToken used?" with zero file reads; pairs with deny rules.
- When to use each pattern (trigger conditions); the combined effect: 147 reads/35 min → 4 reads/6 min.
- Connection to the course: these patterns are progressive disclosure by hand; the graph tools automate the same principle.
- **What's Next**: OKF v0.2 direction (provenance, verification, freshness as first-class); trust systems over self-updating wikis; org-scale serving (okf-server REST/GraphQL, org-wide indexing); ecosystem watch-list (Gbrain memory infra, Kiso publishing, ai-context-hooks — capturing pre-knowledge context); open problems: type registries, typed links vs RDF/OWL reasoning, long-running production case studies (none exist yet — the spec is months old); how to evaluate new tools (the M05 comparison axes + M11's 24-hour test).
**Animations**: CONTEXT_BUDGET (stacked bar of what fills 200K tokens before any code is written; layered setup shrinks each band); PATTERN_PICKER (symptom → pattern flowchart); ROADMAP (timeline extending past today into v0.2 territory, marked "unproven").
**Code**: the layered CLAUDE.md pair (root + package) for orderflow; a deny-rules settings.json; a SKILL.md example — all complete files.
**Quiz themes**: fact-vs-procedure placement; what subagent isolation preserves; deny-rule tradeoff; which pattern for which symptom; what v0.2 adds.

## CAPSTONE — Build a Self-Updating Knowledge Graph Pipeline (Gold, ★★★★☆, 12–18 steps, ~2–3 hours)
**Brief**: You are the platform engineer for orderflow. Agents keep re-deriving its structure and violating its conventions. Build the full three-layer context system: structural graph + OKF bundle + enrichment hook + MCP serving + CI freshness gate.
**Phases**:
1. Baseline measurement: ask 3 structural questions with no graph; record file-reads/tokens.
2. Structural layer: run Graphify (or the provided pure-Python extractor `kg_extract.py` for offline learners) → graph.json; inspect communities and god nodes.
3. Narrative layer: author the OKF bundle (index.md + 5 concepts + log.md) with cross-links.
4. Enrichment hook: git post-commit → diff-scoped concept refresh + log.md append + lint gate.
5. Serving: minimal MCP server exposing search/graph_callers/graph_callees/explore over graph.json + bundle.
6. Freshness gate: CI script cross-checking artifact timestamps vs HEAD; break it on purpose (commit without hook) and watch the gate catch it.
7. Re-measure the 3 questions; compare honestly (expect single-digit-x, not 71x, on a repo this small — that's the lesson).
**Test cases**: 3 happy path (callers query, impact query, canonical WAU definition), 1 edge (symbol not in graph → graceful miss + fallback to grep), 1 failure (stale graph → freshness gate blocks with actionable error).
**Extensions (OPTIONAL)**: two-pass enrichment with citations; graph.html visualization; a router agent (M10); okf-rs comparison run; export to Obsidian.

## CAPSTONE-2 — Large Java Codebase: Measure the Token Reduction (Gold, ★★★☆☆, optional bonus, ~90–120 min)
**Brief**: Capstone 1's repo was deliberately below the ~500-file floor. Here the learner graphs a REAL large Java codebase and produces their own benchmark table — experiencing both halves of the course's central claim: per-question structural lookups are enormously cheaper via a graph, and the advantage grows with the haystack.
**Tools built for this capstone (all tested)**:
- `labs/shared_tools/kg_extract_java.py` — tree-sitter-java extractor, same graph.json schema as the Python one; EXTRACTED (same file) / INFERRED (unique cross-file) / AMBIGUOUS (2–8 candidates); names with >8 definitions are DROPPED as unresolved (a call to a name defined 150 times carries no structural signal — real tools escalate to type resolution, M03's LSP ladder).
- `labs/CAPSTONE-2-java-token-benchmark/gen_java_repo.py` — seeded synthetic Java repo generator with known_truth.json (god node Registry.lookup; on the full 1,491-file output it has exactly 1,192 seeded callers).
- `labs/CAPSTONE-2-java-token-benchmark/solution/measure_tokens.py` — deterministic two-arm benchmark: BASELINE = grep call-site pattern `\bname(`, charge full size of every matched file (the honest floor for a CORRECT answer); GRAPH = MCP answer size + amortized 700-token orientation read. Auto-selects symbols by CALLER COUNT (structural relevance), never by grep expense — selecting by grep expense would manufacture a ceiling case, the exact benchmark sin the course teaches.
- M09 server gained `--graph <path>` to serve any pre-built graph.json.
**Measured reference results (real runs, 2026-08-24 snapshots)**:
| Repo | Files | Nodes/Edges | Files opened/question | Aggregate per-question |
|---|---|---|---|---|
| synthetic-mini | 91 | — | 22 | 8.0x (87.5%) |
| commons-lang | 624 | 10,648 / 40,309 | 46 | 116.5x (99.1%) |
| synthetic | 1,491 | 7,008 / 5,960 | 303 | 13.5x (92.6%) |
| spring-framework | 9,195 | 110,885 / 432,741 | 567 | 33.7x (97.0%) |
Spring headline: 8 questions by exploration = 4,535 files opened ≈ 15.2M tokens; via graph ≈ 451K. Extraction: spring 2m27s, commons-lang 12s.
**Teaching points (Honesty Rule central)**: per-question vs session-level multiples (okf-rs's ~400x/query vs replicated 6.8x–49x sessions); why commons-lang's multiple EXCEEDS spring's (bigger answers: more callers + AMBIGUOUS candidates raise the graph arm's cost — answer quality trades against raw reduction); why published OkHttp = only 13% (session-level, small haystack); Windows longpaths for the spring clone; the M11 tie-in (2.5-min rebuild → how do you detect staleness within 24h — the Capstone-1 freshness gate works unchanged).
**Phases**: extract → verify against ground truth (the step no benchmark reader ever does) → serve over MCP (--graph) → measure at ≥2 repo sizes → honest writeup → optional live `claude -p` comparison (expect a smaller live gap; understanding why is the graduation exercise).
**Test cases**: spring callers query (1 tool call), synthetic exact-count check, graceful miss on unknown symbol, `--symbols toString` → unresolvable row (graph declines to guess).

## M02B — The Context Engineering Frame (Track 1, Indigo, bridge module — after M02, before M03; badge "Module 2B · Bridge", additive to the 14-part numbering)
**Purpose**: couple this course with the sibling course's M03B (Context Engineering). Everything Tracks 2–5 build is one of M03B's four levers, industrialized. This module makes the mapping explicit so learners from either course can hop across.
**Canonical definitions (quote from sibling M03B)**:
- "Context engineering is the practice of deciding what content occupies the model's context window on each turn, in what order, and how it is compressed or fetched. Prompt engineering is a sub-discipline… The first is a writing problem. The second is a budgeting problem."
- "Context rot is the degradation of agent quality caused by accumulated stale, contradictory, or low-relevance content in the context window… you can hit context rot at 60% window utilization. The key signal is signal-to-noise ratio, not raw size."
**The six layers** (system, tools, history, retrieved, tool results, current turn) with M03B's illustrative numbers (turn-8 agent: 420/1,180/3,250/2,800/1,950/85 = 9,685 tokens; user message 0.9%). Where each KG artifact lands: MCP tool schemas → tools layer; concept files → retrieved; graph answers → tool results; index.md pre-flight → the static prefix of history.
**The four levers → this course's machinery (THE mapping table)**:
| Lever (M03B) | What it means | Industrialized by |
|---|---|---|
| add | put it in context | M12 layered CLAUDE.md (facts every session needs) |
| compress | same info, fewer tokens | GRAPH_REPORT.md / 700-token orientation reads (M04, M09); summaries |
| retrieve | fetch on demand instead of carrying | structural graph queries (M03–M05, M09: "answers, not leads"); vector RAG for the long tail (M02, M10) |
| offload | external memory something else maintains | OKF bundle + log.md (M06–M08); MCP servers (M09); subagents (M12) |
Note the taxonomy fork: the sibling's opensource track uses crop/compress/summarize/select; this course uses the Claude-track add/compress/retrieve/offload; crop shows up here as deny rules (M12) and AMBIG_CAP-style refusal (Capstone 2).
**Two altitudes of context rot**: transcript rot (stale tool dumps, superseded instructions — M03B's poisoned transcript) vs infrastructure rot (graph drift, M11's "a stale structural graph is worse than no graph"). Same signal-to-noise disease; the freshness gate is compaction for infrastructure.
**Static-first ordering ⇄ index.md**: M03B's caching rule ("same content in the wrong order can cost 6x more") is why the bundle's index.md is a stable pre-flight read; lost-in-the-middle is why `explore` (M09) returns one compact composite answer instead of scattering facts across a long context.
**Lab (labs/M02B-context-levers)**: fix a poisoned orderflow transcript the two ways the sibling lab left unimplemented — retrieve (one graph_callers/explore answer replaces duplicated grep dumps) and offload (one canonical WAU concept read replaces in-history definition sprawl) — and compare all four arms (raw / compress / retrieve / offload) in tokens + key-fact preservation. Success criterion mirrors the sibling's: the fixed runs must still cite the key facts while spending materially fewer tokens.
**Animations**: SIX_LAYERS (stacked token meter, the 9,685-token inventory); LEVER_MAP (four levers light up their KG-course counterparts); ROT_TWO_ALTITUDES (transcript rot and graph drift progressing side-by-side toward the same wrong answer).
**Quiz themes**: prompt vs context engineering; which lever a given KG mechanism implements; the 60%-utilization point; the two rot altitudes; why index.md ordering matters for caching.

### CAPSTONE-2 addendum — the reference live run (2026-08-24)
Live `claude -p` comparison on the spring snapshot (Sonnet both arms; 2 structural + 2 logic questions; data in labs/CAPSTONE-2-java-token-benchmark/expected_output/live-run-summary.json): the graph arm LOST — 859K tokens/$0.51/23 turns vs baseline 512K/$0.37/14 turns (+68%), comparable answer quality. Four causes taught in the module's "What a Real Live Run Looks Like" section: line-granular Grep undercuts the whole-file floor; bare-name fan-out bloats graph answers (~11K tokens for registerBeanDefinition) vs type-resolved compact answers; the model cross-verifies graph claims (S2: 9 turns); logic questions are a wash (+2%). Frame as THE THREE QUANTITIES: mechanical floor (33.7x) vs replicated session ranges (6.8x–49x) vs your-stack-live (0.6x here) — all correct, different measurements; only the third describes your setup.

### CAPSTONE-2 addendum 2 — the multi-session campaign (2026-08-24, supersedes single-run numbers)
3 independent fresh sessions per cell (24 total, $2.59): medians — baseline 585K tokens/15 turns vs graph 1,004K/26 (+71%; structural +119%, logic +38%). Identical sessions varied up to 2x (L2 graph: 114K–228K); the single-run "+2% logic wash" did not survive medians. Teach: run-N-report-medians is the CodeGraph methodology and the only defensible way to quote live numbers; cache-read share was 91–96% and rose across reps (server-side prompt-cache warming across sessions — report the split, don't hide it). Raw data: labs/CAPSTONE-2-java-token-benchmark/expected_output/live-run-multi.json.

### CAPSTONE-2 addendum 3 — corrected three-way live campaign (2026-08-25, SUPERSEDES addenda 1-2's live numbers)
Both earlier live campaigns were INVALID for the graph arm: the M09 server crashed at startup in every session (mcp SDK 2.x renamed FastMCP -> mcp.server.MCPServer; server.py now imports both) and the failure was silent — with file tools as fallback the agent just noted "tools unavailable" and explored anyway. Caught only by adding a graph-FORCED arm (no fallback to hide behind). Corrected medians-of-3 (Sonnet, spring snapshot, raw data in labs/CAPSTONE-2-java-token-benchmark/expected_output/live-run-multi.json, 30 runs): structural totals baseline 240K / graph-available 570K / graph-forced 178K tokens. Teach: (1) forcing the graph (Graphify-style, MCP-only) unlocks the win — 1 turn/42K on the callers question vs 116K baseline; optional availability HURTS (+137%) because the model re-verifies fan-out answers; (2) fan-out remains the poison (forClass ~tied even forced, spread 45K-698K); (3) logic questions unmoved and unanswerable by forced-graph; (4) the silent-server incident is M11's thesis eating its own benchmark — the forced arm doubles as a canary; verify serving before trusting any live measurement; (5) forced-arm dollar-cost anomaly vs token counts reported openly — tokens/turns are the trustworthy columns.

### CAPSTONE-2 addendum 4 — forced-arm logic results complete the grid (2026-08-25)
Forced-graph on the logic questions: answered BOTH correctly by walking callee edges (override-guard chain; post-processor phase re-scan) but at ~2x baseline cost (L1 524K/12 turns vs 231K/6; L2 234K/8 vs 114K/3). Full-grid medians: structural 240K/570K/178K, logic 345K/389K/758K, all-four 585K/959K/936K (baseline/available/forced). Teach: (1) the graph can SUBSTITUTE for reading code at comprehension, expensively — it cannot beat it; (2) prior-knowledge confound: Spring is in training data, so edge-walking "confirms" partly-known logic — on private code, graph-shaped confidence over unread code is a hallucination risk; (3) the synthesis is M10's router, now measured: structural→forced-graph + logic→files ≈ 523K vs 585K all-baseline. Raw data (36 runs) in expected_output/live-run-multi.json.

### CAPSTONE-2 addendum 5 — fourth arm (init/CLAUDE.md) + shipped tooling (2026-08-25)
Init arm: headless CLAUDE.md written into all 22 spring-* modules (~$3.40, ~35s each; /init doesn't fire in -p mode — use an explicit instruction), then baseline-tool sessions. Medians: init 600K vs baseline 585K (+2% wash) hiding texture — S1 −30% (2 turns; the map worked), S2 +58% (loaded context never paid). Teaching: the add lever provides orientation/conventions, not lookup; per-session wash, one-time cost amortizes only if sessions hit the winning pattern. Full four-arm grid: 585K/600K/959K/936K (baseline/init/available/forced); 48-run dataset in expected_output/live-run-multi.json. The benchmark tooling now SHIPS in labs/CAPSTONE-2-java-token-benchmark/live_bench/ (run_live_bench.py with 4 arms + contamination recording, init_claude_mds.py with --remove, aggregate.py, questions.json, mcp template) and the module gained a "Run These Benchmarks Yourself" section (id run-it-yourself) with the six methodology rules, each bought with a real mistake (fresh-session medians, arm order/contamination, forced-arm-as-canary, one variable per arm, single-line prompts on Windows, cost budgeting).
