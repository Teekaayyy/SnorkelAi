"""
mat_ops.py
==========
Matrix arithmetic helpers: add, subtract, multiply, transpose, identity, diagonal.
All matrices are plain Python lists of lists of floats.
"""
from __future__ import annotations
from typing import Iterable, List, Sequence

Matrix = List[List[float]]
Vector = List[float]


def mat_identity(n: int) -> Matrix:
    """Return the n×n identity matrix."""
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def mat_diag(values: Iterable[float]) -> Matrix:
    """Return a diagonal matrix from a sequence of values."""
    vals = list(values)
    n = len(vals)
    return [[vals[i] if i == j else 0.0 for j in range(n)] for i in range(n)]


def mat_add(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise addition."""
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mat_sub(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise subtraction."""
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    """Matrix multiplication."""
    rows, cols, mid = len(a), len(b[0]), len(b)
    return [[sum(a[i][k] * b[k][j] for k in range(mid)) for j in range(cols)] for i in range(rows)]


def mat_vec_mul(a: Matrix, x: Sequence[float]) -> Vector:
    """Matrix-vector multiplication."""
    return [sum(row[j] * x[j] for j in range(len(x))) for row in a]


def transpose(a: Matrix) -> Matrix:
    """Matrix transpose."""
    return [list(row) for row in zip(*a)]


def outer(a: Sequence[float], b: Sequence[float]) -> Matrix:
    """Outer product of two vectors."""
    return [[x * y for y in b] for x in a]
