"""CLI for image validation against presets and custom specs."""
from __future__ import annotations

from agentbrush.validate.ops import validate_design, compare_images, ALL_PRESETS


def add_parser(subparsers):
    """Register the validate subcommand."""
    p = subparsers.add_parser(
        "validate",
        help="Validate image against presets or custom specs",
    )
    sub = p.add_subparsers(dest="validate_command")

    # validate check <image> [--preset NAME | --type TYPE | --width/--height]
    check = sub.add_parser("check", help="Validate image file")
    check.add_argument("input", help="Image file to validate")
    check.add_argument(
        "--preset", default=None,
        help="Preset name: "
             + ", ".join(ALL_PRESETS.keys()),
    )
    check.add_argument(
        "--type", dest="product_type", default=None,
        help="Product type (backward compat alias for POD presets): "
             "tshirt, hoodie, hat, mug, sticker, deskmat, poster, tote",
    )
    check.add_argument(
        "--width", type=int, default=None,
        help="Expected width in pixels (custom spec)",
    )
    check.add_argument(
        "--height", type=int, default=None,
        help="Expected height in pixels (custom spec)",
    )
    check.add_argument(
        "--transparent", action="store_true", default=None,
        help="Require transparent background",
    )
    check.set_defaults(func=run_check)

    # validate compare <source> <processed>
    compare = sub.add_parser(
        "compare",
        help="Compare source vs processed for opaque pixel loss",
    )
    compare.add_argument("source", help="Original source image")
    compare.add_argument("processed", help="Processed image")
    compare.add_argument(
        "--max-loss", type=float, default=10.0,
        help="Max acceptable opaque pixel loss %% (default: 10)",
    )
    compare.set_defaults(func=run_compare)

    p.set_defaults(func=lambda args: p.print_help() or 0)


def run_check(args):
    transparent = True if args.transparent else None
    result = validate_design(
        args.input,
        product_type=args.product_type,
        preset=args.preset,
        width=args.width,
        height=args.height,
        transparent=transparent,
    )
    print(result.summary())
    return 0 if result.success else 1


def run_compare(args):
    result = compare_images(args.source, args.processed, max_loss_pct=args.max_loss)
    print(result.summary())
    return 0 if result.success else 1
