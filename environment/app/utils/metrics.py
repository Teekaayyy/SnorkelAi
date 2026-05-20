"""
metrics.py
==========
Post-run performance metrics derived from telemetry.

Used by the test suite to assert correctness thresholds and by
the summary printer to give a human-readable performance report.
"""
from __future__ import annotations
import math
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.logger.telemetry import TelemetryRow


def max_abs_theta(rows: List["TelemetryRow"]) -> float:
    """Maximum absolute pole angle across all samples (radians)."""
    return max(abs(r.theta) for r in rows) if rows else 0.0


def max_abs_x(rows: List["TelemetryRow"]) -> float:
    """Maximum absolute cart position across all samples (metres)."""
    return max(abs(r.x) for r in rows) if rows else 0.0


def mean_health(rows: List["TelemetryRow"]) -> float:
    """Mean health score across all samples."""
    return sum(r.health_score for r in rows) / len(rows) if rows else 0.0


def min_health(rows: List["TelemetryRow"]) -> float:
    """Minimum health score across all samples."""
    return min(r.health_score for r in rows) if rows else 0.0


def warning_sample_count(rows: List["TelemetryRow"]) -> int:
    """Number of samples with at least one active health warning."""
    return sum(1 for r in rows if r.health_messages)


def rms(values: List[float]) -> float:
    """Root mean square of a list of values."""
    if not values:
        return 0.0
    return math.sqrt(sum(v * v for v in values) / len(values))
