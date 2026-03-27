"""CLI for batch processing."""
from __future__ import annotations

from agentbrush.batch.ops import batch_process
from agentbrush.validate.ops import ALL_PRESETS


def add_parser(subparsers):
    """Register the batch subcommand."""
    p = subparsers.add_parser(
        "batch",
        help="Process multiple images in a directory",
    )
    p.add_argument("input_dir", help="Input directory containing images")
    p.add_argument("output_dir", help="Output directory for processed images")
    p.add_argument(
        "--operation", default="validate",
        choices=["validate", "remove-bg", "crop", "resize"],
        help="Operation to apply (default: validate)",
    )
    p.add_argument(
        "--preset", default=None,
        help="Preset for validate: " + ", ".join(ALL_PRESETS.keys()),
    )
    p.add_argument(
        "--padding", type=int, default=0,
        help="Padding for crop operation (default: 0)",
    )
    p.add_argument(
        "--width", type=int, default=None,
        help="Target width for resize operation",
    )
    p.add_argument(
        "--height", type=int, default=None,
        help="Target height for resize operation",
    )
    p.add_argument(
        "--scale", type=float, default=None,
        help="Scale factor for resize operation",
    )
    p.add_argument(
        "--color", default="black",
        help="Background color for remove-bg (default: black)",
    )
    p.set_defaults(func=run)


def run(args):
    kwargs = {}
    if args.operation == "crop":
        kwargs["padding"] = args.padding
    elif args.operation == "resize":
        kwargs["width"] = args.width
        kwargs["height"] = args.height
        kwargs["scale"] = args.scale
    elif args.operation == "remove-bg":
        kwargs["color"] = args.color

    result = batch_process(
        args.input_dir, args.output_dir,
        operation=args.operation,
        preset=args.preset,
        **kwargs,
    )

    meta = result.metadata
    total = meta.get("total", 0)
    processed = meta.get("processed", 0)
    failed = meta.get("failed", 0)

    print(f"Batch {args.operation}: {processed}/{total} succeeded, {failed} failed")

    for fr in meta.get("results", []):
        status = "OK" if fr["success"] else "FAIL"
        print(f"  [{status}] {fr['file']}")
        for e in fr.get("errors", []):
            print(f"    ERROR: {e}")
        for w in fr.get("warnings", []):
            print(f"    WARNING: {w}")

    return 0 if result.success else 1
