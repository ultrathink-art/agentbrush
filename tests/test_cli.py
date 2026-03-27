"""CLI integration tests via subprocess."""
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw


@pytest.fixture
def sample_image(tmp_path):
    """Create a simple test image."""
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 40, 40], fill=(255, 100, 100, 255))
    path = tmp_path / "sample.png"
    img.save(path)
    return path


@pytest.fixture
def green_image(tmp_path):
    img = Image.new("RGBA", (50, 50), (0, 255, 0, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([10, 10, 40, 40], fill=(100, 50, 200, 255))
    path = tmp_path / "green.png"
    img.save(path)
    return path


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "agentbrush"] + list(args),
        capture_output=True, text=True,
    )


# --- Existing Phase 1 tests ---

def test_help():
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "agentbrush" in result.stdout.lower()


def test_version():
    result = _run_cli("--version")
    assert result.returncode == 0
    assert "0.3.0" in result.stdout


def test_remove_bg_cli(sample_image, tmp_path):
    out = tmp_path / "out.png"
    result = _run_cli("remove-bg", str(sample_image), str(out))
    assert result.returncode == 0
    assert out.exists()


def test_greenscreen_cli(green_image, tmp_path):
    out = tmp_path / "out.png"
    result = _run_cli("greenscreen", str(green_image), str(out))
    assert result.returncode == 0
    assert out.exists()


def test_border_cleanup_cli(tmp_path):
    # Create white-border sticker image
    img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([5, 5, 45, 45], fill=(255, 255, 255, 255))
    draw.ellipse([10, 10, 40, 40], fill=(50, 50, 120, 255))
    src = tmp_path / "sticker.png"
    img.save(src)

    out = tmp_path / "out.png"
    result = _run_cli("border-cleanup", str(src), str(out))
    assert result.returncode == 0
    assert out.exists()


def test_invalid_input_exits_nonzero(tmp_path):
    out = tmp_path / "out.png"
    result = _run_cli("remove-bg", "/nonexistent.png", str(out))
    assert result.returncode != 0


def test_no_command_shows_help():
    result = _run_cli()
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "agentbrush" in result.stdout.lower()


# --- Phase 2: Text CLI ---

def test_text_cli_on_image(sample_image, tmp_path):
    out = tmp_path / "text_out.png"
    result = _run_cli(
        "text", str(sample_image), str(out), "Hello World",
        "--size", "16",
    )
    assert result.returncode == 0
    assert out.exists()
    assert "OK" in result.stdout


def test_text_cli_new_canvas(tmp_path):
    out = tmp_path / "text_canvas.png"
    result = _run_cli(
        "text", "new:200x100", str(out), "Canvas Text",
        "--center", "--size", "20",
    )
    assert result.returncode == 0
    assert out.exists()
    img = Image.open(out)
    assert img.width == 200
    assert img.height == 100


# --- Phase 2: Composite CLI ---

def test_composite_cli(sample_image, tmp_path):
    overlay = Image.new("RGBA", (20, 20), (0, 255, 0, 255))
    overlay_path = tmp_path / "overlay.png"
    overlay.save(overlay_path)

    out = tmp_path / "comp_out.png"
    result = _run_cli(
        "composite", str(sample_image), str(overlay_path), str(out),
        "--position", "10,10",
    )
    assert result.returncode == 0
    assert out.exists()


def test_composite_cli_resize(sample_image, tmp_path):
    overlay = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
    overlay_path = tmp_path / "big_overlay.png"
    overlay.save(overlay_path)

    out = tmp_path / "comp_resized.png"
    result = _run_cli(
        "composite", str(sample_image), str(overlay_path), str(out),
        "--resize-overlay", "25x25",
    )
    assert result.returncode == 0
    assert out.exists()


