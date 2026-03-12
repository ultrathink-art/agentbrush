#!/usr/bin/env python3
"""Validate image against presets or custom specs.

Usage:
    python validate.py check image.png --preset social-og
    python validate.py check image.png --type sticker
    python validate.py check image.png --width 1200 --height 630
    python validate.py compare source.png processed.png --max-loss 10
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.validate.ops import validate_design, compare_images, ALL_PRESETS


def main():
    parser = argparse.ArgumentParser(description="Image validation")
    sub = parser.add_subparsers(dest="mode")

    p_check = sub.add_parser("check", help="Validate image file")
    p_check.add_argument("input", help="Image to validate")
    p_check.add_argument("--preset", default=None,
                         help="Preset: " + ", ".join(ALL_PRESETS.keys()))
    p_check.add_argument("--type", dest="product_type", default=None,
                         help="Product type (backward compat): "
                              "tshirt, hoodie, hat, mug, sticker, deskmat, poster, tote")
    p_check.add_argument("--width", type=int, default=None,
                         help="Expected width (custom spec)")
    p_check.add_argument("--height", type=int, default=None,
                         help="Expected height (custom spec)")
    p_check.add_argument("--transparent", action="store_true", default=None,
                         help="Require transparent background")

    p_compare = sub.add_parser("compare", help="Compare source vs processed for pixel loss")
    p_compare.add_argument("source", help="Original source image")
    p_compare.add_argument("processed", help="Processed image")
    p_compare.add_argument("--max-loss", type=float, default=10.0,
                           help="Max acceptable opaque pixel loss %%")

    args = parser.parse_args()
    if args.mode is None:
        parser.print_help()
        sys.exit(2)

    if args.mode == "check":
        transparent = True if args.transparent else None
        result = validate_design(
            args.input,
            product_type=args.product_type,
            preset=args.preset,
            width=args.width,
            height=args.height,
            transparent=transparent,
        )
    else:
        result = compare_images(args.source, args.processed, max_loss_pct=args.max_loss)

    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
