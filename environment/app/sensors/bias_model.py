"""
bias_model.py
=============
Sensor bias random walk model.

Each measurement channel carries a slowly drifting bias that evolves as:

    bias[k+1] = bias[k] + N(0, bias_walk_std)

The bias is initialised to zero and updated at every measurement call,
regardless of dropout.
"""
from __future__ import annotations
import random
from typing import List


class BiasModel:
    def __init__(self, n_channels: int, walk_std: float, rng: random.Random) -> None:
        self._bias: List[float] = [0.0] * n_channels
        self._walk_std = walk_std
        self._rng = rng

    def step(self) -> List[float]:
        """Advance the bias random walk by one step and return the current bias."""
        for i in range(len(self._bias)):
            self._bias[i] += self._rng.gauss(0.0, self._walk_std)
        return self._bias[:]

    @property
    def current(self) -> List[float]:
        """Return the current bias without advancing."""
        return self._bias[:]

    def reset(self) -> None:
        """Reset all bias channels to zero."""
        self._bias = [0.0] * len(self._bias)
