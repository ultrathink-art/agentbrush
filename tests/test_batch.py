"""Tests for batch processing module."""
import os

from PIL import Image, ImageDraw

from agentbrush.batch.ops import batch_process


def _create_test_images(dir_path, count=3, size=(50, 50)):
    """Helper: create N simple test images in a directory."""
    paths = []
    for i in range(count):
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        color = ((i * 80) % 255, (i * 50 + 100) % 255, 200, 255)
        draw.rectangle([10, 10, 40, 40], fill=color)
        path = dir_path / f"image_{i:02d}.png"
        img.save(path)
        paths.append(path)
    return paths


def test_batch_validate(tmp_path):
    """Batch validate with a preset."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    _create_test_images(input_dir, count=3)

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="validate",
        preset="thumbnail",
    )
    assert result.success
    assert result.metadata["total"] == 3
    assert result.metadata["operation"] == "validate"


def test_batch_crop(tmp_path):
    """Batch crop images."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    _create_test_images(input_dir, count=2, size=(100, 100))

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="crop",
        padding=5,
    )
    assert result.success
    assert result.metadata["processed"] == 2
    # Verify output files exist
    out_files = list(output_dir.iterdir())
    assert len(out_files) == 2


def test_batch_resize(tmp_path):
    """Batch resize images."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    _create_test_images(input_dir, count=2)

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="resize",
        width=200,
        height=200,
    )
    assert result.success
    assert result.metadata["processed"] == 2

    for f in output_dir.iterdir():
        img = Image.open(f)
        assert img.width == 200
        assert img.height == 200


def test_batch_remove_bg(tmp_path):
    """Batch background removal."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    for i in range(2):
        img = Image.new("RGBA", (50, 50), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, 40, 40], fill=(255, 100, 100, 255))
        img.save(input_dir / f"img_{i}.png")

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="remove-bg",
        color="black",
    )
    assert result.success
    assert result.metadata["processed"] == 2


def test_batch_empty_dir(tmp_path):
    """Empty directory → error."""
    input_dir = tmp_path / "empty"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    result = batch_process(str(input_dir), str(output_dir))
    assert not result.success
    assert "No images" in result.errors[0]


def test_batch_nonexistent_dir(tmp_path):
    result = batch_process("/nonexistent", str(tmp_path / "output"))
    assert not result.success


def test_batch_skips_non_images(tmp_path):
    """Non-image files are skipped."""
    input_dir = tmp_path / "mixed"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    _create_test_images(input_dir, count=1)
    (input_dir / "readme.txt").write_text("not an image")
    (input_dir / "data.json").write_text("{}")

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="crop",
    )
    assert result.success
    assert result.metadata["total"] == 1


def test_batch_per_file_results(tmp_path):
    """Per-file results included in metadata."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    _create_test_images(input_dir, count=2)

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="crop",
    )
    assert "results" in result.metadata
    assert len(result.metadata["results"]) == 2
    for fr in result.metadata["results"]:
        assert "file" in fr
        assert "success" in fr


def test_batch_unknown_operation(tmp_path):
    """Unknown operation → all files fail."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    _create_test_images(input_dir, count=1)

    result = batch_process(
        str(input_dir), str(output_dir),
        operation="nonexistent",
    )
    assert result.metadata["failed"] == 1
