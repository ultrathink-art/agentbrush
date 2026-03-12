"""Cross-platform font discovery with bundled fallbacks.

Search order: (1) bundled fonts, (2) system dirs, (3) Pillow default.
NEVER hardcode macOS-specific paths like /Users/*/Library/Fonts/.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from PIL import ImageFont

# Bundled fonts directory (relative to package root)
_FONTS_DIR = Path(__file__).parent.parent.parent.parent / "fonts"

# Font name aliases → filename mappings
_FONT_MAP = {
    "mono": "SpaceMono-Regular.ttf",
    "mono-bold": "SpaceMono-Bold.ttf",
    "space": "SpaceMono-Regular.ttf",
    "space-bold": "SpaceMono-Bold.ttf",
    "space-mono": "SpaceMono-Regular.ttf",
    "space-mono-bold": "SpaceMono-Bold.ttf",
    "jetbrains": "JetBrainsMono-Regular.ttf",
    "jetbrains-bold": "JetBrainsMono-Bold.ttf",
    "dejavu": "DejaVuSansMono.ttf",
    "dejavu-bold": "DejaVuSansMono-Bold.ttf",
}

# System font directories by platform
_SYSTEM_FONT_DIRS = {
    "darwin": [
        "/System/Library/Fonts",
        "/System/Library/Fonts/Supplemental",
        "/Library/Fonts",
        Path.home() / "Library" / "Fonts",
    ],
    "linux": [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".local" / "share" / "fonts",
        Path.home() / ".fonts",
    ],
    "win32": [
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts",
    ],
}


def _get_system_dirs():
    platform = sys.platform
    if platform.startswith("linux"):
        platform = "linux"
    return [Path(d) for d in _SYSTEM_FONT_DIRS.get(platform, [])]


def _search_dirs(filename: str) -> Optional[Path]:
    """Search bundled fonts dir, then system dirs for a font file."""
    # Bundled fonts first
    bundled = _FONTS_DIR / filename
    if bundled.exists():
        return bundled

    # System dirs
    for d in _get_system_dirs():
        candidate = Path(d) / filename
        if candidate.exists():
            return candidate
        # Recursive search (fonts often in subdirs)
        if Path(d).is_dir():
            for root, _dirs, files in os.walk(d):
                if filename in files:
                    return Path(root) / filename

    return None


def find_font(
    name: str,
    size: int = 24,
    bold: bool = False,
) -> ImageFont.FreeTypeFont:
    """Find and load a font by name.

    Args:
        name: Font name alias (e.g. 'mono', 'jetbrains') or filename.
        size: Font size in points.
        bold: If True and name is an alias, prefer the bold variant.

    Returns:
        Loaded Pillow FreeTypeFont. Falls back to Pillow default if not found.
    """
    # Resolve alias
    lookup = name.lower().strip()
    if bold and lookup in _FONT_MAP and not lookup.endswith("-bold"):
        lookup = lookup + "-bold"

    filename = _FONT_MAP.get(lookup)

    if filename:
        path = _search_dirs(filename)
        if path:
            return ImageFont.truetype(str(path), size)

    # Try as direct filename
    path = _search_dirs(name)
    if path:
        return ImageFont.truetype(str(path), size)

    # Try as absolute/relative path
    if os.path.exists(name):
        return ImageFont.truetype(name, size)

    # Fallback to Pillow default
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Older Pillow versions don't accept size param
        return ImageFont.load_default()
