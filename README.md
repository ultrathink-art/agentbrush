# AgentBrush

Image editing toolkit for AI agents. Photoshop for Claude Code, Codex, Cursor, and friends.

## Install

```bash
pip install agentbrush
```

## Quick Start

```python
from agentbrush import remove_background, remove_greenscreen, cleanup_border

# Remove black background (edge-based flood fill, safe for artwork)
result = remove_background("input.png", "output.png", color="black", threshold=25)
print(result.summary())

# Remove green screen (multi-pass: flood fill + color sweep)
result = remove_greenscreen("input.png", "output.png")

# Clean up white sticker border
result = cleanup_border("input.png", "output.png", passes=15, threshold=185)
```

## CLI

```bash
agentbrush remove-bg input.png output.png --color black --threshold 25 --smooth
agentbrush greenscreen input.png output.png --upscale 3
agentbrush border-cleanup input.png output.png --passes 15 --green-halo-passes 20
```

## Core Primitives

```python
from agentbrush.core import (
    flood_fill_from_edges,   # BFS flood fill (4-conn or 8-conn)
    is_near_color,           # Color matching
    smooth_edges,            # Edge feathering
    smooth_alpha_edges,      # Gaussian alpha smoothing
    find_artwork_bounds,     # Opaque pixel bounding box
    crop_to_content,         # Crop to content with padding
    ensure_single_shape,     # Die-cut single shape (8-connected BFS)
    count_components,        # Connected component analysis
    find_font,               # Cross-platform font discovery
)
```

## Why Edge-Based Flood Fill?

Threshold-based removal (`magick -fuzz -transparent black`) destroys internal outlines and details. AgentBrush starts flood fill from image edges only, preserving artwork interior.

## License

MIT
