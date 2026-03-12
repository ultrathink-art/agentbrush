#!/usr/bin/env python3
"""Clean up sticker borders: white border erosion + green halo removal.

Usage:
    python border_cleanup.py input.png output.png [--passes 15] [--green-halo-passes 20]
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.border.ops import cleanup_border


def main():
    parser = argparse.ArgumentParser(description="Clean up sticker borders")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--passes", type=int, default=15, help="White border erosion passes")
    parser.add_argument("--threshold", type=int, default=185, help="White pixel threshold")
    parser.add_argument("--green-halo-passes", type=int, default=0, help="Green halo erosion passes")
    parser.add_argument("--alpha-smooth", action="store_true", help="Apply alpha edge smoothing")
    parser.add_argument("--alpha-blur-radius", type=float, default=1.5, help="Blur radius for alpha smoothing")
    args = parser.parse_args()

    result = cleanup_border(
        args.input, args.output,
        passes=args.passes, threshold=args.threshold,
        green_halo_passes=args.green_halo_passes,
        alpha_smooth=args.alpha_smooth,
        alpha_blur_radius=args.alpha_blur_radius,
    )
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
