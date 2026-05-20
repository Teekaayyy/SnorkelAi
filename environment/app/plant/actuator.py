"""
actuator.py
===========
Actuator model: rate-limiting, saturation, and fault-period scaling.

    rate limit  — max force change per timestep
    saturation  — hard clamp to ±actuator_limit
    fault drop  — output scaled by actuator_drop_scale during [drop_start, drop_end]
"""
from __future__ import annotations
from app.core.config import PlantConfig, FaultConfig
from app.math.scalar_ops import clamp


class Actuator:
    def __init__(self, cfg: PlantConfig, faults: FaultConfig) -> None:
        self.cfg = cfg
        self.faults = faults
        self.last_force: float = 0.0

    def apply(self, requested_force: float, t: float) -> float:
        """Apply rate limiting, saturation, and fault injection."""
        max_delta = self.cfg.actuator_rate_limit * self.cfg.dt
        rate_limited = clamp(
            requested_force,
            self.last_force - max_delta,
            self.last_force + max_delta,
        )
        saturated = clamp(rate_limited, -self.cfg.actuator_limit, self.cfg.actuator_limit)
        if self.faults.actuator_drop_start <= t <= self.faults.actuator_drop_end:
            saturated *= self.faults.actuator_drop_scale
        self.last_force = saturated
        return saturated
