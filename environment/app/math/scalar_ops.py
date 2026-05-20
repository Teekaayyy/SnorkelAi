"""
scalar_ops.py
=============
Scalar utility functions: angle wrapping, value clamping, and quadratic cost.
All functions operate on plain Python floats and sequences.
"""
from __future__ import annotations
import math
from typing import Sequence


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to the closed interval [low, high]."""
    return max(low, min(high, value))


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the principal interval using modular arithmetic."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def quadratic_cost(x: Sequence[float], q_diag: Sequence[float]) -> float:
    """Weighted quadratic cost for a diagonal weight matrix (Mahalanobis form)."""
    return sum(q * xi for q, xi in zip(q_diag, x))
