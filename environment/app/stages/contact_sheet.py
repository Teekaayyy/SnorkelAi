"""Stage 3: Combine watermarked images into a 3-column contact sheet using ImageMagick montage."""

import subprocess
from pathlib import Path

from config.settings import (
    CONTACT_SHEET_COLUMNS,
    CONTACT_SHEET_GEOMETRY,
    CONTACT_SHEET_BACKGROUND,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def run_contact_sheet(images: list[Path], output_path: Path) -> None:
    """Combine all images into a contact sheet with CONTACT_SHEET_COLUMNS columns."""
    if not images:
        raise ValueError("No images provided for contact sheet generation")

    tile = f"{CONTACT_SHEET_COLUMNS}x"

    cmd = (
        ["montage", str(output_path)]
        + [str(img) for img in images]
        + [
            "-tile", tile,
            "-geometry", CONTACT_SHEET_GEOMETRY,
            "-background", CONTACT_SHEET_BACKGROUND,
            str(output_path),
        ]
    )
    subprocess.run(cmd, check=True)
    logger.info("Contact sheet saved to %s", output_path)