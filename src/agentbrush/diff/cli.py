"""CLI for image comparison / diff."""
from __future__ import annotations

from agentbrush.diff.ops import diff_images


def add_parser(subparsers):
    """Register the diff subcommand."""
    p = subparsers.add_parser(
        "diff",
        help="Diff two images and highlight changes",
    )
    p.add_argument("image_a", help="First image (before)")
    p.add_argument("image_b", help="Second image (after)")
    p.add_argument(
        "--output", required=True,
        help="Output diff image path",
    )
    p.add_argument(
        "--threshold", type=int, default=10,
        help="Per-channel difference threshold 0-255 (default: 10)",
    )
    p.add_argument(
        "--highlight-color", default="255,0,0,255",
        help="Highlight color as R,G,B,A (default: red)",
    )
    p.add_argument(
        "--dim", type=float, default=0.3,
        help="Dim factor for unchanged pixels 0-1 (default: 0.3)",
    )
    p.set_defaults(func=run)


def run(args):
    highlight = tuple(int(x) for x in args.highlight_color.split(","))
    result = diff_images(
        args.image_a, args.image_b,
        output_path=args.output,
        threshold=args.threshold,
        highlight_color=highlight,
        dim_factor=args.dim,
    )
    print(result.summary())
    return 0 if result.success else 1
