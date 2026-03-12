"""CLI for border cleanup."""
from __future__ import annotations

import argparse

from agentbrush.border.ops import cleanup_border


def add_parser(subparsers):
    """Register the border-cleanup subcommand."""
    p = subparsers.add_parser(
        "border-cleanup",
        help="Remove border artifacts and edge halos",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--passes", type=int, default=15,
        help="White border erosion passes (default: 15)",
    )
    p.add_argument(
        "--threshold", type=int, default=185,
        help="White pixel threshold (default: 185)",
    )
    p.add_argument(
        "--green-halo-passes", type=int, default=0,
        help="Green halo erosion passes (default: 0, disabled)",
    )
    p.add_argument(
        "--alpha-smooth", action="store_true",
        help="Apply Gaussian alpha edge smoothing",
    )
    p.add_argument(
        "--alpha-blur-radius", type=float, default=1.5,
        help="Alpha blur radius (default: 1.5)",
    )
    p.set_defaults(func=run)


def run(args):
    result = cleanup_border(
        args.input, args.output,
        passes=args.passes,
        threshold=args.threshold,
        green_halo_passes=args.green_halo_passes,
        alpha_smooth=args.alpha_smooth,
        alpha_blur_radius=args.alpha_blur_radius,
    )
    print(result.summary())
    return 0 if result.success else 1
