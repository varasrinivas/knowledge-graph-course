# /build-index — Regenerate the course landing page

Regenerate `output/index.html` from the modules currently present in `output/`.

## Steps
1. List `output/M*.html` and `output/CAPSTONE-*.html`.
2. Read `prompts/02-visual-design-system.md` for colors/typography and `prompts/00-course-philosophy.md` for the course map.
3. Generate `output/index.html`: course hero, track sections in order (Track 0 → Track 5 → Capstone) with track signature colors, one card per module (number, title, est. time, 1-line description, link), and a "start here → M00" call to action. Mark any module missing from `output/` as "coming soon" (card present, link disabled).
4. Self-contained: all CSS inline, Google Fonts only external import, responsive at 768px and 1440px.
