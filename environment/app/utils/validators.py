"""Validation helpers for pipeline inputs and outputs."""

from pathlib import Path
import subprocess


def assert_file_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected file not found: {path}")


def get_image_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) of an image using ImageMagick identify."""
    result = subprocess.run(
        ["identify", "-format", "%wx%h", str(path)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split("x")
    return int(w), int(h)


def get_image_format(path: Path) -> str:
    """Return image format string e.g. 'PNG' using ImageMagick identify."""
    result = subprocess.run(
        ["identify", "-format", "%m", str(path)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()