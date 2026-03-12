"""Tests for format conversion module."""
from PIL import Image

from agentbrush.convert.ops import convert_image


def test_png_to_jpeg(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.jpg"
    result = convert_image(str(black_bg_with_circle), str(out))
    assert result.success
    assert out.exists()
    assert result.metadata["output_format"] == "JPEG"
    img = Image.open(out)
    assert img.mode == "RGB"


def test_png_to_webp(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.webp"
    result = convert_image(str(black_bg_with_circle), str(out))
    assert result.success
    assert result.metadata["output_format"] == "WEBP"


def test_rgba_to_jpeg_flattens_alpha(tmp_path):
    """RGBA -> JPEG should flatten alpha onto bg_color."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    img.load()[25, 25] = (255, 0, 0, 255)
    src = tmp_path / "alpha.png"
    img.save(src)

    out = tmp_path / "out.jpg"
    result = convert_image(str(src), str(out), bg_color=(255, 255, 255))
    assert result.success
    assert result.metadata.get("alpha_flattened") is True
    output = Image.open(out)
    # Corner should be white (bg color)
    px = output.getpixel((0, 0))
    assert px[0] > 240


def test_explicit_format_override(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.dat"  # unusual extension
    result = convert_image(
        str(black_bg_with_circle), str(out),
        output_format="PNG",
    )
    assert result.success
    assert result.metadata["output_format"] == "PNG"


def test_ensure_rgba(tmp_path):
    img = Image.new("RGB", (50, 50), (255, 0, 0))
    src = tmp_path / "rgb.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = convert_image(str(src), str(out), ensure_rgba=True)
    assert result.success
    assert result.metadata["converted_to"] == "RGBA"


def test_file_not_found(tmp_path):
    out = tmp_path / "out.png"
    result = convert_image("/nonexistent.png", str(out))
    assert not result.success


def test_png_to_bmp(black_bg_with_circle, tmp_path):
    out = tmp_path / "out.bmp"
    result = convert_image(str(black_bg_with_circle), str(out))
    assert result.success
    assert result.metadata["output_format"] == "BMP"


def test_quality_param(black_bg_with_circle, tmp_path):
    out_high = tmp_path / "high.jpg"
    out_low = tmp_path / "low.jpg"
    convert_image(str(black_bg_with_circle), str(out_high), quality=95)
    convert_image(str(black_bg_with_circle), str(out_low), quality=10)
    # Low quality should be smaller file
    assert out_low.stat().st_size < out_high.stat().st_size
