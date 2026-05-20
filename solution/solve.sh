#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────────────────────

cat > /service/app/math/scalar_ops.py << 'PYEOF'
"""
scalar_ops.py
=============
Scalar utility functions: angle wrapping, value clamping, and quadratic cost.
All functions operate on plain Python floats and sequences.
"""
from __future__ import annotations
import math
from typing import Sequence


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value to the closed interval [low, high]."""
    return max(low, min(high, value))


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the principal interval using modular arithmetic."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def quadratic_cost(x: Sequence[float], q_diag: Sequence[float]) -> float:
    """Weighted quadratic cost for a diagonal weight matrix (Mahalanobis form)."""
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
Combines a timed impulse event with persistent low-amplitude sinusoidal forcing.
"""
from __future__ import annotations
import math
from app.core.config import PlantConfig, FaultConfig


def compute_disturbance(t: float, cfg: PlantConfig, faults: FaultConfig) -> float:
    """Return the net external disturbance force acting on the cart at time t."""
    if abs(t - faults.impulse_time) <= cfg.dt * 0.5:
        return faults.impulse_magnitude
    return 0.25 * math.sin(1.7 * t) + 0.08 * math.sin(8.2 * t)
PYEOF

cat > /service/app/plant/integrator.py << 'PYEOF'
"""
integrator.py
=============
Numerical integration for the cart-pole plant.
RK4 is used for ground-truth simulation; Euler for fast MPC prediction rollouts.
"""
from __future__ import annotations
from typing import Callable, List
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
    """Advance state by dt using the classical Runge-Kutta method."""
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
PYEOF

# ─────────────────────────────────────────────────────────────
# CONTROLLER
# ─────────────────────────────────────────────────────────────

cat > /service/app/controller/cost.py << 'PYEOF'
"""
cost.py
=======
Cost function for the sampling-based MPC rollout.
Computes stage and terminal costs over a finite horizon.
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
    """State error relative to the reference setpoint."""
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
    """Total cost of a control sequence from start_state over the horizon."""
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
Selects control actions by rolling out candidate sequences through the plant model.
Confidence is updated from the EKF innovation energy each step.
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

cat > /service/app/controller/candidates.py << 'PYEOF'
"""
candidates.py
=============
Candidate control sequence generation for the sampling-based MPC.
Generates warm-started and constant-hold sequences for evaluation.
"""
from __future__ import annotations
import itertools
from typing import List, Tuple
from app.core.config import ControllerConfig


def generate_candidates(
    last_plan: List[float],
    cfg: ControllerConfig,
) -> List[Tuple[float, ...]]:
    """Return all candidate control sequences for the current MPC step."""
    base = [cfg.warm_start_decay * u for u in last_plan[1:] + [0.0]]
    positions = [0, 1, 3, 7, 12]
    sequences: List[Tuple[float, ...]] = []

    for choices in itertools.product(cfg.candidates, repeat=2):
        seq = base[:]
        for idx, pos in enumerate(positions):
            if pos < len(seq):
                seq[pos] = choices[idx % 2]
        sequences.append(tuple(seq))

    for constant in cfg.candidates:
        sequences.append(tuple([constant] * cfg.horizon))

    return sequences
PYEOF

# ─────────────────────────────────────────────────────────────
# ESTIMATOR
# ─────────────────────────────────────────────────────────────

cat > /service/app/estimator/ekf.py << 'PYEOF'
"""
ekf.py
======
Extended Kalman Filter for cart-pole state estimation.
Implements predict and update steps with adaptive measurement noise scaling.
"""
from __future__ import annotations
from typing import List, Optional
from app.core.config import EstimatorConfig, PlantConfig, FaultConfig
from app.plant.cart_pole import CartPolePlant
from app.math.vec_ops import vec_add, vec_sub
from app.math.mat_ops import (
    mat_add, mat_sub, mat_mul, mat_identity, mat_diag, mat_vec_mul, transpose,
)
from app.math.linalg import inverse_4x4, finite_difference_jacobian
from app.math.scalar_ops import wrap_angle


class ExtendedKalmanFilter:
    def __init__(
        self,
        cfg: EstimatorConfig,
        plant_cfg: PlantConfig,
        fault_cfg: FaultConfig,
        initial_state: List[float],
    ) -> None:
        self.cfg = cfg
        self.model = CartPolePlant(plant_cfg, fault_cfg)
        self.x: List[float] = initial_state[:]
        self.P = mat_diag(cfg.initial_covariance_diag)
        self.Q = mat_diag(cfg.process_noise_diag)
        self.R = mat_diag(cfg.measurement_noise_diag)
        self.H = mat_identity(4)
        self.innovation_energy: float = 0.0

    def predict(self, u: float, dt: float) -> None:
        """Propagate state and covariance forward through the plant model."""
        def f(local_state: List[float]) -> List[float]:
            return self.model.predict_step(local_state, u, dt)

        F = finite_difference_jacobian(f, self.x)
        self.x = f(self.x)
        Ft = transpose(F)
        self.P = mat_add(mat_mul(mat_mul(F, self.P), Ft), self.Q)

    def update(self, z: Optional[List[float]]) -> None:
        """Incorporate a measurement into the state estimate."""
        if z is None:
            inflation = mat_diag([0.0005, 0.006, 0.0005, 0.006])
            self.P = mat_add(self.P, inflation)
            return

        y = vec_sub(z, self.x)
        y[2] = wrap_angle(y[2])

        S = mat_add(mat_mul(mat_mul(self.H, self.P), transpose(self.H)), self.R)
        K = mat_mul(mat_mul(self.P, transpose(self.H)), inverse_4x4(S))
        correction = mat_vec_mul(K, y)
        self.x = vec_add(self.x, correction)
        self.x[2] = wrap_angle(self.x[2])

        eye = mat_identity(4)
        self.P = mat_mul(mat_sub(eye, mat_mul(K, self.H)), self.P)

        self.innovation_energy = 0.96 * self.innovation_energy + 0.04 * sum(v * v for v in y)
        scale = 1.0 + self.cfg.adaptive_noise_gain * min(50.0, self.innovation_energy)
        self.R = mat_diag([v * scale for v in self.cfg.measurement_noise_diag])

    def state(self) -> List[float]:
        """Return a copy of the current state estimate."""
        return self.x[:]
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
Issues warnings and computes a normalised health score each timestep.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class HealthReport:
    """Summary of system health at a single timestep."""
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
        """Compute health metrics and return a HealthReport for this timestep."""
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

# Clear bytecode cache so Python picks up patched source files.
find /service -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
