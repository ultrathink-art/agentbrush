"""CLI for AI image generation."""
from __future__ import annotations

from agentbrush.generate.ops import generate_image


def add_parser(subparsers):
    """Register the generate subcommand."""
    p = subparsers.add_parser(
        "generate",
        help="Generate image from text prompt (OpenAI or Pollinations)",
    )
    p.add_argument("prompt", help="Text prompt describing the image")
    p.add_argument("output", help="Output image path")
    p.add_argument(
        "--provider", default="openai",
        choices=["openai", "pollinations"],
        help="Image generation provider (default: openai)",
    )
    p.add_argument("--width", type=int, default=1024, help="Width (default: 1024)")
    p.add_argument("--height", type=int, default=1024, help="Height (default: 1024)")
    p.add_argument("--model", default=None, help="Model override")
    p.add_argument("--api-key", default=None, help="API key (OpenAI)")
    p.add_argument(
        "--quality", default="auto",
        help="Quality: auto, low, medium, high (OpenAI only, default: auto)",
    )
    p.set_defaults(func=run)


def run(args):
    result = generate_image(
        args.prompt, args.output,
        provider=args.provider,
        width=args.width, height=args.height,
        model=args.model, api_key=args.api_key,
        quality=args.quality,
    )
    print(result.summary())
    return 0 if result.success else 1
