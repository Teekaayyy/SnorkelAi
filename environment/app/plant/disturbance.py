"""
disturbance.py
==============
External disturbance model applied to the cart.

    impulse    — single force spike at impulse_time
    persistent — low-amplitude sinusoidal background forcing
"""
from __future__ import annotations
import math
from app.core.config import PlantConfig, FaultConfig


def compute_disturbance(t: float, cfg: PlantConfig, faults: FaultConfig) -> float:
    """Return the total external disturbance force at time t."""
    if t >= faults.impulse_time and t <= faults.impulse_time + cfg.dt:
        return faults.impulse_magnitude
    return 0.25 * math.sin(1.7 * t) + 0.08 * math.sin(8.2 * t)
