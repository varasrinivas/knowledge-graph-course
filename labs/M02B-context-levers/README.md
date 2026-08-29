# M02B Lab: Context Levers — Fix the Poisoned Transcript the Other Two Ways

> The sibling course's M03B lab fixed a rotted transcript by **compressing** it. This lab fixes the same disease with the two levers that lab left unimplemented — **retrieve** (one graph answer) and **offload** (one concept read) — using the machinery this course builds.

## Prerequisites
- M01 lab (the reverse-index BFS — you'll reuse the walk)
- M06 lab solution present (the canonical WAU concept file)
- M09 lab solution present (`server.py` — its `explore()` is imported directly)
- `pip install python-frontmatter` (already in labs/requirements.txt)
- Recommended first: the sibling course's `labs-opensource/M03B-context-engineering` lab, so you've seen the compress lever

## The Lab in One Sentence
Load a poisoned orderflow transcript (duplicate grep dumps, a stale WAU definition, resolved detours), fix it four ways — compress / retrieve / offload / both — and verify each lever preserves the key facts it owns while spending materially fewer tokens.

## Files
| File | Status | What It Is |
|---|---|---|
| `starter/poisoned_transcript.json` | Complete | ~17-turn rotted session over orderflow: two timed-out grep retries, the same grep dump attached twice, a stale WAU paragraph retrieved twice, a resolved expiry detour |
| `starter/context_levers.py` | **TODOs** | `ContextBudget` with `account()`, `render()`, `raw()` and `fix_by_compress()` complete; you implement the two new levers + the combination |
| `solution/context_levers.py` | Complete | Peek if stuck |
| `expected_output/sample_output.txt` | Complete | The table a correct run prints |

## What You Implement
1. `fix_by_retrieve()` — replace ALL tool results with ONE `graph.explore('decode_jwt')` answer, extended with named `transitive_callers` (BFS over the reverse index — the M01 walk, three lines).
2. `fix_by_offload()` — replace both stale retrieved chunks with ONE read of the canonical `weekly_active_users.md` concept, and drop the now-settled WAU debate from history.
3. `fix_combined()` — offload first, then retrieve.

Provided complete: token counting (chars/4), the six-layer `account()`, the naive-extractive `fix_by_compress()` (the sibling lab's lever), the fact checker.

## Run It
```bash
cd labs/M02B-context-levers/solution   # or starter, once your TODOs are done
python context_levers.py --check
```
**Expected shape of the output** (exact table in `expected_output/sample_output.txt`):
```
arm                  tokens   vs raw  facts preserved
raw                   3,034    100%  ALL
compress              1,454     48%  ALL
retrieve                952     31%  ALL
offload               2,802     92%  ALL
retrieve+offload        721     24%  ALL
SUCCESS CRITERION MET
```

**The success criterion:** each lever must preserve the facts it owns — retrieve owns the caller facts (`verify_token`, `post_invoice`), offload owns the WAU facts (7-day window, completed orders, internal-tester exclusion) — at fewer tokens than raw. If `retrieve` loses the transitive caller, your BFS follows edges forward instead of backward. If `offload` loses a WAU fact, your history filter dropped the concept text too.

Note what the table teaches: `raw` also "preserves ALL facts" — buried in 3,034 tokens of noise. Context rot is a **signal-to-noise problem, not a budget problem** (M03B's exact words); the levers don't add facts, they remove everything else.

## Stretch Goals
- Wire the sibling lab's `strategy()` bands to auto-pick a lever: `< 0.60 → ok`, `< 0.75 → compress`, `< 0.90 → retrieve`, else `retrieve+offload`.
- Add a 7th `scratchpad` layer to `account()` and poison it with a stale plan.
- Live comparison: ask a model the transcript's final question with the raw vs the combined context and compare answer quality and reported token usage (needs an API key).
