# Changelog

## 0.1.0 (2026-03-11)

Initial release.

### Core Library
- `agentbrush.core`: flood fill, color matching, alpha ops, geometry, connectivity, fonts, Result dataclass
- Edge-based flood fill (BFS from edges only) — never threshold-based removal
- Cross-platform font discovery with bundled Space Mono, JetBrains Mono, DejaVu Sans Mono

### Modules
- `background`: Solid-color background removal via edge-based flood fill
- `greenscreen`: Multi-pass green screen pipeline (flood fill + color sweep + post-upscale sweep)
- `border`: White border erosion + green halo cleanup + alpha edge smoothing
- `text`: Pillow text rendering with textbbox y-offset correction and getmetrics() line height
- `composite`: Alpha compositing with overlay positioning and centered paste
- `resize`: Scale, fit, pad modes with LANCZOS resampling
- `validate`: Design QA — dimensions, aspect ratio, transparency, sticker layout/complexity detection
- `convert`: Format conversion (PNG, JPEG, WEBP, BMP, TIFF) with RGBA->RGB alpha flattening
- `generate`: AI image generation via OpenAI GPT Image and Pollinations (optional dependency)

### CLI
- `agentbrush <command>` dispatcher with 9 subcommands
- Uniform exit codes: 0=success, 1=validation fail, 2=input error

### Agent Skills Package
- `skill/agent-brush/SKILL.md` — Agent Skills standard entrypoint
- `skill/agent-brush/references/` — product specs, troubleshooting guide
- `skill/agent-brush/scripts/` — standalone wrappers (work without pip install)

### Documentation
- Pipeline guides: sticker, t-shirt, mug
- 122 tests (all synthetic fixtures)
