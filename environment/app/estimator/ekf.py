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
        self.P = mat_mul(mat_sub(eye, mat_mul(self.H, K)), self.P)

        self.innovation_energy = 0.96 * self.innovation_energy + 0.04 * sum(v * v for v in y)
        scale = 1.0 + self.cfg.adaptive_noise_gain * min(50.0, self.innovation_energy)
        self.R = mat_diag([v * scale for v in self.cfg.measurement_noise_diag])

    def state(self) -> List[float]:
        """Return a copy of the current state estimate."""
        return self.x[:]
