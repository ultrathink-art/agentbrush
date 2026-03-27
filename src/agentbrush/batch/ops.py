"""Batch processing — apply operations to all images in a directory.

Supports running any agentbrush operation (remove-bg, resize, crop,
validate, etc.) across every image in an input directory, writing
results to an output directory.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from PIL import Image

from agentbrush.core.result import Result
from agentbrush.validate.ops import ALL_PRESETS, validate_design
from agentbrush.crop.ops import smart_crop
from agentbrush.resize.ops import resize_image
from agentbrush.background.ops import remove_background

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"}

OPERATIONS: Dict[str, Callable] = {
    "validate": None,
    "remove-bg": None,
    "crop": None,
    "resize": None,
}


def _find_images(input_dir: Path) -> List[Path]:
    """Find all image files in a directory (non-recursive)."""
    return sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def batch_process(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    operation: str = "validate",
    preset: Optional[str] = None,
    **kwargs,
) -> Result:
    """Process all images in a directory.

    Args:
        input_dir: Directory containing source images.
        output_dir: Directory for output images (created if needed).
        operation: Operation to apply: 'validate', 'remove-bg', 'crop', 'resize'.
        preset: Preset name for validate operation.
        **kwargs: Extra arguments passed to the operation function.

    Returns:
        Result with batch stats in metadata:
            - total: number of images found
            - processed: number successfully processed
            - failed: number that failed
            - results: per-file result summaries
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        return Result(errors=[f"Input directory not found: {input_dir}"])
    if not input_dir.is_dir():
        return Result(errors=[f"Not a directory: {input_dir}"])

    images = _find_images(input_dir)
    if not images:
        return Result(
            errors=[f"No images found in {input_dir}"],
            metadata={"total": 0},
        )

    os.makedirs(output_dir, exist_ok=True)

    processed = 0
    failed = 0
    file_results = []

    for img_path in images:
        out_path = output_dir / img_path.name

        if operation == "validate":
            r = validate_design(
                str(img_path),
                preset=preset,
                product_type=kwargs.get("product_type"),
            )
            if r.success:
                Image.open(img_path).save(out_path)
                r.output_path = out_path
        elif operation == "remove-bg":
            r = remove_background(
                str(img_path), str(out_path),
                color=kwargs.get("color", "black"),
                threshold=kwargs.get("threshold", 25),
            )
        elif operation == "crop":
            r = smart_crop(
                str(img_path), str(out_path),
                padding=kwargs.get("padding", 0),
            )
        elif operation == "resize":
            r = resize_image(
                str(img_path), str(out_path),
                width=kwargs.get("width"),
                height=kwargs.get("height"),
                scale=kwargs.get("scale"),
                fit=kwargs.get("fit", False),
                pad=kwargs.get("pad", False),
            )
        else:
            r = Result(errors=[f"Unknown operation: {operation}"])

        if r.success:
            processed += 1
        else:
            failed += 1

        file_results.append({
            "file": img_path.name,
            "success": r.success,
            "errors": r.errors,
            "warnings": r.warnings,
        })

    result = Result(
        output_path=output_dir,
        metadata={
            "total": len(images),
            "processed": processed,
            "failed": failed,
            "operation": operation,
            "results": file_results,
        },
    )
    if failed > 0:
        result.warnings.append(f"{failed}/{len(images)} images failed")
    return result
