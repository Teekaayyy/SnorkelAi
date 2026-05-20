"""
vec_ops.py
==========
Vector arithmetic helpers used across the estimator and controller.
All functions operate on plain Python lists of floats.
"""
from __future__ import annotations
from typing import Sequence, List

Vector = List[float]


def vec_add(a: Sequence[float], b: Sequence[float]) -> Vector:
    """Element-wise addition."""
    return [x + y for x, y in zip(a, b)]


def vec_sub(a: Sequence[float], b: Sequence[float]) -> Vector:
    """Element-wise subtraction."""
    return [x - y for x, y in zip(a, b)]


def vec_scale(a: Sequence[float], s: float) -> Vector:
    """Scalar multiplication."""
    return [x * s for x in a]


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Inner product."""
    return sum(x * y for x, y in zip(a, b))
