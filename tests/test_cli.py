"""CLI integration tests via subprocess."""
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw


@pytest.fixture
def sample_image(tmp_path):
    """Create a simple test image."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 40, 40], fill=(255, 100, 100, 255))
    path = tmp_path / "sample.png"
    img.save(path)
    return path


@pytest.fixture
def green_image(tmp_path):
    img = Image.new("RGBA", (50, 50), (0, 255, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 40, 40], fill=(100, 50, 200, 255))
    path = tmp_path / "green.png"
    img.save(path)
    return path


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "agentbrush"] + list(args),
        capture_output=True, text=True,
    )


def test_help():
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "agentbrush" in result.stdout.lower()


def test_version():
    result = _run_cli("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_remove_bg_cli(sample_image, tmp_path):
    out = tmp_path / "out.png"
    result = _run_cli("remove-bg", str(sample_image), str(out))
    assert result.returncode == 0
    assert out.exists()


def test_greenscreen_cli(green_image, tmp_path):
    out = tmp_path / "out.png"
    result = _run_cli("greenscreen", str(green_image), str(out))
    assert result.returncode == 0
    assert out.exists()


def test_border_cleanup_cli(tmp_path):
    # Create white-border sticker image
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([5, 5, 45, 45], fill=(255, 255, 255, 255))
    draw.ellipse([10, 10, 40, 40], fill=(50, 50, 120, 255))
    src = tmp_path / "sticker.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = _run_cli("border-cleanup", str(src), str(out))
    assert result.returncode == 0
    assert out.exists()


def test_invalid_input_exits_nonzero(tmp_path):
    out = tmp_path / "out.png"
    result = _run_cli("remove-bg", "/nonexistent.png", str(out))
    assert result.returncode != 0


def test_no_command_shows_help():
    result = _run_cli()
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "agentbrush" in result.stdout.lower()
