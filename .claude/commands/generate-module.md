# /generate-module — Generate a complete module HTML file

Generate the module named in `$ARGUMENTS` (e.g., `M06`) as one self-contained HTML file in `output/`.

## Steps
1. Read, in order: `prompts/00-course-philosophy.md`, `prompts/01-module-template.md`, `prompts/02-visual-design-system.md`, `prompts/05-module-content-reference.md` (the section for this module), `prompts/07-depth-rules.md`, and `CLAUDE.md`.
2. Confirm the module's track, track color, position (M00–M12 + CAPSTONE = 14 parts), prerequisites, and previous/next modules.
3. Generate `output/M{XX}-{slug}.html` following the template section order exactly. All CSS/JS inline; Google Fonts only external import.
4. Cover EVERY concept and concrete fact listed for this module in `prompts/05-module-content-reference.md` — including the honest benchmark ranges where flagged.
5. Include at least 3 animations from the catalog with play/pause/restart controls and `prefers-reduced-motion` fallbacks.
6. Include a 5+ question quiz with immediate feedback.
7. Run the Quality Checklist from `CLAUDE.md` against the output; fix any failures before finishing.
