# CAPSTONE-2 — Large Java Codebase: Measure the Token Reduction

**Difficulty**: ★★★☆☆ (6 phases, ~15 steps, ~90–120 min) · **Optional bonus** after Capstone 1.

## Project Brief
Capstone 1 built the full stack on a 15-file repo — deliberately below the ~500-file payoff floor, so your measured multiple was small. This capstone flips it: you graph a **real, large Java codebase** and produce your own benchmark table — the same shape as the published ones the course taught you to read skeptically (M04/M05). By the end you'll have measured, with your own numbers, both halves of the course's central claim: *per-question structural lookups are enormously cheaper through a graph, and the advantage grows with the size of the haystack.*

## What You'll Build
```
kg_extract_java.py  ──►  graph.json  ──►  MCP server (M09, --graph flag)
        │                                        │
   [Java repo]                          measure_tokens.py
   commons-lang (624 files)                      │
   spring-framework (9,247 files)         your benchmark table
   synthetic (offline fallback)           (per-question + aggregate)
```

## Targets (pick at least two sizes — the comparison IS the lesson)
| Target | Files | How |
|---|---|---|
| synthetic-mini | ~91 | `python gen_java_repo.py <dir> --files 100` (offline, known ground truth) |
| commons-lang | 624 | `git clone --depth 1 https://github.com/apache/commons-lang.git` |
| synthetic | ~1,491 | `python gen_java_repo.py <dir>` (offline, known ground truth) |
| spring-framework | 9,247 | `git -c core.longpaths=true clone --depth 1 https://github.com/spring-projects/spring-framework.git` (Windows: longpaths required, clone to a SHORT path like `D:\tmp`) |

## Phase 1 — Extract (steps 1–3)
1. `pip install tree-sitter tree-sitter-java` (already in labs/requirements.txt).
2. Extract each target:
```bash
python ../shared_tools/kg_extract_java.py <repo> --out <repo>-graph.json --quiet
```
Expected shape (commons-lang): `Rebuilt: 10648 nodes, 40309 edges` with `EXTRACTED: 2055, INFERRED: 5921, AMBIGUOUS: 32333` and an `unresolved` line dropping over-ambiguous names (`append`, `toString`, `get`…). Spring: `110885 nodes, 432741 edges` in ~2.5 min.
3. ✅ Checkpoint — note what the `unresolved` line tells you: a bare-name resolver DECLINES to guess when a name has >8 definitions. Java overloading makes AMBIGUOUS provenance common; M03's LSP ladder is how real tools do better.

## Phase 2 — Verify against ground truth (steps 4–6)
4. On a synthetic target, compare against `known_truth.json`: the god node `Registry.lookup` must have exactly the seeded caller count (1,192 on the full synthetic).
5. On commons-lang, hand-verify 2 edges: pick a caller from `graph_callers("capitalize")` output and open the file/line to confirm the call site exists.
6. ✅ Checkpoint — you have done what no benchmark reader ever does: verified the instrument before trusting its numbers.

## Phase 3 — Serve (steps 7–8)
7. The M09 server now takes `--graph`:
```bash
python ../M09-mcp-graph-server/solution/server.py --graph <repo>-graph.json
claude mcp add java-graph -- python /abs/path/server.py --graph /abs/path/<repo>-graph.json
```
8. ✅ Ask through your assistant: "who calls `registerBeanDefinition`?" — one tool call, no file reads. Also test the graceful miss: an unknown symbol must return `error: ... try grep`, not a crash.

## Phase 4 — Measure (steps 9–11)
9. Run the harness on each target:
```bash
python solution/measure_tokens.py <repo> <repo>-graph.json --questions 8 --json bench-<name>.json
```
10. Reference results (yours will match closely — the harness is deterministic per repo snapshot):

| Repo | Files | Files opened/question | Aggregate per-question multiple |
|---|---|---|---|
| synthetic-mini | 91 | 22 | 8.0x |
| commons-lang | 624 | 46 | 116.5x |
| synthetic | 1,491 | 303 | 13.5x |
| spring-framework | 9,195 | 567 | **33.7x** (97.0% reduction) |

11. ✅ Checkpoint — spring's headline row: answering 8 structural questions by exploration means opening **4,535 files (~15.2M tokens)**; through the graph it costs ~451K tokens.

## Phase 5 — The honest writeup (steps 12–14)
12. In `NOTES.md`, explain the number you produced:
    - These are **per-question** multiples (same class as okf-rs's ~400x/query) — NOT session-level savings (replications: 6.8x–49x), because sessions also spend tokens on reasoning and edits a graph can't remove.
    - Why does commons-lang show a HIGHER multiple than spring? (Spring's answers are bigger — more callers, more AMBIGUOUS candidates — so the graph arm costs more per answer. Answer quality and ambiguity trade against raw reduction.)
    - Why did the published OkHttp number land at only 13%? (645 files, session-level measurement, small haystack.)
13. Plot or tabulate files-opened-per-question vs repo size across your runs — the exploration burden curve is the course's central claim, now in your own data.
14. ✅ The M11 question, again: your spring graph took ~2.5 min to build. How would you detect it going stale within 24 hours? (Your Capstone-1 freshness gate works unchanged here.)

## Phase 6 — OPTIONAL live measurement (step 15)
15. With an API key and quota: ask `claude -p` the same 2 questions with and without the MCP server registered and compare the reported token usage. Expect the live gap to be smaller than the harness's mechanical floor — the live agent reads files partially and reasons either way. Write down both numbers; understanding WHY they differ is the graduation exercise.

## Test Cases
| # | Type | Input | Expected |
|---|---|---|---|
| 1 | happy | `graph_callers("registerBeanDefinition")` on spring graph | non-empty caller list, one tool call |
| 2 | happy | synthetic `graph_callers("lookup")` | exactly the seeded caller count from known_truth.json |
| 3 | happy | harness on any target | table + aggregate + honesty notes render |
| 4 | edge | `graph_callers("notASymbol")` | graceful `error: ... try grep` |
| 5 | edge | harness question on an over-ambiguous name (`--symbols toString`) | row marked unresolvable — the graph declines to guess |

## Going Further (OPTIONAL)
- Wire the Capstone-1 freshness gate to the spring graph in CI.
- Run Graphify or CodeGraph over commons-lang and diff their edge sets against kg_extract_java's (expect them to win on resolution — they do type analysis).
- Add `extends`/`implements` queries to the MCP server (`graph_api`-style) — the data is already in graph.json.
- Extend gen_java_repo.py with a `--noise` flag (dead code, comments mentioning symbols) and measure how the baseline arm degrades while the graph arm doesn't.
