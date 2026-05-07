"""Stage 1: Resize images to 800x600 using ImageMagick."""

import subprocess
from pathlib import Path

from config.settings import RESIZE_DIMENSIONS
from utils.file_ops import output_path
from utils.logger import get_logger

logger = get_logger(__name__)


def resize_image(src: Path, dest: Path) -> None:
    """Resize a single image to 800x600 and save as PNG."""
    subprocess.run(
        ["convert", str(src), "-resize", f"{RESIZE_DIMENSIONS}", str(dest)],
        check=True,
    )
    logger.info("Resized %s → %s", src.name, dest)


def run_resize(images: list[Path], output_dir: Path) -> None:
    """Resize all images in the list and write to output_dir."""
    for img in images:
        dest = output_path(img, output_dir)
        resize_image(img, dest)