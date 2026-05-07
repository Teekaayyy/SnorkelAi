"""Stage 2: Stamp IMAGES_YES watermark on resized images using ImageMagick."""

import subprocess
from pathlib import Path

from config.settings import (
    WATERMARK_TEXT,
    WATERMARK_GRAVITY,
    WATERMARK_POINTSIZE,
    WATERMARK_FILL,
    WATERMARK_UNDERCOLOR,
    WATERMARK_FONT,
)
from utils.file_ops import output_path
from utils.logger import get_logger

logger = get_logger(__name__)


def watermark_image(src: Path, dest: Path) -> None:
    """Apply centered text watermark to a single image and save as PNG."""
    subprocess.run(
        [
            "convert", str(src),
            "-gravity", WATERMARK_GRAVITY,
            "-pointsize", str(WATERMARK_POINTSIZE),
            "-font", WATERMARK_FONT,
            "-fill", WATERMARK_FILL,
            "-undercolor", WATERMARK_UNDERCOLOR,
            "-annotate", "90", WATERMARK_TEXT,
            str(dest),
        ],
        check=True,
    )
    logger.info("Watermarked %s → %s", src.name, dest)


def run_watermark(images: list[Path], output_dir: Path) -> None:
    """Apply watermark to all images in the list and write to output_dir."""
    for img in images:
        dest = output_path(img, output_dir)
        watermark_image(img, dest)