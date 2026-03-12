"""Background removal via edge-based flood fill.

NEVER use threshold-based removal — it destroys internal outlines/details.
This module starts flood fill from image edges only, preserving artwork.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.alpha import smooth_edges
from agentbrush.core.color import ColorTuple, parse_color
from agentbrush.core.flood_fill import flood_fill_from_edges
from agentbrush.core.result import Result


def remove_background(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    color: str = "black",
    threshold: int = 25,
    smooth: bool = False,
    resize: Optional[Tuple[int, int]] = None,
) -> Result:
    """Remove solid-color background using edge-based flood fill.

    Args:
        input_path: Source image path.
        output_path: Destination path for processed image.
        color: Background color name or 'R,G,B' string.
        threshold: Color match threshold 0-255.
        smooth: Apply 1px edge feathering for cleaner cutlines.
        resize: Optional (width, height) to resize output.

    Returns:
        Result with stats about the operation.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    target_color = parse_color(color)
    img = Image.open(input_path).convert("RGBA")

    # Check if already transparent (no-op)
    data = list(img.get_flattened_data())
    initial_transparent = sum(1 for p in data if p[3] == 0)
    if initial_transparent == len(data):
        result = Result.from_image(img, output_path)
        result.warnings.append("Image is already fully transparent")
        os.makedirs(output_path.parent, exist_ok=True)
        img.save(output_path, "PNG")
        return result

    img, removed = flood_fill_from_edges(
        img, target_color=target_color, threshold=threshold
    )

    if smooth:
        img = smooth_edges(img, radius=1)

    if resize:
        img = img.resize(resize, Image.LANCZOS)

    os.makedirs(output_path.parent, exist_ok=True)
    img.save(output_path, "PNG")

    result = Result.from_image(img, output_path)
    result.metadata["pixels_removed"] = removed
    result.metadata["color"] = color
    result.metadata["threshold"] = threshold
    return result
