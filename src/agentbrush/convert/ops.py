"""Image format conversion with mode handling.

Converts between PNG, JPEG, WEBP, BMP, TIFF.
Handles RGBA → RGB conversion (with configurable background for transparency).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.result import Result

SUPPORTED_FORMATS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"}


def convert_image(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    output_format: Optional[str] = None,
    quality: int = 95,
    bg_color: Tuple[int, int, int] = (255, 255, 255),
    ensure_rgba: bool = False,
) -> Result:
    """Convert image between formats.

    Args:
        input_path: Source image.
        output_path: Destination path. Format inferred from extension if
            output_format is None.
        output_format: Explicit format override (e.g. 'PNG', 'JPEG').
        quality: JPEG/WEBP quality 1-100 (default: 95).
        bg_color: Background color for RGBA→RGB conversion (default: white).
        ensure_rgba: If True, convert output to RGBA mode regardless.

    Returns:
        Result with operation stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    # Determine output format
    if output_format is None:
        ext = output_path.suffix.lower().lstrip(".")
        if ext in ("jpg", "jpeg"):
            output_format = "JPEG"
        elif ext == "webp":
            output_format = "WEBP"
        elif ext == "bmp":
            output_format = "BMP"
        elif ext == "tiff":
            output_format = "TIFF"
        elif ext == "gif":
            output_format = "GIF"
        else:
            output_format = "PNG"

    img = Image.open(input_path)
    metadata = {
        "input_mode": img.mode,
        "output_format": output_format,
    }

    if ensure_rgba:
        img = img.convert("RGBA")
        metadata["converted_to"] = "RGBA"
    elif output_format in ("JPEG", "BMP") and img.mode in ("RGBA", "LA", "PA"):
        # JPEG/BMP don't support alpha — flatten onto background
        background = Image.new("RGB", img.size, bg_color)
        if img.mode == "RGBA":
            background.paste(img, mask=img.split()[3])
        else:
            img_rgba = img.convert("RGBA")
            background.paste(img_rgba, mask=img_rgba.split()[3])
        img = background
        metadata["alpha_flattened"] = True
        metadata["bg_color"] = f"{bg_color[0]},{bg_color[1]},{bg_color[2]}"
    elif output_format in ("JPEG", "BMP") and img.mode != "RGB":
        img = img.convert("RGB")

    os.makedirs(output_path.parent, exist_ok=True)

    save_kwargs = {}
    if output_format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality
    if output_format == "PNG":
        img = img.convert("RGBA") if img.mode not in ("RGBA", "RGB", "L", "P") else img

    img.save(output_path, output_format, **save_kwargs)

    # Build result from saved file
    saved = Image.open(output_path)
    result = Result(
        output_path=output_path,
        width=saved.width,
        height=saved.height,
    )
    result.metadata = metadata
    return result
