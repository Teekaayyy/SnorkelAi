"""
disturbance.py
==============
External disturbance model applied to the cart.
Combines a timed impulse event with persistent low-amplitude sinusoidal forcing.
"""
from __future__ import annotations
import math
from app.core.config import PlantConfig, FaultConfig


def compute_disturbance(t: float, cfg: PlantConfig, faults: FaultConfig) -> float:
    """Return the net external disturbance force acting on the cart at time t."""
    if t >= faults.impulse_time and t <= faults.impulse_time + cfg.dt:
        return faults.impulse_magnitude
    return 0.25 * math.sin(1.7 * t) + 0.08 * math.sin(8.2 * t)
