"""
sensor_suite.py
===============
Sensor model: Gaussian noise, random dropout, bias random walk, and fault-period bias injection.

    dropout  — returns None with probability dropout_probability
    bias     — slow random walk on each channel
    fault    — adds sensor_theta_bias to theta during [sensor_bias_start, sensor_bias_end]
"""
from __future__ import annotations
import random
from typing import List, Optional
from app.core.config import SensorConfig, FaultConfig


class SensorSuite:
    def __init__(self, cfg: SensorConfig, faults: FaultConfig) -> None:
        self.cfg = cfg
        self.faults = faults
        self.rng = random.Random(cfg.seed)
        self.bias: List[float] = [0.0, 0.0, 0.0, 0.0]
        self.std: List[float] = [cfg.x_std, cfg.xdot_std, cfg.theta_std, cfg.thetadot_std]
        self.last_measurement: Optional[List[float]] = None

    def measure(self, state: List[float], t: float) -> Optional[List[float]]:
        """Return a noisy measurement, or None on dropout."""
        if self.rng.random() < self.cfg.dropout_probability:
            return None
        for i in range(4):
            self.bias[i] += self.rng.gauss(0.0, self.cfg.bias_walk_std)
        measurement = [
            state[i] + self.bias[i] + self.rng.gauss(0.0, self.std[i])
            for i in range(4)
        ]
        if self.faults.sensor_bias_start <= t <= self.faults.sensor_bias_end:
            measurement[2] += self.faults.sensor_theta_bias
        self.last_measurement = measurement
        return measurement
