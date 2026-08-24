# Module HTML Template & Animation Catalog

## HTML Structure

Every module MUST contain these sections in this order:

### 1. COURSE HEADER
- Course title, track name (with track color), module number and title
- Progress indicator showing position (e.g., "Module 6 of 14")
- Estimated completion time
- Prerequisites (which modules must be completed first)

### 2. LEARNING OBJECTIVES
- 3-5 specific, measurable objectives
- Skill level indicator (Beginner / Intermediate / Advanced)

### 3. CONCEPT EXPLAINERS (for each concept in the module)
- **"Everyday Analogy" box** — real-world metaphor, unpacked per depth rule 1 (BEFORE → PAIN → MAPPING)
- **"Technical Definition" box** — precise explanation, every sub-term defined
- **ANIMATED VISUAL** — CSS/JS animation with play/pause/restart controls and annotations
- **"Why It Matters" callout** — with concrete numbers
- **"Common Misconceptions" callout** — for each major new concept

### 4. CODE WALKTHROUGHS
- Code annotated in 3-5 chunks (WHAT/WHY/GOTCHA), conversational teacher voice
- Python AND Node.js tabs where API code applies; single blocks for CLI/YAML/Markdown
- Copy button on all code blocks
- "What Just Happened?" checkpoint after complete code blocks

### 5. HANDS-ON EXERCISE
- Follows depth rule 13: numbered steps, each with What & Why, complete code, run command, expected output, ✅ checkpoint, troubleshooting
- References the matching `labs/` folder

### 6. KNOWLEDGE CHECK
- 5+ interactive quiz questions with immediate feedback and explanations for wrong answers

### 7. MODULE SUMMARY
- Key concepts recap (visual cheat sheet)
- "What we built" on the orderflow running example
- "Next module preview"

### 8. REFERENCE SIDEBAR
- Links to the tools' repos/specs (Graphify, OKF spec, CodeGraph, okf-rs, okf CLI)
- Source articles from the research corpus

## Animation Catalog (Knowledge Graph course)

Each animation MUST have play ▶ / pause ⏸ / restart ↻ controls and a `prefers-reduced-motion` static fallback. CSS + vanilla JS only; `requestAnimationFrame`; `transform`/`opacity` for GPU acceleration.

| Pattern | Description | Use In |
|---|---|---|
| `LOST_AGENT` | Agent icon opens file after file, token meter climbs into red; contrast path with map | M00 |
| `THREE_LAYERS` | Three context sources (structural/narrative/semantic) feeding one agent | M00, M10 |
| `TIMELINE` | Horizontal event timeline animating left to right | M00, M12 |
| `GRAPH_BUILD` | Files morph into nodes; typed edges draw in with labels | M01, M03 |
| `TRAVERSAL` | Query walks edges hop by hop; token counter stays flat | M01, M09 |
| `COMMUNITY_DETECT` | Nodes cluster into colored communities; god node pulses | M01, M04 |
| `SHREDDER` | Structured doc passes through chunker; table rows and links sever | M02 |
| `COSINE_ROULETTE` | Query pulls 3 chunks of varying quality; different every run | M02 |
| `AST_GROW` | Source text morphs into a labeled parse tree | M03 |
| `PIPELINE_FLOW` | Left-to-right staged transformation with a diff-scope filter | M04, M08 |
| `BENCHMARK_BARS` | Animated bars comparing vendor claim vs replicated range | M04, M05 |
| `SYNC_LAYERS` | File save → OS watcher → debounce batch → single sync; staleness flag path | M05 |
| `BUNDLE_TREE` | Directory tree draws in; index.md pulses as entry point | M06 |
| `FRONTMATTER_ANATOMY` | Concept file dissects: YAML lifts and labels, links glow into edges | M06 |
| `PROGRESSIVE_DISCLOSURE` | Agent walks index → branch → concept; token meter barely moves | M06, M09 |
| `LINK_GRAPH` | Concept files connect by links into a graph overlaying the folder tree | M07 |
| `TWO_PASS` | Pass 1 drafts a concept; pass 2 draws citation threads | M08 |
| `MCP_HANDSHAKE` | Client ↔ server protocol frames with highlighted message types | M09 |
| `TOKEN_SCALE` | 24KB file vs one-line answer on a balance scale | M09 |
| `STAGED_PIPELINE` | One query descends OKF → graph → vector stages with token meter | M10 |
| `DECISION_TREE` | Symptom branches light up toward a tool trigger | M10 |
| `DRIFT_TIMELINE` | Commits accumulate; graph timestamp freezes; divergence gap widens | M11 |
| `SILENT_FAILURES` | Four failure doors, each ending in a green light over a red state | M11 |
| `FRESHNESS_GATE` | CI compares timestamps; stale → pipeline blocks with alarm | M11, CAPSTONE |
| `CONTEXT_BUDGET` | Stacked bar of what fills 200K tokens; layered setup shrinks bands | M12 |
