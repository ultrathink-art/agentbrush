#!/usr/bin/env python3
"""Resize image with aspect-ratio preservation and padding.

Usage:
    python resize.py input.png output.png --width 4500 --height 5400
    python resize.py input.png output.png --scale 2.0
    python resize.py input.png output.png --width 2700 --height 1050 --fit
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.resize.ops import resize_image


def main():
    parser = argparse.ArgumentParser(description="Resize image")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--width", type=int, help="Target width")
    parser.add_argument("--height", type=int, help="Target height")
    parser.add_argument("--scale", type=float, help="Scale factor (e.g. 2.0)")
    parser.add_argument("--fit", action="store_true", help="Fit within bounds, preserve aspect")
    parser.add_argument("--pad", action="store_true", help="Fit then pad to exact dimensions")
    parser.add_argument("--pad-color", default="0,0,0,0", help="Padding RGBA color")
    args = parser.parse_args()

    pad_color = tuple(int(x) for x in args.pad_color.split(","))
    result = resize_image(
        args.input, args.output,
        width=args.width, height=args.height,
        scale=args.scale, fit=args.fit,
        pad=args.pad, pad_color=pad_color,
    )
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
