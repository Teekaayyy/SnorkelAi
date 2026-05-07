"""Tests for milestone 1. Run alone to verify only milestone 1: pytest tests/test_m1.py"""

import subprocess
from pathlib import Path


class TestMilestone1:
    """Tests for milestone 1: resize images to 800x600 and save as PNG to /app/output/resized/."""

    RESIZED_DIR = Path("/app/output/resized")
    IMAGES = ["image_1.png", "image_2.png", "image_3.png"]

    def test_resized_directory_exists(self) -> None:
        assert self.RESIZED_DIR.is_dir(), f"Directory {self.RESIZED_DIR} does not exist"

    def test_all_resized_files_present(self) -> None:
        for name in self.IMAGES:
            p = self.RESIZED_DIR / name
            assert p.exists(), f"Resized file missing: {p}"

    def test_resized_dimensions_are_800x600(self) -> None:
        for name in self.IMAGES:
            p = self.RESIZED_DIR / name
            result = subprocess.run(
                ["identify", "-format", "%wx%h", str(p)],
                capture_output=True, text=True, check=True
            )
            dims = result.stdout.strip()
            assert dims == "800x600", f"{name}: expected 800x600, got {dims}"

    def test_resized_files_are_png(self) -> None:
        for name in self.IMAGES:
            p = self.RESIZED_DIR / name
            result = subprocess.run(
                ["identify", "-format", "%m", str(p)],
                capture_output=True, text=True, check=True
            )
            fmt = result.stdout.strip()
            assert fmt == "PNG", f"{name}: expected PNG format, got {fmt}"