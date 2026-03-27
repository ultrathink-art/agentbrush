"""CLI for smart crop."""
from __future__ import annotations

from agentbrush.crop.ops import smart_crop


def add_parser(subparsers):
    """Register the crop subcommand."""
    p = subparsers.add_parser(
        "crop",
        help="Auto-detect content bounds and crop to tight bounding box",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--padding", type=int, default=0,
        help="Extra pixels around content bounds (default: 0)",
    )
    p.add_argument(
        "--threshold", type=int, default=20,
        help="Alpha threshold for opaque detection (default: 20)",
    )
    p.add_argument(
        "--bg-color", default=None,
        help="Background color as R,G,B to remove before cropping",
    )
    p.set_defaults(func=run)


def run(args):
    bg_color = None
    if args.bg_color:
        bg_color = tuple(int(x) for x in args.bg_color.split(","))
    result = smart_crop(
        args.input, args.output,
        padding=args.padding,
        alpha_threshold=args.threshold,
        bg_color=bg_color,
    )
    print(result.summary())
    return 0 if result.success else 1