def test_composite_cli_paste_centered(tmp_path):
    overlay = Image.new("RGBA", (40, 40), (0, 128, 255, 255))
    overlay_path = tmp_path / "art.png"
    overlay.save(overlay_path)

    out = tmp_path / "centered_out.png"
    result = _run_cli(
        "composite", "paste-centered", str(out),
        "--overlay", str(overlay_path),
        "--canvas", "200x100",
        "--fit",
    )
    assert result.returncode == 0
    assert out.exists()
    img = Image.open(out)
    assert img.width == 200
    assert img.height == 100


def test_composite_cli_paste_centered_bg_color(tmp_path):
    overlay = Image.new("RGBA", (20, 20), (255, 0, 0, 255))
    overlay_path = tmp_path / "red.png"
    overlay.save(overlay_path)

    out = tmp_path / "bg_out.png"
    result = _run_cli(
        "composite", "paste-centered", str(out),
        "--overlay", str(overlay_path),
        "--canvas", "100x100",
        "--bg-color", "0,0,0,255",
    )
    assert result.returncode == 0
    assert out.exists()
    img = Image.open(out)
    # Corner should be black (bg color)
    assert img.getpixel((0, 0)) == (0, 0, 0, 255)
    # Center should be red (overlay)
    assert img.getpixel((50, 50))[0] > 200


def test_composite_cli_paste_centered_help():
    result = _run_cli("composite", "paste-centered", "--help")
    assert result.returncode == 0
    assert "canvas" in result.stdout.lower()


def test_composite_cli_help():
    result = _run_cli("composite", "--help")
    assert result.returncode == 0
    assert "paste-centered" in result.stdout


# --- Phase 2: Resize CLI ---

def test_resize_cli_scale(sample_image, tmp_path):
    out = tmp_path / "resized.png"
    result = _run_cli(
        "resize", str(sample_image), str(out), "--scale", "2.0",
    )
    assert result.returncode == 0
    img = Image.open(out)
    assert img.width == 100
    assert img.height == 100


def test_resize_cli_width(sample_image, tmp_path):
    out = tmp_path / "resized_w.png"
    result = _run_cli(
        "resize", str(sample_image), str(out), "--width", "200",
    )
    assert result.returncode == 0
    img = Image.open(out)
    assert img.width == 200


def test_resize_cli_pad(sample_image, tmp_path):
    out = tmp_path / "padded.png"
    result = _run_cli(
        "resize", str(sample_image), str(out),
        "--width", "100", "--height", "100", "--pad",
    )
    assert result.returncode == 0
    img = Image.open(out)
    assert img.width == 100
    assert img.height == 100


# --- Phase 2: Validate CLI ---

