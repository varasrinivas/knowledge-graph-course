# /review-module — Review a module against quality standards

Review the module named in `$ARGUMENTS` (e.g., `M06`) against the course standards.

## Steps
1. Read `CLAUDE.md` (Quality Checklist), `prompts/07-depth-rules.md`, and `prompts/05-module-content-reference.md` (this module's section).
2. Read the module HTML from `output/`.
3. Report, in a table: each checklist item pass/fail; each depth rule pass/fail with one example; any content-reference concept that is missing or taught inaccurately; any benchmark number quoted without its replicated range (Honesty Rule violations).
4. If asked to fix, apply fixes directly to the HTML, then re-run the checklist.
