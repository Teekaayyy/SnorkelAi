"""
cart_pole.py
============
Top-level CartPolePlant: composes actuator, disturbance, dynamics, and integrator.

Used by both the simulation (rk4_step) and the MPC rollout (predict_step).
"""
from __future__ import annotations
from typing import List, Tuple
from app.core.config import PlantConfig, FaultConfig
from app.plant.actuator import Actuator
from app.plant.disturbance import compute_disturbance
from app.plant.dynamics import derivatives
from app.plant.integrator import rk4_step, euler_step

State = List[float]


class CartPolePlant:
    def __init__(self, cfg: PlantConfig, faults: FaultConfig) -> None:
        self.cfg = cfg
        self.faults = faults
        self.actuator = Actuator(cfg, faults)

    def rk4_step(self, state: State, requested_force: float, t: float) -> Tuple[State, float]:
        """Full physics step with actuator model and RK4 integration."""
        u = self.actuator.apply(requested_force, t)
        d = compute_disturbance(t, self.cfg, self.faults)

        def deriv_fn(s: State, f: float, ts: float) -> State:
            return derivatives(s, f, ts, self.cfg, d)

        nxt = rk4_step(state, u, t, self.cfg.dt, deriv_fn, self.cfg)
        return nxt, u

    def predict_step(self, state: State, force: float, dt: float) -> State:
        """Lightweight Euler prediction used by the MPC rollout (no actuator model)."""
        deriv = derivatives(state, force, 0.0, self.cfg, 0.0)
        return euler_step(state, deriv, dt)
