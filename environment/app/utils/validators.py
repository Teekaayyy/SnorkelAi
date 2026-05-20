"""
validators.py
=============
Input validation for simulation configuration values.

Raises ValueError with a descriptive message if any parameter is
outside its physically valid range.
"""
from __future__ import annotations
from app.core.config import PlantConfig, ControllerConfig, EstimatorConfig


def validate_plant_config(cfg: PlantConfig) -> None:
    """Raise ValueError if any plant parameter is invalid."""
    if cfg.cart_mass <= 0:
        raise ValueError(f"cart_mass must be positive, got {cfg.cart_mass}")
    if cfg.pole_mass <= 0:
        raise ValueError(f"pole_mass must be positive, got {cfg.pole_mass}")
    if cfg.pole_length <= 0:
        raise ValueError(f"pole_length must be positive, got {cfg.pole_length}")
    if cfg.dt <= 0:
        raise ValueError(f"dt must be positive, got {cfg.dt}")
    if cfg.actuator_limit <= 0:
        raise ValueError(f"actuator_limit must be positive, got {cfg.actuator_limit}")


def validate_controller_config(cfg: ControllerConfig) -> None:
    """Raise ValueError if any controller parameter is invalid."""
    if cfg.horizon <= 0:
        raise ValueError(f"horizon must be positive, got {cfg.horizon}")
    if not (0.0 <= cfg.warm_start_decay <= 1.0):
        raise ValueError(f"warm_start_decay must be in [0, 1], got {cfg.warm_start_decay}")


def validate_estimator_config(cfg: EstimatorConfig) -> None:
    """Raise ValueError if any estimator parameter is invalid."""
    if any(v <= 0 for v in cfg.process_noise_diag):
        raise ValueError("All process_noise_diag values must be positive.")
    if any(v <= 0 for v in cfg.measurement_noise_diag):
        raise ValueError("All measurement_noise_diag values must be positive.")
    if any(v <= 0 for v in cfg.initial_covariance_diag):
        raise ValueError("All initial_covariance_diag values must be positive.")
