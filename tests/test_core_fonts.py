"""Tests for cross-platform font discovery."""
from PIL import ImageFont

from agentbrush.core.fonts import find_font


def test_find_bundled_space_mono():
    font = find_font("mono", size=24)
    assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))


def test_find_bundled_space_mono_bold():
    font = find_font("mono", size=24, bold=True)
    assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))


def test_find_by_alias():
    for alias in ["space", "space-bold", "jetbrains", "dejavu"]:
        font = find_font(alias, size=20)
        assert font is not None


def test_find_fallback_for_unknown():
    """Unknown font name should fall back to Pillow default, not crash."""
    font = find_font("NonExistentFontXYZ123", size=16)
    assert font is not None


def test_find_by_filename():
    """Direct filename should work if bundled."""
    font = find_font("SpaceMono-Regular.ttf", size=20)
    assert isinstance(font, (ImageFont.FreeTypeFont, ImageFont.ImageFont))
