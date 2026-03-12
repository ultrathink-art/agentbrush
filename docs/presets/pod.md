# Print-on-Demand Presets

Detailed specifications for print-on-demand product validation.

## Product Dimensions

### Apparel (transparent background required)

**T-shirt** (`--preset tshirt` or `--type tshirt`)
- Print area: 4500 x 5400 px
- Aspect ratio: 0.7 - 1.2
- MUST have transparent background — graphic prints on fabric
- Tolerance: +/- 500px

**Hoodie** (`--preset hoodie` or `--type hoodie`)
- Print area: 4500 x 5400 px
- Aspect ratio: 0.7 - 1.2
- MUST have transparent background
- Tolerance: +/- 500px

**Hat / Trucker Cap** (`--preset hat` or `--type hat`)
- Print area: 1890 x 765 px
- Aspect ratio: >= 1.5 (wide horizontal)
- MUST have transparent background
- Tolerance: +/- 200px

**Tote Bag** (`--preset tote` or `--type tote`)
- Print area: 3900 x 4800 px
- Aspect ratio: 0.7 - 0.95
- MUST have transparent background
- Tolerance: +/- 500px

### Drinkware

**Mug 11oz** (`--preset mug` or `--type mug`)
- Print area: 2700 x 1050 px (NOT square!)
- Aspect ratio: >= 2.0
- Transparent background recommended
- Wraps around the mug surface
- Tolerance: +/- 100px

**Mug 15oz**
- Print area: 2700 x 1140 px
- Same constraints as 11oz, taller wrap

### Stickers

**Die-cut Sticker** (`--preset sticker` or `--type sticker`)
- Recommended: 1664 x 1664 px (square canvas)
- Max: 1800 x 1800 px
- Aspect ratio: 0.9 - 1.1
- MUST have transparent background
- MUST be a single continuous shape (no floating elements)
- Die-cut follows artwork outline
- Tolerance: +/- 500px

**Sticker Sheet**
- Print area: 825 x 525 px (6x4" sheet)
- Multiple sticker designs composited onto one sheet

### Large Format

**Poster** (`--preset poster` or `--type poster`)
- Print area: 5400 x 7200 px (portrait)
- Aspect ratio: 0.65 - 0.85
- Solid background OK (no transparency needed)
- Tolerance: +/- 500px

**Desk Mat** (`--preset deskmat` or `--type deskmat`)
- Print area: 9200 x 4500 px (31.5 x 15.5")
- Aspect ratio: 1.8 - 2.3
- Solid background OK
- Tolerance: +/- 500px

## Validation Examples

```bash
# Validate t-shirt design
agentbrush validate check tee_design.png --preset tshirt

# Validate sticker (checks die-cut layout + visual complexity)
agentbrush validate check sticker.png --preset sticker

# Validate mug wrap
agentbrush validate check mug_wrap.png --preset mug

# Backward-compat --type flag still works
agentbrush validate check design.png --type poster
```

## Design Guidelines

### Transparency Rules
- Apparel: transparent bg MANDATORY — only the graphic prints on fabric
- Stickers: transparent bg MANDATORY — die-cut machine follows the outline
- Mugs: transparent bg recommended — design wraps around surface
- Posters/Desk mats: solid background OK — prints on the full surface

### Sticker-Specific Rules
- **Single continuous shape**: must form one connected piece
- **No rectangular backgrounds**: the illustration outline IS the cut line
- **Visual complexity minimum**: text-only on a flat color is flagged as slop
- **Poster-layout detection**: >70% fill + >75% rectangularity = automatic FAIL

### File Format
- PNG for designs with transparency
- JPEG for solid-background designs (smaller file size)
