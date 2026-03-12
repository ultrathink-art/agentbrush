---
name: agent-brush
description: Image editing toolkit for AI agents. Use when processing images for print-on-demand products (stickers, t-shirts, mugs, hoodies, posters), removing backgrounds, adding text overlays, compositing layers, or validating designs against product specs.
allowed-tools: Bash(python *), Bash(agentbrush *), Read, Glob
---

# AgentBrush — Image Editing for AI Agents

Production-tested image processing toolkit. Handles background removal, green screen processing, border cleanup, text rendering, compositing, resizing, validation, and format conversion.

## Quick Reference

All commands follow: `agentbrush <command> <input> <output> [options]`

### Background Removal (edge-based flood fill — NEVER threshold-based)

```bash
# Remove black background
agentbrush remove-bg input.png output.png --color black --threshold 25

# Remove white background with edge smoothing
agentbrush remove-bg input.png output.png --color white --smooth

# Remove custom color background
agentbrush remove-bg input.png output.png --color "24,242,41" --threshold 40
```

### Green Screen Removal (multi-pass pipeline)

```bash
# Standard green screen removal
agentbrush greenscreen input.png output.png

# With upscale + halo cleanup (for print-quality output)
agentbrush greenscreen input.png output.png --upscale 3 --halo-passes 20
```

### Border Cleanup (sticker post-processing)

```bash
# Remove white AI sticker border
agentbrush border-cleanup input.png output.png --passes 15 --threshold 185

# Full cleanup: white border + green halo + alpha smoothing
agentbrush border-cleanup input.png output.png --passes 15 --green-halo-passes 20 --alpha-smooth
```

### Text Rendering (Pillow-based, accurate)

```bash
# Add text to existing image
agentbrush text input.png output.png "HELLO WORLD" --font mono --bold --size 72 --color "255,255,255,255"

# Render text on new canvas (use new:WxH as input)
agentbrush text new:1664x1664 output.png "BUG\nFEATURE" --font mono --bold --size 120 --center
```

### Compositing

```bash
# Overlay image onto base
agentbrush composite base.png overlay.png output.png --position 100,200

# Center artwork on product canvas
agentbrush composite paste-centered output.png --overlay artwork.png --canvas 4500x5400 --fit
```

### Resize (with product presets)

```bash
# Resize for specific product
agentbrush resize input.png output.png --width 4500 --height 5400

# Scale by factor
agentbrush resize input.png output.png --scale 3.0

# Fit within bounds preserving aspect ratio
agentbrush resize input.png output.png --width 2700 --height 1050 --fit

# Fit and pad to exact dimensions
agentbrush resize input.png output.png --width 2700 --height 1050 --pad
```

### Validation (design QA)

```bash
# Validate against product specs
agentbrush validate check design.png --type sticker
agentbrush validate check design.png --type tshirt

# Compare source vs processed (verify bg removal didn't damage artwork)
agentbrush validate compare source.png processed.png --max-loss 10
```

### Format Conversion

```bash
agentbrush convert input.png output.jpg
agentbrush convert input.png output.webp --quality 90
```

### AI Image Generation (requires OpenAI key)

```bash
agentbrush generate --provider openai --prompt "cute cat coding" --output cat.png
agentbrush generate --provider pollinations --prompt "robot painting" --output robot.png
```

## Python API

```python
from agentbrush import (
    remove_background,
    remove_greenscreen,
    cleanup_border,
    add_text, render_text,
    composite, paste_centered,
    resize_image,
    validate_design, compare_images,
    convert_image,
)

# All functions return a Result object
result = remove_background("in.png", "out.png", color="black")
print(result.success)     # True/False
print(result.summary())   # Human-readable output
print(result.width)       # Output dimensions
print(result.transparent_pct)  # Transparency percentage
```

## Product Dimensions Reference

| Product       | Width  | Height | Transparent | Notes                     |
|---------------|--------|--------|-------------|---------------------------|
| T-shirt       | 4500   | 5400   | Yes         | Apparel — no solid bg     |
| Hoodie        | 4500   | 5400   | Yes         | Apparel — no solid bg     |
| Hat           | 1890   | 765    | Yes         | Wide horizontal format    |
| Mug (11oz)    | 2700   | 1050   | Yes         | Wrap-around print area    |
| Mug (15oz)    | 2700   | 1140   | Yes         | Taller wrap area          |
| Sticker       | 1664   | 1664   | Yes         | Square, die-cut shape     |
| Desk mat      | 9200   | 4500   | No          | Large format              |
| Poster        | 5400   | 7200   | No          | Portrait orientation      |
| Sticker sheet | 825    | 525    | Yes         | 6x4" multi-sticker layout |

## Critical Rules

1. **NEVER use threshold-based background removal** — destroys internal outlines/details. Always use edge-based flood fill (`remove-bg`).
2. **Stickers must be a single continuous shape** — no floating/detached elements. Use `validate check --type sticker` to verify.
3. **Apparel designs MUST have transparent backgrounds** — validate with `validate check --type tshirt`.
4. **Use Pillow for text, not AI generation** — AI mangles long text. Use `agentbrush text` for accurate rendering.
5. **Green screen technique**: prompt AI for "#00FF00 background", then use `agentbrush greenscreen` for clean removal.

## Additional Resources

- For complete product specs and print guidelines, see [references/product-specs.md](references/product-specs.md)
- For common issues and fixes, see [references/troubleshooting.md](references/troubleshooting.md)

## Standalone Scripts

The `scripts/` directory contains standalone wrappers for each command. These work without `pip install` — they auto-detect the `src/` directory:

```bash
python scripts/remove_bg.py input.png output.png --color black
python scripts/validate.py check design.png --type sticker
```
