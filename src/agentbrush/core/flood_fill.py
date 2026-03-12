"""Edge-seeded BFS flood fill for background removal.

NEVER use threshold-based removal (destroys internal details).
This module implements edge-based flood fill: only pixels connected
to the image border are removed.
"""
from __future__ import annotations

from collections import deque
from typing import Callable, Optional, Tuple, Union

from PIL import Image

from agentbrush.core.color import ColorTuple, is_near_color


def flood_fill_from_edges(
    img: Image.Image,
    color_test_fn: Optional[Callable] = None,
    target_color: Optional[ColorTuple] = None,
    threshold: int = 25,
    connectivity: int = 4,
) -> Tuple[Image.Image, int]:
    """Remove background via BFS flood fill seeded from image edges.

    Only removes pixels that are:
    1. Matched by color_test_fn (or near target_color) AND
    2. Connected to the image border via other matching pixels

    Args:
        img: RGBA Pillow image.
        color_test_fn: Optional callable(pixel) -> bool. If provided,
            used instead of target_color/threshold.
        target_color: RGB tuple for color matching (used if color_test_fn is None).
        threshold: Color match threshold (used with target_color).
        connectivity: 4 or 8 connected neighbors.

    Returns:
        Tuple of (modified image, number of pixels removed).
    """
    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    if color_test_fn is None:
        if target_color is None:
            target_color = (0, 0, 0)

        def color_test_fn(px):
            return is_near_color(px, target_color, threshold)

    neighbors_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors_8 = neighbors_4 + [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    neighbors = neighbors_8 if connectivity == 8 else neighbors_4

    visited = set()
    queue = deque()

    # Seed from edge pixels matching the color test
    for x in range(width):
        for y in [0, height - 1]:
            if color_test_fn(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))
    for y in range(1, height - 1):
        for x in [0, width - 1]:
            if color_test_fn(pixels[x, y]) and (x, y) not in visited:
                queue.append((x, y))
                visited.add((x, y))

    # BFS
    while queue:
        x, y = queue.popleft()
        pixels[x, y] = (0, 0, 0, 0)
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                if color_test_fn(pixels[nx, ny]):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return img, len(visited)
