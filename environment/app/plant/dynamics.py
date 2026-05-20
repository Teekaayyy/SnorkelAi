"""
dynamics.py
===========
Nonlinear cart-pole equations of motion.

State vector: [x, x_dot, theta, theta_dot]

    x        — cart position (m)
    x_dot    — cart velocity (m/s)
    theta    — pole angle from vertical (rad)
    theta_dot — pole angular velocity (rad/s)
"""
from __future__ import annotations
import math
from typing import List
from app.core.config import PlantConfig

State = List[float]


def derivatives(state: State, force: float, t: float, cfg: PlantConfig, disturbance: float) -> State:
    """Return the time derivatives of the state vector."""
    x, x_dot, theta, theta_dot = state
    c = math.cos(theta)
    s = math.sin(theta)
    total_mass = cfg.cart_mass + cfg.pole_mass
    polemass_length = cfg.pole_mass * cfg.pole_length

    friction = cfg.viscous_friction * x_dot
    if abs(x_dot) > 1e-4:
        friction += cfg.coulomb_friction * (1.0 if x_dot > 0 else -1.0)

    effective_force = force + disturbance - friction
    temp = (effective_force + polemass_length * theta_dot * theta_dot * s) / total_mass
    denom = cfg.pole_length * (4.0 / 3.0 - cfg.pole_mass * c * c / total_mass)
    theta_acc = (cfg.gravity * s - c * temp) / denom
    x_acc = temp - polemass_length * theta_acc * c / total_mass
    return [x_dot, x_acc, theta_dot, theta_acc]
