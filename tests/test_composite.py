"""Tests for compositing module."""
from PIL import Image, ImageDraw

from agentbrush.composite.ops import composite, paste_centered


def test_composite_basic(tmp_path):
    base = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    overlay = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
    base_path = tmp_path / "base.png"
    overlay_path = tmp_path / "overlay.png"
    base.save(base_path)
    overlay.save(overlay_path)

    out = tmp_path / "out.png"
    result = composite(str(base_path), str(overlay_path), str(out), position=(25, 25))
    assert result.success
    assert out.exists()

    img = Image.open(out)
    # Center should be blue (overlay)
    px = img.getpixel((50, 50))
    assert px[2] > 200
    # Corner should be red (base)
    px = img.getpixel((0, 0))
    assert px[0] > 200


def test_composite_with_resize(tmp_path):
    base = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    overlay = Image.new("RGBA", (200, 200), (0, 255, 0, 255))
    base_path = tmp_path / "base.png"
    overlay_path = tmp_path / "overlay.png"
    base.save(base_path)
    overlay.save(overlay_path)

    out = tmp_path / "out.png"
    result = composite(
        str(base_path), str(overlay_path), str(out),
        resize_overlay=(50, 50),
    )
    assert result.success
    assert result.metadata["overlay_size"] == "50x50"


def test_composite_opacity(tmp_path):
    base = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    overlay = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
    base_path = tmp_path / "base.png"
    overlay_path = tmp_path / "overlay.png"
    base.save(base_path)
    overlay.save(overlay_path)

    out = tmp_path / "out.png"
    result = composite(
        str(base_path), str(overlay_path), str(out),
        opacity=0.5,
    )
    assert result.success
    img = Image.open(out)
    px = img.getpixel((25, 25))
    # Should be a blend of red and blue
    assert px[0] > 50  # some red
    assert px[2] > 50  # some blue


def test_composite_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = composite("/nonexistent.png", "/also_missing.png", str(out))
    assert not result.success


def test_paste_centered_basic(tmp_path):
    overlay = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    overlay_path = tmp_path / "overlay.png"
    overlay.save(overlay_path)

    out = tmp_path / "out.png"
    result = paste_centered(200, 200, str(overlay_path), str(out))
    assert result.success
    assert result.width == 200
    assert result.height == 200

    img = Image.open(out)
    # Center should be red
    assert img.getpixel((100, 100))[0] > 200
    # Corner should be transparent
    assert img.getpixel((0, 0))[3] == 0


def test_paste_centered_fit(tmp_path):
    overlay = Image.new("RGBA", (400, 200), (0, 255, 0, 255))
    overlay_path = tmp_path / "overlay.png"
    overlay.save(overlay_path)

    out = tmp_path / "out.png"
    result = paste_centered(100, 100, str(overlay_path), str(out), fit=True)
    assert result.success
    assert result.width == 100
    assert result.height == 100


def test_paste_centered_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = paste_centered(100, 100, "/nonexistent.png", str(out))
    assert not result.success


def test_paste_centered_bg_color(tmp_path):
    overlay = Image.new("RGBA", (20, 20), (255, 0, 0, 255))
    overlay_path = tmp_path / "overlay.png"
    overlay.save(overlay_path)

    out = tmp_path / "out.png"
    result = paste_centered(
        100, 100, str(overlay_path), str(out),
        bg_color=(0, 0, 0, 255),
    )
    assert result.success
    img = Image.open(out)
    # Corner should be black bg
    assert img.getpixel((0, 0)) == (0, 0, 0, 255)
