# M03 Lab — tree-sitter Extraction

**What you'll build**: a real tree-sitter parse of `shared/auth.py`, extracting function definitions and call edges with provenance tags — then compare against the stdlib-`ast` fallback (`shared_tools/kg_extract.py`).
**Time**: 45–60 min · **Prerequisites**: `pip install tree-sitter tree-sitter-python`.

## Step 1: Parse one file
```python
import tree_sitter_python
from tree_sitter import Language, Parser

parser = Parser(Language(tree_sitter_python.language()))
source = open("../sample-project/shared/auth.py", "rb").read()
tree = parser.parse(source)
print(tree.root_node)   # the AST, as an S-expression
```
✅ Checkpoint: you see a `(module ...)` S-expression with `function_definition` nodes.

## Step 2: Prove fault tolerance
On a COPY of the file, delete the closing parenthesis on the **`def verify_token(token: str | None) -> dict:` line** (line 41) and re-parse. tree-sitter still returns a tree; the damage is an `ERROR` island around `verify_token`, and `decode_jwt` **still extracts normally**. This is why real tools use it: development never happens in a permanently compilable state.

✅ Checkpoint: your function list drops from `['decode_jwt', 'verify_token']` to `['decode_jwt']` — one function lost, not the file.

⚠️ Which parenthesis you delete matters, and that is worth knowing. Break one *inside a function body* and the error is usually contained the same way. But delete the paren on line 9 (`SIGNING_KEY = os.environ.get(...)`) or on `def decode_jwt(...)` itself and recovery fails completely — the parse yields **no** functions at all. Error recovery is best-effort and local: it contains damage that stays inside a construct, and loses the file when the break is at module level or in the first definition's own signature. Tools like Graphify hit this too; it is a reason extraction is re-run per commit rather than trusted forever.

## Step 3: Extract defs and calls
Walk the tree: collect `function_definition` names, and inside each, `call` nodes. Resolve each call name against your collected defs:
- unique match in the same module → `EXTRACTED`
- unique match elsewhere → `INFERRED`
- multiple matches → `AMBIGUOUS` (emit all candidates)
- zero matches → external, skip

## Step 4: Compare with the fallback
Run `python ../shared_tools/kg_extract.py ../sample-project` and diff the edges for `shared.auth` against yours. They should agree on `verify_token → decode_jwt (EXTRACTED)`.

## Stretch
Time both parsers on 1,000 synthetic copies of auth.py. tree-sitter's incremental design is why Graphify/CodeGraph index tens of thousands of files in minutes.
