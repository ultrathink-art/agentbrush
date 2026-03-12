## README Visual Examples

- **BG removal demos: subject MUST contrast strongly with background** — bright/colorful subject on black bg, or dark subject on white bg. Dark-on-dark (e.g. dark robot on black bg) causes flood fill to leak into the subject, destroying the illustration. Two commits made this mistake before the fix.
- Comparison images built with `/tmp/rebuild_readme_examples.py` pattern: Pillow checker-bg composites, side-by-side panels, labeled with `find_font()` Menlo fallback.
- Composite example (#4) reuses the bg-removal cutout — if #1 looks bad, #4 cascades.
