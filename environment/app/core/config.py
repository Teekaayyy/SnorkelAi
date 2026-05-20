"""
config.py
=========
All configuration dataclasses for the adaptive MPC system.
Each sub-config is frozen and composed into ChallengeConfig.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class PlantConfig:
    gravity: float = 9.81
    cart_mass: float = 1.0
    pole_mass: float = 0.18
    pole_length: float = 0.55
    viscous_friction: float = 0.08
    coulomb_friction: float = 0.025
    actuator_limit: float = 14.0
    actuator_rate_limit: float = 80.0
    rail_limit: float = 2.4
    dt: float = 0.02


@dataclass(frozen=True)
class SensorConfig:
    x_std: float = 0.003
    xdot_std: float = 0.018
    theta_std: float = 0.0025
    thetadot_std: float = 0.014
    dropout_probability: float = 0.01
    bias_walk_std: float = 0.0004
    seed: int = 22


@dataclass(frozen=True)
class ControllerConfig:
    horizon: int = 18
    dt: float = 0.02
    q_x: float = 1.4
    q_xdot: float = 0.08
    q_theta: float = 42.0
    q_thetadot: float = 0.55
    r_force: float = 0.035
    terminal_scale: float = 8.0
    candidates: Tuple[float, ...] = (-10.0, -6.5, -3.5, -1.5, 0.0, 1.5, 3.5, 6.5, 10.0)
    warm_start_decay: float = 0.75
    safety_theta_limit_rad: float = 0.8


@dataclass(frozen=True)
class EstimatorConfig:
    process_noise_diag: Tuple[float, float, float, float] = (2e-5, 2.5e-3, 2e-5, 2.0e-3)
    measurement_noise_diag: Tuple[float, float, float, float] = (9e-6, 3.24e-4, 6.25e-6, 1.96e-4)
    initial_covariance_diag: Tuple[float, float, float, float] = (0.02, 0.15, 0.02, 0.15)
    adaptive_noise_gain: float = 0.018


@dataclass(frozen=True)
class FaultConfig:
    impulse_time: float = 3.2
    impulse_magnitude: float = 2.4
    actuator_drop_start: float = 5.3
    actuator_drop_end: float = 6.25
    actuator_drop_scale: float = 0.55
    sensor_bias_start: float = 7.0
    sensor_bias_end: float = 8.0
    sensor_theta_bias: float = 0.035


@dataclass(frozen=True)
class SimulationConfig:
    duration: float = 10.0
    initial_state: Tuple[float, float, float, float] = (0.0, 0.0, 0.16, 0.0)
    reference_x: float = 0.0
    reference_theta: float = 0.0
    log_every: int = 4


@dataclass(frozen=True)
class ChallengeConfig:
    plant: PlantConfig = field(default_factory=PlantConfig)
    sensor: SensorConfig = field(default_factory=SensorConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    estimator: EstimatorConfig = field(default_factory=EstimatorConfig)
    faults: FaultConfig = field(default_factory=FaultConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
