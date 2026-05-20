"""
adaptive_mpc.py
===============
Sampling-based Adaptive Model Predictive Controller.

At each step:
    1. Generate candidate control sequences.
    2. Roll out each candidate using the plant model.
    3. Select the sequence with lowest cost.
    4. Apply the first element, scaled by model confidence.
    5. Update confidence from EKF innovation energy.

Model confidence:
    High confidence → full control output.
    Low confidence  → reduced output (more cautious).
"""
from __future__ import annotations
import math
from typing import List, Sequence
from app.core.config import ControllerConfig, PlantConfig, FaultConfig
from app.plant.cart_pole import CartPolePlant
from app.controller.cost import rollout_cost
from app.controller.candidates import generate_candidates
from app.math.scalar_ops import clamp


class AdaptiveMPC:
    def __init__(
        self,
        cfg: ControllerConfig,
        plant_cfg: PlantConfig,
        fault_cfg: FaultConfig,
    ) -> None:
        self.cfg = cfg
        self.plant_cfg = plant_cfg
        self.plant = CartPolePlant(plant_cfg, fault_cfg)
        self.last_plan: List[float] = [0.0] * cfg.horizon
        self.last_force: float = 0.0
        self.model_confidence: float = 1.0

    def compute(
        self,
        estimated_state: Sequence[float],
        ref_x: float,
        ref_theta: float,
    ) -> float:
        """Select the best control action for the current estimated state."""
        best_cost = math.inf
        best_seq = self.last_plan[:]

        for seq in generate_candidates(self.last_plan, self.cfg):
            c = rollout_cost(
                estimated_state, seq, ref_x, ref_theta,
                self.last_force, self.cfg,
                self.plant.predict_step,
            )
            if c < best_cost:
                best_cost = c
                best_seq = list(seq)

        self.last_plan = best_seq
        u = best_seq[0]
        u *= 1.0 + (1.0 - self.model_confidence) * 0.25
        u = clamp(u, -self.plant_cfg.actuator_limit, self.plant_cfg.actuator_limit)
        self.last_force = u
        return u

    def adapt(self, innovation_energy: float) -> None:
        """Update model confidence from EKF innovation energy."""
        target = 1.0 / (1.0 + 0.15 * innovation_energy)
        self.model_confidence = 0.98 * self.model_confidence + 0.02 * target
