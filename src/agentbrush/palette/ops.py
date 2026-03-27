"""Color palette extraction — analyze image and output dominant colors.

Uses Pillow's quantize() for accurate color clustering without external
dependencies. Supports JSON, text, and hex output formats.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from PIL import Image

from agentbrush.core.result import Result


def extract_palette(
    input_path: Union[str, Path],
    count: int = 6,
    ignore_transparent: bool = True,
    min_alpha: int = 128,
) -> Result:
    """Extract dominant colors from an image.

    Uses Pillow's median-cut quantization to find the most prominent
    colors. Transparent/semi-transparent pixels are excluded by default.

    Args:
        input_path: Source image path.
        count: Number of colors to extract (default: 6).
        ignore_transparent: Skip pixels with alpha < min_alpha (default: True).
        min_alpha: Alpha threshold for pixel inclusion (default: 128).

    Returns:
        Result with palette data in metadata:
            - colors: list of {r, g, b, hex, pct} dicts
            - total_sampled: number of pixels analyzed
    """
    input_path = Path(input_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    if count < 1 or count > 64:
        return Result(errors=[f"Color count must be 1-64, got {count}"])

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    pixels = img.load()

    opaque_pixels = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if not ignore_transparent or a >= min_alpha:
                opaque_pixels.append((r, g, b))

    if not opaque_pixels:
        result = Result(output_path=input_path, width=w, height=h)
        result.metadata = {"colors": [], "total_sampled": 0}
        result.warnings.append("No opaque pixels found")
        return result

    rgb_img = Image.new("RGB", (len(opaque_pixels), 1))
    rgb_img.putdata(opaque_pixels)

    quantized = rgb_img.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    quantized_rgb = quantized.convert("RGB")
    color_counts: Dict[Tuple[int, int, int], int] = {}
    for pixel in quantized_rgb.get_flattened_data():
        rgb = (pixel[0], pixel[1], pixel[2])
        color_counts[rgb] = color_counts.get(rgb, 0) + 1

    total = len(opaque_pixels)
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

    colors = []
    for (r, g, b), cnt in sorted_colors[:count]:
        pct = round(100.0 * cnt / total, 1)
        hex_val = f"#{r:02x}{g:02x}{b:02x}"
        colors.append({
            "r": r, "g": g, "b": b,
            "hex": hex_val,
            "pct": pct,
        })

    result = Result(output_path=input_path, width=w, height=h)
    result.metadata = {
        "colors": colors,
        "total_sampled": total,
    }
    return result


def format_palette(result: Result, fmt: str = "json") -> str:
    """Format palette result for output.

    Args:
        result: Result from extract_palette().
        fmt: Output format — 'json', 'text', or 'hex'.

    Returns:
        Formatted string.
    """
    colors = result.metadata.get("colors", [])

    if fmt == "json":
        return json.dumps({"colors": colors}, indent=2)
    elif fmt == "hex":
        return "\n".join(c["hex"] for c in colors)
    else:
        lines = []
        for c in colors:
            lines.append(
                f"{c['hex']}  rgb({c['r']},{c['g']},{c['b']})  {c['pct']}%"
            )
        return "\n".join(lines)
