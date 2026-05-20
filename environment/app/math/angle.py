"""
angle.py
========
Angle arithmetic helpers beyond basic wrapping.

    angle_diff  — shortest signed difference between two angles
    near_zero   — return True if angle is near zero
    sign        — return +1, -1, or 0
"""
from __future__ import annotations
from app.math.scalar_ops import wrap_angle


def angle_diff(a: float, b: float) -> float:
    """Return the shortest signed difference a - b, wrapped to the principal interval."""
    return wrap_angle(a - b)


def near_zero(angle: float, threshold: float = 0.05) -> bool:
    """Return True if the absolute angle is below threshold (radians)."""
    return abs(angle) < threshold


def sign(value: float) -> int:
    """Return +1 for positive values, -1 for negative values, 0 for zero."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0
