# The Four Benchmark Scenarios — Full Documentation

This document describes the four scenarios ("arms") we tested against spring-framework (9,195 Java files), exactly how each was configured, how to reproduce each step by step, what we measured, and what went wrong along the way. Every number is a **median of 3 independent fresh `claude -p` sessions** (Sonnet in all arms); the 48-run raw dataset is in `../expected_output/live-run-multi.json`.

The question set (in `questions.json`) mixes two classes on purpose:
- **Structural** (S1, S2): "who calls X?" — answerable from a call graph
- **Logic** (L1, L2): "why does X happen / how does mechanism Y work?" — requires comprehension

Common setup for every scenario:

```bash
# one-time: the structural graph and the MCP server (Capstone-2 Phases 1-3)
python ../../shared_tools/kg_extract_java.py D:/tmp/spring-framework --out D:/tmp/spring-graph.json --quiet
python ../../M09-mcp-graph-server/solution/server.py --graph D:/tmp/spring-graph.json   # smoke-test: must print "serving over stdio"
cp mcp-config.template.json mcp.json    # then edit both paths to absolute ones
```

---

## Scenario 1 — `baseline`: a normal agent, nothing added

**What it simulates:** the out-of-the-box experience — an agent with file tools and no curated context of any kind. This is the control every other scenario is measured against.

| | |
|---|---|
| Tools allowed | `Read`, `Glob`, `Grep` |
| Prompt extras | none (just the question + an effort cap) |
| Repo state | clean — **zero CLAUDE.md files** (the runner records the count per run and warns if nonzero) |

**Steps:**
```bash
cd labs/CAPSTONE-2-java-token-benchmark/live_bench
python run_live_bench.py D:/tmp/spring-framework --arms baseline --reps 3
```
Run this scenario FIRST — before Scenario 2 ever touches the repo — or your control is contaminated.

**Measured:** structural 240K tokens, logic 345K, all-four **585K** — the number to beat.

**Key insight:** this arm is far stronger than the mechanical benchmark predicts (33.7x), because a real agent's Grep returns matching *lines*, not whole files. It answered "who calls registerBeanDefinition" in 3 turns without opening files wholesale. Any tool that wants to beat it has to beat *line-granular grep*, not the whole-file strawman.

---

## Scenario 2 — `init`: curated CLAUDE.md context (the ADD lever)

**What it simulates:** a team that invested in per-module context files — M12's layered-CLAUDE.md pattern. Claude Code auto-loads a module's CLAUDE.md when the agent works inside that directory, so the curated orientation rides along "for free" — except nothing is free in tokens.

| | |
|---|---|
| Tools allowed | `Read`, `Glob`, `Grep` — **identical to baseline** |
| Prompt extras | none — the ONLY variable is the repo state |
| Repo state | a CLAUDE.md in **every** `spring-*` module (22 files) |

**Steps:**
```bash
# 1. generate the context files headlessly (~$0.15/module, ~35s each, resumable)
python init_claude_mds.py D:/tmp/spring-framework --prefix spring-
#    gotcha: `/init` does NOT fire in `claude -p` mode — the script uses an
#    explicit "analyze this module and Write CLAUDE.md" instruction instead
# 2. run the arm
python run_live_bench.py D:/tmp/spring-framework --arms init --reps 3
# 3. restore the clean repo so later baseline runs stay valid
python init_claude_mds.py D:/tmp/spring-framework --remove
```

**Measured:** structural 278K (+16%), logic 321K (−7%), all-four **600K (+2%)** — a wash, plus the one-time ~$3.40 generation cost.

**Key insight:** the +2% average hides the real story. On S1 the CLAUDE.md map sent the agent straight to the right module — **81K tokens, 2 turns, a 30% win**. On S2 the auto-loaded context never paid for itself — **+58%**. CLAUDE.mds are *orientation and conventions* context, not a lookup index; they pay off when a session's first problem is "where do I even start?", and cost overhead when it isn't. The generation cost amortizes only across many sessions that hit the winning pattern.

---

## Scenario 3 — `available`: graph offered, not imposed (the RETRIEVE lever, optional)

**What it simulates:** the common real-world integration — a graph MCP server registered alongside normal tools, with guidance to prefer it. The agent chooses.

