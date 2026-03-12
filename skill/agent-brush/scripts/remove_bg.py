#!/usr/bin/env python3
"""Remove solid-color background via edge-based flood fill.

Usage:
    python remove_bg.py input.png output.png [--color black] [--threshold 25] [--smooth]
"""
import argparse
import sys
import os

# Auto-detect src/ for standalone usage (no pip install needed)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.background.ops import remove_background


def main():
    parser = argparse.ArgumentParser(description="Remove background via edge-based flood fill")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--color", default="black", help="Background color (default: black)")
    parser.add_argument("--threshold", type=int, default=25, help="Color match threshold 0-255")
    parser.add_argument("--smooth", action="store_true", help="Apply 1px edge feathering")
    parser.add_argument("--resize", help="Resize output: WxH (e.g. 1664x1664)")
    args = parser.parse_args()

    resize = None
    if args.resize:
        w, h = args.resize.lower().split("x")
        resize = (int(w), int(h))

    result = remove_background(
        args.input, args.output,
        color=args.color, threshold=args.threshold,
        smooth=args.smooth, resize=resize,
    )
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
