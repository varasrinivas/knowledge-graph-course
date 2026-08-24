# M02 Lab — Watch RAG Shred Context

**What you'll build**: a deliberately naive keyword-RAG over orderflow's docs that retrieves the WRONG (stale) WAU definition — then the one-file deterministic lookup that gets it right.
**Time**: 25–35 min · **Prerequisites**: M01 lab.

`docs/architecture.md` contains a deliberately preserved stale paragraph defining WAU as "any API call in 7 days, no tester exclusion." The canonical definition lives in `services/orders/metrics.py`. This lab makes the retrieval failure happen on your machine.

## Step 1: Chunk the docs
Write `chunker.py`: split every file under `sample-project/docs/` into ~400-character chunks on paragraph boundaries; keep `{text, source, chunk_index}`. (No embeddings needed — keyword scoring shows the same failure mode without an API key.)

## Step 2: Retrieve
Write `retrieve.py`: score chunks by query-term overlap for the query *"how is weekly active users calculated?"* and print the top 3. You will get the stale architecture.md paragraph among them — it is keyword-dense and semantically close. Nothing crashed; the pipeline "worked."

## Step 3: The deterministic alternative
Read `M06`'s solution concept `weekly_active_users.md` with `python-frontmatter` and print its Computation Rules section. Same question, one exact file, zero ambiguity.

## Step 4: Reflect (answer in comments)
1. Would a better embedding model fix Step 2? (No — the stale text is legitimately similar; the problem is that similarity is the wrong criterion for canonical facts.)
2. What operational process would have prevented the stale paragraph? (M08's enrichment hook + log.md.)

✅ Done when your retrieval demonstrably surfaces the stale definition and your OKF lookup returns the canonical one.
