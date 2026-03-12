#!/usr/bin/env python3
"""Validate design against product specs.

Usage:
    python validate.py check design.png --type sticker
    python validate.py compare source.png processed.png --max-loss 10
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.validate.ops import validate_design, compare_images


def main():
    parser = argparse.ArgumentParser(description="Design validation")
    sub = parser.add_subparsers(dest="mode")

    p_check = sub.add_parser("check", help="Validate design file")
    p_check.add_argument("input", help="Image to validate")
    p_check.add_argument("--type", dest="product_type", default=None,
                         help="Product type: tshirt, hoodie, hat, mug, sticker, deskmat, poster, tote")

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
        result = validate_design(args.input, product_type=args.product_type)
    else:
        result = compare_images(args.source, args.processed, max_loss_pct=args.max_loss)

    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
