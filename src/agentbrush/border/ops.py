"""Border artifact erosion and edge halo removal.

Handles:
- White border erosion (AI generators often add unwanted white outlines)
- Green halo erosion (anti-aliased fringe after green screen removal)
- Alpha edge smoothing (Gaussian blur on edges, interior preserved)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

from PIL import Image

from agentbrush.core.alpha import smooth_alpha_edges
from agentbrush.core.result import Result


def _erode_white_border(
    img: Image.Image,
    passes: int = 15,
    threshold: int = 185,
) -> tuple:
    """Iteratively remove light pixels adjacent to transparent (border artifacts).

    Threshold < 170 eats into colored artwork. 185 is the safe default.
    """
    w, h = img.size
    pixels = img.load()
    total = 0

    for _ in range(passes):
        to_remove = []
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                if r > threshold and g > threshold and b > threshold:
                    adj_transparent = False
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            if pixels[nx, ny][3] == 0:
                                adj_transparent = True
                                break
                        else:
                            adj_transparent = True
                            break
                    if adj_transparent:
                        to_remove.append((x, y))
        for x, y in to_remove:
            pixels[x, y] = (0, 0, 0, 0)
        total += len(to_remove)
        if len(to_remove) == 0:
            break

    return img, total


def _erode_green_halo(
    img: Image.Image,
    passes: int = 20,
) -> tuple:
    """Remove green-tinted pixels adjacent to transparent (anti-alias fringe)."""
    w, h = img.size
    pixels = img.load()
    total = 0

    for _ in range(passes):
        to_remove = []
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                is_greenish = g > 80 and g > r * 1.2 and g > b * 1.2
                if not is_greenish:
                    continue
                adj_transparent = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if pixels[nx, ny][3] == 0:
                            adj_transparent = True
                            break
                    else:
                        adj_transparent = True
                        break
                if adj_transparent:
                    to_remove.append((x, y))
        for x, y in to_remove:
            pixels[x, y] = (0, 0, 0, 0)
        total += len(to_remove)
        if len(to_remove) == 0:
            break

    return img, total


def cleanup_border(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    passes: int = 15,
    threshold: int = 185,
    green_halo_passes: int = 0,
    alpha_smooth: bool = False,
    alpha_blur_radius: float = 1.5,
) -> Result:
    """Remove border artifacts: white edge erosion + optional green halo removal.

    Args:
        input_path: Source image path.
        output_path: Destination path.
        passes: Number of white border erosion passes.
        threshold: White pixel threshold (R,G,B all above this = white).
        green_halo_passes: Number of green halo erosion passes (0 to skip).
        alpha_smooth: Apply Gaussian alpha smoothing on edges.
        alpha_blur_radius: Blur radius for alpha smoothing.

    Returns:
        Result with operation stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    img = Image.open(input_path).convert("RGBA")
    metadata = {}

    img, white_removed = _erode_white_border(img, passes=passes, threshold=threshold)
    metadata["white_border_removed"] = white_removed

    if green_halo_passes > 0:
        img, green_removed = _erode_green_halo(img, passes=green_halo_passes)
        metadata["green_halo_removed"] = green_removed

    if alpha_smooth:
        img = smooth_alpha_edges(img, blur_radius=alpha_blur_radius)
        metadata["alpha_smoothed"] = True

    os.makedirs(output_path.parent, exist_ok=True)
    img.save(output_path, "PNG")

    result = Result.from_image(img, output_path)
    result.metadata = metadata
    return result
