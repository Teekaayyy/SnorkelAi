"""
rail_constraint.py
==================
Rail constraint model for the cart-pole track.

The cart is confined to [-rail_limit, +rail_limit] metres.
Position is hard-clamped after each integration step.
The cart velocity is not zeroed at the rail — the integrator
handles that implicitly through the clamped position.
"""
from __future__ import annotations
from app.math.scalar_ops import clamp


def apply_rail(x: float, rail_limit: float) -> float:
    """Clamp cart position to the physical rail bounds."""
    return clamp(x, -rail_limit, rail_limit)


def at_rail(x: float, rail_limit: float, margin: float = 0.0) -> bool:
    """Return True if the cart is within margin of either rail end."""
    return abs(x) >= rail_limit - margin
