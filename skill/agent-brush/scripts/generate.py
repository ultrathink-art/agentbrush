#!/usr/bin/env python3
"""Generate image from text prompt (OpenAI/Pollinations).

Usage:
    python generate.py --prompt "cute cat" --output cat.png
    python generate.py --provider pollinations --prompt "robot" --output robot.png
"""
import argparse
import sys
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_script_dir, "..", "..", "..", "src")
if os.path.isdir(_src_dir):
    sys.path.insert(0, _src_dir)

from agentbrush.generate.ops import generate_image


def main():
    parser = argparse.ArgumentParser(description="AI image generation")
    parser.add_argument("--prompt", required=True, help="Text description of image")
    parser.add_argument("--output", required=True, help="Output image path")
    parser.add_argument("--provider", default="openai", choices=["openai", "pollinations"],
                        help="Generation provider")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--quality", default="auto", help="Quality: auto, low, medium, high")
    args = parser.parse_args()

    result = generate_image(
        args.prompt, args.output,
        provider=args.provider,
        width=args.width, height=args.height,
        model=args.model, quality=args.quality,
    )
    print(result.summary())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
