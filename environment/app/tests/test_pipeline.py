"""Unit tests for the pipeline stages (run locally to verify working code)."""

import subprocess
from pathlib import Path


IMAGES_DIR = Path("/app/images")
RESIZED_DIR = Path("/app/output/resized")
WATERMARKED_DIR = Path("/app/output/watermarked")
CONTACT_SHEET = Path("/app/output/contact_sheet.png")
IMAGES = ["image_1.png", "image_2.png", "image_3.png"]


class TestResize:
    def test_resized_files_exist(self):
        for name in IMAGES:
            assert (RESIZED_DIR / name).exists()

    def test_resized_dimensions(self):
        for name in IMAGES:
            result = subprocess.run(
                ["identify", "-format", "%wx%h", str(RESIZED_DIR / name)],
                capture_output=True, text=True, check=True,
            )
            assert result.stdout.strip() == "800x600"

    def test_resized_format_is_png(self):
        for name in IMAGES:
            result = subprocess.run(
                ["identify", "-format", "%m", str(RESIZED_DIR / name)],
                capture_output=True, text=True, check=True,
            )
            assert result.stdout.strip() == "PNG"


class TestWatermark:
    def test_watermarked_files_exist(self):
        for name in IMAGES:
            assert (WATERMARKED_DIR / name).exists()

    def test_watermarked_differs_from_resized(self):
        import hashlib
        for name in IMAGES:
            wm = (WATERMARKED_DIR / name).read_bytes()
            rs = (RESIZED_DIR / name).read_bytes()
            assert hashlib.md5(wm).hexdigest() != hashlib.md5(rs).hexdigest()

    def test_watermarked_dimensions_preserved(self):
        for name in IMAGES:
            result = subprocess.run(
                ["identify", "-format", "%wx%h", str(WATERMARKED_DIR / name)],
                capture_output=True, text=True, check=True,
            )
            assert result.stdout.strip() == "800x600"


class TestContactSheet:
    def test_contact_sheet_exists(self):
        assert CONTACT_SHEET.exists()

    def test_contact_sheet_is_png(self):
        result = subprocess.run(
            ["identify", "-format", "%m", str(CONTACT_SHEET)],
            capture_output=True, text=True, check=True,
        )
        assert result.stdout.strip() == "PNG"

    def test_contact_sheet_wider_than_single_image(self):
        result = subprocess.run(
            ["identify", "-format", "%w", str(CONTACT_SHEET)],
            capture_output=True, text=True, check=True,
        )
        assert int(result.stdout.strip()) > 800