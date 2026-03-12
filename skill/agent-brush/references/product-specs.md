# Product Specifications Reference

## Print-on-Demand Product Dimensions

### Apparel (transparent background required)

**T-shirt** (Printify Blueprint 145)
- Print area: 4500 x 5400 px
- Aspect ratio: 0.7 - 1.2
- MUST have transparent background — graphic prints on fabric
- Tolerance: +/- 500px

**Hoodie** (Printify Blueprint 458)
- Print area: 4500 x 5400 px
- Aspect ratio: 0.7 - 1.2
- MUST have transparent background
- Tolerance: +/- 500px

**Hat / Trucker Cap**
- Print area: 1890 x 765 px
- Aspect ratio: >= 1.5 (wide horizontal)
- MUST have transparent background
- Tolerance: +/- 200px

**Tote Bag**
- Print area: 3900 x 4800 px
- Aspect ratio: 0.7 - 0.95
- MUST have transparent background
- Tolerance: +/- 500px

### Drinkware

**Mug 11oz** (Printify Blueprint 175)
- Print area: 2700 x 1050 px (NOT square!)
- Aspect ratio: >= 2.0
- Transparent background recommended
- Wraps around the mug surface
- Tolerance: +/- 100px

**Mug 15oz**
- Print area: 2700 x 1140 px
- Same constraints as 11oz, taller wrap

### Stickers

**Die-cut Sticker** (Printify Blueprint 600)
- Recommended: 1664 x 1664 px (square canvas)
- Max: 1800 x 1800 px
- Aspect ratio: 0.9 - 1.1
- MUST have transparent background
- MUST be a single continuous shape (no floating elements)
- Die-cut follows artwork outline
- Tolerance: +/- 500px

**Sticker Sheet** (Printify Blueprint 661)
- Print area: 825 x 525 px (6x4" sheet)
- Multiple sticker designs composited onto one sheet

### Large Format

**Poster** (Printify Blueprint 97)
- Print area: 5400 x 7200 px (portrait)
- Aspect ratio: 0.65 - 0.85
- Solid background OK (no transparency needed)
- Tolerance: +/- 500px

**Desk Mat** (Printify Blueprint 975)
- Print area: 9200 x 4500 px (31.5 x 15.5")
- Aspect ratio: 1.8 - 2.3
- Solid background OK
- Tolerance: +/- 500px

## Design Guidelines

### Transparency Rules
- Apparel: transparent bg MANDATORY. Only the graphic prints on fabric.
- Stickers: transparent bg MANDATORY. Die-cut machine follows the outline.
- Mugs: transparent bg recommended. Design wraps around surface.
- Posters/Desk mats: solid background OK — prints on the full surface.

### Sticker-Specific Rules
- **Single continuous shape**: Die-cut stickers must form one connected piece. Floating elements (code symbols, decorative dots) can't be printed as separate pieces.
- **No rectangular backgrounds**: Adding a colored rectangle/circle behind the illustration defeats die-cut. The illustration outline IS the cut line.
- **Visual complexity minimum**: Text-only stickers on a flat color aren't compelling products. Include illustration, characters, or visual humor.
- **Poster-layout detection**: >70% fill + >75% rectangularity = automatic FAIL.

### Color Space
- All designs: RGB color space for digital mockups
- Print files: CMYK conversion handled by print provider
- Avoid pure black (#000000) in large areas — use near-black (#1a1a1a) for richer print

### Resolution
- Minimum 1000px in any dimension (below = pixelated in print)
- AI-generated images: generate at target size or larger, then resize down
- Upscaling: use LANCZOS resampling (best quality for downscaling too)

### File Format
- PNG for designs with transparency
- JPEG for solid-background designs (smaller file size)
- Always validate with `agentbrush validate check <file> --type <product>` before upload

## Common Product Pipelines

### Sticker Pipeline
1. Generate illustration (AI or manual)
2. Remove background (`remove-bg` or `greenscreen`)
3. Clean up borders (`border-cleanup`)
4. Add text overlay if needed (`agentbrush text input.png output.png "TEXT" [options]`)
5. Ensure single shape (validated by `validate check --type sticker`)
6. Resize to 1664x1664 if needed

### Apparel Pipeline (T-shirt/Hoodie)
1. Create artwork at 4500x5400 or resize to fit
2. Ensure transparent background
3. Validate: `validate check --type tshirt`

### Mug Pipeline
1. Create or adapt artwork
2. Remove background if source has one
3. Resize/pad to 2700x1050 (11oz) or 2700x1140 (15oz)
4. Validate: `validate check --type mug`
