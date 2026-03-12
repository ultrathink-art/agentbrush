"""Image compositing: layer artwork onto canvases.

Handles alpha-composite layering, centering, and positioning.
Used for sticker sheet assembly, mug wrap compositing, etc.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.result import Result


def composite(
    base_path: Union[str, Path],
    overlay_path: Union[str, Path],
    output_path: Union[str, Path],
    position: Tuple[int, int] = (0, 0),
    resize_overlay: Optional[Tuple[int, int]] = None,
    opacity: float = 1.0,
) -> Result:
    """Alpha-composite an overlay image onto a base image.

    Args:
        base_path: Background image path.
        overlay_path: Foreground image path (composited on top).
        output_path: Destination path.
        position: (x, y) where overlay top-left corner is placed.
        resize_overlay: Optional (width, height) to resize overlay before compositing.
        opacity: Overlay opacity 0.0-1.0 (default: fully opaque).

    Returns:
        Result with stats.
    """
    base_path = Path(base_path)
    overlay_path = Path(overlay_path)
    output_path = Path(output_path)

    for p in [base_path, overlay_path]:
        if not p.exists():
            return Result(errors=[f"File not found: {p}"])

    base = Image.open(base_path).convert("RGBA")
    overlay = Image.open(overlay_path).convert("RGBA")

    if resize_overlay:
        overlay = overlay.resize(resize_overlay, Image.LANCZOS)

    if opacity < 1.0:
        # Reduce overlay alpha by opacity factor
        r, g, b, a = overlay.split()
        a = a.point(lambda x: int(x * opacity))
        overlay = Image.merge("RGBA", (r, g, b, a))

    # Paste overlay at position using its own alpha as mask
    base.paste(overlay, position, overlay)

    os.makedirs(output_path.parent, exist_ok=True)
    base.save(output_path, "PNG")

    result = Result.from_image(base, output_path)
    result.metadata = {
        "overlay_size": f"{overlay.width}x{overlay.height}",
        "position": f"{position[0]},{position[1]}",
        "opacity": opacity,
    }
    return result


def paste_centered(
    canvas_width: int,
    canvas_height: int,
    overlay_path: Union[str, Path],
    output_path: Union[str, Path],
    bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
    resize_overlay: Optional[Tuple[int, int]] = None,
    fit: bool = False,
) -> Result:
    """Place an image centered on a new canvas.

    Args:
        canvas_width: Canvas width.
        canvas_height: Canvas height.
        overlay_path: Image to center on canvas.
        output_path: Destination path.
        bg_color: Canvas background color (default: transparent).
        resize_overlay: Optional explicit (w, h) resize for overlay.
        fit: If True, scale overlay to fit canvas while preserving aspect ratio.

    Returns:
        Result with stats.
    """
    overlay_path = Path(overlay_path)
    output_path = Path(output_path)

    if not overlay_path.exists():
        return Result(errors=[f"File not found: {overlay_path}"])

    canvas = Image.new("RGBA", (canvas_width, canvas_height), bg_color)
    overlay = Image.open(overlay_path).convert("RGBA")

    if resize_overlay:
        overlay = overlay.resize(resize_overlay, Image.LANCZOS)
    elif fit:
        # Scale to fit while preserving aspect ratio
        scale = min(canvas_width / overlay.width, canvas_height / overlay.height)
        new_w = int(overlay.width * scale)
        new_h = int(overlay.height * scale)
        overlay = overlay.resize((new_w, new_h), Image.LANCZOS)

    # Center overlay on canvas
    x = (canvas_width - overlay.width) // 2
    y = (canvas_height - overlay.height) // 2

    canvas.paste(overlay, (x, y), overlay)

    os.makedirs(output_path.parent, exist_ok=True)
    canvas.save(output_path, "PNG")

    result = Result.from_image(canvas, output_path)
    result.metadata = {
        "canvas": f"{canvas_width}x{canvas_height}",
        "overlay_size": f"{overlay.width}x{overlay.height}",
        "position": f"{x},{y}",
    }
    return result
