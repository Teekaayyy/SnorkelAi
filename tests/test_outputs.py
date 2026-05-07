"""Tests for the imagemagick-pipeline-processor task."""

import hashlib
import subprocess
from pathlib import Path

IMAGES = ["image_1.png", "image_2.png", "image_3.png"]
RESIZED_DIR = Path("/app/output/resized")
WATERMARKED_DIR = Path("/app/output/watermarked")
CONTACT_SHEET = Path("/app/output/contact_sheet.png")


def test_pipeline_script_exists() -> None:
    """Verify that /app/pipeline.py exists."""
    assert Path("/app/pipeline.py").exists(), "pipeline.py not found at /app/pipeline.py"


def test_resized_directory_exists() -> None:
    """Verify that /app/output/resized/ was created."""
    assert RESIZED_DIR.is_dir(), f"{RESIZED_DIR} does not exist"


def test_all_resized_files_present() -> None:
    """Verify all 3 resized images exist with original filenames."""
    for name in IMAGES:
        assert (RESIZED_DIR / name).exists(), f"Missing resized file: {name}"


def test_resized_dimensions_are_800x600() -> None:
    """Verify every resized image is exactly 800x600 pixels."""
    for name in IMAGES:
        result = subprocess.run(
            ["identify", "-format", "%wx%h", str(RESIZED_DIR / name)],
            capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip() == "800x600", \
            f"{name}: expected 800x600, got {result.stdout.strip()}"


def test_resized_files_are_png() -> None:
    """Verify every resized output file is PNG format."""
    for name in IMAGES:
        result = subprocess.run(
            ["identify", "-format", "%m", str(RESIZED_DIR / name)],
            capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip() == "PNG", \
            f"{name}: expected PNG, got {result.stdout.strip()}"


def test_watermarked_directory_exists() -> None:
    """Verify that /app/output/watermarked/ was created."""
    assert WATERMARKED_DIR.is_dir(), f"{WATERMARKED_DIR} does not exist"


def test_all_watermarked_files_present() -> None:
    """Verify all 3 watermarked images exist with original filenames."""
    for name in IMAGES:
        assert (WATERMARKED_DIR / name).exists(), f"Missing watermarked file: {name}"


def test_watermarked_files_are_png() -> None:
    """Verify every watermarked output file is PNG format."""
    for name in IMAGES:
        result = subprocess.run(
            ["identify", "-format", "%m", str(WATERMARKED_DIR / name)],
            capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip() == "PNG", \
            f"{name}: expected PNG, got {result.stdout.strip()}"


def test_watermarked_differs_from_resized() -> None:
    """Verify each watermarked image differs from its resized source — watermark must be present."""
    for name in IMAGES:
        wm = hashlib.md5((WATERMARKED_DIR / name).read_bytes()).hexdigest()
        rs = hashlib.md5((RESIZED_DIR / name).read_bytes()).hexdigest()
        assert wm != rs, f"{name}: watermarked file identical to resized — watermark not applied"


def test_watermarked_dimensions_preserved() -> None:
    """Verify watermarking did not alter the 800x600 dimensions."""
    for name in IMAGES:
        result = subprocess.run(
            ["identify", "-format", "%wx%h", str(WATERMARKED_DIR / name)],
            capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip() == "800x600", \
            f"{name}: dimensions changed after watermarking: {result.stdout.strip()}"


def test_contact_sheet_exists() -> None:
    """Verify the contact sheet was created at /app/output/contact_sheet.png."""
    assert CONTACT_SHEET.exists(), "contact_sheet.png not found"


def test_contact_sheet_is_png() -> None:
    """Verify the contact sheet is PNG format."""
    result = subprocess.run(
        ["identify", "-format", "%m", str(CONTACT_SHEET)],
        capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "PNG", f"Expected PNG, got {result.stdout.strip()}"


def test_contact_sheet_width_confirms_3_columns() -> None:
    """Verify the contact sheet is wider than a single image, confirming 3-column layout."""
    result = subprocess.run(
        ["identify", "-format", "%w", str(CONTACT_SHEET)],
        capture_output=True, text=True, check=True,
    )
    width = int(result.stdout.strip())
    assert width > 800, \
        f"Contact sheet width {width}px not wider than a single image — 3-column layout may be missing"


def test_contact_sheet_not_empty() -> None:
    """Verify the contact sheet file is not suspiciously small."""
    assert CONTACT_SHEET.stat().st_size > 10_000, "Contact sheet is suspiciously small"


def test_contact_sheet_differs_from_any_single_image() -> None:
    """Verify the contact sheet is not identical to any individual watermarked image."""
    sheet_hash = hashlib.md5(CONTACT_SHEET.read_bytes()).hexdigest()
    for name in IMAGES:
        img_hash = hashlib.md5((WATERMARKED_DIR / name).read_bytes()).hexdigest()
        assert sheet_hash != img_hash, \
            f"Contact sheet is identical to {name} — montage may not have run"