"""Tests for background removal module."""
from pathlib import Path

from PIL import Image

from agentbrush.background import remove_background


def test_remove_black_bg(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(str(black_bg_with_circle), str(out), color="black")
    assert result.success
    assert result.transparent_pct > 50
    assert out.exists()
    # Circle should be preserved
    img = Image.open(out)
    assert img.load()[50, 50][3] > 0


def test_remove_white_bg(white_bg_with_red_square, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(str(white_bg_with_red_square), str(out), color="white")
    assert result.success
    assert result.transparent_pct > 50
    # Red square center preserved
    img = Image.open(out)
    px = img.load()[50, 50]
    assert px[0] > 200  # red
    assert px[3] > 0    # opaque


def test_already_transparent(fully_transparent, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(str(fully_transparent), str(out))
    assert result.success
    assert len(result.warnings) > 0
    assert "already fully transparent" in result.warnings[0]


def test_solid_black_100pct(solid_black, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(str(solid_black), str(out))
    assert result.success
    assert result.transparent_pct > 99


def test_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = remove_background("/nonexistent/path.png", str(out))
    assert not result.success
    assert "not found" in result.errors[0].lower()


def test_smooth_produces_softer_edges(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(str(black_bg_with_circle), str(out), smooth=True)
    assert result.success
    # Check for semi-transparent pixels at edge (alpha between 0-255)
    img = Image.open(out)
    data = list(img.getdata())
    semi_transparent = [p for p in data if 0 < p[3] < 255]
    assert len(semi_transparent) > 0


def test_resize_output(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(
        str(black_bg_with_circle), str(out), resize=(200, 200)
    )
    assert result.success
    assert result.width == 200
    assert result.height == 200


def test_metadata_has_pixels_removed(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = remove_background(str(black_bg_with_circle), str(out))
    assert "pixels_removed" in result.metadata
    assert result.metadata["pixels_removed"] > 0
