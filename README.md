# AgentBrush

[![PyPI version](https://img.shields.io/pypi/v/agentbrush.svg)](https://pypi.org/project/agentbrush/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agent--skills-compatible-purple.svg)](https://agentskills.io)
[![Tests](https://img.shields.io/badge/tests-126%20passed-brightgreen.svg)](#testing)

Image editing toolkit for AI agents. Photoshop for Claude Code, Codex, Cursor, and friends.

Built from 134 production sessions of print-on-demand image processing. Battle-tested algorithms for background removal, green screen processing, border cleanup, text rendering, compositing, validation, and more.

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
from agentbrush import remove_background, remove_greenscreen, cleanup_border

# Remove black background (edge-based flood fill, safe for artwork)
result = remove_background("input.png", "output.png", color="black", threshold=25)
print(result.summary())
# [OK] output.png
#   Size: 1024x1024px
#   Transparent: 72.3%  Opaque: 27.7%
#   pixels_removed: 758432

# Remove green screen (multi-pass: flood fill + color sweep)
result = remove_greenscreen("input.png", "output.png", halo_passes=20)

# Clean up white sticker border from AI-generated art
result = cleanup_border("input.png", "output.png", passes=15, threshold=185)
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

# Border cleanup
agentbrush border-cleanup input.png output.png --passes 15 --green-halo-passes 20

# Text rendering
agentbrush text add input.png output.png --text "HELLO" --font mono-bold --size 72
agentbrush text render output.png --width 1664 --height 1664 --text "BUG\nFEATURE" --center

# Compositing
agentbrush composite base.png art.png output.png --position 100,200
agentbrush composite paste-centered output.png --overlay art.png --canvas 4500x5400 --fit

# Resize
agentbrush resize input.png output.png --width 4500 --height 5400
agentbrush resize input.png output.png --scale 3.0
agentbrush resize input.png output.png --width 2700 --height 1050 --fit --pad

# Validate design against product specs
agentbrush validate check design.png --type sticker
agentbrush validate compare source.png processed.png --max-loss 10

# Format conversion
agentbrush convert input.png output.jpg --quality 95

# AI image generation (requires openai package)
agentbrush generate --provider openai --prompt "cat coding" --output cat.png
```

Exit codes: `0` = success, `1` = validation failure, `2` = input error.

## Agent Skills

AgentBrush ships as an [Agent Skills](https://agentskills.io) package. Copy `skill/agent-brush/` into your project's `.claude/skills/` directory:

```bash
cp -r skill/agent-brush/ .claude/skills/agent-brush/
```

Claude Code (and other compatible tools) will automatically discover the skill and use it when processing images. The skill includes:

- **SKILL.md** — instructions and quick reference for the agent
- **references/** — product specs, troubleshooting guides
- **scripts/** — standalone wrappers that work without `pip install`

## Usage Without Install

The standalone scripts work directly from a git clone — no `pip install` needed:

```bash
git clone https://github.com/ultrathink-art/agentbrush.git
cd agentbrush

# Run scripts directly (auto-detects src/ directory)
python skill/agent-brush/scripts/remove_bg.py input.png output.png --color black
python skill/agent-brush/scripts/validate.py check design.png --type sticker
python skill/agent-brush/scripts/greenscreen.py input.png output.png --upscale 3
```

Only requirement: `pip install Pillow` (if not already installed).

## Modules

| Module | Description | Key function |
|--------|-------------|-------------|
| `background` | Edge-based flood fill bg removal | `remove_background()` |
| `greenscreen` | Multi-pass green screen pipeline | `remove_greenscreen()` |
| `border` | White border erosion + green halo | `cleanup_border()` |
| `text` | Pillow text rendering (accurate) | `add_text()`, `render_text()` |
| `composite` | Image layering + centering | `composite()`, `paste_centered()` |
| `resize` | Resize with fit/pad/scale modes | `resize_image()` |
| `validate` | Design QA against product specs | `validate_design()`, `compare_images()` |
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

## Product Presets

Built-in dimensions for print-on-demand products:

| Product | Width | Height | Transparent | Notes |
|---------|-------|--------|-------------|-------|
| T-shirt | 4500 | 5400 | Required | Apparel |
| Hoodie | 4500 | 5400 | Required | Apparel |
| Hat | 1890 | 765 | Required | Wide horizontal |
| Mug (11oz) | 2700 | 1050 | Recommended | Wrap-around |
| Sticker | 1664 | 1664 | Required | Die-cut, single shape |
| Desk mat | 9200 | 4500 | No | Large format |
| Poster | 5400 | 7200 | No | Portrait |

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

## Examples

Full pipeline guides with code:

- [Sticker Pipeline](docs/examples/sticker_pipeline.md) — AI art -> green screen -> border cleanup -> validate die-cut
- [T-Shirt Pipeline](docs/examples/tshirt_pipeline.md) — artwork -> transparent bg -> resize to 4500x5400
- [Mug Pipeline](docs/examples/mug_pipeline.md) — sticker adaptation -> wrap format -> multi-sticker composition

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

All tests use synthetic Pillow-generated fixtures (no production images). 126 tests covering all modules.

## Dependencies

- **Required**: `Pillow >= 12.1`
- **Optional**: `openai >= 1.0` (for `generate` command)
- **Dev**: `pytest >= 7.0`, `pytest-cov`

## License

MIT
