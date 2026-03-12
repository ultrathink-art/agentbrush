"""CLI for image compositing.

Supports two modes:
    agentbrush composite <base> <overlay> <output> [--position X,Y] [--opacity N]
    agentbrush composite paste-centered <output> --overlay <img> --canvas WxH [--fit] [--bg-color R,G,B,A]
"""
from __future__ import annotations

import argparse

from agentbrush.composite.ops import composite, paste_centered


def add_parser(subparsers):
    """Register the composite subcommand."""
    p = subparsers.add_parser(
        "composite",
        help="Composite images: overlay onto base, or center on new canvas",
        usage=(
            "agentbrush composite <base> <overlay> <output> [options]\n"
            "       agentbrush composite paste-centered <output> "
            "--overlay <img> --canvas WxH [--fit]"
        ),
    )
    p.add_argument("rest", nargs=argparse.REMAINDER)
    p.set_defaults(func=run)


def _overlay_parser():
    """Parser for overlay mode (default)."""
    p = argparse.ArgumentParser(
        prog="agentbrush composite",
        description="Alpha-composite overlay onto base image",
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
    return p


def _paste_centered_parser():
    """Parser for paste-centered mode."""
    p = argparse.ArgumentParser(
        prog="agentbrush composite paste-centered",
        description="Center image on a new canvas",
    )
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--overlay", required=True,
        help="Image to center on canvas",
    )
    p.add_argument(
        "--canvas", required=True,
        help="Canvas size as WxH (e.g. 4500x5400)",
    )
    p.add_argument(
        "--bg-color", default="0,0,0,0",
        help="Background color as R,G,B,A (default: transparent)",
    )
    p.add_argument(
        "--resize-overlay",
        help="Resize overlay before centering: WxH",
    )
    p.add_argument(
        "--fit", action="store_true",
        help="Scale overlay to fit canvas while preserving aspect ratio",
    )
    return p


def _parse_color(s):
    parts = [int(x) for x in s.split(",")]
    if len(parts) == 3:
        parts.append(255)
    return tuple(parts)


def run(args):
    """Dispatch composite command based on mode."""
    remaining = args.rest

    # Strip leading '--' if argparse inserted it
    if remaining and remaining[0] == "--":
        remaining = remaining[1:]

    if not remaining or remaining[0] in ("-h", "--help"):
        print(
            "Usage:\n"
            "  agentbrush composite <base> <overlay> <output> [--position X,Y]\n"
            "  agentbrush composite paste-centered <output> "
            "--overlay <img> --canvas WxH [--fit]\n"
            "\n"
            "Modes:\n"
            "  (default)        Alpha-composite overlay onto base image\n"
            "  paste-centered   Center image on a new canvas\n"
            "\n"
            "Run 'agentbrush composite paste-centered --help' for mode-specific help."
        )
        return 0

    if remaining[0] == "paste-centered":
        return _run_paste_centered(remaining[1:])
    else:
        return _run_overlay(remaining)


def _run_overlay(argv):
    """Run overlay composite mode."""
    parser = _overlay_parser()
    ov_args = parser.parse_args(argv)

    resize = None
    if ov_args.resize_overlay:
        w, h = ov_args.resize_overlay.lower().split("x")
        resize = (int(w), int(h))

    if ov_args.position == "center":
        from PIL import Image
        base = Image.open(ov_args.base)
        result = paste_centered(
            base.width, base.height,
            ov_args.overlay, ov_args.output,
            resize_overlay=resize,
        )
    else:
        pos = tuple(int(x) for x in ov_args.position.split(","))
        result = composite(
            ov_args.base, ov_args.overlay, ov_args.output,
            position=pos, resize_overlay=resize,
            opacity=ov_args.opacity,
        )

    print(result.summary())
    return 0 if result.success else 1


def _run_paste_centered(argv):
    """Run paste-centered composite mode."""
    parser = _paste_centered_parser()
    pc_args = parser.parse_args(argv)

    cw, ch = [int(v) for v in pc_args.canvas.lower().split("x")]

    resize = None
    if pc_args.resize_overlay:
        w, h = pc_args.resize_overlay.lower().split("x")
        resize = (int(w), int(h))

    result = paste_centered(
        cw, ch, pc_args.overlay, pc_args.output,
        bg_color=_parse_color(pc_args.bg_color),
        resize_overlay=resize,
        fit=pc_args.fit,
    )

    print(result.summary())
    return 0 if result.success else 1
