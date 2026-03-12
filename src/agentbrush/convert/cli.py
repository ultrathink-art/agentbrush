"""CLI for image format conversion."""
from __future__ import annotations

from agentbrush.convert.ops import convert_image


def add_parser(subparsers):
    """Register the convert subcommand."""
    p = subparsers.add_parser(
        "convert",
        help="Convert image format (PNG, JPEG, WEBP, BMP, TIFF)",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("output", help="Output image path (format from extension)")
    p.add_argument(
        "--format", dest="output_format", default=None,
        help="Explicit output format (overrides extension)",
    )
    p.add_argument(
        "--quality", type=int, default=95,
        help="JPEG/WEBP quality 1-100 (default: 95)",
    )
    p.add_argument(
        "--bg-color", default="255,255,255",
        help="Background color for RGBA->RGB: R,G,B (default: white)",
    )
    p.add_argument(
        "--ensure-rgba", action="store_true",
        help="Force output to RGBA mode",
    )
    p.set_defaults(func=run)


def run(args):
    bg = tuple(int(x) for x in args.bg_color.split(","))
    result = convert_image(
        args.input, args.output,
        output_format=args.output_format,
        quality=args.quality,
        bg_color=bg,
        ensure_rgba=args.ensure_rgba,
    )
    print(result.summary())
    return 0 if result.success else 1
