"""Tests for geometry operations."""
from PIL import Image, ImageDraw

from agentbrush.core.geometry import find_artwork_bounds, crop_to_content, find_opaque_centroid


def test_find_artwork_bounds():
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 30, 60, 70], fill=(255, 0, 0, 255))
    bounds = find_artwork_bounds(img)
    assert bounds[0] == 20  # min_x
    assert bounds[1] == 30  # min_y
    assert bounds[2] == 61  # max_x + 1
    assert bounds[3] == 71  # max_y + 1


def test_find_artwork_bounds_empty():
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    bounds = find_artwork_bounds(img)
    assert bounds == (0, 0, 50, 50)


def test_crop_to_content():
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 40, 40], fill=(255, 0, 0, 255))
    cropped = crop_to_content(img)
    assert cropped.width == 21
    assert cropped.height == 21


def test_crop_to_content_with_padding():
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 40, 40], fill=(255, 0, 0, 255))
    cropped = crop_to_content(img, padding=5)
    assert cropped.width == 31
    assert cropped.height == 31


def test_find_opaque_centroid():
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Square at top-left corner
    draw.rectangle([0, 0, 20, 20], fill=(255, 0, 0, 255))
    cx, cy = find_opaque_centroid(img)
    assert cx == 10
    assert cy == 10


def test_find_opaque_centroid_region():
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 20, 20], fill=(255, 0, 0, 255))
    draw.rectangle([60, 60, 80, 80], fill=(0, 0, 255, 255))
    # Only look at bottom-right region
    cx, cy = find_opaque_centroid(img, region=(50, 50, 100, 100))
    assert cx >= 60
    assert cy >= 60


def test_find_opaque_centroid_empty():
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    cx, cy = find_opaque_centroid(img)
    assert cx == 25
    assert cy == 25
