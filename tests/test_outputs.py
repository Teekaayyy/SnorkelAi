"""Verifier tests for the adaptive MPC cart-pole debugging task."""

import sys
sys.path.insert(0, "/service")

import pytest

from app.core.config import ChallengeConfig
from app.utils.simulation import ClosedLoopSimulation
from app.logger.telemetry import TelemetryLogger


def run_sim() -> TelemetryLogger:
    """Run a fresh closed-loop simulation with the default ChallengeConfig."""
    cfg = ChallengeConfig()
    sim = ClosedLoopSimulation(cfg)
    return sim.run()


@pytest.fixture(scope="module")
def logger():
    """Module-scoped simulation result fixture."""
    return run_sim()


@pytest.fixture(scope="module")
def rows(logger):
    """Module-scoped telemetry rows fixture."""
    return logger.rows


class TestSimulationCompletes:

    def test_produces_telemetry(self, rows):
        """Verify the simulation produces at least one logged telemetry row."""
        assert len(rows) > 0, "No telemetry rows produced"

    def test_runs_full_duration(self, rows):
        """Verify the simulation logs at least 40 samples covering the full 10-second run."""
        assert len(rows) >= 40, (
            f"Simulation produced only {len(rows)} samples — "
            "expected at least 40 for a full 10 s run at log_every=4"
        )

    def test_no_emergency_stop(self, rows):
        """Verify the simulation completes all 500 steps without triggering an emergency stop."""
        assert len(rows) == 41, (
            f"Got {len(rows)} logged samples; expected 41. "
            "Emergency stop triggered — system destabilised before 10 s."
        )


class TestPoleAngleStability:

    def test_max_abs_theta_within_bounds(self, rows):
        """Verify the pole angle never exceeds 0.25 radians throughout the run."""
        max_theta = max(abs(r.theta) for r in rows)
        assert max_theta < 0.25, (
            f"Max |theta| = {max_theta:.4f} rad exceeds 0.25 rad — "
            "pole control is degraded"
        )

    def test_theta_matches_golden(self, rows):
        """Verify the peak pole angle matches the known-good reference value within tolerance."""
        max_theta = max(abs(r.theta) for r in rows)
        assert abs(max_theta - 0.160073) < 0.01, (
            f"max |theta| = {max_theta:.6f} rad, expected ~0.160073 rad"
        )

    def test_initial_theta_correct(self, rows):
        """Verify the initial pole angle is approximately 0.16 rad as configured."""
        assert abs(rows[0].theta - 0.16) < 0.01, (
            f"Initial theta = {rows[0].theta:.6f} rad, expected ~0.16 rad"
        )


class TestCartPosition:

    def test_max_abs_x_within_rail(self, rows):
        """Verify the cart never reaches the physical rail limit of 2.4 m."""
        max_x = max(abs(r.x) for r in rows)
        assert max_x < 2.4, (
            f"Max |x| = {max_x:.4f} m — cart reached or exceeded the 2.4 m rail limit"
        )

    def test_x_matches_golden(self, rows):
        """Verify the peak cart displacement matches the known-good reference value."""
        max_x = max(abs(r.x) for r in rows)
        assert abs(max_x - 2.345751) < 0.05, (
            f"max |x| = {max_x:.6f} m, expected ~2.345751 m"
        )


class TestHealthScore:

    def test_health_scores_non_negative(self, rows):
        """Verify every health score is non-negative — the score must be clamped to [0, 1]."""
        neg = [r for r in rows if r.health_score < 0.0]
        assert len(neg) == 0, (
            f"{len(neg)} rows have negative health score. "
            "Health score must be clamped to [0, 1] at all times."
        )

    def test_health_scores_at_most_one(self, rows):
        """Verify no health score exceeds 1.0."""
        over = [r for r in rows if r.health_score > 1.0]
        assert len(over) == 0, (
            f"{len(over)} rows have health score > 1.0"
        )

    def test_mean_health_matches_golden(self, rows):
        """Verify the mean health score across the run matches the known-good reference."""
        mean_h = sum(r.health_score for r in rows) / len(rows)
        assert abs(mean_h - 0.942424) < 0.05, (
            f"Mean health = {mean_h:.6f}, expected ~0.942424"
        )

    def test_min_health_non_negative(self, rows):
        """Verify the minimum health score across the run is non-negative."""
        min_h = min(r.health_score for r in rows)
        assert min_h >= 0.0, (
            f"Minimum health score = {min_h:.6f} — score went negative"
        )


class TestWarningCount:

    def test_warning_samples_match_golden(self, rows):
        """Verify the number of samples with active health warnings matches the reference count."""
        warnings = sum(1 for r in rows if r.health_messages)
        assert warnings == 3, (
            f"warning_samples = {warnings}, expected 3. "
            "Unexpected control degradation or false alarm activity detected."
        )


class TestDeterminism:

    def test_same_config_same_trajectory(self):
        """Verify two independent runs with the same config produce identical trajectories."""
        r1 = run_sim().rows
        r2 = run_sim().rows
        assert len(r1) == len(r2), "Run lengths differ — simulation is non-deterministic"
        assert abs(r1[0].theta - r2[0].theta) < 1e-10
        assert abs(r1[-1].theta - r2[-1].theta) < 1e-10

    def test_first_row_theta_deterministic(self):
        """Verify the first logged theta value is identical across repeated runs."""
        r1 = run_sim().rows[0].theta
        r2 = run_sim().rows[0].theta
        assert r1 == r2, f"First theta differs between runs: {r1} vs {r2}"


class TestControlOutput:

    def test_commanded_force_within_limits(self, rows):
        """Verify the commanded force never exceeds the actuator saturation limit of 14 N."""
        for r in rows:
            assert abs(r.commanded_force) <= 14.0 + 1e-9, (
                f"commanded_force = {r.commanded_force:.3f} N at t={r.t:.2f} s "
                "exceeds the 14 N limit"
            )

    def test_actual_force_within_limits(self, rows):
        """Verify the actual applied force never exceeds the actuator saturation limit of 14 N."""
        for r in rows:
            assert abs(r.actual_force) <= 14.0 + 1e-9, (
                f"actual_force = {r.actual_force:.3f} N at t={r.t:.2f} s "
                "exceeds the 14 N limit"
            )


class TestEKFInnovation:

    def test_innovation_energy_non_negative(self, rows):
        """Verify the EKF innovation energy is non-negative at every logged timestep."""
        for r in rows:
            assert r.innovation_energy >= 0.0, (
                f"innovation_energy = {r.innovation_energy} at t={r.t:.2f} s is negative"
            )

    def test_innovation_energy_bounded(self, rows):
        """Verify the EKF innovation energy stays bounded, indicating the filter has not diverged."""
        max_ie = max(r.innovation_energy for r in rows)
        assert max_ie < 10.0, (
            f"Max innovation_energy = {max_ie:.4f} — EKF appears to be diverging"
        )
