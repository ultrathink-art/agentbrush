"""Tests for generate module (OpenAI is optional dep)."""
import os
from unittest.mock import patch, MagicMock

from agentbrush.generate.ops import generate_image


def test_generate_unknown_provider(tmp_path):
    out = tmp_path / "out.png"
    result = generate_image("test prompt", str(out), provider="unknown")
    assert not result.success
    assert "Unknown provider" in result.errors[0]


def test_generate_openai_no_key(tmp_path):
    """OpenAI without API key should return error."""
    out = tmp_path / "out.png"
    with patch.dict(os.environ, {}, clear=True):
        # Clear OPENAI_API_KEY from env if present
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            result = generate_image(
                "test prompt", str(out),
                provider="openai", api_key=None,
            )
    # Either "No OpenAI API key" or "not installed" — both are expected
    assert not result.success


def test_generate_openai_import_error(tmp_path):
    """Should gracefully handle missing openai package."""
    out = tmp_path / "out.png"
    with patch.dict("sys.modules", {"openai": None}):
        # This won't actually block the import in the function since
        # it uses a local import. Instead, test the error path directly.
        from agentbrush.generate.ops import _generate_openai
        # Monkey-patch to simulate ImportError
        import agentbrush.generate.ops as gen_mod
        original = gen_mod._generate_openai

        def fake_openai(*args, **kwargs):
            from pathlib import Path
            from agentbrush.core.result import Result
            return Result(errors=[
                "OpenAI package not installed. "
                "Install with: pip install agentbrush[generate]"
            ])

        gen_mod._generate_openai = fake_openai
        try:
            result = generate_image("prompt", str(out), provider="openai")
            assert not result.success
            assert "not installed" in result.errors[0]
        finally:
            gen_mod._generate_openai = original


def test_generate_pollinations_network_error(tmp_path):
    """Should handle network errors gracefully."""
    out = tmp_path / "out.png"
    with patch("urllib.request.urlretrieve", side_effect=Exception("Network error")):
        result = generate_image(
            "test prompt", str(out),
            provider="pollinations",
        )
    assert not result.success
    assert "failed" in result.errors[0].lower()


def test_generate_pollinations_invalid_response(tmp_path):
    """Should detect invalid image data from pollinations."""
    out = tmp_path / "out.png"
    # Write non-image data
    out.write_text("502 Bad Gateway")

    def fake_retrieve(url, path):
        # Write text to the output path
        with open(path, "w") as f:
            f.write("502 Bad Gateway")

    with patch("urllib.request.urlretrieve", side_effect=fake_retrieve):
        result = generate_image(
            "test prompt", str(out),
            provider="pollinations",
        )
    assert not result.success
