"""Combined test output file for platform checker. Contains all milestone tests."""

import hashlib
import subprocess
from pathlib import Path


# --- Milestone 1: Resize images to 800x600 ---

RESIZED_DIR = Path("/app/output/resized")
WATERMARKED_DIR = Path("/app/output/watermarked")
CONTACT_SHEET = Path("/app/output/contact_sheet.png")
IMAGES = ["image_1.png", "image_2.png", "image_3.png"]


def test_resized_directory_exists() -> None:
    assert RESIZED_DIR.is_dir(), f"Directory {RESIZED_DIR} does not exist"


def test_all_resized_files_present() -> None:
    for name in IMAGES:
        p = RESIZED_DIR / name
        assert p.exists(), f"Resized file missing: {p}"


def test_resized_dimensions_are_800x600() -> None:
    for name in IMAGES:
        p = RESIZED_DIR / name
        result = subprocess.run(
            ["identify", "-format", "%wx%h", str(p)],
            capture_output=True, text=True, check=True
        )
        dims = result.stdout.strip()
        assert dims == "800x600", f"{name}: expected 800x600, got {dims}"


def test_resized_files_are_png() -> None:
    for name in IMAGES:
        p = RESIZED_DIR / name
        result = subprocess.run(
            ["identify", "-format", "%m", str(p)],
            capture_output=True, text=True, check=True
        )
        fmt = result.stdout.strip()
        assert fmt == "PNG", f"{name}: expected PNG format, got {fmt}"


# --- Milestone 2: Watermark images ---

def test_watermarked_directory_exists() -> None:
    assert WATERMARKED_DIR.is_dir(), f"Directory {WATERMARKED_DIR} does not exist"


def test_all_watermarked_files_present() -> None:
    for name in IMAGES:
        p = WATERMARKED_DIR / name
        assert p.exists(), f"Watermarked file missing: {p}"


def test_watermarked_files_are_png() -> None:
    for name in IMAGES:
        p = WATERMARKED_DIR / name
        result = subprocess.run(
            ["identify", "-format", "%m", str(p)],
            capture_output=True, text=True, check=True
        )
        fmt = result.stdout.strip()
        assert fmt == "PNG", f"{name}: expected PNG format, got {fmt}"


def test_watermarked_files_differ_from_resized() -> None:
    """Watermarked images must be different from resized (watermark was applied)."""
    for name in IMAGES:
        wm = (WATERMARKED_DIR / name).read_bytes()
        rs = (RESIZED_DIR / name).read_bytes()
        assert hashlib.md5(wm).hexdigest() != hashlib.md5(rs).hexdigest(), (
            f"{name}: watermarked image is identical to resized — watermark may not have been applied"
        )


# --- Milestone 3: Contact sheet ---

def test_contact_sheet_exists() -> None:
    assert CONTACT_SHEET.exists(), f"Contact sheet missing: {CONTACT_SHEET}"


def test_contact_sheet_is_png() -> None:
    result = subprocess.run(
        ["identify", "-format", "%m", str(CONTACT_SHEET)],
        capture_output=True, text=True, check=True
    )
    fmt = result.stdout.strip()
    assert fmt == "PNG", f"Expected PNG format, got {fmt}"


def test_contact_sheet_width_spans_3_images() -> None:
    """Contact sheet should be wider than a single watermarked image (3-column layout)."""
    result = subprocess.run(
        ["identify", "-format", "%w", str(CONTACT_SHEET)],
        capture_output=True, text=True, check=True
    )
    width = int(result.stdout.strip())
    assert width > 800, (
        f"Contact sheet width {width}px is not wider than a single image (800px) — "
        "3-column layout may not have been applied"
    )


def test_contact_sheet_is_not_empty() -> None:
    assert CONTACT_SHEET.stat().st_size > 10_000, (
        "Contact sheet file is suspiciously small — may be blank or corrupt"
    )