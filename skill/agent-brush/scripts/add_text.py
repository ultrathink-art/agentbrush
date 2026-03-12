#!/usr/bin/env python3
"""Render text onto an image or new canvas.

Usage:
    python add_text.py add input.png output.png --text "HELLO" --font mono-bold --size 72
    python add_text.py render output.png --width 1664 --height 1664 --text "TEXT" --center
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.text.ops import add_text, render_text


def _parse_color(s):
    parts = [int(x) for x in s.split(",")]
    if len(parts) == 3:
        parts.append(255)
    return tuple(parts)


def main():
    parser = argparse.ArgumentParser(description="Text rendering")
    sub = parser.add_subparsers(dest="mode")

    # add mode
    p_add = sub.add_parser("add", help="Add text to existing image")
    p_add.add_argument("input", help="Input image path")
    p_add.add_argument("output", help="Output image path")
    p_add.add_argument("--text", required=True, help="Text to render")
    p_add.add_argument("--font", default="mono", help="Font name (default: mono)")
    p_add.add_argument("--size", type=int, default=24, help="Font size")
    p_add.add_argument("--bold", action="store_true", help="Use bold variant")
    p_add.add_argument("--color", default="255,255,255,255", help="RGBA color")
    p_add.add_argument("--position", default="0,0", help="X,Y position")
    p_add.add_argument("--max-width", type=int, default=None, help="Max width for text wrapping")

    # render mode
    p_render = sub.add_parser("render", help="Render text on new canvas")
    p_render.add_argument("output", help="Output image path")
    p_render.add_argument("--width", type=int, required=True, help="Canvas width")
    p_render.add_argument("--height", type=int, required=True, help="Canvas height")
    p_render.add_argument("--text", required=True, help="Text to render (use \\n for newlines)")
    p_render.add_argument("--font", default="mono", help="Font name")
    p_render.add_argument("--size", type=int, default=48, help="Font size")
    p_render.add_argument("--bold", action="store_true", help="Use bold variant")
    p_render.add_argument("--color", default="255,255,255,255", help="RGBA color")
    p_render.add_argument("--bg-color", default="0,0,0,0", help="RGBA background")
    p_render.add_argument("--center", action="store_true", help="Center text")
    p_render.add_argument("--max-width", type=int, default=None, help="Max width for wrapping")

    args = parser.parse_args()
    if args.mode is None:
        parser.print_help()
        sys.exit(2)

    if args.mode == "add":
        x, y = [int(v) for v in args.position.split(",")]
        result = add_text(
            args.input, args.output,
            text=args.text.replace("\\n", "\n"),
            position=(x, y),
            font_name=args.font, font_size=args.size,
            bold=args.bold, color=_parse_color(args.color),
            max_width=args.max_width,
        )
    else:
        result = render_text(
            args.width, args.height, args.output,
            text=args.text.replace("\\n", "\n"),
            font_name=args.font, font_size=args.size,
            bold=args.bold, color=_parse_color(args.color),
            bg_color=_parse_color(args.bg_color),
            center=args.center, max_width=args.max_width,
        )

    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
