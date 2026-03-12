# Sticker Pipeline

End-to-end workflow for creating die-cut stickers from AI-generated artwork.

## Overview

```
AI prompt → generate image → remove background → clean borders
  → add text (optional) → validate die-cut → resize → upload
```

## Step 1: Generate Artwork

Use green screen technique for cleanest separation:

```bash
agentbrush generate \
  --provider openai \
  --prompt "cute cartoon cat sitting at a laptop with coffee, thick clean smooth black outlines, kawaii style, pure bright green background hex 00FF00, no text" \
  --output raw_cat.png \
  --width 1024 --height 1024
```

**Tips:**
- Prompt for `"pure bright green background (hex 00FF00)"` — green is fully separable from dark artwork
- Include `"thick clean smooth black outlines"` for cleaner die-cut edges
- Specify `"no text"` — AI text often has errors; add text with Pillow instead
- Use `--width 1024 --height 1024` minimum; larger = higher quality

## Step 2: Remove Green Screen

```bash
agentbrush greenscreen raw_cat.png clean_cat.png \
  --halo-passes 20 \
  --upscale 3
```

Three-pass pipeline:
1. Edge flood fill removes green connected to borders
2. Color sweep catches trapped green patches
3. Post-upscale sweep removes LANCZOS anti-alias fringe

**Check for pre-transparency:** OpenAI sometimes pre-removes green. AgentBrush auto-detects and skips flood fill.

## Step 3: Clean Up Borders

AI generators often add a white "sticker border" around illustrations:

```bash
agentbrush border-cleanup clean_cat.png trimmed_cat.png \
  --passes 15 \
  --threshold 185 \
  --green-halo-passes 20 \
  --alpha-smooth
```

- `--passes 15`: Number of erosion iterations (increase for thick borders)
- `--threshold 185`: Pixels with R,G,B all above this = white border. Below 170 eats artwork.
- `--alpha-smooth`: Gaussian blur on alpha edges for clean die-cut outline

## Step 4: Add Text (Optional)

For stickers with text, use Pillow rendering (NOT AI text):

```python
from agentbrush import add_text

result = add_text(
    "trimmed_cat.png", "labeled_cat.png",
    text="SHIP IT",
    position=(100, 800),
    font_name="mono-bold",
    font_size=72,
    color=(255, 255, 255, 255),
)
```

**Rules:**
- Text MUST overlap/touch the illustration (on a screen, banner, speech bubble)
- Floating text = disconnected element = fails die-cut validation
- Use `mono-bold` or `jetbrains-bold` for readable text at print size

## Step 5: Validate

```bash
agentbrush validate check labeled_cat.png --type sticker
```

Checks:
- **Dimensions**: Near 1664x1664px
- **Aspect ratio**: 0.9 - 1.1 (square)
- **Transparency**: Must have transparent background
- **Single shape**: No floating/detached elements
- **No poster layout**: >70% fill + >75% rectangularity = FAIL
- **Visual complexity**: <25 colors + <8% edge density = slop warning

Also verify bg removal didn't damage artwork:

```bash
agentbrush validate compare raw_cat.png labeled_cat.png --max-loss 10
```

## Step 6: Resize for Print

```bash
agentbrush resize labeled_cat.png final_sticker.png \
  --width 1664 --height 1664 --pad
```

The `--pad` flag preserves aspect ratio and adds transparent padding to hit exact dimensions.

## Complete Python Script

```python
from agentbrush import (
    generate_image, remove_greenscreen, cleanup_border,
    add_text, validate_design, resize_image,
)

# Generate
result = generate_image(
    "cute cat coding, thick black outlines, bright green background #00FF00",
    "step1_raw.png", provider="openai",
)
assert result.success, result.summary()

# Remove green screen
result = remove_greenscreen(
    "step1_raw.png", "step2_clean.png",
    halo_passes=20, upscale=3,
)
assert result.success, result.summary()

# Clean borders
result = cleanup_border(
    "step2_clean.png", "step3_trimmed.png",
    passes=15, green_halo_passes=20, alpha_smooth=True,
)
assert result.success, result.summary()

# Add text
result = add_text(
    "step3_trimmed.png", "step4_labeled.png",
    text="SHIP IT", position=(100, 800),
    font_name="mono-bold", font_size=72,
    color=(255, 255, 255, 255),
)
assert result.success, result.summary()

# Validate
result = validate_design("step4_labeled.png", product_type="sticker")
assert result.success, result.summary()

# Resize
result = resize_image(
    "step4_labeled.png", "final_sticker.png",
    width=1664, height=1664, pad=True,
)
assert result.success, result.summary()
print("Sticker ready for upload!")
```

## Common Mistakes

1. **Using threshold-based bg removal** — destroys internal outlines. Always use edge flood fill.
2. **Rectangular background behind illustration** — defeats die-cut. Illustration outline = cut line.
3. **Floating text or decorative elements** — die-cut can't handle disconnected pieces.
4. **AI-generated text** — frequently has spelling, placement, and kerning defects. Use Pillow.
5. **Skipping border cleanup** — leaves visible white ring in print.
