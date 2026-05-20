"""
covariance.py
=============
Covariance matrix utilities for the Extended Kalman Filter.

    symmetrise   — enforce P = (P + Pᵀ) / 2  to counteract floating-point drift
    is_positive  — check all diagonal entries are positive
    inflate      — add a diagonal inflation matrix (used during sensor dropout)
"""
from __future__ import annotations
from typing import List
from app.math.mat_ops import mat_add, transpose, Matrix


def symmetrise(P: Matrix) -> Matrix:
    """Return (P + Pᵀ) / 2 to enforce symmetry."""
    n = len(P)
    Pt = transpose(P)
    return [[(P[i][j] + Pt[i][j]) / 2.0 for j in range(n)] for i in range(n)]


def is_positive_definite_diag(P: Matrix) -> bool:
    """Return True if all diagonal entries of P are strictly positive."""
    return all(P[i][i] > 0.0 for i in range(len(P)))


def inflate(P: Matrix, diagonal_values: List[float]) -> Matrix:
    """Add diagonal inflation to P (used during measurement dropout)."""
    n = len(P)
    inflation = [[diagonal_values[i] if i == j else 0.0 for j in range(n)] for i in range(n)]
    return mat_add(P, inflation)
