"""
innovation.py
=============
Innovation energy tracker for the EKF adaptive noise scaling.

Innovation energy is an exponential moving average of the squared
measurement residual norm:

    E[k] = α × E[k-1] + (1 - α) × ||y[k]||²

When innovation energy is high the filter has been surprised by measurements,
suggesting model mismatch. The measurement noise covariance R is scaled up
to make the filter more conservative.
"""
from __future__ import annotations
from typing import List

_ALPHA: float = 0.96
_BETA: float = 1.0 - _ALPHA


def update_energy(current: float, residual: List[float]) -> float:
    """Return the updated innovation energy given the current residual vector."""
    norm_sq = sum(v * v for v in residual)
    return _ALPHA * current + _BETA * norm_sq


def noise_scale(energy: float, gain: float, cap: float = 50.0) -> float:
    """Return the R scaling factor from innovation energy."""
    return 1.0 + gain * min(cap, energy)
