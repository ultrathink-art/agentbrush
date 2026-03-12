"""Design validation — Python port of bin/design-qa.

Validates design files against product specs: dimensions, transparency,
aspect ratio, visual complexity (sticker slop gate), layout detection.
No external dependencies (ImageMagick, tesseract) — pure Pillow.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from PIL import Image

from agentbrush.core.result import Result


PRODUCT_SPECS: Dict[str, Dict] = {
    "tshirt": {
        "width": 4500, "height": 5400, "transparent": True,
        "apparel": True, "tolerance": 500,
        "aspect_min": 0.7, "aspect_max": 1.2,
    },
    "hoodie": {
        "width": 4500, "height": 5400, "transparent": True,
        "apparel": True, "tolerance": 500,
        "aspect_min": 0.7, "aspect_max": 1.2,
    },
    "hat": {
        "width": 1890, "height": 765, "transparent": True,
        "apparel": True, "tolerance": 200,
        "aspect_min": 1.5,
    },
    "mug": {
        "width": 2700, "height": 1050, "transparent": True,
        "tolerance": 100, "aspect_min": 2.0,
    },
    "sticker": {
        "width": 1664, "height": 1664, "transparent": True,
        "tolerance": 500,
        "aspect_min": 0.9, "aspect_max": 1.1,
    },
    "deskmat": {
        "width": 9200, "height": 4500, "transparent": False,
        "tolerance": 500,
        "aspect_min": 1.8, "aspect_max": 2.3,
    },
    "poster": {
        "width": 5400, "height": 7200, "transparent": False,
        "tolerance": 500,
        "aspect_min": 0.65, "aspect_max": 0.85,
    },
    "tote": {
        "width": 3900, "height": 4800, "transparent": True,
        "apparel": True, "tolerance": 500,
        "aspect_min": 0.7, "aspect_max": 0.95,
    },
}

# Filename patterns for auto-detection
_TYPE_PATTERNS = {
    "tshirt": ["tee", "shirt", "tshirt"],
    "hoodie": ["hoodie"],
    "hat": ["hat", "cap"],
    "mug": ["mug", "cup"],
    "sticker": ["sticker"],
    "deskmat": ["deskmat", "desk_mat", "desk-mat", "mousepad"],
    "poster": ["poster"],
    "tote": ["tote"],
}


def detect_product_type(filename: str) -> Optional[str]:
    """Auto-detect product type from filename."""
    lower = filename.lower()
    for ptype, patterns in _TYPE_PATTERNS.items():
        for pat in patterns:
            if pat in lower:
                return ptype
    return None


def validate_design(
    input_path: Union[str, Path],
    product_type: Optional[str] = None,
) -> Result:
    """Validate a design file against product specs.

    Checks: dimensions, aspect ratio, transparency, visual complexity
    (stickers), sticker layout (poster-layout detection).

    Args:
        input_path: Image file to validate.
        product_type: Product type (auto-detected from filename if omitted).

    Returns:
        Result with errors/warnings. success=True means design is acceptable.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        return Result(errors=[f"File not found: {input_path}"])

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    if product_type is None:
        product_type = detect_product_type(input_path.name)

    result = Result(
        output_path=input_path,
        width=w,
        height=h,
    )
    result.metadata["product_type"] = product_type or "unknown"
    result.metadata["dimensions"] = f"{w}x{h}"

    # Compute transparency stats
    pixels = img.load()
    total = w * h
    transparent_count = 0
    step = max(1, w // 200)
    sampled = 0
    for x in range(0, w, step):
        for y in range(0, h, step):
            sampled += 1
            if pixels[x, y][3] == 0:
                transparent_count += 1
    trans_pct = (transparent_count * 100.0 / sampled) if sampled > 0 else 0
    result.transparent_pct = trans_pct
    result.opaque_pct = 100.0 - trans_pct

    spec = PRODUCT_SPECS.get(product_type) if product_type else None
    if spec is None:
        if product_type is None:
            result.warnings.append(
                "Could not detect product type from filename. "
                "Specify product_type parameter."
            )
        return result

    aspect = w / h if h > 0 else 0

    # Aspect ratio checks
    aspect_min = spec.get("aspect_min")
    aspect_max = spec.get("aspect_max")
    if aspect_min and aspect < aspect_min:
        result.errors.append(
            f"ASPECT RATIO: Image too tall/narrow ({aspect:.2f}). "
            f"{product_type} needs >= {aspect_min}:1"
        )
    if aspect_max and aspect > aspect_max:
        result.errors.append(
            f"ASPECT RATIO: Image too wide ({aspect:.2f}). "
            f"{product_type} needs <= {aspect_max}:1"
        )

    # Dimension tolerance check
    tol = spec.get("tolerance", 500)
    if abs(w - spec["width"]) > tol or abs(h - spec["height"]) > tol:
        result.warnings.append(
            f"DIMENSIONS: {w}x{h} differs from recommended "
            f"{spec['width']}x{spec['height']} (tolerance: +/-{tol}px)"
        )

    # Transparency check
    if spec.get("transparent"):
        has_transparency = trans_pct > 1.0
        if not has_transparency:
            if spec.get("apparel"):
                result.errors.append(
                    "TRANSPARENCY: Apparel designs MUST have transparent "
                    "backgrounds (not solid rectangles)"
                )
            else:
                result.warnings.append(
                    "TRANSPARENCY: Image may not have transparent areas"
                )
        else:
            # Check internal transparency holes for apparel
            if spec.get("apparel"):
                _check_interior_holes(img, result)

    # Resolution check
    if w < 1000 or h < 1000:
        result.warnings.append(
            f"RESOLUTION: Low resolution ({w}x{h}). "
            "May appear pixelated in print."
        )

    # Sticker-specific checks
    if product_type == "sticker":
        _check_visual_complexity(img, result)
        _check_sticker_layout(img, result)

    return result


def _check_interior_holes(img: Image.Image, result: Result):
    """Detect internal transparency caused by threshold-based bg removal."""
    w, h = img.size
    pixels = img.load()
    x_start, x_end = int(w * 0.2), int(w * 0.8)
    y_start, y_end = int(h * 0.2), int(h * 0.8)
    step = max(1, (x_end - x_start) // 40)
    total = 0
    transparent = 0
    for x in range(x_start, x_end, step):
        for y in range(y_start, y_end, step):
            total += 1
            if pixels[x, y][3] == 0:
                transparent += 1
    pct = (transparent * 100) // total if total > 0 else 0
    result.metadata["interior_transparency_pct"] = pct
    if 15 < pct < 85:
        result.warnings.append(
            f"INTERNAL HOLES: {pct}% of artwork interior is transparent. "
            "Possible threshold-based bg removal damage."
        )


def _check_visual_complexity(img: Image.Image, result: Result):
    """Detect text-only slop: low color variety + low edge density."""
    w, h = img.size
    pixels = img.load()

    color_set = set()
    step = max(1, w // 100)
    for x in range(0, w, step):
        for y in range(0, h, step):
            r, g, b, a = pixels[x, y]
            if a > 128:
                color_set.add((r // 8, g // 8, b // 8))

    edge_count = 0
    sample_count = 0
    step2 = max(2, w // 80)
    for x in range(step2, w - step2, step2):
        for y in range(step2, h - step2, step2):
            r1, g1, b1, a1 = pixels[x, y]
            r2, g2, b2, a2 = pixels[x + step2, y]
            r3, g3, b3, a3 = pixels[x, y + step2]
            if a1 > 128 and a2 > 128 and a3 > 128:
                sample_count += 1
                dx = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
                dy = abs(r1 - r3) + abs(g1 - g3) + abs(b1 - b3)
                if dx > 30 or dy > 30:
                    edge_count += 1

    edge_pct = (edge_count * 100) // sample_count if sample_count > 0 else 0
    colors = len(color_set)

    result.metadata["color_buckets"] = colors
    result.metadata["edge_density_pct"] = edge_pct

    if colors < 25 and edge_pct < 8:
        result.warnings.append(
            f"SLOP WARNING: Very low visual complexity ({colors} colors, "
            f"{edge_pct}% edges). Likely text-only flat design."
        )
    elif colors < 40 and edge_pct < 12:
        result.warnings.append(
            f"LOW COMPLEXITY: Design may be too simple ({colors} colors, "
            f"{edge_pct}% edges)."
        )


def _check_sticker_layout(img: Image.Image, result: Result):
    """Detect poster-layout stickers (rectangular bg = hard fail)."""
    w, h = img.size
    pixels = img.load()

    # 1. Opaque fill ratio
    step = max(1, w // 200)
    sampled = 0
    opaque = 0
    for x in range(0, w, step):
        for y in range(0, h, step):
            sampled += 1
            if pixels[x, y][3] > 20:
                opaque += 1
    fill_pct = (opaque * 100) // sampled if sampled > 0 else 0

    # 2. Rectangularity — consistency of row widths
    col_y_start = int(h * 0.10)
    col_y_end = int(h * 0.90)
    row_step = max(1, h // 50)
    row_widths = []
    for y in range(col_y_start, col_y_end, row_step):
        left = -1
        right = -1
        for x in range(w):
            if pixels[x, y][3] > 20:
                if left == -1:
                    left = x
                right = x
        if left >= 0:
            row_widths.append(right - left)

    rect_score = 0
    if len(row_widths) >= 5:
        avg_w = sum(row_widths) / len(row_widths)
        if avg_w > 0:
            variance = sum((rw - avg_w) ** 2 for rw in row_widths) / len(row_widths)
            std_dev = variance ** 0.5
            coeff_var = (std_dev / avg_w) * 100
            rect_score = 100 - min(100, int(coeff_var * 5))

    result.metadata["fill_pct"] = fill_pct
    result.metadata["rect_score"] = rect_score

    # Hard fail: poster layout
    if fill_pct > 70 and rect_score > 75:
        result.errors.append(
            f"POSTER LAYOUT DETECTED: Sticker has rectangular background "
            f"({fill_pct}% fill, {rect_score}% rect). "
            "Die-cut stickers must be cut to illustration shape on "
            "transparent background."
        )
    elif fill_pct > 65 and rect_score > 70:
        result.warnings.append(
            f"POSSIBLE POSTER LAYOUT: High fill ({fill_pct}%) and "
            f"rectangular shape ({rect_score}% rect)."
        )


def compare_images(
    source_path: Union[str, Path],
    processed_path: Union[str, Path],
    max_loss_pct: float = 10.0,
) -> Result:
    """Compare source vs processed image for opaque pixel loss.

    Used after background removal to verify artwork wasn't damaged.

    Args:
        source_path: Original image before processing.
        processed_path: Processed image after bg removal.
        max_loss_pct: Maximum acceptable opaque pixel loss (default: 10%).

    Returns:
        Result with loss percentage in metadata. Errors if loss > max_loss_pct.
    """
    source_path = Path(source_path)
    processed_path = Path(processed_path)

    for p in [source_path, processed_path]:
        if not p.exists():
            return Result(errors=[f"File not found: {p}"])

    src = Image.open(source_path).convert("RGBA")
    proc = Image.open(processed_path).convert("RGBA")

    src_opaque = sum(1 for p in src.get_flattened_data() if p[3] > 128)
    proc_opaque = sum(1 for p in proc.get_flattened_data() if p[3] > 128)

    loss_pct = ((src_opaque - proc_opaque) * 100) // src_opaque if src_opaque > 0 else 0

    result = Result(
        output_path=processed_path,
        width=proc.width,
        height=proc.height,
    )
    result.metadata = {
        "source_opaque": src_opaque,
        "processed_opaque": proc_opaque,
        "loss_pct": loss_pct,
    }

    if loss_pct > max_loss_pct:
        result.errors.append(
            f"Opaque pixel loss {loss_pct}% exceeds threshold {max_loss_pct}%. "
            "Likely threshold-based removal destroyed artwork details."
        )
    elif loss_pct > max_loss_pct / 2:
        result.warnings.append(
            f"Opaque pixel loss {loss_pct}% — verify artwork integrity"
        )

    return result
