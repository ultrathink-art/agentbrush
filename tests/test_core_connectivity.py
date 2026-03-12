"""Tests for die-cut connectivity (single shape verification)."""
from PIL import Image, ImageDraw

from agentbrush.core.connectivity import ensure_single_shape, count_components


def test_single_shape_keeps_largest(two_component_image):
    img = Image.open(two_component_image).convert("RGBA")
    result, removed = ensure_single_shape(img)
    assert removed > 0
    # Should have exactly 1 component remaining
    sizes = count_components(result)
    assert len(sizes) == 1


def test_count_components_two_shapes(two_component_image):
    img = Image.open(two_component_image).convert("RGBA")
    sizes = count_components(img)
    assert len(sizes) == 2


def test_single_shape_noop_for_connected():
    """Single connected shape should not lose any pixels."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([5, 5, 45, 45], fill=(255, 0, 0, 255))
    result, removed = ensure_single_shape(img)
    assert removed == 0


def test_count_components_empty():
    """Fully transparent should have 0 components."""
    img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    sizes = count_components(img)
    assert len(sizes) == 0


def test_ensure_single_shape_empty():
    img = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    result, removed = ensure_single_shape(img)
    assert removed == 0


def test_three_components():
    """Three disconnected shapes — keep largest, remove two."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, 15, 15], fill=(255, 0, 0, 255))     # small
    draw.rectangle([30, 30, 70, 70], fill=(0, 255, 0, 255))    # large
    draw.rectangle([80, 80, 90, 90], fill=(0, 0, 255, 255))    # small
    sizes = count_components(img)
    assert len(sizes) == 3

    result, removed = ensure_single_shape(img)
    sizes_after = count_components(result)
    assert len(sizes_after) == 1
    assert removed > 0
