"""Tests for validate module (port of bin/design-qa)."""
from PIL import Image, ImageDraw

from agentbrush.validate.ops import (
    validate_design, compare_images, detect_product_type, PRODUCT_SPECS,
)


def test_detect_product_type():
    assert detect_product_type("my_tshirt_design.png") == "tshirt"
    assert detect_product_type("cool_hoodie.png") == "hoodie"
    assert detect_product_type("sticker_cat.png") == "sticker"
    assert detect_product_type("desk_mat_vim.png") == "deskmat"
    assert detect_product_type("poster_art.png") == "poster"
    assert detect_product_type("random_image.png") is None
    assert detect_product_type("coffee_mug.png") == "mug"


def test_validate_sticker_pass(tmp_path):
    """Valid sticker: near-square, transparent bg, complex artwork."""
    img = Image.new("RGBA", (1664, 1664), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Complex illustration
    for i in range(0, 1200, 30):
        draw.ellipse(
            [200 + i % 400, 200 + i % 300, 250 + i % 400, 250 + i % 300],
            fill=(i % 255, (i * 3) % 255, (i * 7) % 255, 255),
        )
    path = tmp_path / "good_sticker.png"
    img.save(path)

    result = validate_design(str(path), product_type="sticker")
    assert result.success
    assert result.metadata["product_type"] == "sticker"


def test_validate_sticker_poster_layout_fail(tmp_path):
    """Sticker with rectangular bg should HARD FAIL."""
    img = Image.new("RGBA", (1664, 1664), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Colored rectangle filling most of the canvas
    draw.rounded_rectangle(
        [50, 50, 1614, 1614], radius=30,
        fill=(100, 150, 200, 255),
    )
    path = tmp_path / "poster_sticker.png"
    img.save(path)

    result = validate_design(str(path), product_type="sticker")
    assert not result.success
    assert any("POSTER LAYOUT" in e for e in result.errors)


def test_validate_tshirt_transparent(tmp_path):
    """Valid tshirt: has transparent background."""
    img = Image.new("RGBA", (4500, 5400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([500, 500, 4000, 4900], fill=(255, 100, 50, 255))
    path = tmp_path / "good_tee.png"
    img.save(path)

    result = validate_design(str(path), product_type="tshirt")
    assert result.success


def test_validate_tshirt_no_transparency(tmp_path):
    """Tshirt without transparency should fail."""
    img = Image.new("RGBA", (4500, 5400), (0, 0, 0, 255))
    path = tmp_path / "bad_tee.png"
    img.save(path)

    result = validate_design(str(path), product_type="tshirt")
    assert not result.success
    assert any("TRANSPARENCY" in e for e in result.errors)


def test_validate_wrong_aspect_ratio(tmp_path):
    """Wrong aspect ratio should error."""
    img = Image.new("RGBA", (1000, 5000), (0, 0, 0, 0))
    path = tmp_path / "narrow.png"
    img.save(path)

    result = validate_design(str(path), product_type="tshirt")
    assert not result.success
    assert any("ASPECT RATIO" in e for e in result.errors)


def test_validate_dimension_warning(tmp_path):
    """Dimensions outside tolerance should warn."""
    img = Image.new("RGBA", (2000, 2400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 1900, 2300], fill=(255, 0, 0, 255))
    path = tmp_path / "small_tee.png"
    img.save(path)

    result = validate_design(str(path), product_type="tshirt")
    assert any("DIMENSIONS" in w for w in result.warnings)


def test_validate_low_resolution(tmp_path):
    """Low resolution should warn."""
    img = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 450, 450], fill=(255, 0, 0, 255))
    path = tmp_path / "small_sticker.png"
    img.save(path)

    result = validate_design(str(path), product_type="sticker")
    assert any("RESOLUTION" in w for w in result.warnings)


def test_validate_auto_detect_type(tmp_path):
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    path = tmp_path / "my_sticker_design.png"
    img.save(path)

    result = validate_design(str(path))
    assert result.metadata["product_type"] == "sticker"


def test_validate_unknown_type(tmp_path):
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    path = tmp_path / "random.png"
    img.save(path)

    result = validate_design(str(path))
    assert result.success  # unknown type = no spec to check against
    assert result.metadata["product_type"] == "unknown"


def test_validate_file_not_found():
    result = validate_design("/nonexistent.png")
    assert not result.success


def test_validate_poster_no_transparency_needed(tmp_path):
    """Poster does not require transparency."""
    img = Image.new("RGBA", (5400, 7200), (30, 30, 30, 255))
    path = tmp_path / "poster.png"
    img.save(path)

    result = validate_design(str(path), product_type="poster")
    # Should not fail for transparency
    transparency_errors = [e for e in result.errors if "TRANSPARENCY" in e]
    assert len(transparency_errors) == 0


def test_compare_images_pass(tmp_path):
    """Small pixel loss should pass."""
    src = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    proc = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    # Remove a few pixels
    proc_px = proc.load()
    for x in range(5):
        proc_px[x, 0] = (0, 0, 0, 0)
    src_path = tmp_path / "src.png"
    proc_path = tmp_path / "proc.png"
    src.save(src_path)
    proc.save(proc_path)

    result = compare_images(str(src_path), str(proc_path))
    assert result.success
    assert result.metadata["loss_pct"] < 10


def test_compare_images_fail(tmp_path):
    """Large pixel loss should fail."""
    src = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    proc = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    # Most pixels removed
    src_path = tmp_path / "src.png"
    proc_path = tmp_path / "proc.png"
    src.save(src_path)
    proc.save(proc_path)

    result = compare_images(str(src_path), str(proc_path))
    assert not result.success
    assert result.metadata["loss_pct"] > 90


def test_compare_file_not_found(tmp_path):
    result = compare_images("/missing.png", "/also_missing.png")
    assert not result.success


def test_product_specs_complete():
    """All expected product types should be in specs."""
    expected = {"tshirt", "hoodie", "hat", "mug", "sticker", "deskmat", "poster", "tote"}
    assert set(PRODUCT_SPECS.keys()) == expected
