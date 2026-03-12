"""CLI for text rendering."""
from __future__ import annotations

from agentbrush.text.ops import add_text, render_text


def add_parser(subparsers):
    """Register text subcommands."""
    p = subparsers.add_parser(
        "text",
        help="Render text onto an image or new canvas",
    )
    p.add_argument("input", help="Input image path (use 'new:WxH' for blank canvas)")
    p.add_argument("output", help="Output image path")
    p.add_argument("text", help="Text to render")
    p.add_argument(
        "--font", default="mono",
        help="Font name or alias (default: mono)",
    )
    p.add_argument(
        "--size", type=int, default=24,
        help="Font size in points (default: 24)",
    )
    p.add_argument("--bold", action="store_true", help="Use bold variant")
    p.add_argument(
        "--color", default="255,255,255,255",
        help="Text color as R,G,B,A (default: white)",
    )
    p.add_argument(
        "--position", default="0,0",
        help="Position as X,Y (default: 0,0)",
    )
    p.add_argument("--center", action="store_true", help="Center text on canvas")
    p.add_argument(
        "--max-width", type=int, default=None,
        help="Max width for text wrapping (pixels)",
    )
    p.set_defaults(func=run)


def _parse_color(s):
    parts = [int(x.strip()) for x in s.split(",")]
    if len(parts) == 3:
        return tuple(parts) + (255,)
    return tuple(parts)


def run(args):
    color = _parse_color(args.color)

    if args.input.startswith("new:"):
        dims = args.input[4:]
        w, h = [int(x) for x in dims.lower().split("x")]
        result = render_text(
            w, h, args.output, args.text,
            font_name=args.font, font_size=args.size,
            bold=args.bold, color=color,
            center=args.center, max_width=args.max_width,
        )
    else:
        pos = tuple(int(x) for x in args.position.split(","))
        result = add_text(
            args.input, args.output, args.text,
            position=pos, font_name=args.font,
            font_size=args.size, bold=args.bold,
            color=color, max_width=args.max_width,
        )

    print(result.summary())
    return 0 if result.success else 1
