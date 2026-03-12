"""Tests for core flood fill primitives."""
from PIL import Image

from agentbrush.core.flood_fill import flood_fill_from_edges
from agentbrush.core.color import is_near_color


def test_flood_fill_black_bg(black_bg_with_circle):
    img = Image.open(black_bg_with_circle).convert("RGBA")
    result, removed = flood_fill_from_edges(img, target_color=(0, 0, 0), threshold=25)
    assert removed > 0
    pixels = result.load()
    # Center of white circle should be preserved
    assert pixels[50, 50][3] > 0
    # Corner (was black bg) should be transparent
    assert pixels[0, 0][3] == 0


def test_flood_fill_preserves_interior_black():
    """Black outlines inside artwork must NOT be removed."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    pixels = img.load()
    # Create a colored border around center black
    for x in range(50):
        for y in range(50):
            if 10 <= x <= 40 and 10 <= y <= 40:
                pixels[x, y] = (200, 100, 50, 255)  # colored artwork
    # Put black pixels inside artwork (internal detail)
    for x in range(20, 30):
        for y in range(20, 30):
            pixels[x, y] = (0, 0, 0, 255)

    result, removed = flood_fill_from_edges(img, target_color=(0, 0, 0), threshold=25)
    result_pixels = result.load()
    # Internal black should be preserved (not connected to edge)
    assert result_pixels[25, 25][3] > 0
    # Edge black removed
    assert result_pixels[0, 0][3] == 0


def test_flood_fill_8_connected():
    """8-connectivity should remove diagonal-connected pixels."""
    img = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    pixels = img.load()
    # Place black pixels diagonally from corner
    pixels[0, 0] = (0, 0, 0, 255)
    pixels[1, 1] = (0, 0, 0, 255)
    pixels[2, 2] = (0, 0, 0, 255)

    result, removed = flood_fill_from_edges(
        img, target_color=(0, 0, 0), threshold=25, connectivity=8
    )
    assert removed == 3
    result_pixels = result.load()
    assert result_pixels[0, 0][3] == 0
    assert result_pixels[2, 2][3] == 0


def test_flood_fill_4_connected_stops_at_diagonal():
    """4-connectivity should NOT follow diagonal connections."""
    img = Image.new("RGBA", (10, 10), (255, 255, 255, 255))
    pixels = img.load()
    pixels[0, 0] = (0, 0, 0, 255)
    pixels[1, 1] = (0, 0, 0, 255)  # diagonal only

    result, removed = flood_fill_from_edges(
        img, target_color=(0, 0, 0), threshold=25, connectivity=4
    )
    # Only corner pixel removed (diagonal not followed)
    assert removed == 1
    result_pixels = result.load()
    assert result_pixels[0, 0][3] == 0
    assert result_pixels[1, 1][3] > 0


def test_flood_fill_custom_fn():
    """Custom color test function should work."""
    img = Image.new("RGBA", (20, 20), (100, 200, 100, 255))
    # Use custom green test
    result, removed = flood_fill_from_edges(
        img, color_test_fn=lambda px: px[1] > 150
    )
    assert removed == 20 * 20


def test_flood_fill_no_match():
    """If no edge pixels match, nothing should be removed."""
    img = Image.new("RGBA", (20, 20), (255, 0, 0, 255))
    result, removed = flood_fill_from_edges(
        img, target_color=(0, 0, 0), threshold=25
    )
    assert removed == 0
