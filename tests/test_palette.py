"""Tests for color palette extraction module."""
import json

from PIL import Image, ImageDraw

from agentbrush.palette.ops import extract_palette, format_palette


def test_palette_basic(tmp_path):
    """Extract colors from a simple two-color image."""
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 0, 100, 100], fill=(0, 0, 255, 255))
    src = tmp_path / "two_colors.png"
    img.save(src)

    result = extract_palette(str(src), count=2)
    assert result.success
    colors = result.metadata["colors"]
    assert len(colors) == 2
    assert all("hex" in c for c in colors)
    assert all("pct" in c for c in colors)
    total_pct = sum(c["pct"] for c in colors)
    assert 95 < total_pct <= 100.1


def test_palette_count(tmp_path):
    """Request specific number of colors."""
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    src = tmp_path / "red.png"
    img.save(src)

    result = extract_palette(str(src), count=4)
    assert result.success
    # Solid red → quantize may return fewer unique colors
    colors = result.metadata["colors"]
    assert len(colors) >= 1
    assert len(colors) <= 4


def test_palette_ignores_transparent(tmp_path):
    """Transparent pixels excluded by default."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 20, 100], fill=(255, 0, 0, 255))
    src = tmp_path / "mostly_transparent.png"
    img.save(src)

    result = extract_palette(str(src))
    assert result.success
    colors = result.metadata["colors"]
    assert len(colors) >= 1
    # Primary color should be reddish
    assert colors[0]["r"] > 200


def test_palette_include_transparent(tmp_path):
    """Include transparent pixels when flag set."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 10, 10], fill=(255, 0, 0, 255))
    src = tmp_path / "mostly_transparent.png"
    img.save(src)

    result = extract_palette(str(src), ignore_transparent=False)
    assert result.success
    assert result.metadata["total_sampled"] == 10000


def test_palette_fully_transparent(fully_transparent, tmp_path):
    """Fully transparent image → warning, no colors."""
    result = extract_palette(str(fully_transparent))
    assert result.success
    assert len(result.metadata["colors"]) == 0
    assert len(result.warnings) > 0


def test_palette_file_not_found():
    result = extract_palette("/nonexistent.png")
    assert not result.success


def test_palette_invalid_count(tmp_path):
    """Invalid count returns error."""
    img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    src = tmp_path / "tiny.png"
    img.save(src)

    result = extract_palette(str(src), count=0)
    assert not result.success
    assert "1-64" in result.errors[0]


def test_palette_format_json(tmp_path):
    """JSON format output."""
    img = Image.new("RGBA", (50, 50), (100, 200, 50, 255))
    src = tmp_path / "green.png"
    img.save(src)

    result = extract_palette(str(src), count=2)
    output = format_palette(result, "json")
    parsed = json.loads(output)
    assert "colors" in parsed
    assert len(parsed["colors"]) >= 1


def test_palette_format_hex(tmp_path):
    """Hex format output."""
    img = Image.new("RGBA", (50, 50), (255, 128, 0, 255))
    src = tmp_path / "orange.png"
    img.save(src)

    result = extract_palette(str(src), count=2)
    output = format_palette(result, "hex")
    lines = output.strip().split("\n")
    assert all(line.startswith("#") for line in lines)


def test_palette_format_text(tmp_path):
    """Text format output."""
    img = Image.new("RGBA", (50, 50), (0, 0, 255, 255))
    src = tmp_path / "blue.png"
    img.save(src)

    result = extract_palette(str(src), count=2)
    output = format_palette(result, "text")
    assert "rgb(" in output
    assert "%" in output


def test_palette_multicolor(tmp_path):
    """Extract from image with multiple distinct colors."""
    img = Image.new("RGBA", (300, 100), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 100, 100], fill=(255, 0, 0, 255))
    draw.rectangle([100, 0, 200, 100], fill=(0, 255, 0, 255))
    draw.rectangle([200, 0, 300, 100], fill=(0, 0, 255, 255))
    src = tmp_path / "rgb_thirds.png"
    img.save(src)

    result = extract_palette(str(src), count=3)
    assert result.success
    colors = result.metadata["colors"]
    assert len(colors) == 3
    hexes = {c["hex"] for c in colors}
    assert len(hexes) == 3
