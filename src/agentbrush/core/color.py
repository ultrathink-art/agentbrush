"""Color matching and parsing utilities."""
from __future__ import annotations

from typing import Tuple, Union

ColorTuple = Tuple[int, int, int]

NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "green": (0, 255, 0),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
}


def parse_color(color_str: str) -> ColorTuple:
    """Parse a color string into an RGB tuple.

    Accepts named colors ('black', 'white', 'green') or 'R,G,B' format.
    """
    lower = color_str.strip().lower()
    if lower in NAMED_COLORS:
        return NAMED_COLORS[lower]
    parts = [int(x.strip()) for x in color_str.split(",")]
    if len(parts) != 3:
        raise ValueError(
            f"Color must be a named color ({', '.join(NAMED_COLORS)}) "
            f"or 'R,G,B' format, got: {color_str!r}"
        )
    return (parts[0], parts[1], parts[2])


def is_near_color(
    pixel: Union[Tuple[int, ...], list],
    target: ColorTuple,
    threshold: int = 25,
) -> bool:
    """Check if pixel RGB is within threshold of target color.

    Works with both RGB and RGBA pixels (alpha ignored for matching).
    """
    return (
        abs(pixel[0] - target[0]) < threshold
        and abs(pixel[1] - target[1]) < threshold
        and abs(pixel[2] - target[2]) < threshold
    )


def is_green(
    pixel: Union[Tuple[int, ...], list],
    threshold: int = 50,
) -> bool:
    """Check if pixel is in the green-screen color family.

    Green screen pixels have: high G channel, low R, low B,
    with G significantly exceeding both R and B.
    """
    r, g, b = pixel[0], pixel[1], pixel[2]
    return g > 100 and (g - r) > threshold and (g - b) > threshold


def is_near_white(
    pixel: Union[Tuple[int, ...], list],
    threshold: int = 30,
) -> bool:
    """Check if pixel is near-white (all channels above 255 - threshold)."""
    r, g, b = pixel[0], pixel[1], pixel[2]
    limit = 255 - threshold
    return r > limit and g > limit and b > limit
