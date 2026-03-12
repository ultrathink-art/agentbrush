# Architecture

## Design Principles

1. **Edge-based flood fill only** — never threshold-based pixel removal
2. **Uniform Result type** — every operation returns `Result` with the same fields
3. **CLI mirrors API** — every Python function has a CLI subcommand
4. **Cross-platform** — no hardcoded OS paths; bundled fonts as fallback
5. **Minimal dependencies** — only Pillow required; OpenAI optional
6. **Standalone scripts** — work from git clone without pip install

## Directory Layout

```
agentbrush/
├── src/agentbrush/          # Python package (pip installable)
│   ├── __init__.py          # Public API re-exports
│   ├── __main__.py          # python -m agentbrush
│   ├── cli.py               # Top-level argparse dispatcher
│   ├── core/                # Shared primitives
│   │   ├── flood_fill.py    # BFS flood fill (4/8-connectivity)
│   │   ├── color.py         # Color matching, parsing
│   │   ├── alpha.py         # Alpha channel ops, edge smoothing
│   │   ├── geometry.py      # Bounds, crop, centroid
│   │   ├── connectivity.py  # Die-cut single shape (8-connected BFS)
│   │   ├── fonts.py         # Cross-platform font discovery
│   │   └── result.py        # Uniform Result dataclass
│   └── <module>/            # Each module has:
│       ├── __init__.py      #   Re-export from ops
│       ├── cli.py           #   argparse subcommand registration
│       └── ops.py           #   Core logic + public function
├── skill/agent-brush/       # Agent Skills package
│   ├── SKILL.md             # Agent instructions + quick reference
│   ├── references/          # Product specs, troubleshooting
│   └── scripts/             # Standalone wrappers
├── fonts/                   # Bundled OFL fonts
├── tests/                   # pytest suite (synthetic fixtures)
└── docs/examples/           # Pipeline guides
```

## Module Pattern

Every operation module follows the same structure:

```
module/
├── __init__.py    # from .ops import main_function
├── cli.py         # add_parser(subparsers) + run(args) -> exit_code
└── ops.py         # main_function(...) -> Result
```

**ops.py** contains the core logic. It:
- Accepts `Union[str, Path]` for file paths
- Returns `Result` with stats
- Sets `Result.errors` on failure (never raises exceptions to callers)
- Prints nothing (caller prints `result.summary()`)

**cli.py** registers an argparse subparser and converts CLI args to function calls.

**__init__.py** re-exports the main function for `from agentbrush.module import func`.

## Result Dataclass

All operations return `Result`:

```python
@dataclass
class Result:
    output_path: Optional[Path]
    width: int
    height: int
    transparent_pct: float     # 0-100
    opaque_pct: float          # 0-100
    warnings: list[str]        # Non-fatal issues
    errors: list[str]          # Fatal issues
    metadata: dict[str, Any]   # Operation-specific data

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        """Human-readable string for stdout."""
```

## Flood Fill Algorithm

The core differentiator. BFS from all 4 edges simultaneously:

1. Seed queue with all border pixels matching target color
2. BFS expands to adjacent matching pixels (4-connectivity default)
3. Set matched pixels to transparent (alpha=0)
4. Interior pixels matching the color are never reached

This preserves internal outlines and details that threshold-based removal destroys.

## Font Discovery

Search order:
1. Bundled fonts in `fonts/` directory (Space Mono, JetBrains Mono, DejaVu)
2. System directories (macOS, Linux, Windows platform-specific paths)
3. Pillow default fallback

Name aliases map friendly names to filenames: `mono` -> `SpaceMono-Regular.ttf`, `jetbrains-bold` -> `JetBrainsMono-Bold.ttf`, etc.

## Standalone Script Pattern

Each script in `skill/agent-brush/scripts/` uses this auto-detection:

```python
_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)
```

This makes scripts work both:
- **Standalone**: `python scripts/remove_bg.py` (finds `src/` relative to script)
- **Installed**: `python scripts/remove_bg.py` (imports from site-packages)
