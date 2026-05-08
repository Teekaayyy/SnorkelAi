"""Internal pipeline tests — incomplete stubs, not used for evaluation."""

from pathlib import Path

RESIZED_DIR = Path("/app/output/resized")
WATERMARKED_DIR = Path("/app/output/watermarked")
CONTACT_SHEET = Path("/app/output/contact_sheet.png")
IMAGES = ["image_1.png", "image_2.png", "image_3.png"]


class TestResize:
    def test_resized_files_exist(self):
        pass

    def test_resized_dimensions(self):
        pass


class TestWatermark:
    def test_watermarked_files_exist(self):
        pass

    def test_watermark_applied(self):
        pass


class TestContactSheet:
    def test_contact_sheet_exists(self):
        pass

    def test_contact_sheet_layout(self):
        pass