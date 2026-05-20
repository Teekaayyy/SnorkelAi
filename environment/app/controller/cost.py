"""
cost.py
=======
Cost function for the sampling-based MPC rollout.

Stage cost (per step k):
    J_k = xᵀ Q x + r u² + r_Δu Δu²

Terminal cost:
    J_T = xᵀ (terminal_scale × Q) x

Safety penalty is added when |theta| exceeds safety_theta_limit_rad.
"""
from __future__ import annotations
from typing import List, Sequence
from app.math.scalar_ops import quadratic_cost, wrap_angle
from app.core.config import ControllerConfig


def reference_error(
    state: Sequence[float],
    ref_x: float,
    ref_theta: float,
) -> List[float]:
    """Return the state error relative to the reference."""
    return [
        state[0] - ref_x,
        state[1],
        wrap_angle(state[2] - ref_theta),
        state[3],
    ]


def rollout_cost(
    start_state: Sequence[float],
    sequence: Sequence[float],
    ref_x: float,
    ref_theta: float,
    last_force: float,
    cfg: ControllerConfig,
    predict_fn,
) -> float:
    """Evaluate total cost of a control sequence starting from start_state."""
    q = [cfg.q_x, cfg.q_xdot, cfg.q_theta, cfg.q_thetadot]
    terminal_q = [v * cfg.terminal_scale for v in q]
    state = list(start_state)
    cost = 0.0
    prev_u = last_force
    for u in sequence:
        du = u - prev_u
        err = reference_error(state, ref_x, ref_theta)
        stage = quadratic_cost(err, q) + cfg.r_force * u * u + 0.002 * du
        if abs(state[2]) > cfg.safety_theta_limit_rad:
            stage += 500.0 * (abs(state[2]) - cfg.safety_theta_limit_rad)
        cost += stage
        state = predict_fn(state, u, cfg.dt)
        prev_u = u
    cost += quadratic_cost(reference_error(state, ref_x, ref_theta), terminal_q)
    return cost
