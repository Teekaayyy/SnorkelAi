"""
Adaptive MPC Bug Challenge
==========================
Sampling-based adaptive Model Predictive Control for nonlinear cart-pole stabilisation.
"""
from app.utils.simulation import ClosedLoopSimulation
from app.core.config import ChallengeConfig
from app.logger.telemetry import TelemetryLogger

__all__ = ["ClosedLoopSimulation", "ChallengeConfig", "TelemetryLogger"]
__version__ = "1.0.0"
