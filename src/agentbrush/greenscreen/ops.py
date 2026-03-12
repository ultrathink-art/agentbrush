"""Green screen removal: two-pass flood fill + color sweep pipeline.

Three-pass approach:
  1. Edge flood fill (removes background green connected to borders)
  2. Color-targeted sweep (removes remaining trapped green patches)
  3. Post-upscale sweep (anti-aliased green fringe from LANCZOS upscale)

Handles pre-transparent images (OpenAI sometimes pre-removes green).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image

from agentbrush.core.alpha import smooth_edges
from agentbrush.core.color import is_green
from agentbrush.core.flood_fill import flood_fill_from_edges
from agentbrush.core.result import Result


def _sweep_remaining_green(
    img: Image.Image,
    threshold: int = 50,
    passes: int = 3,
) -> Tuple[Image.Image, int]:
    """Remove trapped green patches not reached by flood fill."""
    w, h = img.size
    pixels = img.load()
    total_removed = 0

    for _ in range(passes):
        removed = 0
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue
                if is_green((r, g, b), threshold=threshold):
                    pixels[x, y] = (0, 0, 0, 0)
                    removed += 1
        total_removed += removed
        if removed == 0:
            break

    return img, total_removed


def _is_pre_transparent(img: Image.Image, min_transparent_pct: float = 10.0) -> bool:
    """Detect if OpenAI pre-removed the green screen (returns RGBA with alpha=0)."""
    data = list(img.get_flattened_data())
    total = len(data)
    transparent = sum(1 for p in data if p[3] == 0)
    return (100.0 * transparent / total) > min_transparent_pct if total else False


def remove_greenscreen(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    green_target: Tuple[int, int, int] = (24, 242, 41),
    flood_threshold: int = 60,
    sweep_threshold: int = 50,
    halo_passes: int = 0,
    upscale: Optional[int] = None,
    smooth: bool = True,
) -> Result:
    """Remove green screen background with multi-pass pipeline.

    Args:
        input_path: Source image path.
        output_path: Destination path.
        green_target: RGB target for flood fill (default: bright green).
        flood_threshold: Threshold for flood fill color matching.
        sweep_threshold: Threshold for green sweep pass.
        halo_passes: Number of green halo erosion passes (0 to skip).
        upscale: Optional upscale factor (e.g. 3 for 3x).
        smooth: Apply edge smoothing after removal.

    Returns:
        Result with operation stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    img = Image.open(input_path).convert("RGBA")
    metadata = {}

    # Detect pre-transparent images
    pre_transparent = _is_pre_transparent(img)
    metadata["pre_transparent"] = pre_transparent

    if pre_transparent:
        # Skip flood fill, just sweep + halo
        metadata["flood_fill_removed"] = 0
    else:
        # Pass 1: Edge flood fill
        img, flood_removed = flood_fill_from_edges(
            img,
            target_color=green_target,
            threshold=flood_threshold,
            connectivity=4,
        )
        metadata["flood_fill_removed"] = flood_removed

    # Pass 2: Sweep trapped green patches
    img, sweep_removed = _sweep_remaining_green(img, threshold=sweep_threshold)
    metadata["sweep_removed"] = sweep_removed

    if smooth:
        img = smooth_edges(img, radius=1)

    if upscale and upscale > 1:
        new_w = img.width * upscale
        new_h = img.height * upscale
        img = img.resize((new_w, new_h), Image.LANCZOS)
        metadata["upscaled_to"] = f"{new_w}x{new_h}"

        # Pass 3: Post-upscale sweep (LANCZOS creates green fringe)
        img, post_sweep = _sweep_remaining_green(img, threshold=sweep_threshold)
        metadata["post_upscale_sweep_removed"] = post_sweep

    os.makedirs(output_path.parent, exist_ok=True)
    img.save(output_path, "PNG")

    result = Result.from_image(img, output_path)
    result.metadata = metadata
    return result
