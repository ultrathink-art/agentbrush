"""Image resizing with aspect-ratio preservation and padding.

Supports exact resize, fit-within-bounds, and pad-to-dimensions.
Uses LANCZOS for high-quality downscaling.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.result import Result


def resize_image(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    fit: bool = False,
    pad: bool = False,
    pad_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
    resample: int = Image.LANCZOS,
) -> Result:
    """Resize an image with multiple strategies.

    Modes (in priority order):
    - scale: Multiply dimensions by factor (e.g. 2.0 for 2x).
    - fit + width/height: Scale to fit within bounds, preserving aspect ratio.
    - pad + width/height: Fit then pad to exact dimensions with pad_color.
    - width + height: Exact resize (may distort aspect ratio).
    - width only: Scale proportionally based on width.
    - height only: Scale proportionally based on height.

    Args:
        input_path: Source image path.
        output_path: Destination path.
        width: Target width in pixels.
        height: Target height in pixels.
        scale: Scale factor (e.g. 2.0, 0.5).
        fit: Fit within width x height, preserving aspect ratio.
        pad: Fit then pad to exact dimensions.
        pad_color: Padding color as RGBA (default: transparent).
        resample: Pillow resampling filter (default: LANCZOS).

    Returns:
        Result with operation stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    img = Image.open(input_path).convert("RGBA")
    orig_w, orig_h = img.size
    metadata = {"original_size": f"{orig_w}x{orig_h}"}

    if scale:
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img = img.resize((new_w, new_h), resample)
        metadata["mode"] = f"scale({scale}x)"
    elif (fit or pad) and width and height:
        ratio = min(width / orig_w, height / orig_h)
        new_w = int(orig_w * ratio)
        new_h = int(orig_h * ratio)
        img = img.resize((new_w, new_h), resample)
        metadata["mode"] = "fit" if not pad else "pad"
        if pad:
            canvas = Image.new("RGBA", (width, height), pad_color)
            x = (width - new_w) // 2
            y = (height - new_h) // 2
            canvas.paste(img, (x, y), img)
            img = canvas
            metadata["padding"] = f"{x},{y}"
    elif width and height:
        img = img.resize((width, height), resample)
        metadata["mode"] = "exact"
    elif width:
        ratio = width / orig_w
        new_h = int(orig_h * ratio)
        img = img.resize((width, new_h), resample)
        metadata["mode"] = "width-proportional"
    elif height:
        ratio = height / orig_h
        new_w = int(orig_w * ratio)
        img = img.resize((new_w, height), resample)
        metadata["mode"] = "height-proportional"
    else:
        return Result(errors=["No resize target specified (width, height, or scale)"])

    os.makedirs(output_path.parent, exist_ok=True)
    img.save(output_path, "PNG")

    result = Result.from_image(img, output_path)
    result.metadata = metadata
    return result
