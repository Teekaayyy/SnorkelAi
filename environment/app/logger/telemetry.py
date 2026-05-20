"""
telemetry.py
============
CSV telemetry logger and text summary for a closed-loop simulation run.

Each logged row captures truth state, estimated state, control signals,
EKF innovation energy, and health metrics at the logging rate.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


@dataclass
class TelemetryRow:
    """One logged sample from the closed-loop simulation."""
    t: float
    x: float
    xdot: float
    theta: float
    thetadot: float
    est_x: float
    est_xdot: float
    est_theta: float
    est_thetadot: float
    commanded_force: float
    actual_force: float
    innovation_energy: float
    health_score: float
    health_messages: str


class TelemetryLogger:
    def __init__(self) -> None:
        self.rows: List[TelemetryRow] = []

    def add(self, row: TelemetryRow) -> None:
        """Append a telemetry row."""
        self.rows.append(row)

    def write_csv(self, path: str) -> None:
        """Write all rows to a CSV file, creating parent directories as needed."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(self.rows[0]).keys()))
            writer.writeheader()
            for row in self.rows:
                writer.writerow(asdict(row))

    def summary(self) -> str:
        """Return a human-readable summary of the simulation run."""
        if not self.rows:
            return "No telemetry."
        max_abs_theta = max(abs(r.theta) for r in self.rows)
        max_abs_x = max(abs(r.x) for r in self.rows)
        mean_health = sum(r.health_score for r in self.rows) / len(self.rows)
        last = self.rows[-1]
        warning_count = sum(1 for r in self.rows if r.health_messages)
        return (
            f"samples={len(self.rows)}\n"
            f"max_abs_theta_rad={max_abs_theta:.4f}\n"
            f"max_abs_x_m={max_abs_x:.4f}\n"
            f"mean_health={mean_health:.4f}\n"
            f"final_state=[{last.x:.3f}, {last.xdot:.3f}, {last.theta:.3f}, {last.thetadot:.3f}]\n"
            f"warning_samples={warning_count}"
        )
