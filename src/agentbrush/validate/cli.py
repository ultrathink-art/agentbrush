"""CLI for design validation."""
from __future__ import annotations

from agentbrush.validate.ops import validate_design, compare_images


def add_parser(subparsers):
    """Register the validate subcommand."""
    p = subparsers.add_parser(
        "validate",
        help="Validate design against product specs (port of bin/design-qa)",
    )
    sub = p.add_subparsers(dest="validate_command")

    # validate check <image> [--type TYPE]
    check = sub.add_parser("check", help="Validate design file")
    check.add_argument("input", help="Image file to validate")
    check.add_argument(
        "--type", dest="product_type", default=None,
        help="Product type (auto-detected if omitted): "
             "tshirt, hoodie, hat, mug, sticker, deskmat, poster, tote",
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
    result = validate_design(args.input, product_type=args.product_type)
    print(result.summary())
    return 0 if result.success else 1


def run_compare(args):
    result = compare_images(args.source, args.processed, max_loss_pct=args.max_loss)
    print(result.summary())
    return 0 if result.success else 1
