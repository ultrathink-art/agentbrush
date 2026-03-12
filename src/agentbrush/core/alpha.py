"""Alpha channel operations: edge smoothing, feathering."""
from __future__ import annotations

from PIL import Image, ImageFilter


def smooth_edges(img: Image.Image, radius: int = 1) -> Image.Image:
    """Soften hard edges between transparent and opaque pixels.

    Reduces alpha by 40 on opaque pixels adjacent to transparent ones.
    Preserves fully interior pixels.
    """
    width, height = img.size
    pixels = img.load()
    result = img.copy()
    result_pixels = result.load()

    for x in range(width):
        for y in range(height):
            if pixels[x, y][3] > 0:
                has_transparent = False
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if pixels[nx, ny][3] == 0:
                                has_transparent = True
                                break
                    if has_transparent:
                        break
                if has_transparent:
                    r, g, b, a = pixels[x, y]
                    result_pixels[x, y] = (r, g, b, max(0, a - 40))

    return result


def smooth_alpha_edges(
    img: Image.Image,
    blur_radius: float = 1.5,
) -> Image.Image:
    """Gaussian blur on alpha channel for smooth die-cut outline.

    Interior pixels (alpha > 220) are preserved unchanged.
    Edge pixels get smoothed alpha. Near-transparent pixels (<= 15) are zeroed.
    """
    r, g, b, a = img.split()
    a_smooth = a.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    a_data = list(a.getdata())
    a_smooth_data = list(a_smooth.getdata())

    a_result = []
    for orig, smooth in zip(a_data, a_smooth_data):
        if orig > 220:
            a_result.append(orig)
        elif orig > 15:
            a_result.append(min(orig, smooth))
        else:
            a_result.append(0)

    a_new = Image.new("L", img.size)
    a_new.putdata(a_result)
    return Image.merge("RGBA", (r, g, b, a_new))
