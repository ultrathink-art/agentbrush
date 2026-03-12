---
name: agent-brush
description: Image editing toolkit for AI agents. Use when processing, editing, or validating images. Background removal, compositing, text overlays, resizing, format conversion, and spec validation against presets (social media, icons, thumbnails, print-on-demand).
allowed-tools: Bash(python *), Bash(agentbrush *), Read, Glob
---

# AgentBrush — Image Editing for AI Agents

Image processing toolkit with background removal, green screen processing, border cleanup, text rendering, compositing, resizing, validation, and format conversion.

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

# With upscale + halo cleanup
agentbrush greenscreen input.png output.png --upscale 3 --halo-passes 20
```

### Border Cleanup (edge artifact removal)

```bash
# Remove white border artifacts from AI-generated images
agentbrush border-cleanup input.png output.png --passes 15 --threshold 185

# Full cleanup: white border + green halo + alpha smoothing
agentbrush border-cleanup input.png output.png --passes 15 --green-halo-passes 20 --alpha-smooth
```

### Text Rendering (Pillow-based, accurate)

```bash
# Add text to existing image
agentbrush text input.png output.png "HELLO WORLD" --font mono --bold --size 72 --color "255,255,255,255"

# Render text on new canvas (use new:WxH as input)
agentbrush text new:1200x630 output.png "Title Text" --font mono --bold --size 80 --center
```

### Compositing

```bash
# Overlay image onto base
agentbrush composite base.png overlay.png output.png --position 100,200

# Center artwork on canvas
agentbrush composite paste-centered output.png --overlay artwork.png --canvas 1200x630 --fit
```

### Resize

```bash
# Resize to exact dimensions
agentbrush resize input.png output.png --width 1200 --height 630

# Scale by factor
agentbrush resize input.png output.png --scale 3.0

# Fit within bounds preserving aspect ratio
agentbrush resize input.png output.png --width 1080 --height 1080 --fit

# Fit and pad to exact dimensions
agentbrush resize input.png output.png --width 1200 --height 630 --pad
```

### Validation (preset-based)

```bash
# Validate against built-in presets
agentbrush validate check image.png --preset social-og
agentbrush validate check image.png --preset favicon
agentbrush validate check image.png --preset icon-ios

# Validate with custom spec
agentbrush validate check image.png --width 800 --height 600 --transparent

# POD presets (backward compat via --type)
agentbrush validate check design.png --preset tshirt
agentbrush validate check design.png --type sticker

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

## Available Presets

| Preset | Width | Height | Use Case |
|--------|-------|--------|----------|
| `social-og` | 1200 | 630 | Open Graph / link previews |
| `social-square` | 1080 | 1080 | Instagram, social posts |
| `social-story` | 1080 | 1920 | Stories, reels, vertical |
| `favicon` | 32 | 32 | Browser favicon |
| `icon-ios` | 1024 | 1024 | iOS app icon |
| `icon-android` | 512 | 512 | Android app icon |
| `thumbnail` | 400 | 400 | Thumbnails, previews |
| `banner` | 1920 | 480 | Website/profile banners |
| `avatar` | 256 | 256 | Profile avatars |
| `tshirt` | 4500 | 5400 | T-shirt print area |
| `hoodie` | 4500 | 5400 | Hoodie print area |
| `mug` | 2700 | 1050 | Mug wrap area |
| `sticker` | 1664 | 1664 | Die-cut sticker |
| `poster` | 5400 | 7200 | Poster print area |

## Best Practices

1. **NEVER use threshold-based background removal** — destroys internal outlines/details. Always use edge-based flood fill (`remove-bg`).
2. **Use Pillow for text, not AI generation** — AI mangles long text. Use `agentbrush text` for accurate rendering.
3. **Green screen technique**: prompt AI for "#00FF00 background", then use `agentbrush greenscreen` for clean removal.
4. **Validate before delivery** — use `agentbrush validate check` with the appropriate preset to catch dimension/format issues early.
5. **Compare after bg removal** — `agentbrush validate compare` catches artwork damage from processing.

## Additional Resources

- For POD product specs, see [references/product-specs.md](references/product-specs.md)
- For common issues and fixes, see [references/troubleshooting.md](references/troubleshooting.md)

## Standalone Scripts

The `scripts/` directory contains standalone wrappers for each command. These work without `pip install` — they auto-detect the `src/` directory:

```bash
python scripts/remove_bg.py input.png output.png --color black
python scripts/validate.py check image.png --preset social-og
```
