# Mug Pipeline

End-to-end workflow for creating wrap-around mug designs.

## Overview

```
source artwork → remove background (if needed) → resize/compose to 2700x1050
  → validate → upload
```

## Key Constraints

- **11oz mug**: 2700 x 1050 px (NOT square!)
- **15oz mug**: 2700 x 1140 px
- Design wraps around the mug surface — it's a wide horizontal strip
- Transparent background recommended

## Strategy: Sticker-to-Mug Adaptation

The most common mug workflow: adapt existing sticker/illustration artwork to the mug wrap format.

### Step 1: Prepare Source Artwork

If source has a solid background, remove it first:

```bash
# From black background
agentbrush remove-bg sticker_art.png clean_art.png --color black --threshold 25

# From green screen
agentbrush greenscreen sticker_art.png clean_art.png --halo-passes 15
```

### Step 2: Compose onto Mug Canvas

Center the artwork on the mug wrap dimensions:

```bash
# Center artwork on 11oz mug canvas (transparent padding)
agentbrush composite paste-centered mug_design.png \
  --overlay clean_art.png \
  --canvas 2700x1050 \
  --fit
```

The `--fit` flag scales artwork to fit within 2700x1050 while preserving aspect ratio, then centers it.

For a colored background mug:

```bash
agentbrush composite paste-centered mug_design.png \
  --overlay clean_art.png \
  --canvas 2700x1050 \
  --bg-color "30,30,30,255" \
  --fit
```

### Step 3: Add Text (Optional)

```python
from agentbrush import add_text

# Add text beside/below the artwork
result = add_text(
    "mug_design.png", "mug_with_text.png",
    text="DEBUGGING\nIN PROGRESS",
    position=(1800, 400),  # Right side of wrap
    font_name="mono-bold",
    font_size=48,
    color=(255, 255, 255, 255),
)
```

### Step 4: Validate

```bash
agentbrush validate check mug_design.png --type mug
```

Checks:
- **Dimensions**: Near 2700x1050 (+/- 100px tolerance)
- **Aspect ratio**: >= 2.0 (must be wide, not square)
- **Transparency**: Recommended but not required

### Step 5: 15oz Variant

For the taller 15oz mug, resize the same design:

```bash
agentbrush resize mug_design.png mug_15oz.png \
  --width 2700 --height 1140 --pad
```

## Strategy: Full-Wrap Design

For designs that wrap the entire mug surface (patterns, scenes):

```python
from agentbrush import generate_image, resize_image, validate_design

# Generate wide panoramic design
result = generate_image(
    "panoramic pixel art cityscape with neon signs, "
    "seamless horizontal tile, dark background, no text",
    "panorama_raw.png",
    provider="openai",
    width=1792, height=1024,  # Wide format
)

# Resize to exact mug dimensions
result = resize_image(
    "panorama_raw.png", "mug_wrap.png",
    width=2700, height=1050,
)

# Validate
result = validate_design("mug_wrap.png", product_type="mug")
assert result.success, result.summary()
```

## Strategy: Multi-Sticker Composition

Place multiple small illustrations across the mug surface:

```python
from agentbrush import composite, paste_centered, resize_image
from PIL import Image

# Create transparent mug canvas
canvas = Image.new("RGBA", (2700, 1050), (0, 0, 0, 0))
canvas.save("mug_canvas.png")

# Place stickers at different positions
positions = [
    ("cat_sticker.png", (200, 100)),
    ("code_sticker.png", (1000, 150)),
    ("coffee_sticker.png", (1800, 100)),
]

current = "mug_canvas.png"
for i, (sticker, pos) in enumerate(positions):
    output = f"mug_step{i}.png"
    result = composite(
        current, sticker, output,
        position=pos,
        resize_overlay=(400, 400),  # Uniform sticker size
    )
    current = output

# Final is the last step output
print(f"Mug design complete: {current}")
```

## Complete Python Script (Sticker-to-Mug)

```python
from agentbrush import (
    remove_background, paste_centered,
    add_text, validate_design, compare_images,
)

# Remove background from source artwork
result = remove_background(
    "source_sticker.png", "step1_clean.png",
    color="black", threshold=25,
)
assert result.success

# Verify no artwork damage
result = compare_images("source_sticker.png", "step1_clean.png")
assert result.success, result.summary()

# Center on mug canvas
result = paste_centered(
    2700, 1050,
    "step1_clean.png", "step2_mug.png",
    fit=True,
)
assert result.success

# Add text
result = add_text(
    "step2_mug.png", "step3_text.png",
    text="</ COFFEE >",
    position=(1900, 450),
    font_name="mono-bold", font_size=56,
    color=(255, 255, 255, 255),
)
assert result.success

# Validate
result = validate_design("step3_text.png", product_type="mug")
assert result.success, result.summary()
print("Mug design ready for upload!")
```

## Common Mistakes

1. **Square design for mug** — mugs need 2700x1050 (2.57:1 ratio). Square = distorted or cropped.
2. **Forgetting 15oz variant** — same artwork, just resize to 2700x1140. Easy second SKU.
3. **Design on handle side** — Printify "front" = handle side (usually blank). Position key artwork to show on the opposite side.
4. **Text too small** — mug surface is curved; text under ~36pt becomes hard to read on the actual product.
5. **Ignoring wrap edges** — artwork at the far left/right of the 2700px strip meets at the handle. Avoid placing critical elements at the seam.
