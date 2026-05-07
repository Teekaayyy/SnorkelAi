"""Checksum utilities for comparing image files."""

import hashlib
from pathlib import Path


def md5(path: Path) -> str:
    """Return MD5 hex digest of a file."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def files_are_identical(a: Path, b: Path) -> bool:
    """Return True if two files have the same MD5 checksum."""
    return md5(a) == md5(b)