"""Shared fixtures: synthetic Pillow-generated images. No production images."""
import pytest
from PIL import Image, ImageDraw


@pytest.fixture
def black_bg_with_circle(tmp_path):
    """100x100 black bg with 40px white circle in center."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([30, 30, 70, 70], fill=(255, 255, 255, 255))
    path = tmp_path / "circle_on_black.png"
    img.save(path)
    return path


@pytest.fixture
def white_bg_with_red_square(tmp_path):
    """100x100 white bg with 40x40 red square in center."""
    img = Image.new("RGBA", (100, 100), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 70, 70], fill=(255, 0, 0, 255))
    path = tmp_path / "red_on_white.png"
    img.save(path)
    return path


@pytest.fixture
def green_bg_with_art(tmp_path):
    """100x100 bright green bg (#00FF00) with dark blue circle."""
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([25, 25, 75, 75], fill=(20, 30, 80, 255))
    path = tmp_path / "art_on_green.png"
    img.save(path)
    return path


@pytest.fixture
def green_bg_with_trapped_green(tmp_path):
    """100x100 green bg with dark shape that has trapped green patches inside."""
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 255))
    draw = ImageDraw.Draw(img)
    # Dark ring with green hole in center
    draw.ellipse([20, 20, 80, 80], fill=(30, 30, 30, 255))
    draw.ellipse([40, 40, 60, 60], fill=(0, 255, 0, 255))  # trapped green
    path = tmp_path / "trapped_green.png"
    img.save(path)
    return path


@pytest.fixture
def fully_transparent(tmp_path):
    """100x100 fully transparent image."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    path = tmp_path / "transparent.png"
    img.save(path)
    return path


@pytest.fixture
def white_border_sticker(tmp_path):
    """80x80 dark circle with white border ring (simulates AI sticker border)."""
    img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # White border ring
    draw.ellipse([5, 5, 75, 75], fill=(255, 255, 255, 255))
    # Dark artwork inside
    draw.ellipse([12, 12, 68, 68], fill=(50, 50, 120, 255))
    path = tmp_path / "white_border.png"
    img.save(path)
    return path


@pytest.fixture
def two_component_image(tmp_path):
    """100x100 with two separate opaque shapes (disconnected)."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, 25, 25], fill=(255, 0, 0, 255))
    draw.rectangle([70, 70, 95, 95], fill=(0, 0, 255, 255))
    path = tmp_path / "two_shapes.png"
    img.save(path)
    return path


@pytest.fixture
def solid_black(tmp_path):
    """50x50 solid black image."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    path = tmp_path / "solid_black.png"
    img.save(path)
    return path


@pytest.fixture
def pre_transparent_green(tmp_path):
    """100x100 where green pixels already have alpha=0 (OpenAI pre-removal)."""
    img = Image.new("RGBA", (100, 100), (0, 255, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([25, 25, 75, 75], fill=(200, 50, 50, 255))
    path = tmp_path / "pre_transparent.png"
    img.save(path)
    return path
