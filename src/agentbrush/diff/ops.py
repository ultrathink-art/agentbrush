"""Image comparison — diff two images and highlight changes.

Produces a visual diff image where unchanged pixels are dimmed and
changed pixels are highlighted in a configurable color. Useful for
before/after QA of image processing operations.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.result import Result


def diff_images(
    image_a_path: Union[str, Path],
    image_b_path: Union[str, Path],
    output_path: Union[str, Path],
    threshold: int = 10,
    highlight_color: Tuple[int, int, int, int] = (255, 0, 0, 255),
    dim_factor: float = 0.3,
) -> Result:
    """Generate a visual diff between two images.

    Pixels that differ by more than threshold (per-channel) are highlighted.
    Unchanged pixels are dimmed. Output shows where changes occurred.

    If images differ in size, both are compared at the smaller common
    region; extra area is marked as changed.

    Args:
        image_a_path: First image (typically 'before').
        image_b_path: Second image (typically 'after').
        output_path: Path for the diff output image.
        threshold: Per-channel difference threshold (0-255, default: 10).
        highlight_color: RGBA color for changed pixels (default: red).
        dim_factor: Brightness factor for unchanged pixels (0-1, default: 0.3).

    Returns:
        Result with diff stats in metadata:
            - changed_pixels: number of pixels that differ
            - total_pixels: total pixels compared
            - changed_pct: percentage of changed pixels
            - size_match: whether images had same dimensions
    """
    image_a_path = Path(image_a_path)
    image_b_path = Path(image_b_path)
    output_path = Path(output_path)

    for p in [image_a_path, image_b_path]:
        if not p.exists():
            return Result(errors=[f"File not found: {p}"])

    img_a = Image.open(image_a_path).convert("RGBA")
    img_b = Image.open(image_b_path).convert("RGBA")

    size_match = img_a.size == img_b.size
    out_w = max(img_a.width, img_b.width)
    out_h = max(img_a.height, img_b.height)
    common_w = min(img_a.width, img_b.width)
    common_h = min(img_a.height, img_b.height)

    diff_img = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 255))
    diff_pixels = diff_img.load()
    a_pixels = img_a.load()
    b_pixels = img_b.load()

    changed_count = 0
    total = out_w * out_h

    for y in range(out_h):
        for x in range(out_w):
            if x >= common_w or y >= common_h:
                diff_pixels[x, y] = highlight_color
                changed_count += 1
                continue

            ra, ga, ba, aa = a_pixels[x, y]
            rb, gb, bb, ab = b_pixels[x, y]

            dr = abs(ra - rb)
            dg = abs(ga - gb)
            db = abs(ba - bb)
            da = abs(aa - ab)

            if dr > threshold or dg > threshold or db > threshold or da > threshold:
                diff_pixels[x, y] = highlight_color
                changed_count += 1
            else:
                dim_r = int(ra * dim_factor)
                dim_g = int(ga * dim_factor)
                dim_b = int(ba * dim_factor)
                diff_pixels[x, y] = (dim_r, dim_g, dim_b, 255)

    os.makedirs(output_path.parent, exist_ok=True)
    diff_img.save(output_path, "PNG")

    changed_pct = round(100.0 * changed_count / total, 1) if total > 0 else 0.0

    result = Result(
        output_path=output_path,
        width=out_w,
        height=out_h,
    )
    result.metadata = {
        "changed_pixels": changed_count,
        "total_pixels": total,
        "changed_pct": changed_pct,
        "size_match": size_match,
        "threshold": threshold,
    }

    if changed_pct > 50:
        result.warnings.append(
            f"High difference: {changed_pct}% of pixels changed"
        )

    return result
