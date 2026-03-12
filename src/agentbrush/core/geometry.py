"""Geometric operations: bounds detection, cropping, centroid."""
from __future__ import annotations

from typing import Optional, Tuple

from PIL import Image


def find_artwork_bounds(
    img: Image.Image,
    alpha_threshold: int = 20,
) -> Tuple[int, int, int, int]:
    """Find bounding box of opaque pixels.

    Returns (min_x, min_y, max_x+1, max_y+1) — suitable for img.crop().
    Returns (0, 0, width, height) if no opaque pixels found.
    """
    w, h = img.size
    pixels = img.load()
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    found = False

    for y in range(h):
        for x in range(w):
            if pixels[x, y][3] > alpha_threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                found = True

    if not found:
        return (0, 0, w, h)
    return (min_x, min_y, max_x + 1, max_y + 1)


def crop_to_content(
    img: Image.Image,
    padding: int = 0,
    alpha_threshold: int = 20,
) -> Image.Image:
    """Crop image to bounding box of opaque content, with optional padding."""
    x1, y1, x2, y2 = find_artwork_bounds(img, alpha_threshold)
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(img.width, x2 + padding)
    y2 = min(img.height, y2 + padding)
    return img.crop((x1, y1, x2, y2))


def find_opaque_centroid(
    img: Image.Image,
    region: Optional[Tuple[int, int, int, int]] = None,
    alpha_threshold: int = 50,
) -> Tuple[int, int]:
    """Find centroid of opaque pixels within a region.

    Args:
        img: RGBA image.
        region: Optional (x1, y1, x2, y2) bounding box. Defaults to full image.
        alpha_threshold: Minimum alpha to count as opaque.

    Returns:
        (cx, cy) centroid coordinates. Falls back to region center if no pixels found.
    """
    if region is None:
        x1, y1, x2, y2 = 0, 0, img.width, img.height
    else:
        x1, y1, x2, y2 = region

    pixels = img.load()
    total_x, total_y, count = 0, 0, 0

    for y in range(max(0, y1), min(img.height, y2)):
        for x in range(max(0, x1), min(img.width, x2)):
            if pixels[x, y][3] > alpha_threshold:
                total_x += x
                total_y += y
                count += 1

    if count == 0:
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return (total_x // count, total_y // count)
