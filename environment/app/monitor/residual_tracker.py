"""
residual_tracker.py
===================
Rolling-window residual and force-error statistics for the fault monitor.

Maintains two fixed-length windows (default 60 samples) and exposes
their running means for threshold comparison.
"""
from __future__ import annotations
from typing import List


class RollingWindow:
    def __init__(self, maxlen: int = 60) -> None:
        self._data: List[float] = []
        self._maxlen = maxlen

    def push(self, value: float) -> None:
        """Append a new value and evict the oldest if at capacity."""
        self._data.append(value)
        if len(self._data) > self._maxlen:
            self._data = self._data[-self._maxlen:]

    def mean(self) -> float:
        """Return the mean of the window, or 0.0 if empty."""
        if not self._data:
            return 0.0
        return sum(self._data) / len(self._data)

    def __len__(self) -> int:
        return len(self._data)


class ResidualTracker:
    """Tracks estimator residual and actuator force error over a rolling window."""

    def __init__(self, maxlen: int = 60) -> None:
        self.residuals = RollingWindow(maxlen)
        self.force_errors = RollingWindow(maxlen)

    def update(
        self,
        truth: List[float],
        estimate: List[float],
        commanded_force: float,
        actual_force: float,
    ) -> None:
        """Push new residual and force error into their windows."""
        residual = sum((truth[i] - estimate[i]) ** 2 for i in range(4)) ** 0.5
        self.residuals.push(residual)
        self.force_errors.push(abs(commanded_force - actual_force))

    @property
    def avg_residual(self) -> float:
        return self.residuals.mean()

    @property
    def avg_force_error(self) -> float:
        return self.force_errors.mean()
