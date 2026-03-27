"""CLI for color palette extraction."""
from __future__ import annotations

from agentbrush.palette.ops import extract_palette, format_palette


def add_parser(subparsers):
    """Register the palette subcommand."""
    p = subparsers.add_parser(
        "palette",
        help="Extract dominant colors from an image",
    )
    p.add_argument("input", help="Input image path")
    p.add_argument(
        "--count", type=int, default=6,
        help="Number of colors to extract (default: 6)",
    )
    p.add_argument(
        "--format", dest="output_format", default="json",
        choices=["json", "text", "hex"],
        help="Output format (default: json)",
    )
    p.add_argument(
        "--include-transparent", action="store_true",
        help="Include transparent pixels in analysis",
    )
    p.set_defaults(func=run)


def run(args):
    result = extract_palette(
        args.input,
        count=args.count,
        ignore_transparent=not args.include_transparent,
    )
    if not result.success:
        print(result.summary())
        return 1
    print(format_palette(result, args.output_format))
    return 0
