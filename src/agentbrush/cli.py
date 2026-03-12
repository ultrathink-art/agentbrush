"""Top-level CLI dispatcher for agentbrush.

Usage:
    agentbrush <command> [options]

Commands:
    remove-bg        Remove solid-color background via edge-based flood fill
    greenscreen      Remove green screen background (multi-pass pipeline)
    border-cleanup   Remove white sticker border + optional green halo
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

    add_bg(subparsers)
    add_gs(subparsers)
    add_border(subparsers)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    exit_code = args.func(args)
    sys.exit(exit_code or 0)
