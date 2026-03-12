"""Tests for border cleanup module."""
from PIL import Image

from agentbrush.border import cleanup_border


def test_erode_white_border(white_border_sticker, tmp_path):
    out = tmp_path / "out.png"
    result = cleanup_border(str(white_border_sticker), str(out), passes=15)
    assert result.success
    assert result.metadata.get("white_border_removed", 0) > 0


def test_dark_artwork_not_eroded(tmp_path):
    """Dark artwork (R,G,B < 185) should NOT be removed by border erosion."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    # Dark artwork touching transparent edge
    for x in range(10, 40):
        for y in range(10, 40):
            img.load()[x, y] = (50, 50, 120, 255)
    src = tmp_path / "dark.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = cleanup_border(str(src), str(out), passes=15, threshold=185)
    assert result.success
    # Dark pixels should be preserved
    assert result.metadata.get("white_border_removed", 0) == 0


def test_interior_preserved(white_border_sticker, tmp_path):
    out = tmp_path / "out.png"
    result = cleanup_border(str(white_border_sticker), str(out))
    assert result.success
    img = Image.open(out)
    # Center should still be opaque
    assert img.load()[40, 40][3] > 200


def test_green_halo_erosion(tmp_path):
    """Green halo pixels adjacent to transparent should be removed."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    pixels = img.load()
    # Green halo at edge
    for x in range(10, 40):
        pixels[x, 10] = (50, 180, 50, 255)  # green halo
    for x in range(10, 40):
        for y in range(11, 40):
            pixels[x, y] = (50, 50, 120, 255)  # dark artwork
    src = tmp_path / "halo.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = cleanup_border(str(src), str(out), passes=0, green_halo_passes=10)
    assert result.success
    assert result.metadata.get("green_halo_removed", 0) > 0


def test_alpha_smooth(white_border_sticker, tmp_path):
    out = tmp_path / "out.png"
    result = cleanup_border(
        str(white_border_sticker), str(out),
        alpha_smooth=True, alpha_blur_radius=2.0,
    )
    assert result.success
    assert result.metadata.get("alpha_smoothed") is True


def test_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = cleanup_border("/nonexistent.png", str(out))
    assert not result.success
