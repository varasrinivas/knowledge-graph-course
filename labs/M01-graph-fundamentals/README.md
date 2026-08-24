# M01 Lab — Graph Fundamentals in Pure Python

**What you'll build**: an adjacency-list code graph of orderflow, a BFS "who calls X?" query, and a transitive blast-radius calculator — no libraries.
**Time**: 30–45 min · **Prerequisites**: labs/SETUP.md done.

## Step 1: Load the graph
`starter/graph_basics.py` ships with a loader that runs the course extractor and returns `nodes` and `edges`. Run it:

```bash
cd labs/M01-graph-fundamentals/starter
python graph_basics.py
```

Expected: `36 nodes, 22 edges loaded`.
✅ Checkpoint: if you see an import error, run from inside `starter/` so the relative paths resolve.

## Step 2: Build the reverse adjacency list (TODO 1)
Direct callers of a symbol are one dict away IF you index edges by target. Fill in `build_reverse_index` so `callers("decode_jwt")` returns `["verify_token"]`.

## Step 3: BFS blast radius (TODO 2)
Fill in `blast_radius` — walk the reverse index transitively from a target; the result is every function whose behavior could change if the target changes. `blast_radius("decode_jwt")` must include `verify_token` AND `post_invoice` (two hops).

## Step 4: Respect provenance (TODO 3)
Add the `min_confidence` filter: when `"EXTRACTED"` is required, INFERRED edges are skipped. Compare blast radii with and without — this is the honesty distinction every serious tool ships.

## Verify

```bash
python graph_basics.py --check
```

Expected final output: see `expected_output/sample_output.txt`. 🎉 If `ALL CHECKS PASSED` prints, you're done.

## Troubleshooting
- `KeyError: 'edges'` → you edited the loader; restore it or diff against solution/.
- Empty blast radius → your BFS probably follows edges forward (caller→callee). You need callee→caller.
