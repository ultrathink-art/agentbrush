#!/usr/bin/env python3
"""Convert image format (PNG, JPEG, WEBP, etc.).

Usage:
    python convert.py input.png output.jpg
    python convert.py input.png output.webp --quality 90
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.convert.ops import convert_image


def main():
    parser = argparse.ArgumentParser(description="Image format conversion")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path (format inferred from extension)")
    parser.add_argument("--format", dest="output_format", help="Explicit format: PNG, JPEG, WEBP")
    parser.add_argument("--quality", type=int, default=95, help="JPEG/WEBP quality 1-100")
    parser.add_argument("--bg-color", default="255,255,255",
                         help="Background color for RGBA->RGB (default: white)")
    parser.add_argument("--ensure-rgba", action="store_true", help="Force RGBA output mode")
    args = parser.parse_args()

    bg_color = tuple(int(x) for x in args.bg_color.split(","))
    result = convert_image(
        args.input, args.output,
        output_format=args.output_format,
        quality=args.quality,
        bg_color=bg_color,
        ensure_rgba=args.ensure_rgba,
    )
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
