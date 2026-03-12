"""Tests for text rendering module."""
from pathlib import Path

from PIL import Image

from agentbrush.text.ops import add_text, render_text


def test_add_text_basic(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = add_text(
        str(black_bg_with_circle), str(out), "Hello",
        position=(10, 10), color=(255, 255, 255, 255),
    )
    assert result.success
    assert out.exists()
    assert result.metadata["lines"] == 1


def test_add_text_multiline(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = add_text(
        str(black_bg_with_circle), str(out), "Line 1\nLine 2\nLine 3",
        position=(5, 5),
    )
    assert result.success
    assert result.metadata["lines"] == 3


def test_add_text_wrapping(tmp_path):
    """max_width should wrap long text."""
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 255))
    src = tmp_path / "src.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = add_text(
        str(src), str(out),
        "This is a long text that should wrap to multiple lines",
        position=(5, 5), font_size=16, max_width=150,
    )
    assert result.success
    assert result.metadata["lines"] > 1


def test_add_text_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = add_text("/nonexistent.png", str(out), "Hello")
    assert not result.success


def test_add_text_bold(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = add_text(
        str(black_bg_with_circle), str(out), "Bold",
        bold=True, font_size=20,
    )
    assert result.success


def test_add_text_custom_color(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = add_text(
        str(black_bg_with_circle), str(out), "Red",
        position=(10, 10), color=(255, 0, 0, 255),
    )
    assert result.success
    img = Image.open(out)
    # There should be red pixels from the text
    data = list(img.get_flattened_data())
    red_pixels = [p for p in data if p[0] > 200 and p[1] < 50 and p[2] < 50 and p[3] > 0]
    assert len(red_pixels) > 0


def test_render_text_basic(tmp_path):
    out = tmp_path / "out.png"
    result = render_text(
        200, 100, str(out), "Hello World",
        font_size=20, center=True,
    )
    assert result.success
    assert result.width == 200
    assert result.height == 100
    assert result.metadata["canvas"] == "200x100"


def test_render_text_no_center(tmp_path):
    out = tmp_path / "out.png"
    result = render_text(
        200, 100, str(out), "Top Left",
        font_size=16, center=False,
    )
    assert result.success


def test_render_text_with_bg(tmp_path):
    out = tmp_path / "out.png"
    result = render_text(
        100, 50, str(out), "BG",
        bg_color=(0, 0, 0, 255),
        color=(255, 255, 255, 255),
    )
    assert result.success
    img = Image.open(out)
    # Background should be black
    assert img.getpixel((0, 0))[0] < 50


def test_render_text_wrapping(tmp_path):
    out = tmp_path / "out.png"
    result = render_text(
        200, 200, str(out),
        "This long text should wrap within the max width",
        font_size=16, max_width=150,
    )
    assert result.success
    assert result.metadata["lines"] > 1
