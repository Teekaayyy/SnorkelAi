"""
summary.py
==========
Summary statistics computed from a completed telemetry run.

    max_abs_theta     — worst pole deviation from vertical
    max_abs_x         — worst cart displacement
    mean_health       — average health score across all logged samples
    warning_samples   — number of samples with at least one active warning
    rms_theta         — root-mean-square pole angle
    rms_x             — root-mean-square cart position
"""
from __future__ import annotations
import math
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.logger.telemetry import TelemetryRow


def compute_summary(rows: List["TelemetryRow"]) -> dict:
    """Return a dictionary of summary statistics from a list of TelemetryRow objects."""
    if not rows:
        return {}
    n = len(rows)
    max_abs_theta = max(abs(r.theta) for r in rows)
    max_abs_x = max(abs(r.x) for r in rows)
    mean_health = sum(r.health_score for r in rows) / n
    warning_samples = sum(1 for r in rows if r.health_messages)
    rms_theta = math.sqrt(sum(r.theta ** 2 for r in rows) / n)
    rms_x = math.sqrt(sum(r.x ** 2 for r in rows) / n)
    return {
        "samples": n,
        "max_abs_theta_rad": max_abs_theta,
        "max_abs_x_m": max_abs_x,
        "mean_health": mean_health,
        "warning_samples": warning_samples,
        "rms_theta_rad": rms_theta,
        "rms_x_m": rms_x,
    }
