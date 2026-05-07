"""Tests for milestone 2. Run alone to verify only milestone 2: pytest tests/test_m2.py"""

import subprocess
from pathlib import Path


class TestMilestone2:
    """Tests for milestone 2: apply IMAGES_YES watermark to resized images."""

    WATERMARKED_DIR = Path("/app/output/watermarked")
    IMAGES = ["image_1.png", "image_2.png", "image_3.png"]

    def test_watermarked_directory_exists(self) -> None:
        assert self.WATERMARKED_DIR.is_dir(), f"Directory {self.WATERMARKED_DIR} does not exist"

    def test_all_watermarked_files_present(self) -> None:
        for name in self.IMAGES:
            p = self.WATERMARKED_DIR / name
            assert p.exists(), f"Watermarked file missing: {p}"

    def test_watermarked_files_are_png(self) -> None:
        for name in self.IMAGES:
            p = self.WATERMARKED_DIR / name
            result = subprocess.run(
                ["identify", "-format", "%m", str(p)],
                capture_output=True, text=True, check=True
            )
            fmt = result.stdout.strip()
            assert fmt == "PNG", f"{name}: expected PNG format, got {fmt}"

    def test_watermarked_files_differ_from_resized(self) -> None:
        """Watermarked images must be different from resized (watermark was applied)."""
        import hashlib
        resized_dir = Path("/app/output/resized")
        for name in self.IMAGES:
            wm = (self.WATERMARKED_DIR / name).read_bytes()
            rs = (resized_dir / name).read_bytes()
            assert hashlib.md5(wm).hexdigest() != hashlib.md5(rs).hexdigest(), (
                f"{name}: watermarked image is identical to resized — watermark may not have been applied"
            )