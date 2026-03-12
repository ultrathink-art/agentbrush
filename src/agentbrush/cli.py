"""Top-level CLI dispatcher for agentbrush.

Usage:
    agentbrush <command> [options]

Commands:
    remove-bg        Remove solid-color background via edge-based flood fill
    greenscreen      Remove green screen background (multi-pass pipeline)
    border-cleanup   Remove border artifacts and edge halos
    text             Render text onto an image or new canvas
    composite        Alpha-composite overlay onto base image
    resize           Resize image (exact, fit, pad, or scale)
    validate         Validate image against presets or custom specs
    convert          Convert image format (PNG, JPEG, WEBP, etc.)
    generate         Generate image from text prompt (OpenAI/Pollinations)
"""
from __future__ import annotations

import argparse
import sys

from agentbrush import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="agentbrush",
        description="Image editing toolkit for AI agents",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"agentbrush {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Register subcommands
    from agentbrush.background.cli import add_parser as add_bg
    from agentbrush.greenscreen.cli import add_parser as add_gs
    from agentbrush.border.cli import add_parser as add_border
    from agentbrush.text.cli import add_parser as add_text
    from agentbrush.composite.cli import add_parser as add_composite
    from agentbrush.resize.cli import add_parser as add_resize
    from agentbrush.validate.cli import add_parser as add_validate
    from agentbrush.convert.cli import add_parser as add_convert
    from agentbrush.generate.cli import add_parser as add_generate

    add_bg(subparsers)
    add_gs(subparsers)
    add_border(subparsers)
    add_text(subparsers)
    add_composite(subparsers)
    add_resize(subparsers)
    add_validate(subparsers)
    add_convert(subparsers)
    add_generate(subparsers)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    exit_code = args.func(args)
    sys.exit(exit_code or 0)
