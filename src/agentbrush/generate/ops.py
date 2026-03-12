"""AI image generation with provider abstraction.

Providers:
- openai: Uses OpenAI GPT Image (requires `openai` package — optional dep).
- pollinations: Free Pollinations.ai API (no key needed, unreliable).

OpenAI is an optional dependency: `pip install agentbrush[generate]`.
"""
from __future__ import annotations

import os
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Union

from PIL import Image

from agentbrush.core.result import Result


def generate_image(
    prompt: str,
    output_path: Union[str, Path],
    provider: str = "openai",
    width: int = 1024,
    height: int = 1024,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    quality: str = "auto",
) -> Result:
    """Generate an image from a text prompt.

    Args:
        prompt: Text description of the image to generate.
        output_path: Where to save the generated image.
        provider: 'openai' or 'pollinations'.
        width: Image width in pixels.
        height: Image height in pixels.
        model: Model name override. Defaults to 'gpt-image-1' for openai,
            'flux' for pollinations.
        api_key: OpenAI API key (falls back to OPENAI_API_KEY env var).
        quality: OpenAI quality param ('auto', 'low', 'medium', 'high').

    Returns:
        Result with generation metadata.
    """
    output_path = Path(output_path)

    if provider == "openai":
        return _generate_openai(
            prompt, output_path,
            width=width, height=height,
            model=model or "gpt-image-1",
            api_key=api_key,
            quality=quality,
        )
    elif provider == "pollinations":
        return _generate_pollinations(
            prompt, output_path,
            width=width, height=height,
            model=model or "flux",
        )
    else:
        return Result(errors=[f"Unknown provider: {provider}. Use 'openai' or 'pollinations'."])


def _generate_openai(
    prompt: str,
    output_path: Path,
    width: int,
    height: int,
    model: str,
    api_key: Optional[str],
    quality: str,
) -> Result:
    """Generate via OpenAI Images API."""
    try:
        from openai import OpenAI
    except ImportError:
        return Result(errors=[
            "OpenAI package not installed. "
            "Install with: pip install agentbrush[generate]"
        ])

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return Result(errors=[
            "No OpenAI API key. Set OPENAI_API_KEY env var or pass api_key param."
        ])

    try:
        client = OpenAI(api_key=key)

        size = f"{width}x{height}"

        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size,
            quality=quality,
        )

        image_url = response.data[0].url
        if image_url is None:
            # b64_json response
            import base64
            b64 = response.data[0].b64_json
            if b64 is None:
                return Result(errors=["OpenAI returned no image data"])
            img_data = base64.b64decode(b64)
            os.makedirs(output_path.parent, exist_ok=True)
            output_path.write_bytes(img_data)
        else:
            os.makedirs(output_path.parent, exist_ok=True)
            urllib.request.urlretrieve(image_url, str(output_path))

        img = Image.open(output_path)
        result = Result(
            output_path=output_path,
            width=img.width,
            height=img.height,
        )
        result.metadata = {
            "provider": "openai",
            "model": model,
            "prompt_length": len(prompt),
        }
        return result

    except Exception as e:
        return Result(errors=[f"OpenAI generation failed: {e}"])


def _generate_pollinations(
    prompt: str,
    output_path: Path,
    width: int,
    height: int,
    model: str,
) -> Result:
    """Generate via Pollinations.ai (free, no API key, unreliable)."""
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&model={model}&nologo=true"
    )

    try:
        os.makedirs(output_path.parent, exist_ok=True)
        urllib.request.urlretrieve(url, str(output_path))

        # Verify it's an actual image (Pollinations returns 502 as text sometimes)
        try:
            img = Image.open(output_path)
            img.verify()
            # Re-open after verify
            img = Image.open(output_path)
        except Exception:
            return Result(errors=[
                "Pollinations returned invalid image data (possibly 502). "
                "Retry or use --provider openai."
            ])

        result = Result(
            output_path=output_path,
            width=img.width,
            height=img.height,
        )
        result.metadata = {
            "provider": "pollinations",
            "model": model,
            "prompt_length": len(prompt),
        }
        return result

    except Exception as e:
        return Result(errors=[f"Pollinations generation failed: {e}"])
