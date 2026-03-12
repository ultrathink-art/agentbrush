# Changelog

## 0.2.0 (2026-03-12)

### Validate Module
- Added 9 general-purpose presets: `social-og`, `social-square`, `social-story`, `favicon`, `icon-ios`, `icon-android`, `thumbnail`, `banner`, `avatar`
- `--preset` is now the primary validation flag (works for both general and domain-specific presets)
- `--type` retained for backward compatibility
- Custom specs via `--width`, `--height`, `--transparent` CLI flags
- New exports: `PRESETS`, `POD_PRESETS`, `ALL_PRESETS` (plus `PRODUCT_SPECS` alias)

### CLI
- `border-cleanup` help: generalized from "sticker border" to "border artifacts"
- `validate` help: generalized from "product specs" to "presets or custom specs"

### Docs
- README: general-purpose only — POD presets/workflows moved to `docs/presets/`
- SKILL.md: rewritten as general-purpose image toolkit
- New: `docs/examples/social_media_images.md` — OG images, avatars, icons
- New: `docs/examples/background_removal.md` — general bg removal guide
- Domain-specific presets (POD) available in `docs/presets/pod.md`
- Domain-specific workflows available in `docs/examples/pod_workflows.md`

### Internal
- `connectivity.py` docstrings: generalized to icons/logos/sprites
- `border/ops.py` docstrings: removed sticker-specific framing

### Tests
- 8 new tests for general presets, custom specs, and backward compat
- 134 tests total (up from 126)

## 0.1.1 (2026-03-11)

### CLI
- Added `paste-centered` subcommand to `agentbrush composite` — center artwork on a new canvas with `--canvas WxH`, `--fit`, `--bg-color` options
- Fixed README composite syntax: removed spurious `overlay` subcommand prefix

### Docs
- Fixed `text` CLI examples in SKILL.md and README — removed nonexistent `add`/`render` subcommands, correct syntax is `agentbrush text <input> <output> <text>` (use `new:WxH` as input for blank canvas)
- Fixed `--font mono-bold` → `--font mono --bold` (CLI uses separate flag)
- Fixed README standalone requirements: Python >= 3.10 + Pillow >= 12.1 (was "pip install Pillow")

### Tests
- 126 tests (up from 122)

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
