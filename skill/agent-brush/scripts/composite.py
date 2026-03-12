#!/usr/bin/env python3
"""Image compositing: layer artwork onto canvases.

Usage:
    python composite.py overlay base.png overlay.png output.png --position 100,200
    python composite.py paste-centered output.png --overlay art.png --canvas 4500x5400 --fit
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.composite.ops import composite, paste_centered


def _parse_color(s):
    parts = [int(x) for x in s.split(",")]
    if len(parts) == 3:
        parts.append(255)
    return tuple(parts)


def main():
    parser = argparse.ArgumentParser(description="Image compositing")
    sub = parser.add_subparsers(dest="mode")

    # overlay mode
    p_overlay = sub.add_parser("overlay", help="Composite overlay onto base")
    p_overlay.add_argument("base", help="Background image")
    p_overlay.add_argument("overlay", help="Foreground image")
    p_overlay.add_argument("output", help="Output image path")
    p_overlay.add_argument("--position", default="0,0", help="X,Y position for overlay")
    p_overlay.add_argument("--resize-overlay", help="Resize overlay: WxH")
    p_overlay.add_argument("--opacity", type=float, default=1.0, help="Overlay opacity 0.0-1.0")

    # paste-centered mode
    p_center = sub.add_parser("paste-centered", help="Center image on new canvas")
    p_center.add_argument("output", help="Output image path")
    p_center.add_argument("--overlay", required=True, help="Image to center")
    p_center.add_argument("--canvas", required=True, help="Canvas size: WxH")
    p_center.add_argument("--bg-color", default="0,0,0,0", help="Background RGBA")
    p_center.add_argument("--resize-overlay", help="Resize overlay: WxH")
    p_center.add_argument("--fit", action="store_true", help="Scale to fit canvas")

    args = parser.parse_args()
    if args.mode is None:
        parser.print_help()
        sys.exit(2)

    if args.mode == "overlay":
        x, y = [int(v) for v in args.position.split(",")]
        resize_overlay = None
        if args.resize_overlay:
            w, h = args.resize_overlay.lower().split("x")
            resize_overlay = (int(w), int(h))
        result = composite(
            args.base, args.overlay, args.output,
            position=(x, y), resize_overlay=resize_overlay,
            opacity=args.opacity,
        )
    else:
        cw, ch = [int(v) for v in args.canvas.lower().split("x")]
        resize_overlay = None
        if args.resize_overlay:
            w, h = args.resize_overlay.lower().split("x")
            resize_overlay = (int(w), int(h))
        result = paste_centered(
            cw, ch, args.overlay, args.output,
            bg_color=_parse_color(args.bg_color),
            resize_overlay=resize_overlay,
            fit=args.fit,
        )

    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
