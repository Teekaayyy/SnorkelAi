"""
warm_start.py
=============
Warm-start plan management for the MPC.

Between timesteps, the previous optimal plan is shifted by one step
and decayed to avoid stale high-force commands.

    shifted[i] = decay * plan[i + 1]  for i in 0 … H-2
    shifted[H-1] = 0.0
"""
from __future__ import annotations
from typing import List


def shift_and_decay(plan: List[float], decay: float) -> List[float]:
    """Return the warm-started plan for the next timestep."""
    shifted = [decay * u for u in plan[1:]]
    shifted.append(0.0)
    return shifted


def constant_plan(value: float, horizon: int) -> List[float]:
    """Return a horizon-length plan holding a constant force value."""
    return [value] * horizon
