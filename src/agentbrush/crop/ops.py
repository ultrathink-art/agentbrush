"""Smart crop — auto-detect content bounds and crop to tight bounding box.

Uses alpha channel to find opaque content bounds, then crops with
configurable padding. Works on any RGBA image with transparent regions.
For RGB images, detects dominant edge color as background.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.geometry import find_artwork_bounds
from agentbrush.core.result import Result


def smart_crop(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    padding: int = 0,
    alpha_threshold: int = 20,
    bg_color: Optional[Tuple[int, int, int]] = None,
) -> Result:
    """Crop image to tight bounding box around content.

    For RGBA images: finds opaque pixel bounds (alpha > threshold).
    For RGB images: if bg_color given, converts matching edge pixels
    to transparent first; otherwise uses alpha-based detection on the
    RGBA conversion (which preserves all pixels as opaque).

    Args:
        input_path: Source image path.
        output_path: Destination path.
        padding: Extra pixels around content bounds (default: 0).
        alpha_threshold: Minimum alpha to consider opaque (default: 20).
        bg_color: Optional RGB tuple — treat this color as background
            (useful for RGB images with solid bg).

    Returns:
        Result with crop stats in metadata.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    img = Image.open(input_path).convert("RGBA")
    orig_w, orig_h = img.size

    if bg_color is not None:
        pixels = img.load()
        for y in range(orig_h):
            for x in range(orig_w):
                r, g, b, a = pixels[x, y]
                if (
                    abs(r - bg_color[0]) < 30
                    and abs(g - bg_color[1]) < 30
                    and abs(b - bg_color[2]) < 30
                ):
                    pixels[x, y] = (r, g, b, 0)

    x1, y1, x2, y2 = find_artwork_bounds(img, alpha_threshold)

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(orig_w, x2 + padding)
    y2 = min(orig_h, y2 + padding)

    cropped = img.crop((x1, y1, x2, y2))

    os.makedirs(output_path.parent, exist_ok=True)
    cropped.save(output_path, "PNG")

    result = Result(
        output_path=output_path,
        width=cropped.width,
        height=cropped.height,
    )
    result.metadata = {
        "original_size": f"{orig_w}x{orig_h}",
        "crop_box": f"{x1},{y1},{x2},{y2}",
        "padding": padding,
        "pixels_removed": (orig_w * orig_h) - (cropped.width * cropped.height),
    }
    return result
