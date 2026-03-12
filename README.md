# AgentBrush

[![PyPI version](https://img.shields.io/pypi/v/agentbrush.svg)](https://pypi.org/project/agentbrush/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agent--skills-compatible-purple.svg)](https://agentskills.io)
[![Tests](https://img.shields.io/badge/tests-134%20passed-brightgreen.svg)](#testing)

Image editing toolkit for AI agents. Background removal, compositing, text rendering, resizing, format conversion, and spec validation.

## Install

```bash
pip install agentbrush
```

With AI image generation support:

```bash
pip install agentbrush[generate]
```

## Quick Start

### Python API

```python
from agentbrush import remove_background, resize_image, validate_design

# Remove background (edge-based flood fill, safe for artwork)
result = remove_background("photo.png", "cutout.png", color="white")

# Resize for social media
result = resize_image("cutout.png", "og_image.png", width=1200, height=630, pad=True)

# Validate against a preset
result = validate_design("og_image.png", preset="social-og")
print(result.summary())
```

Every function returns a `Result` object:

```python
result.success         # True if no errors
result.width           # Output width in px
result.height          # Output height in px
result.transparent_pct # Percentage of transparent pixels
result.warnings        # Non-fatal issues
result.errors          # Fatal issues
result.metadata        # Operation-specific data
result.summary()       # Human-readable string
```

### CLI

```bash
# Background removal
agentbrush remove-bg input.png output.png --color black --threshold 25 --smooth

# Green screen removal
agentbrush greenscreen input.png output.png --upscale 3 --halo-passes 20

# Border artifact cleanup
agentbrush border-cleanup input.png output.png --passes 15 --green-halo-passes 20

# Text rendering
agentbrush text input.png output.png "HELLO" --font mono --bold --size 72
agentbrush text new:1200x630 output.png "Title Text" --bold --center

# Compositing
agentbrush composite base.png art.png output.png --position 100,200
agentbrush composite paste-centered output.png --overlay art.png --canvas 1200x630 --fit

# Resize
agentbrush resize input.png output.png --width 1200 --height 630
agentbrush resize input.png output.png --scale 3.0
agentbrush resize input.png output.png --width 1080 --height 1080 --fit --pad

# Validate against presets
agentbrush validate check image.png --preset social-og
agentbrush validate check image.png --preset favicon
agentbrush validate check image.png --width 800 --height 600 --transparent
agentbrush validate compare source.png processed.png --max-loss 10

# Format conversion
agentbrush convert input.png output.jpg --quality 95
agentbrush convert input.png output.webp --quality 90

# AI image generation (requires openai package)
agentbrush generate --provider openai --prompt "cat coding" --output cat.png
```

Exit codes: `0` = success, `1` = validation failure, `2` = input error.

## Examples

### Background Removal

Edge-based flood fill removes the background while preserving internal dark details that threshold-based tools destroy.

![Background removal: black bg to transparent](docs/images/compare_01_removebg.png)

```bash
agentbrush remove-bg input.png output.png --color black --threshold 25 --smooth
```

### Green Screen Removal

Multi-pass pipeline: flood fill from edges, trapped patch sweep, upscale with halo cleanup.

![Green screen removal](docs/images/compare_02_greenscreen.png)

```bash
agentbrush greenscreen input.png output.png --upscale 3 --halo-passes 20
```

### Border Cleanup

Iterative erosion removes white "sticker border" artifacts and green halos left by AI image generators.

![Border artifact cleanup](docs/images/compare_03_border.png)

```bash
agentbrush border-cleanup input.png output.png --passes 15 --green-halo-passes 20
```

### Text Rendering

Accurate Pillow-based text rendering on new or existing canvases — no AI text mangling.

![Text rendering on canvas](docs/images/compare_04_text.png)

```bash
agentbrush text new:1200x630 output.png "HELLO WORLD" --font mono --bold --size 72 --center
```

### Compositing

Layer images with automatic centering, fit-to-canvas, and alpha blending.

![Image compositing](docs/images/compare_05_composite.png)

```bash
agentbrush composite paste-centered output.png --overlay art.png --canvas 800x400 --fit
```

### Resize & Pad

Resize to exact dimensions with letterbox padding to preserve aspect ratio.

![Resize with padding](docs/images/compare_06_resize.png)

```bash
agentbrush resize input.png output.png --width 1200 --height 630 --fit --pad
```

## Agent Skills

AgentBrush ships as an [Agent Skills](https://agentskills.io) package. Copy `skill/agent-brush/` into your project's `.claude/skills/` directory:

```bash
cp -r skill/agent-brush/ .claude/skills/agent-brush/
```

Claude Code (and other compatible tools) will automatically discover the skill and use it when processing images.

## Usage Without Install

The standalone scripts work directly from a git clone — no `pip install` needed:

```bash
git clone https://github.com/ultrathink-art/agentbrush.git
cd agentbrush

python skill/agent-brush/scripts/remove_bg.py input.png output.png --color black
python skill/agent-brush/scripts/validate.py check image.png --preset social-og
python skill/agent-brush/scripts/resize.py input.png output.png --width 1200 --height 630
```

Requirements: **Python >= 3.10** and **Pillow >= 12.1** (`pip install 'Pillow>=12.1'`).

## Modules

| Module | Description | Key function |
|--------|-------------|-------------|
| `background` | Edge-based flood fill bg removal | `remove_background()` |
| `greenscreen` | Multi-pass green screen pipeline | `remove_greenscreen()` |
| `border` | Border artifact erosion + halo cleanup | `cleanup_border()` |
| `text` | Pillow text rendering (accurate) | `add_text()`, `render_text()` |
| `composite` | Image layering + centering | `composite()`, `paste_centered()` |
| `resize` | Resize with fit/pad/scale modes | `resize_image()` |
| `validate` | Spec validation against presets | `validate_design()`, `compare_images()` |
| `convert` | Format conversion (PNG/JPEG/WEBP) | `convert_image()` |
| `generate` | AI image generation (optional) | `generate_image()` |

## Core Primitives

Low-level functions available for custom pipelines:

```python
from agentbrush.core import (
    flood_fill_from_edges,   # BFS flood fill (4-conn or 8-conn)
    is_near_color,           # Color distance matching
    parse_color,             # Parse "black", "white", "R,G,B" strings
    smooth_edges,            # 1px edge feathering
    smooth_alpha_edges,      # Gaussian alpha blur (edges only)
    find_artwork_bounds,     # Opaque pixel bounding box
    crop_to_content,         # Crop to content with padding
    find_opaque_centroid,    # Center of mass for opaque region
    ensure_single_shape,     # Remove floating elements (8-connected BFS)
    count_components,        # Connected component count
    find_font,               # Cross-platform font discovery
)
```

## Presets

### General Purpose

| Preset | Width | Height | Transparent | Use Case |
|--------|-------|--------|-------------|----------|
| `social-og` | 1200 | 630 | No | Open Graph / link previews |
| `social-square` | 1080 | 1080 | No | Instagram, social posts |
| `social-story` | 1080 | 1920 | No | Stories, reels, vertical |
| `favicon` | 32 | 32 | Yes | Browser favicon |
| `icon-ios` | 1024 | 1024 | No | iOS app icon |
| `icon-android` | 512 | 512 | Yes | Android app icon |
| `thumbnail` | 400 | 400 | - | Thumbnails, previews |
| `banner` | 1920 | 480 | - | Website/profile banners |
| `avatar` | 256 | 256 | No | Profile avatars |

### Print-on-Demand

POD presets are also available via `--preset` or `--type` (backward compat):

| Preset | Width | Height | Transparent | Notes |
|--------|-------|--------|-------------|-------|
| `tshirt` | 4500 | 5400 | Required | Apparel |
| `hoodie` | 4500 | 5400 | Required | Apparel |
| `hat` | 1890 | 765 | Required | Wide horizontal |
| `mug` | 2700 | 1050 | Recommended | Wrap-around |
| `sticker` | 1664 | 1664 | Required | Die-cut, single shape |
| `deskmat` | 9200 | 4500 | No | Large format |
| `poster` | 5400 | 7200 | No | Portrait |
| `tote` | 3900 | 4800 | Required | Apparel |

For detailed POD specs, see [docs/presets/pod.md](docs/presets/pod.md).

## Why Edge-Based Flood Fill?

Threshold-based removal (`magick -fuzz -transparent black`) scans every pixel and removes anything "close enough" to the target color — including internal outlines, dark shadows, and fine details inside the artwork.

AgentBrush starts flood fill from image edges only. Interior pixels that happen to match the background color are never touched because flood fill can't reach them without crossing through the artwork.

```
Threshold-based:              Edge-based flood fill:
removes ALL dark pixels       removes ONLY edge-connected dark pixels
+-----------------+           +-----------------+
|                 |           |                 |
|    #########    |           |    #########    |
|   #         #   | <- loses  |   #*********#   | <- preserved!
|   #         #   |   detail  |   #*********#   |
|    #########    |           |    #########    |
|                 |           |                 |
+-----------------+           +-----------------+
```

## Guides

Step-by-step pipeline walkthroughs:

- [Social Media Images](docs/examples/social_media_images.md) — OG images, thumbnails, avatars
- [Background Removal](docs/examples/background_removal.md) — black bg, white bg, green screen techniques
- [POD Workflows](docs/examples/pod_workflows.md) — stickers, t-shirts, mugs, and other products

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

All tests use synthetic Pillow-generated fixtures (no production images).

## Dependencies

- **Required**: `Pillow >= 12.1`
- **Optional**: `openai >= 1.0` (for `generate` command)
- **Dev**: `pytest >= 7.0`, `pytest-cov`

## License

MIT
