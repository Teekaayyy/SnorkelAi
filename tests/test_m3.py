"""Tests for milestone 3. Run alone to verify only milestone 3: pytest tests/test_m3.py"""

import subprocess
from pathlib import Path


class TestMilestone3:
    """Tests for milestone 3: combine watermarked images into a contact sheet."""

    CONTACT_SHEET = Path("/app/output/contact_sheet.png")

    def test_contact_sheet_exists(self) -> None:
        assert self.CONTACT_SHEET.exists(), f"Contact sheet missing: {self.CONTACT_SHEET}"

    def test_contact_sheet_is_png(self) -> None:
        result = subprocess.run(
            ["identify", "-format", "%m", str(self.CONTACT_SHEET)],
            capture_output=True, text=True, check=True
        )
        fmt = result.stdout.strip()
        assert fmt == "PNG", f"Expected PNG format, got {fmt}"

    def test_contact_sheet_width_spans_3_images(self) -> None:
        """Contact sheet should be wider than a single watermarked image (3-column layout)."""
        result = subprocess.run(
            ["identify", "-format", "%w", str(self.CONTACT_SHEET)],
            capture_output=True, text=True, check=True
        )
        width = int(result.stdout.strip())
        assert width > 800, (
            f"Contact sheet width {width}px is not wider than a single image (800px) — "
            "3-column layout may not have been applied"
        )

    def test_contact_sheet_is_not_empty(self) -> None:
        assert self.CONTACT_SHEET.stat().st_size > 10_000, (
            "Contact sheet file is suspiciously small — may be blank or corrupt"
        )