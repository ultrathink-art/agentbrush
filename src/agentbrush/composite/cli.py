"""CLI for image compositing."""
from __future__ import annotations

from agentbrush.composite.ops import composite, paste_centered


def add_parser(subparsers):
    """Register the composite subcommand."""
    p = subparsers.add_parser(
        "composite",
        help="Alpha-composite overlay onto base image",
    )
    p.add_argument("base", help="Base (background) image path")
    p.add_argument("overlay", help="Overlay (foreground) image path")
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--position", default="0,0",
        help="Position as X,Y (default: 0,0). Use 'center' to auto-center.",
    )
    p.add_argument(
        "--resize-overlay",
        help="Resize overlay: WxH (e.g. 400x400)",
    )
    p.add_argument(
        "--opacity", type=float, default=1.0,
        help="Overlay opacity 0.0-1.0 (default: 1.0)",
    )
    p.set_defaults(func=run)


def run(args):
    resize = None
    if args.resize_overlay:
        w, h = args.resize_overlay.lower().split("x")
        resize = (int(w), int(h))

    if args.position == "center":
        # Use paste_centered — create canvas sized to base
        from PIL import Image
        base = Image.open(args.base)
        result = paste_centered(
            base.width, base.height,
            args.overlay, args.output,
            resize_overlay=resize,
        )
    else:
        pos = tuple(int(x) for x in args.position.split(","))
        result = composite(
            args.base, args.overlay, args.output,
            position=pos, resize_overlay=resize,
            opacity=args.opacity,
        )

    print(result.summary())
    return 0 if result.success else 1