| | |
|---|---|
| Tools allowed | `Read`, `Glob`, `Grep` **+** `graph_callers`, `graph_callees`, `explore` |
| Prompt extras | "Prefer the graph tools for caller/callee questions; fall back to Read/Grep only when the graph cannot answer" |
| Repo state | clean |

**Steps:**
```bash
python run_live_bench.py D:/tmp/spring-framework --arms available --reps 3 --mcp-config mcp.json
```

**Measured:** structural 570K (**+137% — the worst arm**), logic 389K (+13%), all-four 959K.

**Key insight:** optionality actively hurts with a fan-out-heavy graph. The model queries the graph, receives a 1,000+-candidate bare-name answer, doesn't fully trust it, and then re-verifies against files — **paying for both retrieval paths** (S2: 10 turns, 415K). The distrust is *rational* given our teaching-grade graph's AMBIGUOUS fan-out; a type-resolved production graph earns trust with compact answers. Lesson: "we added a graph and told the model to prefer it" is not an integration strategy.

---

## Scenario 4 — `forced`: graph as the only tool (the Graphify-style integration)

**What it simulates:** a forced integration where the graph is the single search surface — no file access at all. This is what Graphify-style skills effectively do for structural queries.

| | |
|---|---|
| Tools allowed | `graph_callers`, `graph_callees`, `explore` — **nothing else** |
| Prompt extras | "They are your ONLY tools… note honestly if AMBIGUOUS provenance makes parts uncertain" |
| Repo state | clean |

**Steps:**
```bash
# structural questions only by default:
python run_live_bench.py D:/tmp/spring-framework --arms forced --reps 3 --mcp-config mcp.json
# include the logic questions too (expensive, see below):
python run_live_bench.py D:/tmp/spring-framework --arms forced --reps 3 --mcp-config mcp.json --forced-logic
```

**Measured:** structural **178K (−26% — the only arm that beat baseline)**, with S1 answered in **1 turn at 42K**. Logic 758K (+120%): the agent answered both "why" questions *correctly* by walking callee edges — but at double the cost of just reading the file, and with a confound: Spring is in the model's training data, so edge-walking partly "confirmed" logic it already knew. On a private codebase, that same graph-shaped confidence over unread code is a hallucination risk.

**Key insight (two of them):**
1. **Forcing is what unlocks the structural win** — remove the option to double-check and the graph's one-call answers finally beat grep.
2. **The forced arm is a canary.** Our first two campaigns measured a "graph arm" whose MCP server was silently crashing at startup (an SDK import rename); with file tools available, the failure was invisible — sessions just fell back and produced plausible numbers. Only the forced arm, having no fallback, reported "tools unavailable" and exposed it. Run a forced smoke session before trusting ANY graph-arm measurement.

---

## The combined result

| Scenario | Structural | Logic | All four |
|---|---|---|---|
| 1 baseline | 240K | 345K | **585K** |
| 2 init | 278K (+16%) | **321K (−7%)** | 600K (+2%) |
| 3 available | 570K (+137%) | 389K (+13%) | 959K |
| 4 forced | **178K (−26%)** | 758K (+120%) | 936K |

**No scenario wins everywhere — that IS the finding.** Forced-graph owns structural lookups; plain files own comprehension; CLAUDE.mds help orientation and cost a little everywhere else; an optional graph is the worst of both worlds. The synthesis is M10's router, now derived from data: route structural questions to the forced graph and everything else to files ≈ **523K** for this question set vs 585K all-baseline — with each layer serving only the question class it's good at.

## Reading your own results (the six rules)

1. **Medians of ≥3 fresh sessions** — identical sessions varied up to 2x; one run is a coin flip.
2. **Scenario order matters** — baseline before init; the runner's per-run `repo_claude_md_count` audits this.
3. **Forced-arm smoke test first** — a silently broken server + graceful fallback = confident garbage.
4. **One variable per scenario** — same model, same questions, same repo snapshot everywhere.
5. **Windows: single-line prompts** — the `.cmd` shim truncates argv at newlines.
6. **Budget up front** — ~$0.10–0.40/session at Sonnet; a full 4-arm campaign on this repo ran ≈ $10 including the init pass.
