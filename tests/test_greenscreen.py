"""Tests for green screen removal module."""
from PIL import Image

from agentbrush.greenscreen import remove_greenscreen


def test_remove_pure_green_bg(green_bg_with_art, tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen(str(green_bg_with_art), str(out))
    assert result.success
    assert result.transparent_pct > 40
    # Blue circle should be preserved
    img = Image.open(out)
    assert img.load()[50, 50][3] > 0


def test_trapped_green_removed(green_bg_with_trapped_green, tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen(str(green_bg_with_trapped_green), str(out))
    assert result.success
    # Trapped green in center should be swept
    assert result.metadata.get("sweep_removed", 0) > 0


def test_pre_transparent_detected(pre_transparent_green, tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen(str(pre_transparent_green), str(out))
    assert result.success
    assert result.metadata.get("pre_transparent") is True
    assert result.metadata.get("flood_fill_removed") == 0


def test_dark_artwork_preserved(green_bg_with_art, tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen(str(green_bg_with_art), str(out))
    assert result.success
    img = Image.open(out)
    px = img.load()[50, 50]
    # Dark blue artwork should still have color
    assert px[2] > 50  # blue channel
    assert px[3] > 0   # opaque


def test_upscale(green_bg_with_art, tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen(str(green_bg_with_art), str(out), upscale=2)
    assert result.success
    assert result.width == 200
    assert result.height == 200


def test_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen("/nonexistent.png", str(out))
    assert not result.success


def test_no_smooth(green_bg_with_art, tmp_path):
    out = tmp_path / "out.png"
    result = remove_greenscreen(str(green_bg_with_art), str(out), smooth=False)
    assert result.success
