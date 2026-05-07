"""Tests for the imagemagick-pipeline-processor task."""

import hashlib
import subprocess
from pathlib import Path

IMAGES = ["image_1.png", "image_2.png", "image_3.png"]
RESIZED_DIR = Path("/app/output/resized")
WATERMARKED_DIR = Path("/app/output/watermarked")
CONTACT_SHEET = Path("/app/output/contact_sheet.png")


def test_pipeline_runs_cleanly() -> None:
    """Wipe all outputs and run pipeline.py from scratch — it must exit 0.

    This ensures agents fix the pipeline code itself rather than producing
    correct output files through other means.
    """
    subprocess.run(["rm", "-rf", "/app/output"], check=True)
    result = subprocess.run(
        ["python", "/app/pipeline.py"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"pipeline.py exited with code {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_resized_directory_exists() -> None:
    """Verify that /app/output/resized/ was created by the pipeline."""
    assert RESIZED_DIR.is_dir(), f"{RESIZED_DIR} does not exist"


def test_all_resized_files_present() -> None:
    """Verify all 3 resized images exist as PNG files with original filenames."""
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
    """Verify that /app/output/watermarked/ was created by the pipeline."""
    assert WATERMARKED_DIR.is_dir(), f"{WATERMARKED_DIR} does not exist"


def test_all_watermarked_files_present() -> None:
    """Verify all 3 watermarked images exist as PNG files with original filenames."""
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
    """Verify each watermarked image differs from its resized source."""
    for name in IMAGES:
        wm = hashlib.md5((WATERMARKED_DIR / name).read_bytes()).hexdigest()
        rs = hashlib.md5((RESIZED_DIR / name).read_bytes()).hexdigest()
        assert wm != rs, \
            f"{name}: watermarked file identical to resized — watermark not applied"


def test_watermark_text_correct_via_ocr() -> None:
    """Verify the exact text 'IMAGES_YES' appears in each watermarked image using OCR.

    Runs tesseract on each watermarked image and checks that the extracted
    text contains 'IMAGES_YES'. Catches invisible character substitutions
    (e.g. non-breaking space instead of underscore) and rotated text that
    OCR cannot read reliably.
    """
    for name in IMAGES:
        result = subprocess.run(
            ["tesseract", str(WATERMARKED_DIR / name), "stdout", "--psm", "3"],
            capture_output=True, text=True, check=True,
        )
        ocr_text = result.stdout.strip().replace("\n", " ").replace("  ", " ")
        assert "IMAGES_YES" in ocr_text, (
            f"{name}: OCR output '{ocr_text}' does not contain 'IMAGES_YES' — "
            "watermark text may be wrong, rotated, or contain hidden characters"
        )


def test_watermark_in_center_region() -> None:
    """Verify the watermark is visible in the center region of each image.

    Computes mean pixel difference between watermarked and resized images
    in a 200x100 center crop. A correctly centered watermark produces a
    measurable brightness difference. A corner-placed or fully transparent
    watermark produces near-zero difference in the center region.
    """
    for name in IMAGES:
        result = subprocess.run(
            [
                "convert",
                str(WATERMARKED_DIR / name),
                str(RESIZED_DIR / name),
                "-compose", "Difference",
                "-composite",
                "-crop", "200x100+300+250",
                "+repage",
                "-format", "%[fx:mean]",
                "info:",
            ],
            capture_output=True, text=True, check=True,
        )
        mean_diff = float(result.stdout.strip())
        assert mean_diff > 0.05, (
            f"{name}: center region mean pixel diff is {mean_diff:.4f} — "
            "watermark may be transparent, rotated off-center, or missing"
        )


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
    assert result.stdout.strip() == "PNG", \
        f"Expected PNG, got {result.stdout.strip()}"


def test_contact_sheet_is_3_columns() -> None:
    """Verify the contact sheet width confirms exactly a 3-column layout.

    Three 800px-wide images with +5+5 geometry produce ~2410-2430px width.
    A 1-column sheet is ~810px and a 2-column sheet ~1620px.
    Asserting width >= 2400 rules out both incorrect layouts.
    """
    result = subprocess.run(
        ["identify", "-format", "%w", str(CONTACT_SHEET)],
        capture_output=True, text=True, check=True,
    )
    width = int(result.stdout.strip())
    assert width >= 2400, (
        f"Contact sheet width {width}px too narrow for 3-column layout "
        f"(expected >= 2400px from 3x 800px tiles + padding)"
    )
    assert width <= 2500, (
        f"Contact sheet width {width}px unexpectedly wide — check tile dimensions"
    )


def test_contact_sheet_not_empty() -> None:
    """Verify the contact sheet file is not suspiciously small."""
    assert CONTACT_SHEET.stat().st_size > 10_000, \
        "Contact sheet is suspiciously small — may be blank or corrupt"


def test_contact_sheet_differs_from_any_single_image() -> None:
    """Verify the contact sheet is not identical to any individual watermarked image."""
    sheet_hash = hashlib.md5(CONTACT_SHEET.read_bytes()).hexdigest()
    for name in IMAGES:
        img_hash = hashlib.md5((WATERMARKED_DIR / name).read_bytes()).hexdigest()
        assert sheet_hash != img_hash, \
            f"Contact sheet is identical to {name} — montage may not have run"