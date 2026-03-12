# Troubleshooting Guide

## Background Removal

### Problem: Internal details destroyed after bg removal
**Cause**: Using threshold-based removal (ImageMagick `-fuzz -transparent`).
**Fix**: Always use edge-based flood fill: `agentbrush remove-bg`. It starts from image edges only, preserving artwork interior.

### Problem: Background not fully removed
**Cause**: Threshold too low for the background color variation.
**Fix**: Increase `--threshold` (default: 25). Try 30-50 for noisy backgrounds. Verify with `agentbrush validate compare source.png processed.png`.

### Problem: Image already transparent, nothing to remove
**Symptom**: Warning "Image is already fully transparent".
**Cause**: Source image already has alpha channel with bg removed.
**Fix**: This is a no-op — the image is already processed. Skip this step.

## Green Screen

### Problem: Dark green areas in artwork get removed
**Cause**: Sweep threshold too aggressive.
**Fix**: Increase `--sweep-threshold` (default: 50). Dark greens in artwork (forest, army, etc.) have different hue than pure #00FF00.

### Problem: Green fringe/halo around edges after removal
**Cause**: Anti-aliased edges blend artwork with green background.
**Fix**: Use `--halo-passes 20` for iterative green halo erosion. For best results: `agentbrush greenscreen input.png output.png --upscale 3 --halo-passes 20`.

### Problem: OpenAI pre-removed the green screen
**Symptom**: Flood fill removes <100 pixels.
**Cause**: GPT Image sometimes returns RGBA with alpha=0 on green pixels.
**Fix**: AgentBrush auto-detects this (checks `pre_transparent` in metadata). It skips flood fill and goes straight to sweep + halo cleanup.

### Problem: Trapped green patches inside artwork
**Cause**: Green areas completely enclosed by artwork, unreachable by edge flood fill.
**Fix**: The sweep pass handles this automatically. If patches persist, increase sweep passes or lower sweep threshold.

## Border Cleanup

### Problem: Border erosion eating into colored artwork
**Cause**: Threshold too low — removing pixels that aren't actually white border.
**Fix**: Increase `--threshold` (default: 185). Values below 170 eat into colored artwork. 185 is the safe default.

### Problem: White border still visible after cleanup
**Cause**: Not enough erosion passes for thick borders.
**Fix**: Increase `--passes` (default: 15). AI-generated sticker borders may need 20-25 passes.

## Text Rendering

### Problem: Text lines overlapping at large font sizes
**Cause**: Using `textbbox` height for line spacing instead of `font.getmetrics()`.
**Fix**: AgentBrush handles this correctly internally. If writing custom text code, use `ascent + descent` from `font.getmetrics()` for line height, NOT `textbbox` height.

### Problem: Text positioned incorrectly (offset from expected Y)
**Cause**: Pillow `textbbox` returns non-zero y-offset at large font sizes.
**Fix**: AgentBrush corrects for this automatically. The y-offset from `textbbox((0,0), text, font=font)` must be subtracted from the target Y position.

### Problem: Curved/arc text looks garbled
**Cause**: Pillow's character-by-character curve placement is broken.
**Fix**: Use straight horizontal text only. Stack text lines instead of curving. This is a Pillow limitation.

### Problem: Font not found
**Fix**: AgentBrush bundles three font families (Space Mono, JetBrains Mono, DejaVu Sans Mono) and searches system font directories as fallback. Available aliases: `mono`, `mono-bold`, `jetbrains`, `jetbrains-bold`, `dejavu`, `dejavu-bold`. Falls back to Pillow default if nothing found.

## Compositing

### Problem: Overlay appears with black rectangle instead of transparency
**Cause**: Overlay image not in RGBA mode or alpha channel missing.
**Fix**: AgentBrush auto-converts to RGBA. If using the Python API directly, ensure `img.convert("RGBA")` before compositing.

### Problem: Overlay positioned wrong on product canvas
**Fix**: Use `paste_centered()` with `fit=True` to auto-center and scale. For manual positioning, coordinates are (x, y) from top-left corner.

## Validation

### Problem: "POSTER LAYOUT DETECTED" on sticker
**Cause**: Sticker has a rectangular background fill (>70% fill + >75% rectangularity).
**Fix**: Die-cut stickers must be cut to illustration shape on transparent background. Remove the background rectangle — the illustration outline IS the die-cut line.

### Problem: "SLOP WARNING: Very low visual complexity"
**Cause**: Design has <25 color buckets and <8% edge density (text-only flat design).
**Fix**: Add illustration, characters, or visual elements. Text-only designs aren't compelling products.

### Problem: "TRANSPARENCY: Apparel designs MUST have transparent backgrounds"
**Fix**: Run `agentbrush remove-bg` or `agentbrush greenscreen` to remove the solid background before uploading apparel designs.

### Problem: "INTERNAL HOLES" warning after bg removal
**Cause**: Threshold-based removal damaged artwork interior (transparent holes where detail should be).
**Fix**: Re-process from source using edge-based flood fill (`agentbrush remove-bg`). Verify with `agentbrush validate compare source.png processed.png --max-loss 10`.

## Resize

### Problem: Image distorted after resize
**Cause**: Using exact resize with wrong aspect ratio.
**Fix**: Use `--fit` to preserve aspect ratio, or `--pad` to fit + pad to exact dimensions with transparent padding.

### Problem: Pixelated output after upscale
**Fix**: AgentBrush uses LANCZOS resampling (best quality). For very large upscales (>3x), consider generating at target size instead of upscaling.

## General

### Problem: `ModuleNotFoundError: No module named 'agentbrush'`
**Fix (pip install)**: `pip install agentbrush`
**Fix (standalone)**: Run scripts from the repo root, or use the wrapper scripts in `skill/agent-brush/scripts/` which auto-detect the source path.

### Problem: `PIL`/`Pillow` import error
**Fix**: `pip install Pillow>=12.1`

### Problem: `openai` import error on `generate` command
**Fix**: `pip install agentbrush[generate]` — OpenAI is an optional dependency.

### Problem: Exit code meanings
- **0**: Success
- **1**: Validation failure (design doesn't meet specs)
- **2**: Input error (file not found, missing params)
