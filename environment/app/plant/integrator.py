"""
integrator.py
=============
Numerical integration for the cart-pole plant.

    rk4_step      — 4th-order Runge-Kutta used for the ground-truth simulation
    euler_step    — single forward-Euler step used for fast MPC prediction
"""
from __future__ import annotations
from typing import Callable, List, Tuple
from app.math.scalar_ops import clamp, wrap_angle
from app.core.config import PlantConfig

State = List[float]
DerivFn = Callable[[State, float, float], State]


def rk4_step(
    state: State,
    force: float,
    t: float,
    dt: float,
    deriv_fn: DerivFn,
    cfg: PlantConfig,
) -> State:
    """Advance state by dt using RK4. Returns new state (rail-clamped, angle-wrapped)."""
    k1 = deriv_fn(state, force, t)
    s2 = [state[i] + 0.5 * dt * k1[i] for i in range(4)]
    k2 = deriv_fn(s2, force, t + 0.5 * dt)
    s3 = [state[i] + 0.5 * dt * k2[i] for i in range(4)]
    k3 = deriv_fn(s3, force, t + 0.5 * dt)
    s4 = [state[i] + dt * k3[i] for i in range(4)]
    k4 = deriv_fn(s4, force, t + dt)
    nxt = [state[i] + dt * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6.0 for i in range(4)]
    nxt[0] = clamp(nxt[0], -cfg.rail_limit, cfg.rail_limit)
    nxt[2] = wrap_angle(nxt[2])
    return nxt


def euler_step(state: State, deriv: State, dt: float) -> State:
    """Single forward-Euler integration step."""
    nxt = [state[i] + dt * deriv[i] for i in range(4)]
    nxt[2] = wrap_angle(nxt[2])
    return nxt
