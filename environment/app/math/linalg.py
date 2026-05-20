"""
linalg.py
=========
Linear algebra helpers: 4×4 matrix inversion and finite-difference Jacobian.
Used by the Extended Kalman Filter.
"""
from __future__ import annotations
from typing import Callable, List, Sequence
from app.math.mat_ops import mat_identity, Matrix

Vector = List[float]


def inverse_4x4(a: Matrix) -> Matrix:
    """Gauss-Jordan inverse for a 4×4 matrix."""
    n = 4
    aug = [row[:] + ident for row, ident in zip(a, mat_identity(n))]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [v / div for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            aug[r] = [aug[r][c] - factor * aug[col][c] for c in range(2 * n)]
    return [row[n:] for row in aug]


def finite_difference_jacobian(
    func: Callable[[List[float]], List[float]],
    x: Sequence[float],
    eps: float = 1e-5,
) -> Matrix:
    """Compute a numerical Jacobian via central finite differences."""
    base = func(list(x))
    jac = []
    for i in range(len(base)):
        row = []
        for j in range(len(x)):
            xp = list(x)
            xm = list(x)
            xp[j] += eps
            xm[j] -= eps
            row.append((func(xp)[i] - func(xm)[i]) / (2.0 * eps))
        jac.append(row)
    return jac
