# M06 Lab — OKF Authoring

**What you'll build**: two valid OKF concept files for orderflow (the WAU metric and the orders_fact table) plus a frontmatter validator.
**Time**: 25–35 min · **Prerequisites**: M01 lab; `pip install python-frontmatter`.

## Step 1: Study the shape
Open `starter/knowledge/analytics/metrics/weekly_active_users.md`. The YAML frontmatter is stubbed. Remember the spec: exactly ONE field is required — `type`. Everything else (title, description, resource, tags, timestamp) is recommended, optional.

## Step 2: Complete the two concepts (TODO 1, TODO 2)
Fill the frontmatter and body:
- WAU: computation rule (7-day rolling window, completed orders, EXCLUDES internal testers), `resource:` pointing at `services/orders/metrics.py`, cross-link to `[orders_fact](../tables/orders_fact.md)`.
- orders_fact: schema table (order_id, customer_id, total_cents, completed_at), a Joins section, cross-link back to the metric.

## Step 3: Write the validator (TODO 3)
Complete `starter/validate.py`: for every `.md` under `knowledge/` (skip `index.md`), load with `python-frontmatter`; fail with a clear message if `type` is missing; warn (not fail) on missing recommended fields — leniency is the spec, but your own lint can be stricter.

## Step 4: Verify

```bash
cd labs/M06-okf-authoring/starter
python validate.py knowledge
```

Expected: `2 concepts valid, 0 errors` (see `expected_output/`).
Break it on purpose: delete `type:` from one file and re-run — you should get a non-zero exit and a file path in the error.

## Troubleshooting
- `ScannerError` from YAML → check your frontmatter delimiters are exactly `---` on their own lines.
- Validator passes an empty file → `frontmatter.load` on a file with no frontmatter returns empty metadata; that's why you must explicitly check `'type' in post.metadata`.
