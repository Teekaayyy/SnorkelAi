"""math package — vector, matrix, linear algebra, and scalar utilities."""
from app.math.vec_ops import vec_add, vec_sub, vec_scale, dot
from app.math.mat_ops import (
    mat_identity, mat_diag, mat_add, mat_sub,
    mat_mul, mat_vec_mul, transpose, outer,
)
from app.math.linalg import inverse_4x4, finite_difference_jacobian
from app.math.scalar_ops import clamp, wrap_angle, quadratic_cost

__all__ = [
    "vec_add", "vec_sub", "vec_scale", "dot",
    "mat_identity", "mat_diag", "mat_add", "mat_sub",
    "mat_mul", "mat_vec_mul", "transpose", "outer",
    "inverse_4x4", "finite_difference_jacobian",
    "clamp", "wrap_angle", "quadratic_cost",
]
