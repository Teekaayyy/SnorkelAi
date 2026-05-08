"""Post-stage validation to confirm outputs meet expectations."""

from pathlib import Path
from utils.image_info import get_dimensions, get_format
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_resized(output_dir: Path, expected_dims: tuple[int, int]) -> None:
    """Confirm all PNGs in output_dir have the expected dimensions."""
    for img in sorted(output_dir.glob("*.png")):
        h, w = get_dimensions(img)
        fmt = get_format(img)
        if (h, w) != expected_dims:
            raise ValueError(
                f"{img.name}: expected {expected_dims}, got {(h, w)}"
            )
        if fmt != "PNG":
            raise ValueError(f"{img.name}: expected PNG format, got {fmt}")
        logger.info("Validated resized: %s %s %s", img.name, (h, w), fmt)


def validate_watermarked(output_dir: Path, source_dir: Path) -> None:
    """Confirm watermarked images differ from their resized sources."""
    import hashlib
    for img in sorted(output_dir.glob("*.png")):
        src = source_dir / img.name
        if not src.exists():
            raise FileNotFoundError(f"Source for validation not found: {src}")
        wm_hash = hashlib.md5(img.read_bytes()).hexdigest()
        src_hash = hashlib.md5(src.read_bytes()).hexdigest()
        if wm_hash == src_hash:
            raise ValueError(f"{img.name}: watermarked file is identical to source")
        logger.info("Validated watermark applied: %s", img.name)


def validate_contact_sheet(path: Path, min_width: int) -> None:
    """Confirm contact sheet exists, is PNG, and is wider than a single image."""
    if not path.exists():
        raise FileNotFoundError(f"Contact sheet not found: {path}")
    fmt = get_format(path)
    if fmt != "PNG":
        raise ValueError(f"Contact sheet format expected PNG, got {fmt}")
    w, _ = get_dimensions(path)
    if w <= min_width:
        raise ValueError(f"Contact sheet width {w}px not greater than {min_width}px")
    logger.info("Validated contact sheet: %s width=%d", path.name, w)