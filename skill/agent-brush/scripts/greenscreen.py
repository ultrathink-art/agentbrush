#!/usr/bin/env python3
"""Remove green screen background (multi-pass pipeline).

Usage:
    python greenscreen.py input.png output.png [--upscale 3] [--halo-passes 20]
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.greenscreen.ops import remove_greenscreen


def main():
    parser = argparse.ArgumentParser(description="Remove green screen background")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--flood-threshold", type=int, default=60, help="Flood fill threshold")
    parser.add_argument("--sweep-threshold", type=int, default=50, help="Green sweep threshold")
    parser.add_argument("--halo-passes", type=int, default=0, help="Green halo erosion passes")
    parser.add_argument("--upscale", type=int, default=None, help="Upscale factor (e.g. 3)")
    parser.add_argument("--no-smooth", action="store_true", help="Skip edge smoothing")
    args = parser.parse_args()

    result = remove_greenscreen(
        args.input, args.output,
        flood_threshold=args.flood_threshold,
        sweep_threshold=args.sweep_threshold,
        halo_passes=args.halo_passes,
        upscale=args.upscale,
        smooth=not args.no_smooth,
    )
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
