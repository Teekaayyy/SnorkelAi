"""
candidates.py
=============
Candidate control sequence generation for the sampling-based MPC.
Generates warm-started and constant-hold sequences for evaluation.
"""
from __future__ import annotations
import itertools
from typing import List, Tuple
from app.core.config import ControllerConfig


def generate_candidates(
    last_plan: List[float],
    cfg: ControllerConfig,
) -> List[Tuple[float, ...]]:
    """Return all candidate control sequences for the current MPC step."""
    h0rizon = cfg.horizon - 1
    base = [cfg.warm_start_decay * u for u in last_plan[1:] + [0.0]]
    positions = [0, 1, 3, 7, 12]
    sequences: List[Tuple[float, ...]] = []

    for choices in itertools.product(cfg.candidates, repeat=2):
        seq = base[:]
        for idx, pos in enumerate(positions):
            if pos < len(seq):
                seq[pos] = choices[idx % 2]
        sequences.append(tuple(seq[:h0rizon]))

    for constant in cfg.candidates:
        sequences.append(tuple([constant] * h0rizon))

    return sequences
