"""Text rendering on images via Pillow.

Uses Pillow for accurate text rendering — ImageMagick lacks Freetype.
Supports horizontal text only (curved/arc text is broken in Pillow).
Handles textbbox y-offset gotcha at large font sizes.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image, ImageDraw

from agentbrush.core.fonts import find_font
from agentbrush.core.result import Result


def add_text(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    text: str,
    position: Tuple[int, int] = (0, 0),
    font_name: str = "mono",
    font_size: int = 24,
    bold: bool = False,
    color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    anchor: str = "lt",
    max_width: Optional[int] = None,
    center: bool = False,
) -> Result:
    """Render text onto an image.

    Args:
        input_path: Source image path.
        output_path: Destination path.
        text: Text string to render.
        position: (x, y) pixel coordinates for text placement.
        font_name: Font alias or filename (see core.fonts).
        font_size: Font size in points.
        bold: Use bold variant if available.
        color: RGBA text color tuple.
        anchor: Pillow text anchor (e.g. 'lt'=left-top, 'mm'=middle-middle).
        max_width: Optional max width in pixels — text wraps to fit.
        center: Center text horizontally on canvas (Y from position is used).

    Returns:
        Result with operation stats.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    img = Image.open(input_path).convert("RGBA")
    font = find_font(font_name, size=font_size, bold=bold)

    # Create text overlay on transparent layer (preserves alpha compositing)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lines = _wrap_text(text, font, max_width, draw) if max_width else text.split("\n")

    # Render each line
    x, y = position
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    metadata = {"lines": len(lines), "font": font_name, "font_size": font_size}

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, anchor="lt")
        y_offset = bbox[1]
        if center:
            text_width = bbox[2] - bbox[0]
            lx = (img.width - text_width) // 2
        else:
            lx = x
        draw.text((lx, y - y_offset), line, font=font, fill=color, anchor="lt")
        y += line_height

    img = Image.alpha_composite(img, overlay)

    os.makedirs(output_path.parent, exist_ok=True)
    img.save(output_path, "PNG")

    result = Result.from_image(img, output_path)
    result.metadata = metadata
    return result


def render_text(
    width: int,
    height: int,
    output_path: Union[str, Path],
    text: str,
    font_name: str = "mono",
    font_size: int = 48,
    bold: bool = False,
    color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0),
    center: bool = True,
    max_width: Optional[int] = None,
) -> Result:
    """Render text on a new blank canvas.

    Args:
        width: Canvas width.
        height: Canvas height.
        output_path: Destination path.
        text: Text to render.
        font_name: Font alias or filename.
        font_size: Font size in points.
        bold: Use bold variant.
        color: RGBA text color.
        bg_color: RGBA background color (default: transparent).
        center: Center text both horizontally and vertically.
        max_width: Optional max width for text wrapping.

    Returns:
        Result with stats.
    """
    output_path = Path(output_path)
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    font = find_font(font_name, size=font_size, bold=bold)

    lines = _wrap_text(text, font, max_width, draw) if max_width else text.split("\n")
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    total_height = line_height * len(lines)

    if center:
        y = (height - total_height) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font, anchor="lt")
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y_offset = bbox[1]
            draw.text((x, y - y_offset), line, font=font, fill=color, anchor="lt")
            y += line_height
    else:
        x, y = 0, 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font, anchor="lt")
            y_offset = bbox[1]
            draw.text((x, y - y_offset), line, font=font, fill=color, anchor="lt")
            y += line_height

    os.makedirs(output_path.parent, exist_ok=True)
    img.save(output_path, "PNG")

    result = Result.from_image(img, output_path)
    result.metadata = {
        "lines": len(lines),
        "font": font_name,
        "font_size": font_size,
        "canvas": f"{width}x{height}",
    }
    return result


def _wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font, anchor="lt")
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]
