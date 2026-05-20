"""
simulation.py
=============
Closed-loop simulation runner.

Each step:
    1. Sense — sensor returns a noisy measurement (or None on dropout).
    2. Estimate — EKF predict + update on the measurement.
    3. Control — MPC selects force; confidence is updated from innovation.
    4. Actuate — plant advances by one RK4 step.
    5. Monitor — health report; log at log_every cadence.
    6. Check — return False on emergency stop.
"""
from __future__ import annotations
from app.core.config import ChallengeConfig
from app.controller.adaptive_mpc import AdaptiveMPC
from app.estimator.ekf import ExtendedKalmanFilter
from app.monitor.health import FaultMonitor
from app.logger.telemetry import TelemetryLogger, TelemetryRow
from app.plant.cart_pole import CartPolePlant
from app.sensors.sensor_suite import SensorSuite


class ClosedLoopSimulation:
    def __init__(self, cfg: ChallengeConfig) -> None:
        self.cfg = cfg
        initial = list(cfg.simulation.initial_state)
        self.plant = CartPolePlant(cfg.plant, cfg.faults)
        self.sensors = SensorSuite(cfg.sensor, cfg.faults)
        self.ekf = ExtendedKalmanFilter(cfg.estimator, cfg.plant, cfg.faults, initial)
        self.controller = AdaptiveMPC(cfg.controller, cfg.plant, cfg.faults)
        self.monitor = FaultMonitor()
        self.logger = TelemetryLogger()
        self.truth = initial
        self.commanded_force: float = 0.0
        self.actual_force: float = 0.0

    def step(self, k: int) -> bool:
        """Advance the simulation by one timestep. Returns False on emergency stop."""
        t = k * self.cfg.plant.dt
        measurement = self.sensors.measure(self.truth, t)
        self.ekf.predict(self.actual_force, self.cfg.plant.dt)
        self.ekf.update(measurement)
        estimate = self.ekf.state()
        self.controller.adapt(self.ekf.innovation_energy)
        self.commanded_force = self.controller.compute(
            estimate,
            self.cfg.simulation.reference_x,
            self.cfg.simulation.reference_theta,
        )
        self.truth, self.actual_force = self.plant.rk4_step(
            self.truth, self.commanded_force, t
        )
        report = self.monitor.observe(
            self.truth, estimate, self.commanded_force, self.actual_force
        )
        if k % self.cfg.simulation.log_every == 0:
            self.logger.add(TelemetryRow(
                t=t,
                x=self.truth[0], xdot=self.truth[1],
                theta=self.truth[2], thetadot=self.truth[3],
                est_x=estimate[0], est_xdot=estimate[1],
                est_theta=estimate[2], est_thetadot=estimate[3],
                commanded_force=self.commanded_force,
                actual_force=self.actual_force,
                innovation_energy=self.ekf.innovation_energy,
                health_score=report.score,
                health_messages=";".join(report.messages),
            ))
        return not report.emergency_stop

    def run(self) -> TelemetryLogger:
        """Run the full simulation. Returns the telemetry logger."""
        steps = int(self.cfg.simulation.duration / self.cfg.plant.dt)
        for k in range(steps):
            ok = self.step(k)
            if not ok:
                break
        return self.logger
