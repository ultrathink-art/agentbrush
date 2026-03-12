"""CLI for green screen removal."""
from __future__ import annotations

import argparse

from agentbrush.greenscreen.ops import remove_greenscreen


def add_parser(subparsers):
    """Register the greenscreen subcommand."""
    p = subparsers.add_parser(
        "greenscreen",
        help="Remove green screen background (multi-pass pipeline)",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--flood-threshold", type=int, default=60,
        help="Flood fill color threshold (default: 60)",
    )
    p.add_argument(
        "--sweep-threshold", type=int, default=50,
        help="Green sweep threshold (default: 50)",
    )
    p.add_argument(
        "--halo-passes", type=int, default=0,
        help="Green halo erosion passes (default: 0)",
    )
    p.add_argument(
        "--upscale", type=int, default=None,
        help="Upscale factor (e.g. 3 for 3x)",
    )
    p.add_argument(
        "--no-smooth", action="store_true",
        help="Skip edge smoothing",
    )
    p.set_defaults(func=run)


def run(args):
    result = remove_greenscreen(
        args.input, args.output,
        flood_threshold=args.flood_threshold,
        sweep_threshold=args.sweep_threshold,
        halo_passes=args.halo_passes,
        upscale=args.upscale,
        smooth=not args.no_smooth,
    )
    print(result.summary())
    return 0 if result.success else 1
