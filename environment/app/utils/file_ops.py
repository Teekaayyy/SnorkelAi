"""File system utilities for the pipeline."""

from pathlib import Path


def collect_images(directory: Path) -> list[Path]:
    """Return sorted list of PNG images in a directory."""
    return sorted(directory.glob("*.png"))


def ensure_dirs(directories: list[Path]) -> None:
    """Create directories if they do not exist."""
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)


def output_path(source: Path, destination_dir: Path) -> Path:
    """Derive destination path by placing source filename into destination_dir."""
    return destination_dir / (source.stem + ".jpg")