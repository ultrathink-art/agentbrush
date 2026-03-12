"""Tests for resize module."""
from PIL import Image

from agentbrush.resize.ops import resize_image


def test_resize_exact(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = resize_image(str(black_bg_with_circle), str(out), width=200, height=200)
    assert result.success
    assert result.width == 200
    assert result.height == 200
    assert result.metadata["mode"] == "exact"


def test_resize_width_only(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = resize_image(str(black_bg_with_circle), str(out), width=200)
    assert result.success
    assert result.width == 200
    assert result.height == 200  # 100x100 -> proportional
    assert result.metadata["mode"] == "width-proportional"


def test_resize_height_only(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = resize_image(str(black_bg_with_circle), str(out), height=50)
    assert result.success
    assert result.height == 50
    assert result.width == 50  # 100x100 proportional
    assert result.metadata["mode"] == "height-proportional"


def test_resize_scale(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = resize_image(str(black_bg_with_circle), str(out), scale=3.0)
    assert result.success
    assert result.width == 300
    assert result.height == 300
    assert "scale" in result.metadata["mode"]


def test_resize_fit(tmp_path):
    """Fit should preserve aspect ratio within bounds."""
    img = Image.new("RGBA", (200, 100), (255, 0, 0, 255))
    src = tmp_path / "wide.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = resize_image(str(src), str(out), width=100, height=100, fit=True)
    assert result.success
    assert result.width == 100
    assert result.height == 50  # preserved 2:1 ratio
    assert result.metadata["mode"] == "fit"


def test_resize_pad(tmp_path):
    """Pad should fit then pad to exact dimensions."""
    img = Image.new("RGBA", (200, 100), (255, 0, 0, 255))
    src = tmp_path / "wide.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = resize_image(str(src), str(out), width=100, height=100, pad=True)
    assert result.success
    assert result.width == 100
    assert result.height == 100
    assert result.metadata["mode"] == "pad"
    # Top/bottom should be transparent (padding)
    img_out = Image.open(out)
    assert img_out.getpixel((50, 0))[3] == 0  # top padding
    assert img_out.getpixel((50, 50))[0] > 200  # content area (red)


def test_resize_no_params(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = resize_image(str(black_bg_with_circle), str(out))
    assert not result.success
    assert "No resize target" in result.errors[0]


def test_resize_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = resize_image("/nonexistent.png", str(out), width=100)
    assert not result.success


def test_resize_original_size_in_metadata(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.png"
    result = resize_image(str(black_bg_with_circle), str(out), scale=2.0)
    assert result.metadata["original_size"] == "100x100"


def test_resize_pad_color(tmp_path):
    img = Image.new("RGBA", (200, 100), (255, 0, 0, 255))
    src = tmp_path / "wide.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = resize_image(
        str(src), str(out), width=100, height=100,
        pad=True, pad_color=(0, 0, 0, 255),
    )
    assert result.success
    img_out = Image.open(out)
    # Padding should be black
    assert img_out.getpixel((50, 0))[:3] == (0, 0, 0)