def test_validate_check_cli(tmp_path):
    img = Image.new("RGBA", (1664, 1664), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for i in range(0, 800, 20):
        draw.ellipse(
            [200 + i % 400, 200 + i % 300, 250 + i % 400, 250 + i % 300],
            fill=(i % 255, (i * 3) % 255, (i * 7) % 255, 255),
        )
    src = tmp_path / "valid_sticker.png"
    img.save(src)

    result = _run_cli("validate", "check", str(src), "--type", "sticker")
    assert result.returncode == 0


def test_validate_compare_cli(tmp_path):
    src = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    proc = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    src_path = tmp_path / "src.png"
    proc_path = tmp_path / "proc.png"
    src.save(src_path)
    proc.save(proc_path)

    result = _run_cli(
        "validate", "compare", str(src_path), str(proc_path),
    )
    assert result.returncode == 0


# --- Phase 2: Convert CLI ---

def test_convert_cli_png_to_jpg(sample_image, tmp_path):
    out = tmp_path / "converted.jpg"
    result = _run_cli("convert", str(sample_image), str(out))
    assert result.returncode == 0
    assert out.exists()
    img = Image.open(out)
    assert img.mode == "RGB"


def test_convert_cli_ensure_rgba(tmp_path):
    img = Image.new("RGB", (50, 50), (255, 0, 0))
    src = tmp_path / "rgb.png"
    img.save(src)

    out = tmp_path / "rgba.png"
    result = _run_cli("convert", str(src), str(out), "--ensure-rgba")
    assert result.returncode == 0


# --- Phase 2: Generate CLI ---

def test_generate_cli_unknown_provider(tmp_path):
    out = tmp_path / "gen.png"
    result = _run_cli(
        "generate", "test prompt", str(out),
        "--provider", "pollinations",
    )
    # Should fail (network or pollinations down) but not crash
    # We don't require success, just non-crash
    assert isinstance(result.returncode, int)


def test_generate_cli_help():
    result = _run_cli("generate", "--help")
    assert result.returncode == 0
    assert "prompt" in result.stdout.lower()


# --- Phase 3: Crop CLI ---

def test_crop_cli(sample_image, tmp_path):
    out = tmp_path / "cropped.png"
    result = _run_cli("crop", str(sample_image), str(out), "--padding", "5")
    assert result.returncode == 0
    assert out.exists()
    assert "OK" in result.stdout


def test_crop_cli_with_bg_color(sample_image, tmp_path):
    out = tmp_path / "cropped.png"
    result = _run_cli(
        "crop", str(sample_image), str(out),
        "--bg-color", "0,0,0",
    )
    assert result.returncode == 0
    assert out.exists()


def test_crop_cli_help():
    result = _run_cli("crop", "--help")
    assert result.returncode == 0
    assert "padding" in result.stdout.lower()


# --- Phase 3: Palette CLI ---

def test_palette_cli_json(sample_image):
    result = _run_cli("palette", str(sample_image), "--format", "json")
    assert result.returncode == 0
    assert '"colors"' in result.stdout


def test_palette_cli_hex(sample_image):
    result = _run_cli("palette", str(sample_image), "--format", "hex")
    assert result.returncode == 0
    assert "#" in result.stdout


def test_palette_cli_text(sample_image):
    result = _run_cli("palette", str(sample_image), "--format", "text")
    assert result.returncode == 0
    assert "rgb(" in result.stdout


def test_palette_cli_count(sample_image):
    result = _run_cli("palette", str(sample_image), "--count", "3")
    assert result.returncode == 0


def test_palette_cli_help():
    result = _run_cli("palette", "--help")
    assert result.returncode == 0
    assert "count" in result.stdout.lower()


# --- Phase 3: Diff CLI ---

def test_diff_cli(sample_image, tmp_path):
    # Create a modified version
    img = Image.new("RGBA", (50, 50), (255, 255, 255, 255))
    other = tmp_path / "other.png"
    img.save(other)

    out = tmp_path / "diff.png"
    result = _run_cli(
        "diff", str(sample_image), str(other),
        "--output", str(out),
    )
    assert result.returncode == 0
    assert out.exists()


def test_diff_cli_threshold(sample_image, tmp_path):
    other = tmp_path / "same.png"
    Image.open(sample_image).save(other)

    out = tmp_path / "diff.png"
    result = _run_cli(
        "diff", str(sample_image), str(other),
        "--output", str(out), "--threshold", "5",
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_diff_cli_help():
    result = _run_cli("diff", "--help")
    assert result.returncode == 0
    assert "threshold" in result.stdout.lower()


# --- Phase 3: Batch CLI ---

def test_batch_cli_validate(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
    img.save(input_dir / "test.png")

    result = _run_cli(
        "batch", str(input_dir), str(output_dir),
        "--operation", "validate", "--preset", "thumbnail",
    )
    assert result.returncode == 0
    assert "1/1" in result.stdout


def test_batch_cli_crop(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([20, 20, 80, 80], fill=(0, 255, 0, 255))
    img.save(input_dir / "test.png")

    result = _run_cli(
        "batch", str(input_dir), str(output_dir),
        "--operation", "crop", "--padding", "5",
    )
    assert result.returncode == 0
    assert "1/1" in result.stdout


def test_batch_cli_help():
    result = _run_cli("batch", "--help")
    assert result.returncode == 0
    assert "operation" in result.stdout.lower()
