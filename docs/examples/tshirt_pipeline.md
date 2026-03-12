# T-Shirt Pipeline

End-to-end workflow for creating print-ready t-shirt designs.

## Overview

```
AI prompt → generate artwork → remove background → add text (optional)
  → resize to 4500x5400 → validate → upload
```

## Key Constraint

**T-shirt designs MUST have transparent backgrounds.** Only the graphic prints on fabric. A solid rectangle = printing a rectangle on the shirt.

## Step 1: Generate Artwork

Use green screen technique for clean background separation:

```bash
agentbrush generate \
  --provider openai \
  --prompt "illustrated cartoon skull with headphones and code symbols, developer humor, vibrant colors, thick clean outlines, pure bright green background hex 00FF00, no text" \
  --output raw_design.png \
  --width 1024 --height 1024
```

**Tips:**
- Green screen (`#00FF00`) gives cleanest separation from dark artwork
- For light/pastel artwork, use black background (`#000000`) instead
- Prompt for `"no text"` — add text programmatically for accuracy
- Generate at 1024x1024+ then resize up to 4500x5400

## Step 2: Remove Background

### Green screen source:

```bash
agentbrush greenscreen raw_design.png clean_design.png \
  --halo-passes 15 \
  --upscale 3
```

### Black background source:

```bash
agentbrush remove-bg raw_design.png clean_design.png \
  --color black --threshold 25 --smooth
```

### Verify no artwork damage:

```bash
agentbrush validate compare raw_design.png clean_design.png --max-loss 10
```

## Step 3: Add Text (Optional)

```python
from agentbrush import add_text

result = add_text(
    "clean_design.png", "with_text.png",
    text="WORKS ON\nMY MACHINE",
    position=(512, 900),  # Below main illustration
    font_name="mono-bold",
    font_size=64,
    color=(255, 255, 255, 255),  # White text (shows on dark shirts)
    max_width=800,
)
```

**Note:** White text on transparent background is correct for dark shirt printing. It will look invisible in previews but prints correctly on dark fabric.

## Step 4: Resize to Print Dimensions

```bash
# Fit artwork into 4500x5400 with transparent padding
agentbrush resize with_text.png tshirt_ready.png \
  --width 4500 --height 5400 --pad
```

The `--pad` flag scales the artwork to fit within 4500x5400 while preserving aspect ratio, then pads with transparent pixels to hit exact dimensions. The artwork appears centered on the shirt.

## Step 5: Validate

```bash
agentbrush validate check tshirt_ready.png --type tshirt
```

Validates:
- **Dimensions**: 4500x5400 (+/- 500px tolerance)
- **Aspect ratio**: 0.7 - 1.2
- **Transparency**: MUST have transparent areas (apparel rule)
- **Interior holes**: Warns if bg removal damaged internal details
- **Resolution**: Warns if below 1000px in any dimension

## Complete Python Script

```python
from agentbrush import (
    generate_image, remove_greenscreen, cleanup_border,
    add_text, resize_image, validate_design,
)

# Generate with green screen
result = generate_image(
    "illustrated skull with headphones, developer vibes, "
    "thick outlines, pure bright green background #00FF00, no text",
    "step1_raw.png", provider="openai",
)
assert result.success

# Remove green screen
result = remove_greenscreen(
    "step1_raw.png", "step2_clean.png",
    halo_passes=15, upscale=3,
)
assert result.success

# Optional: clean up any border artifacts
result = cleanup_border(
    "step2_clean.png", "step3_trimmed.png",
    passes=10, green_halo_passes=15,
)
assert result.success

# Add text
result = add_text(
    "step3_trimmed.png", "step4_text.png",
    text="WORKS ON\nMY MACHINE",
    position=(512, 900),
    font_name="mono-bold", font_size=64,
    color=(255, 255, 255, 255),
)
assert result.success

# Resize to t-shirt dimensions
result = resize_image(
    "step4_text.png", "step5_final.png",
    width=4500, height=5400, pad=True,
)
assert result.success

# Validate
result = validate_design("step5_final.png", product_type="tshirt")
assert result.success, result.summary()
print("T-shirt design ready for upload!")
```

## Expanding to Hoodie

Hoodies use the same 4500x5400 print area. Reuse the exact same artwork file:

```bash
agentbrush validate check step5_final.png --type hoodie
```

No changes needed — same dimensions, same transparency requirement.

## Common Mistakes

1. **Solid background on apparel** — prints a colored rectangle on the shirt. Always transparent.
2. **Relying on AI for text** — AI text has kerning, spelling, and placement defects. Use `add_text()`.
3. **White text looks invisible in preview** — this is correct for dark shirt printing. Check pixel opacity with `img.getpixel()`, don't iterate trying to "fix" it.
4. **Wrong aspect ratio** — 4500x5400 is portrait (0.83:1). Don't create landscape designs for shirts.
5. **Low resolution** — generating at 512x512 then upscaling to 4500x5400 = pixelated. Generate at 1024+ or use `--upscale 3` during green screen removal.
