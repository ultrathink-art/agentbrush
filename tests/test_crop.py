"""Tests for smart crop module."""
from PIL import Image, ImageDraw

from agentbrush.crop.ops import smart_crop


def test_crop_transparent_padding(tmp_path):
    """Crop transparent image to content bounds."""
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0, 255))
    src = tmp_path / "padded.png"
    img.save(src)

    out = tmp_path / "cropped.png"
    result = smart_crop(str(src), str(out))
    assert result.success
    assert result.width == 101  # 150 - 50 + 1
    assert result.height == 101
    assert result.metadata["original_size"] == "200x200"
    assert result.metadata["pixels_removed"] > 0


def test_crop_with_padding(tmp_path):
    """Crop with extra padding around content."""
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([80, 80, 120, 120], fill=(0, 255, 0, 255))
    src = tmp_path / "small_content.png"
    img.save(src)

    out = tmp_path / "cropped.png"
    result = smart_crop(str(src), str(out), padding=20)
    assert result.success
    # Content is 41px wide (120-80+1), + 20px padding each side = 81
    assert result.width == 81
    assert result.height == 81
    assert result.metadata["padding"] == 20


def test_crop_padding_clamped_to_bounds(tmp_path):
    """Padding shouldn't extend beyond image bounds."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, 95, 95], fill=(255, 0, 0, 255))
    src = tmp_path / "near_edge.png"
    img.save(src)

    out = tmp_path / "cropped.png"
    result = smart_crop(str(src), str(out), padding=50)
    assert result.success
    assert result.width <= 100
    assert result.height <= 100


def test_crop_fully_opaque(tmp_path):
    """Fully opaque image crops to full size."""
    img = Image.new("RGBA", (80, 60), (100, 100, 200, 255))
    src = tmp_path / "solid.png"
    img.save(src)

    out = tmp_path / "cropped.png"
    result = smart_crop(str(src), str(out))
    assert result.success
    assert result.width == 80
    assert result.height == 60


def test_crop_with_bg_color(tmp_path):
    """Crop RGB image using bg_color to identify background."""
    img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 70, 70], fill=(255, 0, 0, 255))
    src = tmp_path / "white_bg.png"
    img.save(src)

    out = tmp_path / "cropped.png"
    result = smart_crop(str(src), str(out), bg_color=(255, 255, 255))
    assert result.success
    assert result.width < 100
    assert result.height < 100


def test_crop_circle_on_transparent(black_bg_with_circle, tmp_path):
    """Crop from conftest fixture — circle on black bg."""
    out = tmp_path / "cropped.png"
    result = smart_crop(
        str(black_bg_with_circle), str(out),
        bg_color=(0, 0, 0),
    )
    assert result.success
    assert result.width < 100


def test_crop_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = smart_crop("/nonexistent.png", str(out))
    assert not result.success
    assert "not found" in result.errors[0].lower()


def test_crop_preserves_content(tmp_path):
    """Verify cropped image contains the original content pixels."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 60, 60], fill=(128, 64, 32, 255))
    src = tmp_path / "content.png"
    img.save(src)

    out = tmp_path / "cropped.png"
    result = smart_crop(str(src), str(out))
    assert result.success

    cropped = Image.open(out)
    center = cropped.getpixel((cropped.width // 2, cropped.height // 2))
    assert center[0] == 128
    assert center[3] == 255
