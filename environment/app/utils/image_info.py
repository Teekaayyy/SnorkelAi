"""Helpers for retrieving image metadata via ImageMagick."""

import subprocess
from pathlib import Path


def get_dimensions(path: Path) -> tuple[int, int]:
    """Return (width, height) of an image using ImageMagick identify."""
    result = subprocess.run(
        ["identify", "-format", "%w %h", str(path)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split()
    return int(w), int(h)


def get_format(path: Path) -> str:
    """Return the format string (e.g. 'PNG') of an image."""
    result = subprocess.run(
        ["identify", "-format", "%m", str(path)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def get_file_size_bytes(path: Path) -> int:
    """Return file size in bytes."""
    return path.stat().st_size