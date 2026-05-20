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

        score = 1.0 - avg_residual - 0.1 * avg_force_error - 0.03 * len(messages)
        return HealthReport(score=score, messages=messages, emergency_stop=emergency)
