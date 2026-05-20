"""
scalar_ops.py
=============
Scalar utility functions: angle wrapping, value clamping, and quadratic cost.
"""
from __future__ import annotations
import math
from typing import Sequence


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to [low, high]."""
    return max(low, min(high, value))


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the interval [-π, π]."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def quadratic_cost(x: Sequence[float], q_diag: Sequence[float]) -> float:
    """Compute the weighted quadratic cost xᵀ Q x for a diagonal Q."""
    return sum(q * xi for q, xi in zip(q_diag, x))
