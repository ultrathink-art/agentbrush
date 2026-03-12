"""CLI for image resizing."""
from __future__ import annotations

from agentbrush.resize.ops import resize_image


def add_parser(subparsers):
    """Register the resize subcommand."""
    p = subparsers.add_parser(
        "resize",
        help="Resize image (exact, fit, pad, or scale)",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("output", help="Output image path")
    p.add_argument("--width", type=int, help="Target width")
    p.add_argument("--height", type=int, help="Target height")
    p.add_argument("--scale", type=float, help="Scale factor (e.g. 2.0)")
    p.add_argument(
        "--fit", action="store_true",
        help="Fit within width x height preserving aspect ratio",
    )
    p.add_argument(
        "--pad", action="store_true",
        help="Fit then pad to exact dimensions",
    )
    p.add_argument(
        "--pad-color", default="0,0,0,0",
        help="Padding color as R,G,B,A (default: transparent)",
    )
    p.set_defaults(func=run)


def run(args):
    pad_color = tuple(int(x) for x in args.pad_color.split(","))
    result = resize_image(
        args.input, args.output,
        width=args.width, height=args.height,
        scale=args.scale, fit=args.fit,
        pad=args.pad, pad_color=pad_color,
    )
    print(result.summary())
    return 0 if result.success else 1
