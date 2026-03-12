# Print-on-Demand Workflows

Consolidated pipeline guides for POD products. For full dimension specs, see [../presets/pod.md](../presets/pod.md).

## Sticker Pipeline

```
AI prompt → greenscreen → border cleanup → add text → validate → resize
```

```python
from agentbrush import (
    remove_greenscreen, cleanup_border, add_text,
    validate_design, resize_image,
)

# Remove green screen
result = remove_greenscreen("raw.png", "clean.png", halo_passes=20, upscale=3)
assert result.success

# Clean border artifacts
result = cleanup_border("clean.png", "trimmed.png", passes=15,
                        green_halo_passes=20, alpha_smooth=True)
assert result.success

# Validate (checks dimensions, single shape, poster-layout, complexity)
result = validate_design("trimmed.png", preset="sticker")
assert result.success, result.summary()

# Resize to target
result = resize_image("trimmed.png", "final.png", width=1664, height=1664, pad=True)
```

**Sticker rules:**
- Must be a single continuous shape (no floating elements)
- Rectangular background = automatic FAIL (>70% fill + >75% rect)
- Text must overlap/touch the illustration

## T-Shirt / Hoodie Pipeline

```
AI prompt → remove background → add text → resize 4500x5400 → validate
```

```python
from agentbrush import (
    remove_greenscreen, add_text, resize_image, validate_design,
)

# Remove background
result = remove_greenscreen("raw.png", "clean.png", halo_passes=15, upscale=3)
assert result.success

# Resize to print dimensions
result = resize_image("clean.png", "tshirt.png", width=4500, height=5400, pad=True)
assert result.success

# Validate
result = validate_design("tshirt.png", preset="tshirt")
assert result.success, result.summary()
```

**Apparel rules:**
- MUST have transparent background (graphic prints on fabric)
- Same artwork works for both tshirt and hoodie (same dimensions)

## Mug Pipeline

```
source artwork → remove background → compose onto 2700x1050 → validate
```

```bash
# Center artwork on mug wrap canvas
agentbrush composite paste-centered mug_design.png \
  --overlay artwork.png --canvas 2700x1050 --fit

# Validate
agentbrush validate check mug_design.png --preset mug
```

**Mug rules:**
- 11oz: 2700x1050, 15oz: 2700x1140
- Design wraps around the mug surface (wide horizontal strip)
- Artwork at far left/right meets at the handle

## Multi-Sticker Mug Composition

```python
from agentbrush import composite
from PIL import Image

canvas = Image.new("RGBA", (2700, 1050), (0, 0, 0, 0))
canvas.save("mug_canvas.png")

stickers = [
    ("cat.png", (200, 100)),
    ("code.png", (1000, 150)),
    ("coffee.png", (1800, 100)),
]

current = "mug_canvas.png"
for i, (sticker, pos) in enumerate(stickers):
    output = f"mug_step{i}.png"
    composite(current, sticker, output, position=pos, resize_overlay=(400, 400))
    current = output
```

## Poster Pipeline

```bash
# Validate poster dimensions (5400x7200 portrait)
agentbrush validate check poster.png --preset poster
```

**Poster rules:**
- 5400x7200 portrait orientation
- Solid background OK (no transparency needed)

## Desk Mat Pipeline

```bash
# Validate desk mat (9200x4500)
agentbrush validate check deskmat.png --preset deskmat
```

## Cross-Product Expansion

Same artwork across multiple products — resize to each target:

```bash
# Source artwork (transparent bg)
agentbrush resize artwork.png tshirt.png --width 4500 --height 5400 --pad
agentbrush resize artwork.png hoodie.png --width 4500 --height 5400 --pad
agentbrush composite paste-centered mug.png --overlay artwork.png --canvas 2700x1050 --fit
agentbrush resize artwork.png sticker.png --width 1664 --height 1664 --pad
```
