"""CLI for background removal."""
from __future__ import annotations

import argparse
import sys

from agentbrush.background.ops import remove_background


def add_parser(subparsers):
    """Register the remove-bg subcommand."""
    p = subparsers.add_parser(
        "remove-bg",
        help="Remove solid-color background via edge-based flood fill",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--color", default="black",
        help="Background color: black, white, or R,G,B (default: black)",
    )
    p.add_argument(
        "--threshold", type=int, default=25,
        help="Color match threshold 0-255 (default: 25)",
    )
    p.add_argument(
        "--smooth", action="store_true",
        help="Apply 1px edge feathering",
    )
    p.add_argument(
        "--resize",
        help="Resize output: WxH (e.g. 1664x1664)",
    )
    p.set_defaults(func=run)


def run(args):
    resize = None
    if args.resize:
        w, h = args.resize.lower().split("x")
        resize = (int(w), int(h))

    result = remove_background(
        args.input, args.output,
        color=args.color,
        threshold=args.threshold,
        smooth=args.smooth,
        resize=resize,
    )
    print(result.summary())
    return 0 if result.success else 1
