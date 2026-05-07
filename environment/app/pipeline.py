"""
pipeline.py — Image processing pipeline using ImageMagick via subprocess.

Stages:
    1. Resize images to 800x600 → /app/output/resized/
    2. Watermark each resized image with "IMAGES_YES" → /app/output/watermarked/
    3. Combine watermarked images into a 3-column contact sheet → /app/output/contact_sheet.png
"""

import sys
from pathlib import Path

from stages.resize import run_resize
from stages.watermark import run_watermark
from stages.contact_sheet import run_contact_sheet
from utils.logger import get_logger
from utils.file_ops import collect_images, ensure_dirs
from config.settings import (
    IMAGES_DIR,
    RESIZED_DIR,
    WATERMARKED_DIR,
    CONTACT_SHEET_PATH,
)

logger = get_logger(__name__)


def main() -> None:
    logger.info("Pipeline started")

    ensure_dirs([RESIZED_DIR, WATERMARKED_DIR])

    images = collect_images(IMAGES_DIR)
    if not images:
        logger.error("No images found in %s", IMAGES_DIR)
        sys.exit(1)

    logger.info("Found %d images to process", len(images))

    logger.info("Stage 1: Resizing images")
    run_resize(images, RESIZED_DIR)

    logger.info("Stage 2: Applying watermarks")
    resized_images = collect_images(RESIZED_DIR)
    run_watermark(resized_images, WATERMARKED_DIR)

    logger.info("Stage 3: Building contact sheet")
    watermarked_images = collect_images(WATERMARKED_DIR)
    run_contact_sheet(watermarked_images, CONTACT_SHEET_PATH)

    logger.info("Pipeline complete. Contact sheet: %s", CONTACT_SHEET_PATH)


if __name__ == "__main__":
    main()