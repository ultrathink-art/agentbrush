# Background Removal

Techniques for removing backgrounds from images using edge-based flood fill.

## Why Edge-Based?

Threshold-based removal (ImageMagick `-fuzz -transparent`) scans every pixel — removes internal outlines, shadows, and fine details that match the target color.

AgentBrush uses BFS from image edges only. Interior pixels matching the background color are preserved because flood fill can't reach them through the artwork.

## Black Background

```bash
agentbrush remove-bg photo.png output.png --color black --threshold 25
```

- `--threshold 25`: how far from pure black to match (0=exact, higher=more aggressive)
- `--smooth`: optional edge feathering after removal

```python
from agentbrush import remove_background

result = remove_background("photo.png", "output.png", color="black", threshold=25)
print(f"Removed {result.metadata['pixels_removed']} pixels")
print(f"Transparency: {result.transparent_pct:.1f}%")
```

## White Background

```bash
agentbrush remove-bg photo.png output.png --color white --threshold 30
```

White backgrounds often need a slightly higher threshold due to JPEG compression artifacts near edges.

## Custom Color

```bash
# Remove blue background
agentbrush remove-bg photo.png output.png --color "0,0,200" --threshold 40
```

## Green Screen (Multi-Pass)

For green screen images, use the dedicated `greenscreen` command which runs three passes:

1. **Edge flood fill** — removes green connected to image borders
2. **Color sweep** — catches trapped green patches inside the image
3. **Post-upscale sweep** — removes LANCZOS anti-alias green fringe after upscaling

```bash
# Standard
agentbrush greenscreen input.png output.png

# With upscale and halo cleanup
agentbrush greenscreen input.png output.png --upscale 3 --halo-passes 20
```

**Tip:** When generating AI images, prompt for `"pure bright green background (hex 00FF00)"` — green is fully separable from most artwork colors.

## Verifying Results

Always verify background removal didn't damage the artwork:

```bash
agentbrush validate compare source.png processed.png --max-loss 10
```

This checks opaque pixel loss. >10% loss usually means the removal was too aggressive.

## Border Cleanup After Removal

AI-generated images often have a white outline around the subject. After bg removal, this outline becomes visible:

```bash
agentbrush border-cleanup cleaned.png final.png --passes 15 --threshold 185
```

For green screen sources, also clean green halo:

```bash
agentbrush border-cleanup cleaned.png final.png \
  --passes 15 --green-halo-passes 20 --alpha-smooth
```

## Complete Pipeline

```python
from agentbrush import (
    remove_background, cleanup_border,
    validate_design, compare_images,
)

# Remove background
result = remove_background("input.png", "step1.png", color="black", threshold=25)
assert result.success

# Verify no damage
result = compare_images("input.png", "step1.png", max_loss_pct=10)
assert result.success, f"Too much pixel loss: {result.metadata['loss_pct']}%"

# Clean up border artifacts
result = cleanup_border("step1.png", "final.png", passes=15, alpha_smooth=True)
assert result.success

print(f"Final: {result.width}x{result.height}, {result.transparent_pct:.1f}% transparent")
```
