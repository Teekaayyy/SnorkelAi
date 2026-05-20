#!/usr/bin/env bash
set -euo pipefail

# =============================================================
# solve.sh
# Overwrites all buggy files with their correct implementations.
# =============================================================

# ─────────────────────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────────────────────

cat > /service/app/math/scalar_ops.py << 'PYEOF'
"""
scalar_ops.py
=============
Scalar utility functions: angle wrapping, value clamping, and quadratic cost.
"""
from __future__ import annotations
import math
from typing import Sequence


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to [low, high]."""
    return max(low, min(high, value))


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the interval [-π, π]."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def quadratic_cost(x: Sequence[float], q_diag: Sequence[float]) -> float:
    """Compute the weighted quadratic cost xᵀ Q x for a diagonal Q."""
    return sum(q * xi * xi for q, xi in zip(q_diag, x))
PYEOF

# ─────────────────────────────────────────────────────────────
# PLANT
# ─────────────────────────────────────────────────────────────

cat > /service/app/plant/disturbance.py << 'PYEOF'
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
    if abs(t - faults.impulse_time) <= cfg.dt * 0.5:
        return faults.impulse_magnitude
    return 0.25 * math.sin(1.7 * t) + 0.08 * math.sin(8.2 * t)
PYEOF

# ─────────────────────────────────────────────────────────────
# CONTROLLER
# ─────────────────────────────────────────────────────────────

cat > /service/app/controller/cost.py << 'PYEOF'
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
        stage = quadratic_cost(err, q) + cfg.r_force * u * u + 0.002 * du * du
        if abs(state[2]) > cfg.safety_theta_limit_rad:
            stage += 500.0 * (abs(state[2]) - cfg.safety_theta_limit_rad)
        cost += stage
        state = predict_fn(state, u, cfg.dt)
        prev_u = u
    cost += quadratic_cost(reference_error(state, ref_x, ref_theta), terminal_q)
    return cost
PYEOF

cat > /service/app/controller/adaptive_mpc.py << 'PYEOF'
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
        u *= 1.0 - (1.0 - self.model_confidence) * 0.25
        u = clamp(u, -self.plant_cfg.actuator_limit, self.plant_cfg.actuator_limit)
        self.last_force = u
        return u

    def adapt(self, innovation_energy: float) -> None:
        """Update model confidence from EKF innovation energy."""
        target = 1.0 / (1.0 + 0.15 * innovation_energy)
        self.model_confidence = 0.98 * self.model_confidence + 0.02 * target
PYEOF

# ─────────────────────────────────────────────────────────────
# MONITOR
# ─────────────────────────────────────────────────────────────

cat > /service/app/monitor/health.py << 'PYEOF'
"""
health.py
=========
Fault and safety monitor for the closed-loop system.

Tracks rolling residuals and force errors over a 60-sample window.
Issues warnings and emergency stops based on configurable thresholds.

Health score:
    score = clamp(1.0 − avg_residual − 0.1 × avg_force_error, 0.0, 1.0)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class HealthReport:
    """Summary of system health for a single timestep."""
    score: float
    messages: List[str]
    emergency_stop: bool


class FaultMonitor:
    def __init__(self) -> None:
        self.residual_window: List[float] = []
        self.force_window: List[float] = []
        self.trip_count: int = 0

    def observe(
        self,
        truth: List[float],
        estimate: List[float],
        commanded_force: float,
        actual_force: float,
    ) -> HealthReport:
        """Compute health metrics and return a HealthReport."""
        residual = sum((truth[i] - estimate[i]) ** 2 for i in range(4)) ** 0.5
        self.residual_window.append(residual)
        self.force_window.append(abs(commanded_force - actual_force))
        self.residual_window = self.residual_window[-60:]
        self.force_window = self.force_window[-60:]

        avg_residual = sum(self.residual_window) / max(1, len(self.residual_window))
        avg_force_error = sum(self.force_window) / max(1, len(self.force_window))

        messages: List[str] = []
        if avg_residual > 0.18:
            messages.append("Estimator residual high")
        if avg_force_error > 2.0:
            messages.append("Actuator mismatch likely")
        if abs(truth[0]) > 2.25:
            messages.append("Rail limit proximity")
        if abs(truth[2]) > 0.75:
            messages.append("Pole angle unsafe")

        emergency = abs(truth[0]) > 2.38 or abs(truth[2]) > 1.2
        if emergency:
            self.trip_count += 1

        raw_score = 1.0 - avg_residual - 0.1 * avg_force_error
        score = max(0.0, min(1.0, raw_score))
        return HealthReport(score=score, messages=messages, emergency_stop=emergency)
PYEOF

echo "All files restored to correct implementations."

# Clear bytecode cache so Python picks up patched source files.
find /service -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
