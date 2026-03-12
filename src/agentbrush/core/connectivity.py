"""Die-cut connectivity: single shape verification via 8-connected BFS."""
from __future__ import annotations

from collections import deque
from typing import List, Tuple

from PIL import Image


def count_components(
    img: Image.Image,
    alpha_threshold: int = 20,
) -> List[int]:
    """Count connected components of opaque pixels (8-connected).

    Returns list of component sizes sorted descending (largest first).
    """
    w, h = img.size
    pixels = img.load()
    visited = set()
    sizes = []

    for y in range(h):
        for x in range(w):
            if pixels[x, y][3] > alpha_threshold and (x, y) not in visited:
                size = 0
                q = deque([(x, y)])
                visited.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    size += 1
                    for dx, dy in [
                        (-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (1, -1), (-1, 1), (1, 1),
                    ]:
                        nx, ny = cx + dx, cy + dy
                        if (
                            0 <= nx < w
                            and 0 <= ny < h
                            and (nx, ny) not in visited
                            and pixels[nx, ny][3] > alpha_threshold
                        ):
                            visited.add((nx, ny))
                            q.append((nx, ny))
                sizes.append(size)

    sizes.sort(reverse=True)
    return sizes


def ensure_single_shape(
    img: Image.Image,
    alpha_threshold: int = 20,
) -> Tuple[Image.Image, int]:
    """Keep only the largest connected component (8-connected).

    Removes all floating/detached elements. Essential for die-cut stickers
    where the cutting machine follows a single outline.

    Returns:
        Tuple of (modified image, number of pixels removed).
    """
    w, h = img.size
    pixels = img.load()
    visited = set()
    components = []

    for y in range(h):
        for x in range(w):
            if pixels[x, y][3] > alpha_threshold and (x, y) not in visited:
                comp = []
                q = deque([(x, y)])
                visited.add((x, y))
                while q:
                    cx, cy = q.popleft()
                    comp.append((cx, cy))
                    for dx, dy in [
                        (-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (1, -1), (-1, 1), (1, 1),
                    ]:
                        nx, ny = cx + dx, cy + dy
                        if (
                            0 <= nx < w
                            and 0 <= ny < h
                            and (nx, ny) not in visited
                            and pixels[nx, ny][3] > alpha_threshold
                        ):
                            visited.add((nx, ny))
                            q.append((nx, ny))
                components.append(comp)

    if not components:
        return img, 0

    components.sort(key=len, reverse=True)
    removed = 0
    for comp in components[1:]:
        for px_x, px_y in comp:
            pixels[px_x, px_y] = (0, 0, 0, 0)
            removed += 1

    return img, removed
