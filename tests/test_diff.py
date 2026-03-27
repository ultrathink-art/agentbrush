"""Tests for image diff module."""
from PIL import Image, ImageDraw

from agentbrush.diff.ops import diff_images


def test_diff_identical_images(tmp_path):
    """Identical images → 0% change."""
    img = Image.new("RGBA", (50, 50), (100, 100, 100, 255))
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    img.save(a)
    img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out))
    assert result.success
    assert result.metadata["changed_pct"] == 0.0
    assert result.metadata["changed_pixels"] == 0
    assert result.metadata["size_match"] is True


def test_diff_completely_different(tmp_path):
    """Completely different images → 100% change."""
    a_img = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    b_img = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
    a = tmp_path / "black.png"
    b = tmp_path / "white.png"
    a_img.save(a)
    b_img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out))
    assert result.success
    assert result.metadata["changed_pct"] == 100.0
    assert result.metadata["changed_pixels"] == 2500


def test_diff_partial_change(tmp_path):
    """Half the image changed → ~50% change."""
    a_img = Image.new("RGBA", (100, 100), (100, 100, 100, 255))
    b_img = Image.new("RGBA", (100, 100), (100, 100, 100, 255))
    draw = ImageDraw.Draw(b_img)
    draw.rectangle([0, 0, 50, 100], fill=(255, 0, 0, 255))
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    a_img.save(a)
    b_img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out))
    assert result.success
    pct = result.metadata["changed_pct"]
    assert 40 < pct < 60


def test_diff_different_sizes(tmp_path):
    """Different-sized images still produce output."""
    a_img = Image.new("RGBA", (50, 50), (100, 100, 100, 255))
    b_img = Image.new("RGBA", (80, 60), (100, 100, 100, 255))
    a = tmp_path / "small.png"
    b = tmp_path / "big.png"
    a_img.save(a)
    b_img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out))
    assert result.success
    assert result.width == 80
    assert result.height == 60
    assert result.metadata["size_match"] is False
    assert result.metadata["changed_pixels"] > 0


def test_diff_threshold(tmp_path):
    """High threshold ignores small differences."""
    a_img = Image.new("RGBA", (50, 50), (100, 100, 100, 255))
    b_img = Image.new("RGBA", (50, 50), (105, 100, 100, 255))
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    a_img.save(a)
    b_img.save(b)

    # Default threshold=10 → 5 difference is below threshold
    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out), threshold=10)
    assert result.metadata["changed_pct"] == 0.0

    # Low threshold=3 → 5 difference is above threshold
    out2 = tmp_path / "diff2.png"
    result2 = diff_images(str(a), str(b), str(out2), threshold=3)
    assert result2.metadata["changed_pct"] == 100.0


def test_diff_output_is_valid_image(tmp_path):
    """Output diff is a valid PNG image."""
    a_img = Image.new("RGBA", (30, 30), (200, 0, 0, 255))
    b_img = Image.new("RGBA", (30, 30), (0, 200, 0, 255))
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    a_img.save(a)
    b_img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out))
    assert result.success
    assert out.exists()

    diff_img = Image.open(out)
    assert diff_img.size == (30, 30)


def test_diff_highlight_color(tmp_path):
    """Changed pixels use the specified highlight color."""
    a_img = Image.new("RGBA", (10, 10), (0, 0, 0, 255))
    b_img = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    a_img.save(a)
    b_img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(
        str(a), str(b), str(out),
        highlight_color=(0, 255, 0, 255),
    )
    assert result.success
    diff_img = Image.open(out)
    pixel = diff_img.getpixel((5, 5))
    assert pixel == (0, 255, 0, 255)


def test_diff_file_not_found(tmp_path):
    a = tmp_path / "exists.png"
    Image.new("RGBA", (10, 10)).save(a)

    result = diff_images(str(a), "/nonexistent.png", str(tmp_path / "out.png"))
    assert not result.success


def test_diff_alpha_changes(tmp_path):
    """Detect changes in alpha channel."""
    a_img = Image.new("RGBA", (20, 20), (100, 100, 100, 255))
    b_img = Image.new("RGBA", (20, 20), (100, 100, 100, 0))
    a = tmp_path / "opaque.png"
    b = tmp_path / "transparent.png"
    a_img.save(a)
    b_img.save(b)

    out = tmp_path / "diff.png"
    result = diff_images(str(a), str(b), str(out))
    assert result.success
    assert result.metadata["changed_pct"] == 100.0
